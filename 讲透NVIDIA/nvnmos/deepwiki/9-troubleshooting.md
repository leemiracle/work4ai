<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvnmos · page 9 Troubleshooting · fetched 2026-10-26 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [entrypoint.sh](entrypoint.sh)

</details>



This document provides a systematic approach to diagnosing and resolving issues with the NvNmos library. It covers general troubleshooting methodology, diagnostic tools, log interpretation, and common failure modes across the system's architecture.

For detailed guidance on specific categories of issues, see:
- [Common Build Issues](#9.1) - Dependency resolution, CMake configuration, and Conan-related problems
- [Runtime Issues](#9.2) - DNS-SD failures, port conflicts, connection activation errors, and registry communication problems

## Diagnostic Framework

NvNmos operates as a multi-layered system with several potential failure points. Systematic diagnosis requires understanding where in the stack the failure occurs and what diagnostic information is available at that layer.

### System Layer Diagnostic Map

```mermaid
graph TB
    subgraph "Diagnostic Entry Points"
        APP["Application Layer"]
        API["C API Layer<br/>(nvnmos.h)"]
        IMPL["Implementation Layer<br/>(nvnmos.cpp, nvnmos_impl.cpp)"]
        NMOS_CPP["nmos-cpp Layer"]
        DEPS["Dependencies<br/>(Boost, cpprestsdk, Avahi/Bonjour)"]
        SYSTEM["System Services<br/>(avahi-daemon, dbus, network)"]
    end
    
    subgraph "Observable Symptoms"
        BUILD_FAIL["Build Failures"]
        STARTUP_FAIL["Startup Failures"]
        DISCOVERY_FAIL["Discovery Failures"]
        CONN_FAIL["Connection Failures"]
        RUNTIME_ERR["Runtime Errors"]
    end
    
    subgraph "Diagnostic Outputs"
        COMPILE_ERR["Compiler Errors"]
        LINK_ERR["Linker Errors"]
        LOG_MSG["Log Messages<br/>(via log_callback)"]
        API_RETURN["API Return Values"]
        HTTP_ERR["HTTP Error Responses"]
        SYS_LOG["System Logs<br/>(journalctl, Event Viewer)"]
    end
    
    BUILD_FAIL --> COMPILE_ERR
    BUILD_FAIL --> LINK_ERR
    
    STARTUP_FAIL --> LOG_MSG
    STARTUP_FAIL --> API_RETURN
    STARTUP_FAIL --> SYS_LOG
    
    DISCOVERY_FAIL --> LOG_MSG
    DISCOVERY_FAIL --> SYS_LOG
    
    CONN_FAIL --> LOG_MSG
    CONN_FAIL --> HTTP_ERR
    
    RUNTIME_ERR --> LOG_MSG
    RUNTIME_ERR --> API_RETURN
    
    COMPILE_ERR --> DEPS
    LINK_ERR --> DEPS
    
    API_RETURN --> API
    LOG_MSG --> IMPL
    LOG_MSG --> NMOS_CPP
    HTTP_ERR --> NMOS_CPP
    SYS_LOG --> SYSTEM
```

**Sources:** [README.md:340-382]()

### Troubleshooting Decision Tree

```mermaid
flowchart TD
    START["Issue Detected"]
    
    WHEN{"When does<br/>issue occur?"}
    
    BUILD["Build Time"]
    RUNTIME["Runtime"]
    
    BUILD_TYPE{"Type of<br/>build error?"}
    RUNTIME_TYPE{"Type of<br/>runtime error?"}
    
    CONAN_ERR["Conan dependency<br/>resolution failure"]
    CMAKE_ERR["CMake configuration<br/>failure"]
    COMPILE_ERR["Compilation failure"]
    
    STARTUP_ERR["create_nmos_node_server<br/>returns NULL"]
    PORT_ERR["Address already<br/>in use"]
    DNS_ERR["DNSService error<br/>-65537"]
    CONN_ERR["Connection<br/>activation failure"]
    
    START --> WHEN
    
    WHEN -->|"Build"| BUILD
    WHEN -->|"Runtime"| RUNTIME
    
    BUILD --> BUILD_TYPE
    RUNTIME --> RUNTIME_TYPE
    
    BUILD_TYPE --> CONAN_ERR
    BUILD_TYPE --> CMAKE_ERR
    BUILD_TYPE --> COMPILE_ERR
    
    RUNTIME_TYPE --> STARTUP_ERR
    RUNTIME_TYPE --> PORT_ERR
    RUNTIME_TYPE --> DNS_ERR
    RUNTIME_TYPE --> CONN_ERR
    
    CONAN_ERR --> BUILD_PAGE["See Common Build Issues<br/>Section: Dependency Resolution"]
    CMAKE_ERR --> BUILD_PAGE
    COMPILE_ERR --> BUILD_PAGE
    
    STARTUP_ERR --> CHECK_LOG["Check log_callback output<br/>for detailed error"]
    PORT_ERR --> RUNTIME_PAGE["See Runtime Issues<br/>Section: Port Conflicts"]
    DNS_ERR --> RUNTIME_PAGE
    CONN_ERR --> RUNTIME_PAGE
    
    CHECK_LOG --> RUNTIME_PAGE["See Runtime Issues<br/>for specific error patterns"]
```

**Sources:** [README.md:340-382]()

## Log Message Interpretation

The NvNmos library routes all internal log messages through the application-provided `log_callback` function. Understanding the structure and sources of these messages is essential for effective troubleshooting.

### Log Callback Architecture

```mermaid
graph TB
    subgraph "Log Message Sources"
        NVNMOS_CPP["nvnmos.cpp<br/>make_settings()<br/>log_gate routing"]
        NVNMOS_IMPL["nvnmos_impl.cpp<br/>Resource management<br/>SDP parsing<br/>Connection activation"]
        NMOS_MODEL["nmos-cpp<br/>node_model operations"]
        NMOS_SERVER["nmos-cpp<br/>HTTP server<br/>Registration client"]
        NMOS_PROTO["nmos-cpp<br/>Protocol handlers<br/>IS-04/IS-05/IS-09"]
    end
    
    subgraph "Log Routing"
        LOG_GATE["slog::log_gate<br/>(nvnmos.cpp)"]
        WRAP_CALLBACK["Wrapped log_callback<br/>(C++ to C bridge)"]
    end
    
    subgraph "Application Layer"
        APP_CALLBACK["Application log_callback<br/>(NvNmosNodeConfig.log_callback)"]
        APP_LOGGER["Application logging system"]
    end
    
    NVNMOS_CPP --> LOG_GATE
    NVNMOS_IMPL --> LOG_GATE
    NMOS_MODEL --> LOG_GATE
    NMOS_SERVER --> LOG_GATE
    NMOS_PROTO --> LOG_GATE
    
    LOG_GATE --> WRAP_CALLBACK
    WRAP_CALLBACK --> APP_CALLBACK
    APP_CALLBACK --> APP_LOGGER
```

**Sources:** [README.md:310-311](), Architecture diagrams

### Log Level Semantics

| Log Level Range | Severity | Typical Sources | When to Investigate |
|-----------------|----------|-----------------|---------------------|
| > 0 | Warnings and Errors | API validation failures, network errors, resource conflicts | Always - indicates a problem |
| 0 | Informational | Node lifecycle events, registration success | When diagnosing flow |
| -10 to -1 | Debug | Resource creation, connection state changes | When tracing operations |
| < -10 | Trace | HTTP requests/responses, protocol details | When deep debugging |

**Sources:** [README.md:310-312]()

### Common Log Message Patterns

| Log Pattern | Source | Meaning | Resolution |
|-------------|--------|---------|------------|
| `asio listen error: system:98` | nmos-cpp HTTP server | Port already in use | Use different port in `NvNmosNodeConfig.port` |
| `DNSServiceRegister reported error: -65537` | nmos-cpp DNS-SD integration | DNS-SD daemon not running | Start `avahi-daemon` (Linux) or Bonjour Service (Windows) |
| `DNSServiceBrowse reported error: -65537` | nmos-cpp DNS-SD integration | Cannot discover registries | Check DNS-SD daemon status |
| `*** WARNING *** uses the Apple Bonjour compatibility layer` | Avahi compatibility layer | Informational only | Safe to ignore |
| `Failed to parse SDP` | nvnmos_impl.cpp SDP processing | Invalid SDP format | Validate SDP against SMPTE ST 2110 specifications |
| `Connection activation callback returned false` | nvnmos_impl.cpp activation handler | Application rejected activation | Check application's `rtp_connection_activated` implementation |

**Sources:** [README.md:342-382]()

## Diagnostic Methodology

### Step-by-Step Diagnostic Process

```mermaid
flowchart TD
    START["Observe Failure"]
    
    COLLECT["Collect Diagnostic Data"]
    
    BUILD_DATA["- Conan output<br/>- CMake configuration log<br/>- Compiler error messages"]
    RUNTIME_DATA["- Application log_callback output<br/>- System logs (journalctl/Event Viewer)<br/>- Network interface status<br/>- Process/port status (netstat/ss)"]
    
    ISOLATE["Identify Failure Layer"]
    
    LAYER_BUILD["Build System<br/>(Conan/CMake)"]
    LAYER_API["API Layer<br/>(nvnmos.h)"]
    LAYER_IMPL["Implementation<br/>(nvnmos_impl.cpp)"]
    LAYER_NMOS["Protocol<br/>(nmos-cpp)"]
    LAYER_DEPS["Dependencies/System"]
    
    VERIFY["Verify Prerequisites"]
    
    VERIFY_BUILD["- Conan 2.2+ installed<br/>- CMake 3.17+ installed<br/>- Correct toolchain"]
    VERIFY_RUNTIME["- DNS-SD daemon running<br/>- Network interfaces up<br/>- Ports available<br/>- Registry accessible"]
    
    CONSULT["Consult Specific Guide"]
    
    START --> COLLECT
    COLLECT --> |"Build issue"| BUILD_DATA
    COLLECT --> |"Runtime issue"| RUNTIME_DATA
    
    BUILD_DATA --> ISOLATE
    RUNTIME_DATA --> ISOLATE
    
    ISOLATE --> LAYER_BUILD
    ISOLATE --> LAYER_API
    ISOLATE --> LAYER_IMPL
    ISOLATE --> LAYER_NMOS
    ISOLATE --> LAYER_DEPS
    
    LAYER_BUILD --> VERIFY
    LAYER_API --> VERIFY
    LAYER_IMPL --> VERIFY
    LAYER_NMOS --> VERIFY
    LAYER_DEPS --> VERIFY
    
    VERIFY --> |"Build"| VERIFY_BUILD
    VERIFY --> |"Runtime"| VERIFY_RUNTIME
    
    VERIFY_BUILD --> CONSULT
    VERIFY_RUNTIME --> CONSULT
    
    CONSULT --> |"Build"| BUILD_GUIDE["Common Build Issues (9.1)"]
    CONSULT --> |"Runtime"| RUNTIME_GUIDE["Runtime Issues (9.2)"]
```

**Sources:** [README.md:93-382]()

### Enabling Verbose Logging

To obtain detailed diagnostic information, configure the log level when creating the node server:

**Via NvNmosNodeConfig:**
```c
NvNmosNodeConfig config;
// ... other configuration
config.log_level = -40;  // Maximum verbosity
```

**In nvnmos-example:**
```sh
# Fourth argument sets log level
nvnmos-example nmos-api.local 8080 192.0.2.0 -40
```

Verbose logging (`log_level < 0`) produces output including:
- HTTP request/response details
- DNS-SD service discovery events
- Resource creation and modification
- Connection state transitions
- SDP parsing details
- Protocol-level interactions

**Sources:** [README.md:310-312]()

## System Health Verification

### Quick Health Check Commands

**Linux:**
```sh
# Check if Avahi daemon is running
systemctl status avahi-daemon

# Check if D-Bus is running
systemctl status dbus

# Verify network interfaces
ip addr show

# Check for port conflicts
ss -tulpn | grep <port>

# View system logs
journalctl -u avahi-daemon -f
```

**Windows:**
```powershell
# Check if Bonjour Service is running
Get-Service | Where-Object {$_.Name -like "*Bonjour*"}

# Check for port conflicts
netstat -ano | findstr <port>

# View event logs
Get-EventLog -LogName Application -Source Bonjour -Newest 50
```

**Sources:** [README.md:269-290](), [entrypoint.sh:20-24]()

### API Return Value Analysis

All NvNmos C API functions that can fail return indicators of success or failure:

| Function | Success Return | Failure Return | Common Failure Causes |
|----------|----------------|----------------|----------------------|
| `create_nmos_node_server` | Non-NULL pointer | NULL | Invalid config, port conflict, DNS-SD unavailable |
| `add_nmos_sender_to_node_server` | true | false | Invalid SDP, resource ID conflict |
| `add_nmos_receiver_to_node_server` | true | false | Invalid SDP, resource ID conflict |
| `nmos_connection_rtp_activate` | true | false | Invalid connection ID, malformed parameters |
| `remove_nmos_*_from_node_server` | true | false | Resource ID not found |

When an API function fails, detailed error information is available through the `log_callback` mechanism. Always check both the return value and log output when diagnosing failures.

**Sources:** Architecture diagrams, API design patterns

## Common Failure Point Architecture

```mermaid
graph TB
    subgraph "Build-Time Failure Points"
        CONAN_FAIL["Conan Dependency Resolution<br/>(conanfile.py)<br/>Missing packages, version conflicts"]
        CMAKE_FAIL["CMake Configuration<br/>(CMakeLists.txt)<br/>Toolchain issues, missing dependencies"]
        COMPILE_FAIL["Compilation<br/>(nvnmos.cpp, nvnmos_impl.cpp)<br/>API mismatches, missing headers"]
    end
    
    subgraph "Initialization Failure Points"
        CONFIG_FAIL["Configuration Validation<br/>(nvnmos.cpp:make_settings)<br/>Invalid port, interface, or settings"]
        DNS_INIT_FAIL["DNS-SD Initialization<br/>(nmos-cpp)<br/>Daemon not running, no network"]
        HTTP_INIT_FAIL["HTTP Server Start<br/>(nmos-cpp:server)<br/>Port in use, bind failure"]
    end
    
    subgraph "Discovery Failure Points"
        MDNS_FAIL["mDNS Service Discovery<br/>(nmos-cpp + Avahi/Bonjour)<br/>No registry advertisements"]
        REG_CONNECT_FAIL["Registry Connection<br/>(nmos-cpp:registration_handler)<br/>Network unreachable, auth failure"]
        REG_POST_FAIL["Resource Registration<br/>(nmos-cpp IS-04 client)<br/>Invalid resource data, version mismatch"]
    end
    
    subgraph "Runtime Failure Points"
        SDP_PARSE_FAIL["SDP Parsing<br/>(nvnmos_impl.cpp:parse_sdp_parameters)<br/>Invalid format, missing attributes"]
        RESOURCE_FAIL["Resource Management<br/>(nvnmos_impl.cpp:add_sender/receiver)<br/>ID conflict, invalid flow type"]
        ACTIVATION_FAIL["Connection Activation<br/>(nvnmos_impl.cpp:activate_rtp_connection)<br/>Callback rejection, parameter error"]
        CALLBACK_FAIL["Application Callback<br/>(rtp_connection_activated)<br/>Data plane configuration failure"]
    end
    
    CONAN_FAIL -.->|"Prevents"| CMAKE_FAIL
    CMAKE_FAIL -.->|"Prevents"| COMPILE_FAIL
    
    CONFIG_FAIL -.->|"Prevents"| DNS_INIT_FAIL
    DNS_INIT_FAIL -.->|"Prevents"| HTTP_INIT_FAIL
    
    HTTP_INIT_FAIL -.->|"Prevents"| MDNS_FAIL
    MDNS_FAIL -.->|"Prevents"| REG_CONNECT_FAIL
    REG_CONNECT_FAIL -.->|"Prevents"| REG_POST_FAIL
    
    SDP_PARSE_FAIL -.->|"Prevents"| RESOURCE_FAIL
    RESOURCE_FAIL -.->|"Prevents"| ACTIVATION_FAIL
    ACTIVATION_FAIL -.->|"Triggers"| CALLBACK_FAIL
```

**Sources:** [README.md:340-382](), Architecture diagrams

## Environment-Specific Considerations

### Docker Environments

When running NvNmos in containers, additional failure modes exist:

- **D-Bus socket access**: Container must have access to D-Bus system socket
- **Network mode**: Host networking may be required for mDNS functionality
- **Service startup**: DNS-SD daemon must start before application

Reference: [entrypoint.sh:20-30]()

### Multi-Interface Systems

Systems with multiple network interfaces require careful configuration:

- Specify the correct interface IP address in `NvNmosNodeConfig`
- Ensure the interface has connectivity to the NMOS Registry
- Verify that mDNS advertisements use the correct interface

## Gathering Support Information

When requesting assistance, include:

1. **Version Information**
   - NvNmos build version and commit hash
   - Operating system and version
   - Compiler version (GCC/MSVC)

2. **Configuration**
   - Relevant fields from `NvNmosNodeConfig`
   - Network topology and interface configuration
   - DNS-SD daemon version

3. **Diagnostic Output**
   - Complete log output with `log_level = -40`
   - Return values from failed API calls
   - System service status

4. **Minimal Reproduction**
   - Simplified configuration that reproduces the issue
   - Steps to trigger the failure
   - Expected vs. actual behavior

## Related Documentation

- [Common Build Issues](#9.1) - Detailed troubleshooting for dependency, CMake, and compilation problems
- [Runtime Issues](#9.2) - Specific solutions for DNS-SD, networking, and connection activation failures
- [API Reference](#4) - Complete API documentation for understanding function contracts
- [Integration Guide](#7) - Guidance on proper integration patterns to avoid common pitfalls

---

