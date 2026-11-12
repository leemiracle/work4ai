<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/meshgen · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [__init__.py](__init__.py)
- [backend.py](backend.py)
- [preferences.py](preferences.py)
- [tools.py](tools.py)

</details>



This document provides a comprehensive overview of the MeshGen addon's architecture, explaining how the various components interact to create an AI-powered 3D mesh generation system within Blender. For information about installation and setup, see [Installation and Setup](#2), and for details about specific subsystems, see the corresponding pages in [Backend System](#3.1), [Tools System](#3.2), and [State Management](#3.3).

## Core Architecture Overview

MeshGen is built as a Blender addon that integrates language models with Blender's 3D modeling capabilities. The system follows a modular architecture that separates concerns between user interface, backend model management, tool execution, and state tracking.

```mermaid
flowchart TD
    subgraph "User Interface Layer"
        UI["UI Panel"]
        Props["Properties"]
        Ops["Operators"]
    end

    subgraph "Backend Layer"
        BackendMgr["Backend Manager"]
        LLM["Language Models"]
        Agent["Code Agent"]
    end

    subgraph "Tool Execution Layer"
        ToolMgr["Tool Manager"]
        Tools["Blender Tools"]
    end

    subgraph "Configuration"
        Prefs["Preferences"]
    end

    UI -->|"User prompt"| Ops
    Ops -->|"Execute"| BackendMgr
    Ops -->|"Update state"| Props
    UI -->|"Display"| Props
    
    BackendMgr -->|"Initialize"| LLM
    BackendMgr -->|"Create"| Agent
    Prefs -->|"Configure"| BackendMgr
    
    Agent -->|"Use"| ToolMgr
    ToolMgr -->|"Execute in main thread"| Tools
    Tools -->|"Manipulate"| Blender["Blender Objects"]
```

Sources: [__init__.py:33-52](), [backend.py:12-25](), [tools.py:12-90]()

## Component Relationships

The MeshGen addon consists of several key components that work together:

| Component | Purpose | Key Classes | File |
|-----------|---------|-------------|------|
| UI Layer | User interaction | UI panels, operators | ui.py, operators.py |
| Backend | Language model management | `Backend` | backend.py |
| Tool System | Blender operations execution | `ToolManager`, `BlenderTool` | tools.py |
| Configuration | User preferences | `MeshGenPreferences` | preferences.py |
| State | Tracking conversation state | `MeshGenProperties` | properties.py |

### Module Dependencies

```mermaid
graph TD
    init["__init__.py"] -->|"Registers"| operators["operators.py"]
    init -->|"Registers"| ui["ui.py"]
    init -->|"Registers"| prefs["preferences.py"]
    init -->|"Registers"| props["properties.py"]
    
    operators -->|"Uses"| backend["backend.py"]
    operators -->|"Updates"| props
    
    backend -->|"Uses"| tools["tools.py"]
    backend -->|"Configured by"| prefs
    
    ui -->|"Displays"| props
    ui -->|"Calls"| operators
```

Sources: [__init__.py:1-57]()

## Backend System Architecture

The backend system is responsible for managing language models and processing user prompts through an agent.

```mermaid
classDiagram
    class Backend {
        -_instance: Backend
        -_lock: threading.Lock
        -model: Model
        -agent: CodeAgent
        +instance(): Backend
        +is_valid(): bool
        +is_loaded(): bool
        +load()
        +start_chat_completion(messages, temperature, stop_event)
        +reset()
    }
    
    class BackendTypes {
        <<enumeration>>
        LOCAL
        REMOTE
    }
    
    class RemoteProviders {
        <<enumeration>>
        huggingface
        ollama
        anthropic
        openai
    }
    
    Backend --> BackendTypes : supports
    BackendTypes --> RemoteProviders : has providers
```

Sources: [backend.py:12-228](), [preferences.py:35-53](), [preferences.py:70-83]()

### Backend Configuration

The backend system supports two main types of backends:

