# Megatron-LM-Carbon

Training code for the Carbon DNA language model: a thin Python package
layered on top of upstream
[NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM), consumed as
a pinned git submodule so reproducibility doesn't depend on a long-lived
fork.

## Two-phase training

Carbon is trained in two phases:

| Phase | Loss | Entry point | Schedule | Tokens |
|---|---|---|---|---|
| **Phase 1 — pretrain** | Cross-entropy | upstream `pretrain_gpt.py` (no carbon-side modifications) | WSD, peak LR 3e-4 | 100B |
| **Phase 2 — refine** | CE + Factorized Nucleotide Supervision | `src/carbon/pretrain_gpt_hybrid.py` | WSD (3B) / cosine (8B), peak LR 5e-5 | continues from phase-1 checkpoint |

Phase 2 adds the FNS / "BP marginal" loss on top of CE — it marginalises
6-mer-token logits to per-base probabilities and supervises at the
nucleotide level. Lower LR avoids drifting away from the phase-1 weights.

## Layout

```
.
├── pyproject.toml                  carbon-training package metadata
├── src/carbon/
│   ├── __init__.py                 puts the bundled Megatron-LM on sys.path;
│   │                               auto-applies the trackio shim when
│   │                               CARBON_USE_TRACKIO=1
│   ├── pretrain_gpt_hybrid.py      phase-2 hybrid CE + FNS loss entry point
│   ├── generate_token_mask.py      mask .bin/.idx generator (phase 2 only)
│   └── _compat/trackio.py          runtime trackio writer shim
├── scripts/
│   ├── run_3B_pure_dna_1T_generv2_layout_wsd.sh   3B phase 1, 8 nodes
│   ├── run_3B_hyb_from_100B_wsd_lr5e5_16n.sh      3B phase 2, 16 nodes
│   ├── run_8B_pure_dna_1T_wsd_no_mask.sh          8B phase 1, 16 nodes
│   └── run_8B_hyb_from_100B_cosine_lr5e5_32n.sh   8B phase 2, 32 nodes
├── third_party/
│   └── Megatron-LM/                git submodule, NVIDIA/Megatron-LM @ 0dba6a001
└── slurm_logs/                     pre-tracked, default sbatch -o/-e target
```

## Install

```bash
git clone --recurse-submodules https://github.com/huggingface/Megatron-LM-Carbon.git
cd Megatron-LM-Carbon
uv pip install -e .[trackio]
```

If you forgot `--recurse-submodules`:
```bash
git submodule update --init
```

To point at your own Megatron-LM checkout (e.g. for development on the
Megatron side), set:
```bash
export CARBON_MEGATRON_PATH=/path/to/your/Megatron-LM
```

## Running training

Each launcher auto-resolves `REPO_ROOT`, `MEGATRON_PATH`, `TRAINING_SCRIPT`,
and `CARBON_VENV` relative to its own location, so submitting from the
repo root just works:

```bash
sbatch scripts/run_3B_pure_dna_1T_generv2_layout_wsd.sh    # phase 1 (CE)
# wait for phase 1 to reach iter 48000 (100B tokens), then:
sbatch scripts/run_3B_hyb_from_100B_wsd_lr5e5_16n.sh       # phase 2 (hybrid)
```

8B is the same flow, just with the `run_8B_*` scripts and a phase-1 fork
point of iter 24000 (100B tokens at GBS=512).

> **Phase 1 schedule note.** The phase-1 scripts set `TRAIN_ITERS=477k` (3B)
> or `239k` (8B) — the *full* WSD horizon for a 1T-token run — but the
> phase-2 launchers hand-pick a fork checkpoint at the 100B-token mark, so
> phase 1 is interrupted there in practice. Override `TRAIN_ITERS` if you'd
> rather train phase 1 to a different horizon.

### Cluster overrides

The launch scripts default to the paths used on the HF cluster. Override
any of these via env at sbatch time:

