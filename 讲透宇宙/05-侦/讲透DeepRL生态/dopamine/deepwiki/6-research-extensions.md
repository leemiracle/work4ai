> 来源: [https://deepwiki.com/google/dopamine/6-research-extensions](https://deepwiki.com/google/dopamine/6-research-extensions)
> DeepWiki google/dopamine | Last indexed: 18 April 2025 (bec5f4

# Research Extensions

  Relevant source files 
 - [dopamine/labs/atari_100k/README.md](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/README.md?plain=1)
 - [dopamine/labs/atari_100k/configs/DER.gin](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/configs/DER.gin)
 - [dopamine/labs/atari_100k/eval_run_experiment.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/eval_run_experiment.py)
 - [dopamine/labs/atari_100k/train.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/train.py)
 - [dopamine/labs/offline_rl/jax/configs/jax_classy_cql.gin](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/configs/jax_classy_cql.gin)
 - [dopamine/labs/offline_rl/jax/networks.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py)
 - [dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py)
 - [dopamine/labs/offline_rl/jax/train.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/train.py)
 - [dopamine/labs/offline_rl/rlu_tfds/tfds_atari_utils.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/rlu_tfds/tfds_atari_utils.py)
 - [tests/dopamine/labs/atari_100k/train_test.py](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/labs/atari_100k/train_test.py)
 - [tests/dopamine/labs/offline_rl/jax/offline_agent_test.py](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/labs/offline_rl/jax/offline_agent_test.py)
 
  This document provides an overview of the specialized research components and experimental extensions available in the Dopamine framework. These extensions build upon the core reinforcement learning functionality to address specific research challenges and incorporate recent advances in the field.

 For information about the core agent implementations, see [Agent Implementations](https://deepwiki.com/google/dopamine/2-agent-implementations). For experiment running basics, see [Experiment Running](https://deepwiki.com/google/dopamine/4-experiment-running).

 
## Atari 100k Benchmark

 The Atari 100k benchmark evaluates agents after training on only 100k environment steps (400k frames of interaction), representing a more data-efficient evaluation protocol compared to the traditional 200M frames used in standard Atari benchmarks. This benchmark was introduced in the "Model-based Reinforcement Learning for Atari" paper by Kaiser et al. (2019) and has become a standard for evaluating data-efficient RL algorithms.

 Dopamine provides implementations of several state-of-the-art agents for this benchmark:

 
```

```

 Sources: [dopamine/labs/atari_100k/README.md](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/README.md?plain=1) [dopamine/labs/atari_100k/train.py38-43](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/train.py#L38-L43) [dopamine/labs/atari_100k/train.py70-87](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/train.py#L70-L87)

 
### Agent Variants

 
 - **DER (Data Efficient Rainbow)**: An optimized Rainbow agent with parameter settings designed for sample efficiency.
 - **OTRainbow (Over-trained Rainbow)**: Based on Kielak (2020), this agent uses longer training on a limited amount of data.
 - **DrQ (Data-regularized Q)**: Incorporates image augmentation as a regularization technique to improve sample efficiency.
 - **DrQ(ε)**: A variant of DrQ with modified exploration strategy as described in Agarwal et al. (2021).
 - **SPR (Self-Predictive Representations)**: Uses self-supervised representation learning to improve sample efficiency.
 
 All Atari 100k agents are built upon the `JaxFullRainbowAgent` with specific optimizations for data efficiency.

 Sources: [dopamine/labs/atari_100k/README.md7-11](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/README.md?plain=1#L7-L11) [dopamine/labs/atari_100k/train.py70-75](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/train.py#L70-L75)

 
### Evaluation Method

 The Atari 100k benchmark uses a specialized evaluation runner that differs from the standard evaluation in Dopamine:

 
 - **MaxEpisodeEvalRunner**: Evaluates agents based on a fixed number of episodes rather than a fixed number of steps.

 
 - Uses 100 evaluation episodes by default
 - Incorporates random no-op starts for evaluation
 - **DataEfficientAtariRunner**: A more optimized runner that ensures precise training step counts and parallel evaluation for faster runs.
 
 Sources: [dopamine/labs/atari_100k/eval_run_experiment.py26-127](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/eval_run_experiment.py#L26-L127) [dopamine/labs/atari_100k/train.py108-116](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/train.py#L108-L116)

 
### Usage

 To run an Atari 100k agent, use the entry point in `dopamine/labs/atari_100k/train.py` with the appropriate configuration file:

 
```
python -um dopamine.labs.atari_100k.train \
  --base_dir /tmp/dopamine_runs \
  --gin_files dopamine/labs/atari_100k/configs/DER.gin
```

 Agent configurations can be found in the `dopamine/labs/atari_100k/configs/` directory.

 Sources: [dopamine/labs/atari_100k/README.md17-25](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/README.md?plain=1#L17-L25) [dopamine/labs/atari_100k/train.py92-117](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/train.py#L92-L117)

 
## Offline Reinforcement Learning

 Offline RL (or batch RL) focuses on learning policies from fixed datasets of previously collected experiences without further environment interaction. This is particularly important for applications where online interaction is expensive, risky, or impractical.

 Dopamine's offline RL extensions provide implementations of several modern offline RL algorithms and components:

 
```

```

 Sources: [dopamine/labs/offline_rl/jax/train.py62-105](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/train.py#L62-L105) [dopamine/labs/offline_rl/jax/networks.py110-276](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py#L110-L276) [dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py208-240](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py#L208-L240)

 
### Agent Implementations

 
 - **OfflineJaxDQNAgent**: Basic DQN agent adapted for offline learning.
 - **OfflineJaxDR3Agent**: Incorporates DR3 (Decorrelate Representation via Regularized Optimization) for better representation learning in offline settings.
 - **OfflineJaxRainbowAgent**: Offline variant of the Rainbow agent.
 - **OfflineClassyCQLAgent**: Combines TD learning with behavioral cloning (similar to Conservative Q-Learning) and supports various distribution representation techniques:

 
 - Different target types: Q-learning, SARSA, or Monte Carlo returns
 - Various histogram loss functions: HL-Gauss, Two-hot, Binary cross-entropy, or Scalar Q-values
 - **JaxReturnConditionedBCAgent**: Behavioral cloning agent conditioned on expected returns.
 
 Sources: [dopamine/labs/offline_rl/jax/train.py79-88](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/train.py#L79-L88) [dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py208-314](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py#L208-L314) [tests/dopamine/labs/offline_rl/jax/offline_agent_test.py73-82](https://github.com/google/dopamine/blob/bec5f4e1/tests/dopamine/labs/offline_rl/jax/offline_agent_test.py#L73-L82)

 
### Replay System for Offline RL

 Offline RL requires loading pre-collected datasets, which Dopamine handles via:

 
 - **JaxFixedReplayBuffer**: Loads data from stored transitions.
 - **JaxFixedReplayBufferTFDS**: Integrates with TensorFlow Datasets (TFDS) to load standard offline RL datasets.
 - **RLU TFDS Utilities**: Helper functions for working with RL Unplugged datasets, particularly Atari datasets, including:

 
 - Converting episodes to transitions
 - Adding return-to-go calculations
 - Creating subsampled datasets
 - Batch processing utilities
 
 Sources: [dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py385-426](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py#L385-L426) [dopamine/labs/offline_rl/rlu_tfds/tfds_atari_utils.py21-188](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/rlu_tfds/tfds_atari_utils.py#L21-L188)

 
### Network Architectures for Offline RL

 
 - **ParameterizedRainbowNetwork**: A flexible network architecture supporting:

 
 - Distributional representations
 - Optional dueling architecture
 - Choice between CNN or IMPALA encoders
 - Return conditioning
 - **ImpalaEncoder**: An encoder architecture based on the IMPALA deep RL agent, featuring:

 
 - Stacked residual blocks
 - Scalable width parameter
 - Proper representation normalization
 
 Sources: [dopamine/labs/offline_rl/jax/networks.py110-276](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py#L110-L276) [dopamine/labs/offline_rl/jax/networks.py47-83](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py#L47-L83)

 
### Usage

 To run an offline RL experiment, use the entry point in `dopamine/labs/offline_rl/jax/train.py` with the appropriate configuration:

 
```
python -um dopamine.labs.offline_rl.jax.train \
  --base_dir /tmp/offline_dopamine_runs \
  --gin_files dopamine/labs/offline_rl/jax/configs/jax_classy_cql.gin \
  --agent_name jax_classy_cql \
  --replay_dir /path/to/dataset
```

 Sources: [dopamine/labs/offline_rl/jax/train.py92-154](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/train.py#L92-L154) [dopamine/labs/offline_rl/jax/configs/jax_classy_cql.gin](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/configs/jax_classy_cql.gin)

 
## Advanced Network Architectures

 Dopamine includes several advanced network architectures designed for reinforcement learning research:

 
```

```

 Sources: [dopamine/labs/offline_rl/jax/networks.py85-109](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py#L85-L109) [dopamine/labs/offline_rl/jax/networks.py110-132](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py#L110-L132) [dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py41-46](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py#L41-L46)

 
### Key Network Architectures

 
 - **CNNEncoder**: A standard convolutional encoder similar to the DQN network architecture:

 
 - Configurable channels, kernels, and strides
 - Scalable width parameter
 - **ImpalaEncoder**: An encoder architecture based on the IMPALA agent:

 
 - Stacked residual blocks with pooling
 - Better gradient flow for deep networks
 - Scalable width and depth parameters
 - **ParameterizedRainbowNetwork**: A flexible network combining various components:

 
 - Choice of encoder architecture
 - Optional distributional representation
 - Support for value transformation (histogram losses)
 - Return conditioning for return-based agents
 - **Distributional Representations**:

 
 - Gaussian histogram loss (HL_Gauss)
 - Two-hot encoding for improved value approximation
 - Binary cross-entropy losses
 - Standard scalar Q-values
 
 Sources: [dopamine/labs/offline_rl/jax/networks.py85-109](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py#L85-L109) [dopamine/labs/offline_rl/jax/networks.py110-132](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py#L110-L132) [dopamine/labs/offline_rl/jax/networks.py211-276](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/networks.py#L211-L276) [dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py41-46](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py#L41-L46) [dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py272-302](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py#L272-L302)

 
## Integration with Other Systems

 Dopamine's research extensions are designed to integrate with other machine learning frameworks and systems:

 
 - **TensorFlow Datasets (TFDS)**: Integration with TFDS for loading standard offline RL datasets, particularly from the RL Unplugged collection.
 - **JAX Optimization Libraries**: Uses JAX and Optax for efficient optimization and automatic differentiation.
 - **Gin Configuration**: All research extensions leverage Gin configuration for flexible hyperparameter tuning without code changes.
 - **Checkpoint and Logging System**: Integration with TensorBoard for tracking training progress and visualizing results.
 
 Sources: [dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py385-426](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/jax/offline_classy_cql_agent.py#L385-L426) [dopamine/labs/offline_rl/rlu_tfds/tfds_atari_utils.py101-165](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/offline_rl/rlu_tfds/tfds_atari_utils.py#L101-L165) [dopamine/labs/atari_100k/train.py92-116](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/atari_100k/train.py#L92-L116)

 
## Future Directions

 The research extensions in Dopamine continue to evolve with the field of reinforcement learning. Some areas of active development include:

 
 - **More Data-Efficient Algorithms**: Further improvements to sample efficiency in RL agents.
 - **Additional Offline RL Methods**: Implementations of newer offline RL algorithms as they are developed.
 - **Advanced Representation Learning**: Integration of more sophisticated representation learning techniques.
 - **Real-World Applications**: Extensions to handle more complex and realistic environments beyond Atari.
