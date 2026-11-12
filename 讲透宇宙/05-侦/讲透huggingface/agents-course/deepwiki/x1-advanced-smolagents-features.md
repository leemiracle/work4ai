<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/agents-course · extra page Advanced smolagents Features · fetched 2026-10-26 -->

# Advanced smolagents Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [units/en/unit2/smolagents/code_agents.mdx](units/en/unit2/smolagents/code_agents.mdx)
- [units/en/unit2/smolagents/final_quiz.mdx](units/en/unit2/smolagents/final_quiz.mdx)
- [units/en/unit2/smolagents/introduction.mdx](units/en/unit2/smolagents/introduction.mdx)
- [units/en/unit2/smolagents/multi_agent_systems.mdx](units/en/unit2/smolagents/multi_agent_systems.mdx)
- [units/en/unit2/smolagents/quiz1.mdx](units/en/unit2/smolagents/quiz1.mdx)
- [units/en/unit2/smolagents/quiz2.mdx](units/en/unit2/smolagents/quiz2.mdx)
- [units/en/unit2/smolagents/retrieval_agents.mdx](units/en/unit2/smolagents/retrieval_agents.mdx)
- [units/en/unit2/smolagents/tool_calling_agents.mdx](units/en/unit2/smolagents/tool_calling_agents.mdx)
- [units/en/unit2/smolagents/tools.mdx](units/en/unit2/smolagents/tools.mdx)
- [units/en/unit2/smolagents/vision_agents.mdx](units/en/unit2/smolagents/vision_agents.mdx)
- [units/en/unit2/smolagents/why_use_smolagents.mdx](units/en/unit2/smolagents/why_use_smolagents.mdx)
- [units/zh-CN/unit2/smolagents/introduction.mdx](units/zh-CN/unit2/smolagents/introduction.mdx)
- [units/zh-CN/unit2/smolagents/multi_agent_systems.mdx](units/zh-CN/unit2/smolagents/multi_agent_systems.mdx)
- [units/zh-CN/unit2/smolagents/quiz2.mdx](units/zh-CN/unit2/smolagents/quiz2.mdx)
- [units/zh-CN/unit2/smolagents/retrieval_agents.mdx](units/zh-CN/unit2/smolagents/retrieval_agents.mdx)
- [units/zh-CN/unit2/smolagents/tool_calling_agents.mdx](units/zh-CN/unit2/smolagents/tool_calling_agents.mdx)
- [units/zh-CN/unit2/smolagents/tools.mdx](units/zh-CN/unit2/smolagents/tools.mdx)
- [units/zh-CN/unit2/smolagents/vision_agents.mdx](units/zh-CN/unit2/smolagents/vision_agents.mdx)
- [units/zh-CN/unit2/smolagents/why_use_smolagents.mdx](units/zh-CN/unit2/smolagents/why_use_smolagents.mdx)

</details>



