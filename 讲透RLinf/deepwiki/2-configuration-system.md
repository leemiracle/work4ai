<!-- source: DeepWiki mcp.deepwiki.com · repo RLinf/RLinf · page 2 Configuration System · fetched 2026-10-21 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source-en/rst_source/guides/agentic_config.rst](docs/source-en/rst_source/guides/agentic_config.rst)
- [docs/source-en/rst_source/guides/basic_config.rst](docs/source-en/rst_source/guides/basic_config.rst)
- [docs/source-en/rst_source/guides/embodiment_config.rst](docs/source-en/rst_source/guides/embodiment_config.rst)
- [docs/source-en/rst_source/guides/env_decoupled_mode.rst](docs/source-en/rst_source/guides/env_decoupled_mode.rst)
- [docs/source-en/rst_source/guides/performance/index.rst](docs/source-en/rst_source/guides/performance/index.rst)
- [docs/source-zh/rst_source/guides/agentic_config.rst](docs/source-zh/rst_source/guides/agentic_config.rst)
- [docs/source-zh/rst_source/guides/basic_config.rst](docs/source-zh/rst_source/guides/basic_config.rst)
- [docs/source-zh/rst_source/guides/embodiment_config.rst](docs/source-zh/rst_source/guides/embodiment_config.rst)
- [docs/source-zh/rst_source/guides/env_decoupled_mode.rst](docs/source-zh/rst_source/guides/env_decoupled_mode.rst)
- [docs/source-zh/rst_source/guides/performance/index.rst](docs/source-zh/rst_source/guides/performance/index.rst)
- [rlinf/utils/omega_resolver.py](rlinf/utils/omega_resolver.py)

</details>



