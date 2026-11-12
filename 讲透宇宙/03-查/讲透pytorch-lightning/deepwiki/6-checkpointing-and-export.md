<!-- source: DeepWiki mcp.deepwiki.com · repo Lightning-AI/pytorch-lightning · page 6 Checkpointing and Export · fetched 2026-10-21 -->

# Checkpointing and Model Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source-fabric/api/fabric_methods.rst](docs/source-fabric/api/fabric_methods.rst)
- [docs/source-fabric/api/wrappers.rst](docs/source-fabric/api/wrappers.rst)
- [src/lightning/fabric/CHANGELOG.md](src/lightning/fabric/CHANGELOG.md)
- [src/lightning/fabric/fabric.py](src/lightning/fabric/fabric.py)
- [src/lightning/fabric/strategies/ddp.py](src/lightning/fabric/strategies/ddp.py)
- [src/lightning/fabric/strategies/deepspeed.py](src/lightning/fabric/strategies/deepspeed.py)
- [src/lightning/fabric/strategies/fsdp.py](src/lightning/fabric/strategies/fsdp.py)
- [src/lightning/fabric/strategies/strategy.py](src/lightning/fabric/strategies/strategy.py)
- [src/lightning/pytorch/CHANGELOG.md](src/lightning/pytorch/CHANGELOG.md)
- [src/lightning/pytorch/core/module.py](src/lightning/pytorch/core/module.py)
- [src/lightning/pytorch/strategies/ddp.py](src/lightning/pytorch/strategies/ddp.py)
- [src/lightning/pytorch/strategies/deepspeed.py](src/lightning/pytorch/strategies/deepspeed.py)
- [src/lightning/pytorch/strategies/fsdp.py](src/lightning/pytorch/strategies/fsdp.py)
- [src/lightning/pytorch/strategies/strategy.py](src/lightning/pytorch/strategies/strategy.py)
- [tests/tests_fabric/strategies/test_ddp.py](tests/tests_fabric/strategies/test_ddp.py)
- [tests/tests_fabric/strategies/test_deepspeed.py](tests/tests_fabric/strategies/test_deepspeed.py)
- [tests/tests_fabric/strategies/test_deepspeed_integration.py](tests/tests_fabric/strategies/test_deepspeed_integration.py)
- [tests/tests_fabric/strategies/test_fsdp.py](tests/tests_fabric/strategies/test_fsdp.py)
- [tests/tests_fabric/strategies/test_fsdp_integration.py](tests/tests_fabric/strategies/test_fsdp_integration.py)
- [tests/tests_fabric/strategies/test_single_device.py](tests/tests_fabric/strategies/test_single_device.py)
- [tests/tests_fabric/test_fabric.py](tests/tests_fabric/test_fabric.py)
- [tests/tests_pytorch/models/test_onnx.py](tests/tests_pytorch/models/test_onnx.py)
- [tests/tests_pytorch/strategies/test_ddp.py](tests/tests_pytorch/strategies/test_ddp.py)
- [tests/tests_pytorch/strategies/test_ddp_integration.py](tests/tests_pytorch/strategies/test_ddp_integration.py)
- [tests/tests_pytorch/strategies/test_deepspeed.py](tests/tests_pytorch/strategies/test_deepspeed.py)
- [tests/tests_pytorch/strategies/test_fsdp.py](tests/tests_pytorch/strategies/test_fsdp.py)

</details>



This document covers PyTorch Lightning's checkpointing system and model registry infrastructure. The checkpointing system handles saving and loading model states, configurations, and training metadata, while the model registry provides versioning and management capabilities for deployed models.

