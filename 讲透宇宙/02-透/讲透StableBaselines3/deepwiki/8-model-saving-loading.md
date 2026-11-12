<!-- source: DeepWiki mcp.deepwiki.com · repo DLR-RM/stable-baselines3 · page 8 Model Saving & Loading · fetched 2026-10-14 -->

# Model Saving & Loading

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [stable_baselines3/common/save_util.py](stable_baselines3/common/save_util.py)
- [tests/test_save_load.py](tests/test_save_load.py)

</details>



This document covers the model persistence system in Stable-Baselines3, including saving and loading complete models, managing model parameters, and handling individual components like policies and replay buffers. The system provides both high-level APIs for complete model persistence and low-level utilities for fine-grained control over serialization.

For information about model deployment and export to other formats, see [Model Export & Deployment](#9.3).

## Overview

The model saving and loading system is built around a ZIP-based archive format that stores multiple components:

```mermaid
graph TB
    subgraph "Model Archive Structure"
        ZipFile["model.zip"]
        Data["data<br/>(JSON + cloudpickle)"]
        PolicyPth["policy.pth<br/>(PyTorch state_dict)"]
        OptimizerPth["policy.optimizer.pth<br/>(PyTorch state_dict)"]
        PyTorchVars["pytorch_variables.pth<br/>(PyTorch tensors)"]
        SystemInfo["system_info.txt<br/>(Environment metadata)"]
        Version["_stable_baselines3_version<br/>(Library version)"]
    end
    
    ZipFile --> Data
    ZipFile --> PolicyPth
    ZipFile --> OptimizerPth
    ZipFile --> PyTorchVars
    ZipFile --> SystemInfo
    ZipFile --> Version
```

**Sources:** [stable_baselines3/common/save_util.py:294-334](), [stable_baselines3/common/save_util.py:376-457]()

## High-Level Save/Load API

### Complete Model Persistence

The primary interface for model persistence is through the `BaseAlgorithm` class methods:

```mermaid
graph LR
    subgraph "BaseAlgorithm API"
        Save["save(path, exclude=None, include=None)"]
        Load["load(path, env=None, device='auto', custom_objects=None)"]
        GetParams["get_parameters()"]
        SetParams["set_parameters(params, exact_match=True)"]
    end
    
    subgraph "Storage Backend"
        ZipArchive["ZIP Archive Format"]
        JSONData["JSON + Cloudpickle Serialization"]
        PyTorchFiles["PyTorch .pth Files"]
    end
    
    Save --> ZipArchive
    Load --> ZipArchive
    ZipArchive --> JSONData
    ZipArchive --> PyTorchFiles
    
    GetParams --> SetParams
```

**Sources:** [tests/test_save_load.py:39-168](), [stable_baselines3/common/save_util.py:294-337]()

### Parameter Management

The system provides granular access to model parameters through structured dictionaries:

| Method | Purpose | Parameters |
|--------|---------|------------|
| `get_parameters()` | Extract all model parameters | Returns nested dict of state_dicts |
| `set_parameters()` | Update model parameters | `params`: dict, `exact_match`: bool |
| `save()` | Persist complete model | `exclude`: list, `include`: list |
| `load()` | Restore complete model | `custom_objects`: dict, `device`: str |

**Sources:** [tests/test_save_load.py:58-125](), [tests/test_save_load.py:246-283]()

## Component-Specific Saving

### Policy Networks

Individual policy components can be saved and loaded independently:

```mermaid
graph TB
    subgraph "Policy Saving System"
        PolicySave["policy.save(path)"]
        PolicyLoad["PolicyClass.load(path)"]
        ActorSave["actor.save(path)"]
        ActorLoad["ActorClass.load(path)"]
        QNetSave["q_net.save(path)"]
        QNetLoad["QNetClass.load(path)"]
    end
    
    subgraph "Supported Components"
        ActorCriticPolicy["ActorCriticPolicy<br/>(PPO, A2C)"]
        SACPolicy["SACPolicy<br/>(SAC)"]
        TD3Policy["TD3Policy<br/>(TD3, DDPG)"]
        DQNPolicy["DQNPolicy<br/>(DQN)"]
    end
    
    PolicySave --> ActorCriticPolicy
    PolicySave --> SACPolicy
    PolicySave --> TD3Policy
    PolicySave --> DQNPolicy
    
    ActorSave --> SACPolicy
    ActorSave --> TD3Policy
    
    QNetSave --> DQNPolicy
```

**Sources:** [tests/test_save_load.py:433-530](), [tests/test_save_load.py:532-606]()

### Replay Buffers

Off-policy algorithms support independent replay buffer persistence:

```mermaid
graph LR
    subgraph "Replay Buffer Persistence"
        SaveBuffer["save_replay_buffer(path)"]
        LoadBuffer["load_replay_buffer(path)"]
        ReplayBuffer["ReplayBuffer<br/>(SAC, TD3, DQN, DDPG)"]
        HerBuffer["HerReplayBuffer<br/>(Goal-conditioned RL)"]
    end
    
    SaveBuffer --> ReplayBuffer
    SaveBuffer --> HerBuffer
    LoadBuffer --> ReplayBuffer
    LoadBuffer --> HerBuffer
    
    subgraph "Buffer Contents"
        Observations["observations"]
        Actions["actions"]
        Rewards["rewards"]
        Dones["dones"]
        Timeouts["timeouts"]
    end
    
    ReplayBuffer --> Observations
    ReplayBuffer --> Actions
    ReplayBuffer --> Rewards
    ReplayBuffer --> Dones
    ReplayBuffer --> Timeouts
```

**Sources:** [tests/test_save_load.py:352-386]()

## Serialization System

### JSON and Cloudpickle Hybrid

The system uses a two-tier serialization strategy to balance portability and functionality. Objects that are JSON serializable are stored directly, while non-JSON serializable objects are serialized using `cloudpickle` and then base64 encoded for storage within the JSON structure. This allows for complex Python objects to be persisted while maintaining a human-readable and somewhat interoperable format for basic data.

```mermaid
graph TB
    subgraph "Serialization Decision Tree"
        Data["Python Object"]
        IsJSONSerializable{"is_json_serializable(item)?"}
        JSONStore["Store as JSON"]
        CloudPickle["Cloudpickle + Base64 Encode"]
        
        Data --> IsJSONSerializable
        IsJSONSerializable -->|Yes| JSONStore
        IsJSONSerializable -->|No| CloudPickle
    end
    
    subgraph "Functions"
        IsJSONSerializableFunc["is_json_serializable(item)"]
        DataToJSONFunc["data_to_json(data)"]
        JSONToDataFunc["json_to_data(json_string, custom_objects)"]
    end
    
    IsJSONSerializable --> IsJSONSerializableFunc
    JSONStore --> DataToJSONFunc
    CloudPickle --> DataToJSONFunc
    JSONToDataFunc --> Data
```

**Sources:** [stable_baselines3/common/save_util.py:60-74](), [stable_baselines3/common/save_util.py:76-128](), [stable_baselines3/common/save_util.py:131-177]()

### Path Management System

The system provides flexible path handling through single dispatch:

```mermaid
graph TB
    subgraph "Path Handling Dispatch"
        OpenPath["open_path(path, mode, verbose, suffix)"]
        StrPath["open_path_str(str)"]
        PathlibPath["open_path_pathlib(pathlib.Path)"]
        BufferedIO["open_path(io.BufferedIOBase)"]
    end
    
    subgraph "Supported Types"
        StringType["str"]
        PathlibType["pathlib.Path"]
        IOType["io.BufferedIOBase"]
    end
    
    OpenPath --> StrPath
    OpenPath --> PathlibPath
    OpenPath --> BufferedIO
    
    StringType --> StrPath
    PathlibType --> PathlibPath
    IOType --> BufferedIO
    
    subgraph "Operations"
        SaveToPkl["save_to_pkl(path, obj)"]
        LoadFromPkl["load_from_pkl(path)"]
        SaveToZip["save_to_zip_file(path, data, params)"]
        LoadFromZip["load_from_zip_file(path, load_data)"]
    end
    
    OpenPath --> SaveToPkl
    OpenPath --> LoadFromPkl
    OpenPath --> SaveToZip
    OpenPath --> LoadFromZip
```

**Sources:** [stable_baselines3/common/save_util.py:181-292](), [stable_baselines3/common/save_util.py:339-374]()

## Advanced Features

### Custom Objects and Parameter Control

The loading system supports fine-grained control over deserialization:

| Feature | Purpose | Usage Example |
|---------|---------|---------------|
| `custom_objects` | Replace deserialized objects | `{"learning_rate": lambda _: 0.001}` |
| `exclude` | Skip saving parameters | `exclude=["verbose", "tensorboard_log"]` |
| `include` | Force save excluded parameters | `include=["verbose"]` |
| `exact_match` | Strict parameter validation | `set_parameters(params, exact_match=True)` |

**Sources:** [tests/test_save_load.py:246-283](), [tests/test_save_load.py:712-740]()

### Device Management

The system automatically handles device placement during model loading:

```mermaid
graph LR
    subgraph "Device Loading Strategy"
        LoadCall["model.load(path, device=device)"]
        DeviceAuto["device='auto'"]
        DeviceCPU["device='cpu'"]
        DeviceCUDA["device='cuda'"]
        GetDevice["get_device(device)"]
    end
    
    LoadCall --> DeviceAuto
    LoadCall --> DeviceCPU
    LoadCall --> DeviceCUDA
    
    DeviceAuto --> GetDevice
    DeviceCPU --> GetDevice
    DeviceCUDA --> GetDevice
    
    subgraph "Target Components"
        ModelDevice["model.device"]
        PolicyDevice["model.policy.device"]
        BufferDevice["model.replay_buffer.device"]
    end
    
    GetDevice --> ModelDevice
    GetDevice --> PolicyDevice
    GetDevice --> BufferDevice
```

**Sources:** [tests/test_save_load.py:136-164](), [tests/test_save_load.py:363-369]()

### Environment Handling

Model loading supports flexible environment management:

```mermaid
graph TB
    subgraph "Environment Loading Options"
        LoadWithEnv["load(path, env=new_env)"]
        LoadWithoutEnv["load(path, env=None)"]
        ForceReset["force_reset=True"]
        KeepState["force_reset=False"]
    end
    
    subgraph "State Management"
        LastObs["model._last_obs"]
        NumTimesteps["model.num_timesteps"]
        ResetSteps["reset_num_timesteps"]
    end
    
    LoadWithEnv --> ForceReset
    LoadWithEnv --> KeepState
    
    ForceReset --> LastObs
    KeepState --> LastObs
    
    ResetSteps --> NumTimesteps
```

**Sources:** [tests/test_save_load.py:171-243]()

## Error Handling and Compatibility

### Version Compatibility

The system handles backward compatibility through warnings and graceful degradation:

```mermaid
graph TB
    subgraph "Compatibility Handling"
        LoadModel["Load Model"]
        VersionCheck["Check SB3 Version"]
        ComponentCheck["Check Component Availability"]
        Warning["Emit Warning"]
        Fallback["Use Fallback"]
    end
    
    subgraph "Common Issues"
        MissingFeatures["Missing features_extractor"]
        InvalidObjects["Invalid serialized objects"]
        TargetParams["Missing target network params"]
        ScheduleCompat["Schedule compatibility"]
    end
    
    LoadModel --> VersionCheck
    VersionCheck --> ComponentCheck
    ComponentCheck --> Warning
    Warning --> Fallback
    
    MissingFeatures --> Warning
    InvalidObjects --> Warning
    TargetParams --> Warning
    ScheduleCompat --> Warning
```

**Sources:** [tests/test_save_load.py:344-349](), [tests/test_save_load.py:814-824](), [tests/test_save_load.py:826-877]()

---

