> 来源: [https://deepwiki.com/facebookresearch/ReAgent/7-model-serving](https://deepwiki.com/facebookresearch/ReAgent/7-model-serving)
> DeepWiki facebookresearch/ReAgent | Last indexed: 21 April 2025 (9e707c

# Model Serving

  Relevant source files 
 - [reagent/gym/tests/configs/recsim/slate_q_recsim_online_multi_selection.yaml](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/configs/recsim/slate_q_recsim_online_multi_selection.yaml)
 - [reagent/gym/tests/configs/recsim/slate_q_recsim_online_multi_selection_avg_curr.yaml](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/configs/recsim/slate_q_recsim_online_multi_selection_avg_curr.yaml)
 - [reagent/gym/tests/preprocessors/test_default_preprocessors.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/preprocessors/test_default_preprocessors.py)
 - [reagent/gym/tests/preprocessors/test_replay_buffer_inserters.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/preprocessors/test_replay_buffer_inserters.py)
 - [reagent/prediction/predictor_wrapper.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py)
 - [reagent/preprocessing/batch_preprocessor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/preprocessing/batch_preprocessor.py)
 - [reagent/test/base/test_utils.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/base/test_utils.py)
 - [reagent/test/models/test_actor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_actor.py)
 - [reagent/test/models/test_bcq.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_bcq.py)
 - [reagent/test/models/test_no_soft_update_embedding.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_no_soft_update_embedding.py)
 - [reagent/test/models/test_residual_wrapper.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_residual_wrapper.py)
 - [reagent/test/net_builder/test_synthetic_reward_net_builder.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/net_builder/test_synthetic_reward_net_builder.py)
 - [reagent/test/prediction/test_model_with_preprocessor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/prediction/test_model_with_preprocessor.py)
 - [reagent/test/prediction/test_predictor_wrapper.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/prediction/test_predictor_wrapper.py)
 - [reagent/test/preprocessing/test_postprocessing.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/preprocessing/test_postprocessing.py)
 - [reagent/test/preprocessing/test_preprocessing.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/preprocessing/test_preprocessing.py)
 - [reagent/training/slate_q_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/slate_q_trainer.py)
 
  This page documents ReAgent's model serving system, which enables efficient deployment of trained reinforcement learning models to production environments. The model serving system provides standardized interfaces for converting trained models into optimized prediction modules with appropriate preprocessing and postprocessing logic. For training models, see [Training System](https://deepwiki.com/facebookresearch/ReAgent/4-training-system), and for model evaluation, see [Evaluation](https://deepwiki.com/facebookresearch/ReAgent/8-evaluation).

 
## Overview

 The model serving system bridges the gap between ReAgent's training infrastructure and production deployment by providing a unified interface for model inference. It addresses key challenges, including:

 
 - Handling preprocessing of raw feature inputs
 - Optimizing models for efficient inference
 - Providing standardized interfaces for different model types
 - Supporting traceability and reproducibility in production
 
 
```

```

 Sources:

 
 - [reagent/prediction/predictor_wrapper.py1-876](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L1-L876)
 - [reagent/test/prediction/test_predictor_wrapper.py1-444](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/prediction/test_predictor_wrapper.py#L1-L444)
 
 
## Serving Architecture

 The model serving system consists of three primary components:

 
 - **Model with Preprocessor**: Combines a trained model with preprocessing logic to handle raw input feature transformation
 - **Predictor Wrapper**: Wraps the model with preprocessor to provide a standardized interface for prediction
 - **Optimized Served Model**: The final production-ready model created using PyTorch's JIT (Just-In-Time) compilation
 
 
```

```

 Sources:

 
 - [reagent/prediction/predictor_wrapper.py28-92](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L28-L92)
 - [reagent/prediction/predictor_wrapper.py94-129](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L94-L129)
 - [reagent/prediction/predictor_wrapper.py131-150](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L131-L150)
 
 
## Model with Preprocessor Classes

 ReAgent provides different "Model with Preprocessor" classes depending on the type of RL algorithm:

 
| Model Type | Model with Preprocessor Class | Purpose |
|---|---|---|
| Discrete DQN | DiscreteDqnWithPreprocessor | Handles state preprocessing for Q-networks with discrete action spaces |
| Parametric DQN | ParametricDqnWithPreprocessor | Handles both state and action preprocessing for parametric Q-networks |
| Actor | ActorWithPreprocessor | Handles state preprocessing for policy networks (actors) |
| Ranking Actor | RankingActorWithPreprocessor | Specialized actor for ranking use cases |
| Seq2Slate | Seq2SlateWithPreprocessor | For sequence-to-slate models used in ranking/recommendation |
| Seq2Reward | Seq2RewardWithPreprocessor | For reward prediction models |

 These classes follow a similar pattern:

 
 - They accept a model and necessary preprocessors in the constructor
 - They implement a `forward()` method that: 
 - Preprocesses input data
 - Passes preprocessed data to the model
 - Returns model predictions
 - They provide an `input_prototype()` method for generating example inputs
 
 Sources:

 
 - [reagent/prediction/predictor_wrapper.py94-129](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L94-L129)
 - [reagent/prediction/predictor_wrapper.py248-274](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L248-L274)
 - [reagent/prediction/predictor_wrapper.py301-349](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L301-L349)
 - [reagent/prediction/predictor_wrapper.py376-418](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L376-L418)
 - [reagent/prediction/predictor_wrapper.py547-609](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L547-L609)
 - [reagent/prediction/predictor_wrapper.py644-691](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L644-L691)
 
 
## Predictor Wrapper Classes

 Each "Model with Preprocessor" is paired with a corresponding Predictor Wrapper class that provides a standardized interface for inference. These wrapper classes are optimized for production using PyTorch's JIT capabilities:

 
| Model Type | Predictor Wrapper Class | Returns |
|---|---|---|
| Discrete DQN | DiscreteDqnPredictorWrapper | Action names and Q-values |
| Parametric DQN | ParametricDqnPredictorWrapper | Q-value for given state-action pair |
| Actor | ActorPredictorWrapper | Action and log probability |
| Ranking Actor | RankingActorPredictorWrapper | Ranked action |
| Seq2Slate | Seq2SlatePredictorWrapper | Sequence probabilities and target indices |
| Binary Classifier | BinaryDifferenceScorerPredictorWrapper | Probability score |

 
```

```

 Sources:

 
 - [reagent/prediction/predictor_wrapper.py131-150](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L131-L150)
 - [reagent/prediction/predictor_wrapper.py283-298](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L283-L298)
 - [reagent/prediction/predictor_wrapper.py352-373](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L352-L373)
 - [reagent/prediction/predictor_wrapper.py427-449](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L427-L449)
 - [reagent/prediction/predictor_wrapper.py612-640](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L612-L640)
 - [reagent/prediction/predictor_wrapper.py216-230](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L216-L230)
 
 
## Feature Handling and Input Formats

 The model serving system handles various input feature types:

 
### ServingFeatureData

 The standard input format for model serving is `ServingFeatureData`, which consists of:

 
 - **float_features_with_presence**: Tuple of (feature values, presence indicators)
 - **id_list_features**: Dictionary mapping feature IDs to a tuple of (indices, offsets)
 - **id_score_list_features**: Dictionary mapping feature IDs to a tuple of (indices, offsets, scores)
 
 These inputs are converted to `FeatureData` using the `serving_to_feature_data` function before being passed to models:

 
```

```

 Sources:

 
 - [reagent/prediction/predictor_wrapper.py47-59](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L47-L59)
 - [reagent/prediction/predictor_wrapper.py62-91](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L62-L91)
 
 
## Optimization with PyTorch JIT

 The model serving system uses PyTorch's JIT capabilities to optimize models for production:

 
 - **Tracing**: Most models use `torch.jit.trace` for optimization, which requires an input prototype
 - **Scripting**: For models with control flow (like some `Seq2Slate` variants), `torch.jit.script` is used
 
 
```

```

 Sources:

 
 - [reagent/prediction/predictor_wrapper.py140-142](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L140-L142)
 - [reagent/prediction/predictor_wrapper.py615-623](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L615-L623)
 - [reagent/prediction/predictor_wrapper.py597-609](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L597-L609)
 
 
## Special Case: Seq2Slate Models

 Seq2Slate models require special handling due to their complex nature:

 
 - **Input Processing**: Converts state and candidate features into a format suitable for ranking
 - **Output Architecture**: Supports different output architectures like FRECHET_SORT and AUTOREGRESSIVE
 - **Traceability**: Only certain configurations can be traced; others must be scripted
 
 
```

```

 Sources:

 
 - [reagent/prediction/predictor_wrapper.py547-609](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L547-L609)
 - [reagent/prediction/predictor_wrapper.py612-640](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L612-L640)
 - [reagent/test/prediction/test_predictor_wrapper.py237-311](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/prediction/test_predictor_wrapper.py#L237-L311)
 
 
## Usage in ModelManager System

 The model serving components are typically used as part of the ModelManager workflow:

 
```

```

 Sources:

 
 - [reagent/prediction/predictor_wrapper.py1-876](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L1-L876)
 - [reagent/test/prediction/test_predictor_wrapper.py1-444](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/prediction/test_predictor_wrapper.py#L1-L444)
 
 
## Unwrapper Classes for Deployment

 ReAgent provides special "unwrapper" classes that handle the transition between framework-specific input formats and the standardized format used by the predictor wrappers:

 
 - **OSSSparsePredictorUnwrapper**: Adapts inputs for sparse models
 - **OSSPredictorUnwrapper**: Generic adapter for any predictor wrapper
 - **Aliases**: `DiscreteDqnPredictorUnwrapper`, `ActorPredictorUnwrapper`, etc.
 
 These classes make it easier to integrate ReAgent models into different serving systems.

 Sources:

 
 - [reagent/prediction/predictor_wrapper.py153-173](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L153-L173)
 - [reagent/prediction/predictor_wrapper.py234-245](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L234-L245)
 - [reagent/prediction/predictor_wrapper.py243-245](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/prediction/predictor_wrapper.py#L243-L245)
 
 
## Testing and Validation

 The model serving system includes comprehensive testing to ensure that:

 
 - Models behave the same way in training and serving
 - JIT optimization preserves model behavior
 - Input and output formats are consistent
 
 The test suite validates all supported model types under various conditions, including:

 
 - Different feature types (dense, sparse)
 - Variable-length inputs (especially for sequence models)
 - Different optimization strategies (tracing vs scripting)
 
 Sources:

 
 - [reagent/test/prediction/test_predictor_wrapper.py60-443](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/prediction/test_predictor_wrapper.py#L60-L443)
 - [reagent/test/prediction/test_model_with_preprocessor.py20-84](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/prediction/test_model_with_preprocessor.py#L20-L84)
 
 
## Conclusion

 ReAgent's model serving system provides a robust, flexible framework for deploying reinforcement learning models to production. By standardizing interfaces and handling the complexities of preprocessing and optimization, it enables seamless transition from training to serving.

 For more information about related components, refer to:

 
 - [Predictor Wrappers](https://deepwiki.com/facebookresearch/ReAgent/7.1-predictor-wrappers) - Detailed information about specific predictor wrapper implementations
 - [Training System](https://deepwiki.com/facebookresearch/ReAgent/4-training-system) - The system that produces trainable models
 - [Evaluation](https://deepwiki.com/facebookresearch/ReAgent/8-evaluation) - How to evaluate model performance
