> 来源: [https://deepwiki.com/araffin/rl-baselines-zoo/4-utilities-and-tools](https://deepwiki.com/araffin/rl-baselines-zoo/4-utilities-and-tools)
> DeepWiki araffin/rl-baselines-zoo | Last indexed: 24 June 2025 (ff84f3

# Utilities and Tools

  Relevant source files 
 - [.coveragerc](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/.coveragerc)
 - [trained_agents/ppo2/HalfCheetahBulletEnv-v0/config.yml](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/trained_agents/ppo2/HalfCheetahBulletEnv-v0/config.yml)
 - [trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0.pkl](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0.pkl)
 - [trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0/obs_rms.pkl](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0/obs_rms.pkl)
 - [trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0/ret_rms.pkl](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0/ret_rms.pkl)
 - [trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0.pkl](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0.pkl)
 - [trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0/obs_rms.pkl](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0/obs_rms.pkl)
 - [trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0/ret_rms.pkl](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0/ret_rms.pkl)
 - [utils/__init__.py](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/__init__.py)
 - [utils/benchmark.py](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/benchmark.py)
 - [utils/noise.py](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/noise.py)
 - [utils/record_video.py](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/record_video.py)
 - [utils/wrappers.py](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/wrappers.py)
 
  This document covers the various utility tools and helper functions provided by RL Baselines Zoo for benchmarking, visualization, analysis, and development support. These tools complement the core training and evaluation workflows documented in [Getting Started](https://deepwiki.com/araffin/rl-baselines-zoo/2-getting-started).

 For information about Docker containerization and development infrastructure, see [Development and Deployment](https://deepwiki.com/araffin/rl-baselines-zoo/5-development-and-deployment). For details about custom callbacks and training extensions, see [Advanced Features](https://deepwiki.com/araffin/rl-baselines-zoo/6-advanced-features).

 
## Overview

 The utilities system provides several categories of tools:

 
 - **Benchmarking Tools**: Automated performance evaluation and comparison across trained models
 - **Recording and Visualization**: Video capture and results plotting for agent analysis
 - **Environment Extensions**: Custom wrappers and modifications for specialized training scenarios
 - **Noise and Exploration**: Action noise implementations for improved exploration
 - **Development Helpers**: Utility functions for model management and environment creation
 
 
## Utility System Architecture

 
```

```

 **Sources:** [utils/benchmark.py1-133](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/benchmark.py#L1-L133) [utils/record_video.py1-88](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/record_video.py#L1-L88) [utils/wrappers.py1-76](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/wrappers.py#L1-L76) [utils/noise.py1-29](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/noise.py#L1-L29) [utils/__init__.py1-4](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/__init__.py#L1-L4)

 
## Benchmarking System

 The benchmarking system provides automated performance evaluation across all trained models in the repository. The `benchmark.py` script orchestrates the entire process:

 
```

```

 **Key Components:**

 
 - **Model Discovery**: `get_trained_models()` scans the `trained_agents/` directory structure
 - **Evaluation**: Subprocess calls to `enjoy.py` with standardized parameters
 - **Statistics Collection**: Mean reward, standard deviation, episode count, timestep count
 - **Output Generation**: Markdown tables via `pytablewriter.MarkdownTableWriter`
 
 **Algorithm-Specific Handling:**

 
```

```

 **Sources:** [utils/benchmark.py33-51](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/benchmark.py#L33-L51) [utils/benchmark.py89-123](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/benchmark.py#L89-L123)

 
## Video Recording System

 The video recording system captures agent behavior for visual analysis and debugging:

 
```

```

 **Key Features:**

 
 - **Environment Recreation**: Uses `create_test_env()` with saved hyperparameters and normalization statistics
 - **Video Wrapper**: `VecVideoRecorder` handles automatic recording triggers and file naming
 - **Action Processing**: Proper clipping for continuous action spaces via `np.clip()`
 - **Resource Management**: Careful cleanup of environment processes and video handles
 
 **Sources:** [utils/record_video.py55-87](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/record_video.py#L55-L87) [utils/record_video.py66-77](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/record_video.py#L66-L77)

 
## Environment Wrappers

 The wrapper system provides specialized environment modifications:

 
### DoneOnSuccessWrapper

 Modifies episode termination for goal-based environments:

 
| Feature | Implementation |
|---|---|
| Purpose | Reset on goal achievement for GoalEnv |
| Termination | done = done or info.get('is_success', False) |
| Reward Offset | Configurable positive offset for successful episodes |
| Goal Environments | HER-compatible reward computation |

 
### TimeFeatureWrapper

 Adds temporal information to observations:

 
| Feature | Implementation |
|---|---|
| Time Feature | time_feature = 1 - (current_step / max_steps) |
| Observation Space | Extended by 1 dimension |
| Test Mode | Constant time feature (1.0) to test overfitting |
| Use Case | Fixed-length episodes requiring time awareness |

 **Sources:** [utils/wrappers.py6-24](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/wrappers.py#L6-L24) [utils/wrappers.py26-75](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/wrappers.py#L26-L75)

 
## Noise Implementation

 
### LinearNormalActionNoise

 Provides exploration noise with scheduled decay:

 
```

```

 **Features:**

 
 - Linear interpolation between initial and final noise levels
 - Step-based scheduling over training duration
 - Gaussian noise distribution
 - Compatible with Stable-Baselines action noise interface
 
 **Sources:** [utils/noise.py6-28](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/noise.py#L6-L28)

 
## Core Utility Functions

 The `utils/utils.py` module (referenced via imports) provides foundational functions used across the utilities:

 
| Function | Purpose |
|---|---|
| make_env() | Environment factory with wrapper application |
| create_test_env() | Test environment setup with normalization |
| get_saved_hyperparams() | Load hyperparameters from trained models |
| find_saved_model() | Locate model files by algorithm and environment |
| get_trained_models() | Scan and catalog available trained models |

 **Sources:** [utils/__init__.py1-3](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/utils/__init__.py#L1-L3)
