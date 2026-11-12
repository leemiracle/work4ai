<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/rl · page 7 Learning Algorithms · fetched 2026-10-21 -->

# Learning Algorithms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [torchrl/objectives/a2c.py](torchrl/objectives/a2c.py)
- [torchrl/objectives/common.py](torchrl/objectives/common.py)
- [torchrl/objectives/cql.py](torchrl/objectives/cql.py)
- [torchrl/objectives/crossq.py](torchrl/objectives/crossq.py)
- [torchrl/objectives/ddpg.py](torchrl/objectives/ddpg.py)
- [torchrl/objectives/decision_transformer.py](torchrl/objectives/decision_transformer.py)
- [torchrl/objectives/deprecated.py](torchrl/objectives/deprecated.py)
- [torchrl/objectives/iql.py](torchrl/objectives/iql.py)
- [torchrl/objectives/ppo.py](torchrl/objectives/ppo.py)
- [torchrl/objectives/redq.py](torchrl/objectives/redq.py)
- [torchrl/objectives/reinforce.py](torchrl/objectives/reinforce.py)
- [torchrl/objectives/sac.py](torchrl/objectives/sac.py)
- [torchrl/objectives/td3.py](torchrl/objectives/td3.py)
- [torchrl/objectives/td3_bc.py](torchrl/objectives/td3_bc.py)
- [torchrl/objectives/utils.py](torchrl/objectives/utils.py)

</details>



This section documents TorchRL's learning algorithm implementations, specifically loss modules and value estimation methods that enable training of reinforcement learning agents [torchrl/objectives/common.py:87-151](). This covers mathematical objectives, actor-critic coordination, value estimation, and specialized training pipelines.

