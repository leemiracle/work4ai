<!-- source: DeepWiki mcp.deepwiki.com · repo Farama-Foundation/Gymnasium · extra page Transform and Stateful Wrappers · fetched 2026-10-14 -->

# Transform and Stateful Wrappers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/api/env.md](docs/api/env.md)
- [gymnasium/wrappers/atari_preprocessing.py](gymnasium/wrappers/atari_preprocessing.py)
- [gymnasium/wrappers/stateful_observation.py](gymnasium/wrappers/stateful_observation.py)
- [gymnasium/wrappers/stateful_reward.py](gymnasium/wrappers/stateful_reward.py)
- [gymnasium/wrappers/transform_action.py](gymnasium/wrappers/transform_action.py)
- [gymnasium/wrappers/transform_observation.py](gymnasium/wrappers/transform_observation.py)
- [gymnasium/wrappers/vector/stateful_reward.py](gymnasium/wrappers/vector/stateful_reward.py)
- [tests/wrappers/test_atari_preprocessing.py](tests/wrappers/test_atari_preprocessing.py)
- [tests/wrappers/test_discretize_action.py](tests/wrappers/test_discretize_action.py)
- [tests/wrappers/test_discretize_observation.py](tests/wrappers/test_discretize_observation.py)
- [tests/wrappers/test_dtype_observation.py](tests/wrappers/test_dtype_observation.py)
- [tests/wrappers/test_frame_stack_observation.py](tests/wrappers/test_frame_stack_observation.py)
- [tests/wrappers/test_gray_scale_observation.py](tests/wrappers/test_gray_scale_observation.py)
- [tests/wrappers/test_normalize_observation.py](tests/wrappers/test_normalize_observation.py)
- [tests/wrappers/test_normalize_reward.py](tests/wrappers/test_normalize_reward.py)
- [tests/wrappers/test_rescale_action.py](tests/wrappers/test_rescale_action.py)
- [tests/wrappers/test_rescale_observation.py](tests/wrappers/test_rescale_observation.py)
- [tests/wrappers/test_resize_observation.py](tests/wrappers/test_resize_observation.py)
- [tests/wrappers/vector/test_normalize_observation.py](tests/wrappers/vector/test_normalize_observation.py)
- [tests/wrappers/vector/test_normalize_reward.py](tests/wrappers/vector/test_normalize_reward.py)

</details>



This page provides detailed documentation for Gymnasium's transform and stateful wrappers. These wrappers modify observations, actions, or rewards, often maintaining internal state to do so. This includes wrappers for normalization, frame stacking, and Atari preprocessing.

## Observation Transform Wrappers

Observation transform wrappers modify the observations returned by the environment. These wrappers are typically stateless, applying a function directly to the observation.

### `TransformObservation`

The `TransformObservation` wrapper [gymnasium/wrappers/transform_observation.py:43-97]() applies a user-defined function to the observation received from the environment's `reset()` and `step()` methods.

**Implementation Details:**
- The wrapper takes a `func` (a callable) and an optional `observation_space` as arguments during initialization [gymnasium/wrappers/transform_observation.py:71-84]().
- If `observation_space` is provided, it overrides the environment's observation space [gymnasium/wrappers/transform_observation.py:90-91]().
- The `observation()` method simply calls the provided `func` with the raw observation [gymnasium/wrappers/transform_observation.py:95-97]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import TransformObservation
import numpy as np

env = gym.make("CartPole-v1")
env = TransformObservation(env, lambda obs: obs + 0.1 * np.random.random(obs.shape), env.observation_space)
obs, info = env.reset(seed=42)
# obs will be the original observation with added random noise
```

### `FilterObservation`

The `FilterObservation` wrapper [gymnasium/wrappers/transform_observation.py:100-164]() filters `Dict` or `Tuple` observation spaces to include only specified keys or indices.

**Implementation Details:**
- It inherits from `TransformObservation` [gymnasium/wrappers/transform_observation.py:100-103]().
- The constructor validates `filter_keys` based on the observation space type (strings for `Dict`, integers for `Tuple`) [gymnasium/wrappers/transform_observation.py:144-163]().
- It dynamically creates a new observation space containing only the filtered keys/indices.
- The `observation()` method filters the input observation dictionary or tuple.

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import FilterObservation, TimeAwareObservation

env = gym.make("CartPole-v1")
env = TimeAwareObservation(env, flatten=False) # Creates a Dict observation space
# env.observation_space is now Dict('obs': Box(...), 'time': Box(...))
env = FilterObservation(env, filter_keys=['time'])
obs, info = env.reset(seed=42)
# obs will only contain the 'time' key
```

