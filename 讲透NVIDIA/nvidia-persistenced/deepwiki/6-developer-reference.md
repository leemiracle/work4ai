<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-persistenced · page 6 Developer Reference · fetched 2026-10-26 -->

# Developer Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [common-utils/gen-manpage-opts-helper.h](common-utils/gen-manpage-opts-helper.h)
- [common-utils/msg.c](common-utils/msg.c)
- [common-utils/msg.h](common-utils/msg.h)
- [nvstatuscodes.h](nvstatuscodes.h)

</details>



This page provides technical reference information for developers working with or extending the nvidia-persistenced codebase. It covers essential development tools, APIs, patterns, and systems that form the foundation for daemon functionality.

For system administration and deployment information, see [System Integration](#5). For build system details, see [Build System](#3).

## Overview

The nvidia-persistenced codebase provides several developer-focused systems that ensure consistent error handling, logging, and status reporting across all components. These systems are designed to be reusable and provide a uniform interface for both internal daemon operations and external client communication.

The core developer infrastructure includes:

- **Status Code System**: Comprehensive error and status reporting using NVIDIA status codes
- **Message and Logging Framework**: Structured logging with verbosity controls and formatted output
- **Common Utilities**: Shared functionality for memory management, string operations, and cross-platform compatibility

## Status Code Architecture

### NVIDIA Status Code System

The daemon uses a comprehensive status code system defined in [nvstatuscodes.h]() that provides standardized error reporting across all NVIDIA software components.

```mermaid
graph TD
    subgraph "Status Code Categories"
        SUCCESS["NV_OK<br/>0x00000000"]
        ERRORS["Error Codes<br/>NV_ERR_*<br/>0x00000001-0x00000089"]
        WARNINGS["Warning Codes<br/>NV_WARN_*<br/>0x00010001-0x00010009"]
        GENERIC["Generic Error<br/>NV_ERR_GENERIC<br/>0x0000FFFF"]
    end
    
    subgraph "Error Categories"
        DEVICE_ERRORS["Device Errors<br/>NV_ERR_CARD_NOT_PRESENT<br/>NV_ERR_GPU_IS_LOST<br/>NV_ERR_INVALID_DEVICE"]
        MEMORY_ERRORS["Memory Errors<br/>NV_ERR_NO_MEMORY<br/>NV_ERR_MEMORY_ERROR<br/>NV_ERR_GPU_MEMORY_ONLINING_FAILURE"]
        PERMISSION_ERRORS["Permission Errors<br/>NV_ERR_INSUFFICIENT_PERMISSIONS<br/>NV_ERR_PRIV_SEC_VIOLATION"]
        OPERATION_ERRORS["Operation Errors<br/>NV_ERR_NOT_SUPPORTED<br/>NV_ERR_TIMEOUT<br/>NV_ERR_BUSY_RETRY"]
    end
    
    subgraph "Usage Context"
        RPC_RESPONSES["RPC Command Responses"]
        DEVICE_OPS["Device Operations"]
        NUMA_OPS["NUMA Operations"]
        CONFIG_OPS["Configuration Operations"]
    end
    
    ERRORS --> DEVICE_ERRORS
    ERRORS --> MEMORY_ERRORS
    ERRORS --> PERMISSION_ERRORS
    ERRORS --> OPERATION_ERRORS
    
    SUCCESS --> RPC_RESPONSES
    DEVICE_ERRORS --> DEVICE_OPS
    MEMORY_ERRORS --> NUMA_OPS
    OPERATION_ERRORS --> CONFIG_OPS
    WARNINGS --> RPC_RESPONSES
```

### Status Code Structure

Status codes follow a hierarchical pattern with specific ranges for different categories:

| Range | Category | Usage |
|-------|----------|-------|
| `0x00000000` | Success | Operation completed successfully |
| `0x00000001-0x00000089` | Errors | Specific error conditions |
| `0x0000FFFF` | Generic Error | Fallback for unspecified failures |
| `0x00010001-0x00010009` | Warnings | Non-fatal conditions |

**Sources:** [nvstatuscodes.h:27-178]()

## Message and Logging System

### Verbosity Control Architecture

The logging system implements a hierarchical verbosity model that controls message output based on severity and importance.

```mermaid
graph TB
    subgraph "Verbosity Levels"
        V_NONE["NV_VERBOSITY_NONE<br/>No output"]
        V_ERROR["NV_VERBOSITY_ERROR<br/>Errors only"]
        V_DEPRECATED["NV_VERBOSITY_DEPRECATED<br/>+ Deprecation messages"]
        V_WARNING["NV_VERBOSITY_WARNING<br/>+ Warnings"]
        V_ALL["NV_VERBOSITY_ALL<br/>+ Info messages"]
    end
    
    subgraph "Message Functions"
        ERROR_MSG["nv_error_msg()"]
        DEPRECATED_MSG["nv_deprecated_msg()"]
        WARNING_MSG["nv_warning_msg()"]
        INFO_MSG["nv_info_msg()"]
        MSG["nv_msg()"]
    end
    
    subgraph "Output Formatting"
        TERMINAL_WIDTH["Terminal Width Detection"]
        TEXT_FORMATTER["Text Row Formatter"]
        PREFIX_SYSTEM["Prefix System"]
        WHITESPACE_HANDLING["Whitespace Processing"]
    end
    
    V_NONE --> V_ERROR
    V_ERROR --> V_DEPRECATED
    V_DEPRECATED --> V_WARNING
    V_WARNING --> V_ALL
    
    V_ERROR --> ERROR_MSG
    V_DEPRECATED --> DEPRECATED_MSG
    V_WARNING --> WARNING_MSG
    V_ALL --> INFO_MSG
    MSG --> TEXT_FORMATTER
    
    ERROR_MSG --> TEXT_FORMATTER
    DEPRECATED_MSG --> TEXT_FORMATTER
    WARNING_MSG --> TEXT_FORMATTER
    INFO_MSG --> TEXT_FORMATTER
    
    TEXT_FORMATTER --> TERMINAL_WIDTH
    TEXT_FORMATTER --> PREFIX_SYSTEM
    TEXT_FORMATTER --> WHITESPACE_HANDLING
```

### Message System API

The message system provides different functions for various message types, each with appropriate formatting and verbosity checks:

| Function | Purpose | Verbosity Level |
|----------|---------|-----------------|
| `nv_error_msg()` | Error messages with ERROR prefix | `NV_VERBOSITY_ERROR` |
| `nv_deprecated_msg()` | Deprecation warnings | `NV_VERBOSITY_DEPRECATED` |
| `nv_warning_msg()` | Warning messages | `NV_VERBOSITY_WARNING` |
| `nv_info_msg()` | Informational messages | `NV_VERBOSITY_ALL` |
| `nv_msg()` | General messages (always shown) | Always displayed |

**Sources:** [common-utils/msg.h:94-124](), [common-utils/msg.c:126-222]()

### Text Formatting System

The system includes sophisticated text formatting capabilities for terminal output:

```mermaid
graph LR
    subgraph "Input Processing"
        RAW_TEXT["Raw Text Input"]
        FORMAT_PARAMS["Format Parameters<br/>width, prefix, word_boundary"]
    end
    
    subgraph "TextRows Processing"
        TEXT_PARSER["nv_format_text_rows()"]
        LINE_BREAKING["Line Breaking Algorithm"]
        PREFIX_HANDLING["Prefix Alignment"]
        WORD_BOUNDARY["Word Boundary Detection"]
    end
    
    subgraph "Output Generation"
        TEXT_ROWS["TextRows Structure<br/>t: char**<br/>n: row count<br/>m: max length"]
        TERMINAL_OUTPUT["Terminal Output"]
        NON_TERMINAL["Non-terminal Output"]
    end
    
    subgraph "Memory Management"
        ALLOCATION["Dynamic Allocation"]
        CLEANUP["nv_free_text_rows()"]
    end
    
    RAW_TEXT --> TEXT_PARSER
    FORMAT_PARAMS --> TEXT_PARSER
    TEXT_PARSER --> LINE_BREAKING
    LINE_BREAKING --> PREFIX_HANDLING
    PREFIX_HANDLING --> WORD_BOUNDARY
    WORD_BOUNDARY --> TEXT_ROWS
    
    TEXT_ROWS --> TERMINAL_OUTPUT
    TEXT_ROWS --> NON_TERMINAL
    
    TEXT_ROWS --> CLEANUP
    ALLOCATION --> TEXT_ROWS
```

**Sources:** [common-utils/msg.c:252-427](), [common-utils/msg.h:130-140]()

## Development Patterns

### Error Handling Pattern

The codebase follows consistent patterns for error handling and status reporting:

```c
// Standard pattern used throughout the codebase
NvStatus function_name(parameters) {
    NvStatus status = NV_OK;
    
    // Validate parameters
    if (!parameter) {
        return NV_ERR_INVALID_PARAMETER;
    }
    
    // Perform operation
    status = operation();
    if (status != NV_OK) {
        nv_error_msg("Operation failed: %s", nvStatusToString(status));
        return status;
    }
    
    return NV_OK;
}
```

### Logging Integration Pattern

Components integrate with the logging system using consistent verbosity and formatting:

```c
// Typical logging pattern
void daemon_operation(void) {
    nv_info_msg("DAEMON: ", "Starting operation...");
    
    NvStatus status = perform_operation();
    if (status != NV_OK) {
        nv_error_msg("Operation failed with status 0x%x", status);
        return;
    }
    
    nv_info_msg("DAEMON: ", "Operation completed successfully");
}
```

### Memory Management Integration

The message system integrates with the common utilities memory management:

```mermaid
graph TD
    subgraph "Memory Allocation"
        NVALLOC["nvalloc()"]
        NVFREE["nvfree()"]
        NV_VSNPRINTF["NV_VSNPRINTF macro"]
    end
    
    subgraph "Message Buffer Management"
        DYNAMIC_SIZING["Dynamic Buffer Sizing"]
        VSNPRINTF_HANDLING["vsnprintf() Return Value Handling"]
        BUFFER_REALLOCATION["Buffer Reallocation"]
    end
    
    subgraph "TextRows Management"
        TEXTROWS_ALLOC["TextRows Allocation"]
        STRING_DUPLICATION["String Duplication"]
        CLEANUP_REQUIRED["Mandatory Cleanup"]
    end
    
    NVALLOC --> DYNAMIC_SIZING
    NV_VSNPRINTF --> VSNPRINTF_HANDLING
    VSNPRINTF_HANDLING --> BUFFER_REALLOCATION
    DYNAMIC_SIZING --> TEXTROWS_ALLOC
    STRING_DUPLICATION --> CLEANUP_REQUIRED
    NVFREE --> CLEANUP_REQUIRED
```

**Sources:** [common-utils/msg.h:60-86](), [common-utils/msg.c:369-427]()

## Integration with Daemon Components

The developer infrastructure integrates throughout the daemon architecture:

```mermaid
graph TB
    subgraph "Core Daemon"
        MAIN_DAEMON["nvidia-persistenced.c"]
        RPC_SERVER["command_server.c"]
        OPTIONS_PARSER["options.c"]
    end
    
    subgraph "Device Management"
        DEVICE_CONFIG["Device Configuration"]
        NUMA_MANAGER["NUMA Manager"]
    end
    
    subgraph "Developer Infrastructure"
        STATUS_CODES["Status Code System<br/>nvstatuscodes.h"]
        MESSAGE_SYSTEM["Message System<br/>msg.c/msg.h"]
        COMMON_UTILS["Common Utilities"]
    end
    
    subgraph "External Interfaces"
        SYSLOG_OUTPUT["Syslog Output"]
        STDERR_OUTPUT["stderr Output"]
        CLIENT_RESPONSES["Client RPC Responses"]
    end
    
    MAIN_DAEMON --> STATUS_CODES
    RPC_SERVER --> STATUS_CODES
    DEVICE_CONFIG --> STATUS_CODES
    NUMA_MANAGER --> STATUS_CODES
    
    MAIN_DAEMON --> MESSAGE_SYSTEM
    RPC_SERVER --> MESSAGE_SYSTEM
    OPTIONS_PARSER --> MESSAGE_SYSTEM
    
    MESSAGE_SYSTEM --> SYSLOG_OUTPUT
    MESSAGE_SYSTEM --> STDERR_OUTPUT
    STATUS_CODES --> CLIENT_RESPONSES
    
    COMMON_UTILS --> MESSAGE_SYSTEM
    COMMON_UTILS --> STATUS_CODES
```

**Sources:** [nvstatuscodes.h:1-179](), [common-utils/msg.c:1-429](), [common-utils/msg.h:1-143]()

For detailed information about specific status codes and error handling patterns, see [Status Codes and Error Handling](#6.1). For comprehensive logging system documentation, see [Logging and Message System](#6.2).

---

