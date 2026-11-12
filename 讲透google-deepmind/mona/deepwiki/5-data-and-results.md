<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/mona · page 5 Data and Results · fetched 2026-10-26 -->

# Data and Results

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/rollouts.textproto](data/R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/rollouts.textproto)
- [proto/rollout.proto](proto/rollout.proto)
- [src/file_handler.py](src/file_handler.py)

</details>



This document explains how experimental data is stored, organized, and accessed in the MONA research system. It covers the protocol buffer data formats used to store rollout results, the parameter-based file organization system, and how to interpret experimental outcomes.

For information about running experiments that generate this data, see [Experimental Approaches](#3). For details about analyzing results using the visualization tools, see [Results Analysis](#3.3).

## Data Storage Architecture

The MONA system uses a structured approach to store experimental data, with protocol buffers for serialization and a parameter-encoded directory structure for organization.

```mermaid
graph TB
    subgraph "Experimental Data Flow"
        EXP["Value Iteration Experiments<br/>(src/main.py)"] --> HANDLER["FileHandler<br/>(src/file_handler.py)"]
        PPO["PPO Experiments<br/>(ipynb/ppo.ipynb)"] --> HANDLER
    end
    
    subgraph "Data Serialization"
        HANDLER --> PROTO["Protocol Buffer Definitions<br/>(proto/rollout.proto)"]
        PROTO --> ROLLOUT["Rollout Messages"]
        PROTO --> STATS["RolloutStats Messages"]
        PROTO --> ITER["RolloutIteration Messages"]
    end
    
    subgraph "Storage Formats"
        ROLLOUT --> TEXTPROTO["rollouts.textproto<br/>(Human Readable)"]
        ROLLOUT --> BINARYPB["rollouts.pb<br/>(Binary Format)"]
        HANDLER --> NUMPY["value_matrix.npy<br/>(NumPy Arrays)"]
    end
    
    subgraph "File Organization"
        TEXTPROTO --> PARAMDIR["Parameter-Encoded Directories<br/>R=bad-V_init=good-noise_init=0.5..."]
        BINARYPB --> PARAMDIR
        NUMPY --> PARAMDIR
        
        PARAMDIR --> TRIAL1["rollouts.textproto"]
        PARAMDIR --> TRIAL2["rollouts_2.textproto"]
        PARAMDIR --> VALUE["value_matrix.npy"]
    end
    
    EXP -.-> PARAMDIR
    PPO -.-> PARAMDIR
```

Sources: [src/file_handler.py:86-287](), [proto/rollout.proto:16-51](), [data/R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/rollouts.textproto:1-50]()

## Protocol Buffer Data Formats

The system uses protocol buffers defined in `rollout.proto` to structure experimental data. These provide a standardized format for storing rollout trajectories, statistics, and experimental outcomes.

### Core Data Structures

| Message Type | Purpose | Key Fields |
|--------------|---------|------------|
| `Rollout` | Single episode trajectory | `initial_state`, `trajectory`, `num_boxes_in_hole` |
| `RolloutStats` | Aggregate statistics | `average_boxes_in_hole`, `box_milestones` |
| `RolloutIteration` | Results from one iteration | `rollouts[]`, `stats` |
| `RolloutIterations` | Complete experimental run | `iterations[]` |

### Rollout Message Structure

```mermaid
graph LR
    subgraph "Rollout Proto Structure"
        ROLLOUT["Rollout"] --> INITIAL["initial_state: int32<br/>Starting state ID"]
        ROLLOUT --> MILESTONES["steps_to_box_milestones<br/>map<int32, int32>"]
        ROLLOUT --> BOXES["num_boxes_in_hole: int32<br/>Final success count"]
        ROLLOUT --> TRAJ["trajectory: repeated int32<br/>State sequence (packed)"]
    end
    
    subgraph "Statistical Aggregation"
        STATS["RolloutStats"] --> AVG["average_boxes_in_hole<br/>float"]
        STATS --> BOX_MILE["box_milestones[]<br/>BoxMilestone messages"]
        BOX_MILE --> COUNTS["step_counts[]<br/>Steps to reach milestone"]
        BOX_MILE --> NUM_STATES["num_initial_states<br/>Frequency count"]
    end
```

Sources: [proto/rollout.proto:20-41]()

### Data Encoding Options

The `FileHandler` class supports two serialization formats through the `Encoding` enum:

- **TEXTPROTO** (`.textproto`): Human-readable format useful for debugging and manual inspection
- **BINARYPB** (`.pb`): Compact binary format for efficient storage and loading

Sources: [src/file_handler.py:32-40]()

## Parameter-Based File Organization

Experimental results are organized into directories whose names encode the experimental parameters. This allows for systematic organization and easy parameter-based filtering of results.

### Directory Naming Convention

The `FileHandler.get_full_directory()` method constructs directory names using the following pattern:

```
R={reward_function}-V_init={init_vf_name}-noise_init={init_noise_scale}-step_penalty={per_step_penalty}-shape={width}_{height}-boxes={max_boxes}
```

### Parameter Encoding Logic

```mermaid
graph TD
    subgraph "Parameter Processing"
        PARAMS["Experimental Parameters"] --> REWARD["reward_function<br/>Required: R=good|bad"]
        PARAMS --> VF["init_vf_name<br/>Optional: V_init=#name#"]
        PARAMS --> NOISE["init_noise_scale<br/>Optional: noise_init=0.5"]
        PARAMS --> STEPS["num_reward_steps<br/>Optional: R_steps=N"]
        PARAMS --> EXPLORE["explore_prob<br/>Optional: explore=0.1"]
        PARAMS --> BLOCKING["min_blocking_boxes<br/>Default=1: blocking_boxes=N"]
        PARAMS --> PENALTY["per_step_penalty<br/>Required: step_penalty=0.01"]
        PARAMS --> LIMIT["episode_step_limit<br/>Default=50: step_limit=N"]
        PARAMS --> SHAPE["board_shape<br/>Required: shape=4_4"]
        PARAMS --> BOXES["max_boxes<br/>Required: boxes=2"]
    end
    
    subgraph "Directory Construction"
        REWARD --> SUBDIR["Subdirectory Name"]
        VF --> SUBDIR
        NOISE --> SUBDIR
        STEPS --> SUBDIR
        EXPLORE --> SUBDIR
        BLOCKING --> SUBDIR
        PENALTY --> SUBDIR
        LIMIT --> SUBDIR
        SHAPE --> SUBDIR
        BOXES --> SUBDIR
        
        SUBDIR --> FULLPATH["data_dir/R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/"]
    end
```

Sources: [src/file_handler.py:97-151]()

### File Types per Directory

Each parameter directory contains:

- **Rollout files**: `rollouts.textproto`, `rollouts_2.textproto`, etc. (one per trial)
- **Value matrices**: `value_matrix.npy`, `value_matrix_2.npy`, etc. (when available)
- **Trial indexing**: Multiple trials use suffix `_N` for N > 1

Sources: [src/file_handler.py:74-84](), [src/file_handler.py:254-279]()

## Example Experimental Results

The provided rollout data demonstrates typical experimental outcomes in the Camera Dropbox environment. Each rollout shows how an agent's policy performs across different initial states.

### Rollout Interpretation

Looking at the example data from `R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/rollouts.textproto`:

```mermaid
graph LR
    subgraph "Successful Rollout Example"
        R1["Rollout 1<br/>initial_state: 772"] --> MILESTONE["steps_to_box_milestones<br/>key: 1, value: 39"]
        R1 --> SUCCESS["num_boxes_in_hole: 1<br/>Successfully got 1 box"]
        R1 --> TRAJ1["trajectory: [772, 637, 772, 637...]<br/>49-step sequence ending at state 0"]
        TRAJ1 --> TERM["State 0 = Terminal Success"]
    end
    
    subgraph "Failed Rollout Example"  
        R2["Rollout 2<br/>initial_state: 529"] --> NO_MILESTONE["No milestones<br/>(empty map)"]
        R2 --> FAIL["num_boxes_in_hole: 0<br/>Failed to achieve goal"]
        R2 --> TRAJ2["trajectory: [529, 445, 361...]<br/>Looping behavior, no termination"]
    end
```

Sources: [data/R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/rollouts.textproto:1-105]()

### Success Patterns

The example data reveals several behavioral patterns:

1. **Successful trajectories** reach state `0` (terminal success) after achieving box milestones
2. **Failed trajectories** show looping patterns between similar state values
3. **State transitions** represent agent movement and environment changes in the 4x4 grid
4. **Milestone tracking** records the number of steps required to get each box into the hole

### Behavioral Analysis

```mermaid
graph TB
    subgraph "Trajectory Analysis"
        INITIAL["Initial States<br/>772, 529, 793, etc."] --> BEHAVIOR["Agent Behavior Patterns"]
        
        BEHAVIOR --> SUCCESS["Success Pattern<br/>Linear progression to goal<br/>State 0 termination"]
        BEHAVIOR --> LOOP["Failure Pattern<br/>Repeated state cycles<br/>No progression to goal"]
        BEHAVIOR --> PARTIAL["Partial Success<br/>Some milestones achieved<br/>Incomplete goal fulfillment"]
        
        SUCCESS --> METRICS["Performance Metrics<br/>num_boxes_in_hole: 1<br/>steps_to_box_milestones"]
        LOOP --> METRICS2["Performance Metrics<br/>num_boxes_in_hole: 0<br/>No milestones"]
        PARTIAL --> METRICS3["Performance Metrics<br/>Mixed milestone achievement"]
    end
```

### Statistical Aggregation

The `RolloutStats` messages provide aggregate analysis across all rollouts in an iteration, including:

- **Average success rate**: `average_boxes_in_hole` across all initial states
- **Milestone distributions**: `BoxMilestone` entries showing step count histograms for reaching each box count
- **Initial state coverage**: `num_initial_states` showing how many starting positions were tested

Sources: [proto/rollout.proto:27-41](), [data/R=bad-V_init=good-noise_init=0.5-step_penalty=0.01-shape=4_4-boxes=2/rollouts.textproto:1-2800]()

---