### `FlattenObservation`

The `FlattenObservation` wrapper flattens the observation space of the environment. This is useful for environments with complex observation spaces (e.g., `Dict` or `Tuple`) that need to be converted into a single `Box` space.

**Implementation Details:**
- It uses `gymnasium.spaces.utils.flatten_space` to create the new observation space.
- The `observation()` method uses `gymnasium.spaces.utils.flatten` to flatten the actual observation.

### `GrayscaleObservation`

The `GrayscaleObservation` wrapper converts RGB observations to grayscale.

**Implementation Details:**
- It checks if the original observation space is a `Box` with 3 channels (RGB) [gymnasium/wrappers/transform_observation.py:400-402]().
- The `observation()` method performs the grayscale conversion using a weighted sum of RGB channels [gymnasium/wrappers/transform_observation.py:420-421]().
- It supports an optional `keep_dim` argument to maintain the channel dimension (e.g., `(H, W, 1)` instead of `(H, W)`) [gymnasium/wrappers/transform_observation.py:390]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import GrayscaleObservation

env = gym.make("CarRacing-v2") # Original observation is RGB (96, 96, 3)
env = GrayscaleObservation(env) # Observation becomes grayscale (96, 96)
obs, info = env.reset()
```
Sources: [gymnasium/wrappers/transform_observation.py:370-423]()

### `ResizeObservation`

The `ResizeObservation` wrapper resizes array-based observations, typically RGB images.

**Implementation Details:**
- It requires `opencv-python` [gymnasium/wrappers/transform_observation.py:446-450]().
- The constructor validates the `shape` argument [gymnasium/wrappers/transform_observation.py:452-460]().
- The `observation()` method uses `cv2.resize` to perform the resizing [gymnasium/wrappers/transform_observation.py:470-471]().
- It handles both grayscale and RGB observations, preserving the channel dimension if present [tests/wrappers/test_resize_observation.py:53-64]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import ResizeObservation

env = gym.make("CarRacing-v2") # Original observation is RGB (96, 96, 3)
env = ResizeObservation(env, (64, 64)) # Observation becomes (64, 64, 3)
obs, info = env.reset()
```
Sources: [gymnasium/wrappers/transform_observation.py:426-473](), [tests/wrappers/test_resize_observation.py:53-64]()

### `ReshapeObservation`

The `ReshapeObservation` wrapper reshapes array-based observations to a new specified shape.

**Implementation Details:**
- The constructor validates that the product of the new shape dimensions matches the product of the original observation space dimensions [gymnasium/wrappers/transform_observation.py:494-496]().
- The `observation()` method uses `np.reshape` to change the observation's shape [gymnasium/wrappers/transform_observation.py:505-506]().

### `RescaleObservation`

The `RescaleObservation` wrapper rescales observations to a specified range `[min_obs, max_obs]`.

**Implementation Details:**
- It requires the environment's observation space to be a `Box` [gymnasium/wrappers/transform_observation.py:534-536]().
- The `observation()` method applies a linear transformation to map the original observation range to the new `[min_obs, max_obs]` range [gymnasium/wrappers/transform_observation.py:550-551]().
- It uses the `rescale_box` utility function to determine the new observation space [gymnasium/wrappers/transform_observation.py:545]().

### `DtypeObservation`

The `DtypeObservation` wrapper converts the observation's data type to a specified `dtype`.

**Implementation Details:**
- It supports various observation space types including `Box`, `Discrete`, `MultiDiscrete`, and `MultiBinary` [tests/wrappers/test_dtype_observation.py:31-37]().
- The `observation()` method casts the observation to the target `dtype` [gymnasium/wrappers/transform_observation.py:579-580]().
- For `Discrete` spaces, it correctly adjusts the observation space bounds to match the original support while changing the dtype [tests/wrappers/test_dtype_observation.py:90-95]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import DtypeObservation
import numpy as np

