<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/acme · page 6 Experiment Management and Execution · fetched 2026-10-26 -->

# Experiment Management and Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [acme/jax/experiments/__init__.py](acme/jax/experiments/__init__.py)
- [acme/jax/experiments/config.py](acme/jax/experiments/config.py)
- [acme/jax/experiments/make_distributed_experiment.py](acme/jax/experiments/make_distributed_experiment.py)
- [acme/jax/experiments/make_distributed_offline_experiment.py](acme/jax/experiments/make_distributed_offline_experiment.py)
- [acme/jax/experiments/run_experiment.py](acme/jax/experiments/run_experiment.py)
- [acme/jax/experiments/run_experiment_test.py](acme/jax/experiments/run_experiment_test.py)
- [acme/jax/experiments/run_offline_experiment.py](acme/jax/experiments/run_offline_experiment.py)
- [acme/jax/experiments/run_offline_experiment_test.py](acme/jax/experiments/run_offline_experiment_test.py)
- [acme/jax/experiments/test_utils.py](acme/jax/experiments/test_utils.py)

</details>



This document covers Acme's experiment management and execution framework, which provides a unified interface for configuring, running, and scaling reinforcement learning experiments. The system handles component assembly, environment setup, distributed execution, and experiment lifecycle management through a declarative configuration approach.

