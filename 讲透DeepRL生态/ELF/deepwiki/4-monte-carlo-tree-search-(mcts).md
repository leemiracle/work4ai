> 来源: [https://deepwiki.com/pytorch/ELF/4-monte-carlo-tree-search-(mcts)](https://deepwiki.com/pytorch/ELF/4-monte-carlo-tree-search-(mcts))
> DeepWiki pytorch/ELF | Last indexed: 23 April 2025 (e851e7

# Monte Carlo Tree Search (MCTS)

  Relevant source files 
 - [design_doc/mcts.md](https://github.com/pytorch/ELF/blob/e851e786/design_doc/mcts.md?plain=1)
 - [src_cpp/elf/ai/tree_search/tree_search.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h)
 
  This page provides a comprehensive explanation of the Monte Carlo Tree Search (MCTS) implementation in the ELF OpenGo platform. MCTS is a key decision-making algorithm that enables the system to select optimal moves in the game of Go by efficiently exploring game trees. This document focuses specifically on the implementation details, architecture, and integration with other components of the codebase.

 For information about neural network integration with MCTS, see [Neural Network Integration](https://deepwiki.com/pytorch/ELF/4.2-neural-network-integration). For details about the training system that uses MCTS to generate self-play games, see [Training System](https://deepwiki.com/pytorch/ELF/5-training-system).

 
## Overview

 Monte Carlo Tree Search is implemented in ELF OpenGo as a template-based C++ library that combines traditional MCTS with neural network evaluation, following the approach introduced in the AlphaGo Zero paper. The implementation is designed to be both flexible and high-performance, supporting multithreaded execution for efficient tree search.

 The MCTS component sits between the Go game logic and the training system, using neural networks to evaluate board positions and guide the search process:

 
```

```

 Sources: [src_cpp/elf/ai/tree_search/tree_search.h326-529](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L326-L529)

 
## Core Components

 
### TreeSearchT

 The `TreeSearchT` class is the main orchestrator of the tree search process, managing multiple search threads and coordinating the overall search.

 
```

```

 Key methods:

 
 - `run(const State& root_state)`: Starts the tree search from the given root state and returns the best action
 - `treeAdvance(const Action& action)`: Advances the tree after an action is selected, preserving relevant subtree
 - `runPolicyOnly(const State& root_state)`: Quick evaluation using only the policy network
 
 Sources: [src_cpp/elf/ai/tree_search/tree_search.h326-529](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L326-L529)

 
### TreeSearchSingleThreadT

 Each instance of `TreeSearchSingleThreadT` runs on a separate thread and performs MCTS operations independently. Multiple threads share the same search tree to collaboratively build it.

 Key methods:

 
 - `run(int run_id, const std::atomic_bool* stop_search, Actor& actor, SearchTree& search_tree)`: Performs tree search operations on a single thread
 - `batch_rollouts(const RunContext& ctx, Node* root, Actor& actor, SearchTree& search_tree)`: Executes multiple rollouts in a batch
 - `single_rollout(RunContext ctx, Node* root, Actor& actor, SearchTree& search_tree)`: Executes a single MCTS rollout from root to leaf
 
 Sources: [src_cpp/elf/ai/tree_search/tree_search.h65-323](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L65-L323)

 
### NodeT

 The `NodeT` class represents a node in the search tree, storing the game state and statistics for each possible action from that state.

 Key methods:

 
 - `findMove(const AlgOpt& alg_opt, int depth, Action* action)`: Selects the best action using UCT formula
 - `updateEdgeStats(const Action& action, float reward, int virtual_loss)`: Updates statistics after simulation
 - `followEdge(const Action& action, SearchTree& tree)`: Navigates to child node, creating it if necessary
 - `addVirtualLoss(const Action& action, int virtual_loss)`: Adds temporary loss to discourage thread collision
 
 Sources: [src_cpp/elf/ai/tree_search/tree_search_node.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search_node.h)

 
### SearchTreeT

 The `SearchTreeT` class manages the entire tree structure, handling node creation, deletion, and tree advancement.

 Key methods:

 
 - `getRootNode()`: Returns the root node of the tree
 - `addNode(float parent_q)`: Creates and adds a new node to the tree
 - `treeAdvance(const Action& action)`: Moves the root to the selected child node and prunes other branches
 - `clear()`: Resets the entire tree
 
 Sources: [src_cpp/elf/ai/tree_search/tree_search_node.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search_node.h)

 
## MCTS Algorithm Implementation

 The MCTS implementation in ELF OpenGo follows four phases with specific adaptations for Go and neural network integration:

 
```

```

 Sources: [src_cpp/elf/ai/tree_search/tree_search.h347-368](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L347-L368) [src_cpp/elf/ai/tree_search/tree_search.h200-258](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L200-L258)

 
### Selection

 In the selection phase, the UCT (Upper Confidence Bound for Trees) formula is used to balance exploration and exploitation:

 
```
UCT = Q(s,a) + c_puct * P(s,a) * sqrt(N(s)) / (1 + N(s,a))
```

 Where:

 
 - `Q(s,a)` is the mean action value
 - `P(s,a)` is the prior probability from the policy network
 - `N(s)` is the visit count of the parent node
 - `N(s,a)` is the visit count of the edge
 - `c_puct` is the exploration constant
 
 Sources: [src_cpp/elf/ai/tree_search/tree_search_node.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search_node.h)

 
### Expansion and Evaluation

 When a leaf node is reached, the implementation:

 
 - Allocates a new state by applying the selected action
 - Evaluates the state using the neural network to get policy and value estimates
 - Creates child nodes for possible actions
 
 For efficiency, the implementation batches multiple leaf evaluations together before calling the neural network.

 Sources: [src_cpp/elf/ai/tree_search/tree_search.h174-190](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L174-L190) [src_cpp/elf/ai/tree_search/tree_search.h235-244](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L235-L244)

 
### Backpropagation

 After evaluation, the value is backed up through all nodes in the path, updating:

 
 - Edge visit counts
 - Q-values (mean action values)
 - Removing virtual losses applied during selection
 
 Sources: [src_cpp/elf/ai/tree_search/tree_search.h247-258](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L247-L258)

 
### Action Selection

 After the search completes, the best action is selected using one of three methods:

 
 - **strongest_prior**: Selects action with highest prior probability
 - **most_visited**: Selects most visited action (default for playing)
 - **uniform_random**: Selects randomly according to visit counts (useful for training)
 
 Sources: [src_cpp/elf/ai/tree_search/tree_search.h495-527](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L495-L527)

 
## Multithreading and Performance Optimizations

 The MCTS implementation uses several techniques to achieve high performance:

 
### Parallel Tree Search

 Multiple threads execute tree search operations simultaneously on a shared tree:

 
```

```

 Sources: [src_cpp/elf/ai/tree_search/tree_search.h347-368](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L347-L368)

 
### Virtual Loss

 To prevent multiple threads from exploring the same paths simultaneously, a virtual loss is applied when a thread selects an action, making it temporarily less attractive to other threads.

 
```

```

 Sources: [src_cpp/elf/ai/tree_search/tree_search.h286-288](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L286-L288)

 
### Batch Evaluation

 Leaf nodes are evaluated in batches to efficiently utilize GPU resources when running neural network inference:

 
```

```

 Sources: [src_cpp/elf/ai/tree_search/tree_search.h235-238](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L235-L238)

 
### Tree Reuse

 When advancing the tree after a move is played, the implementation keeps the relevant subtree and discards the rest, preserving valuable computation:

 
```

```

 Sources: [src_cpp/elf/ai/tree_search/tree_search.h428-430](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h#L428-L430)

 
## Integration with Go Game Logic

 The MCTS component integrates with Go-specific logic through template specialization and the Actor interface.

 
### GoState and Board Representation

 The generic `State` parameter in the MCTS templates is implemented as `GoState` which encapsulates the Go board representation and rules.

 
```

```

 Sources: [src_cpp/elfgames/go/game/game_state.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/game/game_state.h)

 
### Actor Interface

 The `Actor` concept bridges MCTS and neural network evaluation. For Go, this is implemented in `MCTSActor`:

 Key methods:

 
 - `evaluate(const GoState& s, NodeResponse* resp)`: Processes the state through the neural network
 - `forward(GoState& s, const Coord& c)`: Applies a move to the state
 - `reward(const GoState& s, float)`: Computes the reward/value of a terminal state
 
 Sources: [src_cpp/elfgames/go/mcts/mcts.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/mcts/mcts.h)

 
## Usage Modes

 MCTS is used in different ways depending on the execution mode:

 
### Training and Self-Play

 During training, MCTS generates self-play games that are used as training data for the neural network. The search parameters are configured to generate diverse and challenging games:

 
```
--num_rollouts=800 --num_threads=32 --explore_exploit_ratio=0.25
```

 Sources: [src_cpp/elfgames/go/train/client_manager.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/train/client_manager.h)

 
### GTP Mode

 In GTP (Go Text Protocol) mode, MCTS is used to power the bot when playing against other programs. The search is typically deeper with different parameters:

 
```
--num_rollouts=1600 --num_threads=16 --explore_exploit_ratio=0.1
```

 Sources: [src_cpp/elfgames/go/gtp/gtp_player.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/gtp/gtp_player.h)

 
### Analysis Mode

 In analysis mode, MCTS evaluates board positions and suggests moves, providing statistics like win rate and visit counts for each option.

 Sources: [src_cpp/elfgames/go/analysis/analyzer.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elfgames/go/analysis/analyzer.h)

 
## Conclusion

 The MCTS implementation in ELF OpenGo provides a high-performance, multithreaded framework for decision-making in Go. By integrating neural network evaluation with classic MCTS, the system achieves strong gameplay while maintaining an efficient and flexible architecture.

 The implementation effectively balances exploration and exploitation, makes efficient use of computational resources through batching and multithreading, and seamlessly integrates with both the Go game logic and the neural network training pipeline.

 For more information on how this MCTS implementation fits into the larger training pipeline, refer to [Training System](https://deepwiki.com/pytorch/ELF/5-training-system).

 Sources: [src_cpp/elf/ai/tree_search/tree_search.h](https://github.com/pytorch/ELF/blob/e851e786/src_cpp/elf/ai/tree_search/tree_search.h) [design_doc/mcts.md](https://github.com/pytorch/ELF/blob/e851e786/design_doc/mcts.md?plain=1)