For information about training loop callbacks and model lifecycle hooks, see [Training System](#4). For distributed training coordination, see [Distributed Training](#3).

## System Architecture Overview

The checkpointing and model management system consists of two main subsystems: the checkpoint system for persistent state management and the model registry for model versioning and deployment.

```mermaid
graph TB
    subgraph "User Interface"
        Trainer["Trainer"]
        CLI["LightningCLI"]
        Fabric["Fabric"]
    end
    
    subgraph "Checkpoint System"
        CheckpointConn["CheckpointConnector"]
        SaveConfigCB["SaveConfigCallback"]
        ModelCheckpoint["ModelCheckpoint"]
    end
    
    subgraph "Loading Infrastructure"
        LazyLoad["_lazy_load"]
        NotYetLoadedTensor["_NotYetLoadedTensor"]
        MaterializeTensors["_materialize_tensors"]
    end
    
    subgraph "Distributed Checkpoints"
        FSDPCheckpoint["FSDP Checkpoint"]
        ConsolidateCP["consolidate_checkpoint"]
        DistributedLoad["_load_distributed_checkpoint"]
    end
    
    subgraph "Model Registry"
        RegistryParser["_parse_registry_model_version"]
        ModelFolder["_determine_model_folder"]
        RegistryValidator["_is_registry"]
    end
    
    subgraph "Storage Backends"
        LocalFS["Local FileSystem"]
        CloudFS["Cloud Storage"]
        S3["S3/GCS/Azure"]
    end
    
    Trainer --> CheckpointConn
    CLI --> SaveConfigCB
    Fabric --> LazyLoad
    
    CheckpointConn --> ModelCheckpoint
    CheckpointConn --> SaveConfigCB
    
    LazyLoad --> NotYetLoadedTensor
    NotYetLoadedTensor --> MaterializeTensors
    
    FSDPCheckpoint --> ConsolidateCP
    ConsolidateCP --> DistributedLoad
    
    ModelCheckpoint --> RegistryParser
    RegistryParser --> ModelFolder
    RegistryParser --> RegistryValidator
    
    CheckpointConn --> LocalFS
    CheckpointConn --> CloudFS
    ModelFolder --> S3
```

Sources: [src/lightning/pytorch/cli.py:214-310](), [src/lightning/fabric/utilities/load.py:207-214](), [src/lightning/pytorch/utilities/model_registry.py:29-51](), [docs/source-fabric/guide/checkpoint/distributed_checkpoint.rst:1-38]()

## Checkpoint Loading Architecture

The checkpoint loading system uses lazy loading and tensor materialization to efficiently handle large model states without loading everything into memory at once.

### Lazy Loading Implementation

```mermaid
graph TD
    subgraph "Loading Process"
        LoadRequest["torch.load() / fabric.load()"]
        LazyUnpickler["_LazyLoadingUnpickler"]
        NotYetLoaded["_NotYetLoadedTensor"]
        MaterializeCall["_materialize_tensors()"]
        ActualTensor["torch.Tensor"]
    end
    
    subgraph "Tensor Rebuild System"
        RebuildTensorV2["rebuild_tensor_v2"]
        RebuildParam["rebuild_parameter"]
        RebuildFromType["rebuild_from_type_v2"]
    end
    
    subgraph "Storage Access"
        PyTorchReader["torch.PyTorchFileReader"]
        StorageRecord["storage.archiveinfo"]
        TypedStorage["TypedStorage"]
    end
    
    LoadRequest --> LazyUnpickler
    LazyUnpickler --> NotYetLoaded
    NotYetLoaded --> MaterializeCall
    MaterializeCall --> ActualTensor
    
    LazyUnpickler --> RebuildTensorV2
    RebuildTensorV2 --> RebuildParam
    RebuildParam --> RebuildFromType
    
    NotYetLoaded --> PyTorchReader
    PyTorchReader --> StorageRecord
    StorageRecord --> TypedStorage
```

Sources: [src/lightning/fabric/utilities/load.py:41-176](), [src/lightning/fabric/utilities/load.py:178-205](), [src/lightning/fabric/utilities/load.py:216-221]()

The `_NotYetLoadedTensor` class implements `__torch_function__` to intercept tensor operations and materialize tensors only when needed. This prevents memory exhaustion when loading large checkpoints by keeping tensors as metadata until actually accessed.

### Configuration and State Management

The `SaveConfigCallback` automatically saves training configurations and handles checkpoint metadata:

```mermaid
graph LR
    subgraph "Configuration Saving"
        LightningCLI["LightningCLI"]
        SaveConfigCB["SaveConfigCallback"]
        ParserDump["parser.dump()"]
        ConfigYAML["config.yaml"]
    end
    
    subgraph "State Persistence"
        StateDict["state_dict()"]
        CallbackState["callback_state_dicts"]
        CheckpointDict["checkpoint.ckpt"]
    end
    
    subgraph "Loading Restoration"
        LoadStateDict["load_state_dict()"]
        OnLoadCheckpoint["on_load_checkpoint()"]
        StateRestoration["state restoration"]
    end
    
    LightningCLI --> SaveConfigCB
    SaveConfigCB --> ParserDump
    ParserDump --> ConfigYAML
    
    StateDict --> CallbackState
    CallbackState --> CheckpointDict
    
    CheckpointDict --> LoadStateDict
    LoadStateDict --> OnLoadCheckpoint
    OnLoadCheckpoint --> StateRestoration
```

Sources: [src/lightning/pytorch/cli.py:230-309](), [src/lightning/pytorch/trainer/call.py:235-310](), [src/lightning/fabric/utilities/load.py:223-237]()

## Distributed Checkpointing

Distributed checkpointing enables efficient saving and loading of large models across multiple devices by sharding the state across nodes.

### FSDP Checkpoint Architecture

```mermaid
graph TB
    subgraph "Distributed Training"
        FSDPModel["FSDP Model"]
        ShardedState["Sharded State Dict"]
        LocalShard["Local Shard"]
    end
    
    subgraph "Checkpoint Sharding"
        MetadataFile["meta.pt"]
        ShardFiles["__0_0.distcp, __1_0.distcp, ..."]
        CheckpointDir["checkpoint/"]
    end
    
    subgraph "Consolidation Process"
        ConsolidateTool["consolidate_checkpoint.py"]
        LoadDistributed["_load_distributed_checkpoint()"]
        SingleFile["consolidated.ckpt"]
    end
    
    subgraph "Loading Process"
        DistLoad["torch.distributed.checkpoint.load()"]
        ShardMapping["shard mapping"]
        StateReconstruction["state reconstruction"]
    end
    
    FSDPModel --> ShardedState
    ShardedState --> LocalShard
    LocalShard --> MetadataFile
    LocalShard --> ShardFiles
    MetadataFile --> CheckpointDir
    ShardFiles --> CheckpointDir
    
    CheckpointDir --> ConsolidateTool
    ConsolidateTool --> LoadDistributed
    LoadDistributed --> SingleFile
    
    CheckpointDir --> DistLoad
    DistLoad --> ShardMapping
    ShardMapping --> StateReconstruction
```

Sources: [docs/source-fabric/guide/checkpoint/distributed_checkpoint.rst:13-38](), [src/lightning/fabric/utilities/consolidate_checkpoint.py:14-72](), [src/lightning/pytorch/utilities/consolidate_checkpoint.py:10-26]()

The consolidation process merges distributed checkpoint shards into a single file that can be loaded with standard `torch.load()`. The `_format_checkpoint` function handles the conversion between FSDP format and Lightning Trainer format.

### Checkpoint Upgrade System

```mermaid
graph LR
    subgraph "Legacy Support"
        OldCheckpoint["Legacy .ckpt"]
        UpgradeTool["upgrade_checkpoint.py"]
        MigrateCP["migrate_checkpoint()"]
        NewFormat["Updated .ckpt"]
    end
    
    subgraph "Migration Process"
        PLLegacyPatch["pl_legacy_patch()"]
        VersionCheck["version detection"]
        StateTransform["state transformation"]
    end
    
    subgraph "Batch Processing"
        DirectoryScanner["directory scanner"]
        FilePattern["*.ckpt pattern"]
        ProgressBar["tqdm progress"]
    end
    
    OldCheckpoint --> UpgradeTool
    UpgradeTool --> MigrateCP
    MigrateCP --> NewFormat
    
    MigrateCP --> PLLegacyPatch
    PLLegacyPatch --> VersionCheck
    VersionCheck --> StateTransform
    
    UpgradeTool --> DirectoryScanner
    DirectoryScanner --> FilePattern
    FilePattern --> ProgressBar
```

Sources: [src/lightning/pytorch/utilities/upgrade_checkpoint.py:29-49](), [src/lightning/pytorch/utilities/upgrade_checkpoint.py:59-95](), [tests/tests_pytorch/utilities/test_upgrade_checkpoint.py:25-46]()

## Model Registry System

The model registry provides a standardized way to reference and manage model versions using URI-like paths.

### Registry Path Resolution

```mermaid
graph TD
    subgraph "Registry Path Format"
        RegistryURI["registry:model-name:version:1.0"]
        ParseFunction["_parse_registry_model_version()"]
        ModelName["model-name"]
        Version["1.0"]
    end
    
    subgraph "Path Validation"
        IsRegistryCheck["_is_registry()"]
        PatternMatch["^registry(:.*|$)"]
        ValidFormat["valid format"]
    end
    
    subgraph "Storage Resolution"
        DetermineFolder["_determine_model_folder()"]
        RemoteConfig["remote config"]
        LocalCache["local cache"]
        FinalPath["resolved path"]
    end
    
    RegistryURI --> ParseFunction
    ParseFunction --> ModelName
    ParseFunction --> Version
    
    RegistryURI --> IsRegistryCheck
    IsRegistryCheck --> PatternMatch
    PatternMatch --> ValidFormat
    
    ModelName --> DetermineFolder
    Version --> DetermineFolder
    DetermineFolder --> RemoteConfig
    DetermineFolder --> LocalCache
    DetermineFolder --> FinalPath
```

Sources: [src/lightning/pytorch/utilities/model_registry.py:29-51](), [src/lightning/pytorch/utilities/model_registry.py:53-78](), [src/lightning/pytorch/utilities/model_registry.py:80-135]()

### Model Versioning and Storage

The registry system supports both local and remote model storage with automatic path resolution:

```mermaid
graph LR
    subgraph "Registry Resolution"
        RegistryPath["registry:model:v1.0"]
        ConfigLookup["config lookup"]
        URLResolution["URL resolution"]
    end
    
    subgraph "Storage Backends"
        LocalDir["~/.cache/models/"]
        S3Bucket["s3://models/"]
        HTTPEndpoint["https://api.models/"]
    end
    
    subgraph "Download Management"
        CacheCheck["cache check"]
        DownloadModel["download model"]
        VerifyChecksum["verify checksum"]
        LocalCache["update cache"]
    end
    
    RegistryPath --> ConfigLookup
    ConfigLookup --> URLResolution
    URLResolution --> LocalDir
    URLResolution --> S3Bucket
    URLResolution --> HTTPEndpoint
    
    S3Bucket --> CacheCheck
    HTTPEndpoint --> CacheCheck
    CacheCheck --> DownloadModel
    DownloadModel --> VerifyChecksum
    VerifyChecksum --> LocalCache
```

Sources: [src/lightning/pytorch/utilities/model_registry.py:137-185](), [src/lightning/pytorch/utilities/model_registry.py:187-234]()

The `_determine_model_folder` function handles the complex logic of resolving registry paths to actual file system locations, supporting both local caching and remote model repositories. The system integrates with cloud storage providers and can automatically download models on first access.

---

