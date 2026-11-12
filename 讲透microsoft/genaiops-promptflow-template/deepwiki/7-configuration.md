<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/genaiops-promptflow-template · page 7 Configuration · fetched 2026-10-26 -->

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/class_flows_pr_dev_workflow.yml](.github/workflows/class_flows_pr_dev_workflow.yml)
- [.github/workflows/function_flows_ci_dev_workflow.yml](.github/workflows/function_flows_ci_dev_workflow.yml)
- [.github/workflows/function_flows_pr_dev_workflow.yml](.github/workflows/function_flows_pr_dev_workflow.yml)
- [chat_with_pdf/configs/deployment_config.json](chat_with_pdf/configs/deployment_config.json)
- [class_flows/configs/deployment_config.json](class_flows/configs/deployment_config.json)
- [docs/faqs.md](docs/faqs.md)
- [function_flows/configs/deployment_config.json](function_flows/configs/deployment_config.json)
- [llmops/common/common.py](llmops/common/common.py)
- [llmops/common/create_connections.py](llmops/common/create_connections.py)
- [llmops/common/deployment/generate_env_vars.py](llmops/common/deployment/generate_env_vars.py)
- [llmops/common/experiment.py](llmops/common/experiment.py)
- [llmops/config.py](llmops/config.py)
- [math_coding/configs/deployment_config.json](math_coding/configs/deployment_config.json)
- [named_entity_recognition/configs/deployment_config.json](named_entity_recognition/configs/deployment_config.json)
- [web_classification/configs/deployment_config.json](web_classification/configs/deployment_config.json)

</details>



This document covers the configuration system used throughout the LLMOps Prompt Flow template, including experiment configuration, deployment configuration, environment variable management, and connection setup. The configuration system supports multiple environments (dev, prod, pr) and provides flexible override mechanisms.

