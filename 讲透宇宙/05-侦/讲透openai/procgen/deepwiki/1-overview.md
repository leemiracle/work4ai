<!-- source: DeepWiki mcp.deepwiki.com · repo openai/procgen · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGES.md](CHANGES.md)
- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



## Purpose and Scope

The Procgen Benchmark is a suite of 16 procedurally-generated reinforcement learning environments designed to measure sample efficiency and generalization in RL agents. This repository provides high-performance C++ implementations of these environments with Python bindings, supporting both traditional `gym` and vectorized `gym3` interfaces.

This document provides a high-level overview of the Procgen system architecture, its key components, and how they interact. For detailed installation instructions, see [Installation](#2.1). For information about the build system, see [Build System](#3). For development setup and contribution guidelines, see [Development](#5).

Sources: [README.md:1-280]()

## System Architecture

The Procgen system follows a multi-layered architecture with a high-performance C++ core, Python bindings, and multiple user interfaces:

```mermaid
graph TB
    subgraph "User Interfaces"
        GYM["gym.make()"]
        GYM3["ProcgenGym3Env"]
        INTERACTIVE["procgen.interactive"]
    end
    
    subgraph "Python API Layer"
        PROCENV["ProcgenEnv"]
        PROCGYM3["ProcgenGym3Env class"]
        REGISTER["gym registration"]
    end
    
    subgraph "Core C++ Engine"
        VECGAME["VecGame"]
        GAMES["16 Game Implementations"]
        LIBENV["libenv C interface"]
    end
    
    subgraph "Rendering & Assets"
        QT5["Qt5 Framework"]
        ASSETS["Kenney Art Assets"]
        RENDER["RGB Array Output"]
    end
    
    subgraph "Procedural Generation"
        LEVELGEN["Level Generation"]
        MAZEGEN["Maze Algorithms"]
        RANDOMGEN["Random Asset Generation"]
    end
    
    GYM --> PROCENV
    GYM3 --> PROCGYM3
    INTERACTIVE --> PROCGYM3
    
    PROCENV --> REGISTER
    PROCGYM3 --> VECGAME
    
    VECGAME --> LIBENV
    LIBENV --> GAMES
    
    GAMES --> LEVELGEN
    GAMES --> QT5
    LEVELGEN --> MAZEGEN
    LEVELGEN --> RANDOMGEN
    
    QT5 --> ASSETS
    QT5 --> RENDER
    RANDOMGEN --> ASSETS
    
    RENDER --> VECGAME
```

The system is designed with performance as a primary concern, achieving thousands of steps per second on a single CPU core through its C++ implementation and efficient vectorized operations.

Sources: [README.md:7-8](), [README.md:201-202]()

## Environment Creation and Usage Flow

The following diagram illustrates how user code interacts with Procgen environments, showing the key classes and methods involved:

```mermaid
graph LR
    subgraph "User Code"
        USER["RL Agent/Researcher"]
    end
    
    subgraph "Environment Creation"
        GYMCREATE["gym.make('procgen:procgen-coinrun-v0')"]
        GYM3CREATE["ProcgenGym3Env(num=64, env_name='coinrun')"]
        INTCREATE["python -m procgen.interactive --env-name coinrun"]
    end
    
    subgraph "Environment Configuration"
        OPTIONS["Environment Options:<br/>start_level, num_levels,<br/>distribution_mode, etc."]
        STATE["State Management:<br/>get_state(), set_state()"]
    end
    
    subgraph "Core Environment Interface"
        STEP["step(action)"]
        RESET["reset()"]
        OBSERVE["observe()"]
        RENDER["render()"]
    end
    
    subgraph "C++ Game Engine"
        GAMELOGIC["Game Logic (16 games)"]
        PROCGEN["Procedural Generation"]
        QTRENDER["Qt Rendering"]
    end
    
    USER --> GYMCREATE
    USER --> GYM3CREATE
    USER --> INTCREATE
    
    GYMCREATE --> OPTIONS
    GYM3CREATE --> OPTIONS
    INTCREATE --> OPTIONS
    
    OPTIONS --> STEP
    OPTIONS --> RESET
    OPTIONS --> STATE
    
    STEP --> GAMELOGIC
    RESET --> GAMELOGIC
    OBSERVE --> QTRENDER
    RENDER --> QTRENDER
    
    GAMELOGIC --> PROCGEN
    QTRENDER --> PROCGEN
```

The system supports multiple configuration options that affect environment behavior, including difficulty levels (`distribution_mode`), level generation (`start_level`, `num_levels`), and visual rendering (`use_backgrounds`, `use_monochrome_assets`).

Sources: [README.md:64-76](), [README.md:134-147](), [README.md:166-178]()

## Key Components

### Game Environments

Procgen includes 16 distinct procedurally-generated environments, each implementing unique gameplay mechanics:

| Environment | Core Mechanic | Key Features |
|-------------|---------------|--------------|
| `coinrun` | Platformer | Dodge obstacles, collect coin |
| `bigfish` | Growth game | Eat smaller fish, avoid larger ones |
| `bossfight` | Shooter | Defeat boss with timed vulnerability |
| `maze` | Navigation | Find cheese in procedural maze |
| `heist` | Puzzle | Collect keys, unlock doors |
| `jumper` | Open world platformer | Find carrot with compass guidance |

The complete list of 16 environments covers diverse gameplay patterns to thoroughly test RL agent capabilities across different domains.

Sources: [README.md:104-122]()

### Performance Characteristics

- **Speed**: Thousands of environment steps per second on single CPU core
- **Platforms**: Windows 10, macOS 10.14+, Linux (manylinux2010)
- **Python**: 3.7-3.10 (64-bit only)
- **CPU Requirements**: AVX instruction set support
- **Memory**: Efficient C++ implementation with minimal overhead

Sources: [README.md:17](), [README.md:21-36]()

### Environment Options

The system provides extensive configuration through environment options:

```mermaid
graph TD
    subgraph "Level Generation"
        NUMLEVELS["num_levels=0<br/>(unlimited levels)"]
        STARTLEVEL["start_level=0<br/>(seed offset)"]
        SEQUENTIAL["use_sequential_levels=False<br/>(episode continuity)"]
    end
    
    subgraph "Difficulty Control"
        DISTMODE["distribution_mode='hard'<br/>(easy/hard/extreme/memory/exploration)"]
        CENTERAGENT["center_agent=True<br/>(observation framing)"]
    end
    
    subgraph "Visual Configuration"
        BACKGROUNDS["use_backgrounds=True"]
        THEMES["restrict_themes=False"]
        MONOCHROME["use_monochrome_assets=False"]
        VELOCITY["paint_vel_info=False"]
    end
    
    subgraph "Development Options"
        DEBUG["debug=False"]
        DEBUGMODE["debug_mode=0"]
        GENASSETS["use_generated_assets=False"]
    end
```

These options allow researchers to create controlled experimental conditions and adjust environment complexity for different research needs.

Sources: [README.md:134-147]()

## Build and Distribution System

Procgen uses a sophisticated multi-platform build system:

- **Python Packaging**: `cibuildwheel` for cross-platform wheel generation
- **C++ Compilation**: CMake build system with Qt5 static linking
- **CI/CD**: GitHub Actions for automated building and PyPI publishing
- **Asset Management**: Kenney art assets with comprehensive licensing tracking

The build system handles the complexity of compiling Qt5 from source and linking it statically with the C++ game implementations, enabling distribution of self-contained Python wheels.

Sources: [README.md:185-199]()

## Repository Structure

The codebase is organized into several key areas:

- **C++ Games**: Individual game implementations in `src/games/`
- **Python Bindings**: Python interfaces and gym registration
- **Build System**: CMake configuration and packaging scripts
- **Assets**: Game art and licensing documentation
- **CI/CD**: GitHub Actions workflows for automated builds

For detailed information about specific subsystems, see [Core Architecture](#4), [Build System](#3), and [Asset Library](#6.1).

Sources: [README.md:207-210]()

---

