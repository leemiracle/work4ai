<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/ignite · page 4 Handlers and Callbacks · fetched 2026-10-21 -->

# Handlers and Callbacks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/handlers.rst](docs/source/handlers.rst)
- [ignite/handlers/__init__.py](ignite/handlers/__init__.py)
- [ignite/handlers/checkpoint.py](ignite/handlers/checkpoint.py)
- [tests/ignite/handlers/test_checkpoint.py](tests/ignite/handlers/test_checkpoint.py)

</details>



This page documents event handlers in PyTorch Ignite, which extend training functionality by responding to events fired by the `Engine`. Handlers are callable objects or functions that attach to an `Engine` to execute at specific points during training or evaluation. 

This is a parent page providing a high-level overview. For deep technical details, configuration options, and advanced examples, please refer to the child pages:
- [Checkpoint and Model Saving](#4.1)
- [Training Control Handlers](#4.2)
- [Logging and Experiment Tracking](#4.3)
- [Parameter Schedulers and LR Finder](#4.4)

---

## 1. Overview of Handlers

Handlers in PyTorch Ignite are event-driven components that orchestrate training by responding to lifecycle events fired by the `Engine` [ignite/engine/engine.py](). They encapsulate common training routines into modular, reusable building blocks.

**Handler Event-Driven Architecture**
```mermaid
graph TB
    Engine[""Engine""] -->|"fires"| Events[""Events.ITERATION_STARTED<br/>Events.EPOCH_COMPLETED<br/>Events.COMPLETED""]
    Events -->|"triggers"| Handlers[""Handler Functions / Objects""]
    Handlers -->|"modify"| EngineState[""engine.state<br/>(metrics, iteration, epoch)""]
    Handlers -->|"save"| Disk[""Checkpoints & Artifacts""]
    Handlers -->|"control"| TrainingFlow[""Training Flow Control<br/>(EarlyStopping, TerminateOnNan)""]
    Handlers -->|"update"| Optimizer[""optimizer.param_groups<br/>(Learning Rate, Momentum)""]
```

Handlers can be registered using `engine.add_event_handler()` or via decorators like `@engine.on(Events.EPOCH_COMPLETED)` [ignite/engine/engine.py](). They execute sequentially in the order they are attached.

Sources: [ignite/handlers/__init__.py:1-88](), [ignite/engine/engine.py]()

---

## 2. Checkpoint and Model Saving

Checkpoint handlers manage saving and loading model parameters, optimizer states, learning rate schedulers, and the engine state itself. They ensure fault tolerance, persistence, and automated best-model retention based on validation performance metrics.

For full details on `Checkpoint`, `DiskSaver`, `ModelCheckpoint`, score functions, retention policies (`n_saved`), custom filename patterns, and distributed saving configurations, see [Checkpoint and Model Saving](#4.1).

Sources: [ignite/handlers/checkpoint.py:85-139](), [tests/ignite/handlers/test_checkpoint.py:47-90]()

---

## 3. Training Control Handlers

Training control handlers monitor the training loop and dynamically alter execution flow. This includes stopping training when validation metrics plateau (`EarlyStopping`), aborting runs upon encountering numerical instabilities (`TerminateOnNan`), or bounding training duration (`TimeLimit`).

For comprehensive documentation on `EarlyStopping`, `TerminateOnNan`, `TimeLimit`, `Timer`, EMA handlers, and output stores, see [Training Control Handlers](#4.2).

Sources: [ignite/handlers/early_stopping.py:11-106](), [ignite/handlers/terminate_on_nan.py:13-53](), [ignite/handlers/__init__.py:35-40]()

---

## 4. Logging and Experiment Tracking

Logging handlers synchronize training metrics, parameters, and system stats with external experiment tracking platforms and local consoles. Ignite provides native loggers for TensorBoard, MLflow, Neptune, Weights & Biases, ClearML, Visdom, Polyaxon, and interactive console progress bars (`ProgressBar` using `tqdm`).

For full documentation of all logger integrations, setup helpers, and custom research loggers (`FBResearchLogger`), see [Logging and Experiment Tracking](#4.3).

Sources: [docs/source/handlers.rst:49-70](), [ignite/handlers/__init__.py:4-46]()

---

## 5. Parameter Schedulers and LR Finder

Parameter schedulers dynamically modify optimizer hyperparameters (such as learning rate, momentum, or weight decay) across training iterations or epochs. Ignite includes a rich family of schedulers (cyclical, cosine annealing, piecewise linear, and concatenated schedulers) alongside state parameter schedulers and the `FastaiLRFinder` utility.

For detailed explanations of the scheduler hierarchy, simulation utilities, and learning rate finders, see [Parameter Schedulers and LR Finder](#4.4).

Sources: [docs/source/handlers.rst:110-147](), [ignite/handlers/__init__.py:11-34]()

---

