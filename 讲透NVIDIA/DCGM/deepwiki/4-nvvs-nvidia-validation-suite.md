<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DCGM · page 4 NVVS (NVIDIA Validation Suite) · fetched 2026-10-26 -->

# NVVS (NVIDIA Validation Suite)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dcgmi/Diag.cpp](dcgmi/Diag.cpp)
- [dcgmlib/src/DcgmApi.cpp](dcgmlib/src/DcgmApi.cpp)
- [modules/diag/DcgmDiagManager.cpp](modules/diag/DcgmDiagManager.cpp)
- [nvvs/diag-skus.yaml.in](nvvs/diag-skus.yaml.in)
- [testing/python3/tests/test_dcgm_diag.py](testing/python3/tests/test_dcgm_diag.py)

</details>



## Purpose and Scope

NVVS (NVIDIA Validation Suite) is a standalone diagnostic and validation tool that performs GPU health checks and stress testing. It is spawned as an external process by DCGM's Diagnostic Module to isolate test execution from the main DCGM daemon. NVVS uses a plugin-based architecture where individual test plugins are compiled against multiple CUDA versions, enabling comprehensive hardware validation without risking the stability of the monitoring system.

For information about the Diagnostic Module that orchestrates NVVS execution, see [Diagnostic Module](#3.3). For details about the diag-skus.yaml configuration system, see [Diagnostic SKUs Configuration](#4.1). For the plugin architecture, see [Plugin System](#4.2).

---

## Architecture Overview

NVVS operates as an isolated subprocess within the DCGM ecosystem, providing a safety barrier between potentially unstable diagnostic tests and the core monitoring functionality.

```mermaid
graph TB
    subgraph "DCGM Host Engine"
        DIAG_MOD["DcgmDiagManager"]
        CORE_PROXY["DcgmCoreProxy"]
    end
    
    subgraph "NVVS Process /usr/libexec/datacenter-gpu-manager-4/nvvs"
        NVVS_MAIN["nvvs executable<br/>Test Orchestration"]
        PLUGIN_LOADER["Plugin Loader"]
        
        subgraph "Test Plugins"
            DIAG_PLUGIN["Diagnostic_*.so<br/>GpuBurnPlugin<br/>HGEMM/SGEMM/DGEMM"]
            MEM_PLUGIN["MemTest_*.so<br/>Memory Testing"]
            STRESS_PLUGIN["TargetedStress_*.so<br/>ConstantPerf"]
            POWER_PLUGIN["TargetedPower_*.so<br/>Power Testing"]
            PCIE_PLUGIN["pcie_*.so<br/>Bandwidth Testing"]
            EUD_PLUGIN["eud_*.so<br/>Hardware Diagnostics"]
        end
        
        CONFIG_LOADER["Configuration Parser"]
    end
    
    subgraph "Configuration Files"
        SKU_CONFIG["diag-skus.yaml<br/>Per-SKU Parameters"]
        CUSTOM_CONFIG["Custom Config<br/>User Overrides"]
    end
    
    subgraph "Hardware"
        GPU["NVIDIA GPUs<br/>NVML/CUDA"]
    end
    
    DIAG_MOD -->|"ChildProcessSpawn"| NVVS_MAIN
    DIAG_MOD -->|"FD 0: stdin"| NVVS_MAIN
    NVVS_MAIN -->|"FD 1: stdout"| DIAG_MOD
    NVVS_MAIN -->|"FD 2: stderr"| DIAG_MOD
    NVVS_MAIN -->|"FD 3: Data Channel<br/>dcgmDiagResponse"| DIAG_MOD
    
    NVVS_MAIN --> CONFIG_LOADER
    CONFIG_LOADER --> SKU_CONFIG
    CONFIG_LOADER --> CUSTOM_CONFIG
    
    NVVS_MAIN --> PLUGIN_LOADER
    PLUGIN_LOADER --> DIAG_PLUGIN
    PLUGIN_LOADER --> MEM_PLUGIN
    PLUGIN_LOADER --> STRESS_PLUGIN
    PLUGIN_LOADER --> POWER_PLUGIN
    PLUGIN_LOADER --> PCIE_PLUGIN
    PLUGIN_LOADER --> EUD_PLUGIN
    
    DIAG_PLUGIN --> GPU
    MEM_PLUGIN --> GPU
    STRESS_PLUGIN --> GPU
    POWER_PLUGIN --> GPU
    PCIE_PLUGIN --> GPU
    EUD_PLUGIN --> GPU
    
    DIAG_MOD -.->|"ChildProcessStop<br/>SIGTERM/SIGKILL"| NVVS_MAIN
    DIAG_MOD --> CORE_PROXY
```

**Sources:** [modules/diag/DcgmDiagManager.cpp:1-1200](), [nvvs/diag-skus.yaml.in:1-100]()

---

## Process Isolation Model

NVVS runs as a completely separate process to ensure that diagnostic test failures, crashes, or hangs cannot affect the DCGM host engine's monitoring capabilities.

```mermaid
graph TB
    subgraph "Host Process Space PID=dcgm_pid"
        HOST_ENGINE["nv-hostengine<br/>Main Daemon"]
        DIAG_MGR["DcgmDiagManager<br/>m_nvvsPID<br/>m_childProcessHandle"]
        CHILD_PROXY["ChildProcess API<br/>ChildProcessSpawn<br/>ChildProcessGetStatus<br/>ChildProcessStop<br/>ChildProcessDestroy"]
    end
    
    subgraph "NVVS Process Space PID=nvvs_pid"
        NVVS_BIN["nvvs binary<br/>/usr/libexec/datacenter-gpu-manager-4/nvvs"]
        TEST_THREADS["Test Execution Threads"]
        CUDA_CTX["CUDA Contexts"]
    end
    
    subgraph "Communication Channels"
        STDOUT["stdout pipe"]
        STDERR["stderr pipe"]
        DATA_FD["dataChannelFd=3<br/>Structured Response"]
    end
    
    subgraph "Process Lifecycle"
        SPAWN["dcgmChildProcessParams_v1<br/>executable path<br/>args array<br/>dataChannelFd"]
        STATUS["dcgmChildProcessStatus_v1<br/>running<br/>exitCode<br/>receivedSignal"]
        TERMINATE["Signal Handling<br/>SIGTERM attempt<br/>SIGKILL escalation"]
    end
    
    HOST_ENGINE --> DIAG_MGR
    DIAG_MGR -->|"ChildProcessSpawn"| CHILD_PROXY
    CHILD_PROXY -->|"fork/exec"| NVVS_BIN
    
    NVVS_BIN --> STDOUT
    NVVS_BIN --> STDERR
    NVVS_BIN --> DATA_FD
    
    STDOUT --> DIAG_MGR
    STDERR --> DIAG_MGR
    DATA_FD --> DIAG_MGR
    
    NVVS_BIN --> TEST_THREADS
    TEST_THREADS --> CUDA_CTX
    
    CHILD_PROXY --> SPAWN
    CHILD_PROXY --> STATUS
    CHILD_PROXY --> TERMINATE
    
    DIAG_MGR -->|"ChildProcessGetStatus"| STATUS
    DIAG_MGR -->|"ChildProcessStop"| TERMINATE
    TERMINATE -.->|"SIGTERM/SIGKILL"| NVVS_BIN
```

**Sources:** [modules/diag/DcgmDiagManager.cpp:89-120](), [modules/diag/DcgmDiagManager.cpp:860-900](), [modules/diag/DcgmDiagManager.cpp:122-250]()

---

## NVVS Command Construction

The DcgmDiagManager constructs the NVVS command line with various arguments based on the diagnostic request parameters.

```mermaid
graph LR
    subgraph "dcgmRunDiag_v10 Input"
        DRD_FIELDS["testNames[]<br/>testParms[]<br/>entityIds<br/>fakeGpuList<br/>debugLogFile<br/>statsPath<br/>debugLevel<br/>clocksEventMask<br/>failCheckInterval<br/>totalIterations<br/>watchFrequency<br/>ignoreErrorCodes<br/>configFileContents"]
    end
    
    subgraph "CreateNvvsCommand Function"
        BASE_ARGS["Base Arguments<br/>--channel-fd 3<br/>--response-version"]
        RUN_OPTS["AddRunOptions<br/>--specifiedtest<br/>--parameters"]
        CONFIG_FILE["AddConfigFile<br/>--config tempfile<br/>or --configless"]
        MISC_OPTS["AddMiscellaneousNvvsOptions<br/>--statsonfail<br/>-v verbose<br/>-l logfile<br/>--statspath<br/>-f fakegpus<br/>--entity-id<br/>-d debuglevel<br/>-p plugindir<br/>--clocksevent-mask<br/>--fail-early<br/>--check-interval<br/>--current-iteration<br/>--total-iterations<br/>--watch-frequency<br/>--ignoreErrorCodes<br/>--noHangDetect"]
    end
    
    subgraph "Final Command Vector"
        CMD_VECTOR["vector<string> cmdArgs<br/>args[0] = nvvs_path<br/>args[1..n] = arguments"]
    end
    
    DRD_FIELDS --> BASE_ARGS
    DRD_FIELDS --> RUN_OPTS
    DRD_FIELDS --> CONFIG_FILE
    DRD_FIELDS --> MISC_OPTS
    
    BASE_ARGS --> CMD_VECTOR
    RUN_OPTS --> CMD_VECTOR
    CONFIG_FILE --> CMD_VECTOR
    MISC_OPTS --> CMD_VECTOR
    
    CMD_VECTOR -->|"PerformExternalCommand"| EXEC["Process Execution"]
```

**Sources:** [modules/diag/DcgmDiagManager.cpp:603-646](), [modules/diag/DcgmDiagManager.cpp:325-379](), [modules/diag/DcgmDiagManager.cpp:381-475](), [modules/diag/DcgmDiagManager.cpp:483-600]()

---

## Communication Protocol

NVVS communicates with the DCGM Diag Module through multiple channels, each serving a specific purpose.

```mermaid
graph TB
    subgraph "NVVS Process"
        NVVS["nvvs executable"]
        STDOUT_WRITER["stdout stream<br/>Log messages"]
        STDERR_WRITER["stderr stream<br/>Error messages"]
        DATA_WRITER["FD 3 writer<br/>Binary protocol"]
    end
    
    subgraph "Data Channel Protocol FD=3"
        STRUCT_VERSION["GetStructVersion<br/>First 4 bytes = version"]
        DIAG_STATUS["dcgmDiagStatus_v1<br/>version<br/>totalTests<br/>completedTests<br/>testName<br/>errorCode"]
        DIAG_RESPONSE["dcgmDiagResponse_v12<br/>Complete test results<br/>version=0xC0000000C"]
    end
    
    subgraph "DcgmDiagManager Reader"
        STDOUT_READER["ReadProcessOutput<br/>fmt::memory_buffer"]
        STDERR_READER["ReadProcessOutput<br/>fmt::memory_buffer"]
        DATA_READER["ReadDataFromFd<br/>DcgmDiagResponseWrapper"]
    end
    
    subgraph "Processing"
        UPDATE_STATUS["UpdateDiagStatus<br/>AppendSamples to Cache<br/>DCGM_FI_DEV_DIAG_STATUS"]
        PARSE_RESPONSE["Parse Response<br/>Extract tests<br/>Extract results<br/>Extract errors"]
        EXIT_CODE["Process Exit Status<br/>NVVS_ST_TEST_NOT_FOUND<br/>Signal handling"]
    end
    
    NVVS --> STDOUT_WRITER
    NVVS --> STDERR_WRITER
    NVVS --> DATA_WRITER
    
    STDOUT_WRITER --> STDOUT_READER
    STDERR_WRITER --> STDERR_READER
    DATA_WRITER --> STRUCT_VERSION
    
    STRUCT_VERSION --> DIAG_STATUS
    STRUCT_VERSION --> DIAG_RESPONSE
    
    DIAG_STATUS --> DATA_READER
    DIAG_RESPONSE --> DATA_READER
    
    DATA_READER --> UPDATE_STATUS
    DATA_READER --> PARSE_RESPONSE
    
    STDOUT_READER --> EXIT_CODE
    STDERR_READER --> EXIT_CODE
    PARSE_RESPONSE --> EXIT_CODE
```

**Key Protocol Details:**

| Channel | FD | Content Type | Purpose |
|---------|-----|--------------|---------|
| stdin | 0 | None | Not used |
| stdout | 1 | Text | Informational logs, progress messages |
| stderr | 2 | Text | Error messages, warnings |
| Data Channel | 3 | Binary | Structured diagnostic status and results |

**Data Channel Message Types:**

| Structure | Version Field | Size | Purpose |
|-----------|---------------|------|---------|
| `dcgmDiagStatus_v1` | `dcgmDiagStatus_version` | Variable | Periodic progress updates during test execution |
| `dcgmDiagResponse_v12` | `dcgmDiagResponse_version12` (0xC0000000C) | Large | Final comprehensive test results |

**Sources:** [modules/diag/DcgmDiagManager.cpp:701-757](), [modules/diag/DcgmDiagManager.cpp:906-972](), [modules/diag/DcgmDiagManager.cpp:50]()

---

## Diagnostic Execution Flow

The complete flow from API call to result reporting involves multiple stages of process management and data exchange.

```mermaid
sequenceDiagram
    participant CLI as dcgmi diag
    participant API as dcgmActionValidate_v2
    participant DiagMgr as DcgmDiagManager
    participant ChildAPI as ChildProcess API
    participant NVVS as nvvs Process
    participant Plugin as Test Plugin
    participant GPU as GPU Hardware
    
    CLI->>API: dcgmRunDiag_v10
    API->>DiagMgr: DCGM_DIAG_SR_RUN_DIAG
    
    DiagMgr->>DiagMgr: CreateNvvsCommand<br/>Build argument vector
    DiagMgr->>DiagMgr: CanRunNewNvvsInstance<br/>Check m_nvvsPID
    
    DiagMgr->>ChildAPI: ChildProcessSpawn<br/>dcgmChildProcessParams_v1
    ChildAPI->>NVVS: fork + exec
    Note over NVVS: Process starts<br/>PID assigned
    
    ChildAPI-->>DiagMgr: handle + pid
    DiagMgr->>DiagMgr: UpdateChildPID(pid)
    
    NVVS->>NVVS: Parse arguments<br/>Load configuration
    NVVS->>NVVS: Load test plugins<br/>Initialize tests
    
    loop For Each Test
        NVVS->>Plugin: Execute test
        Plugin->>GPU: CUDA operations<br/>Memory tests<br/>Compute workloads
        GPU-->>Plugin: Results
        Plugin-->>NVVS: Test metrics
        
        NVVS->>DiagMgr: Write dcgmDiagStatus_v1<br/>to FD 3
        DiagMgr->>DiagMgr: UpdateDiagStatus<br/>AppendSamples to cache
    end
    
    NVVS->>DiagMgr: Write dcgmDiagResponse_v12<br/>to FD 3
    NVVS->>NVVS: exit(status)
    
    DiagMgr->>ChildAPI: ChildProcessWait
    ChildAPI-->>DiagMgr: Process exited
    
    DiagMgr->>ChildAPI: ChildProcessGetStatus
    ChildAPI-->>DiagMgr: dcgmChildProcessStatus_v1
    
    DiagMgr->>DiagMgr: Parse results<br/>Build response
    DiagMgr->>ChildAPI: ChildProcessDestroy
    
    DiagMgr-->>API: dcgmDiagResponse_v12
    API-->>CLI: Display results
```

**Sources:** [modules/diag/DcgmDiagManager.cpp:760-1038](), [testing/python3/tests/test_dcgm_diag.py:374-419](), [dcgmi/Diag.cpp:522-574]()

---

## Configuration System

NVVS uses a hierarchical configuration system with default SKU-specific parameters that can be overridden by custom configuration files.

### Configuration File Handling

```mermaid
graph TB
    subgraph "Configuration Sources"
        DRD_CONFIG["drd.configFileContents<br/>In-memory config string"]
        CUSTOM_FILE["Custom Config File<br/>User-specified"]
        DEFAULT_SKU["diag-skus.yaml<br/>Built-in defaults"]
    end
    
    subgraph "AddConfigFile Processing"
        CHECK_CONTENTS["Check configFileContents<br/>strlen > 0?"]
        CREATE_TEMP["mkstemp<br/>/tmp/tmp-dcgm-XXXXXX"]
        WRITE_FILE["write() config contents"]
        SET_PERMS["chmod 0600<br/>Adjust ownership"]
        SERVICE_ACCOUNT["GetServiceAccount<br/>chown if needed"]
    end
    
    subgraph "NVVS Arguments"
        CONFIG_ARG["--config /tmp/tmp-dcgm-XXXXXX"]
        CONFIGLESS_ARG["--configless"]
    end
    
    DRD_CONFIG --> CHECK_CONTENTS
    CHECK_CONTENTS -->|"Yes"| CREATE_TEMP
    CHECK_CONTENTS -->|"No"| CONFIGLESS_ARG
    
    CREATE_TEMP --> WRITE_FILE
    WRITE_FILE --> SET_PERMS
    SET_PERMS --> SERVICE_ACCOUNT
    SERVICE_ACCOUNT --> CONFIG_ARG
    
    CONFIG_ARG -->|"Loaded by NVVS"| CUSTOM_FILE
    CONFIGLESS_ARG -->|"Loaded by NVVS"| DEFAULT_SKU
```

**Configuration File Creation:**

1. **Temporary File Creation** [modules/diag/DcgmDiagManager.cpp:389-402]()
   - Uses `mkstemp()` with template `/tmp/tmp-dcgm-XXXXXX`
   - Retries up to 3 times on failure
   - Sets permissions to 0600 (owner read/write only)

2. **Service Account Handling** [modules/diag/DcgmDiagManager.cpp:420-451]()
   - Retrieves service account via `GetServiceAccount(m_coreProxy)`
   - Calls `GetUserCredentials()` to get uid/gid
   - Uses `chown()` to set file ownership if service account is configured

3. **Content Writing** [modules/diag/DcgmDiagManager.cpp:417-418]()
   - Writes `drd->configFileContents` to temporary file
   - Verifies write succeeded before proceeding

### SKU Configuration Structure

The `diag-skus.yaml` file contains GPU-specific parameters organized by PCI device ID:

```mermaid
graph LR
    subgraph "diag-skus.yaml Structure"
        ROOT["Root<br/>version<br/>spec: dcgm-diag-v1"]
        SKUS["skus array"]
        
        subgraph "Per-SKU Entry"
            SKU_ID["name: GPU Name<br/>id: PCI Device ID hex"]
            
            TP["targeted_power<br/>is_allowed<br/>target_power watts<br/>starting_matrix_dim<br/>use_dgemm bool<br/>ops_per_requeue<br/>max_graphics_clock"]
            
            TS["targeted_stress<br/>is_allowed<br/>target_stress GFLOPs<br/>use_dgemm bool<br/>max_memory_clock<br/>max_graphics_clock"]
            
            SMS["sm_stress<br/>is_allowed<br/>target_stress GFLOPs<br/>use_dgemm bool"]
            
            PCIE["pcie<br/>is_allowed<br/>h2d_d2h_single_pinned<br/>min_pci_generation<br/>min_pci_width"]
            
            MEM["memory<br/>is_allowed<br/>l1cache_size_kb_per_sm<br/>l1_is_allowed"]
            
            DIAG["diagnostic<br/>is_allowed<br/>matrix_dim"]
            
            MEMBW["memory_bandwidth<br/>is_allowed<br/>minimum_bandwidth MB/s"]
            
            PULSE["pulse_test<br/>is_allowed"]
            
            NVBW["nvbandwidth<br/>is_allowed"]
        end
    end
    
    ROOT --> SKUS
    SKUS --> SKU_ID
    SKU_ID --> TP
    SKU_ID --> TS
    SKU_ID --> SMS
    SKU_ID --> PCIE
    SKU_ID --> MEM
    SKU_ID --> DIAG
    SKU_ID --> MEMBW
    SKU_ID --> PULSE
    SKU_ID --> NVBW
```

**Example SKU Configuration:**

| Parameter | Example (H100 80GB HBM3, ID: 0x2330) | Purpose |
|-----------|--------------------------------------|---------|
| `target_power` | 700.0 W | Expected power consumption during power test |
| `target_stress` | 29250.0 GFLOPs | Expected performance during stress test (75% of max) |
| `use_dgemm` | false | Use DGEMM (true) or SGEMM/HGEMM (false) |
| `minimum_bandwidth` | 1905000 MB/s | Minimum acceptable memory bandwidth (75% of spec) |
| `matrix_dim` | 8192 | Matrix dimension for GEMM operations |
| `min_pci_generation` | 3.0 | Minimum required PCIe generation |
| `min_pci_width` | 16 | Minimum required PCIe lane width |

**Sources:** [nvvs/diag-skus.yaml.in:1-100](), [nvvs/diag-skus.yaml.in:139-178](), [modules/diag/DcgmDiagManager.cpp:381-475]()

---

## Test Plugin Architecture

NVVS loads test plugins dynamically at runtime. Each plugin is compiled for specific CUDA versions to match the system's CUDA driver.

### Plugin Discovery and Loading

```mermaid
graph TB
    subgraph "Plugin Location"
        DEFAULT_DIR["/usr/share/nvidia-validation-suite<br/>Default plugin directory"]
        ENV_DIR["NVVS_PLUGIN_DIR<br/>Environment override"]
    end
    
    subgraph "Plugin Files"
        DIAG_11["Diagnostic_11.so"]
        DIAG_12["Diagnostic_12.so"]
        DIAG_13["Diagnostic_13.so"]
        
        MEM_11["MemTest_11.so"]
        MEM_12["MemTest_12.so"]
        MEM_13["MemTest_13.so"]
        
        STRESS_11["TargetedStress_11.so"]
        POWER_11["TargetedPower_11.so"]
        PCIE_11["pcie_11.so"]
        EUD_11["eud_11.so"]
        
        NVBW_12["NVBandwidth_12.so"]
        NVBW_13["NVBandwidth_13.so"]
    end
    
    subgraph "NVVS Runtime"
        DETECT_CUDA["Detect CUDA Runtime<br/>Query driver version"]
        SELECT_PLUGIN["Select Plugin Variant<br/>Match CUDA major version"]
        DLOPEN["dlopen plugin.so<br/>Load shared library"]
        INIT_PLUGIN["Initialize Plugin<br/>Call entry points"]
    end
    
    subgraph "Plugin Interface"
        PLUGIN_BASE["Plugin Base Class"]
        TEST_METHODS["RunTest<br/>GetResults<br/>Cleanup"]
    end
    
    ENV_DIR -->|"If set"| SELECT_PLUGIN
    DEFAULT_DIR -->|"Default"| SELECT_PLUGIN
    
    SELECT_PLUGIN --> DIAG_11
    SELECT_PLUGIN --> DIAG_12
    SELECT_PLUGIN --> DIAG_13
    SELECT_PLUGIN --> MEM_11
    SELECT_PLUGIN --> STRESS_11
    SELECT_PLUGIN --> NVBW_12
    
    DETECT_CUDA --> SELECT_PLUGIN
    SELECT_PLUGIN --> DLOPEN
    DLOPEN --> INIT_PLUGIN
    INIT_PLUGIN --> PLUGIN_BASE
    PLUGIN_BASE --> TEST_METHODS
```

**CUDA Version Mapping:**

| CUDA Driver Version | Plugin Suffix | Example Plugins |
|---------------------|---------------|-----------------|
| CUDA 11.x | `_11.so` | `Diagnostic_11.so`, `MemTest_11.so` |
| CUDA 12.x | `_12.so` | `Diagnostic_12.so`, `NVBandwidth_12.so` |
| CUDA 13.x | `_13.so` | `Diagnostic_13.so`, `NVBandwidth_13.so` |

**Plugin Selection Logic:**
1. Query CUDA driver version via NVML
2. Extract major version number
3. Scan plugin directory for matching `*_<major>.so` files
4. Load plugins in order based on test specification

**Sources:** [modules/diag/DcgmDiagManager.cpp:533-538]()

---

## Test Types and Implementations

NVVS provides multiple test categories, each targeting different aspects of GPU validation.

### Test Categories

```mermaid
graph TB
    subgraph "Deployment Tests"
        SW["Software Test<br/>NVML queries<br/>Driver checks<br/>Permissions"]
    end
    
    subgraph "Hardware Tests"
        PCIE["PCIe Test<br/>Bandwidth measurement<br/>P2P validation<br/>AER error checking"]
    end
    
    subgraph "Integration Tests"
        DIAG["Diagnostic Test<br/>GpuBurnPlugin<br/>GEMM operations<br/>Thermal monitoring<br/>Clocks monitoring"]
        
        MEM["Memory Test<br/>MemTest plugin<br/>Pattern testing<br/>Cache validation"]
        
        MEMBW["Memory Bandwidth<br/>Streaming kernels<br/>Bandwidth validation"]
        
        PULSE["Pulse Test<br/>Quick validation<br/>Basic compute"]
    end
    
    subgraph "Stress Tests"
        TS["Targeted Stress<br/>ConstantPerf<br/>Sustained load<br/>Performance target"]
        
        TP["Targeted Power<br/>Power consumption<br/>Power limit testing"]
        
        SMS["SM Stress<br/>Streaming Multiprocessor<br/>Compute saturation"]
    end
    
    subgraph "EUD Tests"
        EUD["EUD Hardware Diagnostics<br/>Low-level hardware tests<br/>Manufacturing validation"]
    end
```

### Test Implementation Details

| Test Name | Plugin | Primary Function | Key Metrics | Configuration Parameters |
|-----------|--------|------------------|-------------|-------------------------|
| **diagnostic** | `Diagnostic_*.so` | GPU burn-in test using GEMM operations | Temperature, clocks, XID errors | `matrix_dim`, `use_dgemm`, `test_duration` |
| **memtest** | `MemTest_*.so` | Memory pattern testing | Memory errors, pattern failures | `test_duration`, `test_patterns` |
| **targeted_stress** | `TargetedStress_*.so` | Constant performance load | GFLOPs, thermal violations | `target_stress`, `use_dgemm` |
| **targeted_power** | `TargetedPower_*.so` | Power consumption testing | Watts, power violations | `target_power`, `starting_matrix_dim` |
| **pcie** | `pcie_*.so` | PCIe bandwidth and integrity | Bandwidth, AER errors, symbol errors | `min_pci_generation`, `min_pci_width` |
| **memory_bandwidth** | Memory bandwidth plugin | Streaming memory access | MB/s throughput | `minimum_bandwidth` |
| **eud** | `eud_*.so` | Extended Hardware diagnostics | Hardware-specific metrics | EUD version-specific |

### Diagnostic Test (GpuBurnPlugin) Details

The diagnostic test is the primary comprehensive validation test:

```mermaid
graph LR
    subgraph "GpuBurnPlugin Flow"
        INIT["Initialize<br/>Allocate GPU memory<br/>Setup CUDA context"]
        
        SELECT_OP["Select Operation<br/>use_dgemm: DGEMM<br/>else: HGEMM/SGEMM"]
        
        GEMM_LOOP["GEMM Loop<br/>Matrix multiplication<br/>C = A * B"]
        
        MONITOR["Monitoring<br/>Temperature<br/>Power<br/>Clocks<br/>XID errors<br/>Thermal violations"]
        
        VERIFY["Result Verification<br/>Check correctness<br/>Error detection"]
    end
    
    INIT --> SELECT_OP
    SELECT_OP --> GEMM_LOOP
    GEMM_LOOP --> MONITOR
    MONITOR --> VERIFY
    VERIFY -.->|"Continue"| GEMM_LOOP
```

**Matrix Dimensions:**
- Configurable via `matrix_dim` parameter in SKU config
- Typical values: 4096, 8192 for modern GPUs
- Affects memory usage and compute intensity

**Precision Selection:**
- `use_dgemm=true`: Double precision (FP64) operations
- `use_dgemm=false`: Single precision (FP32) or half precision (FP16)
- Choice affects performance characteristics and power consumption

**Error Detection:**
1. **XID Errors**: Monitored via DCGM field `DCGM_FI_DEV_XID_ERRORS`
2. **Thermal Violations**: Monitored via `DCGM_FI_DEV_THERMAL_VIOLATION`
3. **Clock Events**: Monitored via `DCGM_FI_DEV_CLOCKS_EVENT_REASONS`
4. **Temperature**: Monitored via `DCGM_FI_DEV_GPU_TEMP`

**Sources:** [nvvs/diag-skus.yaml.in:93-95](), [nvvs/diag-skus.yaml.in:168-170](), [testing/python3/tests/test_dcgm_diag.py:168-205]()

---

## Result Structures and Handling

NVVS returns comprehensive diagnostic results through structured response objects.

### Response Structure Hierarchy

```mermaid
graph TB
    subgraph "dcgmDiagResponse_v12"
        RESP_HDR["version: 0xC0000000C<br/>dcgmVersion<br/>driverVersion<br/>gpuCount"]
        
        ENTITIES["entities array<br/>dcgmDiagEntityResults_v1"]
        ENTITY_ITEM["entity: entityGroupId + entityId<br/>skuDeviceId<br/>status"]
        
        CATEGORIES["categories array<br/>Software, Hardware<br/>Integration, Stress"]
        
        TESTS["tests array<br/>dcgmDiagTestRun_v2"]
        TEST_ITEM["name<br/>categoryIndex<br/>result: PASS/FAIL/SKIP/WARN<br/>numResults<br/>resultIndices array<br/>numErrors<br/>errorIndices array<br/>numInfo<br/>infoIndices array<br/>auxData"]
        
        RESULTS["results array<br/>dcgmDiagEntityResult_v1"]
        RESULT_ITEM["entity: entityGroupId + entityId<br/>result: PASS/FAIL/SKIP/WARN"]
        
        ERRORS["errors array<br/>dcgmDiagError_v1"]
        ERROR_ITEM["entity<br/>testId<br/>code: DCGM_FR_*<br/>category<br/>severity<br/>msg"]
        
        INFO["info array<br/>dcgmDiagInfo_v1"]
        INFO_ITEM["entity<br/>testId<br/>msg"]
    end
    
    RESP_HDR --> ENTITIES
    ENTITIES --> ENTITY_ITEM
    
    RESP_HDR --> CATEGORIES
    
    RESP_HDR --> TESTS
    TESTS --> TEST_ITEM
    
    RESP_HDR --> RESULTS
    RESULTS --> RESULT_ITEM
    
    RESP_HDR --> ERRORS
    ERRORS --> ERROR_ITEM
    
    RESP_HDR --> INFO
    INFO --> INFO_ITEM
    
    TEST_ITEM -.->|"references"| RESULT_ITEM
    TEST_ITEM -.->|"references"| ERROR_ITEM
    TEST_ITEM -.->|"references"| INFO_ITEM
```

### Result Status Values

| Status Code | C Enum | Meaning | Usage |
|-------------|--------|---------|-------|
| **PASS** | `DCGM_DIAG_RESULT_PASS` | Test passed all validation checks | Normal successful completion |
| **FAIL** | `DCGM_DIAG_RESULT_FAIL` | Test failed validation checks | Errors detected, GPU may be unhealthy |
| **WARN** | `DCGM_DIAG_RESULT_WARN` | Test passed with warnings | Minor issues detected, not critical |
| **SKIP** | `DCGM_DIAG_RESULT_SKIP` | Test was skipped | Not applicable for this GPU or config |
| **NOT_RUN** | `DCGM_DIAG_RESULT_NOT_RUN` | Test was not executed | Test not included in run level |

### Error Code System

Errors are reported using DCGM error codes (`DCGM_FR_*`):

| Error Code | Constant | Category | Description |
|------------|----------|----------|-------------|
| **TEMP_VIOLATION** | `DCGM_FR_TEMP_VIOLATION` | Thermal | GPU temperature exceeded threshold |
| **XID_ERROR** | `DCGM_FR_XID_ERROR` | Hardware | Hardware XID error detected |
| **CLOCKS_THROTTLE** | (various) | Performance | GPU clocks throttled due to thermal/power |
| **NVLINK_ERROR** | `DCGM_FR_NVLINK_ERROR` | Interconnect | NVLink communication error |
| **NVLINK_EFFECTIVE_BER_THRESHOLD** | `DCGM_FR_NVLINK_EFFECTIVE_BER_THRESHOLD` | Interconnect | NVLink bit error rate exceeded |
| **MEMORY_ERROR** | (various) | Memory | Memory subsystem error |

### Result Processing

```mermaid
graph LR
    subgraph "Result Collection"
        PLUGIN_RESULT["Plugin generates<br/>test metrics"]
        NVVS_AGGREGATE["NVVS aggregates<br/>into response"]
        WRITE_FD3["Write to FD 3<br/>dcgmDiagResponse_v12"]
    end
    
    subgraph "DcgmDiagManager Parse"
        READ_RESPONSE["ReadDataFromFd<br/>DcgmDiagResponseWrapper"]
        VALIDATE["Validate response<br/>Check version<br/>Check structure"]
    end
    
    subgraph "Result Analysis"
        GET_FAILURE["GetFailureResult<br/>Check for ISOLATE errors<br/>Aggregate FAIL status"]
        PRIORITY["dcgmErrorGetPriorityByCode<br/>ISOLATE errors = critical"]
    end
    
    subgraph "Display Formatting"
        JSON_OUT["HelperDisplayAsJson<br/>JSON format output"]
        CLI_OUT["HelperDisplayAsCli<br/>Table format output"]
    end
    
    PLUGIN_RESULT --> NVVS_AGGREGATE
    NVVS_AGGREGATE --> WRITE_FD3
    
    WRITE_FD3 --> READ_RESPONSE
    READ_RESPONSE --> VALIDATE
    
    VALIDATE --> GET_FAILURE
    GET_FAILURE --> PRIORITY
    
    PRIORITY --> JSON_OUT
    PRIORITY --> CLI_OUT
```

**Sources:** [dcgmi/Diag.cpp:254-336](), [dcgmi/Diag.cpp:661-681](), [testing/python3/tests/test_dcgm_diag.py:60-90]()

---

## Process Management and Termination

NVVS can be stopped gracefully or forcefully depending on the situation.

### Signal Handling

```mermaid
graph TB
    subgraph "Termination Request"
        USER_STOP["User requests stop<br/>dcgmStopDiagnostic"]
        TIMEOUT["Diagnostic timeout"]
        SIGNAL["System signal<br/>SIGINT/SIGTERM"]
    end
    
    subgraph "DcgmDiagManager::KillActiveNvvs"
        CHECK_PID["Check m_nvvsPID<br/>Valid process?"]
        
        SIGTERM_LOOP["SIGTERM Loop<br/>Max 10 attempts<br/>4 second delays"]
        
        CHECK_STATUS["ChildProcessGetStatus<br/>still running?"]
        
        SIGKILL["SIGKILL<br/>Forced termination"]
        
        CLEANUP["ChildProcessDestroy<br/>Clean up handle"]
    end
    
    subgraph "NVVS Process"
        RECEIVE_SIGNAL["Receive SIGTERM"]
        CLEAN_SHUTDOWN["Clean shutdown<br/>Stop tests<br/>Write partial results"]
        FORCE_EXIT["Receive SIGKILL<br/>Immediate exit"]
    end
    
    USER_STOP --> CHECK_PID
    TIMEOUT --> CHECK_PID
    SIGNAL --> CHECK_PID
    
    CHECK_PID -->|"Valid"| SIGTERM_LOOP
    CHECK_PID -->|"Invalid"| CLEANUP
    
    SIGTERM_LOOP --> CHECK_STATUS
    CHECK_STATUS -->|"Still running"| SIGTERM_LOOP
    CHECK_STATUS -->|"Not running"| CLEANUP
    
    SIGTERM_LOOP -->|"10 attempts failed"| SIGKILL
    SIGKILL --> CHECK_STATUS
    
    SIGTERM_LOOP -.->|"Send signal"| RECEIVE_SIGNAL
    RECEIVE_SIGNAL --> CLEAN_SHUTDOWN
    
    SIGKILL -.->|"Send signal"| FORCE_EXIT
```

**Termination Strategy:**

1. **Graceful Termination (SIGTERM)**
   - Sent up to 10 times with 4-second intervals
   - Allows NVVS to complete current test iteration
   - Gives time for result writing and cleanup
   - Maximum wait time: 40 seconds

2. **Forced Termination (SIGKILL)**
   - Used after SIGTERM exhaustion
   - Immediate process termination
   - No cleanup opportunity for NVVS
   - Used as last resort

**EUD Test Consideration:**
The 40-second timeout is designed to accommodate the EUD test, which can take up to 20 seconds to stop gracefully. The extra time provides buffer for other overhead.

**Sources:** [modules/diag/DcgmDiagManager.cpp:122-250](), [modules/diag/DcgmDiagManager.cpp:1052-1071]()

---

## Environment Variables and Debugging

NVVS behavior can be modified through environment variables for debugging and testing.

### Environment Variables

| Variable | Purpose | Values | Location |
|----------|---------|--------|----------|
| `NVVS_BIN_PATH` | Override NVVS binary location | Directory path | DcgmDiagManager |
| `NVVS_PLUGIN_DIR` | Override plugin directory | Directory path | NVVS |
| `NVVS_HANGDETECT_DISABLE` | Disable hang detection | Set to any value | NVVS |
| `NVVS_HANGDETECT_EXPIRY_SEC` | Hang detection timeout | Seconds (unsigned int) | NVVS |
| `__DCGM_PCIE_AER_COUNT` | Inject PCIe AER errors (debug) | Error count | Test only |

### Binary Path Discovery

```mermaid
graph LR
    subgraph "GetNvvsBinPath Logic"
        DEFAULT["Default Path<br/>/usr/libexec/datacenter-gpu-manager-4/nvvs"]
        
        CHECK_ENV["Check NVVS_BIN_PATH<br/>environment variable"]
        
        BUILD_PATH["Build path<br/>$NVVS_BIN_PATH/nvvs"]
        
        FILE_EXISTS["access() F_OK<br/>Check file exists"]
        
        USE_CUSTOM["Use custom path"]
        USE_DEFAULT["Use default path"]
        WARN["Log warning<br/>Invalid path"]
    end
    
    CHECK_ENV -->|"Not set"| USE_DEFAULT
    CHECK_ENV -->|"Set"| BUILD_PATH
    
    BUILD_PATH --> FILE_EXISTS
    FILE_EXISTS -->|"Exists"| USE_CUSTOM
    FILE_EXISTS -->|"Not found"| WARN
    WARN --> USE_DEFAULT
    
    DEFAULT --> USE_DEFAULT
```

### Hang Detection

NVVS includes hang detection to prevent indefinite test hangs:

- **Default Behavior**: Enabled by default
- **Disable**: Set `NVVS_HANGDETECT_DISABLE` to any value
- **Custom Timeout**: Set `NVVS_HANGDETECT_EXPIRY_SEC` to desired seconds
- **Implementation**: Passed to NVVS via `--noHangDetect` or `--hangDetectExpirySec` arguments

**Sources:** [modules/diag/DcgmDiagManager.cpp:253-282](), [modules/diag/DcgmDiagManager.cpp:478-599]()

---

## Service Account Support

NVVS can be executed under a specific service account for security isolation.

### Service Account Workflow

```mermaid
graph TB
    subgraph "Service Account Configuration"
        GET_SA["GetServiceAccount<br/>Query from CoreProxy"]
        SA_PRESENT{"Service account<br/>configured?"}
        GET_CREDS["GetUserCredentials<br/>Resolve uid/gid/groups"]
    end
    
    subgraph "File Permission Adjustment"
        TEMP_CONFIG["Temporary config file<br/>/tmp/tmp-dcgm-XXXXXX"]
        CHOWN["chown(file, uid, gid)<br/>Set ownership"]
        VERIFY["Verify ownership<br/>Error handling"]
    end
    
    subgraph "Binary Access Validation"
        TRAVERSE_PATH["Traverse binary path<br/>/usr/libexec/datacenter-gpu-manager-4/nvvs"]
        CHECK_PERMS["Check each path component<br/>S_IRUSR | S_IXUSR<br/>S_IRGRP | S_IXGRP<br/>S_IROTH | S_IXOTH"]
        ACCESS_ERROR["Return error if<br/>insufficient permissions"]
    end
    
    subgraph "Process Spawn"
        SET_USER["dcgmChildProcessParams_v1<br/>userName field"]
        SPAWN["ChildProcessSpawn<br/>drops privileges"]
    end
    
    GET_SA --> SA_PRESENT
    SA_PRESENT -->|"Yes"| GET_CREDS
    SA_PRESENT -->|"No"| SPAWN
    
    GET_CREDS --> TEMP_CONFIG
    TEMP_CONFIG --> CHOWN
    CHOWN --> VERIFY
    
    GET_CREDS --> TRAVERSE_PATH
    TRAVERSE_PATH --> CHECK_PERMS
    CHECK_PERMS -->|"Pass"| SET_USER
    CHECK_PERMS -->|"Fail"| ACCESS_ERROR
    
    VERIFY --> SET_USER
    SET_USER --> SPAWN
```

**Permission Validation:**

For each component of the NVVS binary path, the system checks:

1. **User Permissions**: `st_uid == service_uid && (st_mode & S_IRUSR) && (st_mode & S_IXUSR)`
2. **Group Permissions**: `st_gid in groups && (st_mode & S_IRGRP) && (st_mode & S_IXGRP)`
3. **Other Permissions**: `(st_mode & S_IROTH) && (st_mode & S_IXOTH)`

If any component fails all three checks, the diagnostic returns `DCGM_ST_GENERIC_ERROR`.

**Sources:** [modules/diag/DcgmDiagManager.cpp:54-72](), [modules/diag/DcgmDiagManager.cpp:420-457](), [modules/diag/DcgmDiagManager.cpp:799-858](), [modules/diag/DcgmDiagManager.cpp:860-868]()

---

## Iterative Diagnostics

NVVS supports running multiple iterations of diagnostics for extended validation.

### Iteration Control

```mermaid
graph LR
    subgraph "dcgmRunDiag_v10"
        TOTAL["totalIterations<br/>Number of runs"]
        CURRENT["currentIteration<br/>0-based index"]
    end
    
    subgraph "Diag::RunStartDiag"
        CHECK_ITER{"totalIterations<br/>> 1?"}
        SINGLE["RunDiagOnce<br/>Single execution"]
        LOOP["Iteration loop<br/>i = 0 to totalIterations"]
    end
    
    subgraph "Per-Iteration"
        SET_INDEX["m_drd.currentIteration = i"]
        RUN["RunDiagOnce"]
        COLLECT["Collect results<br/>output[NVVS_ITERATIONS][i]"]
        CHECK_FAIL{"Result == OK?"}
        BREAK["Break loop<br/>Set overall failure"]
    end
    
    TOTAL --> CHECK_ITER
    CHECK_ITER -->|"No"| SINGLE
    CHECK_ITER -->|"Yes"| LOOP
    
    LOOP --> SET_INDEX
    SET_INDEX --> RUN
    RUN --> COLLECT
    COLLECT --> CHECK_FAIL
    
    CHECK_FAIL -->|"No"| BREAK
    CHECK_FAIL -->|"Yes"| LOOP
```

**Iteration Parameters:**

The iteration information is passed to NVVS via command-line arguments:

```
--current-iteration <index>
--total-iterations <count>
```

**Failure Handling:**

- **Early Termination**: If any iteration fails, subsequent iterations are skipped
- **Result Aggregation**: All iteration results are stored in JSON output
- **Overall Status**: `DCGM_ST_OK` only if all iterations pass

**Use Cases:**
- Extended burn-in testing
- Intermittent issue detection  
- Stress testing under varying conditions
- Long-running validation

**Sources:** [modules/diag/DcgmDiagManager.cpp:558-564](), [dcgmi/Diag.cpp:577-633]()

---

## Integration with DCGM API

NVVS is invoked through the DCGM API using the `dcgmActionValidate_v2` function.

### API Call Flow

```mermaid
graph TB
    subgraph "Client Application"
        APP["Application Code<br/>dcgmi/pydcgm/custom"]
        SETUP_DRD["Setup dcgmRunDiag_v10<br/>Configure test parameters"]
        ALLOC_RESP["Allocate dcgmDiagResponse_v12"]
    end
    
    subgraph "DCGM API Layer dcgmlib"
        API_ENTRY["dcgmActionValidate_v2<br/>Entry point"]
        MODULE_CMD["dcgm_diag_msg_run_diag_v3<br/>Module command structure"]
        SEND_CMD["dcgmModuleSendBlockingFixedRequest<br/>or processModuleCommand"]
    end
    
    subgraph "Host Engine Core"
        ROUTER["Module Router<br/>Route to Diag Module"]
        DIAG_MODULE["Diag Module<br/>DCGM_DIAG_SR_RUN_DIAG"]
    end
    
    subgraph "Diag Module Processing"
        DIAG_MGR["DcgmDiagManager<br/>PerformNVVSExecute"]
        NVVS_PROC["NVVS Process<br/>Test execution"]
        READ_RESULTS["Read results from FD 3"]
    end
    
    APP --> SETUP_DRD
    SETUP_DRD --> ALLOC_RESP
    ALLOC_RESP --> API_ENTRY
    
    API_ENTRY --> MODULE_CMD
    MODULE_CMD --> SEND_CMD
    
    SEND_CMD --> ROUTER
    ROUTER --> DIAG_MODULE
    
    DIAG_MODULE --> DIAG_MGR
    DIAG_MGR --> NVVS_PROC
    NVVS_PROC --> READ_RESULTS
    
    READ_RESULTS --> MODULE_CMD
    MODULE_CMD --> API_ENTRY
    API_ENTRY --> APP
```

### dcgmRunDiag_v10 Structure

Key fields in the diagnostic request structure:

| Field | Type | Purpose |
|-------|------|---------|
| `version` | uint | Structure version (`dcgmRunDiag_version10`) |
| `groupId` | dcgmGpuGrp_t | Group to test, or `DCGM_GROUP_NULL` if using entityIds |
| `entityIds` | char[1024] | Comma-separated entity list (e.g., "gpu:0,gpu:1" or "0,1") |
| `fakeGpuList` | char[256] | List of fake GPU IDs for testing |
| `validate` | uint | Test level: `DCGM_POLICY_VALID_SV_SHORT/MED/LONG/XLONG` |
| `testNames` | char[DCGM_MAX_TEST_NAMES][MAX_TEST_NAME_LEN] | Specific tests to run |
| `testParms` | char[DCGM_MAX_TEST_PARMS][MAX_TEST_PARMS_LEN] | Test parameters (semicolon-separated) |
| `configFileContents` | char[64KB] | Custom configuration file content |
| `debugLogFile` | char[256] | Path for debug log output |
| `statsPath` | char[256] | Path for statistics output |
| `debugLevel` | uint | Logging level |
| `clocksEventMask` | char[256] | Clocks events to ignore |
| `flags` | uint | `DCGM_RUN_FLAGS_VERBOSE`, `DCGM_RUN_FLAGS_STATSONFAIL`, `DCGM_RUN_FLAGS_FAIL_EARLY` |
| `failCheckInterval` | uint | Interval for fail-early checks (seconds) |
| `totalIterations` | uint | Number of iterations to run |
| `currentIteration` | uint | Current iteration index |
| `watchFrequency` | uint | DCGM field watch frequency (microseconds) |
| `ignoreErrorCodes` | char[256] | Error codes to ignore |

**Test Name Examples:**
- `"diagnostic"` - GpuBurn GEMM test
- `"memtest"` - Memory pattern test
- `"pcie"` - PCIe bandwidth test
- `"1"` (short), `"2"` (medium), `"3"` (long), `"4"` (xlong) - Predefined test suites

**Test Parameter Format:**
```
"diagnostic.test_duration=10;diagnostic.matrix_dim=8192;memtest.test_duration=15"
```

**Sources:** [dcgmlib/src/DcgmApi.cpp:1-50](), [testing/python3/tests/test_dcgm_diag.py:91-107]()

---

## Error Handling and Recovery

NVVS and the Diag Module implement comprehensive error handling to ensure robust operation.

### Error Scenarios

| Error Condition | Detection | Recovery Action | Return Code |
|----------------|-----------|-----------------|-------------|
| NVVS binary not found | `stat()` failure on binary path | Return immediately, no spawn | `DCGM_ST_NVVS_BINARY_NOT_FOUND` |
| NVVS process crash | Exit code ≠ 0 with signal received | Log error, parse partial results | `DCGM_ST_NVVS_KILLED` |
| NVVS timeout | External timeout detection | Call `dcgmStopDiagnostic()` | `DCGM_ST_TIMEOUT` |
| Test not available | NVVS exit code `NVVS_ST_TEST_NOT_FOUND` | Return specific error | `DCGM_ST_NVVS_NO_AVAILABLE_TEST` |
| Empty group | Group has no entities | Immediate error return | `DCGM_ST_GROUP_IS_EMPTY` |
| Group incompatible | Mixed GPU SKUs | Pre-execution validation | `DCGM_ST_GROUP_INCOMPATIBLE` |
| DCGM paused | Host engine in paused state | Cannot run diagnostic | `DCGM_ST_PAUSED` |
| Insufficient permissions | Service account cannot access binary | Permission check failure | `DCGM_ST_GENERIC_ERROR` |
| Config file creation failure | `mkstemp()` failure | Retry up to 3 times | `DCGM_ST_GENERIC_ERROR` |
| Child process spawn failure | `ChildProcessSpawn()` error | Cleanup and return | `DCGM_ST_DIAG_BAD_LAUNCH` |
| Cannot kill NVVS | `KillActiveNvvs()` exhausts retries | Log error, may leave zombie | `DCGM_ST_CHILD_NOT_KILLED` |

### Response Error Codes

System-level errors are reported in the `errors` array with `testId = DCGM_DIAG_RESPONSE_SYSTEM_ERROR`:

```mermaid
graph LR
    subgraph "Error Priority Levels"
        ISOLATE["ISOLATE Errors<br/>Critical hardware issues<br/>Immediate attention required"]
        
        ERROR["ERROR Level<br/>Test failures<br/>Reportable issues"]
        
        WARN["WARN Level<br/>Minor issues<br/>May not affect functionality"]
    end
    
    subgraph "Error Aggregation"
        SCAN["Scan all errors in response"]
        CHECK_PRIO["dcgmErrorGetPriorityByCode"]
        PRIORITY{"Priority?"}
        SET_ISOLATE["Return DCGM_ST_NVVS_ISOLATE_ERROR"]
        SET_ERROR["Return DCGM_ST_NVVS_ERROR"]
        SET_OK["Return DCGM_ST_OK"]
    end
    
    ISOLATE --> SCAN
    ERROR --> SCAN
    WARN --> SCAN
    
    SCAN --> CHECK_PRIO
    CHECK_PRIO --> PRIORITY
    
    PRIORITY -->|"ISOLATE"| SET_ISOLATE
    PRIORITY -->|"ERROR"| SET_ERROR
    PRIORITY -->|"None"| SET_OK
```

**Error Priority Determination:**

The `GetFailureResult()` function determines overall diagnostic status:

1. Scan all errors associated with GPU entities and software tests
2. For each error, call `dcgmErrorGetPriorityByCode(error.code)`
3. If any error has `DCGM_ERROR_ISOLATE` priority, immediately return `DCGM_ST_NVVS_ISOLATE_ERROR`
4. If any errors exist but none are ISOLATE, return `DCGM_ST_NVVS_ERROR`
5. If no errors, return `DCGM_ST_OK`

**Sources:** [modules/diag/DcgmDiagManager.cpp:783-796](), [modules/diag/DcgmDiagManager.cpp:998-1030](), [dcgmi/Diag.cpp:254-336](), [dcgmi/Diag.cpp:374-519]()

---

## Diagnostic Status Updates

During long-running diagnostics, NVVS provides periodic status updates to track progress.

### Status Update Mechanism

```mermaid
graph TB
    subgraph "NVVS Test Execution"
        TEST_START["Test plugin starts"]
        PERIODIC["Periodic status generation<br/>During long tests"]
        TEST_END["Test plugin completes"]
    end
    
    subgraph "dcgmDiagStatus_v1"
        STATUS_STRUCT["version<br/>totalTests<br/>completedTests<br/>testName[128]<br/>errorCode"]
    end
    
    subgraph "DcgmDiagManager Reception"
        READ_STATUS["ReadDataFromFd<br/>Detect dcgmDiagStatus_v1"]
        PARSE_STATUS["UpdateDiagStatus<br/>Parse structure"]
        PRINT_STATUS["PrintDiagStatus<br/>Log to debug"]
    end
    
    subgraph "Cache Manager Integration"
        MAP_FIELD["m_testNameResultFieldId<br/>Map test name to field ID"]
        BUILD_FV["Build DcgmFvBuffer<br/>Add DCGM_FI_DEV_DIAG_STATUS blob<br/>Add test result field"]
        APPEND["AppendSamples<br/>Write to cache"]
    end
    
    subgraph "Field Updates"
        DIAG_STATUS_FIELD["DCGM_FI_DEV_DIAG_STATUS<br/>Blob field"]
        TEST_RESULT_FIELDS["Test-specific result fields<br/>Mapped from test name"]
    end
    
    TEST_START --> PERIODIC
    PERIODIC --> STATUS_STRUCT
    TEST_END --> STATUS_STRUCT
    
    STATUS_STRUCT --> READ_STATUS
    READ_STATUS --> PARSE_STATUS
    PARSE_STATUS --> PRINT_STATUS
    
    PARSE_STATUS --> MAP_FIELD
    MAP_FIELD --> BUILD_FV
    BUILD_FV --> APPEND
    
    APPEND --> DIAG_STATUS_FIELD
    APPEND --> TEST_RESULT_FIELDS
```

**Status Structure Contents:**

```c
typedef struct {
    unsigned int version;        // dcgmDiagStatus_version
    unsigned int totalTests;     // Total number of tests to run
    unsigned int completedTests; // Number completed so far
    char testName[128];         // Current test name
    unsigned int errorCode;      // Current error code (0 = no error)
} dcgmDiagStatus_v1;
```

**Update Frequency:**
- Updates are written periodically during test execution
- Frequency depends on test implementation
- Typical interval: every few seconds for long tests

**Field Mapping:**
The `m_testNameResultFieldId` map associates test names with DCGM field IDs for result tracking. This allows monitoring systems to watch diagnostic progress via standard DCGM field queries.

**Sources:** [modules/diag/DcgmDiagManager.cpp:715-757](), [modules/diag/DcgmDiagManager.cpp:724-757]()

---

This comprehensive documentation covers NVVS's architecture, process model, communication protocols, test types, configuration system, and integration with DCGM. The system's isolation model ensures that diagnostic failures cannot affect core monitoring, while the rich communication protocol provides detailed test results and progress updates.

---