1. **Local Backend**: Runs models directly within Blender using llama_cpp_python
2. **Remote Backend**: Connects to external API services

```mermaid
flowchart TD
    Backend["Backend"]
    
    subgraph "Backend Types"
        Local["Local Backend"]
        Remote["Remote Backend"]
    end
    
    Backend --> Local
    Backend --> Remote
    
    Local -->|"Uses"| LlamaCpp["llama_cpp_python"]
    Local -->|"Loads models from"| ModelsDir[".models directory"]
    
    Remote -->|"Provider"| HF["Hugging Face API"]
    Remote -->|"Provider"| Ollama["Ollama API"]
    Remote -->|"Provider"| Anthropic["Anthropic API"]
    Remote -->|"Provider"| OpenAI["OpenAI API"]
    
    Prefs["MeshGenPreferences"] -->|"Configures"| Backend
```

Sources: [backend.py:57-136](), [preferences.py:35-143]()

## Tool Management System

The tool management system is responsible for executing operations in Blender's main thread, ensuring thread safety while allowing the AI agent to control Blender.

```mermaid
classDiagram
    class ToolManager {
        -_instance: ToolManager
        -_task_queue: Queue
        -_result_dict: Dict
        -_tools: List[Tool]
        +instance(): ToolManager
        +add_task(task): void
        +get_result(task_id): Any
        +process_tasks(context): void
    }
    
    class BlenderTool {
        +name: str
        +description: str
        +inputs: Dict
        +output_type: str
        +run_main_thread_func(func, params): str
        +forward(...): Any
    }
    
    BlenderTool <|-- GetSceneInfoTool
    BlenderTool <|-- GetObjectInfoTool
    BlenderTool <|-- CreateObjectTool
    BlenderTool <|-- ModifyObjectTool
    BlenderTool <|-- DeleteObjectTool
    BlenderTool <|-- SetMaterialTool
    BlenderTool <|-- LlamaMeshGenerateTool
    BlenderTool <|-- LlamaMeshDescribeTool
    BlenderTool <|-- Hyper3dGenerateObjectTool
    
    ToolManager "1" --> "*" BlenderTool : manages
```

Sources: [tools.py:12-90](), [tools.py:92-112](), [tools.py:164-833]()

### Tool Execution Flow

```mermaid
sequenceDiagram
    participant Agent as "CodeAgent"
    participant Tool as "BlenderTool"
    participant Manager as "ToolManager"
    participant Main as "Blender Main Thread"
    
    Agent->>Tool: forward(params)
    Tool->>Tool: prepare parameters
    Tool->>Manager: run_main_thread_func(func, params)
    Manager->>Manager: add_task(task)
    Main->>Manager: process_tasks(context)
    Main->>Main: execute function
    Main->>Manager: store result
    Manager->>Tool: return result
    Tool->>Agent: return formatted result
```

Sources: [tools.py:99-111](), [tools.py:55-64](), [tools.py:66-82]()

## Code Agent System

The CodeAgent is the bridge between natural language prompts and concrete actions in Blender, using a language model to understand user intent.

```mermaid
flowchart TD
    User["User"] -->|"Text prompt"| UI["UI Panel"]
    UI -->|"Forward prompt"| Backend["Backend"]
    
    Backend -->|"Run agent"| Agent["CodeAgent"]
    
    subgraph "Agent Processing"
        Agent -->|"Generate thought"| Thought["Thinking"]
        Thought -->|"Decide action"| Action["Tool Selection"]
        Action -->|"Execute tool"| Tool["Tool Execution"]
        Tool -->|"Observe result"| Observation["Result Observation"]
        Observation -->|"Continue reasoning"| Thought
        Thought -->|"Reach conclusion"| FinalAnswer["Final Answer"]
    end
    
    FinalAnswer -->|"Return to user"| UI
```

Sources: [backend.py:140-156](), [backend.py:158-179](), [backend.py:180-204]()

## State Management

MeshGen implements a state machine to track the status of user interactions and AI processing.

