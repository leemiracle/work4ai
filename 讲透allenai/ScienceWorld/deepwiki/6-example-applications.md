<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/ScienceWorld · page 6 Example Applications · fetched 2026-10-26 -->

# Example Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [examples/human.py](examples/human.py)
- [examples/random_agent.py](examples/random_agent.py)
- [examples/scienceworld-web-server-example.py](examples/scienceworld-web-server-example.py)

</details>



This document provides an overview of the example applications included with ScienceWorld. These applications demonstrate how to interact with the ScienceWorld environment using different interfaces and approaches. For information about the underlying Python API that powers these applications, see [Python API](#3).

## Overview

ScienceWorld includes three main example applications that showcase different ways to interact with the environment:

1. **Human Console**: A command-line interface for direct human interaction
2. **Random Agent**: An automated agent that selects random actions for testing
3. **Web Interface**: A browser-based interface for easier interaction

Each example demonstrates a different approach to working with the ScienceWorld API and can serve as a starting point for developing custom applications.

Sources: [examples/human.py:1-222](), [examples/random_agent.py:1-213](), [examples/scienceworld-web-server-example.py:1-218]()

## Example Applications Architecture

The example applications share a common architecture, all interfacing with the ScienceWorld environment through the Python API.

```mermaid
graph TD
    subgraph "Example Applications"
        HUMAN["Human Console Interface"]
        RANDOM["Random Agent"]
        WEB["Web Interface"]
    end
    
    subgraph "ScienceWorld API"
        ENV["ScienceWorldEnv Class"]
        STEP["env.step()"]
        RESET["env.reset()"]
        VALID["env.get_valid_action_object_combinations()"]
        LOOK["env.look()"]
    end
    
    HUMAN -->|"uses"| ENV
    RANDOM -->|"uses"| ENV
    WEB -->|"uses"| ENV
    
    ENV --- STEP
    ENV --- RESET
    ENV --- VALID
    ENV --- LOOK
```

Sources: [examples/human.py:25-153](), [examples/random_agent.py:8-137](), [examples/scienceworld-web-server-example.py:87-202]()

## Human Console

The Human Console provides a text-based interface for directly interacting with ScienceWorld through the command line.

### Features

- Interactive text-based interface
- Command history and auto-completion (when `prompt_toolkit` is available)
- Support for all ScienceWorld tasks and variations
- Environment simplification options
- Access to environment information (valid actions, objects, goal progress)
- Run history export

### Usage Flow

```mermaid
graph TD
    INIT["Initialize ScienceWorldEnv\n(human.py:37)"] -->|"load task"| LOAD["Load task and variation\n(human.py:43)"]
    LOAD -->|"reset"| RESET["Reset environment\n(human.py:48)"]
    RESET --> LOOP["Main interaction loop\n(human.py:95-141)"]
    LOOP -->|"user enters command"| INPUT["Process user input\n(human.py:114-115)"]
    INPUT -->|"env.step()"| STEP["Execute action in environment"]
    STEP -->|"observation, reward, isCompleted, info"| DISPLAY["Display results to user\n(human.py:117-120)"]
    DISPLAY --> VALID["Get valid actions\n(human.py:128)"]
    VALID -->|"display options"| PROMPT["Prompt for next action\n(human.py:130-137)"]
    PROMPT -->|"loop until exit\nor completion"| LOOP
    LOOP -->|"exit command"| HISTORY["Display run history\n(human.py:143-151)"]
```

### Implementation Details

The Human Console is implemented in `examples/human.py` and consists of:

- `userConsole()` - Main function that handles user interaction with the environment
- `build_simplification_str()` - Helper function to build simplification strings
- Command-line argument parsing for configuration

The application initializes the ScienceWorld environment, loads a specified task and variation, and then enters an interactive loop where users can type commands and see the results.

Example command-line usage:
```
python examples/human.py --task-num 13 --var-num 0 --teleport --open-doors
```

Sources: [examples/human.py:25-153](), [examples/human.py:156-210]()

## Random Agent

The Random Agent is an automated test agent that selects random valid actions at each step, useful for baseline testing or exploring the environment.

### Features

- Fully automated interaction
- Runs multiple episodes on different task variations
- Records scores and statistics
- Saves run histories to JSON files
- Configurable environment simplifications

### Random Agent Flow

```mermaid
graph TD
    INIT["Initialize ScienceWorldEnv\n(random_agent.py:20)"] --> TASK["Select task\n(random_agent.py:26)"]
    TASK --> EPISODES["Loop through episodes\n(random_agent.py:34)"]
    EPISODES --> VARIATION["Select random variation\n(random_agent.py:36)"]
    VARIATION --> LOAD["Load task with variation\n(random_agent.py:37)"]
    LOAD --> RESET["Reset environment\n(random_agent.py:40)"]
    RESET --> LOOP["Episode loop\n(random_agent.py:61)"]
    LOOP -->|"start with 'look around'"| STEP["Call env.step()\n(random_agent.py:66)"]
    STEP -->|"check completion"| CHECK{"isCompleted?"}
    CHECK --"No"--> VALID["Get valid actions\n(random_agent.py:90)"]
    VALID --> RANDOM["Select random action\n(random_agent.py:91)"]
    RANDOM --> STEP
    CHECK --"Yes"--> PROGRESS["Record goal progress\n(random_agent.py:104-105)"]
    PROGRESS --> SCORE["Record final score\n(random_agent.py:109)"]
    SCORE --> SAVE["Save run history\n(random_agent.py:117)"]
    SAVE --> NEXT{"More episodes?"}
    NEXT --"Yes"--> EPISODES
    NEXT --"No"--> REPORT["Report results\n(random_agent.py:127-134)"]
```

### Implementation Details

The Random Agent is implemented in `examples/random_agent.py` and consists of:

- `randomModel()` - Main function that runs the random agent
- Similar helper functions to the Human Console for simplifications and argument parsing

The agent runs for a specified number of episodes, randomly selecting valid actions at each step and recording the results.

Example command-line usage:
```
python examples/random_agent.py --task-num 13 --num-episodes 10 --env-step-limit 100
```

Sources: [examples/random_agent.py:8-137](), [examples/random_agent.py:140-209]()

## Web Interface

The Web Interface provides a browser-based way to interact with ScienceWorld, making it more accessible for users who prefer GUI interfaces.

### Features

- Browser-based user interface
- Task and variation selection through web forms
- HTML-formatted output with styling
- Session transcript export
- JSON history recording and export

### Web Interface Flow

```mermaid
graph TD
    START["Start web server\n(scienceworld-web-server-example.py:218)"] --> INIT["Initialize environment\n(scienceworld-web-server-example.py:96)"]
    INIT --> TASK["User selects task\n(scienceworld-web-server-example.py:104)"]
    TASK --> VARIATION["User selects variation\n(scienceworld-web-server-example.py:107-109)"]
    VARIATION --> LOAD["Load task\n(scienceworld-web-server-example.py:112)"]
    LOAD --> RESET["Reset environment\n(scienceworld-web-server-example.py:113)"]
    RESET --> LOOP["Main interaction loop\n(scienceworld-web-server-example.py:133-200)"]
    LOOP -->|"start with 'look around'"| STEP["Call env.step()\n(scienceworld-web-server-example.py:140)"]
    STEP --> DISPLAY["Display results in browser\n(scienceworld-web-server-example.py:144-149)"]
    DISPLAY --> LOG["Log to HTML and record history\n(scienceworld-web-server-example.py:152-181)"]
    LOG --> INPUT["Get user input from browser\n(scienceworld-web-server-example.py:188-189)"]
    INPUT --> LOOP
    LOOP -->|"completion or exit"| SAVE["Save JSON history\n(scienceworld-web-server-example.py:185)"]
```

### Implementation Details

The Web Interface is implemented in `examples/scienceworld-web-server-example.py` and consists of:

- `app()` - Main web application function
- `OutputLog` class - Helper for HTML formatting
- `saveJSONHistory()` - Function to export session history

The interface uses the `pywebio` library to create a simple web server that renders the environment output in HTML format.

Example command-line usage:
```
python examples/scienceworld-web-server-example.py --port 8080
```

After starting the server, users can connect to http://localhost:8080 in their web browser.

Sources: [examples/scienceworld-web-server-example.py:22-57](), [examples/scienceworld-web-server-example.py:59-81](), [examples/scienceworld-web-server-example.py:87-202]()

## Common Patterns Across Applications

All three example applications share common patterns for interacting with the ScienceWorld environment:

### Environment Initialization

```mermaid
sequenceDiagram
    participant App as "Example Application"
    participant Env as "ScienceWorldEnv"
    participant Backend as "Scala Backend"
    
    App->>Env: "Create ScienceWorldEnv instance"
    Env->>Backend: "Initialize py4j gateway"
    App->>Env: "load(taskName, variationIdx, simplificationStr)"
    Env->>Backend: "Load task in backend"
    App->>Env: "reset()"
    Env->>Backend: "Reset environment state"
    Backend-->>Env: "Return initial observation"
    Env-->>App: "Return initial observation"
```

### Action Execution Pattern

```mermaid
sequenceDiagram
    participant App as "Example Application"
    participant Env as "ScienceWorldEnv"
    participant Backend as "Scala Backend"
    
    App->>Env: "step(userInput)"
    Env->>Backend: "Process action"
    Backend->>Backend: "Update environment state"
    Backend-->>Env: "Return observation, reward, isCompleted, info"
    Env-->>App: "Return observation, reward, isCompleted, info"
    App->>Env: "get_valid_action_object_combinations()"
    Env-->>App: "Return valid actions"
```

### Simplification Options

All examples support the same simplification options to make tasks easier or focus on specific aspects:

| Simplification | Flag | Description |
|----------------|------|-------------|
| Teleportation | `--teleport` | Allows instant movement to any location |
| Self-Watering Plants | `--self-watering-plants` | Plants don't need frequent watering |
| Open Containers | `--open-containers` | All containers are opened by default |
| Open Doors | `--open-doors` | All doors are opened by default |
| No Electrical | `--no-electrical` | Removes electrical actions from action space |
| Easy Preset | `--simplifications-preset easy` | Applies all simplifications |

Sources: [examples/human.py:156-174](), [examples/random_agent.py:140-158]()

## Building Custom Applications

The example applications demonstrate the key patterns for building custom applications with ScienceWorld:

1. **Initialize the environment**:
   ```python
   from scienceworld import ScienceWorldEnv
   env = ScienceWorldEnv()
   ```

2. **Load a task and variation**:
   ```python
   env.load(taskName, variationIdx, simplificationStr)
   ```

3. **Reset the environment**:
   ```python
   initialObs, initialDict = env.reset()
   ```

4. **Interaction loop**:
   ```python
   while not isCompleted:
       observation, reward, isCompleted, info = env.step(action)
       # Process results
       # Choose next action
   ```

5. **Access environment information**:
   ```python
   valid_actions = env.get_valid_action_object_combinations()
   goal_progress = env.get_goal_progress()
   ```

By following these patterns and examining the example applications, developers can create custom agents, interfaces, or evaluation systems for ScienceWorld.

Sources: [examples/human.py:37-48](), [examples/random_agent.py:20-40](), [examples/scienceworld-web-server-example.py:96-113]()

---

