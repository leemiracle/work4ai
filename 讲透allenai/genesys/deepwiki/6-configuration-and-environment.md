<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/genesys · page 6 Configuration and Environment · fetched 2026-10-26 -->

# Configuration and Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [bin/pages/config.py](bin/pages/config.py)

</details>



This document covers the configuration management and environment setup for the Genesys system. It details how the system manages its runtime configuration, environment variables, artifact storage, and deployment settings across development and production environments.

For deployment infrastructure details, see [Deployment and Infrastructure](#6). For Streamlit-specific UI configuration, see [Streamlit Configuration](#5.1).

## System Configuration Architecture

The Genesys system employs a multi-layered configuration approach that separates concerns between user interface theming, environment management, and artifact handling. The configuration system supports both local development and distributed deployment scenarios.

### Configuration Flow

```mermaid
graph TB
    subgraph "Configuration Sources"
        STREAMLIT_CONFIG[".streamlit/config.toml<br/>UI Theme Configuration"]
        DOCKERIGNORE[".dockerignore<br/>Build Artifact Control"]
        ENV_VARS["Environment Variables<br/>API Keys & Paths"]
        CLI_ARGS["CLI Arguments<br/>Runtime Parameters"]
    end
    
    subgraph "Application Layer"
        STREAMLIT_APP["bin/app.py<br/>Main Application"]
        CLI_INTERFACE["cli.py<br/>Command Interface"]
        PAGE_COMPONENTS["bin/pages/*<br/>UI Components"]
    end
    
    subgraph "Runtime Environment"
        DATA_DIRS["Data Directories<br/>wandb/, data/, ckpt/"]
        SECRETS_MGMT["Secrets Management<br/>API Keys Storage"]
        ARTIFACT_STORAGE["Artifact Storage<br/>Models & Checkpoints"]
    end
    
    subgraph "External Services"
        FIREBASE["Firebase<br/>Distributed Coordination"]
        WANDB["Weights & Biases<br/>Experiment Tracking"]
        LLM_APIS["LLM APIs<br/>OpenAI, Anthropic, Together"]
    end
    
    STREAMLIT_CONFIG --> STREAMLIT_APP
    DOCKERIGNORE --> STREAMLIT_APP
    ENV_VARS --> CLI_INTERFACE
    CLI_ARGS --> CLI_INTERFACE
    
    STREAMLIT_APP --> PAGE_COMPONENTS
    CLI_INTERFACE --> PAGE_COMPONENTS
    
    PAGE_COMPONENTS --> DATA_DIRS
    PAGE_COMPONENTS --> SECRETS_MGMT
    PAGE_COMPONENTS --> ARTIFACT_STORAGE
    
    SECRETS_MGMT --> FIREBASE
    SECRETS_MGMT --> WANDB
    SECRETS_MGMT --> LLM_APIS
```

Sources: [.streamlit/config.toml:1-4](), [.dockerignore:1-187]()

## Environment Management Strategy

The system implements a comprehensive environment management strategy that handles sensitive data, artifact storage, and build optimization through multiple configuration layers.

### Artifact Management and Build Optimization

```mermaid
graph LR
    subgraph "Development Artifacts"
        WANDB_DIR["wandb/<br/>Experiment Logs"]
        DATA_DIR["data/<br/>Training Data"]
        CKPT_DIR["ckpt/<br/>Model Checkpoints"]
        SECRETS_DIR["secrets/<br/>API Keys"]
    end
    
    subgraph "Build Process"
        DOCKERIGNORE_RULES[".dockerignore<br/>Exclusion Rules"]
        DOCKER_BUILD["Docker Build<br/>Container Creation"]
        ARTIFACT_FILTER["Artifact Filtering<br/>Size Optimization"]
    end
    
    subgraph "Runtime Environment"
        CONTAINER_ENV["Container Environment<br/>Production Runtime"]
        LOCAL_ENV["Local Environment<br/>Development Runtime"]
        MOUNTED_VOLUMES["Mounted Volumes<br/>Persistent Storage"]
    end
    
    WANDB_DIR --> DOCKERIGNORE_RULES
    DATA_DIR --> DOCKERIGNORE_RULES
    CKPT_DIR --> DOCKERIGNORE_RULES
    SECRETS_DIR --> DOCKERIGNORE_RULES
    
    DOCKERIGNORE_RULES --> DOCKER_BUILD
    DOCKER_BUILD --> ARTIFACT_FILTER
    ARTIFACT_FILTER --> CONTAINER_ENV
    
    WANDB_DIR --> LOCAL_ENV
    DATA_DIR --> LOCAL_ENV
    CKPT_DIR --> LOCAL_ENV
    
    CONTAINER_ENV --> MOUNTED_VOLUMES
    LOCAL_ENV --> MOUNTED_VOLUMES
```

Sources: [.dockerignore:1-11](), [.dockerignore:144-151]()

## Configuration Categories

### User Interface Configuration

The system uses Streamlit's configuration system to provide a consistent dark theme optimized for technical users working with complex ML visualizations.

| Configuration Key | Value | Purpose |
|------------------|-------|---------|
| `theme.base` | `"dark"` | Base theme for reduced eye strain |
| `theme.primaryColor` | `"#8D4BBB"` | Purple accent color for UI elements |
| `theme.font` | `"serif"` | Serif font for improved readability |

The configuration supports the system's technical interface requirements while maintaining visual consistency across all pages and components.

Sources: [.streamlit/config.toml:1-4]()

### Build and Deployment Configuration

The Docker ignore configuration implements a comprehensive exclusion strategy that optimizes container build performance and security:

#### Data and Artifact Exclusions
- **Experiment Data**: `wandb/`, `data/`, `ckpt/` directories containing large training datasets and model checkpoints
- **Security**: `secrets/` directory and API key files
- **Development Files**: `quicknote.md`, `README.md`, and other documentation

#### Python Environment Exclusions
- **Bytecode**: `__pycache__/`, `*.py[cod]`, `*$py.class` files
- **Virtual Environments**: `.env`, `.venv`, `env/`, `venv/` directories
- **Package Management**: `*.egg-info/`, `dist/`, `build/` directories

#### Development Tool Exclusions
- **Testing**: `.pytest_cache/`, `coverage.xml`, `htmlcov/` directories
- **IDE Files**: `.idea/`, `.vscode/`, `.DS_Store` files
- **Version Control**: Git-related temporary files and directories

Sources: [.dockerignore:1-11](), [.dockerignore:18-46](), [.dockerignore:144-151]()

### Environment Variable Management

The system relies on environment variables for configuration of external service integrations and runtime parameters. Key categories include:

- **API Authentication**: Keys for OpenAI, Anthropic, Together AI, and other LLM providers
- **Database Configuration**: Firebase connection parameters and authentication
- **Storage Paths**: Data directory locations and checkpoint storage paths
- **Experiment Tracking**: Weights & Biases project configuration

The environment variable system supports both development and production deployments through flexible configuration inheritance.

Sources: [.dockerignore:144-151]()

## Integration with System Components

The configuration system integrates tightly with the distributed evolution architecture, providing consistent settings across all nodes and components in the system.

### Configuration Distribution Pattern

```mermaid
graph TB
    subgraph "Configuration Management"
        CONFIG_SOURCE["Configuration Sources<br/>Files & Environment"]
        CONFIG_LOADER["Configuration Loader<br/>Runtime Initialization"]
        CONFIG_VALIDATOR["Configuration Validator<br/>Settings Verification"]
    end
    
    subgraph "Distributed Components"
        COMMAND_CENTER["CommandCenter<br/>bin/pages/evolve.py"]
        LISTENER_NODES["Listener Nodes<br/>bin/pages/listen.py"]
        DESIGN_ENGINE["Design Engine<br/>bin/pages/design.py"]
        VERIFY_ENGINE["Verification Engine<br/>bin/pages/verify.py"]
    end
    
    subgraph "External Dependencies"
        FIREBASE_CONFIG["Firebase Configuration<br/>Distributed Coordination"]
        API_CONFIGS["API Configurations<br/>LLM Service Access"]
        STORAGE_CONFIGS["Storage Configurations<br/>Data & Checkpoints"]
    end
    
    CONFIG_SOURCE --> CONFIG_LOADER
    CONFIG_LOADER --> CONFIG_VALIDATOR
    CONFIG_VALIDATOR --> COMMAND_CENTER
    CONFIG_VALIDATOR --> LISTENER_NODES
    CONFIG_VALIDATOR --> DESIGN_ENGINE
    CONFIG_VALIDATOR --> VERIFY_ENGINE
    
    COMMAND_CENTER --> FIREBASE_CONFIG
    LISTENER_NODES --> API_CONFIGS
    DESIGN_ENGINE --> API_CONFIGS
    VERIFY_ENGINE --> STORAGE_CONFIGS
```

Sources: [.streamlit/config.toml:1-4](), [.dockerignore:1-187]()

The configuration system ensures that all components of the distributed evolution system maintain consistent settings and can communicate effectively across the network of nodes participating in the evolutionary process.

---

