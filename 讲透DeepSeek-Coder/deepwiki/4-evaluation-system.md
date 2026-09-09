> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Coder/4-evaluation-system](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/4-evaluation-system)
> DeepWiki deepseek-ai/DeepSeek-Coder

# Evaluation System

  Relevant source files 
 - [Evaluation/HumanEval/eval_instruct.py](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/eval_instruct.py)
 - [Evaluation/HumanEval/utils/utils.py](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/utils/utils.py)
 - [Evaluation/LeetCode/readme.md](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/LeetCode/readme.md?plain=1)
 - [Evaluation/MBPP/eval_instruct.py](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/MBPP/eval_instruct.py)
 - [README.md](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1)
 
  
## Purpose and Scope

 The Evaluation System is a comprehensive framework for benchmarking DeepSeek Coder models across various programming tasks and languages. It provides standardized testing protocols to assess the code generation capabilities of models on different benchmarks including HumanEval, MBPP, and LeetCode contests. This document covers the architecture, workflow, and implementation details of the evaluation system.

 For information about model training and architecture, see [Models](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/2-models). For details on using models for inference, see [Usage and Inference Methods](https://deepwiki.com/deepseek-ai/DeepSeek-Coder/3-usage-and-inference-methods).

 
## System Architecture

 The evaluation system follows a modular architecture that enables consistent evaluation across different benchmarks while accommodating benchmark-specific requirements.

 
```

```

 Sources: [Evaluation/HumanEval/eval_instruct.py](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/eval_instruct.py) [Evaluation/MBPP/eval_instruct.py](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/MBPP/eval_instruct.py) [Evaluation/LeetCode/readme.md](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/LeetCode/readme.md?plain=1)

 
## Evaluation Workflow

 The evaluation process follows a standardized workflow across all benchmarks to ensure consistent assessment of model performance.

 
```

```

 Sources: [Evaluation/HumanEval/eval_instruct.py47-89](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/eval_instruct.py#L47-L89) [Evaluation/MBPP/eval_instruct.py89-129](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/MBPP/eval_instruct.py#L89-L129)

 
## Benchmark Datasets

 
### HumanEval

 HumanEval is a hand-written evaluation set that measures functional correctness for synthesizing programs from docstrings. DeepSeek Coder's evaluation system supports both Python and multilingual variants of HumanEval.

 
| Feature | Description |
|---|---|
| Languages | Python, C++, Java, JavaScript, TypeScript, PHP, C#, Bash |
| Problem Format | Function signature with docstring |
| Evaluation | Functional correctness through test cases |
| Metrics | pass@k (typically k=1) |

 
#### HumanEval Evaluation Process

 
```

```

 Sources: [Evaluation/HumanEval/eval_instruct.py14-46](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/eval_instruct.py#L14-L46) [Evaluation/HumanEval/utils/utils.py54-105](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/utils/utils.py#L54-L105)

 
### MBPP (Mostly Basic Python Programming)

 MBPP consists of 974 Python programming problems focused on basic programming and algorithmic tasks. The evaluation system uses a few-shot approach with examples to guide the model's solution generation.

 
| Feature | Description |
|---|---|
| Language | Python only |
| Problem Format | Problem description + test cases |
| Evaluation Style | Few-shot learning with examples |
| Problem Complexity | Basic programming tasks |

 
#### MBPP Evaluation Process

 
```

```

 Sources: [Evaluation/MBPP/eval_instruct.py14-53](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/MBPP/eval_instruct.py#L14-L53) [Evaluation/MBPP/eval_instruct.py53-87](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/MBPP/eval_instruct.py#L53-L87)

 
### LeetCode Contest Benchmark

 The LeetCode benchmark consists of 180 competition-level problems from recent LeetCode Contests (July 2023 to January 2024), categorized as Easy (45), Medium (91), and Hard (44).

 
| Feature | Description |
|---|---|
| Language | Python |
| Problem Types | Algorithm and data structure challenges |
| Evaluation | 100 test cases per problem |
| Difficulty Levels | Easy, Medium, Hard |
| Optional | Chain-of-Thought (CoT) evaluation |

 
#### LeetCode Evaluation Process

 
```

```

 Sources: [Evaluation/LeetCode/readme.md6-26](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/LeetCode/readme.md?plain=1#L6-L26)

 
## Implementation Details

 
### Code Extraction and Processing

 A critical part of the evaluation process is properly extracting and processing generated code from model outputs. The system includes utilities to handle various programming languages and format conversions.

 
```

```

 Sources: [Evaluation/HumanEval/utils/utils.py1-106](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/utils/utils.py#L1-L106)

 
### Model Integration

 The evaluation system is designed to work with DeepSeek Coder models using the Hugging Face Transformers library. It provides a consistent interface for loading and using different model sizes and variants.

 
```

```

 Sources: [Evaluation/HumanEval/eval_instruct.py22-46](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/eval_instruct.py#L22-L46) [Evaluation/MBPP/eval_instruct.py65-87](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/MBPP/eval_instruct.py#L65-L87)

 
## Performance Metrics

 The primary metric used across all benchmarks is pass@k, which measures the probability that a correct solution is found among k independent samples. The typical configuration uses k=1 for direct comparison with other models.

 
| Benchmark | DeepSeek-Coder-Base-33B | DeepSeek-Coder-Instruct-33B | CodeLlama-34B | GPT-3.5-Turbo |
|---|---|---|---|---|
| HumanEval Python (pass@1) | 73.2% | 75.6% | 65.3% | 72.6% |
| HumanEval Multilingual (pass@1) | 63.8% | - | 54.5% | - |
| MBPP (pass@1) | 72.0% | 74.2% | 61.2% | 74.4% |
| LeetCode Overall | - | 27.8% | 9.4% | 23.3% |
| LeetCode + CoT | - | 28.9% | - | 23.3% |

 Sources: [README.md30-47](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L30-L47) [Evaluation/LeetCode/readme.md28-48](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/LeetCode/readme.md?plain=1#L28-L48)

 
## Running Evaluations

 
### HumanEval Evaluation

 To evaluate a model on HumanEval:

 
```

```

 Sources: [Evaluation/HumanEval/eval_instruct.py119-129](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/HumanEval/eval_instruct.py#L119-L129)

 
### MBPP Evaluation

 To evaluate a model on MBPP:

 
```

```

 Sources: [Evaluation/MBPP/eval_instruct.py131-140](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/MBPP/eval_instruct.py#L131-L140)

 
### LeetCode Evaluation

 To evaluate a model on LeetCode Contest problems:

 
```

```

 Sources: [Evaluation/LeetCode/readme.md6-26](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/Evaluation/LeetCode/readme.md?plain=1#L6-L26)

 
## Integration with Other Systems

 The Evaluation System is closely integrated with other components of the DeepSeek Coder ecosystem:

 
 - **Models**: The system evaluates models of different sizes and types (base vs. instruct).
 - **Inference Methods**: It leverages various inference methods including standard generation and vLLM for high-throughput evaluation.
 - **Fine-tuning**: Performance improvements from fine-tuning can be measured using this evaluation system.
 
 Sources: [README.md30-47](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L30-L47) [README.md317-333](https://github.com/deepseek-ai/DeepSeek-Coder/blob/b7ba5659/README.md?plain=1#L317-L333)
