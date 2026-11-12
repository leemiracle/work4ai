<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cloudai · page 9 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/cloudai/__init__.py](src/cloudai/__init__.py)
- [src/cloudai/_core/exceptions.py](src/cloudai/_core/exceptions.py)
- [src/cloudai/_core/registry.py](src/cloudai/_core/registry.py)
- [src/cloudai/_core/test_scenario.py](src/cloudai/_core/test_scenario.py)
- [src/cloudai/core.py](src/cloudai/core.py)
- [src/cloudai/models/scenario.py](src/cloudai/models/scenario.py)
- [src/cloudai/models/workload.py](src/cloudai/models/workload.py)
- [src/cloudai/parser.py](src/cloudai/parser.py)
- [src/cloudai/registration.py](src/cloudai/registration.py)
- [src/cloudai/systems/slurm/slurm_command_gen_strategy.py](src/cloudai/systems/slurm/slurm_command_gen_strategy.py)
- [src/cloudai/systems/slurm/slurm_system.py](src/cloudai/systems/slurm/slurm_system.py)
- [src/cloudai/test_parser.py](src/cloudai/test_parser.py)
- [src/cloudai/test_scenario_parser.py](src/cloudai/test_scenario_parser.py)
- [src/cloudai/workloads/common/llm_serving.py](src/cloudai/workloads/common/llm_serving.py)
- [src/cloudai/workloads/common/nixl.py](src/cloudai/workloads/common/nixl.py)
- [src/cloudai/workloads/megatron_bridge/__init__.py](src/cloudai/workloads/megatron_bridge/__init__.py)
- [src/cloudai/workloads/megatron_bridge/megatron_bridge.py](src/cloudai/workloads/megatron_bridge/megatron_bridge.py)
- [src/cloudai/workloads/megatron_bridge/report_generation_strategy.py](src/cloudai/workloads/megatron_bridge/report_generation_strategy.py)
- [src/cloudai/workloads/megatron_bridge/slurm_command_gen_strategy.py](src/cloudai/workloads/megatron_bridge/slurm_command_gen_strategy.py)
- [src/cloudai/workloads/nixl_bench/nixl_bench.py](src/cloudai/workloads/nixl_bench/nixl_bench.py)
- [src/cloudai/workloads/nixl_bench/slurm_command_gen_strategy.py](src/cloudai/workloads/nixl_bench/slurm_command_gen_strategy.py)
- [src/cloudai/workloads/nixl_kvbench/__init__.py](src/cloudai/workloads/nixl_kvbench/__init__.py)
- [src/cloudai/workloads/nixl_kvbench/nixl_kvbench.py](src/cloudai/workloads/nixl_kvbench/nixl_kvbench.py)
- [src/cloudai/workloads/nixl_kvbench/slurm_command_gen_strategy.py](src/cloudai/workloads/nixl_kvbench/slurm_command_gen_strategy.py)
- [src/cloudai/workloads/sglang/__init__.py](src/cloudai/workloads/sglang/__init__.py)
- [src/cloudai/workloads/sglang/slurm_command_gen_strategy.py](src/cloudai/workloads/sglang/slurm_command_gen_strategy.py)
- [src/cloudai/workloads/triton_inference/slurm_command_gen_strategy.py](src/cloudai/workloads/triton_inference/slurm_command_gen_strategy.py)
- [src/cloudai/workloads/vllm/slurm_command_gen_strategy.py](src/cloudai/workloads/vllm/slurm_command_gen_strategy.py)
- [src/cloudai/workloads/vllm/vllm.py](src/cloudai/workloads/vllm/vllm.py)
- [tests/ref_data/megatron-bridge.sbatch](tests/ref_data/megatron-bridge.sbatch)
- [tests/ref_data/nixl-kvbench.sbatch](tests/ref_data/nixl-kvbench.sbatch)
- [tests/ref_data/nixl_bench.sbatch](tests/ref_data/nixl_bench.sbatch)
- [tests/ref_data/sglang-disagg-2nodes.sbatch](tests/ref_data/sglang-disagg-2nodes.sbatch)
- [tests/ref_data/sglang-disagg.sbatch](tests/ref_data/sglang-disagg.sbatch)
- [tests/ref_data/sglang.sbatch](tests/ref_data/sglang.sbatch)
- [tests/ref_data/vllm-disagg-2nodes.sbatch](tests/ref_data/vllm-disagg-2nodes.sbatch)
- [tests/ref_data/vllm-disagg.sbatch](tests/ref_data/vllm-disagg.sbatch)
- [tests/ref_data/vllm.sbatch](tests/ref_data/vllm.sbatch)
- [tests/systems/slurm/test_allocation.py](tests/systems/slurm/test_allocation.py)
- [tests/systems/slurm/test_command_gen_strategy.py](tests/systems/slurm/test_command_gen_strategy.py)
- [tests/systems/slurm/test_system.py](tests/systems/slurm/test_system.py)
- [tests/test_acceptance.py](tests/test_acceptance.py)
- [tests/test_init.py](tests/test_init.py)
- [tests/test_registry.py](tests/test_registry.py)
- [tests/test_test_scenario.py](tests/test_test_scenario.py)
- [tests/workloads/megatron_bridge/test_command_gen_strategy_slurm.py](tests/workloads/megatron_bridge/test_command_gen_strategy_slurm.py)
- [tests/workloads/megatron_bridge/test_report_gen_strategy.py](tests/workloads/megatron_bridge/test_report_gen_strategy.py)
- [tests/workloads/nixl_bench/test_command_gen_strategy_slurm.py](tests/workloads/nixl_bench/test_command_gen_strategy_slurm.py)
- [tests/workloads/nixl_kvbench/test_command_gen_slurm.py](tests/workloads/nixl_kvbench/test_command_gen_slurm.py)
- [tests/workloads/sglang/test_command_gen_strategy_slurm.py](tests/workloads/sglang/test_command_gen_strategy_slurm.py)
- [tests/workloads/sglang/test_workload.py](tests/workloads/sglang/test_workload.py)
- [tests/workloads/test_llm_serving.py](tests/workloads/test_llm_serving.py)
- [tests/workloads/vllm/test_command_gen_strategy_slurm.py](tests/workloads/vllm/test_command_gen_strategy_slurm.py)
- [tests/workloads/vllm/test_workload.py](tests/workloads/vllm/test_workload.py)

