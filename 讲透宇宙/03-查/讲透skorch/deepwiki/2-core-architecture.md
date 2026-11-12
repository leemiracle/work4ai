<!-- source: DeepWiki mcp.deepwiki.com · repo skorch-dev/skorch · page 2 Core Architecture · fetched 2026-10-21 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/testing.yml](.github/workflows/testing.yml)
- [README.rst](README.rst)
- [docs/user/installation.rst](docs/user/installation.rst)
- [skorch/net.py](skorch/net.py)
- [skorch/tests/test_net.py](skorch/tests/test_net.py)

</details>



This page explains the core architectural design and main components of the skorch library. It details how skorch bridges PyTorch and scikit-learn by providing a standardized, scikit-learn compatible interface for neural networks implemented in PyTorch.

For more specific information about the NeuralNet class, see [NeuralNet Class](#2.1). For details on dataset handling, see [Dataset Handling](#2.3).

## Overview

skorch's core architecture is designed to make PyTorch models work with scikit-learn's API while minimizing boilerplate code. It handles tasks like converting between NumPy arrays and PyTorch tensors, implementing the training loop, managing batching, and providing a callback system for customization.

```mermaid
graph TD
    subgraph "skorch System Architecture"
        NN["NeuralNet"] --> INIT["Initialization Process"]
        NN --> TF["Training Flow"]
        NN --> IF["Inference Flow"]
        NN --> CP["Component Management"]
        
        INIT --> Lazy["Lazy Initialization"]
        INIT --> PrefixParams["Parameter Handling\nwith Prefixes"]
        
        CP --> MOD["Module"]
        CP --> CRI["Criterion"]
        CP --> OPT["Optimizer"]
        CP --> DS["Dataset"]
        CP --> HIS["History"]
        CP --> CB["Callbacks"]
        
        TF --> Batching["Batching"]
        TF --> Forward["Forward Pass"]
        TF --> Loss["Loss Computation"]
        TF --> Backward["Backward Pass"]
        TF --> OptStep["Optimizer Step"]
        TF --> CallbackHooks["Callback Hooks"]
    end
```

Sources: [skorch/net.py:55-311](). This diagram is based on the core components described in the NeuralNet class docstring.

## Class Hierarchy and Inheritance

skorch provides a scikit-learn compatible interface through its class hierarchy. The base `NeuralNet` class inherits from scikit-learn's `BaseEstimator`, and specialized variants inherit from `NeuralNet`.

```mermaid
classDiagram
    class BaseEstimator {
        <<sklearn>>
        +fit()
        +get_params()
        +set_params()
    }
    
    class NeuralNet {
        +module_
        +criterion_
        +optimizer_
        +history_
        +callbacks_
        +initialize()
        +fit()
        +predict()
        +forward()
    }
    
    class ClassifierMixin {
        <<sklearn>>
        +predict()
        +score()
    }
    
    class RegressorMixin {
        <<sklearn>>
        +predict()
        +score()
    }
    
    class NeuralNetClassifier {
        +predict_proba()
    }
    
    class NeuralNetBinaryClassifier {
        +predict_proba()
    }
    
    class NeuralNetRegressor {
    }
    
    BaseEstimator <|-- NeuralNet
    NeuralNet <|-- NeuralNetClassifier
    NeuralNet <|-- NeuralNetBinaryClassifier
    NeuralNet <|-- NeuralNetRegressor
    ClassifierMixin <|-- NeuralNetClassifier
    ClassifierMixin <|-- NeuralNetBinaryClassifier
    RegressorMixin <|-- NeuralNetRegressor
```

Sources: [skorch/net.py:55-56](), [docs/user/neuralnet.rst:8-16]()

## Core Components

The main components of skorch's architecture work together to provide the bridge between PyTorch and scikit-learn:

```mermaid
graph TD
    subgraph "Core Components"
        NN["NeuralNet"] --- MOD["module_\n(PyTorch Module)"]
        NN --- CRI["criterion_\n(Loss Function)"]
        NN --- OPT["optimizer_\n(PyTorch Optimizer)"]
        NN --- HIS["history_\n(Training History)"]
        NN --- CB["callbacks_\n(Customization Points)"]
        NN --- DS["dataset\n(Data Handling)"]
    end
    
    subgraph "Data Flow"
        Input["Input Data\n(NumPy, PyTorch, etc.)"] --> Dataset["skorch Dataset"]
        Dataset --> DataLoader["PyTorch DataLoader"]
        DataLoader --> to_tensor["to_tensor()"]
        to_tensor --> to_device["to_device()"]
        to_device --> MOD
        MOD --> Output["Output\n(PyTorch Tensor)"]
        Output --> to_numpy["to_numpy()"]
        to_numpy --> FinalOutput["Final Output\n(NumPy array)"]
    end
```

Sources: [skorch/net.py:94-239](), [docs/user/neuralnet.rst:62-101]()

### NeuralNet

The `NeuralNet` class is the central component of skorch's architecture. It acts as a wrapper around PyTorch modules and provides scikit-learn compatibility.

Key responsibilities:
- Initializes and manages PyTorch components (module, criterion, optimizer)
- Implements the training loop
- Converts data between NumPy and PyTorch formats
- Manages callback execution during training
- Tracks training metrics in the history

Sources: [skorch/net.py:55-311](), [docs/user/neuralnet.rst:8-16]()

### Initialization Process

skorch uses lazy initialization, meaning components are only initialized when needed. When a `NeuralNet` is instantiated, arguments are stored but not immediately used.

The initialization sequence is:

```mermaid
sequenceDiagram
    participant User
    participant NeuralNet
    participant Module
    participant Criterion
    participant Optimizer
    participant Callbacks
    
    User->>NeuralNet: __init__(module, criterion, ...)
    Note over NeuralNet: Components not initialized yet
    
    User->>NeuralNet: initialize() or fit()
    activate NeuralNet
    
    NeuralNet->>NeuralNet: _initialize_virtual_params()
    NeuralNet->>NeuralNet: _initialize_callbacks()
    NeuralNet->>NeuralNet: _initialize_module()
    NeuralNet->>Module: Instantiate with module__* params
    NeuralNet->>NeuralNet: _initialize_criterion()
    NeuralNet->>Criterion: Instantiate with criterion__* params
    NeuralNet->>NeuralNet: _initialize_optimizer()
    NeuralNet->>Optimizer: Instantiate with optimizer__* params
    NeuralNet->>NeuralNet: _initialize_history()
    NeuralNet->>Callbacks: initialize()
    
    NeuralNet-->>User: initialized model
    deactivate NeuralNet
```

Sources: [skorch/net.py:929-943](), [docs/user/neuralnet.rst:42-60]()

### Parameter Handling

skorch uses a special parameter naming convention with double underscores to set parameters on subcomponents:

```
module__num_units=100      # Sets num_units=100 on module initialization
criterion__weight=weights  # Sets weight=weights on criterion initialization
optimizer__momentum=0.9    # Sets momentum=0.9 on optimizer initialization
```

This allows convenient configuration of all components from the top-level `NeuralNet` instance.

Sources: [skorch/net.py:63-87](), [docs/user/neuralnet.rst:499-526]()

### Component Management

skorch manages several key components:

1. **module_**: The instantiated PyTorch module that defines the neural network architecture.
2. **criterion_**: The loss function used during training.
3. **optimizer_**: The optimization algorithm that updates model parameters.
4. **history_**: Tracks metrics during training.
5. **callbacks_**: Custom callback objects for modifying the training process.

Components are initialized when needed, and each has a dedicated initialization method:

| Component | Initialization Method | Description |
|-----------|------------------------|-------------|
| Module | `initialize_module()` | Instantiates the PyTorch module |
| Criterion | `initialize_criterion()` | Instantiates the loss function |
| Optimizer | `initialize_optimizer()` | Instantiates the optimizer |
| History | `initialize_history()` | Creates a new History object |
| Callbacks | `initialize_callbacks()` | Sets up all callbacks |

Sources: [skorch/net.py:605-682](), [docs/user/neuralnet.rst:69-119]()

## Training and Inference Flow

The training process in skorch follows a fixed pattern, with callbacks serving as customization points at each step:

```mermaid
flowchart TD
    Start["Start Training"] --> OnTrainBegin["on_train_begin Callbacks"]
    OnTrainBegin --> EpochLoop["For each epoch"]
    
    subgraph "Epoch Loop"
        EpochLoop --> OnEpochBegin["on_epoch_begin Callbacks"]
        OnEpochBegin --> BatchLoop["For each batch"]
        
        subgraph "Batch Loop"
            BatchLoop --> OnBatchBegin["on_batch_begin Callbacks"]
            OnBatchBegin --> ForwardPass["Forward Pass"]
            ForwardPass --> LossComputation["Loss Computation"]
            LossComputation --> BackwardPass["Backward Pass"]
            BackwardPass --> OnGradComputed["on_grad_computed Callbacks"]
            OnGradComputed --> OptimizerStep["Optimizer Step"]
            OptimizerStep --> OnBatchEnd["on_batch_end Callbacks"]
        end
        
        BatchLoop --> ValidationCheck["If validation split"]
        ValidationCheck --> ValidationEval["Compute Validation Metrics"]
        ValidationEval --> OnEpochEnd["on_epoch_end Callbacks"]
    end
    
    EpochLoop --> OnTrainEnd["on_train_end Callbacks"]
    OnTrainEnd --> End["End Training"]
```

Sources: [skorch/net.py:403-446](), [docs/user/callbacks.rst:40-89]()

### Inference Flow

During inference (prediction), the data follows a similar flow but skips the training-specific components:

```mermaid
flowchart LR
    Input["Input Data\n(NumPy, etc.)"] --> DataConversion["Convert to PyTorch tensors"]
    DataConversion --> DeviceTransfer["Transfer to device (CPU/GPU)"]
    DeviceTransfer --> ForwardPass["Module Forward Pass"]
    ForwardPass --> Nonlinearity["Apply predict_nonlinearity\n(if configured)"]
    Nonlinearity --> OutputConversion["Convert to NumPy arrays"]
    OutputConversion --> Output["Output Predictions"]
```

Sources: [skorch/net.py:334-356](), [docs/user/neuralnet.rst:359-388]()

## Callback System

The callback system is a key architectural feature that provides customization points throughout the training process:

```mermaid
classDiagram
    class Callback {
        +initialize()
        +on_train_begin(net, X, y)
        +on_train_end(net, X, y)
        +on_epoch_begin(net, dataset_train, dataset_valid)
        +on_epoch_end(net, dataset_train, dataset_valid)
        +on_batch_begin(net, batch, training)
        +on_batch_end(net, batch, training, loss, y_pred)
        +on_grad_computed(net, named_parameters, X, y)
    }
    
    class EpochTimer {
        +on_epoch_begin()
        +on_epoch_end()
    }
    
    class PrintLog {
        +on_epoch_end()
    }
    
    class PassthroughScoring {
        +on_batch_end()
        +on_epoch_end()
    }
    
    class EarlyStopping {
        +on_epoch_end()
    }
    
    Callback <|-- EpochTimer
    Callback <|-- PrintLog
    Callback <|-- PassthroughScoring
    Callback <|-- EarlyStopping
```

skorch provides default callbacks and allows custom callbacks to be added. The default callbacks include:
- `EpochTimer`: Times each epoch
- `PrintLog`: Prints training metrics
- `PassthroughScoring`: Records metrics during training

Sources: [skorch/net.py:386-398](), [docs/user/callbacks.rst:1-24]()

## Dataset Handling

skorch handles various input data types through its `Dataset` class:

```mermaid
flowchart TD
    subgraph "Input Data Types"
        NumpyArray["NumPy arrays"]
        PyTorchTensor["PyTorch tensors"]
        SciPySparse["SciPy sparse matrices"]
        PandasDF["Pandas DataFrames/Series"]
        Dictionary["Dictionaries"]
        PyTorchDataset["PyTorch Datasets"]
    end
    
    subgraph "skorch Dataset Layer"
        Dataset["skorch.dataset.Dataset"]
        ValidSplit["skorch.dataset.ValidSplit"]
    end
    
    subgraph "PyTorch Data Layer"
        DataLoader["torch.utils.data.DataLoader"]
    end
    
    NumpyArray --> Dataset
    PyTorchTensor --> Dataset
    SciPySparse --> Dataset
    PandasDF --> Dataset
    Dictionary --> Dataset
    PyTorchDataset --> NeuralNet
    
    Dataset --> ValidSplit
    ValidSplit --> TrainSet["Training Dataset"]
    ValidSplit --> ValidSet["Validation Dataset"]
    
    TrainSet --> DataLoader
    ValidSet --> DataLoader
```

The dataset system handles:
- Converting various input types to a format PyTorch can use
- Splitting data into training and validation sets
- Providing a consistent interface for different data types
- Supporting dictionary inputs to match module parameter names

Sources: [docs/user/dataset.rst:1-147](), [skorch/net.py:131-147]()

## Summary

skorch's core architecture provides a clean integration between PyTorch and scikit-learn. The `NeuralNet` class wraps PyTorch modules, the callback system enables customization, and the dataset handling makes working with different data formats seamless.

The architecture is designed to be flexible and extensible while hiding the complexity of boilerplate code, allowing users to focus on model development.

---

