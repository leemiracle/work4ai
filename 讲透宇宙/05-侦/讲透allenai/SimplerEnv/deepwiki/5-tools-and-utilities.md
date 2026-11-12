<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SimplerEnv · page 5 Tools and Utilities · fetched 2026-10-26 -->

# Tools and Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [simpler_env/utils/metrics.py](simpler_env/utils/metrics.py)
- [simpler_env/utils/visualization.py](simpler_env/utils/visualization.py)
- [tools/calc_metrics.py](tools/calc_metrics.py)
- [tools/sysid/sysid.py](tools/sysid/sysid.py)
- [tools/visualize_dataset.py](tools/visualize_dataset.py)

</details>



This page covers the comprehensive set of tools and utilities available in SimplerEnv for system identification, performance analysis, visualization, and debugging. These tools support the core evaluation pipeline by providing metrics calculation, robot parameter optimization, and visualization capabilities.

For information about running evaluations with these tools, see [Evaluation Framework](#4). For policy-specific inference tools, see [Policy Models](#3).

## Metrics and Performance Analysis

SimplerEnv provides sophisticated tools for calculating and analyzing evaluation metrics that compare simulated and real robot performance.

### Core Metrics Framework

The metrics system centers around two key evaluation measures:

| Metric | Purpose | Function |
|--------|---------|----------|
| **Mean Maximum Rank Violation (MMRV)** | Measures ranking consistency between sim and real | `mean_maximum_rank_violation()` |
| **Pearson Correlation** | Measures linear correlation between performances | `pearson_correlation()` |

```mermaid
graph TD
    subgraph "Performance Data Sources"
        REAL_PERF["REAL_PERF Dictionary"]
        SIMPLER_PERF["SIMPLER_PERF Dictionary"]
        USER_DATA["User Evaluation Results"]
    end
    
    subgraph "Metrics Calculation"
        MMRV_FUNC["mean_maximum_rank_violation()"]
        PEARSON_FUNC["pearson_correlation()"]
        KRUSKAL_FUNC["print_all_kruskal_results()"]
    end
    
    subgraph "Analysis Tools"
        CALC_METRICS["calc_metrics.py"]
        GET_DIR_STATS["get_dir_stats()"]
        CONSTRUCT_TRIALS["construct_unordered_trial_results()"]
    end
    
    REAL_PERF --> MMRV_FUNC
    SIMPLER_PERF --> MMRV_FUNC
    USER_DATA --> MMRV_FUNC
    
    REAL_PERF --> PEARSON_FUNC
    SIMPLER_PERF --> PEARSON_FUNC
    USER_DATA --> PEARSON_FUNC
    
    MMRV_FUNC --> CALC_METRICS
    PEARSON_FUNC --> CALC_METRICS
    KRUSKAL_FUNC --> CALC_METRICS
    
    GET_DIR_STATS --> CONSTRUCT_TRIALS
    CONSTRUCT_TRIALS --> KRUSKAL_FUNC
```

**Metrics Calculation Workflow**

The `calc_metrics.py` tool provides a command-line interface for computing evaluation metrics:

Sources: [tools/calc_metrics.py:1-35](), [simpler_env/utils/metrics.py:134-163]()

### Performance Data Management

The metrics system includes comprehensive performance data for both Google Robot and WidowX platforms:

- **Real Performance Data**: Stored in `REAL_PERF` dictionary with task-policy mappings
- **Simulated Performance Data**: Stored in `SIMPLER_PERF` dictionary for baseline comparisons
- **Statistical Analysis**: Kruskal-Wallis tests for comparing trial-by-trial success rates

```mermaid
graph LR
    subgraph "Task Categories"
        GOOGLE_TASKS["google_robot_pick_coke_can<br/>google_robot_move_near<br/>google_robot_open_drawer<br/>google_robot_close_drawer<br/>google_robot_place_apple_in_closed_top_drawer"]
        WIDOWX_TASKS["widowx_spoon_on_towel<br/>widowx_carrot_on_plate<br/>widowx_stack_cube<br/>widowx_put_eggplant_in_basket"]
    end
    
    subgraph "Policy Models"
        RT_POLICIES["rt-2-x<br/>rt-1-converged<br/>rt-1-15pct<br/>rt-1-x<br/>rt-1-begin"]
        OCTO_POLICIES["octo-base<br/>octo-small"]
    end
    
    subgraph "Performance Storage"
        REAL_DICT["REAL_PERF[task][policy]"]
        SIM_DICT["SIMPLER_PERF[task][policy]"]
    end
    
    GOOGLE_TASKS --> REAL_DICT
    WIDOWX_TASKS --> REAL_DICT
    RT_POLICIES --> REAL_DICT
    OCTO_POLICIES --> REAL_DICT
    
    GOOGLE_TASKS --> SIM_DICT
    WIDOWX_TASKS --> SIM_DICT
    RT_POLICIES --> SIM_DICT
    OCTO_POLICIES --> SIM_DICT
```

**Directory-Based Result Analysis**

The `get_dir_stats()` function automatically extracts success/failure statistics from evaluation video files:

Sources: [simpler_env/utils/metrics.py:7-68](), [simpler_env/utils/metrics.py:201-229]()

## System Identification (SysID)

The SysID module provides automated optimization of robot physical parameters to improve simulation accuracy.

### SysID Optimization Process

The system identification process optimizes robot arm stiffness and damping parameters using simulated annealing:

```mermaid
graph TD
    subgraph "Input Data"
        DATASET["Demonstration Dataset<br/>(pickle format)"]
        ROBOT_TYPE["Robot Type<br/>(google_robot_static | widowx)"]
    end
    
    subgraph "Parameter Optimization"
        SA_OPT["Simulated Annealing<br/>sa.minimize()"]
        PARAM_BOUNDS["Parameter Bounds<br/>stiffness_low/high<br/>damping_low/high"]
        INIT_VALUES["Initial Values<br/>init_stiffness<br/>init_damping"]
    end
    
    subgraph "Simulation Loop"
        EP_PROCESS["calc_pose_err_single_ep()"]
        PARALLEL_POOL["Multiprocessing Pool<br/>(up to 18 processes)"]
        POSE_ERROR["TCP Pose Error<br/>Translation + Rotation"]
    end
    
    subgraph "Control Modes"
        GOOGLE_MODE["arm_pd_ee_delta_pose_align_interpolate_by_planner_gripper_pd_joint_pos"]
        WIDOWX_MODE["arm_pd_ee_target_delta_pose_align2_gripper_pd_joint_pos"]
    end
    
    DATASET --> EP_PROCESS
    ROBOT_TYPE --> EP_PROCESS
    
    SA_OPT --> PARAM_BOUNDS
    PARAM_BOUNDS --> INIT_VALUES
    INIT_VALUES --> EP_PROCESS
    
    EP_PROCESS --> PARALLEL_POOL
    PARALLEL_POOL --> POSE_ERROR
    POSE_ERROR --> SA_OPT
    
    ROBOT_TYPE --> GOOGLE_MODE
    ROBOT_TYPE --> WIDOWX_MODE
    GOOGLE_MODE --> EP_PROCESS
    WIDOWX_MODE --> EP_PROCESS
```

**SysID Parameter Optimization**

The optimization process minimizes 6D pose errors by adjusting:

- **Stiffness Parameters**: Joint-specific stiffness values within defined bounds
- **Damping Parameters**: Joint-specific damping coefficients
- **Control Frequency**: Robot-specific simulation and control frequencies
- **Error Metrics**: Combined translation and rotation error minimization

Sources: [tools/sysid/sysid.py:1-14](), [tools/sysid/sysid.py:143-177](), [tools/sysid/sysid.py:180-269]()

### Robot-Specific Configuration

The SysID system supports different robot platforms with specialized parameter ranges:

| Robot | Control Mode | Sim Freq | Control Freq | Joint Count |
|-------|-------------|----------|--------------|-------------|
| `google_robot_static` | `arm_pd_ee_delta_pose_align_interpolate_by_planner_gripper_pd_joint_pos` | 252 Hz | 3 Hz | 7 (+ 2 camera) |
| `widowx` | `arm_pd_ee_target_delta_pose_align2_gripper_pd_joint_pos` | 500 Hz | 5 Hz | 6 |

Sources: [tools/sysid/sysid.py:16-43](), [tools/sysid/sysid.py:199-238]()

## Visualization and Dataset Tools

SimplerEnv provides comprehensive visualization tools for dataset analysis, video generation, and trajectory plotting.

### Video Generation and Processing

The visualization system supports multiple video formats and processing workflows:

```mermaid
graph TD
    subgraph "Input Sources"
        DATASET_IMAGES["Dataset Images<br/>(TensorFlow format)"]
        NUMPY_ARRAYS["NumPy Image Arrays"]
        PIL_IMAGES["PIL Image Objects"]
    end
    
    subgraph "Video Creation"
        WRITE_VIDEO["write_video()"]
        MEDIAPY["mediapy.write_video()"]
        PATH_MANAGEMENT["Path Management<br/>Auto-create directories"]
    end
    
    subgraph "Visualization Types"
        GT_VIDEOS["Ground Truth Videos<br/>{dataset}_vis/{i}_gt.mp4"]
        ACTION_PLOTS["Action Trajectory Plots<br/>plot_pred_and_gt_action_trajectory()"]
        DATASET_VIS["Dataset Visualization<br/>visualize_dataset.py"]
    end
    
    subgraph "Supported Datasets"
        FRACTAL["fractal20220817_data"]
        BRIDGE["bridge"]
        ROBO_NET["robo_net"]
        LANG_TABLE["language_table"]
    end
    
    DATASET_IMAGES --> WRITE_VIDEO
    NUMPY_ARRAYS --> WRITE_VIDEO
    PIL_IMAGES --> WRITE_VIDEO
    
    WRITE_VIDEO --> MEDIAPY
    MEDIAPY --> PATH_MANAGEMENT
    
    WRITE_VIDEO --> GT_VIDEOS
    WRITE_VIDEO --> ACTION_PLOTS
    WRITE_VIDEO --> DATASET_VIS
    
    FRACTAL --> DATASET_VIS
    BRIDGE --> DATASET_VIS
    ROBO_NET --> DATASET_VIS
    LANG_TABLE --> DATASET_VIS
```

**Dataset Visualization Workflow**

The `visualize_dataset.py` tool processes TensorFlow Datasets and generates video summaries:

Sources: [tools/visualize_dataset.py:1-31](), [simpler_env/utils/visualization.py:19-29]()

### Action Trajectory Analysis

The trajectory plotting system provides detailed analysis of predicted vs ground truth actions:

- **Action Dimensions**: `world_vector`, `rotation_delta`, `gripper_closedness_action`, `terminate_episode`
- **Visualization Layout**: Synchronized image strips with multi-subplot action plots
- **Comparison Mode**: Overlaid predicted and ground truth trajectories

```mermaid
graph LR
    subgraph "Action Components"
        WORLD_VEC["world_vector<br/>(x, y, z)"]
        ROT_DELTA["rotation_delta<br/>(roll, pitch, yaw)"]
        GRIPPER["gripper_closedness_action"]
        TERMINATE["terminate_episode"]
    end
    
    subgraph "Plotting System"
        SUBPLOT_MOSAIC["plt.subplot_mosaic()"]
        TIME_SERIES["Time Series Plots"]
        IMAGE_STRIP["Stacked Image Strip"]
    end
    
    subgraph "Output Format"
        FIGURE_LAYOUT["45x10 inch Figure"]
        ACTION_PLOTS["Individual Action Subplots"]
        LEGEND["GT vs Predicted Legend"]
    end
    
    WORLD_VEC --> SUBPLOT_MOSAIC
    ROT_DELTA --> SUBPLOT_MOSAIC
    GRIPPER --> SUBPLOT_MOSAIC
    TERMINATE --> SUBPLOT_MOSAIC
    
    SUBPLOT_MOSAIC --> TIME_SERIES
    TIME_SERIES --> IMAGE_STRIP
    
    TIME_SERIES --> FIGURE_LAYOUT
    IMAGE_STRIP --> ACTION_PLOTS
    ACTION_PLOTS --> LEGEND
```

**Trajectory Plotting Configuration**

Sources: [simpler_env/utils/visualization.py:31-90](), [tools/visualize_dataset.py:32-59]()

## Development and Debugging Utilities

The utility framework includes several helper functions for development and debugging:

### File and Path Management

- **Directory Statistics**: `get_dir_stats()` extracts success/failure counts from video filenames
- **Pattern Matching**: Configurable success/failure detection patterns
- **Recursive Search**: Glob-based recursive file discovery

### Statistical Analysis Tools

- **Trial Construction**: `construct_unordered_trial_results()` converts success rates to trial arrays
- **Kruskal-Wallis Testing**: Statistical significance testing between simulation and real results
- **Result Aggregation**: Automated collection and analysis of evaluation outcomes

### Color and Font Resources

The visualization system includes predefined palettes and font resources:

- **Color Palette**: Deterministic random color generation for consistent visualization
- **Font Support**: Ubuntu Mono font for consistent text rendering
- **Image Processing**: Binary dilation and drawing utilities

Sources: [simpler_env/utils/metrics.py:189-229](), [simpler_env/utils/visualization.py:1-17]()

---

