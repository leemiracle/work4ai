> 来源: [https://deepwiki.com/pytorch/ELF/3-game-logic](https://deepwiki.com/pytorch/ELF/3-game-logic)
> DeepWiki pytorch/ELF | Last indexed: 23 April 2025 (e851e7

# Game Logic

  Relevant source files 
 - [design_doc/go_game.md](https://github.com/pytorch/ELF/blob/e851e786/design_doc/go_game.md?plain=1)
 - [src_cpp/elf/base/ctrl.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/base/ctrl.h)
 - [src_cpp/elf/utils/utils.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/utils/utils.h)
 - [src_cpp/elfgames/go/base/board.cc](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc)
 - [src_cpp/elfgames/go/base/board_feature.cc](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board_feature.cc)
 
  
## Purpose and Scope

 This document describes the Game Logic component in the ELF OpenGo platform. The Game Logic implements the rules of the game of Go, manages the board state, and provides interfaces for move validation, execution, and feature extraction for neural network processing. It serves as the foundation upon which the Monte Carlo Tree Search operates.

 For information about the Monte Carlo Tree Search implementation that uses this Game Logic, see [Monte Carlo Tree Search (MCTS)](https://deepwiki.com/pytorch/ELF/4-monte-carlo-tree-search-(mcts)). For details on how features are extracted for neural network processing, see [Feature Extraction](https://deepwiki.com/pytorch/ELF/3.2-feature-extraction).

 
## Components Overview

 The Game Logic system consists of three primary components:

 
 - **Board Representation**: The data structures that represent the Go board state
 - **Go State Management**: Classes that manage game progression and history
 - **Board Features**: Functionality to extract features from the board for neural network input
 
 
```

```

 Sources: [src_cpp/elfgames/go/base/board.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.h) [design_doc/go_game.md45-62](https://github.com/pytorch/ELF/blob/e851e786/design_doc/go_game.md?plain=1#L45-L62)

 
## Board Representation

 The foundation of the Game Logic is the `Board` structure which provides a compact and efficient representation of a Go board.

 
### Basic Types

 
```
Coord: unsigned short         // Board coordinate
Stone: unsigned char          // Stone color (BLACK, WHITE, EMPTY, OFF_BOARD)
struct Info                   // Information for each intersection
struct Group                  // Connected group of stones
```

 These basic types are used to represent the state of the board. The coordinate system uses a single index representation rather than x,y coordinates, with helper macros to convert between the two.

 Sources: [design_doc/go_game.md7-17](https://github.com/pytorch/ELF/blob/e851e786/design_doc/go_game.md?plain=1#L7-L17)

 
### Board Structure

 The `Board` structure contains the full representation of a Go board position:

 
```
struct Board {
    Info _infos[BOARD_EXPAND_SIZE * BOARD_EXPAND_SIZE]; // Board state
    Group _groups[MAX_GROUP];                          // Groups of stones
    Stone _next_player;                                // Player to move
    int _ply;                                          // Move number
    Coord _last_move, _last_move2, _last_move3;        // Recent moves
    Coord _simple_ko;                                  // Ko point
    uint64_t _hash;                                    // Position hash
    short _b_cap, _w_cap;                              // Captured stones
    int _num_groups;                                   // Active groups
}
```

 The board is represented as a 1D array with padding around the edges, simplifying the handling of edge cases in the implementation.

 Sources: [design_doc/go_game.md18-21](https://github.com/pytorch/ELF/blob/e851e786/design_doc/go_game.md?plain=1#L18-L21) [src_cpp/elfgames/go/base/board.cc33-106](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L33-L106)

 
### Board Operations

 The board implementation supports critical operations including:

 
```

```

 Sources: [src_cpp/elfgames/go/base/board.cc425-827](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L425-L827) [src_cpp/elfgames/go/base/board.cc850-1002](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L850-L1002) [src_cpp/elfgames/go/base/board.cc1849-2000](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L1849-L2000)

 
## Go State Management

 
### GoState Class

 The `GoState` class wraps the raw `Board` structure and provides higher-level game management functionality:

 
```

```

 This class manages the progression of the game, tracks the history of board positions, and enforces rules like superko (position repetition).

 Sources: [design_doc/go_game.md45-62](https://github.com/pytorch/ELF/blob/e851e786/design_doc/go_game.md?plain=1#L45-L62)

 
### GoStateExt Class

 The `GoStateExt` class extends `GoState` to support additional functionality needed for AI training and playing:

 
```

```

 This class supports online behavior like recording MCTS policies and value predictions, determining when to resign, and exporting game records in SGF format.

 Sources: [design_doc/go_game.md64-85](https://github.com/pytorch/ELF/blob/e851e786/design_doc/go_game.md?plain=1#L64-L85)

 
### GoStateExtOffline Class

 For offline training, the `GoStateExtOffline` class provides additional functionality:

 
```

```

 This class supports features needed for training, like applying random symmetries to the board and processing game records.

 Sources: [design_doc/go_game.md86-101](https://github.com/pytorch/ELF/blob/e851e786/design_doc/go_game.md?plain=1#L86-L101)

 
## Feature Extraction

 The `BoardFeature` class is responsible for converting the raw board state into feature planes that can be processed by neural networks.

 
```

```

 Sources: [design_doc/go_game.md103-122](https://github.com/pytorch/ELF/blob/e851e786/design_doc/go_game.md?plain=1#L103-L122) [src_cpp/elfgames/go/base/board_feature.cc16-290](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board_feature.cc#L16-L290)

 
### Standard Features

 The `extract()` method creates a standard feature set including:

 
 - Liberty information (our liberties, opponent liberties)
 - Stone positions (our stones, opponent stones, empty positions)
 - History information (our history, opponent history)
 - Ko points, distance maps, and other derived features
 
 These features provide a rich representation of the board state for the neural network.

 Sources: [src_cpp/elfgames/go/base/board_feature.cc204-237](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board_feature.cc#L204-L237)

 
### AlphaGo Zero Style Features

 The `extractAGZ()` method creates AlphaGo Zero style features:

 
 - History planes for the current player (past 8 states)
 - History planes for the opponent (past 8 states)
 - Player color indicator
 
 This simpler representation follows the approach described in the AlphaGo Zero paper.

 Sources: [src_cpp/elfgames/go/base/board_feature.cc239-290](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board_feature.cc#L239-L290)

 
## Implementation Details

 
### Board Representation Internals

 The board uses a 1D array representation with padding to simplify edge detection. The actual board coordinates are mapped to this array using offset calculations. Groups of connected stones are tracked using linked lists through the `_infos[c].next` field, allowing efficient traversal of stone groups.

 Sources: [src_cpp/elfgames/go/base/board.cc38-63](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L38-L63)

 
### Move Execution Process

 When a move is played, the system:

 
 - Validates the move using `TryPlay()` (checking for ko, suicide, off-board)
 - Analyzes the impact on neighboring groups using `StoneLibertyAnalysis()`
 - Executes the move with `Play()`: 
 - Updates the stone at the played position
 - Captures opponent groups with no liberties
 - Merges friendly groups connected by the new stone
 - Updates liberties for all affected groups
 - Updates ko points and history
 
 Sources: [src_cpp/elfgames/go/base/board.cc786-828](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L786-L828) [src_cpp/elfgames/go/base/board.cc1297-1401](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L1297-L1401)

 
### Group Management

 Groups of connected stones are managed using:

 
 - `createNewGroup()`: Creates a new group for an isolated stone
 - `MergeToGroup()`: Adds a stone to an existing group
 - `MergeGroups()`: Combines two groups when they become connected
 - `EmptyGroup()`: Removes a captured group
 - `RecomputeGroupLiberties()`: Updates liberty count for a group
 
 Sources: [src_cpp/elfgames/go/base/board.cc661-782](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L661-L782)

 
### Liberty Tracking

 The implementation optimizes liberty tracking, a critical operation in Go:

 
 - Each group maintains its liberty count
 - When stones are added or removed, liberties are incrementally updated
 - `RecomputeGroupLiberties()` performs a full recount when needed
 - Specialized functions like `getLibertyMap()` and `getLibertyMap3()` extract liberty information for feature planes
 
 Sources: [src_cpp/elfgames/go/base/board.cc754-782](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board.cc#L754-L782) [src_cpp/elfgames/go/base/board_feature.cc43-115](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/base/board_feature.cc#L43-L115)

 
## Game Logic Integration with System

 The Game Logic component integrates with the rest of the ELF OpenGo system as follows:

 
```

```

 The Game Logic provides the foundation for the MCTS algorithm, which uses it to represent and advance game states. The feature extraction feeds into the training pipeline, while the Go state management integrates with the self-play process.

 Sources: Core Framework diagram from the provided system architecture diagrams.

 
## Conclusion

 The Game Logic implementation in ELF OpenGo provides an efficient, flexible foundation for representing the game of Go, enforcing its rules, and extracting features for neural network processing. Its C++ implementation balances performance needs with the complexity of Go rules, supporting the demanding requirements of self-play reinforcement learning.

 The key strengths of this implementation include:

 
 - Efficient board representation and group tracking
 - Comprehensive rule enforcement
 - Flexible feature extraction for different neural network architectures
 - Integration with both online play and offline training systems
 
 These elements together enable the core functionality needed for AlphaGo-style reinforcement learning for the game of Go.

 Sources: Integration of all provided files and diagrams.
