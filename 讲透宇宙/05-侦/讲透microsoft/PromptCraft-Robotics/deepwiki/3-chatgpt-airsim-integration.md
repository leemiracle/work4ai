<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/PromptCraft-Robotics · page 3 ChatGPT-AirSim Integration · fetched 2026-10-26 -->

# ChatGPT-AirSim Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [chatgpt_airsim/README.md](chatgpt_airsim/README.md)

</details>



## Purpose and Scope

This document provides a technical overview of the ChatGPT-AirSim integration system, which enables users to control a drone in Microsoft AirSim simulation environments using natural language commands interpreted by OpenAI's ChatGPT. The system acts as a bridge between natural language understanding and robotic control, demonstrating how large language models (LLMs) can be applied to robotics tasks.

For detailed setup instructions, see [Installation and Setup](#3.1). For information about the underlying prompt system that enables the integration, see [Prompt System](#3.3).

## System Overview

The ChatGPT-AirSim integration consists of a Python-based interface that connects OpenAI's ChatGPT language model with the AirSim drone simulation environment. The system allows users to input natural language commands which are processed by ChatGPT to generate executable Python code. This code is automatically executed to control a drone within the simulation.

```mermaid
flowchart TD
    subgraph "User Interface"
        user["User"]
        terminal["Terminal Interface"]
    end
    
    subgraph "Core Components"
        chatgpt_airsim["chatgpt_airsim.py"]
        airsim_wrapper["airsim_wrapper.py"]
        prompts["Prompt System"]
    end
    
    subgraph "External Systems"
        openai_api["OpenAI API"]
        airsim["AirSim Simulator"]
    end
    
    user -->|"Natural language commands"| terminal
    terminal -->|"Process commands"| chatgpt_airsim
    chatgpt_airsim -->|"Send formatted prompts"| openai_api
    openai_api -->|"Return code response"| chatgpt_airsim
    chatgpt_airsim -->|"Extract & run code"| airsim_wrapper
    airsim_wrapper -->|"Execute drone commands"| airsim
    prompts -->|"Provide context"| chatgpt_airsim
```

Sources: [chatgpt_airsim/README.md:3-5]()

## Core Components

The integration consists of three primary components working together:

1. **chatgpt_airsim.py** - The main script that handles user input, communicates with the OpenAI API, and manages code execution
2. **airsim_wrapper.py** - A wrapper library that provides high-level drone control functions and interfaces with the AirSim API
3. **Prompt System** - Text files containing carefully crafted prompts that describe available functions and set ChatGPT's behavior

```mermaid
classDiagram
    class ChatGPTAirSim {
        +process_command()
        +send_to_openai()
        +extract_code()
        +execute_code()
        +display_results()
    }
    
    class AirSimWrapper {
        +takeoff()
        +land()
        +fly_to()
        +get_drone_position()
        +get_position()
        +set_yaw()
        +get_yaw()
        +fly_path()
    }
    
    class PromptSystem {
        +system_prompts
        +user_prompts
        +function_definitions
    }
    
    ChatGPTAirSim --> AirSimWrapper : uses
    ChatGPTAirSim --> PromptSystem : incorporates
```

Sources: [chatgpt_airsim/README.md:3-5]()

## Workflow and Data Flow

The integration follows a clear workflow to process user commands and control the drone:

```mermaid
sequenceDiagram
    participant User
    participant Terminal
    participant ChatGPTAirSim as chatgpt_airsim.py
    participant OpenAI as OpenAI API
    participant AirSimWrapper as airsim_wrapper.py
    participant AirSim as AirSim Simulator
    
    User->>Terminal: Enter natural language command
    Terminal->>ChatGPTAirSim: Process command
    
    ChatGPTAirSim->>ChatGPTAirSim: Combine with prompt templates
    ChatGPTAirSim->>OpenAI: Send API request
    OpenAI->>ChatGPTAirSim: Return text with Python code
    
    ChatGPTAirSim->>ChatGPTAirSim: Extract code blocks
    ChatGPTAirSim->>AirSimWrapper: Execute extracted code
    
    AirSimWrapper->>AirSim: Send drone commands
    AirSim->>AirSimWrapper: Return drone state/data
    AirSimWrapper->>ChatGPTAirSim: Return results
    
    ChatGPTAirSim->>Terminal: Display response and results
    Terminal->>User: Show output
```

Sources: [chatgpt_airsim/README.md:3-5](), [chatgpt_airsim/README.md:26-30]()

## Technical Implementation

### Command Processing

When a user inputs a natural language command at the `AirSim>` prompt, the system:

1. Takes the user input and combines it with pre-defined prompts that include function definitions
2. Sends this combined prompt to the OpenAI API
3. Receives a response containing explanations and Python code
4. Automatically extracts code blocks (content between triple backticks)
5. Executes the extracted code using the AirSim wrapper functions
6. Displays the results to the user

Sources: [chatgpt_airsim/README.md:26-30]()

### Available Drone Functions

The AirSim wrapper provides a set of high-level functions that can be used to control the drone. These functions are exposed to ChatGPT through the prompt templates.

| Function | Description |
|----------|-------------|
| `takeoff()` | Takes off the drone from the ground |
| `land()` | Lands the drone safely on the ground |
| `get_drone_position()` | Returns the current position of the drone |
| `fly_to(x, y, z)` | Flies the drone to the specified coordinates |
| `fly_path(path)` | Flies the drone along a specified path of coordinates |
| `set_yaw(angle)` | Sets the yaw angle of the drone |
| `get_yaw()` | Returns the current yaw angle of the drone |
| `get_position(object_name)` | Gets the position of a named object in the environment |

Sources: [chatgpt_airsim/README.md:3-5]()

### Environment Objects

The AirSim environment contains various objects that the drone can interact with. These objects can be referenced by name in commands.

```mermaid
graph TD
    subgraph "AirSim Environment Objects"
        drone["Drone"]
        
        subgraph "Inspectable Objects"
            turbines["Turbines"]
            towers["Towers"]
            solarpanels["Solar Panels"]
            car["Car"]
            crowd["Crowd"]
        end
        
        turbines --> turbine1["turbine1"]
        turbines --> turbine2["turbine2"]
        
        towers --> tower1["tower1"]
        towers --> tower2["tower2"]
        towers --> tower3["tower3"]
    end
```

Sources: [chatgpt_airsim/README.md:3-5]()

## Configuration and Setup

The system requires configuration of:

1. OpenAI API key in `config.json`
2. AirSim settings in the proper directory
3. Conda environment for dependencies

The actual simulation runs as a separate process, with the Python interface connecting to it via the AirSim client library.

```mermaid
graph TD
    subgraph "Setup Components"
        config["config.json"]
        settings["settings.json"]
        environment["environment.yml"]
    end
    
    subgraph "Running System"
        airsim_binary["AirSim Simulation Binary"]
        python_interface["Python Interface"]
    end
    
    config -->|"API Key"| python_interface
    settings -->|"Simulation Config"| airsim_binary
    environment -->|"Dependencies"| python_interface
    
    python_interface <-->|"Client Connection"| airsim_binary
```

Sources: [chatgpt_airsim/README.md:9-23]()

## Technical Limitations and Considerations

- The system executes generated code directly, which could lead to unpredictable behavior
- Response times depend on the OpenAI API latency
- The wrapper provides a limited set of functions compared to the full AirSim API
- Generated code quality depends on the quality of the prompts and ChatGPT's capabilities

Sources: [chatgpt_airsim/README.md:30-32]()

## Bridging Natural Language to Code Execution

The system bridges the gap between natural language and drone control through a multi-step translation process:

```mermaid
flowchart LR
    subgraph "Natural Language Space"
        nl_input["User Command"]
        nl_examples["Example Commands"]
        nl_context["Context Information"]
    end
    
    subgraph "Translation Layer"
        chatgpt["ChatGPT Model"]
        prompt_engineering["Prompt Templates"]
    end
    
    subgraph "Code Entity Space"
        wrapper_functions["AirSimWrapper Functions"]
        code_blocks["Generated Python Code"]
        airsim_api["AirSim Client API"]
    end
    
    nl_input --> chatgpt
    nl_examples --> prompt_engineering
    nl_context --> prompt_engineering
    prompt_engineering --> chatgpt
    chatgpt --> code_blocks
    code_blocks -->|"Calls"| wrapper_functions
    wrapper_functions -->|"Translates to"| airsim_api
```

Sources: [chatgpt_airsim/README.md:3-5](), [chatgpt_airsim/README.md:26-30]()

## Technical Design Elements

The system's design separates concerns across different files:

```mermaid
graph TD
    subgraph "Configuration Files"
        config_json["config.json"]
        settings_json["settings.json (AirSim config)"]
    end
    
    subgraph "Prompt Files"
        system_prompt["system_prompts/airsim_basic.txt"]
        user_prompt["prompts/airsim_basic.txt"]
    end
    
    subgraph "Code Modules"
        chatgpt_airsim_py["chatgpt_airsim.py"]
        airsim_wrapper_py["airsim_wrapper.py"]
    end
    
    config_json -->|"Provides API key"| chatgpt_airsim_py
    system_prompt -->|"Defines ChatGPT behavior"| chatgpt_airsim_py
    user_prompt -->|"Defines available functions"| chatgpt_airsim_py
    chatgpt_airsim_py -->|"Uses"| airsim_wrapper_py
    settings_json -->|"Configures"| airsim
    airsim_wrapper_py -->|"Interfaces with"| airsim["AirSim API"]
```

Sources: [chatgpt_airsim/README.md:3-5](), [chatgpt_airsim/README.md:9-23]()

---

