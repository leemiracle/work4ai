<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TextWorld · page 8 Challenges and Examples · fetched 2026-10-26 -->

# Challenges and Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [notebooks/Building a simple agent.ipynb](notebooks/Building a simple agent.ipynb)
- [notebooks/Handcrafting a game.ipynb](notebooks/Handcrafting a game.ipynb)
- [notebooks/Playing TextWorld generated games with OpenAI Gym.ipynb](notebooks/Playing TextWorld generated games with OpenAI Gym.ipynb)
- [notebooks/Playing text-based games with TextWorld.ipynb](notebooks/Playing text-based games with TextWorld.ipynb)
- [textworld/challenges/tests/test_coin_collector.py](textworld/challenges/tests/test_coin_collector.py)

</details>



This document covers TextWorld's built-in challenges and comprehensive learning materials, including predefined game scenarios and step-by-step tutorials for building agents and creating games. For information about command-line tools for game generation and playing, see [Command Line Tools](#7).

## Built-in Challenges

TextWorld provides predefined challenges that serve as standardized benchmarks for agent development and research. These challenges offer varying levels of difficulty and complexity to test different aspects of agent capabilities.

### Coin Collector Challenge

The `coin_collector` challenge is a scalable scenario where agents must navigate environments and collect coins. It demonstrates TextWorld's ability to generate games with controlled complexity parameters.

```mermaid
graph TD
    CoinCollector["coin_collector.make()"] --> GameOptions["textworld.GameOptions"]
    CoinCollector --> Settings["settings = {'level': N}"]
    Settings --> Level1["Level 1: quest_length=1, nb_rooms=1"]
    Settings --> Level100["Level 100: quest_length=100, nb_rooms=100"]
    Settings --> Level101["Level 101: quest_length=1, nb_rooms=2"]
    Settings --> Level200["Level 200: quest_length=100, nb_rooms=200"]
    Settings --> Level201["Level 201: quest_length=1, nb_rooms=3"]
    Settings --> Level300["Level 300: quest_length=100, nb_rooms=300"]
    
    CoinCollector --> GeneratedGame["Generated Game Object"]
    GeneratedGame --> Quests["game.quests[0].commands"]
    GeneratedGame --> Rooms["game.world.rooms"]
```

The challenge supports multiple difficulty levels with different parameters:

| Level | Quest Length | Number of Rooms | Complexity |
|-------|-------------|-----------------|------------|
| 1     | 1           | 1               | Minimal    |
| 100   | 100         | 100             | High       |
| 101   | 1           | 2               | Low        |
| 200   | 100         | 200             | Very High  |
| 201   | 1           | 3               | Low        |
| 300   | 100         | 300             | Maximum    |

Sources: [textworld/challenges/tests/test_coin_collector.py:11-27]()

## Tutorial Notebooks

TextWorld provides comprehensive Jupyter notebooks that guide users through different aspects of the framework, from basic game playing to advanced agent development.

### Learning Progression Overview

```mermaid
graph TD
    BasicPlay["Playing text-based games with TextWorld"] --> GymAPI["Playing TextWorld games with OpenAI Gym"]
    GymAPI --> AgentDev["Building a simple agent"]
    BasicPlay --> GameCreation["Handcrafting a game"]
    
    BasicPlay --> BasicConcepts["textworld.start(), env.step(), env.reset()"]
    GymAPI --> GymConcepts["textworld.gym.register_game(), textworld.gym.make()"]
    AgentDev --> AgentConcepts["RandomAgent, NeuralAgent, CommandScorer"]
    GameCreation --> CreationConcepts["GameMaker, M.new_room(), M.connect()"]
    
    AgentDev --> TrainingCycle["Training Loop with tw-simple games"]
    TrainingCycle --> Evaluation["Performance evaluation and testing"]
```

### Core API Tutorial

The basic tutorial demonstrates fundamental TextWorld concepts using the core API.

Key components covered:
- `textworld.start()` for initializing games
- `textworld.EnvInfos` for requesting game state information
- `env.step(command)` for sending commands
- `env.reset()` for restarting games
- `env.render()` for displaying game output

The tutorial uses external games like Zork1 and demonstrates information extraction including feedback, description, inventory, and score tracking.

Sources: [notebooks/Playing text-based games with TextWorld.ipynb:88-175](), [notebooks/Playing text-based games with TextWorld.ipynb:335-389]()

### OpenAI Gym Integration Tutorial

This tutorial shows how to use TextWorld with the familiar OpenAI Gym interface, making it compatible with existing reinforcement learning frameworks.

