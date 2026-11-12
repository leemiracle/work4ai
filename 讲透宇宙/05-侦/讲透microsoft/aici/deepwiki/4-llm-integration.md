<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/aici · page 4 LLM Integration · fetched 2026-10-26 -->

# LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.vscode/settings.json](.vscode/settings.json)
- [README.md](README.md)
- [aicirt/README.md](aicirt/README.md)

</details>



This page provides an overview of how the Artificial Intelligence Controller Interface (AICI) integrates with different Large Language Model (LLM) inference engines. AICI is designed to be LLM-agnostic, allowing controllers to work with various LLM backends without modification.

For information about specific LLM integrations, see:
- [vLLM Integration](#4.1)
- [HuggingFace Integration](#4.2)
- [rLLM Integration](#4.3)
- [llama.cpp Integration](#4.4)

## Architecture Overview

AICI is designed to sit between client applications and LLM inference engines, providing a standardized interface for controlling token generation. The system uses a multi-process architecture with shared memory for efficient communication between components.

```mermaid
graph TD
    subgraph "Client Applications"
        pyaici["pyaici Client"]
        rest["REST API Clients"]
    end
    
    subgraph "AICI System"
        aicirt["aicirt (AICI Runtime)"]
        controllers["WASM Controllers"]
    end
    
    subgraph "LLM Backends"
        rllm["rLLM"]
        vllm["vLLM"]
        hf["HuggingFace Transformers"]
        llamacpp["llama.cpp"]
    end
    
    pyaici --> aicirt
    rest --> aicirt
    
    aicirt <--> controllers
    
    aicirt <--> rllm
    aicirt <--> vllm
    aicirt <--> hf
    aicirt <--> llamacpp
```

Sources: [README.md:303-328]()

## Communication Protocol

AICI uses a standardized protocol for communication between the runtime and LLM backends. This protocol is based on POSIX shared memory (SHM) and allows for efficient exchange of token logits, constraints, and other information during the generation process.

```mermaid
sequenceDiagram
    participant Client
    participant LLM as "LLM Backend"
    participant AICI as "AICI Runtime"
    participant Controller as "WASM Controller"
    
    Client->>LLM: Request (Prompt + Controller)
    LLM->>AICI: Initialize with prompt and controller
    AICI->>Controller: Load and initialize
    Controller-->>AICI: Process prompt
    AICI-->>LLM: Processed prompt with constraints
    
    loop Token Generation
        LLM->>LLM: Generate logits
        LLM->>AICI: Send logits via SHM
        AICI->>Controller: Process logits
        Controller-->>AICI: Return constraints/biases
        AICI-->>LLM: Apply constraints via SHM
        LLM->>LLM: Sample token
        LLM->>Client: Return token
        LLM->>AICI: Notify token generated
        AICI->>Controller: Update state
    end
```

Sources: [aicirt/README.md:17-36]()

## Supported LLM Backends

AICI currently supports integration with the following LLM backends:

| Backend | Description | Status |
|---------|-------------|--------|
| rLLM | Custom LLM inference engine with CUDA and llama.cpp backends | Stable |
| vLLM | High-performance inference engine with PagedAttention | In progress |
| HuggingFace Transformers | Python-based LLM framework | Stable |
| llama.cpp | C++ inference engine for LLMs | Stable via rLLM |

Sources: [README.md:17](), [README.md:289-291]()

## Integration Architecture

The AICI runtime (`aicirt`) communicates with LLM backends through a well-defined protocol. This allows for a clean separation between the controller logic and the LLM inference engine.

```mermaid
graph TD
    subgraph "AICI Runtime Process"
        aicirt["aicirt Main Process"]
        spawner["Spawner Process"]
        worker["Worker Processes"]
        comms["Common State Process"]
    end
    
    subgraph "LLM Backend Process"
        llm["LLM Inference Engine"]
        gpu["GPU Execution"]
    end
    
    subgraph "Communication Layer"
        shm["Shared Memory (SHM)"]
        futex["Futexes/Semaphores"]
    end
    
    aicirt --> spawner
    spawner --> worker
    spawner --> comms
    
    aicirt <--> shm
    worker <--> shm
    llm <--> shm
    
    shm <--> futex
    
    llm --> gpu
```

Sources: [aicirt/README.md:38-82]()

## Integration Process Flow

When integrating AICI with an LLM backend, the following process flow is followed:

1. The LLM backend receives a request from a client
2. The LLM backend initializes the AICI runtime with the prompt and controller
3. The AICI runtime loads and initializes the controller
4. The controller processes the prompt and returns any initial constraints
5. The LLM backend generates logits for the next token
6. The logits are sent to the AICI runtime via shared memory
7. The AICI runtime passes the logits to the controller
8. The controller processes the logits and returns constraints or biases
9. The AICI runtime sends the constraints back to the LLM backend
10. The LLM backend applies the constraints and samples the next token
11. The process repeats until generation is complete

Sources: [aicirt/README.md:17-36]()

## Python Integration with pyaici

For Python-based LLM backends, AICI provides the `pyaici` package that simplifies integration. This package handles the communication with the AICI runtime and provides a Python-friendly interface for controlling token generation.

```mermaid
graph TD
    subgraph "Python LLM Backend"
        pyaici["pyaici Package"]
        hf["HuggingFace Integration"]
        vllm_py["vLLM Integration"]
    end
    
    subgraph "AICI Runtime"
        aicirt["aicirt Process"]
    end
    
    pyaici <--> aicirt
    hf --> pyaici
    vllm_py --> pyaici
```

Sources: [README.md:330-334]()

## rLLM Integration

rLLM is a custom LLM inference engine that comes with AICI and provides two backends:

1. `rllm-cuda`: A CUDA-based backend for high-performance inference on NVIDIA GPUs
2. `rllm-llamacpp`: A backend based on llama.cpp for CPU-based inference or GPUs without CUDA support

rLLM is tightly integrated with AICI and serves as the reference implementation for AICI integration.

```mermaid
graph TD
    subgraph "rLLM"
        rllm_base["rllm-base"]
        rllm_cuda["rllm-cuda"]
        rllm_llamacpp["rllm-llamacpp"]
    end
    
    subgraph "AICI Runtime"
        aicirt["aicirt"]
    end
    
    rllm_base --> rllm_cuda
    rllm_base --> rllm_llamacpp
    
    rllm_cuda <--> aicirt
    rllm_llamacpp <--> aicirt
```

Sources: [README.md:100-107](), [README.md:289-291]()

## Implementing New LLM Integrations

To add AICI support to a new LLM inference engine, you need to implement the LLM-side of the protocol that communicates with the AICI runtime. This involves:

1. Setting up shared memory for communication
2. Implementing the protocol for exchanging logits, constraints, and other information
3. Handling controller initialization and token generation flow

The existing integrations (rLLM, HuggingFace, etc.) can serve as reference implementations for new integrations.

Sources: [README.md:296-298]()

## Performance Considerations

When integrating AICI with an LLM backend, it's important to consider the performance implications. AICI is designed to minimize overhead during token generation, with most of the computation occurring on the CPU in parallel with logit generation on the GPU.

The typical overhead for AICI is around 0.3ms per generation step when executing 10 sequences in parallel, which is well within the 20-50ms budget for token generation on modern GPUs.

Sources: [README.md:350-386]()

## Security Considerations

AICI provides a secure environment for running controllers by:

1. Running the AICI runtime in a separate process from the LLM engine
2. Sandboxing WebAssembly modules using Wasmtime
3. Limiting access to system resources (filesystem, network, etc.)
4. Running each WebAssembly module in a separate process for isolation

These security measures ensure that controllers cannot access sensitive resources or interfere with the LLM engine.

Sources: [README.md:338-349]()

---

