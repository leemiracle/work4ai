<!-- source: DeepWiki mcp.deepwiki.com · repo araffin/rl-baselines-zoo · page 4 Utilities and Tools · fetched 2026-10-30 -->

# Utilities and Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.coveragerc](.coveragerc)
- [trained_agents/ppo2/HalfCheetahBulletEnv-v0/config.yml](trained_agents/ppo2/HalfCheetahBulletEnv-v0/config.yml)
- [trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0.pkl](trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0.pkl)
- [trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0/obs_rms.pkl](trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0/obs_rms.pkl)
- [trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0/ret_rms.pkl](trained_agents/ppo2/InvertedDoublePendulumBulletEnv-v0/ret_rms.pkl)
- [trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0.pkl](trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0.pkl)
- [trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0/obs_rms.pkl](trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0/obs_rms.pkl)
- [trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0/ret_rms.pkl](trained_agents/ppo2/InvertedPendulumSwingupBulletEnv-v0/ret_rms.pkl)
- [utils/__init__.py](utils/__init__.py)
- [utils/benchmark.py](utils/benchmark.py)
- [utils/noise.py](utils/noise.py)
- [utils/record_video.py](utils/record_video.py)
- [utils/wrappers.py](utils/wrappers.py)

</details>



