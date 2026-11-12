# text2sql-active-learning

**SHARP — Stratified Heteroscedastic Active Retrieval on a Partitioned Manifold**

Code for the paper *"Robust Active Learning for Few-Shot Example Selection in Text-to-SQL"* (Arash Pourhabib, NVIDIA, 2026).

## Overview

SHARP addresses the problem of selecting which natural language queries to annotate with SQL in order to build a high-quality few-shot example bank for text-to-SQL systems. It formalizes the selection as a constrained experimental design problem over the low-dimensional intrinsic manifold of semantic query embeddings, with:

- **Heteroscedastic noise modeling** — σ²(x) estimated from LLM self-consistency; hard queries are down-weighted.
- **Partition matroid constraints** — one annotated example per semantic cluster, enforcing diversity.
- **Graceful misspecification** — the approximation guarantee degrades by an additive constant (not catastrophically) when the kernel is misspecified.

## Repository Layout

```
.
├── pyproject.toml             # Package metadata + console scripts
├── requirements.txt           # Pinned runtime dependencies
├── example_config.json        # Template for domain configuration (--config flag)
├── LICENSE                    # Apache 2.0
├── README.md
├── src/text2sql_active_learning/
│   ├── __init__.py
│   ├── run_experiment.py      # Main entry point — runs all experiments and produces paper figures
│   ├── gp_active_learner.py   # GP regression + Algorithm 1 (Stratified Greedy Heteroscedastic MI)
│   ├── embedding_kernel.py    # Kernel implementations (SE, Matérn, RFF)
│   ├── sql_evaluator.py       # SQL semantic evaluation (Component Match, SemanticScore)
│   ├── estimate_noise_prior.py# Pre-compute heteroscedastic noise priors via LLM self-consistency
│   └── replot.py              # Regenerate figures from saved CSVs without re-running experiments
└── tests/
    └── test_smoke.py
```

## Installation

Editable install (recommended for development):

```bash
pip install -e .
```

This exposes three console scripts:

| Console script                  | Module entry point                                    |
|---------------------------------|-------------------------------------------------------|
| `text2sql-run-experiment`       | `text2sql_active_learning.run_experiment:main`        |
| `text2sql-estimate-noise-prior` | `text2sql_active_learning.estimate_noise_prior:main`  |
| `text2sql-replot`               | `text2sql_active_learning.replot:main`                |

You can also invoke modules directly:

```bash
python -m text2sql_active_learning.run_experiment --db milvus.db
python -m text2sql_active_learning.replot
```

## Building Your Milvus Database