```mermaid
stateDiagram-v2
    [*] --> READY: Initial State
    
    READY --> LOADING: Backend.load()
    LOADING --> READY: Loading error
    LOADING --> RUNNING: Loading completed
    
    READY --> RUNNING: Submit prompt
    RUNNING --> THINKING: Agent thinking
    THINKING --> STEP: Agent produces step
    STEP --> THINKING: Continue thinking
    
    THINKING --> FINAL_ANSWER: Agent completes
    THINKING --> ERROR: Error occurs
    THINKING --> CANCELED: User cancels
    
    FINAL_ANSWER --> READY: Reset state
    ERROR --> READY: Reset state
    CANCELED --> READY: Reset state
```

Sources: [preferences.py:18-29](), [backend.py:158-179]()

## Integration Architecture

MeshGen supports integrations with external libraries and services to enhance mesh generation capabilities.

```mermaid
flowchart TD
    MeshGen["MeshGen Core"]
    
    subgraph "Integrations"
        LlamaMesh["LLaMA-Mesh Integration"]
        Hyper3D["Hyper3D Integration"]
    end
    
    MeshGen -->|"Optional"| LlamaMesh
    MeshGen -->|"Optional"| Hyper3D
    
    subgraph "LLaMA-Mesh Features"
        LlamaMeshGen["Generate Mesh from Text"]
        LlamaMeshDesc["Describe 3D Object"]
    end
    
    LlamaMesh --> LlamaMeshGen
    LlamaMesh --> LlamaMeshDesc
    
    subgraph "Hyper3D Features"
        Hyper3DGen["Generate High-Quality 3D Object"]
    end
    
    Hyper3D --> Hyper3DGen
```

Sources: [tools.py:842-893](), [tools.py:974-1038](), [tools.py:1110-1155](), [tools.py:1158-1350](), [preferences.py:175-184]()

## Data Flow

The following diagram illustrates how data flows through the MeshGen system, from user input to 3D model creation:

```mermaid
flowchart LR
    User["User"] -->|"Natural language prompt"| UI["Blender UI Panel"]
    UI -->|"Text prompt"| Operators["MeshGen Operators"]
    
    Operators -->|"Forward prompt"| Backend["Backend Manager"]
    Backend -->|"Process with LLM"| Agent["CodeAgent"]
    
    Agent -->|"Execute tools"| ToolMgr["Tool Manager"]
    ToolMgr -->|"Run in main thread"| BlenderAPI["Blender API"]
    
    BlenderAPI -->|"Create/modify"| Objects["3D Objects"]
    BlenderAPI -->|"Set"| Materials["Materials"]
    
    Objects --> Scene["Blender Scene"]
    Materials --> Scene
    
    Scene -->|"Visual feedback"| User
```

Sources: [__init__.py:33-52](), [backend.py:158-179](), [tools.py:278-408](), [tools.py:66-82]()

## System Initialization

The initialization flow for MeshGen shows how components are registered and loaded:

```mermaid
sequenceDiagram
    participant Blender as "Blender"
    participant Init as "__init__.py"
    participant Operators as "operators.py"
    participant UI as "ui.py"
    participant Prefs as "preferences.py"
    participant Props as "properties.py"
    
    Blender->>Init: register()
    Init->>Operators: register()
    Init->>UI: register()
    Init->>Prefs: register()
    Init->>Props: register()
    
    Prefs->>Blender: Register MeshGenPreferences
    Props->>Blender: Register MeshGenProperties
    UI->>Blender: Register UI panels
    Operators->>Blender: Register operators
```

Sources: [__init__.py:34-40]()

## Conclusion

The MeshGen architecture is designed with modularity and extensibility in mind. By separating concerns between the UI, backend, and tool execution layers, the system can support multiple model backends and tool implementations while maintaining a consistent user experience.

For more detailed information about specific subsystems, see the corresponding wiki pages:
- [Backend System](#3.1) for details on language model management
- [Tools System](#3.2) for information about tool implementation and execution
- [State Management](#3.3) for details on conversation state tracking

---

