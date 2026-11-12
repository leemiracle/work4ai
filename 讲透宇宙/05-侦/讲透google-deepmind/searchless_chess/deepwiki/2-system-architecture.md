<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/searchless_chess · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/config.py](src/config.py)
- [src/constants.py](src/constants.py)

</details>



## Purpose and Scope

This document provides a high-level overview of the SearchLess Chess system architecture, explaining how different components interact to enable transformer-based chess playing without traditional search algorithms. It covers the major subsystems, data flows, and component dependencies.

For details about specific components, please refer to their dedicated pages:
- [Training System](#3)
- [Data Management](#4)
- [Chess Engines](#5)
- [Evaluation System](#6)

## System Overview

The SearchLess Chess system is composed of several interconnected components that work together to train, evaluate, and deploy transformer-based chess engines.

### High-Level Component Diagram

```mermaid
graph TD
    subgraph "Data Subsystem"
        DataFiles["Data Files (.bag)"]
        DataLoader["Data Loader"]
    end
    
    subgraph "Training Subsystem"
        TrainLoop["Training Loop"]
        TransformerModels["Transformer Models"]
        Checkpoints["Model Checkpoints"]
    end
    
    subgraph "Engine Subsystem"
        NeuralEngines["Neural Engines"]
        StockfishEngine["Stockfish Engine"]
        Lc0Engine["Leela Chess Zero Engine"]
    end
    
    subgraph "Evaluation Subsystem"
        MetricsEval["Metrics Evaluation"]
        PuzzleEval["Puzzle Evaluation"]
        TournamentEval["Tournament System"]
    end
    
    DataFiles --> DataLoader
    DataLoader --> TrainLoop
    TrainLoop --> TransformerModels
    TransformerModels --> Checkpoints
    Checkpoints --> NeuralEngines
    
    NeuralEngines --> MetricsEval
    StockfishEngine --> MetricsEval
    Lc0Engine --> MetricsEval
    
    NeuralEngines --> PuzzleEval
    StockfishEngine --> PuzzleEval
    Lc0Engine --> PuzzleEval
    
    NeuralEngines --> TournamentEval
    StockfishEngine --> TournamentEval
    Lc0Engine --> TournamentEval
```

Sources: [README.md:19-66]()

## Data Flow Architecture

The SearchLess Chess system processes data through several stages, from raw chess positions to trained models and evaluation results.

```mermaid
flowchart LR
    subgraph "Data Sources"
        ChessBench["ChessBench Dataset"]
    end
    
    subgraph "Data Processing"
        BagzReader["Bagz Reader"]
        Tokenizer["Chess Board Tokenizer"]
    end
    
    subgraph "Training Pipeline"
        DataLoader["Data Loader"]
        TrainingLoop["Training Loop"]
        ModelParameters["Model Parameters"]
    end
    
    subgraph "Model Storage"
        Checkpoints["Checkpoints"]
    end
    
    subgraph "Inference"
        NeuralEngines["Neural Engines"]
    end
    
    subgraph "Evaluation"
        PuzzleSolver["Puzzle Solver"]
        Tournament["Tournament System"]
        MetricsEvaluator["Metrics Evaluator"]
    end
    
    ChessBench --> BagzReader
    BagzReader --> DataLoader
    DataLoader --> Tokenizer
    Tokenizer --> TrainingLoop
    TrainingLoop --> ModelParameters
    ModelParameters --> Checkpoints
    Checkpoints --> NeuralEngines
    NeuralEngines --> PuzzleSolver
    NeuralEngines --> Tournament
    NeuralEngines --> MetricsEvaluator
```

Sources: [src/bagz.py](), [src/data_loader.py](), [src/tokenizer.py](), [src/training.py](), [README.md:180-241]()

## Component Dependencies

The system relies on several external libraries and frameworks for its core functionality:

```mermaid
flowchart TB
    subgraph "External Libraries"
        JAX["JAX"]
        Optax["Optax"]
        Haiku["dm-haiku"]
        PyGrain["PyGrain"]
        OrbaxCP["Orbax Checkpoint"]
        ChessLib["Chess Library"]
        BayesElo["BayesElo"]
    end
    
    subgraph "Core Components"
        TrainingSystem["Training System"]
        DataSystem["Data System"]
        Checkpointing["Checkpointing System"]
        EngineSystem["Engine System"]
        EvaluationSystem["Evaluation System"]
    end
    
    JAX --> TrainingSystem
    Optax --> TrainingSystem
    Haiku --> TrainingSystem
    PyGrain --> DataSystem
    OrbaxCP --> Checkpointing
    ChessLib --> EngineSystem
    BayesElo --> EvaluationSystem
    
    DataSystem --> TrainingSystem
    Checkpointing --> TrainingSystem
    TrainingSystem --> EngineSystem
    EngineSystem --> EvaluationSystem
```

Sources: [README.md:68-146]()

## Key Interfaces

The system defines several important interfaces to enable modular design and interoperability between components.

### Engine Interface

```mermaid
classDiagram
    class Engine {
        <<Interface>>
        +analyse(board: chess.Board) -> AnalysisResult
        +play(board: chess.Board) -> chess.Move
    }
    
    class StockfishEngine {
        -_raw_engine: SimpleEngine
        -_limit: chess.engine.Limit
        +analyse(board)
        +play(board)
    }
    
    class Lc0Engine {
        -_raw_engine: SimpleEngine
        -_limit: chess.engine.Limit
        +analyse(board)
        +play(board)
    }
    
    class NeuralEngine {
        -predict_fn
        -temperature
        +analyse(board)
        +play(board)
    }
    
    class ActionValueEngine
    class StateValueEngine
    class BCEngine
    
    Engine <|.. StockfishEngine
    Engine <|.. Lc0Engine
    Engine <|.. NeuralEngine
    
    NeuralEngine <|-- ActionValueEngine
    NeuralEngine <|-- StateValueEngine
    NeuralEngine <|-- BCEngine
```

Sources: [src/engines/engine.py](), [src/engines/neural_engines.py](), [src/engines/stockfish_engine.py](), [src/engines/lc0_engine.py]()

### Data and Configuration Interfaces

The system uses structured configurations to define data loading and training parameters:

```mermaid
classDiagram
    class DataConfig {
        +batch_size: int
        +shuffle: bool
        +seed: int|None
        +drop_remainder: bool
        +worker_count: int|None
        +num_return_buckets: int
        +split: Literal['train', 'test']
        +policy: PolicyType
        +num_records: int|None
    }
    
    class TrainConfig {
        +data: DataConfig
        +learning_rate: float
        +max_grad_norm: float
        +num_steps: int
        +ckpt_frequency: int|None
        +ckpt_max_to_keep: int|None
        +save_frequency: int|None
        +log_frequency: int|None
    }
    
    class EvalConfig {
        +data: DataConfig
        +num_eval_data: int|None
        +use_ema_params: bool
        +policy: PolicyType
        +num_return_buckets: int
        +batch_size: int|None
    }
    
    class DataLoaderBuilder {
        <<Protocol>>
        +__call__(config: DataConfig) -> pygrain.DataLoader
    }
    
    class Evaluator {
        <<Abstract>>
        +step(params: hk.Params, step: int) -> Mapping[str, Any]
    }
    
    TrainConfig *-- DataConfig
    EvalConfig *-- DataConfig
```

Sources: [src/config.py:16-91](), [src/constants.py:54-82]()

## Data Representation

The system uses different data types to represent chess positions and related information:

| Data Type | Structure | Purpose |
|-----------|-----------|---------|
| `ActionValueData` | `(fen: str, move: str, win_prob: float)` | Stores a position, move, and win probability |
| `StateValueData` | `(fen: str, win_prob: float)` | Stores a position and its value |
| `BehavioralCloningData` | `(fen: str, move: str)` | Stores a position and expert move |
| `Sequences` | `UInt32[Array, 'B T']` | Tokenized board representations |
| `Predictions` | `Float32[Array, '*B']` or `Float32[Array, '*B T F']` | Model predictions |

Sources: [src/constants.py:30-119]()

## System Workflow

1. **Data Preparation**: The ChessBench dataset is processed into `.bag` files for efficient loading during training
2. **Model Training**: Transformer models of various sizes (9M, 136M, 270M parameters) are trained on the processed data
3. **Model Checkpointing**: Trained models are saved as checkpoints for later use
4. **Engine Creation**: Neural engines are created using the trained models, implementing the common Engine interface
5. **Evaluation**: The neural engines are evaluated against traditional engines (Stockfish, Leela Chess Zero) through puzzle accuracy, tournament play, and metrics computation

Sources: [README.md:180-241]()

## Directory Structure

The repository is organized as follows:

```
.
|
├── BayesElo                        - Elo computation (need to be installed)
|
├── checkpoints                     - Model checkpoints (need to be downloaded)
|   ├── 136M
|   ├── 270M
|   └── 9M
|
├── data                            - Datasets (need to be downloaded)
|   ├── eco_openings.csv
|   ├── test
|   ├── train
|   └── puzzles.csv
|
├── lc0                             - Leela Chess Zero (needs to be installed)
|
├── src
|   ├── engines
|   |   ├── constants.py            - Engine constants
|   |   ├── engine.py               - Engine interface
|   |   ├── lc0_engine.py           - Leela Chess Zero engine
|   |   ├── neural_engines.py       - Neural engines
|   |   └── stockfish_engine.py     - Stockfish engine
|   |
|   ├── bagz.py                     - Readers for our .bag data files
|   ├── config.py                   - Experiment configurations
|   ├── constants.py                - Constants, interfaces, and types
|   ├── data_loader.py              - Data loader
|   ├── metrics_evaluator.py        - Metrics (e.g., Kendall's tau) evaluator
|   ├── puzzles.py                  - Puzzle evaluation script
|   ├── searchless_chess.ipynb      - Model analysis notebook
|   ├── tokenizer.py                - Chess board tokenization
|   ├── tournament.py               - Elo tournament script
|   ├── train.py                    - Example training + evaluation script
|   ├── training.py                 - Training loop
|   ├── training_utils.py           - Training utility functions
|   ├── transformer.py              - Decoder-only Transformer
|   └── utils.py                    - Utility functions
|
├── Stockfish                       - Stockfish (needs to be installed)
```

Sources: [README.md:19-66]()

---

