# Production Release Artifacts

Scripts in this directory create or validate checked-in production artifacts
under `s2and/data/`. The model release artifact is a native
`production_model_vX.Y/` directory. Do not create production pickles.

Examples below use `X.Y` as the target production bundle version.

## 1. Train Pairwise

```powershell
uv run python scripts/production/model/train_pairwise.py `
  --production-version X.Y `
  --output-dir s2and/data/production_model_vX.Y `
  --run-full
```

This writes the pairwise-only bundle stage:

```text
production_model_vX.Y/
  clusterer.json
  manifest.json
  pairwise/
    main.lgb
    nameless.lgb
    metadata.json
    main_prediction_fixture.json
    nameless_prediction_fixture.json
  reproducibility/
    pairwise_training_config.json
    pairwise_training_summary.json
```

This stage is loadable for training/finalization, but it is not a complete
runtime production model until the linker is added.

## 2. Train Linker And Finalize

```powershell
uv run python scripts/production/model/train_linker_and_finalize.py `
  --production-bundle-version X.Y `
  --target-json s2and/data/production_model_vX.Y/reproducibility/incremental_linker_training_target.json `
  --pairwise-model-path s2and/data/production_model_vX.Y `
  --save-production-bundle-to s2and/data/production_model_vX.Y `
  --linker-artifact-version vX.Y `
  --output-dir scratch/production_linker_vX.Y `
  --run-full
```

This writes:

```text
production_model_vX.Y/
  incremental_linker/
    booster.lgb
    metadata.json
  reproducibility/
    incremental_linker_training_target.json
  manifest.json
```

After this step, users load the model with:

```python
from s2and.production_model import load_production_model

clusterer = load_production_model("s2and/data/production_model_vX.Y")
```

## Arrow Release Validation

For local release-root smoke checks that do not touch S3 or scan large Arrow
tables, run:

```powershell
uv run python scripts/verification/validate_local_arrow_release.py `
  --release-root s2and/data
```

This verifies manifest checksums, required local files, raw-planner batch-index
paths, replay-bundle manifest references, and `name_counts_index/manifest.json`
targets. Use `scripts/convert_to_arrow.py validate --dataset-dir ...` for
deeper per-dataset Arrow schema/table validation.

## Count Artifacts

The `counts/` scripts document production count artifacts:

- `counts/generate_name_counts.py`: documents the internal query used to build
  `name_counts.pickle`.
- `counts/generate_orcid_name_prefix_counts.py`: documents the internal query
  used to build `first_k_letter_counts_from_orcid.json`.
