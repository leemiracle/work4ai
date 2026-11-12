# Ai2 ScholarQA Evaluation


## Components

This repository contains code and data from **ScholarQA-CS2 Evaluations**, and is associated with two publications:

**[1]** Hwang et al. 2026, [*Deep Research, Shallow Evaluation:A Case Study in Meta-Evaluation for Long-Form QA Benchmarks*](https://arxiv.org/abs/2603.06942)\
**[2]** Bragg et al. 2025, [*AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite*](https://arxiv.org/abs/2510.21652)

This repository includes:

* **Meta-Evaluation Code and Data**:
  [Code](https://github.com/allenai/ai2-scholarqa-eval/tree/main/meta_evaluation/agreement_calculation/) and [human (preference) annotated data](https://github.com/allenai/ai2-scholarqa-eval/tree/main/meta_evaluation/agreement_calculation/annotation) from in the human meta-evaluation conducted over of ScholarQA-CS2 **[1]**. It includes, analysis of agreement between human and automated model evaluations in pairwise comparisons of ScholarQA-CS2 Eval system outputs. We also include [deep-research system responses](https://github.com/allenai/ai2-scholarqa-eval/tree/main/meta_evaluation/system_reports) used for meta-evaluation.

* **Rubric Building Pipeline**:
The implementation of the [automated rubric building pipeline](https://github.com/allenai/ai2-scholarqa-eval/tree/main/rubric_building/) supporting ScholarQA-CS2 discussed and released with AstaBench **[2]**. ScholarQA-CS2's [rubrics](https://huggingface.co/datasets/allenai/asta-bench/tree/main/tasks/sqa) (see `*_recomputed.json`) are generated via this pipeline. 
The automated pipeline for generates evaluation rubrics from system reports using Claude's API. Extracts key requirements from reports and unifies them into comprehensive, weighted evaluation criteria.


## Requirements
- Python 3.10+
- Rubric building scripts require Claude API.

## Quick Set Up
Clone the repo and set up the environment as follows:
```
git clone https://github.com/allenai/ai2-scholarqa-eval.git
cd ai2-scholarqa-eval
conda create -n sqaeval python=3.10
conda activate sqaeval
```

Both scripts uses API key to run Claude. However, sanity-check test runs 
(default set up; quick run without API call) will let you execute the script without it.
To specify your key run:
```
export ANTHROPIC_API_KEY='your-api-key-here'
```


To run **meta-evaluation analyses**:
```
cd meta_evaluation/ 
```
👉 See [`meta_evaluation/README.md`](meta_evaluation/README.md) for details.


To run **rubric building**:

- For generating ingredients (step 1 of the pipeline):
    
    ```
    python rubric_building/1_generate_ingredients.py
    ```
- For unifying ingredients into rubric (step 2):
    ```
    python rubric_building/2_unify_ingredients.py
    ```

👉 See [`rubric_building/README.md`](rubric_building/README.md) for details.

## License

The code is licensed under Apache 2.0. The data is licensed under ODC-BY 1.0. The artifacts are intended for research and educational use in accordance with Ai2's Responsible Use Guidelines. 

## How to Cite

Citations are supplied in the README files within the respective directory.