The experiments require a [Milvus Lite](https://milvus.io/docs/milvus_lite.md) database (a local SQLite-backed `.db` file). **The database is not included in this repository** — you must build your own from your domain's annotated query corpus.

### Required collection schema

**SQL examples collection** (default name: `text2sql_examples`):

| Field      | Type          | Description                                      |
|------------|---------------|--------------------------------------------------|
| `id`       | int64 (PK)    | Row identifier                                   |
| `text`     | varchar       | Natural language question                        |
| `sql`      | varchar       | Ground-truth SQL query                           |
| `analysis` | varchar       | Domain/analysis-type label (used for clustering) |
| `vector`   | float_vector  | Text embedding (e.g. d=2048)                     |

**DDL collection** (optional, default name: `text2sql_ddl`):

| Field | Type    | Description              |
|-------|---------|--------------------------|
| `ddl` | varchar | Table definition strings |

### Example: populating the database

```python
from pymilvus import MilvusClient, DataType

client = MilvusClient("milvus.db")

# Create the SQL examples collection
schema = client.create_schema(auto_id=False, enable_dynamic_field=False)
schema.add_field("id",       DataType.INT64,        is_primary=True)
schema.add_field("text",     DataType.VARCHAR,      max_length=2000)
schema.add_field("sql",      DataType.VARCHAR,      max_length=4000)
schema.add_field("analysis", DataType.VARCHAR,      max_length=200)
schema.add_field("vector",   DataType.FLOAT_VECTOR, dim=2048)

index_params = client.prepare_index_params()
index_params.add_index("vector", metric_type="L2")

client.create_collection("text2sql_examples", schema=schema, index_params=index_params)

# Insert your annotated examples
data = [
    {"id": i, "text": q, "sql": s, "analysis": domain, "vector": embed(q)}
    for i, (q, s, domain) in enumerate(your_corpus)
]
client.insert("text2sql_examples", data)
```

The embedding model used in the paper is `nvidia/llama-3.2-nv-embedqa-1b-v2` (d=2048), available via the [NVIDIA NIM API](https://build.nvidia.com/). Any sentence embedder works, as long as the `vector` dimension matches what you put in.

## Domain Configuration

By default, domains and test-set sizes are **auto-detected from your database**:

- `seed_domain` — the domain with the most examples (natural cold-start bias).
- `sim_test_sizes` — ~20% of each domain's examples, capped to [4, 10].
- `llm_domains` — all domains found in the DB.
- `llm_test_sizes` — same formula applied to LLM domains.

To override any of these, create a JSON config file (use `example_config.json` as a template):

```json
{
  "seed_domain": "my_domain",
  "sim_test_sizes": {"my_domain": 10, "other_domain": 8},
  "llm_domains": ["my_domain"],
  "llm_test_sizes": {"my_domain": 10}
}
```

All fields are optional — omit any field to fall back to auto-detection. Pass the file via `--config`:

```bash
text2sql-run-experiment --sim-only --db /path/to/milvus.db --config my_config.json
text2sql-estimate-noise-prior --db /path/to/milvus.db --config my_config.json
```

## Running the Experiments

All scripts accept `--db`, `--collection`, and `--ddl-collection` arguments. You can also set them via environment variables or a `.env` file in the working directory:

```bash
MILVUS_DB_PATH=/path/to/milvus.db
MILVUS_COLLECTION=text2sql_examples
MILVUS_DDL_COLLECTION=text2sql_ddl
```

### Retrieval simulation (fast, no LLM, ~2 min)

Evaluates all four methods using oracle SemanticScore retrieval. No API key required.

```bash
text2sql-run-experiment --sim-only --db /path/to/milvus.db
```

### End-to-end LLM evaluation (~25 min)

Requires an LLM API key. Set `NGC_API_KEY` for the NVIDIA API or `OPENAI_API_KEY` for OpenAI-compatible endpoints. Override the model and endpoint via environment variables:

```bash
export NGC_API_KEY=your_key
export LLM_BASE_URL=https://integrate.api.nvidia.com/v1   # or your endpoint
export LLM_MODEL=meta/llama-3.1-70b-instruct

text2sql-run-experiment --llm-only --db /path/to/milvus.db
```

To run multiple seeds and tighten bootstrap confidence intervals:

```bash
text2sql-run-experiment --append --db /path/to/milvus.db  # adds a second run
text2sql-run-experiment --append --db /path/to/milvus.db  # adds a third run, etc.
```

### Full pipeline

```bash
text2sql-run-experiment --db /path/to/milvus.db
```

### Realistic GP experiment (LLM-scored labels)

```bash
text2sql-run-experiment --realistic --db /path/to/milvus.db
```

### Regenerate figures from saved results

```bash
text2sql-replot
```

### Pre-compute heteroscedastic noise priors

Run this before the main experiment to enable the full SHARP noise model. Takes ~750 LLM calls (default settings).

```bash
text2sql-estimate-noise-prior --db /path/to/milvus.db
```

## Output

All results are written to `./results/` (relative to the working directory):

| File                           | Description                                          |
|--------------------------------|------------------------------------------------------|
| `sim_results.csv`              | Per-round retrieval simulation metrics               |
| `sim_efficiency.csv`           | Domain discovery efficiency summary                  |
| `llm_results.csv`              | LLM end-to-end evaluation metrics                    |
| `llm_per_query.json`           | Per-query scores for bootstrap confidence intervals  |
| `gp_pred_results.csv`          | GP prediction RMSE/MSE on held-out pool              |
| `realistic_results.csv`        | Realistic GP experiment (LLM-scored labels)          |
| `noise_prior.json`             | Pre-computed heteroscedastic noise priors            |
| `learning_curves_sim.png`      | Domain coverage + non-seed domain score              |
| `efficiency_sim.png`           | Bar chart: labels to reach 6/7 domain coverage       |
| `learning_curves_llm.png`      | 4-panel LLM evaluation curves                        |
| `gp_pred_sim.png`              | GP prediction RMSE/MSE curves                        |
| `learning_curves_realistic.png`| Realistic GP experiment learning curves              |

## Methods

| Method key    | Display name          | Description                                          |
|---------------|-----------------------|------------------------------------------------------|
| `random`      | Random                | Uniform random sampling from pool                    |
| `uncertainty` | Uncertainty Sampling  | Logistic regression on binarized labels              |
| `threshold`   | Dist-to-Threshold     | Greedy max-min-distance (space-filling baseline)     |
| `proposed`    | SHARP                 | Algorithm 1: Stratified Greedy Heteroscedastic MI    |

All methods use:
- The same system prompt: *"You are a SQL generation assistant. Given few-shot question/SQL examples and a new question, output only the SQL query."*
- The same K=5 nearest-neighbor retrieval at evaluation time.

## Key Hyperparameters

| Parameter        | Value | Description                                    |
|------------------|-------|------------------------------------------------|
| `SEED_SIZE`      | 5     | Initial labeled examples (single domain)       |
| `BATCH_SIZE`     | 5     | Examples added per active learning round       |
| `N_ROUNDS`       | 9     | Rounds → 50 total labeled examples             |
| `K_RETRIEVAL`    | 5     | Nearest neighbors retrieved per test query     |
| `PCA_COMPONENTS` | 30    | Manifold projection dimension (d_I ≈ 18)       |
| `GP_NOISE_VAR`   | 0.05  | Base GP observation noise                      |
| `NOISE_MIN`      | 0.03  | Minimum heteroscedastic noise σ²(x)            |

## Tests

```bash
pip install -e ".[dev]"
pytest
```

The shipped tests are smoke tests for the kernel math. End-to-end tests require a Milvus database, so they are not bundled here.

## Citation

```bibtex
@article{pourhabib2026sharp,
  title   = {Robust Active Learning for Few-Shot Example Selection in Text-to-SQL},
  author  = {Pourhabib, Arash},
  year    = {2026},
  note    = {NVIDIA}
}
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Support

**Support level: Experimental / research code.** This repository is published as a reference implementation accompanying the paper. Issues and pull requests will be reviewed on a best-effort basis; there is no SLA for response times. For questions about the algorithm or the paper, please open a GitHub issue.

## Security

Please **do not** file public GitHub issues for security reports. See [SECURITY.md](SECURITY.md) for NVIDIA's vulnerability disclosure process.

## License

Apache License 2.0 — see [LICENSE](LICENSE). Third-party dependency licenses are listed in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
