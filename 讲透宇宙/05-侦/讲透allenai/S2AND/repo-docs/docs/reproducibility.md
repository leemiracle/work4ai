# Reproducibility

This document covers the paper-era environment and compatibility notes for older released artifacts.

## Paper-era branch

The original paper experiments were run on the `s2and_paper` branch with a Python `3.7.9` environment captured in `paper_experiments_env.txt`.

If you need to reproduce the paper-era setup:

```bash
git checkout s2and_paper
uv venv --python 3.7.9
```

Then install the pinned environment from `paper_experiments_env.txt` inside that isolated environment and rerun the paper experiment command set from the `s2and_paper` branch. The current branch keeps a reference copy at `scripts/archive/paper_experiments.sh`, but that file is historical and not the supported entrypoint for current `main` development.

## Paper-era released artifacts

Paper-era seed artifacts such as:

- `full_union_seed_*.pickle`

are legacy artifacts for reproducing the original paper setup and should be used
from the `s2and_paper` branch, not current `main`.

Some historical model pickles used by the paper-era branch stored a dictionary
with a `clusterer` key rather than a bare clusterer object. Current `main`
compatibility artifacts use versioned names such as `production_model_v1.2.pickle`
and are covered below.

## Current branch

For current work on `main`, prefer the checked-in native production bundle:

- `production_model_v1.21/`

Legacy pickles are still present for compatibility and parity checks:

- `production_model_v1.2.pickle`
- `production_model_v1.1.pickle`

The v1.21 bundle includes the promoted incremental linker under
`incremental_linker/`. Its replay target is tracked separately at
`production_model_v1.21/reproducibility/incremental_linker_training_target.json`;
replay scripts should not depend on machine-local analysis artifacts.

For repeated promoted-linker replay, materialized feature bundles can be reused
only through the explicit `precomputed-promoted` mode. The bundle must be
portable and validated against the replay target JSON. Feature-table metadata in
the reusable input bundle must use bundle-relative paths; finalized production
artifact audit metadata may still record historical scratch/provenance paths,
but replay must not depend on them.

See [production_inference.md](production_inference.md) for the current inference contract.
