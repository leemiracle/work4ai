<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/jericho · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/tutorial_quick.rst](docs/source/tutorial_quick.rst)
- [jericho/__init__.py](jericho/__init__.py)
- [jericho/jericho.py](jericho/jericho.py)
- [tests/test_valid_actions.py](tests/test_valid_actions.py)

</details>



## Purpose and Scope

Jericho is a Python interface connecting reinforcement learning agents with interactive fiction games. It provides a standardized environment wrapper around the Frotz Z-machine interpreter, enabling AI research on text-based adventure games through a clean, gym-like API.

This document introduces Jericho's core architecture, main components, and research-oriented features. For installation and basic usage, see [Getting Started](#2). For detailed API documentation, see [API Reference](#7). For information about supported games, see [Game Library](#6).

Sources: [README.md:19-21](), [jericho/jericho.py:371-383]()

## System Architecture

Jericho implements a layered architecture that separates the Python research interface from the underlying Z-machine interpreter implementation:

```mermaid
graph TB
    subgraph "Python Research Interface"
        FrotzEnv["FrotzEnv"]
        TemplateActionGenerator["TemplateActionGenerator"] 
        util["jericho.util"]
        defines["jericho.defines"]
    end
    
    subgraph "C Library Interface"
        frotz_lib["libfrotz.so"]
        _load_frotz_lib["_load_frotz_lib()"]
        ctypes_bindings["ctypes bindings"]
    end
    
    subgraph "Z-Machine Runtime"
        frotz_interpreter["Frotz Interpreter"]
        z_machine_state["Z-Machine State"]
        game_memory["Game Memory & Stack"]
    end
    
    subgraph "Game Data"
        z_files["Z5/Z8 Game Files"]
        game_bindings["Game Bindings"]
        walkthroughs["Walkthroughs"]
        grammar_templates["Grammar Templates"]
    end
    
    FrotzEnv --> _load_frotz_lib
    FrotzEnv --> TemplateActionGenerator
    _load_frotz_lib --> frotz_lib
    frotz_lib --> ctypes_bindings
    ctypes_bindings --> frotz_interpreter
    frotz_interpreter --> z_machine_state
    frotz_interpreter --> game_memory
    z_files --> frotz_interpreter
    game_bindings --> FrotzEnv
    grammar_templates --> TemplateActionGenerator
    walkthroughs --> defines
```

This architecture enables high-performance game execution through the C layer while providing rich research features through the Python layer.

Sources: [jericho/jericho.py:216-339](), [jericho/jericho.py:36-37](), [jericho/__init__.py:1-2]()

## Core Interface

The `FrotzEnv` class serves as the primary interface for interacting with interactive fiction games. It implements a reinforcement learning environment API similar to OpenAI Gym:

```mermaid
graph LR
    subgraph "FrotzEnv Core Methods"
        reset["reset()"]
        step["step(action)"]
        get_valid_actions["get_valid_actions()"]
        get_state["get_state()"]
        set_state["set_state(state)"]
    end
    
    subgraph "Game State Access"
        get_world_objects["get_world_objects()"]
        get_player_object["get_player_object()"]
        get_inventory["get_inventory()"]
        get_dictionary["get_dictionary()"]
    end
    
    subgraph "Game Info"
        get_score["get_score()"]
        get_moves["get_moves()"]
        victory["victory()"]
        game_over["game_over()"]
    end
    
    reset --> step
    step --> get_valid_actions
    get_state --> set_state
```

### Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `reset()` | Initialize/restart game | `(observation, info)` |
| `step(action)` | Execute action | `(observation, reward, done, info)` |
| `get_valid_actions()` | Generate valid actions | `list[str]` |
| `get_state()` | Serialize game state | `tuple` |
| `set_state(state)` | Restore game state | `None` |

The environment automatically handles game loading, state management, and provides rich introspection capabilities for research purposes.

Sources: [jericho/jericho.py:371-383](), [jericho/jericho.py:448-462](), [jericho/jericho.py:464-491](), [jericho/jericho.py:554-576]()

## Action Generation System

Jericho includes sophisticated action generation through the `TemplateActionGenerator` class, which automatically produces valid actions based on game grammar and current world state:

