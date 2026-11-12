<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/smolagents · page 2 Getting Started · fetched 2026-10-27 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/en/index.md](docs/source/en/index.md)
- [docs/source/en/installation.md](docs/source/en/installation.md)
- [docs/source/en/tutorials/secure_code_execution.md](docs/source/en/tutorials/secure_code_execution.md)
- [pyproject.toml](pyproject.toml)
- [src/smolagents/__init__.py](src/smolagents/__init__.py)

</details>



This section provides everything you need to begin using `smolagents`: installation instructions, your first agent, and an introduction to core concepts. For advanced configuration and deployment patterns, see the Agent Framework section ([Agent Framework](#3)) and later chapters.

## What is smolagents?

`smolagents` is a lightweight Python library designed to make it extremely easy to build and run agents using just a few lines of code [docs/source/en/index.md:9-9](). Unlike traditional agent frameworks where agents output JSON tool calls, `smolagents`' `CodeAgent` writes Python code snippets to perform actions, enabling natural composability like function nesting and loops [docs/source/en/index.md:15-15]().

The framework is deliberately minimal—the core logic fits in approximately 1,000 lines of code [README.md:36-36]()—while providing production-ready features including:

- **Model-agnostic design**: Works with local `transformers`, cloud APIs (OpenAI, Anthropic, etc.), and 100+ providers via `LiteLLM` [README.md:42-42]().
- **Secure execution**: AST-based local interpreter or sandboxed environments via Blaxel, E2B, Modal, Docker, or Pyodide+Deno WebAssembly [README.md:38-38]().
- **Hub integration**: Share and load agents/tools from Hugging Face Hub as Gradio Spaces [docs/source/en/index.md:19-19]().
- **Multiple interfaces**: Python API, CLI (`smolagent`, `webagent`), and Gradio web UI [docs/source/en/index.md:27-27]().

## Package Structure

The library is organized into focused modules with optional dependency groups for different use cases:

"Core Package Architecture"
```mermaid
graph TB
    subgraph "Core_Package_smolagents"
        agents["agents.py<br/>CodeAgent, ToolCallingAgent<br/>MultiStepAgent base"]
        models["models.py<br/>TransformersModel, InferenceClientModel<br/>LiteLLMModel, OpenAIModel, etc."]
        tools["tools.py<br/>Tool base class, @tool decorator"]
        default_tools["default_tools.py<br/>WebSearchTool, PythonInterpreterTool<br/>SpeechToTextTool"]
        executor["local_python_executor.py<br/>LocalPythonExecutor<br/>AST-based code execution"]
        remote["remote_executors.py<br/>E2BExecutor, BlaxelExecutor<br/>DockerExecutor, ModalExecutor"]
        memory["memory.py<br/>AgentMemory, MemoryStep types"]
        monitoring["monitoring.py<br/>AgentLogger, Monitor"]
        gradio_ui["gradio_ui.py<br/>GradioUI"]
        cli["cli.py<br/>smolagent command"]
    end
    
    subgraph "Optional_Dependencies_pyproject_toml"
        toolkit["[toolkit]<br/>ddgs, markdownify<br/>For WebSearchTool"]
        transformers_deps["[transformers]<br/>transformers, accelerate, torch<br/>For TransformersModel"]
        litellm_deps["[litellm]<br/>litellm<br/>For LiteLLMModel"]
        gradio_deps["[gradio]<br/>gradio>=5.14.0<br/>For GradioUI"]
        e2b_deps["[e2b]<br/>e2b-code-interpreter<br/>For E2BExecutor"]
        blaxel_deps["[blaxel]<br/>blaxel, websocket-client<br/>For BlaxelExecutor"]
        openai_deps["[openai]<br/>openai>=1.58.1<br/>For OpenAIModel"]
    end
    
    agents --> models
    agents --> tools
    agents --> executor
    agents --> memory
    agents --> monitoring
    
    tools --> default_tools
    executor --> remote
    
    gradio_ui --> agents
    cli --> agents
    
    default_tools -.requires.-> toolkit
    models -.requires.-> transformers_deps
    models -.requires.-> litellm_deps
    models -.requires.-> openai_deps
    gradio_ui -.requires.-> gradio_deps
    remote -.requires.-> e2b_deps
    remote -.requires.-> blaxel_deps
```

**Sources**: [pyproject.toml:24-94](), [src/smolagents/__init__.py:19-32]()

## Entry Points to Code

The library provides three main ways to interact with agents, each mapping to specific code entry points:

"UI to Code Entity Mapping"
```mermaid
graph LR
    subgraph "User_Interfaces"
        python["Python Script<br/>import smolagents"]
        terminal["Terminal<br/>$ smolagent / $ webagent"]
        browser["Web Browser<br/>Gradio UI"]
    end
    
    subgraph "Code_Entry_Points"
        init["__init__.py<br/>Exports all public classes"]
        cli_main["cli.py::main()<br/>CLI entry point"]
        web_main["vision_web_browser.py::main()<br/>Web CLI entry point"]
        gradio_class["gradio_ui.py::GradioUI"]
    end
    
    subgraph "Core_Classes"
        CodeAgent["agents.py::CodeAgent"]
        ToolCallingAgent["agents.py::ToolCallingAgent"]
        models_module["models.py<br/>InferenceClientModel<br/>TransformersModel<br/>LiteLLMModel, etc."]
        tools_module["tools.py<br/>Tool, @tool"]
    end
    
    python --> init
    terminal --> cli_main
    terminal --> web_main
    browser --> gradio_class
    
    init --> CodeAgent
    init --> ToolCallingAgent
    init --> models_module
    init --> tools_module
    
    cli_main --> CodeAgent
    cli_main --> ToolCallingAgent
    
    gradio_class --> CodeAgent
    gradio_class --> ToolCallingAgent
```

**Sources**: [pyproject.toml:139-141](), [src/smolagents/__init__.py:19-32]()

## Installation

### Minimal Installation

For basic functionality with cloud-based models:

```bash
pip install smolagents
```

This installs core dependencies including `huggingface-hub`, `requests`, `rich`, `jinja2`, `pillow`, and `python-dotenv` [pyproject.toml:14-22]().

### With Default Tools

To enable the built-in toolbox (e.g., `DuckDuckGoSearchTool`, `VisitWebpageTool`):

```bash
pip install "smolagents[toolkit]"
```

### With Local Models

For running models locally using `transformers` or Apple Silicon with `MLX`:

```bash
pip install "smolagents[transformers]"  # Standard transformers [pyproject.toml:79-83]
pip install "smolagents[mlx-lm]"       # Apple Silicon [pyproject.toml:59-61]
```

### Common Combinations

For all available extras (includes remote executors, telemetry, etc.):

```bash
pip install "smolagents[all]"
```

**For detailed dependency information and use-case-specific installations, see [Installation & Dependencies](#2.1).**

**Sources**: [pyproject.toml:24-94](), [docs/source/en/installation.md:38-251]()

## Your First Agent in 30 Seconds

Here's a minimal working example using a cloud-based model and web search:

```python
from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel

# Initialize model (uses Hugging Face Inference API)
model = InferenceClientModel()

# Create agent with web search capability
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

# Run a task
result = agent.run("What is the current weather in Paris?")
print(result)
```

### What Happens Internally

1. `CodeAgent` receives the task and initializes `AgentMemory` [src/smolagents/__init__.py:25]().
2. The agent enters a ReAct loop:
   - It generates Python code to call tools via `model.generate()` [src/smolagents/models.py:126]().
   - Executes code using `LocalPythonExecutor` (default) [src/smolagents/local_python_executor.py:545]().
   - Stores the execution result in memory steps.
   - Repeats until a final answer is produced.

**For a complete walkthrough with multiple examples, see [Quick Start Guide](#2.2).**

**Sources**: [docs/source/en/index.md:68-79](), [README.md:60-67]()

## Agent Types: CodeAgent vs ToolCallingAgent

The library provides two agent paradigms with different execution models [docs/source/en/index.md:15-17]():

| Aspect | `CodeAgent` | `ToolCallingAgent` |
|--------|-------------|-------------------|
| **Action Format** | Python code snippets | JSON/Text tool calls |
| **Tool Invocation** | `result = tool_name(arg)` | Structured JSON blobs |
| **Execution** | `LocalPythonExecutor` (AST) or Sandbox | Direct tool execution |
| **Strengths** | Composability, loops, reasoning | Standard industry format |

**For detailed comparison and when to use each, see [Key Concepts](#2.3) and [Agent Framework](#3).**

**Sources**: [docs/source/en/index.md:15-17](), [docs/source/en/tutorials/secure_code_execution.md:10-24]()

## Model Integration Overview

The framework is model-agnostic. All models implement the `Model` interface [src/smolagents/models.py:126]():

"Model Provider Architecture"
```mermaid
graph TB
    subgraph "Model_Interface_models_py_Model"
        generate["generate(messages, stop_sequences)<br/>→ ChatMessage"]
    end
    
    subgraph "Local_Execution"
        TransformersModel["TransformersModel<br/>Local GPU/CPU inference"]
        MLXModel["MLXModel<br/>Apple Silicon optimized"]
        VLLMModel["VLLMModel<br/>High-performance serving"]
    end
    
    subgraph "Cloud_APIs"
        InferenceClientModel["InferenceClientModel<br/>Hub Inference Providers"]
        LiteLLMModel["LiteLLMModel<br/>100+ providers via LiteLLM"]
        OpenAIModel["OpenAIModel<br/>OpenAI-compatible APIs"]
        AzureOpenAIModel["AzureOpenAIModel<br/>Azure deployments"]
        AmazonBedrockModel["AmazonBedrockModel<br/>AWS Bedrock"]
    end
    
    generate --> TransformersModel
    generate --> MLXModel
    generate --> VLLMModel
    generate --> InferenceClientModel
    generate --> LiteLLMModel
    generate --> OpenAIModel
    generate --> AzureOpenAIModel
    generate --> AmazonBedrockModel
```

**For complete model configuration and provider-specific examples, see [Model Integration](#4).**

**Sources**: [src/smolagents/models.py:126-785](), [README.md:80-173]()

## Execution Environment Quick Reference

`CodeAgent` requires a Python execution environment. Choice affects security [docs/source/en/tutorials/secure_code_execution.md:43-47]():

| Executor Type | Security Level | Setup Complexity |
|---------------|----------------|------------------|
| **LocalPythonExecutor** (default) | Medium (AST-based) | None |
| **Remote Executors** (E2B, Blaxel, Modal, Docker) | High (Sandboxed) | Requires API keys/Docker |

**LocalPythonExecutor** works by loading the Abstract Syntax Tree (AST) and executing operation by operation with strict rules on imports and resource usage [docs/source/en/tutorials/secure_code_execution.md:54-60]().

**For detailed security models and deployment recommendations, see [Code Execution & Security](#6).**

**Sources**: [docs/source/en/tutorials/secure_code_execution.md:51-103](), [src/smolagents/remote_executors.py:23]().

## Next Steps

Now that you understand the basics:

1. **[Installation & Dependencies](#2.1)**: Detailed dependency groups and environment setup.
2. **[Quick Start Guide](#2.2)**: Step-by-step examples with `CodeAgent` and `ToolCallingAgent`.
3. **[Key Concepts](#2.3)**: Deep dive into the ReAct loop, memory, and tools.

**Sources**: Wiki Table of Contents structure.

---

