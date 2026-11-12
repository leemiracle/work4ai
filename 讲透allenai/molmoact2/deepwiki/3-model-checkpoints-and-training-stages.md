<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/molmoact2 · page 3 Model Checkpoints and Training Stages · fetched 2026-10-26 -->

# Model Checkpoints and Training Stages

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



MolmoAct2 models are released in a tiered structure representing the progression from a general-purpose vision-language model to a specialized robotic controller. This hierarchy allows researchers and engineers to enter the pipeline at different stages depending on whether they intend to perform foundational pre-training, task-specific fine-tuning, or direct deployment on supported hardware.

The training pipeline transitions from discrete token prediction (for reasoning and depth) to continuous flow-matching (for precise action control) [README.md:35-36]().

## Training Progression Overview

The following diagram illustrates the relationship between the released checkpoints and the training stages they represent.

### Model Lineage and Stage Transitions
```mermaid
graph TD
    subgraph "Stage 1: Embodied Reasoning"
        ER["Molmo2-ER (Backbone)"]
    end

    subgraph "Stage 2: VLA Pre-training"
        PT["MolmoAct2-Pretrain (Discrete VLA)"]
    end

    subgraph "Stage 3: Foundation Action Training"
        MA2["MolmoAct2 (Flow-Matching)"]
        MA2T["MolmoAct2-Think (Depth + Flow)"]
    end

    subgraph "Stage 4: Deployment Fine-tuning"
        MA2D["MolmoAct2-DROID"]
        MA2Y["MolmoAct2-BimanualYAM"]
        MA2S["MolmoAct2-SO100_101"]
        MA2L["MolmoAct2-LIBERO"]
        MA2TL["MolmoAct2-Think-LIBERO"]
    end

    ER --> PT
    PT --> MA2
    PT --> MA2T
    MA2 --> MA2D
    MA2 --> MA2Y
    MA2 --> MA2S
    MA2 --> MA2L
    MA2T --> MA2TL

    style ER stroke-dasharray: 5 5
    style PT stroke-dasharray: 5 5
```
**Sources:** [README.md:50-67]()

## Checkpoint Categories

### Base (Foundation) Checkpoints
These checkpoints serve as the starting points for further development. They range from the `Molmo2-ER` backbone, which contains no action-specific heads, to `MolmoAct2`, which is ready for robotic fine-tuning using the continuous action expert [README.md:46-55]().

*   **Molmo2-ER**: The vision-language foundation trained on spatial and 3D reasoning.
*   **MolmoAct2-Pretrain**: A discrete autoregressive version used for internal training stages.
*   **MolmoAct2**: The standard foundation for robot fine-tuning.
*   **MolmoAct2-Think**: A variant that incorporates depth-token reasoning for improved geometric understanding.

For detailed specifications and HuggingFace paths, see **[Base (Foundation) Checkpoints](#3.1)**.

### Fine-Tuned Deployment Checkpoints
These models have been trained on specific robotics datasets (e.g., DROID, LIBERO, or YAM) and are optimized for direct inference or near-neighbor transfer learning [README.md:57-68]().

*   **Hardware-Specific**: Checkpoints for Franka (DROID), SO-100/101, and Bimanual YAM.
*   **Benchmark-Specific**: Optimized versions for the LIBERO simulation suites.

For hardware configurations and action conventions, see **[Fine-Tuned Deployment Checkpoints](#3.2)**.

## Integration with Training Workflows

All MolmoAct2 checkpoints are compatible with the `allenai/lerobot` framework. The repository includes a submodule pinned to the `molmoact2-policy` branch, which provides the necessary `lerobot` policy classes to load these checkpoints for continued training or evaluation [README.md:81-83]().

### Mapping Code Entities to Training Stages
```mermaid
graph LR
    subgraph "Checkpoints (HuggingFace)"
        HF_BASE["allenai/MolmoAct2"]
        HF_FT["allenai/MolmoAct2-DROID"]
    end

    subgraph "LeRobot Integration (Code)"
        sub["lerobot/ submodule"]
        branch["branch: molmoact2-policy"]
    end

    subgraph "Action Logic"
        FM["Flow-Matching Expert"]
        DT["Depth-Token Generator"]
    end

    HF_BASE -- "Loaded by" --> sub
    HF_FT -- "Loaded by" --> sub
    sub -- "Implements" --> FM
    HF_BASE -- "Optional" --> DT
```
**Sources:** [README.md:39-41](), [README.md:81-83]()

## Summary Table

| Stage | Model Name | Primary Use Case |
| :--- | :--- | :--- |
| **Backbone** | `Molmo2-ER` | Starting point for new VLA architectures [README.md:55](). |
| **Pre-training** | `MolmoAct2-Pretrain` | Continuing discrete VLA training [README.md:54](). |
| **Foundation** | `MolmoAct2` | Default starting point for new robot embodiments [README.md:52](). |
| **Reasoning** | `MolmoAct2-Think` | Tasks requiring explicit geometric reasoning (depth) [README.md:53](). |
| **Deployment** | `MolmoAct2-[Variant]` | Direct inference or fine-tuning for specific hardware [README.md:63-67](). |

**Sources:** [README.md:50-67]()

---

