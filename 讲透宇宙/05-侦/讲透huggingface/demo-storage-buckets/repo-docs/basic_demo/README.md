# Storage Buckets Demo — NVIDIA Physical AI Meeting

Live demo scripts for the NVIDIA meeting (Apr 7, 2026).
See `TALK_TRACK.md` for the full talk track with transitions.

## Prerequisites

```bash
curl -LsSf https://hf.co/cli/install.sh | bash # hf CLI
curl -fsSL https://raw.githubusercontent.com/huggingface/hf-mount/main/install.sh | sh # hf-mount
hf auth login  # or export HF_TOKEN=hf_...
```

## Demo Flow (20 min)

| Order | Script | Slide | Duration |
|-------|--------|-------|----------|
| 1 | `demo_01_xet_dedup.py` | Xet: The Storage Backend | ~5 min |
| 2 | `demo_02_bucket_basics.sh` | Storage Buckets + CDN Pre-warming | ~5 min |
| 3 | `demo_03_hf_mount.sh` | hf-mount: Filesystem Access + Jobs | ~5 min |

Backup demo (for Q&A):

| # | Script | Topic |
|---|--------|-------|
| 4 | `demo_04_dataset_sync.sh` | Incremental sync for growing datasets |

### Pre-demo setup (run before the meeting)

```bash
# 1. Configure scripts with your HF username
./prep.sh <your-hf-username>

# 2. Clean up any buckets from a previous run
./cleanup.sh

# 3. Verify
grep BUCKET demo_01_xet_dedup.py  # should show your username
```

## Cleanup

```bash
./cleanup.sh
```