| Variable | Phase | Default |
|---|---|---|
| `CARBON_VENV` | both | `/fsx/loubna/.megatron-cu124` |
| `MEG_DATA` | both | `/fsx/loubna/.../tokenized_data_megatron_qwen3h` |
| `TOKEN_DATA_BASE`, `MASK_DATA_BASE` | phase 2 | same root as `MEG_DATA` |
| `SAVE_PATH` | both | `/fsx/loubna/.../checkpoints/${RUN_NAME}` |
| `LOAD_PATH`, `SRC_CKPT_DIR` | phase 2 | derived from the phase-1 default |
| `MEGATRON_PATH` | both | `${REPO_ROOT}/third_party/Megatron-LM` |
| `TRAINING_SCRIPT` | both | phase 1: `${MEGATRON_PATH}/pretrain_gpt.py` · phase 2: `${REPO_ROOT}/src/carbon/pretrain_gpt_hybrid.py` |

Example with overrides:
```bash
CARBON_VENV=/path/to/my/venv \
MEG_DATA=/path/to/my/tokenized_data \
SAVE_PATH=/scratch/me/carbon-3B-phase1 \
sbatch scripts/run_3B_pure_dna_1T_generv2_layout_wsd.sh
```

## Phase 2 — hybrid loss configuration

`pretrain_gpt_hybrid.py` reads a few knobs from the environment (the
launch scripts already export them):

```bash
export HYBRID_BP_TOKENIZER="hf-carbon/qwen3-hybrid-dna-tokenizer-128"
export HYBRID_BP_WEIGHT=1.0     # weight on the BP-marginal (FNS) loss
export HYBRID_NL_WEIGHT=0.15    # weight on the natural-language CE loss
export HYBRID_BP_LOSS_MODE=unconditional   # full-vocab softmax (paper definition)
export TOKEN_DATA_BASE=/path/to/tokenized_data_megatron_qwen3h
export MASK_DATA_BASE=/path/to/tokenized_data_megatron_qwen3h
```

### Tokenized data

Carbon uses non-overlapping 6-mer DNA tokens via the
`hf-carbon/qwen3-hybrid-dna-tokenizer-128` tokenizer. Phase 1 needs only
the `.bin/.idx` token shards; phase 2 also needs parallel `_mask.bin/.idx`
files marking k-mer-token positions.

Mask files are generated by `python src/carbon/generate_token_mask.py`
from existing tokenized shards. See the
[GenBank pipeline](https://github.com/huggingface/genbank-pipeline) for
an end-to-end example of producing both.

## Logging

### wandb (default)

The launch scripts already set `--wandb-project hf-carbon`,
`--wandb-entity huggingface`, and `--wandb-exp-name ${RUN_NAME}`. Provide
a `WANDB_API_KEY` (or `wandb login` once on the submission host) and the
runs land at `wandb.ai/huggingface/hf-carbon`.

### trackio (optional)

Upstream Megatron's wandb writer doesn't `.item()` torch tensors before
calling `.log(...)`, which silently drops trackio runs on
`Type is not JSON serializable: Tensor`. This repo's
`carbon._compat.trackio` ships a runtime shim that wraps the writer to
fix that, plus initialises trackio with the standard Megatron wandb
knobs.

To enable, set `CARBON_USE_TRACKIO=1` before sbatch — `import carbon` at
the top of the entry script will then auto-apply the shim:

```bash
export CARBON_USE_TRACKIO=1
export CARBON_TRACKIO_SPACE_ID="hf-carbon/carbon-trackio"   # default
sbatch scripts/run_3B_hyb_from_100B_wsd_lr5e5_16n.sh
```

## Released checkpoints

Carbon-3B and Carbon-8B were trained with this codebase against
`NVIDIA/Megatron-LM @ 0dba6a001` (the upstream commit pinned by this
repo's submodule). 

Released models are available in the
**[Carbon Checkpoints collection](https://huggingface.co/collections/HuggingFaceBio/carbon)**
on Hugging Face.
## License

Apache 2.0 — same as upstream Megatron-LM.
