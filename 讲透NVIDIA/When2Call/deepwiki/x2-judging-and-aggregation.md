<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/When2Call · extra page Judging and Aggregation · fetched 2026-11-09 -->

# Judging and Aggregation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py](evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py)
- [evaluation/llm_as_a_judge/run_openai_judge.py](evaluation/llm_as_a_judge/run_openai_judge.py)

</details>



This section covers subsection 4.2.2 of the When2Call evaluation pipeline, focusing on the LLM-as-a-Judge prompting strategy implemented in `evaluation/llm_as_a_judge/run_openai_judge.py` and the per-category scoring and response distribution analysis implemented in `evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py`.

---

## 1. Judge Prompting and Classification (`run_openai_judge.py`)

The LLM-as-a-Judge stage evaluates model responses generated during the inference phase against the expected categories. It uses an OpenAI-compatible API client to classify each model response into one of four distinct categories: `direct_answer`, `tool_call`, `request_for_info`, or `cannot_answer` [evaluation/llm_as_a_judge/run_openai_judge.py:26-55].

### Implementation Details

1. **Input Loading**: The script reads model responses from a JSONL file, parsing `target_tool` and `tools` fields where applicable [evaluation/llm_as_a_judge/run_openai_judge.py:89-96].
2. **Resumable Execution**: It checks `args.results_path` to count existing lines, allowing resumption of interrupted judgment jobs [evaluation/llm_as_a_judge/run_openai_judge.py:98-107].
3. **Prompt Construction**: `JUDGE_PROMPT` formats the available tools, the user's question, and the model's response into XML-like tags (`<AVAILABLE_TOOLS>`, `<USER_QUESTION>`, `<AI_MODEL_RESPONSE>`) [evaluation/llm_as_a_judge/run_openai_judge.py:109-115].
4. **Structured JSON Output & Fallback**: The judge model is requested to return strict JSON matching `{"classification": "<category>"}` [evaluation/llm_as_a_judge/run_openai_judge.py:52-55]. If parsing fails, a correction prompt is appended to the message history, asking the model to rewrite its response into valid JSON [evaluation/llm_as_a_judge/run_openai_judge.py:122-134].

```mermaid
title "OpenAI Judge Processing Flow"
graph TD
    A["Input: Responses JSONL file"] --> B["evaluation/llm_as_a_judge/run_openai_judge.py:main()"]
    B --> C{"Check existing results"}
    C -->|Resuming| D["Skip processed indices"]
    C -->|Start/Continue| E["Format JUDGE_PROMPT"]
    E --> F["OpenAI API chat.completions.create"]
    F --> G{"JSON parse successful?"}
    G -->|Yes| H["Append to results_path"]
    G -->|No| I["Send retry prompt to model"]
    I --> F
    H --> J["Next item"]
```

Sources: [evaluation/llm_as_a_judge/run_openai_judge.py:15-146]()

---

## 2. Per-Category Scoring and Aggregation (`aggregate_llm_as_a_judge_results.py`)

Once judge responses are collected, `aggregate_llm_as_a_judge_results.py` computes performance metrics across the different behavioral categories [evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py:21-62].

### Aggregation Logic

* **Categories Tracked**: `tool_call`, `request_for_info`, and `cannot_answer` [evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py:43-47].
* **Scoring**: For each item, a binary score is awarded (`1` or `0`) depending on whether the judge's classification matches `item["question"]["correct_answer"]` [evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py:50].
* **Response Distribution**: `Counter` from the standard library tallies the full distribution of judge classifications per category to analyze confusion patterns [evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py:18, 51, 56].
* **Mean Accuracy**: Category scores are averaged over the total number of items in that category [evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py:55].

```mermaid
title "Results Aggregation Data Flow"
graph LR
    A["Judge Responses JSONL"] --> B["aggregate_llm_as_a_judge_results.py"]
    B --> C["Group by correct_answer"]
    C --> D["Compute Accuracy Score"]
    C --> E["Compute Response Distribution (Counter)"]
    D & E --> F["Print Category Metrics Summary"]
```

Sources: [evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py:15-62]()

---

## 3. Code Entity Summary

| Natural Language Concept | Code File | Key Functions / Variables |
| :--- | :--- | :--- |
| Judge Prompt & Inference Loop | `evaluation/llm_as_a_judge/run_openai_judge.py` | `JUDges_PROMPT`, `main()` |
| Results Aggregation & Scoring | `evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py` | `main()`, `Counter` |

Sources: [evaluation/llm_as_a_judge/run_openai_judge.py:1-146](), [evaluation/llm_as_a_judge/aggregate_llm_as_a_judge_results.py:1-62]()

---

