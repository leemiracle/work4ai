<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/streetlearn · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [WORKSPACE](WORKSPACE)
- [streetlearn/python/environment/game.py](streetlearn/python/environment/game.py)
- [streetlearn/python/environment/observations.py](streetlearn/python/environment/observations.py)
- [streetlearn/python/environment/streetlearn.py](streetlearn/python/environment/streetlearn.py)

</details>



## Purpose and Scope

This document explains the overall architecture of StreetLearn, a navigation learning platform that enables training AI agents in real-world photographic street environments using Google Street View data. It covers the multi-layer system design, component interactions, and data flow patterns across the C++ engine core, Python environment layer, and agent interfaces.

For information about specific environment games and observation types, see [Environment System](#3). For details on agent implementations and training, see [Agent System](#4) and [Training and Experimentation](#5).

## Architecture Overview

StreetLearn follows a layered architecture that separates high-performance computation (C++) from flexible environment logic (Python), connected through CLIF bindings.

### System Layers

```mermaid
graph TB
    subgraph "Data_Layer" ["Data Layer"]
        GSV["Google Street View<br/>Dataset"]
        Proto["Protocol Buffers<br/>streetlearn/proto"]
        LevelDB_Storage["LevelDB Storage"]
    end
    
    subgraph "Cpp_Engine" ["C++ Engine Layer"]
        StreetLearnEngine["StreetLearnEngine<br/>streetlearn/engine"]
        NodeCache["NodeCache"]
        GraphRenderer["GraphRenderer"] 
        PanoGraph["PanoGraph"]
    end
    
    subgraph "Python_Env" ["Python Environment Layer"]
        StreetLearn_Class["StreetLearn<br/>streetlearn.py"]
        Game_Classes["Game Classes<br/>game.py"]
        Observations_System["Observation System<br/>observations.py"]
        Config_System["DEFAULT_CONFIG<br/>default_config.py"]
    end
    
    subgraph "Agent_Layer" ["Agent Layer"]
        AI_Agents["AI Learning Agents<br/>goal_nav_agent, plain_agent"]
        Oracle_Agents["Oracle Agents<br/>oracle_agent"]
        Human_Agents["Interactive Agents<br/>human_agent"]
    end
    
    subgraph "Interface_Layer" ["Interface Layer"]
        CLIF_Bindings["CLIF Bindings"]
        PyGame_UI["PyGame UI<br/>pygame"]
    end
    
    GSV --> StreetLearnEngine
    Proto --> StreetLearnEngine
    LevelDB_Storage --> StreetLearnEngine
    
    StreetLearnEngine --> NodeCache
    StreetLearnEngine --> GraphRenderer
    StreetLearnEngine --> PanoGraph
    
    StreetLearnEngine --> CLIF_Bindings
    CLIF_Bindings --> StreetLearn_Class
    Config_System --> StreetLearn_Class
    StreetLearn_Class --> Game_Classes
    StreetLearn_Class --> Observations_System
    
    Game_Classes --> AI_Agents
    Game_Classes --> Oracle_Agents
    StreetLearn_Class --> Human_Agents
    
    Human_Agents --> PyGame_UI
```

**Sources**: [README.md:32-63](), [streetlearn/python/environment/streetlearn.py:108-183]()

## Core Component Architecture

### Engine and Environment Interface

The C++ engine provides high-performance panorama processing and graph operations, while the Python environment handles game logic and agent interactions.

```mermaid
graph LR
    subgraph "CPP_Core" ["C++ Core Components"]
        StreetLearnEngine_Create["StreetLearnEngine::Create()"]
        RenderObservation["RenderObservation()"]
        DrawGraph["DrawGraph()"] 
        MoveToNextPano["MoveToNextPano()"]
        GetMetadata["GetMetadata()"]
        SetPosition["SetPosition()"]
    end
    
    subgraph "CLIF_Interface" ["CLIF Interface Layer"]
        streetlearn_engine["streetlearn_engine module"]
    end
    
    subgraph "Python_Environment" ["Python Environment"]
        StreetLearn_init["StreetLearn.__init__()"]
        step_method["step()"]
        reset_method["reset()"]
        observation_method["observation()"]
    end
    
    subgraph "Observation_Classes" ["Observation Classes"]
        ViewImage["ViewImage.observation"]
        GraphImage["GraphImage.observation"]
        Metadata_Obs["Metadata.observation"]
        LatLng["LatLng.observation"]
    end
    
    StreetLearnEngine_Create --> streetlearn_engine
    RenderObservation --> streetlearn_engine
    DrawGraph --> streetlearn_engine
    MoveToNextPano --> streetlearn_engine
    GetMetadata --> streetlearn_engine
    SetPosition --> streetlearn_engine
    
    streetlearn_engine --> StreetLearn_init
    streetlearn_engine --> step_method
    streetlearn_engine --> reset_method
    
    observation_method --> ViewImage
    observation_method --> GraphImage
    observation_method --> Metadata_Obs
    observation_method --> LatLng
    
    ViewImage --> RenderObservation
    GraphImage --> DrawGraph
    Metadata_Obs --> GetMetadata
    step_method --> MoveToNextPano
```

**Sources**: [streetlearn/python/environment/streetlearn.py:172-182](), [streetlearn/python/environment/observations.py:77-135]()

### Configuration and Game System

The environment uses a factory pattern with configuration-driven game instantiation and observation selection.

```mermaid
graph TB
    subgraph "Config_System" ["Configuration System"]
        DEFAULT_CONFIG["DEFAULT_CONFIG<br/>default_config.py"]
        ApplyDefaults["ApplyDefaults()"]
        NAME_TO_GAME["NAME_TO_GAME<br/>registry"]
    end
    
    subgraph "Environment_Init" ["Environment Initialization"]
        StreetLearn_constructor["StreetLearn.__init__()"]
        engine_create["engine.Create()"]
        observations_create["Observation.create()"]
    end
    
    subgraph "Game_Hierarchy" ["Game Class Hierarchy"]
        Game_base["Game (ABC)"]
        CoinGame["CoinGame"]
        CourierGame["CourierGame"] 
        InstructionGame["GoalInstructionGame"]
    end
    
    subgraph "Observation_Factory" ["Observation Factory"]
        Observation_create_method["Observation.create()"]
        observation_dispatch["dispatch dictionary"]
        ViewImage_class["ViewImage"]
        GraphImage_class["GraphImage"]
        Metadata_class["Metadata"]
    end
    
    DEFAULT_CONFIG --> ApplyDefaults
    ApplyDefaults --> StreetLearn_constructor
    NAME_TO_GAME --> StreetLearn_constructor
    
    StreetLearn_constructor --> engine_create
    StreetLearn_constructor --> observations_create
    
    Game_base --> CoinGame
    Game_base --> CourierGame
    Game_base --> InstructionGame
    
    observations_create --> Observation_create_method
    Observation_create_method --> observation_dispatch
    observation_dispatch --> ViewImage_class
    observation_dispatch --> GraphImage_class
    observation_dispatch --> Metadata_class
```

**Sources**: [streetlearn/python/environment/streetlearn.py:111-189](), [streetlearn/python/environment/observations.py:62-74](), [streetlearn/python/environment/game.py:40-107]()

## Data Flow and Caching Architecture

### Multi-Level Caching System

StreetLearn implements sophisticated caching to optimize Street View data access and rendering performance.

```mermaid
graph TD
    subgraph "Data_Sources" ["Data Sources"]
        StreetView_Dataset["Street View Dataset<br/>LevelDB files"]
        Proto_Metadata["Pano Metadata<br/>Protocol Buffers"]
    end
    
    subgraph "Engine_Caching" ["Engine Caching Layer"]
        NodeCache_size["NodeCache<br/>max_cache_size config"]
        GetMetadata_cache["GetMetadata() cache"]
        PanoFetcher["Panorama fetching"]
    end
    
    subgraph "Rendering_Pipeline" ["Rendering Pipeline"]
        RenderObservation_call["RenderObservation()"]
        DrawGraph_call["DrawGraph()"]
        graph_image_buffer["graph_image buffer"]
        view_image_buffer["view_image buffer"]
    end
    
    subgraph "Python_Observations" ["Python Observation Layer"]
        ViewImage_buffer["ViewImage._buffer"]
        GraphImage_buffer["GraphImage._buffer"]
        reshape_hwc["reshape_hwc()"]
        observation_dict["observation dictionary"]
    end
    
    StreetView_Dataset --> PanoFetcher
    Proto_Metadata --> GetMetadata_cache
    PanoFetcher --> NodeCache_size
    
    NodeCache_size --> RenderObservation_call
    GetMetadata_cache --> DrawGraph_call
    
    RenderObservation_call --> view_image_buffer
    DrawGraph_call --> graph_image_buffer
    
    view_image_buffer --> ViewImage_buffer
    graph_image_buffer --> GraphImage_buffer
    ViewImage_buffer --> reshape_hwc
    GraphImage_buffer --> reshape_hwc
    reshape_hwc --> observation_dict
```

**Sources**: [streetlearn/python/environment/streetlearn.py:172-183](), [streetlearn/python/environment/observations.py:87-134](), [streetlearn/python/environment/observations.py:30-43]()

### Action Processing and State Updates

The environment processes actions through a structured pipeline that updates agent state and triggers game logic.

```mermaid
graph LR
    subgraph "Action_Input" ["Action Input"]
        action_array["action: np.ndarray"]
        ACTION_SETS["ACTION_SETS dictionary"]
        get_action_set["get_action_set()"]
    end
    
    subgraph "Action_Processing" ["Action Processing"]
        step_method_call["step() method"]
        move_forward_calc["move_forward calculation"]
        rotation_calc["rotation calculations"]
        zoom_calc["map_zoom calculation"]
    end
    
    subgraph "Engine_Updates" ["Engine State Updates"]
        MoveToNextPano_call["MoveToNextPano()"]
        RotateObserver_call["RotateObserver()"]
        SetZoom_call["SetZoom()"]
        SetPosition_call["SetPosition()"]
    end
    
    subgraph "Game_Logic" ["Game Logic Updates"]
        game_on_step["game.on_step()"]
        get_reward_call["game.get_reward()"]
        get_info_call["game.get_info()"]
        done_check["episode done check"]
    end
    
    action_array --> step_method_call
    ACTION_SETS --> get_action_set
    get_action_set --> step_method_call
    
    step_method_call --> move_forward_calc
    step_method_call --> rotation_calc
    step_method_call --> zoom_calc
    
    move_forward_calc --> MoveToNextPano_call
    rotation_calc --> RotateObserver_call
    zoom_calc --> SetZoom_call
    
    MoveToNextPano_call --> game_on_step
    game_on_step --> get_reward_call
    game_on_step --> get_info_call
    game_on_step --> done_check
```

**Sources**: [streetlearn/python/environment/streetlearn.py:332-377](), [streetlearn/python/environment/streetlearn.py:60-98]()

## Build System and Dependencies

### External Dependencies Architecture

The system relies on multiple external libraries coordinated through Bazel build configuration.

| Component | Library | Purpose | Build Integration |
|-----------|---------|---------|-------------------|
| Machine Learning | TensorFlow | Neural network training | `@org_tensorflow` |
| Computer Vision | OpenCV | Image processing | `@opencv` local repository |
| Graphics Rendering | Cairo | 2D graphics rendering | `@cairo` local repository |
| Geometry | S2 Geometry | Spherical calculations | `@com_google_s2geometry` |
| Storage | LevelDB | Key-value panorama storage | `@com_google_leveldb` |
| Serialization | Protocol Buffers | Data structure serialization | `@com_google_protobuf` |
| Python Bindings | CLIF | C++/Python interface | `@clif` environment variable |

**Sources**: [WORKSPACE:1-106](), [README.md:64-201]()

### Component Interaction Boundaries

The architecture maintains clear separation between performance-critical C++ components and flexible Python logic through well-defined interfaces.

```mermaid
graph TB
    subgraph "Build_Dependencies" ["Build Dependencies"]
        bazel_workspace["WORKSPACE file"]
        tensorflow_dep["TensorFlow dependency"]
        opencv_dep["OpenCV dependency"]
        clif_dep["CLIF dependency"]
    end
    
    subgraph "CPP_Libraries" ["C++ Libraries"]
        streetlearn_engine_lib["streetlearn_engine library"]
        s2geometry_lib["S2 Geometry library"]
        leveldb_lib["LevelDB library"]
        protobuf_lib["Protocol Buffers library"]
    end
    
    subgraph "Python_Modules" ["Python Modules"]
        environment_module["environment module"]
        ui_module["ui module"]
        agents_module["agents module"]
    end
    
    subgraph "Interface_Bindings" ["Interface Bindings"]
        clif_bindings["CLIF generated bindings"]
        python_wrappers["Python wrapper classes"]
    end
    
    bazel_workspace --> tensorflow_dep
    bazel_workspace --> opencv_dep
    bazel_workspace --> clif_dep
    
    clif_dep --> streetlearn_engine_lib
    streetlearn_engine_lib --> s2geometry_lib
    streetlearn_engine_lib --> leveldb_lib
    streetlearn_engine_lib --> protobuf_lib
    
    streetlearn_engine_lib --> clif_bindings
    clif_bindings --> python_wrappers
    python_wrappers --> environment_module
    environment_module --> ui_module
    environment_module --> agents_module
```

**Sources**: [WORKSPACE:89-106](), [README.md:97-104](), [README.md:158-171]()

---

