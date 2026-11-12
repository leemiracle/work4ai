<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SimplerEnv · page 7 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/octo_put_in_drawer_variant_agg.sh](scripts/octo_put_in_drawer_variant_agg.sh)
- [scripts/octo_put_in_drawer_visual_matching.sh](scripts/octo_put_in_drawer_visual_matching.sh)
- [scripts/rt1_put_in_drawer_variant_agg.sh](scripts/rt1_put_in_drawer_variant_agg.sh)
- [scripts/rt1_put_in_drawer_visual_matching.sh](scripts/rt1_put_in_drawer_visual_matching.sh)
- [tools/save_video_frame.py](tools/save_video_frame.py)

</details>



This document covers advanced configuration options, specialized evaluation scenarios, and expert-level usage patterns in SimplerEnv. It focuses on task-specific evaluation scripts, custom video processing workflows, and advanced rendering configurations for specialized research scenarios. For basic evaluation setup, see [Evaluation Framework](#4). For general tool usage, see [Tools and Utilities](#5).

## Task-Specific Evaluation Configurations

SimplerEnv provides specialized evaluation scripts that demonstrate advanced configuration patterns for specific manipulation tasks. These scripts showcase sophisticated parameter tuning and environment variations that go beyond basic policy evaluation.

### Drawer Operation Evaluations

The drawer operation task requires specific configurations due to the importance of visual depth cues and precise robot positioning. SimplerEnv includes dedicated scripts for both visual matching and variant aggregation approaches.

#### Visual Matching Configuration

The visual matching approach for drawer operations uses real background images and precise robot positioning to match real-world evaluation conditions.

```mermaid
graph TD
    subgraph "Visual Matching Pipeline"
        VM_SCRIPT["rt1_put_in_drawer_visual_matching.sh"]
        OCTO_SCRIPT["octo_put_in_drawer_visual_matching.sh"]
    end
    
    subgraph "Configuration Parameters"
        RT_ENABLE["--enable-raytracing"]
        URDF_VAR["urdf_version variations"]
        RGB_OVERLAY["--rgb-overlay-path"]
        PRECISE_POS["precise robot positioning"]
    end
    
    subgraph "Real World Data"
        REAL_IMG["real_inpainting/open_drawer_*.png"]
        STATIONS["A0, B0, C0 positions"]
    end
    
    subgraph "Evaluation Scenarios"
        SCENARIO_A["Position A0: x=0.644 y=-0.179"]
        SCENARIO_B["Position B0: x=0.652 y=0.009"] 
        SCENARIO_C["Position C0: x=0.665 y=0.224"]
    end
    
    VM_SCRIPT --> RT_ENABLE
    OCTO_SCRIPT --> RT_ENABLE
    VM_SCRIPT --> URDF_VAR
    VM_SCRIPT --> RGB_OVERLAY
    
    RGB_OVERLAY --> REAL_IMG
    PRECISE_POS --> STATIONS
    
    STATIONS --> SCENARIO_A
    STATIONS --> SCENARIO_B
    STATIONS --> SCENARIO_C
    
    SCENARIO_A --> REAL_IMG
    SCENARIO_B --> REAL_IMG
    SCENARIO_C --> REAL_IMG
```

Key configuration patterns include:

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `--enable-raytracing` | Enable realistic shadows for depth perception | Required for drawer tasks |
| `--rgb-overlay-path` | Real background image overlay | `./ManiSkill2_real2sim/data/real_inpainting/open_drawer_a0.png` |
| `urdf_version` | Visual appearance variations | `recolor_cabinet_visual_matching_1` |
| `station_name` | Cabinet configuration | `mk_station_recolor` |
| Robot positioning | Precise real-world alignment | x=0.644, y=-0.179 for station A0 |

**Sources:** [scripts/rt1_put_in_drawer_visual_matching.sh:1-71](), [scripts/octo_put_in_drawer_visual_matching.sh:1-67]()

#### Variant Aggregation Configuration

The variant aggregation approach systematically varies environmental conditions to test policy robustness across different scenarios.

```mermaid
graph TD
    subgraph "Variant Aggregation Pipeline"
        VAR_SCRIPT["rt1_put_in_drawer_variant_agg.sh"]
        OCTO_VAR["octo_put_in_drawer_variant_agg.sh"]
    end
    
    subgraph "Base Configuration"
        BASE_SCENE["frl_apartment_stage_simple"]
        BASE_ARGS["--enable-raytracing model_ids=apple"]
    end
    
    subgraph "Background Variations"
        BG_MODERN["modern_bedroom_no_roof"]
        BG_OFFICE["modern_office_no_roof"]
    end
    
    subgraph "Lighting Variations"
        LIGHT_BRIGHT["light_mode=brighter"]
        LIGHT_DARK["light_mode=darker"]
    end
    
    subgraph "Station Variations"
        STATION2["station_name=mk_station2"]
        STATION3["station_name=mk_station3"]
    end
    
    VAR_SCRIPT --> BASE_SCENE
    OCTO_VAR --> BASE_SCENE
    BASE_SCENE --> BASE_ARGS
    
    VAR_SCRIPT --> BG_MODERN
    VAR_SCRIPT --> BG_OFFICE
    VAR_SCRIPT --> LIGHT_BRIGHT
    VAR_SCRIPT --> LIGHT_DARK
    VAR_SCRIPT --> STATION2
    VAR_SCRIPT --> STATION3
```

The variant aggregation approach tests policies across multiple conditions:

- **Base Setup**: Standard apartment scene with ray-tracing enabled
- **Background Variations**: Modern bedroom and office scenes
- **Lighting Variations**: Brighter and darker lighting conditions
- **Station Variations**: Different cabinet configurations (mk_station2, mk_station3)

**Sources:** [scripts/rt1_put_in_drawer_variant_agg.sh:1-84](), [scripts/octo_put_in_drawer_variant_agg.sh:1-81]()

## Custom Video Processing Workflows

SimplerEnv provides tools for extracting and processing video frames from evaluation results, enabling detailed analysis of policy behavior and failure modes.

### Frame Extraction Tool

The `save_video_frame.py` tool enables extraction of specific frames from evaluation videos for analysis and visualization purposes.

```mermaid
graph LR
    subgraph "Input"
        VIDEO["evaluation video.mp4"]
        FRAME_NUM["frame number"]
    end
    
    subgraph "Processing Pipeline"
        MEDIA_READ["mediapy.read_video()"]
        FRAME_SELECT["video[frame_num]"]
        PIL_SAVE["PIL.Image.save()"]
    end
    
    subgraph "Output"
        FRAME_IMG["extracted frame.png"]
    end
    
    VIDEO --> MEDIA_READ
    FRAME_NUM --> FRAME_SELECT
    MEDIA_READ --> FRAME_SELECT
    FRAME_SELECT --> PIL_SAVE
    PIL_SAVE --> FRAME_IMG
```

**Usage Pattern:**
```bash
python tools/save_video_frame.py \
  -i /path/to/evaluation/video.mp4 \
  -o /path/to/output/frame.png \
  -n 0  # frame number
```

The tool supports:
- **Video Input**: Any evaluation video generated by SimplerEnv
- **Frame Selection**: Specific frame number (default: 0 for first frame)
- **Output Format**: PNG image file
- **Integration**: Can be used in batch processing scripts for systematic frame extraction

**Sources:** [tools/save_video_frame.py:1-43]()

### Advanced Video Analysis

Frame extraction enables several advanced analysis workflows:

| Use Case | Frame Selection | Analysis Purpose |
|----------|----------------|------------------|
| Initial conditions | Frame 0 | Verify environment setup |
| Failure analysis | Final frames | Understand failure modes |
| Action visualization | Key action frames | Analyze policy decisions |
| Success comparison | Final frames | Compare successful vs failed episodes |

## Advanced Rendering Configuration

SimplerEnv supports advanced rendering options that are crucial for specific evaluation scenarios, particularly those requiring realistic visual depth cues.

### Ray-Tracing Configuration

Ray-tracing rendering is essential for tasks like drawer operations where policies rely on shadows and lighting for depth perception.

```mermaid
graph TD
    subgraph "Rendering Pipeline"
        RT_FLAG["--enable-raytracing"]
        SHADER_DIR["shader_dir=rt"]
        LIGHT_MODE["light_mode parameter"]
    end
    
    subgraph "Visual Effects"
        SHADOWS["realistic shadows"]
        REFLECTIONS["surface reflections"]
        DEPTH_CUES["depth perception cues"]
    end
    
    subgraph "Task Requirements"
        DRAWER_TASK["drawer operations"]
        DEPTH_POLICY["depth-dependent policies"]
        VISUAL_MATCH["visual matching scenarios"]
    end
    
    RT_FLAG --> SHADOWS
    SHADER_DIR --> REFLECTIONS
    LIGHT_MODE --> DEPTH_CUES
    
    SHADOWS --> DRAWER_TASK
    DEPTH_CUES --> DEPTH_POLICY
    REFLECTIONS --> VISUAL_MATCH
```

**Key Configuration Parameters:**

| Parameter | Values | Purpose |
|-----------|--------|---------|
| `--enable-raytracing` | Boolean flag | Enable ray-tracing renderer |
| `shader_dir` | `rt` | Specify ray-tracing shader directory |
| `light_mode` | `simple`, `brighter`, `darker` | Control lighting intensity |
| `disable_bad_material` | `True` | Remove problematic materials |

**Sources:** [scripts/rt1_put_in_drawer_visual_matching.sh:1-71](), [scripts/rt1_put_in_drawer_variant_agg.sh:1-84]()

### Environment Build Parameters

Advanced environment configuration uses the `--additional-env-build-kwargs` parameter to pass complex configuration options:

```mermaid
graph TD
    subgraph "Build Parameters"
        STATION["station_name"]
        LIGHT["light_mode"]
        URDF["urdf_version"]
        MODEL["model_ids"]
        MATERIALS["disable_bad_material"]
    end
    
    subgraph "Station Configurations"
        MK_RECOLOR["mk_station_recolor"]
        MK_STATION2["mk_station2"]
        MK_STATION3["mk_station3"]
    end
    
    subgraph "Visual Variants"
        RECOLOR1["recolor_cabinet_visual_matching_1"]
        RECOLOR2["recolor_tabletop_visual_matching_1"]
        RECOLOR3["recolor_tabletop_visual_matching_2"]
    end
    
    subgraph "Object Models"
        APPLE["apple"]
        BAKED_APPLE["baked_apple_v2"]
    end
    
    STATION --> MK_RECOLOR
    STATION --> MK_STATION2
    STATION --> MK_STATION3
    
    URDF --> RECOLOR1
    URDF --> RECOLOR2
    URDF --> RECOLOR3
    
    MODEL --> APPLE
    MODEL --> BAKED_APPLE
```

**Advanced Parameter Combinations:**

```bash
# Visual matching configuration
EXTRA_ARGS="--enable-raytracing --additional-env-build-kwargs \
  station_name=mk_station_recolor \
  light_mode=simple \
  disable_bad_material=True \
  urdf_version=recolor_cabinet_visual_matching_1 \
  model_ids=baked_apple_v2"

# Variant aggregation configuration
EXTRA_ARGS="--additional-env-build-kwargs \
  shader_dir=rt \
  light_mode=brighter \
  model_ids=apple"
```

**Sources:** [scripts/rt1_put_in_drawer_visual_matching.sh:21-23](), [scripts/rt1_put_in_drawer_variant_agg.sh:62-68]()

## Expert Configuration Patterns

### Multi-Checkpoint Evaluation

Advanced evaluation scripts demonstrate patterns for testing multiple policy checkpoints across various conditions:

```mermaid
graph TD
    subgraph "Checkpoint Management"
        CKPT_ARRAY["declare -a ckpt_paths"]
        CKPT1["rt_1_tf_trained_for_000400120"]
        CKPT2["rt_1_tf_trained_for_000058240"]
        CKPT3["rt_1_x_tf_trained_for_002272480_step"]
        CKPT4["rt_1_tf_trained_for_000001120"]
    end
    
    subgraph "Nested Evaluation Loops"
        OUTER_LOOP["for ckpt_path in ckpt_paths"]
        MIDDLE_LOOP["for env_name in env_names"]
        INNER_LOOP["for scene_name in scene_names"]
        EVAL_FUNC["EvalSim() function"]
    end
    
    subgraph "Systematic Testing"
        ALL_COMBOS["all checkpoint × environment × scene combinations"]
        COMPREHENSIVE["comprehensive robustness evaluation"]
    end
    
    CKPT_ARRAY --> CKPT1
    CKPT_ARRAY --> CKPT2
    CKPT_ARRAY --> CKPT3
    CKPT_ARRAY --> CKPT4
    
    OUTER_LOOP --> MIDDLE_LOOP
    MIDDLE_LOOP --> INNER_LOOP
    INNER_LOOP --> EVAL_FUNC
    
    EVAL_FUNC --> ALL_COMBOS
    ALL_COMBOS --> COMPREHENSIVE
```

This pattern enables systematic evaluation across:
- Multiple policy checkpoints from different training stages
- Various environment configurations
- Different scene backgrounds and lighting conditions
- Comprehensive robustness testing

**Sources:** [scripts/rt1_put_in_drawer_variant_agg.sh:5-10](), [scripts/rt1_put_in_drawer_variant_agg.sh:36-40]()

### Precise Robot Initialization

Advanced scripts demonstrate precise robot positioning for matching real-world evaluation conditions:

| Position | X Coordinate | Y Coordinate | Rotation (RPY) | Purpose |
|----------|--------------|--------------|----------------|---------|
| A0 | 0.644 | -0.179 | -0.03 rad | Match real station A |
| B0 | 0.652 | 0.009 | 0.0 rad | Match real station B |
| C0 | 0.665 | 0.224 | 0.0 rad | Match real station C |

The positioning parameters use range specifications for systematic variation:
- `--robot-init-x 0.644 0.644 1`: Fixed X position
- `--robot-init-y -0.179 -0.179 1`: Fixed Y position  
- `--robot-init-rot-rpy-range 0 0 1 0 0 1 -0.03 -0.03 1`: Fixed rotation

**Sources:** [scripts/rt1_put_in_drawer_visual_matching.sh:29-33](), [scripts/rt1_put_in_drawer_visual_matching.sh:40-44]()

---