RLinf uses [Hydra](https://hydra.cc/) for compositional configuration management, enabling modular experiment design through YAML-based configuration files. This system allows users to define complex distributed training setups by composing reusable configuration components and overriding specific parameters without modifying code. [docs/source-en/rst_source/guides/basic_config.rst:11-20]()

For information about how configurations are used to instantiate workers and manage distributed execution, see [Distributed Scheduler](#3.1). For details on configuring specific RL algorithms and models, see [Algorithm and Model Configuration](#2.3).

## Configuration Composition

Hydra enables **hierarchical composition** where base configuration files are inherited and selectively overridden. Configuration files are organized by component type and can be composed using the `defaults` directive. [docs/source-en/rst_source/guides/embodiment_config.rst:8-23]()

### Defaults Directive

The `defaults` section at the top of a configuration file specifies which base configurations to compose. RLinf splits configurations into specific groups such as `env`, `model`, and `training_backend` to cater to different research needs. The `<group>@<target>` syntax is used to mount presets onto specific config nodes (e.g., `model/openvla_oft@actor.model` fills the `actor.model` configuration). [docs/source-en/rst_source/guides/embodiment_config.rst:20-23]()

**Title: Configuration Composition Flow**
```mermaid
graph TB
    ["Main Config YAML<br/>(e.g., maniskill_ppo_openvlaoft.yaml)"] -- "defaults: composition" --> Defaults
    
    subgraph Defaults["Composition Keys"]
        ["env/maniskill@env.train"]
        ["model/openvla_oft@actor.model"]
        ["weight_syncer/patch_syncer@weight_syncer"]
    end
    
    subgraph BaseConfigs["Base Configuration Files"]
        ["config/env/maniskill_*.yaml"]
        ["config/model/openvla_oft.yaml"]
        ["config/weight_syncer/patch_syncer.yaml"]
    end
    
    subgraph FinalConfig["Merged OmegaConf Object"]
        ["env: train: {...}"]
        ["actor: model: {...}"]
        ["runner: {...}"]
    end
    
    Defaults -.-> BaseConfigs
    BaseConfigs --> FinalConfig
```

**Sources**: [docs/source-en/rst_source/guides/embodiment_config.rst:8-32](), [docs/source-zh/rst_source/guides/embodiment_config.rst:7-32]()

## Configuration File Structure

All RLinf experiments follow a standard configuration structure defined via `omegaconf.DictConfig`. The system supports multiple task types (e.g., `embodied`, `math`) and training backends like `megatron` and `fsdp`. [docs/source-en/rst_source/guides/basic_config.rst:1-9](), [docs/source-en/rst_source/guides/agentic_config.rst:80-90]()

| Section | Purpose | Reference |
|---------|---------|-----------|
| `cluster` | Distributed execution topology, node counts, and component placement | [docs/source-en/rst_source/guides/basic_config.rst:32-55]() |
| `runner` | Training loop orchestration, task types, logging, and checkpointing | [docs/source-en/rst_source/guides/basic_config.rst:78-130]() |
| `algorithm` | RL hyperparameters (PPO, GRPO, SAC), loss settings, and sampling | [docs/source-en/rst_source/guides/basic_config.rst:132-210]() |
| `actor` | Training worker logic, precision, and backend-specific settings | [docs/source-en/rst_source/guides/basic_config.rst:241-265]() |
| `rollout` | Inference engine settings (SGLang/vLLM), TP/PP degrees, and memory | [docs/source-en/rst_source/guides/agentic_config.rst:80-157]() |
| `env` | Environment simulation settings, parallel env counts, and auto-reset | [docs/source-en/rst_source/guides/embodiment_config.rst:149-204]() |
| `data` | Dataset paths, batch sizes, and prompt/answer key mappings | [docs/source-en/rst_source/guides/agentic_config.rst:190-248]() |

### Cluster and Placement Configuration

The `cluster` section defines the distributed execution topology. The `component_placement` mapping assigns components to hardware ranks (e.g., GPU IDs). [docs/source-en/rst_source/guides/basic_config.rst:32-55]()

**Placement Logic**:
- **COLLOCATED / PACKED**: Workers are placed in a close-packed manner, optionally sharing accelerators.
- **DISAGGREGATED / FLEXIBLE**: Allows specifying exact global hardware ranks for each process. [docs/source-en/rst_source/guides/basic_config.rst:50-54]()
- **Rank Syntax**: Supports `all`, single integers (`3`), lists (`0,2,3`), or ranges (`0-3`). [docs/source-en/rst_source/guides/basic_config.rst:56-75]()

**Title: Config Entity to Implementation Mapping**
```mermaid
graph LR
    subgraph Config["YAML Config Entities"]
        ["cluster.component_placement"]
        ["cluster.num_nodes"]
        ["rollout.rollout_backend"]
    end
    
    subgraph CodeClasses["Code Implementation Space"]
        CC_CPS["PlacementStrategy (rlinf/scheduler/placement/placement.py)"]
        CC_PPS["PackedPlacementStrategy (rlinf/scheduler/placement/packed.py)"]
        CC_FPS["FlexiblePlacementStrategy (rlinf/scheduler/placement/flexible.py)"]
        CC_CC["ClusterConfig (rlinf/scheduler/cluster/config.py)"]
    end
    
    subgraph ClusterSubsystem["Cluster Subsystem"]
        ["Cluster (rlinf/scheduler/cluster/cluster.py)"]
        ["NodeGroupConfig (rlinf/scheduler/cluster/config.py)"]
    end
    
    ["cluster.component_placement"] --> CC_PPS
    ["cluster.component_placement"] --> CC_FPS
    ["cluster.num_nodes"] --> CC_CC
    CC_PPS -- "inherits" --> CC_CPS
    CC_FPS -- "inherits" --> CC_CPS
    CC_CC --> ClusterSubsystem
```

**Sources**: [docs/source-en/rst_source/guides/basic_config.rst:32-75](), [rlinf/utils/omega_resolver.py:23-42]()

## Advanced Configuration Features

### OmegaConf Resolvers
RLinf registers custom OmegaConf resolvers to handle arithmetic and torch-specific types directly within YAML files. This includes `multiply`, `int_div`, `subtract`, `not`, and `torch.dtype`. [rlinf/utils/omega_resolver.py:32-42]()

### Decoupled Mode
For embodied AI, `runner.enable_decoupled_mode` allows `EnvWorker` instances to be independent of `RolloutWorker` instances. Observations are pushed to a shared `Channel`, and idle `RolloutWorker` ranks fetch batches dynamically. [docs/source-en/rst_source/guides/embodiment_config.rst:60-67](), [docs/source-en/rst_source/guides/env_decoupled_mode.rst:4-12]()

### Inference Engine Integration
RLinf supports multiple inference backends for rollout generation, specifically `sglang` and `vllm`. Each backend has a dedicated configuration block to tune performance (e.g., `enable_chunked_prefill`, `attention_backend`). [docs/source-en/rst_source/guides/agentic_config.rst:80-118]()

## Configuration Details

For more specific details on the sub-components of the configuration system, refer to the following child pages:

- **[Hydra Composition and Defaults](#2.1)**: Detail how Hydra defaults work, configuration inheritance, and searchpath resolution for modular experiment design. [docs/source-en/rst_source/guides/embodiment_config.rst:8-32]()
- **[Component Placement Strategies](#2.2)**: Explain `COLLOCATED`, `DISAGGREGATED`, and `AUTO` placement modes, and how GPU allocation syntax works across multi-node clusters. [docs/source-en/rst_source/guides/basic_config.rst:32-75](), [docs/source-en/rst_source/guides/performance/index.rst:13-14]()
- **[Algorithm and Model Configuration](#2.3)**: Document how to configure RL algorithms (PPO, SAC, GRPO), model architectures, training hyperparameters, and sampling parameters for both embodied and agentic tasks. [docs/source-en/rst_source/guides/basic_config.rst:132-210](), [docs/source-en/rst_source/guides/agentic_config.rst:29-78]()

**Sources**: [docs/source-en/rst_source/guides/basic_config.rst:1-240](), [docs/source-en/rst_source/guides/embodiment_config.rst:1-215](), [docs/source-en/rst_source/guides/agentic_config.rst:1-255](), [rlinf/utils/omega_resolver.py:1-46](), [docs/source-en/rst_source/guides/env_decoupled_mode.rst:1-135]()

---

