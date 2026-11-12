<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/streetlearn · page 7 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [streetlearn/engine/BUILD](streetlearn/engine/BUILD)
- [streetlearn/engine/graph_image_cache_test.cc](streetlearn/engine/graph_image_cache_test.cc)
- [streetlearn/engine/graph_renderer_test.cc](streetlearn/engine/graph_renderer_test.cc)
- [streetlearn/python/agents/BUILD](streetlearn/python/agents/BUILD)
- [streetlearn/python/environment/BUILD](streetlearn/python/environment/BUILD)

</details>



This document provides instructions for developers working on the StreetLearn codebase, covering build configuration, extending C++ engine components, and developing new Python environment features. For general system architecture information, see [System Architecture](#2). For specific guidance on training agents, see [Training and Experimentation](#5).

## Build System Overview

StreetLearn uses Bazel as its build system with a modular architecture separating C++ engine components from Python interfaces. The build configuration manages complex dependencies including computer vision libraries, geographical computation tools, and machine learning frameworks.

### Build Structure

```mermaid
graph TB
    subgraph "Root Workspace"
        WORKSPACE["WORKSPACE file<br/>External dependencies"]
    end
    
    subgraph "C++ Engine Layer"
        EngineBuild["streetlearn/engine/BUILD<br/>Core C++ libraries"]
        PythonBindings["streetlearn/engine/python/BUILD<br/>CLIF bindings"]
    end
    
    subgraph "Python Layer"
        EnvironmentBuild["streetlearn/python/environment/BUILD<br/>Game logic & environments"]
        AgentsBuild["streetlearn/python/agents/BUILD<br/>AI agents"]
    end
    
    subgraph "Protocol Buffers"
        ProtoBuild["streetlearn/proto/BUILD<br/>Data structures"]
    end
    
    subgraph "External Dependencies"
        TensorFlow["@tensorflow"]
        OpenCV["@opencv"]
        Cairo["@cairo"]
        S2Geometry["@com_google_s2geometry"]
        LevelDB["@com_google_leveldb"]
        AbslCpp["@com_google_absl"]
    end
    
    WORKSPACE --> EngineBuild
    WORKSPACE --> EnvironmentBuild
    WORKSPACE --> AgentsBuild
    
    EngineBuild --> TensorFlow
    EngineBuild --> OpenCV
    EngineBuild --> Cairo
    EngineBuild --> S2Geometry
    EngineBuild --> LevelDB
    EngineBuild --> AbslCpp
    
    EngineBuild --> PythonBindings
    PythonBindings --> EnvironmentBuild
    ProtoBuild --> EngineBuild
    ProtoBuild --> EnvironmentBuild
    
    EnvironmentBuild --> AgentsBuild
```

**Sources:** [streetlearn/engine/BUILD:1-615](), [streetlearn/python/environment/BUILD:1-49](), [streetlearn/python/agents/BUILD:1-33]()

### Key Build Targets

| Target | Purpose | Dependencies |
|--------|---------|--------------|
| `//streetlearn/engine:streetlearn_engine` | Core C++ engine | Cairo, OpenCV, S2Geometry, LevelDB |
| `//streetlearn/engine:pano_graph` | Panorama graph management | Dataset, caching, math utilities |
| `//streetlearn/engine:graph_renderer` | Graph visualization | Cairo, image processing |
| `//streetlearn/python/environment:environment_py` | Python environment API | Engine bindings, protocol buffers |
| `//streetlearn/python/agents:agents_py` | AI agent implementations | Environment, neural network components |

**Sources:** [streetlearn/engine/BUILD:119-139](), [streetlearn/engine/BUILD:142-158](), [streetlearn/engine/BUILD:279-301](), [streetlearn/python/environment/BUILD:23-49](), [streetlearn/python/agents/BUILD:23-32]()

## Engine Development

The C++ engine provides high-performance components for panorama processing, graph management, and rendering. Development involves working with computer vision libraries, caching systems, and geographical computations.

### Core Engine Architecture

```mermaid
graph TD
    subgraph "Data Layer"
        Dataset["Dataset interface<br/>dataset.h"]
        LevelDBDataset["LevelDBDataset<br/>leveldb_dataset.h/.cc"]
        DatasetFactory["DatasetFactory<br/>dataset_factory.h/.cc"]
    end
    
    subgraph "Caching Layer"
        NodeCache["NodeCache<br/>node_cache.h/.cc"]
        MetadataCache["MetadataCache<br/>metadata_cache.h/.cc"]
        GraphImageCache["GraphImageCache<br/>graph_image_cache.h/.cc"]
        PanoFetcher["PanoFetcher<br/>pano_fetcher.h/.cc"]
    end
    
    subgraph "Graph Management"
        PanoGraph["PanoGraph<br/>pano_graph.h/.cc"]
        PanoGraphNode["PanoGraphNode<br/>pano_graph_node.h/.cc"]
        PanoCalculations["PanoCalculations<br/>pano_calculations.h"]
    end
    
    subgraph "Rendering Systems"
        PanoRenderer["PanoRenderer<br/>pano_renderer.h/.cc"]
        GraphRenderer["GraphRenderer<br/>graph_renderer.h/.cc"]
        PanoProjection["PanoProjection<br/>pano_projection.h/.cc"]
    end
    
    subgraph "Main Engine"
        StreetLearnEngine["StreetLearnEngine<br/>streetlearn_engine.h/.cc"]
    end
    
    subgraph "Utilities"
        MathUtil["Math utilities<br/>math_util.h, vector.h"]
        ColorUtils["Color utilities<br/>color.h"]
        ImageUtils["Image utilities<br/>image.h"]
    end
    
    DatasetFactory --> LevelDBDataset
    DatasetFactory --> Dataset
    Dataset --> PanoFetcher
    PanoFetcher --> NodeCache
    Dataset --> MetadataCache
    PanoGraph --> GraphImageCache
    
    NodeCache --> PanoGraph
    MetadataCache --> PanoGraph
    PanoGraph --> PanoGraphNode
    PanoGraphNode --> PanoCalculations
    
    PanoGraph --> PanoRenderer
    PanoGraph --> GraphRenderer
    PanoRenderer --> PanoProjection
    
    StreetLearnEngine --> PanoGraph
    StreetLearnEngine --> PanoRenderer
    StreetLearnEngine --> GraphRenderer
    StreetLearnEngine --> MetadataCache
    
    MathUtil --> PanoGraph
    MathUtil --> PanoRenderer
    MathUtil --> GraphRenderer
    ColorUtils --> GraphRenderer
    ImageUtils --> PanoGraphNode
```

**Sources:** [streetlearn/engine/BUILD:81-88](), [streetlearn/engine/BUILD:104-116](), [streetlearn/engine/BUILD:119-139](), [streetlearn/engine/BUILD:142-158](), [streetlearn/engine/BUILD:219-231](), [streetlearn/engine/BUILD:279-301]()

### Adding New Rendering Features

To extend the rendering system, developers typically work with the `GraphRenderer` and `PanoRenderer` classes:

1. **Graph Rendering Extensions**: Modify `graph_renderer.h/.cc` for new visualization features
2. **Panorama Processing**: Extend `pano_renderer.h/.cc` for new projection methods
3. **Caching Optimization**: Update cache classes for new data types

Testing new rendering features requires test data and image comparison utilities:

```mermaid
graph LR
    subgraph "Test Infrastructure"
        TestDataset["TestDataset<br/>test_dataset.h/.cc"]
        TestUtils["test_utils.h/.cc<br/>Image comparison"]
    end
    
    subgraph "Rendering Tests"
        GraphRendererTest["GraphRendererTest<br/>graph_renderer_test.cc"]
        GraphImageCacheTest["GraphImageCacheTest<br/>graph_image_cache_test.cc"]
        PanoRendererTest["PanoRendererTest<br/>pano_renderer_test.cc"]
    end
    
    subgraph "Test Data"
        TestImages["Test reference images<br/>engine/test_data/*.png"]
    end
    
    TestDataset --> GraphRendererTest
    TestDataset --> GraphImageCacheTest
    TestDataset --> PanoRendererTest
    TestUtils --> GraphRendererTest
    TestUtils --> GraphImageCacheTest
    TestImages --> GraphRendererTest
    TestImages --> GraphImageCacheTest
```

**Sources:** [streetlearn/engine/graph_renderer_test.cc:1-155](), [streetlearn/engine/graph_image_cache_test.cc:1-125](), [streetlearn/engine/BUILD:322-338](), [streetlearn/engine/BUILD:575-604]()

### Cache System Development

The caching system uses LRU policies and thread-safe operations. Key classes for extension:

| Class | Purpose | Thread Safety | Cache Policy |
|-------|---------|---------------|--------------|
| `NodeCache` | Panorama data caching | Thread-safe | LRU eviction |
| `MetadataCache` | Panorama metadata | Thread-safe | Size-based |
| `GraphImageCache` | Rendered graph images | Not specified | Custom regions |

**Sources:** [streetlearn/engine/BUILD:219-231](), [streetlearn/engine/BUILD:208-217](), [streetlearn/engine/BUILD:260-276]()

## Environment Development

Python environment development focuses on creating new games, observation types, and agent interfaces. The system uses a factory pattern for game instantiation and modular observation processing.

### Environment System Structure

```mermaid
graph TB
    subgraph "Configuration System"
        DefaultConfig["DEFAULT_CONFIG<br/>default_config.py"]
        ApplyDefaults["ApplyDefaults function"]
        NameToGame["NAME_TO_GAME registry"]
    end
    
    subgraph "Base Environment"
        StreetLearn["StreetLearn class<br/>streetlearn.py"]
        BatchedStreetLearn["BatchedStreetLearn<br/>batched_streetlearn.py"]
    end
    
    subgraph "Game Implementations"
        GameBase["Game base class<br/>game.py"]
        CoinGame["CoinGame<br/>coin_game.py"]
        CourierGame["CourierGame<br/>courier_game.py"]
        CurriculumCourierGame["CurriculumCourierGame<br/>curriculum_courier_game.py"]
        ExplorationGame["ExplorationGame<br/>exploration_game.py"]
        GoalInstructionGame["GoalInstructionGame<br/>goal_instruction_game.py"]
        IncrementalInstructionGame["IncrementalInstructionGame<br/>incremental_instruction_game.py"]
        StepByStepInstructionGame["StepByStepInstructionGame<br/>step_by_step_instruction_game.py"]
    end
    
    subgraph "Observation System"
        Observations["Observations module<br/>observations.py"]
        ThumbnailHelper["ThumbnailHelper<br/>thumbnail_helper.py"]
    end
    
    subgraph "Instruction Systems"
        InstructionsBase["InstructionsBase<br/>instructions_base.py"]
        InstructionsCurriculum["InstructionsCurriculum<br/>instructions_curriculum.py"]
        InstructionsDensification["InstructionsDensification<br/>instructions_densification.py"]
    end
    
    DefaultConfig --> ApplyDefaults
    NameToGame --> StreetLearn
    ApplyDefaults --> StreetLearn
    StreetLearn --> BatchedStreetLearn
    
    StreetLearn --> GameBase
    GameBase --> CoinGame
    CoinGame --> CourierGame
    CourierGame --> CurriculumCourierGame
    GameBase --> ExplorationGame
    GameBase --> GoalInstructionGame
    GameBase --> IncrementalInstructionGame
    GameBase --> StepByStepInstructionGame
    
    StreetLearn --> Observations
    Observations --> ThumbnailHelper
    
    GoalInstructionGame --> InstructionsBase
    IncrementalInstructionGame --> InstructionsBase
    StepByStepInstructionGame --> InstructionsBase
    InstructionsBase --> InstructionsCurriculum
    InstructionsBase --> InstructionsDensification
```

**Sources:** [streetlearn/python/environment/BUILD:23-49]()

### Creating New Games

To implement a new game type:

1. **Inherit from Game Base**: Extend the base `Game` class in `game.py`
2. **Register in Factory**: Add to `NAME_TO_GAME` registry in appropriate module
3. **Implement Required Methods**: Override `on_reset()`, `on_step()`, `get_reward()`, `get_info()`
4. **Define Observations**: Specify observation space and observation processing

### Agent Development Structure

```mermaid
graph TD
    subgraph "Agent Base Components"
        LocalePathway["LocalePathway<br/>locale_pathway.py"]
        PlainAgent["PlainAgent<br/>plain_agent.py"]
    end
    
    subgraph "Navigation Agents"
        GoalNavAgent["GoalNavAgent<br/>goal_nav_agent.py"]
        CityNavAgent["CityNavAgent<br/>city_nav_agent.py"]
    end
    
    subgraph "Neural Network Components"
        ConvNet["ConvNet2D layers"]
        LSTMCore["LSTM memory core"]
        PolicyHead["Policy output head"]
        ValueHead["Value output head"]
    end
    
    PlainAgent --> ConvNet
    PlainAgent --> LSTMCore
    PlainAgent --> PolicyHead
    PlainAgent --> ValueHead
    
    LocalePathway --> GoalNavAgent
    PlainAgent --> GoalNavAgent
    GoalNavAgent --> CityNavAgent
```

**Sources:** [streetlearn/python/agents/BUILD:23-32]()

### Testing Environment Extensions

Environment testing involves:

1. **Unit Tests**: Test individual game logic components
2. **Integration Tests**: Verify environment-agent interactions
3. **Observation Validation**: Ensure correct observation space definitions
4. **Reward Function Testing**: Validate reward calculations and game termination

The build system provides test targets that can be extended for new components:

| Test Type | Build Pattern | Example |
|-----------|---------------|---------|
| C++ Unit Tests | `cc_test` | `streetlearn_engine_test` |
| Python Unit Tests | `py_test` | Environment game tests |
| Integration Tests | Cross-language | Engine-Python binding tests |

**Sources:** [streetlearn/engine/BUILD:340-604]()

---

