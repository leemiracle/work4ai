> 来源: [https://deepwiki.com/pytorch/ELF/6-execution-modes](https://deepwiki.com/pytorch/ELF/6-execution-modes)
> DeepWiki pytorch/ELF | Last indexed: 23 April 2025 (e851e7

# Execution Modes

  Relevant source files 
 - [README.rst](https://github.com/pytorch/ELF/blob/e851e786/README.rst)
 - [scripts/elfgames/go/df_console.py](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/df_console.py)
 - [scripts/elfgames/go/selfplay.py](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py)
 - [scripts/elfgames/go/train.py](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py)
 
  
## Overview

 ELF OpenGo can be executed in multiple modes, each designed for a specific purpose in the development, training, and deployment of Go-playing AI systems. This document details the different execution modes available in the ELF OpenGo platform, how to configure them, and their typical use cases. The execution modes represent different entry points into the system with varying behaviors and configurations.

 For information about the runners that execute these modes, see [Execution Runners](https://deepwiki.com/pytorch/ELF/5.3-execution-runners).

 
## Execution Mode Architecture

 The ELF OpenGo platform supports five primary execution modes, each implemented as separate entry points with specific configuration options and behaviors.

 
```

```

 Sources: [README.rst115-168](https://github.com/pytorch/ELF/blob/e851e786/README.rst#L115-L168) [scripts/elfgames/go/train.py23-144](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L23-L144) [scripts/elfgames/go/selfplay.py1-202](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L1-L202) [scripts/elfgames/go/df_console.py1-86](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/df_console.py#L1-L86)

 
## Mode Descriptions

 
### 1. Training Mode

 Training mode is used to train the neural network models through reinforcement learning. It coordinates both model training and data generation through self-play.

 
#### Configuration and Usage

 Training mode is executed through `train.py` and typically operates in a distributed environment with:

 
 - A server process that runs the training loop
 - Multiple client processes that generate self-play data
 
 
```

```

 Key components and workflow:

 
 - The training script initializes a `GameContext` and registers callbacks for training
 - Models are versioned and saved to a specified directory
 - The server manages version control and notifies clients when new models are available
 - Supports both online and offline training modes
 
 Example command:

 
```

```

 Sources: [scripts/elfgames/go/train.py23-144](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L23-L144) [README.rst119-135](https://github.com/pytorch/ELF/blob/e851e786/README.rst#L119-L135)

 
### 2. Self-Play Mode

 Self-play mode is used to generate game data by having the AI play against itself. This data is then used for training.

 
#### Configuration and Usage

 Self-play mode is executed through `selfplay.py` and typically runs as multiple client processes that:

 
 - Load models from a specified location
 - Generate self-play games using these models
 - Report game statistics and results
 - Send game data to the training server
 
 
```

```

 Key components and workflow:

 
 - Loads specified model versions for black and white players
 - Supports evaluating specific model pairs against each other
 - Collects statistics on batch utilization and win rates
 - Can be configured to terminate after a specified number of games
 
 Example command:

 
```

```

 Sources: [scripts/elfgames/go/selfplay.py1-202](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L1-L202) [README.rst119-135](https://github.com/pytorch/ELF/blob/e851e786/README.rst#L119-L135)

 
### 3. GTP Mode

 GTP (Go Text Protocol) mode provides an interface for the AI to play against external Go programs or human players through a standardized protocol.

 
#### Configuration and Usage

 GTP mode is executed through `gtp.sh` and sets up a GTP-compliant interface for the AI:

 
 - Loads a pretrained model
 - Sets up MCTS parameters for optimal play
 - Accepts GTP commands and returns responses
 
 
```

```

 Key parameters for GTP mode:

 
 - `--mcts_puct`: Controls exploration vs. exploitation in MCTS (default: 1.50)
 - `--batchsize`: Neural network batch size (default: 16)
 - `--mcts_rollout_per_thread`: Controls thinking time per move (default: 8192)
 - `--resign_thres`: Resignation threshold (default: 0.05)
 
 Example command:

 
```

```

 Sources: [README.rst136-152](https://github.com/pytorch/ELF/blob/e851e786/README.rst#L136-L152)

 
### 4. Analysis Mode

 Analysis mode is used to analyze existing Go games (in SGF format) move by move, providing AI evaluations and alternative suggestions.

 
#### Configuration and Usage

 Analysis mode is executed through `analysis.sh` and:

 
 - Loads a specified model
 - Analyzes an existing SGF file
 - Generates detailed tree files with search information for each move
 - Can start analysis from a specific move in the game
 
 
```

```

 Key parameters for analysis mode:

 
 - `--preload_sgf`: Path to the SGF file to analyze
 - `--preload_sgf_move_to`: Move number to start analysis from
 - `--dump_record_prefix`: Prefix for the generated tree files
 
 Example command:

 
```

```

 Sources: [README.rst153-168](https://github.com/pytorch/ELF/blob/e851e786/README.rst#L153-L168)

 
### 5. Debug Console Mode

 Debug console mode provides an interactive console for debugging and testing the AI system.

 
#### Configuration and Usage

 Debug console mode is executed through `df_console.py` and:

 
 - Sets up an interactive console with GTP capabilities
 - Allows direct interaction with the AI system
 - Supports debugging of model behavior and game state
 
 
```

```

 Key components:

 
 - `GoConsoleGTP`: Provides the console interface with GTP support
 - Evaluator: Handles model evaluation for the console
 - Human actor callback: Processes human input
 - AI actor callback: Processes AI responses
 
 Example command:

 
```

```

 Sources: [scripts/elfgames/go/df_console.py1-86](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/df_console.py#L1-L86)

 
## Execution Mode Selection

 The following table summarizes when to use each execution mode:

 
| Mode | Entry Point | Primary Use Case | Key Components |
|---|---|---|---|
| Training | train.py | Training neural network models | MultiProcessRunner, Trainer |
| Self-Play | selfplay.py | Generating game data for training | SingleProcessRunner, Evaluator |
| GTP | gtp.sh | Playing against external programs/humans | TreeSearch, ModelInterface |
| Analysis | analysis.sh | Analyzing existing Go games | TreeSearch, SGF parsing |
| Debug Console | df_console.py | Interactive debugging and testing | GoConsoleGTP, Evaluator |

 Sources: [README.rst115-168](https://github.com/pytorch/ELF/blob/e851e786/README.rst#L115-L168) [scripts/elfgames/go/train.py23-144](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/train.py#L23-L144) [scripts/elfgames/go/selfplay.py1-202](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/selfplay.py#L1-L202) [scripts/elfgames/go/df_console.py1-86](https://github.com/pytorch/ELF/blob/e851e786/scripts/elfgames/go/df_console.py#L1-L86)

 
## Common Configuration Parameters

 Many configuration parameters are shared across execution modes:

 
```

```

 The configuration options vary slightly between modes but generally allow control over:

 
 - Neural network architecture and model loading
 - MCTS search parameters
 - Hardware resource allocation
 - Game and evaluation settings
 
 Sources: [README.rst136-168](https://github.com/pytorch/ELF/blob/e851e786/README.rst#L136-L168)

 
## Conclusion

 ELF OpenGo's multiple execution modes allow it to serve different purposes throughout the AI development lifecycle. Each mode is specialized for a particular task, from training and self-play data generation to interactive play and game analysis. Understanding the different execution modes and their configuration options is essential for effectively using the ELF OpenGo platform.
