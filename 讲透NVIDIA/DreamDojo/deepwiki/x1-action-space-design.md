<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DreamDojo · extra page Action Space Design · fetched 2026-10-26 -->

# Action Space Design

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/POSTTRAIN.md](docs/POSTTRAIN.md)
- [groot_dreams/data/dataset.py](groot_dreams/data/dataset.py)
- [shared_meta/AgiBot_modality.json](shared_meta/AgiBot_modality.json)

</details>



## Purpose and Scope

This document details DreamDojo's 384-dimensional unified action space design, which enables a single model to support multiple robot embodiments (GR-1, Unitree G1, AgiBot, YAM) along with MANO hand parameterizations and learned latent actions. This design is central to the post-training phase where robot-specific adaptation occurs.

For information about the post-training process itself, see [Post-Training](#4.2). For robot-specific training configurations, see [Robot-Specific Training](#4.2.2). For details on the Latent Action Model that provides the latent action component, see [Latent Action Model (LAM)](#3.3).

**Sources**: [docs/POSTTRAIN.md:1-34]()

## Unified Action Space Overview

DreamDojo uses a fixed 384-dimensional action space to accommodate all robot platforms and action representations in a single unified framework. Rather than training separate models for each robot, the action space is partitioned into non-overlapping regions where each robot writes its actions to a designated slice of the full vector.

During inference or training, a robot-specific configuration specifies which dimensions are active. The remaining dimensions are typically zero-padded. This architecture simplifies checkpoint management, enables potential transfer learning between robots, and maintains a consistent model architecture across experiments.

### Action Space to Code Mapping

The following diagram illustrates how high-level robot definitions map to specific dimension ranges and the internal model components that process them.

```mermaid
graph TB
    subgraph "Action_Input_Processing"
        ["RobotActions"] -- "Variable dims: 22-46" --> ["UnifiedActionVector"]
        ["MANO_Params"] -- "132 dimensions" --> ["UnifiedActionVector"]
        ["LAM_Latent_Actions"] -- "32 dimensions" --> ["UnifiedActionVector"]
    end
    
    subgraph "Unified_384_Space"
        ["UnifiedActionVector"]
        ["Dim_0_29"]["[0:29] Fourier_GR1"]
        ["Dim_29_58"]["[29:58] Manus_GR1"]
        ["Dim_58_101"]["[58:101] Unitree_G1"]
        ["Dim_101_147"]["[101:147] Bimanual_YAM"]
        ["Dim_147_169"]["[147:169] AgiBot"]
        ["Dim_169_220"]["[169:220] Reserved"]
        ["Dim_220_352"]["[220:352] MANO_Actions"]
        ["Dim_352_384"]["[352:384] Latent_Actions"]
        
        ["UnifiedActionVector"] --> ["Dim_0_29"]
        ["UnifiedActionVector"] --> ["Dim_29_58"]
        ["UnifiedActionVector"] --> ["Dim_58_101"]
        ["UnifiedActionVector"] --> ["Dim_101_147"]
        ["UnifiedActionVector"] --> ["Dim_147_169"]
        ["UnifiedActionVector"] --> ["Dim_220_352"]
        ["UnifiedActionVector"] --> ["Dim_352_384"]
    end
    
    subgraph "Text2WorldCondition_Module"
        ["Action_Projection_Layer"]["First Linear Layer (384 to hidden_dim)"]
        ["Action_Embeddings"]
        ["Text_Conditioning"]
        ["Cross_Attention_Embeddings"]
    end
    
    ["Dim_0_29"] --> ["Action_Projection_Layer"]
    ["Dim_29_58"] --> ["Action_Projection_Layer"]
    ["Dim_58_101"] --> ["Action_Projection_Layer"]
    ["Dim_101_147"] --> ["Action_Projection_Layer"]
    ["Dim_147_169"] --> ["Action_Projection_Layer"]
    ["Dim_220_352"] --> ["Action_Projection_Layer"]
    ["Dim_352_384"] --> ["Action_Projection_Layer"]
    
    ["Action_Projection_Layer"] --> ["Action_Embeddings"]
    ["Action_Embeddings"] --> ["Cross_Attention_Embeddings"]
    ["Text_Conditioning"] --> ["Cross_Attention_Embeddings"]
```

**Sources**: [docs/POSTTRAIN.md:17-25](), [groot_dreams/data/dataset.py:108-130]()

## Dimension Allocation Table

The following table specifies the exact dimension ranges allocated to each robot platform and action representation type as defined in the post-training documentation:

| Dimension Range | Size | Robot/Action Type | Description |
|-----------------|------|-------------------|-------------|
| [0, 29) | 29 | Fourier GR-1 | GR-1 robot with Fourier teleoperation interface |
| [29, 58) | 29 | Manus GR-1 | GR-1 robot with retargeted actions from Manus gloves |
| [58, 101) | 43 | Unitree G1 | Unitree G1 humanoid robot actions |
| [101, 147) | 46 | Bimanual YAM | YAM bimanual manipulation robot |
| [147, 169) | 22 | AgiBot | AgiBot robot platform |
| [169, 220) | 51 | Reserved | Reserved for future robot platforms or extensions |
| [220, 352) | 132 | MANO | MANO hand pose parameters |
| [352, 384) | 32 | Latent Actions | Learned latent action representation from LAM |

**Total**: 384 dimensions

The reserved region [169, 220) provides flexibility for integrating additional robot platforms without requiring architectural changes to the primary `Text2WorldModelRectifiedFlow` or the underlying `MiniTrainDIT` network.

**Sources**: [docs/POSTTRAIN.md:17-25]()

## Robot-Specific Action Mappings

### GR-1 Robot (Fourier and Manus Variants)

The GR-1 robot has two separate dimension allocations:

- **Fourier GR-1** [0:29]: Actions from the Fourier teleoperation interface.
- **Manus GR-1** [29:58]: Actions retargeted from Manus gloves for more dexterous control.

Both representations use 29 dimensions. During post-training, experiments specify which variant to use via configuration files like `2b_480_640_gr1.yaml`.

### Unitree G1 [58:101]

The Unitree G1 humanoid robot uses 43 dimensions for full-body control. This includes coordinated control of arms, legs, torso, and end-effector positions. Configuration file: `2b_480_640_g1.yaml`.

### Bimanual YAM [101:147]

The YAM bimanual manipulation system uses 46 dimensions to represent dual-arm manipulation actions. This platform is designed for tabletop manipulation tasks. Configuration file: `2b_480_640_yam.yaml`.

### AgiBot [147:169]

The AgiBot platform uses 22 dimensions. This is a compact action representation. The data schema for AgiBot includes fields like `left_arm_joint_position`, `right_arm_joint_position`, `head_position`, and `robot_velocity`.

**Sources**: [docs/POSTTRAIN.md:8-14](), [docs/POSTTRAIN.md:17-25](), [shared_meta/AgiBot_modality.json:67-140]()

## MANO Hand Parameterization [220:352]

The MANO (hand Model with Articulated and Non-rigid defOrmations) representation occupies 132 dimensions. This allocation enables DreamDojo to model detailed hand manipulation actions, which is particularly relevant for egocentric human video understanding during the pretraining phase on the 44k hour human video dataset.

**Sources**: [docs/POSTTRAIN.md:24]()

## Latent Actions from LAM [352:384]

The final 32 dimensions are reserved for latent actions extracted by the Latent Action Model (LAM). LAM processes video inputs to produce learned 32-dimensional latent action representations (`z_rep`).

### Latent Action Data Flow

```mermaid
graph LR
    subgraph "LAM_Subsystem"
        ["Video_Input"] --> ["LAM_Encoder"]
        ["LAM_Encoder"] -- "24 Blocks" --> ["Latent_Z_Rep"]
        ["Latent_Z_Rep"] -- "32-dim" --> ["Action_Vector_Slicing"]
    end
    
    subgraph "Action_Space_Integration"
        ["Action_Vector_Slicing"] -- "Indices [352:384]" --> ["Unified_384_Vector"]
    end
    
    subgraph "Main_Model_Forward"
        ["Unified_384_Vector"] --> ["Action_Projection"]
        ["Action_Projection"] --> ["Text2WorldCondition"]
    end
```

During pretraining on human egocentric videos, LAM extracts these latent actions directly from video observations. During post-training on robot datasets, latent action extraction can be disabled (set to zero) to focus on the explicit robot action dimensions.

**Sources**: [docs/POSTTRAIN.md:7](), [docs/POSTTRAIN.md:25]()

## Implementation Architecture

### Action Projection Layer

The first layer of the action conditioning pathway is a linear projection that maps the full 384-dimensional action space to the model's hidden dimension. This design choice is mentioned explicitly in the documentation:

> "For simplicity of implementation, we set the dimension of the first action projection layer to 384. This will slightly increase computational requirements but makes checkpoint resuming easier."

The projection layer ensures that all robot platforms benefit from the same learned action embedding space, facilitating transfer learning.

### Configuration and Dataset Mapping

The `LeRobotSingleDataset` and its modality configurations handle the mapping of raw data to the model's expected input. The `ModalityConfig` class defines the keys to load and the delta indices for sampling.

- `dataset_path`: Path to the LeRobot formatted dataset [groot_dreams/data/dataset.py:83]().
- `modality_configs`: Configuration for each modality, including action keys [groot_dreams/data/dataset.py:84]().
- `embodiment_tag`: Identifies the robot type (e.g., GR1, G1) [groot_dreams/data/dataset.py:85]().

### Zero-Padding Strategy

During inference or training with a specific robot, only that robot's allocated dimensions contain meaningful values. All other dimensions are zero-padded. This approach provides:
- Simplified data pipeline implementation.
- Consistent tensor shapes across experiments.
- Easy checkpoint compatibility when switching between robots.

**Sources**: [docs/POSTTRAIN.md:17](), [groot_dreams/data/dataset.py:67-91]()

## Design Rationale and Benefits

### Unified Model Architecture
The 384-dimensional design allows training and deploying a single model architecture that supports multiple robot embodiments. This eliminates the need to maintain separate codebases or manage incompatible checkpoint formats for different robots.

### Checkpoint Compatibility
As noted in `POSTTRAIN.md`, the fixed 384-dimensional projection layer simplifies checkpoint resuming. A model pretrained on one robot platform or on the general human video dataset can be loaded and fine-tuned on another platform without architectural modifications.

### Extensibility
The reserved dimensions [169:220) provide a buffer for adding new robot platforms without breaking existing checkpoints. New robots can be integrated by allocating dimensions from the reserved range and creating a new configuration YAML file.

### Computational Considerations
The documentation acknowledges that the 384-dimensional projection "will slightly increase computational requirements" compared to using only the minimal dimensions needed for a specific robot. However, this overhead is acceptable given the benefits of unified architecture and simplified checkpoint management.

**Sources**: [docs/POSTTRAIN.md:17-25]()

## Usage in Post-Training

During post-training, the action space design integrates with the overall training pipeline as follows:

1. **Load Pretrained Checkpoint**: Set `load_path` in `cosmos_predict2/experiments/base/action.py` to the pretrained checkpoint (e.g., `iter_000140000`).
2. **Select Robot Configuration**: Choose the experiment config matching the target robot.
3. **Launch Training**: Use `launch.sh` with the selected configuration.

Example commands for each robot platform:
```bash
bash launch.sh dreamdojo_2b_480_640_gr1
bash launch.sh dreamdojo_2b_480_640_g1
bash launch.sh dreamdojo_2b_480_640_agibot
bash launch.sh dreamdojo_2b_480_640_yam
```

The training script automatically maps the robot's actions to the correct dimension range based on the `EmbodimentTag` and dataset configuration.

**Sources**: [docs/POSTTRAIN.md:3-15](), [groot_dreams/data/dataset.py:117-121]()

---

