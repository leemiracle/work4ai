<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SimplerEnv · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [images/example_visualization/google_robot_pick_random_object.png](images/example_visualization/google_robot_pick_random_object.png)
- [images/example_visualization/google_robot_put_apple_in_closed_top_drawer.png](images/example_visualization/google_robot_put_apple_in_closed_top_drawer.png)
- [requirements_full_install.txt](requirements_full_install.txt)
- [simpler_env/__init__.py](simpler_env/__init__.py)

</details>



This document provides a comprehensive overview of SimplerEnv, a simulation-based evaluation framework for robotic manipulation policies. SimplerEnv enables scalable and reproducible evaluation of robot policies by creating simulated environments that closely match real-world robot setups.

For installation instructions and basic usage examples, see [Getting Started](#2). For detailed information about supported policy models, see [Policy Models](#3). For comprehensive evaluation procedures and metrics, see [Evaluation Framework](#4).

## Purpose and Scope

SimplerEnv addresses the challenge of evaluating generalist robot manipulation policies in a scalable and reproducible manner. Real-world robot evaluation is operationally expensive and inefficient, making it difficult to compare policies or perform systematic analysis. This system provides a simulation-based alternative that offers:

- **Scalable evaluation**: Run hundreds of policy evaluations in parallel simulation environments
- **Reproducible benchmarks**: Standardized environments and metrics for consistent comparison
- **Real-to-sim validation**: Two evaluation methodologies (Visual Matching and Variant Aggregation) that correlate with real-world performance
- **Multi-policy support**: Built-in integration with RT-1, Octo, and MolmoAct policy architectures

The system is built on the SAPIEN physics simulator and extends the ManiSkill2 benchmark with real-world robot environments and objects.

## System Architecture

The following diagram illustrates the high-level architecture of SimplerEnv and how its major components interact:

### SimplerEnv System Components

```mermaid
graph TB
    subgraph "SimplerEnv Package"
        SE_MAKE["simpler_env.make()"]
        SE_ENVS["ENVIRONMENTS"]
        SE_MAP["ENVIRONMENT_MAP"]
    end
    
    subgraph "ManiSkill2_real2sim Submodule"
        MS2_ENVS["ManiSkill2 Environments"]
        MS2_ROBOTS["Robot Agents"]
        MS2_ASSETS["Custom Assets"]
        MS2_SCENES["Scene Backgrounds"]
    end
    
    subgraph "Policy Layer"
        RT1_INF["RT1Inference"]
        OCTO_INF["OctoInference"]
        MOLMO_INF["MolmoActInference"]
    end
    
    subgraph "Evaluation Framework"
        MAIN_INF["main_inference.py"]
        MS2_EVAL["maniskill2_evaluator"]
        ARGPARSE_MOD["evaluation.argparse"]
    end
    
    subgraph "SAPIEN Backend"
        SAPIEN_SIM["SAPIEN Physics Engine"]
        VULKAN_RENDER["Vulkan Rendering"]
    end
    
    SE_MAKE --> MS2_ENVS
    SE_ENVS --> SE_MAP
    SE_MAP --> MS2_ENVS
    
    MS2_ENVS --> MS2_ROBOTS
    MS2_ENVS --> MS2_ASSETS
    MS2_ENVS --> MS2_SCENES
    MS2_ENVS --> SAPIEN_SIM
    
    MAIN_INF --> ARGPARSE_MOD
    MAIN_INF --> MS2_EVAL
    MAIN_INF --> RT1_INF
    MAIN_INF --> OCTO_INF
    MAIN_INF --> MOLMO_INF
    
    MS2_EVAL --> SE_MAKE
    SAPIEN_SIM --> VULKAN_RENDER
    
    RT1_INF --> MS2_ENVS
    OCTO_INF --> MS2_ENVS
    MOLMO_INF --> MS2_ENVS
```

Sources: [README.md:182-221](), [simpler_env/__init__.py:1-89]()

## Evaluation Methodologies

SimplerEnv implements two distinct approaches for real-to-sim evaluation, each designed to address different aspects of the simulation-to-reality gap:

### Real-to-Sim Evaluation Approaches

```mermaid
graph LR
    subgraph "Real World Data"
        REAL_ROBOTS["Real Robot Setups"]
        REAL_IMAGES["Real Background Images"]  
        REAL_OBJECTS["Real Object Textures"]
        REAL_PERF["Real Performance Data"]
    end
    
    subgraph "Visual Matching Pipeline"
        VM_BG["real_inpainting/"]
        VM_TEX["Custom Object Textures"]
        VM_CAM["Calibrated Camera Views"]
        VM_ENV["Visual Matching Environments"]
    end
    
    subgraph "Variant Aggregation Pipeline"
        VA_VARIANTS["Multiple Scene Variants"]
        VA_LIGHTING["Varied Lighting Conditions"]
        VA_BACKGROUNDS["Different Backgrounds"]
        VA_ENV["Variant Aggregation Environments"]
    end
    
    subgraph "Metrics Calculation"
        MMRV_CALC["mean_maximum_rank_violation()"]
        PEARSON_CALC["pearson_correlation()"]
        CALC_METRICS["tools/calc_metrics.py"]
    end
    
    REAL_IMAGES --> VM_BG
    REAL_OBJECTS --> VM_TEX
    REAL_ROBOTS --> VM_CAM
    
    VM_BG --> VM_ENV
    VM_TEX --> VM_ENV
    VM_CAM --> VM_ENV
    
    VA_VARIANTS --> VA_ENV
    VA_LIGHTING --> VA_ENV
    VA_BACKGROUNDS --> VA_ENV
    
    VM_ENV --> MMRV_CALC
    VA_ENV --> MMRV_CALC
    REAL_PERF --> MMRV_CALC
    
    VM_ENV --> PEARSON_CALC
    VA_ENV --> PEARSON_CALC
    REAL_PERF --> PEARSON_CALC
    
    MMRV_CALC --> CALC_METRICS
    PEARSON_CALC --> CALC_METRICS
```

Sources: [README.md:11-14](), [README.md:156-180]()

## Code Organization and Entry Points

The system provides multiple entry points for different use cases, from simple environment creation to comprehensive policy evaluation:

### Core Code Structure and Entry Points

```mermaid
graph TD
    subgraph "User Entry Points"
        SIMPLE_ENTRY["simple_inference_visual_matching_prepackaged_envs.py"]
        MAIN_ENTRY["main_inference.py"]
        MAKE_FUNC["simpler_env.make()"]
        MANUAL_DEMO["demo_manual_control_custom_envs.py"]
    end
    
    subgraph "Environment Building"
        ENV_BUILDER["utils/env/env_builder.py"]
        OBS_UTILS["utils/env/observation_utils.py"]
        GET_IMAGE["get_image_from_maniskill2_obs_dict()"]
    end
    
    subgraph "Policy Integration"
        RT1_POLICY["policies/rt1/"]
        OCTO_POLICY["policies/octo/"]
        MOLMO_POLICY["policies/molmoact/"]
    end
    
    subgraph "Evaluation System"
        EVALUATOR["evaluation/maniskill2_evaluator.py"]
        ARGPARSE_EVAL["evaluation/argparse.py"]
        SHELL_SCRIPTS["scripts/*.sh"]
    end
    
    subgraph "Analysis Tools"
        METRICS_TOOLS["tools/calc_metrics.py"]
        DEBUG_TOOLS["utils/debug/"]
        SYSID_TOOLS["tools/sysid/"]
        VIDEO_TOOLS["tools/merge_videos.py"]
    end
    
    MAKE_FUNC --> ENV_BUILDER
    SIMPLE_ENTRY --> MAKE_FUNC
    SIMPLE_ENTRY --> GET_IMAGE
    
    MAIN_ENTRY --> ARGPARSE_EVAL
    MAIN_ENTRY --> EVALUATOR
    MAIN_ENTRY --> RT1_POLICY
    MAIN_ENTRY --> OCTO_POLICY
    MAIN_ENTRY --> MOLMO_POLICY
    
    EVALUATOR --> ENV_BUILDER
    SHELL_SCRIPTS --> MAIN_ENTRY
    
    METRICS_TOOLS --> EVALUATOR
    DEBUG_TOOLS --> RT1_POLICY
    DEBUG_TOOLS --> OCTO_POLICY
    DEBUG_TOOLS --> MOLMO_POLICY
```

Sources: [README.md:182-221](), [simpler_env/__init__.py:74-88](), [README.md:124-128]()

## Key System Components

### Environment Management

The `simpler_env.make()` function serves as the primary entry point for creating evaluation environments. It maps high-level task names to specific ManiSkill2 environment configurations:

| Component | Description | Code Location |
|-----------|-------------|---------------|
| `ENVIRONMENTS` | List of supported task names | [simpler_env/__init__.py:5-31]() |
| `ENVIRONMENT_MAP` | Mapping from task names to ManiSkill2 environments | [simpler_env/__init__.py:33-71]() |
| `make()` function | Environment factory with prepackaged configurations | [simpler_env/__init__.py:74-88]() |

### Policy Support

SimplerEnv provides built-in support for three major policy architectures:

| Policy Type | Implementation | Key Dependencies |
|-------------|----------------|------------------|
| RT-1 | `simpler_env/policies/rt1/` | TensorFlow 2.15.x, tf_agents |
| Octo | `simpler_env/policies/octo/` | JAX with CUDA, Flax |
| MolmoAct | `simpler_env/policies/molmoact/` | vLLM 0.8.5, Transformers 4.52.3 |

### Evaluation Infrastructure

The evaluation system supports both simple and advanced evaluation scenarios:

- **Simple evaluation**: Use `simple_inference_visual_matching_prepackaged_envs.py` for basic policy testing
- **Advanced evaluation**: Use `main_inference.py` with `evaluation/maniskill2_evaluator.py` for comprehensive evaluation with logging and metrics
- **Batch evaluation**: Shell scripts in `scripts/` directory for reproducing paper results

Sources: [README.md:34-63](), [README.md:245-323](), [requirements_full_install.txt:1-24]()

The system integrates with the ManiSkill2_real2sim submodule to provide the underlying simulation environments, robot models, and object assets needed for realistic manipulation task evaluation.

---