```mermaid
graph TB
    subgraph "Action Generation Pipeline"
        grammar_templates["Grammar Templates"]
        _identify_interactive_objects["_identify_interactive_objects()"]
        _score_object_names["_score_object_names()"]
        generate_actions["TemplateActionGenerator.generate_actions()"]
        _filter_candidate_actions["_filter_candidate_actions()"]
    end
    
    subgraph "Object Detection Sources"
        object_tree["Object Tree"]
        observation_text["Observation Text"]
        location_description["Location Description"] 
        inventory_description["Inventory Description"]
    end
    
    subgraph "Filtering & Validation"
        world_diff["World State Diff"]
        ctypes_filtering["C Library Filtering"]
        parallel_filtering["Parallel Processing"]
    end
    
    object_tree --> _identify_interactive_objects
    observation_text --> _identify_interactive_objects
    location_description --> _identify_interactive_objects
    inventory_description --> _identify_interactive_objects
    
    _identify_interactive_objects --> _score_object_names
    _score_object_names --> generate_actions
    grammar_templates --> generate_actions
    generate_actions --> _filter_candidate_actions
    
    _filter_candidate_actions --> world_diff
    _filter_candidate_actions --> ctypes_filtering
    _filter_candidate_actions --> parallel_filtering
```

The system uses natural language processing to extract objects from game text, scores object names by relevance, generates actions from grammar templates, and filters them by testing actual game state changes.

Sources: [jericho/jericho.py:33](), [jericho/jericho.py:554-576](), [jericho/jericho.py:840-936](), [jericho/jericho.py:938-1013]()

## Game Support Framework

Jericho supports 40+ interactive fiction games through a game-specific binding system that maps game files to customized behavior:

```mermaid
graph LR
    subgraph "Game Detection"
        story_file["Story File (.z5/.z8)"]
        md5_hash["MD5 Hash"]
        BINDINGS_DICT["defines.BINDINGS_DICT"]
        _load_bindings["_load_bindings()"]
    end
    
    subgraph "Game Bindings"
        name["name"]
        walkthrough["walkthrough"]  
        grammar["grammar"]
        seed["seed"]
        max_word_length["max_word_length"]
    end
    
    subgraph "C-Level Customization"
        frotz_lib_is_supported["frotz_lib.is_supported()"]
        game_specific_functions["Game-Specific C Functions"]
        victory_detection["Victory Detection"]
        score_calculation["Score Calculation"]
    end
    
    story_file --> md5_hash
    md5_hash --> BINDINGS_DICT
    BINDINGS_DICT --> _load_bindings
    _load_bindings --> name
    _load_bindings --> walkthrough
    _load_bindings --> grammar
    _load_bindings --> seed
    _load_bindings --> max_word_length
    
    story_file --> frotz_lib_is_supported
    frotz_lib_is_supported --> game_specific_functions
    game_specific_functions --> victory_detection
    game_specific_functions --> score_calculation
```

Games are identified by MD5 hash and mapped to specific configurations including walkthroughs, action grammars, and custom scoring logic implemented in C.

Sources: [jericho/jericho.py:342-360](), [jericho/jericho.py:420-421](), [jericho/jericho.py:414-418]()

## Research Features

Jericho provides several advanced features specifically designed for AI research on interactive fiction:

### World State Introspection

```mermaid
graph TB
    subgraph "Z-Machine State Access"
        ZObject["ZObject Structure"]
        get_world_objects["get_world_objects()"]
        get_player_location["get_player_location()"] 
        get_inventory["get_inventory()"]
        get_world_state_hash["get_world_state_hash()"]
    end
    
    subgraph "State Serialization"
        get_state["get_state()"]
        ram["RAM State"]
        stack["Stack State"] 
        registers["PC/SP/FP Registers"]
        rng_state["RNG State"]
    end
    
    subgraph "Change Detection"
        _world_changed["_world_changed()"]
        _get_world_diff["_get_world_diff()"]
        moved_objects["Moved Objects"]
        attribute_changes["Attribute Changes"]
    end
    
    ZObject --> get_world_objects
    get_world_objects --> get_player_location
    get_world_objects --> get_inventory
    get_world_objects --> get_world_state_hash
    
    get_state --> ram
    get_state --> stack  
    get_state --> registers
    get_state --> rng_state
    
    _world_changed --> _get_world_diff
    _get_world_diff --> moved_objects
    _get_world_diff --> attribute_changes
```

### Key Research Capabilities

| Feature | Purpose | Implementation |
|---------|---------|----------------|
| State Serialization | Save/restore exact game state | `get_state()` / `set_state()` |
| Object Tree Access | Inspect game world structure | `ZObject` / `get_world_objects()` |
| Action Validation | Generate semantically valid actions | `get_valid_actions()` |
| Change Detection | Track world state modifications | `_world_changed()` / `_get_world_diff()` |
| Dictionary Access | Query parser vocabulary | `get_dictionary()` |
| Walkthrough Replay | Reproduce optimal solutions | `get_walkthrough()` |

These features enable sophisticated research including state space exploration, action space analysis, world model learning, and systematic evaluation of agent capabilities.

Sources: [jericho/jericho.py:59-129](), [jericho/jericho.py:578-632](), [jericho/jericho.py:664-692](), [jericho/jericho.py:710-738](), [jericho/jericho.py:764-819]()

---

