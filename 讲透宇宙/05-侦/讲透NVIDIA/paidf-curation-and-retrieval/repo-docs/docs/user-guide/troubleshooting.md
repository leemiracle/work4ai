<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Troubleshooting

1. [About Curation and Retrieval](README.md)
2. [Installation](installation.md)
3. [Samples and Cookbooks](samples-and-cookbooks.md)
4. [Get Started](getting-started.md)
5. [Cosmos Curator](operations-curator.md)
6. [Data Mining](operations-tao-mining.md)
7. [Cosmos Dataset Search](operations-cds.md)
8. [VLM and LLM Endpoints](vlm-llm-endpoints.md)
9. [Troubleshooting](troubleshooting.md)

Make targets validate inputs before expensive GPU work when it can. Treat every
nonzero exit as failure.

## Preflight Failures

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| `DATA_DIR= required` | Missing Make variable | Pass `DATA_DIR=$PWD/...` |
| Path not contained in `DATA_DIR` | File outside mount root | Move data under `DATA_DIR` |
| Namespace / parquet empty | Empty S or B | Check row counts |
| Non-finite embedding / NaN | Corrupt vectors | Regenerate embeddings |
| Dimension mismatch between S and B | Different model families mixed | Rebuild both sides; set matching `TDM_EMBEDDING_BACKEND` |
| Reserved `embedding` column on embedding **input** | Input already has embeddings | Use a fresh input parquet |
| Missing `text` column | Text-embeddings input wrong schema | Add `text` |
| `class_stratified` without detections | Incomplete unique-neighbor-matching knobs | Set detection files, format, and `RARE_CLASS_LIST` |
| COCO detection is a directory | Wrong shape for `DETECTION_FORMAT=coco` | Pass a single JSON **file** |
| KITTI detection is a file / empty dir | Wrong shape for `kitti` | Pass a directory of `.txt` labels |
| Invalid metric `l2` | Unsupported alias | Use `euclidean` |
| Image not found locally | Pull skipped | `make pull-data-mining` |

## Docker and GPU

**Docker permission denied**

```bash
sudo usermod -aG docker $USER && newgrp docker
```

**GPU not visible in container**

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

Install or repair NVIDIA Container Toolkit if the second command fails.

| Symptom | What to do |
|---------|------------|
| Invalid GPU device | `GPUS='"device=9999"'` fails. Use `GPUS=all` or a valid device index. |

## Cosmos Curator

| Symptom | What to do |
|---------|------------|
| Curator skips already-processed videos | Delete or change `output_clip_path`. |
| Vision-language model (VLM) or model load failures | Check Hugging Face token file permissions, `nvidia-smi`, and `MODELS_DIR`. For remote endpoints, confirm `/v1/models` health and `EXTRA_DOCKER_ARGS` host-gateway mapping. Refer to [VLM and LLM Endpoints](vlm-llm-endpoints.md). |
| Endpoint unreachable from Curator | Set `EXTRA_DOCKER_ARGS="--add-host host.docker.internal:host-gateway"` when URLs use `host.docker.internal`. |
| VLM HTTP 500 / `EngineDeadError` | Endpoint failure, not Curator. Relaunch the VLM with `--max-num-seqs 1` and check `/v1/models` again. |
| Out of memory | Lower `captioning_window_size` / batch sizes, or restrict `GPUS`. |
| `ffmpeg: command not found` in container | `make ffmpeg-install` and `make check-setup`. |
| Ray "Deadline Exceeded" | Prefer `DOCKER_NETWORK=bridge`. If Docker disk is nearly full, set `CURATOR_TMP` to a large filesystem. |

## TAO Embeddings and Mining

