> 来源: [https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/3-environment-system](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/3-environment-system)
> DeepWiki ikostrikov/pytorch-a2c-ppo-acktr-gail | Last indexed: 21 April 2025 (41332b

# Environment System

  Relevant source files 
 - [a2c_ppo_acktr/envs.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py)
 - [evaluation.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/evaluation.py)
 
  The Environment System in the pytorch-a2c-ppo-acktr-gail repository provides a standardized interface for reinforcement learning algorithms to interact with various simulation environments. It handles environment creation, preprocessing, vectorization, observation normalization, and frame stacking to ensure that different environments can be used consistently with the implemented algorithms.

 For information about how this system integrates with the training loop, see [Training System](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/2-training-system).

 
## Environment Creation Process

 The environment creation is managed through two primary functions:

 
 - `make_env`: Creates a single environment with appropriate wrappers
 - `make_vec_envs`: Creates multiple environments and combines them into a vectorized environment
 
 
```

```

 Sources: [a2c_ppo_acktr/envs.py35-80](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L35-L80) [a2c_ppo_acktr/envs.py83-114](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L83-L114)

 
## Supported Environment Types

 The system supports multiple environment types:

 
| Environment Type | Creation Method | Additional Support |
|---|---|---|
| OpenAI Gym | gym.make() | General environments |
| Atari Games | gym.make() | Special preprocessing wrappers |
| DeepMind Control Suite | dmc2gym.make() | Domain/task specification |
| Roboschool | gym.make() | Imported if available |
| PyBullet | gym.make() | Imported if available |

 Sources: [a2c_ppo_acktr/envs.py19-32](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L19-L32) [a2c_ppo_acktr/envs.py37-42](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L37-L42)

 
## Environment Wrappers

 Environment wrappers modify the behavior of environments or preprocess observations. The system uses various types of wrappers:

 
```

```

 Sources: [a2c_ppo_acktr/envs.py118-127](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L118-L127) [a2c_ppo_acktr/envs.py138-164](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L138-L164) [a2c_ppo_acktr/envs.py167-190](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L167-L190) [a2c_ppo_acktr/envs.py193-213](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L193-L213) [a2c_ppo_acktr/envs.py218-259](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L218-L259)

 
### Basic Wrappers

 
 - **TimeLimitMask**: Marks transitions that occur due to time limits in the environment

 
 - Important for correct value estimation since time-limited terminations aren't true episode ends
 - **TransposeImage**: Transposes image observations to the format expected by PyTorch (BCHW)

 
 - Converts from environment's (H,W,C) format to PyTorch's (C,H,W) format
 
 Sources: [a2c_ppo_acktr/envs.py118-127](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L118-L127) [a2c_ppo_acktr/envs.py146-164](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L146-L164)

 
### Atari-Specific Wrappers

 For Atari environments, specialized preprocessing is applied:

 
| Wrapper | Purpose |
|---|---|
| NoopResetEnv | Performs random number of no-op actions at episode start |
| MaxAndSkipEnv | Skips frames (usually 4) to reduce computation |
| EpisodicLifeEnv | Treats loss of life as end of episode |
| FireResetEnv | Presses FIRE button to start games that require it |
| WarpFrame | Resizes frames to 84x84 and converts to grayscale |
| ClipRewardEnv | Clips rewards to {-1, 0, 1} |

 Sources: [a2c_ppo_acktr/envs.py44-66](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L44-L66)

 
### Vectorized Environment Wrappers

 Vectorized environments allow running multiple environment instances in parallel:

 
 - **VecPyTorch**: Converts observations to PyTorch tensors and handles action conversion

 
 - Translates between NumPy arrays and PyTorch tensors
 - Ensures proper device placement (CPU/GPU)
 - **VecNormalize**: Normalizes observations and optionally rewards

 
 - Tracks running mean and standard deviation
 - Can be toggled between training and evaluation modes
 - Essential for stable training on environments with varying scales
 - **VecPyTorchFrameStack**: Stacks multiple frames together for temporal information

 
 - Important for partially observable environments
 - Default of 4 frames for image observations
 
 Sources: [a2c_ppo_acktr/envs.py167-190](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L167-L190) [a2c_ppo_acktr/envs.py193-213](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L193-L213) [a2c_ppo_acktr/envs.py218-259](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L218-L259)

 
## Environment Interaction Flow

 The Environment System interacts with other components in the reinforcement learning framework as follows:

 
```

```

 Sources: [a2c_ppo_acktr/envs.py83-114](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L83-L114) [evaluation.py8-48](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/evaluation.py#L8-L48)

 
## Usage in Evaluation

 The Environment System is also used during evaluation through the `evaluate` function:

 
 - Create evaluation environments using `make_vec_envs` with a different seed
 - If observation normalization is used, the statistics are shared from the training environments
 - Evaluation runs until a sufficient number of episodes are completed
 - Mean reward is calculated across completed episodes
 
 Sources: [evaluation.py8-48](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/evaluation.py#L8-L48)

 
## Key Implementation Details

 
### make_env Function

 The `make_env` function creates a thunk (closure) that sets up an environment with appropriate wrappers:

 
 - Creates base environment based on ID
 - Applies specialized Atari preprocessing if needed
 - Sets the random seed
 - Adds `TimeLimitMask` if the environment has a time limit
 - Adds monitoring wrapper if logging is enabled
 - Applies additional Atari preprocessing if needed
 - Transposes image observations for PyTorch compatibility
 
 Sources: [a2c_ppo_acktr/envs.py35-80](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L35-L80)

 
### make_vec_envs Function

 The `make_vec_envs` function creates multiple environments and combines them:

 
 - Creates multiple environment thunks using `make_env`
 - Combines them using `SubprocVecEnv` (parallel) or `DummyVecEnv` (sequential)
 - Applies `VecNormalize` for 1D observation spaces
 - Wraps with `VecPyTorch` to convert to PyTorch tensors
 - Applies `VecPyTorchFrameStack` if needed
 
 Sources: [a2c_ppo_acktr/envs.py83-114](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L83-L114)

 
### VecPyTorch

 The `VecPyTorch` wrapper handles the conversion between NumPy arrays and PyTorch tensors:

 
 - Converts observations from NumPy to PyTorch tensors
 - Converts actions from PyTorch to NumPy for the environment
 - Ensures tensors are on the correct device (CPU/GPU)
 
 Sources: [a2c_ppo_acktr/envs.py167-190](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L167-L190)

 
### VecNormalize

 The `VecNormalize` wrapper normalizes observations and optionally rewards:

 
 - Extends `VecNormalize_` from stable-baselines3
 - Adds `train()` and `eval()` methods to control statistic updates
 - Normalizes observations using running mean and variance
 
 Sources: [a2c_ppo_acktr/envs.py193-213](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L193-L213)

 
### VecPyTorchFrameStack

 The `VecPyTorchFrameStack` wrapper stacks multiple frames along the first dimension:

 
 - Maintains a tensor of stacked observations
 - Updates the stack with each new observation
 - Resets the stack when an episode ends
 - Ensures proper device placement (CPU/GPU)
 
 Sources: [a2c_ppo_acktr/envs.py218-259](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/envs.py#L218-L259)