</details>



This glossary defines codebase-specific terms, jargon, and domain concepts used throughout CloudAI. It provides a mapping between natural language concepts and their technical implementations within the Python source code.

## Core Domain Concepts

### The Three-Schema System
CloudAI uses a hierarchical configuration system composed of three distinct TOML-based schemas to define how AI benchmarks are executed.

| Term | Description | Code Entities |
| :--- | :--- | :--- |
| **System** | Defines the hardware and scheduler environment (e.g., Slurm partitions, node lists, account names). | `System`, `SlurmSystem`, `KubernetesSystem` |
| **Test** | A template for a workload, defining the base command arguments, Docker images, and installation requirements. | `TestDefinition`, `CmdArgs` |
| **TestScenario** | An execution plan that instantiates Tests with specific parameters and defines dependencies between them. | `TestScenario`, `TestRun` |

**Sources:** [src/cloudai/core.py:17-34](), [src/cloudai/systems/slurm/slurm_system.py:96-120](), [src/cloudai/models/scenario.py:37-38]().

---

## Technical Terms & Jargon

### Command Generation Strategy (CommandGenStrategy)
A pattern used to translate the abstract `TestRun` definition into the specific shell commands or job manifests required by a scheduler.

*   **Implementation:** The `CommandGenStrategy` class is specialized for different system/workload combinations. For Slurm, it typically generates `srun` or `sbatch` commands.
*   **Data Flow:** `TestRun` -> `CommandGenStrategy.gen_exec_command()` -> Shell Script/Manifest.

**Sources:** [src/cloudai/core.py:30-30](), [src/cloudai/systems/slurm/slurm_command_gen_strategy.py:28-32](), [src/cloudai/workloads/megatron_bridge/slurm_command_gen_strategy.py:33-81]().

### Design Space Exploration (DSE)
The process of automatically iterating over a range of hyperparameters (e.g., TP/PP sizes, batch sizes) to find the optimal configuration for a workload.

*   **Key Class:** `GridSearchAgent` manages the exploration trajectory.
*   **Reporting:** `DSEReporter` aggregates results across all iterations to visualize performance trends.

**Sources:** [src/cloudai/registration.py:38-49](), [tests/test_test_scenario.py:19-19]().

### Installables
Objects representing software dependencies that must be present before a test can run. CloudAI handles concurrent installation and caching of these entities.

*   **Types:** `DockerImage`, `GitRepo`, `PythonExecutable`, `File`, `HFModel`.
*   **Process:** The `BaseInstaller` (e.g., `SlurmInstaller`) iterates through `TestDefinition.installables` to ensure they are prepared on the target system.

