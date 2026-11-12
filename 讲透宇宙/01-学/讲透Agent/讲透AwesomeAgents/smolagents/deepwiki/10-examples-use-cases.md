<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/smolagents · page 10 Examples & Use Cases · fetched 2026-10-26 -->

# Examples & Use Cases

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/multiple_tools.py](examples/multiple_tools.py)
- [examples/open_deep_research/README.md](examples/open_deep_research/README.md)
- [examples/open_deep_research/app.py](examples/open_deep_research/app.py)
- [examples/open_deep_research/run.py](examples/open_deep_research/run.py)
- [examples/open_deep_research/run_gaia.py](examples/open_deep_research/run_gaia.py)
- [examples/open_deep_research/visual_vs_text_browser.ipynb](examples/open_deep_research/visual_vs_text_browser.ipynb)
- [examples/rag.py](examples/rag.py)
- [examples/rag_using_chromadb.py](examples/rag_using_chromadb.py)

</details>



This page provides practical examples demonstrating common agent patterns and real-world applications. These examples show how to use the framework's core components—agents, models, and tools—to build functional agentic systems.

For detailed information about specific framework components, see: Agent Framework ([MultiStepAgent & ReAct Loop](#3.1)), Model Integration ([Model Integration](#4)), Tool System ([Tool System](#5)), and User Interfaces ([User Interfaces](#8)).

---

## Basic Agent Usage

The simplest agent requires only a model and optionally a list of tools. The framework supports two primary agent types: `CodeAgent` (writes actions as Python code) and `ToolCallingAgent` (writes actions as JSON tool calls).

### Minimal Agent Workflow

```mermaid
graph LR
    ["UserTask"] -- "Task String" --> ["CodeAgent/ToolCallingAgent"]
    ["Model"] -- "LLM Engine" --> ["CodeAgent/ToolCallingAgent"]
    ["CodeAgent/ToolCallingAgent"] -- "Python Code" --> ["LocalPythonExecutor"]
    ["LocalPythonExecutor"] -- "Execution Result" --> ["FinalAnswerTool"]
```

**Basic Implementation Patterns**
Users can initialize agents using various model providers. A common pattern involves defining tools with the `@tool` decorator [examples/multiple_tools.py:15-16]() and passing them to a `CodeAgent` [examples/multiple_tools.py:205-210](). The framework also supports using an `InferenceClientModel` for a serverless experience [examples/multiple_tools.py:8]().

For more simple examples of agent creation, tool usage, and task execution, see **[Basic Agent Usage](#10.1)**.

**Sources:** [examples/multiple_tools.py:1-210]()

---

## Web Automation & Browser Control

Web automation allows agents to interact with live websites using specialized tools and browser drivers.

### Browser Control Architecture

```mermaid
graph TD
    subgraph "Natural Language Space"
        ["UserPrompt"] -- "'Search for X'" --> ["AgentAction"]
    end

    subgraph "Code Entity Space"
        ["AgentAction"] -- "exec()" --> ["CodeAgent"]
        ["CodeAgent"] -- "call" --> ["GoogleSearchTool"]
        ["CodeAgent"] -- "call" --> ["VisitTool"]
        ["VisitTool"] -- "wraps" --> ["SimpleTextBrowser"]
    end
```

**Browser Implementation Patterns**
Advanced browser control often involves a `SimpleTextBrowser` [examples/open_deep_research/run.py:71]() combined with a suite of navigation tools such as `VisitTool`, `PageUpTool`, and `FinderTool` [examples/open_deep_research/run.py:74-79](). For visual tasks, the framework supports vision-based browser control using `helium` and screenshots [examples/open_deep_research/visual_vs_text_browser.ipynb:171-189]().

For examples using the `webagent` CLI, vision-based browser control, and advanced scraping patterns, see **[Web Automation & Browser Control](#10.2)**.

**Sources:** [examples/open_deep_research/run.py:71-81](), [examples/open_deep_research/visual_vs_text_browser.ipynb:153-205]()

---

## Retrieval-Augmented Generation (RAG)

RAG examples demonstrate how to combine search tools with document processing to provide agents with external knowledge.

### Agentic RAG Workflow

```mermaid
graph LR
    ["KnowledgeBase"] -- "load_dataset" --> ["RecursiveCharacterTextSplitter"]
    ["RecursiveCharacterTextSplitter"] -- "DocumentChunks" --> ["RetrieverTool"]
    ["RetrieverTool"] -- "forward(query)" --> ["BM25Retriever/Chroma"]
    ["BM25Retriever/Chroma"] -- "Context" --> ["CodeAgent"]
```

**Implementation Patterns**
Agentic RAG transforms a static pipeline into a reasoning-driven process. Implementations typically involve subclassing the `Tool` base class to create a `RetrieverTool` [examples/rag.py:29-38](). This tool can wrap a lexical search engine like `BM25Retriever` [examples/rag.py:42]() or a vector store like `Chroma` for semantic search [examples/rag_using_chromadb.py:68-71]().

For details on document processing and vector store integration, see **[Retrieval-Augmented Generation (RAG)](#10.3)**.

**Sources:** [examples/rag.py:26-52](), [examples/rag_using_chromadb.py:71-96]()

---

## Async Integration & Web Applications

Agents can be integrated into larger applications or exposed via interactive web interfaces.

**Web Deployment**
The library provides a `GradioUI` class to quickly deploy an agent as a web application [examples/open_deep_research/app.py:8](). This interface allows users to interact with the agent in a chat-like environment and see the underlying tool execution steps.

**Multi-Tool Integration**
Applications often require multiple tools to be available simultaneously, such as weather lookups, currency conversion, and news fetching [examples/multiple_tools.py:15-115](). The `CodeAgent` manages these by generating Python scripts that call the necessary tools in sequence or conditionally [examples/multiple_tools.py:205-210]().

For examples of Gradio deployment and async usage, see **[Async Integration & Web Applications](#10.4)**.

**Sources:** [examples/open_deep_research/app.py:1-11](), [examples/multiple_tools.py:1-210]()

---

## Multi-Agent Orchestration

Multi-agent systems divide tasks among specialized agents, improving performance through hierarchical delegation.

### Hierarchical Orchestration

```mermaid
graph TB
    subgraph "Natural Language Space"
        ["UserGoal"] -- "Deep Research" --> ["ManagerLogic"]
    end

    subgraph "Code Entity Space"
        ["ManagerLogic"] -- "instance of" --> ["CodeAgent"]
        ["CodeAgent"] -- "manages" --> ["ManagedAgent"]
        ["ManagedAgent"] -- "wraps" --> ["ToolCallingAgent"]
        ["ToolCallingAgent"] -- "uses" --> ["GoogleSearchTool"]
    end
```

**Delegation Patterns**
The "Open Deep Research" example demonstrates a hierarchical pattern where a `CodeAgent` acts as a manager [examples/open_deep_research/run.py:101-109](). It delegates web-intensive tasks to a `search_agent` (a `ToolCallingAgent`) [examples/open_deep_research/run.py:82-96](). The manager can also use tools like `TextInspectorTool` and `visualizer` for direct data processing [examples/open_deep_research/run.py:102-103]().

For details on delegation patterns and multi-agent benchmarks like GAIA, see **[Multi-Agent Orchestration](#10.5)**.

**Sources:** [examples/open_deep_research/run.py:60-109](), [examples/open_deep_research/run_gaia.py:82-134]()

---

