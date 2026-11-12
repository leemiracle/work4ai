<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/clrs · page 2 Baseline Models · fetched 2026-10-26 -->

# Baseline Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [clrs/_src/baselines.py](clrs/_src/baselines.py)
- [clrs/_src/baselines_test.py](clrs/_src/baselines_test.py)
- [clrs/models.py](clrs/models.py)

</details>



This document describes the implementation and functionality of the baseline neural network models in the CLRS (Cormen, Leiserson, Rivest, and Stein) algorithmic reasoning benchmark. These models serve as reference implementations for learning to execute algorithms through neural networks. For information about specific neural architectures used within these models, see [Neural Network Architecture](#2.1).

## Overview

The CLRS baseline models implement message-passing neural networks designed to learn algorithm execution through graph-based representations. There are two primary model variants:

1. **BaselineModel**: The standard implementation for both training and evaluation
2. **BaselineModelChunked**: A variant that processes data in fixed-time chunks, optimized for training longer sequences

Both models follow a similar architecture with encoders, a processor, and decoders, but differ in how they handle sequential data and state management.

Sources: [clrs/_src/baselines.py:136-455](), [clrs/_src/baselines.py:507-687](), [clrs/models.py:1-32]()

## Model Architecture

### BaselineModel

The BaselineModel consists of three main components:

```mermaid
flowchart TD
    subgraph "BaselineModel"
        Encoders["Encoders"] --> |"Hidden states"| Processor["Message-Passing Processor"]
        Processor --> |"Updated hidden states"| OptionalLSTM["Optional LSTM"]
        OptionalLSTM --> Decoders["Decoders"]
        Processor --> |"If LSTM disabled"| Decoders
        
        Decoders --> Outputs["Algorithm Outputs"]
        Decoders --> Hints["Hint Predictions"]
        
        Hints --> |"Teacher forcing"| Encoders
    end
    
    AlgorithmInputs["Algorithm Inputs"] --> Encoders
    GroundTruths["Ground Truth"] --> |"Loss computation"| LossFunction["Loss Function"]
    Outputs --> LossFunction
    Hints --> LossFunction
```

This architecture enables the model to:
1. Encode node, edge, and graph features
2. Process these features using message passing
3. Decode the processed features into algorithm outputs and intermediate state predictions (hints)
4. Optionally feed predicted hints back as inputs (with teacher forcing)

Sources: [clrs/_src/baselines.py:139-206](), [clrs/_src/baselines.py:251-269]()

### Component Relationships

```mermaid
classDiagram
    class BaselineModel {
        +_spec: Spec or List[Spec]
        +decode_hints: bool
        +nb_msg_passing_steps: int
        +init(features, seed)
        +feedback(rng_key, feedback, algorithm_index): loss
        +predict(rng_key, features, algorithm_index)
        +compute_grad(rng_key, feedback)
        -_loss(params, rng_key, feedback, algorithm_index)
        -_update_params(params, grads, opt_state)
    }
    
    class BaselineModelChunked {
        +mp_states: List[List[MessagePassingStateChunked]]
        +init_mp_states: List[List[MessagePassingStateChunked]]
        +init(features, seed)
        +feedback(rng_key, feedback, algorithm_index): loss
        -_loss(params, rng_key, feedback, mp_state, algorithm_index)
    }
    
    class Net {
        +__call__(features, repred, algorithm_index)
    }
    
    class NetChunked {
        +__call__(features, mp_states, repred, algorithm_index)
    }
    
    class Processor {
        <<interface>>
        +__call__(hidden, adj_mat)
    }
    
    class PGN {
        +__call__(hidden, adj_mat)
    }
    
    class MPNN {
        +__call__(hidden, adj_mat)
    }
    
    class GAT {
        +__call__(hidden, adj_mat)
    }
    
    BaselineModel *-- Net : uses
    BaselineModelChunked *-- NetChunked : uses
    BaselineModelChunked --|> BaselineModel : extends
    Net ..> Processor : requires
    NetChunked ..> Processor : requires
    PGN ..|> Processor : implements
    MPNN ..|> Processor : implements
    GAT ..|> Processor : implements
```

Sources: [clrs/_src/baselines.py:136-455](), [clrs/_src/baselines.py:507-687](), [clrs/models.py:16-32]()

## Key Features

### Initialization and Configuration

The BaselineModel constructor takes several parameters that determine the model's behavior:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `spec` | Algorithm specification(s) | (required) |
| `dummy_trajectory` | Sample feedback for initialization | (required) |
| `processor_factory` | Factory for creating the message-passing processor | (required) |
| `hidden_dim` | Size of hidden message-passing vectors | 32 |
| `encode_hints` | Whether to use hints as inputs | False |
| `decode_hints` | Whether to predict hints as outputs | True |
| `use_lstm` | Whether to add an LSTM after message passing | False |
| `hint_teacher_forcing` | Probability of using ground truth hints as inputs | 0.0 |
| `hint_repred_mode` | How to process predicted hints (`soft`, `hard`, `hard_on_eval`) | `soft` |
| `nb_msg_passing_steps` | Number of message passing steps per hint | 1 |

Sources: [clrs/_src/baselines.py:139-206]()

### Training and Inference

The BaselineModel implements several core methods:

1. **`init(features, seed)`**: Initializes model parameters
2. **`feedback(rng_key, feedback, algorithm_index)`**: Performs a training step
3. **`predict(rng_key, features, algorithm_index)`**: Runs inference
4. **`compute_grad(rng_key, feedback, algorithm_index)`**: Computes gradients without updating parameters

The training flow involves:
1. Encoding the input features
2. Processing via the message-passing neural network
3. Decoding to produce outputs and hints
4. Computing losses against ground truth
5. Updating parameters via gradient descent

Sources: [clrs/_src/baselines.py:281-391](), [clrs/_src/baselines.py:406-442]()

## Multi-Algorithm Support

One significant capability of the BaselineModel is supporting multiple algorithms with a shared processor:

```mermaid
flowchart TD
    subgraph "Multi-Algorithm BaselineModel"
        Processor["Shared Message-Passing Processor"]
        
        subgraph "Algorithm 1"
            Encoders1["Encoders_1"] --> Processor
            Processor --> Decoders1["Decoders_1"]
            Decoders1 --> Outputs1["Outputs_1"]
        end
        
        subgraph "Algorithm 2"
            Encoders2["Encoders_2"] --> Processor
            Processor --> Decoders2["Decoders_2"]
            Decoders2 --> Outputs2["Outputs_2"]
        end
        
        subgraph "Algorithm N"
            EncodersN["Encoders_N"] --> Processor
            Processor --> DecodersN["Decoders_N"]
            DecodersN --> OutputsN["Outputs_N"]
        end
    end
```

Key points:
- The processor parameters are shared across all algorithms
- Each algorithm has its own dedicated encoders and decoders
- During training, only the relevant algorithm's encoders and decoders are updated
- The processor is updated regardless of which algorithm is being trained
- An optional `freeze_processor` parameter allows keeping the processor fixed while training algorithm-specific encoders/decoders

Sources: [clrs/_src/baselines.py:161-166](), [clrs/_src/baselines.py:443-456](), [clrs/_src/baselines_test.py:158-227]()

## Chunked Model for Processing Long Sequences

The BaselineModelChunked extends BaselineModel to process data in fixed-time chunks:

```mermaid
flowchart TD
    subgraph "BaselineModelChunked"
        direction LR
        ChunkedData["Chunked Input\n(time × batch × ...)"] --> MPState["Message Passing State"]
        MPState --> NetChunked["NetChunked"]
        NetChunked --> UpdatedMPState["Updated MP State"]
        NetChunked --> Outputs["Outputs"]
        UpdatedMPState --> |"Next chunk"| NetChunked
    end
```

Key differences from BaselineModel:
- Processes fixed-time chunks rather than full sequences
- Maintains message passing state between chunks
- Uses tensors with dimensions: `chunk_length × batch_size × ...`
- Signal for new samples via an `is_first` tensor (`chunk_length × batch_size`)
- Optimized for training but not for validation/testing

The chunked model enables training on longer sequences that might not fit in memory when processed in full.

Sources: [clrs/_src/baselines.py:507-517](), [clrs/_src/baselines.py:523-548](), [clrs/_src/baselines_test.py:89-156]()

## Loss Computation and Optimization

Both models calculate loss based on:
1. Output loss: Comparing model predictions to ground truth algorithm outputs
2. Hint loss: Comparing intermediate step predictions to the ground truth algorithm state (if `decode_hints=True`)

```mermaid
flowchart TD
    subgraph "Loss Computation"
        Outputs["Model Outputs"] --> OutputLoss["Output Loss"]
        Hints["Hint Predictions"] --> HintLoss["Hint Loss"]
        OutputLoss --> TotalLoss["Total Loss"]
        HintLoss --> TotalLoss
        
        GroundTruthOutputs["Ground Truth Outputs"] --> OutputLoss
        GroundTruthHints["Ground Truth Hints"] --> HintLoss
    end
    
    TotalLoss --> GradientComputation["Gradient Computation"]
    GradientComputation --> ParameterUpdate["Parameter Update"]
```

The optimization process includes:
- Support for gradient clipping via `grad_clip_max_norm`
- Selective parameter updates based on algorithm index
- Option to freeze processor weights while updating encoders/decoders

Sources: [clrs/_src/baselines.py:406-442](), [clrs/_src/baselines.py:582-619](), [clrs/_src/baselines.py:443-456]()

## Distributed Processing Support

Both models include support for multi-device computation using JAX:

- Functions for reshaping data across devices
- pmapping computations across multiple devices
- Handling device-specific parameters and optimization state
- Utility functions for restacking results from parallel computations

This enables efficient scaling of training and inference across multiple accelerators.

Sources: [clrs/_src/baselines.py:57-133](), [clrs/_src/baselines.py:364-369]()

## Checkpoint Management

The models provide methods for saving and loading parameters:

- `save_model(file_name)`: Saves model parameters and optimizer state
- `restore_model(file_name, only_load_processor)`: Restores model parameters with option to only load processor weights

This enables model persistence and transfer learning between different algorithm sets.

Sources: [clrs/_src/baselines.py:486-504]()

---

