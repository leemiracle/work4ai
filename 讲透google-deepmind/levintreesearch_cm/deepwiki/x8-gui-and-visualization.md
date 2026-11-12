<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/levintreesearch_cm · extra page GUI and Visualization · fetched 2026-10-26 -->

# GUI and Visualization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lts-cm/gui.rkt](lts-cm/gui.rkt)
- [lts-cm/misc.rkt](lts-cm/misc.rkt)

</details>



This page documents the Play-World GUI and visualization system in the LTS-CM codebase. The GUI provides interactive visualization capabilities for exploring problem domains, viewing solutions, and replaying action sequences. It serves as a crucial tool for debugging, demonstration, and analysis of the Levin Tree Search algorithm's behavior on various domains.

## Overview and Purpose

The visualization system provides:
1. Interactive playback of solution trajectories
2. Manual exploration of action spaces
3. Visual representation of problem states
4. Probability visualization for action selection

The GUI is domain-agnostic, using a pluggable architecture where domain-specific visualization functions can be supplied to render different problem types (Sliding Tile Puzzle, Sokoban, etc.).

Sources: [lts-cm/gui.rkt:1-196]()

## Architecture

The following diagram illustrates how the GUI system integrates with the rest of the LTS-CM framework:

```mermaid
flowchart TD
    subgraph "GUI System"
        play_world["play-world"]
        make_play_domain["make-play-domain+main"]
        
        play_world -->|creates| GUI_Window["GUI Window"]
        make_play_domain -->|produces| Domain_GUI["Domain-Specific GUI"]
        Domain_GUI -->|uses| play_world
    end
    
    subgraph "Domain Implementation"
        state_to_pict["state->pict"]
        do_action["do-action"]
        key_event["key-event->action"]
        solution_check["solution?"]
    end
    
    subgraph "Solution Replay"
        act_seq["Action Sequence"]
        pcond_seq["Probability Sequence"]
        log_files["Log Files"]
    end
    
    Domain_Implementation["Domain Implementation"] -->|provides| state_to_pict
    Domain_Implementation -->|provides| do_action
    Domain_Implementation -->|provides| key_event
    Domain_Implementation -->|provides| solution_check
    
    play_world -->|displays| state_to_pict
    play_world -->|executes| do_action
    play_world -->|uses| key_event
    play_world -->|checks| solution_check
    
    log_files -->|contain| act_seq
    log_files -->|contain| pcond_seq
    act_seq -->|fed to| play_world
    pcond_seq -->|visualized by| play_world

    GUI_Window -->|user controls| UI_Controls["Space: Step\nEnter: Run\nBackspace: Undo\nHome: Reset"]
```

Sources: [lts-cm/gui.rkt:35-133](), [lts-cm/gui.rkt:135-195]()

## Core Components

### play-world Function

The `play-world` function is the central component of the visualization system. It creates an interactive window displaying a problem state and allows navigation through action sequences.

```mermaid
classDiagram
    class play_world {
        +state->pict
        +do-action
        +key-event->action
        +user-actions-label
        +label
        +act-seq
        +pcond-seq
        +solution?
    }
    
    class GUI_Controls {
        +Step forward (Space)
        +Run sequence (Enter)
        +Undo action (Backspace)
        +Reset (Home)
    }
    
    class GUI_Display {
        +Header
        +State visualization
        +Time step
        +Solution status
        +Probability visualization
    }
    
    play_world --> GUI_Controls: creates
    play_world --> GUI_Display: renders
```

The function takes the following key parameters:
- `wld`: The initial state to visualize
- `state->pict`: Function to convert a state to a graphical representation
- `do-action`: Function to apply an action to a state, producing a new state
- `key-event->action`: Function that maps key presses to domain actions
- `solution?`: Predicate that determines if a state is a solution

Optional parameters:
- `act-seq`: Sequence of actions for automatic replay
- `pcond-seq`: Sequence of probabilities for visualizing model confidence
- `label`: Window title
- `user-actions-label`: Text describing available user actions

Sources: [lts-cm/gui.rkt:35-133]()

### make-play-domain+main Function

This utility function creates domain-specific visualization capabilities by packaging together:
1. A domain-specific play function
2. A main function for command-line launching

```mermaid
flowchart LR
    subgraph "make-play-domain+main"
        play_domain["play-domain"]
        play_domain_log_file["play-domain-log-file"]
        play_domain_choose_from["play-domain-choose-from"]
        main_function["main function"]
    end
    
    subgraph "Required Parameters"
        here["file location"]
        label["window label"]
        to_pict["->pict function"]
        do_action["do-action function"]
        action_codes["action-codes"]
        solution_check["solution? function"]
        spec_to_state["spec->state function"]
    end
    
    Required_Parameters -->|configures| make_play_domain+main
    
    make_play_domain+main -->|returns| play_domain
    make_play_domain+main -->|returns| main_function
    
    main_function -->|may call| play_domain_log_file
    main_function -->|may call| play_domain_choose_from
    
    play_domain_log_file -->|calls| play_domain
    play_domain_choose_from -->|calls| play_domain_log_file
    
    play_domain -->|calls| play_world["play-world"]
```

