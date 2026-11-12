<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/PromptCraft-Robotics · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

PromptCraft-Robotics is a community-driven repository designed to explore and demonstrate the applications of large language models (LLMs) in robotics. This repository serves as a platform for users to test, share, and collaborate on prompt engineering examples for robotics tasks. The primary focus is on utilizing OpenAI's ChatGPT, though examples from other LLMs are welcome.

This overview document provides a high-level understanding of the PromptCraft-Robotics system, its architecture, and key components. For detailed setup instructions, see [Installation and Setup](#3.1). For information on contributing new prompts, see [Community Contribution Guidelines](#2).

Sources: [README.md:1-11]()

## System Architecture Overview

The PromptCraft-Robotics repository consists of three main components that work together to enable natural language control of robotic systems:

```mermaid
flowchart TD
    subgraph "PromptCraft-Robotics"
        A["ChatGPT-AirSim Integration"] --> B["Robotics Simulator"]
        C["Prompt Engineering Framework"] --> A
        D["Community Contribution Model"] --> C
    end
    
    E["User"] --> |"Natural language commands"| A
    E --> |"Submits prompts"| D
    A --> |"Controls"| B
    B --> |"Provides feedback"| E
```

1. **ChatGPT-AirSim Integration**: The core technical component that connects language models to a robotics simulator
2. **Prompt Engineering Framework**: A structured approach for creating effective prompts for various robotics tasks
3. **Community Contribution Model**: A process for users to submit, review, and share interesting prompt examples

Sources: [README.md:3-11](), [README.md:55-59]()

## ChatGPT-AirSim Integration

The ChatGPT-AirSim integration is the primary technical implementation in the repository, allowing users to control a simulated drone using natural language commands.

```mermaid
flowchart TD
    subgraph "Natural Language Space"
        NLCommand["Natural Language Command"]
    end
    
    subgraph "Code Entity Space"
        Terminal["Terminal Interface"]
        ChatGPTAirSim["chatgpt_airsim.py"]
        AirSimWrapper["airsim_wrapper.py"]
        OpenAIAPI["OpenAI API"]
        AirSim["AirSim Simulator"]
        ConfigJson["config.json"]
        Prompts["prompts/airsim_basic.txt"]
        SystemPrompts["system_prompts/airsim_basic.txt"]
    end
    
    NLCommand --> Terminal
    Terminal --> ChatGPTAirSim
    
    ChatGPTAirSim --> |"Sends prompts"| OpenAIAPI
    OpenAIAPI --> |"Returns code"| ChatGPTAirSim
    
    ChatGPTAirSim --> |"Executes code"| AirSimWrapper
    AirSimWrapper --> |"Controls drone"| AirSim
    
    ConfigJson --> |"API key"| ChatGPTAirSim
    Prompts --> |"Available functions"| ChatGPTAirSim
    SystemPrompts --> |"LLM behavior"| ChatGPTAirSim
```

The system works as follows:
1. User enters a natural language command
2. The command is sent to ChatGPT with context from system prompts
3. ChatGPT generates Python code to accomplish the task
4. The code is executed through the AirSim wrapper to control the drone
5. Results are returned to the user

Sources: [README.md:55-57]()

## Prompt Engineering Framework

The repository organizes prompts into categories based on different robotics domains, providing a structured approach to prompt engineering for robotics applications.

```mermaid
flowchart TD
    subgraph "Prompt Engineering Framework"
        PromptCategories["Prompt Categories"]
        
        PromptCategories --> EmbodiedAgent["Embodied Agent"]
        PromptCategories --> AerialRobotics["Aerial Robotics"]
        PromptCategories --> Manipulation["Manipulation"]
        PromptCategories --> SpatialTemporal["Spatial-temporal Reasoning"]
        
        EmbodiedAgent --> EA1["Object Navigation"]
        EA1 --> EA1Code["examples/embodied_agents/visual_language_navigation_1.md"]
        
        AerialRobotics --> AR1["Turbine Inspection"]
        AR1 --> AR1Code["examples/aerial_robotics/airsim_turbine_inspection.md"]
        
        Manipulation --> M1["Pick and Stack"]
        M1 --> M1Code["examples/manipulation/pick_stack_msft_logo.md"]
        
        SpatialTemporal --> ST1["Visual Servoing"]
        ST1 --> ST1Code["examples/spatial_temporal_reasoning/visual_servoing_basketball.md"]
    end
```

The framework includes example prompts across various domains:

| Category | Example Tasks | File Path |
|----------|---------------|-----------|
| Embodied Agents | Object navigation, RGBD navigation | examples/embodied_agents/* |
| Aerial Robotics | Turbine inspection, obstacle avoidance | examples/aerial_robotics/* |
| Manipulation | Picking, stacking, building | examples/manipulation/* |
| Spatial-temporal | Visual servoing | examples/spatial_temporal_reasoning/* |

Sources: [README.md:35-53]()

## Community Contribution Model

PromptCraft-Robotics follows a community-driven approach where users can contribute prompts through GitHub Discussions.

```mermaid
sequenceDiagram
    actor User
    participant Discussions as "GitHub Discussions"
    participant Community
    participant Admins
    participant Repository
    
    User->>Discussions: Submit prompt example
    Note over User,Discussions: Formatted as markdown
    
    Discussions->>Community: Review
    Community->>Discussions: Upvote interesting examples
    
    Discussions->>Admins: Review highly upvoted examples
    Admins->>Repository: Add interesting/useful examples
    
    Repository->>User: Available for testing and adaptation
```

The contribution process:
1. Users submit prompts to the GitHub Discussions section
2. Prompts are categorized in appropriate robotics domains
3. The community reviews and upvotes interesting examples
4. Repository admins add selected prompts to the main repository
5. Submissions should be formatted in markdown with LLM details and visuals

Sources: [README.md:7-11]()

## Data and Control Flow

The following diagram illustrates how user commands flow through the system to control the simulated drone:

```mermaid
flowchart LR
    subgraph "User Interface"
        User["User"]
        Command["Natural Language Command"]
    end
    
    subgraph "Processing Layer"
        ChatGPT["OpenAI ChatGPT"]
        CodeGen["Python Code Generation"]
    end
    
    subgraph "Execution Layer"
        Wrapper["airsim_wrapper.py"]
        AirSim["AirSim API"]
    end
    
    subgraph "Simulation"
        Drone["Drone"]
        Environment["Virtual Environment"]
    end
    
    User --> Command
    Command --> ChatGPT
    ChatGPT --> CodeGen
    CodeGen --> Wrapper
    Wrapper --> AirSim
    AirSim --> Drone
    Drone --> Environment
    Environment --> User
```

This architecture enables a natural language interface for robotics control, removing the need for users to write code directly. Instead, the LLM interprets commands and generates appropriate code to accomplish the desired tasks.

Sources: [README.md:55-57]()

## AirSim Environment Objects

The AirSim environment includes various objects that can be interacted with using the drone:

```mermaid
graph TD
    subgraph "AirSim Environment Objects"
        Drone["Drone"]
        
        subgraph "Scene Objects"
            Turbines["Turbines (turbine1, turbine2)"]
            Towers["Towers (tower1, tower2, tower3)"]
            Others["Other Objects (solarpanels, car, crowd)"]
        end
    end
    
    subgraph "Drone Control Functions"
        TakeoffFn["aw.takeoff()"]
        LandFn["aw.land()"]
        GetPosFn["aw.get_drone_position()"]
        FlyToFn["aw.fly_to()"]
        FlyPathFn["aw.fly_path()"]
        YawFn["aw.set_yaw() / aw.get_yaw()"]
        GetObjPosFn["aw.get_position()"]
    end
    
    Drone --- TakeoffFn
    Drone --- LandFn
    Drone --- GetPosFn
    Drone --- FlyToFn
    Drone --- FlyPathFn
    Drone --- YawFn
    
    GetObjPosFn --- Turbines
    GetObjPosFn --- Towers
    GetObjPosFn --- Others
```

Through the AirSim wrapper functions, users can control the drone to perform various tasks like inspecting wind turbines, avoiding obstacles, or navigating to specific objects.

For more information on the available functions and environment objects, see [Drone Control API](#3.4) and [AirSim Environment Objects](#3.5).

Sources: [README.md:45-47]()

## Research and Resources

PromptCraft-Robotics is accompanied by research publications and additional resources:

- **Research Paper**: "ChatGPT for Robotics: Design Principles and Model Abilities"
- **Blog Post**: Available at aka.ms/ChatGPT-Robotics
- **Demo Videos**: Available on YouTube showing various applications

The project welcomes contributions from the community to expand the range of prompts, robotic applications, and integrations with other simulators.

Sources: [README.md:13-33](), [README.md:61-67]()

## Getting Started

To get started with PromptCraft-Robotics:

1. Explore the existing prompt examples in different categories
2. Set up the ChatGPT-AirSim integration for testing your own prompts
3. Contribute your interesting prompt examples through GitHub Discussions

For detailed setup instructions, see [Installation and Setup](#3.1). For information on using the system with examples, see [Using the System](#4).

Sources: [README.md:55-59]()

---

