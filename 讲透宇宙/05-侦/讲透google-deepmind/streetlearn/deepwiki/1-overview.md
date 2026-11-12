<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/streetlearn · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

StreetLearn is a navigation learning platform that enables training AI agents in real-world photographic street environments using Google Street View data. This system provides a C++ engine for high-performance panorama processing and a Python environment interface for implementing navigation games and training agents.

This document covers the high-level architecture and core components of StreetLearn. For detailed information about specific subsystems, see [System Architecture](#2), [Environment System](#3), [Agent System](#4), and [Training and Experimentation](#5).

Sources: [README.md:1-425]()

## System Architecture Overview

StreetLearn follows a layered architecture with clear separation between the high-performance C++ engine and the flexible Python environment layer.

```mermaid
graph TB
    subgraph "Data Storage Layer"
        GSV["Google Street View Dataset"]
        LevelDB[("LevelDB Storage")]
        ProtoFiles["streetlearn/proto<br/>Protocol Buffers"]
    end
    
    subgraph "C++ Engine Layer (streetlearn/engine)"
        StreetLearnEngine["StreetLearnEngine"]
        NodeCache["NodeCache<br/>(LRU Panorama Cache)"]
        PanoGraph["PanoGraph<br/>(Navigation Structure)"]
        GraphRenderer["GraphRenderer<br/>(Visualization)"]
    end
    
    subgraph "Python Bindings"
        CLIF["CLIF Bindings<br/>(C++/Python Interface)"]
    end
    
    subgraph "Python Environment Layer (streetlearn/python/environment)"
        StreetLearnEnv["StreetLearn Environment"]
        DefaultConfig["default_config.py<br/>DEFAULT_CONFIG"]
        GameRegistry["NAME_TO_GAME<br/>(Game Factory)"]
    end
    
    subgraph "Game Implementations"
        CoinGame["coin_game.py"]
        CourierGame["courier_game.py"] 
        InstructionGames["*instruction_game.py"]
    end
    
    subgraph "Agent Layer (streetlearn/python/ui)"
        HumanAgent["human_agent.py"]
        OracleAgent["oracle_agent.py"]
        LearningAgents["AI Learning Agents"]
    end
    
    GSV --> LevelDB
    ProtoFiles --> StreetLearnEngine
    LevelDB --> StreetLearnEngine
    StreetLearnEngine --> NodeCache
    StreetLearnEngine --> PanoGraph
    StreetLearnEngine --> GraphRenderer
    
    StreetLearnEngine --> CLIF
    CLIF --> StreetLearnEnv
    DefaultConfig --> StreetLearnEnv
    GameRegistry --> StreetLearnEnv
    
    StreetLearnEnv --> CoinGame
    StreetLearnEnv --> CourierGame
    StreetLearnEnv --> InstructionGames
    
    CoinGame --> HumanAgent
    CourierGame --> OracleAgent
    InstructionGames --> LearningAgents
```

The system processes Google Street View panoramas through a multi-layered caching and rendering pipeline, exposing navigation functionality through Python interfaces that support various game types and agent implementations.

Sources: [README.md:32-62]()

## Core Components

### C++ Engine (`streetlearn/engine`)

The `StreetLearnEngine` provides high-performance panorama processing with the following key capabilities:

| Component | Function | Description |
|-----------|----------|-------------|
| `StreetLearnEngine` | Core engine | Loads, caches, and serves Street View panoramas |
| `NodeCache` | Caching | LRU cache for panorama data |
| `PanoGraph` | Navigation | Street graph structure for movement |
| `GraphRenderer` | Visualization | Renders top-down graph images |

The engine projects panoramas from equirectangular representation to first-person view at specified yaw, pitch, and field of view parameters.

Sources: [README.md:36-41]()

### Python Environment (`streetlearn/python/environment`)

The Python layer provides OpenAI Gym-compatible interfaces through:

- `StreetLearn` environment class with `step(action)` and `reset()` methods
- `BatchedStreetLearn` for multi-environment parallelization  
- Game factory system using `NAME_TO_GAME` registry
- Configuration management through `DEFAULT_CONFIG`

Sources: [README.md:45-51](), [README.md:259-264]()

### Protocol Buffers (`streetlearn/proto`)

Message definitions for storing panorama metadata and street graph structure, enabling efficient serialization and cross-language compatibility.

Sources: [README.md:42-44]()

## Data Flow Architecture

```mermaid
graph TD
    subgraph "Input Data"
        StreetViewAPI["Google Street View API"]
        Datasets["StreetLearn Datasets<br/>(manhattan, pittsburgh)"]
    end
    
    subgraph "Storage & Serialization"
        LevelDBStorage[("LevelDB<br/>Key-Value Store")]
        ProtocolBuffers["Protocol Buffers<br/>Pano Messages"]
    end
    
    subgraph "Engine Processing (streetlearn/engine)"
        PanoFetcher["Panorama Fetcher<br/>(Async Loading)"]
        NodeCacheSystem["NodeCache<br/>(max_cache_size)"]
        PanoGraphSystem["PanoGraph<br/>(Navigation Graph)"]
        GraphRenderSystem["GraphRenderer<br/>(Image Generation)"]
        PanoProjection["Panorama Projection<br/>(Equirectangular to FOV)"]
    end
    
    subgraph "Environment Interface"
        ObservationDict["Observation Dictionary"]
        ViewImage["view_image<br/>(RGB panorama)"]
        GraphImage["graph_image<br/>(Top-down map)"]
        Metadata["metadata<br/>(Pano protocol buffer)"]
        LatLng["latlng<br/>(GPS coordinates)"]
    end
    
    StreetViewAPI --> Datasets
    Datasets --> LevelDBStorage
    Datasets --> ProtocolBuffers
    
    LevelDBStorage --> PanoFetcher
    ProtocolBuffers --> PanoFetcher
    PanoFetcher --> NodeCacheSystem
    NodeCacheSystem --> PanoGraphSystem
    PanoGraphSystem --> GraphRenderSystem
    PanoGraphSystem --> PanoProjection
    
    PanoProjection --> ViewImage
    GraphRenderSystem --> GraphImage
    PanoGraphSystem --> Metadata
    PanoGraphSystem --> LatLng
    
    ViewImage --> ObservationDict
    GraphImage --> ObservationDict
    Metadata --> ObservationDict
    LatLng --> ObservationDict
```

The data flows from raw Street View panoramas through caching and processing layers to produce rich observations for agent training. The `NodeCache` uses LRU eviction with configurable `max_cache_size`, while the `PanoGraph` maintains navigation connectivity.

Sources: [README.md:268-383]()

## Environment Configuration and Games

### Configuration System

Environment settings are managed through `streetlearn/python/default_config.py` with key parameters:

| Parameter Category | Key Settings | Purpose |
|-------------------|--------------|---------|
| Visual | `width`, `height`, `field_of_view` | Panorama rendering |
| Graph | `min_graph_depth`, `max_graph_depth` | BFS exploration bounds |
| Caching | `max_cache_size` | Memory management |
| Games | `game_name`, `action_spec` | Game selection and controls |

Sources: [README.md:266-343]()

### Game Factory System

Games are registered in the `NAME_TO_GAME` dictionary and instantiated dynamically:

```mermaid
graph LR
    subgraph "Game Selection"
        GameName["game_name config"]
        NameToGame["NAME_TO_GAME<br/>Registry"]
    end
    
    subgraph "Available Games"
        CoinGameClass["coin_game.py<br/>CoinGame"]
        CourierGameClass["courier_game.py<br/>CourierGame"]
        CurriculumCourierClass["curriculum_courier_game.py"]
        GoalInstructionClass["goal_instruction_game.py"]
        IncrementalInstructionClass["incremental_instruction_game.py"]
        StepByStepClass["step_by_step_instruction_game.py"]
    end
    
    subgraph "Game Features"
        RewardSystem["Reward Calculation"]
        ObservationGen["Observation Generation"]
        ActionHandling["Action Processing"]
    end
    
    GameName --> NameToGame
    NameToGame --> CoinGameClass
    NameToGame --> CourierGameClass
    NameToGame --> CurriculumCourierClass
    NameToGame --> GoalInstructionClass
    NameToGame --> IncrementalInstructionClass
    NameToGame --> StepByStepClass
    
    CoinGameClass --> RewardSystem
    CourierGameClass --> ObservationGen
    GoalInstructionClass --> ActionHandling
```

Each game implements specific reward structures and observation types, from simple coin collection to complex instruction-following navigation tasks.

Sources: [README.md:384-416]()

## Agent and Interface Architecture

StreetLearn supports multiple agent types through the UI system in `streetlearn/python/ui`:

| Agent Type | Implementation | Purpose |
|------------|----------------|---------|
| `human_agent.py` | Interactive control | Manual navigation and testing |
| `oracle_agent.py` | Ground truth navigation | Performance baselines |
| `batched_oracle_agent.py` | Parallel oracle processing | Batch evaluation |
| AI Learning Agents | Neural network-based | Reinforcement learning training |

The system uses PyGame for visualization, displaying both `view_image` (first-person view) and `graph_image` (top-down map) with navigation indicators and status information.

Sources: [README.md:52-62](), [README.md:173-216]()

---

