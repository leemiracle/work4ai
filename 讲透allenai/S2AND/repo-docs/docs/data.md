# Data and Models

This document covers dataset download, checked-in model artifacts, and `path_config.json`.

## Dataset download

Download the Arrow-native production runtime release into `s2and/data/` for
Rust/Arrow prediction and evaluation:

```bash
aws s3 sync --no-sign-request s3://ai2-s2-research-public/s2and-release-arrow s2and/data/
```

Expected size is about `10.1 GiB`. The release root contains the benchmark
dataset directories, shared `name_counts_index/`, `production_model_v1.21/`,
and the promoted-linker replay bundle.

Download the legacy JSON/pickle S2AND release only when you need paper-era
`ANDData` inputs:

```bash
aws s3 sync --no-sign-request s3://ai2-s2-research-public/s2and-release s2and/data/
```

Expected legacy release size is about `55.5 GiB`.

The promoted-linker replay subbundle can also be downloaded by itself:

```bash
aws s3 sync --no-sign-request s3://ai2-s2-research-public/s2and-release-arrow/s2and_and_big_blocks_linker_dataset_20260525 s2and/data/s2and_and_big_blocks_linker_dataset_20260525
```

`s2and/data/s2and_and_big_blocks_linker_dataset_20260525` is the canonical
local name for the published Arrow replay subbundle.

The Arrow release stores runtime signatures, papers, paper authors, and SPECTER
rows as Arrow IPC files. It intentionally does not duplicate legacy `raw/`,
`embeddings/`, or precomputed `features_corrected/` directories.

The current production model bundle is checked into this repo under
`s2and/data/production_model_v1.21/`.

## Production model bundle

The current production model is a native bundle directory:

- `s2and/data/production_model_v1.21/manifest.json`
- `s2and/data/production_model_v1.21/clusterer.json`
- `s2and/data/production_model_v1.21/pairwise/main.lgb`
- `s2and/data/production_model_v1.21/pairwise/nameless.lgb`
- `s2and/data/production_model_v1.21/pairwise/metadata.json`
- `s2and/data/production_model_v1.21/pairwise/main_prediction_fixture.json`
- `s2and/data/production_model_v1.21/pairwise/nameless_prediction_fixture.json`
- `s2and/data/production_model_v1.21/incremental_linker/booster.lgb`
- `s2and/data/production_model_v1.21/incremental_linker/metadata.json`
- `s2and/data/production_model_v1.21/reproducibility/incremental_linker_training_target.json`

See [production_inference.md](production_inference.md) for what each file is
for.

This bundle is included in package data, so prediction does not require a
separate model download. The older `production_model_v1.2.pickle` is retained
for legacy pairwise compatibility, but the documented production loader points
at the v1.21 bundle.

New production releases should be built as native bundle directories with
`scripts/production/model/train_pairwise.py` followed by
`scripts/production/model/train_linker_and_finalize.py`; do not create new
production pickles.

The replay target for rebuilding/auditing the promoted incremental linker lives
at:

```text
s2and/data/production_model_v1.21/reproducibility/incremental_linker_training_target.json
```

Prediction logic does not consume it, but bundle load validation includes its
manifest checksum. It records feature order and training params for the replay
script.

The promoted linker train/calibrate/eval replay data is published under the
Arrow release prefix. Download it when you need to rebuild or audit the
promoted linker artifact:

```bash
aws s3 sync --no-sign-request s3://ai2-s2-research-public/s2and-release-arrow/s2and_and_big_blocks_linker_dataset_20260525 s2and/data/s2and_and_big_blocks_linker_dataset_20260525
```

This source bundle is the default `--source-bundle-root` for
`scripts/production/model/linker_train_calibrate_eval.py`.

## Configuring `s2and/data/path_config.json`

Some scripts look up the main data root through `s2and/data/path_config.json`
or the `S2AND_PATH_CONFIG` environment variable. This config points at the
downloaded benchmark dataset root; it is separate from the package data checked
in under `s2and/data/`.

Example:

```json
{
  "main_data_dir": "absolute path to your downloaded S2AND data",
  "internal_data_dir": ""
}
```

Guidance:

- Set `main_data_dir` to the directory containing your downloaded S2AND datasets.
- `internal_data_dir` is only relevant for internal AI2 workflows and can be left empty.
- If your data lives in this repo's `s2and/data/` directory, the default placeholder config already resolves there.

## Dataset file expectations

Arrow production/eval workflows use each dataset's `manifest.json` to resolve:

- `signatures.arrow`
- `papers.arrow`
- `paper_authors.arrow`
- `specter.arrow` or `specter2.arrow`
- raw-planner `*_batch_index.bin` sidecars
- shared `name_counts_index/`
- eval-only clusters JSON when metrics are requested

Legacy workflows use the standard S2AND JSON files for:

- signatures
- papers
- clusters
- optional cluster seeds
- SPECTER embeddings

The tutorial script supports Arrow by default when a dataset manifest exists,
and JSON only when `--input-format json` is requested or Arrow artifacts are
absent. JSON mode supports:

- mini-dataset naming such as `<dataset>_papers.json`
- plain fixture naming such as `papers.json`

See [production_inference.md](production_inference.md) for the minimal inference input contract, and [training.md](training.md) for training-mode dataset requirements.
