<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/jericho · page 4 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frotz/src/dumb/dumb_blorb.c](frotz/src/dumb/dumb_blorb.c)
- [frotz/src/dumb/dumb_frotz.h](frotz/src/dumb/dumb_frotz.h)
- [frotz/src/dumb/dumb_init.c](frotz/src/dumb/dumb_init.c)
- [frotz/src/dumb/dumb_input.c](frotz/src/dumb/dumb_input.c)
- [frotz/src/dumb/dumb_output.c](frotz/src/dumb/dumb_output.c)
- [frotz/src/dumb/dumb_pic.c](frotz/src/dumb/dumb_pic.c)
- [frotz/src/interface/frotz_interface.c](frotz/src/interface/frotz_interface.c)
- [jericho/jericho.py](jericho/jericho.py)

</details>



This document provides a technical deep dive into Jericho's internal architecture, explaining how the major components interact to provide a Python interface for interactive fiction games. It covers the layered design, game customization framework, and Z-machine integration patterns.

For information about using the FrotzEnv interface, see [Core Components](#3). For details on adding new games, see [Adding New Games](#5.2).

## Layered Architecture Overview

Jericho employs a clean layered architecture that separates the Python interface from the underlying Z-machine implementation:

```mermaid
graph TB
    subgraph "Python Interface Layer"
        FrotzEnv["FrotzEnv Class<br/>(jericho.py)"]
        TAG["TemplateActionGenerator<br/>(template_action_generator.py)"]
        Bindings["Game Bindings<br/>(defines.py)"]
        Utils["Utilities<br/>(util.py)"]
    end
    
    subgraph "C Library Layer"
        Interface["frotz_interface.c<br/>Main C Interface"]
        GameDispatch["Game Function Dispatch<br/>ROM_IDX + Function Arrays"]
        FrotzCore["Frotz Z-Machine Core<br/>(libfrotz.so)"]
    end
    
    subgraph "Game Files"
        ZFiles[".z5/.z8 Game Files"]
        GameLogic["Game-Specific C Files<br/>(zork1.c, hhgg.c, etc.)"]
    end
    
    FrotzEnv --> Interface
    TAG --> Bindings
    Interface --> GameDispatch
    GameDispatch --> FrotzCore
    GameDispatch --> GameLogic
    ZFiles --> FrotzCore
```

The architecture provides clear separation of concerns: Python handles the high-level API and action generation, while C handles the performance-critical Z-machine interpretation and game-specific logic.

**Sources:** [jericho/jericho.py:371-388](), [frotz/src/interface/frotz_interface.c:174-311]()

## Python Interface Layer

The Python layer provides the main user-facing API through the `FrotzEnv` class and supporting components:

```mermaid
graph LR
    subgraph "FrotzEnv Core Methods"
        Reset["reset()"]
        Step["step(action)"]
        GetValidActions["get_valid_actions()"]
        GetState["get_state()"]
        SetState["set_state(state)"]
    end
    
    subgraph "State Management"
        StateData["RAM + Stack + PC + SP + FP<br/>+ Frame Count + RNG"]
        WorldObjects["World Object Tree<br/>ZObject instances"]
        GameInfo["Game Metadata<br/>Score, Moves, Victory"]
    end
    
    subgraph "Action Generation"
        TAG2["TemplateActionGenerator"]
        Templates["Grammar Templates"]
        ObjectIdentifier["Interactive Object<br/>Identification"]
        ActionFilter["Action Filtering<br/>(C-level validation)"]
    end
    
    Reset --> StateData
    Step --> GameInfo
    GetValidActions --> TAG2
    TAG2 --> Templates
    TAG2 --> ObjectIdentifier
    ObjectIdentifier --> ActionFilter
    GetState --> StateData
    SetState --> StateData
```

The `FrotzEnv` class in [jericho/jericho.py:371-388]() serves as the main interface, managing game state and coordinating between the action generation system and the underlying C library. Key methods include:

- `reset()` - Initializes game state and returns initial observation
- `step(action)` - Executes an action and returns observation, reward, done, info
- `get_valid_actions()` - Generates contextually valid actions using templates and object detection
- `get_state()`/`set_state()` - Serializes/deserializes complete game state for checkpointing

**Sources:** [jericho/jericho.py:448-491](), [jericho/jericho.py:554-576](), [jericho/jericho.py:578-632]()

## C Library Interface

The C layer provides the bridge between Python and the Frotz Z-machine interpreter:

```mermaid
graph TB
    subgraph "Python ctypes Interface"
        LoadLib["_load_frotz_lib()<br/>Dynamic library loading"]
        CtypeBindings["Function signatures<br/>argtypes + restype"]
    end
    
    subgraph "frotz_interface.c Main Functions"
        Setup["setup(story_file, seed, rom, size)"]
        Step2["step(action_bytes)"]
        GetObject["get_object(obj_ptr, obj_num)"]
        SaveState["save_str(buffer)"]
        RestoreState["restore_str(buffer)"]
        GetRAM["getRAM(ram_ptr)"]
        SetRAM["setRAM(ram_ptr)"]
    end
    
    subgraph "Game Detection & Dispatch"
        LoadBindings["load_rom_bindings(story_file)<br/>MD5 hash calculation"]
        ROMIndex["ROM_IDX enum<br/>Game identification"]
        FunctionArrays["Function pointer arrays<br/>victory_fns[], game_over_fns[], etc."]
    end
    
    LoadLib --> CtypeBindings
    CtypeBindings --> Setup
    CtypeBindings --> Step2
    Setup --> LoadBindings
    LoadBindings --> ROMIndex
    ROMIndex --> FunctionArrays
```

The interface layer handles several critical responsibilities:

1. **Dynamic Library Loading**: [jericho/jericho.py:216-339]() loads `libfrotz.so` and defines ctypes signatures for all C functions
2. **Game Detection**: [frotz/src/interface/frotz_interface.c:174-311]() calculates MD5 hashes of game files to determine which game-specific implementations to use
3. **State Serialization**: Functions like `save_str()` and `restore_str()` enable complete game state checkpointing
4. **Memory Management**: Direct access to Z-machine RAM, stack, and registers through functions like `getRAM()`/`setRAM()`

**Sources:** [jericho/jericho.py:216-339](), [frotz/src/interface/frotz_interface.c:313-374](), [frotz/src/interface/frotz_interface.c:376-455]()

## Game Customization Framework

Jericho supports 40+ different interactive fiction games through a sophisticated dispatch system:

```mermaid
graph TB
    subgraph "Game Detection"
        MD5["MD5 Hash Calculation<br/>from game file bytes"]
        HashLookup["Hash → ROM_IDX mapping<br/>192+ MD5 comparisons"]
        DefaultFallback["DEFAULT_ enum<br/>for unsupported games"]
    end
    
    subgraph "Function Pointer Arrays"
        VictoryFns["victory_fns[]<br/>Game completion detection"]
        GameOverFns["game_over_fns[]<br/>Failure condition detection"]
        ScoreFns["get_score_fns[]<br/>Score extraction"]
        CleanFns["clean_observation_fns[]<br/>Text processing"]
        RAMFns["ram_addr_fns[]<br/>Special memory locations"]
    end
    
    subgraph "Game-Specific Implementations"
        Zork1["zork1.c<br/>ZORK1_ functions"]
        HHGG["hhgg.c<br/>HHGG_ functions"]
        Curses["curses.c<br/>CURSES_ functions"]
        Textworld["textworld.c<br/>TEXTWORLD_ functions"]
        OtherGames["40+ other game files"]
    end
    
    MD5 --> HashLookup
    HashLookup --> DefaultFallback
    HashLookup --> VictoryFns
    VictoryFns --> Zork1
    VictoryFns --> HHGG
    VictoryFns --> Curses
    VictoryFns --> Textworld
    VictoryFns --> OtherGames
```

Each supported game has an entry in the ROM_IDX enum and corresponding implementations for critical functions:

| Function Category | Purpose | Example Implementation |
|------------------|---------|----------------------|
| Victory Detection | Determine game completion | `zork1_victory()` |
| Game Over Detection | Detect failure conditions | `hhgg_game_over()` |
| Score Calculation | Extract current score | `curses_get_score()` |
| Observation Cleaning | Process game text | `textworld_clean_observation()` |
| Special RAM Addresses | Game-specific memory locations | `zork1_ram_addrs()` |

The dispatch mechanism in [frotz/src/interface/frotz_interface.c:469-529]() uses function pointer arrays indexed by `ROM_IDX` to call the appropriate game-specific implementations.

**Sources:** [frotz/src/interface/frotz_interface.c:174-311](), [frotz/src/interface/frotz_interface.c:469-1148]()

## Z-Machine State Management

Jericho provides complete access to the Z-machine's internal state for research applications:

```mermaid
graph LR
    subgraph "Z-Machine Memory"
        RAM["Dynamic RAM<br/>(h_dynamic_size bytes)"]
        Stack["Call Stack<br/>(STACK_SIZE * zword)"]
        Registers["Registers<br/>PC, SP, FP"]
        RNG["Random Number Generator<br/>A, Interval, Counter"]
    end
    
    subgraph "Python State Tuple"
        StateRAM["ram: np.array"]
        StateStack["stack: np.array"]
        StatePC["pc: int"]
        StateSP["sp: int"]
        StateFP["fp: int"]
        StateFrameCount["frame_count: int"]
        StateOpcode["opcode: int"]
        StateRNG["rng: tuple"]
        StateNarrative["narrative: bytes"]
    end
    
    subgraph "State Operations"
        GetState2["get_state()<br/>Serialize to Python"]
        SetState2["set_state(state)<br/>Restore from Python"]
        SaveQuetzal["save_str(buffer)<br/>Quetzal format"]
        RestoreQuetzal["restore_str(buffer)<br/>Quetzal format"]
    end
    
    RAM --> StateRAM
    Stack --> StateStack
    Registers --> StatePC
    Registers --> StateSP
    Registers --> StateFP
    RNG --> StateRNG
    
    StateRAM --> GetState2
    StateStack --> GetState2
    GetState2 --> SetState2
    GetState2 --> SaveQuetzal
    RestoreQuetzal --> SetState2
```

The state management system enables several key research capabilities:

1. **Perfect Checkpointing**: Complete game state can be saved and restored
2. **Deterministic Replay**: With saved state + actions, games can be replayed exactly
3. **State Analysis**: Access to object trees, memory, and internal variables
4. **Parallel Exploration**: Multiple environments can be forked from the same state

State serialization is handled by [jericho/jericho.py:605-632]() which extracts all Z-machine components into a Python tuple, while [jericho/jericho.py:578-604]() restores the state by calling the corresponding C functions.

**Sources:** [jericho/jericho.py:605-632](), [jericho/jericho.py:578-604](), [frotz/src/interface/frotz_interface.c:376-455]()

## Action Generation and Validation

The action generation system automatically produces valid actions based on game grammar and current context:

```mermaid
graph TB
    subgraph "Object Identification"
        Look["Look command<br/>Extract location objects"]
        Inventory["Inventory command<br/>Extract possessed objects"]
        Examine["Examine objects<br/>Filter interactive ones"]
        ObjectTree["Z-Machine Object Tree<br/>get_world_objects()"]
    end
    
    subgraph "Template Application"
        Grammar["Grammar templates<br/>from game bindings"]
        TemplateGen["generate_actions()<br/>Apply objects to templates"]
        CandidateActions["Candidate action list"]
    end
    
    subgraph "Action Filtering"
        FilterC["filter_candidate_actions()<br/>C-level validation"]
        ExecuteTest["Execute each action<br/>Check for world changes"]
        WorldDiff["get_world_diff()<br/>Detect state changes"]
        ValidActions["Valid action list"]
    end
    
    Look --> TemplateGen
    Inventory --> TemplateGen
    Examine --> TemplateGen
    ObjectTree --> TemplateGen
    Grammar --> TemplateGen
    TemplateGen --> CandidateActions
    CandidateActions --> FilterC
    FilterC --> ExecuteTest
    ExecuteTest --> WorldDiff
    WorldDiff --> ValidActions
```

The action generation process in [jericho/jericho.py:554-576]() follows these steps:

1. **Object Identification**: Uses `_identify_interactive_objects()` to find objects in the current location and inventory
2. **Template Generation**: Applies grammar templates to identified objects using `TemplateActionGenerator`
3. **Action Filtering**: Tests each candidate action by executing it and checking for world state changes
4. **Parallelization**: Can use multiprocessing to speed up action filtering for large candidate sets

The filtering process is performance-critical and can optionally use C-level optimization (`use_ctypes=True`) and parallel processing (`use_parallel=True`).

**Sources:** [jericho/jericho.py:554-576](), [jericho/jericho.py:938-1036](), [jericho/jericho.py:840-936]()

---

