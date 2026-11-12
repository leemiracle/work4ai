<!-- source: DeepWiki mcp.deepwiki.com · repo jarrycyx/openlens-ai · page 4 LLM Router Infrastructure · fetched 2026-10-27 -->

# LLM Router Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [llm_router/create_yaml.py](llm_router/create_yaml.py)
- [llm_router/proxy_update.sh](llm_router/proxy_update.sh)

</details>



The LLM Router Infrastructure provides centralized language model routing, load balancing, and API key management for OpenLens AI. This system acts as a proxy layer between the multi-agent system and external language model providers, enabling efficient distribution of requests across multiple API keys and model endpoints while maintaining high availability and performance.

For information about configuring specific models, see [Model Configuration](#4.1). For details on vLLM deployment, see [vLLM Deployment](#4.2). For performance monitoring and testing, see [Performance Testing](#4.3).

## System Architecture

The router infrastructure consists of three main components: YAML configuration generation, LiteLLM proxy server, and API key management with balance validation.

### Router Infrastructure Overview

```mermaid
graph TB
    subgraph "Configuration Generation"
        API_KEY_FILES["API Key Files<br/>keys_*.txt"]
        CREATE_YAML["create_yaml.py<br/>YAML Generator"]
        MODEL_LIST_YAML["model_list.yaml<br/>LiteLLM Config"]
        EXTRA_MODEL_LIST["extra_model_list.yaml<br/>Additional Models"]
    end
    
    subgraph "Balance Validation"
        CHECK_BALANCE["check_balance()<br/>SiliconFlow API"]
        MULTIPROCESS_POOL["Pool(processes)<br/>Parallel Validation"]
        VALID_KEYS["valid_keys<br/>Filtered API Keys"]
    end
    
    subgraph "LiteLLM Proxy Server"
        LITELLM_PROXY["LiteLLM Proxy<br/>Port 8077"]
        ROUTER_SETTINGS["routing_strategy<br/>simple-shuffle"]
        LANGSMITH_CALLBACK["langsmith<br/>Success Callback"]
    end
    
    subgraph "OpenLens AI Integration"
        AGENTS["Multi-Agent System"]
        EVALUATION["Evaluation Framework"]
    end
    
    API_KEY_FILES --> CREATE_YAML
    CREATE_YAML --> CHECK_BALANCE
    CHECK_BALANCE --> MULTIPROCESS_POOL
    MULTIPROCESS_POOL --> VALID_KEYS
    VALID_KEYS --> MODEL_LIST_YAML
    EXTRA_MODEL_LIST --> MODEL_LIST_YAML
    MODEL_LIST_YAML --> LITELLM_PROXY
    ROUTER_SETTINGS --> LITELLM_PROXY
    LANGSMITH_CALLBACK --> LITELLM_PROXY
    LITELLM_PROXY --> AGENTS
    LITELLM_PROXY --> EVALUATION
```

Sources: [llm_router/create_yaml.py:1-253](), [llm_router/proxy_update.sh:1-5]()

## YAML Configuration Generation

The `create_yaml.py` script orchestrates the generation of LiteLLM configuration files by processing API key files, validating account balances, and creating model entries for each valid key-model-endpoint combination.

### Configuration Generation Workflow

```mermaid
graph LR
    subgraph "Input Processing"
        READ_API_KEYS["read_api_keys()<br/>File Processing"]
        API_KEY_FILES_INPUT["keys_0909_100.txt<br/>keys_0909_200.txt"]
        ALL_API_KEYS["all_api_keys<br/>List[str]"]
    end
    
    subgraph "Balance Validation"
        CHECK_BALANCE_FUNC["check_balance()<br/>SiliconFlow API"]
        POOL_MAP["pool.map()<br/>Parallel Processing"]
        BALANCE_RESULTS["results<br/>Tuple[str, bool, float]"]
    end
    
    subgraph "Model Entry Generation"
        CREATE_MODEL_LIST["create_model_list()<br/>Main Function"]
        FORWARD_NAMES["forward_names<br/>Model Name Mapping"]
        MODEL_ENTRIES["model_entry<br/>Dict Configuration"]
    end
    
    subgraph "Output Generation"
        YAML_DUMP["yaml.dump()<br/>File Output"]
        MODEL_LIST_YAML_OUTPUT["model_list.yaml<br/>Final Configuration"]
        ROUTER_SETTINGS_OUTPUT["router_settings<br/>Routing Strategy"]
    end
    
    API_KEY_FILES_INPUT --> READ_API_KEYS
    READ_API_KEYS --> ALL_API_KEYS
    ALL_API_KEYS --> CHECK_BALANCE_FUNC
    CHECK_BALANCE_FUNC --> POOL_MAP
    POOL_MAP --> BALANCE_RESULTS
    BALANCE_RESULTS --> CREATE_MODEL_LIST
    FORWARD_NAMES --> CREATE_MODEL_LIST
    CREATE_MODEL_LIST --> MODEL_ENTRIES
    MODEL_ENTRIES --> YAML_DUMP
    YAML_DUMP --> MODEL_LIST_YAML_OUTPUT
    ROUTER_SETTINGS_OUTPUT --> MODEL_LIST_YAML_OUTPUT
```

Sources: [llm_router/create_yaml.py:35-56](), [llm_router/create_yaml.py:88-159]()

### Model Name Mapping

The system maintains a `forward_names` dictionary that maps internal model identifiers to simplified names used by LiteLLM:

| Internal Model Name | Forward Name |
|---------------------|--------------|
| `zai-org/GLM-4.5` | `glm-4.5` |
| `zai-org/GLM-4.5-Air` | `glm-4.5-air` |
| `zai-org/GLM-4.5V` | `glm-4.5v` |
| `Qwen/Qwen3-235B-A22B-Instruct-2507` | `qwen3-235b-a22b-instruct-2507` |
| `BAAI/bge-reranker-v2-m3` | `bge-reranker-v2-m3` |

The mapping is defined in [llm_router/create_yaml.py:20-30]() and applied during model entry generation in [llm_router/create_yaml.py:147]().

Sources: [llm_router/create_yaml.py:20-34](), [llm_router/create_yaml.py:147]()

## API Key Management and Load Balancing

The router implements sophisticated API key validation and load balancing through parallel balance checking and strategic key distribution.

### Balance Validation Process

The `check_balance()` function validates API keys by querying the SiliconFlow API endpoint and filtering keys based on minimum balance requirements:

```mermaid
graph TB
    subgraph "Balance Check Function"
        CHECK_BALANCE_START["check_balance(api_key)"]
        SILICONFLOW_REQUEST["GET https://api.siliconflow.cn/v1/user/info"]
        RESPONSE_PARSING["response.json()<br/>Extract balance"]
        BALANCE_VALIDATION["balance >= min_balance"]
        RETURN_TUPLE["Tuple[str, bool, float]"]
    end
    
    subgraph "Multiprocess Coordination"
        POOL_CREATION["Pool(processes=cpu_count())"]
        PARALLEL_EXECUTION["pool.map(check_balance, all_api_keys)"]
        RESULTS_AGGREGATION["Process results<br/>Filter valid keys"]
    end
    
    subgraph "Key Filtering"
        VALID_KEYS_LIST["valid_keys<br/>List[Tuple[str, float]]"]
        BALANCE_LOGGING["Print balance status<br/>Include/exclude decisions"]
        TOTAL_BALANCE["Combined balance calculation"]
    end
    
    CHECK_BALANCE_START --> SILICONFLOW_REQUEST
    SILICONFLOW_REQUEST --> RESPONSE_PARSING
    RESPONSE_PARSING --> BALANCE_VALIDATION
    BALANCE_VALIDATION --> RETURN_TUPLE
    
    POOL_CREATION --> PARALLEL_EXECUTION
    PARALLEL_EXECUTION --> RESULTS_AGGREGATION
    RESULTS_AGGREGATION --> VALID_KEYS_LIST
    VALID_KEYS_LIST --> BALANCE_LOGGING
    BALANCE_LOGGING --> TOTAL_BALANCE
```

Sources: [llm_router/create_yaml.py:58-86](), [llm_router/create_yaml.py:116-140]()

### Load Balancing Configuration

The generated configuration includes router settings that implement load balancing through `simple-shuffle` routing strategy with fallback mechanisms:

- **Routing Strategy**: `simple-shuffle` distributes requests randomly across available model instances
- **Fallbacks**: Configuration maps `glm-4.5-air` to fall back to `glm-4.5` when unavailable
- **Retry Logic**: `num_retries: 3` ensures resilience against temporary failures

The configuration is assembled in [llm_router/create_yaml.py:221-230]() and includes LangSmith integration for request tracing.

Sources: [llm_router/create_yaml.py:221-236]()

## Proxy Server Operations

The LiteLLM proxy server operates on port 8077 and serves as the central routing hub for all language model requests within OpenLens AI.

### Proxy Startup and Configuration

The `proxy_update.sh` script orchestrates the complete proxy lifecycle:

1. **Configuration Generation**: Executes `create_yaml.py` with specified API key files
2. **Proxy Launch**: Starts LiteLLM server with generated configuration
3. **Port Binding**: Binds to port 8077 for client connections

```bash
python llm_router/create_yaml.py --api-key-files llm_router/keys_0909_100.txt llm_router/keys_0909_200.txt --output llm_router/model_list.yaml
litellm --config llm_router/model_list.yaml --port 8077
```

Sources: [llm_router/proxy_update.sh:3-4]()

### Model Entry Structure

Each model entry in the generated configuration follows a standardized structure that LiteLLM uses for request routing:

```yaml
model_name: glm-4.5
litellm_params:
  model: openai/zai-org/GLM-4.5
  api_base: https://api.siliconflow.cn/v1/
  api_key: <validated_api_key>
```

This structure is generated for each combination of valid API key, model name, and API base URL in [llm_router/create_yaml.py:146-156]().

Sources: [llm_router/create_yaml.py:146-156]()

## Integration with OpenLens AI

The router infrastructure integrates seamlessly with the broader OpenLens AI system by providing a unified interface for all language model interactions.

### Client Integration Points

The router serves requests from multiple system components:

- **Multi-Agent System**: All five agents (Supervisor, Literature Reviewer, Data Analyzer, Coder, LaTeX Writer) route requests through the proxy
- **Evaluation Framework**: Parallel testing and quality assessment leverage the router for consistent model access
- **Development Environment**: Local development and testing utilize the same routing infrastructure

### Environment Configuration

The router integrates with external monitoring through environment variables:

| Variable | Purpose | Source |
|----------|---------|---------|
| `LANGSMITH_API_KEY` | Request tracing authentication | Environment |
| `LANGSMITH_PROJECT` | Project identifier for traces | Hard-coded as "litellm" |

These settings enable comprehensive request tracking and performance monitoring across the entire system.

Sources: [llm_router/create_yaml.py:231-235]()

---

