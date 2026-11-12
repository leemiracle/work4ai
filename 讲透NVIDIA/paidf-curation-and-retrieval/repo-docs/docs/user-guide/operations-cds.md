<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Cosmos Dataset Search

1. [About Curation and Retrieval](README.md)
2. [Installation](installation.md)
3. [Samples and Cookbooks](samples-and-cookbooks.md)
4. [Get Started](getting-started.md)
5. [Cosmos Curator](operations-curator.md)
6. [Data Mining](operations-tao-mining.md)
7. [Cosmos Dataset Search](operations-cds.md)
8. [VLM and LLM Endpoints](vlm-llm-endpoints.md)
9. [Troubleshooting](troubleshooting.md)

This page is the operator recipe for **Path D**: take Cosmos-Embed1 (CE1)
clips from Cosmos Curator, start Cosmos Dataset Search (CDS) on this host,
ingest those clips, and search with a text query. The supported path is
public generally available (GA) 1.2.0.

You do not need prior CDS, Docker Compose, or Milvus experience. Run the
commands from the repository root. The public interface is Make. Do not invent
extra CLI flags.

The repository README lists Path A through Path D. This page is the Path D
recipe. Use Choose a Path, then copy each block as written unless a comment
tells you to substitute a value.

## Choose a Path

| Goal | Section |
|------|---------|
| Public generally available (GA) 1.2.0 on this host | [Public GA Recipe](#public-ga-recipe) |
| CDS already deployed | [Using a CDS You Deployed Yourself](#using-a-cds-you-deployed-yourself) |

## What CDS Includes

CDS is a search API. It stores clip embeddings and returns the closest
clips for a text query.

This repository:

- **Does** pull a published CDS container image (GA).
- **Does** start a small local stack with Docker Compose: etcd, LocalStack,
  Milvus, and the CDS API on port **8888**.
- **Does** work against a CDS API you deployed yourself, anywhere. Set
  `CDS_URL` and every step below behaves the same.
- **Does not** build the CDS image or deploy CDS on Kubernetes. Cluster
  bring-up belongs to the CDS repository.
- **Does not** run on ARM. The CDS API and Cosmos-Embed1 images are
  published for `linux/amd64` only, so an ARM64/aarch64 host cannot start
  the stack even with a supported NVIDIA GPU. Use an x86_64 host.
- **Does not** support Blackwell (B-series) GPUs. The Cosmos-Embed1
  1.2.0 image has no kernels for compute capability 10.0
  (`sm_100`: B100, B200, GB200) or 12.0 (`sm_120`: RTX PRO 6000 Blackwell);
  the CDS API itself does not use the GPU. Use a Hopper (H100, H20), Ada
  (L40S, L4, L20), or Ampere (A100, A40) class GPU with 16GB+ VRAM.
- **Does** start Cosmos-Embed1 for text search on host port **9000**.
  Ingest of **already computed** CE1 vectors does not need it. Refer to
  [Verify Cosmos-Embed1](#verify-cosmos-embed1).
- **Does not** accept InternVideo2 (IV2) embeddings. Warehouse
  `split-minimal.yaml` uses IV2 for Path C / TMM, not Path D.

## Ingest Modes

| Mode | When | What you pass |
|------|------|----------------|
| **Lab document ingest** | Local compose; parquet on disk | Collection **id** and `ALLOW_LAB_DOCUMENT_FALLBACK=1` |
| **GA bulk ingest** | CDS can read `s3://` parquet | Collection **id** and `PARQUET_URI=s3://...` |

Local compose accepts `POST /v1/insert-data` but cannot read a parquet
file on the host filesystem. Such a request returns HTTP 400
(`Parquet imports require plain s3://bucket/key paths`), after which the
adapter falls back to document ingest. No operator action is required.

Use lab document ingest as the Path D smoke test on compose. It does
**not** validate GA bulk ingest, which requires parquet in object
storage.

## Using a CDS You Deployed Yourself

Compose is the laptop Path D stack. On a cluster or a shared host, CDS is a **prerequisite endpoint**: deploy it from
its own repository, then point this repo at it. This repository does not
deploy CDS on Kubernetes and does not wrap CDS `k8s_up.sh` (AWS EKS).

```bash
git clone https://github.com/NVIDIA-Omniverse-blueprints/cosmos-dataset-search.git
cd cosmos-dataset-search
# Deploy by whichever route that repository documents for your target.
# CDS documents AWS EKS; refer to its README for current options.

# Kubernetes: CDS sets FASTAPI_ROOT_PATH=/api and its ingress routes /api/,
# so the base URL carries that prefix. Compose has no prefix
# (http://localhost:8888).
export CDS_URL=https://cds.example.com/api
make ds-health
```

`CDS_URL` is the API root without `/v1`; the client appends it. `/health` is
served at the service root rather than under `/v1`, so with the prefix above
the precheck resolves to `https://cds.example.com/api/health`.

If CDS's own bring-up generated its self-signed TLS certificate, point
`REQUESTS_CA_BUNDLE` at that certificate before running `ds-health`, or the
call fails certificate verification rather than reporting on CDS.

`make ds-health` is the precheck: run it before any collection, ingest,
or search target. Every one of those targets accepts `--cds-url`
and honors `CDS_URL`, so nothing else changes. If health fails, fix the
endpoint before continuing; the later steps will only fail less clearly.

After health, continue from collection create using the collection **id**.

## Before You Start

Complete **Path A** with Cosmos-Embed1. Traffic first-run:

```bash
make run-pipeline \
  CONFIG_FILE=cookbook/traffic-video-analytics/split-minimal.yaml \
  DATA_DIR=$PWD/cookbook/traffic-video-analytics \
  MODELS_DIR=/path/to/models \
  FFMPEG_DIR=$HOME/cosmos-curator-ffmpeg
```

Replace `/path/to/models` with the host directory that contains
`nvidia/Cosmos-Embed1-224p`.

**Success for Path A:** this directory exists and contains `.parquet`
files:

`cookbook/traffic-video-analytics/output/split-minimal/ce1_embd_224p_parquet/`

Also required:

- Docker 20.10+ and permission to run `docker` without sudo (or use sudo
  consistently).
- `docker login nvcr.io` already succeeded (same as Curator pull).
- `uv sync --extra dev` already succeeded.
- Port **8888** free on the host (CDS API). Ports **19530** and **9091**
  free (Milvus).

### Do Not Reuse an InternVideo2 Output Directory

If `output/split-minimal/` already has `iv2_embd_parquet/` from an older
run, Curator might skip videos and never write CE1 for them. For a clean
CE1 run, delete that output directory or change `output_clip_path` in the
YAML (for example `/data/output/split-minimal-ce1`). Confirm
`summary.json` contains `"embedding_algorithm": "cosmos-embed1-224p"`.

### Environment File Precedence

The Makefile loads `.env`, then **`local.env`**. `local.env` wins.

The default profile, `CDS_PROFILE=public`, always uses the public `1.2.0`
image. It ignores any `DATASET_SEARCH_REGISTRY` or `DATASET_SEARCH_TAG` in
those files.

Image pins in those files take effect only when one of them sets
`CDS_PROFILE` to a value other than `public`. Bare `make pull-dataset-search`
and `make up-dataset-search` then use those pins, not public `1.2.0`.
A shell prefix does **not** override a value set in an environment file:

```bash
# Does NOT beat CDS_PROFILE set in local.env
CDS_PROFILE=public make pull-dataset-search
```

Pass `CDS_PROFILE=public` as a Make argument on the `make` command itself
(refer to [Public GA Recipe](#public-ga-recipe)).

## Public GA Recipe

### Pull the Public CDS Image

From the repository root:

```bash
docker login nvcr.io
make pull-dataset-search \
  CDS_PROFILE=public \
  DATASET_SEARCH_REGISTRY=nvcr.io/nvidia/blueprint/cosmos-dataset-search \
  DATASET_SEARCH_TAG=1.2.0
```

**Success:** the command prints `Pull complete: cosmos-dataset-search:1.2.0`.

If it prints `DATASET_SEARCH_REGISTRY and DATASET_SEARCH_TAG are not
set`, or a tag other than `1.2.0`, `.env` or `local.env` sets `CDS_PROFILE`
to another profile. Re-run with the Make arguments above.

### Stop Leftover Compose Containers

An old Milvus container with a newly created etcd will exit with code 1
(`disconnected from etcd`). Tear the stack down first:

```bash
make down-dataset-search
docker compose -f deploy/compose/docker-compose.yml down --remove-orphans
```

If `compose-milvus-1` is still listed in `docker ps -a`, remove it:

```bash
docker rm -f compose-milvus-1
```

### Start CDS

```bash
make up-dataset-search \
  CDS_PROFILE=public \
  DATASET_SEARCH_REGISTRY=nvcr.io/nvidia/blueprint/cosmos-dataset-search \
  DATASET_SEARCH_TAG=1.2.0 \
  COSMOS_EMBED_MODELS_DIR=/path/to/Cosmos-Embed1-224p
```

The public profile adds `deploy/compose/docker-compose.embed.yml`, which
runs Cosmos-Embed1 as a service and sets `COSMOS_EMBED_URI` for the API.
Point `COSMOS_EMBED_MODELS_DIR` at a snapshot of the pinned revision. Refer to
[Cosmos-Embed1 Weights](installation.md#cosmos-embed1-weights).

If the overlay is omitted, the API reports healthy but the first
collection call returns HTTP 500 (`No pipelines have been initialised`).

**Success:** Compose shows etcd, LocalStack, Milvus, and `cosmos-embed`
**Healthy**, and `compose-dataset-search-1` **Started** or **Healthy**. The
image column must be `cosmos-dataset-search:1.2.0`.

```bash
docker ps --filter name=compose- --format '{{.Names}} {{.Image}} {{.Status}}'
```

Compose returns as soon as the CDS container **starts**. Gunicorn might
still be booting. Do not run `make ds-health` in the same paste as `up`.

### Wait Until the API Answers

Retry until health is OK (often 30–90 seconds):

```bash
until curl -sf http://localhost:8888/health; do
  echo "CDS still starting; retry in 10 seconds"
  sleep 10
done
make ds-health
```

**Success:** `make ds-health` prints `{"status": "OK"}`.

If the wait loop prints `Connection reset by peer`, wait and retry. That error means
the port is open but the process is not serving yet.

### Confirm the Video Pipeline Is Enabled

```bash
make ds-pipelines
curl -sS http://localhost:8888/v1/pipelines
```

`make ds-pipelines` lists pipeline **names** only. It does **not** show
whether a pipeline loaded. The `curl` JSON must contain
`"id": "cosmos_video_search_milvus"` and `"enabled": true`.

If `"enabled": false`, read the `"missing"` list. On the public `1.2.0`
image those fields are empty and the pipeline is enabled. If the image
is not `1.2.0`, switch to public `1.2.0` (pull, stop leftover containers,
and start CDS).

### Create a Collection and Copy the Id

CDS looks up collections by **id**, not by the human name `traffic`.
`GET /v1/collections/traffic` returns 404.

```bash
make ds-create-collection \
  NAME=traffic \
  PIPELINE=cosmos_video_search_milvus
```

**Success:** JSON includes both a name and an id, for example:

```json
{
  "id": "a4892af7c_eadb_4e21_a833_9273d21e0d86",
  "name": "traffic",
  "pipeline": "cosmos_video_search_milvus",
  "tags": {}
}
```

Copy the `id` string. In the rest of this page it is
`TRAFFIC_COLLECTION_ID`. Your id will differ. Do not paste the
placeholder `TRAFFIC_COLLECTION_ID` into Make; that 404s the same as
using the collection name.

Confirm:

```bash
make ds-get-collection COLLECTION=TRAFFIC_COLLECTION_ID
```

Substitute your id. This must return HTTP 200. Using `COLLECTION=traffic`
here fails.

### Convert CE1 and Ingest

`CURATOR_DIR` is the Curator **output root**, not the parquet folder.

| Wrong | Right |
|-------|--------|
| `.../output/split-minimal/ce1_embd_224p_parquet` | `.../output/split-minimal` |

The ingest step searches **under** `CURATOR_DIR` for `ce1_embd_*_parquet/`.

```bash
make ingest-curator \
  CURATOR_DIR=$PWD/cookbook/traffic-video-analytics/output/split-minimal \
  OUT=$PWD/cookbook/traffic-video-analytics/output/cds-traffic.parquet \
  EMBEDDING_BACKEND=ce1 \
  COLLECTION=TRAFFIC_COLLECTION_ID \
  ALLOW_LAB_DOCUMENT_FALLBACK=1
```

Substitute `TRAFFIC_COLLECTION_ID`. Keep
`ALLOW_LAB_DOCUMENT_FALLBACK=1` on local compose.

**Success:** two JSON objects. The second looks like:

```json
{
  "ingested": true,
  "collection": "TRAFFIC_COLLECTION_ID",
  "job_id": "documents:13",
  "embedding_family": "ce1"
}
```

`documents:13` means 13 clip vectors were posted. Your count depends on
how many CE1 clips Curator wrote.

If `CURATOR_DIR` points at the parquet directory itself, ingest exits
with `No ce1_embd_parquet/ or ce1_embd_*_parquet/`. Point at the parent.

If `COLLECTION=traffic` (the name), fallback posts to
`/v1/collections/traffic/documents` and CDS returns 404. Use the id.

Collection metadata might still show `"total_documents_count": 0`. Search is the check that vectors are queryable.

### Verify Cosmos-Embed1

Cosmos-Embed1 embeds the **text query**. `make up-dataset-search` starts
it when you start CDS, and the API reaches it at `COSMOS_EMBED_URI`. It listens on
host port **9000**.

```bash
curl -sf http://127.0.0.1:9000/v1/health/ready
```

**Success:** HTTP 200. Ingest can succeed while this check fails; search
cannot.

| Response | Cause | Action |
|----------|-------|--------|
| HTTP 503, `CE1 snapshot checksum mismatch` | `COSMOS_EMBED_MODELS_DIR` holds the wrong snapshot revision | Re-download the weights at the pinned revision ([Cosmos-Embed1 weights](installation.md#cosmos-embed1-weights)) |
| Connection refused | The embedder is not running | Confirm `cosmos-embed` is Healthy in `docker ps`, then start CDS again |

### Search

Use the **same collection id**:

```bash
make search \
  COLLECTION=TRAFFIC_COLLECTION_ID \
  QUERY='pedestrian crossing the road'
```

**Success:** JSON array of hits. Each hit has `id`, `score`, and `meta`
(source video, time span, clip path). Traffic first-run CE1 is often
`SDG-Intersection-02.mp4` if clip 01 was already processed with IV2 in
the same output directory.

### GA Bulk Insert

Use this only when CDS can read an `s3://` URI. Stage first. Pass
credential **environment variable names**, never secret values on the
command line:

```bash
make ingest-curator \
  CURATOR_DIR=$PWD/cookbook/traffic-video-analytics/output/split-minimal \
  OUT=$PWD/cookbook/traffic-video-analytics/output/cds-traffic.parquet \
  EMBEDDING_BACKEND=ce1

make stage-cds-artifact \
  STAGE_SOURCE=$PWD/cookbook/traffic-video-analytics/output/cds-traffic.parquet \
  STAGE_DESTINATION=s3://bucket/cds-traffic.parquet \
  OBJECT_STORE_ENDPOINT=https://objects.example

make ds-bulk-insert \
  COLLECTION=TRAFFIC_COLLECTION_ID \
  PARQUET_URI=s3://bucket/cds-traffic.parquet \
  CDS_EMBEDDING_FAMILY=ce1

make ds-job-status JOB_ID=<job-id-from-bulk-insert> WAIT=1
```

Do not treat lab document ingest (`documents:N`) as success of this path.

## Stop the Stack

```bash
make down-dataset-search
```

## If a Step Fails

| What you see | Cause | What to do |
|--------------|-------|------------|
| Pull says registry/tag not set | `.env` or `local.env` sets another `CDS_PROFILE` | Pass `CDS_PROFILE=public` and the public `1.2.0` Make arguments |
| Image is not `1.2.0` | `.env` or `local.env` sets another `CDS_PROFILE` | Down, then up with the public Make arguments |
| HTTP 500: `No pipelines have been initialised` | Cosmos-Embed1 overlay missing or image is not `1.2.0` | Start CDS with the public Make arguments and `COSMOS_EMBED_MODELS_DIR` |
| Milvus exited (1) after etcd healthy | Old Milvus + new empty etcd | Stop leftover Compose containers, then start CDS again |
| `--remove-orphans` stopped other containers | Same Compose project | Recreate those services; they are not part of Path D |
| `Connection reset by peer` on health | Gunicorn still booting | Wait loop in Wait Until the API Answers |
| `No ce1_embd_*_parquet` | `CURATOR_DIR` is the parquet folder | Use `output/split-minimal` |
| `/v1/insert-data` HTTP 404 or 400 | Local path or collection **name** | Lab ingest with collection **id** and fallback=1 |
| `/v1/collections/traffic/documents` 404 | Name used as id | Use the id from create-collection |
| `/v1/collections/TRAFFIC_COLLECTION_ID/documents` 404 | Placeholder pasted as the id | Substitute the id from create-collection |
| Search fails, ingest worked | Cosmos-Embed NIM down | Port **9000** health check |
| Search hits only clip 02 | Clip 01 skipped (old IV2 output) | Fresh `output_clip_path` and re-run Path A |
| `ds-health` 404 against a CDS on Kubernetes | `CDS_URL` missing the `/api` prefix that `FASTAPI_ROOT_PATH` and the CDS ingress expect | `export CDS_URL=https://<host>/api` |
| `ds-health` TLS error against a remote CDS | CDS bring-up issued a self-signed certificate | Point `REQUESTS_CA_BUNDLE` at that certificate |
| `ds-health` fails another way | `CDS_URL` wrong, or that CDS is not up | Confirm the URL serves `/health`; bring-up belongs to the CDS repository |

Make target list: `make help`. Image pins and host limits: [Installation](installation.md).
