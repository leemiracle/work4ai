<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SimplerEnv · page 3 Policy Models · fetched 2026-10-26 -->

# Policy Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [simpler_env/main_inference.py](simpler_env/main_inference.py)
- [simpler_env/policies/octo/octo_model.py](simpler_env/policies/octo/octo_model.py)
- [simpler_env/policies/octo/octo_server_model.py](simpler_env/policies/octo/octo_server_model.py)
- [simpler_env/policies/rt1/rt1_model.py](simpler_env/policies/rt1/rt1_model.py)
- [simpler_env/simple_inference_visual_matching_prepackaged_envs.py](simpler_env/simple_inference_visual_matching_prepackaged_envs.py)
- [simpler_env/utils/env/env_builder.py](simpler_env/utils/env/env_builder.py)

</details>



This document covers the policy model implementations supported by SimplerEnv for robotic manipulation evaluation. Policy models are the core components that process visual observations and language instructions to generate robot actions. SimplerEnv supports three main policy architectures: RT-1, Octo, and MolmoAct, each with different inference backends and configurations.

For information about running evaluations with these policies, see [Evaluation Framework](#4). For setup and installation of policy dependencies, see [Installation](#2.1).

## Policy Architecture Overview

SimplerEnv implements a unified interface for different policy models, allowing seamless evaluation across various architectures. All policies follow a common pattern for initialization, reset, and action generation.

```mermaid
graph TB
    subgraph "Policy Interface"
        RESET["reset(task_description)"]
        STEP["step(image, task_description)"]
        VISUALIZE["visualize_epoch()"]
    end
    
    subgraph "RT-1 Implementation"
        RT1_CLASS["RT1Inference"]
        RT1_TFA["TensorFlow Agents Policy"]
        RT1_LANG["Universal Sentence Encoder"]
    end
    
    subgraph "Octo Implementation"
        OCTO_CLASS["OctoInference"]
        OCTO_SERVER["OctoServerInference"]
        OCTO_MODEL["OctoModel (JAX/Flax)"]
        OCTO_ENSEMBLE["ActionEnsembler"]
    end
    
    subgraph "MolmoAct Implementation"
        MOLMO_CLASS["MolmoActInference"]
        MOLMO_VLLM["MolmoActInferenceVLLM"]
        MOLMO_HF["HuggingFace Backend"]
        MOLMO_VLLM_ENGINE["vLLM Engine"]
    end
    
    subgraph "Action Processing"
        RAW_ACTION["Raw Policy Output"]
        PROCESSED_ACTION["Processed ManiSkill2 Action"]
        WORLD_VEC["world_vector (3D translation)"]
        ROT_AXANGLE["rot_axangle (axis-angle rotation)"]
        GRIPPER["gripper (open/close)"]
        TERMINATE["terminate_episode"]
    end
    
    RESET --> RT1_CLASS
    RESET --> OCTO_CLASS
    RESET --> MOLMO_CLASS
    
    STEP --> RT1_CLASS
    STEP --> OCTO_CLASS
    STEP --> MOLMO_CLASS
    
    RT1_CLASS --> RT1_TFA
    RT1_CLASS --> RT1_LANG
    
    OCTO_CLASS --> OCTO_MODEL
    OCTO_CLASS --> OCTO_ENSEMBLE
    OCTO_SERVER --> OCTO_MODEL
    
    MOLMO_CLASS --> MOLMO_HF
    MOLMO_VLLM --> MOLMO_VLLM_ENGINE
    
    RT1_CLASS --> RAW_ACTION
    OCTO_CLASS --> RAW_ACTION
    MOLMO_CLASS --> RAW_ACTION
    
    RAW_ACTION --> PROCESSED_ACTION
    PROCESSED_ACTION --> WORLD_VEC
    PROCESSED_ACTION --> ROT_AXANGLE
    PROCESSED_ACTION --> GRIPPER
    PROCESSED_ACTION --> TERMINATE
```

Sources: [simpler_env/policies/rt1/rt1_model.py:14-282](), [simpler_env/policies/octo/octo_model.py:16-273](), [simpler_env/main_inference.py:52-89]()

## Common Policy Interface

All policy implementations follow a standardized interface for integration with the evaluation framework. The interface consists of three main methods and consistent action output formats.

### Core Methods

| Method | Purpose | Input | Output |
|--------|---------|--------|--------|
| `reset(task_description)` | Initialize policy state for new episode | Task description string | None |
| `step(image, task_description)` | Generate action from observation | RGB image array, optional task description | Raw action dict, processed action dict |
| `visualize_epoch(actions, images, save_path)` | Generate visualization of policy predictions | Action sequence, image sequence, output path | None |

### Action Output Format

All policies output actions in a consistent format for ManiSkill2 environment integration:

```mermaid
graph LR
    subgraph "Raw Policy Output"
        RAW_WORLD["world_vector (3,)"]
        RAW_ROT["rotation_delta (3,)"]
        RAW_GRIP["open_gripper (1,)"]
    end
    
    subgraph "Action Processing"
        SCALE["Action Scaling"]
        ROT_CONVERT["Rotation Conversion"]
        GRIP_PROCESS["Gripper Processing"]
    end
    
    subgraph "ManiSkill2 Action"
        MS_WORLD["world_vector (3,)"]
        MS_ROT["rot_axangle (3,)"]
        MS_GRIP["gripper (1,)"]
        MS_TERM["terminate_episode (1,)"]
    end
    
    RAW_WORLD --> SCALE --> MS_WORLD
    RAW_ROT --> ROT_CONVERT --> MS_ROT
    RAW_GRIP --> GRIP_PROCESS --> MS_GRIP
    GRIP_PROCESS --> MS_TERM
```

Sources: [simpler_env/policies/rt1/rt1_model.py:150-230](), [simpler_env/policies/octo/octo_model.py:130-242]()

## Policy Model Instantiation

The `main_inference.py` entry point handles policy model selection and instantiation based on command-line arguments. The system supports different inference modes and configurations for each policy type.

```mermaid
graph TD
    subgraph "main_inference.py"
        ARGS["get_args()"]
        POLICY_CHECK["Policy Model Check"]
        MODEL_INIT["Model Instantiation"]
    end
    
    subgraph "RT-1 Path"
        RT1_CHECK["args.policy_model == 'rt1'"]
        RT1_INIT["RT1Inference(saved_model_path, policy_setup, action_scale)"]
    end
    
    subgraph "Octo Path"
        OCTO_CHECK["'octo' in args.policy_model"]
        OCTO_SERVER_CHECK["'server' in args.policy_model"]
        OCTO_LOCAL["OctoInference(model_type, policy_setup, init_rng, action_scale)"]
        OCTO_SERVER_INIT["OctoServerInference(model_type, policy_setup, action_scale)"]
    end
    
    subgraph "MolmoAct Path"
        MOLMO_CHECK["'molmoact' in args.policy_model"]
        MOLMO_VLLM_CHECK["'vllm' in args.policy_model"]
        MOLMO_HF["MolmoActInference(saved_model_path, policy_setup)"]
        MOLMO_VLLM_INIT["MolmoActInferenceVLLM(saved_model_path, policy_setup)"]
    end
    
    ARGS --> POLICY_CHECK
    POLICY_CHECK --> RT1_CHECK
    POLICY_CHECK --> OCTO_CHECK
    POLICY_CHECK --> MOLMO_CHECK
    
    RT1_CHECK --> RT1_INIT
    OCTO_CHECK --> OCTO_SERVER_CHECK
    OCTO_SERVER_CHECK -->|Yes| OCTO_SERVER_INIT
    OCTO_SERVER_CHECK -->|No| OCTO_LOCAL
    
    MOLMO_CHECK --> MOLMO_VLLM_CHECK
    MOLMO_VLLM_CHECK -->|Yes| MOLMO_VLLM_INIT
    MOLMO_VLLM_CHECK -->|No| MOLMO_HF
    
    RT1_INIT --> MODEL_INIT
    OCTO_LOCAL --> MODEL_INIT
    OCTO_SERVER_INIT --> MODEL_INIT
    MOLMO_HF --> MODEL_INIT
    MOLMO_VLLM_INIT --> MODEL_INIT
```

Sources: [simpler_env/main_inference.py:52-89]()

## Policy Setup Configurations

Each policy model supports different robot configurations through the `policy_setup` parameter. The two main setups are `google_robot` and `widowx_bridge`, which define robot-specific action processing and gripper control strategies.

| Policy Setup | Robot Type | Gripper Control | Action Normalization |
|--------------|------------|-----------------|---------------------|
| `google_robot` | Google Robot (static base) | Continuous with sticky gripper | Native policy output |
| `widowx_bridge` | WidowX Bridge | Binary open/close | Action rescaling applied |

### Google Robot Configuration

For Google Robot setups, policies implement sticky gripper behavior where gripper commands are repeated for multiple timesteps to ensure reliable execution.

```mermaid
graph LR
    subgraph "Google Robot Gripper Logic"
        GRIPPER_CMD["Current Gripper Command"]
        PREV_CMD["Previous Gripper Command"]
        STICKY_CHECK["Sticky Action Check"]
        REPEAT_COUNT["Repeat Counter"]
        STICKY_ACTION["Sticky Gripper Action"]
    end
    
    GRIPPER_CMD --> PREV_CMD
    PREV_CMD --> STICKY_CHECK
    STICKY_CHECK -->|"Change > 0.5"| REPEAT_COUNT
    REPEAT_COUNT -->|"< 15 steps"| STICKY_ACTION
    STICKY_ACTION --> GRIPPER_CMD
```

Sources: [simpler_env/policies/octo/octo_model.py:187-232](), [simpler_env/policies/rt1/rt1_model.py:214-224]()

### WidowX Bridge Configuration

WidowX Bridge setups use binary gripper control and may apply action normalization depending on the policy type.

Sources: [simpler_env/policies/octo/octo_model.py:234-238](), [simpler_env/policies/rt1/rt1_model.py:46-52]()

## Action Processing Pipeline

All policies follow a consistent action processing pipeline that converts raw policy outputs into ManiSkill2-compatible actions. The pipeline handles coordinate transformations, action scaling, and robot-specific adaptations.

```mermaid
graph TD
    subgraph "Raw Policy Action"
        RAW_TRANS["Translation (world_vector)"]
        RAW_ROT["Rotation (rotation_delta)"]
        RAW_GRIP["Gripper (open_gripper)"]
    end
    
    subgraph "Processing Steps"
        SCALE_TRANS["Apply action_scale to translation"]
        CONVERT_ROT["Convert rotation to axis-angle"]
        PROCESS_GRIP["Process gripper based on policy_setup"]
        ADD_TERMINATE["Add terminate_episode flag"]
    end
    
    subgraph "ManiSkill2 Action"
        MS_TRANS["world_vector (3,)"]
        MS_ROT["rot_axangle (3,)"]
        MS_GRIP["gripper (1,)"]
        MS_TERM["terminate_episode (1,)"]
    end
    
    RAW_TRANS --> SCALE_TRANS --> MS_TRANS
    RAW_ROT --> CONVERT_ROT --> MS_ROT
    RAW_GRIP --> PROCESS_GRIP --> MS_GRIP
    PROCESS_GRIP --> ADD_TERMINATE --> MS_TERM
```

### Rotation Conversion

Rotation actions are converted from Euler angles to axis-angle representation using the `transforms3d` library. This ensures compatibility with ManiSkill2's expected rotation format.

Sources: [simpler_env/policies/rt1/rt1_model.py:185-207](), [simpler_env/policies/octo/octo_model.py:178-185]()

## Image Processing

All policies implement consistent image preprocessing to ensure proper input formatting. Images are resized to policy-specific dimensions and converted to the appropriate data types.

| Policy Type | Input Size | Resize Method | Data Type |
|-------------|------------|---------------|-----------|
| RT-1 | 320x256 | `resize_with_pad` | uint8 |
| Octo | 256x256 | `lanczos3` with antialiasing | uint8 |
| MolmoAct | Variable | Policy-dependent | uint8 |

Sources: [simpler_env/policies/rt1/rt1_model.py:101-104](), [simpler_env/policies/octo/octo_model.py:88-96]()

---

