<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/accelerate · page 11 Experiment Tracking · fetched 2026-10-21 -->

# Experiment Tracking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/package_reference/tracking.md](docs/source/package_reference/tracking.md)
- [docs/source/usage_guides/tracking.md](docs/source/usage_guides/tracking.md)
- [examples/by_feature/README.md](examples/by_feature/README.md)
- [src/accelerate/tracking.py](src/accelerate/tracking.py)
- [tests/test_examples.py](tests/test_examples.py)
- [tests/test_tracking.py](tests/test_tracking.py)

</details>



This page documents the experiment tracking system in Accelerate, which provides a unified interface for logging metrics, hyperparameters, and artifacts to various tracking platforms. The tracking system supports TensorBoard, Weights & Biases, CometML, MLflow, Aim, ClearML, DVCLive, SwanLab, and trackio through a common API.

For information about how the Accelerator class manages trackers, see [The Accelerator Class](#2). For details on the `log_with` parameter during initialization, see [Initialization and Configuration](#2.1).

---

## Purpose and Scope

The tracking system enables users to:
- Initialize one or more experiment tracking platforms with a single API call
- Log metrics, hyperparameters, images, and tables during training
- Coordinate logging across distributed processes (main process only by default)
- Create custom tracker integrations by extending the base class

The tracking system is designed to work seamlessly with distributed training, automatically handling multi-process coordination and ensuring that logging operations don't interfere with training performance.

Sources: [src/accelerate/tracking.py:1-43]()

---

## System Architecture

The tracking system follows a plugin-based architecture where each tracking platform is implemented as a subclass of `GeneralTracker`. The `Accelerator` class manages tracker lifecycle and provides the user-facing API.

### Component Diagram

```mermaid
graph TB
    subgraph "User Interface"
        AcceleratorAPI["Accelerator<br/>init_trackers()<br/>log()<br/>end_training()"]
    end
    
    subgraph "Core Tracking System"
        GeneralTracker["GeneralTracker<br/>Base Class<br/>tracking.py:102-178"]
        filter_trackers["filter_trackers()<br/>Validation & Setup<br/>tracking.py:1262-1318"]
        on_main_process["on_main_process<br/>Decorator<br/>tracking.py:78-94"]
    end
    
    subgraph "Tracker Implementations"
        TensorBoard["TensorBoardTracker<br/>tracking.py:179-295<br/>requires_logging_directory=True"]
        WandB["WandBTracker<br/>tracking.py:297-420<br/>main_process_only=False"]
        Trackio["TrackioTracker<br/>tracking.py:422-497"]
        CometML["CometMLTracker<br/>tracking.py:499-591"]
        Aim["AimTracker<br/>tracking.py:593-694"]
        MLflow["MLflowTracker<br/>tracking.py:696-901"]
        ClearML["ClearMLTracker<br/>tracking.py:903-1059"]
        DVCLive["DVCLiveTracker<br/>tracking.py:1061-1147"]
        SwanLab["SwanLabTracker<br/>tracking.py:1149-1247"]
    end
    
    subgraph "Tracker Registry"
        LOGGER_TYPE_TO_CLASS["LOGGER_TYPE_TO_CLASS<br/>Dict mapping<br/>tracking.py:1249-1260"]
        _available_trackers["_available_trackers<br/>Runtime detection<br/>tracking.py:46-73"]
    end
    
    AcceleratorAPI --> filter_trackers
    filter_trackers --> LOGGER_TYPE_TO_CLASS
    filter_trackers --> _available_trackers
    
    GeneralTracker --> TensorBoard
    GeneralTracker --> WandB
    GeneralTracker --> Trackio
    GeneralTracker --> CometML
    GeneralTracker --> Aim
    GeneralTracker --> MLflow
    GeneralTracker --> ClearML
    GeneralTracker --> DVCLive
    GeneralTracker --> SwanLab
    
    on_main_process -.decorates.-> TensorBoard
    on_main_process -.decorates.-> WandB
    on_main_process -.decorates.-> CometML
```

Sources: [src/accelerate/tracking.py:1-1318](), [src/accelerate/tracking.py:46-73](), [src/accelerate/tracking.py:1249-1260]()

---

## GeneralTracker Base Class

All tracker implementations inherit from `GeneralTracker`, which defines the standard interface for experiment tracking platforms. For detailed implementation guides, see [Tracker Integration](#11.1).

### Required Attributes and Properties

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | String identifier for the tracker (e.g., "tensorboard", "wandb") |
| `requires_logging_directory` | `bool` | Whether the tracker needs a filesystem directory for logs |
| `tracker` | `property` | Returns the underlying tracker object (e.g., `SummaryWriter`, `wandb.run`) |
| `main_process_only` | `bool` | Whether operations should only run on the main process (default: `True`) |

### Core Methods

```mermaid
graph LR
    subgraph "Tracker Lifecycle"
        Init["__init__()<br/>Store configuration"]
        Start["start()<br/>Lazy initialization"]
        StoreConfig["store_init_configuration()<br/>Log hyperparameters"]
        Log["log()<br/>Log metrics"]
        Finish["finish()<br/>Cleanup"]
    end
    
    Init --> Start
    Start --> StoreConfig
    StoreConfig --> Log
    Log --> Finish
```

**Method Signatures:**

- `__init__(self, _blank=False)` - Constructor that validates required attributes [src/accelerate/tracking.py:121-141]()
- `start(self)` - Lazy initialization called by Accelerator after distributed setup [src/accelerate/tracking.py:143-147]()
- `store_init_configuration(self, values: dict)` - Log hyperparameters at experiment start [src/accelerate/tracking.py:149-159]()
- `log(self, values: dict, step: Optional[int], **kwargs)` - Log metrics during training [src/accelerate/tracking.py:161-171]()
- `finish(self)` - Clean up resources and finalize logging [src/accelerate/tracking.py:173-177]()

Sources: [src/accelerate/tracking.py:102-178]()

---

## Supported Trackers

Accelerate supports nine experiment tracking platforms out of the box. For usage instructions, see [Tracker Integration](#11.1).

### Tracker Comparison Table

| Tracker | Class Name | Requires Logging Dir | Main Process Only | Special Features |
|---------|-----------|---------------------|-------------------|------------------|
| TensorBoard | `TensorBoardTracker` | ✓ | ✓ | Writes to local filesystem, supports scalars/text/images |
| Weights & Biases | `WandBTracker` | ✗ | ✗ | Cloud-based, supports tables, all processes can log |
| trackio | `TrackioTracker` | ✗ | ✗ | Lightweight alternative to WandB |
| CometML | `CometMLTracker` | ✗ | ✓ | Supports offline mode, experiment resumption |
| Aim | `AimTracker` | ✓ | ✓ | Local-first tracking, custom visualizations |
| MLflow | `MLflowTracker` | ✗ | ✓ | Supports artifacts, model logging, figure logging |
| ClearML | `ClearMLTracker` | ✗ | ✓ | Auto-detects existing tasks, supports tables/images |
| DVCLive | `DVCLiveTracker` | ✗ | ✓ | Integrates with DVC, Git-based versioning |
| SwanLab | `SwanLabTracker` | ✗ | ✗ | Local or cloud, supports images |

Sources: [src/accelerate/tracking.py:46-73](), [src/accelerate/tracking.py:179-1247]()

---

## Logging and Multi-Process Coordination

The tracking system ensures that logging operations only occur on the main process (process 0) by default to avoid duplicate logs and race conditions. This is managed via the `on_main_process` decorator and the `main_process_only` attribute.

For a deep dive into synchronization and deferred initialization, see [Logging and Multi-Process Coordination](#11.2).

### Coordination Mechanism

```mermaid
sequenceDiagram
    participant U as User Code
    participant A as Accelerator
    participant T as GeneralTracker
    participant PS as PartialState
    
    U->>A: log(metrics, step)
    A->>T: log(metrics, step)
    Note over T: Decorated with @on_main_process
    T->>PS: check main process?
    alt is main process
        PS-->>T: continue
        T->>T: write to backend
    else is not main process
        PS-->>T: skip
    end
```

Sources: [src/accelerate/tracking.py:78-94](), [src/accelerate/tracking.py:119]()

---

## Custom Trackers

Users can create custom tracker integrations by subclassing `GeneralTracker` and registering them with the system. This allows for integrating proprietary or niche logging systems into the standard `Accelerator.log()` workflow.

For a guide on implementation and registration, see [Custom Trackers](#11.3).

### Registration Flow

```mermaid
graph LR
    Custom["MyCustomTracker<br/>(Subclass of GeneralTracker)"]
    Reg["register_tracker_class()"]
    Dict["LOGGER_TYPE_TO_CLASS"]
    
    Custom --> Reg
    Reg --> Dict
```

Sources: [src/accelerate/tracking.py:102-117](), [src/accelerate/tracking.py:1262-1265]()

---

