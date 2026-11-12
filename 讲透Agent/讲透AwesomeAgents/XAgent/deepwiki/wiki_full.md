# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [XAgentGen/README.md](XAgentGen/README.md)

</details>



XAgent is an open-source autonomous agent system powered by Large Language Models (LLMs) designed to solve complex tasks without human intervention. This page provides a high-level overview of XAgent's architecture, key components, and capabilities. For installation instructions, see [Installation and Setup](#1.2).

## What is XAgent?

XAgent is an experimental autonomous agent framework that leverages the reasoning capabilities of large language models to break down complex tasks, plan solutions, and execute them using various tools. The system is designed with the following key features:

- **Autonomy**: Automatically solves various tasks without human participation
- **Safety**: All actions are constrained inside a Docker container
- **Extensibility**: Easily extensible with new tools and agents
- **GUI**: User-friendly interface for interaction
- **Human Collaboration**: Can follow human guidance and seek human assistance when needed

Sources: [README.md:28-48]()

## System Architecture

XAgent consists of several interconnected systems that work together to provide a complete autonomous agent experience.

```mermaid
flowchart TB
    subgraph "User Interfaces"
        Web["XAgentWeb (Web UI)"]
        CLI["Command Line Interface"]
    end

    subgraph "Server Layer"
        XAS["XAgentServer"]
    end

    subgraph "Core System"
        XA["XAgent Core"]
        TS["ToolServer"]
        XAG["XAgentGen (Optional)"]
    end

    subgraph "External Services"
        LLM["LLM APIs (OpenAI/Azure)"]
    end

    User --> Web
    User --> CLI
    Web -->|WebSocket| XAS
    CLI --> XA
    XAS --> XA
    XA --> LLM
    XA --> TS
    XA --> XAG
```

**XAgent System Components:**

| Component | Description |
|-----------|-------------|
| XAgent Core | The main intelligent agent system that processes tasks, generates plans, and executes actions |
| ToolServer | Provides a safe environment with various tools for XAgent to use |
| XAgentServer | Facilitates client-agent interaction via WebSockets |
| XAgentWeb | Web interface for interacting with XAgent |
| XAgentGen | Component for generating customized models to support XAgent |

Sources: [README.md:50-53](), [README.md:61-70]()

## Core Components

XAgent's core system consists of three main components that work together to process tasks:

```mermaid
flowchart TB
    Task["User Task"] --> Dispatcher
    
    subgraph "XAgent Core"
        Dispatcher --> Planner
        Planner --> Actor
        
        Dispatcher -->|"Task Management"| RunningRecorder["Running Recorder"]
        Planner -->|"Plan Generation"| RunningRecorder
        Actor -->|"Action Execution"| RunningRecorder
    end
    
    Actor --> ToolServer
    ToolServer --> Results["Task Results"]
```

**XAgent Core Components:**

| Component | Description |
|-----------|-------------|
| Dispatcher | Responsible for dynamically instantiating and dispatching tasks to different agents |
| Planner | Generates and rectifies plans for tasks, dividing tasks into subtasks with milestones |
| Actor | Conducts actions to achieve goals and finish subtasks using various tools |
| Running Recorder | Records task execution for later inspection and analysis |

The workflow of XAgent involves:
1. The Dispatcher receives a task and manages its execution
2. The Planner breaks down the task into subtasks with specific milestones
3. The Actor executes each subtask using appropriate tools
4. The Running Recorder logs all interactions for later analysis

Sources: [README.md:51-53](), [README.md:54-59]()

## ToolServer System

ToolServer provides a safe execution environment for XAgent's tools through Docker containers.

```mermaid
flowchart LR
    XAgent --> TSM["ToolServerManager"]
    
    subgraph "ToolServer System"
        TSM -->|"Creates/Manages"| TSNode["ToolServerNode"]
        TSMonitor["ToolServerMonitor"] -->|"Monitors"| TSNode
    end
    
    subgraph "Available Tools"
        TSNode --> FileEditor["File Editor"]
        TSNode --> PyNotebook["Python Notebook"]
        TSNode --> WebBrowser["Web Browser"]
        TSNode --> Shell["Shell"]
        TSNode --> RapidAPI["Rapid API"]
    end
```

**Available Tools in ToolServer:**

| Tool | Description |
|------|-------------|
| File Editor | Provides text editing capabilities to write, read, and modify files |
| Python Notebook | Interactive Python environment that can run code to validate ideas and visualize data |
| Web Browser | Allows searching and visiting webpages |
| Shell | Bash shell that can execute shell commands, install programs, and host services |
| Rapid API | Retrieves and calls APIs from Rapid API |

Sources: [README.md:62-70]()

## Data Flow and Communication

XAgent components communicate and persist data through various channels:

```mermaid
sequenceDiagram
    participant Client as "User (Web/CLI)"
    participant XAS as "XAgentServer"
    participant XA as "XAgent Core"
    participant TS as "ToolServer"
    participant LLM as "OpenAI/Azure API"
    
    Client->>XAS: Send task request
    XAS->>XA: Initialize XAgent with task
    
    loop Task Execution
        XA->>LLM: Generate plan/action
        LLM->>XA: Response
        XA->>TS: Execute tool operations
        TS->>XA: Tool results
        XA->>XAS: Update progress
        XAS->>Client: Send updates
        
        alt Human intervention needed
            XA->>XAS: Request human input
            XAS->>Client: Prompt for input
            Client->>XAS: Provide input
            XAS->>XA: Forward input
        end
    end
    
    XA->>XAS: Task completed
    XAS->>Client: Send final results
```

**Data Storage:**

| Storage Type | Purpose |
|--------------|---------|
| MySQL Database | Stores interaction data through XAgentServer |
| Redis | Manages session state |
| Running Records | Logs all execution details including LLM calls and tool usage |
| File System | Stores files generated during task execution |
| Local Workspace | Provides workspace for the current session |

Sources: [README.md:126-136]()

## Integration with XAgentGen

XAgentGen extends XAgent's capabilities by providing customized models with constrained text generation:

```mermaid
flowchart LR
    XAgent -->|"Function Calls"| XAgentGen
    
    subgraph "XAgentGen System"
        XAgentGen --> CustomModels["Customized Models"]
        CustomModels --> XAgentLlama["XAgentLlama"]
    end
    
    CustomModels -->|"Constrained Generation"| FunctionCalls["JSON Schema\nFunction Calls"]
```

XAgentGen allows XAgent to use custom models that can generate function calls with complex JSON schemas, similar to OpenAI's function calling capability.

Sources: [XAgentGen/README.md:1-9]()

## Use Cases and Capabilities

XAgent can handle a wide range of complex tasks, such as:

1. **Data Analysis**: Processing and analyzing datasets, generating visualizations and reports
2. **Information Retrieval**: Searching the web for specific information and compiling reports
3. **Code Development**: Writing, debugging, and optimizing code
4. **Model Training**: Training machine learning models based on user requirements
5. **Task Automation**: Automating repetitive tasks through planning and tool execution

Sources: [README.md:153-176]()

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [XAgent/recorder.py](XAgent/recorder.py)
- [XAgentGen/README.md](XAgentGen/README.md)
- [XAgentServer/server.py](XAgentServer/server.py)
- [docker-compose.yml](docker-compose.yml)

</details>



This document provides an overview of the XAgent system architecture, explaining the relationships and interactions between its core components. It aims to help developers understand the high-level design and how different parts of the system work together.

For details on installation, see [Installation and Setup](#1.2). For deeper information about specific subsystems, refer to their dedicated wiki pages ([XAgent Core](#2), [ToolServer](#3), [XAgentServer](#4), and [XAgentWeb](#5)).

## System Overview

XAgent is an autonomous agent system designed to solve complex tasks using large language models (LLMs). The system architecture follows a modular design that separates concerns between task planning, tool execution, user interaction, and persistence.

```mermaid
graph TB
    User["User"] -->|interacts with| Web["XAgentWeb"]
    User -->|command line| CLI["Command Line Interface"]
    
    Web -->|WebSocket| XAS["XAgentServer"]
    CLI -->|direct calls| XA["XAgent Core"]
    
    XAS -->|orchestrates| XA
    
    XA -->|uses| OpenAI["OpenAI/Azure API"]
    XA -->|calls tools via| TS["ToolServer"]
    XA -->|optional| XAG["XAgentGen"]
    
    subgraph "Core Components"
        XA
        TS
        XAS
        XAG
    end
    
    subgraph "User Interfaces"
        Web
        CLI
    end
    
    subgraph "External Services"
        OpenAI
    end

    class XA,TS,XAS,XAG core
    class Web,CLI ui
    class OpenAI external
```

**XAgent System Architecture**

Sources:
- [README.md:41-53]()
- [README.md:61-70]()
- [docker-compose.yml:1-110]()

## Key Components

### XAgent Core

The XAgent Core is the central component responsible for processing user tasks, planning solutions, and coordinating execution. It consists of several key subcomponents:

```mermaid
graph LR
    subgraph "XAgent Core"
        Dispatcher["Dispatcher"]
        Planner["Planner"]
        Actor["Actor"]
        Reflection["Reflection Agent"]
        RunningRecorder["RunningRecorder"]
    end
    
    Query["User Query"] --> Dispatcher
    Dispatcher --> Planner
    Planner --> PlanGenAgent["Plan Generate Agent"]
    PlanGenAgent --> PlanRefineAgent["Plan Refine Agent"]
    PlanRefineAgent --> Actor
    Actor --> ToolAgent["Tool Agent"]
    ToolAgent --> Reflection
    
    Dispatcher --> RunningRecorder
    Planner --> RunningRecorder
    Actor --> RunningRecorder
    Reflection --> RunningRecorder
    
    ToolAgent -->|uses| ToolServer["ToolServer"]
```

**XAgent Core Components**

1. **Dispatcher**: Dynamically instantiates and dispatches tasks to different agents based on task requirements.
2. **Planner**: Generates and refines plans for tasks, dividing complex tasks into manageable subtasks with milestones.
3. **Actor**: Conducts actions to achieve goals and complete subtasks using various tools and potentially collaborating with humans.
4. **Reflection Agent**: Learns from execution processes to improve future task handling.
5. **RunningRecorder**: Records all interactions and execution details for later inspection and analysis.

Sources:
- [README.md:50-53]()
- [XAgent/recorder.py:48-346]()
- [XAgentServer/server.py:20-109]()

### ToolServer

The ToolServer provides a safe and controlled environment for executing tools requested by XAgent. It runs as a Docker container to isolate tool execution from the host system.

```mermaid
graph TD
    subgraph "ToolServer System"
        TSM["ToolServerManager"]
        TSMonitor["ToolServerMonitor"]
        TSNode1["ToolServerNode 1"]
        TSNode2["ToolServerNode 2"]
        TSNodeN["ToolServerNode N"]
    end
    
    XAgent -->|API calls| TSM
    TSM -->|creates/manages| TSNode1
    TSM -->|creates/manages| TSNode2
    TSM -->|creates/manages| TSNodeN
    TSMonitor -->|monitors| TSNode1
    TSMonitor -->|monitors| TSNode2
    TSMonitor -->|monitors| TSNodeN
    
    subgraph "Available Tools"
        TSNode1 --> FileEditor["File Editor"]
        TSNode1 --> PythonNotebook["Python Notebook"]
        TSNode1 --> WebBrowser["Web Browser"]
        TSNode1 --> Shell["Shell"]
        TSNode1 --> RapidAPI["Rapid API"]
    end
```

**ToolServer Architecture**

The ToolServer provides the following tools:
- **File Editor**: For writing, reading, and modifying files
- **Python Notebook**: Interactive Python environment for code execution
- **Web Browser**: For web searches and browsing
- **Shell**: Bash shell for executing system commands
- **Rapid API**: For retrieving and calling external APIs

Sources:
- [README.md:61-70]()
- [docker-compose.yml:4-30]()

### XAgentServer

XAgentServer acts as the bridge between user interfaces (primarily XAgentWeb) and the XAgent Core system. It handles WebSocket connections, manages user sessions, and persists interaction data.

```mermaid
sequenceDiagram
    participant Client as "Web Client"
    participant XAS as "XAgentServer"
    participant XA as "XAgent Core"
    participant TS as "ToolServer"
    
    Client->>XAS: Connect WebSocket
    XAS->>Client: Connection established
    
    Client->>XAS: Send task with parameters
    XAS->>XAS: Create interaction record
    XAS->>XA: Initialize XAgent with task
    
    XA->>XAS: Request planning
    XAS->>Client: Send "starting" status
    
    loop For each subtask
        XA->>TS: Execute tool operations
        TS->>XA: Return tool results
        XA->>XAS: Update subtask progress
        XAS->>Client: Send subtask updates
        
        alt Human intervention needed
            XAS->>Client: Request human input
            Client->>XAS: Provide input
            XAS->>XA: Forward human input
        end
    end
    
    XA->>XAS: Task completed
    XAS->>Client: Send completion status
    XAS->>Client: Close WebSocket
```

**XAgentServer Communication Flow**

The server component integrates with:
- **MySQL**: For storing interaction data and user information
- **Redis**: For managing session state
- **ToolServerManager**: For creating and managing ToolServer instances

Sources:
- [XAgentServer/server.py:1-109]()
- [docker-compose.yml:43-64]()

### XAgentWeb

XAgentWeb provides a graphical user interface for interacting with XAgent. It communicates with XAgentServer via WebSockets to send tasks and receive updates.

### XAgentGen (Optional)

XAgentGen is an optional component that implements guided generation of customized models to support XAgent. It allows models to generate function calls with complex JSON schemas similar to OpenAI's function calling.

Sources:
- [XAgentGen/README.md:1-49]()

## Data Flow and Persistence

XAgent maintains several types of persistent storage for different purposes:

```mermaid
graph TD
    subgraph "User Interfaces"
        Web["XAgentWeb"]
        CLI["Command Line"]
    end
    
    subgraph "Runtime State"
        Redis["Redis Database"]
        RunningRecords["Running Records"]
        LocalWorkspace["Local Workspace"]
    end
    
    subgraph "Persistent Storage"
        MySQL["MySQL Database"]
        FileSystem["File System"]
    end
    
    Web -->|WebSocket| XAgentServer
    CLI -->|direct| XAgent
    
    XAgentServer -->|stores interactions| MySQL
    XAgentServer -->|session state| Redis
    
    XAgent -->|logs executions| RunningRecords
    XAgent -->|stores files| LocalWorkspace
    
    XAgent -->|uses| ToolServer
    ToolServer -->|stores files| FileSystem
```

**Data Flow and Persistence**

- **MySQL Database**: Stores user information, interaction history, and task details
- **Redis Database**: Manages session state and temporary data
- **Running Records**: Logs detailed execution records including LLM inputs/outputs and tool calls
- **Local Workspace**: Stores files generated during task execution
- **File System**: Used by ToolServer to manage files in the isolated environment

Sources:
- [XAgent/recorder.py:48-346]()
- [docker-compose.yml:66-94]()

## Deployment Architecture

The entire XAgent system is designed to be deployed using Docker containers, with the following container structure:

```mermaid
graph TB
    subgraph "Docker Network: tool-server-network"
        XAgentServer["XAgent-Server Container"]
        ToolServerManager["ToolServerManager Container"]
        ToolServerNode["ToolServerNode Containers"]
        Database["Database Containers"]
    end
    
    Database -->|consists of| MySQL["MySQL Container"]
    Database -->|consists of| Redis["Redis Container"]
    Database -->|consists of| MongoDB["MongoDB Container"]
    
    ToolServerManager -->|creates| ToolServerNode
    
    XAgentServer -->|API calls| ToolServerManager
    XAgentServer -->|stores data| MySQL
    XAgentServer -->|manages sessions| Redis
    ToolServerManager -->|stores data| MongoDB
    
    Users["Users"] -->|Web UI| XAgentServer
    Users -->|CLI| XAgentCLI["XAgent Core (local)"]
    
    XAgentCLI -->|API calls| ToolServerManager
```

**Deployment Architecture**

This containerized approach ensures:
1. Isolation of tool execution for security
2. Scalability through container orchestration
3. Easy deployment across different environments
4. Separation of concerns between components

Sources:
- [docker-compose.yml:1-110]()

## System Workflow

When a user submits a task to XAgent, the following workflow is initiated:

1. **Task Reception**: The task is received either through the web interface or command line interface
2. **Task Planning**: XAgent Core's Planner breaks down the task into subtasks and creates a plan
3. **Tool Execution**: The Actor executes the plan using tools provided by ToolServer
4. **Progress Monitoring**: The system continuously monitors progress and updates the user
5. **Human Collaboration**: If needed, XAgent can request human assistance for specific subtasks
6. **Task Completion**: When all subtasks are completed, the final results are presented to the user

Throughout this process, the RunningRecorder logs all activities for later inspection and analysis.

Sources:
- [README.md:50-59]()
- [XAgentServer/server.py:27-109]()

## Key Technical Specifications

| Component | Technology | Purpose |
|-----------|------------|---------|
| XAgent Core | Python | Task planning and execution |
| ToolServer | Docker | Isolated tool execution environment |
| XAgentServer | FastAPI | WebSocket API and HTTP endpoints |
| XAgentWeb | React | User interface |
| Database | MySQL, Redis, MongoDB | Data persistence |
| LLM Integration | OpenAI API | Language processing capabilities |

Sources:
- [docker-compose.yml:1-110]()
- [README.md:26-70]()

## Security Architecture

XAgent is designed with security in mind:

1. **Isolation**: All tool execution occurs in isolated Docker containers
2. **Controlled Access**: ToolServer restricts access to system resources
3. **API Key Management**: Sensitive information like API keys is securely managed
4. **Authentication**: The web interface requires authentication for access

This architecture ensures that potentially risky operations (like shell commands) can be executed safely without endangering the host system.

Sources:
- [README.md:44-46]()
- [docker-compose.yml:24-30]()

## Conclusion

The XAgent architecture is designed to be modular, extensible, and secure. By separating concerns between planning, execution, and user interaction, the system can effectively tackle a wide range of tasks autonomously. The use of Docker containers for tool execution provides a safe environment for running potentially risky operations, while the integration with large language models enables sophisticated reasoning and planning capabilities.

For more detailed information about specific components, please refer to their dedicated wiki pages.

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [XAgentGen/README.md](XAgentGen/README.md)
- [assets/config.yml](assets/config.yml)
- [assets/gpt-3.5-turbo_config.yml](assets/gpt-3.5-turbo_config.yml)
- [assets/gpt4_config.yml](assets/gpt4_config.yml)
- [requirements.txt](requirements.txt)
- [tests/__init__.py](tests/__init__.py)
- [tests/test_1106_model_openai.py](tests/test_1106_model_openai.py)
- [tests/test_model_alias.py](tests/test_model_alias.py)
- [tests/test_run.py](tests/test_run.py)

</details>



This document provides detailed instructions for installing and configuring XAgent, an autonomous agent system driven by Large Language Models (LLMs). It covers the prerequisites, core components setup, configuration options, and running methods. For information about XAgent's architecture, see [Architecture](#1.1).

## Overview of Setup Process

XAgent consists of multiple interrelated components that need to be properly set up and configured to work together. The main setup steps include:

1. Setting up the ToolServer environment (Docker container)
2. Installing XAgent Core dependencies
3. Configuring API keys and system settings
4. Running XAgent via command line or web interface

```mermaid
flowchart TB
    subgraph "Setup Process"
        step1["Install Prerequisites"] --> step2["Setup ToolServer"]
        step2 --> step3["Install XAgent Core"]
        step3 --> step4["Configure XAgent"]
        step4 --> step5["Run XAgent"]
    end
    
    subgraph "Running Options"
        step5 --> cmd["Command Line Interface"]
        step5 --> web["Web Interface (GUI)"]
    end
```

Sources: [README.md:72-147](). [XAgentGen/README.md:10-48]()

## Prerequisites

Before installing XAgent, ensure your system meets the following requirements:

- **Python**: Version 3.10 or higher
- **Docker**: Latest stable version (for ToolServer)
- **docker-compose**: Latest stable version (for ToolServer)
- **Hardware**: 
  - Any standard system capable of running Docker containers
  - For XAgentGen (optional): NVIDIA GPU with CUDA support

Sources: [README.md:110-111](). [XAgentGen/README.md:12-14]()

## Setting up ToolServer

ToolServer provides a safe environment (Docker container) for XAgent to use tools like file editing, web browsing, Python execution, and shell commands.

### Method 1: Pull pre-built image and start containers

```bash
docker compose up
```

Run in background mode with:

```bash
docker compose up -d
```

### Method 2: Build image from local sources

```bash
docker compose build
docker compose up
```

To update ToolServer after changes:

```bash
docker compose pull
```
or
```bash
docker compose build
```

```mermaid
flowchart LR
    subgraph "ToolServer Setup"
        method1["Pull pre-built image"] --> docker_compose["docker compose up"]
        method2["Build from local source"] --> docker_compose
        docker_compose --> ToolServer["ToolServer Container"]
    end
    
    subgraph "Available Tools"
        ToolServer --> FileEditor["File Editor"]
        ToolServer --> PythonNotebook["Python Notebook"]
        ToolServer --> WebBrowser["Web Browser"]
        ToolServer --> Shell["Shell"]
        ToolServer --> RapidAPI["Rapid API"]
    end
```

Sources: [README.md:76-106](). [README.md:61-70]()

## Installing XAgent Core

After setting up ToolServer, install the XAgent Core:

1. Install Python requirements:

```bash
pip install -r requirements.txt
```

Sources: [README.md:110-116](). [requirements.txt:1-31]()

## Configuring XAgent

XAgent requires configuration before running. The main configuration file is `assets/config.yml`.

### API Key Configuration

At minimum, configure your OpenAI API keys in the configuration file:

```yaml
api_keys:
  gpt-3.5-turbo-16k:
    - api_key: sk-xxxxx
      organization: org-xxxxx
      model: gpt-3.5-turbo-16k
  gpt-4:    
    - api_key: sk-xxxxx
      organization: org-xxxxx
      model: gpt-4
  gpt-4-32k:
    - api_key: sk-xxxxx
      organization: org-xxxxx
      model: gpt-4-32k
```

You can also configure Azure OpenAI endpoints:

```yaml
api_keys:
  gpt-3.5-turbo-16k:
    - api_key: sk-xxxxx
      api_base: https://example.com
      api_type: azure
      api_version: 2023-07-01-preview
      engine: GPT-35-Turbo-16k
```

### Model Selection

Specify which model to use as default:

```yaml
default_request_type: openai
default_completion_kwargs:
  model: gpt-4-32k  # or gpt-4, gpt-3.5-turbo-16k
  temperature: 0.2
  request_timeout: 60
```

### Other Configuration Options

```yaml
# ToolServer connection
use_selfhost_toolserver: true
selfhost_toolserver_url: http://localhost:8080

# Task handling parameters
max_retry_times: 5
max_subtask_chain_length: 15
max_plan_refine_chain_length: 3
max_plan_tree_depth: 3
max_plan_tree_width: 5
max_plan_length: 8192

# Feature toggles
enable_summary: true
enable_ask_human_for_help: False

# Tool configurations
rapidapi_retrieve_tool_count: 0
tool_blacklist:
  - FileSystemEnv_print_filesys_struture
```

```mermaid
classDiagram
    class ConfigurationFile {
        api_keys
        default_request_type
        default_completion_kwargs
        enable_summary
        use_selfhost_toolserver
        selfhost_toolserver_url
        max_retry_times
        max_subtask_chain_length
        max_plan_refine_chain_length
        enable_ask_human_for_help
        tool_blacklist
        record_dir
    }
    
    class ApiKeyConfig {
        model
        api_key
        organization
        api_base?
        api_type?
        api_version?
        engine?
    }
    
    class CompletionConfig {
        model
        temperature
        request_timeout
    }
    
    ConfigurationFile --> ApiKeyConfig: contains
    ConfigurationFile --> CompletionConfig: contains
```

Sources: [assets/config.yml:1-59](). [assets/gpt4_config.yml:1-48](). [assets/gpt-3.5-turbo_config.yml:1-40]()

## Running XAgent

### Command Line Interface

Run XAgent with a specific task using:

```bash
python run.py --task "put your task here" --config-file "assets/config.yml"
```

Additional options:
- `--upload-files`: Select initial files to submit to XAgent
- `--record-dir`: Load from a previous record to reproduce a former run

### Web Interface (GUI)

After starting the containers with `docker compose up`, access the web interface:

1. Navigate to `http://localhost:5173` in your browser
2. Log in with default credentials:
   - Username: `guest`
   - Password: `xagent`

```mermaid
flowchart TB
    subgraph "XAgent Execution Methods"
        CLI["Command Line Interface (CLI)"]
        GUI["Web Interface (GUI)"]
    end
    
    CLI --> run.py["run.py"]
    run.py --> CommandLine["CommandLine class"]
    CommandLine --> Dispatcher["XAgent.dispatcher.Dispatcher"]
    
    GUI --> WebUI["http://localhost:5173"]
    WebUI --> XAgentServer["XAgentServer WebSocket API"]
    XAgentServer --> Dispatcher
    
    Dispatcher --> Planner["XAgent.agent.Planner"]
    Dispatcher --> Actor["XAgent.agent.Actor"]
    Dispatcher --> Reflection["XAgent.agent.ReflectionAgent"]
    
    Planner --> ToolServer["ToolServer API"]
    Actor --> ToolServer
    Reflection --> ToolServer
```

Sources: [README.md:125-148](). [tests/test_run.py:1-58]()

## Output and Records

After execution:

1. Local workspace is created in the `local_workspace` directory
2. Running records containing intermediate steps information are stored in `running_records`
3. The entire workspace from ToolServerNode is copied to `running_records`

You can examine:
- Task statuses
- LLM's input-output pairs
- Used tools
- Generated files

Sources: [README.md:130-137]()

## Optional: Setting up XAgentGen (Custom Models)

For those who want to use custom models instead of OpenAI APIs, XAgent supports running with XAgentLlama via XAgentGen.

### Install CUDA Container Toolkit

Follow the [NVIDIA documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker) to install the CUDA Container Toolkit.

### Set up XAgentGen Container

Pull the pre-built Docker image:

```bash
docker pull xagentteam/xagentgen:latest
```

Or build from source:

```bash
docker build -f dockerfiles/XAgentGen/Dockerfile -t xagentteam/xagentgen .
```

Run the Docker image:

```bash
docker run -it -p 13520:13520 --network tool-server-network -v /host/model/path:/model:rw --gpus all --ipc=host xagentteam/xagentgen:latest python app.py --model-path /model --port 13520
```

### Configure XAgent to Use Custom Model

Use the sample configuration file `assets/xagentllama.yml` and run XAgent with:

```bash
python run.py --task "your task" --config-file "assets/xagentllama.yml"
```

Sources: [XAgentGen/README.md:10-48]()

## Troubleshooting

Common issues:

1. **Docker container not starting**: Ensure Docker and docker-compose are properly installed and have sufficient permissions
2. **API key errors**: Verify your OpenAI API keys are correctly configured with proper organization IDs
3. **Model availability**: Some models like `gpt-4-32k` may have limited availability; have fallback models configured

For tests to ensure your setup is correct, you can run:

```bash
pytest tests/test_model_alias.py  # Test model aliasing
pytest tests/test_1106_model_openai.py  # Test OpenAI API integration
```

Sources: [tests/test_model_alias.py:1-53](). [tests/test_1106_model_openai.py:1-53]()

---

# Page: XAgent Core

# XAgent Core

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [XAgent/agent/utils.py](XAgent/agent/utils.py)
- [XAgent/running_recorder.py](XAgent/running_recorder.py)
- [XAgent/vector_db.py](XAgent/vector_db.py)
- [XAgent/workflow/plan_exec.py](XAgent/workflow/plan_exec.py)
- [XAgentGen/README.md](XAgentGen/README.md)
- [run.py](run.py)

</details>



XAgent Core is the central component of the XAgent system that provides the intelligence, planning, and execution capabilities for autonomous task solving. It serves as the brain of the system, coordinating the planning and execution of complex tasks through a structured workflow involving multiple specialized agents.

This page documents the architecture, components, and workflow of XAgent Core. For information about the ToolServer system that provides tools for XAgent, see [ToolServer](#3). For details about user interfaces, see [XAgentServer](#4) and [XAgentWeb](#5).

## Architecture Overview

XAgent Core follows a structured architecture designed to break down complex tasks into manageable subtasks, plan their execution, and carry them out using appropriate tools. At a high level, XAgent Core consists of three primary components:

```mermaid
graph TD
    subgraph "XAgent Core"
        Dispatcher["Dispatcher"]
        Planner["Planner"]
        Actor["Actor"]
        RunningRecorder["RunningRecorder"]
    end
    
    Task["User Task"] --> Dispatcher
    Dispatcher --> Planner
    Planner --> Actor
    
    Dispatcher --> RunningRecorder
    Planner --> RunningRecorder
    Actor --> RunningRecorder
    
    Actor --> ToolServer["ToolServer"]
    
    subgraph "External Services"
        OpenAI["OpenAI/Azure API"]
    end
    
    Dispatcher --> OpenAI
    Planner --> OpenAI
    Actor --> OpenAI
```

The core components work together to process tasks through a sequential workflow:

1. **Dispatcher**: Dynamically instantiates and dispatches tasks to different specialized agents
2. **Planner**: Generates and refines plans for tasks, breaking them down into subtasks with milestones
3. **Actor**: Executes actions to achieve goals and complete subtasks
4. **RunningRecorder**: Records all task execution details for logging and analysis

Sources: [README.md:50-53]()

## Dispatcher

The Dispatcher is the entry point for user tasks into the XAgent system. It's responsible for:

- Processing the initial user query
- Dynamically instantiating appropriate agents for different aspects of the task
- Dispatching tasks to specialized agents based on their capabilities
- Coordinating the overall task execution flow

This component enables XAgent to be extensible, as new agents can be added to handle different types of tasks or provide specialized capabilities.

## Planner

The Planner is the strategic component of XAgent Core, responsible for generating, refining, and managing execution plans. It plays a crucial role in breaking down complex tasks into manageable subtasks.

### Planning Process

```mermaid
sequenceDiagram
    participant User
    participant Dispatcher as "Dispatcher"
    participant PlanGen as "Plan Generation Agent"
    participant PlanRefine as "Plan Refinement Agent"
    participant PlanExec as "Plan Execution"
    
    User->>Dispatcher: Submit task
    Dispatcher->>PlanGen: Generate initial plan
    PlanGen->>PlanRefine: Initial plan draft
    PlanRefine->>PlanGen: Refinement suggestions
    
    loop Plan Refinement
        PlanGen->>PlanRefine: Updated plan
        PlanRefine->>PlanGen: Additional refinements
    end
    
    PlanRefine->>PlanExec: Finalized plan
    PlanExec->>User: Plan execution results
```

### Plan Structure

The Planner organizes tasks in a hierarchical tree structure:

```mermaid
graph TD
    RootTask["Root Task"]
    SubTask1["Subtask 1"]
    SubTask2["Subtask 2"]
    SubTask3["Subtask 3"]
    SubTask1_1["Subtask 1.1"]
    SubTask1_2["Subtask 1.2"]
    SubTask2_1["Subtask 2.1"]
    
    RootTask --> SubTask1
    RootTask --> SubTask2
    RootTask --> SubTask3
    SubTask1 --> SubTask1_1
    SubTask1 --> SubTask1_2
    SubTask2 --> SubTask2_1
```

Each node in the plan tree is a `Plan` object which contains:
- Task name and description
- Goal of the task
- Status (TODO, IN_PROGRESS, DONE, FAILED, etc.)
- Relations to parent and child tasks

The implementation limits the plan tree's width and depth through configuration parameters (`max_plan_tree_width` and `max_plan_tree_depth`).

Key classes involved in planning:
- `PlanAgent`: Manages the overall planning process
- `PlanRefineChain`: Tracks plan refinement history
- `Plan`: Represents a node in the plan tree

Sources: [XAgent/workflow/plan_exec.py:32-495](), [README.md:51-52]()

## Actor

The Actor is the execution component of XAgent Core, responsible for carrying out actions to achieve goals and complete the subtasks defined in the plan. It serves as the bridge between the planning stage and actual tool usage.

### Actor Responsibilities

- Executing subtasks according to the plan
- Using appropriate tools through ToolServer
- Evaluating the results of tool executions
- Deciding next steps based on execution results
- Collaborating with humans when necessary

### Tool Interaction Process

```mermaid
sequenceDiagram
    participant Actor as "Actor"
    participant ToolAgent as "Tool Agent"
    participant ToolServer as "ToolServer"
    participant Tools as "Tools (Web/Shell/Python/etc.)"
    
    Actor->>ToolAgent: Request tool use for subtask
    ToolAgent->>ToolServer: Select appropriate tool
    ToolServer->>Tools: Execute tool operation
    Tools->>ToolServer: Operation result
    ToolServer->>ToolAgent: Tool execution result
    ToolAgent->>Actor: Processed result
```

The Actor uses a specialized Tool Agent to interact with ToolServer, which provides access to various tools like the File Editor, Python Notebook, Web Browser, Shell, and Rapid API.

Sources: [README.md:53]()

## RunningRecorder

The RunningRecorder is responsible for logging and persistence of the execution process. It captures the entire execution flow, which is valuable for debugging, analysis, and reproducibility.

### Information Recorded

- LLM input/output pairs
- Tool server requests and responses
- Tool calls and their results
- Plan modifications
- Configuration settings
- Task query information

```mermaid
graph TD
    subgraph "RunningRecorder"
        RecordRootDir["Record Root Directory"]
        LLM_IO["LLM Input/Output Pairs"]
        ToolServerPairs["Tool Server Pairs"]
        PlanModifications["Plan Modifications"]
        ConfigFile["Configuration File"]
        QueryFile["Query File"]
    end
    
    Dispatcher --> LLM_IO
    Planner --> PlanModifications
    Actor --> ToolServerPairs
    
    LLM_IO --> RecordRootDir
    ToolServerPairs --> RecordRootDir
    PlanModifications --> RecordRootDir
    ConfigFile --> RecordRootDir
    QueryFile --> RecordRootDir
    
    User --> LocalWorkspace["Local Workspace"]
    RecordRootDir --> RunningRecords["Running Records"]
```

Each execution generates a unique directory in the `running_records` folder, containing all the recorded information. This system allows for loading from previous records to reproduce a former run.

Sources: [XAgent/running_recorder.py:1-398](), [README.md:134-137]()

## Command-Line Interface

XAgent Core can be accessed directly through a command-line interface, which is implemented in the `run.py` file. This provides a simple way to interact with XAgent without using the web interface.

### Usage

```
python run.py --task "your task description" --config-file "assets/config.yml"
```

### Command-Line Parameters

| Parameter | Description |
|-----------|-------------|
| `--task` | The task description (required) |
| `--upload-files` | List of files to upload |
| `--model` | Model identifier for the task |
| `--record-dir` | Directory to record task execution logs |
| `--mode` | Operational mode: 'auto' or 'manual' |
| `--quiet` | Run in quiet mode; minimal output |
| `--config-file` | Path to the configuration file |
| `--enable-ask-human-for-help` | Flag to enable asking for human assistance |

The command-line interface creates a `CommandLine` object with the provided parameters and starts the XAgent process. The execution is then handled by the XAgent Core components.

Sources: [run.py:1-92]()

## Integration with External Systems

### OpenAI/Azure API Integration

XAgent Core relies heavily on OpenAI/Azure's language models for its intelligence. It uses these models for:

- Plan generation and refinement
- Tool selection and usage
- Reasoning about task execution
- Summarizing results

The integration is configured in the `config.yml` file, which specifies:
- API keys
- Model selection (recommended: `gpt-4-32k` or `gpt-4`)
- Default completion parameters

### ToolServer Integration

XAgent Core interacts with ToolServer to execute various tools needed for task completion. The integration works through API calls to the ToolServer, which runs as a separate Docker container.

Available tools include:
- File Editor: for writing, reading, and modifying files
- Python Notebook: for running Python code
- Web Browser: for searching and visiting webpages
- Shell: for executing shell commands
- Rapid API: for accessing external APIs

### XAgentGen Integration (Optional)

XAgent can optionally integrate with XAgentGen to use customized models instead of OpenAI's models. This is configured by using a different configuration file (e.g., `assets/xagentllama.yml`).

XAgentGen implements guided generation with constrained text generation, allowing models to generate function calls with complex JSON schema.

Sources: [XAgentGen/README.md:1-48](), [README.md:118-122]()

## Core Components Workflow

The complete workflow of XAgent Core involves the coordinated operation of all components to process a user task from beginning to end:

```mermaid
flowchart TD
    User["User"] -->|"Submits task"| Dispatcher
    
    subgraph "XAgent Core Workflow"
        Dispatcher -->|"Processes query"| PlanGen["Plan Generation Agent"]
        PlanGen -->|"Creates initial plan"| PlanRefine["Plan Refinement Agent"]
        PlanRefine -->|"Refines plan"| Plan["Finalized Plan"]
        
        Plan -->|"Executes subtasks"| Actor
        Actor -->|"Uses tools via"| ToolAgent["Tool Agent"]
        ToolAgent -->|"Executes tools"| ToolServer
        
        Actor -->|"Evaluates results"| PlanRefine
        PlanRefine -->|"Updates plan if needed"| Plan
        
        Dispatcher -->|"Records interactions"| RunningRecorder
        PlanGen -->|"Records plan generation"| RunningRecorder
        PlanRefine -->|"Records plan refinement"| RunningRecorder
        Actor -->|"Records tool usage"| RunningRecorder
    end
    
    RunningRecorder -->|"Saves to"| Records["Running Records"]
    ToolServer -->|"Provides tool results"| Actor
    Actor -->|"Returns results"| User
```

This workflow demonstrates how XAgent Core processes a task:

1. The user submits a task to the Dispatcher
2. The Dispatcher processes the query and triggers the Plan Generation Agent
3. The initial plan is created and then refined by the Plan Refinement Agent
4. The Actor executes the plan by using tools through ToolAgent and ToolServer
5. Results are evaluated, and the plan may be updated if needed
6. All interactions are recorded by the RunningRecorder
7. Finally, the results are returned to the user

Throughout this process, XAgent Core aims to solve tasks autonomously but can also collaborate with humans when needed.

Sources: [README.md:42-53]()

## System Requirements and Configuration

XAgent Core requires:
- Python 3.10 or higher
- OpenAI API keys (at least one `gpt-3.5-turbo-16k` key, preferably `gpt-4-32k` or `gpt-4`)
- Docker and Docker Compose (for ToolServer)
- Configured `assets/config.yml` file

The configuration file controls various aspects of XAgent Core's behavior, including:
- Model selection and parameters
- Plan tree constraints (max width and depth)
- Maximum subtask chain length
- Maximum retry times
- Human assistance settings

Sources: [README.md:115-122]()

---

# Page: Task Planning System

# Task Planning System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgent/agent/dispatcher.py](XAgent/agent/dispatcher.py)
- [XAgent/agent/plan_generate_agent/prompt.py](XAgent/agent/plan_generate_agent/prompt.py)
- [XAgent/agent/plan_refine_agent/prompt.py](XAgent/agent/plan_refine_agent/prompt.py)
- [XAgent/agent/reflect_agent/prompt.py](XAgent/agent/reflect_agent/prompt.py)
- [XAgent/agent/tool_agent/prompt.py](XAgent/agent/tool_agent/prompt.py)
- [XAgent/agent/utils.py](XAgent/agent/utils.py)
- [XAgent/ai_functions/request/utils.py](XAgent/ai_functions/request/utils.py)
- [XAgent/inner_loop_search_algorithms/ReACT.py](XAgent/inner_loop_search_algorithms/ReACT.py)
- [XAgent/running_recorder.py](XAgent/running_recorder.py)
- [XAgent/vector_db.py](XAgent/vector_db.py)
- [XAgent/workflow/plan_exec.py](XAgent/workflow/plan_exec.py)
- [XAgent/workflow/task_handler.py](XAgent/workflow/task_handler.py)
- [XAgent/workflow/working_memory.py](XAgent/workflow/working_memory.py)
- [run.py](run.py)

</details>



The Task Planning System is a core component of XAgent that converts high-level user queries into executable plans. It breaks down complex tasks into manageable subtasks, coordinates their execution, and adapts plans based on execution results. This system serves as the cognitive engine that enables XAgent to approach problems methodically and solve them effectively.

For information about the tools used to execute the subtasks, see [Tool System](#2.2).

## System Overview

The Task Planning System consists of multiple interacting components that work together to create and execute plans. The system follows a hierarchical approach to task handling, first generating a high-level plan, then refining it as needed, and finally executing each subtask with appropriate tools.

```mermaid
flowchart TD
    subgraph "Task Planning System"
        Dispatcher["Dispatcher"] --> Planner["Planner"]
        Planner --> PlanGenAgent["Plan Generate Agent"]
        PlanGenAgent --> PlanRefineAgent["Plan Refine Agent"]
        PlanRefineAgent --> TaskHandler["Task Handler"]
        TaskHandler --> ReACTSearch["ReACT Chain Search"]
        ReACTSearch --> ToolAgent["Tool Agent"]
        ToolAgent --> ReflectionAgent["Reflection Agent"]
    end
    
    User["User Query"] --> Dispatcher
    ToolAgent --> ToolServer["ToolServer"]
    ReflectionAgent --> RunningRecorder["RunningRecorder"]
    
    classDef component stroke:#333,stroke-width:1px
    class Dispatcher,Planner,PlanGenAgent,PlanRefineAgent,TaskHandler,ReACTSearch,ToolAgent,ReflectionAgent component
```

Sources: [XAgent/workflow/task_handler.py](), [XAgent/agent/dispatcher.py]()), [XAgent/inner_loop_search_algorithms/ReACT.py]()

## Core Components and Workflow

### 1. Plan Generation

The plan generation phase breaks down the user's high-level task into a tree of subtasks. This is handled by the Plan Generate Agent.

```mermaid
sequenceDiagram
    participant User
    participant TaskHandler as "TaskHandler"
    participant PlanAgent as "PlanAgent"
    participant PlanGenAgent as "Plan Generate Agent"
    
    User->>TaskHandler: Submit Query
    TaskHandler->>PlanAgent: initial_plan_generation()
    PlanAgent->>PlanGenAgent: Generate Initial Plan
    PlanGenAgent->>PlanAgent: Return Subtask Tree
    PlanAgent->>TaskHandler: Plan Created
```

Each subtask in the plan has a structured JSON format:

```
{
  "subtask name": string,
  "goal.goal": string,
  "goal.criticism": string,
  "milestones": list[string]
}
```

The Plan Generate Agent is designed to create efficient, non-redundant subtasks that collectively achieve the user's goal. It follows these key principles:
- Keep plans feasible and efficient
- Combine similar goals into single subtasks
- Avoid unnecessary complexity
- Utilize the capabilities of Large Language Models

Sources: [XAgent/agent/plan_generate_agent/prompt.py:1-41](), [XAgent/workflow/plan_exec.py:141-183]()

### 2. Plan Refinement

Plans can be refined when necessary, particularly after a subtask fails or when additional information becomes available. The Plan Refine Agent handles this process through several operations:

1. **Split**: Divide a complex subtask into smaller, more manageable subtasks
2. **Add**: Add new subtasks as siblings to existing ones
3. **Delete**: Remove unnecessary subtasks
4. **Exit**: Conclude the refinement process

```mermaid
flowchart TD
    subgraph "Plan Tree Operations"
        Split["SPLIT: Divides subtask into children<br>e.g., 1.2 → 1.2.1, 1.2.2"]
        Add["ADD: Adds sibling subtasks<br>e.g., after 1.1 → add 1.2, 1.3"]
        Delete["DELETE: Removes a subtask<br>e.g., delete 1.2.1"]
        Exit["EXIT: Completes refinement"]
    end
    
    Failed["Failed Subtask"] --> Split
    NeedsMoreTasks["Incomplete Plan"] --> Add
    RedundantTask["Redundant Task"] --> Delete
    PlanComplete["Plan Complete"] --> Exit
```

The plan tree has configurable constraints:
- `max_plan_tree_width`: Maximum number of subtasks a parent task can have
- `max_plan_tree_depth`: Maximum levels of task hierarchy
- `max_plan_refine_chain_length`: Maximum number of refinement operations

Sources: [XAgent/agent/plan_refine_agent/prompt.py:1-58](), [XAgent/workflow/plan_exec.py:205-266]()

### 3. Task Execution via Inner and Outer Loops

The execution of plans is managed by the TaskHandler through an outer loop and inner loop pattern:

```mermaid
flowchart TD
    subgraph "Task Execution Loops"
        OuterLoop["Outer Loop<br>task_handler.outer_loop()"]
        InnerLoop["Inner Loop<br>task_handler.inner_loop()"]
        ReACT["ReACT Chain Search<br>search_method.run()"]
        ToolCalls["Tool Calls<br>tool_agent.parse()"]
    end
    
    OuterLoop -->|"For each subtask"| InnerLoop
    InnerLoop -->|"Execute subtask"| ReACT
    ReACT -->|"Make tool calls"| ToolCalls
    ToolCalls -->|"Return result"| ReACT
    ReACT -->|"Success/Failure"| OuterLoop
    
    OuterLoop -->|"After subtask"| PosteriorProcess["Posterior Process<br>get_posterior_knowledge()"]
    PosteriorProcess -->|"Next subtask"| OuterLoop
```

The outer loop (`TaskHandler.outer_loop`) manages the sequence of subtasks:
1. Gets the next subtask from the plan
2. Executes it using the inner loop
3. Processes the results
4. Refines the plan if needed
5. Repeats until all subtasks are complete

The inner loop (`TaskHandler.inner_loop`) handles individual subtask execution:
1. Dispatches an agent for the task
2. Creates a search method (ReACT Chain Search)
3. Executes the task
4. Records the results

Sources: [XAgent/workflow/task_handler.py:65-196](), [XAgent/workflow/task_handler.py:196-266](), [XAgent/inner_loop_search_algorithms/ReACT.py:56-114]()

### 4. ReACT Chain Search

The ReACT (Reasoning and Acting) Chain Search algorithm is used to execute individual subtasks. It implements a sequential approach:

```mermaid
sequenceDiagram
    participant TaskHandler
    participant ReACT as "ReACTChainSearch"
    participant ToolAgent
    participant ToolServer
    
    TaskHandler->>ReACT: run(config, agent, task_id)
    loop For each step in chain
        ReACT->>ReACT: make_message(now_node)
        ReACT->>ToolAgent: parse(messages, functions)
        ToolAgent->>ReACT: Return tool_node
        ReACT->>ToolServer: handle_tool_call(tool_node)
        ToolServer->>ReACT: Return tool_output
        alt Tool call status
            ReACT->>ReACT: Process next step
        else Subtask complete
            ReACT->>TaskHandler: Return with success
        else Subtask failed
            ReACT->>TaskHandler: Return with failure
        end
    end
```

Key constraints in ReACT Chain Search:
- `max_subtask_chain_length`: Maximum number of steps in a subtask chain
- It builds a tree of tool calls, with each node representing an action

Sources: [XAgent/inner_loop_search_algorithms/ReACT.py:56-114](), [XAgent/inner_loop_search_algorithms/ReACT.py:199-314]()

### 5. Tool Agent

The Tool Agent is responsible for executing tool calls to interact with the real world. It receives a subtask, thinks about how to approach it, and then executes appropriate tool calls.

```mermaid
flowchart LR
    subgraph "Tool Agent Workflow"
        Receive["Receive subtask"]
        Think["Think and plan approach"]
        Choose["Choose appropriate tool"]
        Execute["Execute tool call"]
        Process["Process results"]
        NextStep["Decide next step"]
    end
    
    Receive --> Think
    Think --> Choose
    Choose --> Execute
    Execute --> Process
    Process --> NextStep
    NextStep -->|"Continue subtask"| Choose
    NextStep -->|"Submit subtask"| Complete["Subtask complete"]
```

The Tool Agent has access to various resources:
- Internet access for search and information gathering
- File system for reading and writing files
- Python notebook for code execution
- Shell environment for executing commands
- And other specialized tools

Sources: [XAgent/agent/tool_agent/prompt.py:1-59]()

### 6. Reflection and Learning

After a subtask is completed, the system performs reflection to learn from the experience:

```mermaid
flowchart TD
    subgraph "Reflection Process"
        Summary["Summary of actions"]
        ReflectPlan["Reflection on planning"]
        ReflectTools["Reflection on tool usage"]
    end
    
    CompletedTask["Completed Subtask"] --> Summary
    Summary --> ReflectPlan
    ReflectPlan --> ReflectTools
    ReflectTools --> Knowledge["Posterior Knowledge"]
    Knowledge -->|"Inform future tasks"| NextTasks["Future Task Planning"]
```

The reflection process extracts three types of knowledge:
1. **Summary**: A concise description of what was done and achieved
2. **Plan Reflection**: Insights about the planning process that can improve future plans
3. **Tool Reflection**: Lessons about tool usage and effectiveness

This knowledge is stored and used to improve planning and execution in subsequent tasks.

Sources: [XAgent/agent/reflect_agent/prompt.py:1-27](), [XAgent/workflow/task_handler.py:268-300]()

## Data Structure: Plan Tree

Plans in XAgent are represented as tree structures, where each node is a subtask. The hierarchical structure allows for organized task decomposition and execution.

```mermaid
graph TD
    Task1["Task 1<br>Root Task"] --> Task1_1["Task 1.1"]
    Task1 --> Task1_2["Task 1.2"]
    Task1 --> Task1_3["Task 1.3"]
    
    Task1_2 --> Task1_2_1["Task 1.2.1"]
    Task1_2 --> Task1_2_2["Task 1.2.2"]
    
    classDef current stroke:#333,stroke-width:2px
    class Task1_2 current
```

Task IDs follow a hierarchical numbering scheme (e.g., "1.2.1") that indicates the position in the tree. The system traverses this tree in inorder traversal to execute subtasks sequentially.

Key operations on the plan tree:
- `Plan.make_relation(parent, child)`: Establish parent-child relationship
- `Plan.pop_next_subtask(current)`: Get the next subtask to execute
- `Plan.get_remaining_subtask(current)`: Get all remaining subtasks
- `Plan.get_inorder_travel(plan)`: Get subtasks in execution order

Sources: [XAgent/workflow/plan_exec.py:18-34](), [XAgent/workflow/plan_exec.py:318-495]()

## Recording and Monitoring

The RunningRecorder keeps track of all operations performed during task execution:

```mermaid
flowchart TD
    subgraph "RunningRecorder"
        LLM["LLM Interactions"]
        Tool["Tool Calls"]
        Plan["Plan Modifications"]
        Query["Query Information"]
        Config["Configuration"]
    end
    
    TaskHandler -->|"regist_tool_call()"| Tool
    PlanAgent -->|"regist_plan_modify()"| Plan
    Agents -->|"regist_llm_inout()"| LLM
    System -->|"regist_query()"| Query
    System -->|"regist_config()"| Config
    
    LLM --> RecordDir["Record Directory"]
    Tool --> RecordDir
    Plan --> RecordDir
    Query --> RecordDir
    Config --> RecordDir
```

The recorder creates a unique directory for each run with subdirectories for different types of data:
- LLM input/output pairs
- Tool server calls
- Plan refinements
- Task execution logs

This comprehensive recording enables debugging, reproducibility, and analysis of the system's performance.

Sources: [XAgent/running_recorder.py:34-93](), [XAgent/running_recorder.py:108-130](), [XAgent/running_recorder.py:201-224]()

## Configuration Parameters

The Task Planning System behavior can be customized through several configuration parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `max_plan_tree_width` | Maximum number of subtasks under a parent | 4 |
| `max_plan_tree_depth` | Maximum depth of the subtask hierarchy | 3 |
| `max_plan_refine_chain_length` | Maximum number of plan refinement operations | 4 |
| `max_subtask_chain_length` | Maximum steps in a subtask execution chain | 10 |
| `enable_ask_human_for_help` | Whether to allow asking humans for help | False |
| `max_retry_times` | Maximum attempts for failed subtasks | 3 |

These parameters can be set via command line arguments or in the configuration file.

Sources: [run.py:18-36]()

## Example Workflow

1. **User submits a query**: "Write a Python calculator"
2. **Plan Generate Agent creates a plan**:
   - Task 1: Define calculator requirements
   - Task 2: Implement basic arithmetic operations
   - Task 3: Create a user interface
   - Task 4: Test the calculator
3. **Task Handler processes each subtask**:
   - For Task 1: Defines the requirements using ReACT Chain Search
   - For Task 2: Implements the operations using the Tool Agent
   - If Task 2 fails: Plan Refine Agent might split it into smaller tasks
   - For Task 3: Creates the UI
   - For Task 4: Tests the calculator
4. **Reflection Agent learns from the process**
5. **Results are returned to the user**

Throughout this process, the Task Planning System adapts to challenges, refines plans as needed, and leverages appropriate tools to accomplish the user's goal.

## Integration with Other XAgent Components

The Task Planning System integrates with other XAgent components:

- **XAgent Core**: The Task Planning System is a central component of XAgent Core
- **ToolServer**: Tool Agent calls tools provided by ToolServer
- **Command Line Interface**: Users can submit tasks through the CLI
- **XAgentServer**: Web interface communicates with the Task Planning System through XAgentServer

This integration enables a seamless user experience while maintaining the structured, methodical approach to task execution.

Sources: [XAgent/agent/dispatcher.py:94-201](), [XAgent/workflow/task_handler.py:16-63]()

---

# Page: Tool System

# Tool System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ToolServer/ToolServerNode/core/envs/pycoding.py](ToolServer/ToolServerNode/core/envs/pycoding.py)
- [XAgent/agent/plan_generate_agent/prompt.py](XAgent/agent/plan_generate_agent/prompt.py)
- [XAgent/agent/plan_refine_agent/prompt.py](XAgent/agent/plan_refine_agent/prompt.py)
- [XAgent/agent/reflect_agent/prompt.py](XAgent/agent/reflect_agent/prompt.py)
- [XAgent/agent/summarize.py](XAgent/agent/summarize.py)
- [XAgent/agent/tool_agent/agent.py](XAgent/agent/tool_agent/agent.py)
- [XAgent/agent/tool_agent/prompt.py](XAgent/agent/tool_agent/prompt.py)
- [XAgent/ai_functions/pure_functions/task_manage_functions.yml](XAgent/ai_functions/pure_functions/task_manage_functions.yml)
- [XAgent/ai_functions/request/obj_generator.py](XAgent/ai_functions/request/obj_generator.py)
- [XAgent/ai_functions/request/utils.py](XAgent/ai_functions/request/utils.py)

</details>



The Tool System in XAgent provides a mechanism for autonomous agents to interact with external resources and perform actions in the world. This system enables agents to use specialized tools like file operations, Python code execution, web browsing, and shell commands to accomplish complex tasks. It serves as the bridge between the agent's reasoning capabilities and the ability to effect changes in the external environment.

For information about the specific tools available and their capabilities, see [Tool Types and Capabilities](#3.2). For details on how tool execution is managed in isolated environments, see [ToolServer Architecture](#3.1).

## Architecture Overview

The Tool System consists of several key components that work together to enable tool usage by agents:

```mermaid
flowchart TD
    subgraph "XAgent Core"
        PlannerAgent["Planner Agent"]
        ToolAgent["Tool Agent"]
        ReflectionAgent["Reflection Agent"]
        Dispatcher["Dispatcher"]
    end
    
    subgraph "Tool System"
        OBJGenerator["OBJGenerator"]
        FunctionManager["Function Manager"]
        ToolNode["ToolNode"]
        SchemaValidator["Schema Validator"]
    end
    
    subgraph "ToolServer"
        ToolServerManager["ToolServerManager"]
        ToolServerNode["ToolServerNode"]
        Tools["Available Tools"]
    end

    PlannerAgent -->|"creates plan with\nexpected tools"| ToolAgent
    ToolAgent -->|"calls"| OBJGenerator
    OBJGenerator -->|"validates\nfunction calls"| SchemaValidator
    OBJGenerator -->|"executes\nrequests"| ToolServerManager
    ToolServerManager -->|"routes to"| ToolServerNode
    ToolServerNode -->|"executes"| Tools
    Tools -->|"returns results"| ToolAgent
    ToolAgent -->|"creates"| ToolNode
    ToolNode -->|"records execution"| ReflectionAgent
```

Sources: [XAgent/agent/tool_agent/agent.py:16-175](), [XAgent/ai_functions/request/obj_generator.py:20-224]()

The Tool System's architecture enables:

1. **Tool Call Generation**: The ToolAgent decides which tool to use based on the current task
2. **Schema Validation**: The OBJGenerator validates tool calls against predefined schemas
3. **Tool Execution**: Valid tool calls are forwarded to the ToolServer for execution
4. **Result Processing**: Tool execution results are returned to the agent for further action

## Tool Agent

The Tool Agent is the primary component responsible for executing subtasks using appropriate tools. It interprets the plan created by the Planner Agent and translates high-level goals into specific tool calls.

```mermaid
sequenceDiagram
    participant Dispatcher
    participant ToolAgent
    participant OBJGenerator
    participant ToolServer
    
    Dispatcher->>ToolAgent: Assign subtask
    Note over ToolAgent: Parse subtask requirements
    ToolAgent->>OBJGenerator: Generate tool call
    OBJGenerator->>OBJGenerator: Validate against schema
    
    alt Schema validation fails
        OBJGenerator->>OBJGenerator: Attempt to fix JSON
        OBJGenerator->>ToolAgent: Return error for retry
    else Schema validation succeeds
        OBJGenerator->>ToolServer: Execute tool call
        ToolServer->>OBJGenerator: Return tool result
        OBJGenerator->>ToolAgent: Return formatted result
    end
    
    ToolAgent->>ToolAgent: Create ToolNode with result
    ToolAgent->>Dispatcher: Return subtask result
```

Sources: [XAgent/agent/tool_agent/agent.py:27-175](), [XAgent/agent/tool_agent/prompt.py:1-96]()

The Tool Agent uses a specialized prompt that provides:
- Context about the current subtask
- Available operations (tool calling or subtask submission)
- Guidelines for tool usage
- Budget constraints (maximum number of tool calls)

## Tool Calls and Schema Validation

Tool calls in XAgent follow a structured format and undergo rigorous schema validation to ensure correctness.

### Function Call Structure

Tool calls are structured as function calls with the following format:

```
{
  "name": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2",
    ...
  }
}
```

For the OpenAI request type, tool calls are wrapped in a `subtask_handle` function with a `tool_call` field:

```
{
  "name": "subtask_handle",
  "arguments": {
    "tool_call": {
      "tool_name": "tool_name",
      "tool_input": {
        "param1": "value1",
        "param2": "value2",
        ...
      }
    },
    "other_fields": {...}
  }
}
```

Sources: [XAgent/agent/tool_agent/agent.py:104-132]()

### Validation Process

The OBJGenerator class handles validation of tool calls against their schemas:

1. **Schema Retrieval**: The tool schema is retrieved based on the tool name
2. **JSON Validation**: The tool arguments are validated against the schema
3. **Error Handling**: If validation fails, the system attempts to fix the JSON
4. **Retry Mechanism**: If the fix fails, the error is reported and the call is retried

```mermaid
flowchart TD
    A["Start Validation"] --> B{"Is JSON\nValid?"}
    B -->|"Yes"| C["Execute Tool Call"]
    B -->|"No"| D["Try to Fix JSON"]
    D --> E{"Fix\nSuccessful?"}
    E -->|"Yes"| B
    E -->|"No"| F["Report Error & Retry"]
    F --> A
```

Sources: [XAgent/ai_functions/request/obj_generator.py:94-169]()

## Tool Types and Implementations

XAgent supports various types of tools that can be used to accomplish different tasks. Here's an overview of some key tool types:

| Tool Type | Description | Common Uses |
|-----------|-------------|-------------|
| FileSystemEnv | File operations (read/write/list) | Managing files and directories |
| PythonNotebook | Execute Python code in a notebook | Data analysis, testing code |
| ShellEnv | Execute shell commands | System operations, installations |
| WebBrowser | Browse the web and extract information | Research, information gathering |
| RapidAPI | Make API calls to external services | Data retrieval, integrations |

### Python Notebook Example

The Python Notebook tool provides a way to execute Python code within a Jupyter-like environment:

```mermaid
sequenceDiagram
    participant ToolAgent
    participant PythonNotebook
    participant NotebookClient
    participant Kernel
    
    ToolAgent->>PythonNotebook: execute_cell(code)
    PythonNotebook->>NotebookClient: async_execute_cell()
    NotebookClient->>Kernel: Send code for execution
    Kernel->>NotebookClient: Return output
    NotebookClient->>PythonNotebook: Return cell outputs
    PythonNotebook->>ToolAgent: Format and return results
```

Sources: [ToolServer/ToolServerNode/core/envs/pycoding.py:16-181]()

## Tool Usage Workflow

The complete workflow of tool usage in XAgent involves several steps:

1. **Task Planning**: The Planner identifies which tools are needed for a task
2. **Subtask Assignment**: The Dispatcher assigns a subtask to the Tool Agent
3. **Tool Selection**: The Tool Agent selects the appropriate tool for the current step
4. **Tool Call**: The Tool Agent generates a tool call with the necessary parameters
5. **Validation**: The OBJGenerator validates the tool call against its schema
6. **Execution**: The validated tool call is sent to the ToolServer for execution
7. **Result Processing**: The tool execution result is returned to the Tool Agent
8. **Action Recording**: The action and its result are recorded as a ToolNode
9. **Reflection**: The Reflection Agent learns from the tool usage experience

### Action Summarization

After tool execution, actions are summarized to provide concise information about what was done:

```mermaid
flowchart TD
    A["Tool Execution Completed"] --> B["Record Raw Action"]
    B --> C["Summarize Action"]
    C --> D["Generate Action Summary"]
    D --> E["Create ToolNode"]
    E --> F["Add to Running Records"]
    F --> G["Reflect on Actions"]
```

Sources: [XAgent/agent/summarize.py:11-163](), [XAgent/agent/reflect_agent/prompt.py:1-43]()

## Integration with Other XAgent Components

The Tool System is tightly integrated with other components of XAgent:

1. **Planner Integration**: The Planner Agent includes expected tools in its subtask plans
2. **Tool Server Communication**: The Tool System communicates with the ToolServer to execute tools in isolated environments
3. **Task Recording**: All tool usage is recorded for later inspection and learning
4. **Reflection Learning**: The Reflection Agent learns from tool usage to improve future performance

```mermaid
flowchart TD
    UserQuery["User Query"] --> Dispatcher
    Dispatcher --> PlannerAgent
    
    PlannerAgent -->|"creates plan with\nexpected tools"| PlanRefineAgent
    PlanRefineAgent -->|"refines plan if needed"| ToolAgent
    
    ToolAgent -->|"executes tools via"| ToolSystem["Tool System"]
    ToolSystem -->|"calls"| ToolServer
    ToolServer -->|"returns results"| ToolSystem
    ToolSystem -->|"provides results"| ToolAgent
    
    ToolAgent -->|"reports progress"| RunningRecorder
    ToolAgent -->|"submits completed subtask"| ReflectionAgent
    ReflectionAgent -->|"learns from tool usage"| Dispatcher
    Dispatcher -->|"assigns next subtask or\ncompletes task"| UserResponse["User Response"]
```

Sources: [XAgent/agent/plan_generate_agent/prompt.py:1-55](), [XAgent/agent/plan_refine_agent/prompt.py:1-83](), [XAgent/agent/tool_agent/prompt.py:1-96]()

## Schema Validation and Error Recovery

One of the key strengths of XAgent's Tool System is its robust schema validation and error recovery mechanism.

### Schema Definition

Tools are defined with JSON schemas that specify:
- Required parameters
- Parameter types
- Parameter constraints
- Default values

### Error Recovery Process

When a tool call fails schema validation:

1. The error is logged
2. The broken JSON is sent to the AI model with the error message
3. The model attempts to fix the JSON to match the schema
4. The fixed JSON is validated again
5. If validation succeeds, the tool call proceeds
6. If validation fails again, the process retries up to 3 times

```mermaid
flowchart TD
    A["Generate Tool Call"] --> B["Validate Against Schema"]
    B -->|"Valid"| C["Execute Tool"]
    B -->|"Invalid"| D["Log Error"]
    D --> E["AI Fixes JSON"]
    E --> F["Validate Fixed JSON"]
    F -->|"Valid"| C
    F -->|"Invalid"| G{"Retry < 3?"}
    G -->|"Yes"| A
    G -->|"No"| H["Report Failure"]
```

Sources: [XAgent/ai_functions/request/obj_generator.py:94-169](), [XAgent/agent/tool_agent/agent.py:104-132]()

## Conclusion

The Tool System is a critical component of XAgent that bridges the gap between agent reasoning and real-world actions. Through a structured approach to tool definition, validation, execution, and result processing, it enables autonomous agents to effectively use a wide range of tools to accomplish complex tasks.

The combination of robust schema validation, error recovery mechanisms, and integration with other XAgent components makes the Tool System both powerful and reliable, allowing agents to focus on high-level reasoning while ensuring that tool usage is correct and effective.

---

# Page: Command Line Interface

# Command Line Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgent/agent/utils.py](XAgent/agent/utils.py)
- [XAgent/running_recorder.py](XAgent/running_recorder.py)
- [XAgent/vector_db.py](XAgent/vector_db.py)
- [XAgent/workflow/plan_exec.py](XAgent/workflow/plan_exec.py)
- [run.py](run.py)

</details>



The Command Line Interface (CLI) provides a way to interact with XAgent directly from the terminal, bypassing the need for the web interface. This allows for programmatic interaction with XAgent, making it suitable for automation, scripting, and batch processing of tasks.

For information about the web-based interface, see [XAgentWeb](#5).

## 1. Overview

```mermaid
graph TD
    User["User"] -->|"Inputs commands"| CLI["Command Line Interface"]
    CLI -->|"Creates task"| XAgent["XAgent Core"]
    XAgent -->|"Executes tools via"| ToolServer["ToolServer"]
    XAgent -->|"Uses"| LLM["OpenAI/Other LLM API"]
    
    CLI -->|"Records execution"| Recorder["RunningRecorder"]
    
    subgraph "XAgent System"
        XAgent
        ToolServer
        Recorder
    end
```

*Diagram: XAgent CLI Integration with Core Components*

The Command Line Interface provides a simple way to interact with XAgent Core directly. It processes user commands, initializes the XAgent system with the specified task and parameters, and manages the execution flow. The CLI integrates with the RunningRecorder to log all actions and results for later inspection.

Sources: [run.py:1-91]()

## 2. Command Line Arguments

XAgent's CLI accepts a variety of command line arguments to configure task execution:

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--task` | Yes | N/A | The task description for XAgent to perform |
| `--upload-files` | No | None | List of files to upload for the task |
| `--model` | No | From config | Model identifier (e.g., "gpt-4") |
| `--record-dir` | No | From config | Directory to store execution logs |
| `--mode` | No | "auto" | Execution mode: "auto" or "manual" |
| `--quiet` | No | False | Run with minimal output, logging to file |
| `--max-subtask-chain-length` | No | From config | Maximum length of subtask chain |
| `--enable-ask-human-for-help` | No | False | Enable asking human for assistance |
| `--max-plan-refine-chain-length` | No | From config | Maximum plan refinement iterations |
| `--max-plan-tree-depth` | No | From config | Maximum depth of plan tree |
| `--max-plan-tree-width` | No | From config | Maximum width of plan tree |
| `--max-retry-times` | No | From config | Maximum number of retry attempts |
| `--config-file` | No | "assets/config.yml" | Path to configuration file |

Sources: [run.py:9-38]()

## 3. Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Parser as "ArgumentParser"
    participant CommandProcess as "execute_command_line_process"
    participant CommandLine as "CommandLine"
    participant XAgentCore as "XAgent Core"
    
    User->>Parser: Input command with arguments
    Parser->>CommandProcess: Parsed arguments
    
    alt Quiet Mode
        CommandProcess->>CommandProcess: Redirect stdout to file
    end
    
    CommandProcess->>CommandLine: Create CommandLineParam
    CommandLine->>CommandLine: Initialize CommandLine object
    CommandLine->>XAgentCore: Start execution
    
    XAgentCore->>CommandLine: Return results
    
    alt Not Quiet Mode
        CommandLine->>User: Display results in terminal
    else Quiet Mode
        CommandLine->>CommandProcess: Write results to file
    end
```

*Diagram: CLI Command Execution Flow*

When executing a command through the XAgent CLI, the following process occurs:

1. Command line arguments are parsed using Python's `argparse` module
2. The parsed arguments are processed by `execute_command_line_process()`
3. If quiet mode is enabled, stdout is redirected to a file
4. A `CommandLineParam` object is created with the task and configuration
5. A `CommandLine` object is created and its `start()` method is called
6. XAgent Core processes the task and returns results
7. Results are displayed in the terminal or written to a file

Sources: [run.py:41-83]()

## 4. Usage Examples

### Basic Task Execution

To run a simple task:

```bash
python run.py --task "Find information about climate change and summarize it"
```

### Uploading Files for Processing

To upload files along with your task:

```bash
python run.py --task "Analyze this CSV data and create charts" --upload-files data.csv
```

### Using a Specific Model

To specify which LLM to use:

```bash
python run.py --task "Write a short story" --model "gpt-4"
```

### Running in Quiet Mode

To run with minimal output (results written to file):

```bash
python run.py --task "Analyze website performance" --quiet
```

### Using Manual Mode

To use manual mode with human confirmation for steps:

```bash
python run.py --task "Refactor this codebase" --mode "manual"
```

### Using a Custom Configuration File

To use a custom configuration:

```bash
python run.py --task "Create a database schema" --config-file "my_custom_config.yml"
```

Sources: [run.py:9-91]()

## 5. Quiet Mode and Logging

When running XAgent in quiet mode (`--quiet`), all console output is redirected to a log file instead of being displayed in the terminal. This is particularly useful for batch processing or when running XAgent as part of an automated pipeline.

The log file is created in the directory specified by the RunningRecorder's `record_root_dir`, with the filename "command_line.ansi". This file contains all the output that would normally be displayed in the terminal, including colored text (as ANSI escape sequences).

```python
# When quiet mode is enabled, output is redirected to a file
if quiet_mode:
    from XAgent.running_recorder import recorder
    record_file_path = os.path.join(recorder.record_root_dir, "command_line.ansi")
    with open(record_file_path, "w", encoding="utf-8") as file, redirect_stdout(file):
        start_command_line(args_dict)
else:
    start_command_line(args_dict)
```

Sources: [run.py:59-66](), [XAgent/running_recorder.py:50-61]()

## 6. Integration with RunningRecorder

The CLI is integrated with the RunningRecorder system, which captures all interactions and outputs during task execution. This includes:

- LLM input/output pairs
- Tool calls and responses
- Plan generations and refinements
- Task status updates

These records are stored in a structured directory hierarchy under the `record_root_dir`, which by default is set to "./running_records/" with a timestamp and UUID to ensure uniqueness.

The recording system creates the following directory structure:

```
running_records/
└── YYYY_MM_DD_HH_MM_SS_[UUID]/
    ├── LLM_inout_pair/           # Records of LLM interactions
    │   ├── 00000.json
    │   ├── 00001.json
    │   └── ...
    ├── tool_server_pair/         # Records of tool server interactions
    │   ├── 00000.json
    │   ├── 00001.json
    │   └── ...
    ├── [subtask_id]/             # Records for each subtask
    │   ├── plan_refine_00000.json
    │   ├── tool_00000.json
    │   └── ...
    ├── config.yml                # Configuration used for this run
    └── query.json                # The query/task that was executed
```

The recorded data can be used for:
- Debugging and troubleshooting
- Performance analysis
- Auditing of agent actions
- Reproducing results
- Regression testing

Sources: [XAgent/running_recorder.py:1-397]()

## 7. CommandLine and CommandLineParam Classes

The CLI functionality is primarily implemented through two classes:

1. `CommandLineParam` - A data class that holds the parameters for the command line execution:
   - `task`: The description of the task to perform
   - `upload_files`: List of files to upload for the task
   - `role`: The role XAgent should take (default: "Assistant")
   - `mode`: Execution mode (auto or manual)

2. `CommandLine` - The main class that manages the command line execution:
   - Initializes with a `CommandLineParam` object
   - Handles the actual execution through its `start()` method
   - Manages interaction with XAgent Core

```python
param = CommandLineParam(
    task=args_dict['task'],
    upload_files=args_dict.get('upload_files'),
    role="Assistant",
    mode=args_dict["mode"],
)
cmd = CommandLine(param)
cmd.start()
```

Sources: [run.py:76-83]()

## 8. Configuration Handling

The CLI uses a configuration system that combines:

1. Default settings from the configuration file (typically "assets/config.yml")
2. Command line arguments (which override the defaults)
3. Environment variables (CONFIG_FILE can point to a different config file)

This layered approach provides flexibility for different usage scenarios. The configuration handling works as follows:

1. The default config file path can be set via the `CONFIG_FILE` environment variable
2. This can be overridden by the `--config-file` command line argument
3. Individual settings can be overridden by specific command line arguments

When a configuration setting is not provided via command line, the system falls back to the value in the config file.

Sources: [run.py:35-58](), [run.py:87-91]()

## 9. Command Response Handling

When XAgent completes a task through the CLI, the response is processed using utilities like `get_command()` from the agent utilities module. This function parses the JSON response and extracts the command name and arguments:

```python
def get_command(response_json: Dict):
    """
    Parses the response and returns the command name and arguments.
    """
    # ... [implementation details]
    command_name = command["name"]
    arguments = command.get("args", {})
    return command_name, arguments
```

This pattern is used to extract structured information from the LLM responses, which can then be acted upon by the CLI.

Sources: [XAgent/agent/utils.py:4-49]()

---

# Page: OpenAI Integration

# OpenAI Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgent/ai_functions/request/openai.py](XAgent/ai_functions/request/openai.py)
- [XAgent/config.py](XAgent/config.py)
- [assets/config.yml](assets/config.yml)
- [assets/gpt-3.5-turbo_config.yml](assets/gpt-3.5-turbo_config.yml)
- [assets/gpt4_config.yml](assets/gpt4_config.yml)

</details>



This document details how XAgent integrates with OpenAI's APIs to facilitate language model-based interactions. It covers configuration of API keys, model selection, request handling, and fallback strategies when dealing with context length limitations.

## 1. Integration Overview

XAgent integrates with OpenAI's API through a robust request handling system that supports both older (pre-1.0) and newer versions of the OpenAI Python library. The integration provides:

- Support for multiple OpenAI models (GPT-3.5, GPT-4, etc.)
- API key rotation and management
- Automatic fallback to larger context models when needed
- Configurable retry logic for API call failures
- Support for both standard OpenAI and Azure OpenAI endpoints

```mermaid
flowchart TD
    subgraph "XAgent Components"
        XAgentCore["XAgent Core"]
        Config["XAgentConfig"]
        OpenAIRequest["OpenAI Request Handler"]
    end
    
    subgraph "OpenAI Services"
        OpenAIAPI["OpenAI API"]
        AzureOpenAI["Azure OpenAI Service"]
    end
    
    XAgentCore -->|"Uses"| OpenAIRequest
    OpenAIRequest -->|"Gets configuration from"| Config
    OpenAIRequest -->|"Sends requests to"| OpenAIAPI
    OpenAIRequest -->|"Alternative endpoint"| AzureOpenAI
    Config -->|"Stores"| APIKeys["API Keys & Model Settings"]
```

Sources: [XAgent/ai_functions/request/openai.py:1-214](), [XAgent/config.py:1-191]()

## 2. Configuration System

### 2.1 Model Configuration

XAgent uses YAML configuration files to define API keys, model preferences, and other settings. The configuration system supports multiple models with different parameter settings.

```mermaid
flowchart LR
    ConfigFile["Configuration File
    (YAML)"] -->|"Loaded by"| ConfigClass["XAgentConfig"]
    
    ConfigClass -->|"Provides"| ModelConfig["Model Configurations"]
    ConfigClass -->|"Provides"| APIConfig["API Configurations"]
    ConfigClass -->|"Provides"| DefaultSettings["Default Settings"]
    
    ModelConfig -->|"Used by"| RequestHandler["chatcompletion_request()"]
    APIConfig -->|"Used by"| RequestHandler
    DefaultSettings -->|"Used by"| RequestHandler
```

Sources: [XAgent/config.py:7-26](), [XAgent/config.py:124-126](), [assets/config.yml:1-59]()

### 2.2 API Key Configuration

API keys are configured in the YAML configuration files. The system supports multiple keys for each model type, enabling key rotation to distribute load and handle rate limits.

Example configuration structure:

```yaml
api_keys:
  gpt-3.5-turbo-16k:
    - api_key: sk-xxxxx
      organization: org-xxxxx
      model: gpt-3.5-turbo-16k
    - api_key: sk-xxxxx
      organization: org-xxxxxx
      model: gpt-3.5-turbo-16k
  gpt-4:    
    - api_key: sk-xxxxx
      organization: org-xxxxx
      model: gpt-4
```

For Azure OpenAI, the configuration includes additional Azure-specific parameters:

```yaml
api_keys:
  gpt-3.5-turbo-16k:
    - api_key: sk-xxxxx
      api_base: https://example.com
      api_type: azure
      api_version: 2023-07-01-preview
      engine: GPT-35-Turbo-16k
```

Sources: [assets/config.yml:1-26](), [assets/gpt4_config.yml:1-16](), [assets/gpt-3.5-turbo_config.yml:1-9]()

## 3. Request Handling Mechanism

XAgent employs a sophisticated request handling mechanism through the `chatcompletion_request` function, which manages interactions with OpenAI's API.

```mermaid
sequenceDiagram
    participant XAgent as "XAgent Component"
    participant ChatRequest as "chatcompletion_request()"
    participant Config as "XAgentConfig"
    participant OpenAI as "OpenAI API"
    
    XAgent->>ChatRequest: Call with model and parameters
    ChatRequest->>Config: Get normalized model name
    ChatRequest->>Config: Fetch API config for model
    Config->>Config: Rotate API keys
    
    ChatRequest->>OpenAI: Send API request
    
    alt Request successful
        OpenAI->>ChatRequest: Return response
        ChatRequest->>XAgent: Return processed response
    else Context length exceeded
        OpenAI->>ChatRequest: Return error
        ChatRequest->>Config: Get fallback model
        ChatRequest->>OpenAI: Retry with larger context model
        OpenAI->>ChatRequest: Return response
        ChatRequest->>XAgent: Return processed response
    else Other error
        OpenAI->>ChatRequest: Return error
        ChatRequest->>XAgent: Propagate error
    end
```

Sources: [XAgent/ai_functions/request/openai.py:26-94](), [XAgent/ai_functions/request/openai.py:106-211]()

### 3.1 Version Compatibility

The OpenAI request handler supports both older (pre-1.0) and newer versions of the OpenAI Python library. It includes version detection and appropriate error handling for each version.

For OpenAI version < 1.0:
- Uses `openai.ChatCompletion.create()`
- Handles `AuthenticationError`, `PermissionError`, `InvalidRequestError`

For OpenAI version >= 1.0:
- Uses `client.chat.completions.create()`
- Handles `AuthenticationError`, `PermissionDeniedError`, `BadRequestError`

Sources: [XAgent/ai_functions/request/openai.py:16-94](), [XAgent/ai_functions/request/openai.py:96-211]()

### 3.2 Retry Logic

The integration implements a robust retry mechanism using the `tenacity` library. It retries requests when encountering transient errors but raises exceptions for authentication or permission errors.

Key retry settings:
- Maximum retry attempts: Configured by `CONFIG.max_retry_times + 3`
- Retry wait strategy: Exponential backoff (61-293 seconds) after 3 immediate retries
- Non-retryable errors: Authentication, permission, and invalid request errors

Sources: [XAgent/ai_functions/request/openai.py:6-13](), [XAgent/ai_functions/request/openai.py:26-33](), [XAgent/ai_functions/request/openai.py:106-113]()

## 4. Context Length Management

XAgent automatically handles context length limitations by implementing a fallback strategy to models with larger context windows when needed.

```mermaid
flowchart TD
    Request["Request with
    model parameters"] -->|"Send to"| OpenAI["OpenAI API"]
    
    OpenAI -->|"Context length exceeded"| CheckFallback["Check for fallback models"]
    CheckFallback -->|"gpt-4"| TryGPT432k["Try gpt-4-32k"]
    CheckFallback -->|"gpt-4 (if gpt-4-32k unavailable)"| TryGPT41106["Try gpt-4-1106-preview"]
    CheckFallback -->|"gpt-3.5-turbo"| TryGPT351106["Try gpt-3.5-turbo-1106"]
    CheckFallback -->|"other models"| TryGPT3516k["Try gpt-3.5-turbo-16k"]
    
    TryGPT432k -->|"Retry with"| OpenAI
    TryGPT41106 -->|"Retry with"| OpenAI
    TryGPT351106 -->|"Retry with"| OpenAI
    TryGPT3516k -->|"Retry with"| OpenAI
    
    OpenAI -->|"Success"| Return["Return response"]
```

Fallback Path Examples:
- `gpt-4` → `gpt-4-32k` → `gpt-4-1106-preview` → `gpt-3.5-turbo-16k`
- `gpt-3.5-turbo` → `gpt-3.5-turbo-1106` → `gpt-3.5-turbo-16k`

Sources: [XAgent/ai_functions/request/openai.py:64-92](), [XAgent/ai_functions/request/openai.py:176-209]()

## 5. Model Name Normalization

To handle various ways a model might be referenced, XAgent normalizes model names through the `get_model_name` function.

| Input Model Name | Normalized Model Name |
|------------------|----------------------|
| `gpt4` | `gpt-4` |
| `gpt4-32` | `gpt-4-32k` |
| `gpt-35-16k` | `gpt-3.5-turbo-16k` |
| `gpt-4-turbo` | `gpt-4-1106-preview` |

This normalization ensures that model references are consistent throughout the system, regardless of how they are specified in user input.

Sources: [XAgent/config.py:128-170]()

## 6. API Configuration Retrieval

The `get_apiconfig_by_model` function handles retrieving the appropriate API configuration for a given model and implements API key rotation:

1. Normalizes the model name
2. Retrieves the first API configuration for the model from `CONFIG.api_keys`
3. Rotates the API keys by moving the used key to the end of the list
4. Returns the API configuration for use in requests

This rotation mechanism helps distribute load across multiple API keys and ensures continued operation if one key reaches its rate limit.

Sources: [XAgent/config.py:173-190]()

## 7. Azure OpenAI Integration

XAgent supports both standard OpenAI API and Azure OpenAI endpoints through different configuration paths:

```mermaid
flowchart TD
    Request["chatcompletion_request()"] -->|"Check configuration"| ConfigCheck{"Azure or Standard?"}
    
    ConfigCheck -->|"Azure OpenAI"| AzureSetup["Set up Azure client
    - api_key
    - azure_endpoint
    - api_version"]
    
    ConfigCheck -->|"Standard OpenAI"| StandardSetup["Set up OpenAI client
    - api_key
    - organization
    - base_url"]
    
    AzureSetup --> CreateClient["Create appropriate
    client instance"]
    StandardSetup --> CreateClient
    
    CreateClient --> SendRequest["Send API request"]
```

Key differences in Azure configuration:
- Requires `api_version` parameter
- Uses `engine` instead of `model` for model specification
- Uses `azure_endpoint` instead of `base_url`

Sources: [XAgent/ai_functions/request/openai.py:141-175](), [assets/config.yml:2-8]()

## 8. Configuration Options

The following table summarizes key configuration options for OpenAI integration:

| Configuration Option | Description | Example Value |
|----------------------|-------------|--------------|
| `default_request_type` | Default API provider type | `openai` |
| `default_completion_kwargs.model` | Default model to use | `gpt-4` |
| `default_completion_kwargs.temperature` | Temperature setting for generation | `0.2` |
| `default_completion_kwargs.request_timeout` | Timeout for API requests (seconds) | `60` |
| `max_retry_times` | Maximum number of retry attempts | `3` |

Sources: [assets/config.yml:28-33](), [assets/config.yml:42](), [assets/gpt4_config.yml:17-22](), [assets/gpt-3.5-turbo_config.yml:10-14]()

## 9. Error Handling

XAgent handles various error scenarios when interacting with OpenAI APIs:

1. Authentication errors - Immediately raised without retries
2. Permission errors - Immediately raised without retries
3. Invalid request errors - Immediately raised unless related to context length
4. Context length errors - Attempts fallback to larger context models
5. Transient errors - Retried with exponential backoff

Sources: [XAgent/ai_functions/request/openai.py:19-24](), [XAgent/ai_functions/request/openai.py:99-104](), [XAgent/ai_functions/request/openai.py:184-209]()

---

# Page: Task Recording

# Task Recording

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgent/agent/utils.py](XAgent/agent/utils.py)
- [XAgent/recorder.py](XAgent/recorder.py)
- [XAgent/running_recorder.py](XAgent/running_recorder.py)
- [XAgent/vector_db.py](XAgent/vector_db.py)
- [XAgent/workflow/plan_exec.py](XAgent/workflow/plan_exec.py)
- [XAgentServer/server.py](XAgentServer/server.py)
- [docker-compose.yml](docker-compose.yml)
- [run.py](run.py)

</details>



This documentation covers the task recording system within XAgent, which maintains a record of all interactions, operations, and decisions made during task execution. Task recording serves multiple purposes including debugging, result inspection, performance analysis, and caching to optimize repeated operations.

For information about the Web interface for viewing recorded tasks, see [XAgentWeb](#5).

## 1. Overview of Task Recording

The XAgent task recording system captures detailed information about task execution processes, including LLM queries, tool operations, plan refinements, and configuration details. This comprehensive recording enables post-execution analysis, debugging, and the optimization of future tasks through caching mechanisms.

```mermaid
flowchart TD
    subgraph "Task Execution Flow"
        Task("User Task Request") --> Dispatcher["Dispatcher"]
        Dispatcher --> Planner["Planner"]
        Planner --> Actor["Actor"]
        Actor --> Tools["Tools Execution"]
        Tools --> Reflection["Reflection"]
    end

    subgraph "Recording System"
        Recorder["RunningRecorder"]
        DB[(Database Storage)]
        Files[("File System Storage")]
    end

    Dispatcher -- "Records" --> Recorder
    Planner -- "Records" --> Recorder
    Actor -- "Records" --> Recorder
    Tools -- "Records" --> Recorder
    Reflection -- "Records" --> Recorder

    Recorder -- "Server Mode" --> DB
    Recorder -- "CLI Mode" --> Files
```

Sources: [XAgent/recorder.py:47-318](), [XAgent/running_recorder.py:34-396]()

## 2. Recording Components

XAgent employs two different implementations of the recording system depending on the execution mode:

1. **Server Mode Recorder** - Stores recordings in a MySQL database
2. **CLI Mode Recorder** - Stores recordings in the local file system

Both implementations provide similar functionality but differ in storage mechanisms and integration points.

### 2.1 Server Mode Recording

The server mode recorder (`RunningRecoder` class in `recorder.py`) integrates with XAgent's server architecture and stores all records in a MySQL database. This enables persistent storage and retrieval of execution details across different server instances.

```mermaid
classDiagram
    class RunningRecoder {
        +record_id: str
        +record_root_dir: str
        +newly_start: bool
        +logger: Logger
        +query: dict
        +config: dict
        +llm_interface_id: int
        +toolserver_interface_id: int
        +tool_call_id: int
        +plan_refine_id: int
        +llm_server_cache: list
        +tool_server_cache: list
        +tool_call_cache: list
        +plan_refine_cache: list
        +now_subtask_id: str
        +change_now_task()
        +generate_record()
        +regist_plan_modify()
        +regist_llm_inout()
        +query_llm_inout()
        +regist_tool_call()
        +regist_tool_server()
        +query_tool_server_cache()
        +regist_query()
        +get_query()
        +regist_config()
        +get_config()
        +load_from_db()
    }

    class XAgentRunningRecord {
        +record_id: str
        +current: str
        +node_id: str
        +node_type: RecorderTypeEnum
        +data: dict
        +create_time: datetime
        +update_time: datetime
        +is_deleted: bool
    }

    class RunningRecordCRUD {
        +insert_record()
        +get_record_by_type()
    }

    RunningRecoder --> XAgentRunningRecord: creates
    RunningRecoder --> RunningRecordCRUD: uses
```

Sources: [XAgent/recorder.py:47-318](), [XAgentServer/server.py:20-109]()

### 2.2 CLI Mode Recording

The CLI mode recorder (`RunningRecoder` class in `running_recorder.py`) operates independently and stores all records in the local file system. This approach is suitable for standalone executions and offline analysis.

```mermaid
flowchart TD
    CLI[Command Line Interface] --> |"1. Initialize recorder"| RunningRecoder
    RunningRecoder --> |"2. Create directory structure"| FileSystem[("File System")]
    RunningRecoder --> |"3. Record execution"| RecordTypes
    
    subgraph "RecordTypes"
        LLM["LLM Input/Output Pairs"]
        ToolServer["Tool Server API Calls"]
        ToolCall["Tool Executions"]
        PlanRefine["Plan Refinements"]
        Query["Query Data"]
        Config["Configuration"]
    end
    
    LLM --> |"Store in"| LLMDir["LLM_inout_pair directory"]
    ToolServer --> |"Store in"| ToolDir["tool_server_pair directory"]
    ToolCall --> |"Store in"| SubtaskDir["Subtask directories"]
    PlanRefine --> |"Store in"| SubtaskDir
    Query --> |"Store in"| RootDir["Root directory"]
    Config --> |"Store in"| RootDir
    
    LLMDir --> FileSystem
    ToolDir --> FileSystem
    SubtaskDir --> FileSystem
    RootDir --> FileSystem
```

Sources: [XAgent/running_recorder.py:34-396](), [run.py:41-91]()

## 3. Recorded Data Types

The task recording system captures several types of data during execution:

### 3.1 LLM Interactions

Records all inputs sent to and outputs received from the language model:

```mermaid
classDiagram
    class LLMRecord {
        +input: dict
        +output: dict
        +llm_interface_id: int
    }
    
    class Input {
        +messages: list
        +functions: list
        +function_call: dict
        +model: string
        +stop: any
        +other_args: dict
    }
    
    LLMRecord --> Input: contains
```

Sources: [XAgent/recorder.py:132-161](), [XAgent/running_recorder.py:130-159]()

### 3.2 Tool Interactions

Records all tool calls made during execution, including inputs, outputs, and status codes:

```mermaid
classDiagram
    class ToolCallRecord {
        +tool_name: string
        +tool_input: any
        +tool_output: any
        +tool_status_code: int
        +thought: any
    }
    
    class ToolServerRecord {
        +url: string
        +payload: any
        +response_status_code: int
        +tool_output: any
    }
```

Sources: [XAgent/recorder.py:191-243](), [XAgent/running_recorder.py:201-245]()

### 3.3 Plan Refinements

Records all modifications made to the execution plan:

```mermaid
classDiagram
    class PlanRefineRecord {
        +refine_function_name: string
        +refine_function_input: any
        +refine_function_output: any
        +plan_after: any
    }
```

Sources: [XAgent/recorder.py:108-130](), [XAgent/running_recorder.py:108-129](), [XAgent/workflow/plan_exec.py:49-107]()

### 3.4 Configurations and Queries

Records the initial configuration and query that started the task:

```mermaid
classDiagram
    class QueryRecord {
        +role_name: string
        +task: string
        +plan: list
    }
    
    class ConfigRecord {
        +model_configs: dict
        +tool_configs: dict
        +system_configs: dict
    }
```

Sources: [XAgent/recorder.py:271-317](), [XAgent/running_recorder.py:279-324]()

## 4. Using the Task Recording System

The task recording system is integrated into XAgent's core components and operates automatically during task execution. However, there are several ways to interact with and leverage the recording system:

### 4.1 Command Line Options

When using the command line interface, you can specify recording options:

| Option | Description |
|--------|-------------|
| `--record-dir` | Directory to store execution logs |
| `--quiet` | Run in quiet mode, outputting to a file instead of the terminal |

Sources: [run.py:9-38]()

### 4.2 Caching and Performance Optimization

The recording system includes caching mechanisms that can improve performance by avoiding redundant operations:

```mermaid
flowchart TD
    Request["API/Tool Request"] --> Cache{"Check Cache"}
    Cache -- "Cache Hit" --> Return["Return Cached Result"]
    Cache -- "Cache Miss" --> Execute["Execute Request"]
    Execute --> Store["Store Result in Cache"]
    Store --> Return
```

Sources: [XAgent/recorder.py:163-184](), [XAgent/recorder.py:245-269](), [XAgent/running_recorder.py:161-199](), [XAgent/running_recorder.py:247-276]()

### 4.3 Replaying Previous Executions

The recording system enables loading and replaying previous task executions:

```mermaid
flowchart TD
    Start["Start XAgent"] --> Mode{"Mode?"}
    Mode -- "New Task" --> Initialize["Initialize New Recorder"]
    Mode -- "Replay Task" --> Load["Load From DB/Disk"]
    Load --> Cache["Populate Caches"]
    Initialize --> Execute["Execute Task"]
    Cache --> Execute
```

Sources: [XAgent/recorder.py:319-346](), [XAgent/running_recorder.py:338-395]()

## 5. Database Schema (Server Mode)

When using the server mode, task recordings are stored in the MySQL database according to the following schema:

```mermaid
erDiagram
    XAgentRunningRecord {
        string record_id
        string current
        int node_id
        enum node_type
        json data
        datetime create_time
        datetime update_time
        boolean is_deleted
    }
    
    RecorderTypeEnum {
        QUERY
        CONFIG
        LLM_INPUT_PAIR
        TOOL_SERVER_PAIR
        TOOL_CALL
        PLAN_REFINE
    }
    
    XAgentRunningRecord ||--|| RecorderTypeEnum : "has type"
```

Sources: [docker-compose.yml:66-94](), [XAgent/recorder.py:96-105]()

## 6. File System Structure (CLI Mode)

When using the CLI mode, task recordings are organized in the file system as follows:

```
running_records/
└── TIMESTAMP_UUID/
    ├── config.yml              # Task configuration
    ├── query.json              # Initial task query
    ├── LLM_inout_pair/         # LLM interactions
    │   ├── 00000.json
    │   ├── 00001.json
    │   └── ...
    ├── tool_server_pair/       # Tool server API calls
    │   ├── 00000.json
    │   ├── 00001.json
    │   └── ...
    └── SUBTASK_ID/             # Subtask-specific recordings
        ├── tool_00000.json     # Tool calls
        ├── tool_00001.json
        ├── plan_refine_00000.json  # Plan refinements
        └── ...
```

Sources: [XAgent/running_recorder.py:50-76](), [XAgent/running_recorder.py:108-245]()

## 7. Integration with XAgent Core

The task recording system integrates with XAgent Core through a global recorder instance, which is accessed by various components during execution:

```mermaid
flowchart TD
    Core["XAgentCoreComponents"] --> Recorder["global_recorder"]
    Planner["PlanAgent"] --> Recorder
    Actor["TaskHandler"] --> Recorder
    ToolServer["ToolServerInterface"] --> Recorder
    LLMInterface["LLMInterface"] --> Recorder
    
    Recorder --> DB[("Database (Server Mode)")]
    Recorder --> Files[("Files (CLI Mode)")]
```

Sources: [XAgent/workflow/plan_exec.py:69-74](), [XAgentServer/server.py:26-109]()

## 8. Technical Implementation Details

### 8.1 Data Serialization

The recording system uses a utility function `dump_common_things()` to serialize various data types before storage:

| Data Type | Serialization Method |
|-----------|----------------------|
| Primitive types (str, int, float, bool) | Direct storage |
| Dictionaries | Recursive serialization of keys and values |
| Lists | Recursive serialization of elements |
| Custom objects | Call `to_json()` method if available |

Sources: [XAgent/recorder.py:19-29](), [XAgent/running_recorder.py:14-32]()

### 8.2 Record Type Enumeration

Records are categorized using the `RecorderTypeEnum` enumeration:

| Record Type | Description |
|-------------|-------------|
| QUERY | Initial task query data |
| CONFIG | Task configuration data |
| LLM_INPUT_PAIR | LLM input/output pairs |
| TOOL_SERVER_PAIR | Tool server API calls |
| TOOL_CALL | Tool executions |
| PLAN_REFINE | Plan refinements |

Sources: [XAgent/recorder.py:96-105](), [XAgentServer/enums/recorder_type.py]() (inferred)

## 9. Best Practices and Considerations

When working with the task recording system, consider the following:

1. **Storage Requirements**: Extensive recordings can consume significant disk space or database resources, especially for complex tasks.

2. **Performance Impact**: While the recording system is designed to be lightweight, it may have a small impact on performance during execution.

3. **Security Considerations**: Recordings may contain sensitive information (e.g., API keys, user data). The system automatically masks API keys, but be cautious with other sensitive data.

4. **Replay Limitations**: Not all aspects of a task execution can be perfectly replayed, especially those involving external systems or time-dependent operations.

5. **Debugging**: Task recordings are valuable debugging tools, providing insight into the decision-making process and execution flow.

Sources: [XAgent/recorder.py:87-88](), [XAgent/recorder.py:163-184]()

---

# Page: ToolServer

# ToolServer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [ToolServer/README.md](ToolServer/README.md)
- [ToolServer/README_ZH.md](ToolServer/README_ZH.md)
- [ToolServer/ToolServerNode/core/envs/web.py](ToolServer/ToolServerNode/core/envs/web.py)
- [XAgentGen/README.md](XAgentGen/README.md)

</details>



ToolServer is a component within the XAgent system that provides a safe, isolated environment for executing tools and operations. It serves as a crucial bridge between the agent's planning capabilities and real-world actions, offering a containerized environment where tools can be executed without risking the host system's security. For information about the XAgent Core that uses the ToolServer, see [XAgent Core](#2).

## Introduction

ToolServer is designed as a Docker-based system that hosts various tools like file editing, Python notebooks, web browsing, shell execution, and API calling. It provides a robust API that the XAgent system uses to discover and execute tools in a controlled environment. The system isolates tool execution in containers to ensure security while providing powerful capabilities.

### ToolServer Architecture Overview

```mermaid
graph TD
    subgraph "XAgent System"
        XA["XAgent Core"]
    end
    
    subgraph "ToolServer System"
        TSM["ToolServerManager"]
        TSMonitor["ToolServerMonitor"]
        TSN1["ToolServerNode 1"]
        TSN2["ToolServerNode 2"]
        TSN3["ToolServerNode N"]
    end
    
    XA -->|"API calls"| TSM
    TSM -->|"creates/manages"| TSN1
    TSM -->|"creates/manages"| TSN2
    TSM -->|"creates/manages"| TSN3
    TSMonitor -->|"monitors"| TSN1
    TSMonitor -->|"monitors"| TSN2
    TSMonitor -->|"monitors"| TSN3
    
    subgraph "Tools in Node"
        TSN1 --> FileEditor["FileEnv (File Editor)"]
        TSN1 --> PythonNotebook["PythonEnv (Notebook)"]
        TSN1 --> WebBrowser["WebEnv (Browser)"]
        TSN1 --> Shell["ShellEnv (Shell)"]
        TSN1 --> RapidAPI["RapidAPIEnv"]
    end
```

Sources: [README.md:61-70](), [ToolServer/README.md:1-16]()

## System Components

ToolServer consists of three primary components that work together to provide tool execution capabilities:

### ToolServerManager

The ToolServerManager serves as the entry point for API requests from the XAgent Core. It's responsible for:
- Creating new ToolServerNode instances (Docker containers)
- Managing the lifecycle of these containers
- Routing tool execution requests to the appropriate node
- Providing an API for node interaction

### ToolServerMonitor

The ToolServerMonitor maintains system health by:
- Periodically checking the status of all ToolServerNode instances
- Detecting and removing non-responsive or malfunctioning nodes
- Cleaning up idle nodes after a configurable period of inactivity (default: 30 minutes)

### ToolServerNode

Each ToolServerNode is a Docker container that:
- Hosts the actual tool implementations
- Provides a safe execution environment for tools
- Isolates tool operations from the host system
- Exposes tools through a standardized interface

Sources: [ToolServer/README.md:4-9]()

### Component Interactions Sequence

```mermaid
sequenceDiagram
    participant XA as "XAgent Core"
    participant TSM as "ToolServerManager"
    participant TSM as "ToolServerMonitor"
    participant TSN as "ToolServerNode"
    
    XA->>TSM: GET /get_cookies
    TSM->>TSN: Create new node if needed
    TSM->>XA: Return cookie with node_id
    
    XA->>TSM: GET /get_available_tools
    TSM->>TSN: Forward request
    TSN->>TSM: Return registered tools
    TSM->>XA: List of tools and schemas
    
    XA->>TSM: POST /execute_tool (tool_name, arguments)
    TSM->>TSN: Forward execution request
    TSN->>TSM: Tool execution result
    TSM->>XA: Return result to agent
    
    XA->>TSM: POST /close_session
    TSM->>TSN: Stop the container
    TSM->>XA: Confirmation
```

Sources: [ToolServer/README.md:38-184]()

## Tool System

The ToolServer provides several built-in tools, each implementing different capabilities for the agent:

### Tool Registration System

```mermaid
classDiagram
    class BaseEnv {
        +__init__(config)
        +register_tool(func)
    }
    
    class WebEnv {
        +search_and_browse(query, goals)
        +browse_website(url, goals)
    }
    
    class FileEnv {
        +read_file(file_path)
        +write_file(file_path, content)
        +list_files(dir_path)
    }
    
    class PythonEnv {
        +execute_python(code)
        +create_visualization(data, type)
    }
    
    class ShellEnv {
        +execute_shell(command)
        +read_stdout()
    }
    
    class RapidAPIEnv {
        +search_apis(query)
        +call_api(api_name, params)
    }
    
    BaseEnv <|-- WebEnv
    BaseEnv <|-- FileEnv
    BaseEnv <|-- PythonEnv
    BaseEnv <|-- ShellEnv
    BaseEnv <|-- RapidAPIEnv
    
    class toolwrapper {
        <<decorator>>
        +registers tools with manager
    }
    
    toolwrapper --> BaseEnv : "registers"
```

Tools in ToolServer are implemented as environment classes that extend the `BaseEnv` class. Each environment provides methods that are registered as tools using the `toolwrapper` decorator.

Sources: [ToolServer/ToolServerNode/core/envs/web.py:1-126]()

### Available Tools

ToolServer provides five main tools:

1. **File Editor (FileEnv)**
   - Read, write, and modify files
   - List directory contents
   - Create and delete files and directories

2. **Python Notebook (PythonEnv)**
   - Execute Python code in a notebook environment
   - Create visualizations and charts
   - Perform data analysis and validation

3. **Web Browser (WebEnv)**
   - Search the internet using Bing API or DuckDuckGo (fallback)
   - Browse websites and extract content
   - Navigate links within web pages

4. **Shell (ShellEnv)**
   - Execute shell commands
   - Install software packages
   - Run and manage services

5. **Rapid API (RapidAPIEnv)**
   - Search for APIs from Rapid API
   - Call external APIs with parameters
   - Process API responses

Sources: [README.md:61-70](), [ToolServer/README.md:10-16]()

#### Example: WebEnv Implementation

The WebEnv class provides two primary methods:
- `search_and_browse`: Searches the web and browses the results
- `browse_website`: Extracts the content from a specific URL

The tool implements safety checks to prevent accessing local URLs and uses either the Bing API (if configured) or DuckDuckGo as a fallback for search functionality.

Sources: [ToolServer/ToolServerNode/core/envs/web.py:11-126]()

## API Documentation

ToolServer exposes a RESTful API for XAgent to interact with the tools:

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/get_cookies` | GET | Returns a cookie with the node_id |
| `/get_available_tools` | GET | Lists all registered tools and schemas |
| `/retrieving_tools` | POST | Returns relevant tools for a question |
| `/get_json_schema_for_tools` | POST | Returns JSON schema for specific tools |
| `/get_json_schema_for_envs` | POST | Returns JSON schema for environments |
| `/execute_tool` | POST | Executes a specified tool with parameters |
| `/close_session` | POST | Stops the ToolServerNode container |
| `/release_session` | POST | Deletes the ToolServerNode container |

### Tool Execution Flow

```mermaid
flowchart TD
    A["XAgent Core"] -->|"1. /get_cookies"| B["ToolServerManager"]
    B -->|"2. Create container"| C["ToolServerNode"]
    A -->|"3. /get_available_tools"| B
    B -->|"4. Get tools list"| C
    A -->|"5. /execute_tool"| B
    B -->|"6. Execute tool"| C
    C -->|"7. Run tool method"| D["Tool Implementation"]
    D -->|"8. Return result"| C
    C -->|"9. Return result"| B
    B -->|"10. Return result"| A
    A -->|"11. /close_session"| B
    B -->|"12. Stop container"| C
```

Some tools, especially interactive ones like Shell, may return HTTP status code 450, indicating that further calls are required to complete the execution.

Sources: [ToolServer/README.md:38-184]()

## Configuration

ToolServer can be configured through several YAML files:

### Configuration Files

| File | Description |
|------|-------------|
| `assets/config/manager.yml` | ToolServerManager configuration |
| `assets/config/monitor.yml` | ToolServerMonitor configuration |
| `assets/config/node.yml` | ToolServerNode configuration |

### Key Configuration Options

- **Manager Configuration**
  - `node.privileged`: Whether nodes have privileged Docker access
  - Docker image settings and network configuration

- **Monitor Configuration**
  - `idling_close_minutes`: Time to wait before closing idle nodes (default: 30)

- **Node Configuration**
  - API keys for services (Bing, Rapid API)
  - Tool-specific settings

Sources: [ToolServer/README.md:18-25]()

## Building and Running ToolServer

ToolServer uses Docker Compose for easy deployment:

### Starting with Pre-built Images

```bash
docker compose up
```

### Building from Source

```bash
docker compose build
docker compose up
```

To run in the background, add the `-d` flag:

```bash
docker compose up -d
```

If the ToolServer needs to be updated, rebuild the images with:

```bash
docker compose pull
# or
docker compose build
```

Sources: [README.md:76-106](), [ToolServer/README.md:26-37]()

## Integration with XAgent

The ToolServer is a critical component in the XAgent system, providing the agent's tool execution capabilities:

```mermaid
graph TD
    subgraph "XAgent System"
        User["User"] -->|"tasks"| XA["XAgent Core"]
        XA -->|"plans tasks"| Planner["Planner"]
        XA -->|"executes actions"| Actor["Actor"]
        Actor -->|"calls tools"| ToolAgent["Tool Agent"]
    end
    
    subgraph "ToolServer System"
        ToolAgent -->|"API calls"| TSM["ToolServerManager"]
        TSM -->|"manages"| TSNode["ToolServerNode"]
        TSMonitor["ToolServerMonitor"] -->|"monitors"| TSNode
        TSNode -->|"hosts"| Tools["File Editor<br>Python Notebook<br>Web Browser<br>Shell<br>Rapid API"]
    end
    
    subgraph "External Integrations"
        Tools -->|"search"| Web["Internet"]
        Tools -->|"API calls"| APIs["External APIs"]
        Tools -->|"file operations"| FS["File System"]
    end
```

When XAgent needs to execute a tool, the Tool Agent sends a request to the ToolServerManager, which routes the request to the appropriate ToolServerNode. The node executes the requested tool and returns the result, which is then processed by the XAgent Core to continue task execution.

Sources: [README.md:50-59]()

## Security Considerations

ToolServer enhances security through containerization:

1. **Isolation**: Tools run in isolated Docker containers, preventing them from affecting the host system
2. **URL Validation**: The WebEnv implements checks to prevent accessing local URLs
3. **Privileged Mode Control**: Can disable privileged mode to prevent Docker-in-Docker operations
4. **Session Management**: Nodes can be closed or released when no longer needed

Sources: [ToolServer/ToolServerNode/core/envs/web.py:27-46](), [ToolServer/README.md:18-25]()

## Conclusion

ToolServer provides a secure and extensible platform for tool execution within the XAgent system. By containerizing tools and providing a standardized API, it enables the autonomous agent to perform a wide range of tasks while maintaining system security. The modular design makes it easy to add new tools and capabilities, allowing the system to grow and adapt to new requirements.

---

# Page: ToolServer Architecture

# ToolServer Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ToolServer/README.md](ToolServer/README.md)
- [ToolServer/README_ZH.md](ToolServer/README_ZH.md)
- [ToolServer/ToolServerManager/main.py](ToolServer/ToolServerManager/main.py)
- [ToolServer/ToolServerManager/node_checker.py](ToolServer/ToolServerManager/node_checker.py)
- [ToolServer/ToolServerNode/core/envs/web.py](ToolServer/ToolServerNode/core/envs/web.py)

</details>



This document describes the architecture of ToolServer, a critical component in the XAgent system that provides a safe and controlled environment for executing various tools required by the agent. For information about the specific tools provided by ToolServer, see [Tool Types and Capabilities](#3.2). For details on managing ToolServer instances, see [ToolServer Management](#3.3).

## Overview

ToolServer enables XAgent to execute external operations safely by providing containerized environments for tool execution. The architecture uses Docker containers to isolate tool execution, preventing potential security risks while allowing XAgent to access powerful capabilities like web browsing, file editing, and executing shell commands.

```mermaid
graph TD
    subgraph "ToolServer System"
        TSM["ToolServerManager"]
        TSMonitor["ToolServerMonitor"]
        TSNodes["ToolServerNodes<br>(Docker Containers)"]
    end
    
    XA["XAgent Core"] -->|"API calls"| TSM
    TSM -->|"creates/manages"| TSNodes
    TSMonitor -->|"monitors status"| TSNodes
    TSNodes -->|"provides"| Tools["Available Tools"]
    
    subgraph "Tools"
        FileEditor["File Editor"]
        PythonNotebook["Python Notebook"]
        WebBrowser["Web Browser"]
        Shell["Shell"]
        RapidAPI["Rapid API"]
    end
    
    Tools --- FileEditor
    Tools --- PythonNotebook
    Tools --- WebBrowser
    Tools --- Shell
    Tools --- RapidAPI
```

Sources: [ToolServer/README.md:2-9]()

## Components

The ToolServer system consists of three primary components that work together to provide tool execution capabilities to XAgent.

### ToolServerManager

ToolServerManager is responsible for creating and managing ToolServerNode instances. Implemented as a FastAPI application, it handles requests from XAgent Core, creates Docker containers for tool execution, and routes requests to the appropriate node.

```mermaid
sequenceDiagram
    participant XA as "XAgent Core"
    participant TSM as "ToolServerManager"
    participant DC as "Docker Client"
    participant TSN as "ToolServerNode"
    
    XA->>TSM: POST /get_cookie
    TSM->>DC: containers.run()
    DC-->>TSM: container_id
    TSM->>TSM: Create ToolServerNode in DB
    TSM->>TSM: wait_for_node_startup()
    TSM-->>XA: Response with node_id cookie
    
    XA->>TSM: Tool execution request
    TSM->>TSM: route_to_node()
    TSM->>TSN: Forward request
    TSN-->>TSM: Tool execution result
    TSM-->>XA: Return result
    
    XA->>TSM: POST /close_session
    TSM->>DC: container.stop()
    
    XA->>TSM: POST /release_session
    TSM->>DC: container.kill() and remove()
```

Key functionality provided by ToolServerManager:

1. **Node Creation**: Creates new ToolServerNode Docker containers when a session is initiated
2. **Request Routing**: Routes tool execution requests to the appropriate node
3. **Session Management**: Handles reconnecting, closing, and releasing of sessions

Sources: [ToolServer/ToolServerManager/main.py:16-229]()

### ToolServerMonitor

ToolServerMonitor is responsible for monitoring the status of ToolServerNode instances. It periodically checks each node's status, updates the database with the current state, and manages idle nodes.

```mermaid
flowchart TD
    Start["Start Monitor Loop"] --> CheckDB["Query all nodes from DB"]
    CheckDB --> LoopNodes["For each node"]
    LoopNodes --> QueryDocker["Query node status from Docker"]
    
    QueryDocker --> NodeExists{"Node exists?"}
    NodeExists -->|"No"| DeleteFromDB["Delete node from DB"]
    NodeExists -->|"Yes"| UpdateStatus["Update node status in DB"]
    
    UpdateStatus --> CheckHealth{"Health check<br>enabled?"}
    CheckHealth -->|"Yes"| UpdateHealth["Update node health"]
    CheckHealth -->|"No"| SkipHealth["Skip health update"]
    
    UpdateHealth --> CheckIdle{"Node idle > threshold?"}
    SkipHealth --> CheckIdle
    CheckIdle -->|"Yes"| StopNode["Stop idle node"]
    CheckIdle -->|"No"| NextNode["Process next node"]
    
    StopNode --> NextNode
    DeleteFromDB --> NextNode
    NextNode --> Sleep["Sleep for interval"]
    Sleep --> CheckDB
```

The monitor continually runs this check cycle, ensuring that:

1. Nodes that no longer exist in Docker are removed from the database
2. Node status (running, stopped, etc.) is kept up-to-date in the database
3. Node health status is updated if health checking is enabled
4. Idle nodes are automatically stopped after a configurable timeout period

Sources: [ToolServer/ToolServerManager/node_checker.py:11-69]()

### ToolServerNode

ToolServerNode instances are Docker containers that provide the actual tool execution environment. Each node hosts a variety of tools that XAgent can use to accomplish tasks.

```mermaid
graph TB
    subgraph "ToolServerNode"
        API["FastAPI Application"]
        ToolRegistry["Tool Registry"]
        
        subgraph "Tool Environments"
            FileEnv["File Environment"]
            WebEnv["Web Environment"]
            ShellEnv["Shell Environment"]
            PythonEnv["Python Environment"]
            RapidAPIEnv["RapidAPI Environment"]
        end
    end
    
    API -->|"register_tool()"| ToolRegistry
    API -->|"execute_tool()"| ToolRegistry
    ToolRegistry -->|"dispatch"| FileEnv
    ToolRegistry -->|"dispatch"| WebEnv
    ToolRegistry -->|"dispatch"| ShellEnv
    ToolRegistry -->|"dispatch"| PythonEnv
    ToolRegistry -->|"dispatch"| RapidAPIEnv
    
    FileEnv -->|"provides"| FileOps["File Operations"]
    WebEnv -->|"provides"| WebOps["Web Operations"]
    ShellEnv -->|"provides"| ShellOps["Shell Operations"]
    PythonEnv -->|"provides"| PythonOps["Python Operations"]
    RapidAPIEnv -->|"provides"| APIAccess["API Access"]
```

Each ToolServerNode provides endpoints for:

1. Listing available tools
2. Retrieving tool schemas
3. Executing tools with parameters
4. Getting environment information

Sources: [ToolServer/README.md:9-16](), [ToolServer/ToolServerNode/core/envs/web.py:11-126]()

## Communication Flow

The communication between XAgent Core and the tools happens through a multi-stage process involving the ToolServerManager and ToolServerNodes.

```mermaid
sequenceDiagram
    participant XA as "XAgent Core"
    participant TSM as "ToolServerManager"
    participant TSN as "ToolServerNode"
    participant Tool as "Tool Implementation"
    
    Note over XA,Tool: Session Initialization
    XA->>TSM: POST /get_cookie
    TSM->>TSM: Create Docker container
    TSM-->>XA: Return node_id cookie
    
    Note over XA,Tool: Tool Discovery
    XA->>TSM: GET /get_available_tools
    TSM->>TSN: Forward request
    TSN->>TSN: List registered tools
    TSN-->>TSM: Return tool list and schemas
    TSM-->>XA: Return available tools
    
    Note over XA,Tool: Tool Execution
    XA->>TSM: POST /execute_tool
    activate TSM
    TSM->>TSN: Forward request
    activate TSN
    TSN->>Tool: Execute tool with parameters
    activate Tool
    Tool-->>TSN: Return execution result
    deactivate Tool
    TSN-->>TSM: Return tool result
    deactivate TSN
    TSM-->>XA: Return execution result
    deactivate TSM
    
    Note over XA,Tool: Session Termination
    XA->>TSM: POST /close_session
    TSM->>TSM: Stop Docker container
    TSM-->>XA: Confirm session closed
    
    XA->>TSM: POST /release_session
    TSM->>TSM: Kill and remove Docker container
    TSM-->>XA: Confirm session released
```

Sources: [ToolServer/ToolServerManager/main.py:107-226](), [ToolServer/README.md:38-186]()

## Database and State Management

ToolServer uses a database (MongoDB via Beanie ODM) to track the state of all node instances and provide persistence across restarts.

```mermaid
classDiagram
    class ToolServerNode {
        +String id
        +String short_id
        +String status
        +String ip
        +int port
        +DateTime last_req_time
        +String health
    }
    
    class NodeChecker {
        +String manager_id
        +float interval
        +int pid
    }
    
    class Database {
        +connect()
        +close()
        +query()
        +update()
    }
    
    ToolServerManager --> Database : uses
    Database --> ToolServerNode : stores
    Database --> NodeChecker : stores
```

Key database entities:

1. **ToolServerNode**: Represents a Docker container providing tool execution capabilities
   - Tracks container ID, status, IP address, port, and health status
   - Records last request time for idle detection
   
2. **NodeChecker**: Tracks monitoring process information
   - Stores manager ID, checking interval, and process ID

Sources: [ToolServer/ToolServerManager/main.py:26-28](), [ToolServer/ToolServerManager/main.py:134-142]()

## Docker Integration

ToolServer uses Docker extensively to provide isolated environments for tool execution.

```mermaid
graph TD
    subgraph "Host System"
        TSM["ToolServerManager"]
        Docker["Docker Engine"]
        DockerNetwork["Docker Network"]
    end
    
    subgraph "Docker Containers"
        TSN1["ToolServerNode 1"]
        TSN2["ToolServerNode 2"]
        TSN3["ToolServerNode 3"]
    end
    
    TSM -->|"containers.run()"| Docker
    Docker -->|"creates"| TSN1
    Docker -->|"creates"| TSN2
    Docker -->|"creates"| TSN3
    
    DockerNetwork -->|"connects"| TSM
    DockerNetwork -->|"connects"| TSN1
    DockerNetwork -->|"connects"| TSN2
    DockerNetwork -->|"connects"| TSN3
    
    TSM -->|"HTTP requests<br>via internal network"| TSN1
    TSM -->|"HTTP requests<br>via internal network"| TSN2
    TSM -->|"HTTP requests<br>via internal network"| TSN3
```

The Docker integration provides several benefits:

1. **Isolation**: Each tool execution environment is isolated, preventing cross-contamination
2. **Resource Control**: Docker allows limiting CPU, memory, and other resources
3. **Security**: Container isolation prevents security risks from affecting the host system
4. **Statelessness**: Containers can be destroyed and recreated easily, ensuring clean environments

Sources: [ToolServer/ToolServerManager/main.py:127-130](), [ToolServer/README.md:3]()

## API Endpoints

The ToolServerManager provides several key API endpoints for managing ToolServerNode instances and executing tools.

| Endpoint | Method | Purpose | Description |
|----------|--------|---------|-------------|
| `/get_cookie` | POST | Create node | Creates a new ToolServerNode and returns its ID as a cookie |
| `/reconnect_session` | POST | Restart node | Restarts an existing ToolServerNode |
| `/close_session` | POST | Stop node | Stops a ToolServerNode but keeps its state |
| `/release_session` | POST | Delete node | Terminates and removes a ToolServerNode |
| `/alive` | GET | Health check | Simple endpoint to verify service is running |
| Tool paths | GET/POST | Tool execution | Routes tool execution requests to the appropriate node |

The ToolServerNode instances typically provide these endpoints:

| Endpoint | Method | Purpose | Description |
|----------|--------|---------|-------------|
| `/get_available_tools` | GET | Tool discovery | Lists all available tools and their schemas |
| `/retrieving_tools` | POST | Tool search | Finds tools relevant to a specific question |
| `/get_json_schema_for_tools` | POST | Schema retrieval | Gets detailed schemas for specific tools |
| `/get_json_schema_for_envs` | POST | Environment info | Gets information about tool environments |
| `/execute_tool` | POST | Tool execution | Executes a tool with specified parameters |

Sources: [ToolServer/README.md:39-154](), [ToolServer/ToolServerManager/main.py:65-269]()

## Monitoring and Lifecycle Management

ToolServer includes built-in monitoring capabilities to ensure nodes are functioning correctly and to manage their lifecycle.

```mermaid
stateDiagram-v2
    [*] --> Created: containers.run()
    Created --> Running: Status check
    Running --> Healthy: Health check passed
    Running --> Unhealthy: Health check failed
    Healthy --> Idle: No requests for period
    Idle --> Stopped: Idle timeout reached
    Unhealthy --> Removed: Monitor cleanup
    Stopped --> [*]: container.remove()
    
    Running --> Stopped: close_session()
    Healthy --> Stopped: close_session()
    Idle --> Stopped: close_session()
    
    Running --> Removed: release_session()
    Healthy --> Removed: release_session()
    Idle --> Removed: release_session()
    Stopped --> Removed: release_session()
    
    Removed --> [*]: Final state
```

Key lifecycle events:

1. **Creation**: Node is created via Docker container
2. **Health Checking**: Node's health is periodically verified
3. **Idle Detection**: Nodes with no activity are marked as idle
4. **Automatic Stopping**: Idle nodes are automatically stopped after a timeout
5. **Explicit Management**: Nodes can be restarted, stopped, or removed via API calls

Sources: [ToolServer/ToolServerManager/node_checker.py:11-55](), [ToolServer/ToolServerManager/main.py:182-226]()

## Integration with XAgent Core

The ToolServer is integrated with XAgent Core through an API-based approach, where XAgent Core makes HTTP requests to the ToolServerManager to access tools.

```mermaid
graph LR
    subgraph "XAgent Core"
        Dispatcher["Dispatcher"]
        ToolAgent["Tool Agent"]
    end
    
    subgraph "ToolServer"
        TSM["ToolServerManager"]
        TSN["ToolServerNode"]
    end
    
    ToolAgent -->|"API calls"| TSM
    TSM -->|"route_to_node()"| TSN
    TSN -->|"execute tool"| Tools["Tool Implementation"]
    Tools -->|"return result"| TSN
    TSN -->|"return result"| TSM
    TSM -->|"return result"| ToolAgent
```

The integration flow typically follows these steps:

1. XAgent Core initializes a session by requesting a cookie with a node ID
2. XAgent discovers available tools by querying the ToolServer
3. When a tool needs to be executed, XAgent makes a request to the ToolServer with the tool name and parameters
4. ToolServer routes the request to the appropriate node, executes the tool, and returns the result
5. When the task is complete, XAgent releases the session

Sources: [ToolServer/README.md:3-9]()

## Security Considerations

ToolServer is designed with security in mind, providing several layers of protection:

1. **Container Isolation**: Each ToolServerNode runs in its own Docker container, isolating it from the host system and other nodes
2. **URL Validation**: The Web Environment validates URLs to prevent accessing local resources
3. **Resource Limitations**: Docker containers can be configured with resource limits to prevent denial-of-service attacks
4. **Automatic Cleanup**: Idle nodes are automatically stopped and removed to prevent resource exhaustion
5. **Session Management**: Each client gets its own isolated environment, preventing cross-session interference

Sources: [ToolServer/ToolServerNode/core/envs/web.py:27-46](), [ToolServer/ToolServerManager/main.py:127-130]()

## Configuration Options

ToolServer provides several configuration options to customize its behavior:

| Configuration | Purpose | Description |
|--------------|---------|-------------|
| `node.health_check` | Enable/disable health checking | Determines whether to perform health checks on nodes |
| `node.health_check_interval` | Health check frequency | Time between health checks in seconds |
| `node.creation_wait_seconds` | Node startup timeout | Maximum time to wait for a node to start |
| `node.idling_close_minutes` | Idle timeout | Time after which idle nodes are stopped |
| `node.privileged` | Container privileges | Whether containers have elevated privileges |
| `node.device_requests` | Hardware access | Configures access to special hardware (e.g., GPUs) |
| `builtin_monitor` | Enable/disable monitoring | Controls whether the built-in monitor is active |
| `redirect_to_node_path` | API routing | Configures which paths should be routed to nodes |

Sources: [ToolServer/README.md:18-24](), [ToolServer/ToolServerManager/main.py:31-45]()

---

# Page: Tool Types and Capabilities

# Tool Types and Capabilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ToolServer/README.md](ToolServer/README.md)
- [ToolServer/README_ZH.md](ToolServer/README_ZH.md)
- [ToolServer/ToolServerNode/core/envs/pycoding.py](ToolServer/ToolServerNode/core/envs/pycoding.py)
- [ToolServer/ToolServerNode/core/envs/web.py](ToolServer/ToolServerNode/core/envs/web.py)
- [XAgent/agent/summarize.py](XAgent/agent/summarize.py)
- [XAgent/ai_functions/pure_functions/task_manage_functions.yml](XAgent/ai_functions/pure_functions/task_manage_functions.yml)

</details>



This document describes the different types of tools available in the ToolServer component of XAgent and their capabilities. The ToolServer provides a safe, isolated environment for executing tools that extend XAgent's abilities to interact with the external world. For details on the overall ToolServer architecture, see [ToolServer Architecture](#3.1), and for information about managing ToolServer instances, refer to [ToolServer Management](#3.3).

## Tool Overview

ToolServer currently provides five primary tool types, each designed to handle specific interaction patterns:

| Tool Type | Description | Primary Capabilities |
|-----------|-------------|---------------------|
| File Editor | Text editing tool | Write, read, and modify files |
| Python Notebook | Interactive Python environment | Run code, validate ideas, create visualizations |
| Web Browser | Web interaction interface | Search online, visit webpages, extract information |
| Shell | Command-line interface | Execute shell commands, install programs, host services |
| Rapid API | API interaction tool | Retrieve and call APIs from Rapid API hub |

Sources: [ToolServer/README.md:10-15]()

## Tool Architecture

The tools in ToolServer follow a consistent architecture pattern, with each tool implemented as an environment class that extends the `BaseEnv` class and is registered with the `toolwrapper` decorator.

```mermaid
classDiagram
    direction TB
    
    class "BaseEnv" {
        +__init__(config)
    }
    
    class "PythonNotebook" {
        +execute_cell(code, cell_index, reset)
        +print_notebook()
    }
    
    class "WebEnv" {
        +search_and_browse(search_query, goals_to_browse, region, num_results)
        +browse_website(url, goals_to_browse)
    }
    
    class "FileEditorEnv" {
        +write_file(filepath, content)
        +read_file(filepath)
        +list_files(directory)
    }
    
    class "ShellEnv" {
        +execute_command(command)
        +read_stdout()
    }
    
    class "RapidAPIEnv" {
        +retrieve_apis(query)
        +call_api(api_name, parameters)
    }
    
    "BaseEnv" <|-- "PythonNotebook"
    "BaseEnv" <|-- "WebEnv"
    "BaseEnv" <|-- "FileEditorEnv"
    "BaseEnv" <|-- "ShellEnv"
    "BaseEnv" <|-- "RapidAPIEnv"
```

Sources: [ToolServer/ToolServerNode/core/envs/pycoding.py:16-17](), [ToolServer/ToolServerNode/core/envs/web.py:12-14]()

## Detailed Tool Descriptions

### File Editor

The File Editor provides capabilities for working with files in the ToolServer environment. It allows agents to read, write, and modify text files.

Key capabilities:
- Creating new text files
- Reading existing file content
- Modifying file content
- Listing directories and files

Sources: [ToolServer/README.md:11]()

### Python Notebook

The Python Notebook provides an interactive environment for executing Python code, similar to Jupyter notebooks. This enables agents to test ideas, validate algorithms, and generate visualizations.

```mermaid
sequenceDiagram
    participant "XAgent" as XA
    participant "ToolServer" as TS
    participant "PythonNotebook" as PN
    participant "NotebookClient" as NC
    
    XA->>TS: execute_tool(tool="PythonNotebook.execute_cell", parameters)
    TS->>PN: execute_cell(code, cell_index, reset)
    
    alt reset is True or kernel not running
        PN->>PN: _reset()
        PN->>NC: create_kernel_manager()
        PN->>NC: async_start_new_kernel()
        PN->>NC: async_start_new_kernel_client()
    end
    
    PN->>PN: Append/Replace cell
    PN->>NC: async_execute_cell()
    NC-->>PN: Execution result
    PN->>PN: _format_outputs()
    PN-->>TS: Formatted output
    TS-->>XA: Execution result
```

Key capabilities:
- Creating and executing Python code cells
- Maintaining persistent notebook state between calls
- Supporting kernel reset when needed
- Saving notebook outputs (text and binary data like images)
- Displaying formatted outputs, including error tracebacks

Example usage:
```python
# First cell: basic calculation
execute_cell(code='print(2 + 2)')  # Output: 4

# Second cell: creating a variable
execute_cell(code='x = [1, 2, 3]\nprint(x)')  # Output: [1, 2, 3]

# Third cell: using previously defined variable
execute_cell(code='print(sum(x))')  # Output: 6
```

Sources: [ToolServer/ToolServerNode/core/envs/pycoding.py:16-181]()

### Web Browser

The Web Browser provides capabilities for interacting with web content. It enables agents to search the web, visit websites, and extract information from webpages.

```mermaid
sequenceDiagram
    participant "XAgent" as XA
    participant "ToolServer" as TS
    participant "WebEnv" as WE
    participant "SearchEngine" as SE
    participant "Website" as WS
    
    XA->>TS: execute_tool(tool="WebEnv.search_and_browse", parameters)
    TS->>WE: search_and_browse(search_query, goals_to_browse, region, num_results)
    
    alt Bing API key available
        WE->>SE: Bing search request
    else No API key
        WE->>SE: DuckDuckGo search request
    end
    
    SE-->>WE: Search results (URLs)
    
    loop For each result URL
        WE->>WE: browse_website(url, goals_to_browse)
        WE->>WS: HTTP GET request
        WS-->>WE: HTML response
        WE->>WE: Parse HTML, extract text and links
    end
    
    WE-->>TS: Compiled search results
    TS-->>XA: Search and browse results
```

Key capabilities:
- Performing web searches using either Bing API or DuckDuckGo
- Browsing specific URLs to extract text content
- Extracting and formatting links from webpages
- Processing HTTP redirects
- Configurable user-agent and region settings

Security features:
- URL validation to prevent access to local resources
- HTTP client with configurable timeouts

Sources: [ToolServer/ToolServerNode/core/envs/web.py:12-126]()

### Shell

The Shell provides a command-line interface for executing system commands. This allows agents to run shell commands, install software, and interact with the host system.

Key capabilities:
- Executing arbitrary shell commands
- Reading command outputs
- Managing running processes
- Installing software packages
- Hosting services or running server applications

Security note: The Shell tool runs in a containerized environment to isolate it from the host system.

Sources: [ToolServer/README.md:14]()

### Rapid API

The Rapid API tool provides access to a wide range of third-party APIs through the Rapid API hub. This enables agents to leverage external services and data sources.

Key capabilities:
- Retrieving API information based on queries
- Calling APIs with appropriate parameters
- Processing API responses
- Access to hundreds of APIs across various domains

Sources: [ToolServer/README.md:15]()

## Tool Execution Flow

When XAgent needs to use a tool, it follows a specific flow to interact with the ToolServer system:

```mermaid
flowchart TD
    subgraph "XAgent Core"
        direction TB
        TA["Tool Agent"]
        XA["XAgent"]
    end
    
    subgraph "ToolServer System"
        direction TB
        TSM["ToolServerManager"]
        TSN["ToolServerNode"]
        
        subgraph "Available Tools"
            direction TB
            FE["FileEditorEnv"]
            PN["PythonNotebook"]
            WE["WebEnv"]
            SE["ShellEnv"]
            RE["RapidAPIEnv"]
        end
    end
    
    XA --> TA
    TA -->|"1. execute_tool(tool_name, parameters)"| TSM
    TSM -->|"2. Route to appropriate node"| TSN
    TSN -->|"3. Identify requested tool"| TSN
    TSN -->|"4a. File operations"| FE
    TSN -->|"4b. Python code execution"| PN
    TSN -->|"4c. Web browsing/searching"| WE
    TSN -->|"4d. Shell commands"| SE
    TSN -->|"4e. API calls"| RE
    
    FE & PN & WE & SE & RE -->|"5. Return result"| TSN
    TSN -->|"6. Process and format result"| TSM
    TSM -->|"7. Return formatted result"| TA
    TA -->|"8. Process tool output"| XA
```

Sources: [ToolServer/README.md:5-9](), [ToolServer/README.md:158-180]()

## Tool Discoverability and Selection

XAgent can discover and select appropriate tools through several methods provided by the ToolServer API:

1. **Tool Listing**: Get a complete list of available tools with their schemas:
   ```
   GET /get_available_tools
   ```

2. **Tool Retrieval**: Find relevant tools for a specific question:
   ```
   POST /retrieving_tools
   {
     "question": "How do I create a visualization?",
     "top_k": 3
   }
   ```

3. **Schema Retrieval**: Get JSON schemas for specific tools:
   ```
   POST /get_json_schema_for_tools
   {
     "tools": ["PythonNotebook.execute_cell", "WebEnv.browse_website"]
   }
   ```

These capabilities allow XAgent to dynamically discover and use the appropriate tools for different tasks, enhancing its flexibility and problem-solving capabilities.

Sources: [ToolServer/README.md:43-130]()

## Tool Integration with XAgent

Tools are integrated with XAgent through the tool agent system. When XAgent needs to perform a specific operation, it:

1. Selects an appropriate tool based on the task requirements
2. Constructs the tool call with appropriate parameters
3. Executes the tool via the ToolServer
4. Processes and summarizes the tool output

The action summarization system in XAgent helps process tool outputs for better integration into the agent's workflow:

```mermaid
sequenceDiagram
    participant XA as "XAgent"
    participant TS as "ToolServer"
    participant SA as "Summarize Action"
    
    XA->>TS: execute_tool(tool, parameters)
    TS-->>XA: Tool execution result
    
    XA->>SA: summarize_action(action_process, task)
    Note over SA: Process action output
    Note over SA: Generate summary
    Note over SA: Format for agent consumption
    
    SA-->>XA: Summarized action
    
    XA->>XA: Incorporate result into reasoning
```

Sources: [XAgent/agent/summarize.py:11-163]()

## Tool Extension

The modular design of the ToolServer allows for easy extension with new tools. New tools can be added by creating a new environment class that extends the `BaseEnv` class and registering it with the `toolwrapper` decorator.

This extensibility enables XAgent to continuously evolve with new capabilities as needed for different use cases.

Sources: [ToolServer/README.md:16]()

---

# Page: ToolServer Management

# ToolServer Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ToolServer/ToolServerManager/main.py](ToolServer/ToolServerManager/main.py)
- [ToolServer/ToolServerManager/models.py](ToolServer/ToolServerManager/models.py)
- [ToolServer/ToolServerManager/node_checker.py](ToolServer/ToolServerManager/node_checker.py)
- [ToolServer/ToolServerManager/requirements.txt](ToolServer/ToolServerManager/requirements.txt)

</details>



This document details the mechanisms and procedures for managing ToolServer instances within the XAgent system. It covers the creation, monitoring, health-checking, and lifecycle management of ToolServer nodes, which are Docker containers that provide isolated environments for tool execution. For information about the overall ToolServer architecture, see [ToolServer Architecture](#3.1). For details about the specific tools available within ToolServer, see [Tool Types and Capabilities](#3.2).

## 1. ToolServer Management Components

The ToolServer management system consists of three primary components that work together to create, monitor, and maintain tool execution environments.

```mermaid
graph TD
    subgraph "ToolServerManager"
        TSM["ToolServerManager API"]
        NC["NodeChecker"]
    end
    
    TSM -->|"creates/manages"| TSN1["ToolServerNode 1"]
    TSM -->|"creates/manages"| TSN2["ToolServerNode 2"]
    TSM -->|"creates/manages"| TSN3["ToolServerNode N"]
    
    NC -->|"monitors"| TSN1
    NC -->|"monitors"| TSN2
    NC -->|"monitors"| TSN3
    
    DB[(MongoDB)] <-->|"stores node info"| TSM
    DC["Docker Client"] <-->|"container operations"| TSM
    
    TSM -->|"starts on startup"| NC
    
    subgraph "Docker Environment"
        TSN1
        TSN2
        TSN3
    end
    
    Client["XAgent/Client"] -->|"API requests"| TSM
    Client -->|"tool calls"| TSN1
    Client -->|"tool calls"| TSN2
    Client -->|"tool calls"| TSN3
```

Sources: [ToolServer/ToolServerManager/main.py:10-45](), [ToolServer/ToolServerManager/node_checker.py:10-69]()

### 1.1 ToolServerManager

The ToolServerManager is a FastAPI application that serves as the central control point for managing ToolServer nodes. It provides endpoints for:

- Creating new nodes (`/get_cookie`)
- Reconnecting to existing nodes (`/reconnect_session`)
- Closing nodes (`/close_session`)
- Releasing nodes (`/release_session`)
- Routing API calls to specific nodes

It interacts with Docker to create, start, stop, and remove containers, and maintains node metadata in a database.

### 1.2 NodeChecker

The NodeChecker (also called ToolServerMonitor) is responsible for continuously monitoring the status of all ToolServer nodes. It:

- Verifies node existence in Docker
- Updates node status and health information in the database
- Automatically stops idle nodes based on configured timeout values
- Runs as an asynchronous task within the ToolServerManager

### 1.3 ToolServerNode

A ToolServerNode is a Docker container that provides a controlled environment for executing tools. Each node has:

- A unique identifier (Docker container ID)
- Status information (running, stopped, etc.)
- Health status
- Network information (IP address and port)
- Timestamp of the last request

## 2. ToolServerNode Lifecycle Management

ToolServer nodes go through a defined lifecycle from creation to removal. The ToolServerManager provides APIs to control this lifecycle.

```mermaid
stateDiagram-v2
    [*] --> Created: "/get_cookie"
    Created --> Running: "wait_for_node_startup"
    Running --> Restarted: "/reconnect_session"
    Restarted --> Running
    Running --> Stopped: "/close_session or idle timeout"
    Stopped --> Running: "/reconnect_session"
    Running --> Removed: "/release_session"
    Stopped --> Removed: "/release_session"
    Removed --> [*]
```

Sources: [ToolServer/ToolServerManager/main.py:75-106](), [ToolServer/ToolServerManager/main.py:108-226]()

### 2.1 Node Creation

Nodes are created via the `/get_cookie` endpoint, which:

1. Creates a Docker container using configured parameters
2. Records node information in the database
3. Waits for the node to become ready
4. Returns the node ID as a cookie to the client

```mermaid
sequenceDiagram
    participant Client
    participant TSM as "ToolServerManager"
    participant DC as "Docker Client"
    participant DB as "MongoDB"
    
    Client->>+TSM: POST /get_cookie
    TSM->>+DC: containers.run(CONFIG['node']['creation_kwargs'])
    DC-->>-TSM: return container
    
    TSM->>DB: Insert ToolServerNode record
    
    TSM->>+TSM: wait_for_node_startup(container.id)
    loop Probe until healthy or timeout
        TSM->>DB: Find node
        TSM->>TSM: Check node.health == 'healthy'
    end
    TSM-->>-TSM: Node ready or timeout
    
    TSM-->>-Client: Response with node_id cookie
```

Sources: [ToolServer/ToolServerManager/main.py:108-150](), [ToolServer/ToolServerManager/main.py:75-106]()

### 2.2 Node Reconnection

If a node is stopped or needs to be restarted, the `/reconnect_session` endpoint handles this by:

1. Retrieving node information from the database
2. Restarting the Docker container
3. Waiting for the node to become ready again

Sources: [ToolServer/ToolServerManager/main.py:152-179]()

### 2.3 Node Closure

When a node is no longer needed but may be reused later, it can be stopped via the `/close_session` endpoint, which:

1. Retrieves node information from the database
2. Stops the Docker container if it's running

Sources: [ToolServer/ToolServerManager/main.py:181-200]()

### 2.4 Node Release

When a node is completely finished with and should be removed, the `/release_session` endpoint:

1. Retrieves node information from the database
2. Kills the Docker container if it's still running
3. Removes the Docker container

Sources: [ToolServer/ToolServerManager/main.py:202-226]()

## 3. Node Monitoring and Health Checking

The NodeChecker continuously monitors all ToolServer nodes to maintain accurate status information and perform cleanup operations.

```mermaid
flowchart TD
    Start["check_nodes_status_loop()"] --> Check["check_nodes_status()"]
    
    subgraph "For each node in database"
        Check --> GetContainer["Get container from Docker"]
        GetContainer --> ContainerExists{"Container exists?"}
        
        ContainerExists -->|"No"| DeleteFromDB["Delete node from database"]
        ContainerExists -->|"Yes"| UpdateStatus["Update node status in database"]
        
        UpdateStatus --> HealthCheck{"Health check enabled?"}
        HealthCheck -->|"Yes"| UpdateHealth["Update node health in database"]
        HealthCheck -->|"No"| Skip["Skip health update"]
        
        UpdateHealth --> IdleCheck{"Node running and idle?"}
        Skip --> IdleCheck
        
        IdleCheck -->|"Yes"| StopNode["Stop container"]
        IdleCheck -->|"No"| Next["Process next node"]
        
        StopNode --> Next
        DeleteFromDB --> Next
    end
    
    Next --> Sleep["Sleep for health_check_interval"]
    Sleep --> Check
```

Sources: [ToolServer/ToolServerManager/node_checker.py:11-68]()

### 3.1 Node Status Checking

The NodeChecker performs the following status checks:

1. Verifies each node in the database exists in Docker
2. Updates node status based on Docker container state
3. If health checking is enabled, updates node health status
4. Checks for idle nodes and stops them based on configured timeout

```python
# Pseudocode for idle node detection
if node_status == "running":
    if current_time - node.last_req_time >= CONFIG['node']['idling_close_minutes']:
        container.stop()
```

Sources: [ToolServer/ToolServerManager/node_checker.py:11-55]()

### 3.2 Automatic Health Monitoring

When configured, the system can use Docker's built-in health checking to monitor node health:

1. The `health_check` configuration option enables health monitoring
2. Node health status is updated in the database during status checks
3. Health status is used to determine if a node is ready during startup

This provides a robust mechanism for ensuring nodes are operational before routing requests to them.

Sources: [ToolServer/ToolServerManager/node_checker.py:42-46](), [ToolServer/ToolServerManager/main.py:97-102]()

## 4. Request Routing to Nodes

The ToolServerManager acts as a proxy, routing requests to the appropriate ToolServerNode based on the `node_id` cookie.

```mermaid
sequenceDiagram
    participant Client
    participant TSM as "ToolServerManager"
    participant TSN as "ToolServerNode"
    participant DB as "MongoDB"
    
    Client->>+TSM: Request with node_id cookie
    TSM->>DB: Find node by ID
    
    alt Invalid node_id
        TSM-->>Client: 403 Forbidden - Invalid node_id
    else Node not running
        TSM-->>Client: 503 Service Unavailable - Node not running
    else Node is running
        TSM->>DB: Update node.last_req_time
        
        TSM->>+TSN: Forward request to node.ip:node.port
        
        alt Node responds
            TSN-->>-TSM: Response
            TSM-->>-Client: Forward response
        else Node not responding
            TSM-->>Client: 503 Service Unavailable - Node not responding
        end
    end
```

Sources: [ToolServer/ToolServerManager/main.py:228-269]()

The routing process involves:

1. Validating the node ID from the cookie
2. Checking that the node is running
3. Updating the last request time in the database
4. Forwarding the request to the node
5. Capturing and forwarding the response back to the client

This proxy mechanism allows clients to maintain a connection to a specific ToolServerNode while the ToolServerManager handles the underlying container management.

## 5. Configuration Parameters

The ToolServer management system is configured through several parameters that control node creation, monitoring, and lifecycle management.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `builtin_monitor` | Enable/disable the built-in node monitor | `true` |
| `node.health_check` | Enable/disable Docker health checks | Varies |
| `node.health_check_interval` | Interval between health checks (seconds) | `1` |
| `node.creation_wait_seconds` | Maximum time to wait for node startup | Varies |
| `node.idling_close_minutes` | Minutes of inactivity before node is stopped | Varies |
| `node.creation_kwargs` | Docker container creation parameters | Varies |
| `node.device_requests` | Device requests for Docker containers (e.g., GPU) | Varies |
| `node.port` | Port for ToolServerNode | `31942` |

Sources: [ToolServer/ToolServerManager/main.py:31-45](), [ToolServer/ToolServerManager/main.py:127-141](), [ToolServer/ToolServerManager/node_checker.py:52-54]()

## 6. Dependencies and Requirements

The ToolServerManager has several dependencies required for operation:

- FastAPI: Web framework for the API
- Uvicorn: ASGI server for running FastAPI
- Docker: Python client for Docker API
- HTTPX: HTTP client for making requests to nodes
- Beanie: MongoDB ODM for Python
- Motor: MongoDB driver for Python
- Psutil: Library for process and system monitoring

Sources: [ToolServer/ToolServerManager/requirements.txt:1-9]()

These dependencies enable the ToolServerManager to create and manage Docker containers, handle HTTP requests, store data in MongoDB, and monitor system resources.

---

# Page: XAgentServer

# XAgentServer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgent/recorder.py](XAgent/recorder.py)
- [XAgentServer/README.md](XAgentServer/README.md)
- [XAgentServer/README_zh.md](XAgentServer/README_zh.md)
- [XAgentServer/database/change/change_desc.sql](XAgentServer/database/change/change_desc.sql)
- [XAgentServer/server.py](XAgentServer/server.py)
- [docker-compose.yml](docker-compose.yml)

</details>



XAgentServer is a crucial component in the XAgent system that serves as the bridge between the web interface (XAgentWeb) and the XAgent Core. It provides a communication layer that allows users to interact with the autonomous agent system through a web-based interface. XAgentServer handles WebSocket connections, manages sessions, and orchestrates the execution of tasks by the underlying XAgent Core system.

For information about the core agent system that XAgentServer communicates with, see [XAgent Core](#2).

## 1. Purpose and Functionality

XAgentServer serves several key purposes:

1. **Frontend-Backend Bridge**: Acts as an intermediary between the web frontend (XAgentWeb) and the core XAgent system
2. **WebSocket Communication**: Manages real-time bidirectional communication with clients
3. **Task Orchestration**: Coordinates task execution by the XAgent Core
4. **Session Management**: Maintains user sessions using Redis
5. **Data Persistence**: Stores interaction data in MySQL database
6. **File Handling**: Manages file uploads and transfers them to the appropriate workspaces

Sources:
- [XAgentServer/README.md:1-19]()
- [XAgentServer/server.py:1-24]()

## 2. System Architecture

XAgentServer is built on FastAPI, a modern web framework for Python. It uses WebSocket for long-connection communication services and integrates with Redis for state management and MySQL for data persistence.

### 2.1 Component Overview

```mermaid
graph TB
    Client["Web Client"]
    XAS["XAgentServer"]
    XAC["XAgent Core"]
    TS["ToolServer"]
    Redis[(Redis)]
    MySQL[(MySQL)]
    
    Client <-->|"WebSocket"| XAS
    XAS -->|"Session State"| Redis
    XAS -->|"Stores Data"| MySQL
    XAS -->|"Orchestrates"| XAC
    XAC -->|"Tool Requests"| TS
    
    subgraph "XAgentServer Components"
        Routers["Routers"]
        WSHandlers["WebSocket Handlers"]
        Schemas["Request/Response Schemas"]
        CRUDS["Database CRUDS"]
    end
    
    XAS --- Routers
    XAS --- WSHandlers
    XAS --- Schemas
    XAS --- CRUDS
```

Sources:
- [XAgentServer/README.md:24-28]()
- [XAgentServer/README.md:30-51]()
- [docker-compose.yml:43-64]()

### 2.2 Directory Structure

XAgentServer is organized into the following key directories:

| Directory | Purpose |
|-----------|---------|
| application/core | Core configuration files |
| application/cruds | Database operations (Create, Read, Update, Delete) |
| application/routers | FastAPI route definitions |
| application/schemas | Request and response data structures |
| application/websockets | WebSocket communication framework |
| database | Database models and connection handling |
| enums | Enumeration type definitions |
| exts | Extensions and utilities |
| loggers | Logging functionality |
| models | Business module definitions |

Sources:
- [XAgentServer/README.md:30-51]()

## 3. Communication Flow

XAgentServer communicates with clients via WebSocket connections, which allow real-time bidirectional communication. This enables XAgentServer to send continuous updates to the client as the agent works on tasks.

```mermaid
sequenceDiagram
    participant Client as "Web Client"
    participant XAS as "XAgentServer"
    participant XAC as "XAgent Core"
    participant TS as "ToolServer"
    participant DB as "MySQL + Redis"
    
    Client->>XAS: Connect WebSocket
    XAS->>Client: Connection established
    
    Client->>XAS: Send task request
    XAS->>DB: Create interaction record
    XAS->>XAC: Initialize XAgent with task
    
    XAC->>XAS: Request planning
    XAS->>Client: Send "starting" status
    
    loop For each subtask
        XAC->>TS: Execute tool operations
        TS->>XAC: Return tool results
        XAC->>XAS: Update subtask progress
        XAS->>Client: Send real-time updates
        
        alt Human intervention needed
            XAS->>Client: Request human input
            Client->>XAS: Provide input
            XAS->>XAC: Forward human input
        end
    end
    
    XAC->>XAS: Task completed
    XAS->>Client: Send completion status
    XAS->>DB: Update interaction record
```

Sources:
- [XAgentServer/server.py:27-109]()
- [XAgentServer/README.md:1-3]()

## 4. Server Implementation

The core of XAgentServer is implemented in the `XAgentServer` class, which handles the interaction between clients and the XAgent Core system.

### 4.1 Core Server Class

The `XAgentServer` class provides the main functionality for handling client requests and orchestrating the XAgent Core system. The key method is `interact()`, which:

1. Receives a task from the client
2. Initializes the XAgent Core with the task parameters
3. Handles file uploads
4. Starts the task execution process
5. Manages the communication back to the client

Sources:
- [XAgentServer/server.py:20-109]()

### 4.2 Task Execution Flow

When a task is received, XAgentServer follows this process:

1. Receives an `XAgentInteraction` object containing task parameters
2. Creates an `XAgentParam` object with the user's query
3. Builds XAgent Core components with the parameters
4. Transfers any uploaded files to the workspace
5. Starts the task handler to execute the task
6. Returns results and updates to the client in real-time

Sources:
- [XAgentServer/server.py:27-109]()

## 5. Database Integration

XAgentServer uses two primary data stores:

1. **MySQL**: For persistent storage of interaction data
2. **Redis**: For session state management

### 5.1 MySQL Integration

MySQL stores interaction records, user data, and task information. The database schema includes tables for:

- Interactions: Records of user interactions with XAgent
- Users: User account information
- Tasks: Task details and status
- Running records: Detailed execution logs

The database operations are handled through SQLAlchemy ORM using CRUD (Create, Read, Update, Delete) operations defined in the application/cruds directory.

Sources:
- [XAgentServer/README.md:24-28]()
- [XAgentServer/database/change/change_desc.sql:1-4]()
- [docker-compose.yml:66-84]()
- [XAgent/recorder.py:18-346]()

### 5.2 Redis Integration

Redis is used for managing session state and caching. It provides:

- Fast access to session data
- Temporary storage for intermediate results
- State management for long-running tasks

Sources:
- [docker-compose.yml:85-94]()
- [XAgentServer/README.md:12-17]()

## 6. Recording System

XAgentServer includes a comprehensive recording system that tracks all aspects of task execution. This is implemented through the `RunningRecoder` class, which:

1. Records all LLM interactions
2. Tracks tool calls and their results
3. Maintains a record of the planning process
4. Logs query and configuration information

```mermaid
graph LR
    XAS["XAgentServer"]
    XAC["XAgent Core"]
    RR["RunningRecoder"]
    DB[(MySQL)]
    
    XAS -->|"Creates"| RR
    XAC -->|"Uses"| RR
    RR -->|"Records"| DB
    
    subgraph "Record Types"
        LLM["LLM_INPUT_PAIR"]
        TOOL["TOOL_CALL"]
        PLAN["PLAN_REFINE"]
        TS["TOOL_SERVER_PAIR"]
        QUERY["QUERY"]
        CONFIG["CONFIG"]
    end
    
    RR --- LLM
    RR --- TOOL
    RR --- PLAN
    RR --- TS
    RR --- QUERY
    RR --- CONFIG
```

Sources:
- [XAgent/recorder.py:48-346]()

## 7. Deployment

XAgentServer can be deployed using Docker and docker-compose. The docker-compose configuration specifies:

1. The XAgentServer container
2. Dependencies on MySQL and Redis
3. Volume mounts for persistent storage
4. Network configuration
5. Environment variables

A typical deployment will involve starting the XAgentServer, MySQL, and Redis services using docker-compose, then starting the nginx service within the XAgentServer container to serve the frontend.

Sources:
- [docker-compose.yml:43-64]()
- [XAgentServer/README.md:53-69]()

## 8. Using XAgentServer

After deployment, users can access the XAgentServer frontend by visiting http://localhost:5173 in a web browser. The system provides:

1. A login interface with default credentials (Guest/xagent)
2. A playground interface for interacting with XAgent
3. Real-time updates as the agent works on tasks
4. File upload and management capabilities

Sources:
- [XAgentServer/README.md:70-79]()

## 9. Integration with XAgent Core

XAgentServer integrates with XAgent Core through the `interact` method, which:

1. Creates an `XAgentParam` object with the user's query
2. Builds the XAgent Core components
3. Transfers any uploaded files to the workspace
4. Starts the task handler to execute the task

This integration allows XAgentServer to orchestrate the XAgent Core system while maintaining a clean separation of concerns.

```mermaid
graph TD
    Client["Web Client"]
    XAS["XAgentServer"]
    
    subgraph "XAgent Core Components"
        XAC["XAgentCoreComponents"]
        XAP["XAgentParam"]
        TaskHandler["TaskHandler"]
        Dispatcher["Dispatcher"]
        Planner["Planner"]
        Actor["Actor"]
    end
    
    Client -->|"WebSocket"| XAS
    XAS -->|"Creates"| XAP
    XAS -->|"Builds"| XAC
    XAS -->|"Creates"| TaskHandler
    TaskHandler -->|"Uses"| Dispatcher
    Dispatcher -->|"Uses"| Planner
    Dispatcher -->|"Uses"| Actor
```

Sources:
- [XAgentServer/server.py:27-109]()

## Summary

XAgentServer is a critical component in the XAgent ecosystem, providing the communication layer between the web interface and the core agent system. It handles WebSocket connections, manages sessions, orchestrates task execution, and records all interactions for later analysis. By using FastAPI, Redis, and MySQL, it provides a robust and scalable platform for users to interact with the autonomous agent system.

---

# Page: Server Architecture

# Server Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgentServer/README.md](XAgentServer/README.md)
- [XAgentServer/README_zh.md](XAgentServer/README_zh.md)
- [XAgentServer/application/websockets/base.py](XAgentServer/application/websockets/base.py)
- [XAgentServer/database/change/change_desc.sql](XAgentServer/database/change/change_desc.sql)
- [XAgentServer/database/models.py](XAgentServer/database/models.py)
- [XAgentServer/database/sql/create_mysql_table.sql](XAgentServer/database/sql/create_mysql_table.sql)

</details>



This document describes the architecture of the XAgentServer component, which serves as the communication layer between clients and the XAgent Core system. XAgentServer provides WebSocket connections for real-time interaction with XAgent while handling data persistence, state management, and client communication.

For information about WebSocket communication protocols and message formats, see [WebSocket Interface](#4.2). For details about database integration, see [Database Integration](#4.3).

## Overview

XAgentServer is built using FastAPI as the web framework and provides a WebSocket-based communication channel with essential RESTful APIs for auxiliary operations. It serves as the bridge between the user interfaces (like XAgentWeb) and the XAgent Core system.

```mermaid
graph TB
    subgraph "Client Side"
        WebClient["Web Client"]
        CLI["Command Line Client"]
    end
    
    subgraph "XAgentServer"
        FastAPI["FastAPI Application"]
        WebSockets["WebSocket Handlers"]
        Routers["RESTful Routers"]
        Interaction["Interaction Module"]
    end
    
    subgraph "State & Storage"
        Redis[(Redis)]
        MySQL[(MySQL)]
    end
    
    subgraph "XAgent Core"
        XAgent["XAgent Core"]
        ToolServer["Tool Server"]
    end
    
    WebClient -->|"WebSocket"| WebSockets
    CLI -->|"HTTP Requests"| Routers
    
    WebSockets --> FastAPI
    Routers --> FastAPI
    
    FastAPI --> Interaction
    Interaction -->|"Uses"| Redis
    Interaction -->|"Persists"| MySQL
    
    Interaction -->|"Interacts with"| XAgent
    XAgent -->|"Uses"| ToolServer
```

Sources:
- [XAgentServer/README.md:24-28]()
- [XAgentServer/README.md:30-49]()
- [XAgentServer/application/websockets/base.py:1-20]()

## Key Components

The XAgentServer is organized into several key components:

### Application Layer

The application layer contains the core FastAPI application and includes:

1. **Core Configuration** - Basic settings and environment variables
2. **Routers** - FastAPI route handlers for HTTP endpoints
3. **WebSockets** - WebSocket handlers for real-time communication
4. **CRUDs** - Database operations for interactions, users, etc.
5. **Schemas** - Request and response data models

### Communication Layer

The communication layer is primarily WebSocket-based, allowing for bidirectional communication between the client and server:

1. **WebSocket Server** - Handles client connections and messages
2. **Task Handler** - Processes client requests in a separate thread
3. **Data Sender** - Sends updates to clients asynchronously

### Data Persistence Layer

XAgentServer uses several technologies for data storage and state management:

1. **MySQL Database** - Stores interaction data, user information, etc.
2. **Redis** - Manages the state of ongoing interactions
3. **Local Storage** - Stores interaction logs and files

```mermaid
graph TB
    subgraph "XAgentServer Components"
        subgraph "Application Layer"
            FastAPI["FastAPI Application"]
            Routers["RESTful Routes"]
            WSHandlers["WebSocket Handlers"]
            Deps["Dependencies"]
        end
        
        subgraph "Business Logic"
            Interaction["interaction.py"]
            Server["server.py"]
            CRUDs["Database CRUDs"]
        end
        
        subgraph "Data Layer"
            Models["Data Models"]
            ORM["SQLAlchemy ORM"]
        end
    end
    
    subgraph "External Dependencies"
        MySQL[(MySQL)]
        Redis[(Redis)]
        FileSystem["Local File System"]
    end
    
    FastAPI -->|"Uses"| Routers
    FastAPI -->|"Uses"| WSHandlers
    FastAPI -->|"Injects"| Deps
    
    WSHandlers -->|"Calls"| Interaction
    Routers -->|"Calls"| CRUDs
    
    Interaction -->|"Uses"| Server
    Interaction -->|"Uses"| CRUDs
    
    CRUDs -->|"Uses"| ORM
    ORM -->|"Maps"| Models
    
    ORM -->|"Connects to"| MySQL
    Interaction -->|"State management"| Redis
    Interaction -->|"Logs to"| FileSystem
```

Sources:
- [XAgentServer/README.md:30-49]()
- [XAgentServer/application/websockets/base.py:69-81]()

## WebSocket Communication Flow

The WebSocket server is the primary means of communication with clients. The main class `MainServer` extends `WebSocketEndpoint` and handles connections, message receiving, and task execution.

```mermaid
sequenceDiagram
    participant Client as "Web Client"
    participant WSServer as "MainServer (WebSocket)"
    participant Redis as "Redis"
    participant DB as "MySQL Database"
    participant XAgent as "XAgent Interaction"
    
    Client->>WSServer: Connect WebSocket with client_id
    WSServer->>WSServer: Create logger and validate user
    WSServer->>DB: Create/update interaction record
    WSServer->>Client: Connection established
    
    Client->>WSServer: Send task data (args, agent, mode)
    WSServer->>DB: Store interaction parameters
    WSServer->>WSServer: Start scheduler for pong and send_data
    
    WSServer->>XAgent: Start task_handler thread
    activate XAgent
    
    XAgent->>DB: Update interaction status to "running"
    XAgent->>XAgent: Execute task
    
    loop Task Execution
        XAgent->>DB: Save progress in raw table
        Redis->>Redis: Set flag to indicate data to send
        
        WSServer->>DB: Check for data to send
        WSServer->>Client: Send updates via WebSocket
        
        alt Human Intervention Needed
            XAgent->>DB: Mark as needing human help
            WSServer->>Client: Request human input
            Client->>WSServer: Send human input
            WSServer->>Redis: Signal received input
            XAgent->>DB: Read human input
        end
    end
    
    XAgent->>DB: Update status to "finished" or "failed"
    deactivate XAgent
    
    WSServer->>Client: Send final result
    Client->>WSServer: Disconnect
    WSServer->>Redis: Set status to "close"
    WSServer->>WSServer: Clean up resources
```

Sources:
- [XAgentServer/application/websockets/base.py:81-126]()
- [XAgentServer/application/websockets/base.py:283-337]()
- [XAgentServer/application/websockets/base.py:338-389]()

## Database Schema

XAgentServer uses MySQL for data persistence with several key tables. The database schema is designed to support the stateful nature of agent interactions and user management.

### Core Tables

```mermaid
erDiagram
    users {
        int id PK
        string user_id UK
        string email UK
        string name
        string token
        boolean available
        boolean is_beta
        string create_time
        string update_time
    }
    
    interactions {
        int id PK
        string interaction_id
        string user_id FK
        string create_time
        string update_time
        text description
        string agent
        string mode
        text recorder_root_dir
        json file_list
        string status
        text message
        string current_step
        boolean is_deleted
        string call_method
    }
    
    interaction_parameters {
        int id PK
        string interaction_id FK
        string parameter_id
        json args
    }
    
    raw {
        int id PK
        string node_id UK
        string interaction_id FK
        string current
        int step
        json data
        json file_list
        string status
        boolean do_interrupt
        int wait_seconds
        boolean ask_for_human_help
        boolean is_human
        json human_data
        boolean is_send
        boolean is_receive
    }
    
    running_record {
        int id PK
        string record_id
        string current
        string node_id
        string node_type
        json data
        string create_time
        string update_time
        boolean is_deleted
    }
    
    users ||--o{ interactions : "creates"
    interactions ||--o{ interaction_parameters : "has"
    interactions ||--o{ raw : "produces"
    interactions ||--o{ running_record : "records"
```

Sources:
- [XAgentServer/database/sql/create_mysql_table.sql:28-138]()
- [XAgentServer/database/models.py:6-138]()

## Data Flow Architecture

The data flow in XAgentServer involves multiple components communicating with each other to handle user interactions with XAgent.

```mermaid
graph TD
    subgraph "Client Input"
        WebSocketMsg["WebSocket Message"]
    end
    
    subgraph "XAgentServer"
        WSHandler["MainServer WebSocket Handler"]
        TaskHandler["Task Handler Thread"]
        DataSender["Async Data Sender"]
        Scheduler["APScheduler"]
    end
    
    subgraph "Data Processing"
        XAgentInteraction["XAgentInteraction"]
        XAgentServerObj["XAgentServer Object"]
    end
    
    subgraph "Storage"
        RedisState["Redis State"]
        MySQLDB["MySQL Database"]
        LogFiles["Log Files"]
    end
    
    WebSocketMsg -->|"1. Receive task"| WSHandler
    WSHandler -->|"2. Store parameters"| MySQLDB
    WSHandler -->|"3. Start thread"| TaskHandler
    WSHandler -->|"4. Start scheduler"| Scheduler
    
    TaskHandler -->|"5. Create interaction"| XAgentInteraction
    XAgentInteraction -->|"6. Register logger"| LogFiles
    XAgentInteraction -->|"7. Register DB"| MySQLDB
    
    TaskHandler -->|"8. Create server"| XAgentServerObj
    XAgentServerObj -->|"9. Interact"| XAgentInteraction
    
    XAgentInteraction -->|"10. Update status"| MySQLDB
    XAgentInteraction -->|"10. Set flags"| RedisState
    
    Scheduler -->|"11. Poll for updates"| RedisState
    Scheduler -->|"12. Check for data"| MySQLDB
    Scheduler -->|"13. Send updates"| WSHandler
    
    RedisState -->|"14. Status signals"| Scheduler
```

Sources:
- [XAgentServer/application/websockets/base.py:206-281]()
- [XAgentServer/application/websockets/base.py:344-389]()

## Server Integration with XAgent Core

XAgentServer integrates with XAgent Core through the `interaction.py` module, which serves as the bridge between the server and the agent system.

```mermaid
graph LR
    subgraph "XAgentServer"
        WSHandler["WebSocket Handler"]
        TaskHandler["Task Handler"]
    end
    
    subgraph "Integration Layer"
        Interaction["XAgentInteraction"]
        Server["XAgentServer class"]
    end
    
    subgraph "XAgent Core"
        XAgentCore["XAgent Core"]
        ToolServer["Tool Server"]
    end
    
    WSHandler -->|"Creates and configures"| TaskHandler
    TaskHandler -->|"1. Creates"| Interaction
    TaskHandler -->|"2. Creates"| Server
    
    Interaction -->|"Stores parameters"| Interaction
    
    Server -->|"3. interact() method"| Interaction
    Interaction -->|"4. Calls XAgent methods"| XAgentCore
    XAgentCore -->|"5. Uses tools via"| ToolServer
    
    XAgentCore -->|"6. Returns results"| Interaction
    Interaction -->|"7. Updates DB"| WSHandler
```

Sources:
- [XAgentServer/application/websockets/base.py:283-325]()
- [XAgentServer/README.md:24-28]()

## Deployment Configuration

XAgentServer is designed to be deployed using Docker, with configurations for service dependencies and networking.

```mermaid
graph TB
    subgraph "Docker Deployment"
        XAgentServerContainer["XAgent-Server Container"]
        NginxService["Nginx Service"]
    end
    
    subgraph "Required Dependencies"
        MySQL["MySQL Container<br>Port 3306"]
        Redis["Redis Container<br>Port 6379"]
    end
    
    subgraph "Network Configuration"
        Port8090["Port 8090<br>FastAPI Server"]
        Port5173["Port 5173<br>Frontend"]
    end
    
    XAgentServerContainer -->|"Connects to"| MySQL
    XAgentServerContainer -->|"Uses"| Redis
    XAgentServerContainer -->|"Runs"| NginxService
    
    NginxService -->|"Exposes"| Port5173
    XAgentServerContainer -->|"Exposes"| Port8090
    
    Port5173 -->|"Web UI"| Clients[("Web Clients")]
    Port8090 -->|"API/WebSocket"| Clients
```

Sources:
- [XAgentServer/README.md:5-17]()
- [XAgentServer/README.md:53-67]()

## Component Directory Structure

XAgentServer has a well-organized directory structure that separates different concerns:

| Directory | Purpose |
|-----------|---------|
| `application/core` | Core configuration files |
| `application/cruds` | Database CRUD operations |
| `application/routers` | FastAPI route definitions |
| `application/schemas` | Request/response schemas |
| `application/websockets` | WebSocket handlers |
| `database` | Database connection and models |
| `enums` | Enumeration types |
| `exts` | Extensions and utilities |
| `loggers` | Logging configuration |
| `models` | Business model definitions |
| `dockerfiles` | Docker build files |

Sources:
- [XAgentServer/README.md:30-49]()
- [XAgentServer/README_zh.md:31-51]()

## Error Handling and State Management

XAgentServer implements robust error handling and state management to maintain system integrity during interactions.

```mermaid
graph TD
    subgraph "State Management"
        RedisState["Redis State Store"]
        ClientIDKey["client_id key"]
        SendFlag["client_id_send flag"]
        ReceiveFlag["client_id_node_id_receive flag"]
    end
    
    subgraph "Error Handling"
        ConnectError["XAgentWebSocketConnectError"]
        GeneralError["XAgentError"]
        ErrorLog["Error Logging"]
        DBErrorRecord["Database Error Record"]
    end
    
    subgraph "Flow Control"
        TaskExecution["Task Execution"]
        ErrorHandling["Error Handling Block"]
        Cleanup["Cleanup Block"]
    end
    
    TaskExecution -->|"Success Path"| RedisState
    TaskExecution -->|"Error Path"| ErrorHandling
    ErrorHandling -->|"Logs"| ErrorLog
    ErrorHandling -->|"Records"| DBErrorRecord
    ErrorHandling -->|"Sets flag"| SendFlag
    
    ErrorHandling -->|"Finally"| Cleanup
    TaskExecution -->|"Finally"| Cleanup
    
    Cleanup -->|"Update interaction"| DBErrorRecord
    Cleanup -->|"Signal close"| RedisState
```

Sources:
- [XAgentServer/application/websockets/base.py:81-125]()
- [XAgentServer/application/websockets/base.py:325-337]()

---

# Page: WebSocket Interface

# WebSocket Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgentServer/application/websockets/base.py](XAgentServer/application/websockets/base.py)
- [XAgentServer/database/models.py](XAgentServer/database/models.py)
- [XAgentServer/database/sql/create_mysql_table.sql](XAgentServer/database/sql/create_mysql_table.sql)
- [XAgentWeb/src/views/playground/chat.vue](XAgentWeb/src/views/playground/chat.vue)
- [XAgentWeb/vite.config.ts](XAgentWeb/vite.config.ts)

</details>



This page documents the WebSocket interface in XAgent, which provides real-time bidirectional communication between the XAgentWeb frontend and the XAgentServer backend. The WebSocket interface allows clients to send task requests, receive execution updates, and interact with the autonomous agent system as tasks are processed.

For information about the overall XAgentServer architecture, see [Server Architecture](#4.1).

## WebSocket Connection Architecture

The WebSocket interface connects the client (XAgentWeb) and server (XAgentServer) components, enabling real-time updates during task execution by XAgent Core.

```mermaid
flowchart LR
    subgraph "Client Side"
        WebClient["XAgentWeb Client"]
        WsClient["WebSocket Client\n(chat.vue)"]
    end
    
    subgraph "Server Side"
        Router["FastAPI WebSocket Router"]
        WsServer["WebSocketEndpoint\n(MainServer)"]
        XAgentInteraction["XAgentInteraction"]
        XAgentCoreSystem["XAgent Core System"]
    end
    
    subgraph "Data Storage"
        MySQL[(MySQL DB)]
        Redis[(Redis)]
    end
    
    WebClient --> WsClient
    WsClient <-->|"ws://{host}/ws/{type}/{client_id}"| Router
    Router --> WsServer
    WsServer <-->|"session state"| Redis
    WsServer <-->|"interaction data"| MySQL
    WsServer --> XAgentInteraction
    XAgentInteraction --> XAgentCoreSystem
```

Sources: [XAgentServer/application/websockets/base.py:56-410](), [XAgentWeb/src/views/playground/chat.vue:232-481]()

## WebSocket Connection Types

XAgent supports four types of WebSocket connections based on the interaction mode:

| Connection Type | WebSocket Path | Purpose |
|----------------|---------------|---------|
| New Talk | `/ws/base/{client_id}` | Start a new task with XAgent |
| Playback | `/ws/replay/{client_id}` | Replay a previously executed task |
| Recorder | `/ws/recorder/{client_id}` | Replay a recorded interaction |
| Shared Task | `/ws/share/{client_id}` | Run a task shared by another user |

The `client_id` is a unique identifier for the interaction, and each connection type follows a specific protocol for data exchange.

Sources: [XAgentWeb/src/views/playground/chat.vue:240-245](), [XAgentServer/application/websockets/base.py:56]()

## WebSocket Connection Establishment

The following diagram shows the WebSocket connection establishment process:

```mermaid
sequenceDiagram
    participant Client as "XAgentWeb Client"
    participant Server as "XAgentServer WebSocketEndpoint"
    participant DB as "MySQL Database"
    participant Redis as "Redis Cache"
    
    Client->>Server: WebSocket Connection Request
    Note over Client,Server: ws://host/ws/{type}/{client_id}?user_id={id}&token={token}
    
    Server->>DB: Validate User Credentials
    Server->>DB: Check for Running Interactions
    Server->>DB: Create Interaction Record
    Server->>Redis: Set Connection Status Key
    
    alt Authentication Success
        Server->>Client: {"status": "connect", "success": true}
    else Authentication Failure
        Server->>Client: {"status": "connect", "success": false, "message": "error"}
        Server->>Client: Close Connection
    end
```

Sources: [XAgentServer/application/websockets/base.py:126-192](), [XAgentWeb/src/views/playground/chat.vue:413-457]()

## WebSocket Message Protocol

### Client to Server Messages

Messages sent from the client to the server follow this structure:

```json
{
  "type": "data|ping|disconnect|connect",
  "args": {
    "goal": "Task description or user input"
  },
  "agent": "agent_name",
  "mode": "auto|manual",
  "file_list": [],
  "node_id": "optional_node_id"
}
```

Key fields:
- `type`: Message type (data, ping, disconnect, connect)
- `args`: Task parameters including the goal
- `agent`: Agent type to use (if applicable)
- `mode`: Execution mode (auto or manual)
- `file_list`: List of uploaded files for the task
- `node_id`: Optional ID for specific node responses

Sources: [XAgentWeb/src/views/playground/chat.vue:414-434](), [XAgentServer/application/websockets/base.py:206-270]()

### Server to Client Messages

Messages sent from the server to the client follow this structure:

```json
{
  "status": "connect|start|inner|subtask_submit|refinement|subtask|finished|failed|pong",
  "success": true,
  "message": "Status message",
  "data": {},
  "current": "current_step",
  "node_id": "node_id",
  "workspace_file_list": []
}
```

Key fields:
- `status`: Current status of the task execution
- `success`: Whether the operation was successful
- `message`: Descriptive message about the status
- `data`: Detailed data about the current step
- `current`: Current execution step
- `node_id`: ID of the current node
- `workspace_file_list`: List of files in the workspace

Sources: [XAgentServer/application/websockets/base.py:368-376](), [XAgentWeb/src/views/playground/chat.vue:334-410]()

## WebSocket Message Flow

The communication flow between the client and server during task execution:

```mermaid
sequenceDiagram
    participant Client as "XAgentWeb Client"
    participant Server as "XAgentServer"
    participant XAgent as "XAgent Core"
    participant DB as "Database"
    
    Client->>Server: Connect WebSocket
    Server->>Client: Connection Established
    
    Client->>Server: {"type": "data", "args": {"goal": "..."}}
    Server->>DB: Store Interaction Parameters
    
    alt New Interaction
        Server->>DB: Initialize Interaction Record
        Server->>DB: Insert Raw Data
        Server->>Client: {"status": "start", ...}
    else Continuing Interaction
        Server->>DB: Update Human Input Data
        Server->>Redis: Set Receive Flag
    end
    
    Note over Server: Start Scheduler for Sending Updates
    
    Server->>XAgent: Start Task Processing
    
    loop Task Execution
        XAgent->>DB: Update Status and Data
        Server->>Client: {"status": "inner", ...}
        Server->>Client: {"status": "subtask", ...}
        
        alt Manual Mode
            Server->>Client: Request Human Input
            Client->>Server: {"type": "data", "args": {"goal": "..."}}
            Server->>XAgent: Forward Human Input
        end
    end
    
    alt Task Completed
        XAgent->>DB: Mark Task as Finished
        Server->>Client: {"status": "finished", ...}
    else Task Failed
        XAgent->>DB: Mark Task as Failed
        Server->>Client: {"status": "failed", "message": "error"}
    end
    
    Client->>Server: {"type": "disconnect"}
    Server->>Client: Close WebSocket
```

Sources: [XAgentServer/application/websockets/base.py:206-270](), [XAgentServer/application/websockets/base.py:344-390](), [XAgentWeb/src/views/playground/chat.vue:334-410]()

## WebSocket Connection Management

### Ping/Pong Mechanism

The WebSocket connection implements a ping/pong mechanism to keep the connection alive:

1. The server sends a pong message every 20 seconds
2. The client responds with a ping message
3. This prevents the connection from timing out

```mermaid
sequenceDiagram
    participant Client as "XAgentWeb Client"
    participant Server as "XAgentServer"
    
    loop Every 20 seconds
        Server->>Client: {"type": "pong"}
        Client->>Server: {"type": "ping"}
    end
```

Sources: [XAgentServer/application/websockets/base.py:338-342](), [XAgentWeb/src/views/playground/chat.vue:354-356]()

### Error Handling

The WebSocket interface includes error handling to manage various failure scenarios:

1. **Authentication Failures**: If user authentication fails, the server sends an error message and closes the connection
2. **Task Execution Failures**: If the task execution fails, the server sends a "failed" status with an error message
3. **Connection Errors**: Client-side connection errors are handled with appropriate UI feedback
4. **Disconnections**: If the client disconnects, the server cleans up resources and marks the interaction as closed

Sources: [XAgentServer/application/websockets/base.py:173-185](), [XAgentWeb/src/views/playground/chat.vue:343-352]()

## Database Integration

The WebSocket interface interacts with several database tables to persist interaction data:

```mermaid
erDiagram
    "interactions" ||--o{ "interaction_parameters" : "has"
    "interactions" ||--o{ "raw" : "contains"
    
    "interactions" {
        int id
        string interaction_id
        string user_id
        string create_time
        string description
        string agent
        string mode
        json file_list
        string status
        string message
        string current_step
    }
    
    "interaction_parameters" {
        int id
        string interaction_id
        string parameter_id
        json args
    }
    
    "raw" {
        int id
        string node_id
        string interaction_id
        string current
        int step
        json data
        json file_list
        string status
        boolean do_interrupt
        boolean ask_for_human_help
        boolean is_send
        boolean is_receive
        json human_data
    }
```

The `interactions` table stores the main interaction metadata, `interaction_parameters` stores the task parameters, and `raw` stores the detailed execution data with step-by-step updates.

Sources: [XAgentServer/database/sql/create_mysql_table.sql:29-88](), [XAgentServer/database/models.py:25-115]()

## Redis State Management

Redis is used to manage the WebSocket connection state and synchronize data between the WebSocket handler and the task execution thread:

1. **Connection Status**: Redis stores the connection status using the key `{client_id}`
2. **Send Flags**: Redis sets `{client_id}_send` when there is data to be sent to the client
3. **Receive Flags**: Redis sets `{client_id}_{node_id}_receive` when data is received from the client
4. **Scheduler Coordination**: The WebSocket handler checks Redis flags to determine what data to send

Sources: [XAgentServer/application/websockets/base.py:92-124](), [XAgentServer/application/websockets/base.py:348-389]()

## Client-Side Implementation

The client-side WebSocket implementation is in the `chat.vue` component of XAgentWeb. Key components include:

1. **Connection Management**: Establishing and maintaining WebSocket connections
2. **Message Handling**: Processing messages from the server and updating the UI
3. **Task Control**: Sending commands to control task execution
4. **Mode Support**: Supporting different interaction modes (auto/manual)
5. **UI Updates**: Updating the UI based on task progress

Sources: [XAgentWeb/src/views/playground/chat.vue:232-481]()

## Server-Side Implementation

The server-side WebSocket implementation is in the `MainServer` class in `base.py`. Key components include:

1. **Connection Handling**: Accepting and validating connections
2. **Message Processing**: Processing client messages and updating the interaction state
3. **Task Execution**: Running XAgent tasks in separate threads
4. **Data Sending**: Sending task updates to the client
5. **State Management**: Managing interaction state using Redis and the database

Sources: [XAgentServer/application/websockets/base.py:57-390]()

## Proxy Configuration

For production deployments, the WebSocket connections are typically proxied through the web server. The Vite development server includes proxy configuration to forward WebSocket connections:

```javascript
server: {
  proxy: {
    '/api': {
      target: loadEnv(mode, process.cwd()).VITE_BACKEND_URL,
      changeOrigin: true,
      rewrite: (path) => path.replace(/\/api/, ''),
    },
    '/workspace': {
      target: loadEnv(mode, process.cwd()).VITE_BACKEND_URL,
      changeOrigin: true
    },
  },
}
```

Sources: [XAgentWeb/vite.config.ts:62-74]()

This configuration ensures that WebSocket connections from the web client are correctly routed to the XAgentServer backend.

---

# Page: Database Integration

# Database Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgent/recorder.py](XAgent/recorder.py)
- [XAgentServer/README.md](XAgentServer/README.md)
- [XAgentServer/README_zh.md](XAgentServer/README_zh.md)
- [XAgentServer/database/__init__.py](XAgentServer/database/__init__.py)
- [XAgentServer/database/change/change_desc.sql](XAgentServer/database/change/change_desc.sql)
- [XAgentServer/database/connect.py](XAgentServer/database/connect.py)
- [XAgentServer/server.py](XAgentServer/server.py)
- [docker-compose.yml](docker-compose.yml)

</details>



This page documents the database integration in XAgent, explaining how persistent data storage and session management are implemented. XAgent uses MySQL for long-term data storage and Redis for ephemeral session management. For information about the WebSocket interface that communicates with these databases, see [WebSocket Interface](#4.2).

## Database Architecture Overview

XAgent employs a dual-database approach for different persistence needs:

```mermaid
graph TD
    subgraph "XAgentServer"
        XAS["XAgentServer"]
        XA["XAgent Core"]
    end
    
    subgraph "Database Systems"
        MySQL[("MySQL Database")]
        Redis[("Redis Database")]
    end
    
    XAS -->|"Stores interactions\nuser data"| MySQL
    XAS -->|"Manages sessions\nstate tracking"| Redis
    XA -->|"Records execution logs\ntool calls"| MySQL
    
    subgraph "Primary Tables"
        interactions[("interactions")]
        shared_interactions[("shared_interactions")]
        running_records[("running_records")]
    end
    
    MySQL --- interactions
    MySQL --- shared_interactions
    MySQL --- running_records
```

Sources:
- [docker-compose.yml:66-94]()
- [XAgentServer/README.md:25-27]()

## Connection Management

### MySQL Connection

The MySQL database connection is managed through SQLAlchemy ORM. The connection is defined in `XAgentServer/database/connect.py`:

```mermaid
flowchart LR
    env["Environment Variable\nMYSQL_DB_URL"] -->|"Falls back to"| default["Default URL\nXAgentServerEnv.DB.db_url"]
    default -->|"Configures"| engine["SQLAlchemy Engine"]
    engine -->|"Creates"| session_factory["SessionLocal"]
    session_factory -->|"Produces"| db_session["Database Session"]
    engine -->|"Creates schema via"| base["SQLAlchemy Base"]
```

The engine is configured with connection pooling for efficiency:

```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_size=10, 
    max_overflow=2, 
    pool_timeout=3600, 
    pool_recycle=7200
)
```

A context manager pattern is used to ensure proper session handling:

```python
@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
```

Sources:
- [XAgentServer/database/connect.py:1-20]()
- [XAgent/recorder.py:32-45]()

### Redis Connection

Redis connection is configured through environment variables and used primarily by XAgentServer for session management:

```
REDIS_HOST=xagent-redis
```

Sources:
- [docker-compose.yml:54]()

## Data Flow

The following sequence diagram illustrates the data flow between system components and databases:

```mermaid
sequenceDiagram
    participant Client as "Web Client"
    participant XAS as "XAgentServer"
    participant XA as "XAgent Core"
    participant MySQL as "MySQL DB"
    participant Redis as "Redis DB"
    
    Client->>XAS: Connect via WebSocket
    XAS->>Redis: Create session
    Client->>XAS: Submit task
    XAS->>MySQL: Create interaction record
    XAS->>XA: Initialize XAgent with task
    
    loop Task Execution
        XA->>MySQL: Record LLM interactions
        XA->>MySQL: Record tool calls
        XA->>MySQL: Record plan refinements
        XA->>XAS: Send progress updates
        XAS->>Redis: Update task state
        XAS->>Client: Send updates via WebSocket
    end
    
    XA->>MySQL: Record task completion
    XAS->>Redis: Update session state
```

Sources:
- [XAgentServer/server.py:27-109]()
- [XAgent/recorder.py:48-346]()

## MySQL Schema

The primary tables in the MySQL database are:

```mermaid
classDiagram
    class XAgentRunningRecord {
        +String record_id
        +String current
        +Integer node_id
        +String node_type
        +JSON data
        +DateTime create_time
        +DateTime update_time
        +Boolean is_deleted
    }
    
    class Interaction {
        +String interaction_id
        +String user_id
        +String title
        +Text description
        +String status
        +DateTime start_time
        +DateTime finish_time
        +String record_id
    }
    
    class SharedInteraction {
        +String share_id
        +String interaction_id
        +String title
        +Text description
        +String status
        +DateTime start_time
        +DateTime finish_time
        +String record_id
    }
    
    Interaction --> XAgentRunningRecord: references
    SharedInteraction --> Interaction: references
```

The schema evolves over time as needed. For example, a modification was made to extend the description field:

```sql
-- Changed the description field from Varchar(255) to Text
alter table shared_interactions modify `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'description / 描述';
alter table interactions modify `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'description / 描述';
```

Sources:
- [XAgentServer/database/change/change_desc.sql:1-4]()
- [XAgent/recorder.py:96-105]()

## Record Types

The system records various types of data, defined in the `RecorderTypeEnum`:

```mermaid
graph TD
    subgraph "RecorderTypeEnum"
        QUERY["QUERY"]
        CONFIG["CONFIG"]
        LLM["LLM_INPUT_PAIR"]
        TOOL_SERVER["TOOL_SERVER_PAIR"]
        TOOL_CALL["TOOL_CALL"]
        PLAN_REFINE["PLAN_REFINE"]
    end
    
    RunningRecords[("running_records table")] --- QUERY
    RunningRecords --- CONFIG
    RunningRecords --- LLM
    RunningRecords --- TOOL_SERVER
    RunningRecords --- TOOL_CALL
    RunningRecords --- PLAN_REFINE
    
    QUERY --> QueryData["User task & plan"]
    CONFIG --> ConfigData["XAgent configuration"]
    LLM --> LLMData["LLM requests & responses"]
    TOOL_SERVER --> ToolServerData["API calls to ToolServer"]
    TOOL_CALL --> ToolCallData["Tool executions"]
    PLAN_REFINE --> PlanRefineData["Plan modifications"]
```

Each record type stores specific information:

| Record Type | Description | Key Data Elements |
|-------------|-------------|------------------|
| QUERY | User query information | Task description, role name, plan |
| CONFIG | System configuration | API keys, model settings, parameters |
| LLM_INPUT_PAIR | LLM interaction | Input messages, functions, output response |
| TOOL_SERVER_PAIR | Tool server API calls | URL, payload, response, status code |
| TOOL_CALL | Tool execution | Tool name, input, output, status |
| PLAN_REFINE | Plan modifications | Function name, inputs, outputs, new plan |

Sources:
- [XAgent/recorder.py:107-242]()
- [XAgent/recorder.py:271-317]()

## Recording Process

The `RunningRecoder` class in `XAgent/recorder.py` handles data persistence:

```mermaid
flowchart TD
    subgraph "XAgent Components"
        LLM["LLM Interface"]
        ToolServer["Tool Server Interface"]
        PlanRefine["Plan Refiner"]
    end
    
    subgraph "Recording System"
        Recorder["RunningRecorder"]
        GenRecord["generate_record()"]
    end
    
    subgraph "Database Access"
        GetDB["get_db() context"]
        CRUD["RunningRecordCRUD"]
        MySQL[("MySQL Database")]
    end
    
    LLM -->|"regist_llm_inout()"| Recorder
    ToolServer -->|"regist_tool_server()"| Recorder
    PlanRefine -->|"regist_plan_modify()"| Recorder
    
    Recorder -->|"Creates record"| GenRecord
    GenRecord -->|"Returns record"| Recorder
    Recorder -->|"Opens DB session"| GetDB
    GetDB -->|"Provides session"| CRUD
    CRUD -->|"insert_record()"| MySQL
```

The recording process involves these steps:

1. A component calls a registration method (`regist_*`) on the `RunningRecoder`
2. The recorder creates an `XAgentRunningRecord` object with appropriate data
3. A database session is obtained using the `get_db()` context manager
4. The record is inserted via `RunningRecordCRUD.insert_record()`
5. The transaction is committed when the context manager exits

Sources:
- [XAgent/recorder.py:82-105]()
- [XAgent/recorder.py:132-161]()
- [XAgent/recorder.py:214-242]()

## Database Deployment

The databases are deployed as Docker containers with specific configurations:

### MySQL Container Configuration

```yaml
xagent-mysql:
  image: mysql
  command:
    - --default-authentication-plugin=caching_sha2_password
    - --character-set-server=utf8mb4
    - --collation-server=utf8mb4_unicode_ci
  environment:
    MYSQL_ROOT_PASSWORD: xagent
  ports:
    - "3306:3306"
  volumes:
    - ./XAgentServer/database/sql:/docker-entrypoint-initdb.d
  healthcheck:
    test: ["CMD-SHELL", "mysql -h localhost -u root -pxagent -e 'SELECT 1'"]
    timeout: 20s
    retries: 20
```

### Redis Container Configuration

```yaml
xagent-redis:
  image: redis
  ports:
    - "6379:6379"
  command: redis-server --requirepass xagent
  healthcheck:
    test: [ "CMD", "redis-cli", "ping" ]
    interval: 5s
    timeout: 3s
    retries: 20
```

These configurations are defined in the `docker-compose.yml` file and linked to the XAgentServer through environment variables.

Sources:
- [docker-compose.yml:66-94]()
- [docker-compose.yml:53-54]()

## Data Access Patterns

### Querying Cached Data

The `RunningRecoder` provides methods to retrieve previously recorded data:

- `query_llm_inout`: Retrieves cached LLM interactions to avoid redundant API calls
- `query_tool_server_cache`: Retrieves cached tool server responses
- `get_query`: Retrieves the original user query
- `get_config`: Retrieves the system configuration

Example from `query_tool_server_cache`:

```python
def query_tool_server_cache(self, url, payload):
    if self.newly_start:
        return None
    
    if not self.tool_server_cache:
        with get_db() as db:
            tool_record = RunningRecordCRUD.get_record_by_type(
                db=db,
                record_id=self.record_id,
                node_id=0,
                node_type=RecorderTypeEnum.TOOL_SERVER_PAIR,
            )
        self.tool_server_cache = [json.loads(record.data) for record in tool_record]
    
    for cache in self.tool_server_cache:
        if cache["url"] == url.split("/")[-1] and cache["payload"] == dump_common_things(payload):
            return cache["tool_output"]
    
    return None
```

### Loading Previous Sessions

The `load_from_db` method loads all previous records for a given record ID:

```python
def load_from_db(self, record_id):
    self.newly_start = False
    
    with get_db() as db:
        records = RunningRecordCRUD.get_record_by_type(
            db=db,
            record_id=record_id
        )
    
    for record in records:
        if record.node_type == RecorderTypeEnum.QUERY:
            self.query = AutoGPTQuery.from_json(record.data)
        elif record.node_type == RecorderTypeEnum.CONFIG:
            # Load configuration
        # Load other record types...
```

This enables resuming previous interactions or replaying recorded sessions.

Sources:
- [XAgent/recorder.py:163-184]()
- [XAgent/recorder.py:245-268]()
- [XAgent/recorder.py:319-346]()

## XAgentServer Integration with Databases

In the XAgentServer component, the database integration is used for:

1. Storing interaction metadata (title, description, status)
2. Managing user sessions and authentication
3. Recording the full history of interactions for later retrieval
4. Managing uploaded files and their relationships to interactions

The XAgentServer connects to the databases using the environment variables specified in the Docker configuration:

```
MYSQL_DB_URL=mysql+pymysql://root:xagent@xagent-mysql:3306/xagent
REDIS_HOST=xagent-redis
```

Sources:
- [XAgentServer/server.py:11-14]()
- [docker-compose.yml:53-54]()

---

# Page: XAgentWeb

# XAgentWeb

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgentWeb/src/views/playground/chat.vue](XAgentWeb/src/views/playground/chat.vue)
- [XAgentWeb/src/views/playground/components/HistorySidebar.vue](XAgentWeb/src/views/playground/components/HistorySidebar.vue)
- [XAgentWeb/src/views/playground/index.vue](XAgentWeb/src/views/playground/index.vue)
- [XAgentWeb/src/views/playground/share.vue](XAgentWeb/src/views/playground/share.vue)
- [XAgentWeb/vite.config.ts](XAgentWeb/vite.config.ts)

</details>



XAgentWeb is the web-based user interface component of the XAgent system, providing a user-friendly way to interact with the autonomous agent capabilities. It serves as the frontend application that communicates with XAgentServer via WebSockets to execute tasks, manage files, and display agent interactions.

For information about the server component that XAgentWeb communicates with, see [XAgentServer](#4).

## Architecture Overview

XAgentWeb is built using Vue.js, with Vite as the build tool. It follows a component-based architecture with central state management using Pinia stores.

### Position in XAgent Ecosystem

```mermaid
graph LR
    User["User"] --> |"interacts with"| XAgentWeb["XAgentWeb"]
    XAgentWeb --> |"WebSocket communication"| XAgentServer["XAgentServer"]
    XAgentServer --> |"orchestrates"| XAgentCore["XAgent Core"]
    XAgentCore --> |"uses"| ToolServer["ToolServer"]
    
    classDef current fill:#f9f,stroke:#333,stroke-width:2px
    class XAgentWeb current
```

Sources: [XAgentWeb/vite.config.ts:1-94]()

### Component Architecture

```mermaid
graph TD
    subgraph "XAgentWeb"
        Router["Vue Router"] --> |"routes to"| Playground["Playground View"]
        Playground --> |"contains"| HistorySidebar["History Sidebar"]
        Playground --> |"shows"| Chat["Chat Interface"]
        Playground --> |"or"| NewTalk["New Talk Setup"]
        Playground --> |"or"| Share["Shared Conversations"]
        
        Chat --> |"uses"| Tab["Task Tab Component"]
        Chat --> |"uses"| WorkSpace["Workspace Component"]
        
        Pinia["Pinia Stores"] --> |"provides state to"| Chat
        Pinia --> |"provides state to"| HistorySidebar
        Pinia --> |"provides state to"| NewTalk
        Pinia --> |"provides state to"| Share
    end
    
    XAgentWeb --> |"WebSocket"| Server["XAgentServer"]
```

Sources: [XAgentWeb/src/views/playground/chat.vue:1-847](), [XAgentWeb/src/views/playground/components/HistorySidebar.vue:1-598](), [XAgentWeb/src/views/playground/index.vue:1-139]()

## WebSocket Communication

XAgentWeb communicates with XAgentServer via WebSockets, which enable real-time communication and updates during task execution.

### WebSocket Connection Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Web as XAgentWeb
    participant Server as XAgentServer
    participant XAgent as XAgent Core
    
    User->>Web: Enter task and settings
    Web->>Server: Establish WebSocket connection
    Note over Web,Server: Connection endpoints:<br>/ws/base/ (new talk)<br>/ws/replay/ (playback)<br>/ws/recorder/ (recorder)<br>/ws/share/ (shared)
    
    Server->>Web: Connection established
    Web->>Server: Send task parameters
    Note over Web,Server: Includes:<br>- goal (task description)<br>- agent type<br>- mode (auto/manual)<br>- file list
    
    Server->>XAgent: Initialize task
    Server->>Web: Send "start" status
    
    loop Task Execution
        XAgent->>Server: Execute subtask
        Server->>Web: Send subtask updates
        Web->>User: Display execution progress
        
        alt Manual Mode
            User->>Web: Provide input
            Web->>Server: Send user input
            Server->>XAgent: Forward input
        end
    end
    
    XAgent->>Server: Task completed
    Server->>Web: Send "finished" status
    Web->>User: Display results
```

Sources: [XAgentWeb/src/views/playground/chat.vue:231-511]()

### WebSocket Message Handling

The WebSocket communication is managed in the chat component, which handles various message types:

1. **Connection Messages**:
   - `connect`: Initializes the connection
   - `ping`/`pong`: Keeps connection alive

2. **Task Status Messages**:
   - `start`: Task initialization
   - `inner`: Inner node execution
   - `subtask_submit`: Submitting subtask results
   - `refinement`: Task refinement
   - `subtask`: Next subtask execution
   - `finished`: Task completion
   - `failed`: Task failure

3. **Workspace Messages**:
   - File list updates
   - Node ID updates

Sources: [XAgentWeb/src/views/playground/chat.vue:333-411]()

## User Interface Components

XAgentWeb provides several key interface components for interacting with the XAgent system.

### Main Layout

The main layout consists of:

1. History sidebar (left)
2. Main content area (center)
3. Input/workspace area (bottom)

Each area serves a specific purpose in facilitating user interaction with the agent.

Sources: [XAgentWeb/src/views/playground/chat.vue:1-51](), [XAgentWeb/src/views/playground/components/HistorySidebar.vue:1-147]()

### History Sidebar

The history sidebar displays previous conversations and provides navigation options:

```mermaid
graph TD
    HistorySidebar["History Sidebar"] --> Logo["Logo"]
    HistorySidebar --> NewTalk["New Talk Button"]
    HistorySidebar --> HistoryList["History List"]
    HistorySidebar --> Settings["Settings Dropdown"]
    
    HistoryList --> HistoryItem["History Items"]
    HistoryItem --> PlaybackButton["Playback Button"]
    HistoryItem --> DeleteButton["Delete Button"]
    
    Settings --> Blog["Blog Link"]
    Settings --> Community["Community Link"]
    Settings --> Logout["Logout Option"]
```

The sidebar provides:
- Creation of new conversations
- Access to conversation history
- Playback of previous conversations
- Account and system settings

Sources: [XAgentWeb/src/views/playground/components/HistorySidebar.vue:1-147]()

### Chat Interface

The chat interface displays the conversation between the user and XAgent:

```mermaid
graph TD
    ChatInterface["Chat Interface"] --> MessageList["Message List"]
    ChatInterface --> WorkspacePanel["Workspace Panel"]
    
    MessageList --> UserMessage["User Message"]
    MessageList --> AgentMessage["Agent Message"]
    
    AgentMessage --> TaskTab["Task Tab Component"]
    TaskTab --> PlanDisplay["Plan Display"]
    TaskTab --> SubtaskExecution["Subtask Execution"]
    TaskTab --> ToolExecution["Tool Execution"]
    
    WorkspacePanel --> FileList["File List"]
    WorkspacePanel --> FileContent["File Content"]
```

The chat interface includes:
- User messages
- Agent responses
- Task execution display
- Workspace file management

Sources: [XAgentWeb/src/views/playground/chat.vue:1-51](), [XAgentWeb/src/views/playground/chat.vue:51-84]()

## Task Execution Modes

XAgentWeb supports several task execution modes:

| Mode | Description | WebSocket Endpoint |
|------|-------------|-------------------|
| New Talk | Starting a new conversation | `/ws/base/` |
| Playback | Replaying a previous conversation | `/ws/replay/` |
| Recorder | Recording a conversation | `/ws/recorder/` |
| Shared | Running a shared conversation | `/ws/share/` |

Each mode follows a different initialization process but uses the same underlying WebSocket communication protocol.

### Auto vs. Manual Mode

XAgentWeb supports two execution modes:
- **Auto Mode**: The agent executes the entire task automatically
- **Manual Mode**: The user must approve each subtask execution

The mode is selected during task configuration and affects how the task is executed.

Sources: [XAgentWeb/src/views/playground/chat.vue:213-225](), [XAgentWeb/src/views/playground/index.vue:26-42]()

## Workspace Integration

XAgentWeb includes a workspace panel for managing files:

1. **File Upload**: Users can upload files to be used by the agent
2. **File Management**: Files can be viewed and managed in the workspace panel
3. **File List**: The agent can access and modify workspace files

The workspace is collapsed by default but can be expanded to view and manage files.

Sources: [XAgentWeb/src/views/playground/chat.vue:51-84](), [XAgentWeb/src/views/playground/index.vue:1-15]()

## Community Features

XAgentWeb includes features for community interaction:

### Shared Conversations

The share view displays conversations shared by community members:

```mermaid
graph TD
    ShareView["Share View"] --> Header["Header"]
    ShareView --> Pagination["Pagination"]
    ShareView --> ConversationsList["Conversations List"]
    
    ConversationsList --> ConversationCard["Conversation Card"]
    ConversationCard --> CardHeader["Header Info"]
    ConversationCard --> TaskDescription["Task Description"]
    ConversationCard --> Creator["Creator Info"]
    ConversationCard --> RunButton["Run Button"]
```

Users can:
- Browse shared conversations
- View conversation details
- Run shared conversations

Sources: [XAgentWeb/src/views/playground/share.vue:1-461]()

## Technical Implementation

### State Management

XAgentWeb uses Pinia stores for state management:

1. **TaskStore**: Manages task execution state
2. **ConfigStore**: Manages configuration settings
3. **HistoryTalkStore**: Manages conversation history
4. **UserStore**: Manages user information

Stores provide centralized state management for components.

Sources: [XAgentWeb/src/views/playground/chat.vue:100-104](), [XAgentWeb/src/views/playground/components/HistorySidebar.vue:162-166]()

### Build Configuration

XAgentWeb uses Vite as the build tool with the following configuration:

- Vue plugin for Vue components
- React plugin for React components
- Auto-import for Vue components
- Element Plus UI library
- Icon resolver for icons
- HTML plugin for HTML generation
- Proxy configuration for API requests

The build process is optimized for production with minification and compression.

Sources: [XAgentWeb/vite.config.ts:1-94]()

## API Integration

XAgentWeb communicates with the backend API through:

1. **WebSocket**: For real-time communication during task execution
2. **HTTP API**: For user authentication, history management, and file operations

API endpoints include:
- User authentication
- Conversation history retrieval
- File management
- Shared conversations

The backend URL is configured in the environment variables and used for API requests.

Sources: [XAgentWeb/vite.config.ts:62-73](), [XAgentWeb/src/views/playground/chat.vue:234-238]()

---

# Page: User Interface Components

# User Interface Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgentWeb/README.md](XAgentWeb/README.md)
- [XAgentWeb/package.json](XAgentWeb/package.json)
- [XAgentWeb/src/views/playground/components/FileUpload.vue](XAgentWeb/src/views/playground/components/FileUpload.vue)
- [XAgentWeb/src/views/playground/components/HistorySidebar.vue](XAgentWeb/src/views/playground/components/HistorySidebar.vue)
- [XAgentWeb/src/views/playground/components/Inferencing.vue](XAgentWeb/src/views/playground/components/Inferencing.vue)
- [XAgentWeb/src/views/playground/components/Setting.vue](XAgentWeb/src/views/playground/components/Setting.vue)
- [XAgentWeb/src/views/playground/index.vue](XAgentWeb/src/views/playground/index.vue)
- [XAgentWeb/src/views/playground/share.vue](XAgentWeb/src/views/playground/share.vue)

</details>



This page documents the user interface components of XAgentWeb, the web frontend for the XAgent system. XAgentWeb provides a browser-based interface for users to interact with XAgent, configure settings, upload files, and view task execution progress. For information about WebSocket communication with the server, see [WebSocket Interface](#4.2).

## Overview of XAgentWeb Architecture

XAgentWeb is built using Vue.js and communicates with XAgentServer via WebSockets. The interface consists of several key components that work together to provide a cohesive user experience.

```mermaid
graph TD
    User["User"] --> XAgentWeb["XAgentWeb Interface"]
    
    XAgentWeb --> PlaygroundView["PlaygroundView (index.vue)"]
    XAgentWeb --> ShareView["ShareView (share.vue)"]
    
    PlaygroundView --> HistorySidebar["HistorySidebar.vue"]
    PlaygroundView --> Setting["Setting.vue"]
    PlaygroundView --> FileUpload["FileUpload.vue"]
    PlaygroundView --> TalkInput["TalkInput.vue"]
    PlaygroundView --> Inferencing["Inferencing.vue"]
    
    PlaygroundView --WebSocket--> XAgentServer["XAgentServer"]
    XAgentServer --> XAgentCore["XAgent Core"]
```

Sources: [XAgentWeb/src/views/playground/index.vue:1-138](), [XAgentWeb/src/views/playground/components/HistorySidebar.vue:1-597](), [XAgentWeb/src/views/playground/components/FileUpload.vue:1-203](), [XAgentWeb/src/views/playground/components/Setting.vue:1-302](), [XAgentWeb/src/views/playground/components/Inferencing.vue:1-354](), [XAgentWeb/src/views/playground/share.vue:1-460]()

## Main View Components

### Playground View

The Playground view (`index.vue`) is the main interface where users interact with XAgent. It organizes the various UI components and handles their interactions.

```mermaid
graph TD
    PlaygroundView["PlaygroundView (index.vue)"]
    
    PlaygroundView --> ConfigCards["config-cards div"]
    PlaygroundView --> InputBorder["input-border div"]
    
    ConfigCards --> SettingComponent["Setting (settingChange)"]
    ConfigCards --> FileUploadComponent["FileUpload"]
    
    InputBorder --> TalkInputComponent["TalkInput (sendMessage)"]
    InputBorder --> DisclaimerWarning["warning div (disclaimer)"]
    
    SettingComponent --> UseTaskStore["useTaskStore()"]
    SettingComponent --> UseConfigStore["useConfigStore()"]
    
    TalkInputComponent --> RouterPush["router.push('/newtalk')"]
```

The Playground view:
- Imports and renders Setting, FileUpload, and TalkInput components
- Manages task configuration through the `settingChange` method
- Initializes chat preparation via the `useInitChatPreparation` API call
- Handles message sending with validation through the `sendMessage` method
- Routes to the actual conversation view upon sending a valid message

Sources: [XAgentWeb/src/views/playground/index.vue:1-138]()

### History Sidebar

The History Sidebar (`HistorySidebar.vue`) displays past conversations and provides navigation and management functions.

```mermaid
graph TD
    HistorySidebar["HistorySidebar.vue"]
    
    HistorySidebar --> Logo["logo_name_border div"]
    HistorySidebar --> NewTalk["new-talk div (createNewTalk)"]
    HistorySidebar --> HistoryList["history-list div"]
    HistorySidebar --> SettingsDropdown["el-dropdown (handleCommand)"]
    
    HistoryList --> HistoryItems["history-item div (v-for)"]
    HistoryItems --> ConvTitle["ellipsis span (switchToConversation)"]
    HistoryItems --> PlaybackButton["playback-icon span (playbackItem)"]
    HistoryItems --> DeleteButton["delete_btn span (deleteHistory)"]
    
    SettingsDropdown --> BlogOption["Blog (handleCommand('blog'))"]
    SettingsDropdown --> CommunityOption["Community (handleCommand('community'))"]
    SettingsDropdown --> LogoutOption["Logout (handleCommand('logout'))"]
    
    HistorySidebar --> UseHistoryTalkStore["useHistoryTalkStore()"]
    HistorySidebar --> UseUserStore["useUserStore()"]
    HistorySidebar --> UseAuthStore["useAuthStore()"]
```

The History Sidebar:
- Displays the XAgent logo and a "New Talk" button
- Lists previous conversations with playback and delete options
- Provides a settings dropdown with links to blog, community, and logout option
- Fetches conversation history via the `queryHistoryData` method and `useHistoryListRequest` API call

Sources: [XAgentWeb/src/views/playground/components/HistorySidebar.vue:1-597]()

### Setting Component

The Setting component (`Setting.vue`) allows users to configure agent parameters before starting a conversation.

```mermaid
graph TD
    Setting["Setting.vue"]
    
    Setting --> SettingTop["setting_top div"]
    Setting --> ContentSection["content div"]
    
    SettingTop --> Title["title span"]
    SettingTop --> Subtitle["sub_title span"]
    
    ContentSection --> ContentLeft["content-left div"]
    ContentLeft --> AgentRow["row div (agent)"]
    ContentLeft --> ModeRow["row div (mode)"]
    
    AgentRow --> AgentLabel["label span"]
    AgentRow --> AgentSelect["el-select (v-model: agent)"]
    AgentSelect --> AgentOptions["el-option (agentOptions)"]
    
    ModeRow --> ModeLabel["label span"]
    ModeRow --> ModeSelect["el-select (v-model: mode)"]
    ModeSelect --> ModeOptions["el-option (modeOptions)"]
    
    Setting --> EmitSettingChange["emit('settingChange')"]
```

The Setting component:
- Displays a title and subtitle
- Provides dropdowns to select an agent (currently only "XAgent" option)
- Provides mode selection (Auto or Manual)
- Emits a `settingChange` event whenever settings are updated
- Uses the Vue.js `watchEffect` function to monitor changes

Sources: [XAgentWeb/src/views/playground/components/Setting.vue:1-302]()

### File Upload Component

The FileUpload component (`FileUpload.vue`) enables users to upload files for processing by the agent.

```mermaid
graph TD
    FileUpload["FileUpload.vue"]
    
    FileUpload --> UploadWrapper["file-uploader-wrapper div"]
    UploadWrapper --> ElUpload["el-upload"]
    
    ElUpload --> TriggerSlot["template #trigger"]
    ElUpload --> TipSlot["template #tip"]
    
    TriggerSlot --> UploadButton["el-button"]
    TipSlot --> UploadTip["el-upload__tip div"]
    
    ElUpload --> HandleChange["handleChange"]
    ElUpload --> HandlePreview["handlePreview"]
    ElUpload --> HandleRemove["handleRemove"]
    ElUpload --> UploadFile["uploadFile"]
    ElUpload --> HandleSuccess["handleSuccess"]
    
    UploadFile --> FormData["formData"]
    FormData --> AxiosPost["axios.post(url, formData)"]
    AxiosPost --> ConfigStoreAddFiles["configStore.addFiles"]
```

The FileUpload component:
- Provides a file upload button with Element Plus `el-upload` component
- Supports multiple file formats (.txt, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .png, .jpeg, .gif, .py, .zip)
- Limits uploads to 5 files of up to 1MB each
- Handles file validation, upload, removal, and preview
- Uses axios to send files to the server via POST request
- Updates the config store with uploaded files

Sources: [XAgentWeb/src/views/playground/components/FileUpload.vue:1-203]()

### Inferencing Component

The Inferencing component (`Inferencing.vue`) displays the agent's thinking process during task execution.

```mermaid
graph TD
    Inferencing["Inferencing.vue"]
    
    Inferencing --> InferBorder["infer-border div"]
    
    InferBorder --> ThoughtsSection["row div (thoughts)"]
    InferBorder --> ReasoningSection["row div (reasoning)"]
    InferBorder --> PlanSection["row div (plan)"]
    InferBorder --> CriticismSection["row div (criticism)"]
    InferBorder --> SubtaskSubmitInfo["subtask-submit-info div"]
    InferBorder --> RunButton["el-button (runToNextNode)"]
    
    ThoughtsSection --> ThoughtsLabel["key-name-label span"]
    ThoughtsSection --> ThoughtsInput["el-input/read-only-input"]
    
    SubtaskSubmitInfo --> ToolsTitle["end-subtask-info-title div"]
    SubtaskSubmitInfo --> SubmitSubtaskInfo["SubmitSubtaskInfo component"]
    
    Inferencing --> TaskStore["useTaskStore()"]
    Inferencing --> HistoryTalkStore["useHistoryTalkStore()"]
```

The Inferencing component:
- Displays the agent's thoughts, reasoning, plan, and criticism
- Shows tools being used by the agent
- Provides a RUN button in manual mode to proceed to the next step
- Allows editing of the agent's thoughts in manual mode
- Emits events to coordinate with other components

Sources: [XAgentWeb/src/views/playground/components/Inferencing.vue:1-354]()

### Share View

The Share view (`share.vue`) displays conversations shared by the community.

```mermaid
graph TD
    ShareView["share.vue"]
    
    ShareView --> MainPageContainer["main-page-container div"]
    MainPageContainer --> MainPageWrapper["main-page-wrapper div"]
    
    MainPageWrapper --> Title["h3 (Conversations Shared...)"]
    MainPageWrapper --> Pagination["el-pagination"]
    MainPageWrapper --> ConversationsListWrapper["conversations-list-wrapper div"]
    
    ConversationsListWrapper --> ConversationItems["history-item div (v-for)"]
    ConversationItems --> HeaderInfoRow["header-info-row div"]
    ConversationItems --> ConversationTitle["ellipsis span"]
    ConversationItems --> FooterInfoRow["footer-info-row div"]
    ConversationItems --> ActionButtons["delete_btn div"]
    
    ActionButtons --> PlaybackButton["playback-icon span (runSharedItem)"]
    
    ShareView --> GetSharedData["getSharedData"]
    GetSharedData --> UseSharedConvsRequest["useSharedConvsRequest"]
    UseSharedConvsRequest --> HistoryTalkStore["chatMsgInfoStore.setSharedArr"]
```

The Share view:
- Displays a grid of conversations shared by the community
- Shows agent/mode information, conversation goal, and creator
- Provides a playback button to view shared conversations
- Includes pagination for navigating through shared conversations
- Fetches shared conversations via the `getSharedData` method and `useSharedConvsRequest` API call

Sources: [XAgentWeb/src/views/playground/share.vue:1-460]()

## State Management and Data Flow

XAgentWeb uses Vue.js stores to manage application state across components. Key stores include:

- `userStore`: Manages user information
- `authStore`: Handles authentication state
- `historyTalkStore`: Manages conversation history
- `taskStore`: Tracks current task execution
- `configStore`: Stores configuration settings

```mermaid
sequenceDiagram
    participant User
    participant PlaygroundView as "index.vue"
    participant Setting as "Setting.vue"
    participant FileUpload as "FileUpload.vue"
    participant TalkInput as "TalkInput.vue"
    participant ConfigStore as "configStore"
    participant TaskStore as "taskStore"
    participant Server as "XAgentServer"
    
    User->>Setting: Select agent & mode
    Setting->>ConfigStore: setNewtalkSettings()
    
    User->>FileUpload: Upload files
    FileUpload->>Server: POST /api/workspace/upload
    Server-->>FileUpload: Response with file list
    FileUpload->>ConfigStore: addFiles()
    
    User->>TalkInput: Enter message
    TalkInput->>PlaygroundView: sendMessage()
    PlaygroundView->>ConfigStore: setNewtalkSettings()
    PlaygroundView->>ConfigStore: setInput()
    PlaygroundView->>+Server: Initialize task
    Server-->>-TaskStore: setCurrentNewTalkId()
    
    PlaygroundView->>User: Navigate to conversation view
```

The data flow in XAgentWeb follows these general steps:

1. User configures agent settings (agent type and mode)
2. User optionally uploads files for processing
3. User enters a task description or message
4. The application sends the configuration, files, and message to XAgentServer
5. XAgentServer processes the task and returns results
6. Results are displayed to the user through the conversation view

Sources: [XAgentWeb/src/views/playground/index.vue:25-52](), [XAgentWeb/src/views/playground/components/FileUpload.vue:88-132](), [XAgentWeb/src/views/playground/components/Setting.vue:165-173]()

## Component Dependency Table

The following table shows the dependencies between XAgentWeb components:

| Component | Dependencies | Stores Used |
|-----------|--------------|------------|
| `index.vue` (Playground) | Setting, FileUpload, TalkInput | taskStore, configStore |
| `HistorySidebar.vue` | ElMessage, ElMessageBox | userStore, authStore, historyTalkStore |
| `Setting.vue` | ElSelect, ElOption | none |
| `FileUpload.vue` | ElUpload, ElButton, ElMessage | configStore, userStore |
| `Inferencing.vue` | ModalInfo, ElMessage, SubmitSubtaskInfo | historyTalkStore, taskStore |
| `share.vue` | ElPagination, ElSkeleton, ElMessage | userStore, historyTalkStore |

Sources: [XAgentWeb/package.json:11-36]()

## User Interaction Flow

The following diagram illustrates the typical user interaction flow through the XAgentWeb interface:

```mermaid
graph LR
    Login["Login"] --> Playground["Playground View"]
    
    Playground --> A["Configure Settings (agent/mode)"]
    Playground --> B["Upload Files (optional)"]
    Playground --> C["Enter Task Description"]
    
    A --> D["Send Task"]
    B --> D
    C --> D
    
    D --> ConversationView["Conversation View"]
    
    ConversationView --> E["View Task Planning"]
    ConversationView --> F["View Task Execution"]
    ConversationView --> G["Provide Input (Manual Mode)"]
    
    E --> Results["View Results"]
    F --> Results
    G --> F
    
    Results --> NewTask["Start New Task"]
    NewTask --> Playground
    
    Playground --> HistoryView["View History (HistorySidebar)"]
    HistoryView --> PlaybackTask["Replay Previous Task"]
    HistoryView --> DeleteTask["Delete Previous Task"]
    
    Playground --> ShareView["Share View"]
    ShareView --> ViewSharedTasks["View Shared Tasks"]
    ViewSharedTasks --> PlaySharedTask["Run Shared Task"]
```

Sources: [XAgentWeb/src/views/playground/index.vue:57-88](), [XAgentWeb/src/views/playground/components/HistorySidebar.vue:173-252](), [XAgentWeb/src/views/playground/share.vue:99-106]()

## Summary

XAgentWeb provides a comprehensive user interface for interacting with the XAgent system. Its components enable users to configure agents, upload files, send tasks, and view execution progress. The UI is designed to be intuitive while providing access to the powerful capabilities of XAgent.

For information about how XAgentWeb communicates with XAgentServer, see [WebSocket Interface](#4.2). For details on file management in the web interface, see [File Upload and Management](#5.5).

---

# Page: Chat Interface

# Chat Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgentWeb/index.html](XAgentWeb/index.html)
- [XAgentWeb/src/composables/useApi.ts](XAgentWeb/src/composables/useApi.ts)
- [XAgentWeb/src/router/index.ts](XAgentWeb/src/router/index.ts)
- [XAgentWeb/src/store/modules/config.ts](XAgentWeb/src/store/modules/config.ts)
- [XAgentWeb/src/views/playground/chat.vue](XAgentWeb/src/views/playground/chat.vue)
- [XAgentWeb/src/views/playground/components/SubmitSubtaskInfo.vue](XAgentWeb/src/views/playground/components/SubmitSubtaskInfo.vue)
- [XAgentWeb/src/views/playground/components/WorkSpace.vue](XAgentWeb/src/views/playground/components/WorkSpace.vue)
- [XAgentWeb/vite.config.ts](XAgentWeb/vite.config.ts)

</details>



This document explains the chat interface component of XAgentWeb, which provides the interactive user interface for communicating with the XAgent autonomous agent system. The chat interface handles WebSocket communication with XAgentServer, displays agent responses, and visualizes task execution progress.

For details about the broader web interface, see [User Interface Components](#5.1). For information about task management specifically, see [Task Management](#5.4).

## 1. Architecture Overview

The chat interface is a key component of XAgentWeb that establishes WebSocket connections with XAgentServer to facilitate real-time communication between users and the XAgent system. It displays both user messages and agent responses, while providing mechanisms for monitoring task execution progress and interacting with generated files.

```mermaid
flowchart TB
    subgraph "XAgentWeb"
        ChatInterface["Chat Interface\n(chat.vue)"]
        TabComponent["Tab Component\n(Tab.vue)"]
        WorkspaceComponent["Workspace Component\n(WorkSpace.vue)"]
        
        ChatInterface --> TabComponent
        ChatInterface --> WorkspaceComponent
    end
    
    subgraph "XAgentServer"
        WebSocketEndpoint["WebSocket Endpoints\n(/ws/base, /ws/replay, /ws/recorder, /ws/share)"]
    end
    
    subgraph "Client Environment"
        Browser["Web Browser"]
    end
    
    subgraph "Data Stores"
        TaskStore["TaskStore\n(Vuex state management)"]
        ConfigStore["ConfigStore\n(Configuration state)"]
        HistoryTalkStore["HistoryTalkStore\n(Message history)"]
    end
    
    Browser --> ChatInterface
    ChatInterface <-->|"WebSocket (status updates, commands)"| WebSocketEndpoint
    ChatInterface <--> TaskStore
    ChatInterface <--> ConfigStore
    ChatInterface <--> HistoryTalkStore
```

Sources: [XAgentWeb/src/views/playground/chat.vue:87-131](), [XAgentWeb/src/router/index.ts:89-98]()

## 2. WebSocket Communication

The chat interface establishes different types of WebSocket connections depending on the interaction mode. The connection is used to send task specifications to the server and receive real-time updates about task execution.

### 2.1. Connection Types

The chat interface supports four types of WebSocket connections, each corresponding to a different interaction mode:

```mermaid
flowchart TD
    ChatInterface["Chat Interface\n(chat.vue)"]
    
    subgraph "WebSocket Connection Types"
        New["New Task Connection\n(/ws/base/)"]
        Playback["Playback Connection\n(/ws/replay/)"]
        Recorder["Recorder Connection\n(/ws/recorder/)"]
        Shared["Shared Task Connection\n(/ws/share/)"]
    end
    
    ChatInterface --> New
    ChatInterface --> Playback
    ChatInterface --> Recorder
    ChatInterface --> Shared
```

Sources: [XAgentWeb/src/views/playground/chat.vue:240-245](), [XAgentWeb/src/views/playground/chat.vue:458-482]()

### 2.2. WebSocket Message Flow

```mermaid
sequenceDiagram
    participant UI as Chat Interface
    participant WS as WebSocket Connection
    participant Server as XAgentServer
    
    UI->>WS: Establish connection based on mode
    Note over UI,WS: newTalkUrl, playbackUrl, recordUrl, or shareUrl
    
    UI->>WS: Send initial data (type: "data" or mode-specific)
    WS->>Server: Forward message
    
    Server->>WS: Send "connect" status
    WS->>UI: Forward message
    UI->>WS: Send connect response (type: "connect")
    
    Server->>WS: Send "start" status with task structure
    WS->>UI: Forward message
    Note over UI: Initialize subtasks in TaskStore
    
    loop Task Execution
        Server->>WS: Send updates (inner, subtask_submit, refinement, subtask)
        WS->>UI: Forward message
        Note over UI: Update UI components via TaskStore
        
        alt Manual Mode
            UI->>WS: Send next subtask command (RunNextSubtask)
            WS->>Server: Forward command
        end
    end
    
    alt Task Completion
        Server->>WS: Send "finished" status
        WS->>UI: Forward message
        UI->>WS: Close connection
        Note over UI: Show completion notification
    else Task Failure
        Server->>WS: Send "failed" status with error message
        WS->>UI: Forward message
        UI->>WS: Close connection
        Note over UI: Show error notification
    end
```

Sources: [XAgentWeb/src/views/playground/chat.vue:333-410](), [XAgentWeb/src/views/playground/chat.vue:425-456]()

## 3. UI Components

The chat interface consists of several key UI components that work together to display the conversation and task execution progress.

### 3.1. Component Structure

```mermaid
flowchart TD
    subgraph "Chat Interface (chat.vue)"
        HistoryList["History List\nDisplays user messages and agent responses"]
        InputBorder["Input Border\nContains workspace toggle and disclaimer"]
        
        subgraph "Tab Component (Tab.vue)"
            PlanInfo["Plan Information\nDisplays task planning"]
            SubtaskList["Subtask List\nDisplays individual subtasks"]
            ToolOutputs["Tool Outputs\nDisplays tool execution results"]
        end
        
        subgraph "WorkSpace Component (WorkSpace.vue)"
            FileList["File List\nDisplays workspace files"]
            FileViewer["File Viewer\nDisplays file contents"]
        end
    end
    
    HistoryList --> Tab
    InputBorder --> WorkSpace
    
    class HistoryList,InputBorder,Tab,WorkSpace,FileList,FileViewer boxnode
```

Sources: [XAgentWeb/src/views/playground/chat.vue:1-84](), [XAgentWeb/src/views/playground/components/WorkSpace.vue:1-49]()

### 3.2. Message Display

The chat interface displays two types of messages:

1. **User Messages**: Displayed with a user avatar and the message content in a white bubble
2. **Agent Responses**: Displayed with the XAgent logo and containing the Tab component that shows task execution details

```mermaid
sequenceDiagram
    participant HistoryList as "History List"
    participant UserMessage as "User Message Bubble"
    participant AgentResponse as "Agent Response (Tab)"
    participant WorkspacePanel as "Workspace Panel"
    
    Note over HistoryList: Conversation flow
    HistoryList->>UserMessage: Display user input
    HistoryList->>AgentResponse: Display agent response
    
    Note over AgentResponse: Contains tabbed interface with:
    Note over AgentResponse: - Plan information
    Note over AgentResponse: - Subtask list
    Note over AgentResponse: - Tool output
    
    HistoryList->>WorkspacePanel: Toggle workspace visibility
    Note over WorkspacePanel: Shows generated files
```

Sources: [XAgentWeb/src/views/playground/chat.vue:9-47]()

## 4. Interaction Modes

The chat interface supports four different interaction modes, each with its own behavior and WebSocket connection type.

### 4.1. Mode Overview

| Mode | Description | WebSocket Endpoint | Auto Mode |
|------|-------------|-------------------|-----------|
| new | Creates a new task | /ws/base/ | Configurable |
| playback | Replays a previous task | /ws/replay/ | Always auto |
| recorder | Plays a recorded task | /ws/recorder/ | Always auto |
| runshared | Runs a shared task | /ws/share/ | Always auto |

Sources: [XAgentWeb/src/views/playground/chat.vue:213-217](), [XAgentWeb/src/views/playground/chat.vue:458-482]()

### 4.2. Mode Selection and Initialization

```mermaid
flowchart LR
    Router["Router\n(router/index.ts)"] --> |"Extracts mode and id from URL"| ChatInterface
    ChatInterface --> |"Sets page mode"| ModeInitialization
    
    subgraph "ModeInitialization"
        New["New Mode\n- Uses user input\n- Configurable auto/manual"]
        Playback["Playback Mode\n- Uses task history\n- Always auto mode"]
        Recorder["Recorder Mode\n- Uses recorder directory\n- Always auto mode"]
        RunShared["RunShared Mode\n- Uses shared task\n- Always auto mode"]
    end
    
    ModeInitialization --> |"Initialize appropriate WebSocket"| WSConnection
```

Sources: [XAgentWeb/src/views/playground/chat.vue:114-146](), [XAgentWeb/src/views/playground/chat.vue:213-225]()

## 5. Message Processing

The chat interface processes different types of WebSocket messages to update the UI and task state.

### 5.1. Message Types and Handling

```mermaid
flowchart TD
    WSMessage["WebSocket Message"] --> MessageHandler["wsMessageHandler()\nProcesses incoming messages"]
    
    MessageHandler --> |"status: start"| InitializeSubtasks["taskStore.initializeSubtasks()\nInitializes task structure"]
    MessageHandler --> |"status: inner"| AddInner["taskStore.addInner()\nAdds inner execution node"]
    MessageHandler --> |"status: subtask_submit"| AddLastInner["taskStore.addLastInner()\nAdds final inner node"]
    MessageHandler --> |"status: refinement"| AddRefinement["taskStore.addRefinementInfo()\nAdds plan refinement info"]
    MessageHandler --> |"status: subtask"| NextSubtask["taskStore.nextsubtask()\nAdvances to next subtask"]
    MessageHandler --> |"status: finished"| HandleFinished["handleTaskCompletelyFinished()\nCompletes task and shows notification"]
    MessageHandler --> |"status: failed"| HandleFailed["handleConnectFailNotification()\nShows error message"]
    MessageHandler --> |"status: connect"| SendConnectResponse["sendConnectResponse()\nSends connection acknowledgment"]
    
    MessageHandler --> |"workspace_file_list property"| UpdateWorkspace["taskStore.setWorkspaceFiles()\nUpdates workspace files"]
    MessageHandler --> |"node_id property"| UpdateNodeId["taskStore.setLastStepId()\nUpdates last step ID"]
```

Sources: [XAgentWeb/src/views/playground/chat.vue:333-410]()

### 5.2. Task Control Flow

In manual mode, the user can control task execution by triggering the next subtask or inner node:

```mermaid
sequenceDiagram
    participant UI as Chat Interface
    participant Tab as Tab Component
    participant WS as WebSocket Connection
    
    UI->>Tab: Render tab with subtasks
    
    alt Manual Mode
        Note over Tab: User clicks "Run" button
        Tab->>UI: RunNextSubtask(data)
        UI->>WS: Send subtask execution request
        
        Note over Tab: User provides input for inner node
        Tab->>UI: RunNextinnerNode(data)
        UI->>WS: Send inner node execution request
    end
```

Sources: [XAgentWeb/src/views/playground/chat.vue:486-510]()

## 6. Workspace Integration

The chat interface includes a workspace panel that displays files generated during task execution. This panel can be toggled on and off by the user.

### 6.1. Workspace UI Components

```mermaid
flowchart TD
    WorkspaceToggle["Workspace Toggle Button\nShows file count badge"] --> WorkspacePanel["Workspace Panel"]
    
    subgraph "WorkspacePanel"
        FileList["File List\nDisplays all workspace files"]
        FileViewer["File Viewer\nDisplays selected file content"]
        
        FileList --> |"Selected file"| FileViewer
    end
    
    subgraph "FileTypeHandlers"
        CodeViewer["Code Viewer\nFor text and code files"]
        NotebookViewer["Python Notebook Viewer\nFor .ipynb files"]
        ImageViewer["Images Viewer\nFor image files"]
    end
    
    FileViewer --> |"File type: unknown"| CodeViewer
    FileViewer --> |"File type: jpt"| NotebookViewer
    FileViewer --> |"File type: img"| ImageViewer
```

Sources: [XAgentWeb/src/views/playground/chat.vue:51-83](), [XAgentWeb/src/views/playground/components/WorkSpace.vue:1-49]()

### 6.2. File Loading Process

When a user selects a file from the workspace file list, the system fetches the file content from the server and displays it in the appropriate viewer based on the file type.

```mermaid
sequenceDiagram
    participant User
    participant WorkSpace as WorkSpace Component
    participant API as useWorkspaceFileRequest API
    participant Server as XAgentServer
    
    User->>WorkSpace: Click on file
    WorkSpace->>WorkSpace: Set current active file
    WorkSpace->>API: Request file content
    API->>Server: Send file request
    Server->>API: Return file content
    API->>WorkSpace: Return file data
    
    alt File is .ipynb
        WorkSpace->>WorkSpace: Set fileWrapper for NotebookViewer
    else File is image
        WorkSpace->>WorkSpace: Prepare image data for ImagesViewer
    else Other file type
        WorkSpace->>WorkSpace: Set viewedCodeStr for CodeViewer
    end
    
    WorkSpace->>User: Display file content in appropriate viewer
```

Sources: [XAgentWeb/src/views/playground/components/WorkSpace.vue:87-111](), [XAgentWeb/src/composables/useApi.ts:98-100]()

## 7. Connection Management

The chat interface carefully manages WebSocket connections to ensure proper communication with the server and prevent resource leaks.

### 7.1. Connection Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    
    Disconnected --> Connecting: RunConnection()
    Connecting --> Connected: ws.onopen
    Connected --> MessageHandling: send initial data
    
    MessageHandling --> MessageHandling: receive and process messages
    MessageHandling --> Disconnecting: Task finished/failed
    MessageHandling --> Disconnecting: User navigates away
    
    Disconnecting --> Disconnected: disConnectWebsocket()
    
    Disconnected --> [*]
```

Sources: [XAgentWeb/src/views/playground/chat.vue:458-483](), [XAgentWeb/src/views/playground/chat.vue:294-298]()

### 7.2. Connection Keep-Alive

To maintain long-running WebSocket connections, the chat interface implements a ping/pong mechanism:

```mermaid
sequenceDiagram
    participant UI as Chat Interface
    participant WS as WebSocket Connection
    participant Server as XAgentServer
    
    UI->>WS: pingKeepAlive() - Send {type: "ping"}
    WS->>Server: Forward ping message
    Server->>WS: Send {type: "pong"}
    WS->>UI: Receive message
    Note over UI: If message.type === "pong", call pingKeepAlive()
```

Sources: [XAgentWeb/src/views/playground/chat.vue:310-312](), [XAgentWeb/src/views/playground/chat.vue:354-356]()

## 8. Error Handling

The chat interface includes robust error handling to address various failure scenarios in the WebSocket communication.

### 8.1. Error Types and Responses

| Error Type | Handling |
|------------|----------|
| Connection establishment failure | Display error message and redirect to playground |
| Server-side task failure | Display error message with details and disconnect |
| Invalid response format | Log error and continue |
| WebSocket error events | Log error and possibly reset state |

Sources: [XAgentWeb/src/views/playground/chat.vue:279-290](), [XAgentWeb/src/views/playground/chat.vue:344-352]()

## 9. Integration with Router

The chat interface integrates with Vue Router to handle different URL patterns for various modes of operation.

```mermaid
flowchart TD
    Router["Vue Router\n(router/index.ts)"] --> |"/playground/chat/:mode?/:id?"| ChatInterface
    
    subgraph "URL Patterns"
        NewTask["/playground/chat/new\nCreate new task"]
        Playback["/playground/chat/playback/:id\nView task history"]
        Recorder["/playground/chat/recorder/:id\nView recorded task"]
        RunShared["/playground/chat/runshared/:id\nRun shared task"]
    end
    
    Router --> NewTask
    Router --> Playback
    Router --> Recorder
    Router --> RunShared
```

Sources: [XAgentWeb/src/router/index.ts:92-98](), [XAgentWeb/src/views/playground/chat.vue:114-140]()

## 10. State Management

The chat interface uses several Vuex stores to manage state across the application:

### 10.1. Store Integration

```mermaid
flowchart LR
    ChatInterface["Chat Interface\n(chat.vue)"] <--> TaskStore["TaskStore\nManages task execution state"]
    ChatInterface <--> ConfigStore["ConfigStore\nManages configuration settings"]
    ChatInterface <--> HistoryTalkStore["HistoryTalkStore\nManages message history"]
    ChatInterface <--> UserStore["UserStore\nManages user information"]
    
    TaskStore --> |"workspaceFiles"| WorkspaceComponent
    TaskStore --> |"subtasks, inners"| TabComponent
    
    ConfigStore --> |"input, newtalkSettings"| ChatInterface
    UserStore --> |"user_id, token"| WebSocketAuth
```

Sources: [XAgentWeb/src/views/playground/chat.vue:102-104](), [XAgentWeb/src/store/modules/config.ts:13-63]()

This comprehensive documentation of the Chat Interface provides a technical understanding of how users interact with the XAgent system through the web interface, how real-time communication is managed via WebSockets, and how task execution is visualized and controlled.

---

# Page: Authentication

# Authentication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [XAgentWeb/.gitignore](XAgentWeb/.gitignore)
- [XAgentWeb/components.d.ts](XAgentWeb/components.d.ts)
- [XAgentWeb/src/components/Business/Feedback/index.vue](XAgentWeb/src/components/Business/Feedback/index.vue)
- [XAgentWeb/src/router/guard/permission.ts](XAgentWeb/src/router/guard/permission.ts)
- [XAgentWeb/src/store/modules/user.ts](XAgentWeb/src/store/modules/user.ts)
- [XAgentWeb/src/utils/throttle.ts](XAgentWeb/src/utils/throttle.ts)
- [XAgentWeb/src/views/exception/mobile.vue](XAgentWeb/src/views/exception/mobile.vue)
- [XAgentWeb/src/views/login/component/ApplyForm.vue](XAgentWeb/src/views/login/component/ApplyForm.vue)
- [XAgentWeb/src/views/login/login.vue](XAgentWeb/src/views/login/login.vue)
- [XAgentWeb/types/talk-type.ts](XAgentWeb/types/talk-type.ts)
- [XAgentWeb/types/user.ts](XAgentWeb/types/user.ts)

</details>



This document details the authentication system within XAgentWeb, covering the login/signup flows, token management, and route protection mechanisms. For information about task management via the web interface, see [Task Management](#5.4).

## Overview

XAgentWeb implements a simple email and token-based authentication system. The core authentication functionality consists of a login page, registration mechanism, persistent token storage, and route guards that restrict access to protected routes. The system distinguishes between regular users and beta users, with some routes exclusively accessible to beta users.

```mermaid
flowchart TD
    User --> LoginPage["Login Page"]
    User --> SignupPage["Signup Form"]
    
    LoginPage -->|"submit credentials"| LoginAPI["Login API"]
    SignupPage -->|"submit registration"| SignupAPI["Signup API"]
    
    LoginAPI -->|"success"| TokenStorage["Token Storage"]
    TokenStorage -->|"persisted in"| LocalStorage["Browser LocalStorage"]
    
    TokenStorage --> RouteGuard["Route Permission Guard"]
    RouteGuard -->|"check token"| ProtectedRoutes["Protected Routes"]
    ProtectedRoutes -->|"beta users only"| BetaRoutes["Beta-Only Routes"]
    ProtectedRoutes -->|"all users"| RegularRoutes["Regular Routes"]
```

Sources: [XAgentWeb/src/views/login/login.vue](), [XAgentWeb/src/router/guard/permission.ts]()

## Authentication Flow

### Login Process

When a user attempts to log in, they provide an email address and token. The login component calls the API to validate these credentials, and upon successful authentication, stores the user information and token in the user and authentication stores.

```mermaid
sequenceDiagram
    participant User
    participant LoginForm as "Login Form"
    participant AuthAPI as "Authentication API"
    participant UserStore as "User Store"
    participant AuthStore as "Auth Store"
    participant Router

    User->>LoginForm: Enter email and token
    LoginForm->>LoginForm: Validate inputs
    LoginForm->>AuthAPI: Submit credentials
    AuthAPI-->>LoginForm: Return auth result

    alt Login Success
        LoginForm->>UserStore: Store user info
        LoginForm->>AuthStore: Set login state
        LoginForm->>AuthStore: Store token
        LoginForm->>Router: Redirect to /playground
    else Login Failure
        LoginForm->>User: Display error message
    end
```

The login form is implemented in [XAgentWeb/src/views/login/login.vue:264-282](), with the form submission logic:

```javascript
const submit = async () => {
  // Validate inputs
  // ...
  
  const param = {
    email: loginForm.email,
    token: loginForm.token,
  }

  const res: any = await useLoginRequest(param);
  
  if (res?.success || res?.message === 'success') {
    userStore.setUserInfo(res?.data)
    authStore.setLoginState(true)
    authStore.setLoginToken(res?.data?.token)

    router.push({ path: '/playground' })
  } else {
    // Handle error
  }
}
```

Sources: [XAgentWeb/src/views/login/login.vue:238-282]()

### Registration Process

The registration process allows new users to sign up by providing personal and professional information. After submission, the system awaits approval before granting full access.

```mermaid
sequenceDiagram
    participant User
    participant SignupForm as "Signup Form"
    participant AuthAPI as "Auth API"
    participant LoginPage as "Login Page"

    User->>SignupForm: Fill registration form
    SignupForm->>SignupForm: Validate inputs
    SignupForm->>AuthAPI: Submit registration
    AuthAPI-->>SignupForm: Return result

    alt Signup Success
        SignupForm->>LoginPage: Show success message
        LoginPage->>User: Display "Review Pending" message
    else Signup Failure
        SignupForm->>User: Display error message
    end
```

The registration form collects the following information:
- Name
- Company/College name
- Industry
- Position
- Email (company or school email)

Sources: [XAgentWeb/src/views/login/component/ApplyForm.vue:7-89](), [XAgentWeb/src/views/login/component/ApplyForm.vue:180-206]()

## Token Management

Authentication tokens are stored in both the AuthStore and local browser storage to maintain session persistence across page reloads. The token is used by route guards to verify authentication status.

```mermaid
flowchart LR
    Login["Login Success"] -->|"token"| AuthStore["Auth Store"]
    AuthStore -->|"persist"| LocalStorage["Local Storage"]
    LocalStorage -->|"retrieve on reload"| AuthStore
    AuthStore -->|"validate"| RouteGuard["Route Guards"]
    RouteGuard -->|"protect"| SecureRoutes["Secure Routes"]
```

Sources: [XAgentWeb/src/store/modules/user.ts:34-37](), [XAgentWeb/src/router/guard/permission.ts:24]()

## Route Protection

The permission guard in the router checks the authentication status before allowing access to protected routes. It handles several scenarios:

1. Mobile device detection and redirection
2. Authentication status verification
3. Beta user status verification for accessing restricted features

For protected routes, the guard checks the user's authentication status and redirects unauthenticated users to the login page. For beta-only features, it checks if the current user has beta access and redirects non-beta users accordingly.

```mermaid
flowchart TD
    RouteChange["Route Change"] --> MobileCheck["Check Device Type"]
    
    MobileCheck -->|"mobile device"| MobilePage["Redirect to Mobile Page"]
    MobileCheck -->|"desktop device"| TokenCheck["Check Authentication Token"]
    
    TokenCheck -->|"token exists"| LoginStateCheck["Check Login State"]
    TokenCheck -->|"no token"| RouteMetaCheck["Check Route Meta"]
    
    LoginStateCheck -->|"is logged in"| BetaCheck["Check Beta Status"]
    LoginStateCheck -->|"not logged in"| ValidateToken["Validate Token"]
    
    ValidateToken -->|"token valid"| BetaCheck
    ValidateToken -->|"token invalid"| LoginRedirect["Redirect to Login"]
    
    RouteMetaCheck -->|"requireAuth=false"| AllowAccess["Allow Access"]
    RouteMetaCheck -->|"requireAuth=true"| LoginRedirect
    
    BetaCheck -->|"is beta user"| AllowAccess
    BetaCheck -->|"not beta & beta-only route"| SharePage["Redirect to Share Page"]
    BetaCheck -->|"not beta & regular route"| AllowAccess
```

Key logic from the route guard:

```javascript
// Check if token exists
const isLogin = authStore.getLoginState
const token = authStore.getToken
const isBetaUser = userInfo?.is_beta === true;

if (token) {
  if (isLogin) {
    // Handle routes based on beta status
  } else {
    // Validate token and handle results
    const loginState = await authStore.checkAuthAction()
  }
} else {
  // Redirect to login for protected routes
  to.path === '/login' ? next() : next('/login')
}
```

Sources: [XAgentWeb/src/router/guard/permission.ts:5-63]()

## User Types and Access Levels

XAgent distinguishes between two types of users:

| User Type | Access Level | Routes Available |
|-----------|--------------|------------------|
| Beta User | Full access  | All routes including `/playground` |
| Regular User | Limited access | Only non-beta routes like `/share` |

The distinction is made based on the `is_beta` flag in the user information object:

```typescript
export interface UserInfo {
  // Other fields...
  is_beta?: boolean
}
```

Sources: [XAgentWeb/types/user.ts:6-25](), [XAgentWeb/src/router/guard/permission.ts:26-36]()

## Implementation Details

### Local Storage for Persistence

User information and authentication tokens are stored in the browser's local storage to maintain session state across page reloads. The user store provides methods to manage this state:

```typescript
// Store user info
setUserInfo(val: UserInfo) {
  this.userInfo = val
  useSetLocalCache<UserInfo>(val, USER_INFO)
}

// Clear user info
clearUserInfo() {
  useClearLocalCache(USER_INFO)
  this.userInfo = null
}
```

Sources: [XAgentWeb/src/store/modules/user.ts:34-41]()

### Guest Account

The system provides a default guest account for development or testing purposes:

```typescript
const DEFAULT_ACCOUNT = 'Guest'
const DEFAULT_PSWD = 'xagent'
```

This is used as the default value in the login form.

Sources: [XAgentWeb/src/views/login/login.vue:131-138]()

## Security Considerations

The authentication system in XAgentWeb is relatively simple and designed primarily for access control rather than high security. Some security considerations:

1. Token-based authentication without apparent expiration
2. Email validation during registration
3. Route-based access control with beta/non-beta user distinction
4. No visible password reset functionality
5. Simple email and token form without multi-factor authentication

For production environments, additional security measures might be considered, such as token expiration, CSRF protection, and more robust user validation.

Sources: [XAgentWeb/src/views/login/login.vue](), [XAgentWeb/src/router/guard/permission.ts]()

---

# Page: Task Management

# Task Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgentWeb/src/store/modules/task.ts](XAgentWeb/src/store/modules/task.ts)
- [XAgentWeb/src/views/playground/components/CodeViewer.vue](XAgentWeb/src/views/playground/components/CodeViewer.vue)
- [XAgentWeb/src/views/playground/components/Tab.vue](XAgentWeb/src/views/playground/components/Tab.vue)
- [XAgentWeb/src/views/playground/layout.vue](XAgentWeb/src/views/playground/layout.vue)

</details>



This page documents how tasks are managed within the XAgentWeb interface of the XAgent system. It covers the core task data structure, state management, and UI components that allow users to create, monitor, and interact with tasks as they are processed by the autonomous agent system.

For information about the web interface components in general, see [User Interface Components](#5.1), and for details about authentication flow, see [Authentication](#5.3).

## Task Data Structure

The Task Management system in XAgentWeb uses a hierarchical structure to represent and track tasks. The core data model is defined in the task store:

```mermaid
classDiagram
    class TaskState {
        subtasks: subtask[]
        current_subtask_index: number
        current_inner_index: number
        currentTaskId: string|null
        currentNewTalkId: string|null
        isCompleted: boolean
        isAutoMode: boolean
        workspaceFiles: any[]
        last_step_id: string|null
    }
    
    class subtask {
        node_id: number|string
        task_id: number|string
        name: string
        goal: string|null
        inner: any[]
        isFinished: boolean
        isRunning: boolean
        refinement: any
        isShowRefinement: boolean
    }
    
    TaskState "1" --o "many" subtask : contains
    subtask "1" --o "many" inner : contains
```

Sources: [XAgentWeb/src/store/modules/task.ts:1-24]()

### Task State Management

The task state is managed through a Pinia store called `useTaskStore`, which maintains the current state of tasks and provides methods for manipulating this state. The store handles:

- The collection of subtasks
- Current indexes for tracking active subtask and inner step
- Task completion status
- Auto/manual execution mode
- Workspace files related to tasks

```mermaid
flowchart LR
    subgraph "TaskStore State"
        A["subtasks[]"] --> B["current_subtask_index"]
        A --> C["current_inner_index"]
        A --> D["isCompleted"]
        A --> E["isAutoMode"]
        A --> F["workspaceFiles[]"]
    end
    
    subgraph "Identifiers"
        G["currentTaskId"]
        H["currentNewTalkId"]
        I["last_step_id"]
    end
    
    TaskStore --> "TaskStore State"
    TaskStore --> "Identifiers"
```

Sources: [XAgentWeb/src/store/modules/task.ts:26-40]()

## Task Management Operations

The task store provides several actions for managing the task lifecycle:

### Task Initialization and Progression

```mermaid
sequenceDiagram
    participant Client
    participant TaskStore as "useTaskStore"
    participant XAgent as "XAgent Core"
    
    Client->>TaskStore: initializeSubtasks(data)
    TaskStore->>TaskStore: Reset indexes
    TaskStore->>TaskStore: Set subtasks
    
    Client->>TaskStore: setCurrentTaskId(id)
    
    Client->>XAgent: runSubtask(query)
    XAgent-->>TaskStore: addInner(data)
    Note over TaskStore: Add step to current subtask
    
    XAgent-->>TaskStore: nextsubtask(data)
    Note over TaskStore: Move to next subtask
    
    XAgent-->>TaskStore: completeSubtask()
    Note over TaskStore: Mark task as completed
```

Sources: [XAgentWeb/src/store/modules/task.ts:41-133]()

### Task Refinement and Reset

The store provides methods to handle task refinement and state reset:

1. `addRefinementInfo` - Adds refinement data to the current subtask
2. `setTaskRefineInfoArray` - Sets refinement information for multiple subtasks
3. `reset` - Clears all task state and resets to initial values

### Workspace File Management

Tasks can generate and manipulate files that are tracked in the task state:

1. `addWorkspaceFiles` - Adds a new file to the workspace
2. `setWorkspaceFiles` - Sets the complete list of workspace files

Sources: [XAgentWeb/src/store/modules/task.ts:134-175]()

## Task UI Components

### Tab Interface

The primary UI component for task management is the Tab interface, which displays subtasks as tabs and their inner steps as collapsible sections:

```mermaid
flowchart TD
    subgraph "TabComponent"
        A["Task Tabs (Outer Loop)"] --> B["Subtask 1"]
        A --> C["Subtask 2"]
        A --> D["Subtask N"]
        
        B --> E["Inner Steps (Inner Loop)"]
        E --> F["Step 1"]
        E --> G["Step 2"]
        E --> H["Step N"]
        
        F --> I["Thoughts"]
        F --> J["Reasoning"]
        F --> K["Plan"]
        F --> L["Criticism"]
    end
    
    subgraph "TaskControls"
        M["Run Button"]
        N["Auto Mode"]
        O["Task Goal Input"]
    end
    
    TabComponent --> TaskControls
```

The Tab interface allows users to:
- View all subtasks in a hierarchical structure
- See completion status with visual indicators
- Input goals for subtasks
- Run specific subtasks manually
- View task refinement information

Sources: [XAgentWeb/src/views/playground/components/Tab.vue:1-163](), [XAgentWeb/src/views/playground/components/Tab.vue:164-396]()

### Task Execution Controls

The Tab component provides controls for task execution:

1. Task execution in manual or automatic mode
2. Ability to run individual subtasks
3. Collapse/expand inner steps
4. View task completion status

The component watches for changes in the current subtask index and inner index to update the UI accordingly:

```mermaid
sequenceDiagram
    participant UI as "Tab Component"
    participant Store as "TaskStore"
    participant XAgent as "XAgent Core"
    
    UI->>Store: Get current subtask index
    Store-->>UI: Return current index
    UI->>UI: Update active tab
    
    UI->>Store: Get subtasks data
    Store-->>UI: Return subtasks
    UI->>UI: Render subtasks and inner steps
    
    User->>UI: Click run subtask button
    UI->>XAgent: emit("runSubtask", query)
    UI->>UI: isSubtaskGenerating = true
    
    XAgent-->>Store: Update task state
    Store-->>UI: Reactive update
    UI->>UI: Show new inner steps
```

Sources: [XAgentWeb/src/views/playground/components/Tab.vue:196-242](), [XAgentWeb/src/views/playground/components/Tab.vue:313-367]()

### Code Viewing

The CodeViewer component is used to display code generated or manipulated during task execution:

```mermaid
classDiagram
    class CodeViewer {
        +props: value, isShowLineNum, isLineWrapping
        +computed: code, showLineNum
        +data: extensions, CodeEditorOptions
        +methods: handleReady()
    }
    
    CodeViewer --> Codemirror : uses
```

The CodeViewer provides:
- Syntax highlighting for Python code
- Line numbering (optional)
- Line wrapping (optional)
- Dark theme support

Sources: [XAgentWeb/src/views/playground/components/CodeViewer.vue:1-86]()

## Integration with Playground Layout

The task management UI is integrated into the playground layout, which provides the overall structure for the XAgentWeb interface:

```mermaid
flowchart TB
    subgraph "PlaygroundLayout"
        HS["HistorySidebar"]
        CB["Container Box"]
    end
    
    CB --> TabComponent
    TabComponent --> TaskView
    
    TaskView --> CodeViewer
    TaskView --> TaskControls
    
    HistorySidebar --> HS
```

The layout provides a consistent structure with:
- A sidebar for browsing task history
- The main container for displaying and interacting with tasks

Sources: [XAgentWeb/src/views/playground/layout.vue:1-59]()

## Task Lifecycle

The full lifecycle of a task in the XAgentWeb interface follows this pattern:

```mermaid
stateDiagram-v2
    [*] --> "Task Creation"
    "Task Creation" --> "Initial Planning"
    "Initial Planning" --> "Subtask Generation"
    
    "Subtask Generation" --> "Subtask Execution"
    "Subtask Execution" --> "Inner Step Execution"
    
    "Inner Step Execution" --> "Tool Usage"
    "Tool Usage" --> "Inner Step Execution"
    
    "Inner Step Execution" --> "Subtask Completion"
    "Subtask Completion" --> "Subtask Refinement"
    "Subtask Refinement" --> "Next Subtask"
    "Next Subtask" --> "Subtask Execution"
    
    "Next Subtask" --> "Task Completion"
    "Task Completion" --> [*]
```

This lifecycle is managed through the task store actions and reflected in the UI components, providing users with a clear view of task progress and the ability to intervene when necessary.

Sources: [XAgentWeb/src/store/modules/task.ts:41-133](), [XAgentWeb/src/views/playground/components/Tab.vue:313-367]()

## Summary

The Task Management system in XAgentWeb provides a comprehensive interface for tracking and interacting with autonomous agent tasks. Through a combination of state management and UI components, users can:

1. Create new tasks with specific goals
2. Monitor the execution of tasks through subtasks and inner steps
3. View detailed information about each step including thoughts, reasoning, and plans
4. Run tasks in automatic or manual mode
5. View and manage files generated during task execution

The system is designed to make the complex processes of the XAgent autonomous system transparent and accessible to users, allowing for both observation and intervention as needed.

---

# Page: File Upload and Management

# File Upload and Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgentWeb/README.md](XAgentWeb/README.md)
- [XAgentWeb/index.html](XAgentWeb/index.html)
- [XAgentWeb/package.json](XAgentWeb/package.json)
- [XAgentWeb/src/composables/useApi.ts](XAgentWeb/src/composables/useApi.ts)
- [XAgentWeb/src/router/index.ts](XAgentWeb/src/router/index.ts)
- [XAgentWeb/src/store/modules/config.ts](XAgentWeb/src/store/modules/config.ts)
- [XAgentWeb/src/views/playground/components/FileUpload.vue](XAgentWeb/src/views/playground/components/FileUpload.vue)
- [XAgentWeb/src/views/playground/components/Inferencing.vue](XAgentWeb/src/views/playground/components/Inferencing.vue)
- [XAgentWeb/src/views/playground/components/Setting.vue](XAgentWeb/src/views/playground/components/Setting.vue)
- [XAgentWeb/src/views/playground/components/SubmitSubtaskInfo.vue](XAgentWeb/src/views/playground/components/SubmitSubtaskInfo.vue)
- [XAgentWeb/src/views/playground/components/WorkSpace.vue](XAgentWeb/src/views/playground/components/WorkSpace.vue)

</details>



## Purpose and Scope

This document describes the file upload and management system in XAgent's web interface. It covers how files are uploaded by users, stored in the system, and displayed in the workspace. This documentation focuses on client-side implementations of file upload features and their integration with the backend services.

## Overview

The file upload and management system allows users to upload files that can be used by XAgent during task execution. The system enforces file type restrictions, size limits, and integrates with the user authentication system to maintain file ownership.

```mermaid
graph TB
    subgraph "User Interface"
        Upload["FileUpload Component"]
        Workspace["WorkSpace Component"]
    end
    
    subgraph "Data Management"
        ConfigStore["Config Store - filelist"]
        API["API Services"]
    end
    
    subgraph "Backend Services"
        FileStorage["File Storage"]
        TaskAssociation["Task/Interaction Association"]
    end
    
    User -->|"Selects files"| Upload
    Upload -->|"Uploads files"| API
    API -->|"Stores files"| FileStorage
    API -->|"Returns file metadata"| ConfigStore
    ConfigStore -->|"Updates file list"| Workspace
    User -->|"Views files"| Workspace
    Workspace -->|"Requests file content"| API
    API -->|"Retrieves file"| FileStorage
    FileStorage -->|"Returns file content"| Workspace
    TaskAssociation --- FileStorage
```

Sources:
- [XAgentWeb/src/views/playground/components/FileUpload.vue:1-204]()
- [XAgentWeb/src/views/playground/components/WorkSpace.vue:1-208]()
- [XAgentWeb/src/store/modules/config.ts:1-64]()

## File Upload Component

The file upload functionality is implemented as a dedicated Vue component that provides an intuitive interface for users to upload files.

### Component Implementation

The file upload component is built using Element Plus's upload component with customized styling and behavior. It includes:

- Upload button with icon
- File list display
- Informational tips about file constraints
- Success/error message handling

```mermaid
sequenceDiagram
    participant User as "User"
    participant FUC as "FileUpload Component"
    participant API as "Axios API"
    participant Backend as "Backend Server"
    participant Store as "Config Store"
    
    User->>FUC: Selects file(s)
    FUC->>FUC: handleChange() validation
    
    User->>FUC: Triggers upload
    FUC->>FUC: uploadFile() method
    
    FUC->>API: Creates FormData with file, user_id, token
    API->>Backend: POST to "/api/workspace/upload"
    
    Backend->>Backend: Processes files
    Backend->>API: Returns file metadata
    
    alt Upload Successful
        API->>FUC: Success response
        FUC->>Store: configStore.addFiles(file_list)
        FUC->>User: Success message
    else Upload Failed
        API->>FUC: Error response
        FUC->>User: Error message
    end
```

Sources:
- [XAgentWeb/src/views/playground/components/FileUpload.vue:3-32]()
- [XAgentWeb/src/views/playground/components/FileUpload.vue:91-133]()

### Upload Constraints

The file upload system enforces several constraints to ensure compatibility with the XAgent system:

| Constraint | Value |
|------------|-------|
| Maximum files | 5 files |
| Maximum file size | 1MB per file |
| Supported formats | .txt, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .png, .jpeg, .gif, .py, .zip |

The constraints are enforced through:
1. UI limitations (limit prop in upload component)
2. File type validation through the accept attribute
3. User-friendly error messages

Sources:
- [XAgentWeb/src/views/playground/components/FileUpload.vue:3-15]()
- [XAgentWeb/src/views/playground/components/FileUpload.vue:26-30]()

## File Storage and Management

### Config Store Implementation

The system maintains file metadata in the Config Store, which provides an interface for managing the file list:

```mermaid
classDiagram
    class ConfigStore {
        filelist: any[]
        recorder_dir: string|null
        newtalkSettings: object
        input: string
        +getFileList()
        +getRecorderDir()
        +addFileItem(val)
        +addFiles(val[])
        +setFileList(val[])
        +resetConfig()
    }
```

Sources:
- [XAgentWeb/src/store/modules/config.ts:1-64]()

### Upload Process

The upload process involves several steps:

1. File selection by the user
2. Creation of FormData containing:
   - File data
   - User ID
   - Authentication token
3. POST request to `/api/workspace/upload`
4. Processing of server response
5. On success: update of the file list in the Config Store
6. Display of success/error message

Sources:
- [XAgentWeb/src/views/playground/components/FileUpload.vue:91-133]()

## Workspace File Display

The workspace component provides a file explorer-like interface for viewing and managing uploaded files.

### Workspace Layout

```mermaid
graph LR
    subgraph "WorkSpace Component"
        FileList["File List Sidebar"]
        ViewArea["Content View Area"]
    end
    
    FileList -->|"Selected file"| ViewArea
    ViewArea -->|"Displays content via"| Viewers
    
    subgraph "Viewers"
        CodeViewer["Code Viewer"]
        NotebookViewer["Python Notebook Viewer"]
        ImageViewer["Images Viewer"]
    end
```

Sources:
- [XAgentWeb/src/views/playground/components/WorkSpace.vue:1-49]()

### File Content Retrieval

When a user selects a file in the workspace:

1. The system sends a request to `/api/workspace/file`
2. The request includes:
   - User ID
   - Authentication token
   - Interaction ID (task ID)
   - File name
3. The server returns the file content
4. The appropriate viewer is chosen based on file type:
   - Code files: Code viewer with syntax highlighting
   - Notebook files (.ipynb): Notebook viewer
   - Image files (.png, .jpg, etc.): Image viewer

Sources:
- [XAgentWeb/src/views/playground/components/WorkSpace.vue:87-111]()
- [XAgentWeb/src/composables/useApi.ts:98-100]()

### File Type Handling

The system intelligently detects file types and renders them with appropriate viewers:

| File Type Category | Extensions | Viewer Component |
|--------------------|------------|------------------|
| Code/Text | .txt, .py, .pdf, .doc, .docx, etc. | CodeViewer |
| Jupyter Notebook | .ipynb | PythonNotebookViewer |
| Images | .png, .jpg, .jpeg, .gif, .bmp | ImagesViewer |

Sources:
- [XAgentWeb/src/views/playground/components/WorkSpace.vue:71-80]()
- [XAgentWeb/src/views/playground/components/WorkSpace.vue:32-46]()

## API Integration

The file system integrates with two main API endpoints:

### File Upload API

```
Endpoint: /api/workspace/upload
Method: POST
Content-Type: multipart/form-data
Parameters:
  - files: File object(s)
  - user_id: User identification
  - token: Authentication token
```

Sources:
- [XAgentWeb/src/views/playground/components/FileUpload.vue:52-104]()

### File Retrieval API

```
Endpoint: /api/workspace/file
Method: POST
Parameters:
  - user_id: User identification
  - token: Authentication token
  - interaction_id: Task/Interaction ID
  - file_name: Name of file to retrieve
```

Sources:
- [XAgentWeb/src/views/playground/components/WorkSpace.vue:91-97]()
- [XAgentWeb/src/composables/useApi.ts:98-100]()

## Integration with Task Execution

Files uploaded through the system are available to XAgent during task execution. The file-task association is maintained through the interaction_id parameter, ensuring that each task has access to its relevant files.

### Task Output File Display

In addition to user-uploaded files, XAgent can generate files during task execution, such as:

- Code files
- Images
- Jupyter notebooks

These files are displayed in the same workspace component but are created during task execution rather than through explicit file upload.

Sources:
- [XAgentWeb/src/views/playground/components/SubmitSubtaskInfo.vue:62-64]()
- [XAgentWeb/src/views/playground/components/WorkSpace.vue:87-111]()

## Security Considerations

The file upload system implements several security measures:

1. **Authentication**: All file operations require user_id and token
2. **File type restrictions**: Only specific file types are allowed
3. **Size limitations**: 1MB maximum per file
4. **File isolation**: Files are associated with specific interactions/users

Sources:
- [XAgentWeb/src/views/playground/components/FileUpload.vue:93-102]()
- [XAgentWeb/src/views/playground/components/FileUpload.vue:3-15]()

---

# Page: XAgentGen

# XAgentGen

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [XAgentGen/README.md](XAgentGen/README.md)
- [XAgentGen/app.py](XAgentGen/app.py)
- [XAgentGen/xgen/models/__init__.py](XAgentGen/xgen/models/__init__.py)
- [XAgentGen/xgen/models/transformers.py](XAgentGen/xgen/models/transformers.py)
- [XAgentGen/xgen/parser/function_parser.py](XAgentGen/xgen/parser/function_parser.py)
- [XAgentGen/xgen/text/generate/__init__.py](XAgentGen/xgen/text/generate/__init__.py)
- [XAgentGen/xgen/text/generate/regex.py](XAgentGen/xgen/text/generate/regex.py)

</details>



XAgentGen is a component of the XAgent system that implements guided generation of customized models to support XAgent's functionality. It allows language models to generate function calls with complex JSON schemas, similar to OpenAI's function calling feature, but for locally hosted models. This page provides a technical overview of XAgentGen's architecture, its model generation capabilities, and integration with the XAgent system.

## 1. Overview

XAgentGen enables constrained text generation, specifically targeting function calls that must adhere to predefined JSON schemas. It achieves this by transforming JSON schemas into regular expressions that guide the token generation process, ensuring the model outputs valid JSON conforming to the schema.

Sources: [XAgentGen/README.md:1-9](). [XAgentGen/README.md:42-48]()

## 2. System Architecture

XAgentGen operates as a standalone service within the XAgent ecosystem. It exposes a chat completions API endpoint that accepts messages, functions, and function call specifications, then returns constrained responses that adhere to the specified schemas.

```mermaid
graph TB
    subgraph "XAgentGen Service"
        API["FastAPI Server"]
        Engine["LLM Engine (vLLM)"]
        Parser["Function Parser"]
        Generator["Constrained Generator"]
    end
    
    subgraph "External Components"
        XAgent["XAgent Core"]
        Model["Language Models (e.g., XAgentLlama)"]
    end
    
    XAgent -->|"1. Request (messages, functions, schema)"|API
    API -->|"2. Format prompt"|Engine
    API -->|"3. Create constraint"|Parser
    Parser -->|"4. Generate regex"|Generator
    Generator -->|"5. Apply constraint"|Engine
    Engine -->|"6. Get constrained tokens"|Model
    Engine -->|"7. Return valid response"|API
    API -->|"8. Return structured response"|XAgent
    
    classDef default stroke-width:2px
```

Diagram: XAgentGen System Architecture

Sources: [XAgentGen/app.py:1-31](), [XAgentGen/app.py:86-170]()

XAgentGen consists of the following components:

1. **FastAPI Server**: Provides a RESTful API interface with a `/chat/completions` endpoint that mimics OpenAI's API structure.
2. **vLLM Engine**: Handles the efficient execution of language models with support for tensor parallelism and GPU optimization.
3. **Function Parser**: Converts JSON schemas into Pydantic models and regular expressions.
4. **Constrained Generator**: Uses regular expressions to guide the model's token generation process.

## 3. Model Generation Process

The core functionality of XAgentGen is transforming JSON schemas into constraints that guide the token generation process. This process involves several steps:

```mermaid
flowchart TD
    A["Receive JSON Schema"] --> B["Create Pydantic Models"]
    B --> C["Convert to Regular Expressions"]
    C --> D["Apply as Token Constraints"]
    D --> E["Generate Text with Constraints"]
    
    subgraph "FunctionParser"
        B
        C
    end
    
    subgraph "XRegex"
        D
        E
    end

    classDef default stroke-width:2px
```

Diagram: XAgentGen Model Generation Process

Sources: [XAgentGen/xgen/parser/function_parser.py:36-372](), [XAgentGen/xgen/text/generate/regex.py:19-78]()

### 3.1 JSON Schema to Pydantic Models

XAgentGen uses Pydantic to create runtime validation models from JSON schemas. The `FunctionParser` class:

1. Converts JSON Schema types to Python types
2. Creates dynamic Pydantic models for function calls and arguments
3. Handles complex nested objects, arrays, and enums

The parsing process supports various JSON Schema features including:
- Required and optional properties
- Nested objects and arrays
- Enumerations
- Type constraints (minimum, maximum, regex patterns)
- Multi-type properties (union types)

Sources: [XAgentGen/xgen/parser/function_parser.py:72-238]()

### 3.2 Pydantic Models to Regex Patterns

Once Pydantic models are created, they are converted to regular expressions that can constrain the token generation:

1. Models are converted to JSON Schema representation
2. JSON Schemas are transformed into regular expressions
3. Regular expressions are compiled into finite state machines (FSMs)
4. FSMs are determinized and indexed for the tokenizer's vocabulary

This process enables token-by-token generation that adheres to the structure defined by the JSON schema.

Sources: [XAgentGen/xgen/parser/function_parser.py:289-301](), [XAgentGen/xgen/text/generate/regex.py:19-62]()

### 3.3 Constrained Token Generation

The constrained generation process:

1. Creates a logits processor that applies constraints to the model's output distribution
2. At each generation step, the FSM determines which tokens are valid continuations
3. Invalid tokens have their logits set to negative infinity, effectively preventing their selection
4. The model generates tokens only from the valid set, ensuring adherence to the schema

```mermaid
sequenceDiagram
    participant Client
    participant API as "API Server"
    participant Parser as "Function Parser"
    participant Generator as "Constrained Generator"
    participant Model as "Language Model"
    
    Client->>API: Request with schema and messages
    API->>Parser: Create constraint from schema
    Parser->>Parser: Convert schema to Pydantic model
    Parser->>Parser: Convert model to regex pattern
    Parser->>Generator: Apply regex pattern as constraint
    
    loop Token Generation
        API->>Model: Request next token
        Model->>Generator: Propose logits for all tokens
        Generator->>Generator: Filter logits based on FSM state
        Generator->>Model: Return masked logits
        Model->>API: Return selected token
    end
    
    API->>Client: Return complete constrained response
```

Diagram: XAgentGen Constrained Token Generation Flow

Sources: [XAgentGen/app.py:92-152](), [XAgentGen/xgen/models/transformers.py:33-71]()

## 4. Integration with XAgent

XAgentGen is designed to be easily integrated with XAgent. The service provides an API endpoint compatible with OpenAI's chat completions API, allowing XAgent to use it as a drop-in replacement.

```mermaid
graph TB
    subgraph "XAgent System"
        XAgentCore["XAgent Core"]
        ConfigFile["Configuration File"]
    end
    
    subgraph "XAgentGen Service"
        XAgentGenAPI["XAgentGen API"]
        ModelService["Model Service"]
    end
    
    subgraph "Models"
        XAgentLlama["XAgentLlama (Code-Llama based)"]
    end
    
    ConfigFile -->|"Specifies model endpoint"|XAgentCore
    XAgentCore -->|"1. Send messages & function schemas"|XAgentGenAPI
    XAgentGenAPI -->|"2. Request constrained generation"|ModelService
    ModelService -->|"3. Load & execute"|XAgentLlama
    XAgentLlama -->|"4. Return constrained output"|ModelService
    ModelService -->|"5. Format & return JSON response"|XAgentGenAPI
    XAgentGenAPI -->|"6. Return structured function call"|XAgentCore
    
    classDef default stroke-width:2px
```

Diagram: XAgentGen Integration with XAgent

Sources: [XAgentGen/README.md:42-48](), [XAgentGen/app.py:86-170]()

### 4.1 Configuration

To use XAgentGen with XAgent:

1. A custom configuration file (e.g., `assets/xagentllama.yml`) specifies the XAgentGen endpoint
2. XAgent is configured to use this endpoint instead of OpenAI's API
3. Function schemas are passed to XAgentGen in the same format as they would be to OpenAI

Sources: [XAgentGen/README.md:44-48]()

### 4.2 Docker Deployment

XAgentGen is deployed as a Docker container:

1. The container includes the XAgentGen service and its dependencies
2. It requires CUDA for GPU acceleration
3. It connects to the same Docker network as ToolServer
4. The service listens on port 13520 by default
5. Model files are mounted from the host system

Sources: [XAgentGen/README.md:16-38]()

## 5. Supported Models

Currently, XAgentGen supports the following models:

- **XAgentLlama**: The official model of XAgent, based on Code-Llama
  - Available on [Hugging Face](https://huggingface.co/collections/XAgentTeam/xagentllm-655ae4091c419bb072940e74)
  - Specialized for function calling with constrained output

Sources: [XAgentGen/README.md:6-8]()

## 6. Example Usage

To use XAgentGen with XAgent:

1. Set up the XAgentGen service by pulling or building the Docker image
2. Mount a model directory containing the XAgentLlama model
3. Run XAgent with the custom configuration file

Example command:

```bash
python run.py --task "find all the prime numbers <=100" --config-file "assets/xagentllama.yml"
```

Sources: [XAgentGen/README.md:46-48]()

## Summary

XAgentGen is a specialized component that enables XAgent to use locally hosted models with function calling capabilities. By constraining the token generation process, it ensures the model produces structured outputs that conform to predefined JSON schemas. This allows XAgent to operate with open-source models while maintaining compatibility with the function-calling pattern established by commercial APIs like OpenAI.

---

# Page: Model Generation

# Model Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [XAgentGen/app.py](XAgentGen/app.py)
- [XAgentGen/xgen/models/__init__.py](XAgentGen/xgen/models/__init__.py)
- [XAgentGen/xgen/models/transformers.py](XAgentGen/xgen/models/transformers.py)
- [XAgentGen/xgen/parser/function_parser.py](XAgentGen/xgen/parser/function_parser.py)
- [XAgentGen/xgen/text/generate/__init__.py](XAgentGen/xgen/text/generate/__init__.py)
- [XAgentGen/xgen/text/generate/regex.py](XAgentGen/xgen/text/generate/regex.py)

</details>



## Purpose and Scope

This document provides a technical explanation of the Model Generation system in XAgentGen, a component of the XAgent architecture that enables constrained text generation. XAgentGen serves to create customized language model outputs that conform to specific formats and structures, especially for generating valid JSON responses according to defined schemas and function signatures.

For information about how XAgentGen integrates with the broader XAgent system, see [Integration with XAgent](#6.2).

## Overview

XAgentGen implements constrained text generation by using regular expressions to guide the language model's output, ensuring it follows specified patterns and structures. This is particularly useful for enforcing JSON schema compliance when generating structured data like function calls and arguments.

```mermaid
flowchart LR
    subgraph "Client"
        "ClientRequest"
    end
    
    subgraph "XAgentGen"
        "App" --> "FunctionParser"
        "FunctionParser" --> "RegexGenerator"
        "RegexGenerator" --> "ConstrainedLogitsProcessor"
        "ConstrainedLogitsProcessor" --> "TransformerModel"
    end
    
    "ClientRequest" --> "App"
    "TransformerModel" --> "ConstrainedResponse"
    
    "ConstrainedResponse" --> "Client"
```

Sources: [XAgentGen/app.py:90-170](), [XAgentGen/xgen/parser/function_parser.py:36-371]()

## Key Components

### FastAPI Server

XAgentGen exposes its functionality through a FastAPI server, which handles JSON requests for model generation with constrained outputs.

```mermaid
sequenceDiagram
    participant "Client" as C
    participant "FastAPI Server" as API
    participant "Model Engine" as ME
    
    C->>API: POST /chat/completions
    API->>API: Parse request parameters
    API->>API: Create ConstrainedLogitsProcessor
    API->>ME: Generate with constraints
    ME->>API: Return response
    API->>C: JSON response
```

Sources: [XAgentGen/app.py:23-31](), [XAgentGen/app.py:91-170]()

### Function Parser

The `FunctionParser` class converts JSON schemas and function descriptions into Pydantic models, which are then used to generate regex patterns for constrained output.

```mermaid
flowchart TD
    subgraph "FunctionParser"
        "create_all_functions_model" --> "add_function_model"
        "add_function_model" --> "create_object_model"
        "create_object_model" --> "add_property"
        "models_to_regex" --> "build_regex_from_object"
    end
    
    "JSONSchema" --> "create_all_functions_model"
    "build_regex_from_object" --> "RegexPattern"
```

Sources: [XAgentGen/xgen/parser/function_parser.py:36-371]()

### Constrained Logits Processor

The `ConstrainedLogitsProcessor` applies masks to the model's logits (token probabilities) to ensure that only tokens that follow the regex pattern have non-zero probability, effectively constraining the model's output.

```mermaid
flowchart LR
    subgraph "ConstrainedLogitsProcessor"
        "TokenIds" --> "RegexFSM"
        "RegexFSM" --> "MaskedLogits"
    end
    
    "ModelLogits" --> "TokenIds"
    "MaskedLogits" --> "NextTokenSelection"
```

Sources: [XAgentGen/app.py:68-84](), [XAgentGen/xgen/models/transformers.py:33-71]()

### XTransformers Model

The `XTransformers` class extends the base Transformers model with additional logits processing capabilities, enabling constrained text generation.

```mermaid
classDiagram
    class Transformers {
        +forward()
    }
    
    class XTransformers {
        +logits_processor
        +reset()
        +add_logits_processor()
        +forward()
    }
    
    Transformers <|-- XTransformers
```

Sources: [XAgentGen/xgen/models/transformers.py:33-71]()

## Regex-Based Generation

XAgentGen uses a regex-based approach to constrain the model's output, which is implemented through the `XRegex` class and the `multi_regex` function.

```mermaid
flowchart TD
    subgraph "RegexGeneration"
        "RegexPatterns" --> "FSM[Finite State Machine]"
        "FSM[Finite State Machine]" --> "TokenConstraints"
        "TokenConstraints" --> "ConstrainedGeneration"
    end
```

Sources: [XAgentGen/xgen/text/generate/regex.py:19-78]()

## API Interface

### Chat Completions Endpoint

The primary endpoint for interacting with XAgentGen is `/chat/completions`, which accepts JSON requests with the following structure:

| Parameter | Type | Description |
|-----------|------|-------------|
| model | string | Model identifier (should be "agentllama" or "xagentllm") |
| messages | array | Conversation history |
| arguments | object | Extra arguments schema |
| functions | array | Function definitions |
| function_call | object | Function call specification |
| temperature | float | Sampling temperature |
| top_p | float | Top-p sampling parameter |
| frequency_penalty | float | Frequency penalty |
| presence_penalty | float | Presence penalty |
| repetition_penalty | float | Repetition penalty |
| max_tokens | integer | Maximum number of tokens to generate |

Sources: [XAgentGen/app.py:91-170]()

### Request Processing Flow

```mermaid
flowchart TD
    "Request" --> "ParseJSON"
    "ParseJSON" --> "FormatPrompt"
    "FormatPrompt" --> "CreateLogitsProcessor"
    "CreateLogitsProcessor" --> "SetSamplingParams"
    "SetSamplingParams" --> "TokenizePrompt"
    "TokenizePrompt" --> "GenerateResponse"
    "GenerateResponse" --> "ProcessOutput"
    "ProcessOutput" --> "ReturnJSON"
```

Sources: [XAgentGen/app.py:91-170]()

## Constrained Generation Process

1. **Schema Parsing**: Convert JSON schemas into Pydantic models
2. **Regex Generation**: Create regex patterns from the Pydantic models
3. **FSM Construction**: Build finite state machines from the regex patterns
4. **Token Mapping**: Map FSM states to allowed tokens
5. **Logits Processing**: Apply masks to model logits based on the token mapping
6. **Text Generation**: Generate text using the constrained token selection

Sources: [XAgentGen/xgen/parser/function_parser.py:270-352](), [XAgentGen/xgen/text/generate/regex.py:19-78]()

## Usage Example

When a client wants to generate a JSON response that conforms to a specific schema:

1. The client sends a request to the `/chat/completions` endpoint with the schema
2. The server creates a `ConstrainedLogitsProcessor` with the schema
3. The processor converts the schema to regex patterns
4. The model generates text, constrained by the regex patterns
5. The server returns the constrained text to the client

Sources: [XAgentGen/app.py:91-170]()

## Model Initialization and Configuration

XAgentGen uses vLLM (a high-performance inference engine) to load and run the language model:

```mermaid
flowchart LR
    "ModelPath" --> "AsyncEngineArgs"
    "AsyncEngineArgs" --> "AsyncLLMEngine"
    "AsyncLLMEngine" --> "Tokenizer"
    "AsyncLLMEngine" --> "InferenceEngine"
```

Sources: [XAgentGen/app.py:40-65]()

## Performance Considerations

The `XRegex` class implements caching of the finite state machines to improve performance for repeated calls with the same regex patterns:

```python
pstate_to_vocab_path_cache = TTLCache(maxsize=20, ttl=3600)
```

This cache stores the compiled FSMs, states to token maps, and empty token IDs for up to 20 different regex patterns, with a time-to-live of 1 hour.

Sources: [XAgentGen/xgen/text/generate/regex.py:13-56]()

---

# Page: Integration with XAgent

# Integration with XAgent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [XAgentGen/README.md](XAgentGen/README.md)
- [XAgentGen/app.py](XAgentGen/app.py)
- [XAgentGen/xgen/models/__init__.py](XAgentGen/xgen/models/__init__.py)
- [XAgentGen/xgen/models/transformers.py](XAgentGen/xgen/models/transformers.py)
- [XAgentGen/xgen/parser/function_parser.py](XAgentGen/xgen/parser/function_parser.py)
- [XAgentGen/xgen/text/generate/__init__.py](XAgentGen/xgen/text/generate/__init__.py)
- [XAgentGen/xgen/text/generate/regex.py](XAgentGen/xgen/text/generate/regex.py)

</details>



This document details how XAgentGen integrates with XAgent Core, enabling the use of custom trained language models for autonomous agent operations. XAgentGen provides function-constrained text generation capabilities that can be used as an alternative to external APIs like OpenAI's. For information about the model generation aspects of XAgentGen, see [Model Generation](#6.1).

## 1. XAgentGen Overview

XAgentGen implements guided generation of customized models that support XAgent's operation. Its primary capability is allowing models to generate structured function calls with complex JSON schemas, similar to OpenAI's function calling API. This enables XAgent to use open-source or custom-trained models while maintaining structured output formats required by the agent system.

The component runs as a separate service that exposes an API endpoint similar to OpenAI's `/chat/completions` interface, making it a drop-in replacement in the XAgent architecture.

```mermaid
graph TD
    subgraph "XAgentGen Service"
        API["API Server"]
        Parser["Function Parser"]
        Model["XAgentLLM Models"]
    end
    
    XAgent["XAgent Core"] -->|"API requests"| API
    API -->|"Parse function schemas"| Parser
    Parser -->|"Constrain generation"| Model
    Model -->|"Structured response"| API
    API -->|"JSON response"| XAgent
```

Sources: [XAgentGen/README.md:1-49](), [XAgentGen/app.py:1-34]()

## 2. Integration Architecture

XAgentGen is designed as a separate service that can be run alongside XAgent Core. The integration is implemented through an API interface that mimics the OpenAI API structure, allowing XAgent to interact with XAgentGen models using the same patterns it uses for external models.

### 2.1 System Components

```mermaid
graph LR
    subgraph "XAgent Core"
        XA["XAgent"]
        Config["Configuration"]
    end
    
    subgraph "XAgentGen"
        Server["FastAPI Server"]
        FunctionParser["Function Parser"]
        Models["XTransformers"]
        VLLM["VLLM Engine"]
    end
    
    XA -->|"API requests"| Server
    Config -->|"Model selection"| XA
    Server -->|"Parse functions"| FunctionParser
    FunctionParser -->|"Constrain generation"| Models
    Models -->|"Inference"| VLLM
    VLLM -->|"Generated text"| Server
    Server -->|"Structured JSON"| XA
```

Sources: [XAgentGen/app.py:1-170](), [XAgentGen/xgen/parser/function_parser.py:1-371]()

### 2.2 Communication Flow

The communication between XAgent and XAgentGen follows this sequence:

```mermaid
sequenceDiagram
    participant XAgent as "XAgent Core"
    participant Server as "XAgentGen Server"
    participant Parser as "Function Parser"
    participant Model as "LLM Model"
    
    XAgent->>Server: POST /chat/completions with messages & functions
    Server->>Parser: Create function constraints
    Parser->>Parser: Convert JSON schema to regex
    Server->>Model: Initialize with constraints
    Model->>Model: Generate constrained text
    Model->>Server: Return generated text
    Server->>Server: Validate function call format
    Server->>XAgent: Return structured JSON response
```

Sources: [XAgentGen/app.py:85-170](), [XAgentGen/xgen/parser/function_parser.py:239-345]()

## 3. API Interface

XAgentGen exposes a FastAPI server with endpoints that mimic the OpenAI API structure, making it compatible with existing XAgent code that uses the OpenAI client.

### 3.1 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat/health` | POST | Health check endpoint |
| `/chat/completions` | POST | Main endpoint for generating text completions |

Sources: [XAgentGen/app.py:85-91](), [XAgentGen/app.py:92-170]()

### 3.2 Request Format

The request to the `/chat/completions` endpoint follows this structure:

```
{
  "model": "xagentllm",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "functions": [
    {
      "name": "function_name",
      "parameters": {
        "type": "object",
        "properties": {
          "param1": {"type": "string"},
          "param2": {"type": "integer"}
        },
        "required": ["param1"]
      }
    }
  ],
  "function_call": {"name": "function_name"},
  "arguments": {...},
  "temperature": 0.8,
  "top_p": 1.0,
  "max_tokens": 4000
}
```

Sources: [XAgentGen/app.py:92-117]()

### 3.3 Response Format

The response from the API follows this structure:

```
{
  "model": "xagentllm",
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "choices": [
    {
      "message": {
        "content": "{\"name\":\"function_name\",\"arguments\":{\"param1\":\"value\",\"param2\":42}}"
      },
      "finish_reason": "stop",
      "index": 0
    }
  ]
}
```

Sources: [XAgentGen/app.py:143-169]()

## 4. Function Calling Mechanism

A key feature of XAgentGen is its ability to generate text that conforms to a specified JSON schema, similar to OpenAI's function calling capability. This is implemented through a function parsing and constraint system.

### 4.1 Function Parsing Process

```mermaid
flowchart TD
    JSON["JSON Schema"] -->|"Parse"| Parser["FunctionParser"]
    Parser -->|"Create"| Models["Pydantic Models"]
    Models -->|"Convert to"| Regex["Regular Expressions"]
    Regex -->|"Constrain"| Generator["Text Generator"]
    Generator -->|"Outputs"| Structured["Structured JSON"]
```

Sources: [XAgentGen/xgen/parser/function_parser.py:36-268](), [XAgentGen/xgen/parser/function_parser.py:289-300]()

### 4.2 Function Schema Processing

1. The `FunctionParser` class takes JSON schemas for functions and converts them to Pydantic models
2. These models are then converted to regular expressions that constrain the output space
3. The `ConstrainedLogitsProcessor` applies these constraints during text generation
4. The resulting text is guaranteed to conform to the specified schema

Sources: [XAgentGen/app.py:68-84](), [XAgentGen/xgen/text/generate/regex.py:19-78]()

## 5. Configuration for XAgent

To use XAgentGen with XAgent Core, you need to configure XAgent to use the custom model instead of the default OpenAI models.

### 5.1 Configuration File

XAgent provides a sample configuration file (`assets/xagentllama.yml`) for using XAgentGen. The key aspects of this configuration include:

1. Setting the model type to the custom model
2. Providing the endpoint URL for the XAgentGen server
3. Configuring generation parameters

Sources: [XAgentGen/README.md:42-48]()

### 5.2 Docker Network Configuration

XAgentGen and XAgent must be on the same Docker network to communicate efficiently. When running XAgentGen, it should be started with the `--network tool-server-network` parameter to join XAgent's network.

Sources: [XAgentGen/README.md:35-38]()

## 6. Usage Example

### 6.1 Starting XAgentGen Service

To use XAgentGen with XAgent:

1. Start the XAgentGen Docker container:
```bash
docker run -it -p 13520:13520 --network tool-server-network -v /host/model/path:/model:rw --gpus all --ipc=host xagentteam/xagentgen:latest python app.py --model-path /model --port 13520
```

2. Run XAgent with the custom configuration:
```bash
python run.py --task "find all the prime numbers <=100" --config-file "assets/xagentllama.yml"
```

Sources: [XAgentGen/README.md:35-48]()

### 6.2 Integration Flow

```mermaid
flowchart LR
    User["User"] -->|"Task"| Runner["XAgent run.py"]
    Runner -->|"Read config"| Config["xagentllama.yml"]
    Runner -->|"Initialize"| XAgent["XAgent Core"]
    XAgent -->|"/chat/completions"| XAgentGen["XAgentGen Server"]
    XAgentGen -->|"Generate function calls"| XAgent
    XAgent -->|"Execute tools"| ToolServer["ToolServer"]
    XAgent -->|"Results"| User
```

Sources: [README.md:42-54](), [XAgentGen/README.md:42-48]()

## 7. Technical Implementation Details

### 7.1 Constrained Text Generation

The core technical innovation in XAgentGen is its constrained text generation system:

1. JSON schemas are converted to Pydantic models for validation
2. Models are then converted to regular expressions via the `build_regex_from_object` function
3. The `XRegex` and `multi_regex` classes create finite state machines from these regular expressions
4. The `ConstrainedLogitsProcessor` applies these constraints during text generation by masking invalid next tokens

This ensures that the model output always conforms to the specified schema structure, enabling reliable function calling.

Sources: [XAgentGen/xgen/parser/function_parser.py:289-300](), [XAgentGen/xgen/text/generate/regex.py:19-78](), [XAgentGen/app.py:68-84]()

### 7.2 Model Implementation

XAgentGen extends the standard Transformers library with the `XTransformers` class that adds support for:

1. Custom logits processors for constrained generation
2. Token counting for usage statistics
3. Integration with VLLM for efficient inference

Sources: [XAgentGen/xgen/models/transformers.py:33-71]()

## 8. Advantages of XAgentGen Integration

Using XAgentGen with XAgent provides several advantages:

1. **Independence from external APIs**: Reduces reliance on proprietary APIs like OpenAI
2. **Cost reduction**: Eliminates API usage costs for high-volume scenarios
3. **Customization**: Allows training specialized models for specific domains
4. **Privacy**: Keeps sensitive information within your infrastructure
5. **Compatibility**: Maintains the same function calling interface as OpenAI

This integration represents an important step toward making XAgent more self-contained and customizable for different deployment scenarios.

Sources: [XAgentGen/README.md:1-49]()

---

# Page: Configuration Reference

# Configuration Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [XAgentGen/README.md](XAgentGen/README.md)
- [assets/config.yml](assets/config.yml)
- [assets/gpt-3.5-turbo_config.yml](assets/gpt-3.5-turbo_config.yml)
- [assets/gpt4_config.yml](assets/gpt4_config.yml)

</details>



## Overview

This document provides a comprehensive reference for all configuration options available in XAgent. The configuration file controls aspects like API access, model parameters, tool server settings, task processing limits, and various experimental features.

For installation instructions, see [Installation and Setup](#1.2).

Sources: [README.md:113-120]()

## Configuration File Location and Format

XAgent uses YAML format for configuration files. The primary configuration file is located at `assets/config.yml`. There are also model-specific configuration templates available such as:

- `assets/gpt4_config.yml` - Optimized for GPT-4
- `assets/gpt-3.5-turbo_config.yml` - Optimized for GPT-3.5-Turbo
- `assets/xagentllama.yml` - For using XAgentGen with custom models

To use a specific configuration file, specify it with the `--config-file` argument when running XAgent:

```bash
python run.py --task "your task here" --config-file "assets/config.yml"
```

Sources: [README.md:126-128](), [assets/config.yml](), [assets/gpt4_config.yml](), [assets/gpt-3.5-turbo_config.yml]()

## Configuration Structure

The following diagram shows the main sections of the XAgent configuration file:

```mermaid
graph TD
    subgraph "XAgent Configuration"
        A["API Keys"] --> XA["XAgent System"]
        B["Default Request Settings"] --> XA
        C["ToolServer Configuration"] --> XA
        D["Task Processing Limits"] --> XA
        E["Summary Settings"] --> XA
        F["Human Interaction"] --> XA
        G["Tool Management"] --> XA
        H["Recording and Experiments"] --> XA
    end
    
    XA --> I["Execution Environment"]
    
    class A,B,C,D,E,F,G,H configSection
    class XA system
    class I environment
```

Sources: [assets/config.yml]()

## API Keys Configuration

This section defines the API keys for language models that XAgent can use. Multiple keys can be provided for each model type for fallback and load balancing.

### Structure

```mermaid
graph TD
    subgraph "api_keys Section"
        A["Model Type\n(e.g., gpt-4-32k)"] --> B["List of API Configurations"]
        B --> C1["API Config 1"]
        B --> C2["API Config 2"]
        C1 --> D1["api_key"]
        C1 --> D2["organization\n(OpenAI only)"]
        C1 --> D3["api_base\n(Custom endpoint)"]
        C1 --> D4["api_type\n(e.g., azure)"]
        C1 --> D5["Other Parameters"]
    end
```

### Example Configuration

```yaml
api_keys:
  gpt-3.5-turbo-16k:
    - api_key: sk-xxxxx
      api_base: https://example.com
      api_type: azure
      api_version: 2023-07-01-preview
      engine: GPT-35-Turbo-16k
    - api_key: sk-xxxxx
      organization: org-xxxxxx
      model: gpt-3.5-turbo-16k
  gpt-4:    
    - api_key: sk-xxxxx
      organization: org-xxxxx
      model: gpt-4
  gpt-4-32k:
    - api_key: sk-xxxxx
      organization: org-xxxxx
      model: gpt-4-32k
```

### Supported Parameters

Each API configuration can include:

- **OpenAI-specific parameters:**
  - `api_key`: Your OpenAI API key
  - `organization`: Your OpenAI organization ID
  - `model`: The specific model identifier

- **Azure OpenAI-specific parameters:**
  - `api_key`: Your Azure OpenAI API key
  - `api_base`: The base URL for your Azure OpenAI resource
  - `api_type`: Set to "azure"
  - `api_version`: Azure API version (e.g., "2023-07-01-preview")
  - `engine`: The deployment name in Azure

- **Any additional parameters supported by the underlying API client**

Note: At least one `gpt-3.5-turbo-16k` API key should be provided as a backup model, even if using GPT-4 as the primary model.

Sources: [assets/config.yml:1-25](), [README.md:117-122]()

## Default Request Configuration

This section controls the default behavior of model requests.

```yaml
default_request_type: openai  # or xagent
default_completion_kwargs:
  model: gpt-4-32k
  temperature: 0.2
  request_timeout: 60
```

- `default_request_type`: Specifies the API type to use (options: "openai" or "xagent")
- `default_completion_kwargs`: Default parameters for completion requests:
  - `model`: The default model to use
  - `temperature`: Controls randomness (0-1, lower is more deterministic)
  - `request_timeout`: Timeout for API requests in seconds

Sources: [assets/config.yml:28-32](), [assets/gpt4_config.yml:17-21](), [assets/gpt-3.5-turbo_config.yml:10-14]()

## Summary Configuration

Controls how XAgent summarizes information during task execution.

```yaml
enable_summary: true
summary:
  single_action_max_length: 2048
  max_return_length: 12384
```

- `enable_summary`: Whether to enable summarization (true/false)
- `summary`: Summarization parameters:
  - `single_action_max_length`: Maximum length of a single action to summarize
  - `max_return_length`: Maximum length of summarized content

Sources: [assets/config.yml:34-37](), [assets/gpt4_config.yml:23-26](), [assets/gpt-3.5-turbo_config.yml:16-19]()

## ToolServer Configuration

ToolServer provides the environment where XAgent executes tools. This section configures how XAgent connects to ToolServer.

```yaml
use_selfhost_toolserver: true
selfhost_toolserver_url: http://localhost:8080
```

- `use_selfhost_toolserver`: Whether to use a self-hosted ToolServer (true/false)
- `selfhost_toolserver_url`: The URL where ToolServer is running

The following diagram shows how XAgent connects to ToolServer:

```mermaid
sequenceDiagram
    participant "XAgent Core" as XA
    participant "ToolServerManager" as TSM
    participant "ToolServerNode" as TSN
    
    XA->>TSM: Connect to ToolServer
    Note over XA,TSM: Configuration used: selfhost_toolserver_url
    TSM->>TSN: Create/manage node
    XA->>TSN: Execute tools
```

Sources: [assets/config.yml:39-40](), [assets/gpt4_config.yml:28-29](), [assets/gpt-3.5-turbo_config.yml:21-22](), [README.md:76-96]()

## Task Processing Configuration

Controls how XAgent approaches task planning and execution with parameters that limit various aspects of the process.

```yaml
max_retry_times: 5
max_subtask_chain_length: 15
max_plan_refine_chain_length: 3
max_plan_tree_depth: 3
max_plan_tree_width: 5
max_plan_length: 8192
```

- `max_retry_times`: Maximum number of retries when a task fails
- `max_subtask_chain_length`: Maximum number of subtasks in a chain
- `max_plan_refine_chain_length`: Maximum iterations of plan refinement
- `max_plan_tree_depth`: Maximum depth of the planning tree
- `max_plan_tree_width`: Maximum width (branching factor) of the planning tree
- `max_plan_length`: Maximum token length of a plan

The planning structure is illustrated in this diagram:

```mermaid
graph TD
    subgraph "XAgent Planning System"
        A["Main Task"] --> B1["Subtask 1"]
        A --> B2["Subtask 2"]
        A --> B3["Subtask 3"]
        B1 --> C1["Subtask 1.1"]
        B1 --> C2["Subtask 1.2"]
        B2 --> C3["Subtask 2.1"]
    end
    
    D["Planning Parameters"]
    D -- "max_plan_tree_depth\nControls maximum depth" --> A
    D -- "max_plan_tree_width\nControls maximum branches" --> A
    D -- "max_subtask_chain_length\nControls chain length" --> A
```

Sources: [assets/config.yml:42-47](), [assets/gpt4_config.yml:31-36](), [assets/gpt-3.5-turbo_config.yml:24-29]()

## RapidAPI Configuration

Controls the integration with RapidAPI for accessing external API tools.

```yaml
rapidapi_retrieve_tool_count: 0
```

- `rapidapi_retrieve_tool_count`: Number of tools to retrieve from RapidAPI
  - Set to 0 to disable RapidAPI integration
  - Higher values allow XAgent to access more external API tools

Sources: [assets/config.yml:49](), [assets/gpt4_config.yml:38](), [assets/gpt-3.5-turbo_config.yml:31](), [README.md:68-69]()

## Human Interaction Configuration

Controls whether and how XAgent can request human assistance.

```yaml
enable_ask_human_for_help: False
```

- `enable_ask_human_for_help`: Whether XAgent can ask for human assistance (true/false)

When enabled, XAgent can pause execution and request human input to overcome obstacles.

Sources: [assets/config.yml:51](), [assets/gpt4_config.yml:40](), [assets/gpt-3.5-turbo_config.yml:33](), [README.md:48]()

## Tool Management Configuration

Controls which tools are available to XAgent.

```yaml
tool_blacklist:
  - FileSystemEnv_print_filesys_struture
```

- `tool_blacklist`: List of tools that XAgent is not allowed to use

Sources: [assets/config.yml:53-54](), [assets/gpt4_config.yml:42-43](), [assets/gpt-3.5-turbo_config.yml:34-36]()

## Record Directory Configuration

Controls how XAgent records its execution for analysis and debugging.

```yaml
record_dir:
```

- `record_dir`: Directory where execution records are stored
  - Leave empty to disable recording
  - Set to a valid path to save execution records

Execution records contain all intermediate steps, including task statuses, LLM input-output pairs, and tool usage. Sensitive information such as API keys is automatically removed from records.

Sources: [assets/config.yml:56](), [assets/gpt4_config.yml:45](), [assets/gpt-3.5-turbo_config.yml:38](), [README.md:135-137]()

## Experiment Configuration

Controls experimental features in XAgent.

```yaml
experiment:
  redo_action: false
```

- `experiment`: Container for experimental settings
  - `redo_action`: Whether to enable the redo action feature (true/false)

Sources: [assets/config.yml:58-59](), [assets/gpt4_config.yml:47-48](), [assets/gpt-3.5-turbo_config.yml:40-41]()

## XAgentGen Integration

XAgentGen is a component that enables the use of custom models with XAgent. It requires additional configuration.

### Using XAgentGen

1. Set up the XAgentGen service (see [XAgentGen README](XAgentGen/README.md))
2. Use the XAgentLlama configuration:

```bash
python run.py --task "your task here" --config-file "assets/xagentllama.yml"
```

The `xagentllama.yml` configuration specifies how to connect to the XAgentGen service.

Sources: [XAgentGen/README.md:1-48]()

## Recommended Configurations

XAgent provides different configuration templates optimized for specific use cases:

| Configuration | Use Case | Notes |
|---------------|----------|-------|
| `config.yml` | Production use | Default configuration with GPT-4-32k |
| `gpt4_config.yml` | Standard use | For GPT-4 with modest context window |
| `gpt-3.5-turbo_config.yml` | Budget use | For GPT-3.5-Turbo-16k |
| `xagentllama.yml` | Custom models | For using with XAgentGen |

While XAgent can work with different models, we recommend:
- GPT-4-32k for best performance
- GPT-4 for most standard tasks
- GPT-3.5-Turbo-16k as a minimum requirement backup

XAgent is not recommended to run with standard GPT-3.5-Turbo due to its limited context length.

Sources: [README.md:117-122]()

## Configuration Application Workflow

The following diagram illustrates how configuration settings are applied during XAgent initialization:

```mermaid
flowchart TD
    A["Configuration File"] --> B["Config Parsing"]
    B --> C["API Key Validation"]
    C --> D["Default Settings Applied"]
    D --> E["XAgent Core Initialization"]
    E --> F["ToolServer Connection"]
    F --> G["Task Execution"]
    
    H["Command Line Arguments"] --> B
    
    subgraph "XAgent System"
        B
        C
        D
        E
        F
        G
    end
```

Sources: [README.md:126-137]()

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [README_ZH.md](README_ZH.md)
- [XAgent/recorder.py](XAgent/recorder.py)
- [XAgentGen/README.md](XAgentGen/README.md)
- [XAgentServer/server.py](XAgentServer/server.py)
- [docker-compose.yml](docker-compose.yml)

</details>



This page provides a comprehensive guide to deploying XAgent in various environments. It covers the deployment architecture, requirements, setup procedures, and configuration options. For information about XAgent's architecture and functionality, see [Architecture](#1.1), and for installation instructions without deployment details, see [Installation and Setup](#1.2).

## Deployment Architecture

XAgent consists of several components that work together to provide its functionality. When deploying XAgent, you'll need to set up these components and configure them properly.

```mermaid
graph TB
    subgraph "Docker Environment"
        subgraph "Core Services"
            TSM["ToolServerManager\n(xagentteam/toolserver-manager)"]
            TSN["ToolServerNode\n(xagentteam/toolserver-node)"]
            XAS["XAgentServer\n(xagentteam/xagent-server)"]
        end
        
        subgraph "Databases"
            MongoDB["MongoDB\n(for ToolServer)"]
            MySQL["MySQL\n(for XAgentServer)"]
            Redis["Redis\n(for XAgentServer)"]
        end
        
        subgraph "Optional Services"
            XAG["XAgentGen\n(xagentteam/xagentgen)"]
        end
    end
    
    User[/"User"/]
    CLI["Command Line\nInterface"]
    Web["Web Browser"]
    
    User --> CLI
    User --> Web
    CLI --> XAgent
    Web --> XAS
    
    XAgent --> TSM
    XAS --> TSM
    TSM --> TSN
    
    TSM --> MongoDB
    XAS --> MySQL
    XAS --> Redis
    
    XAgent -.-> XAG
    
    class TSM,TSN,XAS,XAG service
    class MongoDB,MySQL,Redis database
    class CLI,Web interface
```

Sources: [docker-compose.yml:1-111](), [README.md:72-146]()

## Prerequisites

Before deploying XAgent, ensure you have the following prerequisites:

1. **Docker and Docker Compose**: Required for containerization
2. **Python 3.10 or higher**: For running XAgent CLI
3. **OpenAI API Key**: At least one key is required for accessing OpenAI services
4. **Hardware Requirements**:
   - Minimum 8GB RAM
   - 10GB free disk space
   - For XAgentGen (optional): NVIDIA GPU with CUDA support

Sources: [README.md:77-80](), [README.md:110-123](), [XAgentGen/README.md:12-14]()

## Basic Deployment

The basic deployment includes the ToolServer components and allows interaction via the command line interface.

### Setting up ToolServer

ToolServer is where XAgent's actions take place. It provides a safe environment for running tools.

1. Create a docker-compose.yml file with the following contents (or use the one provided with XAgent):

```
# See docker-compose.yml for the complete configuration
```

2. Start the ToolServer containers:

```bash
docker compose up
```

Alternatively, to build the images from local sources:

```bash
docker compose build
docker compose up
```

To run the containers in the background:

```bash
docker compose up -d
```

### Container Structure

The ToolServer deployment consists of the following containers:

```mermaid
graph LR
    TSM["ToolServerManager\n(Port 8080)"] --> TSN["ToolServerNode"]
    TSM --> MongoDB["MongoDB\n(Authentication enabled)"]
    
    subgraph "Docker Network: tool-server-network"
        TSM
        TSN
        MongoDB
    end
    
    CLI["XAgent CLI"] --> TSM
    
    Volume1["toolserverconfig\n(./assets/config)"] --> TSM
    Volume1 --> TSN
    Volume2["xagentmongodb\n(MongoDB data)"] --> MongoDB
```

Sources: [docker-compose.yml:4-41](), [README.md:76-96]()

### Running XAgent with CLI

After setting up ToolServer, you can run XAgent using the command line interface:

1. Install Python requirements:

```bash
pip install -r requirements.txt
```

2. Configure XAgent in `assets/config.yml`. At minimum, provide one OpenAI API key.

3. Run XAgent:

```bash
python run.py --task "your task here" --config-file "assets/config.yml"
```

You can use the `--upload-files` parameter to select initial files for XAgent.

Sources: [README.md:107-136]()

## Full Deployment with Web Interface

The full deployment includes XAgentServer, which provides a web interface for interacting with XAgent.

### Setting up XAgentServer

XAgentServer requires MySQL and Redis for database and session management:

1. Ensure the full docker-compose.yml is used, which includes XAgentServer, MySQL, and Redis.

2. Start all services:

```bash
docker compose up -d
```

### Accessing the Web Interface

After deploying XAgentServer:

1. Navigate to `http://localhost:5173` in your web browser.

2. Log in using the default credentials:
   - Username: `guest`
   - Password: `xagent`

```mermaid
graph TB
    subgraph "Docker Containers"
        XAS["XAgentServer\n(Ports: 5173, 8090)"]
        MySQL["MySQL\n(Port: 3306)"]
        Redis["Redis\n(Port: 6379)"]
        TSM["ToolServerManager\n(Port: 8080)"]
    end
    
    Web["Web Browser"] --"HTTP (5173)"--> XAS
    XAS --"Internal Communication"--> TSM
    XAS --"SQL Queries"--> MySQL
    XAS --"Session Data"--> Redis
    
    Volume1["assets (mounted to /app/assets)"] --> XAS
    Volume2["SQL init scripts\n(XAgentServer/database/sql)"] --> MySQL
```

Sources: [docker-compose.yml:43-94](), [README.md:143-146](), [XAgentServer/server.py:1-110]()

## Optional: Deploying with XAgentGen

XAgentGen implements guided generation of customized models to support XAgent. This is optional and requires a GPU.

### Prerequisites for XAgentGen

- NVIDIA GPU
- NVIDIA CUDA Container Toolkit installed

### Deploying XAgentGen

1. Pull the pre-built docker image (recommended):

```bash
docker pull xagentteam/xagentgen:latest
```

Or build it yourself:

```bash
docker build -f dockerfiles/XAgentGen/Dockerfile -t xagentteam/xagentgen .
```

2. Run the XAgentGen container:

```bash
docker run -it -p 13520:13520 --network tool-server-network -v /host/model/path:/model:rw --gpus all --ipc=host xagentteam/xagentgen:latest python app.py --model-path /model --port 13520
```

Replace `/host/model/path` with the path to your model directory.

3. Configure XAgent to use the customized model:

```bash
python run.py --task "your task here" --config-file "assets/xagentllama.yml"
```

Sources: [XAgentGen/README.md:1-49]()

## Configuration Options

XAgent offers several configuration options to customize its behavior.

### Environment Variables

The following environment variables can be set in the `.env` file:

- `DB_USERNAME`: MongoDB username
- `DB_PASSWORD`: MongoDB password
- `DB_COLLECTION`: MongoDB collection name
- `CONFIG_FILE`: Path to the configuration file for XAgentServer

### Configuration Files

The main configuration file is `assets/config.yml`, which contains settings for XAgent:

- API keys for OpenAI
- Model configurations
- Human feedback settings
- Workspace configurations

For XAgentGen, a sample configuration file is available at `assets/xagentllama.yml`.

Sources: [docker-compose.yml:15-19](), [README.md:115-123]()

## Data and Workspace

When running XAgent, several directories are used for data storage:

1. **local_workspace**: Contains files generated by XAgent during execution
2. **running_records**: Contains execution records, including intermediate steps, task statuses, and LLM input-output pairs
3. **toolserverconfig**: Docker volume that contains configuration for the ToolServer

```mermaid
graph LR
    subgraph "Host Machine"
        Workspace["local_workspace\n(XAgent working files)"]
        Records["running_records\n(Execution records)"]
        Config["assets/config\n(Configuration files)"]
    end
    
    subgraph "Docker Volumes"
        TSConfig["toolserverconfig\n(Bind mount from ./assets/config)"]
        MongoDB["xagentmongodb\n(MongoDB data)"]
    end
    
    XAgent --> Workspace
    XAgent --> Records
    XAgent --> Config
    Config --> TSConfig
    
    TSM["ToolServerManager"] --> TSConfig
    TSN["ToolServerNode"] --> TSConfig
    Mongo["MongoDB Container"] --> MongoDB
```

Sources: [docker-compose.yml:98-106](), [README.md:129-136](), [XAgent/recorder.py:1-347]()

## Troubleshooting

### Common Issues

1. **Docker Service Not Starting**:
   - Check if Docker is running: `docker info`
   - Ensure you have enough disk space: `df -h`

2. **ToolServer Connection Issues**:
   - Verify the ToolServerManager is running: `docker ps | grep ToolServerManager`
   - Check ToolServerManager logs: `docker logs $(docker ps -q --filter name=ToolServerManager)`

3. **XAgentServer Not Accessible**:
   - Check if the container is running: `docker ps | grep XAgent-Server`
   - Verify port mapping: `docker port XAgent-Server`
   - Check if the required ports (5173, 8090) are not already in use

4. **XAgentGen GPU Issues**:
   - Verify CUDA is properly installed: `nvidia-smi`
   - Ensure Docker has GPU access: `docker run --gpus all nvidia/cuda:11.0-base nvidia-smi`

### Updating XAgent

To update XAgent components:

1. Pull the latest images:
```bash
docker compose pull
```

2. Or rebuild the images:
```bash
docker compose build
```

3. Restart the services:
```bash
docker compose down
docker compose up -d
```

Sources: [README.md:98-108]()

## Security Considerations

When deploying XAgent, consider the following security aspects:

1. **API Keys**: OpenAI API keys in the configuration should be kept secure
2. **Database Authentication**: Ensure strong passwords for MongoDB, MySQL, and Redis
3. **Web Access**: Consider using a reverse proxy with HTTPS for production deployments
4. **Container Isolation**: ToolServerNode provides isolation for executed code

Sources: [docker-compose.yml:67-90](), [README.md:115-123]()

---

# Page: Developer Guide

# Developer Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [XAgentWeb/.gitignore](XAgentWeb/.gitignore)
- [XAgentWeb/components.d.ts](XAgentWeb/components.d.ts)
- [XAgentWeb/src/App.vue](XAgentWeb/src/App.vue)
- [XAgentWeb/src/components/Business/Feedback/index.vue](XAgentWeb/src/components/Business/Feedback/index.vue)
- [XAgentWeb/src/views/login/component/ApplyForm.vue](XAgentWeb/src/views/login/component/ApplyForm.vue)
- [XAgentWeb/tsconfig.json](XAgentWeb/tsconfig.json)
- [XAgentWeb/tsconfig.node.json](XAgentWeb/tsconfig.node.json)
- [requirements.txt](requirements.txt)
- [start_server.py](start_server.py)
- [tests/__init__.py](tests/__init__.py)
- [tests/test_1106_model_openai.py](tests/test_1106_model_openai.py)
- [tests/test_model_alias.py](tests/test_model_alias.py)
- [tests/test_run.py](tests/test_run.py)

</details>



This guide provides essential information for developers who want to contribute to the XAgent project. It covers development environment setup, project structure, coding standards, testing procedures, and component-specific guidelines. For user installation and usage instructions, please see [Installation and Setup](#1.2).

## Development Environment Setup

To set up a development environment for XAgent, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/OpenBMB/XAgent.git
   cd XAgent
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the web frontend** (if working on XAgentWeb):
   ```bash
   cd XAgentWeb
   npm install
   ```

4. **Create or edit configuration files**:
   Create appropriate configuration files by copying the examples:
   ```bash
   cp assets/config.example.yml assets/config.yml
   ```

5. **Install development tools**:
   ```bash
   pip install pytest
   ```

### Development Dependencies

The main Python dependencies required for development include:

| Category | Dependencies |
| --- | --- |
| Web Framework | fastapi, uvicorn, websockets |
| Data Processing | pydantic, jsonschema, orjson, PyYAML, json5 |
| Database | sqlalchemy, redis, pymysql |
| AI/LLM | openai, tiktoken, tenacity |
| Testing | pytest |
| UI/Display | termcolor, tqdm, Markdown, Pillow |
| Utilities | python-dotenv, requests, regex, colorama |

Sources: [requirements.txt:1-31]()

## Project Structure

XAgent is organized into several main components that work together to provide autonomous agent functionality.

```mermaid
graph TD
    subgraph "XAgent Project Structure"
        XAgentCore["XAgent Core"]
        ToolSrv["ToolServer"]
        XAgentSrv["XAgentServer"]
        XAgentWeb["XAgentWeb Frontend"]
        XAgentGen["XAgentGen"]
        Tests["Tests"]
        Assets["Configuration & Assets"]
    end
    
    XAgentCore -->|"orchestrates"| ToolSrv
    XAgentSrv -->|"uses"| XAgentCore
    XAgentSrv -->|"provides API for"| XAgentWeb
    XAgentCore -->|"may use"| XAgentGen
    Tests -->|"verifies"| XAgentCore
    Tests -->|"verifies"| ToolSrv
    Tests -->|"verifies"| XAgentSrv
    Assets -->|"configures"| XAgentCore
    Assets -->|"configures"| ToolSrv
    Assets -->|"configures"| XAgentSrv
```

Sources: [.gitignore:1-43]()

### Key Directories

| Directory | Purpose |
| --- | --- |
| `XAgent/` | Core XAgent functionality |
| `ToolServer/` | Tool execution environment |
| `XAgentServer/` | Backend server for web interface |
| `XAgentWeb/` | Web frontend |
| `XAgentGen/` | Custom model generation |
| `tests/` | Test files |
| `assets/` | Configuration files |
| `local_workspace/` | Local workspace for agent operations |

## Component Development Guidelines

### XAgent Core Development

The XAgent Core contains the main logic for the autonomous agent system. When developing for this component, focus on:

1. Task planning system
2. Tool system integration
3. LLM integration
4. Command line interface

```mermaid
graph TD
    subgraph "XAgent Core Development"
        ModelInteg["LLM Integration"]
        Planning["Task Planning"]
        Tools["Tool System"]
        CLI["Command Line Interface"]
        Recording["Task Recording"]
    end
    
    Planning -->|"creates tasks for"| Tools
    Tools -->|"provides results to"| Planning
    ModelInteg -->|"powers"| Planning
    ModelInteg -->|"supports"| Tools
    CLI -->|"initializes"| Planning
    Recording -->|"logs activity from"| Planning
    Recording -->|"logs activity from"| Tools
```

Sources: [tests/test_1106_model_openai.py:1-49](), [tests/test_model_alias.py:1-53]()

#### Testing XAgent Core

To test XAgent Core functionality, use the pytest framework. Test files should be placed in the `tests/` directory.

Example of testing command line functionality:

```python
# Test the command line argument parser
def test_parse_args(mock_argv):
    args = parse_args()
    assert args.task == "example_task"
    assert args.upload_files == ["file1", "file2"]
    assert args.model == "model1"
```

Sources: [tests/test_run.py:1-59]()

#### OpenAI Integration Testing

Testing the integration with OpenAI APIs is important for ensuring model compatibility:

```python
# Test compatibility with different OpenAI model versions
def test_model_alias():
    # Mock OpenAI client and responses
    with mock.patch("openai.OpenAI") as mock_openai:
        # Set up mock
        # Test functionality
        # Verify results
```

Sources: [tests/test_1106_model_openai.py:8-48](), [tests/test_model_alias.py:8-48]()

### ToolServer Development

When developing for the ToolServer component, consider:

1. Docker container integration
2. Tool implementation
3. Security considerations
4. Resource management

### XAgentServer Development

The XAgentServer handles client-server communication and coordinates between the web interface and XAgent Core:

1. FastAPI endpoint development
2. WebSocket communication
3. Database integration (MySQL and Redis)
4. Authentication and session management

```mermaid
graph TD
    subgraph "XAgentServer Development"
        FastAPI["FastAPI Application"]
        WebSockets["WebSocket Handlers"]
        DB["Database Modules"]
        Auth["Authentication"]
        XAgentIntegration["XAgent Integration"]
    end
    
    FastAPI -->|"includes"| WebSockets
    FastAPI -->|"includes"| DB
    FastAPI -->|"includes"| Auth
    FastAPI -->|"calls"| XAgentIntegration
    WebSockets -->|"updates"| DB
    Auth -->|"verifies against"| DB
```

Sources: [start_server.py:1-13]()

### XAgentWeb Development

For frontend development in XAgentWeb:

1. Vue.js component development
2. TypeScript configuration
3. WebSocket client implementation
4. UI/UX considerations

```mermaid
graph TD
    subgraph "XAgentWeb Development"
        VueComps["Vue Components"]
        TypeScript["TypeScript Configuration"]
        API["API Client"]
        UI["UI Components"]
        WebSocketClient["WebSocket Client"]
    end
    
    VueComps -->|"uses"| TypeScript
    VueComps -->|"includes"| UI
    VueComps -->|"communicates via"| API
    API -->|"includes"| WebSocketClient
    TypeScript -->|"validates"| API
```

Sources: [XAgentWeb/tsconfig.json:1-28](), [XAgentWeb/tsconfig.node.json:1-13](), [XAgentWeb/src/App.vue:1-40](), [XAgentWeb/components.d.ts:1-45]()

#### TypeScript Configuration

TypeScript is configured to provide type safety for the web frontend:

```typescript
// TypeScript configuration for Vue components
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "strict": true,
    "jsx": "preserve",
    // Additional configuration...
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"]
}
```

Sources: [XAgentWeb/tsconfig.json:1-27]()

#### Vue Components

The web interface is built using Vue.js components:

```vue
// Basic App component structure
<script setup lang="ts"></script>

<template><router-view /></template>

<style>
#app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
```

Sources: [XAgentWeb/src/App.vue:1-40]()

## Testing Guidelines

XAgent uses pytest for testing. Here are key guidelines for writing tests:

1. **Unit Tests**: Write tests for individual functions and classes
2. **Integration Tests**: Test interaction between components
3. **Mock External Services**: Use mock objects for external services like OpenAI

```python
# Example of testing with mocks
@patch('run.CommandLine')
def test_start_command_line(mock_command_line, mock_argv):
    args = parse_args()
    start_command_line(vars(args))
    
    called_args, _ = mock_command_line.call_args
    called_param = called_args[0]
    assert called_param.task == args.task
```

Sources: [tests/test_run.py:44-58]()

### Running Tests

To run tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_run.py

# Run with verbosity
pytest -v
```

## Contributing Workflow

1. **Fork the repository** on GitHub
2. **Create a feature branch** from main
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit with descriptive messages
4. **Write tests** for new functionality
5. **Submit a pull request** to the main repository

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Document functions and classes with docstrings
- For TypeScript code, follow the configured linting rules

## Troubleshooting Development Issues

### Common Issues

1. **Dependencies**:
   - Ensure all dependencies are installed with the correct versions
   - Check for conflicts between packages

2. **Configuration**:
   - Verify that configuration files exist and have the correct format
   - Check API keys and other credentials

3. **Docker Issues**:
   - For ToolServer, verify Docker is installed and running
   - Check container permissions and network settings

4. **Testing**:
   - Use mocks for external services to avoid rate limits or network issues
   - Isolate tests to prevent side effects

## System Integration

When making changes that span multiple components, consider the following integration diagram:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Git as "Git Repository"
    participant CI as "CI/CD Pipeline"
    participant Test as "Test Environment"
    
    Dev->>Git: Push code changes
    Git->>CI: Trigger CI pipeline
    CI->>CI: Run linting
    CI->>CI: Run unit tests
    CI->>Test: Deploy to test environment
    Test->>Test: Run integration tests
    Test->>Dev: Report test results
    
    alt Tests Pass
        Dev->>Git: Merge to main branch
    else Tests Fail
        Dev->>Dev: Fix issues
        Dev->>Git: Push fixes
    end
```

Sources: [tests/__init__.py:1]()

## Conclusion

This developer guide provides an overview of the XAgent development process. For more detailed information on specific components, refer to the corresponding sections in this wiki:

- [XAgent Core](#2)
- [ToolServer](#3)
- [XAgentServer](#4)
- [XAgentWeb](#5)
- [XAgentGen](#6)

Remember that XAgent is an evolving project, and contributions that improve functionality, performance, and documentation are always welcome.