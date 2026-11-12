> 来源: [https://deepwiki.com/pytorch/ELF/5-training-system](https://deepwiki.com/pytorch/ELF/5-training-system)
> DeepWiki pytorch/ELF | Last indexed: 23 April 2025 (e851e7

# Training System

  Relevant source files 
 - [scripts/elfgames/go/df_console.py](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/df_console.py)
 - [scripts/elfgames/go/selfplay.py](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py)
 - [scripts/elfgames/go/train.py](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py)
 
  The Training System in ELF OpenGo is a sophisticated reinforcement learning infrastructure that enables self-play based training of Go AI models through distributed computing. This page details the core components, architecture, and workflow of the training system, focusing on the implementation details of model training through self-play.

 For information about the specific Game Logic used in training, see [Game Logic](https://deepwiki.com/pytorch/ELF/3-game-logic). For details on Monte Carlo Tree Search integration, see [Monte Carlo Tree Search](https://deepwiki.com/pytorch/ELF/4-monte-carlo-tree-search-(mcts)).

 
## Architecture Overview

 The Training System uses a distributed client-server architecture to efficiently manage the training process and distribute workloads.

 
```

```

 Sources: [scripts/elfgames/go/train.py52-56](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L52-L56) [scripts/elfgames/go/selfplay.py143-156](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L143-L156)

 
## Core Components

 
### Model Versioning System

 The training system uses a versioned approach to model management, tracking models with increasing version numbers.

 
```

```

 Sources: [scripts/elfgames/go/train.py52-56](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L52-L56) [scripts/elfgames/go/train.py122-127](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L122-L127)

 
### Training Process

 The training process is responsible for consuming game data from self-play, updating model parameters, and managing model versions.

 
```

```

 Sources: [scripts/elfgames/go/train.py44-48](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L44-L48) [scripts/elfgames/go/train.py70-78](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L70-L78) [scripts/elfgames/go/train.py117-120](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L117-L120) [scripts/elfgames/go/train.py136-138](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L136-L138)

 
## Training Workflow

 
### Self-Play Data Generation

 Self-play is the process where neural network models play against each other to generate training data.

 
 - Two actor models (black and white) are loaded from saved models
 - Games are played using Monte Carlo Tree Search guided by the neural networks
 - Game outcomes and board positions are recorded as training data
 - Statistics like win rates are tracked to monitor progress
 
 
```

```

 Sources: [scripts/elfgames/go/selfplay.py87-111](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L87-L111) [scripts/elfgames/go/selfplay.py138-157](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L138-L157) [scripts/elfgames/go/selfplay.py172-196](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L172-L196)

 
### Model Training Process

 The training process updates model parameters based on self-play data.

 
 - The server loads an initial model
 - Self-play clients generate game data with the current model version
 - The server trains on batches of game data
 - When sufficient improvement is observed, a new model version is created
 - Self-play clients are notified to load the new model version
 
 
```

```

 Sources: [scripts/elfgames/go/train.py70-78](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L70-L78) [scripts/elfgames/go/train.py80-102](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L80-L102) [scripts/elfgames/go/train.py122-127](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L122-L127)

 
## Key Implementation Features

 
### Version Management and Synchronization

 The training system carefully manages model versions to ensure consistency between training and self-play.

 
 - Each model is saved with a version number: `save-<version>.bin`
 - Self-play clients track which model version generated each batch of data
 - The training process checks version compatibility before training on a batch
 - A synchronization mechanism ensures sufficient self-play data is available for each model version
 
 **Version Detection and Loading:**

 
```
model_filename = model_loader.options.load
if isinstance(model_filename, str) and model_filename != "":
    realpath = os.path.realpath(model_filename)
    m = matcher.match(os.path.basename(realpath))
    if m:
        model_ver = int(m.group(1))
```

 Sources: [scripts/elfgames/go/train.py52-56](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L52-L56) [scripts/elfgames/go/train.py70-78](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L70-L78)

 
### Training Control Flow

 The training system implements a control flow that manages when to train on batches and when to update model versions.

 
```

```

 Sources: [scripts/elfgames/go/train.py70-78](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L70-L78) [scripts/elfgames/go/train.py122-127](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L122-L127)

 
### Batch Statistics and Monitoring

 The training system includes monitoring capabilities to track progress and performance.

 
| Statistic | Description | Implementation |
|---|---|---|
| Batch Usage | Percentage of available batch capacity used | self.total_sel_batchsize / self.total_batchsize |
| Win Rate | Percentage of games won by black player | 100.0 * wr.black_wins / wr.total_games |
| Actor Count | Number of actors (players) in the system | self.actor_count |
| Total Games | Total number of games played | wr.total_games |

 Sources: [scripts/elfgames/go/selfplay.py33-48](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L33-L48) [scripts/elfgames/go/selfplay.py158-170](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L158-L170)

 
## Execution Modes

 The training system supports different execution modes to accommodate various training scenarios.

 
```

```

 Sources: [scripts/elfgames/go/train.py136-138](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L136-L138) [scripts/elfgames/go/selfplay.py109-111](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L109-L111) [scripts/elfgames/go/df_console.py44-56](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/df_console.py#L44-L56)

 
## Evaluation and Analysis

 The training system includes components for evaluating and analyzing model performance.

 
 - **Win Rate Analysis**: Tracks win rates between different model versions
 - **Batch Usage Statistics**: Monitors efficiency of the batch processing
 - **Game Statistics**: Collects comprehensive game outcome data
 - **Model Evaluation**: Provides mechanisms to evaluate model performance against previous versions
 
 Sources: [scripts/elfgames/go/selfplay.py33-48](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L33-L48) [scripts/elfgames/go/selfplay.py158-170](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L158-L170)

 
## Integration Points

 The Training System integrates with several other components of the ELF OpenGo platform:

 
 - **Game Logic**: Provides the rules and board representation for self-play
 - **MCTS**: Provides the tree search algorithm for game playing
 - **Neural Network Models**: Provides the policy and value networks for guiding MCTS
 - **Distributed Communication**: Enables communication between server and clients
 
 This integration creates a complete reinforcement learning system capable of training superhuman Go AI through self-play.
