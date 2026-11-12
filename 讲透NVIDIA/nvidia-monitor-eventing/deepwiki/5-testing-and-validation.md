<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-monitor-eventing · page 5 Testing and Validation · fetched 2026-10-26 -->

# Testing and Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/selftest.hpp](include/selftest.hpp)
- [src/selftest.cpp](src/selftest.cpp)
- [test/selftest_test.cpp](test/selftest_test.cpp)
- [tools/event_validation.py](tools/event_validation.py)
- [tools/jtag/meson.build](tools/jtag/meson.build)
- [tools/meson.build](tools/meson.build)
- [tools/modules/com.py](tools/modules/com.py)
- [tools/modules/event_accessor_script.py](tools/modules/event_accessor_script.py)
- [tools/modules/event_logging_script.py](tools/modules/event_logging_script.py)
- [tools/modules/injector_script_base.py](tools/modules/injector_script_base.py)
- [tools/modules/templates/event_accessor_script.bash](tools/modules/templates/event_accessor_script.bash)
- [tools/selftest_tool.cpp](tools/selftest_tool.cpp)

</details>



This document covers the comprehensive testing and validation ecosystem for the nvidia-monitor-eventing system. The testing framework ensures hardware monitoring events are properly detected, processed, and logged through multiple validation layers including end-to-end event injection, hardware self-tests, and interface validation tools.