| Symptom | What to do |
|---------|------------|
| `make check-data-mining-image` fails | Run `make pull-data-mining` after `docker login nvcr.io`. |
| Nearest neighbors dimension mismatch | Regenerate S and B with the same embedding model; declare `TDM_EMBEDDING_BACKEND` correctly. |
| Custom column names ignored | Nearest neighbors uses `SOURCE_EMBED_COLUMN_NAME` / `TARGET_EMBED_COLUMN_NAME`. Unique neighbor matching uses `SOURCE_EMBEDDING_COLUMN` / `TARGET_EMBEDDING_COLUMN`. |
| Unique neighbor matching `class_stratified` rejected | Supply both detection paths, `DETECTION_FORMAT`, and non-empty `RARE_CLASS_LIST`. |
| Unique neighbor matching output missing `final_unique_files.parquet` | The job did not complete; inspect logs and `summary.json` if present. |

## Cosmos Dataset Search

Full recipe: [Cosmos Dataset Search](operations-cds.md).

| Symptom | What to do |
|---------|------------|
| Image is not `cosmos-dataset-search:1.2.0` | `.env` or `local.env` sets `CDS_PROFILE` to a value other than `public`; image pins in those files apply only then. For public generally available (GA), pass `make pull-dataset-search CDS_PROFILE=public DATASET_SEARCH_TAG=1.2.0 DATASET_SEARCH_REGISTRY=nvcr.io/nvidia/blueprint/cosmos-dataset-search` (Make arguments, not shell prefixes). Confirm `docker ps` shows `cosmos-dataset-search:1.2.0`. Refer to [Public GA Recipe](operations-cds.md#public-ga-recipe). |
| `ds-health` fails against a CDS you deployed yourself | `CDS_URL` must point at an API that serves `/health`. Deploying CDS outside Compose belongs to the CDS repository; this repository only talks to the endpoint. Refer to [Using a CDS You Deployed Yourself](operations-cds.md#using-a-cds-you-deployed-yourself). |
| Create-collection HTTP 500 `No pipelines have been initialised` | The running image disabled `cosmos_video_search_milvus`. Use public `1.2.0` with the Cosmos-Embed1 overlay (pass `COSMOS_EMBED_MODELS_DIR`). Confirm `curl -sS http://localhost:8888/v1/pipelines` has `"enabled": true` and `"missing": []`. |
| Milvus exited (1) | Leftover Milvus with a new etcd. Run `make down-dataset-search`, then `docker compose -f deploy/compose/docker-compose.yml down --remove-orphans`, then `make up-dataset-search` with the public `1.2.0` Make arguments. `--remove-orphans` can stop other containers on the same Compose project. |
| `COLLECTION=TRAFFIC_COLLECTION_ID` HTTP 404 | That string is a placeholder in the docs. Paste the id from create-collection. |
| `Connection reset by peer` on `ds-health` | gunicorn is still starting. Wait and retry `curl -sf http://localhost:8888/health`. Do not chain health in the same paste as `up-dataset-search`. |
| `No ce1_embd_*_parquet` | `CURATOR_DIR` must be the Curator output root (`.../output/split-minimal`), not `ce1_embd_224p_parquet`. |
| `/v1/insert-data` or `/collections/traffic/documents` HTTP 404 | CDS keys collections by **id**, not name. Local files are not visible inside the CDS container. Copy the id from create-collection and rerun ingest with `ALLOW_LAB_DOCUMENT_FALLBACK=1`. Do not paste the placeholder `TRAFFIC_COLLECTION_ID`. |
| Search fails after ingest | Cosmos-Embed1 on port 9000 is not healthy. Check `curl -sf http://127.0.0.1:9000/v1/health/ready` and confirm `cosmos-embed` is Healthy in `docker ps`. |
| Hits only `SDG-Intersection-02.mp4` | Curator skipped clip 01 because `processed_videos` already existed (often InternVideo2). Use a new `output_clip_path` and rerun Path A. |

## Registry Authentication

Use Docker interactive login. Never embed tokens in scripts or logs.

## Still Stuck

1. `make help`
2. Rerun with a minimal fixture ([Get Started](getting-started.md))
3. Confirm image tags with `make check-image` / `make check-data-mining-image`
