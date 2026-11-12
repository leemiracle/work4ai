> 来源: [https://deepwiki.com/deepseek-ai/ESFT/2-expert-evaluation-system](https://deepwiki.com/deepseek-ai/ESFT/2-expert-evaluation-system)
> DeepWiki deepseek-ai/ESFT

# Expert Evaluation System

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/ESFT/blob/579a7711/README.md?plain=1)
 - [eval_multigpu.py](https://github.com/deepseek-ai/ESFT/blob/579a7711/eval_multigpu.py)
 - [scripts/eval_expert.sh](https://github.com/deepseek-ai/ESFT/blob/579a7711/scripts/eval_expert.sh)
 
  
## Purpose and Scope

 The Expert Evaluation System is a core component of the ESFT (Expert-Specialized Fine-Tuning) framework that enables efficient customization of MoE (Mixture-of-Experts) language models. This system is responsible for evaluating expert performance, calculating expert relevance scores for specific tasks, and generating optimal expert configurations for fine-tuning.

 This document covers the architecture, workflow, and implementation details of the Expert Evaluation System. For information about the training process that uses these expert configurations, see [Training System](https://deepwiki.com/deepseek-ai/ESFT/3-training-system).

 
## System Overview

 The Expert Evaluation System consists of three main components that work together to determine which experts in a MoE model are most relevant for specific tasks:

 
```

```

 Sources: [eval_multigpu.py](https://github.com/deepseek-ai/ESFT/blob/579a7711/eval_multigpu.py) [scripts/eval_expert.sh](https://github.com/deepseek-ai/ESFT/blob/579a7711/scripts/eval_expert.sh)

 
## Key Components

 
### 1. Model Evaluation

 The model evaluation component assesses the base MoE model's performance on specific datasets. It uses multi-GPU parallel processing to efficiently evaluate models on various benchmark tasks.

 
```

```

 The evaluation process leverages a device mapping strategy to distribute model layers across multiple GPUs efficiently. The framework supports various benchmark tasks through specialized evaluator classes.

 Sources: [eval_multigpu.py30-64](https://github.com/deepseek-ai/ESFT/blob/579a7711/eval_multigpu.py#L30-L64)

 
### 2. Expert Scoring

 The expert scoring component analyzes how each expert in the MoE model contributes to performance on specific tasks. It calculates relevance scores that indicate which experts are most important for each task.

 
```

```

 The expert scoring system processes a specific number of tokens (configurable via the `n_sample_tokens` parameter) to gather statistically significant data on expert utilization patterns.

 Sources: [scripts/eval_expert.sh1-8](https://github.com/deepseek-ai/ESFT/blob/579a7711/scripts/eval_expert.sh#L1-L8)

 
### 3. Expert Configuration Generation

 The expert configuration component takes the expert scores as input and generates a configuration file that specifies which experts should be trained and which should be frozen during the fine-tuning process.

 
```

```

 The configuration generation process offers several customization options:

 
 - `score_function`: Method for scoring experts (default: token)
 - `top_p`: Percentage of top-scoring experts to select
 - Optional flags to include shared experts or non-expert modules in training
 
 Sources: [scripts/eval_expert.sh9-16](https://github.com/deepseek-ai/ESFT/blob/579a7711/scripts/eval_expert.sh#L9-L16)

 
## Workflow

 The complete workflow of the Expert Evaluation System demonstrates how these components interact in sequence:

 
```

```

 The workflow begins with model evaluation, proceeds to expert scoring, and culminates in the generation of an expert configuration that can be used by the Training System to fine-tune the model efficiently.

 Sources: [scripts/eval_expert.sh](https://github.com/deepseek-ai/ESFT/blob/579a7711/scripts/eval_expert.sh)

 
## Implementation Details

 
### Model Evaluation Implementation

 The model evaluation is implemented in `eval_multigpu.py`, which:

 
 - Loads the base model from a specified path
 - Distributes the model across multiple GPUs
 - Evaluates the model on specific datasets using task-specific evaluators
 - Saves the evaluation results
 
 
```

```

 The script supports several task-specific evaluators:

 
 - `IntentEvaluator`: For intent classification tasks
 - `SummaryEvaluator`: For summarization tasks
 - `LawEvaluator`: For legal analysis tasks
 - `TranslationEvaluator`: For translation tasks
 
 Sources: [eval_multigpu.py30-64](https://github.com/deepseek-ai/ESFT/blob/579a7711/eval_multigpu.py#L30-L64)

 
### Expert Scoring and Configuration

 The expert scoring and configuration process is implemented in two main scripts:

 
 - `get_expert_scores.py`: Calculates expert relevance scores

 
 - Processes a configurable number of tokens from the dataset
 - Analyzes router decisions and expert activations
 - Outputs scores for each expert
 - `generate_expert_config.py`: Creates expert configurations

 
 - Takes expert scores as input
 - Applies a scoring function to rank experts
 - Selects top-performing experts based on the `top_p` parameter
 - Generates a JSON configuration file specifying which experts to train
 
 This configuration file is structured to identify which experts should be trained and which should be frozen during the fine-tuning process.

 Sources: [scripts/eval_expert.sh](https://github.com/deepseek-ai/ESFT/blob/579a7711/scripts/eval_expert.sh)

 
## Usage Example

 The Expert Evaluation System can be used through the `eval_expert.sh` script, which orchestrates the entire process:

 
 - Calculate expert scores:
 
 
```

```

 
 - Generate expert configuration:
 
 
```

```

 The resulting expert configuration is then used as input to the training process (covered in [Training System](https://deepwiki.com/deepseek-ai/ESFT/3-training-system)).

 Sources: [scripts/eval_expert.sh](https://github.com/deepseek-ai/ESFT/blob/579a7711/scripts/eval_expert.sh) [README.md54-77](https://github.com/deepseek-ai/ESFT/blob/579a7711/README.md?plain=1#L54-L77)

 
## Technical Configuration Parameters

 
| Parameter | Description | Default | Example |
|---|---|---|---|
| eval_dataset | Dataset to evaluate expert performance on | - | translation, intent, summary, law |
| base_model_path | Path to the MoE model | - | deepseek-ai/ESFT-vanilla-lite |
| n_sample_tokens | Number of tokens to sample for scoring | - | 131072 |
| world_size | Number of processes for parallel evaluation | 4 | 4 |
| gpus_per_rank | Number of GPUs per process | 2 | 2 |
| score_function | Method to score experts | token | token |
| top_p | Percentage of top experts to select | - | 0.2 |
| train_shared_experts | Whether to train shared experts | False | - |
| train_non_expert_modules | Whether to train non-expert modules | False | - |

 Sources: [scripts/eval_expert.sh](https://github.com/deepseek-ai/ESFT/blob/579a7711/scripts/eval_expert.sh) [eval_multigpu.py67-78](https://github.com/deepseek-ai/ESFT/blob/579a7711/eval_multigpu.py#L67-L78)
