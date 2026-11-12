> 来源: [https://deepwiki.com/facebookresearch/ReAgent/8-evaluation](https://deepwiki.com/facebookresearch/ReAgent/8-evaluation)
> DeepWiki facebookresearch/ReAgent | Last indexed: 21 April 2025 (9e707c

# Evaluation

  Relevant source files 
 - [reagent/evaluation/cb/base_evaluator.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/base_evaluator.py)
 - [reagent/evaluation/cb/policy_evaluator.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/policy_evaluator.py)
 - [reagent/evaluation/cb/utils.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/utils.py)
 - [reagent/evaluation/evaluation_data_page.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/evaluation_data_page.py)
 - [reagent/gym/policies/scorers/continuous_scorer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/policies/scorers/continuous_scorer.py)
 - [reagent/gym/tests/test_gym_replay_buffer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/gym/tests/test_gym_replay_buffer.py)
 - [reagent/models/__init__.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/__init__.py)
 - [reagent/models/seq2slate.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/seq2slate.py)
 - [reagent/net_builder/synthetic_reward_net_builder.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/net_builder/synthetic_reward_net_builder.py)
 - [reagent/preprocessing/identify_types.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/preprocessing/identify_types.py)
 - [reagent/test/evaluation/cb/test_integration.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/evaluation/cb/test_integration.py)
 - [reagent/test/evaluation/cb/test_policy_evaluator.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/evaluation/cb/test_policy_evaluator.py)
 - [reagent/test/evaluation/cb/test_utils.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/evaluation/cb/test_utils.py)
 - [reagent/test/models/test_disjoint_linucb_predictor.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_disjoint_linucb_predictor.py)
 - [reagent/test/models/test_mab.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_mab.py)
 - [reagent/training/c51_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/c51_trainer.py)
 - [reagent/training/cfeval/bayes_by_backprop_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/cfeval/bayes_by_backprop_trainer.py)
 - [reagent/training/discrete_crr_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/discrete_crr_trainer.py)
 - [reagent/training/dqn_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer.py)
 - [reagent/training/dqn_trainer_base.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py)
 - [reagent/training/multi_stage_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/multi_stage_trainer.py)
 - [reagent/training/qrdqn_trainer.py](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/qrdqn_trainer.py)
 
  This page documents the evaluation system in ReAgent, which provides mechanisms to assess model performance both during training and offline. This system is particularly focused on off-policy evaluation techniques for reinforcement learning and contextual bandits algorithms. For information about training workflows, see [Training System](https://deepwiki.com/facebookresearch/ReAgent/4-training-system).

 
## Overview of the Evaluation System

 ReAgent's evaluation system provides capabilities to measure the performance of policies without deploying them in real environments. This is crucial for safe deployment of RL systems, especially in high-stakes scenarios where deploying suboptimal policies can be costly.

 The evaluation system supports:

 
 - **Counterfactual Policy Evaluation (CPE)** - Evaluating a policy using historical data collected by a different policy
 - **Offline Evaluation** - Assessing policy performance without additional environment interaction
 - **Integrated Metrics** - Collecting relevant metrics during training for model improvement
 
 
```

```

 Sources:

 
 - [reagent/training/dqn_trainer_base.py81-106](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py#L81-L106)
 - [reagent/training/dqn_trainer_base.py455-510](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py#L455-L510)
 - [reagent/evaluation/cb/policy_evaluator.py16-166](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/policy_evaluator.py#L16-L166)
 
 
## Evaluation Data Structure

 The central data structure for evaluation is `EvaluationDataPage`, which contains all necessary information for policy evaluation:

 
```

```

 This data structure captures both:

 
 - The **historical data** (logged actions, rewards, propensities)
 - The **model predictions** (what the model would have done in the same situation)
 
 The `EvaluationDataPage` is created during model validation steps and is algorithm-specific, with dedicated creation methods for different algorithms such as `create_from_tensors_dqn()`, `create_from_tensors_parametric_dqn()`, and `create_from_tensors_seq2slate()`.

 Sources:

 
 - [reagent/evaluation/evaluation_data_page.py30-648](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/evaluation_data_page.py#L30-L648)
 
 
## Counterfactual Policy Evaluation

 Counterfactual Policy Evaluation (CPE) is integrated into the DQN training system via the `DQNTrainerBaseLightning` class. CPE works by training separate networks specifically for evaluation purposes:

 
```

```

 Key CPE functionality:

 
 - **Initialization**: The `_initialize_cpe()` method sets up networks specifically for evaluation.
 - **Calculation**: The `_calculate_cpes()` method computes evaluation metrics using these networks.
 - **Optimization**: The CPE networks are trained alongside the main policy network.
 
 Sources:

 
 - [reagent/training/dqn_trainer_base.py244-332](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py#L244-L332)
 - [reagent/training/dqn_trainer_base.py333-454](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py#L333-L454)
 - [reagent/training/dqn_trainer.py109-111](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer.py#L109-L111)
 
 
## Training Integration

 Evaluation is seamlessly integrated into the training process through the PyTorch Lightning framework. The key integration points are:

 
 - **Validation Step**: Creates `EvaluationDataPage` objects from validation batches
 - **Gather Eval Data**: Aggregates evaluation data from multiple validation steps
 - **Validation Epoch End**: Conducts final evaluation at the end of an epoch
 
 
```

```

 This integration allows for continuous evaluation during training without impacting the training process itself.

 Sources:

 
 - [reagent/training/dqn_trainer_base.py486-511](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py#L486-L511)
 - [reagent/training/dqn_trainer_base.py455-485](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer_base.py#L455-L485)
 - [reagent/training/dqn_trainer.py363-380](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer.py#L363-L380)
 
 
## Offline Evaluation for Contextual Bandits

 ReAgent provides specialized support for offline evaluation of contextual bandit policies through the `PolicyEvaluator` class, which inherits from `BaseOfflineEval`.

 
```

```

 The offline evaluation process for contextual bandits works as follows:

 
 - **Ingesting Data**: The `ingest_batch()` method processes a batch of data, comparing model actions with logged actions.
 - **Computing Importance Weights**: For actions where the model's choice matches the logged action, we apply importance weighting.
 - **Aggregating Results**: The `_aggregate_across_instances()` method combines results across training instances.
 - **Reporting Metrics**: The `log_metrics()` method reports evaluation metrics like average reward.
 
 Sources:

 
 - [reagent/evaluation/cb/base_evaluator.py16-248](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/base_evaluator.py#L16-L248)
 - [reagent/evaluation/cb/policy_evaluator.py16-166](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/policy_evaluator.py#L16-L166)
 - [reagent/evaluation/cb/utils.py9-47](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/utils.py#L9-L47)
 
 
## Evaluation in Different Algorithms

 ReAgent implements evaluation differently across various algorithms:

 
### DQN and Variants

 DQN-based algorithms use the `DQNTrainerBaseLightning` class for evaluation. They create evaluation data through `create_from_tensors_dqn()` which calculates:

 
 - Model action probabilities
 - Estimated Q-values
 - Reward estimates
 
 Key algorithms with integrated evaluation:

 
 - Standard DQN
 - Quantile Regression DQN (QR-DQN)
 - Categorical DQN (C51)
 - Discrete CRR (Critic Regularized Regression)
 
 Sources:

 
 - [reagent/training/dqn_trainer.py363-380](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/dqn_trainer.py#L363-L380)
 - [reagent/training/qrdqn_trainer.py168-228](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/qrdqn_trainer.py#L168-L228)
 - [reagent/training/c51_trainer.py100-194](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/c51_trainer.py#L100-L194)
 - [reagent/training/discrete_crr_trainer.py407-441](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/training/discrete_crr_trainer.py#L407-L441)
 
 
### Contextual Bandits

 Contextual bandit algorithms use the `PolicyEvaluator` class, which implements importance sampling-based evaluation:

 
```

```

 Supported bandit models include:

 
 - Linear UCB
 - Disjoint Linear UCB
 - Multi-Armed Bandits (UCB1)
 
 Sources:

 
 - [reagent/evaluation/cb/policy_evaluator.py16-166](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/cb/policy_evaluator.py#L16-L166)
 - [reagent/test/evaluation/cb/test_policy_evaluator.py34-199](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/evaluation/cb/test_policy_evaluator.py#L34-L199)
 - [reagent/test/models/test_disjoint_linucb_predictor.py22-124](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_disjoint_linucb_predictor.py#L22-L124)
 - [reagent/test/models/test_mab.py20-109](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/models/test_mab.py#L20-L109)
 
 
## Seq2Slate Evaluation

 For ranking problems, ReAgent supports evaluation of Seq2Slate models with specialized methods:

 
```

```

 This evaluation approach can assess both greedy and stochastic ranking policies.

 Sources:

 
 - [reagent/evaluation/evaluation_data_page.py90-183](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/evaluation/evaluation_data_page.py#L90-L183)
 - [reagent/models/seq2slate.py382-606](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/models/seq2slate.py#L382-L606)
 
 
## Integration with Testing

 The evaluation system is tested extensively through unit tests:

 
 - `test_integration.py`: Tests the integration of evaluation within training loops
 - `test_policy_evaluator.py`: Tests the core functionality of `PolicyEvaluator`
 - `test_utils.py`: Tests utility functions like importance weight calculations
 
 These tests ensure that the evaluation system correctly measures policy performance across various scenarios.

 Sources:

 
 - [reagent/test/evaluation/cb/test_integration.py23-299](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/evaluation/cb/test_integration.py#L23-L299)
 - [reagent/test/evaluation/cb/test_policy_evaluator.py34-199](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/evaluation/cb/test_policy_evaluator.py#L34-L199)
 - [reagent/test/evaluation/cb/test_utils.py14-56](https://github.com/facebookresearch/ReAgent/blob/9e707c09/reagent/test/evaluation/cb/test_utils.py#L14-L56)
 
 
## Summary

 ReAgent's evaluation system provides comprehensive capabilities for assessing model performance both during training and offline. The integration of counterfactual policy evaluation with different algorithms enables safe iteration on reinforcement learning policies before deployment. Key features include:

 
 - **Unified Data Structure**: `EvaluationDataPage` provides a consistent format for evaluation data across algorithms
 - **Algorithm-Specific Methods**: Different evaluation approaches for DQN, contextual bandits, and ranking problems
 - **Training Integration**: Seamless integration with the training loop via PyTorch Lightning
 - **Offline Evaluation**: Ability to evaluate new policies using only historical data
 
 These capabilities make ReAgent suitable for real-world applications where safety and performance guarantees are critical before deploying new policies.