This document covers the advanced capabilities of the smolagents framework that extend beyond basic agent functionality. These features enable sophisticated multi-modal interactions, system orchestration, and tool ecosystem integration. For information about core agent types like `CodeAgent` and `ToolCallingAgent`, see [3.1.1](#3.1.1).

## Vision-Language Model Integration

The smolagents framework provides built-in support for vision-language models (VLMs) through specialized agent configurations and image handling mechanisms. This enables agents to process visual content dynamically during execution.

### Vision Agent Architecture

```mermaid
graph TB
    subgraph "VLM Agent Execution"
        TA["TaskStep"] --> AS["ActionStep"]
        AS --> SO["step_callback()"]
        SO --> OI["observation_images"]
        OI --> MEM["Agent Memory"]
    end
    
    subgraph "Image Sources"
        II["Initial Images"] --> TA
        SS["Screenshots"] --> SO
        DR["Dynamic Retrieval"] --> AS
    end
    
    subgraph "VLM Models"
        OAIS["OpenAIServerModel('gpt-4o')"]
        IC["InferenceClientModel"]
    end
    
    MEM --> OAIS
    MEM --> IC
    
    subgraph "Browser Integration"
        HEL["helium.get_driver()"]
        SS_FUNC["save_screenshot()"]
        TOOLS["@tool browser functions"]
    end
    
    HEL --> SS_FUNC
    SS_FUNC --> SS
    TOOLS --> AS
```

The vision system operates through the `MultiStepAgent` framework where images are captured and stored at different execution stages:

- **TaskStep**: Stores initial images provided via the `images` parameter
- **ActionStep**: Captures dynamic images through `observation_images` during execution
- **step_callbacks**: Functions that execute after each agent step to capture screenshots

Sources: [units/en/unit2/smolagents/vision_agents.mdx:104-111]()

### Dynamic Image Capture

Vision agents can dynamically capture and process images during web browsing sessions. The `save_screenshot` function integrates with browser automation tools to capture visual state:

```mermaid
graph LR
    subgraph "Browser Automation"
        DR["driver.get_screenshot_as_png()"]
        PIL["Image.open(BytesIO(png_bytes))"]
        COPY["image.copy()"]
    end
    
    subgraph "Agent Memory Integration"
        SL["step_log: ActionStep"]
        OI["observations_images = [image]"]
        OBS["observations += url_info"]
    end
    
    DR --> PIL
    PIL --> COPY
    COPY --> OI
    SL --> OI
    SL --> OBS
```

The browser integration uses `helium` and `selenium` for web automation, with specialized tools like `search_item_ctrl_f`, `go_back`, and `close_popups` enabling human-like web navigation.

Sources: [units/en/unit2/smolagents/vision_agents.mdx:155-174]()

## Multi-Agent System Orchestration

The smolagents framework supports sophisticated multi-agent workflows through the `managed_agents` parameter and hierarchical task delegation. This enables specialized agents to collaborate on complex tasks while maintaining separate memory contexts.

### Multi-Agent Coordination Architecture

```mermaid
graph TB
    subgraph "Manager Agent"
        MA["CodeAgent(managed_agents=[...])"]
        TOOLS_M["Tools: calculate_cargo_travel_time"]
        IMPORTS["additional_authorized_imports"]
        PLAN["planning_interval"]
    end
    
    subgraph "Managed Agents"
        WA["web_agent: CodeAgent"]
        TOOLS_W["Tools: GoogleSearchTool, VisitWebpageTool"]
        DESC["description: 'Browses web'"]
        VERB["verbosity_level: 0"]
    end
    
    subgraph "Execution Flow"
        TASK["Task Input"]
        DELEGATE["Task Delegation"]
        MEMORY_SEP["Separate Memory Contexts"]
        RESULTS["Result Aggregation"]
    end
    
    MA --> WA
    TASK --> MA
    MA --> DELEGATE
    DELEGATE --> WA
    WA --> MEMORY_SEP
    MEMORY_SEP --> RESULTS
    RESULTS --> MA
```

The multi-agent system provides two key benefits:
- **Focused Performance**: Each agent specializes in specific tasks
- **Memory Efficiency**: Separate contexts reduce token count and latency

Sources: [units/en/unit2/smolagents/multi_agent_systems.mdx:227-232]()

### Agent Hierarchy Implementation

The framework implements agent coordination through the `managed_agents` parameter, enabling a manager agent to delegate tasks to specialized sub-agents:

```mermaid
graph TB
    subgraph "Manager Configuration"
        MODEL["InferenceClientModel('deepseek-ai/DeepSeek-R1')"]
        MANAGED["managed_agents=[web_agent]"]
        CHECKS["final_answer_checks=[check_function]"]
        MAX_STEPS["max_steps=15"]
    end
    
    subgraph "Web Agent Configuration"
        WEB_MODEL["InferenceClientModel('Qwen/Qwen2.5-Coder-32B-Instruct')"]
        WEB_TOOLS["GoogleSearchTool, VisitWebpageTool"]
        WEB_NAME["name='web_agent'"]
        WEB_MAX["max_steps=10"]
    end
    
    subgraph "Execution Control"
        VIS["agent.visualize()"]
        RUN["agent.run(task)"]
        STATE["agent.python_executor.state"]
    end
    
    MODEL --> MANAGED
    MANAGED --> WEB_MODEL
    VIS --> RUN
    RUN --> STATE
```

The `visualize()` method provides a hierarchical view of the agent structure, showing tools, imports, and managed agent relationships.

Sources: [units/en/unit2/smolagents/multi_agent_systems.mdx:299-322]()

## Agentic RAG Systems

Smolagents implements advanced Retrieval-Augmented Generation through intelligent query processing, multi-step retrieval, and source integration. This extends traditional RAG systems with autonomous query formulation and result critique capabilities.

### RAG System Architecture

```mermaid
graph TB
    subgraph "Query Processing"
        UQ["User Query"]
        QR["Query Reformulation"]
        QD["Query Decomposition"]
        QE["Query Expansion"]
    end
    
    subgraph "Retrieval Systems"
        DDG["DuckDuckGoSearchTool"]
        KB["Custom Knowledge Base"]
        BM25["BM25Retriever"]
        VDB["Vector Database"]
    end
    
    subgraph "Agent Integration"
        CA["CodeAgent"]
        TOOLS["Tools: [search_tool, retriever_tool]"]
        MEMORY["Conversation Memory"]
    end
    
    UQ --> QR
    QR --> QD
    QD --> QE
    QE --> DDG
    QE --> KB
    KB --> BM25
    KB --> VDB
    DDG --> CA
    BM25 --> CA
    CA --> MEMORY
```

The agentic RAG system enables several advanced strategies:
- **Query Reformulation**: Optimizing search terms for better document matching
- **Multi-Step Retrieval**: Using initial results to inform subsequent queries  
- **Source Integration**: Combining web search with local documentation
- **Result Validation**: Analyzing content relevance before inclusion

Sources: [units/en/unit2/smolagents/retrieval_agents.mdx:154-164]()

### Custom Knowledge Base Implementation

The framework supports custom retrieval tools through the `Tool` class hierarchy and integration with LangChain retrievers:

```mermaid
graph LR
    subgraph "Tool Definition"
        PT["PartyPlanningRetrieverTool(Tool)"]
        NAME["name = 'party_planning_retriever'"]
        INPUTS["inputs = {'query': {...}}"]
        FORWARD["forward(query: str)"]
    end
    
    subgraph "Retrieval Backend"
        DOCS["Document collection"]
        SPLITTER["RecursiveCharacterTextSplitter"]
        RETRIEVER["BM25Retriever.from_documents()"]
        INVOKE["retriever.invoke(query)"]
    end
    
    subgraph "Agent Integration"
        AGENT["CodeAgent(tools=[retriever_tool])"]
        RUN["agent.run(query)"]
    end
    
    PT --> RETRIEVER
    DOCS --> SPLITTER
    SPLITTER --> RETRIEVER
    RETRIEVER --> INVOKE
    INVOKE --> FORWARD
    PT --> AGENT
    AGENT --> RUN
```

The custom retrieval tool integrates document splitting, semantic search, and result formatting to provide context-aware responses.

Sources: [units/en/unit2/smolagents/retrieval_agents.mdx:78-144]()

## Advanced Tool Ecosystem

Smolagents provides extensive tool integration capabilities, supporting multiple source types including Hugging Face Spaces, LangChain tools, and MCP servers. This creates a rich ecosystem for extending agent functionality.

### Tool Integration Architecture

```mermaid
graph TB
    subgraph "Tool Sources"
        HUB["Hugging Face Hub"]
        SPACES["HF Spaces"]
        LANGCHAIN["LangChain Tools"]
        MCP["MCP Servers"]
    end
    
    subgraph "Integration Methods"
        LOAD["load_tool()"]
        FROM_SPACE["Tool.from_space()"]
        FROM_LC["Tool.from_langchain()"]
        FROM_MCP["ToolCollection.from_mcp()"]
    end
    
    subgraph "Tool Management"
        PUSH["tool.push_to_hub()"]
        GRADIO["gradio_client integration"]
        COLLECTION["ToolCollection"]
        TRUST["trust_remote_code=True"]
    end
    
    HUB --> LOAD
    SPACES --> FROM_SPACE
    LANGCHAIN --> FROM_LC
    MCP --> FROM_MCP
    FROM_SPACE --> GRADIO
    FROM_MCP --> COLLECTION
    LOAD --> PUSH
```

### Hub Integration and Sharing

The framework enables seamless tool sharing through the Hugging Face Hub with automatic Space generation:

```mermaid
graph LR
    subgraph "Tool Development"
        TOOL_DEF["@tool or Tool class"]
        AGENT_DEF["CodeAgent(tools=[tool])"]
        PUSH_TOOL["tool.push_to_hub()"]
        PUSH_AGENT["agent.push_to_hub()"]
    end
    
    subgraph "Hub Resources"
        REPO["Hub Repository"]
        SPACE["Automatic HF Space"]
        METADATA["Tool Metadata"]
    end
    
    subgraph "Community Usage"
        LOAD_TOOL["load_tool('username/tool')"]
        LOAD_AGENT["agent.from_hub('username/agent')"]
        TRUST_CODE["trust_remote_code=True"]
    end
    
    TOOL_DEF --> PUSH_TOOL
    AGENT_DEF --> PUSH_AGENT
    PUSH_TOOL --> REPO
    PUSH_AGENT --> SPACE
    REPO --> LOAD_TOOL
    SPACE --> LOAD_AGENT
```

Shared agents automatically become available as interactive Hugging Face Spaces, enabling real-time community interaction.

Sources: [units/en/unit2/smolagents/tools.mdx:185-216]()

### External Tool Integration

The framework supports three major external tool sources:

**Hugging Face Spaces Integration**: Uses `gradio_client` to connect with Space backends, requiring the `gradio_client` package installation.

**LangChain Tools**: Enables reuse of existing LangChain tools through `Tool.from_langchain(load_tools(["serpapi"])[0])`, bridging the ecosystems.

**MCP Server Integration**: Supports hundreds of MCP servers through `ToolCollection.from_mcp()` with `StdioServerParameters` configuration.

Sources: [units/en/unit2/smolagents/tools.mdx:243-301]()

## Observability and Monitoring

Smolagents integrates with OpenTelemetry for comprehensive agent tracing and monitoring, enabling production-ready observability through platforms like Langfuse.

### Observability Architecture

```mermaid
graph TB
    subgraph "Agent Execution"
        CA["CodeAgent.run()"]
        STEPS["MultiStepAgent steps"]
        TOOLS["Tool executions"]
    end
    
    subgraph "Instrumentation"
        SI["SmolagentsInstrumentor"]
        TP["TracerProvider"]
        OTLP["OTLPSpanExporter"]
        SP["SimpleSpanProcessor"]
    end
    
    subgraph "External Platforms"
        LF["Langfuse Cloud"]
        OTEL_ENDPOINT["OTEL_EXPORTER_OTLP_ENDPOINT"]
        AUTH["OTEL_EXPORTER_OTLP_HEADERS"]
    end
    
    CA --> SI
    STEPS --> SI
    TOOLS --> SI
    SI --> TP
    TP --> SP
    SP --> OTLP
    OTLP --> LF
    LF --> OTEL_ENDPOINT
    LF --> AUTH
```

The observability system captures comprehensive execution traces including step-by-step agent reasoning, tool calls, and error handling, enabling debugging and performance analysis.

Sources: [units/en/unit2/smolagents/code_agents.mdx:349-378]()

---

