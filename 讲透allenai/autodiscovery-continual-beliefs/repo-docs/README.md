![autodiscovery_logo.png](artifacts/autodiscovery_continual_logo.png)
# Evidence-Informed LLM Beliefs for <mark>Continual</mark> Scientific Discovery

> Paper: https://arxiv.org/abs/2606.29182  
> Previous Work: [AutoDiscovery](https://openreview.net/pdf?id=kJqTkj2HhF) (NeurIPS 2025)

## Installation

### pip (command-line tool)

Use **Python 3.10 or newer**. This repository uses 3.10+ syntax (for example `float | None` type hints). **Anaconda `base` is often Python 3.9**, which cannot run the code and, for a long time, could not install `matplotlib` 3.10 at all—use the `autodiscovery` conda env from `environment.yml` (Python 3.11), or a 3.10+ venv, for `pip install -e .`.

From the repository root, install in editable mode so the `autodiscovery` CLI is on your `PATH`. **Use the same interpreter for pip and python** (see below):

```sh
python -m pip install -e .
```

Plain `pip install` can invoke a **different** Python than `python` (for example Anaconda 3.9’s `pip` while `python` is 3.13 from the Microsoft Store or `py` launcher paths—common in Git Bash/Cygwin). That produces errors like `requires a different Python: 3.9.20 not in '>=3.10'`. Check with `python -m pip --version` and `python --version`.

Then run a short exploration demo:

```sh
autodiscovery \
    --work_dir="work" \
    --out_dir="outputs" \
    --dataset_metadata="discoverybench/real/test/nls_ses/metadata_0.json" \
    --n_experiments=16 \
    --model="gpt-4o" \
    --belief_model="gpt-4o"
```

See [Evidence-informed / ICL beliefs (paper configurations)](#evidence-informed--icl-beliefs-paper-configurations) below for the full experiment commands used in the paper.

You can also invoke the package as a module (no `PYTHONPATH` needed after install). The importable package directory is still named `src`:

```sh
python -m src.run --help
```

On Windows, if the `autodiscovery` command is not found, ensure the `Scripts` directory for that Python install is on your `PATH` (pip mentions the exact folder when it installs console scripts).

### conda

Create the environment with:

```sh
conda env create -f environment.yml
conda activate autodiscovery
```

`environment.yml` installs the project in editable mode (`pip install -e .`), where the runtime dependencies are pulled from `pyproject.toml` and the `autodiscovery` CLI is available in the env.

Set environment variables:

```sh
# (for Linux/MacOS/Bash/Cygwin)
export PYTHONPATH=$(pwd):$PYTHONPATH;

# (for Windows CMD)
set PYTHONPATH=%cd%;%PYTHONPATH%

# (if OPENAI_API_KEY is not already set)
export OPENAI_API_KEY=<key>
```

## Datasets

### DiscoveryBench

```sh
git clone https://github.com/allenai/discoverybench.git temp_db
cp -r temp_db/discoverybench discoverybench
rm -rf temp_db
```

### Blade

```sh
git clone https://github.com/behavioral-data/BLADE.git temp_db
cp -r temp_db/blade_bench/datasets blade
rm -rf temp_db
```

### BYO-Datasets!
You can also use your own datasets. To do this, pass in a dataset metadata JSON file containing descriptions of the paths of datasets (relative to the metadata file) and their column descriptions in natural language. You can have a look at the metadata files in the `DiscoveryBench` directory from above as examples, or see a description of the metadata format from the DiscoveryBench repository [here](https://github.com/allenai/discoverybench/blob/main/discoverybench/README.md).

## Run AutoDiscovery (MCTS-based hypothesis search and verification)

After `pip install -e .`, use `autodiscovery` or `python src/run.py` interchangeably. To resume a previous run, pass
`--continue_from_dir=<log_dir>` (or `--continue_from_json=<mcts_nodes.json>`) so MCTS continues from saved nodes.

## Evidence-informed / ICL beliefs (paper configurations)

The paper uses three CLI entry points:

| Tool | Purpose |
| --- | --- |
| `autodiscovery` / `python src/run.py` | MCTS search with optional in-context (ICL) belief rewards |
| `python -m src.eval_icl_baselines` | Post-hoc ICL evaluation on a fixed `mcts_nodes_all.json` |
| `python scripts/get_hyp_embeds.py`, `python src/deduplication.py` | Hypothesis embeddings (top-k ICL context) and offline dedupe |

### Shared defaults (paper runs)

These settings were used across the main search and eval experiments (see `args.json` in each run directory):

- `--model=gpt-4o`, `--belief_model=gpt-5-mini`, `--belief_reasoning_effort=low`
- `--n_experiments=500` for search runs; `--n_experiments=200` for the base eval trajectories used by the spurious-surprisal figures
- `--compute_icl_beliefs` (always log ICL deltas, even for static runs)
- `--topk_for_icl_beliefs=25`
- `--mcts_selection=ucb1_recursive`, `--branching_factor=8`, `--n_belief_samples=5`, `--surprisal_width=0.2`
- Datasets: `nls-ses`, `archaeology`, `evo-fresh-fish`, `mortgage`, `fertility` (add `--dataset_metadata_type=blade` for the last two)

**Flag distinction:** `--compute_icl_beliefs` elicits ICL priors for logging and analysis; `--use_icl_beliefs` uses those
priors for MCTS reward (non-stationary search).

### MCTS search variants

Paper run names encode three independent axes. Combine the suffixes below (e.g. `icl-topk-dedupe-nextthresholdshiftleast`).

| Axis | CLI flag | Static (off) | Non-stationary / variant (on) |
| --- | --- | --- | --- |
| Belief reward | `--use_icl_beliefs` | omit | `--use_icl_beliefs` |
| Online dedupe | `--use_online_dedupe` | omit | `--use_online_dedupe` |
| Next experiment | `--next_experiment_strategy` | `random` (default) | see strategy suffix table |

| Run-name suffix | `--next_experiment_strategy` |
| --- | --- |
| (none) | `random` |
| `-nextleast` | `least_similar_topk` |
| `-nextleastshift` | `least_prior_shift_topk` |
| `-nextthresholdshift` | `threshold_prior_shift_topk` |
| `-nextthresholdshiftleast` | `threshold_prior_shift_topk#least_similar_topk` |

**Four main search methods** (DiscoveryBench NLS SES example; paper labels in parentheses):

```sh
# Static (offline)
autodiscovery \
    --work_dir=work --out_dir=outputs \
    --dataset_metadata=discoverybench/real/test/nls_ses/metadata_0.json \
    --n_experiments=500 --model=gpt-4o --belief_model=gpt-5-mini \
    --belief_reasoning_effort=low --compute_icl_beliefs --topk_for_icl_beliefs=25

# Non-stationary (icl-topk): add --use_icl_beliefs
# Static + online dedupe (offline-dedupe): add --use_online_dedupe
# Non-stationary + online dedupe (icl-topk-dedupe): add both flags
```

**Evidence-informed search** (belief-update filtering + diversity maximization; ablation figures):

```sh
autodiscovery \
    --work_dir=work --out_dir=outputs \
    --dataset_metadata=discoverybench/real/test/nls_ses/metadata_0.json \
    --n_experiments=500 --model=gpt-4o --belief_model=gpt-5-mini \
    --belief_reasoning_effort=low --compute_icl_beliefs --topk_for_icl_beliefs=25 \
    --next_experiment_strategy=threshold_prior_shift_topk#least_similar_topk
    # add --use_icl_beliefs for the non-stationary variant (icl-topk-nextthresholdshiftleast)
    # add --use_online_dedupe for the online-dedupe variants
```

Search runs in the paper warm-started from a prior 200-node eval trajectory:

```sh
autodiscovery ... --continue_from_dir=<path/to/net-eval_gpt4o_offline-dedupe_<seed>_<dataset>-sparse/<timestamp>/>
```

### Post-hoc ICL evaluation (`python -m src.eval_icl_baselines`)

Used for the **spurious surprisal** figures: evaluate many ICL context variants on the same fixed hypothesis list from
an `offline-dedupe` eval run (`mcts_nodes_all.json` under
`net-eval_gpt4o_offline-dedupe_<seed>_<dataset>-sparse/<timestamp>/`).

Base eval trajectory (200 nodes, static prior, online dedupe during search):

```sh
autodiscovery \
    --work_dir=work --out_dir=outputs \
    --dataset_metadata=discoverybench/real/test/nls_ses/metadata_0.json \
    --n_experiments=200 --model=gpt-4o --belief_model=gpt-5-mini \
    --belief_reasoning_effort=low --use_online_dedupe --compute_icl_beliefs
```

Then run ICL baselines on the saved nodes (writes `icl*.json` into the run directory):

```sh
RUN=<path/to/net-eval_.../timestamp>

# All prior hypotheses as context -> icl.json
python -m src.eval_icl_baselines \
    --nodes-path=$RUN/mcts_nodes_all.json \
    --output=$RUN/icl.json \
    --model=gpt-5-mini --reasoning-effort=low --n-shuffles=0

# Top-k context (matches search --topk_for_icl_beliefs=25) -> icl-top25.json
python scripts/get_hyp_embeds.py \
    --input=$RUN/mcts_nodes_all.json \
    --output=embeds/nls-ses_0.npy

python -m src.eval_icl_baselines \
    --nodes-path=$RUN/mcts_nodes_all.json \
    --output=$RUN/icl-top25.json \
    --path-to-embeds=embeds/nls-ses_0.npy \
    --top-k=25 --model=gpt-5-mini --reasoning-effort=low
```

Other context ablations in the paper (each produces a separate JSON in the run directory):

| Output file | Extra flags |
| --- | --- |
| `icl-top1.json`, `icl-top5.json`, `icl-top10.json`, `icl-top50.json` | `--top-k={1,5,10,50}` |
| `icl-top10-mem0.json` | `--top-k=10 --mem0` |
| `icl-top10-explicit-causes.json` | `--top-k=10 --explicit-causes --explicit-causes-method=add` |

### Appendix: reasoning effort and top-k (fertility ablations)

The appendix top-k / reasoning-effort figures use `eval_icl_baselines` on a **deduped fertility hypothesis list**
(`notebooks/data/merged_mcts_fertility_deduped.json`), not live MCTS search:

```sh
# Reasoning-effort sweep -> merged_mcts_fertility_deduped_icl-{minimal,low,medium,high}.json
python -m src.eval_icl_baselines \
    --nodes-path=notebooks/data/merged_mcts_fertility_deduped.json \
    --output=notebooks/data/merged_mcts_fertility_deduped_icl-low.json \
    --reasoning-effort=low --n-shuffles=<N>

# Top-k at fixed low effort -> merged_mcts_fertility_deduped_icl-low-top{k}.json
# (omit --top-k for "all context" -> merged_mcts_fertility_deduped_icl-low.json)
python -m src.eval_icl_baselines \
    --nodes-path=notebooks/data/merged_mcts_fertility_deduped.json \
    --output=notebooks/data/merged_mcts_fertility_deduped_icl-low-top25.json \
    --path-to-embeds=<embeds.npy> --top-k=25 --reasoning-effort=low
```

Build the deduped node list with `python src/deduplication.py` on merged MCTS outputs (see `notebooks/data/merged_mcts_fertility_experiment.md` for the workflow).

## Reproducing paper figures

Plot-ready aggregated tables live in [`paper_results/`](paper_results/) (see [`paper_results/README.md`](paper_results/README.md)).
Regenerate every figure with:

```sh
python scripts/make_all_figs.py
```

See [`scripts/README.md`](scripts/README.md) for the figure-to-script mapping. No raw run data or cloud mounts are required.

## ✍️ Get in touch!

Please reach out to us on email or open a GitHub issue in case of any issues running the code: dagarwal@cs.umass.edu **(Dhruv Agarwal)**, bodhisattwam@allenai.org **(Bodhisattwa Prasad Majumder)**.

## 📄 Citation
If you find our work useful, please cite our paper:
```
@article{agarwal2026evidence,
  title={Evidence-Informed LLM Beliefs for Continual Scientific Discovery},
  author={Agarwal, Dhruv and Adamson, Reece and McCallum, Andrew and Clark, Peter and Sabharwal, Ashish and Majumder, Bodhisattwa Prasad},
  journal={arXiv preprint arXiv:2606.29182},
  year={2026}
}
```
