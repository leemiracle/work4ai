# Improving Attributed Long-form Question Answering with Intent Awareness

**[Paper](https://openreview.net/forum?id=fRCm5c8x0j)** | **[Demo](#demo)**

> **ICLR 2026** — Xinran Zhao, Aakanksha Naik, Jay DeYoung, Joseph Chee Chang, Jena D. Hwang, Tongshuang Wu, Varsha Kishore

---

## News

- **August 6, 2026** — SFT datasets and model checkpoints released in the [intent-aware-lfqa HuggingFace collection](https://huggingface.co/collections/allenai/intent-aware-lfqa).
- **March 14, 2026** — Initial commit.

---

## Overview

This work studies how language models can generate better deep research style attributed long-form answers to scientific questions by modeling **author intent** — the implicit reasoning behind what an author chose to write and which papers they chose to cite.

We propose tag-based schemes that extract two types of intent signals:
- **Paragraph intent (PIT)**: *Why* was this paragraph written? (exposition, comparison, background, etc.)
- **Citation intent (CIT)**: *Why* was this paper cited? (supporting evidence, contrast, methodology, etc.)

These signals improve both **zero-shot generation** with large commercial models and **supervised fine-tuning (SFT)** of smaller models, yielding gains of **+2.9 pp** (large models) and **+12.3 pp** (smaller models) on the ScholarQA benchmark.

<p align="center">
  <img src="figs/intent_motivation_02.png" alt="Intent motivation figure" width="700"/>
  <br><em>Figure: Intent-aware signals improve both citation quality and readability of generated reports.</em>
</p>

---

## Data

```
data/
├── rubrics/
│   ├── rubrics_v1_recomputed.json   # Dev split  — 100 evaluated questions + rubrics
│   └── rubrics_v2_recomputed.json   # Test split — 100 evaluated questions + rubrics
├── test_sqa_traces/                 # Cached retrieval traces for the test split
└── dev_traces/                      # Cached retrieval traces for the dev split
```

### Rubrics and Query Selection

The **rubrics files** are the source of truth for which queries are evaluated. Each entry is one benchmark question together with its evaluation criteria (`ingredients`):

```json
{
  "question":    "Apart from preventing overfitting, are there any side effects of dropout?",
  "case_id":     0,
  "ingredients": [
    { "name": "answer_critical_0",
      "criterion": "Discuss the model ensemble / model averaging interpretation ..." },
    ...
  ]
}
```

Both rubrics files contain exactly **100 questions** each.  The trace folders (`test_sqa_traces/`, `dev_traces/`) contain pre-cached retrieval results for a larger set of queries, but the inference scripts load the rubrics first and then filter traces to only those 100 questions:

```python
# from inference/inference_commercial.py (mirrors trial_gemini.py)
with open(f"data/rubrics/rubrics_{version}_recomputed.json") as f:
    rubrics = json.load(f)

for file in os.listdir(trace_path):              # load all cached traces
    item = json.load(open(...))
    traces[item["query"]] = item

queries = [item["question"] for item in rubrics  # keep only rubric questions
           if item["question"] in traces]
```

### Running Example: How the Pipeline Works

Below is a concrete walkthrough for the query:

> *"Apart from preventing overfitting, are there any side effects (desirable or otherwise) of applying dropout in deep neural networks?"*

---

#### 1. Trace File — Cached Retrieval

Each file in `data/test_sqa_traces/` (or `dev_traces/`) is a JSON object that caches the full retrieval state for one query, so evaluation can run without re-querying Semantic Scholar. The inference scripts load these and pass them to `ScholarQA.answer_query(..., cached_snippets=trace, ...)`.

Top-level keys:

```json
{
  "query":            "Apart from preventing overfitting ...",
  "decomposed_query": { ... },   // LLM-rewritten query + keyword query + field filters
  "candidates":       [ ... ],   // papers retrieved from Semantic Scholar (up to 256)
  "quotes": {
    "quotes":         [ ... ]    // top-N snippets extracted from candidates
  },
  "cluster":          { ... },   // section outline plan (from earlier pipeline version)
  "summary":          { ... }    // stored generated answer (for offline analysis)
}
```

The `decomposed_query` shows how the original question was expanded for retrieval:

```json
{
  "rewritten_query": "Side effects of dropout regularization in deep neural networks",
  "keyword_query":   "dropout deep neural networks side effects regularization",
  "search_filters":  { "fieldsOfStudy": "Computer Science" }
}
```

---

#### 2. Quotes — What Gets Fed to the LLM

Each element of `quotes.quotes` is one passage extracted from a retrieved paper's full text:

```json
{
  "key":     "[11353672 | Srivastava et al. | 2014 | Citations: 38521]",
  "snippets": "Dropout provides a way of approximately combining exponentially many
               different neural network architectures efficiently ...",
  "inline_citations": {
    "[204838063 | Hinton et al. | 2012 | Citations: 7041]":
        "We used a new regularization technique called 'dropout' that consisted of
         setting to zero the output of each hidden neuron with probability 0.5 ..."
  }
}
```

- **`key`** — citation label `[corpus_id | Author et al. | year | Citations: N]`; this exact string appears as the reference identifier in the generated answer
- **`snippets`** — verbatim passage from the paper's PDF
- **`inline_citations`** — papers cited *within* this snippet; values are their abstracts (used when `args.use_inline_citations = True`)

---

#### 3. Generation Prompt

`ScholarQA.run_qa_pipeline()` in `scholarqa/scholar_qa.py` formats the quotes into a numbered list and fills the prompt template (selected from `scholarqa/llms/prompts.py` based on `args.intent`):

```
[Citation 1]: Dropout provides a way of approximately combining exponentially many
              different neural network architectures efficiently ...
[Citation 2]: Setting to zero the output of each hidden neuron with probability 0.5
              during training prevents units from co-adapting too much ...
...
```

For intent-aware variants (`args.intent = "pcit"`), the prompt additionally instructs the model to emit paragraph-intent (`<bpit>`) and citation-intent (`<bcit>`) annotation tags around each paragraph and each cited claim.

---

#### 4. Raw LLM Output

The LLM returns plain text delimited by `SECTION;` markers. Each section begins with a mandatory two-sentence `TLDR;`:

**Baseline (`intent = "default"`):**
```
SECTION; Introduction
TLDR; Dropout is a regularization method that randomly deactivates neurons to prevent overfitting.
While its main purpose is regularization, it also produces a range of other effects.

Dropout randomly deactivates a fraction of neurons during each training step [Citation 30][Citation 32].
This core mechanism prevents neurons from co-adapting too strongly [Citation 17][Citation 27].

SECTION; Desirable Effects: Model Ensembling and Uncertainty Quantification
TLDR; Dropout can be interpreted as implicitly training an ensemble of many subnetworks.
The same mechanism also enables cheap uncertainty estimation at test time.

A key benefit of dropout is that it approximates model averaging [Citation 2][Citation 9] ...
```

**Intent-aware (`intent = "pcit"`):** identical structure, but with annotation tags:
```
SECTION; Introduction
TLDR; Dropout is a regularization method that randomly deactivates neurons ...

<bpit>[Exposition]: Sets up the core mechanism of dropout to contextualize the subsequent
discussion of its side effects. <epit>
Dropout randomly deactivates a fraction of neurons during each training step [Citation 30][Citation 32].

SECTION; Desirable Effects: Model Ensembling
TLDR; Dropout implicitly trains an exponential number of subnetworks simultaneously.

<bpit>[Mechanism]: Explains the theoretical reason dropout acts as an ensemble. <epit>
A key benefit of dropout is that it approximates model averaging
<bcit>[BACKGROUND]: Establishes the ensemble interpretation as the theoretical basis. </bcit>[Citation 2] ...
```

| Tag | Scope | Meaning |
|-----|-------|---------|
| `<bpit>...<epit>` | Paragraph | *Why* was this paragraph written? (exposition, compare, background, …) |
| `<bcit>...</bcit>` | Inline | *Why* was this paper cited? (background, support, contrast, …) |

This raw text is saved as `output/<split>/raw/raw_output_<intent>_<model>.json` in the format `[{"cache": "<raw text>"}, ...]`.

---

#### 5. Parsed Outputs

`parse_text_response_to_json()` (`scholarqa/scholar_qa.py:126`) converts the raw text into two objects:

**`json_response`** — sections with intent tags preserved (used internally for analysis):
```json
{
  "question": "Apart from preventing overfitting ...",
  "response": {
    "sections": [
      {
        "title": "Introduction",
        "text":  "TLDR; Dropout is a regularization method ...\n\n<bpit>[Exposition]: ...<epit>\nDropout randomly ...",
        "citations": [
          { "id": "[1]", "snippets": ["Dropout provides a way of approximately combining ..."] }
        ]
      }
    ]
  }
}
```

**`clean_json_response`** — all intent tags stripped via `remove_tagged_text_clean()` (the user-facing answer, and the format used for SFT training data):
```json
{
  "question": "Apart from preventing overfitting ...",
  "response": {
    "sections": [
      {
        "title": "Introduction",
        "text":  "Dropout is a regularization method that randomly deactivates neurons ...",
        "citations": [ ... ]
      }
    ]
  }
}
```

Outputs are saved to:
- `output/<split>/` — `json_response` (with tags)
- `output/<split>/formatted/` — `clean_json_response` (clean)
- `output/<split>/raw/` — raw LLM string

---

#### A Note on Intent Reranking

The inference scripts also support `args.rerank = "intent"`, which replaces `quotes.quotes` with an intent-annotated version (`quotes.intent_quotes`). These are produced separately by `rerank_intent.py`, which asks an LLM to label each quote with a citation intent (e.g., `BACKGROUND`, `SUPPORT`) and a relevance score before generation. This augmented re-ranking is one of the methods evaluated in the paper. To generate intent-reranked traces for your own queries, run:

```bash
python rerank_intent.py   # edits args at the bottom of the script
```

---

## Environment Setup

```bash
# 1. Clone this repo
git clone https://github.com/allenai/intent-aware-lfqa
cd intent-aware-lfqa

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API keys
cp .env.example .env
# Edit .env with your keys (S2_API_KEY is required; at least one LLM key)
```

**Required API keys:**
- `S2_API_KEY` — [Semantic Scholar API](https://www.semanticscholar.org/product/api) (for retrieval, if you want to run your own queries besides the provided cached ones)
- At least one of: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`

---

## Inference Pipeline

### Commercial LLMs (Gemini, GPT-4, Claude, …)

```bash
python inference/inference_commercial.py
```

Configure the model and intent variant at the bottom of the script:

```python
args.llm_model = GEMINI_25_PRO   # or GPT_4o, CLAUDE_37_SONNET, etc.
args.intent = "pcit"             # "default", "cit", "pit", or "pcit"
args.rerank = "intent"           # "no" (baseline) or "intent" (intent-aware reranking)
```

### Self-hosted Model via SGLang

Start the SGLang server:

```bash
bash sft/sglang_server.sh
# Edit MODEL_PATH in the script to point to your model
```

Then run inference:

```bash
export OPENAI_BASE_URL=http://localhost:8008/v1
python inference/inference_sglang.py
```

### Configuration Args

All settings are controlled via the `args` object at the bottom of each inference script. Key parameters:

| Arg | Values | Description |
|-----|--------|-------------|
| `args.intent` | `"default"` / `"cit"` / `"pit"` / `"pcit"` | Intent annotation variant (see table below) |
| `args.rerank` | `"no"` / `"intent"` | Use baseline quotes or intent-reranked quotes |
| `args.llm_model` | `GEMINI_25_PRO`, `GPT_4o`, `CLAUDE_37_SONNET`, … | LLM to call (constants from `scholarqa/llms/constants.py`) |
| `args.debug` | `True` / `False` | If `True`, runs only 2 queries — useful for sanity-checking |
| `args.n_rerank` | int (default `50`) | How many quotes to pass to the LLM after reranking |
| `args.max_prompt_tokens` | int (default `30000`) | Token budget for the generation prompt |
| `args.use_inline_citations` | `True` / `False` | Whether to include abstracts of papers cited within a snippet |
| `args.complex_citations` | `True` / `False` | Whether to include inline citation details or simple [1],[2] |
| `args.citations_format` | `"quotes"` / `"candidates"` | Whether to use extracted quotes or raw candidate passages |
| `args.prompt_extraction` | `"yes"` / `"no"` | Whether to extract snippets from candidates on the fly (used for the SFT data prepration) |

**Quick-start examples:**

```python
# Fast debugging run (2 queries, dev split, no intent)
args.split = "dev"
args.intent = "default"
args.debug = True

# Full test run with best intent variant
args.split = "test"
args.intent = "pcit"
args.rerank = "no"
args.debug = False

# Intent-reranked quotes + pcit generation (highest quality)
args.split = "test"
args.intent = "pcit"
args.rerank = "intent"   # requires running rerank_intent.py first
args.debug = False
```

Output is written to `output/<split>/` (with tags), `output/<split>/formatted/` (clean), and `output/<split>/raw/` (raw LLM text).

### Intent Prompts

Four intent variants are available (see Table 2 in the paper):

| Variant | Description |
|---------|-------------|
| `default` | Baseline — no intent tags in prompt |
| `cit`     | Citation intent annotations only |
| `pit`     | Paragraph intent annotations only |
| `pcit`    | Both paragraph + citation intent (best overall) |

Prompts are in `scholarqa/llms/prompts.py`.

---

## SFT Pipeline

### Step 1 — Generate Training Annotations

Run the ScholarQA pipeline on your training queries to produce silver-labeled answers:

```bash
python sft/annotate.py
```

Requires:
- `data/sft/queries.csv` — one query per line
- `data/sft/traces/` — cached retrieval traces
- `data/sft/query_mapping.json` — maps query → trace file ID

If you need the training queries and query mapping, please contact the original author (**xinranz3 [at] andrew [dot] cmu [dot] edu**).

### Step 2 — Convert to Chat Format

Convert annotated outputs to the open-instruct JSONL format:

```bash
python sft/sft_data_synthesis.py
```

### Step 3 — Fine-tune with open-instruct

We use [open-instruct](https://github.com/allenai/open-instruct) for supervised fine-tuning. Example commands for all four variants:

```bash
bash sft/sft_commands.sh
```

### Model & Dataset Variants

Four SFT variants corresponding to the four intent configurations:

- **Baseline** — plain ScholarQA output, no intent tags
- **Explicit** — explicit `<bpit>`/`<bcit>` intent annotations in the output
- **Implicit** — intent baked into the writing style (no visible tags)
- **Multiview** — multi-view intent (combined citation + paragraph intent signals)

All datasets and model checkpoints are available in the [intent-aware-lfqa HuggingFace collection](https://huggingface.co/collections/allenai/intent-aware-lfqa):

| Variant | HuggingFace Dataset | Qwen3-4B | Qwen3-8B | Llama3-8B |
|---------|--------------------|----------|----------|-----------|
| Baseline | [intent-aware-lfqa-baseline](https://huggingface.co/datasets/allenai/intent-aware-lfqa-baseline) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-qwen3-4b-baseline) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-qwen3-8b-baseline) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-llama3-8b-baseline) |
| Explicit | [intent-aware-lfqa-intent-explicit](https://huggingface.co/datasets/allenai/intent-aware-lfqa-intent-explicit) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-qwen3-4b-intent-explicit) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-qwen3-8b-intent-explicit) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-llama3-8b-intent-explicit) |
| Implicit | [intent-aware-lfqa-intent-implicit](https://huggingface.co/datasets/allenai/intent-aware-lfqa-intent-implicit) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-qwen3-4b-intent-implicit) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-qwen3-8b-intent-implicit) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-llama3-8b-intent-implicit) |
| Multiview | [intent-aware-lfqa-multiview](https://huggingface.co/datasets/allenai/intent-aware-lfqa-multiview) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-qwen3-4b-multiview) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-qwen3-8b-multiview) | [checkpoint](https://huggingface.co/allenai/intent-aware-lfqa-llama3-8b-multiview) |

---

## Demo

### Static Report Viewer

A static side-by-side comparison of **Baseline** vs **Intent-Aware** reports is available in `demo/demo.html`.

To view it:
```bash
cd demo
python3 -m http.server 8000
# Open http://localhost:8000/demo.html
```

The demo lets you browse all 100 dev-set questions and see how intent annotations change the generated reports — highlighting paragraph intent (`<bpit>`) and citation intent (`<bcit>`) signals inline.

### Human Evaluation Survey

We conducted a human evaluation study (Section 4.3 of our paper) using a Streamlit-based survey app where participants compared reports from the **Baseline** and **Intent-Aware** systems. A simplified version of the survey is available in `demo/survey/` so you can experience the evaluation interface yourself.

The survey presents AI-generated scientific reports one at a time and asks participants to:
1. **Report Overview Eval** — for each section, rate whether the preview information (section title + paragraph intent label) is sufficient to decide whether to read it (without opening the paragraphs)
2. **Citation Eval** — hover over highlighted citations to see paper snippets, then rate whether you can predict what you would learn from following that citation

Annotations are saved locally to `demo/survey/annotations/`.

**Demo users** (pre-assigned for easy testing):

| Username | Reports served |
|----------|----------------|
| `tester-1`, `IntentTester-1` | 4 Baseline (SQA) reports |
| `IntentTester-2` | 4 Intent-Aware reports |

To run the survey locally:
```bash
pip install streamlit pandas
cd demo/survey
streamlit run app.py
# Open http://localhost:8501
# Log in with: tester-1, IntentTester-1, or IntentTester-2
```

---

## Code Overview

```
intent-aware-lfqa/
│
├── scholarqa/                  # Core ScholarQA library
│   ├── scholar_qa.py           # Main pipeline entry point
│   ├── models.py               # Data models
│   ├── utils.py                # Utilities
│   ├── llms/
│   │   ├── prompts.py          # Intent-aware generation prompts
│   │   ├── rerank_prompts.py   # Intent-aware reranking prompts
│   │   ├── litellm_helper.py   # LLM API wrapper (LiteLLM)
│   │   └── constants.py        # Model name constants
│   ├── rag/
│   │   ├── retrieval.py        # Paper retrieval pipeline
│   │   ├── retriever_base.py   # Base retriever (Semantic Scholar)
│   │   ├── reranker/           # Cross-encoder reranker
│   │   └── multi_step_qa_pipeline.py
│   ├── preprocess/             # Query preprocessing / decomposition
│   └── postprocess/            # Output post-processing
│
├── inference/
│   ├── inference_commercial.py # Run with commercial LLMs
│   └── inference_sglang.py     # Run with self-hosted model (SGLang)
│
├── sft/
│   ├── annotate.py             # Generate SFT training data
│   ├── sft_data_synthesis.py   # Convert to open-instruct format
│   ├── sft_commands.sh         # Fine-tuning commands
│   └── sglang_server.sh        # Start SGLang inference server
│
├── demo/
│   ├── demo.html               # Static side-by-side demo viewer
│   ├── baseline_reports.json   # 100 baseline report examples
│   ├── intent_reports.json     # 100 intent-aware report examples
│   └── survey/                 # Human evaluation survey (Streamlit)
│       ├── app.py              # Survey application
│       ├── requirements.txt
│       └── data/               # Task assignments + model reports (6-report subset)
│
├── data/
│   ├── test_sqa_traces/        # Cached test split traces (236 queries)
│   └── dev_traces/             # Cached dev split traces (100 queries)
│
├── figs/
│   └── intent_motivation_02.pdf
│
├── rerank_intent.py            # Intent-aware snippet reranking
├── rank_intent_quotes.py       # Quote ranking utilities
├── requirements.txt
└── .env.example
```

---

## Evaluation

Automatic evaluation of the generated reports is handled by the **[ASTA-Bench](https://github.com/allenai/asta-bench)** framework. ASTA-Bench provides rubric-based scoring that checks whether a generated report covers the key ingredients specified in `data/rubrics/`. Please refer to that repository for full details on how to run evaluation on your own outputs.

This work is also evaluated on two additional long-form QA benchmarks:

- **[ResearchQA](https://github.com/realliyifei/ResearchQA)** — a benchmark for attributed research question answering
- **[DeepScholarBench](https://github.com/guestrin-lab/deepscholar)** — a benchmark for deep scientific literature understanding

If you need help running evaluation on any of these benchmarks, or have questions about the paper or codebase in general, feel free to reach out: **xinranz3 [at] andrew [dot] cmu [dot] edu**.

---

## Citation

If you use this work, please cite:

```bibtex
@inproceedings{
zhao2026improving,
title={Improving Attributed Long-form Question Answering with Intent Awareness},
author={Xinran Zhao and Aakanksha Naik and Jay DeYoung and Joseph Chee Chang and Jena D. Hwang and Tongshuang Wu and Varsha Kishore},
booktitle={The Fourteenth International Conference on Learning Representations},
year={2026},
url={https://openreview.net/forum?id=fRCm5c8x0j}
}
```
