> 来源: [https://deepwiki.com/Unity-Technologies/ml-agents/6-advanced-topics](https://deepwiki.com/Unity-Technologies/ml-agents/6-advanced-topics)
> DeepWiki Unity-Technologies/ml-agents | Last indexed: 22 May 2026 (d52b00

# Advanced Topics

  Relevant source files 
 - [docs/FAQ.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/FAQ.md?plain=1)
 - [docs/Getting-Started.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Getting-Started.md?plain=1)
 - [docs/Learning-Environment-Create-New.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Create-New.md?plain=1)
 - [docs/Learning-Environment-Design-Agents.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design-Agents.md?plain=1)
 - [docs/Learning-Environment-Design.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design.md?plain=1)
 - [docs/Learning-Environment-Examples.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Examples.md?plain=1)
 - [docs/Learning-Environment-Executable.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Executable.md?plain=1)
 - [docs/ML-Agents-Overview.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/ML-Agents-Overview.md?plain=1)
 - [docs/Readme.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Readme.md?plain=1)
 - [docs/Training-Configuration-File.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-Configuration-File.md?plain=1)
 - [docs/Training-ML-Agents.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-ML-Agents.md?plain=1)
 - [ml-agents/mlagents/trainers/ghost/trainer.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/ghost/trainer.py)
 - [ml-agents/mlagents/trainers/poca/trainer.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/poca/trainer.py)
 - [ml-agents/mlagents/trainers/ppo/trainer.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/ppo/trainer.py)
 - [ml-agents/mlagents/trainers/sac/trainer.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/sac/trainer.py)
 - [ml-agents/mlagents/trainers/tests/test_rl_trainer.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_rl_trainer.py)
 - [ml-agents/mlagents/trainers/tests/test_trainers.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_trainers.py)
 - [ml-agents/mlagents/trainers/trainer/rl_trainer.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer/rl_trainer.py)
 - [ml-agents/mlagents/trainers/trainer/trainer.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/trainer/trainer.py)
 
  This document covers advanced features and specialized use cases in the Unity ML-Agents Toolkit. It's intended for users who are already familiar with the basics of training ML-Agents and want to explore more sophisticated techniques and configurations.

 
## Example Environments and Multi-Agent Training

 The ML-Agents Toolkit provides over 17 example environments that highlight various features of the toolkit [docs/Readme.md26](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Readme.md?plain=1#L26-L26) These environments serve as templates for new designs or benchmarks for reinforcement learning algorithms [docs/Learning-Environment-Examples.md5-9](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Examples.md?plain=1#L5-L9)

 
### Cooperative and Adversarial Patterns

 Multi-agent scenarios are categorized into cooperative and adversarial patterns:

 
 - **Adversarial (Self-Play)**: Agents are divided into teams using `BehaviorParameters.TeamId`. The `GhostTrainer` manages self-play by keeping snapshots of past policies to act as opponents [ml-agents/mlagents/trainers/ghost/trainer.py28-40](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/ghost/trainer.py#L28-L40)
 - **Cooperative (MA-POCA)**: Uses the `SimpleMultiAgentGroup` API to group agents. The MA-POCA trainer (Multi-Agent Post-hoc Attention) allows agents to work together towards a shared goal even if agents are added or removed during the episode [docs/ML-Agents-Overview.md92-102](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/ML-Agents-Overview.md?plain=1#L92-L102)
 
 **Multi-Agent Coordination Architecture**

 
```

```

 For details, see [Example Environments and Multi-Agent Training](https://deepwiki.com/Unity-Technologies/ml-agents/6.1-example-environments-and-multi-agent-training).

 Sources: [docs/Learning-Environment-Design-Agents.md38-41](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Learning-Environment-Design-Agents.md?plain=1#L38-L41) [ml-agents/mlagents/trainers/ghost/trainer.py28-40](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/ghost/trainer.py#L28-L40) [docs/ML-Agents-Overview.md92-102](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/ML-Agents-Overview.md?plain=1#L92-L102)

 
## Docker and Cloud Training

 Training can be scaled by moving from the Unity Editor to standalone builds running in Docker containers or cloud infrastructure.

 
### Docker Containers

 Docker provides a consistent environment for training, especially useful for headless servers. The `mlagents-learn` command supports a `--no-graphics` flag for these environments [docs/FAQ.md47-51](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/FAQ.md?plain=1#L47-L51)

 
### Cloud Infrastructure

 Users can train on AWS, Azure, or Google Cloud Platform by deploying Docker images. This allows for:

 
 - **Concurrent Instances**: Training using multiple parallel Unity instances to speed up experience collection [docs/Training-ML-Agents.md25](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-ML-Agents.md?plain=1#L25-L25)
 - **Remote Monitoring**: Accessing training progress via TensorBoard hosted on the cloud instance.
 
 For details, see [Docker and Cloud Training](https://deepwiki.com/Unity-Technologies/ml-agents/6.2-docker-and-cloud-training).

 Sources: [docs/FAQ.md47-51](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/FAQ.md?plain=1#L47-L51) [docs/Training-ML-Agents.md25](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-ML-Agents.md?plain=1#L25-L25)

 
## Analytics and Monitoring

 ML-Agents includes a robust system for tracking metrics through the `StatsReporter` and `StatsRecorder` classes.

 
### Metric Tracking Pipeline

 The `StatsReporter` in Python collects data from the trainers (PPO, SAC, etc.) and writes them to TensorBoard summaries [ml-agents/mlagents/trainers/ppo/trainer.py103-107](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/ppo/trainer.py#L103-L107)

 **Analytics Data Flow**

 
```

```

 
### Key Metrics

 
| Category | Metric Name | Source |
|---|---|---|
| Environment | Cumulative Reward | ml-agents/mlagents/trainers/trainer/rl_trainer.py80 |
| Policy | Value Estimate | ml-agents/mlagents/trainers/ppo/trainer.py103-106 |
| Self-Play | ELO | ml-agents/mlagents/trainers/ghost/trainer.py81-82 |

 For details, see [Analytics and Monitoring](https://deepwiki.com/Unity-Technologies/ml-agents/6.3-analytics-and-monitoring).

 Sources: [ml-agents/mlagents/trainers/ppo/trainer.py103-107](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/ppo/trainer.py#L103-L107) [ml-agents/mlagents/trainers/ghost/trainer.py81-82](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/ghost/trainer.py#L81-L82) [docs/Training-ML-Agents.md91-95](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-ML-Agents.md?plain=1#L91-L95)

 
## Contributing and Development

 The toolkit is designed to be extensible, allowing developers to add custom algorithms and sensors.

 
### Trainer Plugin System

 The `Trainer` class serves as the base for all algorithms. Developers can implement new trainers by extending `RLTrainer` or `OnPolicyTrainer`/`OffPolicyTrainer` [ml-agents/mlagents/trainers/tests/test_rl_trainer.py21](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_rl_trainer.py#L21-L21)

 
### Testing and Quality

 The codebase includes a suite of unit tests for both the Unity SDK and Python trainers. For example, `test_rl_trainer.py` validates the advance of the training loop and checkpoint saving [ml-agents/mlagents/trainers/tests/test_rl_trainer.py97-114](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_rl_trainer.py#L97-L114)

 For details, see [Contributing and Development](https://deepwiki.com/Unity-Technologies/ml-agents/6.4-contributing-and-development).

 Sources: [ml-agents/mlagents/trainers/tests/test_rl_trainer.py21-63](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/mlagents/trainers/tests/test_rl_trainer.py#L21-L63) [docs/Readme.md32](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Readme.md?plain=1#L32-L32)
