<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/QCalEval · page 2 Evaluation Pipeline · fetched 2026-10-26 -->

# Evaluation Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [benchmark_icl.py](benchmark_icl.py)
- [benchmark_judge.py](benchmark_judge.py)
- [benchmark_zeroshot.py](benchmark_zeroshot.py)

</details>



The QCalEval evaluation pipeline is a multi-stage process designed to measure Vision-Language Model (VLM) performance on quantum calibration tasks. The pipeline transitions from raw data loading and model inference to structured scoring and final metric aggregation. It is implemented through three primary scripts that communicate via standardized JSON files.

### Pipeline Architecture

The following diagram illustrates the flow of data from the HuggingFace dataset through the inference engines and into the scoring judge.

**Data Flow: From Inference to Results**
```mermaid
graph TD
  subgraph "Input Space"
    [HF_Dataset] -- "load_dataset" --> [benchmark_scripts]
  end

  subgraph "Inference Space"
    [benchmark_scripts] -- "HTTP POST" --> [VLM_Endpoint]
    [VLM_Endpoint] -- "JSON Response" --> [benchmark_scripts]
    [benchmark_scripts] -- "write" --> [results_json]
  end

  subgraph "Scoring Space"
    [results_json] -- "read" --> [benchmark_judge_py]
    [benchmark_judge_py] -- "Programmatic" --> [Scores]
    [benchmark_judge_py] -- "LLM Judge" --> [Scores]
    [Scores] -- "write" --> [judged_json]
  end

  [benchmark_scripts]:::code
  [benchmark_judge_py]:::code
  [results_json]:::file
  [judged_json]:::file

  classDef code font-family:monospace,font-weight:bold
  classDef file font-family:monospace,stroke-dasharray: 5 5
```
Sources: [benchmark_zeroshot.py:18-27](), [benchmark_icl.py:18-27](), [benchmark_judge.py:18-27]()

---

### Inference Modes

The pipeline supports two distinct inference strategies: Zero-Shot and In-Context Learning (ICL). Both scripts utilize an asynchronous concurrency model to maximize throughput against OpenAI-compatible API endpoints.

#### Zero-Shot Inference
The `benchmark_zeroshot.py` script evaluates the model's baseline performance. It sends each of the six question types (Q1–Q6) as independent requests to the model, ensuring no leakage between different aspects of the same experiment.
*   **Key File:** `benchmark_zeroshot.py`
*   **Mechanism:** Iterates through `Q_PROMPT_KEYS` [benchmark_zeroshot.py:51-51]() and calls `ask_single_question` [benchmark_zeroshot.py:89-91]().
*   **For details, see [Zero-Shot Inference (benchmark_zeroshot.py)](#2.1).**

#### In-Context Learning (ICL) Inference
The `benchmark_icl.py` script provides the model with labeled demonstration examples from the same experiment family. This mode evaluates the model's ability to adapt to specific calibration patterns and extraction schemas.
*   **Key File:** `benchmark_icl.py`
*   **Mechanism:** Uses `FEWSHOT_Q_MAP` [benchmark_icl.py:42-46]() to handle Q3, Q5, and Q6. It interleaves multiple images into the prompt using `<image>` tags [benchmark_icl.py:79-92]().
*   **For details, see [In-Context Learning Inference (benchmark_icl.py)](#2.2).**

---

### Scoring and Judging

Once inference is complete, `benchmark_judge.py` processes the model responses. The scoring architecture is hybrid, combining deterministic programmatic checks with LLM-based qualitative assessment.

**Code Entity Mapping: Scoring Logic**
```mermaid
graph LR
  subgraph "benchmark_judge.py"
    [score_entry] --> [Programmatic_Scoring]
    [score_entry] --> [LLM_Judge_Scoring]
    
    subgraph "Programmatic_Scoring"
      [score_enum_match]
      [score_q1_programmatic]
      [score_q5_field]
      [extract_status]
    end

    subgraph "LLM_Judge_Scoring"
      [call_judge_structured] --> [CHECKLIST_PROMPT]
    end
  end

  [score_entry]:::func
  [score_enum_match]:::func
  [score_q1_programmatic]:::func
  [score_q5_field]:::func
  [extract_status]:::func
  [call_judge_structured]:::func

  classDef func font-family:monospace
```
Sources: [benchmark_judge.py:46-53](), [benchmark_judge.py:200-204](), [benchmark_judge.py:57-64]()

#### Programmatic Scoring
Questions with objective or structured answers (Q2, Q4, Q5, Q6) are scored using regular expressions and JSON parsing. For example, `extract_status` [benchmark_judge.py:163-184]() normalizes model output against `KNOWN_STATUSES` [benchmark_judge.py:150-160]() to determine if a calibration diagnosis is correct.

#### LLM-Based Judging
For open-ended scientific reasoning (Q3) and technical descriptions (Q1), the pipeline employs an LLM judge. The judge uses a `CHECKLIST_PROMPT` [benchmark_judge.py:57-64]() to verify if the model's response covers specific key points defined in the ground truth.

**For details, see [Scoring and Judging (benchmark_judge.py)](#2.3).**

---

### Execution Sequence

To run the full pipeline, follow these steps:

1.  **Inference:** Run either `benchmark_zeroshot.py` or `benchmark_icl.py`. This generates a results JSON file containing raw model answers.
2.  **Judging:** Run `benchmark_judge.py`, passing the results file from step 1. This script will append scores and aggregate metrics.
3.  **Analysis:** The final output includes a `summary` block with mean scores across all question types and experiment families.

Sources: [README.md:148-160]()

---

