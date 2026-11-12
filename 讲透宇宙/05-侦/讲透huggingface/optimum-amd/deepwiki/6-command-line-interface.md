<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-amd · page 6 Command Line Interface · fetched 2026-10-26 -->

# Command Line Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/test_zentorch_plugin.yaml](.github/workflows/test_zentorch_plugin.yaml)
- [docker/transformers-pytorch-amd-cpu-zentorch/Dockerfile](docker/transformers-pytorch-amd-cpu-zentorch/Dockerfile)
- [optimum/amd/cli.py](optimum/amd/cli.py)
- [optimum/amd/topology_utils.py](optimum/amd/topology_utils.py)
- [setup.py](setup.py)
- [tests/zentorch/test_sanity.py](tests/zentorch/test_sanity.py)
- [tests/zentorch/testing_utils.py](tests/zentorch/testing_utils.py)

</details>



The optimum-amd command line interface provides the `amdrun` CLI tool for automatically optimizing environment variables and hardware configurations when running Python scripts on AMD hardware. The CLI detects available AMD hardware (ROCm GPUs, ZenTorch CPUs) and sets appropriate environment variables to maximize performance without requiring manual configuration.

For hardware-specific optimization details, see [ROCm GPU Support](#4) and [ZenTorch CPU Optimization](#5). For programmatic model optimization, see [RyzenAI System](#2).

## CLI Entry Point and Registration

The `amdrun` command is registered as a console script entry point in the package setup and provides a wrapper around script execution with optimized environment variables.

```mermaid
flowchart TD
    Setup["setup.py entry_points"] --> ConsoleScript["amdrun console script"]
    ConsoleScript --> CLIModule["optimum.amd.cli.amdrun()"]
    CLIModule --> HardwareDetection["Hardware Detection"]
    CLIModule --> EnvOptimization["Environment Optimization"]
    CLIModule --> ScriptExecution["Script Execution"]
    
    HardwareDetection --> ROCmCheck["rocm-smi availability"]
    HardwareDetection --> ZenTorchCheck["zentorch import check"]
    
    EnvOptimization --> ROCmEnv["get_amd_rocm_env()"]
    EnvOptimization --> ZenTorchEnv["get_amd_zentorch_env()"]
    
    ScriptExecution --> SubprocessRun["subprocess.run(sys.argv[1:])"]
```

**Sources:** [setup.py:80](), [optimum/amd/cli.py:126-143]()

## Hardware Detection and Availability

The CLI automatically detects available AMD hardware components through runtime checks, setting global flags that determine which optimizations to apply.

```mermaid
flowchart TD
    CLIStart["amdrun command execution"] --> ROCmDetection["ROCm Detection"]
    CLIStart --> ZenTorchDetection["ZenTorch Detection"]
    
    ROCmDetection --> ROCmSMI["subprocess.run(['rocm-smi'])"]
    ROCmSMI --> ROCmSuccess["ROCM_AVAILABLE = True"]
    ROCmSMI --> ROCmFail["ROCM_AVAILABLE = False"]
    
    ZenTorchDetection --> ZenTorchImport["import zentorch"]
    ZenTorchImport --> ZenTorchSuccess["ZENTORCH_AVAILABLE = True"]
    ZenTorchImport --> ZenTorchFail["ZENTORCH_AVAILABLE = False"]
    
    ROCmSuccess --> ApplyROCmEnv["Apply ROCm environment variables"]
    ZenTorchSuccess --> ApplyZenTorchEnv["Apply ZenTorch environment variables"]
```

**Sources:** [optimum/amd/cli.py:9-21](), [optimum/amd/cli.py:135-139]()

## ZenTorch CPU Environment Optimization

When ZenTorch is available, the CLI configures OpenMP, memory allocation, and AMD-specific optimization settings for CPU performance.

| Environment Variable | Purpose | Default Value |
|---------------------|---------|---------------|
| `OMP_NUM_THREADS` | OpenMP thread count | `{CPU_COUNT}` |
| `OMP_DYNAMIC` | Dynamic thread allocation | `"False"` |
| `OMP_WAIT_POLICY` | OpenMP wait strategy | `"ACTIVE"` |
| `ZENDNN_GEMM_ALGO` | GEMM algorithm selection | `"4"` |
| `GOMP_CPU_AFFINITY` | CPU core affinity | `"0-{CPU_COUNT-1}"` |
| `LD_PRELOAD` | Jemalloc library preload | `"/usr/lib/x86_64-linux-gnu/libjemalloc.so"` |
| `MALLOC_CONF` | Jemalloc configuration | Complex configuration string |

```mermaid
flowchart TD
    GetZenTorchEnv["get_amd_zentorch_env()"] --> CPUCount["os.cpu_count()"]
    GetZenTorchEnv --> OMPSettings["OpenMP Configuration"]
    GetZenTorchEnv --> MemorySettings["Memory Allocation Settings"]
    GetZenTorchEnv --> AMDSettings["AMD-specific Settings"]
    
    OMPSettings --> OMPThreads["OMP_NUM_THREADS = CPU_COUNT"]
    OMPSettings --> OMPDynamic["OMP_DYNAMIC = False"]
    OMPSettings --> OMPWait["OMP_WAIT_POLICY = ACTIVE"]
    OMPSettings --> GOMPAffinity["GOMP_CPU_AFFINITY = 0-{CPU_COUNT-1}"]
    
    MemorySettings --> LDPreload["LD_PRELOAD = libjemalloc.so"]
    MemorySettings --> MallocConf["MALLOC_CONF = optimization_string"]
    
    AMDSettings --> ZenDNNAlgo["ZENDNN_GEMM_ALGO = 4"]
    
    LDPreload --> JemallocCheck["os.path.exists() validation"]
    JemallocCheck --> JemallocWarning["Warning if not found"]
```

**Sources:** [optimum/amd/cli.py:39-88]()

## ROCm GPU Environment Optimization

For ROCm GPU scenarios, the CLI automatically selects optimal GPU devices based on inter-device bandwidth topology to maximize distributed training performance.

```mermaid
flowchart TD
    GetROCmEnv["get_amd_rocm_env()"] --> ParseArgs["Parse sys.argv for device count"]
    ParseArgs --> TorchrunStyle["--nproc_per_node argument"]
    ParseArgs --> DeepSpeedStyle["--ngpus argument"]
    ParseArgs --> EarlyExit["Early exit if no device count found"]
    
    TorchrunStyle --> ExtractDeviceCount["Extract num_devices"]
    DeepSpeedStyle --> ExtractDeviceCount
    
    ExtractDeviceCount --> GetBandwidthMatrix["get_bandwidth_matrix()"]
    GetBandwidthMatrix --> ExtractCluster["extract_max_avg_bandwidth_cluster()"]
    ExtractCluster --> SetROCRVisible["ROCR_VISIBLE_DEVICES = device_list"]
    
    GetBandwidthMatrix --> AMDSMIInit["amdsmi.amdsmi_init()"]
    AMDSMIInit --> GetDeviceHandles["amdsmi.amdsmi_get_device_handles()"]
    GetDeviceHandles --> BandwidthMatrix["Build bandwidth matrix"]
    BandwidthMatrix --> AMDSMIShutdown["amdsmi.amdsmi_shut_down()"]
```

**Sources:** [optimum/amd/cli.py:91-123](), [optimum/amd/topology_utils.py:7-52]()

## Bandwidth Matrix and GPU Topology

The topology optimization system builds a comprehensive bandwidth matrix between all GPU devices and selects the optimal subset for distributed workloads.

```mermaid
flowchart TD
    BuildMatrix["get_bandwidth_matrix()"] --> DirectBandwidth["Direct device-to-device bandwidth"]
    BuildMatrix --> IndirectBandwidth["Indirect bandwidth via intermediary"]
    BuildMatrix --> FillMissing["Fill missing values with 0"]
    
    DirectBandwidth --> AMDSMIQuery["amdsmi.amdsmi_get_minmax_bandwidth()"]
    AMDSMIQuery --> SelfBandwidth["Set self-bandwidth to inf"]
    AMDSMIQuery --> PairBandwidth["Set pairwise max_bandwidth"]
    
    IndirectBandwidth --> MaxMinSearch["Find maximum minimum path bandwidth"]
    MaxMinSearch --> UpdateMatrix["Update bandwidth_matrix[i][j]"]
    
    FillMissing --> ExtractCluster["extract_max_avg_bandwidth_cluster()"]
    ExtractCluster --> CombinationsSearch["combinations(devices, cluster_size)"]
    CombinationsSearch --> AvgBandwidthCalc["np.mean() excluding diagonal"]
    AvgBandwidthCalc --> MaxCluster["Return cluster with maximum avg bandwidth"]
```

**Sources:** [optimum/amd/topology_utils.py:55-77]()

## Environment Variable Overrides

The CLI supports runtime environment variable overrides through command-line arguments using key-value pair syntax.

```mermaid
flowchart TD
    CLIArgs["sys.argv command line arguments"] --> ParseOverrides["get_env_vars_overrides()"]
    ParseOverrides --> FindEquals["Search for '=' in arguments"]
    FindEquals --> SplitKeyValue["Split into key=value pairs"]
    SplitKeyValue --> OverrideDict["Return override dictionary"]
    
    OverrideDict --> ZenTorchCheck["ZenTorch environment check"]
    ZenTorchCheck --> JemallocOverride["Check LD_PRELOAD override"]
    JemallocOverride --> SkipWarning["Skip jemalloc warning if overridden"]
    
    OverrideDict --> MergeEnv["Merge with detected environment variables"]
    MergeEnv --> SubprocessExec["subprocess.run() with merged environment"]
```

**Sources:** [optimum/amd/cli.py:24-36](), [optimum/amd/cli.py:73-77]()

## Usage Patterns and Examples

The CLI is designed to work as a drop-in replacement for direct script execution, automatically applying hardware-specific optimizations.

| Usage Pattern | Command Example | Optimization Applied |
|---------------|----------------|---------------------|
| Single script execution | `amdrun python script.py` | ZenTorch CPU + ROCm detection |
| Distributed training (torchrun) | `amdrun torchrun --nproc_per_node 4 train.py` | Multi-GPU topology optimization |
| Distributed training (accelerate) | `amdrun accelerate launch --ngpus 2 train.py` | Multi-GPU topology optimization |
| Environment override | `amdrun LD_PRELOAD=/custom/path python script.py` | Custom environment variables |
| Test execution | `amdrun pytest tests/ -s -v -n 32` | Parallel testing with optimizations |

```mermaid
flowchart LR
    AMDRun["amdrun"] --> ScriptArgs["script_name + arguments"]
    ScriptArgs --> EnvMerge["Merge optimized environment"]
    EnvMerge --> SubprocessCall["subprocess.run(sys.argv[1:], env=env)"]
    SubprocessCall --> ExitCode["Return script exit code"]
    
    EnvMerge --> CPUOptimizations["ZenTorch CPU optimizations"]
    EnvMerge --> GPUOptimizations["ROCm GPU optimizations"]
    EnvMerge --> UserOverrides["Command-line overrides"]
```

**Sources:** [optimum/amd/cli.py:126-143](), [.github/workflows/test_zentorch_plugin.yaml:50]()

## Integration with Testing Infrastructure

The CLI is integrated into the testing infrastructure to ensure consistent environment optimization across development and CI/CD workflows.

```mermaid
flowchart TD
    CIWorkflow[".github/workflows/test_zentorch_plugin.yaml"] --> DockerBuild["Build optimum-amd-zentorch image"]
    DockerBuild --> InstallOptimumAMD["pip install -e .[zentorch,tests]"]
    InstallOptimumAMD --> AMDRunTests["amdrun pytest tests/zentorch -s -v -n 32"]
    
    AMDRunTests --> EnvValidation["test_amdrun_zentorch_setup()"]
    EnvValidation --> OMPValidation["Assert OMP_* variables"]
    EnvValidation --> ZenDNNValidation["Assert ZENDNN_GEMM_ALGO"]
    EnvValidation --> JemallocValidation["Assert LD_PRELOAD and MALLOC_CONF"]
    
    DockerImage["transformers-pytorch-amd-cpu-zentorch"] --> JemallocInstall["libjemalloc-dev installation"]
    JemallocInstall --> ZenTorchWheel["zentorch wheel installation"]
```

**Sources:** [.github/workflows/test_zentorch_plugin.yaml:40-50](), [tests/zentorch/test_sanity.py:21-31](), [docker/transformers-pytorch-amd-cpu-zentorch/Dockerfile:31]()

---

