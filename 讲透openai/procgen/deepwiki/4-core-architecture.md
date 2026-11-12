<!-- source: DeepWiki mcp.deepwiki.com · repo openai/procgen · page 4 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [procgen/CMakeLists.txt](procgen/CMakeLists.txt)
- [procgen/__init__.py](procgen/__init__.py)
- [procgen/builder.py](procgen/builder.py)

</details>



This page provides a technical deep-dive into the core architecture of the Procgen Benchmark system, focusing on the C++ game engine, Python integration layer, and the overall system design that enables high-performance procedural environment generation. For information about the build process, see [Build System](#3). For details about individual game implementations, see [Game Environments](#4.1). For Python API documentation, see [Python API](#4.2).

## System Overview

The Procgen architecture is built around a high-performance C++ core that implements 16 procedurally generated games, with Python bindings that expose both traditional OpenAI Gym and vectorized Gym3 interfaces. The system is designed for reinforcement learning research requiring fast, reproducible, and customizable environments.

```mermaid
graph TB
    subgraph "Python Layer"
        PROCENV["ProcgenEnv"]
        PROCGYM3["ProcgenGym3Env"] 
        REGISTER["register_environments()"]
    end
    
    subgraph "C++ Core Library"
        VECGAME["VecGame"]
        GAMEREGISTRY["GameRegistry"]
        BASEGAME["Game (base class)"]
    end
    
    subgraph "Game Implementations"
        COINRUN["coinrun.cpp"]
        BIGFISH["bigfish.cpp"] 
        DODGEBALL["dodgeball.cpp"]
        MAZE["maze.cpp"]
        OTHERGAMES["+ 12 more games"]
    end
    
    subgraph "Core Systems"
        ASSETGEN["assetgen.cpp"]
        MAZEGEN["mazegen.cpp"]
        RANDGEN["randgen.cpp"]
        ROOMGEN["roomgen.cpp"]
    end
    
    subgraph "Rendering"
        QT5["Qt5::Gui"]
        RESOURCES["resources.cpp"]
    end
    
    PROCENV --> VECGAME
    PROCGYM3 --> VECGAME
    REGISTER --> GAMEREGISTRY
    
    VECGAME --> GAMEREGISTRY
    GAMEREGISTRY --> BASEGAME
    
    BASEGAME --> COINRUN
    BASEGAME --> BIGFISH
    BASEGAME --> DODGEBALL
    BASEGAME --> MAZE
    BASEGAME --> OTHERGAMES
    
    COINRUN --> ASSETGEN
    BIGFISH --> MAZEGEN
    MAZE --> RANDGEN
    OTHERGAMES --> ROOMGEN
    
    ASSETGEN --> QT5
    RESOURCES --> QT5
```

Sources: [procgen/__init__.py:7-8](), [procgen/CMakeLists.txt:42-73]()

## C++ Core Architecture

The C++ core implements a modular game engine with shared infrastructure for procedural generation, rendering, and environment management. All games inherit from a common base class and integrate with the vectorized environment system.

```mermaid
graph TD
    subgraph "Environment Management"
        VECGAME["VecGame<br/>vecgame.cpp"]
        VECOPTIONS["VecOptions<br/>vecoptions.cpp"]
    end
    
    subgraph "Game Framework"
        GAME["Game<br/>game.cpp"]
        BASICGAME["BasicAbstractGame<br/>basic-abstract-game.cpp"]
        ENTITY["Entity<br/>entity.cpp"]
    end
    
    subgraph "16 Game Implementations"
        COINRUN_CPP["coinrun.cpp"]
        BIGFISH_CPP["bigfish.cpp"]
        BOSSFIGHT_CPP["bossfight.cpp"]
        CAVEFLYER_CPP["caveflyer.cpp"]
        CLIMBER_CPP["climber.cpp"]
        CHASER_CPP["chaser.cpp"]
        DODGEBALL_CPP["dodgeball.cpp"]
        FRUITBOT_CPP["fruitbot.cpp"]
        HEIST_CPP["heist.cpp"]
        JUMPER_CPP["jumper.cpp"]
        LEAPER_CPP["leaper.cpp"]
        MAZE_CPP["maze.cpp"]
        MINER_CPP["miner.cpp"]
        NINJA_CPP["ninja.cpp"]
        PLUNDER_CPP["plunder.cpp"]
        STARPILOT_CPP["starpilot.cpp"]
    end
    
    subgraph "Procedural Generation"
        MAZEGEN_CPP["mazegen.cpp"]
        RANDGEN_CPP["randgen.cpp"] 
        ROOMGEN_CPP["roomgen.cpp"]
    end
    
    subgraph "Asset & Rendering"
        ASSETGEN_CPP["assetgen.cpp"]
        RESOURCES_CPP["resources.cpp"]
        CPPUTILS["cpp-utils.cpp"]
    end
    
    VECGAME --> VECOPTIONS
    VECGAME --> GAME
    
    GAME --> BASICGAME
    BASICGAME --> ENTITY
    
    GAME --> COINRUN_CPP
    GAME --> BIGFISH_CPP
    GAME --> BOSSFIGHT_CPP
    GAME --> CAVEFLYER_CPP
    GAME --> CLIMBER_CPP
    GAME --> CHASER_CPP
    GAME --> DODGEBALL_CPP
    GAME --> FRUITBOT_CPP
    GAME --> HEIST_CPP
    GAME --> JUMPER_CPP
    GAME --> LEAPER_CPP
    GAME --> MAZE_CPP
    GAME --> MINER_CPP
    GAME --> NINJA_CPP
    GAME --> PLUNDER_CPP
    GAME --> STARPILOT_CPP
    
    COINRUN_CPP --> RANDGEN_CPP
    MAZE_CPP --> MAZEGEN_CPP
    HEIST_CPP --> ROOMGEN_CPP
    
    GAME --> ASSETGEN_CPP
    ASSETGEN_CPP --> RESOURCES_CPP
    RESOURCES_CPP --> CPPUTILS
```

Sources: [procgen/CMakeLists.txt:50-66](), [procgen/CMakeLists.txt:44-72]()

### Game Registration System

The game registry provides dynamic game instantiation and management through a centralized registration system. Each game registers itself with the `GameRegistry` using factory patterns.

| Component | File | Purpose |
|-----------|------|---------|
| `GameRegistry` | `game-registry.cpp` | Central registration and factory system |
| `VecGame` | `vecgame.cpp` | Vectorized environment coordinator |
| `Game` | `game.cpp` | Base class for all game implementations |
| `VecOptions` | `vecoptions.cpp` | Configuration management |

Sources: [procgen/CMakeLists.txt:49](), [procgen/CMakeLists.txt:71-72]()

## Python Integration Layer  

The Python layer provides two main interfaces: `ProcgenEnv` for traditional Gym compatibility and `ProcgenGym3Env` for vectorized environments. Both interfaces communicate with the C++ core through the `gym3.libenv` protocol.

```mermaid
graph LR
    subgraph "Python Interface"
        INIT["__init__.py"]
        ENV["env.py"]
        GYMREG["gym_registration.py"]
    end
    
    subgraph "Environment Classes"
        PROCENV["ProcgenEnv"]
        PROCGYM3["ProcgenGym3Env"]
    end
    
    subgraph "C++ Integration"
        LIBENV["gym3.libenv"]
        BUILDER["builder.py"]
        VECGAME_PY["VecGame (C++)"]
    end
    
    subgraph "Build System"
        CMAKE["CMakeLists.txt"]
        SHAREDLIB["libenv.so/.dll"]
    end
    
    INIT --> PROCENV
    INIT --> PROCGYM3
    INIT --> GYMREG
    
    ENV --> PROCENV
    ENV --> PROCGYM3
    
    PROCENV --> LIBENV
    PROCGYM3 --> LIBENV
    
    LIBENV --> BUILDER
    BUILDER --> CMAKE
    CMAKE --> SHAREDLIB
    SHAREDLIB --> VECGAME_PY
```

Sources: [procgen/__init__.py:7-12](), [procgen/builder.py:11]()

### Build Integration

The `builder.py` module manages the compilation of the C++ library and provides process-safe building with dependency resolution for Qt5 and CMake.

| Function | Purpose |
|----------|---------|
| `build()` | Main build orchestration with lock management |
| `_attempt_configure()` | CMake configuration with Qt5 path detection |
| `chdir()` | Context manager for directory changes |
| `check()` | Process result validation and error handling |

Sources: [procgen/builder.py:95-147]()

## Rendering and Asset System

The rendering system uses Qt5 for cross-platform graphics with a resource management system that supports both human-designed and procedurally generated assets.

```mermaid
graph TB
    subgraph "Qt5 Integration"
        QT5GUI["Qt5::Gui"]
        QTCMAKE["find_package(Qt5 COMPONENTS Gui)"]
    end
    
    subgraph "Asset Management" 
        RESOURCES["resources.cpp"]
        ASSETGEN["assetgen.cpp"]
        KENNEY["Kenney Abstract Assets"]
    end
    
    subgraph "Rendering Pipeline"
        GAMERENDER["Game::render()"]
        RGBARRAY["RGB Array Output<br/>64x64x3"]
        VIEWERWRAPPER["gym3.ViewerWrapper"]
    end
    
    subgraph "Asset Options"
        USEGENERATED["use_generated_assets"]
        USEBACKGROUNDS["use_backgrounds"] 
        RESTRICTTHEMES["restrict_themes"]
        MONOCHROME["use_monochrome_assets"]
    end
    
    QTCMAKE --> QT5GUI
    QT5GUI --> GAMERENDER
    
    RESOURCES --> ASSETGEN
    KENNEY --> ASSETGEN
    ASSETGEN --> GAMERENDER
    
    GAMERENDER --> RGBARRAY
    RGBARRAY --> VIEWERWRAPPER
    
    USEGENERATED --> ASSETGEN
    USEBACKGROUNDS --> ASSETGEN
    RESTRICTTHEMES --> ASSETGEN
    MONOCHROME --> ASSETGEN
```

Sources: [procgen/CMakeLists.txt:40](), [procgen/CMakeLists.txt:77](), [procgen/CMakeLists.txt:44](), [procgen/CMakeLists.txt:70]()

## Environment Lifecycle

The environment lifecycle manages game instantiation, state management, and the observation-action loop through the vectorized environment system.

### Core Lifecycle Components

| Phase | C++ Component | Python Interface |
|-------|---------------|------------------|
| Initialization | `VecGame` constructor | `ProcgenGym3Env.__init__()` |
| Game Selection | `GameRegistry::make_game()` | `env_name` parameter |
| Level Generation | `Game::game_init()` | `start_level`, `num_levels` |
| Observation | `Game::observe()` | `env.observe()` |
| Action Processing | `Game::step()` | `env.act()` |
| State Management | `Game::get_state()` | `env.callmethod("get_state")` |

### Vectorization Architecture

The `VecGame` class coordinates multiple game instances within a single process, enabling high-throughput training:

```mermaid
graph TB
    subgraph "VecGame Coordinator"
        VECGAME_MAIN["VecGame"]
        GAMEINSTANCES["Game Instances Array"]
        INFOTYPES["info_types vector"]
    end
    
    subgraph "Per-Game State"
        GAME1["Game Instance 1"]
        GAME2["Game Instance 2"] 
        GAMEN["Game Instance N"]
    end
    
    subgraph "Shared Resources"
        REGISTRY["GameRegistry"]
        OPTIONS["VecOptions"]
        QTRESOURCES["Qt Resources"]
    end
    
    VECGAME_MAIN --> GAMEINSTANCES
    VECGAME_MAIN --> INFOTYPES
    
    GAMEINSTANCES --> GAME1
    GAMEINSTANCES --> GAME2
    GAMEINSTANCES --> GAMEN
    
    GAME1 --> REGISTRY
    GAME2 --> REGISTRY
    GAMEN --> REGISTRY
    
    VECGAME_MAIN --> OPTIONS
    GAME1 --> QTRESOURCES
    GAME2 --> QTRESOURCES
    GAMEN --> QTRESOURCES
```

Sources: [procgen/CMakeLists.txt:71](), [procgen/CMakeLists.txt:72](), [procgen/CMakeLists.txt:49]()

---

