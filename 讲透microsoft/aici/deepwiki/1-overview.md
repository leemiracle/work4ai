<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/aici · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.vscode/settings.json](.vscode/settings.json)
- [README.md](README.md)
- [aicirt/README.md](aicirt/README.md)
- [aicirt/src/api.rs](aicirt/src/api.rs)
- [aicirt/src/hostimpl.rs](aicirt/src/hostimpl.rs)
- [aicirt/src/main.rs](aicirt/src/main.rs)
- [aicirt/src/moduleinstance.rs](aicirt/src/moduleinstance.rs)
- [aicirt/src/worker.rs](aicirt/src/worker.rs)

</details>



The Artificial Intelligence Controller Interface (AICI) is a system that enables fine-grained control over large language model (LLM) inference. It provides a framework for building Controllers that can constrain and direct the output of LLMs in real-time during the token generation process.

This document introduces the core architecture of AICI, its key components, and how they interact to provide controlled text generation. For detailed information about specific components, please refer to their respective wiki pages.

## What is AICI?

AICI is designed to be a layer in the LLM inference stack that separates the control logic from the inference engine. It allows developers to implement custom Controllers that can:

- Constrain token generation using various methods (regex, grammars, etc.)
- Maintain state during generation
- Backtrack to previous states
- Fork generation into multiple branches
- Fast-forward tokens when they are known in advance

Sources: [README.md:4-17](), [README.md:303-316]()

## System Architecture

```mermaid
graph TD
    subgraph "AICI Core Components"
        aicirt["aicirt (AICI Runtime)"]
        controllers["Controllers (WASM Modules)"]
        abi["AICI ABI"]
    end
    
    subgraph "LLM Integration"
        rllm["rLLM"]
        vllm["vLLM Integration"]
        hf["HuggingFace Integration"]
        llamacpp["llama.cpp Integration"]
    end
    
    subgraph "Python Interface"
        pyaici["pyaici"]
        guidance["Guidance"]
        promptlib["PromptLib"]
    end
    
    subgraph "Controller Types"
        pyctrl["Python Controller (pyctrl)"]
        jsctrl["JavaScript Controller (jsctrl)"]
        declctrl["Declarative Controller (declctrl)"]
        llguidance["LLGuidance Controller"]
    end
    
    aicirt --- abi
    controllers --- abi
    
    pyaici --- aicirt
    pyaici --- vllm
    pyaici --- hf
    
    rllm --- aicirt
    vllm --- aicirt
    hf --- aicirt
    llamacpp --- aicirt
    
    guidance --- llguidance
    promptlib --- declctrl
    
    controllers --- pyctrl
    controllers --- jsctrl
    controllers --- declctrl
    controllers --- llguidance
```

Sources: [README.md:303-316](), [README.md:317-328]()

## AICI Runtime Architecture

The AICI Runtime (`aicirt`) is the central component that manages the execution of WebAssembly (WASM) controllers and communicates with LLM inference engines. It uses a multi-process architecture for isolation and security.

```mermaid
graph TD
    subgraph "AICI Runtime (aicirt)"
        main["Main Process"]
        spawner["Spawner Process"]
        worker["Worker Processes"]
        comms["Common State Process"]
    end
    
    subgraph "Communication"
        shm["Shared Memory (SHM)"]
        futex["Futex/Semaphores"]
        msgchannel["Message Channels"]
    end
    
    subgraph "LLM Engine"
        llm["LLM Inference Engine"]
        gpu["GPU Execution"]
    end
    
    main --> spawner
    spawner --> worker
    spawner --> comms
    worker --- comms
    
    main --- shm
    worker --- shm
    comms --- shm
    
    shm --- futex
    shm --- msgchannel
    
    llm --- shm
    llm --> gpu
```

Sources: [aicirt/README.md:1-36](), [aicirt/src/main.rs:39-47]()

## Token Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant LLM as "LLM Engine"
    participant AICI as "AICI Runtime"
    participant Controller as "WASM Controller"
    
    User->>LLM: Request (Prompt + Controller)
    LLM->>AICI: Forward request
    AICI->>Controller: Initialize
    Controller-->>AICI: Process prompt
    AICI-->>LLM: Processed prompt
    
    loop Token Generation
        LLM->>LLM: Generate logits
        LLM->>AICI: Send logits
        AICI->>Controller: Mid-process
        Controller-->>AICI: Logit bias, constraints
        AICI-->>LLM: Apply constraints
        LLM->>LLM: Sample token
        LLM->>User: Return token
        LLM->>AICI: Token generated
        AICI->>Controller: Update state
    end
