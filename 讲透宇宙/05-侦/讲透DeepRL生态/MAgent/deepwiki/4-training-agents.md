> 来源: [https://deepwiki.com/geek-ai/MAgent/4-training-agents](https://deepwiki.com/geek-ai/MAgent/4-training-agents)
> DeepWiki geek-ai/MAgent | Last indexed: 26 October 2025 (2144db

# Training Agents

  Relevant source files 
 - [README.md](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1)
 - [doc/get_started.md](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1)
 - [examples/train_battle.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py)
 - [python/magent/model.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py)
 - [src/render/frontend/index.html](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/render/frontend/index.html)
 - [src/render/frontend/js/render-handle.js](https://github.com/geek-ai/MAgent/blob/2144dbd4/src/render/frontend/js/render-handle.js)
 
  
## Purpose and Scope

 This page provides a complete guide to training reinforcement learning agents in MAgent. It covers the training workflow, model interfaces, parallel execution architecture, and practical implementation details. The focus is on the mechanics of collecting experience and updating models through the ProcessingModel system.

 For specific RL algorithm implementations (DQN, DRQN, A2C) and their hyperparameters, see [RL Algorithms](https://deepwiki.com/geek-ai/MAgent/4.3-rl-algorithms). For competitive/cooperative training strategies and opponent modeling, see [Multi-Agent Training Strategies](https://deepwiki.com/geek-ai/MAgent/4.4-multi-agent-training-strategies). For replay buffer implementation and sampling strategies, see [Experience Buffers and Sampling](https://deepwiki.com/geek-ai/MAgent/4.6-experience-buffers-and-sampling).

 
---

 
## Training Workflow Overview

 The MAgent training workflow follows the standard reinforcement learning cycle organized around agent groups. Each group shares an agent type and control policy, enabling parameter sharing across large numbers of agents.

 
### Basic Training Loop Structure

 
```

```

 **Sources:** [examples/train_battle.py43-234](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L43-L234) [doc/get_started.md62-102](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L62-L102)

 
---

 
## Model Interfaces

 MAgent provides a two-tier model architecture: `BaseModel` defines the interface for RL algorithms, while `ProcessingModel` handles parallel execution.

 
### BaseModel Abstract Interface

 The `BaseModel` class defines the contract that all RL algorithm implementations must satisfy:

 
| Method | Purpose | Parameters | Returns |
|---|---|---|---|
| __init__(env, handle, ...) | Initialize model with environment context | env: GridWorld instancehandle: group handle | None |
| infer_action(raw_obs, ids, ...) | Generate actions for agents | raw_obs: (view, feature) tupleids: agent ID array | actions: int32 array |
| train(sample_buffer, ...) | Update model from experience | sample_buffer: EpisodesBuffer instance | (loss, value): training metrics |
| save(save_dir, epoch, ...) | Persist model to disk | save_dir: directory pathepoch: checkpoint number | None |
| load(save_dir, epoch, ...) | Restore model from checkpoint | save_dir: directory pathepoch: checkpoint number | None |

 **Sources:** [python/magent/model.py14-68](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L14-L68)

 
### ProcessingModel: Multi-Process Wrapper

 The `ProcessingModel` class wraps any `BaseModel` implementation in a separate process, enabling true parallelism for multi-agent training:

 
```

```

 **Key Constructor Parameters:**

 
| Parameter | Type | Purpose |
|---|---|---|
| env | GridWorld | Environment instance for querying observation/action spaces |
| handle | GroupHandle | Handle identifying which agent group this model controls |
| name | str | Model name used when saving checkpoints |
| port | int | Port number or pipe suffix for IPC communication |
| sample_buffer_capacity | int | Maximum transitions stored per episode (default: 1000) |
| RLModel | class | BaseModel subclass (e.g., DeepQNetwork) |
| **kwargs | dict | Additional parameters passed to RLModel constructor |

 **Sources:** [python/magent/model.py115-156](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L115-L156) [examples/train_battle.py189-196](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L189-L196)

 
---

 
## Training Data Flow

 
### Phase 1: Observation to Action

 The observation-to-action pipeline demonstrates how non-blocking inference enables parallel model execution:

 
```

```

 **Sources:** [python/magent/model.py174-212](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L174-L212) [python/magent/model.py308-321](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L308-L321) [examples/train_battle.py62-71](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L62-L71)

 
### Phase 2: Reward Collection to Training

 After simulation steps complete, rewards are collected and stored in replay buffers for training:

 
```

```

 **Sources:** [python/magent/model.py157-173](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L157-L173) [python/magent/model.py214-238](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L214-L238) [python/magent/model.py322-326](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L322-L326) [examples/train_battle.py115-127](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L115-L127)

 
---

 
## Parallel Execution Patterns

 
### Non-Blocking Inference for Multiple Groups

 When training multiple agent groups, non-blocking inference allows all models to compute actions simultaneously:

 
```

```

 **Implementation Pattern:**

 
```

```

 **Sources:** [examples/train_battle.py62-71](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L62-L71) [doc/get_started.md66-78](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L66-L78)

 
### Non-Blocking Training Pattern

 Training follows the same pattern, allowing multiple models to update parameters simultaneously:

 
```

```

 **Sources:** [examples/train_battle.py120-124](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L120-L124) [doc/get_started.md82-88](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L82-L88)

 
---

 
## NDArrayPackage: Inter-Process Array Transfer

 The `NDArrayPackage` class handles efficient serialization of NumPy arrays for inter-process communication:

 
```

```

 **Key Features:**

 
| Feature | Implementation | Purpose |
|---|---|---|
| Zero-copy transfer | conn.send_bytes(array) | Direct memory access without intermediate copies |
| Automatic segmentation | max_len = (1 << 30) / 4 (268M items) | Prevents pipe buffer overflow on large arrays |
| Shape preservation | Stores (shape, dtype) metadata | Receiver reconstructs array with correct dimensions |
| Threaded sending | use_thread=True option | Sender continues execution while transfer proceeds |

 **Segmentation Logic:**

 
```

```

 **Sources:** [python/magent/model.py70-112](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L70-L112)

 
---

 
## Complete Training Example

 This example from the battle scenario demonstrates all training components working together:

 
### Environment and Model Initialization

 
```

```

 **Sources:** [examples/train_battle.py152-196](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L152-L196)

 
### Map Generation

 
```

```

 **Sources:** [examples/train_battle.py15-41](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L15-L41)

 
### Training Round Implementation

 
```

```

 **Sources:** [examples/train_battle.py43-131](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L43-L131)

 
### Main Training Loop with Checkpointing

 
```

```

 **Sources:** [examples/train_battle.py214-234](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L214-L234)

 
---

 
## Model State Management

 
### Checkpoint Saving

 The `save()` method persists model state to disk:

 
```

```

 The save operation is dispatched to the subprocess, which handles serialization without blocking the main training loop.

 **Sources:** [python/magent/model.py240-253](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L240-L253) [examples/train_battle.py227-230](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L227-L230)

 
### Checkpoint Loading

 The `load()` method restores model state from disk:

 
```

```

 The optional `name` parameter allows loading a model saved under a different identifier, useful for competitive training where one agent learns against a fixed opponent.

 **Sources:** [python/magent/model.py255-269](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L255-L269) [examples/train_battle.py199-206](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L199-L206)

 
---

 
## Communication Protocol

 The `ProcessingModel` uses a command-based protocol over named pipes (or sockets) for inter-process communication.

 
### Command Protocol Specification

 
| Command | Direction | Parameters | Response | Purpose |
|---|---|---|---|---|
| ["act", policy, eps, array_info] | Main → Sub | policy: str, eps: float, array_info: list | array_info | Request action inference |
| ["sample", array_info] | Main → Sub | array_info: list | "done" | Store transition in buffer |
| ["train", print_every] | Main → Sub | print_every: int | (loss, value) | Train model on buffer |
| ["save", save_dir, epoch] | Main → Sub | save_dir: str, epoch: int | "done" | Save checkpoint |
| ["load", save_dir, epoch, name] | Main → Sub | save_dir: str, epoch: int, name: str | "done" | Load checkpoint |
| ["quit"] | Main → Sub | None | None | Terminate subprocess |

 **Sources:** [python/magent/model.py288-347](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L288-L347)

 
### Subprocess State Machine

 
```

```

 **Sources:** [python/magent/model.py147-156](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L147-L156) [python/magent/model.py288-347](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L288-L347)

 
---

 
## Performance Considerations

 
### Memory Management

 
| Component | Configuration | Typical Value | Impact |
|---|---|---|---|
| Replay Buffer | sample_buffer_capacity | 1000-20000 | Memory per subprocess; affects training stability |
| Batch Size | batch_size | 256-512 | GPU memory usage; affects gradient quality |
| Model Memory | memory_size | 2^20 (1M) | Total transitions stored across episodes |
| Array Segmentation | max_len in NDArrayPackage | 268M items | Prevents pipe buffer overflow |

 **Sources:** [python/magent/model.py120-137](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L120-L137) [python/magent/model.py80](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L80-L80) [examples/train_battle.py168-178](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L168-L178)

 
### Timing Analysis

 With non-blocking operations, inference and sampling for multiple groups execute in parallel:

 
```

```

 Non-blocking execution reduces wall-clock time by approximately 50% when training two groups with equal inference time.

 **Sources:** [examples/train_battle.py62-96](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L62-L96) [doc/get_started.md66-88](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L66-L88)

 
### Scalability Options

 
 - **Horizontal Scaling**: Change pipe addresses to sockets for distributed training:

 
```

```
 - **Vertical Scaling**: Assign different GPUs to each model in the RLModel constructor
 - **Batch Scaling**: Increase `batch_size` for better GPU utilization during training
 
 **Sources:** [python/magent/model.py145-146](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L145-L146) [doc/get_started.md89](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1#L89-L89)

 
---

 
## Error Handling

 
### Non-Blocking Operation Verification

 Always call `check_done()` after non-blocking operations to catch exceptions from the subprocess:

 
```

```

 **Sources:** [python/magent/model.py271-273](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L271-L273) [examples/train_battle.py99-101](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L99-L101)

 
### Common Issues and Solutions

 
| Issue | Symptom | Solution |
|---|---|---|
| Out of Memory | Training crashes with OOM error | Reduce batch_size or memory_size in model args |
| Pipe Buffer Full | Process hangs during array transfer | Arrays auto-segment; issue likely elsewhere |
| Zombie Process | Training script hangs on exit | Call model.quit() for each ProcessingModel |
| Checkpoint Load Failure | Shape mismatch error on load | Verify model architecture matches saved checkpoint |
| Slow Inference | Low FPS during training | Check infer_batch_size in model; reduce if too large |

 **Sources:** [README.md57-58](https://github.com/geek-ai/MAgent/blob/2144dbd4/README.md?plain=1#L57-L58) [python/magent/model.py275-285](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L275-L285)

 
---

 
## Integration with GridWorld

 The training system integrates with the GridWorld environment through group handles:

 
```

```

 Each `ProcessingModel` is bound to a specific group handle at initialization, ensuring observations and actions are correctly attributed.

 **Sources:** [examples/train_battle.py152-196](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py#L152-L196) [python/magent/model.py115-156](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py#L115-L156)

 
---

 
## Summary

 Training agents in MAgent follows these key steps:

 
 - **Initialization**: Create `GridWorld`, obtain group handles, instantiate `ProcessingModel` instances for each group
 - **Sampling**: Execute observation → inference → action → step → reward cycle to collect experience
 - **Training**: Update model parameters from replay buffer using RL algorithm (DQN/DRQN/A2C)
 - **Checkpointing**: Periodically save model state for evaluation and resumption
 - **Parallel Execution**: Leverage non-blocking operations to train multiple groups simultaneously
 
 The `ProcessingModel` architecture enables true parallelism through process isolation, eliminating Python GIL constraints. The `NDArrayPackage` class provides efficient inter-process array transfer with automatic segmentation for large arrays. The command-based protocol ensures coordinated execution between the main training loop and model subprocesses.

 For RL algorithm details, see [RL Algorithms](https://deepwiki.com/geek-ai/MAgent/4.3-rl-algorithms). For multi-agent training strategies, see [Multi-Agent Training Strategies](https://deepwiki.com/geek-ai/MAgent/4.4-multi-agent-training-strategies). For replay buffer implementation, see [Experience Buffers and Sampling](https://deepwiki.com/geek-ai/MAgent/4.6-experience-buffers-and-sampling).

 **Sources:** [examples/train_battle.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/examples/train_battle.py) [python/magent/model.py](https://github.com/geek-ai/MAgent/blob/2144dbd4/python/magent/model.py) [doc/get_started.md](https://github.com/geek-ai/MAgent/blob/2144dbd4/doc/get_started.md?plain=1)
