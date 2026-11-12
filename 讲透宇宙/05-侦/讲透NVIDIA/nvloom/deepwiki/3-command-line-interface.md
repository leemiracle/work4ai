<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvloom · page 3 Command Line Interface · fetched 2026-10-26 -->

# Command Line Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [cli/nvloom_cli.cpp](cli/nvloom_cli.cpp)
- [cli/util.cpp](cli/util.cpp)
- [cli/util.h](cli/util.h)

</details>



The `nvloom_cli` application provides a comprehensive command-line interface for executing Multi-Node NVLink (MNNVL) fabric benchmarks. This document covers the CLI application's architecture, command-line options, test execution patterns, and integration with the nvloom core library.

For information about the underlying benchmarking engine, see [Core Library](#4). For visualization of benchmark results, see [Visualization Tools](#6). For details about specific test patterns and suites, see [Testing Framework](#5).

## CLI Application Architecture

The `nvloom_cli` application is built around a modular architecture that handles command-line parsing, test discovery, and benchmark execution coordination.

```mermaid
graph TB
    subgraph "CLI Entry Point"
        MAIN["main()"]
        RUN_PROGRAM["run_program()"]
    end
    
    subgraph "Command Line Processing"
        BOOST_OPTIONS["boost::program_options"]
        VARIABLES_MAP["variables_map"]
        HELP_HANDLER["Help & List Options"]
    end
    
    subgraph "Test Management"
        BUILD_TESTCASES["buildTestcases()"]
        TESTCASES_MAP["testcases map"]
        SUITES_MAP["suites map"]
        FILTER_RUN["filterRun()"]
    end
    
    subgraph "System Discovery"
        DISCOVER_RANKS["discoverRanks()"]
        RACK_MAP["rackToProcessMap"]
        NVLOOM_INIT["NvLoom::initialize()"]
    end
    
    subgraph "Execution Control"
        SHOULD_CONTINUE["shouldContinue()"]
        REPEAT_LOGIC["Repeat/Duration Logic"]
        CLEAR_POOLS["clearAllocationPools()"]
    end
    
    subgraph "Output System"
        OUTPUT_MATRIX["OutputMatrix"]
        RICH_OUTPUT["richOutput flag"]
        EXECUTION_TIMING["ExecutionTime reporting"]
    end
    
    MAIN --> RUN_PROGRAM
    RUN_PROGRAM --> BOOST_OPTIONS
    BOOST_OPTIONS --> VARIABLES_MAP
    VARIABLES_MAP --> HELP_HANDLER
    
    RUN_PROGRAM --> BUILD_TESTCASES
    BUILD_TESTCASES --> TESTCASES_MAP
    BUILD_TESTCASES --> SUITES_MAP
    
    RUN_PROGRAM --> DISCOVER_RANKS
    DISCOVER_RANKS --> RACK_MAP
    RACK_MAP --> NVLOOM_INIT
    
    TESTCASES_MAP --> FILTER_RUN
    FILTER_RUN --> SHOULD_CONTINUE
    SHOULD_CONTINUE --> REPEAT_LOGIC
    REPEAT_LOGIC --> CLEAR_POOLS
    
    FILTER_RUN --> OUTPUT_MATRIX
    OUTPUT_MATRIX --> RICH_OUTPUT
    OUTPUT_MATRIX --> EXECUTION_TIMING
```

Sources: [cli/nvloom_cli.cpp:54-207](), [cli/util.cpp:59-118](), [cli/util.h:34-137]()

## Command Line Options

The CLI supports a comprehensive set of options for controlling test execution, memory allocation strategies, and output formatting.

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--help` | `-h` | flag | - | Display help message |
| `--listTestcases` | `-l` | flag | false | List all available testcases |
| `--testcase` | `-t` | string[] | all | Specific testcase(s) to run |
| `--suite` | `-s` | string[] | all | Test suite(s) to run |
| `--bufferSize` | `-b` | int | 512 | Buffer size in MiB |
| `--allocatorStrategy` | `-a` | string | "reuse" | Memory allocation strategy |
| `--richOutput` | `-r` | flag | false | Show detailed per-measurement data |
| `--gpuToRackSamples` | - | int | 5 | Samples per rack in gpu-to-rack suite |
| `--iterations` | `-i` | int | 16 | Copy iterations per measurement |
| `--repeat` | `-c` | int | 1 | Times to repeat each testcase |
| `--duration` | `-d` | int | -1 | Duration in seconds to repeat testcases |

### Memory Allocation Strategies

The `--allocatorStrategy` option controls how CUDA memory allocations are handled:

- **`unique`**: Fresh allocation/deallocation for each measurement
- **`reuse`**: Pool-based caching via `AllocationPool` class  
- **`cudapool`**: CUDA Stream-Ordered Memory Allocator for device/EGM memory

### Test Suites

The CLI organizes tests into logical suites accessible via `--suite`:

- **`pairwise`**: O(n²) all-pairs testing between GPUs
- **`fabric-stress`**: Simultaneous copies from every GPU
- **`gpu-to-rack`**: Linear-time sampling across racks
- **`rack-to-rack`**: Inter-rack communication patterns
- **`all-to-one`**: Multiple GPUs accessing single GPU memory
- **`multicast`**: One-to-many broadcast patterns
- **`egm`**: Extended GPU Memory (CPU RAM) testing

Sources: [cli/nvloom_cli.cpp:65-78](), [README.md:51-58](), [README.md:143-151]()

## Test Execution Flow

The CLI follows a structured execution pattern that coordinates test discovery, system initialization, and benchmark execution.

```mermaid
graph TD
    subgraph "Initialization Phase"
        PARSE_ARGS["Parse Arguments"]
        VALIDATE_OPTIONS["Validate Options"]
        BUILD_TC["buildTestcases(allocatorStrategy)"]
        DISCOVER["discoverRanks(rackToProcessMap)"]
        NVLOOM_INIT["NvLoom::initialize(localDevice, rackToProcessMap)"]
    end
    
    subgraph "Test Selection"
        LIST_CHECK{"`--listTestcases?`"}
        SUITE_SELECTION["Process --suite options"]
        TC_SELECTION["Process --testcase options"]
        DEFAULT_ALL["Default: all testcases"]
        FINAL_SET["testcasesToRunSet"]
    end
    
    subgraph "Execution Loop"
        TC_ITERATOR["for testcase in testcasesToRunSet"]
        REPEAT_LOOP["Repeat/Duration Loop"]
        START_TIME["Record startTime"]
        FILTER_RUN_CALL["testcases[testcase]->filterRun(bufferSizeInB)"]
        END_TIME["Record endTime"]
        SHOULD_CONT{"`shouldContinue()?`"}
        CLEAR_POOLS_CALL["clearAllocationPools()"]
        EXECUTION_OUTPUT["Output ExecutionTime"]
    end
    
    subgraph "Cleanup"
        NVLOOM_FIN["NvLoom::finalize()"]
        EXIT["Return exit code"]
    end
    
    PARSE_ARGS --> VALIDATE_OPTIONS
    VALIDATE_OPTIONS --> BUILD_TC
    BUILD_TC --> DISCOVER
    DISCOVER --> NVLOOM_INIT
    
    NVLOOM_INIT --> LIST_CHECK
    LIST_CHECK -->|Yes| EXIT
    LIST_CHECK -->|No| SUITE_SELECTION
    SUITE_SELECTION --> TC_SELECTION
    TC_SELECTION --> DEFAULT_ALL
    DEFAULT_ALL --> FINAL_SET
    
    FINAL_SET --> TC_ITERATOR
    TC_ITERATOR --> REPEAT_LOOP
    REPEAT_LOOP --> START_TIME
    START_TIME --> FILTER_RUN_CALL
    FILTER_RUN_CALL --> END_TIME
    END_TIME --> SHOULD_CONT
    SHOULD_CONT -->|Yes| REPEAT_LOOP
    SHOULD_CONT -->|No| CLEAR_POOLS_CALL
    CLEAR_POOLS_CALL --> EXECUTION_OUTPUT
    EXECUTION_OUTPUT --> TC_ITERATOR
    
    TC_ITERATOR --> NVLOOM_FIN
    NVLOOM_FIN --> EXIT
```

Sources: [cli/nvloom_cli.cpp:125-196](), [cli/nvloom_cli.cpp:36-52]()

## System Discovery and Initialization

The CLI performs comprehensive system discovery to map processes to GPUs and rack topology before benchmark execution.

### GPU and Rack Discovery Process

```mermaid
graph LR
    subgraph "Host Information"
        HOSTNAME["gethostname()"]
        DEVICE_COUNT["cuDeviceGetCount()"]
        LOCAL_RANK["Calculate localRank"]
        LOCAL_DEVICE["localDevice = localRank % deviceCount"]
    end
    
    subgraph "MPI Communication"
        HOSTNAME_EXCHANGE["MPI_Allgather hostnames"]
        RACK_GUID["getRackGuid(localDevice)"]
        GUID_EXCHANGE["MPI_Allgather rackGuids"]
        DEVICE_INFO["getDeviceDisplayInfo()"]
        DEVICE_EXCHANGE["MPI_Allgather device info"]
    end
    
    subgraph "Topology Mapping"
        RACK_MAP["rackToProcessMap"]
        TRIM_GUID["trimRackGuid()"]
        PROCESS_OUTPUT["Process mapping output"]
    end
    
    HOSTNAME --> HOSTNAME_EXCHANGE
    DEVICE_COUNT --> LOCAL_RANK
    LOCAL_RANK --> LOCAL_DEVICE
    LOCAL_DEVICE --> RACK_GUID
    
    HOSTNAME_EXCHANGE --> GUID_EXCHANGE
    RACK_GUID --> GUID_EXCHANGE
    LOCAL_DEVICE --> DEVICE_INFO
    DEVICE_INFO --> DEVICE_EXCHANGE
    
    GUID_EXCHANGE --> TRIM_GUID
    TRIM_GUID --> RACK_MAP
    DEVICE_EXCHANGE --> PROCESS_OUTPUT
    RACK_MAP --> PROCESS_OUTPUT
```

The discovery process outputs detailed topology information:
```
Process  0 (hostname1): device 0: NVIDIA H100 80GB HBM3 (00001234:85:00.0); rackGuid: ABC123
Process  1 (hostname1): device 1: NVIDIA H100 80GB HBM3 (00001234:86:00.0); rackGuid: ABC123
```

Sources: [cli/util.cpp:59-118](), [cli/util.cpp:39-57]()

## Output System and Result Formatting

The CLI provides flexible output formatting through the `OutputMatrix` class and configurable verbosity levels.

### OutputMatrix Structure

The `OutputMatrix` class handles incremental printing and statistical aggregation:

```mermaid
graph TB
    subgraph "OutputMatrix Components"
        DATA_STORAGE["data vector<double>"]
        LABELS_XY["labelsX, labelsY vectors"]
        NOTES["notes vector"]
        SEPARATORS["columnSeparators"]
        BUFFERING["Buffering mode"]
    end
    
    subgraph "Output Methods"
        SET_METHOD["set(x, y, value, note)"]
        INCREMENTAL["incrementalPrint(stage)"]
        DESTRUCTOR["~OutputMatrix() statistics"]
    end
    
    subgraph "Statistics Output"
        MIN_BW["MinBW calculation"]
        AVG_BW["AvgBW calculation"]
        MAX_BW["MaxBW calculation"]
        TOTAL_BW["TotalBW calculation"]
    end
    
    DATA_STORAGE --> SET_METHOD
    LABELS_XY --> INCREMENTAL
    NOTES --> INCREMENTAL
    SEPARATORS --> INCREMENTAL
    BUFFERING --> INCREMENTAL
    
    SET_METHOD --> INCREMENTAL
    INCREMENTAL --> DESTRUCTOR
    DESTRUCTOR --> MIN_BW
    DESTRUCTOR --> AVG_BW
    DESTRUCTOR --> MAX_BW
    DESTRUCTOR --> TOTAL_BW
```

### Rich Output Mode

When `--richOutput` is enabled, the CLI displays detailed per-measurement data instead of aggregated statistics. This is particularly useful for `gpu-to-rack` suite analysis where individual sample measurements are shown with specific GPU pair labels.

Sources: [cli/util.h:34-137](), [cli/util.cpp:120-157](), [README.md:162-168]()

## Integration with Core Library

The CLI serves as a wrapper around the nvloom core library, providing a user-friendly interface to the underlying benchmarking capabilities.

### Library Integration Points

```mermaid
graph LR
    subgraph "CLI Layer"
        CLI_MAIN["nvloom_cli main()"]
        OPTIONS_PARSING["Command line parsing"]
        TEST_SELECTION["Test selection logic"]
    end
    
    subgraph "Interface Layer"
        BUILD_TESTCASES_FUNC["buildTestcases()"]
        TESTCASE_BASE["Testcase base class"]
        FILTER_RUN_METHOD["filterRun() method"]
    end
    
    subgraph "Core Library"
        NVLOOM_CLASS["NvLoom class"]
        NVLOOM_INIT_METHOD["initialize()"]
        NVLOOM_BENCHMARK["doBenchmark()"]
        NVLOOM_FINALIZE["finalize()"]
    end
    
    subgraph "Memory Management"
        ALLOC_STRATEGY["AllocatorStrategy enum"]
        CLEAR_POOLS_FUNC["clearAllocationPools()"]
        ALLOCATION_POOLS["AllocationPool instances"]
    end
    
    CLI_MAIN --> OPTIONS_PARSING
    OPTIONS_PARSING --> TEST_SELECTION
    TEST_SELECTION --> BUILD_TESTCASES_FUNC
    
    BUILD_TESTCASES_FUNC --> TESTCASE_BASE
    TESTCASE_BASE --> FILTER_RUN_METHOD
    FILTER_RUN_METHOD --> NVLOOM_BENCHMARK
    
    CLI_MAIN --> NVLOOM_INIT_METHOD
    NVLOOM_INIT_METHOD --> NVLOOM_CLASS
    NVLOOM_CLASS --> NVLOOM_BENCHMARK
    NVLOOM_BENCHMARK --> NVLOOM_FINALIZE
    
    OPTIONS_PARSING --> ALLOC_STRATEGY
    ALLOC_STRATEGY --> ALLOCATION_POOLS
    ALLOCATION_POOLS --> CLEAR_POOLS_FUNC
```

The CLI handles the complete lifecycle:
1. **Initialization**: Calls `NvLoom::initialize()` with discovered topology
2. **Test Execution**: Invokes `filterRun()` on selected testcases
3. **Memory Management**: Manages allocation pools based on strategy
4. **Cleanup**: Calls `clearAllocationPools()` and `NvLoom::finalize()`

Sources: [cli/nvloom_cli.cpp:18-20](), [cli/nvloom_cli.cpp:137](), [cli/nvloom_cli.cpp:176](), [cli/nvloom_cli.cpp:183](), [cli/nvloom_cli.cpp:205]()

---

