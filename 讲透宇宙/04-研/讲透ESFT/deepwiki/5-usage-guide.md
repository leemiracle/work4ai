> 来源: [https://deepwiki.com/deepseek-ai/ESFT/5-usage-guide](https://deepwiki.com/deepseek-ai/ESFT/5-usage-guide)
> DeepWiki deepseek-ai/ESFT

# Usage Guide

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1)
 
  This guide provides comprehensive instructions for using the DeepSeek-Prover-V1.5 system to generate and verify mathematical proofs in Lean 4. It covers how to run proof search experiments with different algorithms, configure parameters, and evaluate results. For installation and setup information, see [Installation and Setup](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/1.1-installation-and-setup). For detailed explanations of the underlying algorithms, see [Proof Search Algorithms](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/2.2-proof-search-algorithms).

 
## 1. Basic Workflow

 DeepSeek-Prover-V1.5 follows a general workflow for theorem proving:

 
```

```

 Sources: [README.md134-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L134-L145)

 
## 2. Quick Start Examples

 
### 2.1 Using Transformers Library for Single Proof Generation

 For a quick test, you can use Hugging Face's Transformers library to generate proofs for individual problems:

 
```

```

 Sources: [README.md135-136](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L135-L136)

 
### 2.2 Running Proof Search with RMaxTS

 To run a complete proof search experiment using the RMaxTS algorithm:

 
```

```

 You can specify which GPUs to use:

 
```

```

 To summarize the results after completion:

 
