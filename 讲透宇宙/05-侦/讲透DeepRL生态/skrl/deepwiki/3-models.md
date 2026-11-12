> 来源: [https://deepwiki.com/Toni-SM/skrl/3-models](https://deepwiki.com/Toni-SM/skrl/3-models)
> DeepWiki Toni-SM/skrl | Last indexed: 17 August 2026 (3cdc7f

# Models

  Relevant source files 
 - [skrl/memories/jax/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/__init__.py)
 - [skrl/memories/jax/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/base.py)
 - [skrl/memories/jax/random.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/random.py)
 - [skrl/memories/torch/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py)
 - [skrl/memories/torch/random.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/random.py)
 - [skrl/memories/warp/random.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/warp/random.py)
 - [skrl/models/jax/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/__init__.py)
 - [skrl/models/jax/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/base.py)
 - [skrl/models/torch/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/base.py)
 - [skrl/models/torch/categorical.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/categorical.py)
 - [skrl/models/torch/deterministic.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/deterministic.py)
 - [skrl/models/torch/gaussian.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/gaussian.py)
 - [skrl/models/torch/multivariate_gaussian.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/multivariate_gaussian.py)
 
  Models in **skrl** are neural network-based function approximators that represent policies, value functions, and other decision-making components used by reinforcement learning agents. The model system provides a flexible architecture supporting **PyTorch**, **JAX**, and **Warp** backends, with a mixin-based design that allows users to combine different action space behaviors with custom network architectures.

 For information about how models are used within RL agents, see [Agents](https://deepwiki.com/Toni-SM/skrl/2-agents). For details about training these models, see [Trainers](https://deepwiki.com/Toni-SM/skrl/5-trainers).

 
## Architecture Overview

 The model system is built around a dual-backend architecture with base classes and behavioral mixins that can be composed to create models for different action spaces and domains.

 
```

```

 Sources: [skrl/models/torch/base.py15-30](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/base.py#L15-L30) [skrl/models/jax/base.py40-64](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/base.py#L40-L64) [skrl/models/torch/gaussian.py15-26](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/gaussian.py#L15-L26) [skrl/models/torch/categorical.py13-21](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/categorical.py#L13-L21)

 
## Model Base Classes

 The foundation of the model system consists of backend-specific base classes that provide common functionality for neural network operations, device management, and state handling.

 
### PyTorch Base Class

 The PyTorch `Model` class extends `torch.nn.Module` and introduces high-level methods for RL workflows, such as `init_state_dict` for lazy modules [skrl/models/torch/base.py42-58](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/base.py#L42-L58) and `update_parameters` for Polyak averaging [skrl/models/torch/base.py419](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/base.py#L419-L419) It manages observation and action space metadata to ensure compatibility with environments [skrl/models/torch/base.py35-40](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/base.py#L35-L40)

 For details, see [Model Base Classes](https://deepwiki.com/Toni-SM/skrl/3.1-model-base-classes).

 
### JAX Base Class

 The JAX `Model` class extends `flax.linen.Module` [skrl/models/jax/base.py40](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/base.py#L40-L40) Because JAX is functional, it uses a `StateDict` [skrl/models/jax/base.py31-37](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/base.py#L31-L37) to store `apply_fn` and `params`. It supports distributed operations like `reduce_parameters` [skrl/models/jax/base.py419](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/base.py#L419-L419) and `broadcast_parameters` [skrl/models/jax/base.py419](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/base.py#L419-L419)

 For details, see [Model Base Classes](https://deepwiki.com/Toni-SM/skrl/3.1-model-base-classes).

 
## Model Mixins System

 Mixins provide standardized implementations for different action types. By inheriting from both a `Model` base class and a `Mixin`, users can define the network architecture in `compute()` while the mixin handles the RL-specific `act()` logic.

 
### Mixin Inheritance Pattern

 
```

```

 Sources: [skrl/models/torch/gaussian.py15-60](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/gaussian.py#L15-L60) [skrl/models/torch/base.py15-30](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/base.py#L15-L30)

 
### Available Mixins

 
 - **GaussianMixin**: For continuous actions using a Normal distribution [skrl/models/torch/gaussian.py15-60](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/gaussian.py#L15-L60)
 - **DeterministicMixin**: For deterministic continuous actions, often used in DDPG/TD3 or Value functions [skrl/models/torch/deterministic.py10-20](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/deterministic.py#L10-L20)
 - **CategoricalMixin**: For discrete actions using a Categorical distribution [skrl/models/torch/categorical.py13-23](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/categorical.py#L13-L23)
 - **MultivariateGaussianMixin**: For continuous actions with multivariate normal distributions [skrl/models/torch/multivariate_gaussian.py15-46](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/multivariate_gaussian.py#L15-L46)
 
 For details, see [Model Mixins](https://deepwiki.com/Toni-SM/skrl/3.2-model-mixins).

 
## Model Instantiators

 The instantiator system allows for the dynamic creation of models from configuration dictionaries or simple helper functions. This is particularly useful for standard architectures like MLPs or CNNs without writing boilerplate class definitions.

 For details, see [Model Instantiators](https://deepwiki.com/Toni-SM/skrl/3.3-model-instantiators).

 
## Integration with Agents and Memory

 Models are the primary interface for agents to interact with the environment. Agents use the `act()` method provided by mixins to generate actions [skrl/models/torch/gaussian.py62-111](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/gaussian.py#L62-L111) The results, including metadata like `log_prob` or `log_std`, are then stored in `Memory` objects [skrl/memories/torch/base.py20-48](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L20-L48)

 
```

```

 Sources: [skrl/models/torch/gaussian.py62-111](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/gaussian.py#L62-L111) [skrl/memories/torch/base.py121-171](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L121-L171)
