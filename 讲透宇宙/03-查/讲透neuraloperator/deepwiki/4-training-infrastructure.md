<!-- source: DeepWiki mcp.deepwiki.com · repo neuraloperator/neuraloperator · page 4 Training Infrastructure · fetched 2026-10-21 -->

# Training Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [neuralop/training/__init__.py](neuralop/training/__init__.py)
- [neuralop/training/trainer.py](neuralop/training/trainer.py)
- [scripts/login_wandb.py](scripts/login_wandb.py)
- [scripts/test_from_config.py](scripts/test_from_config.py)
- [scripts/train_burgers.py](scripts/train_burgers.py)
- [scripts/train_burgers_pino.py](scripts/train_burgers_pino.py)
- [scripts/train_darcy.py](scripts/train_darcy.py)
- [scripts/train_fnogno_carcfd.py](scripts/train_fnogno_carcfd.py)
- [scripts/train_gino_carcfd.py](scripts/train_gino_carcfd.py)
- [scripts/train_mhd64.py](scripts/train_mhd64.py)
- [scripts/train_navier_stokes.py](scripts/train_navier_stokes.py)
- [scripts/train_poisson.py](scripts/train_poisson.py)
- [scripts/train_uqno_darcy.py](scripts/train_uqno_darcy.py)

</details>



The training infrastructure provides the core orchestration system for training neural operator models. This page documents the high-level training pipeline, including the `Trainer` class, data flow, optimization loops, evaluation modes, and checkpointing mechanisms. The training system is designed to handle both single-GPU and distributed multi-GPU training, with support for mixed precision, autoregressive evaluation, and experiment tracking via Weights & Biases.