**Sources:** [src/cloudai/core.py:27-27](), [src/cloudai/workloads/vllm/vllm.py:89-94](), [src/cloudai/workloads/megatron_bridge/megatron_bridge.py:24-25]().

### Registry
A singleton object that acts as the central lookup for all available system types, runners, test definitions, and strategies. It is populated during the `register_all()` call at application startup.

**Sources:** [src/cloudai/registration.py:36-50](), [src/cloudai/_init_.py:36-38](), [src/cloudai/_core/registry.py:1-20]().

---

## Architecture Diagrams

### From Scenario to Execution
The following diagram bridges the "Natural Language Space" (User Intent) to the "Code Entity Space" (Classes and Functions).

**Scenario Execution Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["'Run Llama-3 on Slurm'"]
        B["'Install Dependencies'"]
    end

    subgraph "Code Entity Space"
        C["TestScenarioParser"]
        D["Registry"]
        E["TestRun"]
        F["SlurmRunner"]
        G["SlurmCommandGenStrategy"]
        H["SlurmInstaller"]
    end

    A --> C
    C -->|lookup| D
    C -->|instantiate| E
    E -->|dispatch| F
    F -->|uses| G
    B --> H
    H -->|checks| E
end
```
**Sources:** [src/cloudai/test_scenario_parser.py:39-40](), [src/cloudai/registration.py:181-185](), [src/cloudai/systems/slurm/slurm_system.py:171-183]().

### Workload Plugin Architecture
How specific workloads (like Megatron-Bridge or vLLM) hook into the framework.

**Workload Integration Diagram**
```mermaid
graph LR
    subgraph "Base Framework"
        TDEF["TestDefinition"]
        STRAT["CommandGenStrategy"]
        REP["ReportGenerationStrategy"]
    end

    subgraph "Megatron-Bridge Implementation"
        MB_TDEF["MegatronBridgeTestDefinition"]
        MB_STRAT["MegatronBridgeSlurmCommandGenStrategy"]
        MB_REP["MegatronBridgeReportGenerationStrategy"]
    end

    subgraph "vLLM Implementation"
        V_TDEF["VllmTestDefinition"]
        V_STRAT["VllmSlurmCommandGenStrategy"]
        V_REP["VLLMBenchReportGenerationStrategy"]
    end

    MB_TDEF --|> TDEF
    MB_STRAT --|> STRAT
    MB_REP --|> REP

    V_TDEF --|> TDEF
    V_STRAT --|> STRAT
    V_REP --|> REP
```
**Sources:** [src/cloudai/workloads/megatron_bridge/megatron_bridge.py:28-150](), [src/cloudai/workloads/vllm/vllm.py:83-174](), [src/cloudai/registration.py:94-104](), [src/cloudai/registration.py:175-179]().

---

## Glossary Table

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Dry Run** | A mode where CloudAI validates configurations and generates command scripts without submitting jobs to the scheduler. | `handle_dry_run_and_run` in [tests/test_acceptance.py:108-132]() |
| **Disaggregated Serving** | An LLM serving architecture where Prefill and Decode phases run on separate GPU sets/nodes. | `LLMServingSlurmCommandGenStrategy` in [src/cloudai/workloads/vllm/slurm_command_gen_strategy.py:29-86]() |
| **NIXL** | NVIDIA Index Library; used for high-performance KV cache transfer and storage benchmarking. | `NIXLBaseCmdArgs` in [src/cloudai/workloads/common/nixl.py:44-58]() |
| **Slurm Node State** | The current status of a node (IDLE, ALLOCATED, DOWN) retrieved via `sinfo`. | `SlurmNodeState` in [src/cloudai/systems/slurm/slurm_node.py:1-20]() |
| **Iteration** | A repeated execution of a `TestRun` within a `TestScenario`. | `TestRun.iterations` in [tests/test_test_scenario.py:106-107]() |
| **Dependency** | A relationship between `TestRuns` (e.g., `start_post_comp`) determining execution order. | `TestRun.dependencies` in [tests/test_test_scenario.py:108-108]() |
| **Grading Strategy** | Logic used to determine if a test passed based on performance thresholds or output logs. | `NcclTestGradingStrategy` in [src/cloudai/registration.py:109-114]() |

**Sources:** [src/cloudai/workloads/vllm/slurm_command_gen_strategy.py:73-86](), [src/cloudai/systems/slurm/slurm_system.py:184-192](), [tests/test_test_scenario.py:104-108]().