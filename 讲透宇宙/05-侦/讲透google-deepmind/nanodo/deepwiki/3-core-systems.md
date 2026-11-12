<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/nanodo · page 3 Core Systems · fetched 2026-10-26 -->

# Core Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nanodo/data.py](nanodo/data.py)
- [nanodo/model.py](nanodo/model.py)
- [nanodo/train.py](nanodo/train.py)

</details>



This document provides an overview of the main architectural components that comprise the nanodo framework. It covers the six primary systems that orchestrate model training: the training orchestrator, model architecture, data pipeline, evaluation system, metrics collection, and optimization components. Each system is implemented as a focused module with clear interfaces and responsibilities.

For detailed implementation guides on each system, see the individual subsections: [Training System](#3.1), [Model Architecture](#3.2), [Data Pipeline](#3.3), [Evaluation System](#3.4), [Metrics and Monitoring](#3.5), and [Optimization](#3.6).

## System Architecture Overview

The nanodo framework follows a modular design where each core system has distinct responsibilities. The training system acts as the central orchestrator, coordinating all other components through well-defined interfaces.

```mermaid
graph TB
    CLI["main.py<br/>train_and_evaluate()"] --> TrainSystem["train.py<br/>Trainer class"]
    
    TrainSystem --> ModelFactory["model_factory.py<br/>get_model_and_loss()"]
    TrainSystem --> DataPipeline["data.py<br/>py_batched_tfds()"]
    TrainSystem --> OptimizerFactory["optimizer.py<br/>get_optimizer()"]
    TrainSystem --> EvalSystem["evaluate.py<br/>Evaluator class"]
    TrainSystem --> MetricsSystem["metrics.py<br/>aggregate_microbatch_metrics()"]
    
    ModelFactory --> ModelArch["model.py<br/>TransformerDo"]
    ModelFactory --> LossLib["loss.py<br/>LossFnFactory"]
    
    DataPipeline --> Tokenizer["SentencePiece<br/>_SPTokenizer"]
    DataPipeline --> Preprocessing["Preprocess.NOAM_PACKED<br/>Preprocess.PADDED"]
    
    OptimizerFactory --> Schedule["Learning Rate Schedule"]
    OptimizerFactory --> BaseOpt["AdamW/Adafactor/Lion"]
    
    ModelArch --> TBlock["TBlock"]
    ModelArch --> CausalAttn["CausalAttn"]
    ModelArch --> MLP["Mlp"]
    
    EvalSystem --> ModelArch
    MetricsSystem --> TrainSystem
```

**Sources:** [nanodo/train.py:54-234](), [nanodo/model_factory.py](), [nanodo/data.py:39-89](), [nanodo/evaluate.py](), [nanodo/metrics.py](), [nanodo/optimizer.py]()

## Training System Core

The training system is built around the `Trainer` class and the `train_and_evaluate` function, which coordinates all training activities including gradient computation, parameter updates, and distributed execution.

```mermaid
graph TD
    TrainEntry["train_and_evaluate(c: ConfigDict)"] --> MeshSetup["Mesh setup<br/>device_count() devices"]
    TrainEntry --> StateInit["_init_train_state()<br/>TrainState creation"]
    
    StateInit --> TrainerClass["Trainer class<br/>step_fn jit compilation"]
    MeshSetup --> TrainerClass
    
    TrainerClass --> TrainLoop["Training Loop<br/>range(step, num_train_steps)"]
    
    TrainLoop --> StepExec["trainer.do_step()<br/>_train_step() dispatch"]
    TrainLoop --> EvalTrigger["Evaluation trigger<br/>evaluator.eval()"]
    TrainLoop --> CheckpointTrigger["Checkpoint trigger<br/>ckpt_mngr.save()"]
    TrainLoop --> MetricsProcess["_process_metrics()<br/>aggregate_microbatch_metrics()"]
    
    StepExec --> GradCompute["jax.value_and_grad()<br/>loss and gradients"]
    StepExec --> ParamUpdate["optax.apply_updates()<br/>new parameters"]
    StepExec --> StateUpdate["state.replace()<br/>new TrainState"]
```

**Sources:** [nanodo/train.py:54-234](), [nanodo/train.py:236-294](), [nanodo/train.py:296-324]()

## Model Architecture System

The model architecture centers on the `TransformerDo` class, which implements a decoder-only transformer using the configuration specified in `DoConfig`. The architecture follows a pre-LayerNorm design with standard transformer components.

```mermaid
graph TB
    Config["DoConfig<br/>(D, H, L, N, V, F)"] --> ModelClass["TransformerDo<br/>decoder-only model"]
    
    ModelClass --> TokenEmbed["embed: nn.Embed<br/>V → D dimensions"]
    ModelClass --> PosEmbed["pos_embed: nn.Embed<br/>L → D dimensions"]
    ModelClass --> Blocks["blocks: List[TBlock]<br/>N transformer layers"]
    ModelClass --> OutNorm["out_ln: nn.LayerNorm<br/>final normalization"]
    
    Blocks --> TBlockComp["TBlock<br/>pre-LayerNorm architecture"]
    
    TBlockComp --> AttnNorm["LayerNorm<br/>attention normalization"]
    TBlockComp --> CausalAttnComp["CausalAttn<br/>self-attention mechanism"]
    TBlockComp --> MlpNorm["LayerNorm<br/>MLP normalization"] 
    TBlockComp --> MlpComp["Mlp<br/>feed-forward network"]
    
    CausalAttnComp --> QKVProj["DenseGeneral<br/>Q, K, V projections"]
    CausalAttnComp --> AttnMask["Causal mask<br/>tril(ones(L, L))"]
    CausalAttnComp --> OutProj["DenseGeneral<br/>output projection"]
    
    MlpComp --> UpProj["Dense(F)<br/>up projection"]
    MlpComp --> GELU["jax.nn.gelu<br/>activation"]
    MlpComp --> DownProj["Dense(D)<br/>down projection"]
```

**Sources:** [nanodo/model.py:29-46](), [nanodo/model.py:48-78](), [nanodo/model.py:97-114](), [nanodo/model.py:116-165](), [nanodo/model.py:80-94]()

## Data Pipeline System

The data pipeline is built around the `py_batched_tfds` function, which creates `grain.DataLoader` instances with configurable preprocessing strategies. The system supports both NOAM packing for training efficiency and padding for evaluation consistency.

```mermaid
graph TD
    DataEntry["py_batched_tfds()<br/>tfds_name, split, context_size"] --> DataSource["tfds.data_source<br/>TFDS dataset loading"]
    
    DataEntry --> IndexSampler["grain.IndexSampler<br/>shuffling and epochs"]
    DataEntry --> Tokenizer["_SPTokenizer<br/>SentencePiece wrapper"]
    
    DataSource --> TokenizeOp["grain.MapOperation<br/>_py_tokenize()"]
    Tokenizer --> TokenizeOp
    
    TokenizeOp --> PreprocessBranch{"preprocessing type"}
    
    PreprocessBranch -->|"NOAM_PACKED"| NoamPack["_NoamPack<br/>context_size packing"]
    PreprocessBranch -->|"PADDED"| PadOp["np.array<br/>fixed-length padding"]
    
    NoamPack --> BatchOp["grain.Batch<br/>batch_size, drop_remainder"]
    PadOp --> BatchOp
    
    BatchOp --> DataLoader["grain.DataLoader<br/>worker_count workers"]
    
    IndexSampler --> DataLoader
    
    DataLoader --> BatchOutput["Iterator[jax.Array]<br/>BxL token arrays"]
```

**Sources:** [nanodo/data.py:39-89](), [nanodo/data.py:102-113](), [nanodo/data.py:115-136](), [nanodo/data.py:138-166]()

## System Integration Flow

The integration between systems follows a clear data flow pattern, with the training system coordinating all components through standardized interfaces and shared state management.

```mermaid
graph LR
    ConfigDict["ml_collections.ConfigDict<br/>configuration"] --> TrainFunc["train_and_evaluate()"]
    
    TrainFunc --> DataSetup["Data Pipeline Setup<br/>train_ds, eval_ds"]
    TrainFunc --> ModelSetup["Model Setup<br/>model, get_loss_fn"]
    TrainFunc --> StateSetup["State Setup<br/>TrainState, shardings"]
    
    DataSetup --> TrainIter["train_iter<br/>Iterator[jax.Array]"]
    ModelSetup --> TrainerInit["Trainer.__init__()"]
    StateSetup --> TrainerInit
    
    TrainerInit --> StepFn["step_fn<br/>jax.jit(_train_step)"]
    
    TrainIter --> DoStep["trainer.do_step()<br/>microbatch processing"]
    StepFn --> DoStep
    
    DoStep --> LossGrad["Loss and Gradients<br/>get_loss_fn + jax.grad"]
    DoStep --> OptUpdate["Optimizer Update<br/>tx.update()"]
    DoStep --> MetricsOut["Metrics Output<br/>get_metrics()"]
    
    MetricsOut --> Aggregation["metrics_lib.aggregate_microbatch_metrics()"]
    Aggregation --> Writer["metric_writers<br/>TensorBoard logging"]
```

**Sources:** [nanodo/train.py:54-85](), [nanodo/train.py:112-118](), [nanodo/train.py:236-294](), [nanodo/train.py:296-324](), [nanodo/metrics.py]()

## Configuration and State Management

The framework uses `ml_collections.ConfigDict` for centralized configuration management and `flax.training.TrainState` for maintaining training state across distributed devices. The configuration system enables reproducible experiments through structured hyperparameter management.

| Component | Configuration Source | State Management |
|-----------|---------------------|------------------|
| Model Architecture | `c.model` (DoConfig fields) | `state.params` |
| Optimization | `c.opt` | `state.opt_state` |
| Data Pipeline | `c.ds_name`, `c.vocab_path` | `train_iter` checkpointing |
| Training Loop | `c.opt.num_train_steps` | `state.step` |
| Evaluation | `c.eval_every_steps` | Stateless evaluation |
| Checkpointing | `c.checkpoint_every_steps` | `orbax.CheckpointManager` |

**Sources:** [nanodo/train.py:74-85](), [nanodo/train.py:327-347](), [nanodo/train.py:350-376]()

---