This function is used to create domain-specific visualization modules that handle the peculiarities of different problem domains.

Sources: [lts-cm/gui.rkt:135-195]()

## Replay System

The GUI includes functionality to replay solution sequences, either step-by-step or automatically:

1. **Manual stepping**: Press Space to advance one action at a time
2. **Automatic replay**: Press Enter to continuously execute the action sequence
3. **Playback speed**: Controlled by the global `*replay-speed*` parameter

The replay system also visualizes action probabilities when available, providing insight into the model's confidence in each action.

```mermaid
sequenceDiagram
    participant User
    participant GUI
    participant State
    participant ActionSeq as "Action Sequence"
    participant ProbSeq as "Probability Sequence"

    User->>GUI: Press Enter (run)
    activate GUI
    
    loop Until end of sequence
        GUI->>ActionSeq: Get next action
        ActionSeq-->>GUI: Return action
        GUI->>State: Apply action
        State-->>GUI: Return new state
        GUI->>ProbSeq: Get probability
        ProbSeq-->>GUI: Return probability
        GUI->>GUI: Update display
        GUI->>GUI: Sleep (*replay-speed*)
    end
    
    deactivate GUI
    
    User->>GUI: Press Space (step)
    GUI->>ActionSeq: Get next action
    ActionSeq-->>GUI: Return action
    GUI->>State: Apply action
    State-->>GUI: Return new state
    GUI->>GUI: Update display
    
    User->>GUI: Press Backspace (undo)
    GUI->>State: Revert to previous state
    GUI->>GUI: Update display
    
    User->>GUI: Press Home (reset)
    GUI->>State: Reset to initial state
    GUI->>GUI: Update display
```

Sources: [lts-cm/gui.rkt:48-133](), [lts-cm/misc.rkt:33]()

## Loading Solutions from Log Files

The system can load and visualize solutions from log files generated during search:

1. **Direct file specification**: Provide a log file path with the `*log*` global parameter
2. **Directory browsing**: Choose from files in a directory specified by `*log-dir*`

Log files contain:
- Problem specification
- Action sequence
- Probability sequence

```mermaid
flowchart TD
    subgraph "Log File Loading"
        log_file["Log File (.rktd)"]
        problems_file["Problems File"]
        
        log_file -->|references| problems_file
        log_file -->|contains| act_seq["Action Sequence"]
        log_file -->|contains| pcond_seq["Probability Sequence"]
        log_file -->|contains| problem_num["Problem Number"]
        
        problems_file -->|contains| problem_specs["Problem Specifications"]
        
        problem_num -->|selects| problem_spec["Specific Problem"]
        problem_specs -->|contains| problem_spec
        
        problem_spec -->|converted via| spec_to_state["spec->state"]
        spec_to_state -->|produces| initial_state["Initial State"]
        
        initial_state -->|visualized with| play_domain["play-domain"]
        act_seq -->|fed to| play_domain
        pcond_seq -->|fed to| play_domain
    end
```

Sources: [lts-cm/gui.rkt:142-179](), [lts-cm/gui.rkt:181-193]()

## Integration with Problem Domains

Domain implementations must provide several key functions to integrate with the visualization system:

| Function | Purpose |
|----------|---------|
| `state->pict` | Converts a domain state to a graphical representation |
| `do-action` | Applies an action to a state, producing a new state |
| `key-event->action` | Maps keyboard events to domain actions |
| `solution?` | Determines if a state represents a solution |
| `spec->state` | Converts a problem specification to an initial state |

This pluggable architecture allows the visualization system to work with any problem domain that can implement these interfaces.

Sources: [lts-cm/gui.rkt:135-157]()

## User Interface

The GUI provides a consistent user interface across all domains:

- **Header**: Shows available commands and domain-specific user actions
- **State visualization**: Domain-specific rendering of the current state
- **Time step counter**: Shows the current position in the action sequence
- **Solution status**: Indicates when a solution state is reached
- **Probability visualization**: Shows model confidence when available

All GUIs implement a common set of keyboard controls:
- **Space**: Step forward one action
- **Enter**: Automatically run through the action sequence
- **Backspace**: Undo the last action
- **Home**: Reset to the initial state
- **Domain-specific keys**: Perform domain-specific actions (e.g., arrow keys for movement)

Sources: [lts-cm/gui.rkt:58-80](), [lts-cm/gui.rkt:92-132]()

---