For information about the neural network components and modules that these learning algorithms operate on, see [Modules and Models](#6). For details about data collection and experience gathering during training, see [Data Collection](#4).

---

## 7.1. Loss Module Architecture

The `LossModule` base class serves as the core abstraction for all RL loss computations in TorchRL [torchrl/objectives/common.py:87-151](). It inherits from `TensorDictModuleBase` and provides a unified interface that reads an input `TensorDict` containing rollouts and returns a collection of scalar loss values (prefixed with `"loss_"`) along with logging metrics [torchrl/objectives/common.py:87-96]().

Key architectural features provided by `LossModule` include automatic functional module conversion for meta-learning and `vmap`, target network lifecycle management via updaters, configurable tensor keys through the `_AcceptedKeys` dataclass pattern, and seamless integration with the `ValueEstimatorBase` framework [torchrl/objectives/common.py:87-114]().

```mermaid
graph TB
    subgraph "Loss Architecture Space"
        LM["LossModule (torchrl/objectives/common.py)"] --> PPO["PPOLoss (torchrl/objectives/ppo.py)"]
        LM --> SAC["SACLoss (torchrl/objectives/sac.py)"]
        LM --> DQN["DQNLoss (test/test_cost.py)"]
        LM --> IQL["IQLLoss (torchrl/objectives/iql.py)"]
        LM --> CQL["CQLLoss (torchrl/objectives/cql.py)"]
        
        LM --> CVT["convert_to_functional()"]
        LM --> MVE["make_value_estimator()"]
        LM --> SK["set_keys()"]
    end

    Sources: [torchrl/objectives/common.py:87-151](), [torchrl/objectives/ppo.py:119-150](), [torchrl/objectives/sac.py:59-64]()
```

For comprehensive details on functional module conversion, target networks, tensor mapping patterns, and custom loss design, see **Loss Module Architecture** (Child Page 7.1).

Sources: [torchrl/objectives/common.py:87-151](), [torchrl/objectives/ppo.py:119-150](), [torchrl/objectives/sac.py:59-64]()

---

## 7.2. On-Policy Algorithms

On-policy algorithms collect rollouts using the latest policy parameters, compute advantage estimates over these trajectories, perform gradient updates, and discard the collected experience. TorchRL implements standard on-policy objectives including `PPOLoss` [torchrl/objectives/ppo.py:119-150](), `A2CLoss` [torchrl/objectives/a2c.py:47-55](), `ReinforceLoss` [torchrl/objectives/reinforce.py:32-36](), and IMPALA losses.

These modules integrate closely with advantage estimation methods, entropy bonuses to prevent premature convergence, and value function clipping to stabilize critic updates [torchrl/objectives/ppo.py:158-160](), [torchrl/objectives/a2c.py:60-108]().

For detailed mathematical formulations, clipping mechanisms, entropy calculation routines, and advantage integration guides, see **On-Policy Algorithms** (Child Page 7.2).

Sources: [torchrl/objectives/ppo.py:119-150](), [torchrl/objectives/a2c.py:47-55](), [torchrl/objectives/reinforce.py:32-36]()

---

## 7.3. Off-Policy Algorithms

Off-policy algorithms reuse historical transitions stored in replay buffers by decoupling data collection from policy optimization. TorchRL provides robust implementations for actor-critic frameworks such as `SACLoss` [torchrl/objectives/sac.py:59-64](), `DDPGLoss` [torchrl/objectives/ddpg.py:27-28](), `TD3Loss` [torchrl/objectives/td3.py:27-28](), as well as ensemble-based variants like CrossQ and TQC.

These loss classes manage actor-critic synchronization, twin Q-networks to mitigate overestimation bias, automatic temperature tuning for maximum entropy objectives, and delayed policy updates [torchrl/objectives/sac.py:89-117](), [torchrl/objectives/td3.py:48-65]().

For deep dives into target network polyak updates, multi-critic coordination, and entropy auto-tuning, see **Off-Policy Algorithms** (Child Page 7.3).

Sources: [torchrl/objectives/sac.py:59-64](), [torchrl/objectives/ddpg.py:27-28](), [torchrl/objectives/td3.py:27-28]()

---

## 7.4. Value-Based Algorithms

Value-based methods learn action-value functions directly without necessarily parameterizing an explicit policy. TorchRL implements foundational and advanced discrete/continuous value algorithms, including DQN, Conservative Q-Learning (`CQLLoss`) [torchrl/objectives/cql.py:38-41](), Implicit Q-Learning (`IQLLoss`) [torchrl/objectives/iql.py:43-46](), and Randomized Ensembled Double Q-Learning (`REDQLoss`) [torchrl/objectives/redq.py:33-38]().

These modules incorporate double Q-learning mechanics, expectile regression for offline value backups, distributional RL components, and penalty regularizers designed to prevent out-of-distribution action overestimation in offline datasets [torchrl/objectives/cql.py:80-90](), [torchrl/objectives/iql.py:66-71]().

For full implementation details on offline regularizers, expectile regression, and ensemble Q-subsampling, see **Value-Based Algorithms** (Child Page 7.4).

Sources: [torchrl/objectives/cql.py:38-41](), [torchrl/objectives/iql.py:43-46](), [torchrl/objectives/redq.py:33-38]()

---

## 7.5. Value Estimators

Value estimators compute advantage functions and target returns required by actor-critic and policy gradient loss modules. The `ValueEstimators` enum defines standard estimation strategies [torchrl/objectives/utils.py:53-71]():

```mermaid
graph TB
    subgraph "Value Estimator Space"
        VE["ValueEstimators (torchrl/objectives/utils.py)"] --> GAE["GAE (Generalized Advantage Estimate)"]
        VE --> TDL["TDLambda (TD(lambda))"]
        VE --> TD0["TD0 (Bootstrapped TD 1-step)"]
        VE --> TD1["TD1 (Infinity-step return)"]
        VE --> VT["VTrace (V-trace off-policy)"]
        
        GAE --> VEM["ValueEstimatorBase (torchrl/objectives/value/advantages.py)"]
        TDL --> VEM
        TD0 --> VEM
    end

    Sources: [torchrl/objectives/utils.py:53-71]()
```

Each estimator inherits from `ValueEstimatorBase` and calculates temporal difference errors, bootstrapped return targets, and advantage tensors directly from rollout `TensorDict` structures [torchrl/objectives/utils.py:53-71]().

For guidance on selecting between GAE, TD-Lambda, and V-Trace based on on-policy or off-policy requirements, see **Value Estimators** (Child Page 7.5).

Sources: [torchrl/objectives/utils.py:53-71]()

---

## 7.6. Model-Based RL: Dreamer and DreamerV3

TorchRL implements state-of-the-art model-based reinforcement learning pipelines centered around Dreamer and DreamerV3. These architectures learn environmental dynamics via Recurrent State Space Models (RSSM), encode observations and rewards using symlog transformations, utilize categorical two-hot value encodings, and perform imagination rollouts in latent space to optimize policy and value networks.

The training framework coordinates world model learning, behavior learning, and specialized optimizers in a unified pipeline. For complete architectural documentation, see **Model-Based RL: Dreamer and DreamerV3** (Child Page 7.6).

Sources: [torchrl/objectives/common.py:87-151]()

---

## 7.7. Imitation and Offline Objectives

To support learning from demonstration and static datasets, TorchRL provides specialized imitation learning and offline objectives. These include Behavior Cloning (BC), Diffusion BC, Architecture for Robotic Manipulation (ACT), Generative Adversarial Imitation Learning (GAIL), and Decision Transformer [torchrl/objectives/decision_transformer.py]().

These objectives bridge offline data loading with online fine-tuning strategies, sequence modeling approaches for trajectory generation, and policy regularization. For implementation details and configuration guides, see **Imitation and Offline Objectives** (Child Page 7.7).

Sources: [torchrl/objectives/common.py:87-151](), [torchrl/objectives/decision_transformer.py:1-20]()

---

