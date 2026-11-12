# Rubric Building for AI2 ScholarQA Evaluation

This directory includes the implementation of automated rubric generation pipeline that supports ScholarQA-CS2 discussed and released with [AstaBench](https://arxiv.org/abs/2510.21652).
Our rubric generation is conducted through a two-stage pipeline that uses Claude’s API to extract key requirements (“ingredients”) from reports and unify them into comprehensive evaluation rubrics with weighted criteria. 

ScholarQA-CS2 evaluation uses **four evaluation metrics**. The generated rubric is used to assess the **Answer Recall** evaluation.
The rubric ingredients are used at answer evaluation-time to measure coverage. For each ingredient 
cluster, the LLM judge gives a score of 0 (does not meet the criterion described in the rubric
ingredient), 1 (somewhat meets the criterion) or 2 (perfectly meets the criterion). The final answer
coverage score is a weighted average of the individual ingredient scores, with ingredient importance
determining the weight with “answer critical” ingredients counting twice as much as the “valuable" ingredients.

The remaining three metrics are as follows. Further details are available in the paper.
* **Answer Relevance**: Fraction of paragraphs in the report that addresses the question
* **Citation Recall**: Fraction of claims in the report fully supported by citations
* **Citation Precision**: Fraction of citations in the report that (fully or partially) support associated claims.


## Overview

The rubric building process consists of two main stages:

1. **Ingredient Extraction** - Analyzes system reports to identify key requirements and criteria. [[See Prompt]](https://github.com/allenai/ai2-scholarqa-eval/blob/84cb60c8352778f6c8c964b49ca63cb2e41e5c9c/rubric_building/utils/prompts.py#L1)
   1. In our study we extract report from 10 sources:
      1. 8 deep-research agents with retrieval: 
         * `ScholarQA` [(Singh et al. 2025](https://arxiv.org/abs/2504.10861); [asta.allenai.ai](https://asta.allen.ai/synthesize))
         * `Elicit` [(elicit.com)](https://elicit.com)
         * `FutureHouse Falcon` [(futurehouse.org)](https://www.futurehouse.org/)
         * `OpenAI Deep Research` [(openai.com)](https://openai.com)
         * `Perplexity Sonar Deep Research` [(perplexity.ai)](https://docs.perplexity.ai/)
         * `SciSpace Deep Review` [(scispace.com)](https://scispace.com/)
         * `STORM` [(Shao et al. 2024](https://arxiv.org/abs/2402.14207); [storm.genie.stanford.edu)](https://storm.genie.stanford.edu/)
         * `You.com Research`[(you.com)](https://you.com/home)
      2. 2 LLMs without retrieval: 
         * `Claude Sonnet 4.0 without thinking` [(anthropic.com)](https://www.anthropic.com/)
         * `Google’s Gemini 2.5 Pro` [(gemini.google.com)](https://gemini.google.com)
2. **Ingredient Unification** - Consolidates ingredients from multiple sources into coherent, non-overlapping rubrics. [[See Prompt]](https://github.com/allenai/ai2-scholarqa-eval/blob/84cb60c8352778f6c8c964b49ca63cb2e41e5c9c/rubric_building/utils/prompts.py#L41)


**Average Cost Estimation**: The estimated cost of running the full rubric-generation pipeline in batch mode for 100 instances using Claude-Opus-4.5 was $120 (July–October 2025).


## Project Structure

```
rubric_building/
├── 1_generate_ingredients.py       # Stage 1: Extract ingredients from reports
├── 2_unify_ingredients.py          # Stage 2: Unify ingredients into rubrics
├── claude_process_batch.py         # Process batch API results
├── utils/
    ├── utils_rubric_building.py    # Utility functions (JSON parsing, batch requests)
    └── prompts.py                  # Prompts for extraction and unification
├── config_extract_ingredients.yaml # Configuration for extraction stage
├── config_unify_ingredients.yaml   # Configuration for unification stage
├── logs_extraction/                # Extraction stage outputs
├── logs_unification/               # Unification stage outputs
└── outputs/                        # Final rubrics
```

## Requirements

- Python 3.10+
- Required packages:
  - anthropic
  - pandas
  - pyyaml
  - tqdm

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```



## Execution Flow

---

### Stage 1: Ingredient Extraction

**Overview**: The extraction stage analyzes system reports to identify:
- **High-level requirements**: What concepts should be covered
- **Specific details**: Examples and citations supporting each requirement
- **Criticality**: Whether requirements are answer-critical (SHOULD) or valuable (MIGHT)

**Key features**:
- Uses Claude's extended thinking mode (3072 token budget)
- Recommended Models: Sonnet-4.6 or Opus-4.5
- Outputs structured JSON with ingredient IDs, descriptions, examples, and citations

**Script**: `1_generate_ingredients.py`

**Config**: `config_extract_ingredients.yaml`
```yaml
batch_run: true          # true = submit as Anthropic batch job (recommended); false = process one-by-one
sanity_check: true       # !! SET TO false to make API call — true only prints prompts, makes no API calls
specific_solvers:        # uncomment lines below to restrict to specific solvers; leave blank to use all
#  - 'sqa-4-tables-solver'
#  - 'openai-deep-research-solver'
query_constraints: []    # list specific query strings to include; leave empty for all
query_excludes: []       # list specific query strings to skip
experiment_name: sample-queries          # !! ASSIGN a meaningful name. This will label your run in output filenames and metadata
solver_reports_path: ../meta_evaluation/system_reports/test/  # path to input reports
log_dir: logs_extraction                 # output directory; leave as-is unless you need a custom path
extractor_model: claude-opus-4-20250514  # Claude model to use for extraction
```

#### Process

1. Fill in configuration. Make sure you assign a meaningful `experiment_name`.  There are two modes of run available:
   * **batch** (`batch_run=true`): builds one API request per triple (extended thinking, prompt caching on system prompt), submits the batch to Anthropic, saves the returned `batch_id`. Batch run requires the use of `claude_process_batch.py` to pull and format the generations (see below). Rest of the pipeline assumes batch run.
   * **individual** (`batch_run=false`; _to be used for test extraction runs only_): \calls Claude sequentially; appends results directly to `logs_extraction/indiv-extractions.json`. Isolated run, for fast spot check and test runs.
2. Run the script.
    ```
    python 1_generate_ingredients.py
    ```
   
3. Find the intermediary outputs in `logs_extraction/`
    * `logs_extraction/YYYYMMDD-HHMM-request_reference.json`: id-assigned instances to be used for the batch request
    * `logs_extraction/YYYYMMDD-HHMM-batch_requests.json`: the requests to be sent to the API
    * `logs_extraction/YYYYMMDD-HHMM-run_info.json`: metadata file required by `claude_process_batch.py` to process the results 
   
4. **Note the timestamp prefix** (e.g., `20250624-1423`) from the `run_info.json` filename — you'll need it for `claude_process_batch.py`.

* Arguments:
  - `-r, --run`: Operation to perform
  - `-l, --log_dir`: Log directory containing run files
  - `-p, --run_prefix`: Timestamp prefix from run_info.json file
  - `-s, --saved_generation`: (Optional) Use cached generation results

* Runs:
  * To check if batch is done: 
    ```
    python claude_process_batch.py -r check_status -l logs_extraction -p YYYYMMDD-HHMM
    ```
  * Once the batch is complete, fetch result from Anthropic:
    ```
    python claude_process_batch.py -r process_extraction_results -l logs_extraction -p YYYYMMDD-HHMM
    ```
  * If you already pulled generation results from Anthropic in a previous run and don't want to re-fetch, pass the saved file with `-s`:
    ```
    python claude_process_batch.py -r process_extraction_results -l logs_extraction -p YYYYMMDD-HHMM \
        -s logs_extraction/YYYYMMDD-HHMM_generation_output.json
    ```

**Output**: `logs_extraction/YYYYMMDD-HHMM-generation_output.jsonl` (*The output file is the input to Stage 2*)

---

### Stage 2: Ingredient Unification

The unification stage:
1. Identifies key concepts and entities from the query
2. Groups overlapping or duplicate ingredients
3. Creates minimal set of non-overlapping requirements
4. Distributes examples across unified requirements
5. Prunes duplicate or irrelevant examples
6. Assigns weights: 2x for answer-critical, 1x for valuable

**Key features**:
- Uses Claude's extended thinking mode (3072 token budget)
- Recommended Model: Opus-4.5


**Script**: `2_unify_ingredients.py`

**Config**: `config_unify_ingredients.yaml`
```yaml
batch_run: true          # same as Stage 1 — true = batch (recommended)
sanity_check: true       # !! SET TO false to make API call — true only prints prompts, makes no API calls
specific_solvers:        # same filtering as Stage 1; leave blank to use all solvers from Stage 1 output
#  - 'sqa-4-tables-solver'
query_constraints: []
query_excludes: []
experiment_name: sample-queries   # !! SET THIS — should MATCH Stage 1 or describe this unification run
all_ingredients_file: logs_extraction/YYYYMMDD-HHMM-generation_output.jsonl  # !! UPDATE to Stage 1 output path
log_dir: logs_unification
unifier_models:
  - claude-opus-4-20250514        # can list multiple models; one batch request per (query, model) pair
```

#### Process

1. Adjust config file. 
   * Note the exact name of the output file from Stage 1 batch process, and update `all_ingredients_file` in the config with the name.
   * There are two modes of run available:
     * **batch** (`batch_run=true`): Batch run requires the use of `claude_process_batch.py` to pull and format the generations (see below). Rest of the pipeline assumes batch run.
     * **individual** (`batch_run=false`; _to be used for test unification runs only_): calls Claude sequentially; appends results directly to `logs_extraction/indiv-unified-generations.json`. Isolated run, meant for fast spot check and test runs.
2. Run the script.
    ```
    python 2_unify_ingredients.py
    ```
3. Find intermediary outputs in `logs_unification/`
   * `YYYYMMDD-HHMM-ingredient_reference.json`: id-assigned instances to be used for batch request
   * `YYYYMMDD-HHMM-batch_requests.json`: the requests to be sent to the API
   * `YYYYMMDD-HHMM-run_info.json`: metadata file required by `claude_process_batch.py` to process the results
4. **Note the timestamp prefix** (e.g., `20250624-1423`) from the `run_info.json` filename — you'll need it for `claude_process_batch.py`.
* Arguments:
  - `-r, --run`: Operation to perform
  - `-l, --log_dir`: Log directory containing run files
  - `-p, --run_prefix`: Timestamp prefix from run_info.json file
  - `-s, --saved_generation`: (Optional) Use cached generation results

* Runs:
  * To check if batch is done: 
    ```
    python claude_process_batch.py -r check_status -l logs_unification -p YYYYMMDD-HHMM
    ```
  * Once the batch is complete, fetch result from Anthropic: 
    ```
    python claude_process_batch.py -r process_unification_results -l logs_unification -p YYYYMMDD-HHMM
    ```
  * If you already pulled generation results from Anthropic in a previous run and don't want to re-fetch, pass the saved file with `-s`:
    ```
    python claude_process_batch.py -r process_unification_results -l logs_unification -p YYYYMMDD-HHMM \
        -s logs_unification/YYYYMMDD-HHMM_generation_output.json
    ```

**Final Output**: `outputs/YYYYMMDD-HHMM-20251022-0809_unified_rubrics-{experiment_name}.jsonl` (final rubric)


**Final Output Rubric format**:
```json
{
  "question": "query text",
  "ingredients": [
    {
      "name": "answer_critical_0",
      "criterion": "requirement description",
      "weight": 0.25,
      "examples": ["example1", "example2"]
    }
  ],
  "case_id": "unique_id",
  "annotator": "auto",
  "exp": "experiment_name"
}
```


## Citation
```
@misc{bragg2025astabenchrigorousbenchmarkingai,
      title={AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite}, 
      author={Jonathan Bragg and Mike D'Arcy and Nishant Balepur and Dan Bareket and Bhavana Dalvi and Sergey Feldman and Dany Haddad and Jena D. Hwang and Peter Jansen and Varsha Kishore and Bodhisattwa Prasad Majumder and Aakanksha Naik and Sigal Rahamimov and Kyle Richardson and Amanpreet Singh and Harshit Surana and Aryeh Tiktinsky and Rosni Vasu and Guy Wiener and Chloe Anastasiades and Stefan Candra and Jason Dunkelberger and Dan Emery and Rob Evans and Malachi Hamada and Regan Huff and Rodney Kinney and Matt Latzke and Jaron Lochner and Ruben Lozano-Aguilera and Cecile Nguyen and Smita Rao and Amber Tanaka and Brooke Vlahos and Peter Clark and Doug Downey and Yoav Goldberg and Ashish Sabharwal and Daniel S. Weld},
      year={2025},
      eprint={2510.21652},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2510.21652}, 
}
```




