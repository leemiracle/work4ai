<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/WindowsAgentArena · page 4 System Components · fetched 2026-10-26 -->

# System Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page provides a comprehensive overview of the Windows Agent Arena (WAA) system components, their purpose, and how they interact with each other. For installation instructions, see [Installation and Setup](#2), and for running experiments, see [Running Experiments](#3).

## Overview

The Windows Agent Arena consists of several interconnected components that work together to provide a platform for evaluating multi-modal AI agents in a Windows environment. The system is designed to be modular, allowing for different components to be swapped or upgraded independently.

```mermaid
graph TD
    subgraph "Container Layer"
        dockerContainer["Docker Container<br>windowsarena/winarena"]
    end
    
    subgraph "Core System Components"
        winVM["Windows 11 VM"]
        server["Windows Arena Server"]
        clientApp["Client Application"]
        naviAgent["Navi Agent"]
        screenUnd["Screen Understanding"]
    end
    
    dockerContainer --> winVM
    dockerContainer --> clientApp
    clientApp --> naviAgent
    naviAgent --> screenUnd
    clientApp <--> server
    server <--> winVM
    
    class naviAgent,screenUnd style="stroke-dasharray: 5 5"
    class winVM,server style="stroke-width:2px"
    class clientApp style="stroke-width:2px"
```

Sources: [README.md:12-14]()

## Windows Arena Container

The Windows Arena Container is the foundational component that encapsulates the entire system. It uses Docker to provide a consistent and reproducible environment for running experiments.

### Container Structure

```mermaid
graph TD
    subgraph "Docker Container Components"
        base["windowsarena/winarena-base<br>Base image with dependencies"]
        main["windowsarena/winarena<br>Main container with code"]
        entrypoint["entry.sh<br>Container entrypoint"]
        storage["VM Storage<br>Windows 11 snapshot"]
    end
    
    base --> main
    main --> entrypoint
    storage --> main
    
    subgraph "Runtime Components"
        qemu["QEMU/KVM<br>VM Hypervisor"]
        python["Python Environment<br>For client application"]
    end
    
    main --> qemu
    main --> python
```

Sources: [README.md:72-99]()

The container provides:
- A consistent environment for running the Windows VM
- QEMU/KVM virtualization for the Windows 11 VM
- Python environment for the client application
- Storage for the Windows 11 VM snapshot (golden image)

## Windows VM

