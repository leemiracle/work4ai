<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/open-nvfwupd · page 7 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli_schema.yaml](cli_schema.yaml)
- [nvfwupd/config.yaml](nvfwupd/config.yaml)
- [nvfwupd_manpage.1](nvfwupd_manpage.1)

</details>



This page provides technical reference documentation for the open-nvfwupd tool, including CLI command specifications, configuration parameters, and implementation details. The reference material covers the complete interface specification for both command-line usage and YAML configuration files.

For detailed CLI command usage examples, see [CLI Reference](#7.1). For comprehensive configuration file documentation, see [Configuration Reference](#7.2). For general usage guidance, see [User Guide](#3).

## CLI Command Architecture

The nvfwupd tool implements a schema-driven CLI architecture where commands are defined declaratively and mapped to implementation classes. The following diagram shows the relationship between CLI schema definitions and their corresponding implementation classes:

### CLI Schema to Implementation Mapping

```mermaid
graph TD
    subgraph "CLI Schema Definition"
        schema["cli_schema.yaml"]
        global_opts["GlobalOptions"]
        commands["Commands"]
        target_opt["Target Option"]
        config_opt["Config Option"]
        verbose_opt["Verbosity Option"]
    end
    
    subgraph "Command Implementations"
        help_cmd["Help Class"]
        version_cmd["ToolVersion Class"]
        show_version_cmd["ShowVersion Class"]
        update_fw_cmd["UpdateFirmware Class"]
        force_update_cmd["ForceUpdate Class"]
        show_progress_cmd["ShowUpdateProgress Class"]
    end
    
    subgraph "Validation Functions"
        validate_target["validate_target"]
        validate_recipe["validate_recipe"]
    end
    
    schema --> global_opts
    schema --> commands
    global_opts --> target_opt
    global_opts --> config_opt
    global_opts --> verbose_opt
    
    commands --> help_cmd
    commands --> version_cmd
    commands --> show_version_cmd
    commands --> update_fw_cmd
    commands --> force_update_cmd
    commands --> show_progress_cmd
    
    target_opt --> validate_target
    show_version_cmd --> validate_recipe
    update_fw_cmd --> validate_recipe
    show_progress_cmd --> validate_recipe
```

Sources: [cli_schema.yaml:1-158]()

### Global Options Structure

The CLI defines three main global option groups that apply across all commands:

| Option | Short | Long | Description | Validator |
|--------|-------|------|-------------|-----------|
| Target | `-t` | `--target` | BMC target specification with IP, credentials, and server type | `validate_target` |
| Config | `-c` | `--config` | Path to YAML configuration file | None |
| Verbosity | `-v` | `--verbose` | Logging verbosity and log file path | None |

The target option accepts multiple key-value pairs including `ip`, `user`, `password`, `port`, and `servertype`. Valid server types are: `DGX`, `HGX`, `HGXB100`, `GB200`, `GB300`, `MGX-NVL`, and `GB200Switch`.

Sources: [cli_schema.yaml:16-47]()

### Command Implementation Classes

Each CLI command maps to a specific implementation class with defined options and validators:

```mermaid
graph LR
    subgraph "Core Commands"
        help["help → Help"]
        version["version → ToolVersion"]
        show_version["show_version → ShowVersion"]
        update_fw["update_fw → UpdateFirmware"]
        force_update["force_update → ForceUpdate"]
        show_progress["show_update_progress → ShowUpdateProgress"]
    end
    
    subgraph "Option Categories"
        package_opts["Package Options (-p)"]
        output_opts["Output Options (-j)"]
        behavior_opts["Behavior Options (-y, -b, -s)"]
        staging_opts["Staging Options (-u, -a)"]
        timeout_opts["Timeout Options (-t)"]
    end
    
    show_version --> package_opts
    show_version --> output_opts
    
    update_fw --> package_opts
    update_fw --> output_opts
    update_fw --> behavior_opts
    update_fw --> staging_opts
    update_fw --> timeout_opts
    
    force_update --> output_opts
    show_progress --> output_opts
```

Sources: [cli_schema.yaml:48-158]()

## Configuration File Architecture

The YAML configuration system provides an alternative to CLI arguments for complex deployment scenarios. The configuration structure supports both single-target and parallel multi-target operations:

### Configuration Schema Structure

```mermaid
graph TD
    subgraph "Configuration Root"
        config_yaml["config.yaml"]
        target_platform["TargetPlatform"]
        fw_update_files["FWUpdateFilePath"]
        bmc_config["BMC Connection Config"]
        update_method["FwUpdateMethod"]
    end
    
    subgraph "Update Methods"
        multipart_method["MultipartHttpPushUri"]
        http_method["HttpPushUri"]
        multipart_opts["MultipartOptions"]
    end
    
    subgraph "Target Configuration"
        single_target["Single Target Config"]
        parallel_targets["Parallel Targets Config"]
        bmc_ip["BMC_IP"]
        rf_username["RF_USERNAME"]
        rf_password["RF_PASSWORD"]
        tunnel_port["TUNNEL_TCP_PORT"]
    end
    
    subgraph "Advanced Options"
        update_targets["UpdateParametersTargets"]
        reset_params["BMCResetParameters"]
        parallel_update["ParallelUpdate"]
        sanitize_log["SANITIZE_LOG"]
    end
    
    config_yaml --> target_platform
    config_yaml --> fw_update_files
    config_yaml --> bmc_config
    config_yaml --> update_method
    
    update_method --> multipart_method
    update_method --> http_method
    multipart_method --> multipart_opts
    
    bmc_config --> single_target
    bmc_config --> parallel_targets
    single_target --> bmc_ip
    single_target --> rf_username
    single_target --> rf_password
    single_target --> tunnel_port
    
    config_yaml --> update_targets
    config_yaml --> reset_params
    config_yaml --> parallel_update
    config_yaml --> sanitize_log
```

Sources: [nvfwupd/config.yaml:1-69]()

### Configuration Parameters Reference

| Parameter | Type | Description | Valid Values |
|-----------|------|-------------|--------------|
| `TargetPlatform` | String | Target hardware platform | `DGX`, `HGX`, `HGXB100`, `GB200`, `GB300`, `MGX-NVL`, `GB200Switch` |
| `FWUpdateFilePath` | List | Firmware package file paths | File paths to `.fwpkg` files |
| `FwUpdateMethod` | String | Update method selection | `MultipartHttpPushUri`, `HttpPushUri` |
| `MultipartHttpPushUri` | String | Multipart update endpoint | Default: `/redfish/v1/UpdateService/update-multipart` |
| `HttpPushUri` | String | HTTP push update endpoint | Default: `/redfish/v1/UpdateService` |
| `TaskServiceUri` | String | Task monitoring endpoint | Default: `/redfish/v1/TaskService/Tasks/` |
| `ParallelUpdate` | Boolean | Enable parallel target updates | `true`, `false` |
| `SANITIZE_LOG` | Boolean | Enable credential sanitization | `true`, `false` |

Sources: [nvfwupd/config.yaml:1-69]()

## Man Page Documentation Structure

The tool provides comprehensive man page documentation following standard Unix conventions:

### Man Page Section Mapping

```mermaid
graph TD
    subgraph "Man Page Sections"
        name_section["NAME Section"]
        synopsis_section["SYNOPSIS Section"]
        description_section["DESCRIPTION Section"]
        global_options_section["GLOBAL OPTIONS Section"]
        commands_section["COMMANDS Section"]
        author_section["AUTHOR Section"]
    end
    
    subgraph "Global Options Detail"
        target_option["-t/--target"]
        config_option["-c/--config"]
        verbose_option["-v/--verbose"]
        target_subopts["Target Sub-options"]
    end
    
    subgraph "Command Details"
        show_version_detail["show_version Command"]
        update_fw_detail["update_fw Command"]
        force_update_detail["force_update Command"]
        show_progress_detail["show_update_progress Command"]
    end
    
    global_options_section --> target_option
    global_options_section --> config_option
    global_options_section --> verbose_option
    target_option --> target_subopts
    
    commands_section --> show_version_detail
    commands_section --> update_fw_detail
    commands_section --> force_update_detail
    commands_section --> show_progress_detail
```

Sources: [nvfwupd_manpage.1:1-107]()

### Command Option Categories

The man page organizes command options into logical categories for each command:

| Command | Required Options | Optional Options | Output Options |
|---------|------------------|------------------|----------------|
| `show_version` | None | `-p/--package`, `-s/--staged` | `-j/--json` |
| `update_fw` | `-p/--package` | `-y/--yes`, `-b/--background`, `-s/--special`, `-t/--timeout`, `-d/--details`, `-u/--staged_update`, `-a/--staged_activate_update` | `-j/--json` |
| `force_update` | `enable\|disable\|status` | None | `-j/--json` |
| `show_update_progress` | `-i/--id` | None | `-j/--json` |

Sources: [nvfwupd_manpage.1:38-101]()

## Validation and Schema Enforcement

The CLI system implements validation functions that ensure parameter correctness and consistency:

### Validation Function Architecture

```mermaid
graph TD
    subgraph "Validation Functions"
        validate_target_func["validate_target()"]
        validate_recipe_func["validate_recipe()"]
    end
    
    subgraph "Target Validation"
        ip_validation["IP Address Validation"]
        credentials_validation["Credentials Validation"]
        servertype_validation["Server Type Validation"]
        port_validation["Port Number Validation"]
    end
    
    subgraph "Recipe Validation"
        package_path_validation["Package Path Validation"]
        json_format_validation["JSON Format Validation"]
        option_combination_validation["Option Combination Validation"]
    end
    
    validate_target_func --> ip_validation
    validate_target_func --> credentials_validation
    validate_target_func --> servertype_validation
    validate_target_func --> port_validation
    
    validate_recipe_func --> package_path_validation
    validate_recipe_func --> json_format_validation
    validate_recipe_func --> option_combination_validation
```

Sources: [cli_schema.yaml:29-117]()

The validation system ensures that:
- Target specifications include required IP and credential information
- Server types match supported platform values
- Package files exist and are accessible
- JSON output options are compatible with other command flags
- Background operations properly bypass confirmation prompts

This reference architecture provides the foundation for both interactive CLI usage and automated deployment scenarios through configuration files.

---

