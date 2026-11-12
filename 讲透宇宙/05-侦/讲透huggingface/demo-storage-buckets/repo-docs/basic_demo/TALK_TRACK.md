# Talk Track (20 min total)

## Section 1: Xet — The Storage Backend (10 min)

### Slide: "How It Works / Why It Matters for NVIDIA"

**Opening** (1 min):
> "Before I show Storage Buckets, let me explain the engine underneath.
> Every repo on the Hub — models, datasets, Spaces — is backed by Xet.
> It was built from the ground up for AI/ML files: large, binary,
> frequently updated."

**CDC explanation** (2 min):
> "Xet splits every file into ~64KB variable-size chunks using a rolling
> hash. The key insight: chunk boundaries are determined by content, not
> position. So if you insert bytes at the beginning of a file, only the
> affected chunks change — the rest are recognized as identical."

> "This gives us byte-level deduplication that works across files, across
> repos, and across versions."

> "Xet stores these chunks as immutable data blocks, which allows for easy
> caching, since no expiration or invalidation to worry about."

**Why it matters for NVIDIA** (2 min):
> "For Cosmos checkpoints: if 90% of weights are frozen between training
> steps, only 10% of the data actually transfers. For a 10 GB model,
> that's 1 GB instead of 10 GB per checkpoint save."

> "For robotics video data: successive frames from robot sensors have
> massive overlap. CDC captures this at the byte level."

> "And cross-repo: all your Cosmos model variants — Predict, Transfer,
> Reason — share most of their base weights. Xet stores those shared
> chunks once."

**Live Demo 2: Dedup** (5 min):
> "Let me show you this live."

Run `python3 demo_01_xet_dedup.py` — show checkpoint uploads where subsequent
saves transfer ~10% of the data.

---

## Section 2: Storage Buckets (10 min)

### Slide: "Storage Buckets — S3-like mutable storage"

**Buckets vs Repos** (2 min):
> "Git repos are great for publishing finished artifacts — you get
> version history, PRs, collaboration. But for working storage —
> checkpoints, logs, intermediate data — you don't want Git overhead."

> "Storage Buckets give you S3-like mutable storage, powered by the
> same Xet backend. Create, sync, cp, rm — it works like you'd expect."

**Live Demo 2: Basics** (3 min):
Run `./demo_02_bucket_basics.sh` — create bucket, upload, sync, browse.

> "Notice the CLI feels exactly like `aws s3`. Your infra team already
> knows this workflow."

**CDN Pre-warming** (2 min — continues in same demo, press Enter):
> "Now that we have data in a bucket, how do we get it close to
> your compute? CDN pre-warming."

> "You select the regions where your clusters live — say us-east-1
> for DGX Cloud — and HF pre-warms the CDN with your bucket data.
> First read is already fast, no cold start penalty."

> "This is critical for physical AI: episode datasets are read
> many times across training runs, and video/sensor data is large.
> Cross-region reads are slow and expensive."

(Show the Hub UI bucket settings page if time permits)

### Slide: "hf-mount: Filesystem Access"

**hf-mount** (2 min):
> "Now here's the part that changes everything for researchers.
> hf-mount exposes any bucket as a local filesystem. Your training
> script just reads and writes files — no SDK, no download step."

> "For Buckets, it's read-write. Save checkpoints directly to a
> mounted path. Other jobs — eval, visualization — can mount the
> same bucket simultaneously."

> "And for Kubernetes: the hf-csi-driver wraps hf-mount behind the
> CSI interface. kubelet manages mount lifecycle automatically.
> This is designed for DGX Cloud."

**Live Demo 5: Mount** (3 min):
Run `./demo_03_hf_mount.sh` — mount bucket, read/write via filesystem,
show the Jobs integration talk track.

> "Your researchers don't need to learn a storage API. They write
> `torch.save(model, '/checkpoints/step_1000.pt')` and it's in the
> bucket."

---

## Transition to Leandro:
> "That's the storage layer. Now Leandro is going to show you how
> this powers real research at HF scale — 15 trillion tokens of
> FineWeb, SmolLM, and what this looks like for robotics data."
