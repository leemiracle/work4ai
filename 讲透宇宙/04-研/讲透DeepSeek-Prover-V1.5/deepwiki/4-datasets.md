> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/4-datasets](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/4-datasets)
> DeepWiki deepseek-ai/DeepSeek-Prover-V1.5

# Datasets

  Relevant source files 
 - [datasets/minif2f.jsonl](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/datasets/minif2f.jsonl)
 - [datasets/minif2f_valid_few_shot.jsonl](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/datasets/minif2f_valid_few_shot.jsonl)
 - [datasets/proofnet.jsonl](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/datasets/proofnet.jsonl)
 
  This page documents the datasets used in the DeepSeek-Prover-V1.5 system. These datasets contain mathematical problems and theorems that the system attempts to prove using the Lean 4 proof assistant. For information about how these datasets are used in specific proof search algorithms, see [Proof Search Algorithms](https://deepwiki.com/deepseek-ai/DeepSeek-Prover-V1.5/2.2-proof-search-algorithms).

 
## Dataset Types and Structure

 DeepSeek-Prover-V1.5 uses three primary types of datasets:

 
 - **miniF2F Dataset**: Contains high-school level mathematical problems from various competitions
 - **ProofNet Dataset**: Contains undergraduate-level mathematical problems
 - **Few-shot Examples**: Provides example proofs to guide the model, selected from the validation set of miniF2F
 
 
### Dataset Structure Diagram

 
```

```

 Sources: [datasets/minif2f.jsonl](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/datasets/minif2f.jsonl) [datasets/minif2f_valid_few_shot.jsonl](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/datasets/minif2f_valid_few_shot.jsonl)

 
### miniF2F Dataset

 The miniF2F dataset is stored in JSONL format, with each line representing a mathematical problem. Each entry has the following structure:

 
```

```

 Field descriptions:

 
| Field | Description |
|---|---|
| name | Identifier following a pattern (e.g., "amc12a_2019_p21" for AMC problem) |
| split | Indicates whether the entry is for training or validation |
| informal_prefix | Natural language description of the problem, often in LaTeX format |
| formal_statement | Formal theorem statement in Lean 4 syntax |
| goal | Readable version of the theorem statement with the goal to be proven |
| header | Common imports, option settings, and namespace openings |

 Example entry from the miniF2F dataset:

 
```

```

 Sources: [datasets/minif2f.jsonl](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/datasets/minif2f.jsonl)

 
### ProofNet Dataset

 The ProofNet dataset follows a similar structure to miniF2F but contains more advanced undergraduate-level mathematical problems.

 
### Few-shot Examples Dataset

 The few-shot examples dataset contains selected problems with their corresponding formal statements and proofs. Each entry includes all fields from the miniF2F dataset plus an additional field:

 
```

```

 The **formal_proof** field contains the Lean 4 proof for the theorem, which serves as an example to guide the model.

 Example entry from the few-shot dataset:

 
```

```

 Sources: [datasets/minif2f_valid_few_shot.jsonl](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/datasets/minif2f_valid_few_shot.jsonl)

 
## Problem Sources and Types

 The miniF2F dataset contains problems from various mathematical competitions and domains:

 
| Source/Domain | Examples |
|---|---|
| AMC12 (American Mathematics Competitions) | amc12a_2019_p21, amc12a_2015_p10, amc12a_2008_p8 |
| AIME (American Invitational Mathematics Examination) | aime_1984_p5, aime_1991_p6, aime_1994_p4 |
| IMO (International Mathematical Olympiad) | imo_1984_p2, imo_1962_p4, imo_1978_p5 |
| Algebra | mathd_algebra_182, mathd_algebra_116, mathd_algebra_43 |
| Number Theory | mathd_numbertheory_169, mathd_numbertheory_48, mathd_numbertheory_109 |
| Induction | induction_sum2kp1npqsqm1, induction_sum_1oktkp1 |
| Complex Analysis | Problems involving complex numbers (z : ℂ) |

 Sources: [datasets/minif2f.jsonl](https://github.com/deepseek-ai/DeepSeek-Prover-V1.5/blob/2c4ba911/datasets/minif2f.jsonl)

 
## Dataset Integration with System

 
### Dataset and System Architecture

 
```

```

 The datasets integrate with the proof search algorithms as follows:

 
 - **RMaxTS Algorithm**: Uses the datasets to explore the proof space efficiently by updating intrinsic rewards based on verification feedback
 - **Basic Sampling**: Uses the datasets for standard proof generation without sophisticated search strategies
 - **Few-shot Sampling**: Uses examples from the few-shot dataset to guide the proof generation process
 
 
### Proof Generation Workflow

 
```

```

 Sources: System overview diagrams

 
## Configuration and Usage

 When using the DeepSeek-Prover-V1.5 system, datasets are selected through configuration files:

 
 - For the RMaxTS algorithm: `configs/RMaxTS.py`
 - For basic sampling: `configs/sampling.py`
 - For few-shot sampling: `configs/sampling_few_shot.py`
 
 Key configuration parameters related to datasets include:

 
| Parameter | Description |
|---|---|
| dataset_name | Path to the dataset file (e.g., "datasets/minif2f.jsonl") |
| few_shot_dataset | Path to the few-shot examples (for few-shot sampling) |
| few_shot_num | Number of few-shot examples to use |

 
## Extending the Datasets

 Users can extend or create new datasets by following the same JSONL format as the existing datasets. The key requirements are:

 
 - The natural language description of the problem in the `informal_prefix` field
 - The formal statement in Lean 4 syntax in the `formal_statement` field
 - The goal to be proven in the `goal` field
 - The necessary imports and settings in the `header` field
 
 For few-shot examples, the `formal_proof` field should also be included, containing the Lean 4 proof for the theorem.
