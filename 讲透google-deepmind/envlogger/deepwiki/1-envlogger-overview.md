<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/envlogger · page 1 EnvLogger Overview · fetched 2026-10-26 -->

# EnvLogger Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docker/Dockerfile](docker/Dockerfile)
- [docs/images/timings.png](docs/images/timings.png)
- [envlogger/backends/in_memory_backend.py](envlogger/backends/in_memory_backend.py)
- [envlogger/backends/riegeli_backend_writer.py](envlogger/backends/riegeli_backend_writer.py)
- [envlogger/examples/random_agent_catch.py](envlogger/examples/random_agent_catch.py)
- [envlogger/setup.py](envlogger/setup.py)

</details>



## Purpose and Scope

EnvLogger is a trajectory logging system for reinforcement learning environments that provides a standard wrapper around `dm_env.Environment` interfaces. It records interactions between agents and environments, storing them persistently for later analysis, training, or evaluation. The system supports multiple storage backends, cross-language integration between Python and C++, and seamless integration with TensorFlow Datasets (TFDS) and Reinforcement Learning Dataset (RLDS) formats.

This document covers the overall system architecture, core components, and data flow patterns. For detailed information about specific storage backends, see [Storage Backends](#3). For build system configuration, see [Build System and Development Setup](#5).

## System Architecture

### Overall Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        EnvLogger["envlogger.EnvLogger<br/>Main wrapper class"]
        Reader["envlogger.Reader<br/>Trajectory reader"]
    end
    
    subgraph "Storage Backend Layer"
        TFDSBackend["TFDSBackendWriter<br/>TensorFlow Datasets backend"]
        RiegeliBackend["RiegeliBackendWriter<br/>High-performance binary storage"]
        InMemoryBackend["InMemoryBackendWriter<br/>Testing/temporary storage"]
    end
    
    subgraph "Data Processing Layer"
        StepData["step_data.StepData<br/>Individual timestep data"]
        Codec["codec.encode/decode<br/>Python serialization"]
        RLDSUtils["RLDS utilities<br/>RL dataset format conversion"]
    end
    
    subgraph "Protocol Buffer Layer"
        StorageProto["storage_pb2.Data<br/>Cross-language data format"]
    end
    
    subgraph "C++ Backend Layer"
        RiegeliDatasetWriter["riegeli_dataset_writer.RiegeliDatasetWriter<br/>C++ implementation"]
        XTensorCodec["xtensor_codec<br/>Numerical array optimization"]
    end
    
    EnvLogger --> TFDSBackend
    EnvLogger --> RiegeliBackend
    EnvLogger --> InMemoryBackend
    
    Reader --> TFDSBackend
    Reader --> RiegeliBackend
    Reader --> InMemoryBackend
    
    TFDSBackend --> RLDSUtils
    RiegeliBackend --> RiegeliDatasetWriter
    
    StepData --> Codec
    Codec --> StorageProto
    StorageProto --> RiegeliDatasetWriter
    StorageProto --> XTensorCodec
    
    style EnvLogger fill:#e8f4f8
    style StorageProto fill:#f0f8e8
    style RiegeliDatasetWriter fill:#f8f0e8
```

Sources: [README.md:1-235](), [envlogger/setup.py:27-174](), [envlogger/backends/riegeli_backend_writer.py:1-100](), [envlogger/backends/in_memory_backend.py:1-92]()

## Core Components

### Environment Wrapper Integration

```mermaid
graph LR
    subgraph "Agent-Environment Loop"
        Agent["RL Agent"]
        Environment["dm_env.Environment"]
    end
    
    subgraph "EnvLogger Core"
        EnvLoggerWrapper["envlogger.EnvLogger"]
        StepFn["step_fn callback<br/>Custom step metadata"]
        EpisodeFn["episode_fn callback<br/>Custom episode metadata"]
    end
    
    subgraph "Data Capture"
        StepDataCapture["step_data.StepData<br/>timestep, action, metadata"]
        MetadataCapture["Metadata Dictionary<br/>Custom user data"]
    end
    
    Agent -->|"actions"| Environment
    Environment -->|"timesteps"| Agent
    
    Environment -.->|"wrapped by"| EnvLoggerWrapper
    
    EnvLoggerWrapper --> StepFn
    EnvLoggerWrapper --> EpisodeFn
    EnvLoggerWrapper --> StepDataCapture
    
    StepFn --> MetadataCapture
    EpisodeFn --> MetadataCapture
    StepDataCapture --> MetadataCapture
```

Sources: [README.md:16-98](), [envlogger/examples/random_agent_catch.py:36-67]()

### Backend Architecture

```mermaid
graph TB
    subgraph "Abstract Interface"
        BackendWriter["backend_writer.BackendWriter<br/>Abstract base class"]
        BackendReader["backend_reader.BackendReader<br/>Abstract base class"]
    end
    
    subgraph "Concrete Implementations"
        TFDSWriter["TFDSBackendWriter<br/>TFDS format writer"]
        RiegeliWriter["RiegeliBackendWriter<br/>Binary format writer"]
        InMemoryWriter["InMemoryBackendWriter<br/>RAM-based writer"]
        
        TFDSReader["TFDSBackendReader<br/>TFDS format reader"]
        RiegeliReader["RiegeliBackendReader<br/>Binary format reader"]
        InMemoryReader["InMemoryBackendReader<br/>RAM-based reader"]
    end
    
    subgraph "Support Components"
        Scheduler["schedulers.BernoulliStepScheduler<br/>Flush timing control"]
        EpisodeInfo["episode_info.EpisodeInfo<br/>Episode metadata"]
    end
    
    BackendWriter <|-- TFDSWriter
    BackendWriter <|-- RiegeliWriter
    BackendWriter <|-- InMemoryWriter
    
    BackendReader <|-- TFDSReader
    BackendReader <|-- RiegeliReader
    BackendReader <|-- InMemoryReader
    
    RiegeliWriter --> Scheduler
    InMemoryWriter --> EpisodeInfo
    InMemoryReader --> EpisodeInfo
```

Sources: [envlogger/backends/riegeli_backend_writer.py:29-100](), [envlogger/backends/in_memory_backend.py:29-92]()

## Data Flow Architecture

### Recording Data Flow

```mermaid
graph TD
    subgraph "Environment Interaction"
        EnvStep["env.step(action)<br/>Returns dm_env.TimeStep"]
        EnvReset["env.reset()<br/>Returns dm_env.TimeStep"]
    end
    
    subgraph "EnvLogger Processing"
        StepRecord["_record_step()<br/>Process timestep data"]
        StepDataCreation["step_data.StepData<br/>Structured data container"]
        MetadataCollection["Metadata Collection<br/>step_fn + episode_fn"]
    end
    
    subgraph "Serialization"
        CodecEncode["codec.encode()<br/>Python to Protocol Buffer"]
        ProtocolBuffer["storage_pb2.Data<br/>Language-neutral format"]
    end
    
    subgraph "Backend Storage"
        BackendWrite["backend._record_step()<br/>Write to storage"]
        FlushScheduler["schedulers.Scheduler<br/>Periodic flushing"]
    end
    
    EnvStep --> StepRecord
    EnvReset --> StepRecord
    
    StepRecord --> MetadataCollection
    StepRecord --> StepDataCreation
    MetadataCollection --> StepDataCreation
    
    StepDataCreation --> CodecEncode
    CodecEncode --> ProtocolBuffer
    
    ProtocolBuffer --> BackendWrite
    BackendWrite --> FlushScheduler
```

Sources: [envlogger/backends/riegeli_backend_writer.py:80-89](), [README.md:40-70]()

### Reading Data Flow

```mermaid
graph TD
    subgraph "Reader Interface"
        ReaderInit["reader.Reader(data_directory)<br/>Initialize reader"]
        EpisodeIteration["for episode in reader.episodes<br/>Episode-level iteration"]
        StepIteration["for step in episode<br/>Step-level iteration"]
    end
    
    subgraph "Backend Reading"
        BackendRead["backend._get_nth_step()<br/>Retrieve stored data"]
        EpisodeInfoRead["backend._get_nth_episode_info()<br/>Episode metadata"]
    end
    
    subgraph "Data Reconstruction"
        CodecDecode["codec.decode()<br/>Protocol Buffer to Python"]
        StepDataReturn["step_data.StepData<br/>Reconstructed timestep"]
    end
    
    ReaderInit --> EpisodeIteration
    EpisodeIteration --> StepIteration
    
    StepIteration --> BackendRead
    EpisodeIteration --> EpisodeInfoRead
    
    BackendRead --> CodecDecode
    CodecDecode --> StepDataReturn
```

Sources: [README.md:149-174](), [envlogger/backends/in_memory_backend.py:66-91]()

## Cross-Language Integration

### Python-C++ Bridge

```mermaid
graph TB
    subgraph "Python Layer"
        PythonAPI["Python API<br/>envlogger.EnvLogger"]
        PythonCodec["Python Codec<br/>codec.encode/decode"]
        PythonBindings["Python Bindings<br/>Pybind11 wrappers"]
    end
    
    subgraph "Protocol Buffer Interface"
        ProtoDefinition["storage.proto<br/>Language-neutral schema"]
        ProtoGenerated["storage_pb2.py<br/>Generated Python bindings"]
    end
    
    subgraph "C++ Layer"
        CppExtensions["C++ Extensions<br/>Bazel-built shared objects"]
        RiegeliCpp["riegeli_dataset_writer<br/>C++ implementation"]
        XTensorCpp["xtensor_codec<br/>Numerical optimization"]
    end
    
    subgraph "Build System"
        BazelBuild["Bazel Build<br/>Cross-language compilation"]
        SetupPy["setup.py<br/>Python package builder"]
    end
    
    PythonAPI --> PythonCodec
    PythonCodec --> ProtoGenerated
    PythonBindings --> CppExtensions
    
    ProtoDefinition --> ProtoGenerated
    ProtoDefinition --> RiegeliCpp
    
    CppExtensions --> RiegeliCpp
    CppExtensions --> XTensorCpp
    
    BazelBuild --> CppExtensions
    SetupPy --> BazelBuild
    SetupPy --> PythonBindings
```

Sources: [envlogger/setup.py:79-137](), [envlogger/setup.py:33-68]()

## Integration Points

### TFDS and RLDS Integration

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| TFDS Backend | TensorFlow Datasets compatibility | `TFDSBackendWriter`, `tfds_backend_writer` |
| RLDS Format | Reinforcement Learning Dataset format | `rlds_utils`, `DatasetConfig` |
| Dataset Configuration | Environment specification | `tfds.features.Tensor`, `tfds.rlds.rlds_base.DatasetConfig` |
| Shard Management | File organization and recovery | `maybe_recover_last_shard`, `max_episodes_per_file` |

Sources: [README.md:100-148]()

### Performance Characteristics

| Backend | Use Case | Performance Notes |
|---------|----------|-------------------|
| InMemory | Testing, small datasets | Fastest access, limited by RAM |
| Riegeli | Production, large datasets | ~2ms overhead per step, compressed storage |
| TFDS | ML pipeline integration | TFDS-compatible format, batch processing |

The system adds approximately 2 milliseconds overhead per environment step based on benchmark data with a random agent on a 100 steps per second Catch environment.

Sources: [README.md:218-228](), [envlogger/backends/in_memory_backend.py:1-92](), [envlogger/backends/riegeli_backend_writer.py:1-100]()

---

