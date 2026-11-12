<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/open-nvfwupd · page 4 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nvfwupd/dut_access.py](nvfwupd/dut_access.py)
- [nvfwupd/rf_target.py](nvfwupd/rf_target.py)
- [nvfwupd/updcommand.py](nvfwupd/updcommand.py)

</details>



This document provides a technical overview of the open-nvfwupd system architecture, covering the core components, design patterns, and data flows that enable firmware updates across multiple NVIDIA hardware platforms. For platform-specific implementation details, see [Platform Abstraction Layer](#4.2). For detailed communication protocols, see [Communication Layer](#4.3).

## System Overview

The open-nvfwupd architecture follows a layered design that abstracts hardware platform differences behind a common interface while supporting multiple communication protocols (Redfish for BMCs, NVUE REST for switches). The system uses factory patterns and abstract base classes to enable extensible support for new hardware platforms.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "CLI Layer"
        A["nvfwupd.py"] --> B["FwUpdCmd"]
        B --> C["FwUpdCmdShowVersion"]
        B --> D["FwUpdCmdUpdateFirmware"] 
        B --> E["FwUpdCmdForceUpdate"]
        B --> F["FwUpdCmdShowUpdateProgress"]
    end
    
    subgraph "Platform Abstraction Layer"
        G["RFTarget"] --> H["BaseRFTarget"]
        G --> I["DGX_RFTarget"]
        G --> J["GB200RFTarget"]
        G --> K["HGXB100RFTarget"]
        G --> L["GB200SwitchTarget"]
        G --> M["ConfigTarget"]
    end
    
    subgraph "Communication Layer"
        N["DUTAccess"] --> O["BMCLoginAccess"]
        N --> P["BMCPortForwardAccess"]
        N --> Q["GB200NVSwitchAccess"]
    end
    
    subgraph "Target Hardware"
        R["BMC Redfish APIs"]
        S["GB200 NVUE REST APIs"]
        T["Hardware Components"]
    end
    
    C --> G
    D --> G
    E --> G
    F --> G
    
    H --> N
    I --> N
    J --> N
    K --> N
    L --> N
    M --> N
    
    O --> R
    P --> R
    Q --> S
    
    R --> T
    S --> T
```

**Sources:** [nvfwupd/updcommand.py:52-99](), [nvfwupd/rf_target.py:30-109](), [nvfwupd/dut_access.py:39-67]()

## Core Components

The system consists of three primary layers that work together to provide platform-agnostic firmware update capabilities:

### Command Processing Layer

The `FwUpdCmd` base class in [nvfwupd/updcommand.py:52-99]() provides the foundation for all CLI operations. Each command inherits from this base and implements specific functionality:

| Command Class | Purpose | Key Methods |
|---------------|---------|-------------|
| `FwUpdCmdShowVersion` | Display firmware inventory | `get_output_json()`, `print_output_json()` |
| `FwUpdCmdUpdateFirmware` | Execute firmware updates | `update_target()`, `update_fw_parallel()` |
| `FwUpdCmdForceUpdate` | Enable/disable force update mode | `run_command()` |
| `FwUpdCmdShowUpdateProgress` | Monitor update task status | `run_command()` |

The command layer handles argument validation, target list processing, and orchestrates calls to the platform abstraction layer.

**Sources:** [nvfwupd/updcommand.py:861-896](), [nvfwupd/updcommand.py:1454-1492](), [nvfwupd/updcommand.py:1280-1307](), [nvfwupd/updcommand.py:1982-2009]()

### Platform Resolution and Factory Pattern

```mermaid
graph LR
    A["validate_target_json()"] --> B["DUTAccess.get_dut_access()"]
    B --> C{"Platform Detection"}
    C --> D["SERVER_TYPE_CLASS_DICT"]
    C --> E["TARGET_CLASS_DICT"]
    D --> F["Platform-Specific RFTarget"]
    E --> F
    F --> G["init_platform()"]
    G --> H["Instantiated Target Class"]
    
    I["ConfigTarget"] --> J["config_dict"]
    J --> K["TargetPlatform"]
    K --> F
```

The system uses two key dictionaries for platform resolution:

- `SERVER_TYPE_CLASS_DICT` in [nvfwupd/rf_target.py:99-107]() - Maps server types to target classes
- `TARGET_CLASS_DICT` in [nvfwupd/rf_target.py:109-114]() - Maps detected platform names to target classes

**Sources:** [nvfwupd/rf_target.py:99-116](), [nvfwupd/updcommand.py:531-547](), [nvfwupd/updcommand.py:607-698]()

## Platform Abstraction Layer

### RFTarget Hierarchy

The `RFTarget` abstract base class defines the contract for all platform implementations:

```mermaid
classDiagram
    class RFTarget {
        <<abstract>>
        +target_access: DUTAccess
        +fungible_components: list
        +update_completion_msg: str
        +update_component()* 
        +is_fungible_component()*
        +get_component_version()*
        +start_update_monitor()
        +process_job_status()
    }
    
    class BaseRFTarget {
        +update_component()
        +get_component_version()
        +is_fungible_component()
    }
    
    class DGX_RFTarget {
        +update_component()
        +fungible_components: ["bmc", "cpld"]
    }
    
    class GB200RFTarget {
        +update_component()
        +get_compute_tray_count()
        +update_compute_tray_fw()
    }
    
    class ConfigTarget {
        +config_dict: dict
        +determine_target_type()
        +delegate_to_concrete_target()
    }
    
    RFTarget <|-- BaseRFTarget
    RFTarget <|-- DGX_RFTarget  
    RFTarget <|-- GB200RFTarget
    RFTarget <|-- ConfigTarget
```

Each platform implementation handles:
- Component version extraction from firmware inventory
- Platform-specific update procedures (HTTP Push URI vs Multipart uploads)
- Fungible component identification (components that can be different SKUs)

**Sources:** [nvfwupd/rf_target.py:30-97](), [nvfwupd/rf_target.py:183-194]()

### Update Method Abstraction

The system supports two primary update methods through abstract methods:

```mermaid
sequenceDiagram
    participant C as "Command Layer"
    participant R as "RFTarget"
    participant D as "DUTAccess"
    participant H as "Hardware"
    
    C->>R: update_component()
    R->>R: determine_update_method()
    
    alt HTTP Push URI
        R->>R: update_component_pushuri()
        R->>D: dispatch_request("PATCH")
        R->>D: dispatch_file_upload()
    else Multipart Upload
        R->>R: update_component_multipart()
        R->>D: multipart_file_upload()
    end
    
    D->>H: POST /redfish/v1/UpdateService
    H-->>D: Task ID Response
    D-->>R: task_id
    R->>R: start_update_monitor()
    
    loop Monitor Progress
        R->>D: dispatch_request(task_service_uri)
        D->>H: GET /redfish/v1/TaskService/Tasks/{id}
        H-->>D: Task Status
        D-->>R: task_dict
        R->>R: check_for_failure()
    end
```

**Sources:** [nvfwupd/rf_target.py:528-692](), [nvfwupd/rf_target.py:694-1076]()

## Communication Layer

### DUTAccess Factory Pattern

The `DUTAccess.get_dut_access()` method implements a factory pattern to instantiate the appropriate communication class:

```mermaid
graph TD
    A["get_dut_access()"] --> B{"servertype Parameter"}
    B -->|"gb200switch"| C["GB200NVSwitchAccess"]
    B -->|"Other/None"| D["Try Access Classes"]
    
    D --> E["BMCPortForwardAccess"]
    D --> F["BMCLoginAccess"]
    
    E --> G{"is_valid() && is_reachable()"}
    F --> H{"is_valid() && is_reachable()"}
    
    G -->|"Success"| I["Return BMCPortForwardAccess"]
    G -->|"Fail"| F
    H -->|"Success"| J["Return BMCLoginAccess"]
    H -->|"Fail"| K["Return None"]
    
    C --> L["NVUE REST API"]
    I --> M["Redfish over Port Forward"]
    J --> N["Direct Redfish Access"]
```

**Sources:** [nvfwupd/dut_access.py:72-181]()

### Protocol Implementations

| Access Class | Protocol | Target Hardware | Key Methods |
|--------------|----------|-----------------|-------------|
| `BMCLoginAccess` | Redfish HTTPS | BMC endpoints | `dispatch_request()`, `get_firmware_inventory()` |
| `BMCPortForwardAccess` | Redfish via SSH tunnel | Port-forwarded BMCs | `update_transport_type()` |
| `GB200NVSwitchAccess` | NVUE REST API | GB200 switches | `dispatch_rest_request_get()`, `get_job_status()` |

### Request Processing Pipeline

```mermaid
graph LR
    A["dispatch_request()"] --> B{"Method Type"}
    B -->|"GET"| C["requests.get()"]
    B -->|"POST"| D["File Upload Logic"]
    B -->|"PATCH"| E["Configuration Update"]
    
    D --> F{"multipart_file_upload()"}
    F --> G["Firmware Package"]
    F --> H["Update Parameters"]
    G --> I["POST Request"]
    H --> I
    
    C --> J["JSON Response"]
    E --> J
    I --> J
    
    J --> K["Response Validation"]
    K --> L["Task ID Extraction"]
    L --> M["Task Monitoring"]
```

**Sources:** [nvfwupd/dut_access.py:857-1091](), [nvfwupd/dut_access.py:1180-1291]()

## Data Flow Architecture

### Firmware Update Flow

```mermaid
sequenceDiagram
    participant CLI as "nvfwupd CLI"
    participant CMD as "FwUpdCmdUpdateFirmware" 
    participant TGT as "Platform RFTarget"
    participant DUT as "DUTAccess"
    participant PKG as "PLDM Package Parser"
    participant HW as "Target Hardware"
    
    CLI->>CMD: run_command()
    CMD->>CMD: validate_cmd()
    CMD->>CMD: validate_target_json()
    CMD->>CMD: validate_recipes()
    
    CMD->>PKG: get_pkg_parser()
    PKG->>PKG: parse_pkg()
    
    CMD->>DUT: get_dut_access()
    DUT->>HW: Test connectivity
    HW-->>DUT: Connection established
    
    CMD->>TGT: init_platform()
    TGT->>TGT: Determine platform type
    
    CMD->>TGT: start_update_monitor()
    TGT->>TGT: update_component()
    TGT->>DUT: Upload firmware
    DUT->>HW: POST /redfish/v1/UpdateService
    HW-->>DUT: Task ID
    
    loop Monitor Update
        TGT->>DUT: GET task_service_uri
        DUT->>HW: GET /redfish/v1/TaskService/Tasks/{id}
        HW-->>DUT: Task status
        DUT-->>TGT: task_dict
        TGT->>TGT: Print progress
    end
    
    TGT-->>CMD: Update completion
    CMD-->>CLI: Exit with status
```

**Sources:** [nvfwupd/updcommand.py:1717-1979](), [nvfwupd/rf_target.py:694-1076]()

### Configuration-Based Target Resolution

For systems using configuration files, the `ConfigTarget` class provides an additional abstraction layer:

```mermaid
graph TB
    A["config.yaml"] --> B["ConfigParser"]
    B --> C["ConfigTarget"]
    C --> D{"TargetPlatform Value"}
    
    D -->|"dgx"| E["DGX_RFTarget"]
    D -->|"gb200"| F["GB200RFTarget"]
    D -->|"hgxb100"| G["HGXB100RFTarget"]
    D -->|"gb200switch"| H["GB200SwitchTarget"]
    
    E --> I["BMC Communication"]
    F --> I
    G --> I
    H --> J["NVUE REST Communication"]
    
    C --> K["config_dict"]
    K --> L["ParallelUpdate"]
    K --> M["FWUpdateFilePath"]
    K --> N["TargetPlatform"]
```

The `ConfigTarget` acts as a proxy that delegates to the appropriate concrete target implementation based on configuration parameters.

**Sources:** [nvfwupd/updcommand.py:642-680](), [nvfwupd/rf_target.py:116]()

This architecture enables the system to support diverse NVIDIA hardware platforms through a unified interface while maintaining extensibility for future platform additions.

---

