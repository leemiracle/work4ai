> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Math/5-evaluation-system](https://deepwiki.com/deepseek-ai/DeepSeek-Math/5-evaluation-system)
> DeepWiki deepseek-ai/DeepSeek-Math

# Evaluation System

  Relevant source files 
 - [evaluation/README.md](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1)
 - [evaluation/submit_eval_jobs.py](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/submit_eval_jobs.py)
 
  The Evaluation System in DeepSeek-Math provides comprehensive tools and infrastructure for assessing the mathematical reasoning capabilities of the DeepSeek-Math model family. This system enables evaluation across multiple benchmarks using various reasoning approaches including chain-of-thought, program-aided language evaluation, and tool-integrated reasoning.

 For information on specific evaluation methods, see [Chain-of-Thought Evaluation](https://deepwiki.com/deepseek-ai/DeepSeek-Math/5.1-chain-of-thought-evaluation), [Program-Aided Language Evaluation](https://deepwiki.com/deepseek-ai/DeepSeek-Math/5.2-program-aided-language-evaluation), and [Tool Integration Evaluation](https://deepwiki.com/deepseek-ai/DeepSeek-Math/5.3-tool-integration-evaluation). For details about the datasets used, see [Evaluation Datasets](https://deepwiki.com/deepseek-ai/DeepSeek-Math/5.4-evaluation-datasets).

 
## System Overview

 The Evaluation System is designed to provide a systematic and efficient way to evaluate different variants of the DeepSeek-Math models against mathematical benchmarks. It supports both zero-shot and few-shot evaluation approaches and can process questions in multiple languages including English and Chinese.

 
```

```

 Sources: [evaluation/README.md1-42](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1#L1-L42) [evaluation/submit_eval_jobs.py1-67](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/submit_eval_jobs.py#L1-L67)

 
## Architecture Components

 The evaluation system consists of several interconnected components that work together to process data, run inference, evaluate answers, and aggregate results.

 
```

```

 Sources: [evaluation/README.md12-34](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1#L12-L34) [evaluation/submit_eval_jobs.py39-64](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/submit_eval_jobs.py#L39-L64)

 
## Configuration System

 The evaluation system uses a configuration-based approach to define evaluation parameters. Each model variant has its own configuration specifying the model path, output directory, and evaluation settings.

 
```

```

 Sources: [evaluation/submit_eval_jobs.py4-37](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/submit_eval_jobs.py#L4-L37)

 
### Configuration Details

 The evaluation system uses predefined configurations for each model variant. These configurations specify:

 
| Parameter | Description |
|---|---|
| output-dir | Directory where evaluation outputs will be stored |
| model-path | Path or HuggingFace ID for the model |
| tokenizer-path | Path or HuggingFace ID for the tokenizer |
| model-size | Size of the model (e.g., "7b") |
| overwrite | Whether to overwrite existing results |
| use-vllm | Whether to use VLLM for inference |
| test-conf | Path to test configuration JSON file |
| prompt_format | Format for prompts (e.g., "few_shot" or "zero_shot") |
| expname | Name of the experiment |

 Sources: [evaluation/submit_eval_jobs.py4-37](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/submit_eval_jobs.py#L4-L37)

 
## Prompt Processing

 The evaluation system processes input questions differently based on the evaluation method and language:

 
### Chain-of-Thought Prompting

 For chain-of-thought evaluation of DeepSeekMath-Instruct and DeepSeekMath-RL:

 
 - **English questions**: Original question followed by `Please reason step by step, and put your final answer within \boxed{}.`
 - **Chinese questions**: Original question followed by `请通过逐步推理来解答问题，并把最终答案放置于\boxed{}中。`
 
 
### Tool-Integrated Reasoning

 For tool-integrated reasoning:

 
 - **English questions**: Original question followed by `Please integrate natural language reasoning with programs to solve the problem above, and put your final answer within \boxed{}.`
 - **Chinese questions**: Original question followed by `请结合自然语言和Python程序语言来解答问题，并把最终答案放置于\boxed{}中。`
 
 Sources: [evaluation/README.md14-20](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1#L14-L20)

 
## Evaluation Process

 The evaluation process involves multiple steps, from job submission to result aggregation:

 
```

```

 Sources: [evaluation/README.md22-37](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1#L22-L37)

 
### Job Submission

 The evaluation system uses `submit_eval_jobs.py` to configure and launch evaluation jobs. This script:

 
 - Selects a model configuration (Base, Instruct, or RL)
 - Constructs a command for `run_subset_parallel.py`
 - Adds command-line arguments based on the configuration
 - Executes the command to start the evaluation process
 
 The script supports parallel processing across multiple GPUs to accelerate evaluations.

 Sources: [evaluation/submit_eval_jobs.py41-63](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/submit_eval_jobs.py#L41-L63)

 
### Result Aggregation

 After all evaluation processes complete, the `summarize_results.py` script aggregates results from all processes:

 
 - Collects outputs from all evaluation runs
 - Calculates aggregate metrics
 - Generates a comprehensive summary in `evaluation_results.json`
 
 For formal theorem proving evaluations (with the `--eval-atp` flag), the system invokes `unsafe_score_minif2f_isabelle.py` to evaluate informal-to-formal proving results using the PISA server.

 Sources: [evaluation/README.md30-37](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1#L30-L37)

 
## Running Evaluations

 To run evaluations on the DeepSeek-Math models:

 
 - **Setup the environment**:

 
```

```
 - **Launch evaluation jobs**:

 
```

```
 - **Aggregate results** after all processes complete:

 
```

```
 
 The evaluation results will be saved as `evaluation_results.json`.

 For custom evaluations, users can modify the configurations in `submit_eval_jobs.py` and the test configurations in `configs/*test_configs.json`.

 Sources: [evaluation/README.md5-37](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1#L5-L37)

 
## Integration with Model System

 The Evaluation System is designed to work with all three DeepSeek-Math model variants, each with its specific evaluation configuration:

 
```

```

 Sources: [evaluation/submit_eval_jobs.py4-37](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/submit_eval_jobs.py#L4-L37) [evaluation/README.md14-20](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1#L14-L20)

 
## Output Structure

 The evaluation system stores outputs in the configured output directories. These outputs include the raw model responses, extracted answers, and evaluation metrics. The complete set of model outputs is also available in the `outputs.zip` file provided with the repository.

 Sources: [evaluation/README.md39-42](https://github.com/deepseek-ai/DeepSeek-Math/blob/b8b0f8ce/evaluation/README.md?plain=1#L39-L42)
