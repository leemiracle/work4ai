<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/streetlearn · page 6 User Interfaces · fetched 2026-10-26 -->

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [streetlearn/python/ui/BUILD](streetlearn/python/ui/BUILD)
- [streetlearn/python/ui/human_agent.py](streetlearn/python/ui/human_agent.py)
- [streetlearn/python/ui/oracle_agent.py](streetlearn/python/ui/oracle_agent.py)

</details>



This document covers the PyGame-based user interface systems in StreetLearn that enable human interaction with navigation environments and provide visualization capabilities for different agent types. The UI layer serves as the primary interface between human users, agent behaviors, and the StreetLearn environment system.

For information about the underlying environment system that these UIs interact with, see [Environment System](#3). For details about the agents that these UIs support, see [Agent System](#4).

## UI Architecture Overview

The StreetLearn UI system is built on PyGame and provides interactive interfaces for multiple agent types. The system follows a modular design where each agent type has its own dedicated UI implementation while sharing common rendering and input handling patterns.

```mermaid
graph TB
    subgraph "UI Layer"
        HumanAgentUI["human_agent.py"]
        OracleAgentUI["oracle_agent.py"]
        InstructionOracleUI["instruction_following_oracle_agent.py"]
        BatchedOracleUI["batched_oracle_agent.py"]
        ScanAgentUI["scan_agent.py"]
    end
    
    subgraph "PyGame Components"
        PyGameInit["pygame.init()"]
        PyGameDisplay["pygame.display"]
        PyGameEvent["pygame.event"]
        PyGameFont["pygame.font"]
        PyGameSurface["pygame.surfarray"]
    end
    
    subgraph "StreetLearn Environment"
        StreetLearnEnv["streetlearn.StreetLearn"]
        GameInstances["Game Instances"]
        Observations["Observation Dictionary"]
    end
    
    subgraph "Visual Components"
        ViewImage["view_image_hwc"]
        GraphImage["graph_image_hwc"]
        Thumbnails["thumbnails"]
        Instructions["instructions"]
    end
    
    HumanAgentUI --> PyGameInit
    OracleAgentUI --> PyGameInit
    
    PyGameInit --> PyGameDisplay
    PyGameInit --> PyGameEvent
    PyGameInit --> PyGameFont
    
    HumanAgentUI --> StreetLearnEnv
    OracleAgentUI --> StreetLearnEnv
    
    StreetLearnEnv --> GameInstances
    StreetLearnEnv --> Observations
    
    Observations --> ViewImage
    Observations --> GraphImage
    Observations --> Thumbnails
    Observations --> Instructions
    
    ViewImage --> PyGameSurface
    GraphImage --> PyGameSurface
```

Sources: [streetlearn/python/ui/BUILD:23-76](), [streetlearn/python/ui/human_agent.py:240-254](), [streetlearn/python/ui/oracle_agent.py:194-196]()

## Human Agent Interface

The `HumanAgent` provides a comprehensive PyGame interface for manual navigation through StreetLearn environments. It supports multiple game types with adaptive screen layouts and keyboard controls.

### Screen Layout System

The UI dynamically adjusts its layout based on the selected game type:

```mermaid
graph TB
    subgraph "Simple Games (coin_game, courier_game)"
        ViewImg1["view_image_hwc<br/>(400x400)"]
        GraphImg1["graph_image_hwc<br/>(400x400)"]
        ViewImg1 --> ConcatSimple["Vertical Concatenation"]
        GraphImg1 --> ConcatSimple
        ConcatSimple --> SimpleScreen["Screen: 400x800"]
    end
    
    subgraph "Instruction Games"
        ViewImg2["view_image_hwc<br/>(400x400)"]
        GraphImg2["graph_image_hwc<br/>(400x400)"]
        ThumbImg["thumbnails<br/>(subsampled)"]
        InstrText["instructions<br/>(text overlay)"]
        
        ViewImg2 --> ComplexLayout["Complex Layout"]
        GraphImg2 --> ComplexLayout
        ThumbImg --> ComplexLayout
        InstrText --> ComplexLayout
        ComplexLayout --> ComplexScreen["Screen: (width + thumb_width + text_width) x 800"]
    end
```

Sources: [streetlearn/python/ui/human_agent.py:117-137](), [streetlearn/python/ui/human_agent.py:242-252]()

### Keyboard Control System

The human agent implements a comprehensive keyboard control scheme:

| Key | Action | Implementation |
|-----|--------|----------------|
| `SPACE` | Move forward | `action_spec['move_forward']` |
| `A` | Rotate left | `-FLAGS.horizontal_rot * action_spec['horizontal_rotation']` |
| `D` | Rotate right | `FLAGS.horizontal_rot * action_spec['horizontal_rotation']` |
| `W` | Look up | `-FLAGS.vertical_rot * action_spec['vertical_rotation']` |
| `S` | Look down | `FLAGS.vertical_rot * action_spec['vertical_rotation']` |
| `I` | Zoom in | `action_spec['map_zoom']` |
| `O` | Zoom out | `-action_spec['map_zoom']` |
| `P` | Screenshot | Save to `/tmp/human_agent_YYYYMMDD_HHMMSS.bmp` |
| `ESC` | Exit | Terminate application |

Sources: [streetlearn/python/ui/human_agent.py:164-190]()

### Configuration System

The human agent uses extensive command-line configuration:

```mermaid
graph LR
    subgraph "Visual Configuration"
        WidthFlag["--width (400)"]
        HeightFlag["--height (400)"]
        FOVFlag["--field_of_view (60)"]
        ZoomFlag["--graph_zoom (1)"]
    end
    
    subgraph "Game Configuration"
        GameFlag["--game"]
        DatasetFlag["--dataset_path"]
        InstructionFlag["--instruction_file"]
        FrameCapFlag["--frame_cap (1000)"]
    end
    
    subgraph "Behavior Configuration"
        HRotFlag["--horizontal_rot (10)"]
        VRotFlag["--vertical_rot (10)"]
        RewardWaypointFlag["--reward_at_waypoint (0.5)"]
        RewardGoalFlag["--reward_at_goal (1.0)"]
    end
    
    subgraph "Environment Config Dictionary"
        ConfigDict["config dictionary"]
    end
    
    WidthFlag --> ConfigDict
    HeightFlag --> ConfigDict
    GameFlag --> ConfigDict
    HRotFlag --> ConfigDict
```

Sources: [streetlearn/python/ui/human_agent.py:40-70](), [streetlearn/python/ui/human_agent.py:195-218]()

## Oracle Agent Interface

The `OracleAgent` provides a streamlined PyGame interface focused on visualizing automated navigation using ground truth information.

### Oracle Navigation System

```mermaid
graph TB
    subgraph "Oracle Decision Logic"
        CurrentPano["current_pano_id"]
        NextPano["next_pano_id"]
        Bearing["bearing_to_next_pano"]
        
        CurrentPano --> BearingCheck["bearing > TOL_BEARING?"]
        NextPano --> BearingCheck
        Bearing --> BearingCheck
    end
    
    subgraph "Action Selection"
        BearingCheck -->|"Yes"| RotateRight["Rotate Right<br/>FLAGS.horizontal_rot * action_spec['horizontal_rotation']"]
        BearingCheck -->|"bearing < -TOL_BEARING"| RotateLeft["Rotate Left<br/>-FLAGS.horizontal_rot * action_spec['horizontal_rotation']"]
        BearingCheck -->|"Within tolerance"| MoveForward["Move Forward<br/>action_spec['move_forward']"]
    end
    
    subgraph "Loop Detection"
        SeenPanos["seen_pano_ids counter"]
        LoopThreshold["visits > 180° / horizontal_rot"]
        TeleportAction["env.goto(next_pano_id, random_yaw)"]
        
        SeenPanos --> LoopThreshold
        LoopThreshold -->|"True"| TeleportAction
    end
```

Sources: [streetlearn/python/ui/oracle_agent.py:127-168](), [streetlearn/python/ui/oracle_agent.py:53]()

### Oracle UI Features

The oracle interface includes specialized functionality:

- **Video Recording**: Press `V` to start, `C` to stop recording frames to `/tmp/oracle_agent_video_*`
- **Statistics Logging**: Optional `--stats_path` for episode performance metrics
- **Zoom Controls**: `I`/`O` keys for map zoom
- **Loop Breaking**: Automatic teleportation when stuck in navigation loops

Sources: [streetlearn/python/ui/oracle_agent.py:77-86](), [streetlearn/python/ui/oracle_agent.py:99-103](), [streetlearn/python/ui/oracle_agent.py:119-123]()

## Visual Rendering System

The UI system uses a consistent approach to render environment observations:

```mermaid
graph TB
    subgraph "Observation Processing"
        EnvObs["env.observation()"]
        ViewImageHWC["observation['view_image_hwc']"]
        GraphImageHWC["observation['graph_image_hwc']"]
        Thumbnails["observation['thumbnails']"]
        Instructions["observation['instructions']"]
    end
    
    subgraph "PyGame Rendering"
        ScreenBuffer["screen_buffer numpy array"]
        SurfArray["pygame.surfarray.blit_array()"]
        DisplayUpdate["pygame.display.update()"]
    end
    
    subgraph "Layout Assembly"
        ViewImageHWC --> ScreenBuffer
        GraphImageHWC --> ScreenBuffer
        Thumbnails --> SubsamplingLogic["Subsampling Logic"]
        SubsamplingLogic --> ScreenBuffer
        Instructions --> TextRendering["blit_instruction()"]
        TextRendering --> ScreenBuffer
    end
    
    ScreenBuffer --> SurfArray
    SurfArray --> DisplayUpdate
```

Sources: [streetlearn/python/ui/human_agent.py:113-137](), [streetlearn/python/ui/oracle_agent.py:92-96]()

### Text Rendering System

The `blit_instruction` function provides multiline text rendering with word wrapping:

```mermaid
graph LR
    subgraph "Text Processing"
        InstructionStr["instruction.split()"]
        WordList["List of words"]
        SpaceWidth["font.size(' ')[0]"]
    end
    
    subgraph "Layout Logic"
        WordList --> WidthCheck["x + word_width >= x_max?"]
        WidthCheck -->|"Yes"| NewLine["x = x_min; y += word_height"]
        WidthCheck -->|"No"| BlitWord["screen.blit(word_surface, (x, y))"]
        NewLine --> BlitWord
        BlitWord --> IncrementX["x += word_width + space_width"]
    end
    
    subgraph "Color Coding"
        CurrentStep["current_step"]
        ColorWaypoint["COLOR_WAYPOINT (0, 178, 178)"]
        ColorGoal["COLOR_GOAL (255, 0, 0)"]
        ColorInstruction["COLOR_INSTRUCTION (255, 255, 255)"]
    end
```

Sources: [streetlearn/python/ui/human_agent.py:77-90](), [streetlearn/python/ui/human_agent.py:72-74](), [streetlearn/python/ui/human_agent.py:144-152]()

## UI Agent Registry

The BUILD file defines multiple UI executables as entry points:

| Binary | Purpose | Primary Game Support |
|--------|---------|---------------------|
| `human_agent` | Manual keyboard control | All games with full UI |
| `oracle_agent` | Automated optimal navigation | `courier_game` focused |
| `instruction_following_oracle_agent` | Oracle with instruction following | Instruction-based games |
| `batched_oracle_agent` | Parallel oracle processing | Batch evaluation |
| `scan_agent` | Environment scanning utility | Data exploration |

All UI agents depend on:
- `//streetlearn/engine/python:streetlearn_engine` - C++ engine bindings
- `//streetlearn/python/environment:environment_py` - Python environment layer

Sources: [streetlearn/python/ui/BUILD:23-76]()

---