env = gym.make("CartPole-v1") # Original observation dtype is float32
env = DtypeObservation(env, dtype=np.float64) # Observation dtype becomes float64
obs, info = env.reset()
assert obs.dtype == np.float64
```
Sources: [gymnasium/wrappers/transform_observation.py:554-582](), [tests/wrappers/test_dtype_observation.py:31-37](), [tests/wrappers/test_dtype_observation.py:90-95]()

### `DiscretizeObservation`

The `DiscretizeObservation` wrapper discretizes a continuous `Box` observation space into a single `Discrete` space.

**Implementation Details:**
- It requires the environment's observation space to be a `Box` [gymnasium/wrappers/transform_observation.py:609-611]().
- The constructor calculates the number of bins for each dimension and the total number of discrete states [gymnasium/wrappers/transform_observation.py:619-627]().
- The `observation()` method maps continuous observations to discrete integer values based on the defined bins [gymnasium/wrappers/transform_observation.py:639-645]().

## Action Transform Wrappers

Action transform wrappers modify the actions sent to the environment.

### `TransformAction`

The `TransformAction` wrapper [gymnasium/wrappers/transform_action.py:25-77]() applies a user-defined function to the action before it is passed to the environment's `step()` method.

**Implementation Details:**
- Similar to `TransformObservation`, it takes a `func` and an optional `action_space` [gymnasium/wrappers/transform_action.py:51-56]().
- The `action()` method applies the provided `func` to the action [gymnasium/wrappers/transform_action.py:75-77]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import TransformAction
import numpy as np

env = gym.make("MountainCarContinuous-v0")
env = TransformAction(env, lambda a: 0.5 * a + 0.1, env.action_space)
# Actions passed to env.step() will be transformed by the lambda function
```
Sources: [gymnasium/wrappers/transform_action.py:25-77]()

### `ClipAction`

The `ClipAction` wrapper [gymnasium/wrappers/transform_action.py:79-127]() clips actions to be within the bounds of the environment's `action_space`.

**Implementation Details:**
- It requires the environment's action space to be a `Box` [gymnasium/wrappers/transform_action.py:109-111]().
- It internally uses `TransformAction` with a `np.clip` function to perform the clipping [gymnasium/wrappers/transform_action.py:116-121]().
- The wrapper's action space is set to `Box(-inf, inf, ...)` because the clipping happens internally, and the agent can theoretically output any value [gymnasium/wrappers/transform_action.py:121-126]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import ClipAction
import numpy as np

env = gym.make("Hopper-v4", disable_env_checker=True)
env = ClipAction(env)
# If an action like np.array([5.0, -2.0, 0.0]) is passed, it will be clipped to [1.0, -1.0, 0.0]
```
Sources: [gymnasium/wrappers/transform_action.py:79-127]()

### `RescaleAction`

The `RescaleAction` wrapper [gymnasium/wrappers/transform_action.py:130-183]() affinely (linearly) rescales a `Box` action space to a new range `[min_action, max_action]`.

**Implementation Details:**
- It requires the environment's action space to be a `Box` [gymnasium/wrappers/transform_action.py:175-177]().
- It uses the `rescale_box` utility function to calculate the transformation [gymnasium/wrappers/transform_action.py:183]().
- The `action()` method applies this linear transformation to the input action.

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import RescaleAction
import numpy as np

env = gym.make("Hopper-v4", disable_env_checker=True)
min_action = -0.5
max_action = np.array([0.0, 0.5, 0.75], dtype=np.float32)
wrapped_env = RescaleAction(env, min_action=min_action, max_action=max_action)
# Actions will be rescaled from the original action space to the new [min_action, max_action] range
```
Sources: [gymnasium/wrappers/transform_action.py:130-183]()

### `DiscretizeAction`

The `DiscretizeAction` wrapper discretizes a continuous `Box` action space into a `Discrete` space.

**Implementation Details:**
- Similar to `DiscretizeObservation`, it maps continuous actions to discrete integer values based on defined bins.
- It requires the environment's action space to be a `Box`.

## Stateful Observation Wrappers

Stateful observation wrappers maintain internal state that influences how observations are processed.

### `DelayObservation`

The `DelayObservation` wrapper [gymnasium/wrappers/stateful_observation.py:35-104]() introduces a delay in the observations returned by the environment. Before the specified `delay` number of timesteps, it returns an array of zeros.

**Implementation Details:**
- It maintains an `observation_queue` (a `deque`) to store past observations [gymnasium/wrappers/stateful_observation.py:86-87]().
- On `reset()`, the queue is cleared [gymnasium/wrappers/stateful_observation.py:92]().
- In `observation()`, the current observation is added to the queue. If the queue size exceeds `delay`, the oldest observation is returned; otherwise, a zero array is returned [gymnasium/wrappers/stateful_observation.py:98-103]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import DelayObservation
import numpy as np

