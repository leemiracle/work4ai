<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/olmo-cookbook · page 3 Command Line Interface · fetched 2026-10-26 -->

# Command Line Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pyproject.toml](pyproject.toml)
- [src/cookbook/cli/utils.py](src/cookbook/cli/utils.py)

</details>



This document provides an overview of the command line interface structure in the olmo-cookbook repository. It covers the four main CLI entry points, their organization, shared utilities, and common patterns used across all command-line tools. For detailed documentation of specific CLI commands, see [Evaluation CLI](#3.1), [Training CLI](#3.2), and [Infrastructure CLI](#3.3).

## CLI Architecture Overview

The olmo-cookbook provides four distinct command-line interfaces, each targeting different workflows in the machine learning pipeline. These CLIs share common utilities and patterns while providing specialized functionality for their respective domains.

**CLI Architecture and Entry Points**
```mermaid
graph TB
    subgraph "CLI Entry Points"
        MAIN_CLI[olmo-cookbook]
        EVAL_CLI[olmo-cookbook-eval] 
        CORE_CLI[olmo-cookbook-core]
        PMR_CLI[poormanray]
    end
    
    subgraph "CLI Module Structure"
        CLI_DIR["cookbook.cli"]
        CLI_MODULE["cli.cli"]
        EVAL_MODULE["eval.cli"]
        CORE_MODULE["core.cli"]
        PMR_MODULE["pmr.cli"]
        UTILS_MODULE["utils.py"]
    end
    
    subgraph "Shared Utilities"
        PYTHON_ENV["PythonEnv"]
        AUTH_UTILS["Authentication Functions"]
        PKG_MGMT["Package Management"]
        REPO_CLONE["Repository Cloning"]
        SECRET_MGMT["Secret Management"]
    end
    
    subgraph "Target Systems"
        TRAINING["Training System"]
        EVALUATION["Evaluation System"]
        INFRASTRUCTURE["Infrastructure Management"]
        CONVERSION["Model Conversion"]
    end
    
    MAIN_CLI --> CLI_MODULE
    EVAL_CLI --> EVAL_MODULE
    CORE_CLI --> CORE_MODULE
    PMR_CLI --> PMR_MODULE
    
    CLI_MODULE --> CLI_DIR
    EVAL_MODULE --> CLI_DIR
    CORE_MODULE --> CLI_DIR
    PMR_MODULE --> CLI_DIR
    
    CLI_DIR --> UTILS_MODULE
    
    UTILS_MODULE --> PYTHON_ENV
    UTILS_MODULE --> AUTH_UTILS
    UTILS_MODULE --> PKG_MGMT
    UTILS_MODULE --> REPO_CLONE
    UTILS_MODULE --> SECRET_MGMT
    
    MAIN_CLI --> TRAINING
    EVAL_CLI --> EVALUATION
    EVAL_CLI --> CONVERSION
    CORE_CLI --> TRAINING
    PMR_CLI --> INFRASTRUCTURE
```

Sources: [pyproject.toml:57-61](), [src/cookbook/cli/utils.py:1-654]()

## Entry Points and Organization

The CLI system is organized around four main entry points, each defined in the project configuration and implemented as separate command modules.

| CLI Command | Entry Point | Module Path | Primary Purpose |
|-------------|-------------|-------------|-----------------|
| `olmo-cookbook` | `cookbook.cli:cli.cli` | `cookbook/cli/cli.py` | Model training orchestration |
| `olmo-cookbook-eval` | `cookbook.cli:eval.cli` | `cookbook/cli/eval.py` | Model evaluation and conversion |
| `olmo-cookbook-core` | `cookbook.cli:core.cli` | `cookbook/cli/core.py` | Core training functionality |
| `poormanray` | `cookbook.cli:pmr.cli` | `cookbook/cli/pmr.py` | Infrastructure management |

Sources: [pyproject.toml:57-61]()

## Common Utilities and Patterns

All CLI modules share a common set of utilities implemented in the `utils.py` module. These utilities handle cross-cutting concerns like environment management, authentication, and package installation.

**Utility Functions and Their Roles**
```mermaid
graph TB
    subgraph "Environment Management"
        PYTHON_ENV_CLASS["PythonEnv"]
        CREATE_ENV["PythonEnv.create()"]
        NULL_ENV["PythonEnv.null()"]
        FIND_ROOT["_find_root_dir()"]
    end
    
    subgraph "Package Installation"
        INSTALL_BEAKER["install_beaker_py()"]
        INSTALL_OE_EVAL["install_oe_eval()"]
        INSTALL_OLMO["install_olmo()"]
        INSTALL_OLMO_CORE["install_olmo_core()"]
        INSTALL_TRANSFORMERS["install_transformers()"]
    end
    
    subgraph "Authentication"
        GET_HF_TOKEN["get_huggingface_token()"]
        GET_AWS_KEY["get_aws_access_key_id()"]
        GET_AWS_SECRET["get_aws_secret_access_key()"]
        GET_BEAKER_TOKEN["get_beaker_token()"]
        GET_BEAKER_USER["get_beaker_user()"]
    end
    
    subgraph "Repository Management"
        CLONE_REPO["clone_repository()"]
        FIND_REPO_ROOT["find_repository_root()"]
    end
    
    subgraph "Secret Management"
        ADD_SECRET["add_secret_to_beaker_workspace()"]
        CHECK_SECRET["check_if_secret_exists_in_beaker_workspace()"]
        ADD_AWS_FLAGS["add_aws_flags()"]
    end
    
    PYTHON_ENV_CLASS --> CREATE_ENV
    PYTHON_ENV_CLASS --> NULL_ENV
    CREATE_ENV --> FIND_ROOT
    
    INSTALL_BEAKER --> PYTHON_ENV_CLASS
    INSTALL_OE_EVAL --> INSTALL_BEAKER
    INSTALL_OE_EVAL --> CLONE_REPO
    INSTALL_OLMO --> CLONE_REPO
    INSTALL_OLMO_CORE --> CLONE_REPO
    INSTALL_TRANSFORMERS --> CLONE_REPO
    
    ADD_AWS_FLAGS --> CHECK_SECRET
    ADD_AWS_FLAGS --> ADD_SECRET
```

Sources: [src/cookbook/cli/utils.py:28-87](), [src/cookbook/cli/utils.py:150-243](), [src/cookbook/cli/utils.py:89-148](), [src/cookbook/cli/utils.py:417-459](), [src/cookbook/cli/utils.py:290-355]()

## Environment Management

The CLI system uses a sophisticated virtual environment management system through the `PythonEnv` class. This allows for isolated package installations and consistent dependency management across different execution contexts.

### PythonEnv Class Structure

The `PythonEnv` class provides three main modes of operation:

- **Isolated Environment**: Created with `PythonEnv.create()` for dependency isolation
- **System Environment**: Created with `PythonEnv.null()` for direct system usage
- **Named Environment**: Custom environments with specific naming and location

```python
# Key methods and properties from PythonEnv
@dataclass(frozen=True)
class PythonEnv:
    name: Optional[str]
    python: str
    pip: str
    
    def path(self) -> dict  # Environment variables with PATH setup
    @classmethod
    def create(cls, name, force=False, root=None) -> "PythonEnv"
    @classmethod  
    def null(cls) -> "PythonEnv"  # Uses system python/pip
```

Sources: [src/cookbook/cli/utils.py:28-87]()

## Package Installation and Dependency Management

The CLI utilities provide functions for installing various ML packages with proper dependency resolution and version management.

### Installation Functions

| Function | Purpose | Key Dependencies |
|----------|---------|------------------|
| `install_beaker_py()` | Beaker client and gantry | `beaker-py`, `beaker-gantry` |
| `install_oe_eval()` | OE-Eval evaluation toolkit | OE-Eval repository, beaker dependencies |
| `install_olmo()` | OLMo training framework | OLMo repository with `[train]` extras |
| `install_olmo_core()` | OLMo-core training system | OLMo-core repository |
| `install_transformers()` | HuggingFace Transformers | Transformers repository, accelerate, torchao |

The installation functions handle complex scenarios like:
- Commit-specific installations from git repositories
- Editable installations for development
- Dependency conflict resolution
- Version compatibility checks

Sources: [src/cookbook/cli/utils.py:150-173](), [src/cookbook/cli/utils.py:174-243](), [src/cookbook/cli/utils.py:462-489](), [src/cookbook/cli/utils.py:552-575]()

## External System Integration

The CLI system integrates with multiple external platforms and services, providing unified authentication and configuration management.

**External System Integration Flow**
```mermaid
graph LR
    subgraph "CLI Layer"
        CLI_COMMANDS["CLI Commands"]
        AUTH_LAYER["Authentication Layer"]
        CONFIG_LAYER["Configuration Layer"]
    end
    
    subgraph "External Platforms"
        BEAKER_PLATFORM["Beaker Platform"]
        AWS_SERVICES["AWS Services"]
        HF_HUB["HuggingFace Hub"]
        WANDB_SERVICE["Weights & Biases"]
    end
    
    subgraph "Authentication Sources"
        ENV_VARS["Environment Variables"]
        CONFIG_FILES["Configuration Files"]
        CLI_TOOLS["CLI Tools (aws, beaker)"]
        TOKEN_FILES["Token Files"]
    end
    
    CLI_COMMANDS --> AUTH_LAYER
    AUTH_LAYER --> CONFIG_LAYER
    
    CONFIG_LAYER --> BEAKER_PLATFORM
    CONFIG_LAYER --> AWS_SERVICES
    CONFIG_LAYER --> HF_HUB
    CONFIG_LAYER --> WANDB_SERVICE
    
    ENV_VARS --> AUTH_LAYER
    CONFIG_FILES --> AUTH_LAYER
    CLI_TOOLS --> AUTH_LAYER
    TOKEN_FILES --> AUTH_LAYER
```

Sources: [src/cookbook/cli/utils.py:89-102](), [src/cookbook/cli/utils.py:104-147](), [src/cookbook/cli/utils.py:316-336]()

## Authentication and Credentials

The CLI system provides comprehensive authentication support for various external services, with multiple fallback mechanisms for credential discovery.

### Authentication Functions

- **HuggingFace**: `get_huggingface_token()` - checks environment variables and token files
- **AWS**: `get_aws_access_key_id()` and `get_aws_secret_access_key()` - supports CLI, environment, and credential files
- **Beaker**: `get_beaker_token()` and `get_beaker_user()` - uses Beaker client configuration

### Secret Management

The system includes functions for managing secrets in Beaker workspaces:
- `add_secret_to_beaker_workspace()` - adds or updates workspace secrets
- `check_if_secret_exists_in_beaker_workspace()` - verifies secret existence
- `add_aws_flags()` - automatically configures AWS secrets for Beaker jobs

Sources: [src/cookbook/cli/utils.py:89-102](), [src/cookbook/cli/utils.py:104-147](), [src/cookbook/cli/utils.py:290-355](), [src/cookbook/cli/utils.py:357-392]()

---

