<!-- source: DeepWiki mcp.deepwiki.com · repo pguso/agents-from-scratch · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PHILOSOPHY.md](PHILOSOPHY.md)
- [QUICKSTART.md](QUICKSTART.md)
- [README.md](README.md)

</details>



The **Agents from Scratch** repository is a technical curriculum designed to demystify AI agents by building one from first principles. Unlike many modern AI projects that rely on complex frameworks (like LangChain or CrewAI) or cloud APIs, this project uses a **local-first philosophy**, requiring only a local LLM and standard Python code [README.md:5-7]().

The core mission is to provide **mechanical understanding**—the ability to debug, extend, and reason about agent systems as software engineering constructs rather than "magical" entities [PHILOSOPHY.md:5-7]().

## Educational Philosophy

This repository is built on the belief that agents are not personalities, but rather **loops, state, and constraints** [README.md:28-30](). It adheres to several strict design principles:

*   **Explicit over Implicit**: No hidden logic or opaque "Chain of Thought" steps. Every state transition is visible in the code [PHILOSOPHY.md:31-40]().
*   **Structured Outputs**: Reliability is achieved through JSON contracts and validation rather than clever prompting alone [PHILOSOPHY.md:64-73]().
*   **Local-First**: All examples run on consumer hardware using `llama-cpp-python` and GGUF models, ensuring privacy and zero API costs [PHILOSOPHY.md:157-165]().
*   **Progressive Complexity**: The agent evolves across 12 lessons, adding exactly one capability at a time [README.md:34-49]().

For a deeper dive into these principles, see **[Design Philosophy](#1.2)**.

## System Architecture

The project bridges the gap between unstructured Natural Language (the LLM's domain) and Structured Code (the application's domain). The following diagram illustrates how the primary code entities interact to form the agent loop.

### Agent Loop and Code Entity Mapping
This diagram shows how the `Agent` class coordinates various subsystems defined in the `agent/` directory.

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserPrompt["User Prompt (String)"]
        LLMOutput["LLM Response (Text/JSON)"]
    end

    subgraph "Code Entity Space (agent/)"
        Agent["Agent Class (agent.py)"]
        State["AgentState (state.py)"]
        Planner["Planner Subsystem (planner.py)"]
        Memory["Memory (memory.py)"]
        Tools["Tool Registry (tools.py)"]
    end

    subgraph "Execution Layer"
        LLM["LocalLLM (shared/llm.py)"]
        SystemExec["Python Environment"]
    end

    UserPrompt --> Agent
    Agent -->|".generate()"| LLM
    LLM --> LLMOutput
    LLMOutput -->|"(utils.safe_json_parse)"| Agent
    Agent -->| "Update" | State
    Agent -->| "Consult" | Memory
    Agent -->| "Create Plan" | Planner
    Agent -->| "Execute" | Tools
    Tools -->| "Side Effects" | SystemExec
```
**Sources:** [agent/agent.py:1-10](), [agent/state.py:1-5](), [agent/planner.py:1-5](), [shared/llm.py:1-10]()

## Repository Structure

The codebase is organized to support a step-by-step learning path.

| Directory / File | Purpose |
| :--- | :--- |
| `agent/` | Contains the core implementation: `agent.py`, `state.py`, `planner.py`, etc. [README.md:89-96]() |
| `lessons/` | Markdown files (01-12) explaining the concepts behind each stage [README.md:99]() |
| `shared/` | Reusable utilities for LLM interaction, prompt building, and JSON parsing [README.md:88]() |
| `complete_example.py` | A reference file demonstrating all 12 lessons in isolation [README.md:84]() |
| `models/` | Local directory for storing GGUF model files [README.md:87]() |

### From Prompt to Action: Data Flow
This diagram maps the transition from a text goal to a validated code execution using specific functions found in the `Planner` and `Agent` classes.

```mermaid
graph LR
    subgraph "Input"
        Goal["Goal: 'Calculate 5+5'"]
    end

    subgraph "Planning (planner.py)"
        P1["create_plan()"]
        P2["create_atomic_action()"]
    end

    subgraph "Execution (agent.py & tools.py)"
        E1["execute_tool_call()"]
        E2["calculator()"]
    end

    Goal --> P1
    P1 -->| "List of steps" | P2
    P2 -->| "Action: 'calculator'" | E1
    E1 -->| "Call" | E2
    E2 -->| "Result: 10" | Goal
```
**Sources:** [agent/planner.py:10-50](), [agent/agent.py:100-120](), [agent/tools.py:1-20]()

## Navigation and Setup

To begin working with the repository, follow these steps:

1.  **Environment Setup**: Install dependencies and download a compatible GGUF model (e.g., Llama-3-8B). For a detailed walkthrough, see **[Getting Started](#1.1)**.
2.  **Verify Installation**: Use the `setup_check.py` script to ensure your environment is configured correctly [QUICKSTART.md:41-42]().
3.  **Run Examples**: Execute `complete_example.py` to see the agent in action across different lesson stages [README.md:73]().
4.  **Follow the Curriculum**: Read through the `lessons/` directory in order, as each lesson builds on the code established in the previous one [README.md:145-151]().

**Sources:** [README.md:70-75](), [QUICKSTART.md:1-50]()

---

