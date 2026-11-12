> 来源: [https://deepwiki.com/hill-a/stable-baselines/6-training-and-monitoring](https://deepwiki.com/hill-a/stable-baselines/6-training-and-monitoring)
> DeepWiki hill-a/stable-baselines | Last indexed: 22 June 2025 (45beb2

# Training and Monitoring

  Relevant source files 
 - [scripts/run_tests.sh](https://github.com/hill-a/stable-baselines/blob/45beb246/scripts/run_tests.sh)
 - [setup.cfg](https://github.com/hill-a/stable-baselines/blob/45beb246/setup.cfg)
 - [stable_baselines/logger.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py)
 - [tests/test_common.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_common.py)
 - [tests/test_logger.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_logger.py)
 - [tests/test_tensorboard.py](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_tensorboard.py)
 
  This document covers the comprehensive training and monitoring infrastructure in stable-baselines, including logging systems, progress tracking, performance monitoring, and result analysis capabilities. The system provides multiple output formats for training metrics, integrates seamlessly with all reinforcement learning algorithms, and offers tools for analyzing training progress and model performance.

 For detailed information about the training loop mechanics and callbacks, see [Training Process](https://deepwiki.com/hill-a/stable-baselines/6.1-training-process). For specific logging configuration and monitoring setup, see [Logging and Monitoring](https://deepwiki.com/hill-a/stable-baselines/6.2-logging-and-monitoring). For model evaluation and results analysis, see [Evaluation and Results](https://deepwiki.com/hill-a/stable-baselines/6.3-evaluation-and-results).

 
## System Architecture

 The training and monitoring system in stable-baselines is built around a flexible logging infrastructure that captures training metrics, algorithm performance data, and diagnostic information across multiple output formats.

 
### Training and Monitoring Overview

 
```

```

 Sources: [stable_baselines/logger.py1-746](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py#L1-L746) [tests/test_tensorboard.py1-52](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_tensorboard.py#L1-L52)

 
## Logger System Architecture

 The logging system is built around a modular architecture with multiple output format writers that can operate simultaneously during training.

 
### Logger Components and Data Flow

 
```

```

 Sources: [stable_baselines/logger.py457-569](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py#L457-L569) [stable_baselines/logger.py27-273](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py#L27-L273)

 
## Algorithm Integration

 All stable-baselines algorithms integrate with the logging system through standardized API calls during training.

 
### Algorithm Logging Integration

 
| Algorithm | TensorBoard Support | Key Metrics Logged | Configuration |
|---|---|---|---|
| A2C | Yes | episode_reward, episode_length, learning_rate, value_loss | tensorboard_log parameter |
| PPO2 | Yes | episode_reward, episode_length, policy_loss, value_loss | tensorboard_log parameter |
| DQN | Yes | episode_reward, episode_length, mean_q_value, learning_rate | tensorboard_log parameter |
| DDPG | Yes | episode_reward, episode_length, actor_loss, critic_loss | tensorboard_log parameter |
| SAC | Yes | episode_reward, episode_length, actor_loss, critic_loss | tensorboard_log parameter |
| TD3 | Yes | episode_reward, episode_length, actor_loss, critic_loss | tensorboard_log parameter |
| TRPO | Yes | episode_reward, episode_length, policy_loss, kl_divergence | tensorboard_log parameter |

 All algorithms automatically create incremental log directories (e.g., `PPO2_1`, `PPO2_2`) when using the same `tb_log_name` parameter across multiple training runs.

 Sources: [tests/test_tensorboard.py13-52](https://github.com/hill-a/stable-baselines/blob/45beb246/tests/test_tensorboard.py#L13-L52)

 
## Output Format Configuration

 The logging system supports multiple simultaneous output formats configured through the `configure()` function or environment variables.

 
### Available Output Formats

 
```

```

 **Default Configuration:** `['stdout', 'log', 'csv']` for rank 0 processes, `['log']` for MPI worker processes.

 **Configuration Examples:**

 
 - Single format: `configure(format_strs=['tensorboard'])`
 - Multiple formats: `configure(format_strs=['stdout', 'csv', 'tensorboard'])`
 - Environment variable: `export OPENAI_LOG_FORMAT="stdout,tensorboard,csv"`
 
 Sources: [stable_baselines/logger.py572-600](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py#L572-L600) [stable_baselines/logger.py251-273](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py#L251-L273)

 
## Data Reading and Analysis

 The system provides utilities for reading and analyzing logged training data across all supported formats.

 
### Data Reading Functions

 
```

```

 **Key Reader Features:**

 
 - `read_tb()` handles both individual TensorBoard files and directories containing multiple event files
 - `read_csv()` and `read_json()` provide direct pandas DataFrame integration
 - All readers return standardized pandas DataFrames for consistent analysis workflows
 
 Sources: [stable_baselines/logger.py681-742](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py#L681-L742)

 
## Performance Monitoring

 The logging system includes built-in performance profiling capabilities for monitoring training efficiency and identifying bottlenecks.

 
### Profiling System

 The `ProfileKV` context manager and `profile` decorator provide automatic timing measurement:

 
```

```

 **Profiling Features:**

 
 - Automatic timing accumulation across multiple calls
 - Integration with standard logging output formats
 - Support for nested profiling contexts
 - Minimal performance overhead
 
 Sources: [stable_baselines/logger.py416-451](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py#L416-L451)

 
## MPI and Distributed Logging

 The system handles multi-process training scenarios with MPI-aware logging configuration.

 **MPI Features:**

 
 - Rank-based log file naming (`log-rank001.txt`)
 - Configurable per-rank output formats via `OPENAI_LOG_FORMAT_MPI`
 - Automatic rank detection through `mpi_rank_or_zero()`
 - Coordinated logging to prevent file conflicts
 
 Sources: [stable_baselines/logger.py586-595](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/logger.py#L586-L595) [stable_baselines/common/misc_util.py](https://github.com/hill-a/stable-baselines/blob/45beb246/stable_baselines/common/misc_util.py)