The Windows 11 VM runs inside the Docker container and provides the operating system environment where tasks are executed. For detailed documentation, see [Windows VM](#4.1).

Key characteristics:
- Based on Windows 11 Enterprise Evaluation
- Pre-configured with necessary software for the benchmark tasks
- Contains the Windows Arena Server for receiving and executing commands

Sources: [README.md:101-150]()

## Server Application

The Server Application runs inside the Windows VM and provides an API for interacting with the Windows environment. For detailed documentation, see [Server Application](#4.3).

```mermaid
graph LR
    subgraph "Server Components"
        server["main.py<br>Flask Server"]
        computerController["computer.py<br>Computer Control"]
        screenCapture["Screenshot APIs"]
        a11yTree["Accessibility Tree APIs"]
        actionExecution["Action Execution APIs"]
    end
    
    server --> computerController
    computerController --> screenCapture
    computerController --> a11yTree
    computerController --> actionExecution
```

Sources: [README.md:101-150]()

The server provides APIs for:
- Capturing screenshots
- Retrieving accessibility tree information
- Executing actions (mouse clicks, keyboard input, etc.)
- Managing the Windows environment

## Client Application

The Client Application runs inside the Docker container (but outside the Windows VM) and coordinates the execution of experiments. For detailed documentation, see [Client Application](#4.2).

```mermaid
graph TD
    subgraph "Client Components"
        runPy["run.py<br>Main entry point"]
        libRunSingle["lib_run_single.py<br>Single example executor"]
        desktopEnv["desktop_env.py<br>Environment interface"]
        trajectoryRec["trajectory_recorder.py<br>Recording actions"]
    end
    
    runPy --> libRunSingle
    libRunSingle --> desktopEnv
    libRunSingle --> trajectoryRec
    
    subgraph "VM Communication"
        vmController["VMController<br>VM management"]
        serverComm["Server communication<br>HTTP requests"]
    end
    
    desktopEnv --> vmController
    desktopEnv --> serverComm
    
    subgraph "Agent Interface"
        agentLoader["Agent loading"]
    end
    
    runPy --> agentLoader
```

Sources: [README.md:12-14](), [README.md:176-197]()

The client application:
- Loads and initializes agents
- Communicates with the Windows Arena Server
- Manages the execution of tasks
- Records trajectories (sequence of actions and observations)
- Evaluates agent performance

## Navi Agent

The Navi Agent is the default agent provided with the Windows Agent Arena. It uses GPT-4 or other LLMs to understand the screen and decide what actions to take. For detailed documentation, see [Navi Agent](#4.4).

```mermaid
graph TD
    subgraph "Agent Architecture"
        naviAgent["NaviAgent<br>Base agent class"]
        predict["predict()<br>Main inference function"]
        reset["reset()<br>Reset agent state"]
    end
    
    subgraph "Screen Understanding"
        screenUnd["Screen Understanding<br>Various modes"]
        ossMode["OSS Mode<br>Webparse + GroundingDINO + OCR"]
        a11yMode["A11y Mode<br>Accessibility tree"]
        omniMode["Omni Mode<br>Omniparser"]
        mixedMode["Mixed Mode<br>Combined approaches"]
    end
    
    subgraph "LLM Integration"
        llmModule["LLM Module<br>API integration"]
        prompt["Prompt Engineering"]
    end
    
    naviAgent --> predict
    naviAgent --> reset
    predict --> screenUnd
    predict --> llmModule
    screenUnd --> ossMode
    screenUnd --> a11yMode
    screenUnd --> omniMode
    screenUnd --> mixedMode
    llmModule --> prompt
```

Sources: [README.md:186-197]()

The Navi Agent features:
- Multiple screen understanding modes (OSS, A11y, Omni, Mixed)
- Integration with LLMs (GPT-4, GPT-4o, Claude)
- Task-specific prompt engineering
- Action generation and execution

## Screen Understanding

The Screen Understanding component is responsible for parsing the Windows screen and providing a structured representation to the agent. For detailed documentation, see [Screen Understanding](#4.5).

```mermaid
graph LR
    subgraph "Screen Understanding Modes"
        screenUnd["Screen Understanding"]
        
        subgraph "OSS Mode"
            webparse["Webparse<br>Web element detection"]
            dino["GroundingDINO<br>Object detection"]
            ocr["TesseractOCR<br>Text recognition"]
        end
        
        subgraph "A11y Mode"
            uia["UIA Backend<br>Slower, more accurate"]
            win32["Win32 Backend<br>Faster, less accurate"]
        end
        
        subgraph "Omni Mode"
            omniparser["Omniparser<br>Microsoft screen parsing model"]
        end
        
        subgraph "Mixed Mode"
            mixedOSS["Mixed-OSS<br>Combines OSS with A11y"]
            mixedOmni["Mixed-Omni<br>Combines Omni with A11y"]
        end
    end
    
    screenUnd --> webparse
    screenUnd --> dino
    screenUnd --> ocr
    screenUnd --> uia
    screenUnd --> win32
    screenUnd --> omniparser
    screenUnd --> mixedOSS
    screenUnd --> mixedOmni
```

Sources: [README.md:186-197]()

The Screen Understanding component provides different modes:
- OSS Mode: Uses web parsing, object detection, and OCR
- A11y Mode: Uses the Windows accessibility tree with UIA or Win32 backends
- Omni Mode: Uses Microsoft's Omniparser model
- Mixed Mode: Combines different approaches for better performance

## Component Interactions

The following diagram illustrates how the components interact during the execution of a task:

```mermaid
sequenceDiagram
    participant Client as Client Application
    participant Agent as Navi Agent
    participant Server as Windows Arena Server
    participant VM as Windows 11 VM
    
    Client->>Agent: Initialize with task
    
    loop Task Execution
        Agent->>Client: Request observation
        Client->>Server: Request screenshot/a11y
        Server->>VM: Capture screenshot/a11y
        VM->>Server: Return screen data
        Server->>Client: Return screen data
        Client->>Agent: Provide observation
        
        Agent->>Agent: Process with LLM
        Agent->>Client: Return action
        
        Client->>Server: Execute action
        Server->>VM: Perform action
        VM->>Server: Return result
        Server->>Client: Return status
        
        Client->>Client: Record to trajectory
        
        alt Task Complete
            Client->>Client: Evaluate success
            Client->>Agent: Reset for next task
        end
    end
```

Sources: [README.md:12-14]()

## Deployment Options

The Windows Agent Arena supports two deployment options: local and Azure.

| Feature | Local Deployment | Azure Deployment |
|---------|------------------|------------------|
| Container | Single Docker container | Multiple containers on Azure VMs |
| Execution | Sequential (one task at a time) | Parallel (multiple tasks simultaneously) |
| Setup | Local machine resources | Azure ML computing resources |
| Performance | Limited by local hardware | Scalable cloud resources |
| Use Case | Development, testing | Large-scale benchmarking |

Sources: [README.md:58-150](), [README.md:204-327]()

### Local Deployment Architecture

```mermaid
graph TD
    subgraph "Local Machine"
        docker["Docker Engine"]
        container["Windows Arena Container"]
    end
    
    subgraph "Container Components"
        vm["Windows 11 VM"]
        client["Client Application"]
        server["Windows Arena Server"]
        agent["Navi Agent"]
    end
    
    docker --> container
    container --> vm
    container --> client
    vm --> server
    client --> agent
    client <--> server
```

Sources: [README.md:58-150]()

### Azure Deployment Architecture

```mermaid
graph TD
    subgraph "Azure ML"
        azureML["Azure ML Service"]
        computeVMs["Multiple Compute VMs"]
    end
    
    subgraph "Each Compute VM"
        container["Windows Arena Container"]
        vm["Windows 11 VM"]
        client["Client Application"]
        server["Windows Arena Server"]
        agent["Navi Agent"]
    end
    
    azureML --> computeVMs
    computeVMs --> container
    container --> vm
    container --> client
    vm --> server
    client --> agent
    client <--> server
```

Sources: [README.md:204-327]()

## Data Flow

The following diagram illustrates the data flow through the system during task execution:

```mermaid
flowchart LR
    subgraph "Input Flow"
        task["Task Configuration"]
        screenshotData["Screenshot Data"]
        a11yData["Accessibility Data"]
    end
    
    subgraph "Processing"
        screenParsing["Screen Parsing"]
        llmProcessing["LLM Processing"]
        actionGeneration["Action Generation"]
    end
    
    subgraph "Output Flow"
        actionExecution["Action Execution"]
        trajectoryRecord["Trajectory Recording"]
        evaluationResult["Evaluation Result"]
    end
    
    task --> screenParsing
    screenshotData --> screenParsing
    a11yData --> screenParsing
    
    screenParsing --> llmProcessing
    llmProcessing --> actionGeneration
    
    actionGeneration --> actionExecution
    actionExecution --> trajectoryRecord
    trajectoryRecord --> evaluationResult
```

Sources: [README.md:176-197]()

The data flow encompasses:
1. Input: Task configuration and screen data (screenshots, accessibility info)
2. Processing: Screen parsing, LLM processing, and action generation
3. Output: Action execution, trajectory recording, and evaluation results

---

