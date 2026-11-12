<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/StemGNN · page 4 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data_loader/forecast_dataloader.py](data_loader/forecast_dataloader.py)
- [main.py](main.py)
- [models/base_model.py](models/base_model.py)
- [models/handler.py](models/handler.py)

</details>



This document provides a high-level overview of the STemGNN system architecture, describing the major components, their relationships, and how data flows through the system during training and evaluation. This page focuses on the overall structure and interactions between components.

For detailed information about specific subsystems, see:
- Main entry point orchestration: [Main Entry Point](#4.1)
- Training and validation loops: [Model Lifecycle Manager](#4.2)
- Neural network implementation: [Neural Network Architecture](#4.3)
- Data loading and preprocessing: [Data Pipeline](#4.4)
- Performance metrics: [Evaluation Metrics](#4.5)

## Layered Architecture Overview

The STemGNN system is organized as a four-layer architecture with clear separation of concerns. Each layer has specific responsibilities and communicates through well-defined interfaces.

```mermaid
graph TB
    subgraph Interface["Interface Layer"]
        CLI["Command-Line Interface<br/>main.py<br/>Argument parsing, configuration"]
    end
    
    subgraph Orchestration["Orchestration Layer"]
        MainOrch["Main Orchestrator<br/>main.py:53-68<br/>Data splitting, workflow control"]
    end
    
    subgraph Application["Application Layer"]
        TrainFunc["train()<br/>models/handler.py:103-191<br/>Training loop, optimization"]
        TestFunc["test()<br/>models/handler.py:194-207<br/>Model evaluation"]
        ValidateFunc["validate()<br/>models/handler.py:67-100<br/>Performance validation"]
        InferenceFunc["inference()<br/>models/handler.py:41-64<br/>Multi-step forecasting"]
    end
    
    subgraph Model["Model Layer"]
        ModelClass["Model class<br/>models/base_model.py:78-179<br/>Neural network architecture"]
        StockBlock["StockBlockLayer class<br/>models/base_model.py:16-75<br/>Spectral processing"]
        GLUClass["GLU class<br/>models/base_model.py:6-13<br/>Gated activation"]
    end
    
    subgraph Data["Data Layer"]
        ForecastDS["ForecastDataset class<br/>data_loader/forecast_dataloader.py:41-73<br/>PyTorch Dataset"]
        NormFunc["normalized()<br/>data_loader/forecast_dataloader.py:7-22<br/>Data normalization"]
        DenormFunc["de_normalized()<br/>data_loader/forecast_dataloader.py:25-38<br/>Denormalization"]
    end
    
    subgraph Utils["Utilities Layer"]
        EvalFunc["evaluate()<br/>utils/math_utils.py<br/>MAPE, MAE, RMSE"]
    end
    
    CLI --> MainOrch
    MainOrch --> TrainFunc
    MainOrch --> TestFunc
    TrainFunc --> ValidateFunc
    TestFunc --> ValidateFunc
    ValidateFunc --> InferenceFunc
    TrainFunc --> ModelClass
    InferenceFunc --> ModelClass
    ModelClass --> StockBlock
    StockBlock --> GLUClass
    TrainFunc --> ForecastDS
    ValidateFunc --> ForecastDS
    ForecastDS --> NormFunc
    ValidateFunc --> DenormFunc
    ValidateFunc --> EvalFunc
```

**Sources:** [main.py:1-68](), [models/handler.py:1-207](), [models/base_model.py:1-180](), [data_loader/forecast_dataloader.py:1-74]()

## Core Component Relationships

The system's components interact through a clearly defined dependency graph. The following diagram maps natural language concepts to their concrete implementations in the codebase.

```mermaid
graph LR
    subgraph EntryPoint["Entry Point"]
        ArgParser["argparse.ArgumentParser<br/>main.py:9"]
        ArgsNamespace["args namespace<br/>main.py:33"]
    end
    
    subgraph DataManagement["Data Management"]
        PandasDF["pandas.read_csv()<br/>main.py:42"]
        TrainData["train_data<br/>main.py:48"]
        ValidData["valid_data<br/>main.py:49"]
        TestData["test_data<br/>main.py:50"]
    end
    
    subgraph ModelLifecycle["Model Lifecycle"]
        TrainHandler["train() function<br/>models/handler.py:103"]
        TestHandler["test() function<br/>models/handler.py:194"]
        SaveModel["save_model()<br/>models/handler.py:16-24"]
        LoadModel["load_model()<br/>models/handler.py:27-38"]
    end
    
    subgraph NeuralNet["Neural Network"]
        ModelInstance["Model instance<br/>models/handler.py:105"]
        TorchOptim["torch.optim.RMSprop<br/>models/handler.py:127"]
        LRScheduler["ExponentialLR<br/>models/handler.py:130"]
        MSELoss["nn.MSELoss<br/>models/handler.py:140"]
    end
    
    subgraph DataPipeline["Data Pipeline"]
        TrainDataset["ForecastDataset(train)<br/>models/handler.py:132"]
        ValidDataset["ForecastDataset(valid)<br/>models/handler.py:134"]
        TestDataset["ForecastDataset(test)<br/>models/handler.py:199"]
        TrainLoader["DataLoader(train)<br/>models/handler.py:136"]
        ValidLoader["DataLoader(valid)<br/>models/handler.py:138"]
        TestLoader["DataLoader(test)<br/>models/handler.py:201"]
    end
    
    subgraph Persistence["Persistence"]
        ModelFile["_stemgnn.pt<br/>models/handler.py:22"]
        NormStatFile["norm_stat.json<br/>models/handler.py:123"]
        ResultsCSV["predict.csv, target.csv<br/>models/handler.py:92-97"]
    end
    
    ArgParser --> ArgsNamespace
    PandasDF --> TrainData
    PandasDF --> ValidData
    PandasDF --> TestData
    
    ArgsNamespace --> TrainHandler
    TrainData --> TrainHandler
    ValidData --> TrainHandler
    TestData --> TestHandler
    
    TrainHandler --> ModelInstance
    TrainHandler --> TorchOptim
    TrainHandler --> LRScheduler
    TrainHandler --> MSELoss
    TrainHandler --> TrainDataset
    TrainHandler --> ValidDataset
    TrainDataset --> TrainLoader
    ValidDataset --> ValidLoader
    TestDataset --> TestLoader
    
    TrainHandler --> SaveModel
    TestHandler --> LoadModel
    SaveModel --> ModelFile
    TrainHandler --> NormStatFile
    TestHandler --> NormStatFile
    TestHandler --> ResultsCSV
```

**Sources:** [main.py:9-68](), [models/handler.py:16-207]()

## Data Flow Through the System

Data flows through multiple transformation stages from raw CSV input to final predictions. This diagram shows the complete pipeline with actual function and class names from the codebase.

```mermaid
flowchart TD
    subgraph Input["Input Stage"]
        CSVFile["CSV File<br/>dataset/*.csv"]
        ReadCSV["pd.read_csv()<br/>main.py:42"]
        RawData["data: numpy array<br/>main.py:42"]
    end
    
    subgraph Split["Data Splitting Stage"]
        SplitLogic["Ratio calculation<br/>main.py:45-47"]
        TrainSplit["train_data = data[:split1]<br/>main.py:48"]
        ValidSplit["valid_data = data[split1:split2]<br/>main.py:49"]
        TestSplit["test_data = data[split2:]<br/>main.py:50"]
    end
    
    subgraph Normalization["Normalization Stage"]
        ComputeStats["Compute mean/std or min/max<br/>models/handler.py:112-119"]
        SaveStats["Save to norm_stat.json<br/>models/handler.py:123"]
        NormalizeData["normalized() function<br/>data_loader/forecast_dataloader.py:7-22"]
    end
    
    subgraph Windowing["Windowing Stage"]
        ForecastDSInit["ForecastDataset.__init__()<br/>data_loader/forecast_dataloader.py:42-54"]
        GetXEndIdx["get_x_end_idx()<br/>data_loader/forecast_dataloader.py:68-73"]
        GetItem["__getitem__(index)<br/>data_loader/forecast_dataloader.py:56-63"]
    end
    
    subgraph Batching["Batching Stage"]
        DataLoader["torch.utils.data.DataLoader<br/>models/handler.py:136-138"]
        BatchTensor["Batched tensors<br/>(batch_size, window_size, nodes)"]
    end
    
    subgraph Forward["Forward Pass Stage"]
        ModelForward["model.forward(x)<br/>models/base_model.py:167-179"]
        GraphLearning["latent_correlation_layer()<br/>models/base_model.py:136-149"]
        StockBlocks["StockBlockLayer.forward()<br/>models/base_model.py:61-75"]
        Predictions["forecast output<br/>(batch_size, horizon, nodes)"]
    end
    
    subgraph Evaluation["Evaluation Stage"]
        InferenceLoop["inference() loop<br/>models/handler.py:41-64"]
        Denormalize["de_normalized()<br/>data_loader/forecast_dataloader.py:25-38"]
        EvalMetrics["evaluate() function<br/>utils/math_utils.py"]
        Results["MAPE, MAE, RMSE scores"]
    end
    
    CSVFile --> ReadCSV
    ReadCSV --> RawData
    RawData --> SplitLogic
    SplitLogic --> TrainSplit
    SplitLogic --> ValidSplit
    SplitLogic --> TestSplit
    
    TrainSplit --> ComputeStats
    ComputeStats --> SaveStats
    ComputeStats --> NormalizeData
    
    NormalizeData --> ForecastDSInit
    ForecastDSInit --> GetXEndIdx
    GetXEndIdx --> GetItem
    GetItem --> DataLoader
    DataLoader --> BatchTensor
    
    BatchTensor --> ModelForward
    ModelForward --> GraphLearning
    GraphLearning --> StockBlocks
    StockBlocks --> Predictions
    
    Predictions --> InferenceLoop
    InferenceLoop --> Denormalize
    Denormalize --> EvalMetrics
    EvalMetrics --> Results
```

**Sources:** [main.py:35-50](), [models/handler.py:41-191](), [data_loader/forecast_dataloader.py:7-73](), [models/base_model.py:136-179]()

## Execution Flow State Machine

The system operates as a state machine controlled by command-line flags. This diagram shows the complete execution flow with actual code references.

```mermaid
stateDiagram-v2
    [*] --> ParseArguments: python main.py
    
    ParseArguments: Parse command-line args<br/>argparse.ArgumentParser<br/>main.py:9-33
    
    ParseArguments --> CreateDirectories
    
    CreateDirectories: Create output directories<br/>os.makedirs()<br/>main.py:38-41
    
    CreateDirectories --> LoadCSV
    
    LoadCSV: Load dataset<br/>pd.read_csv()<br/>main.py:42
    
    LoadCSV --> SplitData
    
    SplitData: Split into train/valid/test<br/>Using ratio parameters<br/>main.py:44-50
    
    SplitData --> CheckTrainFlag
    
    state CheckTrainFlag <<choice>>
    CheckTrainFlag --> TrainingPhase: args.train == True
    CheckTrainFlag --> CheckEvalFlag: args.train == False
    
    state TrainingPhase {
        [*] --> InitializeModel: Model(node_cnt, 2, ...)<br/>models/handler.py:105
        InitializeModel --> ComputeNormStats: Calculate mean/std<br/>models/handler.py:112-124
        ComputeNormStats --> CreateDatasets: ForecastDataset instances<br/>models/handler.py:132-138
        CreateDatasets --> SetupOptimizer: RMSProp or Adam<br/>models/handler.py:126-130
        SetupOptimizer --> EpochLoop: for epoch in range(args.epoch)<br/>models/handler.py:152
        
        state EpochLoop {
            [*] --> TrainMode: model.train()<br/>models/handler.py:154
            TrainMode --> ForwardPass: forecast, _ = model(inputs)<br/>models/handler.py:161
            ForwardPass --> ComputeLoss: MSELoss(forecast, target)<br/>models/handler.py:162
            ComputeLoss --> Backward: loss.backward()<br/>models/handler.py:164
            Backward --> OptimizerStep: my_optim.step()<br/>models/handler.py:165
            OptimizerStep --> SaveCheckpoint: save_model(model, ...)<br/>models/handler.py:169
            SaveCheckpoint --> CheckValidation
            
            state CheckValidation <<choice>>
            CheckValidation --> Validate: epoch % validate_freq == 0<br/>models/handler.py:172
            CheckValidation --> CheckEarlyStop: else
            
            Validate --> CallValidateFunc: validate(model, valid_loader, ...)<br/>models/handler.py:176-178
            CallValidateFunc --> CompareBestMAE: Check if MAE improved<br/>models/handler.py:179-187
            CompareBestMAE --> CheckEarlyStop
            
            state CheckEarlyStop <<choice>>
            CheckEarlyStop --> [*]: Early stop triggered<br/>models/handler.py:189
            CheckEarlyStop --> TrainMode: Continue training
        }
        
        EpochLoop --> [*]: Training complete
    }
    
    TrainingPhase --> CheckEvalFlag
    
    state CheckEvalFlag <<choice>>
    CheckEvalFlag --> TestingPhase: args.evaluate == True
    CheckEvalFlag --> Done: args.evaluate == False
    
    state TestingPhase {
        [*] --> LoadNormStats: Load norm_stat.json<br/>models/handler.py:195-196
        LoadNormStats --> LoadTrainedModel: load_model(result_train_file)<br/>models/handler.py:197
        LoadTrainedModel --> CreateTestDataset: ForecastDataset(test_data, ...)<br/>models/handler.py:199-200
        CreateTestDataset --> CreateTestLoader: DataLoader(test_set, ...)<br/>models/handler.py:201-202
        CreateTestLoader --> CallValidate: validate(model, test_loader, ...)<br/>models/handler.py:203-205
        CallValidate --> SavePredictions: Save predict.csv, target.csv<br/>models/handler.py:92-97
        SavePredictions --> PrintResults: Print MAPE, MAE, RMSE<br/>models/handler.py:206-207
        PrintResults --> [*]
    }
    
    TestingPhase --> Done
    Done --> [*]: Print "done"<br/>main.py:68
```

**Sources:** [main.py:9-68](), [models/handler.py:103-207]()

## Component Responsibility Matrix

The following table summarizes the responsibilities of each major component and maps them to their code locations:

| Component | Primary Responsibility | Key Functions/Classes | File Location |
|-----------|------------------------|----------------------|---------------|
| **CLI Parser** | Parse command-line arguments, provide configuration | `argparse.ArgumentParser` | [main.py:9-33]() |
| **Data Splitter** | Split raw data into train/valid/test sets | Direct array slicing logic | [main.py:44-50]() |
| **Training Orchestrator** | Coordinate training workflow, manage lifecycle | `train()` function | [models/handler.py:103-191]() |
| **Testing Orchestrator** | Coordinate evaluation workflow | `test()` function | [models/handler.py:194-207]() |
| **Validation Engine** | Run inference and compute metrics | `validate()` function | [models/handler.py:67-100]() |
| **Inference Engine** | Multi-step forecasting with auto-regression | `inference()` function | [models/handler.py:41-64]() |
| **Model Persistence** | Save and load trained models | `save_model()`, `load_model()` | [models/handler.py:16-38]() |
| **Neural Network** | STemGNN architecture implementation | `Model` class | [models/base_model.py:78-179]() |
| **Spectral Processing** | Graph convolution and spectral transforms | `StockBlockLayer` class | [models/base_model.py:16-75]() |
| **Gated Activation** | Gated Linear Unit implementation | `GLU` class | [models/base_model.py:6-13]() |
| **Dataset Abstraction** | PyTorch Dataset for time series windows | `ForecastDataset` class | [data_loader/forecast_dataloader.py:41-73]() |
| **Normalization** | Z-score and min-max normalization | `normalized()`, `de_normalized()` | [data_loader/forecast_dataloader.py:7-38]() |
| **Metrics Calculation** | Compute MAPE, MAE, RMSE | `evaluate()` function | Referenced in [models/handler.py:13]() |

**Sources:** [main.py:1-68](), [models/handler.py:1-207](), [models/base_model.py:1-180](), [data_loader/forecast_dataloader.py:1-74]()

## Model Architecture Hierarchy

The neural network implementation follows a hierarchical structure where each layer builds upon lower-level components.

```mermaid
graph TD
    subgraph ModelClass["Model Class (base_model.py:78-179)"]
        ModelInit["__init__()<br/>Initialize components<br/>line 79-104"]
        ModelForward["forward(x)<br/>Main forward pass<br/>line 167-179"]
        
        LatentCorr["latent_correlation_layer(x)<br/>Graph structure learning<br/>line 136-149"]
        SelfAttn["self_graph_attention(input)<br/>Compute attention matrix<br/>line 151-162"]
        GetLaplacian["get_laplacian(graph, normalize)<br/>Compute graph Laplacian<br/>line 106-119"]
        ChebPoly["cheb_polynomial(laplacian)<br/>Chebyshev approximation<br/>line 121-134"]
    end
    
    subgraph StockBlockClass["StockBlockLayer Class (base_model.py:16-75)"]
        SBLInit["__init__()<br/>Initialize weights, GLUs<br/>line 17-44"]
        SBLForward["forward(x, mul_L)<br/>Process through layer<br/>line 61-75"]
        SpeSeqCell["spe_seq_cell(input)<br/>Spectral sequence processing<br/>line 46-59"]
    end
    
    subgraph GLUClass["GLU Class (base_model.py:6-13)"]
        GLUInit["__init__()<br/>Linear transformations<br/>line 7-10"]
        GLUForward["forward(x)<br/>Gated activation<br/>line 12-13"]
    end
    
    subgraph TorchComponents["PyTorch Components"]
        GRULayer["nn.GRU<br/>line 92"]
        FCLayer["nn.Sequential<br/>line 97-101"]
        LeakyReLU["nn.LeakyReLU<br/>line 102"]
        Dropout["nn.Dropout<br/>line 103"]
    end
    
    ModelInit --> GRULayer
    ModelInit --> FCLayer
    ModelInit --> LeakyReLU
    ModelInit --> Dropout
    ModelInit --> SBLInit
    
    ModelForward --> LatentCorr
    LatentCorr --> GRULayer
    LatentCorr --> SelfAttn
    SelfAttn --> GetLaplacian
    GetLaplacian --> ChebPoly
    
    ModelForward --> SBLForward
    SBLForward --> SpeSeqCell
    SpeSeqCell --> GLUForward
    
    SBLInit --> GLUInit
```

**Sources:** [models/base_model.py:1-180]()

## File System and Package Structure

The codebase follows a standard Python package structure with clear module separation:

```
StemGNN/
├── main.py                           # Entry point, orchestration
├── dataset/                          # Data storage
│   ├── ECG_data.csv                 # Sample dataset
│   └── PeMS07.csv                   # Sample dataset
├── models/                          # Neural network models
│   ├── __init__.py                 # Package marker
│   ├── base_model.py               # Model, StockBlockLayer, GLU classes
│   └── handler.py                  # train(), test(), validate(), inference()
├── data_loader/                     # Data preprocessing
│   ├── __init__.py                 # Package marker
│   └── forecast_dataloader.py      # ForecastDataset, normalization functions
├── utils/                           # Utility functions
│   ├── __init__.py                 # Package marker
│   └── math_utils.py               # evaluate() function for metrics
└── output/                          # Generated during runtime
    └── {dataset_name}/
        ├── train/
        │   ├── _stemgnn.pt         # Trained model checkpoint
        │   └── norm_stat.json      # Normalization statistics
        └── test/
            ├── predict.csv          # Predictions
            ├── target.csv           # Ground truth
            ├── predict_abs_error.csv # Absolute errors
            └── predict_ape.csv      # Absolute percentage errors
```

**Sources:** [main.py:35-41](), [models/handler.py:16-24](), [models/handler.py:92-97](), [models/handler.py:123]()

## Key Design Patterns

The system implements several software design patterns that contribute to its modularity and maintainability:

### Separation of Concerns
- **Interface Layer** ([main.py:9-33]()): Handles user interaction and configuration
- **Orchestration Layer** ([main.py:53-68]()): Controls workflow and delegates to subsystems
- **Application Layer** ([models/handler.py]()): Implements ML operations
- **Model Layer** ([models/base_model.py]()): Pure neural network logic
- **Data Layer** ([data_loader/forecast_dataloader.py]()): Data abstraction

### Factory Pattern
The system creates datasets and models based on configuration:
- `ForecastDataset` instantiation with different parameters for train/valid/test ([models/handler.py:132-138](), [models/handler.py:199-200]())
- Model instantiation with configuration-driven architecture ([models/handler.py:105]())

### Strategy Pattern
Normalization methods are selected at runtime:
- `z_score` or `min_max` normalization ([models/handler.py:112-119]())
- Optimizer selection: `RMSProp` or `Adam` ([models/handler.py:126-129]())

### Template Method Pattern
The training loop follows a template with customizable steps:
- Fixed structure: initialization → epoch loop → validation → early stopping
- Customizable: validation frequency, learning rate scheduling, early stopping criteria
- Implementation in [models/handler.py:152-190]()

**Sources:** [main.py:9-68](), [models/handler.py:103-191](), [data_loader/forecast_dataloader.py:41-73]()

## Dependencies Between Subsystems

The following diagram shows the import dependencies between modules, illustrating the coupling structure:

```mermaid
graph LR
    subgraph External["External Libraries"]
        Torch["torch<br/>PyTorch framework"]
        Pandas["pandas<br/>Data loading"]
        Numpy["numpy<br/>Numerical operations"]
    end
    
    subgraph MainModule["main.py"]
        MainPy["main module"]
    end
    
    subgraph ModelsPackage["models/"]
        Handler["handler.py<br/>Line 6: import torch<br/>Line 4: from data_loader.forecast_dataloader<br/>Line 5: from models.base_model<br/>Line 13: from utils.math_utils"]
        BaseModel["base_model.py<br/>Line 1: import torch<br/>Line 2: import torch.nn"]
    end
    
    subgraph DataPackage["data_loader/"]
        DataLoader["forecast_dataloader.py<br/>Line 1: import torch.utils.data<br/>Line 2: import numpy<br/>Line 4: import pandas"]
    end
    
    subgraph UtilsPackage["utils/"]
        MathUtils["math_utils.py<br/>Metrics implementation"]
    end
    
    MainPy --> Handler
    MainPy --> Torch
    MainPy --> Pandas
    
    Handler --> BaseModel
    Handler --> DataLoader
    Handler --> MathUtils
    Handler --> Torch
    
    BaseModel --> Torch
    
    DataLoader --> Torch
    DataLoader --> Numpy
    DataLoader --> Pandas
    
    MathUtils --> Numpy
```

**Sources:** [main.py:1-8](), [models/handler.py:1-13](), [models/base_model.py:1-3](), [data_loader/forecast_dataloader.py:1-4]()

## Workflow Summary

The complete system workflow can be summarized in these stages:

1. **Configuration Stage** ([main.py:9-33]()): Parse command-line arguments into `args` namespace
2. **Data Loading Stage** ([main.py:35-50]()): Load CSV and split into train/valid/test arrays
3. **Training Stage** ([models/handler.py:103-191]()):
   - Initialize `Model` instance
   - Compute normalization statistics
   - Create `ForecastDataset` instances
   - Run optimization loop with periodic validation
   - Save best model to `_stemgnn.pt`
4. **Testing Stage** ([models/handler.py:194-207]()):
   - Load trained model from `_stemgnn.pt`
   - Load normalization stats from `norm_stat.json`
   - Run inference on test data
   - Compute and save evaluation metrics
5. **Output Stage**: Save predictions, errors, and metrics to CSV files

Each stage is independent and can be executed separately by setting appropriate command-line flags (`--train` and `--evaluate`).

**Sources:** [main.py:53-68](), [models/handler.py:103-207]()

---

