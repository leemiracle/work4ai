> 来源: [https://deepwiki.com/OpenRL-Lab/openrl/5-self-play-system](https://deepwiki.com/OpenRL-Lab/openrl/5-self-play-system)
> DeepWiki OpenRL-Lab/openrl | Last indexed: 28 April 2025 (4c92aa

# Self-Play System

  Relevant source files 
 - [examples/selfplay/opponent_templates/tictactoe_opponent/info.json](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/opponent_templates/tictactoe_opponent/info.json)
 - [examples/selfplay/selfplay.yaml](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/selfplay.yaml)
 - [examples/selfplay/test_env.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/test_env.py)
 - [examples/selfplay/train_selfplay.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/train_selfplay.py)
 - [openrl/configs/utils.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/configs/utils.py)
 - [openrl/selfplay/callbacks/selfplay_api.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/callbacks/selfplay_api.py)
 - [openrl/selfplay/opponents/base_opponent.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/opponents/base_opponent.py)
 - [openrl/selfplay/sample_strategy/base_sample_strategy.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/sample_strategy/base_sample_strategy.py)
 - [openrl/selfplay/sample_strategy/last_opponent.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/sample_strategy/last_opponent.py)
 - [openrl/selfplay/sample_strategy/random_opponent.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/sample_strategy/random_opponent.py)
 - [openrl/selfplay/selfplay_api/base_api.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/base_api.py)
 - [openrl/selfplay/selfplay_api/opponent_model.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/opponent_model.py)
 - [openrl/selfplay/selfplay_api/selfplay_api.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_api.py)
 - [openrl/selfplay/selfplay_api/selfplay_client.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_client.py)
 - [setup.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/setup.py)
 - [tests/test_selfplay/test_train_selfplay.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_selfplay/test_train_selfplay.py)
 
  The Self-Play System in OpenRL provides a framework for training agents by having them compete against previous versions of themselves or other agents. This approach is particularly valuable for developing strong policies in competitive environments, where the quality of opponents directly impacts learning outcomes. The system manages opponent selection, tracks performance metrics, and integrates seamlessly with the overall training process.

 For information about training multiple agents in cooperative or competitive settings in general, see [Multi-Agent Training](https://deepwiki.com/OpenRL-Lab/openrl/7.3-multi-agent-training).

 
## Architecture Overview

 The Self-Play System uses a client-server architecture built on Ray Serve to manage the opponent pool and battle results. The system consists of several key components working together to provide self-play capabilities.

 
### Self-Play System Architecture Diagram

 
```

```

 Sources: [openrl/selfplay/selfplay_api/selfplay_api.py1-129](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_api.py#L1-L129) [openrl/selfplay/selfplay_api/selfplay_client.py1-94](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_client.py#L1-L94) [openrl/selfplay/sample_strategy/random_opponent.py1-29](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/sample_strategy/random_opponent.py#L1-L29) [openrl/selfplay/sample_strategy/last_opponent.py1-28](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/sample_strategy/last_opponent.py#L1-L28) [openrl/selfplay/callbacks/selfplay_api.py1-81](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/callbacks/selfplay_api.py#L1-L81)

 
### Component Interaction Flow

 
```

```

 Sources: [openrl/selfplay/selfplay_api/selfplay_api.py38-128](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_api.py#L38-L128) [openrl/selfplay/selfplay_api/selfplay_client.py23-93](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_client.py#L23-L93) [openrl/selfplay/callbacks/selfplay_api.py27-80](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/callbacks/selfplay_api.py#L27-L80)

 
## Core Components

 
### SelfplayAPIServer

 The `SelfplayAPIServer` is a Ray Serve application that manages the opponent pool and provides endpoints for:

 
 - Setting the sample strategy
 - Adding opponents to the pool
 - Retrieving opponents based on the current strategy
 - Tracking battle results
 
 The server maintains a database of opponents and their performance metrics, including TrueSkill ratings that are updated after each battle.

 Sources: [openrl/selfplay/selfplay_api/selfplay_api.py36-129](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_api.py#L36-L129) [openrl/selfplay/selfplay_api/base_api.py52-59](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/base_api.py#L52-L59)

 
### SelfPlayClient

 The `SelfPlayClient` provides a convenient interface for interacting with the API server. It includes methods for:

 
```

```

 Sources: [openrl/selfplay/selfplay_api/selfplay_client.py23-93](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_client.py#L23-L93)

 
### Opponent Model

 The `OpponentModel` represents an opponent in the pool and tracks:

 
 - Opponent ID and path
 - Opponent type and information
 - Battle history (wins, losses, draws)
 - TrueSkill rating
 
 
```

```

 Sources: [openrl/selfplay/selfplay_api/opponent_model.py24-76](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/opponent_model.py#L24-L76)

 
### Sample Strategies

 The Self-Play System supports different strategies for selecting opponents from the pool:

 
 - **RandomOpponent**: Selects an opponent randomly from the pool
 - **LastOpponent**: Always selects the most recently added opponent
 - Additional strategies can be implemented by extending the `BaseSampleStrategy` class
 
 Sources: [openrl/selfplay/sample_strategy/random_opponent.py25-28](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/sample_strategy/random_opponent.py#L25-L28) [openrl/selfplay/sample_strategy/last_opponent.py24-27](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/sample_strategy/last_opponent.py#L24-L27) [openrl/selfplay/sample_strategy/base_sample_strategy.py26-32](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/sample_strategy/base_sample_strategy.py#L26-L32)

 
## Setup and Installation

 To use the Self-Play System, you need to install the necessary dependencies:

 
```

```

 This will install the required packages:

 
 - Ray (with Ray Serve)
 - PettingZoo
 - TrueSkill
 - Other dependencies
 
 Sources: [setup.py74-80](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/setup.py#L74-L80)

 
## Configuration

 Self-play is configured via YAML configuration files. Here's an example configuration:

 
```

```

 Key configuration options:

 
 - `selfplay_api.host` and `selfplay_api.port`: Server address
 - `lazy_load_opponent`: Optimization for loading opponents
 - `callbacks`: Configuration for the SelfplayAPI and SelfplayCallback
 - `sample_strategy`: Strategy for selecting opponents (e.g., "RandomOpponent", "LastOpponent")
 - `save_freq`: How often to save the agent as an opponent
 - `opponent_pool_path`: Directory to store opponent models
 - `opponent_template`: Template for creating opponents
 
 Sources: [examples/selfplay/selfplay.yaml1-28](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/selfplay.yaml#L1-L28)

 
## Usage

 
### Basic Usage

 To use self-play in your training process:

 
 - Create a configuration file with self-play settings
 - Use environment wrappers to enable self-play
 - Train your agent using the standard OpenRL training loop
 
 Here's an example:

 
```

```

 Sources: [examples/selfplay/train_selfplay.py14-39](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/train_selfplay.py#L14-L39)

 
### Environment Wrappers

 Two key environment wrappers are used for self-play:

 
 - **OpponentPoolWrapper**: Selects opponents from the pool during training
 - **RecordWinner**: Tracks and reports match outcomes to update opponent ratings
 
 These wrappers are applied to the environment when it's created using the `make` function.

 Sources: [tests/test_selfplay/test_train_selfplay.py63-71](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_selfplay/test_train_selfplay.py#L63-L71) [examples/selfplay/train_selfplay.py21-28](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/train_selfplay.py#L21-L28)

 
## Evaluation

 After training with self-play, you can evaluate your agent against random opponents or other baselines:

 
```

```

 Sources: [examples/selfplay/train_selfplay.py42-84](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/train_selfplay.py#L42-L84)

 
## Advanced Features

 
### TrueSkill Ratings

 The Self-Play System uses Microsoft's TrueSkill algorithm to rate opponents based on their performance. These ratings are updated after each battle and can be used to select appropriate challengers.

 
```

```

 Sources: [openrl/selfplay/selfplay_api/selfplay_api.py124-126](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/selfplay_api.py#L124-L126)

 
### Battle History Tracking

 The system maintains detailed battle statistics for each opponent:

 
 - Total games played
 - Number of wins, losses, and draws
 - Win rate, loss rate, and draw rate
 
 This information can be used to analyze agent performance over time.

 Sources: [openrl/selfplay/selfplay_api/opponent_model.py30-54](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/selfplay_api/opponent_model.py#L30-L54)

 
## Implementation Considerations

 
### Ray Serve Backend

 The self-play system uses Ray Serve as its backend, providing:

 
 - Scalable opponent management
 - HTTP API for component communication
 - Asynchronous operation
 
 The server is automatically started and stopped as part of the training process through callbacks.

 Sources: [openrl/selfplay/callbacks/selfplay_api.py42-53](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/callbacks/selfplay_api.py#L42-L53) [openrl/selfplay/callbacks/selfplay_api.py72-80](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/selfplay/callbacks/selfplay_api.py#L72-L80)

 
### Opponent Templates

 Opponent templates provide a structure for creating new opponents. They include:

 
 - Type information
 - Description
 - Any necessary code or configuration
 
 
```

```

 Sources: [examples/selfplay/opponent_templates/tictactoe_opponent/info.json1-4](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/examples/selfplay/opponent_templates/tictactoe_opponent/info.json#L1-L4)

 
## Conclusion

 The Self-Play System in OpenRL provides a robust framework for training agents through competition with themselves. By maintaining a pool of opponents at various skill levels and with different strategies, agents can continually improve against increasingly challenging opposition, leading to more robust and effective policies.