For detailed documentation on specific components:
- Trainer class API and methods: see [Trainer Class](#4.1)
- Dataset classes and data processors: see [Data Processing and Datasets](#4.2)
- Loss functions and differentiation utilities: see [Loss Functions and Differentiation](#4.3)
- Model factory and checkpoint management: see [Model Management and Checkpointing](#4.4)

## Training Pipeline Architecture

The training infrastructure centers around the `Trainer` class, which orchestrates model training, evaluation, and checkpointing. The following diagram shows how components interact during a typical training run.

**Training Pipeline Component Interaction**

```mermaid
graph TB
    subgraph "Initialization Phase"
        Config["Configuration<br/>(dict from zencfg)"]
        Setup["setup()<br/>neuralop.training.torch_setup"]
        Device["device, is_logger"]
        
        Config --> Setup
        Setup --> Device
    end
    
    subgraph "Data Pipeline"
        LoadData["load_*_dataset()<br/>(e.g., load_darcy_flow_small)"]
        TrainLoader["train_loader<br/>(torch.utils.data.DataLoader)"]
        TestLoaders["test_loaders<br/>(dict[str, DataLoader])"]
        DataProc["data_processor<br/>(DataProcessor subclass)"]
        MGPatch["MGPatchingDataProcessor<br/>(optional)"]
        
        LoadData --> TrainLoader
        LoadData --> TestLoaders
        LoadData --> DataProc
        DataProc -.upgrade.-> MGPatch
    end
    
    subgraph "Model & Optimization"
        GetModel["get_model(config)<br/>neuralop.models.model_dispatcher"]
        Model["model<br/>(nn.Module)"]
        Optimizer["optimizer<br/>(AdamW/Adam)"]
        Scheduler["scheduler<br/>(ReduceLROnPlateau/CosineAnnealing/StepLR)"]
        DDP["DistributedDataParallel<br/>(optional)"]
        
        GetModel --> Model
        Model -.wrap.-> DDP
    end
    
    subgraph "Loss Configuration"
        TrainLoss["training_loss<br/>(LpLoss/H1Loss/WeightedSumLoss)"]
        EvalLosses["eval_losses<br/>(dict[str, Loss])"]
    end
    
    subgraph "Trainer Execution"
        TrainerInit["Trainer.__init__()<br/>neuralop/training/trainer.py:54"]
        TrainerTrain["Trainer.train()<br/>neuralop/training/trainer.py:96"]
        TrainEpoch["train_one_epoch()<br/>neuralop/training/trainer.py:256"]
        EvalAll["evaluate_all()<br/>neuralop/training/trainer.py:327"]
        Checkpoint["checkpoint()<br/>neuralop/training/trainer.py:765"]
        
        TrainerInit --> TrainerTrain
        TrainerTrain --> TrainEpoch
        TrainerTrain --> EvalAll
        TrainerTrain --> Checkpoint
    end
    
    subgraph "Monitoring"
        WandbLog["wandb.log()"]
        ConsoleLog["print() to stdout"]
        
        TrainEpoch --> ConsoleLog
        EvalAll --> ConsoleLog
        TrainEpoch -.optional.-> WandbLog
        EvalAll -.optional.-> WandbLog
    end
    
    Device --> TrainerInit
    Model --> TrainerInit
    DataProc --> TrainerInit
    
    TrainLoader --> TrainerTrain
    TestLoaders --> TrainerTrain
    Optimizer --> TrainerTrain
    Scheduler --> TrainerTrain
    TrainLoss --> TrainerTrain
    EvalLosses --> TrainerTrain
    
    style TrainerTrain fill:#e8e8e8
    style TrainEpoch fill:#e8e8e8
    style EvalAll fill:#e8e8e8
```

**Sources:** [neuralop/training/trainer.py:25-791](), [scripts/train_darcy.py:1-214](), [scripts/train_navier_stokes.py:1-229]()

## Core Training Components

The training infrastructure consists of several key components that work together to train neural operator models.

**Component Responsibility Table**

| Component | Class/Module | Primary Responsibility | Key Methods |
|-----------|--------------|----------------------|-------------|
| **Trainer** | `neuralop.training.Trainer` | Orchestrates training loop, evaluation, and checkpointing | `train()`, `train_one_epoch()`, `evaluate()` |
| **Data Processor** | `neuralop.data.transforms.data_processors.DataProcessor` | Normalizes inputs/outputs, handles preprocessing/postprocessing | `preprocess()`, `postprocess()` |
| **Data Loader** | `torch.utils.data.DataLoader` | Batches data, handles shuffling and distributed sampling | Standard PyTorch API |
| **Optimizer** | `neuralop.training.AdamW` or `torch.optim.Adam` | Updates model parameters based on gradients | `step()`, `zero_grad()` |
| **Scheduler** | `torch.optim.lr_scheduler.*` | Adjusts learning rate during training | `step()` |
| **Loss Functions** | Various in `neuralop.losses` | Compute training and evaluation metrics | `__call__(out, y, **kwargs)` |
| **Checkpointing** | `neuralop.training.training_state` | Saves/loads model, optimizer, and scheduler state | `save_training_state()`, `load_training_state()` |

**Sources:** [neuralop/training/trainer.py:25-53](), [neuralop/training/__init__.py:1-5]()

## Trainer Class Overview

The `Trainer` class is the central orchestration component. It is initialized with model and training configuration, then its `train()` method executes the full training loop.

**Trainer Initialization Parameters**

```mermaid
graph LR
    subgraph "Required Parameters"
        Model["model: nn.Module"]
        NEpochs["n_epochs: int"]
    end
    
    subgraph "Device & Precision"
        Device["device: str = 'cpu'"]
        MixedPrec["mixed_precision: bool = False"]
        UseDist["use_distributed: bool = False"]
    end
    
    subgraph "Data Processing"
        DataProc["data_processor: nn.Module = None"]
    end
    
    subgraph "Evaluation & Logging"
        EvalInterval["eval_interval: int = 1"]
        WandbLog["wandb_log: bool = False"]
        LogOutput["log_output: bool = False"]
        Verbose["verbose: bool = False"]
    end
    
    TrainerInit["Trainer.__init__()"]
    
    Model --> TrainerInit
    NEpochs --> TrainerInit
    Device --> TrainerInit
    MixedPrec --> TrainerInit
    UseDist --> TrainerInit
    DataProc --> TrainerInit
    EvalInterval --> TrainerInit
    WandbLog --> TrainerInit
    LogOutput --> TrainerInit
    Verbose --> TrainerInit
```

**Sources:** [neuralop/training/trainer.py:54-95]()

**Trainer.train() Method Parameters**

```mermaid
graph TB
    subgraph "Data Loaders"
        TL["train_loader<br/>DataLoader"]
        TLS["test_loaders<br/>dict[str, DataLoader]"]
    end
    
    subgraph "Optimization"
        Opt["optimizer<br/>torch.optim.Optimizer"]
        Sched["scheduler<br/>lr_scheduler"]
        Reg["regularizer<br/>optional"]
    end
    
    subgraph "Loss Functions"
        TrLoss["training_loss<br/>Loss function"]
        EvLosses["eval_losses<br/>dict[str, Loss]"]
        EvModes["eval_modes<br/>dict[str, str]"]
    end
    
    subgraph "Checkpointing"
        SaveEvery["save_every: int<br/>optional"]
        SaveBest["save_best: str<br/>optional"]
        SaveDir["save_dir: str | Path<br/>default './ckpt'"]
        ResumeDir["resume_from_dir: str | Path<br/>optional"]
    end
    
    subgraph "Autoregressive"
        MaxSteps["max_autoregressive_steps: int<br/>optional"]
    end
    
    TrainMethod["Trainer.train()"]
    
    TL --> TrainMethod
    TLS --> TrainMethod
    Opt --> TrainMethod
    Sched --> TrainMethod
    Reg --> TrainMethod
    TrLoss --> TrainMethod
    EvLosses --> TrainMethod
    EvModes --> TrainMethod
    SaveEvery --> TrainMethod
    SaveBest --> TrainMethod
    SaveDir --> TrainMethod
    ResumeDir --> TrainMethod
    MaxSteps --> TrainMethod
```

**Sources:** [neuralop/training/trainer.py:96-254]()

## Training Loop Execution

The training loop follows a hierarchical structure: outer epoch loop, training phase, and evaluation phase.

**Training Loop Flow**

```mermaid
flowchart TD
    Start["Trainer.train() called"]
    
    LoadDevice["Move model and data_processor to device<br/>neuralop/training/trainer.py:198-205"]
    WrapDDP["Wrap model in DDP if distributed<br/>neuralop/training/trainer.py:200-202"]
    ResumeCheck{"resume_from_dir<br/>provided?"}
    Resume["resume_state_from_dir()<br/>neuralop/training/trainer.py:729"]
    
    EpochLoop{"For epoch in range<br/>(start_epoch, n_epochs)"}
    
    TrainPhase["train_one_epoch(epoch, train_loader, training_loss)<br/>neuralop/training/trainer.py:256"]
    
    EvalCheck{"epoch %<br/>eval_interval == 0?"}
    EvalPhase["evaluate_all(epoch, eval_losses, test_loaders, eval_modes)<br/>neuralop/training/trainer.py:327"]
    
    SaveBestCheck{"save_best is not None<br/>and metric improved?"}
    SaveBestCkpt["checkpoint(save_dir)<br/>save_name='best_model'<br/>neuralop/training/trainer.py:765"]
    
    SaveEveryCheck{"save_every is not None<br/>and epoch % save_every == 0?"}
    SaveEveryCkpt["checkpoint(save_dir)<br/>save_name='model'<br/>neuralop/training/trainer.py:765"]
    
    EpochEnd["Update epoch_metrics"]
    
    End["Return final epoch_metrics"]
    
    Start --> LoadDevice
    LoadDevice --> WrapDDP
    WrapDDP --> ResumeCheck
    ResumeCheck -->|Yes| Resume
    ResumeCheck -->|No| EpochLoop
    Resume --> EpochLoop
    
    EpochLoop -->|epoch| TrainPhase
    TrainPhase --> EvalCheck
    
    EvalCheck -->|Yes| EvalPhase
    EvalCheck -->|No| SaveEveryCheck
    
    EvalPhase --> SaveBestCheck
    SaveBestCheck -->|Yes| SaveBestCkpt
    SaveBestCheck -->|No| SaveEveryCheck
    
    SaveEveryCheck -->|Yes| SaveEveryCkpt
    SaveEveryCheck -->|No| EpochEnd
    SaveBestCkpt --> EpochEnd
    SaveEveryCkpt --> EpochEnd
    
    EpochEnd --> EpochLoop
    EpochLoop -->|done| End
```

**Sources:** [neuralop/training/trainer.py:96-254]()

## Training One Epoch

Each epoch consists of iterating through all batches in the training loader, computing losses, and updating model parameters.

**train_one_epoch() Workflow**

```mermaid
flowchart TD
    Start["train_one_epoch(epoch, train_loader, training_loss)"]
    
    Init["Initialize:<br/>- avg_loss = 0<br/>- avg_lasso_loss = 0<br/>- train_err = 0<br/>- n_samples = 0<br/>neuralop/training/trainer.py:275-284"]
    
    SetTrain["Set model and data_processor to train mode<br/>neuralop/training/trainer.py:277-279"]
    
    BatchLoop{"For idx, sample<br/>in enumerate(train_loader)"}
    
    TrainBatch["loss = train_one_batch(idx, sample, training_loss)<br/>neuralop/training/trainer.py:288"]
    
    Backward["loss.backward()<br/>neuralop/training/trainer.py:289"]
    
    OptStep["optimizer.step()<br/>neuralop/training/trainer.py:290"]
    
    Accumulate["Accumulate:<br/>- train_err += loss.item()<br/>- avg_loss += loss.item()<br/>- avg_lasso_loss += regularizer.loss (if exists)<br/>neuralop/training/trainer.py:292-296"]
    
    SchedCheck{"scheduler type?"}
    SchedPlateau["scheduler.step(train_err)<br/>ReduceLROnPlateau<br/>neuralop/training/trainer.py:299"]
    SchedOther["scheduler.step()<br/>Other schedulers<br/>neuralop/training/trainer.py:301"]
    
    ComputeAvg["Compute averages:<br/>- train_err /= len(train_loader)<br/>- avg_loss /= n_samples<br/>- avg_lasso_loss /= n_samples<br/>neuralop/training/trainer.py:305-310"]
    
    LogCheck{"verbose and<br/>epoch % eval_interval == 0?"}
    Log["log_training(epoch, time, avg_loss, train_err, ...)<br/>neuralop/training/trainer.py:316"]
    
    Return["Return train_err, avg_loss,<br/>avg_lasso_loss, epoch_train_time"]
    
    Start --> Init
    Init --> SetTrain
    SetTrain --> BatchLoop
    
    BatchLoop -->|sample| TrainBatch
    TrainBatch --> Backward
    Backward --> OptStep
    OptStep --> Accumulate
    Accumulate --> BatchLoop
    
    BatchLoop -->|done| SchedCheck
    SchedCheck -->|ReduceLROnPlateau| SchedPlateau
    SchedCheck -->|Other| SchedOther
    SchedPlateau --> ComputeAvg
    SchedOther --> ComputeAvg
    
    ComputeAvg --> LogCheck
    LogCheck -->|Yes| Log
    LogCheck -->|No| Return
    Log --> Return
```

**Sources:** [neuralop/training/trainer.py:256-325]()

## Training One Batch

Each batch goes through preprocessing, model forward pass, postprocessing, and loss computation.

**train_one_batch() Details**

```mermaid
flowchart TD
    Start["train_one_batch(idx, sample, training_loss)"]
    
    ZeroGrad["optimizer.zero_grad(set_to_none=True)<br/>neuralop/training/trainer.py:471"]
    
    ResetReg{"regularizer<br/>exists?"}
    ResetRegCall["regularizer.reset()<br/>neuralop/training/trainer.py:473"]
    
    PreCheck{"data_processor<br/>is not None?"}
    PreProc["sample = data_processor.preprocess(sample)<br/>neuralop/training/trainer.py:475"]
    ToDevice["Move sample tensors to device<br/>neuralop/training/trainer.py:478-482"]
    
    CountSamples["n_samples += sample['y'].shape[0]<br/>neuralop/training/trainer.py:484-487"]
    
    MixedCheck{"mixed_precision<br/>enabled?"}
    ForwardAuto["with torch.autocast(device_type):<br/>    out = model(**sample)<br/>neuralop/training/trainer.py:490-491"]
    ForwardNorm["out = model(**sample)<br/>neuralop/training/trainer.py:493"]
    
    PostCheck{"data_processor<br/>is not None?"}
    PostProc["out, sample = data_processor.postprocess(out, sample)<br/>neuralop/training/trainer.py:499"]
    
    LossMixedCheck{"mixed_precision<br/>enabled?"}
    LossAuto["with torch.autocast(device_type):<br/>    loss = training_loss(out, **sample)<br/>neuralop/training/trainer.py:504-505"]
    LossNorm["loss = training_loss(out, **sample)<br/>neuralop/training/trainer.py:507"]
    
    AddReg{"regularizer<br/>exists?"}
    AddRegLoss["loss += regularizer.loss<br/>neuralop/training/trainer.py:510"]
    
    Return["return loss"]
    
    Start --> ZeroGrad
    ZeroGrad --> ResetReg
    ResetReg -->|Yes| ResetRegCall
    ResetReg -->|No| PreCheck
    ResetRegCall --> PreCheck
    
    PreCheck -->|Yes| PreProc
    PreCheck -->|No| ToDevice
    PreProc --> CountSamples
    ToDevice --> CountSamples
    
    CountSamples --> MixedCheck
    MixedCheck -->|Yes| ForwardAuto
    MixedCheck -->|No| ForwardNorm
    
    ForwardAuto --> PostCheck
    ForwardNorm --> PostCheck
    
    PostCheck -->|Yes| PostProc
    PostCheck -->|No| LossMixedCheck
    PostProc --> LossMixedCheck
    
    LossMixedCheck -->|Yes| LossAuto
    LossMixedCheck -->|No| LossNorm
    
    LossAuto --> AddReg
    LossNorm --> AddReg
    
    AddReg -->|Yes| AddRegLoss
    AddReg -->|No| Return
    AddRegLoss --> Return
```

**Sources:** [neuralop/training/trainer.py:454-512]()

## Evaluation Modes

The training infrastructure supports two evaluation modes: **single-step** and **autoregressive**. The mode determines how the model is evaluated on test data.

**Evaluation Mode Comparison**

| Mode | Description | Use Case | Implementation |
|------|-------------|----------|----------------|
| **single_step** | Evaluates one input-output pair at a time | Standard function approximation, stationary PDEs | `eval_one_batch()` [neuralop/training/trainer.py:514-563]() |
| **autoregressive** | Uses previous output as next input, rolls out for multiple steps | Time-dependent PDEs, trajectory prediction | `eval_one_batch_autoreg()` [neuralop/training/trainer.py:565-646]() |

**Evaluation Flow**

```mermaid
flowchart TD
    Start["evaluate_all(epoch, eval_losses, test_loaders, eval_modes)"]
    
    Init["all_metrics = {}<br/>neuralop/training/trainer.py:354"]
    
    LoaderLoop{"For loader_name, loader<br/>in test_loaders.items()"}
    
    GetMode["loader_eval_mode = eval_modes.get(loader_name, 'single_step')<br/>neuralop/training/trainer.py:356"]
    
    Evaluate["loader_metrics = evaluate(eval_losses, loader,<br/>    log_prefix=loader_name, mode=loader_eval_mode)<br/>neuralop/training/trainer.py:357"]
    
    UpdateMetrics["all_metrics.update(**loader_metrics)<br/>neuralop/training/trainer.py:361"]
    
    VerboseCheck{"verbose?"}
    LogEval["log_eval(epoch, all_metrics)<br/>neuralop/training/trainer.py:363"]
    
    Return["return all_metrics"]
    
    Start --> Init
    Init --> LoaderLoop
    
    LoaderLoop -->|loader_name, loader| GetMode
    GetMode --> Evaluate
    Evaluate --> UpdateMetrics
    UpdateMetrics --> LoaderLoop
    
    LoaderLoop -->|done| VerboseCheck
    VerboseCheck -->|Yes| LogEval
    VerboseCheck -->|No| Return
    LogEval --> Return
```

**Sources:** [neuralop/training/trainer.py:327-365]()

**evaluate() Method Structure**

```mermaid
flowchart TD
    Start["evaluate(loss_dict, data_loader, log_prefix, mode)"]
    
    SetEval["Set model and data_processor to eval mode<br/>neuralop/training/trainer.py:398-400"]
    
    InitErrors["errors = {f'{log_prefix}_{loss_name}': 0<br/>    for loss_name in loss_dict.keys()}<br/>neuralop/training/trainer.py:402"]
    
    NoGrad["with torch.no_grad():"]
    
    BatchLoop{"For idx, sample<br/>in enumerate(data_loader)"}
    
    ReturnCheck{"idx == len(data_loader) - 1?"}
    SetReturn["return_output = True<br/>neuralop/training/trainer.py:417"]
    
    ModeCheck{"mode?"}
    SingleStep["eval_step_losses, outs = eval_one_batch(<br/>    sample, loss_dict, return_output)<br/>neuralop/training/trainer.py:419"]
    AutoReg["eval_step_losses, outs = eval_one_batch_autoreg(<br/>    sample, loss_dict, return_output, max_steps)<br/>neuralop/training/trainer.py:421"]
    
    AccumLosses["for loss_name, val_loss in eval_step_losses.items():<br/>    errors[f'{log_prefix}_{loss_name}'] += val_loss<br/>neuralop/training/trainer.py:425-426"]
    
    AvgErrors["for key in errors.keys():<br/>    errors[key] /= n_samples<br/>neuralop/training/trainer.py:428-429"]
    
    LogOutputCheck{"log_output and<br/>wandb_log?"}
    LogImg["errors[f'{log_prefix}_outputs'] = wandb.Image(outs)<br/>neuralop/training/trainer.py:433"]
    
    Return["return errors"]
    
    Start --> SetEval
    SetEval --> InitErrors
    InitErrors --> NoGrad
    NoGrad --> BatchLoop
    
    BatchLoop -->|sample| ReturnCheck
    ReturnCheck -->|Yes| SetReturn
    ReturnCheck -->|No| ModeCheck
    SetReturn --> ModeCheck
    
    ModeCheck -->|single_step| SingleStep
    ModeCheck -->|autoregression| AutoReg
    
    SingleStep --> AccumLosses
    AutoReg --> AccumLosses
    AccumLosses --> BatchLoop
    
    BatchLoop -->|done| AvgErrors
    AvgErrors --> LogOutputCheck
    LogOutputCheck -->|Yes| LogImg
    LogOutputCheck -->|No| Return
    LogImg --> Return
```

**Sources:** [neuralop/training/trainer.py:367-435]()

## Checkpointing and State Management

The training infrastructure provides checkpointing to save and resume training state. Checkpoints include model parameters, optimizer state, scheduler state, optional regularizer state, and current epoch number.

**Checkpoint Structure**

```mermaid
graph TB
    subgraph "Training State Components"
        Model["model.state_dict()"]
        Optimizer["optimizer.state_dict()"]
        Scheduler["scheduler.state_dict()"]
        Regularizer["regularizer.state_dict()<br/>(optional)"]
        Epoch["epoch: int"]
    end
    
    subgraph "Checkpoint Methods"
        Save["save_training_state()<br/>neuralop/training/training_state.py"]
        Load["load_training_state()<br/>neuralop/training/training_state.py"]
    end
    
    subgraph "Saved Files"
        ModelFile["model_state_dict.pt<br/>or best_model_state_dict.pt"]
        OptFile["optimizer.pt"]
        SchedFile["scheduler.pt"]
        RegFile["regularizer.pt<br/>(if exists)"]
        EpochFile["epoch.txt"]
    end
    
    Model --> Save
    Optimizer --> Save
    Scheduler --> Save
    Regularizer --> Save
    Epoch --> Save
    
    Save --> ModelFile
    Save --> OptFile
    Save --> SchedFile
    Save --> RegFile
    Save --> EpochFile
    
    ModelFile --> Load
    OptFile --> Load
    SchedFile --> Load
    RegFile --> Load
    EpochFile --> Load
    
    Load --> Model
    Load --> Optimizer
    Load --> Scheduler
    Load --> Regularizer
    Load --> Epoch
```

**Sources:** [neuralop/training/trainer.py:765-791](), [neuralop/training/trainer.py:729-763](), [neuralop/training/training_state.py:1]()

**Checkpointing Options**

The `Trainer.train()` method supports two checkpointing strategies:

1. **Periodic Checkpointing** (`save_every`): Save checkpoint every N epochs
2. **Best Model Checkpointing** (`save_best`): Save when a specified metric improves

**Checkpointing Configuration Table**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `save_every` | `int` or `None` | Save checkpoint every N epochs | `save_every=10` saves every 10 epochs |
| `save_best` | `str` or `None` | Metric name to monitor for best model | `save_best="test_l2"` saves when test L2 improves |
| `save_dir` | `str` or `Path` | Directory to save checkpoints | `save_dir="./ckpt"` |
| `resume_from_dir` | `str` or `Path` | Directory to resume training from | `resume_from_dir="./ckpt"` |

**Sources:** [neuralop/training/trainer.py:106-110](), [neuralop/training/trainer.py:139-151](), [neuralop/training/trainer.py:192-195]()

## Distributed Training Support

The training infrastructure supports distributed data parallel (DDP) training across multiple GPUs.

**Distributed Training Setup**

```mermaid
flowchart TD
    Start["Training Script Initialization"]
    
    Setup["device, is_logger = setup(config)<br/>neuralop/training/torch_setup.py"]
    
    DistCheck{"config.distributed<br/>.use_distributed?"}
    
    InitDist["torch.distributed.init_process_group()<br/>Called by setup()"]
    
    GetRank["device_id = dist.get_rank()"]
    
    ModelDDP["model = DistributedDataParallel(<br/>    model, device_ids=[device_id],<br/>    output_device=device_id)<br/>neuralop/training/trainer.py:200-202"]
    
    SamplerSetup["Create DistributedSampler for<br/>train_loader and test_loaders<br/>e.g., scripts/train_darcy.py:106-119"]
    
    TrainerInit["trainer = Trainer(<br/>    model=model,<br/>    use_distributed=True,<br/>    ...)<br/>e.g., scripts/train_darcy.py:170"]
    
    Training["trainer.train(...)"]
    
    CheckpointCheck{"comm.get_local_rank() == 0?"}
    SaveCkpt["Save checkpoint<br/>neuralop/training/trainer.py:776"]
    
    End["Training Complete"]
    
    Start --> Setup
    Setup --> DistCheck
    
    DistCheck -->|Yes| InitDist
    DistCheck -->|No| TrainerInit
    
    InitDist --> GetRank
    GetRank --> ModelDDP
    ModelDDP --> SamplerSetup
    SamplerSetup --> TrainerInit
    
    TrainerInit --> Training
    Training --> CheckpointCheck
    
    CheckpointCheck -->|Yes| SaveCkpt
    CheckpointCheck -->|No| End
    SaveCkpt --> End
```

**Sources:** [neuralop/training/trainer.py:200-202](), [neuralop/training/torch_setup.py:1](), [scripts/train_darcy.py:36-37](), [scripts/train_darcy.py:106-119](), [neuralop/training/trainer.py:776-790]()

## Integration with Example Training Scripts

The training infrastructure is used consistently across all example training scripts. Here's how a typical training script integrates with the infrastructure:

**Standard Training Script Structure**

```mermaid
flowchart TD
    Start["Training Script Execution"]
    
    Config["Load configuration from zencfg<br/>e.g., scripts/train_darcy.py:26-34"]
    
    SetupDist["device, is_logger = setup(config)<br/>scripts/train_darcy.py:37"]
    
    WandbInit["Initialize Weights & Biases<br/>(if config.wandb.log)<br/>scripts/train_darcy.py:40-65"]
    
    LoadData["Load dataset using dataset loader<br/>e.g., load_darcy_flow_small()<br/>scripts/train_darcy.py:78-87"]
    
    GetModel["model = get_model(config)<br/>scripts/train_darcy.py:89"]
    
    DataProcCheck{"Patching enabled?<br/>(config.patching.levels > 0)"}
    UpgradeProc["data_processor = MGPatchingDataProcessor(...)<br/>scripts/train_darcy.py:92-102"]
    
    DistSamplerCheck{"Distributed training?"}
    SetupSampler["Setup DistributedSampler for loaders<br/>scripts/train_darcy.py:106-119"]
    
    CreateOpt["optimizer = AdamW(...)<br/>scripts/train_darcy.py:121-125"]
    
    CreateSched["scheduler = torch.optim.lr_scheduler.*<br/>scripts/train_darcy.py:127-143"]
    
    CreateLosses["training_loss = LpLoss(...) or H1Loss(...)<br/>eval_losses = {'h1': h1loss, 'l2': l2loss}<br/>scripts/train_darcy.py:146-158"]
    
    CreateTrainer["trainer = Trainer(<br/>    model=model, n_epochs=...,<br/>    device=device, data_processor=...,<br/>    ...)<br/>scripts/train_darcy.py:170-181"]
    
    LogParams["Log model parameter count to wandb<br/>(if config.wandb.log)<br/>scripts/train_darcy.py:184-198"]
    
    Train["trainer.train(<br/>    train_loader=train_loader,<br/>    test_loaders=test_loaders,<br/>    optimizer=optimizer,<br/>    scheduler=scheduler,<br/>    training_loss=train_loss,<br/>    eval_losses=eval_losses)<br/>scripts/train_darcy.py:201-209"]
    
    Finish["wandb.finish()<br/>(if config.wandb.log)<br/>scripts/train_darcy.py:212-213"]
    
    End["Script Complete"]
    
    Start --> Config
    Config --> SetupDist
    SetupDist --> WandbInit
    WandbInit --> LoadData
    LoadData --> GetModel
    GetModel --> DataProcCheck
    
    DataProcCheck -->|Yes| UpgradeProc
    DataProcCheck -->|No| DistSamplerCheck
    UpgradeProc --> DistSamplerCheck
    
    DistSamplerCheck -->|Yes| SetupSampler
    DistSamplerCheck -->|No| CreateOpt
    SetupSampler --> CreateOpt
    
    CreateOpt --> CreateSched
    CreateSched --> CreateLosses
    CreateLosses --> CreateTrainer
    CreateTrainer --> LogParams
    LogParams --> Train
    Train --> Finish
    Finish --> End
```

**Sources:** [scripts/train_darcy.py:1-214](), [scripts/train_navier_stokes.py:1-229](), [scripts/train_burgers.py:1-226]()

## Mixed Precision Training

The training infrastructure supports mixed precision training using `torch.autocast` to accelerate training and reduce memory usage on compatible hardware.

**Mixed Precision Configuration**

When `mixed_precision=True` is passed to the `Trainer`, forward passes and loss computations are wrapped in `torch.autocast` contexts:

```python
# Forward pass with mixed precision
if self.mixed_precision:
    with torch.autocast(device_type=self.autocast_device_type):
        out = self.model(**sample)
else:
    out = self.model(**sample)

# Loss computation with mixed precision
if self.mixed_precision:
    with torch.autocast(device_type=self.autocast_device_type):
        loss += training_loss(out, **sample)
else:
    loss += training_loss(out, **sample)
```

**Device Type Detection**

The `Trainer` automatically determines the appropriate device type for autocast:
- If device contains "cuda", uses `device_type="cuda"`
- Otherwise, uses `device_type="cpu"`

**Sources:** [neuralop/training/trainer.py:82-91](), [neuralop/training/trainer.py:489-507]()

## Weights & Biases Integration

The training infrastructure integrates with Weights & Biases for experiment tracking and visualization.

**Logged Metrics**

| Metric Type | Examples | Logged By |
|-------------|----------|-----------|
| **Training Metrics** | `train_err`, `avg_loss`, `avg_lasso_loss`, `lr` | `log_training()` [neuralop/training/trainer.py:648-695]() |
| **Evaluation Metrics** | `test_l2`, `test_h1`, `421_l2` (resolution-specific) | `log_eval()` [neuralop/training/trainer.py:697-727]() |
| **Model Info** | `n_params`, `compression_ratio`, `space_savings` | Training scripts [scripts/train_darcy.py:184-198]() |
| **Output Visualizations** | Model output images on last eval batch | `evaluate()` [neuralop/training/trainer.py:432-433]() |

**WandB Logging Flow**

```mermaid
flowchart TD
    Start["wandb_log=True in Trainer"]
    
    CheckActive{"wandb.run<br/>is not None?"}
    
    SetFlag["self.wandb_log = True<br/>neuralop/training/trainer.py:74-76"]
    
    TrainLog["During train_one_epoch():<br/>wandb.log(train_err, avg_loss, ...)<br/>neuralop/training/trainer.py:692-695"]
    
    EvalLog["During evaluate_all():<br/>wandb.log(test_l2, test_h1, ...)<br/>neuralop/training/trainer.py:724-727"]
    
    OutputLog["If log_output=True:<br/>wandb.log(wandb.Image(outs))<br/>neuralop/training/trainer.py:433"]
    
    Commit["commit parameter controls<br/>whether to group metrics:<br/>- False: group with next log<br/>- True: log immediately"]
    
    Start --> CheckActive
    CheckActive -->|Yes| SetFlag
    CheckActive -->|No| Start
    
    SetFlag --> TrainLog
    TrainLog --> EvalLog
    EvalLog --> OutputLog
    OutputLog --> Commit
```

**Sources:** [neuralop/training/trainer.py:73-76](), [neuralop/training/trainer.py:648-727](), [scripts/train_darcy.py:40-65]()

## Common Configuration Patterns

Training scripts typically follow consistent patterns for configuration and initialization. Here are common configuration values:

**Optimizer Configuration**

```python
optimizer = AdamW(
    model.parameters(),
    lr=config.opt.learning_rate,      # e.g., 1e-3
    weight_decay=config.opt.weight_decay,  # e.g., 1e-4
)
```

**Scheduler Configuration**

| Scheduler Type | Configuration | Use Case |
|----------------|---------------|----------|
| `ReduceLROnPlateau` | `factor=0.5, patience=5, mode="min"` | Reduce LR when validation metric plateaus |
| `CosineAnnealingLR` | `T_max=n_epochs` | Smooth LR decay over training |
| `StepLR` | `step_size=50, gamma=0.5` | Fixed LR decay every N epochs |

**Loss Configuration**

```python
# Data losses
l2loss = LpLoss(d=2, p=2)
h1loss = H1Loss(d=2)

# Training loss selection
if config.opt.training_loss == "l2":
    train_loss = l2loss
elif config.opt.training_loss == "h1":
    train_loss = h1loss

# Evaluation losses
eval_losses = {"h1": h1loss, "l2": l2loss}
```

**Sources:** [scripts/train_darcy.py:121-158](), [scripts/train_navier_stokes.py:130-167](), [scripts/train_burgers.py:98-157]()

---