For specific details about experiment configuration files, see [Experiment Configuration](#7.1). For deployment-specific configuration, see [Deployment Configuration](#7.2). For environment variables and secrets management, see [Environment and Secrets Management](#7.3).

## Configuration Architecture

The template uses a multi-layered configuration approach with several interconnected configuration files and mechanisms:

```mermaid
graph TB
    subgraph "Global Configuration"
        CONFIG["config.py<br/>EXECUTION_TYPE"]
    end
    
    subgraph "Use Case Configuration"
        EXPERIMENT["experiment.yaml<br/>Base experiment config"]
        EXPERIMENT_ENV["experiment.{env}.yaml<br/>Environment overlays"]
        DEPLOYMENT["deployment_config.json<br/>Endpoint configurations"]
    end
    
    subgraph "Environment Configuration"
        ENV_YAML["env.yaml<br/>Environment variables"]
        DOT_ENV[".env<br/>Local secrets"]
        INIT_JSON["init.json<br/>Flow initialization"]
    end
    
    subgraph "Runtime Resolution"
        RESOLVE_ENV["resolve_env_vars()<br/>common.py:48-92"]
        LOAD_EXP["load_experiment()<br/>experiment.py:742-780"]
        CREATE_CONN["create_pf_connections()<br/>create_connections.py:33-103"]
    end
    
    CONFIG --> RESOLVE_ENV
    ENV_YAML --> RESOLVE_ENV
    DOT_ENV --> RESOLVE_ENV
    
    EXPERIMENT --> LOAD_EXP
    EXPERIMENT_ENV --> LOAD_EXP
    LOAD_EXP --> CREATE_CONN
    
    RESOLVE_ENV --> CREATE_CONN
```

Sources: [llmops/config.py:1-12](), [llmops/common/common.py:48-92](), [llmops/common/experiment.py:742-780](), [llmops/common/create_connections.py:33-103]()

## Configuration File Types

The template uses several types of configuration files, each serving a specific purpose:

| Configuration Type | File Pattern | Purpose | Location |
|---|---|---|---|
| Global Execution | `config.py` | Controls local vs Azure execution | `llmops/config.py` |
| Experiment Base | `experiment.yaml` | Defines flows, datasets, evaluators | `{use_case}/experiment.yaml` |
| Environment Overlay | `experiment.{env}.yaml` | Environment-specific overrides | `{use_case}/experiment.{env}.yaml` |
| Deployment | `deployment_config.json` | Endpoint deployment settings | `{use_case}/configs/deployment_config.json` |
| Environment Variables | `env.yaml` | Environment variable definitions | `{use_case}/environment/env.yaml` |
| Local Secrets | `.env` | Local development secrets | Project root |
| Flow Initialization | `init.json` | Class flow initialization parameters | `{use_case}/flows/{flow}/init.json` |

Sources: [llmops/config.py:1-12](), [named_entity_recognition/configs/deployment_config.json:1-56](), [llmops/common/common.py:48-92]()

## Execution Type Configuration

The global execution mode is controlled by the `EXECUTION_TYPE` setting in [llmops/config.py:11](). This determines whether operations run locally or on Azure:

```python
EXECUTION_TYPE = "LOCAL"  # or "AZURE"
```

This setting affects how the prompt pipeline and evaluation scripts execute, with local execution using the Prompt Flow client directly and Azure execution using the Azure ML workspace.

Sources: [llmops/config.py:1-12]()

## Environment Variable Resolution

The environment variable resolution system supports hierarchical configuration with placeholder substitution:

```mermaid
flowchart TD
    START["resolve_env_vars()"] --> CHECK_YAML["Check env.yaml exists<br/>common.py:56-57"]
    CHECK_YAML -->|No| EMPTY["Return empty dict<br/>common.py:90-91"]
    CHECK_YAML -->|Yes| LOAD_YAML["Load YAML content<br/>common.py:58-60"]
    
    LOAD_YAML --> ITERATE["Iterate key-value pairs<br/>common.py:61-63"]
    ITERATE --> CHECK_ENV["Check if env var exists<br/>common.py:65-68"]
    CHECK_ENV -->|Yes| USE_ENV["Use existing env value<br/>common.py:67-68"]
    CHECK_ENV -->|No| CHECK_PLACEHOLDER["Check for ${} placeholder<br/>common.py:71-74"]
    
    CHECK_PLACEHOLDER -->|No| SET_DIRECT["Set value directly<br/>common.py:86-88"]
    CHECK_PLACEHOLDER -->|Yes| RESOLVE_REF["Resolve reference<br/>common.py:76-84"]
    
    RESOLVE_REF -->|Success| SET_RESOLVED["Set resolved value<br/>common.py:79-81"]
    RESOLVE_REF -->|Fail| ERROR["Raise ValueError<br/>common.py:83-84"]
    
    USE_ENV --> CONTINUE["Continue iteration"]
    SET_DIRECT --> CONTINUE
    SET_RESOLVED --> CONTINUE
    CONTINUE --> ITERATE
```

The resolution process handles three types of values:
- **Direct values**: Set as-is in the environment
- **Existing environment variables**: Preserved if already set
- **Placeholder references**: `${VARIABLE_NAME}` syntax resolved from environment

Sources: [llmops/common/common.py:48-92]()

## Connection Configuration

Connection configuration enables integration with external services like Azure OpenAI, Cognitive Search, and custom APIs:

```mermaid
graph LR
    subgraph "Connection Definition"
        EXP_CONN["experiment.yaml<br/>connections section"]
        CONN_TYPES["Supported Types:<br/>- AzureOpenAIConnection<br/>- OpenAIConnection<br/>- CognitiveSearchConnection<br/>- CustomConnection<br/>- FormRecognizerConnection"]
    end
    
    subgraph "Connection Creation"
        CREATE_FUNC["create_pf_connections()<br/>create_connections.py:33"]
        CONN_CLASSES["CONNECTION_CLASSES<br/>create_connections.py:22-30"]
        VALIDATE["_get_valid_connection_values()<br/>create_connections.py:105-118"]
    end
    
    subgraph "Connection Resolution"
        ENV_VARS["Environment Variables<br/>${connection}_{property}"]
        PF_CLIENT["PFClient.connections<br/>create_or_update()"]
    end
    
    EXP_CONN --> CREATE_FUNC
    CONN_TYPES --> CONN_CLASSES
    CREATE_FUNC --> VALIDATE
    VALIDATE --> ENV_VARS
    VALIDATE --> PF_CLIENT
```

Connection properties support placeholder resolution where values like `${api_key}` are resolved to environment variables following the pattern `{CONNECTION_NAME}_{PROPERTY}` in uppercase.

Sources: [llmops/common/create_connections.py:22-119](), [llmops/common/experiment.py:626-687]()

## Flow Type Resolution

The system automatically detects flow types based on the files present in the flow directory:

```mermaid
graph TD
    RESOLVE["resolve_flow_type()<br/>common.py:95-206"] --> SCAN["Scan flow directory<br/>common.py:109-121"]
    SCAN --> CHECK_FLEX["Found flow.flex.yaml?<br/>common.py:111-115"]
    SCAN --> CHECK_DAG["Found flow.dag.yaml?<br/>common.py:116-120"]
    
    CHECK_FLEX -->|Yes| PARSE_FLEX["Parse flex file<br/>common.py:127-135"]
    CHECK_DAG -->|Yes & No Flex| DAG_FLOW["FlowTypeOption.DAG_FLOW<br/>common.py:202-204"]
    CHECK_FLEX -->|No| CHECK_DAG
    CHECK_DAG -->|No| NO_FLOW["FlowTypeOption.NO_FLOW<br/>common.py:122-124"]
    
    PARSE_FLEX --> CHECK_ENTRY["Check entry type<br/>common.py:138-147"]
    CHECK_ENTRY -->|Class| CLASS_FLOW["FlowTypeOption.CLASS_FLOW<br/>common.py:198"]
    CHECK_ENTRY -->|Function| FUNC_FLOW["FlowTypeOption.FUNCTION_FLOW<br/>common.py:200"]
    
    CLASS_FLOW --> LOAD_INIT["Load init.json<br/>common.py:150-197"]
```

This automatic detection enables the system to handle different flow types (DAG, Function, Class) with appropriate initialization parameters.

Sources: [llmops/common/common.py:95-206]()

## Deployment Configuration Structure

Each use case contains a standardized deployment configuration supporting multiple endpoint types:

```mermaid
graph TB
    subgraph "deployment_config.json Structure"
        ROOT["deployment_config.json"]
        
        subgraph "Azure Managed Endpoint"
            AME_CONFIG["azure_managed_endpoint[]<br/>- ENV_NAME<br/>- ENDPOINT_NAME<br/>- DEPLOYMENT_VM_SIZE<br/>- DEPLOYMENT_INSTANCE_COUNT"]
        end
        
        subgraph "Kubernetes Endpoint"
            K8S_CONFIG["kubernetes_endpoint[]<br/>- COMPUTE_NAME<br/>- CPU_ALLOCATION<br/>- MEMORY_ALLOCATION"]
        end
        
        subgraph "WebApp Endpoint"
            WEBAPP_CONFIG["webapp_endpoint[]<br/>- APP_PLAN_NAME<br/>- WEB_APP_NAME<br/>- WEB_APP_SKU<br/>- USER_MANAGED_ID"]
        end
    end
    
    ROOT --> AME_CONFIG
    ROOT --> K8S_CONFIG
    ROOT --> WEBAPP_CONFIG
```

Each endpoint type supports environment-specific configuration through the `ENV_NAME` field, allowing different settings for dev, prod, and pr environments.

Sources: [named_entity_recognition/configs/deployment_config.json:1-56](), [web_classification/configs/deployment_config.json:1-56](), [math_coding/configs/deployment_config.json:1-56]()

## Configuration Override Hierarchy

The configuration system supports environment-specific overrides through a layered approach:

1. **Base Configuration**: `experiment.yaml` contains common settings
2. **Environment Overlays**: `experiment.{env}.yaml` files override base settings
3. **Environment Variables**: Runtime values from `env.yaml` and `.env`
4. **CI/CD Variables**: Platform-specific secrets and variables

This hierarchy allows the same codebase to work across multiple environments with appropriate configuration differences while maintaining a single source of truth for common settings.

Sources: [llmops/common/experiment.py:690-740](), [docs/faqs.md:216-223]()

---

