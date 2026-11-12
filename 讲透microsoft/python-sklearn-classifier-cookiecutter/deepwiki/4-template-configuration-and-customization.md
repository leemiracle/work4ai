<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/python-sklearn-classifier-cookiecutter · page 4 Template Configuration and Customization · fetched 2026-10-26 -->

# Template Configuration and Customization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cookiecutter.json](cookiecutter.json)
- [hooks/post_gen_project.py](hooks/post_gen_project.py)

</details>



This document provides a comprehensive guide to configuring and customizing the cookiecutter template for different use cases. It covers the template's configuration system, available customization options, and how to modify the template behavior through configuration variables and post-generation hooks.

For detailed information about specific template variables, see [Template Variables and Options](#4.1). For information about the post-generation processing system, see [Post-Generation Processing](#4.2). For details about Visual Studio integration features, see [Visual Studio Integration](#3.2).

## Configuration Architecture Overview

The template configuration system operates through a layered architecture that processes user input, applies template variables, and executes conditional post-generation logic.

### Template Configuration Flow

```mermaid
graph TD
    subgraph "Configuration Input Layer"
        USER["User Input"]
        DEFAULTS["cookiecutter.json defaults"]
    end
    
    subgraph "Configuration Processing"
        COOKIECUTTER_ENGINE["Cookiecutter Engine"]
        JINJA_PROCESSING["Jinja2 Template Processing"]
        VARIABLE_SUBSTITUTION["Variable Substitution"]
    end
    
    subgraph "Template Variables"
        APP_NAME["app_name"]
        CREATE_VS_PROJECT["create_vs_project"]
        VISUAL_STUDIO_CONFIG["_visual_studio"]
        VS_POST_CMDS["_visual_studio_post_cmds"]
    end
    
    subgraph "Generated Output"
        CLASSIFIER_PY["classifier.py"]
        ENVIRONMENT_YML["environment.yml"] 
        PYPROJ_FILE["{{app_name}}.pyproj"]
        OTHER_FILES["README.md, LICENSE, etc."]
    end
    
    subgraph "Post-Generation Processing"
        POST_GEN_HOOK["post_gen_project.py"]
        DELETE_FILE_FUNC["delete_file()"]
        CONDITIONAL_DELETION["Conditional .pyproj deletion"]
    end
    
    USER --> COOKIECUTTER_ENGINE
    DEFAULTS --> COOKIECUTTER_ENGINE
    COOKIECUTTER_ENGINE --> JINJA_PROCESSING
    JINJA_PROCESSING --> VARIABLE_SUBSTITUTION
    
    VARIABLE_SUBSTITUTION --> APP_NAME
    VARIABLE_SUBSTITUTION --> CREATE_VS_PROJECT
    VARIABLE_SUBSTITUTION --> VISUAL_STUDIO_CONFIG
    VARIABLE_SUBSTITUTION --> VS_POST_CMDS
    
    APP_NAME --> CLASSIFIER_PY
    APP_NAME --> ENVIRONMENT_YML
    APP_NAME --> PYPROJ_FILE
    CREATE_VS_PROJECT --> PYPROJ_FILE
    
    PYPROJ_FILE --> POST_GEN_HOOK
    POST_GEN_HOOK --> DELETE_FILE_FUNC
    DELETE_FILE_FUNC --> CONDITIONAL_DELETION
```

Sources: [cookiecutter.json:1-19](), [hooks/post_gen_project.py:1-10]()

## Core Configuration Components

The template configuration consists of several key components that control project generation behavior:

| Component | Purpose | Configuration Location |
|-----------|---------|----------------------|
| `app_name` | Defines project name and file naming | [cookiecutter.json:2]() |
| `create_vs_project` | Controls Visual Studio project generation | [cookiecutter.json:3]() |
| `_visual_studio` | Visual Studio IDE integration settings | [cookiecutter.json:4-13]() |
| `_visual_studio_post_cmds` | Post-generation IDE commands | [cookiecutter.json:14-19]() |
| Post-generation hooks | Conditional file processing logic | [hooks/post_gen_project.py]() |

### Variable Processing System

```mermaid
graph LR
    subgraph "cookiecutter.json Structure"
        APP_NAME_VAR["app_name: 'classifier'"]
        CREATE_VS_VAR["create_vs_project: 'y'"]
        VS_CONFIG["_visual_studio configuration"]
        VS_COMMANDS["_visual_studio_post_cmds"]
    end
    
    subgraph "Template Processing Engine"
        JINJA_SUBSTITUTION["{{cookiecutter.app_name}}"]
        CONDITIONAL_LOGIC["{{cookiecutter.create_vs_project}}"]
        VS_INTEGRATION["Visual Studio integration"]
    end
    
    subgraph "Generated Files"
        PYPROJ_NAME["{{app_name}}.pyproj"]
        FILE_PATHS["File paths with app_name"]
        PROJECT_STRUCTURE["Project directory structure"]
    end
    
    subgraph "Post-Generation Hook Logic"
        CONDITION_CHECK["if create_vs_project != 'y'"]
        FILE_DELETION["delete_file('{{app_name}}.pyproj')"]
    end
    
    APP_NAME_VAR --> JINJA_SUBSTITUTION
    CREATE_VS_VAR --> CONDITIONAL_LOGIC
    VS_CONFIG --> VS_INTEGRATION
    
    JINJA_SUBSTITUTION --> PYPROJ_NAME
    JINJA_SUBSTITUTION --> FILE_PATHS
    CONDITIONAL_LOGIC --> PROJECT_STRUCTURE
    
    PYPROJ_NAME --> CONDITION_CHECK
    CONDITION_CHECK --> FILE_DELETION
```

Sources: [cookiecutter.json:2-3](), [hooks/post_gen_project.py:8-9]()

## Configuration Variable Types

The template supports several categories of configuration variables:

### User-Facing Variables
- **`app_name`**: Primary project identifier used throughout file naming and content generation
- **`create_vs_project`**: Boolean flag controlling Visual Studio project file generation

### Internal Configuration Variables
- **`_visual_studio`**: Contains metadata for Visual Studio integration including `value_source` mappings and visibility settings
- **`_visual_studio_post_cmds`**: Defines IDE commands executed after project generation

### Visual Studio Integration Configuration

The `_visual_studio` section provides sophisticated IDE integration through value source mapping:

```mermaid
graph TD
    subgraph "Visual Studio Configuration Structure"
        VS_CONFIG["_visual_studio"]
        APP_NAME_CONFIG["app_name configuration"]
        CREATE_VS_CONFIG["create_vs_project configuration"] 
    end
    
    subgraph "Value Source Mapping"
        PROJECT_NAME_SOURCE["value_source: 'ProjectName'"]
        IS_NEW_PROJECT_SOURCE["value_source: 'IsNewProject'"]
        VISIBILITY_HIDDEN["visible: false"]
    end
    
    subgraph "Post-Generation Commands"
        FILE_OPEN_PROJECT["File.OpenProject command"]
        PROJECT_PATH["{{cookiecutter._output_folder_path}}\\{{cookiecutter.app_name}}.pyproj"]
    end
    
    VS_CONFIG --> APP_NAME_CONFIG
    VS_CONFIG --> CREATE_VS_CONFIG
    
    APP_NAME_CONFIG --> PROJECT_NAME_SOURCE
    APP_NAME_CONFIG --> VISIBILITY_HIDDEN
    
    CREATE_VS_CONFIG --> IS_NEW_PROJECT_SOURCE
    CREATE_VS_CONFIG --> VISIBILITY_HIDDEN
    
    PROJECT_NAME_SOURCE --> FILE_OPEN_PROJECT
    FILE_OPEN_PROJECT --> PROJECT_PATH
```

Sources: [cookiecutter.json:4-18]()

## Post-Generation Hook System

The template implements conditional processing through the `post_gen_project.py` hook, which executes after file generation to apply configuration-based modifications:

### Hook Execution Flow

```mermaid
graph TD
    subgraph "Hook Entry Point"
        MAIN_EXECUTION["if __name__ == '__main__'"]
        CONDITION_EVALUATION["'{{cookiecutter.create_vs_project}}'.lower() != 'y'"]
    end
    
    subgraph "File System Operations"
        DELETE_FILE_CALL["delete_file('{{cookiecutter.app_name}}.pyproj')"]
        OS_REMOVE["os.remove()"]
        PATH_RESOLUTION["os.path.join(os.path.realpath(os.path.curdir), filepath)"]
    end
    
    subgraph "Conditional Logic"
        CREATE_VS_CHECK["Check create_vs_project value"]
        FILE_EXISTS["{{app_name}}.pyproj exists"]
        REMOVAL_ACTION["Remove .pyproj file"]
    end
    
    MAIN_EXECUTION --> CONDITION_EVALUATION
    CONDITION_EVALUATION --> CREATE_VS_CHECK
    CREATE_VS_CHECK --> FILE_EXISTS
    FILE_EXISTS --> DELETE_FILE_CALL
    DELETE_FILE_CALL --> PATH_RESOLUTION
    PATH_RESOLUTION --> OS_REMOVE
    OS_REMOVE --> REMOVAL_ACTION
```

Sources: [hooks/post_gen_project.py:7-9]()

The hook implements a simple but effective pattern for conditional file management based on user configuration choices.

## Customization Patterns

The template configuration supports several customization patterns:

### Project Naming Customization
The `app_name` variable drives consistent naming across all generated files and directories through Jinja2 template substitution.

### IDE Integration Control
The `create_vs_project` variable provides granular control over development environment setup, allowing users to opt out of Visual Studio integration while maintaining the core machine learning pipeline functionality.

### Extension Points
The configuration architecture supports extension through:
- Additional variables in `cookiecutter.json`
- Extended post-generation hook logic in `post_gen_project.py`
- Custom Visual Studio command configurations

Sources: [cookiecutter.json:1-19](), [hooks/post_gen_project.py:1-10]()

---

