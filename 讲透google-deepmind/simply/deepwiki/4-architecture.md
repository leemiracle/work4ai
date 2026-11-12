<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/simply · page 4 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [simply/data_lib.py](simply/data_lib.py)
- [simply/main.py](simply/main.py)
- [simply/model_lib.py](simply/model_lib.py)

</details>



## Purpose and Scope

This document provides a comprehensive technical overview of Simply's internal architecture, focusing on how components interact during experiment execution, training, and inference. It covers the core systems implemented in `main.py`, `model_lib.py`, and `data_lib.py`, explaining their roles and relationships.

For configuration management and experiment setup, see [Configuration System](#3). For practical usage guides, see [User Guides](#5). For detailed API documentation of individual modules, see [API Reference](#6).

## System Architecture Overview

Simply's architecture follows a layered design where `main.py` serves as the orchestration layer, delegating to specialized subsystems for model creation, data preparation, and training/inference execution. The system is designed for distributed training on JAX with explicit sharding control.

### Core Component Interaction

```mermaid
graph TB
    CLI["main.main()<br/>CLI Entry Point"]
    ConfigLoad["ExperimentConfigRegistry<br/>ShardingConfigRegistry"]
    MeshSetup["sharding_lib.set_default_mesh_shape()<br/>JAX Device Mesh Creation"]
    Helper["ExperimentHelper<br/>Checkpoint & Logging Manager"]
    
    ModelCreate["create_model()<br/>model_lib.TransformerLM"]
    DataCreate["data_lib.create_dataset()<br/>SeqIO Pipeline"]
    OptInit["config.optimizer.init()<br/>Optimizer State"]
    StateInit["get_init_state()<br/>Load or Initialize Params"]
    
    TrainLoop["run_experiment()<br/>Training Loop Registry"]
    TrainStep["train_one_step()<br/>JAX JIT Compiled"]
    LossFn["compute_train_loss()<br/>Cross-Entropy Computation"]
    GradUpdate["optimizer.apply()<br/>Parameter Updates"]
    
    CLI --> ConfigLoad
    CLI --> MeshSetup
    CLI --> TrainLoop
    
    TrainLoop --> Helper
    TrainLoop --> ModelCreate
    TrainLoop --> DataCreate
    TrainLoop --> StateInit
    
    StateInit --> OptInit
    StateInit --> ModelCreate
    
    TrainLoop --> TrainStep
    TrainStep --> LossFn
    TrainStep --> GradUpdate
    
    LossFn --> ModelCreate
```

**Sources:** [simply/main.py:89-148](), [simply/model_lib.py:2094-2272]()

### Module Responsibilities

| Module | Primary Responsibility | Key Classes/Functions |
|--------|----------------------|---------------------|
| `main.py` | Experiment orchestration, CLI interface | `main()` |
| `model_lib.py` | Model architecture, training, inference | `TransformerLM`, `LMInterface`, `train_one_step()` |
| `data_lib.py` | Dataset creation, vocabulary management | `create_dataset()`, `DataSourceRegistry` |
| `config_lib.py` | Configuration definitions and loading | `ExperimentConfigRegistry`, `ShardingConfigRegistry` |
| `rl_lib.py` | Reinforcement learning training | PPO/GRPO implementations |

**Sources:** [simply/main.py:1-151](), [simply/model_lib.py:1-3548](), [simply/data_lib.py:1-890]()

## Execution Flow

### Experiment Launch Sequence

The execution begins with command-line invocation and proceeds through configuration loading, mesh setup, model initialization, and training loop execution.

```mermaid
sequenceDiagram
    participant User
    participant main.main
    participant ConfigRegistry
    participant MeshSetup
    participant ModelCreation
    participant StateInit
    participant TrainLoop
    participant CheckpointMgr
    
    User->>main.main: python -m simply.main<br/>--experiment_config=Gemma2BV2
    
    main.main->>ConfigRegistry: get_config('Gemma2BV2')
    ConfigRegistry-->>main.main: ExperimentConfig
    
    main.main->>ConfigRegistry: get_config('GSPMDSharding')
    ConfigRegistry-->>main.main: ShardingConfig
    
    main.main->>MeshSetup: set_default_mesh_shape(mesh_shape, dcn_mesh_shape)
    
    main.main->>TrainLoop: run_experiment(config, sharding_config, ...)
    
    TrainLoop->>ModelCreation: create_model(config, sharding_config)
    ModelCreation-->>TrainLoop: TransformerLM instance
    
    TrainLoop->>StateInit: get_init_state(config, sharding_config, ckpt_mngr, ckpt_dir)
    StateInit->>CheckpointMgr: load_checkpoint_from_dir() or model.init()
    CheckpointMgr-->>StateInit: params, opt_state
    StateInit-->>TrainLoop: state = {params, opt_state, steps}
    
    loop Training Steps
        TrainLoop->>TrainLoop: train_one_step_fn(state, batch, lr)
        TrainLoop->>CheckpointMgr: save_ckpt(state, steps)
    end
```

**Sources:** [simply/main.py:89-148](), [simply/model_lib.py:2094-2272](), [simply/model_lib.py:2302-2354]()

### Training Loop Structure

The `run_experiment()` function in `model_lib.py` implements the main training loop, coordinating data iteration, gradient computation, and checkpoint management.

```mermaid
graph TB
    Start["run_experiment()<br/>Entry Point"]
    Init["Setup: model, optimizer,<br/>state, datasets"]
    Compile["JIT Compile:<br/>train_one_step_fn, lr_fn"]
    
    LoopStart{"steps <= num_train_steps<br/>and not early_stop"}
    GetBatch["next(train_set_iter)<br/>Fetch Batch"]
    BuildGlobal["build_global_array_fn(batch)<br/>Distribute Data"]
    
    ComputeLR["lr_fn(state['steps'])<br/>Learning Rate Schedule"]
    TrainStep["train_one_step_fn(state, batch, lr)<br/>Returns: loss, new_state, log_dict"]
    
    LogMetrics["helper.add_metric()<br/>helper.write_scalars()"]
    SaveCkpt["helper.save_ckpt(state, steps)"]
    Validate["run_eval(state)<br/>Optional Validation"]
    
    CheckStop{"Early Stop<br/>Condition?"}
    End["Return final_result"]
    
    Start --> Init
    Init --> Compile
    Compile --> LoopStart
    
    LoopStart -->|Yes| GetBatch
    GetBatch --> BuildGlobal
    BuildGlobal --> ComputeLR
    ComputeLR --> TrainStep
    TrainStep --> LogMetrics
    LogMetrics --> SaveCkpt
    SaveCkpt --> Validate
    Validate --> CheckStop
    
    CheckStop -->|No| LoopStart
    CheckStop -->|Yes| End
    LoopStart -->|No| End
```

**Sources:** [simply/model_lib.py:2094-2272](), [simply/model_lib.py:2125-2270]()

## Model Architecture

### TransformerLM Structure

The `TransformerLM` class implements a decoder-only transformer with configurable layers, attention mechanisms, and feed-forward networks. The architecture is fully parameterized through configuration objects.

```mermaid
graph TB
    Input["Input Tokens<br/>[batch, seq_len]"]
    Embed["Embedding<br/>vocab_size → model_dim<br/>params['embed']"]
    
    InputEnc["Input Encoders<br/>(Optional)<br/>params['input_encoders']"]
    
    BlockN["TransformerBlock (N layers)<br/>params['block_0'], ..., params['block_N-1']"]
    
    FinalLN["LayerNorm<br/>params['final_ln']"]
    OutputLayer["Linear (model_dim → vocab_size)<br/>params['output_layer']<br/>or tied with embed"]
    Logits["Logits<br/>[batch, seq_len, vocab_size]"]
    
    Input --> Embed
    Embed --> InputEnc
    InputEnc --> BlockN
    BlockN --> FinalLN
    FinalLN --> OutputLayer
    OutputLayer --> Logits
    
    subgraph "TransformerBlock Components"
        PreLN0["Pre LayerNorm 0<br/>params['pre_ln_0']"]
        Attn["Attention<br/>params['attn']"]
        PostLN0["Post LayerNorm 0<br/>(optional)"]
        Skip0["Residual Connection"]
        
        PreLN1["Pre LayerNorm 1<br/>params['pre_ln_1']"]
        FFN0["Linear (model_dim → expand_dim)<br/>params['ffn_0']"]
        FFN1["Linear (expand_dim → model_dim)<br/>params['ffn_1']"]
        FFNGate["FFN Gate<br/>(optional)<br/>params['ffn_0_gate']"]
        PostLN1["Post LayerNorm 1<br/>(optional)"]
        Skip1["Residual Connection"]
    end
```

**Sources:** [simply/model_lib.py:1342-1435](), [simply/model_lib.py:1436-1456](), [simply/model_lib.py:1488-1752]()

### Attention Mechanism

The `Attention` module implements multi-head self-attention with rotary positional embeddings (RoPE), optional flash attention, and KV caching for efficient decoding.

```mermaid
graph TB
    Input["x: [batch, seq_len, model_dim]<br/>segment_ids, segment_positions"]
    
    QKVProj["QKV Projection<br/>params['qkv_proj'] or<br/>params['q_proj'], params['kv_proj']"]
    
    QKVSplit["Split Q, K, V<br/>Q: [batch, seq_len, n_heads, per_head_dim]<br/>K, V: [batch, seq_len, n_kv_heads, per_head_dim]"]
    
    QKNorm["QK Normalization<br/>(optional)<br/>params['q_norm'], params['k_norm']"]
    
    RoPE["Rotary Positional Embedding<br/>rotary_positional_embedding()"]
    
    QScale["Query Scaling<br/>q / sqrt(per_head_dim)<br/>or per_dim_scale"]
    
    KVCache["Update Decode State<br/>updated_decode_state()<br/>KV Cache Management"]
    
    AttnChoice{"Flash Attention?<br/>use_flash_attention"}
    
    FlashAttn["splash_attention.make_splash_mha()<br/>Pallas Kernel"]
    StandardAttn["create_mask() + attn()<br/>Standard Attention"]
    
    OProj["Output Projection<br/>params['o_proj']"]
    
    Output["Output: [batch, seq_len, model_dim]<br/>decode_state"]
    
    Input --> QKVProj
    QKVProj --> QKVSplit
    QKVSplit --> QKNorm
    QKNorm --> RoPE
    RoPE --> QScale
    QScale --> KVCache
    
    KVCache --> AttnChoice
    AttnChoice -->|Yes| FlashAttn
    AttnChoice -->|No| StandardAttn
    
    FlashAttn --> OProj
    StandardAttn --> OProj
    OProj --> Output
```

**Sources:** [simply/model_lib.py:617-1081](), [simply/model_lib.py:793-1080](), [simply/model_lib.py:330-363](), [simply/model_lib.py:365-461]()

### Core Module Classes

| Class | Purpose | Key Parameters | Init Location |
|-------|---------|----------------|---------------|
| `TransformerLM` | Top-level model | `config`, `sharding_config` | [model_lib.py:1342-1435]() |
| `TransformerBlock` | Single transformer layer | `model_dim`, `n_heads`, `expand_factor` | [model_lib.py:1083-1306]() |
| `Attention` | Multi-head attention | `model_dim`, `n_heads`, `per_head_dim`, `n_kv_heads` | [model_lib.py:617-1081]() |
| `Embedding` | Token embedding | `vocab_size`, `dim` | [model_lib.py:118-161]() |
| `Linear` | Linear transformation | `input_dim`, `output_dim` | [model_lib.py:163-221]() |
| `LayerNorm` | Layer/RMS normalization | `dim`, `use_bias` | [model_lib.py:223-290]() |

**Sources:** [simply/model_lib.py:118-1306]()

## Training Pipeline

### Gradient Computation and Update

The `train_one_step()` function orchestrates a complete training step, including forward pass, backward pass, gradient clipping, and parameter updates.

```mermaid
graph TB
    Start["train_one_step(state, batch, model, opt, ...)"]
    
    GradAccum{"grad_accum_steps > 1?"}
    
    SingleGrad["_compute_grad(batch)<br/>jax.value_and_grad()<br/>Returns: loss, extra_output, grad"]
    
    AccumLoop["jax.lax.scan()<br/>grad_accum_step_fn<br/>Accumulate gradients"]
    
    GradClip{"clip_grad_norm > 0?"}
    ClipGrad["clip_norm_fn(grad, threshold)<br/>safe_clip() normalization"]
    
    OptApply["opt.apply(state, grad)<br/>Returns: update, new_state"]
    
    UpdateClip{"clip_update_norm > 0<br/>or clip_update_rms > 0?"}
    ClipUpdate["clip_norm_fn() or clip_rms_fn()<br/>Clip updates"]
    
    WeightDecay{"weight_decay > 0?"}
    ApplyDecay["update + params * weight_decay"]
    
    ApplyUpdates["opt.apply_updates(new_state, update * lr)<br/>new_state['steps'] += 1"]
    
    Return["Return: loss, new_state, log_dict"]
    
    Start --> GradAccum
    GradAccum -->|No| SingleGrad
    GradAccum -->|Yes| AccumLoop
    
    SingleGrad --> GradClip
    AccumLoop --> GradClip
    
    GradClip -->|Yes| ClipGrad
    GradClip -->|No| OptApply
    ClipGrad --> OptApply
    
    OptApply --> UpdateClip
    UpdateClip -->|Yes| ClipUpdate
    UpdateClip -->|No| WeightDecay
    ClipUpdate --> WeightDecay
    
    WeightDecay -->|Yes| ApplyDecay
    WeightDecay -->|No| ApplyUpdates
    ApplyDecay --> ApplyUpdates
    
    ApplyUpdates --> Return
```

**Sources:** [simply/model_lib.py:1878-2007](), [simply/model_lib.py:1902-1966]()

### Loss Computation

The `compute_loss()` and `compute_train_loss()` functions implement cross-entropy loss with masked token positions.

```mermaid
graph TB
    Batch["Batch Input<br/>decoder_input_tokens: [batch, seq_len]<br/>decoder_target_tokens: [batch, seq_len]<br/>decoder_loss_weights: [batch, seq_len]"]
    
    Forward["model.apply(params, inputs,<br/>segment_ids, segment_positions)<br/>Returns: logits, extra_output"]
    
    Logits["logits: [batch, seq_len, vocab_size]<br/>Cast to float32"]
    
    OneHot["jax.nn.one_hot(targets, vocab_size)<br/>targets_one_hot: [batch, seq_len, vocab_size]"]
    
    LogSoftmax["jax.nn.log_softmax(logits)<br/>Log probabilities"]
    
    TokenLoss["jnp.einsum('blv,blv->bl',<br/>targets_one_hot, log_softmax)<br/>Per-token loss"]
    
    MaskedLoss["token_loss * loss_weights<br/>Apply loss mask"]
    
    TotalLoss["jnp.sum(masked_loss) / jnp.sum(loss_weights)<br/>Normalized loss"]
    
    Accuracy["argmax(logits) == targets<br/>Compute accuracy"]
    
    ExtraLoss["collect_loss_and_metric(extra_output)<br/>Additional losses from model"]
    
    Return["Return: loss, {accuracy, loss_weight, ...}"]
    
    Batch --> Forward
    Forward --> Logits
    Logits --> LogSoftmax
    
    Batch --> OneHot
    OneHot --> TokenLoss
    LogSoftmax --> TokenLoss
    
    TokenLoss --> MaskedLoss
    Batch --> MaskedLoss
    
    MaskedLoss --> TotalLoss
    Logits --> Accuracy
    Batch --> Accuracy
    
    Forward --> ExtraLoss
    
    TotalLoss --> Return
    Accuracy --> Return
    ExtraLoss --> Return
```

**Sources:** [simply/model_lib.py:1770-1809](), [simply/model_lib.py:1839-1845]()

### Training State Management

| State Component | Type | Purpose | Update Frequency |
|----------------|------|---------|------------------|
| `state['params']` | PyTree | Model parameters | Every step (via optimizer) |
| `state['opt_state']` | PyTree | Optimizer state (momentum, etc.) | Every step |
| `state['steps']` | Array | Training step counter | Every step |
| `state['teacher_params']` | PyTree (optional) | Teacher model parameters for distillation | Static |

**Sources:** [simply/model_lib.py:2302-2354](), [simply/model_lib.py:2094-2272]()

## Inference Pipeline

### LMInterface: High-Level Inference API

The `LMInterface` class provides a user-friendly API for text generation and scoring, managing the complexity of batching, KV caching, and sampling internally.

```mermaid
graph TB
    User["User Code"]
    
    LMInit["LMInterface.__init__(<br/>model, params, vocab,<br/>default_sampling_params)"]
    
    Generate["LMInterface.generate(<br/>input_text, prng_key,<br/>sampling_params)"]
    
    Score["LMInterface.score(<br/>input_text, output_text,<br/>scoring_params)"]
    
    ScoreTokens["LMInterface.score_tokens(<br/>tokens, scoring_params)"]
    
    subgraph "Internal Methods (JIT Compiled)"
        PrefillFn["prefill_fn(params, inputs,<br/>extra_inputs, position)<br/>Process first K tokens"]
        
        DecodeFn["decode_fn(params, init_sampling_state,<br/>temperature, top_k, top_p)<br/>Autoregressive generation"]
        
        PadStateTo["pad_state_to_fn(sampling_state, length)<br/>Extend KV cache"]
    end
    
    InputProcessor["input_processor.encode()<br/>Tokenization"]
    
    ProcessedInput["ProcessedInputBatch<br/>tokens, lengths, extra_inputs"]
    
    SamplingState["SamplingState<br/>tokens, decode_state,<br/>position, prng_key"]
    
    SamplingOutput["SamplingOutput<br/>input/output_chunks,<br/>token_ids, logprobs, scores"]
    
    User --> LMInit
    LMInit --> Generate
    LMInit --> Score
    LMInit --> ScoreTokens
    
    Generate --> InputProcessor
    InputProcessor --> ProcessedInput
    ProcessedInput --> PrefillFn
    PrefillFn --> SamplingState
    
    SamplingState --> DecodeFn
    DecodeFn --> PadStateTo
    PadStateTo --> DecodeFn
    
    DecodeFn --> SamplingOutput
    SamplingOutput --> User
    
    Score --> ScoreTokens
    ScoreTokens --> User
```

**Sources:** [simply/model_lib.py:2690-3150](), [simply/model_lib.py:2774-3050]()

### Decoding Loop: SamplingState and continue_decode

The decoding process uses a while loop with `SamplingState` to manage KV cache, token generation, and stopping conditions.

```mermaid
graph TB
    InitState["SamplingState<br/>position, decode_state,<br/>tokens, input_lens,<br/>max_decode_steps"]
    
    CondFn["position < decode_state_length<br/>and not all(has_ended)"]
    
    BodyStart["continue_decode() body_fn"]
    
    InputTokens["sampling_state.input_tokens<br/>[batch, 1] at position"]
    
    ModelApply["model.apply(params, input_tokens,<br/>segment_positions=position,<br/>decode_state=decode_state)<br/>Returns: logits, extra_output"]
    
    Sample["sample_from_logits(prng_key, logits,<br/>temperature, top_k, top_p)<br/>Returns: output_tokens, output_logprobs"]
    
    SelectToken{"has_ended?"}
    UseInput["Use input_tokens<br/>(prefill)"]
    UseSampled["Use output_tokens<br/>(generation)"]
    
    Score["compute_log_likelihood(logits, output_tokens,<br/>scoring_temperature, scoring_top_k, scoring_top_p)<br/>Returns: output_scores"]
    
    UpdateState["dataclasses.replace(sampling_state,<br/>position=position+1,<br/>decode_state=new_decode_state,<br/>tokens=updated_tokens,<br/>token_logprobs, token_scores)"]
    
    WhileLoop["jax.lax.while_loop(cond_fn, body_fn, init_state)"]
    
    FinalState["Final SamplingState"]
    
    InitState --> WhileLoop
    WhileLoop --> CondFn
    
    CondFn -->|True| BodyStart
    CondFn -->|False| FinalState
    
    BodyStart --> InputTokens
    InputTokens --> ModelApply
    ModelApply --> Sample
    
    Sample --> SelectToken
    SelectToken -->|Yes| UseInput
    SelectToken -->|No| UseSampled
    
    UseInput --> Score
    UseSampled --> Score
    
    Score --> UpdateState
    UpdateState --> CondFn
```

**Sources:** [simply/model_lib.py:3338-3433](), [simply/model_lib.py:2471-2572]()

### Sampling and Scoring Functions

| Function | Purpose | Key Parameters | Returns |
|----------|---------|----------------|---------|
| `sample_from_logits()` | Sample next token from logits | `logits`, `temperature`, `top_k`, `top_p` | `tokens`, `logprobs` |
| `compute_log_likelihood()` | Score given tokens under model | `logits`, `tokens`, `temperature`, `top_k`, `top_p` | `scores` [batch, seq_len] |
| `top_k_mask()` | Create top-k sampling mask | `logits`, `top_k` | Boolean mask |
| `top_p_mask()` | Create nucleus sampling mask | `logits`, `top_p` | Boolean mask |

**Sources:** [simply/model_lib.py:3171-3229](), [simply/model_lib.py:3285-3336](), [simply/model_lib.py:3152-3169]()

## Distributed Execution

### Sharding and Partitioning

Simply uses JAX's GSPMD (General SPMD) for distributed execution. The `ShardingConfig` specifies how tensors are partitioned across the device mesh.

```mermaid
graph TB
    MeshSetup["sharding_lib.set_default_mesh_shape(mesh_shape, dcn_mesh_shape)"]
    
    MeshDef["JAX Device Mesh<br/>Axes: replica, data, model<br/>Example: [1, 265, 1]"]
    
    ShardingConfig["ShardingConfig<br/>Partition annotations for tensors"]
    
    subgraph "Partition Specifications"
        DataPart["data_partition: ('data', None)<br/>Batch dimension sharded across 'data' axis"]
        
        ActivationPart["activation_partition: ('data', None)<br/>Activations sharded across 'data' axis"]
        
        EmbedPart["embed_partition: (None, 'model')<br/>Embedding weights sharded across 'model' axis"]
        
        AttnPart["attn_qkv_partition: (None, 'model', None)<br/>Attention weights sharded"]
        
        FFNPart["ffn0_partition: (None, 'model')<br/>FFN weights sharded"]
    end
    
    ModelInit["model.init(prng_key)<br/>Create parameters with sharding"]
    
    Constrain["with_sharding_constraint(tensor, partition)<br/>Enforce sharding during execution"]
    
    JITCompile["jax.jit(train_one_step_fn)<br/>Compile with partitioning"]
    
    MeshSetup --> MeshDef
    ShardingConfig --> DataPart
    ShardingConfig --> ActivationPart
    ShardingConfig --> EmbedPart
    ShardingConfig --> AttnPart
    ShardingConfig --> FFNPart
    
    MeshDef --> ModelInit
    ShardingConfig --> ModelInit
    
    ModelInit --> Constrain
    Constrain --> JITCompile
```

**Sources:** [simply/model_lib.py:2105-2106](), [simply/model_lib.py:138-141](), [simply/model_lib.py:867-870]()

### Data Distribution: build_global_array

The `build_global_array()` function distributes local data arrays across all devices in the mesh, creating global arrays with specified sharding.

```mermaid
graph TB
    LocalBatch["Local Batch Data<br/>Shape: [local_batch_size, seq_len]<br/>One array per process"]
    
    Split["jnp.split(inputs, len(jax.local_devices()), axis=0)<br/>Split across local devices"]
    
    DevicePut["jax.device_put(arrays, jax.local_devices())<br/>Place on local devices"]
    
    MakeArray["jax.make_array_from_single_device_arrays(<br/>global_shape, init_sharding, arrays)<br/>Create global array"]
    
    GlobalArray["Global Array<br/>Shape: [global_batch_size, seq_len]<br/>Sharded: ('replica', 'data', 'model'), None"]
    
    Constrain["jax.lax.with_sharding_constraint(arr, final_sharding)<br/>Apply final sharding"]
    
    FinalArray["Final Global Array<br/>Sharded: ('data', None)<br/>Ready for training"]
    
    LocalBatch --> Split
    Split --> DevicePut
    DevicePut --> MakeArray
    MakeArray --> GlobalArray
    GlobalArray --> Constrain
    Constrain --> FinalArray
```

**Sources:** [simply/model_lib.py:3439-3447](), [simply/model_lib.py:2288-2300](), [simply/model_lib.py:2199-2200]()

### Key Sharding Functions

| Function | Purpose | Location |
|----------|---------|----------|
| `set_default_mesh_shape()` | Initialize JAX device mesh | `sharding_lib` (imported) |
| `mesh_sharding()` | Create PartitionSpec from annotation | `sharding_lib` (imported) |
| `with_sharding_constraint()` | Apply sharding constraint to tensor | `sharding_lib` (imported) |
| `get_default_mesh()` | Get current device mesh | `sharding_lib` (imported) |
| `build_global_array()` | Distribute local arrays across devices | [model_lib.py:3439-3447]() |

**Sources:** [simply/model_lib.py:59-62](), [simply/model_lib.py:3439-3447]()

## Data Pipeline

### Dataset Creation Flow

The `create_dataset()` function in `data_lib.py` creates training and validation datasets using SeqIO task registry.

```mermaid
graph TB
    Config["ExperimentConfig<br/>dataset_name, seq_len,<br/>batch_size, vocab"]
    
    CreateSplit["create_dataset_split(config, training=True/False)"]
    
    CheckSpec{"dataset_spec?"}
    
    SimpleJSON["DataSourceRegistry.get_instance(name)<br/>SimpleDataSource.load()<br/>Create SimpleDataloader"]
    
    SeqIOTask["seqio.get_dataset(dataset_name,<br/>task_feature_lengths,<br/>batch_size, feature_converter)<br/>TF Dataset"]
    
    FeatureConv{"feature_converter_name?"}
    LMConv["LMFeatureConverter(pack=config.use_packing,<br/>bos_id=config.bos_id)<br/>Target: seq_len"]
    PrefixConv["PrefixLMFeatureConverter(pack=config.use_packing)<br/>Inputs: seq_len/2, Targets: seq_len/2"]
    
    WrapDataset["Dataset(tf_dataset, processors)<br/>Add select_local_batch processor"]
    
    ReturnSets["Return: train_set, validation_set"]
    
    Config --> CreateSplit
    CreateSplit --> CheckSpec
    
    CheckSpec -->|simply_json:| SimpleJSON
    CheckSpec -->|TFDS| SeqIOTask
    
    SeqIOTask --> FeatureConv
    FeatureConv -->|LMFeatureConverter| LMConv
    FeatureConv -->|PrefixLMFeatureConverter| PrefixConv
    
    SimpleJSON --> ReturnSets
    LMConv --> WrapDataset
    PrefixConv --> WrapDataset
    WrapDataset --> ReturnSets
```

**Sources:** [simply/data_lib.py:780-849](), [simply/data_lib.py:720-734]()

### Vocabulary Registration

Simply maintains a registry of vocabularies using `TokenizerRegistry`, with 40+ registered tokenizers for different datasets and model families.

```mermaid
graph TB
    VocabFiles["Vocabulary Files<br/>~/.cache/simply/vocabs/<br/>*.model, *.spiece.model"]
    
    Register["register_vocabs()<br/>data_lib module initialization"]
    
    TokenizerReg["TokenizerRegistry.register_value(<br/>seqio.SentencePieceVocabulary(path), name)"]
    
    subgraph "Registered Vocabularies"
        OpenMix["OpenMix Vocabs<br/>vb100864_openmix_v1,<br/>vb32768_openmix_v1, ..."]
        
        Gemma["Gemma Vocabs<br/>vb256128_gemma2,<br/>vb262144_gemma3"]
        
        Pile["Pile Vocabs<br/>vb50432_v3_pile,<br/>vb100864_v1_pile, ..."]
        
        Custom["Custom Vocabs<br/>fwedu_100864_v1, ..."]
    end
    
    Retrieve["TokenizerRegistry.get(name)<br/>or vocab in config"]
    
    UseInModel["Used by:<br/>- LMInterface input_processor<br/>- Dataset creation<br/>- Token encoding/decoding"]
    
    VocabFiles --> Register
    Register --> TokenizerReg
    
    TokenizerReg --> OpenMix
    TokenizerReg --> Gemma
    TokenizerReg --> Pile
    TokenizerReg --> Custom
    
    OpenMix --> Retrieve
    Gemma --> Retrieve
    Pile --> Retrieve
    Custom --> Retrieve
    
    Retrieve --> UseInModel
```

**Sources:** [simply/data_lib.py:46-82](), [simply/data_lib.py:84-95]()

### Batch Processing

| Batch Field | Shape | Description | Optional |
|-------------|-------|-------------|----------|
| `decoder_input_tokens` | [batch, seq_len] | Input token IDs | No |
| `decoder_target_tokens` | [batch, seq_len] | Target token IDs (shifted by 1) | No |
| `decoder_loss_weights` | [batch, seq_len] | Loss mask (0 or 1) | Yes (defaults to all 1s) |
| `decoder_segment_ids` | [batch, seq_len] | Segment IDs for packed sequences | Yes |
| `decoder_positions` | [batch, seq_len] | Position indices | Yes (auto-generated) |

**Sources:** [simply/model_lib.py:1770-1809](), [simply/data_lib.py:780-849]()

---

