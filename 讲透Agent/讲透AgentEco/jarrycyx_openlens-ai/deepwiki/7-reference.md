<!-- source: DeepWiki mcp.deepwiki.com · repo jarrycyx/openlens-ai · page 7 Reference · fetched 2026-10-27 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [LICENSE](LICENSE)

</details>



This page provides comprehensive reference material for the OpenLens AI system, including configuration parameters, repository structure, and licensing information. For detailed setup instructions, see [Getting Started](#2). For specific configuration guidance during installation, see [Configuration](#2.1).

## Configuration Reference

The OpenLens AI system uses environment variables for configuration, defined in the `.env.example` template file. This section documents all available configuration parameters and their purposes.

### Core Model Configuration

The system supports multiple language models for different tasks:

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `MODEL` | Main language model for general tasks | `glm-4.5-air` |
| `CODE_MODEL` | Language model for code-related tasks | `glm-4.5-air` |
| `VISION_MODEL` | Vision model for image analysis | `glm-4.1v-9b-thinking` |
| `OPENAI_API_KEY` | API key for accessing language models | `<YOUR API KEY>` |
| `BASE_URL` | Base URL for model API service | `https://cloud.infini-ai.com/maas/v1/` |

Sources: [.env.example:1-5]()

### Search and Reranking Configuration

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `RERANK_MODEL` | Reranking model for search relevance | `bge-reranker-v2-m3` |
| `RERANK_API_KEY` | API key for reranking service | `<YOUR API KEY>` |
| `RERANK_BASE_URL` | Base URL for reranking API | `https://cloud.infini-ai.com/maas/v1/` |
| `TAVILY_API_KEY` | API key for Tavily web search | `<YOUR API KEY>` |

Sources: [.env.example:7-11]()

### Context and Token Limits

The system defines various token limits for different operations:

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `MAX_CONTEXT_TOKEN_CNT` | Maximum tokens for normal operations | `32000` |
| `MAX_CONTEXT_TOKEN_CNT_LARGE` | Maximum tokens for large operations | `96000` |
| `MAX_TOOL_TOKEN_CNT` | Maximum tokens in tool responses | `2000` |
| `LITERATURE_SEARCH_MIN_TOOL_CALL` | Minimum tool calls for literature search | `10` |

Sources: [.env.example:13-17]()

### Agent Execution Parameters

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `OPENHANDS_MAX_ITER` | Maximum OpenHands agent iterations | `100` |
| `MAX_SUBTASK_REDO` | Maximum subtask retry attempts | `2` |
| `MAX_LATEX_POLISH_ROUND` | Maximum LaTeX polishing rounds | `2` |
| `DOCKER_NAME` | Docker container name | `agent-med-cpu` |

Sources: [.env.example:19-23]()

### Optional Monitoring and Notifications

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `LANGSMITH_TRACING` | Enable LangSmith tracing | `true` |
| `LANGSMITH_ENDPOINT` | LangSmith service endpoint | `https://api.smith.langchain.com` |
| `LANGSMITH_PROJECT` | LangSmith project name | `openlens` |
| `LANGSMITH_API_KEY` | LangSmith API key | `<YOUR API KEY>` |
| `SMTP_SERVER` | SMTP server for notifications | `smtpdm.aliyun.com` |
| `SMTP_PORT` | SMTP server port | `25` |
| `EMAIL_USER` | Email address for notifications | `<YOUR EMAIL>` |
| `EMAIL_PASSWORD` | Email authentication password | `<YOUR EMAIL SMTP PASSWORD>` |

Sources: [.env.example:28-36]()

## Configuration to Code Entity Mapping

The following diagram shows how configuration parameters map to specific code entities in the system:

```mermaid
graph TD
    subgraph "Environment Configuration"
        ENV_FILE[".env file"]
        MODEL_CONFIG["MODEL, CODE_MODEL, VISION_MODEL"]
        API_KEYS["OPENAI_API_KEY, RERANK_API_KEY, TAVILY_API_KEY"]
        TOKEN_LIMITS["MAX_CONTEXT_TOKEN_CNT, MAX_TOOL_TOKEN_CNT"]
        AGENT_PARAMS["OPENHANDS_MAX_ITER, MAX_SUBTASK_REDO"]
        DOCKER_CONFIG["DOCKER_NAME"]
    end
    
    subgraph "Core System Components"
        BUILD_GRAPH["build_graph.py"]
        AGENTS["agent_*.py modules"]
        OPENHANDS_RUNTIME["OpenHands runtime"]
        DOCKER_CONTAINER["Docker container"]
    end
    
    subgraph "External Service Integrations"
        LLM_CLIENTS["LLM client classes"]
        TAVILY_SEARCH["Tavily search integration"]
        RERANK_SERVICE["Reranking service client"]
        LANGSMITH_TRACE["LangSmith tracing"]
    end
    
    ENV_FILE --> MODEL_CONFIG
    ENV_FILE --> API_KEYS
    ENV_FILE --> TOKEN_LIMITS
    ENV_FILE --> AGENT_PARAMS
    ENV_FILE --> DOCKER_CONFIG
    
    MODEL_CONFIG --> LLM_CLIENTS
    API_KEYS --> LLM_CLIENTS
    API_KEYS --> TAVILY_SEARCH
    API_KEYS --> RERANK_SERVICE
    API_KEYS --> LANGSMITH_TRACE
    
    TOKEN_LIMITS --> BUILD_GRAPH
    AGENT_PARAMS --> AGENTS
    AGENT_PARAMS --> OPENHANDS_RUNTIME
    
    DOCKER_CONFIG --> DOCKER_CONTAINER
    
    BUILD_GRAPH --> AGENTS
    AGENTS --> OPENHANDS_RUNTIME
    OPENHANDS_RUNTIME --> DOCKER_CONTAINER
```

Sources: [.env.example:1-38]()

## Repository Structure Overview

The OpenLens AI repository is organized into several key directories and modules that support the multi-agent research system:

```mermaid
graph TD
    subgraph "Repository Root"
        ROOT["openlens-ai/"]
        LICENSE_FILE["LICENSE"]
        ENV_EXAMPLE[".env.example"]
        README["README.md"]
    end
    
    subgraph "Core System Modules"
        BUILD_GRAPH["build_graph.py"]
        AGENT_MODULES["agent_*.py files"]
        UTILS["utilities and helpers"]
    end
    
    subgraph "LLM Infrastructure"
        LLM_ROUTER["LLM router components"]
        MODEL_DEPLOYMENT["vLLM deployment scripts"]
        CONFIG_YAML["YAML configuration files"]
    end
    
    subgraph "Evaluation Framework"
        EVAL_SCRIPTS["evaluation scripts"]
        TEST_DATA["test datasets"]
        PARALLEL_TESTING["parallel testing tools"]
    end
    
    subgraph "Development Environment"
        DOCKER_CONFIG["Docker configurations"]
        EDITOR_CONFIG["editor settings"]
        GITHUB_CONFIG["GitHub templates and settings"]
    end
    
    ROOT --> LICENSE_FILE
    ROOT --> ENV_EXAMPLE
    ROOT --> README
    ROOT --> BUILD_GRAPH
    ROOT --> AGENT_MODULES
    ROOT --> UTILS
    ROOT --> LLM_ROUTER
    ROOT --> MODEL_DEPLOYMENT
    ROOT --> CONFIG_YAML
    ROOT --> EVAL_SCRIPTS
    ROOT --> TEST_DATA
    ROOT --> PARALLEL_TESTING
    ROOT --> DOCKER_CONFIG
    ROOT --> EDITOR_CONFIG
    ROOT --> GITHUB_CONFIG
```

Sources: [LICENSE:1-26](), [.env.example:1-38]()

## Key System Integration Points

This diagram illustrates how the major system components integrate through configuration and code entities:

```mermaid
graph TB
    subgraph "Configuration Layer"
        ENV_VARS["Environment Variables"]
        API_KEYS_CONFIG["API Key Management"]
        MODEL_SELECTION["Model Selection"]
        LIMITS_CONFIG["Token and Iteration Limits"]
    end
    
    subgraph "Agent System"
        SUPERVISOR_AGENT["supervisor_agent.py"]
        LITERATURE_AGENT["literature_reviewer_agent.py"]
        DATA_AGENT["data_analyzer_agent.py"]
        CODER_AGENT["coder_agent.py"]
        LATEX_AGENT["latex_writer_agent.py"]
    end
    
    subgraph "Execution Environment"
        LANGGRAPH_STATE["LangGraph shared state"]
        OPENHANDS_EXEC["OpenHands execution environment"]
        DOCKER_RUNTIME["agent-med-cpu container"]
    end
    
    subgraph "External Services"
        GLM_MODELS["GLM-4.5-air, GLM-4.1v models"]
        BGE_RERANKER["bge-reranker-v2-m3"]
        TAVILY_API["Tavily search API"]
        LANGSMITH_SERVICE["LangSmith tracing service"]
    end
    
    ENV_VARS --> API_KEYS_CONFIG
    ENV_VARS --> MODEL_SELECTION
    ENV_VARS --> LIMITS_CONFIG
    
    API_KEYS_CONFIG --> GLM_MODELS
    API_KEYS_CONFIG --> BGE_RERANKER
    API_KEYS_CONFIG --> TAVILY_API
    API_KEYS_CONFIG --> LANGSMITH_SERVICE
    
    MODEL_SELECTION --> SUPERVISOR_AGENT
    MODEL_SELECTION --> LITERATURE_AGENT
    MODEL_SELECTION --> DATA_AGENT
    MODEL_SELECTION --> CODER_AGENT
    MODEL_SELECTION --> LATEX_AGENT
    
    LIMITS_CONFIG --> LANGGRAPH_STATE
    LIMITS_CONFIG --> OPENHANDS_EXEC
    
    SUPERVISOR_AGENT --> LANGGRAPH_STATE
    LITERATURE_AGENT --> LANGGRAPH_STATE
    DATA_AGENT --> LANGGRAPH_STATE
    CODER_AGENT --> LANGGRAPH_STATE
    LATEX_AGENT --> LANGGRAPH_STATE
    
    CODER_AGENT --> OPENHANDS_EXEC
    DATA_AGENT --> OPENHANDS_EXEC
    OPENHANDS_EXEC --> DOCKER_RUNTIME
```

Sources: [.env.example:1-38]()

## License Information

OpenLens AI is released under the MIT License, which provides broad permissions for use, modification, and distribution.

### MIT License Summary

The MIT License grants the following permissions:
- **Use**: Run the software for any purpose
- **Copy**: Make copies of the software
- **Modify**: Alter the software's source code
- **Distribute**: Share copies of the software
- **Sublicense**: Include the software in projects with different licenses
- **Sell**: Use the software commercially

### License Requirements

The license requires:
- **Copyright Notice**: Include the original copyright notice
- **License Text**: Include the full license text in substantial portions

### Disclaimer

The software is provided "AS IS" without warranty of any kind. The authors are not liable for any damages arising from the use of the software.

Sources: [LICENSE:1-26]()

## Version and Copyright Information

- **License Type**: MIT License
- **Copyright Year**: 2023
- **License File**: [`LICENSE`]()

The full license text is available in the repository root directory and must be included in any distribution of the software.

Sources: [LICENSE:1-26]()

---

