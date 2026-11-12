<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/web-ui · page 2 System Architecture · fetched 2026-10-30 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/webui/interface.py](src/webui/interface.py)
- [src/webui/webui_manager.py](src/webui/webui_manager.py)
- [webui.py](webui.py)

</details>



## Purpose and Scope

This document explains the high-level layered design of the browser-use web-ui system, its deployment models, and how components interact across the user interface, agent, browser, and LLM tiers. 

Because this is a parent page, it provides a high-level overview of the architecture and points to dedicated child pages for deep technical details:
- For application startup, CLI arguments, and Gradio tab assembly, see [Application Entrypoint and Interface Assembly](#2.1).
- For component registration, state management, chat history, and configuration persistence, see [WebuiManager and State Flow](#2.2).

**Sources:** [webui.py:1-19](), [src/webui/interface.py:1-95](), [src/webui/webui_manager.py:1-122]()

---

## System Layers

The system follows a strict layered architecture separating concerns from the Gradio interface down to Playwright browser automation and multi-provider LLM inference.

### Layered Architecture Overview

The following diagram bridges natural language functional concepts to code entities (`webui.py`, `interface.py`, `WebuiManager`, `CustomBrowser`, `CustomController`, `get_llm_model`) within the codebase:

```mermaid
graph TB
    subgraph "Layer 1: User Interface"
        webui["webui.py<br/>main()"]
        interface["src/webui/interface.py<br/>create_ui()"]
        mgr["src/webui/webui_manager.py<br/>WebuiManager"]
    end
    
    subgraph "Layer 2: Agent Orchestration"
        bu_agent["browser_use.agent.service.Agent"]
        dr_agent["src/agent/deep_research_agent.py<br/>DeepResearchAgent"]
        controller["src/controller/custom_controller.py<br/>CustomController"]
    end
    
    subgraph "Layer 3: Browser Automation"
        custom_browser["src/browser/custom_browser.py<br/>CustomBrowser"]
        custom_context["src/browser/custom_context.py<br/>CustomBrowserContext"]
    end
    
    subgraph "Layer 4: LLM Integration"
        llm_provider["src/llm/llm_provider.py<br/>get_llm_model()"]
    end
    
    webui --> interface
    interface --> mgr
    interface --> bu_agent
    interface --> dr_agent
    bu_agent --> controller
    dr_agent --> controller
    bu_agent --> custom_browser
    dr_agent --> custom_browser
    custom_browser --> custom_context
    bu_agent --> llm_provider
    dr_agent --> llm_provider
```

**Sources:** [webui.py:1-19](), [src/webui/interface.py:1-95](), [src/webui/webui_manager.py:1-122]()

### Layer Responsibilities

| Layer | Primary Code Entities | Responsibilities |
|-------|----------------------|------------------|
| **User Interface** | `webui.py`, `src/webui/interface.py`, `src/webui/webui_manager.py` | CLI parsing, Gradio block assembly, layout themes (`theme_map`), and state coordination |
| **Agent Orchestration** | `Agent`, `DeepResearchAgent`, `CustomController` | Task execution loops, action registration, step planning, and tool dispatch |
| **Browser Automation** | `CustomBrowser`, `CustomBrowserContext` | Playwright lifecycle control, CDP port binding, user data directories, and isolation |
| **LLM Integration** | `src/llm/llm_provider.py` | Multi-provider chat model instantiation and fallback handling |

**Sources:** [webui.py:1-19](), [src/webui/interface.py:1-95](), [src/webui/webui_manager.py:1-122]()

---

## Deployment Architectures

The system supports both local execution via standard Python environments and headless containerized execution via Docker.

### Deployment Architecture Mapping

```mermaid
graph TB
    subgraph "Local Deployment"
        cli["python webui.py<br/>--ip 127.0.0.1 --port 7788"]
        gradio_local["Gradio Server<br/>Port 7788"]
        cli --> gradio_local
    end
    
    subgraph "Docker Deployment"
        supervisord["supervisord<br/>Process Supervisor"]
        xvfb["Xvfb :99<br/>Virtual Display"]
        x11vnc["x11vnc<br/>VNC Server (5901)"]
        novnc["noVNC<br/>Web Client (6080)"]
        app["python webui.py<br/>--ip 0.0.0.0 --port 7788"]
        
        supervisord --> xvfb
        supervisord --> x11vnc
        supervisord --> novnc
        supervisord --> app
    end
```

**Sources:** [webui.py:7-16](), [src/webui/interface.py:22-30]()

---

## Component Interaction Model

The interaction model governs how user triggers pass through the UI manager down to agents, controllers, and browser sessions.

### Request-Response Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as "src/webui/interface.py"
    participant Mgr as "src/webui/webui_manager.py"
    participant Agent as "Agent"
    participant Browser as "CustomBrowser"
    
    User->>UI: Input Task & Click Run
    UI->>Mgr: Register task in WebuiManager
    UI->>Browser: Initialize CustomBrowser
    UI->>Agent: Instantiate & call agent.run()
    loop Step Execution
        Agent->>Browser: Perform action via Playwright
        Browser-->>Agent: Return page state / screenshot
        Agent->>Mgr: Update bu_chat_history
        Mgr->>UI: Render live progress
    end
    Agent-->>UI: Task Complete
```

**Sources:** [src/webui/interface.py:22-95](), [src/webui/webui_manager.py:30-43]()

---

## Subsystem Details and Child Pages

For granular technical documentation on entrypoints, interface building, and state coordination, please refer to the child pages:

- **2.1 Application Entrypoint and Interface Assembly**: Details `webui.py` argument parsing, `theme_map`, `create_ui`, and tab registration in `src/webui/interface.py`.
- **2.2 WebuiManager and State Flow**: Explains component registration via `id_to_component`, chat history, browser reference management, and config save/load routines in `src/webui/webui_manager.py`.

**Sources:** [webui.py:1-19](), [src/webui/interface.py:1-95](), [src/webui/webui_manager.py:1-122]()

---

