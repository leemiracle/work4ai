<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-modprobe · page 4 Common Utilities · fetched 2026-10-26 -->

# Common Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [common-utils/common-utils.c](common-utils/common-utils.c)
- [common-utils/common-utils.h](common-utils/common-utils.h)
- [common-utils/msg.c](common-utils/msg.c)

</details>



The Common Utilities subsystem provides foundational support functions used throughout the nvidia-modprobe system. This includes memory management, string manipulation, file operations, message handling, and version management utilities. These utilities form the base layer that enables safe and consistent operations across all components of the system.

For information about the main nvidia-modprobe implementation that uses these utilities, see [nvidia-modprobe System](#2). For details about the build system configuration, see [Build System](#3).

## Architecture Overview

The Common Utilities system is organized into several functional domains that provide essential services to the core nvidia-modprobe components:

```mermaid
graph TB
    subgraph "Memory Management"
        nvalloc["nvalloc()"]
        nvrealloc["nvrealloc()"]
        nvfree["nvfree()"]
        nvstrdup["nvstrdup()"]
        nvstrndup["nvstrndup()"]
    end
    
    subgraph "String Operations"
        nvstrcat["nvstrcat()"]
        nvvstrcat["nvvstrcat()"]
        nvasprintf["nvasprintf()"]
        nvstrtolower["nvstrtolower()"]
        nvstrtoupper["nvstrtoupper()"]
        nv_trim_space["nv_trim_space()"]
        nv_trim_char["nv_trim_char()"]
    end
    
    subgraph "File Operations"
        nv_open["nv_open()"]
        nv_get_file_length["nv_get_file_length()"]
        nv_mmap["nv_mmap()"]
        nv_basename["nv_basename()"]
        nv_dirname["nv_dirname()"]
        nv_mkdir_recursive["nv_mkdir_recursive()"]
        nv_string_to_file["nv_string_to_file()"]
    end
    
    subgraph "Message System"
        nv_error_msg["nv_error_msg()"]
        nv_warning_msg["nv_warning_msg()"]
        nv_info_msg["nv_info_msg()"]
        nv_msg["nv_msg()"]
        nv_format_text_rows["nv_format_text_rows()"]
        verbosity["NvVerbosity System"]
    end
    
    subgraph "Version Management"
        nv_encode_version["nv_encode_version()"]
        NV_VERSION2["NV_VERSION2()"]
        NV_VERSION3["NV_VERSION3()"]
        NV_VERSION4["NV_VERSION4()"]
    end
    
    subgraph "Core System Components"
        main_exec["nvidia-modprobe.c"]
        modprobe_utils["nvidia-modprobe-utils.c"]
        pci_sysfs["pci-sysfs.c"]
    end
    
    Memory_Management --> main_exec
    String_Operations --> main_exec
    File_Operations --> modprobe_utils
    Message_System --> main_exec
    Version_Management --> main_exec
    
    Memory_Management --> modprobe_utils
    String_Operations --> modprobe_utils
    Message_System --> modprobe_utils
    
    File_Operations --> pci_sysfs
    Message_System --> pci_sysfs
```

Sources: [common-utils/common-utils.h:1-143](), [common-utils/common-utils.c:1-839](), [common-utils/msg.c:1-429]()

## Utility Function Categories

The common utilities are organized into distinct functional categories, each serving specific operational needs:

```mermaid
graph LR
    subgraph "Safe Memory Operations"
        stdlib["Standard Library<br/>malloc, realloc, free"]
        nvalloc_impl["nvalloc()<br/>Error-checked malloc"]
        nvrealloc_impl["nvrealloc()<br/>Error-checked realloc"]
        nvfree_impl["nvfree()<br/>NULL-safe free"]
        
        stdlib --> nvalloc_impl
        stdlib --> nvrealloc_impl
        stdlib --> nvfree_impl
    end
    
    subgraph "String Manipulation"
        string_funcs["String Functions<br/>concat, dup, case conversion"]
        format_funcs["Format Functions<br/>sprintf, append_sprintf"]
        trim_funcs["Trim Functions<br/>whitespace, character removal"]
        
        nvalloc_impl --> string_funcs
        nvalloc_impl --> format_funcs
        nvalloc_impl --> trim_funcs
    end
    
    subgraph "File System Integration"
        posix_api["POSIX API<br/>open, stat, mmap"]
        file_helpers["File Helpers<br/>length, mmap, basename"]
        path_helpers["Path Helpers<br/>dirname, mkdir_recursive"]
        
        posix_api --> file_helpers
        posix_api --> path_helpers
        nvalloc_impl --> file_helpers
        nvalloc_impl --> path_helpers
    end
    
    subgraph "Message Formatting"
        terminal_api["Terminal API<br/>TIOCGWINSZ, isatty"]
        text_rows["TextRows<br/>Word wrapping system"]
        message_levels["Message Levels<br/>Error, Warning, Info"]
        
        terminal_api --> text_rows
        text_rows --> message_levels
        nvalloc_impl --> text_rows
    end
```

Sources: [common-utils/common-utils.c:52-291](), [common-utils/msg.c:62-427]()

## Core Data Structures

The common utilities define several key data structures that support system operations:

| Structure | Definition | Purpose |
|-----------|------------|---------|
| `NvVerbosity` | Enumeration in msg.c | Controls message output levels |
| `NVOptionalBool` | Enum with DEFAULT/FALSE/TRUE | Three-state boolean values |
| `TextRows` | Structure for text formatting | Word-wrapped text display |
| Version encoding | 64-bit integer format | Version comparison and storage |

### NvVerbosity Levels

```mermaid
graph TB
    NV_VERBOSITY_ERROR["NV_VERBOSITY_ERROR<br/>Error messages only"]
    NV_VERBOSITY_WARNING["NV_VERBOSITY_WARNING<br/>Warnings and errors"]
    NV_VERBOSITY_DEPRECATED["NV_VERBOSITY_DEPRECATED<br/>Deprecation messages"]
    NV_VERBOSITY_ALL["NV_VERBOSITY_ALL<br/>All messages including info"]
    NV_VERBOSITY_DEFAULT["NV_VERBOSITY_DEFAULT<br/>Default verbosity level"]
    
    NV_VERBOSITY_ERROR --> NV_VERBOSITY_WARNING
    NV_VERBOSITY_WARNING --> NV_VERBOSITY_DEPRECATED
    NV_VERBOSITY_DEPRECATED --> NV_VERBOSITY_ALL
    NV_VERBOSITY_DEFAULT --> NV_VERBOSITY_WARNING
```

Sources: [common-utils/msg.c:45-55](), [common-utils/common-utils.h:135-139]()

## Error Handling Strategy

The common utilities implement a consistent error handling strategy across all functions:

```mermaid
graph TD
    function_call["Function Call<br/>(nvalloc, nv_open, etc.)"]
    system_call["System Call<br/>(malloc, open, stat, etc.)"]
    check_result["Check Result"]
    success["Success Path<br/>Return result"]
    error_msg["Print Error Message<br/>with strerror(errno)"]
    exit_program["exit(1)<br/>Terminate program"]
    
    function_call --> system_call
    system_call --> check_result
    check_result --> success
    check_result --> error_msg
    error_msg --> exit_program
```

This approach ensures that memory allocation failures, file system errors, and other system-level problems are immediately detected and reported with clear error messages before terminating the program.

Sources: [common-utils/common-utils.c:52-63](), [common-utils/common-utils.c:455-465](), [common-utils/common-utils.c:476-488]()

## Integration with Main System

The common utilities are extensively used throughout the nvidia-modprobe system:

```mermaid
graph TB
    subgraph "nvidia-modprobe.c"
        main_memory["Memory allocation<br/>nvalloc, nvfree"]
        main_strings["String operations<br/>nvstrcat, nvasprintf"]
        main_messages["Message output<br/>nv_error_msg, nv_info_msg"]
    end
    
    subgraph "nvidia-modprobe-utils.c"
        utils_memory["Memory management<br/>nvalloc, nvstrdup"]
        utils_files["File operations<br/>nv_open, nv_string_to_file"]
        utils_paths["Path manipulation<br/>nv_basename, nv_dirname"]
    end
    
    subgraph "pci-sysfs.c"
        pci_files["File access<br/>nv_open, nv_get_file_length"]
        pci_strings["String processing<br/>nv_trim_space, nvstrcat"]
        pci_memory["Memory allocation<br/>nvalloc, nvfree"]
    end
    
    subgraph "Common Utilities"
        memory_mgmt["Memory Management"]
        string_ops["String Operations"]
        file_ops["File Operations"]
        msg_system["Message System"]
    end
    
    memory_mgmt --> main_memory
    string_ops --> main_strings
    msg_system --> main_messages
    
    memory_mgmt --> utils_memory
    file_ops --> utils_files
    string_ops --> utils_paths
    
    file_ops --> pci_files
    string_ops --> pci_strings
    memory_mgmt --> pci_memory
```

Sources: [common-utils/common-utils.h:54-82](), [common-utils/msg.c:126-222]()

## Subsystem Components

The Common Utilities system is detailed in the following subsections:

- **[Utility Functions](#4.1)**: Core memory management, string manipulation, and file system utilities
- **[Message System](#4.2)**: Formatted output, logging, and verbosity control system  
- **[Command Line Parsing](#4.3)**: Portable command-line argument processing utilities
- **[PCI Utilities](#4.4)**: Hardware discovery and PCI device management functions

Each subsection provides detailed documentation of the specific utility functions, their parameters, return values, and usage patterns within the broader nvidia-modprobe system.

Sources: [common-utils/common-utils.h:1-143](), [common-utils/common-utils.c:1-839](), [common-utils/msg.c:1-429]()

---

