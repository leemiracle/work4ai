<!-- source: DeepWiki mcp.deepwiki.com · repo thu-ml/tianshou · page 11 Glossary · fetched 2026-10-30 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [docs/index.rst](docs/index.rst)
- [test/base/env.py](test/base/env.py)
- [test/base/test_batch.py](test/base/test_batch.py)
- [test/base/test_buffer.py](test/base/test_buffer.py)
- [test/base/test_collector.py](test/base/test_collector.py)
- [tianshou/data/batch.py](tianshou/data/batch.py)
- [tianshou/data/collector.py](tianshou/data/collector.py)
- [tianshou/env/atari/atari_network.py](tianshou/env/atari/atari_network.py)
- [tianshou/highlevel/algorithm.py](tianshou/highlevel/algorithm.py)
- [tianshou/utils/net/common.py](tianshou/utils/net/common.py)
- [tianshou/utils/net/continuous.py](tianshou/utils/net/continuous.py)
- [tianshou/utils/net/discrete.py](tianshou/utils/net/discrete.py)

</details>



## Purpose and Scope

This glossary defines core terminology, jargon, classes, modules, and architectural concepts specific to the Tianshou v2 reinforcement learning codebase. It serves as a technical reference linking natural language reinforcement learning concepts to their concrete implementations in Tianshou's codebase, providing code pointers and architectural context.

---

## 1. Core Data Structures and Execution Components

### Batch
`Batch` is Tianshou's central heterogeneous container for data handling, replacing standard dictionaries and custom structures. It supports numpy arrays, PyTorch tensors, scalars, nested `Batch` objects, and torch distributions while offering dynamic attribute access, slicing, concatenation (`cat_`), and splitting (`split`) [tianshou/data/batch.py:1-43](). Type safety and IDE autocompletion are supported via runtime-checkable protocols like `BatchProtocol` [tianshou/data/batch.py:31-42]().

```mermaid
graph TD
    A["BatchContainer"] --> B["NumPyArrays"]
    A --> C["TorchTensors"]
    A --> D["NestedBatchObjects"]
    A --> E["TorchDistributions"]
    
    subclass A BatchClass [tianshou/data/batch.py:1-43]
    subclass B NumPy [tianshou/data/batch.py:120-131]
    subclass C Tensors [test/base/test_batch.py:47-53]
    subclass D Nested [test/base/test_batch.py:98-104]
```
*Sources: [tianshou/data/batch.py:1-43](), [test/base/test_batch.py:47-104]()*

### ReplayBuffer
The base experience storage container and sampling engine in Tianshou. `ReplayBuffer` manages circular buffer memory allocation for online and offline RL. Specialized variants include `VectorReplayBuffer` for parallel vectorized environments, `PrioritizedReplayBuffer` (PER) for prioritized sampling, `HERReplayBuffer` for hindsight goal relabeling, and `CachedReplayBuffer` [test/base/test_buffer.py:13-24]().

*Sources: [test/base/test_buffer.py:13-24]()*

### Collector
The execution bridge connecting policies, environments, and replay buffers. A `Collector` (or `AsyncCollector`) steps through vectorized environments using actions sampled from a `Policy`, computes rollouts, records transition tuples into a `ReplayBuffer`, and returns performance metrics (`CollectStats`) [tianshou/data/collector.py:49-80]().

*Sources: [tianshou/data/collector.py:49-80](), [tianshou/data/collector.py:117-150]()*

### World
The high-level experiment execution context and container managing the experiment lifecycle, environment creation, policy persistence, and logging in the declarative API [tianshou/highlevel/algorithm.py:79-79]().

*Sources: [tianshou/highlevel/algorithm.py:79-79]()*

---

## 2. Algorithm and Policy Framework

### Algorithm vs. Policy (v2 Architecture)
In Tianshou v2, a strict type-level separation is established between **Algorithm** (the optimization engine containing loss functions, gradient computation, and network update logic) and **Policy** (the evaluation interface responsible for action selection and probability distribution outputs) [README.md:10-18](). The package formerly known as `tianshou.policy` was restructured into `tianshou.algorithm` [CHANGELOG.md:110-113]().

