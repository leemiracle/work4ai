> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/3-rmaxts-algorithm](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/3-rmaxts-algorithm)
> DeepWiki deepseek-ai/DeepSeek-Prover-V1.5

# RMaxTS Algorithm

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1)
 - [configs/RMaxTS.py](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py)
 
  
## Purpose and Scope

 This document provides an overview of the RMaxTS (Reward Maximizing Tree Search) algorithm, a core component of the DeepSeek-Prover-V1.5 system. RMaxTS is an advanced proof search algorithm that combines Monte-Carlo Tree Search with an intrinsic reward mechanism to systematically explore diverse proof paths in the Lean 4 proof assistant. For information about other proof search algorithms in the system, see [Sampling Algorithm](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/3.1-sampling-algorithm) and [Few-Shot Sampling](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/3.2-few-shot-sampling).

 
## Algorithm Overview

 As described in the repository documentation, RMaxTS is "a variant of Monte-Carlo tree search that employs an intrinsic-reward-driven exploration strategy to generate diverse proof paths." This approach represents a significant advancement over the single-pass whole-proof generation method used in previous systems by enabling more systematic exploration of possible proof strategies guided by feedback from the Lean 4 proof assistant.

 The algorithm is implemented in the repository's prover module as imported in [configs/RMaxTS.py2](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L2-L2):

 
```

```

 
## System Integration

 
```

```

 Sources: [README.md52-83](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L52-L83)

 
## Search Process

 
```

```

 Sources: [README.md57-61](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L57-L61) [configs/RMaxTS.py26-35](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L26-L35)

 
## Configuration

 The RMaxTS algorithm is configured in [configs/RMaxTS.py](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py) which defines the parameters for the search process:

 
```

```

 Sources: [configs/RMaxTS.py26-35](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L26-L35)

 
### Parameter Descriptions

 
| Parameter | Value | Description |
|---|---|---|
| gamma | 0.99 | Discount factor for future rewards in the reinforcement learning component |
| sample_num | 6400 | Number of samples/proof attempts to generate during search |
| concurrent_num | 32 | Number of concurrent operations for parallelized search |
| tactic_state_comment | True | Whether to include tactic state comments in the proof |
| ckpt_interval | 128 | Interval for saving checkpoints during search |
| log_interval | 32 | Interval for logging information during search |
| n_search_procs | 256 | Number of search processes to run in parallel |

 Sources: [configs/RMaxTS.py26-35](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L26-L35) [configs/RMaxTS.py26](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L26-L26)

 
### System and Model Configuration

 RMaxTS operates within a broader system configuration that includes:

 
```

```

 Sources: [configs/RMaxTS.py5-23](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L5-L23) [configs/RMaxTS.py10-13](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L10-L13) [configs/RMaxTS.py16-23](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L16-L23)

 
## Performance Results

 When combined with the DeepSeek-Prover-V1.5-RL model, RMaxTS achieves state-of-the-art results on mathematical theorem proving benchmarks:

 
| Approach | miniF2F Test | ProofNet |
|---|---|---|
| ReProver | 26.5% | 13.8% |
| GPT-f | 36.6% | - |
| Hypertree Proof Search | 41.0% | - |
| InternLM2-StepProver | 54.5% | 18.1% |
| DeepSeek-Prover-V1 | 50.0% | - |
| DeepSeek-Prover-V1.5-Base | 42.2% | 13.2% |
| DeepSeek-Prover-V1.5-SFT | 57.4% | 22.9% |
| DeepSeek-Prover-V1.5-RL | 60.2% | 22.6% |
| DeepSeek-Prover-V1.5-RL + RMaxTS | 63.5% | 25.3% |

 Sources: [README.md70-82](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L70-L82)

 
## Technical Details

 The RMaxTS algorithm enhances traditional Monte-Carlo Tree Search by incorporating intrinsic rewards to guide exploration. Unlike standard proof generation approaches that produce a single complete proof, RMaxTS:

 
 - Generates multiple proof candidates using the language model
 - Systematically explores these candidates to find viable proof paths
 - Leverages feedback from the Lean 4 proof assistant to calculate intrinsic rewards
 - Uses these rewards to guide further exploration toward promising paths
 - Dynamically refines proof attempts based on verification results
 
 The discount factor (gamma=0.99) ensures that the algorithm properly balances immediate rewards with long-term potential, allowing it to effectively navigate complex proof spaces.

 Sources: [README.md57-61](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L57-L61) [configs/RMaxTS.py28](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/configs/RMaxTS.py#L28-L28)

 
## Usage

 To run the RMaxTS algorithm with the configured parameters, use the following command:

 
```

```

 Results can be summarized using:

 
```

```

 Sources: [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
## Comparison with Other Approaches

 The RMaxTS algorithm represents a significant improvement over basic sampling approaches for theorem proving. While basic sampling (see [Sampling Algorithm](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/3.1-sampling-algorithm)) generates multiple independent proof attempts, RMaxTS leverages information gained from previous attempts to guide the search process, leading to more efficient exploration of the proof space.

 The performance results demonstrate that this approach is particularly effective when combined with reinforcement learning. The DeepSeek-Prover-V1.5-RL model trained with reinforcement learning from proof assistant feedback (RLPAF) provides a strong foundation, but its capabilities are further enhanced by the systematic exploration strategy of RMaxTS.

 Sources: [README.md61-65](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L61-L65) [README.md70-82](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L70-L82)
