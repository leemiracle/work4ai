> 来源: [https://deepwiki.com/rl-tools/rl-tools/5-zoo-system](https://deepwiki.com/rl-tools/rl-tools/5-zoo-system)
> DeepWiki rl-tools/rl-tools | Last indexed: 2 February 2026 (a0aef4

# Zoo System

  Relevant source files 
 - [include/rl_tools/rl/loop/steps/extrack/operations_cpu.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/loop/steps/extrack/operations_cpu.h)
 - [include/rl_tools/rl/loop/steps/extrack/state.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/loop/steps/extrack/state.h)
 - [src/rl/environments/l2f/dr_sac/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/l2f/dr_sac/CMakeLists.txt)
 - [src/rl/environments/l2f/dr_sac/l2f_dr_sac.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/l2f/dr_sac/l2f_dr_sac.cpp)
 - [src/rl/zoo/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/CMakeLists.txt)
 - [src/rl/zoo/l2f/environment_tiny.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/environment_tiny.h)
 - [src/rl/zoo/l2f/plot_learning_curves.py](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/plot_learning_curves.py)
 - [src/rl/zoo/l2f/sac.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/sac.h)
 - [src/rl/zoo/l2f/sac_tiny.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/sac_tiny.h)
 - [src/rl/zoo/zoo.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp)
 - [src/rl/zoo/zoo_cli.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo_cli.cpp)
 
  The Zoo System is RLtools' centralized training entry point that implements a compile-time algorithm-environment composition framework. It provides standardized experiment orchestration, configuration management, and result collection across multiple reinforcement learning algorithms and environments.

 For information about specific algorithms supported by the Zoo system, see [Reinforcement Learning Algorithms](https://deepwiki.com/rl-tools/rl-tools/2-reinforcement-learning-algorithms). For environment details, see [Environments](https://deepwiki.com/rl-tools/rl-tools/4-environments).

 
## Architecture Overview

 The Zoo System uses a compile-time configuration approach where each algorithm-environment pair is compiled into a separate executable. This design eliminates runtime polymorphism overhead while enabling algorithm-specific optimizations.

 
### Zoo System High-Level Architecture

 
```

```

 Sources: [src/rl/zoo/zoo.cpp131-217](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L131-L217) [src/rl/zoo/CMakeLists.txt1-154](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/CMakeLists.txt#L1-L154) [src/rl/zoo/zoo_cli.cpp1-34](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo_cli.cpp#L1-L34)

 
### FACTORY Pattern for Algorithm-Environment Composition

 The Zoo system uses a `FACTORY` template pattern to compose algorithms with environments. Each algorithm-environment combination defines a `FACTORY` class that produces the necessary type configurations.

 
### FACTORY Pattern Structure

 
```

```

 Sources: [src/rl/zoo/l2f/sac_tiny.h13-71](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/sac_tiny.h#L13-L71) [src/rl/zoo/l2f/sac.h7-58](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/sac.h#L7-L58)

 Each `FACTORY` exposes a `LOOP_CORE_CONFIG` type that encapsulates the complete algorithm-environment configuration.

 
## Compile-Time Configuration System

 The Zoo system uses preprocessor directives to select algorithm-environment combinations at compile time. The [src/rl/zoo/zoo.cpp131-217](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L131-L217) file contains nested `#if defined` blocks that resolve to a specific `LOOP_CORE_CONFIG` type based on compile definitions.

 
### Configuration Resolution in zoo.cpp

 The configuration resolution follows this pattern:

 
```

```

 
### Build System Configuration

 The [src/rl/zoo/CMakeLists.txt1-154](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/CMakeLists.txt#L1-L154) defines separate executables for each combination:

 
| Executable | Algorithm Definition | Environment Definition |
|---|---|---|
| rl_zoo_pendulum_v1_sac | RL_TOOLS_RL_ZOO_ALGORITHM_SAC | RL_TOOLS_RL_ZOO_ENVIRONMENT_PENDULUM_V1 |
| rl_zoo_l2f_td3 | RL_TOOLS_RL_ZOO_ALGORITHM_TD3 | RL_TOOLS_RL_ZOO_ENVIRONMENT_L2F |
| rl_zoo_ant_v4_ppo | RL_TOOLS_RL_ZOO_ALGORITHM_PPO | RL_TOOLS_RL_ZOO_ENVIRONMENT_ANT_V4 |

 Each executable is built with:

 
```

```

 This approach provides:

 
 - **Zero runtime overhead**: Algorithm dispatch is resolved at compile time
 - **Compiler optimizations**: Each executable can be fully optimized for its specific configuration
 - **Clear dependencies**: Each combination's dependencies are explicit
 - **Type safety**: Mismatched algorithm-environment configurations fail at compile time
 
 Sources: [src/rl/zoo/zoo.cpp131-217](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L131-L217) [src/rl/zoo/CMakeLists.txt10-154](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/CMakeLists.txt#L10-L154)

 
## Running Experiments

 Zoo executables are invoked through a command-line interface that supports multiple seeds and experiment tracking configuration.

 
### Command-Line Interface

 The [src/rl/zoo/zoo_cli.cpp1-34](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo_cli.cpp#L1-L34) entry point parses command-line arguments:

 
```

```

 **Command-line options:**

 
 - `-s, --seed`: Initial seed value (default: 0)
 - `-n, --n_seeds`: Number of seeds to run (default: 1)
 - `--e, --extrack`: Base path for experiment tracking
 - `--ee, --extrack-experiment`: Experiment name (default: timestamp)
 - `--eep, --extrack-experiment-path`: Explicit experiment path
 - `-c, --config`: Configuration file path
 
 
### The zoo() Function

 The `zoo()` function in [src/rl/zoo/zoo.cpp302-474](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L302-L474) implements the core training orchestration:

 
```

```

 **Execution flow:**

 
 - **Type Resolution**: Instantiates `LOOP_STATE` from `LOOP_CONFIG::State<LOOP_CONFIG>`
 - **Memory Validation**: Asserts `sizeof(LOOP_STATE) < 100000000` for stack size safety
 - **Seed Loop**: Iterates from `initial_seed` to `num_seeds`
 - **ExTrack Configuration**: Sets `extrack_config` fields: 
 - `name`: Set to "zoo"
 - `population_variates`: Set to "environment_algorithm"
 - `population_values`: Constructed from environment and algorithm names (e.g., "l2f_sac")
 - **Device Initialization**: Calls `rlt::malloc(device)` and `rlt::init(device)`
 - **State Initialization**: Calls `rlt::malloc(device, ts)` and `rlt::init(device, ts, seed)`
 - **Training Loop**: Executes `while(!rlt::step(device, ts))`
 - **Result Saving**: Writes `return.json` with evaluation results
 - **Confirmation**: Creates `return.json.set` marker file
 
 Sources: [src/rl/zoo/zoo.cpp302-474](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L302-L474) [src/rl/zoo/zoo_cli.cpp1-34](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo_cli.cpp#L1-L34)

 
### Training Loop Execution Sequence

 
```

```

 Sources: [src/rl/zoo/zoo.cpp302-474](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L302-L474) [src/rl/zoo/zoo.cpp362-414](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L362-L414)

 
## Loop Configuration Hierarchy

 The Zoo system constructs training loops through a decorator pattern where each configuration layer adds functionality. The final `LOOP_CONFIG` type is built by composing multiple configuration layers.

 
### Loop Configuration Composition

 
```

```

 Each configuration layer defines:

 
 - **Parameters**: Compile-time constants (intervals, batch sizes, etc.)
 - **State extension**: Additional state fields via inheritance
 - **Step logic**: Additional operations executed during `rlt::step()`
 
 
### Loop Configuration Parameters

 The [src/rl/zoo/zoo.cpp219-256](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L219-L256) defines configuration parameters:

 
| Configuration | Parameter | Type | Purpose |
|---|---|---|---|
| LOOP_TIMING_CONFIG | TIMING_INTERVAL | constexpr TI | Performance measurement frequency |
| LOOP_EVALUATION_CONFIG | EVALUATION_INTERVAL | constexpr TI | Policy evaluation frequency |
| LOOP_EVALUATION_CONFIG | NUM_EVALUATION_EPISODES | constexpr TI | Episodes per evaluation |
| LOOP_CHECKPOINT_CONFIG | CHECKPOINT_INTERVAL | constexpr TI | Model checkpoint frequency |
| LOOP_SAVE_TRAJECTORIES_CONFIG | INTERVAL | constexpr TI | Trajectory saving frequency |
| LOOP_SAVE_TRAJECTORIES_CONFIG | NUM_EPISODES | constexpr TI | Trajectories to save |

 Example calculation for evaluation interval:

 
```

```

 
### State Composition Through Inheritance

 Each configuration's `State` template inherits from the previous layer:

 
```

```

 This creates a chain: `LOOP_STATE` → `NN_ANALYTICS` → `SAVE_TRAJECTORIES` → `CHECKPOINT` → `EVALUATION` → `EXTRACK` → `TIMING` → `CORE`

 Sources: [src/rl/zoo/zoo.cpp219-260](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L219-L260) [include/rl_tools/rl/loop/steps/extrack/state.h13-19](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/loop/steps/extrack/state.h#L13-L19)

 
## Experiment Tracking (ExTrack)

 The ExTrack system organizes experiment outputs in a hierarchical directory structure that enables systematic result comparison and analysis. The [include/rl_tools/rl/loop/steps/extrack/operations_cpu.h1-43](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/loop/steps/extrack/operations_cpu.h#L1-L43) implements the tracking operations.

 
### ExTrack Directory Structure

 
```

```

 
### ExTrack Configuration

 The `extrack_config` structure in [include/rl_tools/rl/loop/steps/extrack/state.h13-19](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/loop/steps/extrack/state.h#L13-L19) contains:

 
| Field | Type | Purpose | Example |
|---|---|---|---|
| name | std::string | Experiment identifier | "zoo" |
| base_path | std::string | Root directory | "experiments" |
| experiment | std::string | Experiment name | "2024-01-15_10-30-45" |
| population_variates | std::string | Grouping variables | "environment_algorithm" |
| population_values | std::string | Specific values | "l2f_sac" |

 The `extrack_paths` structure contains resolved paths:

 
 - `seed`: Full path to seed directory
 - `checkpoint`: Path to checkpoint directory
 - Other resolved paths for data storage
 
 
### Result Format: return.json

 The `return.json` file contains an array of evaluation results:

 
```

```

 Sources: [src/rl/zoo/zoo.cpp402-414](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L402-L414) [include/rl_tools/rl/loop/steps/extrack/state.h13-19](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/loop/steps/extrack/state.h#L13-L19)

 
## Result Visualization and Analysis

 The Zoo system provides Python-based analysis tools and web-based visualization interfaces.

 
### Python Analysis Script

 The [src/rl/zoo/l2f/plot_learning_curves.py1-151](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/plot_learning_curves.py#L1-L151) demonstrates loading and visualizing experiment results:

 
```

```

 This enables:

 
 - Loading results from multiple seeds
 - Computing aggregate statistics (IQM, percentiles)
 - Plotting learning curves with confidence intervals
 - Comparing different algorithm-environment combinations
 
 
### Web-Based ExTrack UI

 The ExTrack UI provides interactive visualization:

 **Components:**

 
 - **Dashboard**: Overview of recent experiments and zoo runs
 - **Terminal**: Interactive JavaScript console for custom queries
 - **Explorer**: Hierarchical navigation through experiment results
 - **Zoo Viewer**: Comparative learning curve visualization
 
 The UI reads the ExTrack directory structure and `return.json` files to generate visualizations.

 Sources: [src/rl/zoo/l2f/plot_learning_curves.py6-36](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/plot_learning_curves.py#L6-L36)

 
## Extending the Zoo System

 Adding new algorithm-environment combinations requires creating a `FACTORY` template and registering it with the build system.

 
### Step 1: Create FACTORY Header

 Create a header file (e.g., `src/rl/zoo/new_env/new_alg.h`) with a `FACTORY` template:

 
```

```

 
### Step 2: Register in zoo.cpp

 Add the include in [src/rl/zoo/zoo.cpp52-77](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L52-L77):

 
```

```

 Add conditional compilation in [src/rl/zoo/zoo.cpp131-217](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L131-L217):

 
```

```

 Add string name in [src/rl/zoo/zoo.cpp263-290](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L263-L290):

 
```

```

 
### Step 3: Add CMake Target

 Add to [src/rl/zoo/CMakeLists.txt1-154](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/CMakeLists.txt#L1-L154):

 
```

```

 
### Step 4: Build and Run

 
```

```

 Sources: [src/rl/zoo/l2f/sac_tiny.h13-71](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/l2f/sac_tiny.h#L13-L71) [src/rl/zoo/zoo.cpp52-77](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L52-L77) [src/rl/zoo/zoo.cpp131-217](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L131-L217) [src/rl/zoo/CMakeLists.txt104-130](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/CMakeLists.txt#L104-L130)

 
## Performance Considerations

 The Zoo system is designed for performance through:

 
 - **Compile-time configuration**: Algorithm-environment pairs are determined at compile time
 - **Template-based polymorphism**: Avoids runtime overhead of virtual functions
 - **Backend flexibility**: Can leverage CPU, MKL, or CUDA backends depending on configuration
 - **Interval-based logging**: Performance-intensive operations like evaluation and checkpointing occur at configurable intervals
 
 For benchmarking-specific builds, define the `BENCHMARK` macro to disable non-essential features:

 
```

```

 Sources: [src/rl/zoo/zoo.cpp176-179](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/zoo.cpp#L176-L179) [src/rl/zoo/CMakeLists.txt44-49](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/zoo/CMakeLists.txt#L44-L49)
