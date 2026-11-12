> 来源: [https://deepwiki.com/thu-ml/tianshou/10-utilities](https://deepwiki.com/thu-ml/tianshou/10-utilities)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# Utilities

  Relevant source files 
 - [test/base/test_utils.py](https://github.com/thu-ml/tianshou/blob/90846f6b/test/base/test_utils.py)
 - [tianshou/utils/__init__.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/__init__.py)
 - [tianshou/utils/statistics.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/statistics.py)
 - [tianshou/utils/torch_utils.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/torch_utils.py)
 - [tianshou/utils/warning.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/warning.py)
 
  The Tianshou Utilities module provides a collection of supporting tools and functions that enhance the functionality of the core reinforcement learning framework. These utilities offer statistical analysis capabilities, PyTorch-specific helper functions, logging mechanisms, and other auxiliary features needed for efficient reinforcement learning implementation.

 
## Overview of Utility Components

 Tianshou's utilities can be categorized into several functional groups:

 
```

```

 Sources: [tianshou/utils/__init__.py1-22](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/__init__.py#L1-L22)

 
## Statistical Utilities

 Tianshou provides two main statistical utilities that are essential for tracking and normalizing data during reinforcement learning training.

 
### MovAvg

 The `MovAvg` class implements a moving average calculator that automatically excludes invalid values such as infinity and NaN. It's particularly useful for tracking training metrics and smoothing noisy signals.

 
```

```

 Key features:

 
 - Configurable window size
 - Support for scalar and batch inputs
 - Automatic filtering of invalid values (infinity, NaN)
 - Provides both mean and standard deviation statistics
 
 Sources: [tianshou/utils/statistics.py7-67](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/statistics.py#L7-L67)

 
### RunningMeanStd

 The `RunningMeanStd` class calculates running mean and standard deviation of a data stream. This is particularly important for observation normalization in reinforcement learning.

 
```

```

 Key features:

 
 - Efficient parallel algorithm for computing variance
 - Optional value clipping to prevent outliers
 - No need to store historical data, making it memory-efficient
 
 Sources: [tianshou/utils/statistics.py69-114](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/statistics.py#L69-L114)

 
## PyTorch Utilities

 Tianshou provides several PyTorch-specific utilities to help manage model states and create distributions for exploration.

 
```

```

 Sources: [tianshou/utils/torch_utils.py1-77](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/torch_utils.py#L1-L77)

 
### torch_train_mode

 A context manager that temporarily switches a PyTorch module's training mode. This is useful when you need to temporarily change the behavior of components like BatchNormalization during evaluation or training.

 
```

```

 Sources: [tianshou/utils/torch_utils.py14-22](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/torch_utils.py#L14-L22)

 
### policy_within_training_step

 A context manager that temporarily sets a policy's `is_within_training_step` flag, allowing it to differentiate between training and inference/evaluation behaviors. This is useful for controlling behavior like action sampling versus using the most probable action.

 
```

```

 Sources: [tianshou/utils/torch_utils.py25-42](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/torch_utils.py#L25-L42)

 
### create_uniform_action_dist

 Creates a PyTorch distribution that, when sampled from, is equivalent to sampling from the given action space. This function supports both continuous (Box) and discrete action spaces.

 
```

```

 The function returns:

 
 - `torch.distributions.Uniform` for continuous action spaces
 - `torch.distributions.Categorical` for discrete action spaces
 
 Sources: [tianshou/utils/torch_utils.py45-77](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/torch_utils.py#L45-L77)

 
## Learning Rate Utilities

 
### MultipleLRSchedulers

 Manages multiple learning rate schedulers simultaneously, which is useful when training networks with multiple optimizers. This utility simplifies the process of updating learning rates across different components of a complex network.

 
```

```

 Sources: [test/base/test_utils.py109-139](https://github.com/thu-ml/tianshou/blob/90846f6b/test/base/test_utils.py#L109-L139)

 
## Logging Utilities

 Tianshou provides a flexible logging system for tracking and visualizing training metrics across different backends.

 
```

```

 Sources: [tianshou/utils/__init__.py3-5](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/__init__.py#L3-L5)

 
### BaseLogger

 The abstract base class that defines the interface for all loggers in Tianshou. It provides methods for logging training, testing, and update data.

 
### TensorboardLogger

 A logger implementation that uses TensorBoard as the backend for visualizing metrics.

 
### WandbLogger

 A logger implementation that uses Weights & Biases as the backend for tracking and visualizing experiments.

 
### LazyLogger

 A logger wrapper that lazily initializes the actual logger. This is useful when you want to defer the creation of logging resources until they're actually needed.

 
## Progress Tracking

 Tianshou includes utilities for displaying progress during training:

 
### tqdm_config

 Configuration settings for the tqdm progress bar.

 
### DummyTqdm

 A dummy progress bar class that implements the tqdm interface but doesn't display anything. This is useful for environments where visual progress bars are not appropriate or available.

 Sources: [tianshou/utils/__init__.py7](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/__init__.py#L7-L7)

 
## Warning Utilities

 
### deprecation

 A utility function for generating deprecation warnings. It uses Python's warning system to issue warnings when deprecated features are used.

 
```

```

 Sources: [tianshou/utils/warning.py1-8](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/warning.py#L1-L8)

 
## Utilities in the RL Training Pipeline

 The following diagram illustrates how Tianshou's utilities fit into the broader reinforcement learning training pipeline:

 
```

```

 Sources: [tianshou/utils/__init__.py1-22](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/__init__.py#L1-L22) [tianshou/utils/torch_utils.py1-77](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/torch_utils.py#L1-L77) [tianshou/utils/statistics.py1-114](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/statistics.py#L1-L114)

 
## Summary of Available Utilities

 
| Utility | Category | Purpose |
|---|---|---|
| MovAvg | Statistical | Calculates moving average of training metrics |
| RunningMeanStd | Statistical | Tracks running mean and standard deviation for normalization |
| torch_train_mode | PyTorch | Context manager for temporarily changing training mode |
| policy_within_training_step | PyTorch | Context manager for marking policy as within training step |
| create_uniform_action_dist | PyTorch | Creates uniform action distributions for exploration |
| MultipleLRSchedulers | Learning Rate | Manages multiple learning rate schedulers |
| BaseLogger, TensorboardLogger, etc. | Logging | Tracks and visualizes training metrics |
| tqdm_config, DummyTqdm | Progress | Displays training progress |
| deprecation | Warning | Issues deprecation warnings |

 Sources: [tianshou/utils/__init__.py11-22](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/utils/__init__.py#L11-L22)