For information about individual agent implementations and their specific builders, see [Reinforcement Learning Agents](#4). For details about environment wrappers and preprocessing, see [Environment Wrappers](#5).

## Core Configuration System

The experiment management system is built around the `ExperimentConfig` class, which serves as a declarative specification for all aspects of an RL experiment. This configuration-driven approach separates experiment definition from execution details.

### ExperimentConfig Architecture

```mermaid
graph TB
    ExperimentConfig["ExperimentConfig"] --> Builder["builder: ActorLearnerBuilder"]
    ExperimentConfig --> NetworkFactory["network_factory: NetworkFactory"]
    ExperimentConfig --> EnvironmentFactory["environment_factory: EnvironmentFactory"]
    ExperimentConfig --> LoggerFactory["logger_factory: LoggerFactory"]
    ExperimentConfig --> Checkpointing["checkpointing: CheckpointingConfig"]
    ExperimentConfig --> EvaluatorFactories["evaluator_factories: Sequence[EvaluatorFactory]"]
    
    Builder --> MakeReplayTables["make_replay_tables()"]
    Builder --> MakeDatasetIterator["make_dataset_iterator()"]
    Builder --> MakeLearner["make_learner()"]
    Builder --> MakeActor["make_actor()"]
    Builder --> MakeAdder["make_adder()"]
    
    NetworkFactory --> Networks["Networks"]
    EnvironmentFactory --> Environment["dm_env.Environment"]
    
    Networks --> MakePolicy["make_policy()"]
    MakePolicy --> Policy["Policy"]
```

The `ExperimentConfig` class in [acme/jax/experiments/config.py:123-174]() uses the builder pattern to decouple experiment specification from component instantiation. Key attributes include:

| Attribute | Type | Purpose |
|-----------|------|---------|
| `builder` | `ActorLearnerBuilder` | Constructs agent components (actor, learner, replay tables) |
| `network_factory` | `NetworkFactory` | Creates neural network architectures |
| `environment_factory` | `EnvironmentFactory` | Instantiates training environments |
| `max_num_actor_steps` | `int` | Training duration limit |
| `seed` | `int` | Random seed for reproducibility |
| `checkpointing` | `CheckpointingConfig` | Persistence and recovery configuration |

Sources: [acme/jax/experiments/config.py:123-174]()

### Factory Protocol System

The framework uses protocol-based factories to provide flexible component creation while maintaining type safety:

```mermaid
graph LR
    NetworkFactory["NetworkFactory[Networks]"] --> Networks["Networks"]
    PolicyFactory["PolicyFactory[Networks, Policy]"] --> Policy["Policy"]
    EvaluatorFactory["EvaluatorFactory[Policy]"] --> Worker["core.Worker"]
    MakeActorFn["MakeActorFn[Policy]"] --> Actor["core.Actor"]
    
    Networks --> PolicyFactory
    Policy --> EvaluatorFactory
    Policy --> MakeActorFn
    
    EnvironmentSpec["specs.EnvironmentSpec"] --> NetworkFactory
    EnvironmentSpec --> PolicyFactory
    VariableSource["core.VariableSource"] --> MakeActorFn
```

These protocols enable dependency injection and component composition. The `NetworkFactory` protocol in [acme/jax/experiments/config.py:43-47]() creates networks from environment specifications, while `PolicyFactory` in [acme/jax/experiments/config.py:57-62]() constructs policies with evaluation mode support.

Sources: [acme/jax/experiments/config.py:43-47](), [acme/jax/experiments/config.py:57-62](), [acme/jax/experiments/config.py:35-40](), [acme/jax/experiments/config.py:65-70]()

## Single-Threaded Experiment Execution

The `run_experiment()` function provides a simple, single-threaded execution environment suitable for local development and testing. It orchestrates the entire experiment lifecycle from component creation to training loop execution.

### Execution Flow Architecture

```mermaid
flowchart TD
    start["run_experiment()"] --> config["Parse ExperimentConfig"]
    config --> env["Create Environment from environment_factory"]
    env --> nets["Create Networks from network_factory"]
    nets --> policy["Create Policy from make_policy()"]
    policy --> replay["Create Reverb Tables from builder.make_replay_tables()"]
    
    replay --> server["Start Reverb Server"]
    server --> dataset["Create Dataset Iterator from builder.make_dataset_iterator()"]
    dataset --> learner["Create Learner from builder.make_learner()"]
    learner --> adder["Create Adder from builder.make_adder()"]
    adder --> actor["Create Actor from builder.make_actor()"]
    
    actor --> learning_actor["Wrap with _LearningActor"]
    learning_actor --> train_loop["Create Training EnvironmentLoop"]
    train_loop --> eval_setup["Setup Evaluation Loop (if enabled)"]
    eval_setup --> execution["Execute Training/Eval Cycles"]
    execution --> checkpoint["Save Checkpoints"]
    checkpoint --> done["Experiment Complete"]
```

The `run_experiment()` function in [acme/jax/experiments/run_experiment.py:34-179]() creates components in reverse dependency order. The learner is created first as a `VariableSource`, then the adder, and finally the actor which depends on both.

### Learning Actor Integration

A key innovation is the `_LearningActor` wrapper in [acme/jax/experiments/run_experiment.py:183-260]() that combines environment interaction with learning:

```mermaid
graph TB
    LearningActor["_LearningActor"] --> BaseActor["base actor: core.Actor"]
    LearningActor --> Learner["learner: core.Learner"]
    LearningActor --> Iterator["iterator: PrefetchingIterator"]
    LearningActor --> ReplayTables["replay_tables: Sequence[reverb.Table]"]
    
    BaseActor --> SelectAction["select_action()"]
    BaseActor --> Observe["observe()"]
    
    LearningActor --> Update["update()"]
    Update --> MaybeTrain["_maybe_train()"]
    MaybeTrain --> LearnerStep["learner.step()"]
    MaybeTrain --> ActorUpdate["actor.update()"]
```

The `_LearningActor.update()` method in [acme/jax/experiments/run_experiment.py:254-259]() checks for available data and performs learner steps when the replay tables have sufficient samples, ensuring efficient single-threaded learning.

Sources: [acme/jax/experiments/run_experiment.py:34-179](), [acme/jax/experiments/run_experiment.py:183-260]()

## Distributed Experiment Execution

The `make_distributed_experiment()` function creates LaunchPad programs for scalable, distributed training across multiple machines and accelerators. It decomposes the experiment into separate processes for replay storage, learning, and environment interaction.

### Distributed System Architecture

```mermaid
graph TB
    subgraph "LaunchPad Program"
        Counter["Counter Node<br/>counting.Counter"]
        ReplayNode["Reverb Node<br/>reverb.Server"]
        
        subgraph "Learner Group"
            PrimaryLearner["Primary Learner<br/>build_learner()"]
            SecondaryLearners["Secondary Learners<br/>(load balancing)"]
        end
        
        subgraph "Inference Servers"
            InferenceServer1["Inference Server 1<br/>InferenceServer"]
            InferenceServerN["Inference Server N"]
        end
        
        subgraph "Actor Groups"
            ActorNode1["Actor Node 1<br/>MultiThreadingColocation"]
            ActorNodeN["Actor Node N"]
        end
        
        EvaluatorNode["Evaluator Node<br/>evaluation loops"]
        ModelSaver["Model Saver<br/>JAXSnapshotter"]
    end
    
    Counter --> PrimaryLearner
    Counter --> ActorNode1
    Counter --> EvaluatorNode
    
    ReplayNode --> PrimaryLearner
    ReplayNode --> ActorNode1
    
    PrimaryLearner --> InferenceServer1
    PrimaryLearner --> SecondaryLearners
    
    InferenceServer1 --> ActorNode1
    InferenceServerN --> ActorNodeN
    
    PrimaryLearner --> EvaluatorNode
    PrimaryLearner --> ModelSaver
```

The distributed system in [acme/jax/experiments/make_distributed_experiment.py:47-421]() supports several key features:

- **Multi-learner scaling**: Primary learner handles checkpointing while secondary learners provide load balancing for variable requests
- **Inference server optimization**: Batched inference using JAX transformations for efficient GPU/TPU utilization  
- **Actor colocation**: Configurable process vs. thread colocation for actor groups
- **Component isolation**: Separate processes for replay, learning, and environment interaction

### Inference Server Integration

For high-throughput action selection, the framework supports inference servers that batch policy computations:

```mermaid
graph LR
    ActorCorePolicy["ActorCore Policy"] --> InferenceServerConfig["InferenceServerConfig"]
    InferenceServerConfig --> InferenceServer["InferenceServer"]
    
    InferenceServer --> JAXHandler["jax.jit(jax.vmap(policy.select_action))"]
    JAXHandler --> BatchedInference["Batched Action Selection"]
    
    MultipleActors["Multiple Actors"] --> InferenceServer
    InferenceServer --> ActionResponses["Action Responses"]
```

The inference server in [acme/jax/experiments/make_distributed_experiment.py:211-245]() uses `jax.vmap()` to vectorize policy computations across multiple actor requests, maximizing accelerator utilization.

Sources: [acme/jax/experiments/make_distributed_experiment.py:47-421](), [acme/jax/experiments/make_distributed_experiment.py:211-245]()

## Offline Reinforcement Learning Support

The framework provides specialized support for offline RL through `OfflineExperimentConfig` and related execution functions that learn from pre-collected datasets rather than environment interaction.

### Offline Experiment Configuration

```mermaid
graph TB
    OfflineExperimentConfig["OfflineExperimentConfig"] --> OfflineBuilder["builder: OfflineBuilder"]
    OfflineExperimentConfig --> NetworkFactory["network_factory"]
    OfflineExperimentConfig --> DemonstrationDataset["demonstration_dataset_factory"]
    OfflineExperimentConfig --> EnvironmentFactory["environment_factory (for evaluation)"]
    OfflineExperimentConfig --> MaxLearnerSteps["max_num_learner_steps"]
    
    DemonstrationDataset --> Iterator["Iterator[Sample]"]
    OfflineBuilder --> MakeLearner["make_learner()"]
    OfflineBuilder --> MakeActor["make_actor() (for evaluation)"]
    
    Iterator --> MakeLearner
    NetworkFactory --> Networks["Networks"]
    Networks --> MakeLearner
    Networks --> MakeActor
```

The `OfflineExperimentConfig` class in [acme/jax/experiments/config.py:206-255]() replaces environment interaction components with dataset specifications. Key differences from online experiments include:

- `demonstration_dataset_factory`: Creates iterators over pre-collected transitions
- `max_num_learner_steps`: Training duration measured in learning steps rather than environment steps  
- `OfflineBuilder`: Specialized builder for offline learning components

### Offline Execution Flow

```mermaid
flowchart TD
    start["run_offline_experiment()"] --> config["Parse OfflineExperimentConfig"]
    config --> env["Create Environment for Evaluation"]
    env --> nets["Create Networks"]
    nets --> dataset["Create Demonstration Dataset"]
    dataset --> learner["Create Offline Learner"]
    learner --> eval_setup["Setup Evaluation Loop"]
    eval_setup --> train_loop["Training Loop"]
    train_loop --> learner_step["learner.step()"]
    learner_step --> checkpoint["Save Checkpoint"]
    checkpoint --> eval_check["Evaluation Time?"]
    eval_check -->|Yes| eval_run["Run Evaluation"]
    eval_check -->|No| continue_train["Continue Training"]
    eval_run --> continue_train
    continue_train --> done_check["Max Steps Reached?"]
    done_check -->|No| train_loop
    done_check -->|Yes| done["Experiment Complete"]
```

The `run_offline_experiment()` function in [acme/jax/experiments/run_offline_experiment.py:25-120]() focuses on learner progression rather than environment interaction, with periodic evaluation to assess learned policy performance.

Sources: [acme/jax/experiments/config.py:206-255](), [acme/jax/experiments/run_offline_experiment.py:25-120](), [acme/jax/experiments/make_distributed_offline_experiment.py:33-157]()

## Checkpointing and Persistence

The framework provides comprehensive checkpointing capabilities through `CheckpointingConfig`, supporting both periodic snapshots and crash recovery across distributed components.

### Checkpointing System Architecture

```mermaid
graph TB
    CheckpointingConfig["CheckpointingConfig"] --> Directory["directory: checkpoint location"]
    CheckpointingConfig --> TimeDelta["time_delta_minutes: save frequency"]
    CheckpointingConfig --> MaxToKeep["max_to_keep: retention policy"]
    CheckpointingConfig --> ReplayCheckpointing["replay_checkpointing_time_delta_minutes"]
    
    Directory --> LearnerCheckpoints["Learner State Checkpoints"]
    Directory --> CounterCheckpoints["Counter State Checkpoints"]
    Directory --> ReplayCheckpoints["Replay Buffer Checkpoints"]
    Directory --> Snapshots["Model Snapshots"]
    
    LearnerCheckpoints --> CheckpointingRunner["savers.CheckpointingRunner"]
    CounterCheckpoints --> CheckpointingRunner
    ReplayCheckpoints --> ReverbNode["lp.ReverbNode"]
    Snapshots --> JAXSnapshotter["snapshotter.JAXSnapshotter"]
```

The `CheckpointingConfig` class in [acme/jax/experiments/config.py:83-120]() provides fine-grained control over persistence behavior:

| Option | Purpose | Default |
|--------|---------|---------|
| `time_delta_minutes` | Checkpoint save frequency | 5 minutes |
| `max_to_keep` | Number of checkpoints retained | 1 |
| `directory` | Checkpoint storage location | `~/acme` |
| `add_uid` | Unique identifier for parallel runs | `True` |
| `replay_checkpointing_time_delta_minutes` | Replay buffer checkpoint frequency | `None` (disabled) |

### Distributed Checkpointing Strategy

In distributed setups, checkpointing is coordinated across components:

```mermaid
graph TB
    PrimaryLearner["Primary Learner"] --> LearnerCheckpoint["Learner State<br/>CheckpointingRunner"]
    SecondaryLearners["Secondary Learners"] --> RestoreOnly["Restore from Primary<br/>(no checkpointing)"]
    
    Counter["Shared Counter"] --> CounterCheckpoint["Counter State<br/>CheckpointingRunner"]
    
    ReverbNode["Reverb Node"] --> ReplayCheckpoint["Replay Buffer<br/>Asynchronous Checkpointing"]
    
    ModelSaver["Model Saver Node"] --> Snapshots["Model Snapshots<br/>JAXSnapshotter"]
    
    LearnerCheckpoint --> SharedStorage["Shared Storage"]
    CounterCheckpoint --> SharedStorage
    ReplayCheckpoint --> SharedStorage
    Snapshots --> SharedStorage
```

Only the primary learner creates checkpoints in [acme/jax/experiments/make_distributed_experiment.py:189-202](), while secondary learners restore from the primary's state to maintain consistency.

Sources: [acme/jax/experiments/config.py:83-120](), [acme/jax/experiments/make_distributed_experiment.py:189-202]()

## Component Factory Integration

The experiment framework integrates with Acme's broader component ecosystem through standardized factory interfaces that enable flexible agent composition and customization.

### Builder Pattern Integration

```mermaid
graph TB
    ExperimentConfig --> ActorLearnerBuilder["ActorLearnerBuilder[Networks, Policy, Sample]"]
    
    ActorLearnerBuilder --> MakeReplayTables["make_replay_tables(environment_spec, policy)"]
    ActorLearnerBuilder --> MakeDatasetIterator["make_dataset_iterator(replay_client)"]  
    ActorLearnerBuilder --> MakeLearner["make_learner(networks, dataset, ...)"]
    ActorLearnerBuilder --> MakeActor["make_actor(policy, environment_spec, ...)"]
    ActorLearnerBuilder --> MakeAdder["make_adder(replay_client, environment_spec, policy)"]
    ActorLearnerBuilder --> MakePolicy["make_policy(networks, environment_spec, evaluation)"]
    
    MakeReplayTables --> ReverbTables["Sequence[reverb.Table]"]
    MakeDatasetIterator --> Iterator["core.PrefetchingIterator"]
    MakeLearner --> Learner["core.Learner"]
    MakeActor --> Actor["core.Actor"]
    MakeAdder --> Adder["adders.Adder"]
    MakePolicy --> Policy["Policy"]
```

The builder pattern in [acme/agents/jax/builders.py]() provides a consistent interface for agent construction. Each experiment configuration specifies a builder that knows how to create all necessary agent components from the provided networks and environment specification.

### Factory Composition Flow

```mermaid
sequenceDiagram
    participant Config as ExperimentConfig
    participant NetFactory as network_factory
    participant Builder as builder
    participant EnvFactory as environment_factory
    
    Config->>EnvFactory: create environment (seed)
    EnvFactory-->>Config: dm_env.Environment
    Config->>Config: make_environment_spec()
    Config->>NetFactory: create networks (environment_spec)
    NetFactory-->>Config: Networks
    Config->>Builder: make_policy(networks, environment_spec, evaluation=False)
    Builder-->>Config: Policy
    Config->>Builder: make_replay_tables(environment_spec, policy)
    Builder-->>Config: reverb.Tables
    Config->>Builder: make_dataset_iterator(replay_client)
    Builder-->>Config: Iterator
    Config->>Builder: make_learner(networks, iterator, ...)
    Builder-->>Config: Learner
    Config->>Builder: make_adder(replay_client, environment_spec, policy)
    Builder-->>Config: Adder  
    Config->>Builder: make_actor(policy, environment_spec, variable_source, adder)
    Builder-->>Config: Actor
```

This composition flow in [acme/jax/experiments/run_experiment.py:49-106]() ensures that components are created in the correct dependency order, with each component receiving the dependencies it requires.

Sources: [acme/jax/experiments/run_experiment.py:49-106](), [acme/jax/experiments/config.py:278-312]()

---