```

Sources: [aicirt/README.md:17-36](), [aicirt/src/main.rs:637-903]()

## Key Components

### AICI Runtime (aicirt)

The AICI Runtime is a multi-threaded runner for AICI Controllers, built on top of Wasmtime. It manages the lifecycle of controller instances, handles communication between the LLM and controllers, and provides isolation between different user requests.

Key features:
- Multi-process architecture for security and isolation
- Shared memory communication for efficiency
- Support for forking, backtracking, and fast-forwarding

Sources: [aicirt/README.md:1-16](), [aicirt/src/main.rs:5-18]()

### Controllers

Controllers are WebAssembly modules that implement custom logic for controlling token generation. They can be written in any language that compiles to WebAssembly (Rust, C, C++, etc.) or be interpreted inside WebAssembly (Python, JavaScript, etc.).

AICI provides several built-in controller types:
- **Python Controller (pyctrl)**: Allows writing controllers in Python
- **JavaScript Controller (jsctrl)**: Allows writing controllers in JavaScript
- **Declarative Controller (declctrl)**: Uses declarative specifications
- **LLGuidance Controller**: Grammar-based guidance

Sources: [README.md:19-26](), [README.md:145-147]()

### AICI ABI

The AICI Application Binary Interface (ABI) defines how controllers interact with the runtime. It provides functions for:
- Tokenization and detokenization
- Logit biasing
- State management
- Communication between controller instances

Sources: [aicirt/src/hostimpl.rs:418-539]()

### Module Registry

The Module Registry manages WASM modules, including their storage, compilation, and instantiation. It provides functions for:
- Creating and storing modules
- Tagging modules for easy reference
- Instantiating modules for execution

Sources: [aicirt/src/main.rs:173-447]()

## Process Model

```mermaid
graph TD
    subgraph "Process Structure"
        aicirt["AICI Runtime (Main Process)"]
        spawner["Spawner Process"]
        
        subgraph "User Request A"
            A0["Controller A0"]
            A1["Controller A1"]
            A2["Controller A2"]
            CommsA["Common State A"]
        end
        
        subgraph "User Request B"
            B0["Controller B0"]
            B1["Controller B1"]
            CommsB["Common State B"]
        end
    end
    
    aicirt --> spawner
    aicirt -.-> A0
    aicirt -.-> A1
    aicirt -.-> A2
    aicirt -.-> B0
    aicirt -.-> B1
    
    spawner --> A0
    spawner --> CommsA
    spawner --> B0
    spawner --> CommsB
    
    A0 --> A1
    A0 --> A2
    B0 --> B1
    
    A0 -.-> CommsA
    A1 -.-> CommsA
    A2 -.-> CommsA
    
    B0 -.-> CommsB
    B1 -.-> CommsB
```

Sources: [aicirt/README.md:38-82](), [aicirt/src/worker.rs:559-691]()

## Security Model

AICI is designed with security in mind:

- `aicirt` runs in a separate process from the LLM engine
- WebAssembly modules are sandboxed by Wasmtime
- Controllers only have access to explicitly exposed host functions
- Each WebAssembly module runs in a separate process for Spectre/Meltdown mitigation
- Controllers cannot access the filesystem, network, or other resources

Sources: [README.md:337-349](), [aicirt/src/moduleinstance.rs:30-98]()

## Performance Considerations

AICI is designed to be efficient:

- Most computation in Controllers occurs on the CPU, in parallel with logit generation on the GPU
- The generation process is divided into steps, with each step taking about 20-50ms on modern GPUs
- WebAssembly provides near-native performance (less than 2x overhead compared to native code)
- Constraints like regular expressions, grammars, and substring matching are highly optimized

Sources: [README.md:350-388](), [aicirt/src/main.rs:40-46]()

## Integration with LLM Engines

AICI can integrate with various LLM inference engines:

- rLLM (custom tch-based LLM inference engine)
- llama.cpp
- HuggingFace Transformers
- vLLM (in development)

The integration is done through a shared memory interface, allowing efficient communication between the LLM engine and AICI runtime.

Sources: [README.md:17-18](), [README.md:323-328]()

## Conclusion

AICI provides a flexible and efficient framework for controlling LLM generation. By separating the control logic from the inference engine, it enables developers to implement complex control strategies without modifying the underlying LLM code. The WebAssembly-based architecture ensures security, portability, and performance.

For more detailed information about specific components, please refer to their respective wiki pages:
- [AICI Runtime (aicirt)](#2)
- [Controllers](#3)
- [LLM Integration](#4)
- [Python Interface (pyaici)](#5)

---