For information about the core event detection system being tested, see [Event Detection System](#2.1). For configuration of events being validated, see [Event Definitions](#3.1).

## Overview

The testing ecosystem provides multiple validation approaches:

- **End-to-end Event Validation**: Complete event injection and verification workflow
- **Hardware Self-Testing**: Component-level validation and root cause analysis  
- **Interface Validation**: Hardware interface wrapper tools and JTAG testing
- **Configuration Validation**: Event definition and device association testing

The system supports both automated testing scenarios and manual diagnostic workflows, with comprehensive reporting and markdown documentation generation capabilities.

```mermaid
graph TB
    subgraph "Primary Testing Framework"
        EV["event_validation.py<br/>★78.56<br/>End-to-End Validation"]
        ELI["EventLogsInjectorScript<br/>Direct Event Logging"]
        EAI["EventAccessorInjectorScript<br/>Property-Based Injection"]
    end
    
    subgraph "Self-Test System"
        ST["Selftest Class<br/>Hardware Validation"]
        STT["selftest_tool<br/>Standalone Testing"]
        RCT["RootCauseTracer<br/>Failure Analysis"]
    end
    
    subgraph "Hardware Interface Tools"
        MCTP["mctp-error-detection"]
        FPGA["fpga_regtbl_wrapper"]
        PCIE["pcie_wrapper"]
        JTAG["jtag_test"]
    end
    
    subgraph "Target System"
        ED["EventDetection<br/>D-Bus Processing"]
        DA["DataAccessor<br/>Multi-Interface Access"]
        DAEMON["monitor-eventingd<br/>Main Service"]
    end
    
    EV --> ELI
    EV --> EAI
    ELI --> ED
    EAI --> DA
    ST --> RCT
    STT --> ST
    MCTP --> DA
    FPGA --> DA
    PCIE --> DA
    JTAG --> DAEMON
```

Sources: [tools/event_validation.py:1-866](), [src/selftest.cpp:1-673](), [tools/selftest_tool.cpp:1-279]()

## Event Validation Framework

The primary validation tool is `event_validation.py`, which provides comprehensive end-to-end testing of the event monitoring system. This framework injects events through multiple pathways and validates proper logging through the OpenBMC Redfish interface.

### Core Validation Architecture

```mermaid
graph LR
    subgraph "Test Controller"
        EV["event_validation.py<br/>InjectTest Class"]
        CONFIG["Configuration<br/>JSON + DAT Files"]
    end
    
    subgraph "Injection Methods"
        MODE1["Mode 1: Direct Logging<br/>EventLogsInjectorScript"]
        MODE2["Mode 2: Property Changes<br/>EventAccessorInjectorScript"]
    end
    
    subgraph "Target Environment"
        QEMU["QEMU SSH Connection<br/>BMC Environment"]
        BMCWEB["BMCWeb HTTP API<br/>Redfish Interface"]
    end
    
    subgraph "Validation Chain"
        INJECT["Event Injection<br/>Bash Script Generation"]
        MONITOR["Log Monitoring<br/>D-Bus + Redfish"]
        VERIFY["Response Validation<br/>Field Comparison"]
    end
    
    EV --> MODE1
    EV --> MODE2
    CONFIG --> MODE1
    CONFIG --> MODE2
    MODE1 --> INJECT
    MODE2 --> INJECT
    INJECT --> QEMU
    QEMU --> BMCWEB
    BMCWEB --> MONITOR
    MONITOR --> VERIFY
```

The framework operates in two primary modes controlled by the `--mode` parameter:

**Mode 1 (Direct Event Logging)**: Uses `EventLogsInjectorScript` to generate `busctl` commands that directly insert log entries into the phosphor-logging D-Bus service.

**Mode 2 (Property-Based Injection)**: Uses `EventAccessorInjectorScript` to modify D-Bus properties and trigger the monitor-eventing daemon's normal event detection flow.

Sources: [tools/event_validation.py:71-73](), [tools/event_validation.py:318-866]()

### Test Execution Flow

The `InjectTest` class coordinates the complete validation workflow:

1. **Environment Setup**: Establishes SSH connection to QEMU environment and HTTP connection to BMCWeb
2. **Baseline Capture**: Records initial log count before injection
3. **Script Generation**: Creates bash injection scripts from JSON configuration
4. **Event Injection**: Executes generated scripts on target system
5. **Validation**: Compares injected events against Redfish log entries
6. **Reporting**: Generates summary with injection success/failure metrics

```mermaid
sequenceDiagram
    participant EV as event_validation.py
    participant SSH as QEMU SSH
    participant SCRIPT as Generated Script
    participant DBUS as D-Bus Services
    participant BMCWEB as BMCWeb API
    
    EV->>SSH: establish connection
    EV->>BMCWEB: get initial log count
    EV->>SCRIPT: generate injection script
    EV->>SSH: upload and execute script
    SCRIPT->>DBUS: inject events/modify properties
    DBUS->>DBUS: process events
    EV->>BMCWEB: fetch new log entries
    EV->>EV: validate field matches
    EV->>EV: generate summary report
```

Key validation methods include field comparison for mandatory keys (`Severity`, `Resolution`, `MessageId`) and optional keys (`MessageArgs`), with special handling for D-Bus to Redfish severity mapping.

Sources: [tools/event_validation.py:346-815](), [tools/event_validation.py:817-866]()

## Self-Test System

The self-test system provides hardware component validation and root cause analysis capabilities through the `Selftest` class and associated tooling.

### Selftest Architecture

```mermaid
graph TB
    subgraph "Selftest Core"
        ST["Selftest Class<br/>Hardware Validation Engine"]
        TP["TestPointResult<br/>Individual Test Results"]
        DR["DeviceResult<br/>Aggregated Device Results"]
        RR["ReportResult<br/>Complete Test Report"]
    end
    
    subgraph "Test Execution"
        PERFORM["perform()<br/>Single Device Test"]
        TREE["performEntireTree()<br/>Full DAT Test"]
        EVAL["evaluateDevice()<br/>Result Analysis"]
    end
    
    subgraph "Data Sources"
        DAT["Device Association Tree<br/>Test Point Configuration"]
        ACC["DataAccessor<br/>Hardware Interface"]
        LAYERS["Test Layers<br/>power_rail, pin_status, etc."]
    end
    
    subgraph "Output Generation"
        REP["Report Class<br/>JSON Report Generation"]
        HEALTH["Device Health Updates<br/>D-Bus Properties"]
        LOGS["Log Resolution<br/>Phosphor Logging"]
    end
    
    ST --> TP
    TP --> DR
    DR --> RR
    ST --> PERFORM
    ST --> TREE
    PERFORM --> EVAL
    DAT --> ST
    ACC --> PERFORM
    LAYERS --> PERFORM
    RR --> REP
    ST --> HEALTH
    ST --> LOGS
```

The self-test system validates hardware components across multiple test layers including `power_rail`, `erot_control`, `pin_status`, `interface_status`, `firmware_status`, `protocol_status`, and `data_dump`.

Sources: [src/selftest.cpp:160-378](), [include/selftest.hpp:36-326]()

### Test Point Validation

Individual test points are validated through the `TestPointResult` structure, which captures:

- **Target Name**: Test point identifier (e.g., "PGOOD", "DEVICE_HSC0")
- **Expected Value**: DAT-configured expected result
- **Read Value**: Actual value from hardware accessor
- **Result**: Boolean comparison of expected vs actual
- **Severity**: Failure severity level for reporting

The system supports nested device testing where test points can reference other devices in the DAT, enabling hierarchical validation and dependency analysis.

```mermaid
graph LR
    subgraph "Test Point Types"
        HARDWARE["Hardware Test Points<br/>Direct Property Access"]
        DEVICE["Device Test Points<br/>Nested Device Validation"]
    end
    
    subgraph "Validation Logic"
        READ["Accessor Read<br/>getValue()"]
        COMPARE["Value Comparison<br/>expected vs actual"]
        SEVERITY["Severity Assignment<br/>OK/Warning/Critical"]
    end
    
    HARDWARE --> READ
    DEVICE --> READ
    READ --> COMPARE
    COMPARE --> SEVERITY
```

Sources: [src/selftest.cpp:230-344](), [include/selftest.hpp:39-88]()

### Root Cause Analysis

The `RootCauseTracer` class extends self-testing capabilities by performing failure analysis when events are detected:

1. **Problem Device Identification**: Extracts device name from incoming event
2. **Associated Device Testing**: Performs self-test on device and its DAT associations  
3. **Root Cause Detection**: Identifies the most nested device that failed testing
4. **Health Status Update**: Updates device health and origin of condition properties
5. **Report Generation**: Creates detailed self-test report attached to the event

This enables the system to not only detect failures but also trace them to their underlying hardware cause.

Sources: [src/selftest.cpp:607-672](), [include/selftest.hpp:407-471]()

## Hardware Interface Tools

The system includes specialized wrapper tools for accessing different hardware interfaces, enabling comprehensive hardware validation and event injection.

### Interface Wrapper Architecture  

```mermaid
graph TB
    subgraph "Wrapper Tools"
        MCTP["mctp-error-detection<br/>MCTP Device Access"]
        FPGA["fpga_regtbl_wrapper<br/>FPGA Register Access"]
        PCIE["pcie_wrapper<br/>PCIe Status Access"]  
        I2C["i2c_wrapper<br/>I2C Interface Access"]
        NVLINK["nvlink-wp-status-wrapper<br/>NVLink Status"]
    end
    
    subgraph "Hardware Interfaces"
        MCTPDEV["MCTP VDM Devices<br/>GPU, NVSwitch"]
        FPGAREG["FPGA Register Tables<br/>Configuration Data"]
        PCIESTAT["PCIe Link Status<br/>Connectivity Info"]
        I2CBUS["I2C Bus Devices<br/>Sensor Access"]
        NVLINKF["NVLink Fabric<br/>High-Speed Links"]
    end
    
    subgraph "Integration Points"
        DA["DataAccessor<br/>Unified Interface"]
        EV["Event Validation<br/>Test Scenarios"]
        ST["Self-Test System<br/>Hardware Validation"]
    end
    
    MCTP --> MCTPDEV
    FPGA --> FPGAREG  
    PCIE --> PCIESTAT
    I2C --> I2CBUS
    NVLINK --> NVLINKF
    
    MCTP --> DA
    FPGA --> DA
    PCIE --> DA
    I2C --> DA
    NVLINK --> DA
    
    DA --> EV
    DA --> ST
```

These wrappers standardize access to various hardware interfaces and enable consistent testing across different device types.

Sources: [tools/meson.build:33-46]()

### JTAG Testing

The `jtag_test` tool provides low-level hardware validation through JTAG interface access:

```mermaid
graph LR
    subgraph "JTAG Testing"
        JTAG["jtag_test<br/>Hardware Validation"]
        CONFIG["JTAG Configuration<br/>Device Chains"]
        TESTS["Test Scenarios<br/>Boundary Scan"]
    end
    
    subgraph "Hardware Under Test"
        DEVICES["NVIDIA Hardware<br/>GPU, NVSwitch, FPGA"]
        CHAINS["JTAG Chains<br/>Device Connectivity"]
        REGS["Test Registers<br/>Status/Control"]
    end
    
    JTAG --> CONFIG
    CONFIG --> TESTS
    TESTS --> DEVICES
    DEVICES --> CHAINS
    CHAINS --> REGS
```

This provides the lowest-level hardware validation capability, enabling detection of fundamental hardware connectivity and functionality issues.

Sources: [tools/jtag/meson.build:1-11]()

## Event Injection Scripts

The system uses two specialized script generators to create bash injection scripts for different testing scenarios.

### Script Generation Architecture

```mermaid
graph TB
    subgraph "Base Framework"
        BASE["InjectorScriptBase<br/>Abstract Script Generator"]
        JSON["JSON Configuration<br/>event_info.json"]
        TEMPLATE["Bash Templates<br/>Script Generation"]
    end
    
    subgraph "Concrete Generators"
        ELS["EventLogsInjectorScript<br/>Direct Logging Mode"]
        EAS["EventAccessorInjectorScript<br/>Property Change Mode"]
    end
    
    subgraph "Generated Output"
        SCRIPT["Bash Injection Script<br/>busctl Commands"]
        COMMANDS["Individual Commands<br/>Property Changes"]
        VALIDATION["Verification Logic<br/>Success Tracking"]
    end
    
    BASE --> ELS
    BASE --> EAS
    JSON --> BASE
    TEMPLATE --> BASE
    ELS --> SCRIPT
    EAS --> SCRIPT
    SCRIPT --> COMMANDS
    SCRIPT --> VALIDATION
```

### EventLogsInjectorScript

Generates scripts that directly insert log entries into the phosphor-logging system using `busctl call` commands to the `xyz.openbmc_project.Logging.Create` interface.

Key features:
- **Direct Log Creation**: Bypasses normal event detection flow
- **Field Validation**: Tests specific log entry fields and severity levels  
- **Success Tracking**: Counts successful vs failed injections
- **Dry Run Support**: Command preview without execution

The generated scripts include error handling, progress reporting, and temporary file management for reliable test execution.

Sources: [tools/modules/event_logging_script.py:1-156]()

### EventAccessorInjectorScript  

Generates scripts that modify D-Bus properties to trigger normal event detection, providing more realistic testing of the complete monitoring pipeline.

Key capabilities:
- **Property Modification**: Changes D-Bus properties using various methods (equal, not_equal, bitmask, lookup)
- **Multi-Interface Support**: Handles DBUS, DeviceCoreAPI, and CMDLINE accessor types
- **Range Expansion**: Supports device ranges like `GPU[0-7]` for bulk testing
- **State Management**: Includes failure state setup and cleanup logic

The script template provides sophisticated property manipulation logic with support for boolean, numeric, and string property types.

Sources: [tools/modules/event_accessor_script.py:1-429](), [tools/modules/templates/event_accessor_script.bash:1-1300]()

## Integration Testing Flow

The complete testing workflow integrates all validation components into a comprehensive testing pipeline.

### End-to-End Testing Process

```mermaid
sequenceDiagram
    participant USER as Test User
    participant EV as event_validation.py
    participant GEN as Script Generators
    participant TARGET as Target System
    participant MONITOR as Event Monitor
    participant VALIDATE as Validation
    
    USER->>EV: execute with parameters
    EV->>TARGET: establish connections
    EV->>GEN: generate injection scripts
    GEN->>GEN: parse JSON configuration
    GEN->>GEN: create bash commands
    EV->>TARGET: upload and execute scripts
    TARGET->>TARGET: modify properties/inject logs
    TARGET->>MONITOR: trigger event detection
    MONITOR->>MONITOR: process events and log
    EV->>TARGET: fetch log entries via Redfish
    EV->>VALIDATE: compare injected vs logged
    VALIDATE->>USER: generate test report
```

### Configuration-Driven Testing

The system supports flexible testing scenarios through command-line parameters:

- **Device Filtering**: `--device GPU` tests only GPU-related events
- **Event Filtering**: `--event "PCIe Error"` tests specific event types
- **Index Filtering**: `--device-index 0,1` tests specific device instances
- **Property Filtering**: `--property I2C3_ALERT` tests events using specific D-Bus properties
- **Execution Modes**: `--dry-run`, `--unique-event`, `--markdown` for different testing needs

This enables both comprehensive validation and targeted debugging scenarios.

Sources: [tools/event_validation.py:84-225](), [tools/modules/templates/event_accessor_script.bash:89-132]()

### Reporting and Documentation

The validation framework provides multiple output formats:

- **Console Output**: Real-time progress and debug information
- **Summary Reports**: Success/failure counts and error details
- **Markdown Generation**: Formatted documentation for test procedures
- **JSON Reports**: Structured self-test results with detailed metrics
- **Log Integration**: Redfish log entry analysis and additional data extraction

This comprehensive reporting enables both automated CI/CD integration and manual diagnostic workflows.

Sources: [tools/event_validation.py:792-815](), [src/selftest.cpp:384-531]()

---

