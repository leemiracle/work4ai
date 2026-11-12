<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/workbench-llamafactory · page 8 Reference & Configuration · fetched 2026-10-26 -->

# Reference & Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cache/user.config](cache/user.config)
- [data/scratch/.gitkeep](data/scratch/.gitkeep)

</details>



This document provides technical reference materials and detailed configuration options for the workbench-llamafactory system. It covers user-specific configuration files, storage directory mappings, and cache management strategies used throughout the containerized environment.

For information about environment setup and build configuration, see [Environment Setup & Build Process](#3). For data storage and version control strategies, see [Data & Version Control](#6).

## Configuration System Overview

The workbench-llamafactory system employs a multi-layered configuration approach that manages user preferences, model paths, storage locations, and cache directories. Configuration is handled through JSON files, environment variables, and directory conventions established during the container build process.

## Configuration Files Structure

```mermaid
graph TB
    subgraph "Configuration Hierarchy"
        USER_CONFIG["user.config<br/>JSON format"]
        WORKBENCH_SPEC[".project/spec.yaml<br/>Workbench configuration"]
        LLAMAFACTORY_CONFIG["LLaMA-Factory configs<br/>YAML format"]
    end
    
    subgraph "Storage Mappings"
        CACHE_DIR["cache_dir<br/>HuggingFace cache"]
        PATH_DICT["path_dict<br/>Model path mappings"]
        SCRATCH_DIR["data/scratch/<br/>Temporary files"]
    end
    
    subgraph "Runtime Environment"
        HF_CACHE["/mnt/huggingface/<br/>Volume mount"]
        PROJECT_MOUNT["/project/<br/>Container mount"]
        VENV_CONFIG["llama-factory-env<br/>Python environment"]
    end
    
    USER_CONFIG --> PATH_DICT
    USER_CONFIG --> CACHE_DIR
    WORKBENCH_SPEC --> PROJECT_MOUNT
    
    PATH_DICT --> LLAMAFACTORY_CONFIG
    CACHE_DIR --> HF_CACHE
    SCRATCH_DIR --> PROJECT_MOUNT
    
    style USER_CONFIG fill:#f9f9f9
    style SCRATCH_DIR fill:#ffebee
    style HF_CACHE fill:#e8f5e8
```

*Configuration file hierarchy and storage mappings*

Sources: [cache/user.config:1-9]()

## User Configuration Format

The `user.config` file stores user-specific settings in JSON format, including language preferences, model selections, and path mappings.

### Configuration Schema

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `lang` | string | UI language setting | `"en"` |
| `last_model` | string | Most recently used model | `"Mixtral-8x7B"` |
| `path_dict` | object | Model name to path mappings | `{"Mistral-7B-v0.1-Chat": "mistralai/Mistral-7B-Instruct-v0.1"}` |
| `cache_dir` | string/null | Custom cache directory override | `null` (uses default) |

### Model Path Dictionary

The `path_dict` object maps user-friendly model names to their corresponding Hugging Face model identifiers:

```json
{
  "path_dict": {
    "Mistral-7B-v0.1-Chat": "mistralai/Mistral-7B-Instruct-v0.1",
    "Mixtral-8x7B": "mistralai/Mixtral-8x7B-v0.1"
  }
}
```

This mapping enables the LLaMA-Factory interface to present simplified model names while maintaining proper references to the actual model repositories.

Sources: [cache/user.config:4-7]()

## Storage Directory Structure

```mermaid
graph TD
    subgraph "Container Filesystem"
        ROOT["/project/"]
        ROOT --> CODE["code/<br/>Application scripts"]
        ROOT --> DATA["data/<br/>Training data & outputs"]
        ROOT --> MODELS["models/<br/>Model checkpoints"]
        ROOT --> CACHE["cache/<br/>User configurations"]
    end
    
    subgraph "Data Subdirectories"
        DATA --> SCRATCH["scratch/<br/>.gitkeep<br/>Temporary files"]
        DATA --> DATASET_INFO["dataset_info.json<br/>LFS-tracked datasets"]
    end
    
    subgraph "External Mounts"
        HF_VOLUME["/mnt/huggingface/<br/>HuggingFace cache volume"]
        HOME_DIR["/home/workbench/<br/>LLaMA-Factory installation"]
    end
    
    subgraph "Cache Management"
        USER_CONFIG["user.config<br/>cache_dir: null"]
        DEFAULT_CACHE["Default: /mnt/huggingface/"]
        CUSTOM_CACHE["Custom cache directory"]
    end
    
    CACHE --> USER_CONFIG
    USER_CONFIG --> DEFAULT_CACHE
    USER_CONFIG --> CUSTOM_CACHE
    DEFAULT_CACHE --> HF_VOLUME
    
    SCRATCH --> TEMP_FILES["Training outputs<br/>Intermediate results<br/>Temporary datasets"]
    
    style SCRATCH fill:#ffebee
    style HF_VOLUME fill:#e8f5e8
    style TEMP_FILES fill:#fff3e0
```

*Storage directory structure and cache management flow*

Sources: [data/scratch/.gitkeep:1](), [cache/user.config:8]()

## Cache Directory Configuration

The system supports flexible cache directory configuration through the `cache_dir` field in `user.config`. When set to `null` (default), the system uses the standard HuggingFace cache location at `/mnt/huggingface/`.

### Cache Directory Options

- **Default (`null`)**: Uses `/mnt/huggingface/` volume mount for optimal performance
- **Custom Path**: Absolute path to alternative cache location
- **Environment Override**: Can be overridden by `HF_HOME` or `TRANSFORMERS_CACHE` environment variables

### Cache Management Strategy

```mermaid
flowchart LR
    subgraph "Cache Resolution"
        USER_CONFIG_CHECK{"user.config<br/>cache_dir value"}
        NULL_VALUE["null<br/>(default)"]
        CUSTOM_VALUE["Custom path<br/>specified"]
    end
    
    subgraph "Cache Locations"
        DEFAULT_MOUNT["/mnt/huggingface/<br/>Volume mount"]
        CUSTOM_DIR["Custom directory<br/>User-specified"]
        ENV_OVERRIDE["Environment variable<br/>HF_HOME/TRANSFORMERS_CACHE"]
    end
    
    subgraph "Storage Behavior"
        SHARED_CACHE["Shared across containers<br/>Persistent storage"]
        LOCAL_CACHE["Local to container<br/>Temporary storage"]
    end
    
    USER_CONFIG_CHECK --> NULL_VALUE
    USER_CONFIG_CHECK --> CUSTOM_VALUE
    
    NULL_VALUE --> DEFAULT_MOUNT
    CUSTOM_VALUE --> CUSTOM_DIR
    ENV_OVERRIDE --> CUSTOM_DIR
    
    DEFAULT_MOUNT --> SHARED_CACHE
    CUSTOM_DIR --> LOCAL_CACHE
    
    style NULL_VALUE fill:#e8f5e8
    style CUSTOM_VALUE fill:#fff3e0
```

*Cache directory resolution and management flow*

Sources: [cache/user.config:8]()

## Temporary File Management

The `data/scratch/` directory serves as the primary location for temporary files, training outputs, and intermediate results. This directory is managed through Git ignore patterns to prevent temporary files from being committed to version control.

### Scratch Directory Properties

- **Purpose**: Temporary storage for training runs and intermediate files
- **Persistence**: Contents are preserved across container restarts but not tracked in Git
- **Location**: `/project/data/scratch/` within the container
- **Management**: Maintained with `.gitkeep` file to ensure directory exists in repository

The `.gitkeep` file ensures the scratch directory structure is maintained in the repository while allowing the contents to remain untracked.

Sources: [data/scratch/.gitkeep:1]()

## Configuration Best Practices

### Model Path Management
- Use descriptive names in `path_dict` for easy model identification
- Maintain consistency between model names across different configuration files
- Update `last_model` to reflect current working model for session persistence

### Cache Directory Selection
- Keep `cache_dir` as `null` for optimal performance with volume mounts
- Use custom cache directories only when specific storage requirements exist
- Monitor disk usage when using custom cache locations

### Storage Organization
- Utilize `data/scratch/` for all temporary files and training outputs
- Keep large model files in Git LFS-tracked `models/` directory
- Separate training data in `data/` directory with appropriate LFS tracking

Sources: [cache/user.config:1-9]()

---

