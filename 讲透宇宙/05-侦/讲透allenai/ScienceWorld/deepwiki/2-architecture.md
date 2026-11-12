<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/ScienceWorld · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scienceworld/scienceworld.jar](scienceworld/scienceworld.jar)
- [scienceworld/scienceworld.py](scienceworld/scienceworld.py)
- [simulator/build.sbt](simulator/build.sbt)
- [simulator/src/main/scala/scienceworld/runtime/AgentInterface.scala](simulator/src/main/scala/scienceworld/runtime/AgentInterface.scala)
- [simulator/src/main/scala/scienceworld/runtime/pythonapi/PythonInterface.scala](simulator/src/main/scala/scienceworld/runtime/pythonapi/PythonInterface.scala)
- [tests/test_scienceworld.py](tests/test_scienceworld.py)

</details>



This document provides a comprehensive overview of the ScienceWorld system architecture, detailing the core components and their interactions. ScienceWorld is a text-based simulation environment designed for elementary science tasks, featuring a Python frontend that communicates with a Scala backend through a bridge layer.

For information about installing and setting up ScienceWorld, see [Installation & Setup](#1.1). For details about specific Python API methods, see [Python API](#3).

## Overall System Architecture

The ScienceWorld architecture follows a layered design pattern with three main layers:

```mermaid
graph TD
    subgraph "Python Layer (Frontend)"
        PY["ScienceWorldEnv"]
        UTILS["Utility Functions"]
        CONSTANTS["Constants"]
    end
    
    subgraph "Bridge Layer"
        JG["py4j Gateway"]
    end
    
    subgraph "Scala Layer (Backend)"
        PI["PythonInterface"]
        AI["AgentInterface"]
        IP["InputParser"]
        TASK["Task System"]
        ENV["Environment Objects"]
        ACT["Action System"]
    end
    
    PY -->|"sends commands"| JG
    JG -->|"translates calls"| PI
    PI -->|"controls"| AI
    AI -->|"parses input"| IP
    AI -->|"executes actions"| ACT
    AI -->|"manages"| ENV
    TASK -->|"defines goals"| AI
    ACT -->|"modifies"| ENV
    
    JG -->|"returns observations"| PY
```

Sources: [scienceworld/scienceworld.py:17-162](). [simulator/src/main/scala/scienceworld/runtime/pythonapi/PythonInterface.scala:26-141]().

1. **Python Layer**: Provides the front-facing API for agents to interact with the environment.
2. **Bridge Layer**: Uses py4j to enable communication between Python and Scala.
3. **Scala Layer**: Contains the simulation logic, environment objects, and task definitions.

## Initialization and Communication Flow

The following diagram illustrates how ScienceWorld initializes and establishes communication between the Python and Scala layers:

```mermaid
sequenceDiagram
    participant Client as "Agent/Client"
    participant SWEnv as "ScienceWorldEnv"
    participant Gateway as "py4j Gateway"
    participant PI as "PythonInterface"
    participant AI as "AgentInterface"
    
    Client->>SWEnv: ScienceWorldEnv(taskName)
    SWEnv->>SWEnv: launch_gateway(JAR_PATH)
    SWEnv->>Gateway: JavaGateway(port)
    SWEnv->>Gateway: get_callback_server().get_listening_port()
    SWEnv->>Gateway: resetCallbackClient()
    SWEnv->>PI: server = jvm.scienceworld.runtime.pythonapi.PythonInterface()
    SWEnv->>PI: load(taskName, variationIdx, simplificationStr)
    PI->>PI: doLoad(taskName, variationIdx, simplificationStr)
    PI->>AI: new AgentInterface(universe, agent, task, simplificationStr)
    PI-->>SWEnv: Return error string (empty if successful)
    SWEnv->>SWEnv: reset()
    SWEnv->>PI: step("look around")
    PI->>AI: step("look around")
    AI-->>PI: (observation, score, isCompleted)
    PI-->>SWEnv: observation
    SWEnv-->>Client: (observation, info)
```

Sources: [scienceworld/scienceworld.py:23-85](). [simulator/src/main/scala/scienceworld/runtime/pythonapi/PythonInterface.scala:54-145]().

Key points:
1. The Python `ScienceWorldEnv` initializes by starting a JVM with the Scala code
2. It establishes bidirectional communication through py4j
3. A task is loaded, creating an environment with the appropriate objects and goals
4. The agent can then interact with the environment through the `step()` method

## Core Components

### ScienceWorldEnv (Python)

The `ScienceWorldEnv` class serves as the main interface for agents to interact with ScienceWorld. It handles:

```mermaid
classDiagram
    class ScienceWorldEnv {
        -_gateway: JavaGateway
        -server: PythonInterface
        -taskName: String
        -simplificationStr: String
        -variationIdx: int
        -lastStepScore: int
        -envStepLimit: int
        -goldPathGenerated: bool
        
        +__init__(taskName, serverPath, envStepLimit)
        +load(taskName, variationIdx, simplificationStr, generateGoldPath)
        +reset()
        +step(input_str)
        +close()
        +get_task_names()
        +get_possible_actions()
        +get_possible_objects()
        +get_valid_action_object_combinations()
        +get_gold_action_sequence()
        +look()
        +inventory()
        +taskdescription()
    }
```

Sources: [scienceworld/scienceworld.py:17-162]().

### PythonInterface (Scala)

The `PythonInterface` class is the entry point for py4j calls from Python. It manages:

```mermaid
classDiagram
    class PythonInterface {
        -agentInterface: Option[AgentInterface]
        -agent: Option[Agent]
        -taskStr: String
        -taskVariationIdx: Int
        -simplificationStr: String
        -goldActionsStr: Array[String]
        -score: Double
        -isComplete: Boolean
        -taskMaker: TaskMaker1
        
        +load(taskStr, variationIdx, simplificationStr, generateGoldPath)
        +reset()
        +getTaskNames()
        +getTaskMaxVariations(taskName)
        +getVariationsTrain()
        +getVariationsDev()
        +getVariationsTest()
        +getSimplificationsUsed()
        +getPossibleSimplifications()
        +getGoldActionSequence()
        +getPossibleActions()
        +getPossibleObjects()
        +getValidActionObjectCombinations()
        +getScore()
        +getCompleted()
        +step(userInputString)
        +freeActionLook()
        +freeActionInventory()
        +freeActionTaskDesc()
    }
```

Sources: [simulator/src/main/scala/scienceworld/runtime/pythonapi/PythonInterface.scala:26-141]().

### AgentInterface (Scala)

The `AgentInterface` class handles the core simulation logic:

```mermaid
classDiagram
    class AgentInterface {
        -universe: EnvObject
        -agent: Agent
        -task: Task
        -simplificationStr: String
        -objMonitor: ObjMonitor
        -actionHandler: ActionHandler
        -inputParser: InputParser
        -curIter: Int
        
        +getAgentVisibleObjects()
        +getPossibleActions()
        +getPossibleObjects()
        +getValidActionObjectCombinations()
        +processUserInput(inputStr, universe)
        +runFreeAction(action)
        +freeActionLook()
        +freeActionInventory()
        +freeActionTaskDesc()
        +step(userInputStr)
    }
```

Sources: [simulator/src/main/scala/scienceworld/runtime/AgentInterface.scala:19-596]().

## Action Flow

The following diagram illustrates the flow of an action through the system:

```mermaid
graph TD
    subgraph "User/Agent"
        INPUT["Agent Input (e.g., 'look around')"]
    end
    
    subgraph "Python Layer"
        PYAPI["ScienceWorldEnv.step()"]
    end
    
    subgraph "Bridge Layer"
        BRIDGE["py4j Gateway"]
    end
    
    subgraph "Scala Layer"
        PI_STEP["PythonInterface.step()"]
        AI_STEP["AgentInterface.step()"]
        INPUT_PARSE["InputParser.parse()"]
        ACTION_QUEUE["ActionHandler.queueAction()"]
        ACTION_EXEC["ActionHandler.runQueuedActions()"]
        UNIVERSE_TICK["universe.tick()"]
        GOAL_CHECK["task.goalSequence.tick()"]
    end
    
    INPUT -->|"1. Agent provides input"| PYAPI
    PYAPI -->|"2. Forwards to Scala"| BRIDGE
    BRIDGE -->|"3. Translates call"| PI_STEP
    PI_STEP -->|"4. Passes to AgentInterface"| AI_STEP
    AI_STEP -->|"5. Parses input"| INPUT_PARSE
    INPUT_PARSE -->|"6. Creates Action object"| ACTION_QUEUE
    ACTION_QUEUE -->|"7. Executes actions"| ACTION_EXEC
    ACTION_EXEC -->|"8. Modifies environment"| UNIVERSE_TICK
    UNIVERSE_TICK -->|"9. Updates object states"| GOAL_CHECK
    GOAL_CHECK -->|"10. Checks goal progress"| AI_STEP
    AI_STEP -->|"11. Returns (observation, score, isCompleted)"| PI_STEP
    PI_STEP -->|"12. Returns observation"| BRIDGE
    BRIDGE -->|"13. Returns to Python"| PYAPI
    PYAPI -->|"14. Returns (observation, reward, isCompleted, infos)"| INPUT
```

Sources: [scienceworld/scienceworld.py:410-452](). [simulator/src/main/scala/scienceworld/runtime/pythonapi/PythonInterface.scala:351-404](). [simulator/src/main/scala/scienceworld/runtime/AgentInterface.scala:504-594]().

## Environment Object System

ScienceWorld uses a composable object system where environment objects can have various properties:

```mermaid
classDiagram
    class EnvObject {
        +name: String
        +objType: String
        +uuid: UUID
        +containedObjects: Set[EnvObject]
        +addObject(obj)
        +removeObject(obj)
        +tick()
        +getReferents(): Array[String]
    }
    
    class MaterialProperties {
        +temperatureC: Double
        +stateOfMatter: String
        +electricallyConductive: Boolean
        +boilingPoint: Double
        +meltingPoint: Double
    }
    
    class ContainerProperties {
        +isContainer: Boolean
        +isOpen: Boolean
        +isClosable: Boolean
        +maxContentVolume: Double
    }
    
    class DeviceProperties {
        +isActivable: Boolean
        +isActivated: Boolean
        +isUsable: Boolean
        +isBroken: Boolean
    }
    
    class LifeProperties {
        +lifeformType: String
        +minTemp: Double
        +maxTemp: Double
        +isDead: Boolean
        +lifespanTypical: Int
    }
    
    EnvObject "1" -- "0..1" MaterialProperties: "may have"
    EnvObject "1" -- "0..1" ContainerProperties: "may have"
    EnvObject "1" -- "0..1" DeviceProperties: "may have"
    EnvObject "1" -- "0..1" LifeProperties: "may have"
    EnvObject "1" *-- "many" EnvObject: "contains"
```

Sources: [scienceworld/scienceworld.py:292-301]().

## Task System and Simplifications

Tasks define goals that the agent must accomplish. They can be modified through simplifications:

```mermaid
graph TD
    subgraph "Task Definition"
        TASK_DEF["TaskMaker1"]
        TASK_LOAD["load(taskName, variationIdx, simplificationStr)"]
        TASK_VARS["Task Variations"]
        GOALS["GoalSequence"]
    end
    
    subgraph "Simplification System"
        SIMPLE_PARSE["SimplifierProcessor.parseSimplificationStr()"]
        SIMPLE_INIT["SimplifierProcessor.runSimplificationsInitialization()"]
        SIMPLE_TICK["SimplifierProcessor.runSimplificationsEachTick()"]
    end
    
    subgraph "Simplification Types"
        TELEPORT["teleportAction"]
        OPEN_CONT["openContainers"]
        OPEN_DOOR["openDoors"]
        NO_ELEC["noElectricalAction"]
        SELF_WATER["selfWateringFlowerPots"]
        EASY["easy (enables multiple simplifications)"]
    end
    
    TASK_LOAD -->|"creates"| TASK_VARS
    TASK_VARS -->|"defines"| GOALS
    TASK_LOAD -->|"applies"| SIMPLE_PARSE
    SIMPLE_PARSE -->|"enables"| SIMPLE_INIT
    SIMPLE_INIT -->|"modifies environment"| TELEPORT
    SIMPLE_INIT -->|"modifies environment"| OPEN_CONT
    SIMPLE_INIT -->|"modifies environment"| OPEN_DOOR
    SIMPLE_INIT -->|"modifies environment"| NO_ELEC
    SIMPLE_INIT -->|"modifies environment"| SELF_WATER
    EASY -->|"combines"| TELEPORT
    EASY -->|"combines"| OPEN_CONT
    EASY -->|"combines"| OPEN_DOOR
    EASY -->|"combines"| NO_ELEC
    EASY -->|"combines"| SELF_WATER
    SIMPLE_TICK -->|"runs each tick"| GOALS
```

Sources: [scienceworld/scienceworld.py:99-135](). [simulator/src/main/scala/scienceworld/runtime/AgentInterface.scala:36-48]().

Available simplifications:
- **teleportAction**: Adds actions to teleport directly to any possible location
- **openContainers**: Containers are open by default
- **openDoors**: Doors are open by default
- **noElectricalAction**: Remove electrical connection actions to reduce action space
- **selfWateringFlowerPots**: Flower pots water themselves so plants don't die
- **easy**: Enables all the above simplifications (except noElectricalAction for electrical tasks)

## Gold Action Sequences

ScienceWorld supports gold action sequences that provide a demonstration of how to solve a task:

```mermaid
sequenceDiagram
    participant SWEnv as "ScienceWorldEnv"
    participant PI as "PythonInterface"
    participant TM as "TaskMaker1"
    participant GA as "Gold Agent"
    
    SWEnv->>PI: load(taskName, variationIdx, simplificationStr, generateGoldPath=True)
    PI->>PI: doLoad(taskName, variationIdx, simplificationStr)
    PI->>TM: createGoldActions(taskStr, variationIdx, this)
    TM->>GA: Run gold agent to find solution
    GA-->>TM: Return action sequence
    TM-->>PI: Return (goldPath, success)
    PI->>PI: Store goldActionsStr
    PI->>PI: doLoad(taskName, variationIdx, simplificationStr)
    PI->>PI: Restore goldActionsStr
    PI-->>SWEnv: Return
    SWEnv->>SWEnv: Set goldPathGenerated = True
```

Sources: [scienceworld/scienceworld.py:398-407](). [simulator/src/main/scala/scienceworld/runtime/pythonapi/PythonInterface.scala:57-90]().

Gold action sequences serve as:
1. Demonstrations of task solutions
2. Evaluation benchmarks for agent performance
3. Training data for imitation learning approaches

## Summary

The ScienceWorld architecture provides a flexible simulation environment for elementary science tasks through:

1. A layered design that separates the Python API from the Scala simulation engine
2. A composable object system that allows for complex interactions
3. A task system with variations and simplifications
4. Support for gold action sequences as demonstrations

This architecture enables researchers to develop and evaluate AI agents on tasks that test understanding of scientific concepts in a text-based environment.

Sources: [scienceworld/scienceworld.py](). [simulator/src/main/scala/scienceworld/runtime/pythonapi/PythonInterface.scala](). [simulator/src/main/scala/scienceworld/runtime/AgentInterface.scala]().

---

