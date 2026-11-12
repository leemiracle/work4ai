# DRACULA: Action-level Feedback for Deep Research Agents

This repository contains the data, prompting pipelines, and evaluation logic for **DRACULA**, introduced in:

> **DRACULA: Hunting for the Actions Users Want Deep Research Agents to Execute**

![DRACULA](images/image.png)

Scientific Deep Research agents can synthesize papers into reports, but most feedback loops only score final outputs. DRACULA focuses on a key upstream question: **which intermediate actions users actually want agents to execute**.

This repository contains the DRACULA dataset (§2), qualitative coding analyses (§3), and experiments for simulating the actions users select with LLM predictions (§4)

---

## 🔗 Links

If you're interested just in the dataset, or in the **online MyScholarQA system** that we used to collect DRACULA, check out these links:

| Resource | Link |
|----------|------|
| 📝 **Paper** | [DRACULA (Under Review)](https://drive.google.com/file/d/1EOpybBGWVAb5R2s4bzeUFU6ux1cgjZIK/view) |
| 🤗 **Huggingface Dataset** | [allenai/DRACULA](https://huggingface.co/datasets/allenai/DRACULA) |
| 🌐 **Live demo** | [personalized-scholarqa.apps.allenai.org](https://personalized-scholarqa.apps.allenai.org) |
| 💻 **UI repository** | [github.com/allenai/personalized-scholarqa](https://github.com/allenai/personalized-scholarqa) |
| 📊 **MyScholarQA evaluation repository**  | [github.com/allenai/personalized-scholarqa-eval](https://github.com/allenai/personalized-scholarqa-eval) |

---

## 🛠️ Setup

This repository uses Python and `uv` for execution.

### 1️⃣ Clone the repository

```bash
git clone https://github.com/allenai/dracula.git
cd dracula
```

### 2️⃣ Create environment and install dependencies

We recommend using [`uv`](https://github.com/astral-sh/uv) to create and manage your environment and dependencies:

```bash
uv venv
source .venv/bin/activate
uv sync
```

### 3️⃣ Environment variables

Create a `.env` file in the repo root and add the API keys if LLM provides you plan to use (through litellm):

```bash
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
HF_TOKEN=...
```

---

## 📁 Dataset Information

The DRACULA dataset lives under `local_data/`:

- **`local_data/DRACULA/`:** the DRACULA dataset with user queries, profiles, actions
- **`local_data/user_rules/`:** User-written rule for stated preferences experiments

You can also view the DRACULA dataset on [huggingface](https://huggingface.co/datasets/nishantb-ai2/DRACULA)

---

## 🚀 Usage

Our codebase supports three main functionalities: running action prediction models, evaluating those models, and qualitative coding of data in DRACULA. We'll now walk through each step, which can be run using scripts in `sample_scripts/`:

### 1) Action Prediction Experiments

The main experiments for action prediction (§4) can be grouped into prompting experiments without retrieval, prompting experiments with retrieval, and prompting with alternative task formats:

```bash
./sample_scripts/predict_actions.sh                     # Action prediction models without retrieval
./sample_scripts/predict_actions_retrieval.sh           # Action prediction models with retrieval
./sample_scripts/predict_actions_alternative_task.sh    # Action prediction models experiments in pairwise and ranking formats (the preference format is not recommended, it is very expensive and much worse than the other two)
```

Broadly, each script allows you to specify a model you want to run, an enum corresponding to an experiment run in the paper, and hyper-parameters for prediction, which are described in the next section titled "Sample Script Parameters"

### 2) Metrics / analysis

The metrics for our experiments can be found in the `/analysis/ folder:

```python
uv run python3 analysis/accuracy.py               # Accuracy for all binary classification experiments
uv run python3 analysis/accuracy_preferences.py   # Accuracy for pairwise comparison experiments
uv run python3 analysis/accuracy_rank.py          # Accuracy for ranking/multi-classification experiments
```

At the top of each file, you can define the models, the run name, the experiments, and metric (accuracy, F1, Cohen's Kappa, MCC) you want to use for evaluating prediction performance. Each script prints a table with these scores

These Python entry points are also grouped under the following bash script:
```bash
./sample_scripts/metrics.sh
```

### 3) Qualitative Coding

To reproduce our human–LLM method for qualitative coding on actions and rationales (§3.2), you can run the following steps:

First, infer and merge clusters using a sample of actions and rationales with Claude-4.6 Sonnet

```python
uv run python qualitative_coding/cluster_actions.py      # Types of actions
uv run python qualitative_coding/cluster_rationales.py   # Reasons for selecting and rejecting actions
```

This will write merged cluster JSON under `qualitative_coding/results/<model>/`: `action_clusters.json` (for action types), `rationale_clusters_good.json` (for rationales behind selected actions), and `rationale_clusters_bad.json` (for rationales behind rejected actions). By default, `<model>` is `anthropic/claude-opus-4-6`.

Next, prompt Gemini-3 Flash to classify every action and rationale into its appropriate cluster

```python
uv run python qualitative_coding/classify_into_clusters.py  # Classify actions + rationales into their clusters
```

These Python entry points are also grouped under the following bash script:
```bash
./sample_scripts/qualitative_coding.sh
```

The results are saved at `qualitative_coding/results/coded_data.jsonl` (one JSON object per line). The results used in the paper can be found in `saved_results/*`


---

## 🔧 Sample Script Parameters

All three prediction scripts share the same parameters:

| Parameter | Description |
|----------|-------------|
| `current_run_name` | Top-level run ID written into result/model paths (e.g., `results/<run_name>/...`). |
| `models` | List of model identifiers (e.g., `openai/gpt-4.1-2025-04-14`) to loop over. |
| `generation_strategies` | The strategy used to make predictions (ModelStrategy in `enums.py`). Most experiments use `prompt` (prompting LLMs) or `prompt_retrieve` (retrieval experiments) |
| `per_user` | If `true` use user-specific history. If `false`, use examples from all users |
| `experiments` | List of `PromptType` experiment names passed as `--prompt_type` (PromptType in `enums.py`) |
| `num_examples` | For retrieval experiments, the number of examples to use |
| `dataset_name` | Dataset root path (default `local_data/DRACULA`). |
| `train_split`, `val_split`, `test_split` | Dataset split names for endpoint calls. |
| `prompt_dir` | Directory of the prompts (default is `prompts`) |
| `res_dir` | Base results directory where JSONL outputs are written (default is `results`). |
| `model_save_dir` | Directory for saving model artifacts/prompts/checkpoints. |
| `cache_dir` | HF cache directory; exported to `HF_HOME` and `HF_DATASETS_CACHE`. |

Each script runs both:

1. `uv run python3 -m model.endpoints.train ...`
2. `uv run python3 -m model.endpoints.test ...`

for every combination of model × strategy × experiment × reasoning. The `train.py` script constructs prompts, and the `test.py` script applies those prompts to test set examples

---

## 🧪 Experiment Parameters (`PromptType`)

The experiment names below come from `model/enums.py` and are used in `--prompt_type`.

| PromptType value | Category | Purpose |
|------------------|----------|---------|
| `judge_action_vanilla` | Baseline | Zero-shot action judging baseline. |
| `judge_action` | Baseline | Few-shot action judging baseline. |
| `judge_action_exact_number_per_user` | Ablation | Controls example counts between per-user and all user settings. |
| `judge_action_add_user_stats` | Feature engineering | Adds user-level statistics to the prompt context. |
| `judge_action_add_profile` | Feature engineering | Adds user profile/rules information to the prompt context. |
| `judge_action_add_categories_history` | Feature engineering | Adds action qualitative categories to the prompt context. |
| `judge_action_add_cot` | Feature engineering | Adds user rationales for selections as a chain-of-though to the prompt context. |
| `judge_action_add_query_stats_history` | Feature engineering | Adds intent and expertise to the prompt context. |
| `judge_action_retrieve_random` | Retrieval | Retrieves random prior examples as context. |
| `judge_action_retrieve_newest` | Retrieval | Retrieves most recent prior examples. |
| `judge_action_retrieve_oldest` | Retrieval | Retrieves oldest prior examples. |
| `judge_action_retrieve_grit` | Retrieval | Retrieves via GritLM relevance. |
| `judge_action_retrieve_llm` | Retrieval | Retrieves via LLM-as-a-reranker. |
| `judge_action_retrieve_icai` | Retrieval (stated preferences) | Uses LLMs to infer preference rules, then uses them to make predictions (similar to Inverse Constitutional AI). Inferred rules are saved under `local_data/user_rules` |
| `judge_action_human_icai` | Retrieval (stated preferences) | Uses human-authored rules to make predictions. |
| `judge_action_rank_all` | Alternative format | Converting action prediction into a ranking format. |
| `judge_action_preference_single_exhaustive_with_tie` | Alternative format | Converting action prediction into a pairwise format. |

---

## 📂 Project Structure

```text
├── analysis/                  # Metric computation and analysis scripts
├── local_data/                # Local DRACULA datasets and user rules
├── model/
│   ├── endpoints/             # Train/test entrypoints
│   ├── generators/            # Prompt and retrieval generators
│   ├── args.py                # Unified CLI args
│   └── enums.py               # PromptType / strategy / reasoning enums
├── prompts/
│   └── prompt_templates/      # Prompt template files by task family
├── qualitative_coding/        # Logic for qualitative coding
├── sample_scripts/            # Reproducible experiment launch scripts
├── pyproject.toml             # Project metadata and dependencies
└── README.md
```

---

## 📚 Citation

If you use this codebase or dataset, please cite:

```bibtex
Coming soon :)
```

## 📄 License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## 📧 Contact

This work was done during my wonderful internship at Ai2's Semantic Scholar team.

If you encounter issues that are easy to fix, we would appreciate it if you made a pull request! For other concerns or questions about the paper, please reach out to:

- Nishant Balepur, Intern ([mailto:nishantbalepur@gmail.com](nishantbalepur@gmail.com))
- Aakanksha Naik, Mentor ([mailto:aakankshan@allenai.org](aakankshan@allenai.org))

Happy hunting! 🧛