```mermaid
graph LR
    GameFile["game.ulx"] --> RegisterGame["textworld.gym.register_game()"]
    RegisterGame --> EnvID["env_id (e.g., 'tw-v0')"]
    EnvID --> MakeEnv["textworld.gym.make(env_id)"]
    MakeEnv --> GymEnv["Gym Environment"]
    
    GymEnv --> Reset["env.reset() -> obs, infos"]
    GymEnv --> Step["env.step(command) -> obs, score, done, infos"]
    
    EnvInfos["textworld.EnvInfos"] --> RegisterGame
    EnvInfos --> AdmissibleCommands["admissible_commands=True"]
    EnvInfos --> Entities["entities=True"]
    EnvInfos --> Facts["facts=True"]
```

The tutorial demonstrates advanced information extraction capabilities including admissible commands, entity lists, and game state facts for generated games.

Sources: [notebooks/Playing TextWorld generated games with OpenAI Gym.ipynb:57-95](), [notebooks/Playing TextWorld generated games with OpenAI Gym.ipynb:297-345]()

### Agent Development Tutorial

The agent development tutorial provides a comprehensive guide to building and training reinforcement learning agents for TextWorld games.

#### Agent Architecture

```mermaid
graph TD
    RandomAgent["RandomAgent"] --> AgentInterface["textworld.gym.Agent"]
    NeuralAgent["NeuralAgent"] --> AgentInterface
    
    NeuralAgent --> CommandScorer["CommandScorer (PyTorch)"]
    CommandScorer --> Embedding["nn.Embedding"]
    CommandScorer --> EncoderGRU["encoder_gru"]
    CommandScorer --> CmdEncoderGRU["cmd_encoder_gru"]
    CommandScorer --> StateGRU["state_gru"]
    CommandScorer --> Critic["nn.Linear (critic)"]
    CommandScorer --> AttCmd["nn.Linear (att_cmd)"]
    
    AgentInterface --> InfosToRequest["infos_to_request property"]
    InfosToRequest --> Description["description=True"]
    InfosToRequest --> Inventory["inventory=True"]
    InfosToRequest --> AdmissibleCommands["admissible_commands=True"]
```

The tutorial covers:
- Simple random baseline agent implementation
- Neural agent with attention mechanism over commands
- Training loop with policy gradient methods
- Evaluation and testing procedures
- Game generation with different difficulty settings

Training uses games generated with `tw-make tw-simple` with various reward densities and goal specifications.

Sources: [notebooks/Building a simple agent.ipynb:157-186](), [notebooks/Building a simple agent.ipynb:314-535](), [notebooks/Building a simple agent.ipynb:637-653]()

### Game Creation Tutorial

The handcrafting tutorial demonstrates how to programmatically create custom text-based games using the `GameMaker` API.

#### Game Construction Workflow

```mermaid
graph TD
    GameMaker["M = GameMaker()"] --> CreateRooms["M.new_room()"]
    CreateRooms --> ConnectRooms["M.connect(roomA.east, roomB.west)"]
    ConnectRooms --> SetPlayer["M.set_player(room)"]
    SetPlayer --> AddObjects["M.new(type='o/s/c/d/k/f')"]
    AddObjects --> SetProperties["obj.infos.desc, obj.add()"]
    SetProperties --> CreateQuest["M.new_quest()"]
    CreateQuest --> AddEvents["quest.add_event()"]
    AddEvents --> BuildGame["M.build()"]
    BuildGame --> CompileGame["textworld.generator.compile_game()"]
    
    AddObjects --> ObjectTypes["'r': room, 'd': door, 'c': container,<br/>'s': supporter, 'o': object, 'k': key,<br/>'f': food, 'oven': oven, 'stove': stove"]
```

The tutorial covers object types, room connections, quest creation, and game compilation to playable formats.

Sources: [notebooks/Handcrafting a game.ipynb:45-63](), [notebooks/Handcrafting a game.ipynb:174-187]()

## Training Environments and Test Games

TextWorld provides various pre-configured training environments that demonstrate different learning challenges:

### Simple Test Games

The tutorials use a handcrafted world layout for consistent training:
```
                     Bathroom
                        +
                        |
                        +
    Bedroom +-(d1)-+ Kitchen +--(d2)--+ Backyard
      (P)               +                  +
                        |                  |
                        +                  +
                   Living Room           Garden
```

This environment supports different reward configurations:
- **Dense rewards**: Frequent positive feedback for progress
- **Balanced rewards**: Moderate feedback frequency  
- **Sparse rewards**: Minimal feedback, only at goal completion

Goal descriptions can be:
- **Detailed**: Explicit instructions provided
- **Brief**: Goal mentioned but minimal instructions
- **None**: No explicit goal, requires exploration

Sources: [notebooks/Building a simple agent.ipynb:105-133](), [notebooks/Building a simple agent.ipynb:144-151]()

## Performance Evaluation

The tutorials demonstrate systematic evaluation approaches comparing random baselines with trained agents across different game configurations. Training typically involves 500 episodes on single games or 100 games for better generalization.

Sources: [notebooks/Building a simple agent.ipynb:677-721](), [notebooks/Building a simple agent.ipynb:740-796]()

---