This document covers the various utility tools and helper functions provided by RL Baselines Zoo for benchmarking, visualization, analysis, and development support. These tools complement the core training and evaluation workflows documented in [Getting Started](#2).

For information about Docker containerization and development infrastructure, see [Development and Deployment](#5). For details about custom callbacks and training extensions, see [Advanced Features](#6).

## Overview

The utilities system provides several categories of tools:

- **Benchmarking Tools**: Automated performance evaluation and comparison across trained models
- **Recording and Visualization**: Video capture and results plotting for agent analysis  
- **Environment Extensions**: Custom wrappers and modifications for specialized training scenarios
- **Noise and Exploration**: Action noise implementations for improved exploration
- **Development Helpers**: Utility functions for model management and environment creation

## Utility System Architecture

```mermaid
graph TB
    subgraph "Core Utilities"
        A[utils/benchmark.py] --> B["get_trained_models()"]
        A --> C["subprocess.call()"]
        A --> D[pytablewriter]
        
        E[utils/record_video.py] --> F[VecVideoRecorder]
        E --> G["create_test_env()"]
        E --> H["ALGOS.load()"]
    end
    
    subgraph "Environment Extensions"
        I[utils/wrappers.py] --> J[DoneOnSuccessWrapper]
        I --> K[TimeFeatureWrapper]
        
        L[utils/noise.py] --> M[LinearNormalActionNoise]
    end
    
    subgraph "Shared Utilities"
        N[utils/utils.py] --> O["make_env()"]
        N --> P["create_test_env()"]
        N --> Q["get_saved_hyperparams()"]
        N --> R["find_saved_model()"]
    end
    
    subgraph "Outputs"
        S[benchmark.md]
        T[logs/videos/]
        U[logs/benchmark/]
    end
    
    A --> S
    A --> U
    E --> T
    
    B --> N
    G --> N
    
    style A fill:#e1f5fe
    style E fill:#e1f5fe
    style N fill:#f3e5f5
```

**Sources:** [utils/benchmark.py:1-133](), [utils/record_video.py:1-88](), [utils/wrappers.py:1-76](), [utils/noise.py:1-29](), [utils/__init__.py:1-4]()

## Benchmarking System

The benchmarking system provides automated performance evaluation across all trained models in the repository. The `benchmark.py` script orchestrates the entire process:

```mermaid
flowchart TD
    A["benchmark.py startup"] --> B["get_trained_models()"]
    B --> C["Filter models"]
    C --> D{"For each model"}
    
    D --> E["Check if results exist"]
    E --> F{"Results found?"}
    F -->|Yes| G["Skip evaluation"]
    F -->|No| H["subprocess.call(['python', 'enjoy.py'])"]
    
    H --> I["load_results()"]
    I --> J["Calculate statistics"]
    J --> K["Store in results dict"]
    
    G --> L{"More models?"}
    K --> L
    L -->|Yes| D
    L -->|No| M["Create DataFrame"]
    
    M --> N["pytablewriter.MarkdownTableWriter()"]
    N --> O["benchmark.md output"]
```

**Key Components:**

- **Model Discovery**: `get_trained_models()` scans the `trained_agents/` directory structure
- **Evaluation**: Subprocess calls to `enjoy.py` with standardized parameters  
- **Statistics Collection**: Mean reward, standard deviation, episode count, timestep count
- **Output Generation**: Markdown tables via `pytablewriter.MarkdownTableWriter`

**Algorithm-Specific Handling:**
```python
# Single environment algorithms
if algo in ['dqn', 'ddpg', 'sac', 'td3']:
    n_envs = 1
    n_timesteps *= args.n_envs
```

**Sources:** [utils/benchmark.py:33-51](), [utils/benchmark.py:89-123]()

## Video Recording System

The video recording system captures agent behavior for visual analysis and debugging:

```mermaid
graph LR
    subgraph "Video Recording Pipeline"
        A["record_video.py"] --> B["Load trained model"]
        B --> C["create_test_env()"]
        C --> D["VecVideoRecorder wrapper"]
        D --> E["Agent execution loop"]
        E --> F["Video file output"]
    end
    
    subgraph "Environment Handling"
        G["Atari detection"] --> H["Frame stacking"]
        I["Normalization stats"] --> J["VecNormalize"]
        K["Action clipping"] --> L["gym.spaces.Box"]
    end
    
    C --> G
    C --> I
    E --> K
    
    subgraph "Outputs"
        M["logs/videos/{algo}-{env}.mp4"]
    end
    
    F --> M
```

**Key Features:**

- **Environment Recreation**: Uses `create_test_env()` with saved hyperparameters and normalization statistics
- **Video Wrapper**: `VecVideoRecorder` handles automatic recording triggers and file naming
- **Action Processing**: Proper clipping for continuous action spaces via `np.clip()`
- **Resource Management**: Careful cleanup of environment processes and video handles

**Sources:** [utils/record_video.py:55-87](), [utils/record_video.py:66-77]()

## Environment Wrappers

The wrapper system provides specialized environment modifications:

### DoneOnSuccessWrapper

Modifies episode termination for goal-based environments:

| Feature | Implementation |
|---------|----------------|
| **Purpose** | Reset on goal achievement for GoalEnv |
| **Termination** | `done = done or info.get('is_success', False)` |
| **Reward Offset** | Configurable positive offset for successful episodes |
| **Goal Environments** | HER-compatible reward computation |

### TimeFeatureWrapper  

Adds temporal information to observations:

| Feature | Implementation |
|---------|----------------|
| **Time Feature** | `time_feature = 1 - (current_step / max_steps)` |
| **Observation Space** | Extended by 1 dimension |
| **Test Mode** | Constant time feature (1.0) to test overfitting |
| **Use Case** | Fixed-length episodes requiring time awareness |

**Sources:** [utils/wrappers.py:6-24](), [utils/wrappers.py:26-75]()

## Noise Implementation

### LinearNormalActionNoise

Provides exploration noise with scheduled decay:

```python
class LinearNormalActionNoise(ActionNoise):
    def __call__(self):
        t = min(1.0, self._step / self._max_steps)
        sigma = (1 - t) * self._sigma + t * self._final_sigma
        self._step += 1
        return np.random.normal(self._mu, sigma)
```

**Features:**
- Linear interpolation between initial and final noise levels
- Step-based scheduling over training duration  
- Gaussian noise distribution
- Compatible with Stable-Baselines action noise interface

**Sources:** [utils/noise.py:6-28]()

## Core Utility Functions

The `utils/utils.py` module (referenced via imports) provides foundational functions used across the utilities:

| Function | Purpose |
|----------|---------|
| `make_env()` | Environment factory with wrapper application |
| `create_test_env()` | Test environment setup with normalization |
| `get_saved_hyperparams()` | Load hyperparameters from trained models |
| `find_saved_model()` | Locate model files by algorithm and environment |
| `get_trained_models()` | Scan and catalog available trained models |

**Sources:** [utils/__init__.py:1-3]()

---