```

```

 Sources: [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
## 3. Available Models and Algorithms

 DeepSeek-Prover-V1.5 offers three model variants and multiple algorithms for proof search:

 
```

```

 Sources: [README.md87-97](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L87-L97) [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
### 3.1 Model Selection Guide

 
| Model | Description | Best Use Case |
|---|---|---|
| DeepSeek-Prover-V1.5-Base | Base model pre-trained on DeepSeekMath-Base | General mathematical reasoning, few-shot learning |
| DeepSeek-Prover-V1.5-SFT | Supervised fine-tuned model | Improved theorem proving capabilities |
| DeepSeek-Prover-V1.5-RL | Reinforcement learning from proof assistant feedback | Highest performance, especially with RMaxTS |

 Sources: [README.md61-63](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L61-L63) [README.md87-97](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L87-L97)

 
### 3.2 Algorithm Selection Guide

 
| Algorithm | Configuration File | Description | Best Use With |
|---|---|---|---|
| RMaxTS | configs/RMaxTS.py | Monte-Carlo tree search with intrinsic rewards | DeepSeek-Prover-V1.5-RL |
| Basic Sampling | configs/sampling.py | Simple sampling strategy | Any model variant |
| Few-shot Sampling | configs/sampling_few_shot.py | Sampling with example proofs as guidance | DeepSeek-Prover-V1.5-Base |

 Sources: [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
## 4. Running Experiments

 
### 4.1 Configuring Experiments

 DeepSeek-Prover-V1.5 uses Python configuration files to set up experiments. The main configuration files are:

 
 - `configs/RMaxTS.py` - For RMaxTS algorithm
 - `configs/sampling.py` - For basic sampling
 - `configs/sampling_few_shot.py` - For few-shot sampling
 
 
```

```

 Sources: [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
### 4.2 Key Configuration Parameters

 The following table shows important parameters that can be configured for proof search experiments:

 
| Parameter | Description | Default | Location |
|---|---|---|---|
| algorithm | The proof search algorithm to use | - | All config files |
| model_path | Path to the DeepSeek-Prover model | - | All config files |
| dataset_path | Path to the problem dataset | - | All config files |
| sample_num | Number of samples to generate | 6400 (RMaxTS), 128 (Sampling) | Algorithm-specific |
| concurrent_num | Number of concurrent proof attempts | 32 (RMaxTS) | RMaxTS config |
| gamma | Discount factor for rewards | 0.99 | RMaxTS config |
| temperature | Sampling temperature | 1.0 | All config files |
| max_tokens | Maximum tokens per generation | 2048 | All config files |
| lean_timeout | Timeout for Lean verification (seconds) | 300 | All config files |
| n_search_procs | Number of search processes | 256 (RMaxTS), 64 (Sampling) | All config files |
| few_shot_num | Number of examples for few-shot learning | 3 | Few-shot config |

 Sources: [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
## 5. Using Different Proof Search Algorithms

 
### 5.1 RMaxTS Algorithm

 RMaxTS is a variant of Monte-Carlo Tree Search that employs an intrinsic reward-driven exploration strategy. It's the most powerful algorithm for proof generation, especially when paired with the DeepSeek-Prover-V1.5-RL model.

 To run an experiment with RMaxTS:

 
```

```

 Key RMaxTS-specific parameters:

 
 - `gamma`: Discount factor for future rewards (default: 0.99)
 - `sample_num`: Number of proof samples to generate (default: 6400)
 - `concurrent_num`: Number of proof attempts to run concurrently (default: 32)
 - `tactic_state_comment`: Whether to include tactic state comments (default: True)
 
 Sources: [README.md61-63](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L61-L63) [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
### 5.2 Basic Sampling

 Basic sampling is a simpler approach that generates multiple proof candidates and verifies them using Lean 4.

 To run an experiment with basic sampling:

 
```

```

 Key sampling-specific parameters:

 
 - `sample_num`: Number of proof samples to generate (default: 128)
 - `log_interval`: Interval for logging progress (default: 32)
 
 Sources: [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
### 5.3 Few-Shot Sampling

 Few-shot sampling uses example proofs to guide the model in generating new proofs. It's particularly useful with the Base model.

 To run an experiment with few-shot sampling:

 
```

```

 Key few-shot-specific parameters:

 
 - `few_shot_dataset`: Path to the dataset containing example proofs
 - `few_shot_num`: Number of examples to include (default: 3)
 
 Sources: [README.md138-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L138-L145)

 
## 6. Working with Datasets

 DeepSeek-Prover-V1.5 is evaluated on two main datasets:

 
 - **miniF2F**: High school level mathematical problems
 - **ProofNet**: Undergraduate level mathematical problems
 
 
```

```

 Sources: [README.md68-83](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L68-L83)

 
## 7. Evaluating Results

 After running experiments, you can analyze the results using the summarize script:

 
```

```

 This will provide statistics on proof success rates, including:

 
 - Overall success rate
 - Per-problem results
 - Execution time statistics
 
 For more detailed analysis, you can examine the individual proof logs in the specified log directory.

 Sources: [README.md143-145](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L143-L145)

 
## 8. Troubleshooting

 Common issues and solutions:

 
| Issue | Possible Cause | Solution |
|---|---|---|
| Out of memory errors | Too large sample_num or concurrent_num | Reduce these parameters or use more GPUs |
| Lean verification timeouts | Complex proofs or insufficient timeout | Increase lean_timeout parameter |
| Poor performance with Base model | Base model requires guidance | Try using few-shot sampling instead |
| Script hangs | Too many concurrent Lean processes | Adjust lean_max_concurrent_requests and n_search_procs |

 Sources: [README.md100-132](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L100-L132)

 
## 9. Performance Considerations

 When running proof search experiments, consider the following performance tips:

 
 - **GPU Memory**: RMaxTS requires more GPU memory than basic sampling due to the higher number of samples.
 - **CPU Resources**: Lean verification is CPU-intensive; ensure you have sufficient CPU cores available.
 - **Parallelism**: Adjust `n_search_procs` and `concurrent_num` based on your hardware capabilities.
 - **Model Selection**: RL models perform best but require more resources; Base models can be faster but less accurate.
 
 Sources: [README.md68-83](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/README.md?plain=1#L68-L83)
