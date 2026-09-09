> 来源: [https://deepwiki.com/facebookresearch/ReAgent/2-core-data-structures](https://deepwiki.com/facebookresearch/ReAgent/2-core-data-structures)
> DeepWiki facebookresearch/ReAgent | Last indexed: 21 April 2025 (9e707c

# Core Data Structures

  Relevant source files 
 - [reagent/core/types.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py)
 - [reagent/gym/tests/configs/recsim/slate_q_recsim_online_multi_selection.yaml](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/configs/recsim/slate_q_recsim_online_multi_selection.yaml)
 - [reagent/gym/tests/configs/recsim/slate_q_recsim_online_multi_selection_avg_curr.yaml](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/configs/recsim/slate_q_recsim_online_multi_selection_avg_curr.yaml)
 - [reagent/models/embedding_bag_concat.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/embedding_bag_concat.py)
 - [reagent/models/synthetic_reward_sparse_arch.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/synthetic_reward_sparse_arch.py)
 - [reagent/net_builder/synthetic_reward/single_step_synthetic_reward_sparse_arch.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/net_builder/synthetic_reward/single_step_synthetic_reward_sparse_arch.py)
 - [reagent/prediction/predictor_wrapper.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py)
 - [reagent/preprocessing/batch_preprocessor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/preprocessing/batch_preprocessor.py)
 - [reagent/preprocessing/transforms.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/preprocessing/transforms.py)
 - [reagent/preprocessing/types.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/preprocessing/types.py)
 - [reagent/test/core/test_utils.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/core/test_utils.py)
 - [reagent/test/net_builder/test_discrete_dqn_net_builder.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/net_builder/test_discrete_dqn_net_builder.py)
 - [reagent/test/preprocessing/test_transforms.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/preprocessing/test_transforms.py)
 - [reagent/training/slate_q_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/slate_q_trainer.py)
 
  This document describes the fundamental data structures used throughout the ReAgent reinforcement learning framework. These core data types serve as the building blocks for representing states, actions, features, and other elements in reinforcement learning workflows.

 For information about model inputs and outputs, see [Model Inputs and Outputs](https://deepwiki.com/facebookresearch/ReAgent/2.2-model-inputs-and-outputs). For details on feature preprocessing, see [Feature Data and Preprocessing](https://deepwiki.com/facebookresearch/ReAgent/2.1-feature-data-and-preprocessing).

 
## Base Data Classes

 ReAgent builds on PyTorch tensors with additional functionality tailored for reinforcement learning. The framework provides base classes that wrap tensors with reinforcement learning semantics and operations.

 
### TensorDataClass

 `TensorDataClass` is a foundational class that extends PyTorch's tensor operations to dataclasses. It enables seamless application of tensor operations to structured data objects, allowing operations like `cuda()`, `cpu()`, and other tensor methods to be called on dataclass instances.

 
```

```

 Key capabilities of `TensorDataClass`:

 
 - Dynamically forwards PyTorch tensor operations to all tensor attributes
 - Handles device placement (CPU/GPU) for nested tensor structures
 - Preserves dataclass structure when operations are applied
 
 Sources: [reagent/core/types.py50-110](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L50-L110)

 
### ValuePresence

 `ValuePresence` is a simple dataclass that pairs a tensor value with a presence mask tensor. This pattern is used throughout ReAgent to handle missing or masked values.

 
```

```

 Sources: [reagent/core/types.py240-244](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L240-L244)

 
## Feature Representation

 
### Feature Data Types

 ReAgent uses several specific types to represent different kinds of feature data:

 
| Feature Type | Description | Structure |
|---|---|---|
| Dense Features | Continuous or categorical features represented as dense tensors | torch.Tensor with shape [batch_size, feature_dim] |
| ID List Features | Sparse features represented as lists of IDs | Tuple[torch.Tensor, torch.Tensor] representing offsets and values |
| ID Score List Features | Sparse features with importance weights | Tuple[torch.Tensor, torch.Tensor, torch.Tensor] representing offsets, IDs, and weights |

 These types are combined into more complex data structures for model inputs.

 
```

```

 Sources: [reagent/core/types.py112-121](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L112-L121) [reagent/core/types.py314-350](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L314-L350)

 
### FeatureData

 The `FeatureData` class is the central structure for representing input features in ReAgent. It combines dense, sparse, and document features in a single object:

 
```

```

 Key components:

 
 - `float_features`: Dense features with shape `[batch_size, feature_dim]`
 - `id_list_features`/`id_score_list_features`: Sparse features in `KeyedJaggedTensor` format
 - `id_list_features_raw`/`id_score_list_features_raw`: Sparse features in raw dictionary format
 - `candidate_docs`: Document features for ranking systems
 - `time_since_first`: Timing information for sequential models
 
 Sources: [reagent/core/types.py314-388](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L314-L388)

 
### DocList

 `DocList` is specialized for ranking and recommendation use cases, representing a slate of candidate documents:

 
```

```

 Sources: [reagent/core/types.py254-286](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L254-L286)

 
### ServingFeatureData

 For model serving purposes, ReAgent uses `ServingFeatureData` which organizes features by their type:

 
```

```

 Sources: [reagent/core/types.py435-439](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L435-L439) [reagent/prediction/predictor_wrapper.py47-59](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L47-L59)

 
## Feature Configuration

 ReAgent uses several configuration classes to define feature characteristics for models.

 
### Feature Configuration Classes

 
| Configuration Class | Purpose |
|---|---|
| FloatFeatureInfo | Defines a dense feature with a name and ID |
| IdListFeatureConfig | Defines an ID list feature with name, ID, and embedding table |
| IdScoreListFeatureConfig | Defines an ID-score list feature with name, ID, and embedding table |
| IdMappingConfig | Configures an embedding table with size, dimension, and pooling |
| ModelFeatureConfig | Aggregates all feature configurations for a model |

 
```

```

 Sources: [reagent/core/types.py130-232](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L130-L232) [reagent/test/core/test_utils.py18-116](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/core/test_utils.py#L18-L116)

 
## Input Data Structures

 ReAgent defines a hierarchy of input data structures for different model types.

 
### BaseInput

 `BaseInput` is the common base class for most model inputs, containing state, next state, reward, and transition information:

 
```

```

 Sources: [reagent/core/types.py692-772](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L692-L772)

 
### Model-Specific Input Types

 ReAgent provides specialized input types for different reinforcement learning algorithms:

 
```

```

 Various specialized input types include:

 
 - **DiscreteDqnInput** - For discrete action spaces using DQN
 - **ParametricDqnInput** - For parametric/continuous action spaces
 - **PolicyNetworkInput** - For policy-based methods
 - **SlateQInput** - For slate-based recommendation
 - **PolicyGradientInput** - For policy gradient methods
 - **PreprocessedRankingInput** - For ranking models
 
 Sources: [reagent/core/types.py776-1035](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L776-L1035) [reagent/test/net_builder/test_discrete_dqn_net_builder.py18-33](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/net_builder/test_discrete_dqn_net_builder.py#L18-L33)

 
### Ranking-Specific Structures

 For ranking and recommendation tasks, ReAgent provides specialized data structures:

 
 - **DocList** - Represents a collection of candidate documents
 - **PreprocessedRankingInput** - Specialized input for sequence-to-slate models
 
 Sources: [reagent/core/types.py254-286](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L254-L286) [reagent/core/types.py455-673](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L455-L673) [reagent/training/slate_q_trainer.py107-146](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/slate_q_trainer.py#L107-L146)

 
## Batch Processing and Transformations

 
### Batch Preprocessors

 ReAgent includes batch preprocessors that convert raw batch data into structured input formats:

 
```

```

 The batch preprocessors convert raw data dictionaries into structured input classes, handling tensor device placement and preprocessing operations.

 Sources: [reagent/preprocessing/batch_preprocessor.py15-157](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/preprocessing/batch_preprocessor.py#L15-L157)

 
### Feature Transforms

 ReAgent provides a rich set of transformations for preprocessing features:

 
| Transform | Purpose |
|---|---|
| Compose | Apply multiple transforms sequentially |
| ValuePresence | Extract value-presence pairs from data |
| DenseNormalization | Normalize dense features |
| IDListFeatures | Process ID list features into KeyedJaggedTensor |
| IDScoreListFeatures | Process ID-score list features into KeyedJaggedTensor |
| OneHotActions | Convert action indices to one-hot vectors |
| SlateView | Reshape flattened slates into batch × slate_size × feature_dim |

 The transformation system is flexible and extensible, allowing for custom preprocessing pipelines to be constructed.

 Sources: [reagent/preprocessing/transforms.py22-865](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/preprocessing/transforms.py#L22-L865) [reagent/test/preprocessing/test_transforms.py63-866](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/preprocessing/test_transforms.py#L63-L866)

 
## Feature Embedding Integration

 ReAgent provides integration with embedding tables through specialized models and structures.

 
### EmbeddingBagConcat

 `EmbeddingBagConcat` handles sparse feature embedding by:

 
 - Looking up sparse feature embeddings in embedding tables
 - Pooling embedding vectors per feature
 - Concatenating with dense features
 
 This is particularly useful for models that need to handle both dense and sparse features.

 
```

```

 Sources: [reagent/models/embedding_bag_concat.py15-126](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/embedding_bag_concat.py#L15-L126)

 
## Data Flow In ReAgent

 This diagram illustrates how the core data structures are used in the overall flow of data through the ReAgent system:

 
```

```

 This flow highlights how data moves from raw inputs through preprocessing, into the core data structures, through models, and finally to serving outputs.

 Sources: [reagent/core/types.py47-59](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L47-L59) [reagent/prediction/predictor_wrapper.py47-1008](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L47-L1008)

 
## Key Data Types Summary

 The following table summarizes the most important data structures and their roles:

 
| Data Structure | Purpose | Key Applications |
|---|---|---|
| FeatureData | Container for all feature types | Model inputs, feature preprocessing |
| BaseInput | Base for RL input types | Foundation for all model-specific inputs |
| DocList | Document/item representation | Ranking and recommendation models |
| ServingFeatureData | Feature format for serving | Model deployment and inference |
| ModelFeatureConfig | Feature configuration | Model building and feature preprocessing |
| TensorDataClass | Base for tensor operations | Underlying implementation of data classes |

 Sources: [reagent/core/types.py50-1034](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/core/types.py#L50-L1034)

 
## Conclusion

 The core data structures in ReAgent provide a robust foundation for representing features, states, actions, and other elements in reinforcement learning workflows. They enable seamless integration between different components of the system, from data preprocessing to model training and serving.

 These structures balance flexibility with strong typing, allowing ReAgent to support diverse reinforcement learning algorithms while maintaining a consistent interface across the system.