```mermaid
graph TD
    A["WorldExecutionEngine"] --> B["AlgorithmEngine"]
    A --> C["CollectorInstance"]
    B -->|ComputesLossAndUpdates| D["AlgorithmBase"]
    C -->|SelectsActionsVia| E["PolicyInterface"]
    E -->|Wraps| F["NeuralNetworkModules"]
    
    subclass B Algorithm [tianshou/highlevel/algorithm.py:110-112]
    subclass E Policy [tianshou/algorithm/algorithm_base.py:1-29]
    subclass F Modules [tianshou/utils/net/common.py:90-105]
```
*Sources: [README.md:10-18](), [CHANGELOG.md:110-113](), [tianshou/highlevel/algorithm.py:110-112]() [tianshou/algorithm/algorithm_base.py:1-29]()*

### Lagged / Target Network
A secondary neural network copy maintained in off-policy algorithms (such as DQN, DDPG, and TD3) whose weights are updated slowly or periodically tracking the primary training network to stabilize value target computation.

*Sources: [README.md:38-54]()*

### Alpha ($\alpha$)
The entropy regularization coefficient used in algorithms like SAC (`SAC` / `SACPolicy`) that weights the entropy term in the objective function to balance exploration and exploitation.

*Sources: [README.md:54-56](), [tianshou/highlevel/algorithm.py:67-67]()*

### GAE (Generalized Advantage Estimator)
A method for computing variance-reduced advantage estimates for policy gradient algorithms (PPO, TRPO, A2C) parameterized by $\gamma$ and $\lambda$, implemented via episodic return-to-go calculations [CHANGELOG.md:66]().

*Sources: [README.md:66](), [tianshou/algorithm/algorithm_base.py:16-16]() [docs/index.rst:37-37]()*

---

## 3. Advanced Modules and Integration Abstractions

### ICM (Intrinsic Curiosity Module)
An exploration wrapper (`ICMOffPolicyWrapper`, `ICMOnPolicyWrapper`) that computes intrinsic reward bonuses derived from the prediction error of a learned forward dynamics model of the environment [docs/index.rst:35-35]().

*Sources: [docs/index.rst:35-35]() [README.md:68-68]()*

### HER (Hindsight Experience Replay)
An experience replay mechanism (`HERReplayBuffer`, `HERVectorReplayBuffer`) that substitutes achieved goals with desired goals in past trajectories to facilitate learning in sparse-reward environments [docs/index.rst:38-38]() [test/base/test_buffer.py:16-17]().

*Sources: [docs/index.rst:38-38](), [test/base/test_buffer.py:16-17]()*

### PER (Prioritized Experience Replay)
A replay buffer variant (`PrioritizedReplayBuffer`, `PrioritizedVectorReplayBuffer`) that samples transition tuples with probability proportional to their temporal-difference (TD) error magnitude using a segment tree data structure [docs/index.rst:36-36]() [test/base/test_buffer.py:18-19]().

*Sources: [docs/index.rst:36-36](), [test/base/test_buffer.py:18-19](), [test/base/test_buffer.py:21-21]()*

### EnvFactory
A factory class hierarchy in the high-level API responsible for instantiating training and testing environments per execution mode (e.g., vectorized, Gym, EnvPool) [README.md:80-80]() [tianshou/highlevel/algorithm.py:110-112]().

*Sources: [README.md:80-80](), [tianshou/highlevel/algorithm.py:110-112]()*

---

## 4. Summary Table of Key Code Entities

| Natural Language Term | Code Entity Name | Module Path / Reference | Role |
| :--- | :--- | :--- | :--- |
| **Batch Container** | `Batch` | `tianshou.data.Batch` | Heterogeneous container for RL data [tianshou/data/batch.py:1-43]() |
| **Experience Buffer** | `ReplayBuffer` | `tianshou.data.ReplayBuffer` | Stores and samples transition rollouts [test/base/test_buffer.py:28-30]() |
| **Rollout Collector** | `Collector` | `tianshou.data.Collector` | Executes environment steps and populates buffers [tianshou/data/collector.py:49-80]() |
| **Learning Algorithm** | `Algorithm` | `tianshou.algorithm.Algorithm` | Encapsulates training loss and optimization [tianshou/highlevel/algorithm.py:110-112]() |
| **Action Policy** | `Policy` | `tianshou.algorithm.algorithm_base.Policy` | Computes action distributions and selections [tianshou/algorithm/algorithm_base.py:1-29]() |
| **Environment Factory** | `EnvFactory` | `tianshou.highlevel.env` | Builds vectorized/wrapped environments [tianshou/highlevel/algorithm.py:110-112]() |

*Sources: [tianshou/data/batch.py:1-43](), [test/base/test_buffer.py:28-30](), [tianshou/data/collector.py:49-80](), [tianshou/highlevel/algorithm.py:110-112](), [tianshou/algorithm/algorithm_base.py:1-29]()*