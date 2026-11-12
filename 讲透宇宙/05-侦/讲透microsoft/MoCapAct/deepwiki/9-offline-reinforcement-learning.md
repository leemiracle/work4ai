<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/MoCapAct · page 9 Offline Reinforcement Learning · fetched 2026-10-26 -->

# Offline Reinforcement Learning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mocapact/offline_rl/__init__.py](mocapact/offline_rl/__init__.py)
- [mocapact/offline_rl/d4rl_dataset.py](mocapact/offline_rl/d4rl_dataset.py)

</details>



## Purpose and Scope

This page documents MoCapAct's support for offline reinforcement learning - a paradigm where policies are trained using pre-collected datasets of transitions without additional environment interaction. MoCapAct implements support for offline RL through integration with the D4RL (Datasets for Data-Driven Deep Reinforcement Learning) format, enabling the use of expert rollouts for offline policy learning.

For information about generating and managing the expert dataset used in offline RL, see [Dataset Generation and Management](#3.2).

## Overview of Offline RL in MoCapAct

Offline reinforcement learning in MoCapAct allows for training policies using the expert demonstrations collected from the clip snippet experts, without requiring additional environment interactions. This approach leverages the high-quality motion data to learn policies that can reproduce or extend motion capture behaviors.

```mermaid
flowchart TD
    A["Clip Snippet Experts"] -->|"Generate rollouts"| B["Expert Dataset (HDF5)"]
    B -->|"Convert to D4RL format"| C["D4RLDataset"]
    C -->|"Provide transitions"| D["Offline RL Algorithms"]
    D -->|"Train without environment interaction"| E["Trained Policy"]
    
    subgraph "Data Representation"
        C --- F["observations"]
        C --- G["actions"]
        C --- H["rewards"]
        C --- I["next_observations"]
        C --- J["terminals"]
        C --- K["timeouts"]
    end
```

Sources: [mocapact/offline_rl/d4rl_dataset.py:7-106]()

## D4RL Dataset Integration

MoCapAct implements the `D4RLDataset` class which extends the `ExpertDataset` class to provide compatibility with offline RL libraries that expect the D4RL format. This allows seamless integration with popular offline RL implementations.

```mermaid
classDiagram
    class ExpertDataset {
        +__init__(hdf5_fnames, observables, ...)
        +__getitem__(idx)
        +__len__()
        +normalize_observations()
        +normalize_actions()
    }
    
    class D4RLDataset {
        +__init__(hdf5_fnames, observables, ...)
        +get_in_memory_rollouts(max_transitions)
        -_getitem(dset, idx)
        -_sanity_check(data_dict)
    }
    
    ExpertDataset <|-- D4RLDataset
```

The `D4RLDataset` class specializes the generic `ExpertDataset` by:

1. Restricting sequence steps to 1 (single transitions)
2. Providing a D4RL-compatible interface
3. Ensuring proper handling of terminal states and timeouts
4. Supporting observation and action normalization

Sources: [mocapact/offline_rl/d4rl_dataset.py:7-49]()

## Dataset Structure and Access

The offline RL dataset follows a specific structure to enable efficient training of offline RL algorithms:

| Component | Description |
|-----------|-------------|
| observations | Agent state at time t |
| actions | Actions taken at time t |
| rewards | Rewards received at time t |
| next_observations | Agent state at time t+1 |
| terminals | Boolean flags indicating episode termination due to failure |
| timeouts | Boolean flags indicating episode termination due to time limit |

The dataset can be loaded into memory for efficient access during training:

```mermaid
flowchart LR
    A["HDF5 Dataset Files"] -->|"load via D4RLDataset"| B["In-Memory Rollouts"]
    B --> C{{"Offline RL Algorithm"}}
    
    subgraph "In-Memory Format"
        B --- D["numpy arrays"]
        D --- E["observations: (N, obs_dim)"]
        D --- F["actions: (N, act_dim)"]
        D --- G["rewards: (N,)"]
        D --- H["next_observations: (N, obs_dim)"]
        D --- I["terminals: (N,)"]
        D --- J["timeouts: (N,)"]
    end
```

Sources: [mocapact/offline_rl/d4rl_dataset.py:51-81]()

## Data Processing and Validation

The `D4RLDataset` implements several key processing steps:

1. **Data Loading**: Iteratively loads transitions from HDF5 files into numpy arrays
2. **Normalization**: Optionally normalizes observations and actions (mean 0, std 1)
3. **Validation**: Performs sanity checks on the loaded data to ensure compatibility
4. **Extraction**: Handles proper extraction of observables from the dataset

```mermaid
flowchart TD
    A["get_in_memory_rollouts()"] --> B["Load transitions"]
    B --> C["Convert to numpy arrays"]
    C --> D["_sanity_check()"]
    D --> E["Return data_dict"]
    
    F["_getitem()"] --> G["Find dataset and clip indices"]
    G --> H["Extract observations and actions"]
    H --> I["Apply normalization if enabled"]
    I --> J["Handle terminal states"]
    J --> K["Return transition tuple"]
```

Sources: [mocapact/offline_rl/d4rl_dataset.py:51-154]()

## Using the D4RL Dataset

The `D4RLDataset` class provides a straightforward interface for offline RL:

1. **Initialization**: Create an instance with HDF5 filenames and configuration options
2. **Data Access**: Access transitions via indexing or iteration
3. **Memory Loading**: Load all transitions into memory with `get_in_memory_rollouts()`

The dataset supports several configuration options:

| Option | Description |
|--------|-------------|
| `normalize_obs` | Normalize observations to mean 0, std 1 |
| `normalize_act` | Normalize actions to mean 0, std 1 |
| `return_mean_act` | Use mean actions instead of sampled actions |
| `max_transitions` | Maximum number of transitions to load into memory |
| `clip_ids` | Specific clip IDs to include in the dataset |

Sources: [mocapact/offline_rl/d4rl_dataset.py:13-49]()

## Integration with Offline RL Algorithms

MoCapAct's `D4RLDataset` is designed to be compatible with popular offline RL implementations like those found in the D4RL benchmark. This enables training policies using algorithms such as:

- Behavioral Cloning (BC)
- Conservative Q-Learning (CQL)
- Implicit Q-Learning (IQL)
- Advantage-Weighted Regression (AWR)
- Return-Weighted Regression (RWR)

The following diagram illustrates how the `D4RLDataset` integrates with offline RL algorithms:

```mermaid
flowchart TD
    A["MoCap Expert Rollouts"] -->|"stored in"| B["HDF5 Files"]
    B -->|"loaded by"| C["D4RLDataset"]
    C -->|"provides transitions"| D["Offline RL Algorithm"]
    D -->|"trains"| E["Policy Network"]
    E -->|"can be evaluated in"| F["MoCapAct Environments"]
    
    subgraph "D4RLDataset"
        C1["__getitem__()"] --> C2["Observation\nNormalization"]
        C1 --> C3["Action\nNormalization"]
        C1 --> C4["Terminal/Timeout\nHandling"]
    end
    
    subgraph "Offline RL Algorithms"
        D1["Behavioral Cloning"]
        D2["Conservative Q-Learning"]
        D3["Implicit Q-Learning"]
        D4["Advantage-Weighted Regression"]
    end
```

Sources: [mocapact/offline_rl/d4rl_dataset.py:7-154]()

## Summary

MoCapAct provides a robust implementation for offline reinforcement learning through its `D4RLDataset` class, which adapts the expert rollout data to a format compatible with standard offline RL algorithms. This enables:

1. Training policies from expert demonstrations without environment interaction
2. Compatibility with existing offline RL implementations
3. Efficient data loading and preprocessing
4. Proper handling of terminal states and episode boundaries
5. Normalization of observations and actions

These capabilities allow researchers to explore offline learning techniques with the high-quality motion capture data supported by MoCapAct.

Sources: [mocapact/offline_rl/d4rl_dataset.py:7-154]()

---

