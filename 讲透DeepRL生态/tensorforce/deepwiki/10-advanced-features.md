> 来源: [https://deepwiki.com/tensorforce/tensorforce/10-advanced-features](https://deepwiki.com/tensorforce/tensorforce/10-advanced-features)
> DeepWiki tensorforce/tensorforce | Last indexed: 24 April 2025 (d384bd

# Advanced Features

  Relevant source files 
 - [docs/basics/features.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1)
 - [docs/basics/getting-started.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1)
 - [test/test_agents.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_agents.py)
 - [test/test_documentation.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_documentation.py)
 - [test/test_examples.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py)
 - [test/test_reward_estimation.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_reward_estimation.py)
 - [test/test_saving.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_saving.py)
 
  This document provides a comprehensive overview of advanced features in the Tensorforce framework that extend beyond the basic usage patterns. These features enable more sophisticated control, optimization, and deployment of reinforcement learning agents. For basic functionality and getting started information, refer to the [Getting Started](https://deepwiki.com/tensorforce/tensorforce/9-getting-started) page.

 
## Agent Persistence

 Tensorforce provides several methods for saving and loading trained agents, allowing you to persist your models for later use, evaluation, or deployment.

 
### Saving and Loading Formats

 The framework supports multiple formats for saving agent states:

 
| Format | Description | Saves | Use Case |
|---|---|---|---|
| checkpoint | TensorFlow native format | Full model state (default) | Complete model preservation |
| numpy | NumPy arrays | Weights only | Lightweight storage |
| hdf5 | HDF5 format | Weights only | Compatibility with other frameworks |
| saved-model | TensorFlow SavedModel | Model for deployment | Production deployment |

 
### Auto-saving During Training

 You can configure agents to automatically save checkpoints during training:

 
```

```

 
### Manual Saving

 Agents can be manually saved at any point:

 
```

```

 
### Loading Saved Agents

 Loading agents is straightforward:

 
```

```

 
#### Advanced SavedModel Loading

 The `saved-model` format allows deployment in production environments:

 
```

```

 **Diagram: Agent Persistence Workflow**

 
```

```

 Sources: [test/test_saving.py65-146](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_saving.py#L65-L146) [docs/basics/features.md94-130](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1#L94-L130)

 
## Reward Estimation

 Tensorforce offers sophisticated reward estimation techniques that can significantly impact agent learning. These features allow you to customize how rewards are processed, returns are calculated, and advantages are estimated.

 
### Horizon Configuration

 The horizon parameter defines how far into the future the agent looks when estimating rewards:

 
| Horizon Setting | Description |
|---|---|
| Fixed integer (e.g., 3) | Use a fixed number of steps |
| 'episode' | Use the entire episode |

 
### Value Prediction Methods

 Value prediction methods determine how the agent estimates future values:

 
| Method | Description |
|---|---|
| False or None | No value prediction (use actual rewards only) |
| 'early' | Predict values at the beginning of the horizon |
| 'late' | Predict values at the end of the horizon |

 
### Advanced Configuration Options

 
```

```

 **Diagram: Reward Estimation Process**

 
```

```

 Sources: [test/test_reward_estimation.py44-68](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_reward_estimation.py#L44-L68) [test/test_reward_estimation.py148-192](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_reward_estimation.py#L148-L192) [test/test_reward_estimation.py228-276](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_reward_estimation.py#L228-L276)

 
## Action Masking

 Action masking allows you to dynamically restrict which actions an agent can take in a given state. This is particularly useful for environments where some actions may be invalid in certain states.

 
### Implementation

 To implement action masking, your environment needs to provide an action mask along with the state. The mask should be a boolean array where `True` indicates that an action is available and `False` indicates it is unavailable.

 
```

```

 The mask should be named with the pattern `'ACTION_NAME_mask'`. With the default action name 'action', this would be `'action_mask'`.

 
### Example Environment With Action Masking

 
```

```

 Sources: [docs/basics/features.md17-34](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1#L17-L34) [test/test_examples.py269-329](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L269-L329) [test/test_documentation.py354-370](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_documentation.py#L354-L370)

 
## Environment Interaction

 Tensorforce provides several advanced features for environment interaction that can improve training efficiency and handle complex scenarios.

 
### Abort-terminal Handling

 Tensorforce distinguishes between genuine episode termination and episode abortion due to reaching a timestep limit:

 
| Terminal Value | Meaning |
|---|---|
| False or 0 | Non-terminal state |
| True or 1 | True terminal state |
| 2 | Abort-terminal (episode reached timestep limit) |

 When environments are created with `max_episode_timesteps`, they automatically return the appropriate terminal value.

 
### Parallel Environment Execution

 There are several approaches to parallel environment execution:

 
 - **Local Batched Execution**:

 
```

```
 - **Multiprocessing Execution**:

 
```

```
 - **Distributed Execution via Sockets**:

 
```

```
 
 
### Vectorized Environments

 For environments that support it, vectorized execution can be more efficient than parallel execution:

 
```

```

 **Diagram: Parallel Execution Architectures**

 
```

```

 Sources: [docs/basics/features.md11-13](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1#L11-L13) [docs/basics/features.md38-78](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1#L38-L78) [test/test_examples.py490-543](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L490-L543) [test/test_examples.py954-1043](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L954-L1043)

 
## Advanced Training Techniques

 Tensorforce offers several advanced training techniques to enhance agent performance, monitoring, and deployment.

 
### TensorBoard Integration

 You can monitor training progress with TensorBoard:

 
```

```

 
### Act-Experience-Update Interface

 This alternative to the standard act-observe pattern gives more control over experience collection:

 
```

```

 
### Record & Pretrain

 You can record agent interactions and use them to pretrain other agents:

 
```

```

 **Diagram: Act-Experience-Update vs Standard Workflow**

 
```

```

 Sources: [docs/basics/features.md135-145](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1#L135-L145) [docs/basics/features.md149-158](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1#L149-L158) [test/test_examples.py204-267](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L204-L267) [test/test_examples.py545-656](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L545-L656)

 
## Multi-actor Environments

 Tensorforce supports environments with multiple actors, allowing for scenarios with multiple agents interacting.

 
### Implementation

 To create a multi-actor environment:

 
 - Implement the `num_actors()` method that returns the number of actors
 - Handle parallel indices in `reset()` and `execute()`
 - Return actor-specific states, actions, and rewards
 
 
```

```

 Sources: [docs/basics/features.md88-90](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1#L88-L90) [test/test_examples.py419-488](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L419-L488)

 
## Summary

 This document has covered the advanced features of the Tensorforce framework that enable sophisticated reinforcement learning applications:

 
 - **Agent Persistence** - Save and load agents in various formats
 - **Reward Estimation** - Configure how rewards are processed and returns estimated
 - **Action Masking** - Restrict available actions based on the environment state
 - **Environment Interaction** - Handle abort-terminals and parallel execution
 - **Advanced Training Techniques** - Use TensorBoard, alternative interfaces, and pretraining
 - **Multi-actor Environments** - Implement environments with multiple actors
 
 These features provide the tools needed to design, train, evaluate, and deploy complex reinforcement learning systems beyond the basic capabilities covered in the getting started guide.