env = gym.make("CartPole-v1")
env = DelayObservation(env, delay=2)
obs, info = env.reset(seed=123) # Returns zeros
obs, reward, terminated, truncated, info = env.step(env.action_space.sample()) # Returns zeros
obs, reward, terminated, truncated, info = env.step(env.action_space.sample()) # Returns the first actual observation
```
Sources: [gymnasium/wrappers/stateful_observation.py:35-104]()

### `TimeAwareObservation`

The `TimeAwareObservation` wrapper [gymnasium/wrappers/stateful_observation.py:106-160]() augments the observation with the current timestep within an episode.

**Implementation Details:**
- It tracks the current timestep `self.current_timestep` [gymnasium/wrappers/stateful_observation.py:200]().
- The `observation()` method appends the timestep (normalized or raw) to the observation.
- For `Dict` spaces, it adds a `"time"` key; for `Tuple` spaces, it appends to the tuple. Otherwise, it converts the observation space to a `Dict` with `"obs"` and `"time"` keys [gymnasium/wrappers/stateful_observation.py:210-240]().
- The `flatten` argument can be used to flatten the resulting observation space [gymnasium/wrappers/stateful_observation.py:122]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import TimeAwareObservation

env = gym.make("CartPole-v1")
env = TimeAwareObservation(env) # Observation space becomes (original_shape + 1,)
obs, info = env.reset(seed=42) # Last element of obs is 0.0
obs, reward, terminated, truncated, info = env.step(env.action_space.sample()) # Last element of obs is 1.0
```
Sources: [gymnasium/wrappers/stateful_observation.py:106-160]()

### `FrameStackObservation`

The `FrameStackObservation` wrapper stacks the `k` most recent observations along a new axis. This is commonly used in environments like Atari to provide temporal context to the agent.

**Implementation Details:**
- It maintains a `deque` of observations [gymnasium/wrappers/stateful_observation.py:300]().
- On `reset()`, the queue is filled with the initial observation `k` times [gymnasium/wrappers/stateful_observation.py:310-313]().
- In `observation()`, the new observation is added to the queue, and the oldest is removed. The stacked observations are then concatenated [gymnasium/wrappers/stateful_observation.py:317-322]().
- The observation space is updated to reflect the new stacked dimension [gymnasium/wrappers/stateful_observation.py:290-297]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import FrameStackObservation

env = gym.make("CartPole-v1")
env = FrameStackObservation(env, num_stack=4) # Observation space becomes (original_shape * 4,)
obs, info = env.reset() # obs will be 4 stacked observations
```
Sources: [gymnasium/wrappers/stateful_observation.py:259-322]()

### `NormalizeObservation`

The `NormalizeObservation` wrapper [gymnasium/wrappers/stateful_observation.py:325-409]() normalizes observations to have zero mean and unit variance. It uses a running mean and standard deviation for this purpose.

**Implementation Details:**
- It uses a `RunningMeanStd` utility class to track the mean and variance of observations [gymnasium/wrappers/stateful_observation.py:370]().
- The `observation()` method normalizes the observation using the current running mean and standard deviation [gymnasium/wrappers/stateful_observation.py:399-400]().
- The `update_running_mean` property allows freezing the statistics updates, which is useful during evaluation [gymnasium/wrappers/stateful_observation.py:373-374]().
- It ensures `epsilon` (a stability parameter) is strictly positive to prevent division by zero [tests/wrappers/test_normalize_observation.py:83-90]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import NormalizeObservation

env = gym.make("CartPole-v1")
env = NormalizeObservation(env)
obs, info = env.reset() # obs will be normalized
```
Sources: [gymnasium/wrappers/stateful_observation.py:325-409](), [tests/wrappers/test_normalize_observation.py:83-90]()

### `MaxAndSkipObservation`

The `MaxAndSkipObservation` wrapper [gymnasium/wrappers/stateful_observation.py:412-499]() is specific to Atari environments. It performs frame skipping and max-pooling over the last two frames.

**Implementation Details:**
- It takes `skip` as an argument, which is the number of frames to skip [gymnasium/wrappers/stateful_observation.py:440]().
- It maintains an `obs_buffer` to store the last two observations [gymnasium/wrappers/stateful_observation.py:441]().
- The `step()` method performs `skip` internal steps, collecting observations. It then returns the element-wise maximum of the last two collected observations [gymnasium/wrappers/stateful_observation.py:470-499]().

## Stateful Reward Wrappers

Stateful reward wrappers modify rewards based on internal state.

### `NormalizeReward`

The `NormalizeReward` wrapper [gymnasium/wrappers/stateful_reward.py:20-142]() normalizes immediate rewards such that their exponential moving average has an approximately fixed variance.

