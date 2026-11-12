# Meta-Evaluation

This directory contains code and data supporting the paper:

> Hwang et al. 2026, [*Deep Research, Shallow Evaluation: A Case Study in Meta-Evaluation for Long-Form QA Benchmarks*](https://arxiv.org/abs/2603.06942)

We conduct a case study in meta-evaluation for the ScholarQA-CS2 long-form scientific QA benchmark. We validate the benchmark through human pairwise preference judgments and critically examine this approach's strengths, weaknesses, and confounders—showing that pairwise preferences are best suited for system-level evaluation, while metric-wise annotations and annotator expertise are critical for reliable metric-level assessment.

## Directory Structure

```
meta_evaluation/
├── system_reports/         # System outputs for evaluated QA systems
│   ├── dev/                # Dev split (100 questions)
│   ├── test/               # Test split (100 questions)
│   └── expert_written/     # Expert-written questions (25 questions, used for Deep-Expertise setting)
├── annotation_docs/        # Instructions used for guidelines
└── agreement_calculation/  # Agreement analysis code and annotation data
```

## System Reports

The `system_reports/` directory contains the raw outputs from each evaluated system on the ScholarQA-CS2 benchmark questions. Each file is a JSON list of `{"question": ..., "response": ...}` entries.

The following systems are included:

| System | File | Used for Meta Evaluation    |
|--------|------|-----------------------------|
| ScholarQA (SQA) | `sqa.json` | ✔                           |
| ScholarQA + Qwen3-8B SFT | `sqa-qwen3_8b_SFT_fullanswer.json` | ✔                           |
| Claude Sonnet 4 | `claude-sonnet-4-20250514.json` |                             |
| Gemini 2.5 Pro | `gemini-2.5-pro-preview-03-25.json` | ✔                           |
| Elicit | `elicit.json` | ✔ (test and dev set only)   |
| Falcon | `falcon.json` | ✔ (expert-written set only) |
| OpenAI Deep Research | `openai-dr.json` | ✔                           |
| Perplexity | `perplexity.json` | ✔                           |
| SciSpace | `scispace.json` |                             |
| STORM | `storm.json` | ✔                           |
| You.com | `you.json` |                             |

## Agreement Calculation

The `agreement_calculation/` directory contains annotation data and the analysis script for computing agreement between human judgments and automated evaluation metrics. See [`agreement_calculation/README.md`](agreement_calculation/README.md) for full details on the annotation format, usage, and replicating results from the paper.

## Citation

If you use this code or data, please cite:

```bibtex
@misc{hwang2026deepresearchshallowevaluation,
      title={Deep Research, Shallow Evaluation: A Case Study in Meta-Evaluation for Long-Form QA Benchmarks}, 
      author={Jena D. Hwang and Varsha Kishore and Amanpreet Singh and Dany Haddad and Aakanksha Naik and Malachi Hamada and Jonathan Bragg and Mike D'Arcy and Daniel S. Weld and Lucy Lu Wang and Doug Downey and Sergey Feldman},
      year={2026},
      eprint={2603.06942},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2603.06942}, 
}
```
