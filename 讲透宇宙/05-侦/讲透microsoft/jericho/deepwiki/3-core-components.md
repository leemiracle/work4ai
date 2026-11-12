<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/jericho · page 3 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frotz/src/games/omniquest.c](frotz/src/games/omniquest.c)
- [frotz/src/games/plundered.c](frotz/src/games/plundered.c)
- [frotz/src/games/zork1.c](frotz/src/games/zork1.c)
- [jericho/defines.py](jericho/defines.py)
- [jericho/game_info.py](jericho/game_info.py)
- [jericho/jericho.py](jericho/jericho.py)
- [jericho/template_action_generator.py](jericho/template_action_generator.py)

</details>



This document provides a detailed overview of the main architectural components that make up the Jericho system. It covers the Python interface layer, action generation system, game support framework, and Z-machine integration. For information about building and installing Jericho, see [Building and Testing](#5.1). For details about adding support for new games, see [Adding New Games](#5.2).

## Python Interface Layer

The Python interface layer provides the primary API for interacting with interactive fiction games through the `FrotzEnv` class and supporting data structures.

### FrotzEnv Class

The `FrotzEnv` class serves as the main entry point for all game interactions. It wraps the underlying C library and provides a clean Python API compatible with reinforcement learning frameworks.

```mermaid
graph TB
    subgraph "FrotzEnv Core Methods"
        INIT["__init__(story_file, seed)"]
        RESET["reset()"]
        STEP["step(action)"]
        GETVALID["get_valid_actions()"]
    end
    
    subgraph "State Management"
        GETSTATE["get_state()"]
        SETSTATE["set_state(state)"]
        GETHASH["get_world_state_hash()"]
    end
    
    subgraph "Game Information"
        GETOBJ["get_object(obj_num)"]
        GETWORLDOBJ["get_world_objects()"]
        GETDICT["get_dictionary()"]
        GETINV["get_inventory()"]
    end
    
    subgraph "Game Metrics"
        GETSCORE["get_score()"]
        GETMOVES["get_moves()"]
        VICTORY["victory()"]
        GAMEOVER["game_over()"]
    end
    
    INIT --> RESET
    RESET --> STEP
    STEP --> GETVALID
    GETVALID --> STEP
    
    STEP --> GETSTATE
    SETSTATE --> STEP
    
    style INIT fill:#e1f5fe
    style STEP fill:#f3e5f5
    style GETVALID fill:#fff3e0
```

Sources: [jericho/jericho.py:371-492]()

### Z-Machine Data Structures

Jericho exposes key Z-machine data structures through Python classes that provide access to game internals.

#### ZObject Structure

The `ZObject` class represents objects in the Z-machine object tree, providing access to object relationships, attributes, and properties.

```mermaid
graph LR
    subgraph "ZObject Fields"
        NUM["num: int"]
        NAME["name: string"]
        PARENT["parent: int"]
        SIBLING["sibling: int"]
        CHILD["child: int"]
        ATTR["attr: 32-bit array"]
        PROPS["properties: list"]
    end
    
    subgraph "Object Tree Relationships"
        PARENTOBJ["Parent Object"]
        SIBLINGOBJ["Sibling Object"]
        CHILDOBJ["Child Object"]
    end
    
    PARENT --> PARENTOBJ
    SIBLING --> SIBLINGOBJ
    CHILD --> CHILDOBJ
    
    style NUM fill:#e1f5fe
    style NAME fill:#f3e5f5
```

Sources: [jericho/jericho.py:59-129]()

#### DictionaryWord Structure

The `DictionaryWord` class represents vocabulary words recognized by the game parser, including part-of-speech information.

```mermaid
graph TB
    subgraph "DictionaryWord Fields"
        WORD["word: string"]
        ISNOUN["is_noun: boolean"]
        ISVERB["is_verb: boolean"]
        ISPREP["is_prep: boolean"]
        ISMETA["is_meta: boolean"]
        ISPLURAL["is_plural: boolean"]
        ISDIR["is_dir: boolean"]
        ISADJ["is_adj: boolean"]
        ISSPECIAL["is_special: boolean"]
    end
    
    subgraph "Usage Examples"
        NOUNS["Nouns: 'lamp', 'key', 'door'"]
        VERBS["Verbs: 'take', 'open', 'examine'"]
        DIRS["Directions: 'north', 'up', 'out'"]
    end
    
    ISNOUN --> NOUNS
    ISVERB --> VERBS
    ISDIR --> DIRS
```

Sources: [jericho/jericho.py:131-214]()

## Action Generation System

The action generation system automatically creates valid actions from grammar templates and identified interactive objects, enabling systematic exploration of the action space.

### TemplateActionGenerator Architecture

```mermaid
graph TB
    subgraph "Input Processing"
        BINDINGS["rom_bindings"]
        GRAMMAR["grammar string"]
        MAXWORD["max_word_length"]
    end
    
    subgraph "Template Processing"
        PREPROCESS["_preprocess_templates()"]
        VERBSELECT["Verb Selection by Usage"]
        ILLEGAL["Filter ILLEGAL_ACTIONS"]
        NOEFFECT["Filter NO_EFFECT_ACTIONS"]
    end
    
    subgraph "Action Generation"
        GENACTIONS["generate_actions(objs)"]
        GENTEMPLATES["generate_template_actions(objs, obj_ids)"]
        FILLHOLES["Fill Template Holes"]
    end
    
    subgraph "Template Types"
        ZEROHOLES["Zero holes: 'north', 'inventory'"]
        ONEHOLE["One hole: 'take OBJ', 'examine OBJ'"]
        TWOHOLES["Two holes: 'put OBJ on OBJ'"]
    end
    
    BINDINGS --> GRAMMAR
    GRAMMAR --> PREPROCESS
    PREPROCESS --> VERBSELECT
    VERBSELECT --> ILLEGAL
    ILLEGAL --> NOEFFECT
    
    NOEFFECT --> GENACTIONS
    GENACTIONS --> FILLHOLES
    FILLHOLES --> ZEROHOLES
    FILLHOLES --> ONEHOLE
    FILLHOLES --> TWOHOLES
    
    style GENACTIONS fill:#e1f5fe
    style FILLHOLES fill:#f3e5f5
```

Sources: [jericho/template_action_generator.py:22-99]()

### Template Processing Pipeline

The system processes raw grammar strings into usable templates through several steps:

1. **Verb Selection**: When templates contain multiple verbs separated by `/`, the system selects the most commonly used verb based on frequency counts
2. **Filtering**: Templates starting with illegal actions or no-effect actions are filtered out
3. **Hole Filling**: Templates with `OBJ` placeholders are filled with interactive objects

```mermaid
graph LR
    subgraph "Raw Template"
        RAW["'take/get/carry OBJ'"]
    end
    
    subgraph "Processed Template"
        PROCESSED["'take OBJ'"]
    end
    
    subgraph "Generated Actions"
        ACTION1["'take lamp'"]
        ACTION2["'take key'"]
        ACTION3["'take door'"]
    end
    
    RAW --> PROCESSED
    PROCESSED --> ACTION1
    PROCESSED --> ACTION2
    PROCESSED --> ACTION3
```

Sources: [jericho/template_action_generator.py:42-65]()

## Game Support Framework

Jericho supports over 40 different interactive fiction games through a sophisticated binding system that maps game MD5 hashes to game-specific implementations.

### Game Binding System

```mermaid
graph TB
    subgraph "Game Detection"
        ROM["Game ROM File"]
        MD5["Calculate MD5 Hash"]
        LOOKUP["BINDINGS_DICT Lookup"]
    end
    
    subgraph "Binding Components"
        NAME["name: 'zork1'"]
        ROMNAME["rom: 'zork1.z5'"]
        SEED["seed: 12"]
        WALKTHROUGH["walkthrough: 'N/N/U/...'"]
        GRAMMAR["grammar: 'take OBJ;...'"]
        MAXWORD["max_word_length: 6"]
    end
    
    subgraph "C Implementation"
        VICTORY["zork1_victory()"]
        GAMEOVER["zork1_game_over()"]
        SCORE["zork1_get_score()"]
        MOVES["zork1_get_moves()"]
        CLEAN["zork1_clean_observation()"]
    end
    
    ROM --> MD5
    MD5 --> LOOKUP
    LOOKUP --> NAME
    LOOKUP --> ROMNAME
    LOOKUP --> SEED
    LOOKUP --> WALKTHROUGH
    LOOKUP --> GRAMMAR
    LOOKUP --> MAXWORD
    
    NAME --> VICTORY
    NAME --> GAMEOVER
    NAME --> SCORE
    NAME --> MOVES
    NAME --> CLEAN
    
    style MD5 fill:#e1f5fe
    style LOOKUP fill:#f3e5f5
```

Sources: [jericho/defines.py:79-137](), [jericho/game_info.py:17-24]()

### Game-Specific Implementations

Each supported game has a corresponding C implementation that provides customized behavior for victory detection, scoring, observation cleaning, and state management.

| Function Pattern | Purpose | Example |
|------------------|---------|---------|
| `{game}_victory()` | Detect win condition | `zork1_victory()` checks for "Inside the Barrow" |
| `{game}_game_over()` | Detect death/loss | `zork1_game_over()` checks for "You have died" |
| `{game}_get_score()` | Read score from memory | `zork1_get_score()` reads from addresses 8819-8820 |
| `{game}_get_moves()` | Read move count | `zork1_get_moves()` reads from addresses 8821-8822 |
| `{game}_clean_observation()` | Process game text | Remove prompts, clean formatting |

Sources: [frotz/src/games/zork1.c:53-136](), [frotz/src/games/omniquest.c:50-82]()

## Z-Machine Integration

The Python layer communicates with the Z-machine interpreter through a C library interface (`libfrotz.so`) that provides low-level access to game state and execution.

### C Library Interface

```mermaid
graph TB
    subgraph "Python ctypes Interface"
        LOADLIB["_load_frotz_lib()"]
        ARGTYPES["Function Argument Types"]
        RESTYPES["Function Return Types"]
    end
    
    subgraph "Core Z-Machine Operations"
        SETUP["frotz_lib.setup()"]
        STEP["frotz_lib.step()"]
        SHUTDOWN["frotz_lib.shutdown()"]
    end
    
    subgraph "State Access Functions"
        GETRAM["frotz_lib.getRAM()"]
        SETRAM["frotz_lib.setRAM()"]
        GETSTACK["frotz_lib.getStack()"]
        SETSTACK["frotz_lib.setStack()"]
        GETPC["frotz_lib.getPC()"]
        SETPC["frotz_lib.setPC()"]
    end
    
    subgraph "Game Information Functions"
        GETOBJ["frotz_lib.get_object()"]
        GETWORLDOBJS["frotz_lib.get_world_objects()"]
        GETSCORE["frotz_lib.get_score()"]
        GETMOVES["frotz_lib.get_moves()"]
        VICTORY["frotz_lib.victory()"]
        GAMEOVER["frotz_lib.game_over()"]
    end
    
    LOADLIB --> ARGTYPES
    ARGTYPES --> RESTYPES
    
    RESTYPES --> SETUP
    RESTYPES --> STEP
    RESTYPES --> SHUTDOWN
    
    RESTYPES --> GETRAM
    RESTYPES --> SETRAM
    RESTYPES --> GETSTACK
    RESTYPES --> SETSTACK
    
    RESTYPES --> GETOBJ
    RESTYPES --> GETWORLDOBJS
    RESTYPES --> GETSCORE
    RESTYPES --> GETMOVES
    
    style LOADLIB fill:#e1f5fe
    style STEP fill:#f3e5f5
```

Sources: [jericho/jericho.py:216-339]()

### State Management System

The system provides complete access to Z-machine internal state, enabling save/restore functionality and state-based analysis.

```mermaid
graph LR
    subgraph "Z-Machine State Components"
        RAM["RAM Memory"]
        STACK["Stack Memory"]
        PC["Program Counter"]
        SP["Stack Pointer"]
        FP["Frame Pointer"]
        FRAMECOUNT["Frame Count"]
        RNG["Random Number Generator"]
        NARRATIVE["Narrative Text"]
    end
    
    subgraph "State Operations"
        GETSTATE["get_state()"]
        SETSTATE["set_state()"]
        SERIALIZE["State Serialization"]
    end
    
    RAM --> GETSTATE
    STACK --> GETSTATE
    PC --> GETSTATE
    SP --> GETSTATE
    FP --> GETSTATE
    FRAMECOUNT --> GETSTATE
    RNG --> GETSTATE
    NARRATIVE --> GETSTATE
    
    GETSTATE --> SERIALIZE
    SERIALIZE --> SETSTATE
    
    SETSTATE --> RAM
    SETSTATE --> STACK
    SETSTATE --> PC
    SETSTATE --> SP
    SETSTATE --> FP
    SETSTATE --> FRAMECOUNT
    SETSTATE --> RNG
    SETSTATE --> NARRATIVE
```

Sources: [jericho/jericho.py:578-632]()

---