**Implementation Details:**
- It uses a `RunningMeanStd` object to track the mean and standard deviation of the discounted returns [gymnasium/wrappers/stateful_reward.py:111]().
- It maintains `discounted_reward` which is updated at each step [gymnasium/wrappers/stateful_reward.py:134-136]().
- The `step()` method normalizes the reward by dividing it by the standard deviation of the discounted returns (plus `epsilon` for stability) [gymnasium/wrappers/stateful_reward.py:141]().
- The `update_running_mean` property allows freezing the statistics updates [gymnasium/wrappers/stateful_reward.py:117-126]().
- It validates `gamma` to be within `[0, 1]` and `epsilon` to be strictly positive [gymnasium/wrappers/stateful_reward.py:93-106]().

**Example:**
```python
import gymnasium as gym
from gymnasium.wrappers import NormalizeReward
import numpy as np

env = gym.make("MountainCarContinuous-v0")
env = NormalizeReward(env, gamma=0.99, epsilon=1e-8)
obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
# reward will be normalized
```
Sources: [gymnasium/wrappers/stateful_reward.py:20-142](), [gymnasium/wrappers/vector/stateful_reward.py:20-165]()

## Atari Preprocessing

The `AtariPreprocessing` wrapper [gymnasium/wrappers/atari_preprocessing.py:16-254]() implements common preprocessing techniques for Atari 2600 environments, following the guidelines from Machado et al. (2018).

**Implementation Details:**
- **Noop Reset:** Performs a random number of no-op actions at the beginning of an episode [gymnasium/wrappers/atari_preprocessing.py:27]().
- **Frame Skipping:** Steps the environment multiple times for each agent action, returning the observation from the last step [gymnasium/wrappers/atari_preprocessing.py:28]().
- **Max-pooling:** Takes the element-wise maximum of the last two observations after frame skipping [gymnasium/wrappers/atari_preprocessing.py:29]().
- **Terminal on Life Loss:** Optionally terminates an episode when a life is lost [gymnasium/wrappers/atari_preprocessing.py:30]().
- **Resize to Square Image:** Resizes the observation to a specified `screen_size` (e.g., 84x84) [gymnasium/wrappers/atari_preprocessing.py:31]().
- **Grayscale Observation:** Converts RGB observations to grayscale [gymnasium/wrappers/atari_preprocessing.py:32]().
- **Grayscale New Axis:** Optionally adds a channel dimension to grayscale observations [gymnasium/wrappers/atari_preprocessing.py:33]().
- **Scale Observation:** Optionally scales observations to `[0, 1)` [gymnasium/wrappers/atari_preprocessing.py:34]().

**Data Flow Diagram for AtariPreprocessing:**

```mermaid
graph TD
    A[Original Atari Env.step()] --> B{Frame Skipping};
    B -- "Multiple steps" --> C[Collect Observations];
    C -- "Last 2 observations" --> D{Max-Pooling};
    D -- "Max-pooled observation" --> E{Grayscale Conversion};
    E -- "Grayscale observation" --> F{Resize to Screen Size};
    F -- "Resized observation" --> G{Optional: Grayscale New Axis};
    G -- "Observation with/without new axis" --> H{Optional: Scale Observation};
    H --> I[Processed Observation];
    I --> J[AtariPreprocessing.step() returns];

    subgraph "Internal State and Logic"
        B -- "noop_max" --> K[Noop Reset on Env.reset()];
        K --> A;
        B -- "frame_skip" --> B;
        D -- "obs_buffer" --> D;
        A -- "lives" --> L{Terminal on Life Loss?};
        L -- "terminated=True" --> J;
    end
```
Sources: [gymnasium/wrappers/atari_preprocessing.py:16-254]()

**Example:**
```python
import gymnasium as gym
import ale_py # Required for Atari environments
gym.register_envs(ale_py)
from gymnasium.wrappers import AtariPreprocessing

env = gym.make("ALE/Pong-v5", frameskip=1) # Disable original frameskip
env = AtariPreprocessing(
    env,
    noop_max=10,
    frame_skip=4,
    terminal_on_life_loss=True,
    screen_size=84,
    grayscale_obs=True,
    grayscale_newaxis=False,
    scale_obs=False,
)
obs, info = env.reset()
# obs will be a (84, 84) grayscale image, processed with frame skipping and max-pooling
```
Sources: [gymnasium/wrappers/atari_preprocessing.py:16-254]()

---

