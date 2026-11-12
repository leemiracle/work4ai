<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Cosmos Data Factory Curation and Retrieval Documentation

Turn raw video and image collections into training-ready datasets for
physical AI. Curation and Retrieval runs three GPU-accelerated NVIDIA engines
behind one Make interface:

- **Cosmos Curator** splits, captions, filters, and shards video and images.
- **Data Mining** generates embeddings and selects data by nearest neighbor.
- **Cosmos Dataset Search** indexes curated clips and finds them by text query.

![Curation and Retrieval architecture](assets/CDF-CC-CDS-TDM.png)

## Quick Start

New to the product? Read these three pages in order.

| Step | Page | You finish with |
|------|------|-----------------|
| 1 | [Installation](user-guide/installation.md) | A cloned repository, synced tools, and pulled images |
| 2 | [Samples and Cookbooks](user-guide/samples-and-cookbooks.md) | Sample clips and a cookbook that fits your data |
| 3 | [Get Started](user-guide/getting-started.md) | Your first end-to-end run |

## Choose Your Path

Each path is a complete workflow. Path B is the fastest way to a result.

| Path | What you do | Engines | Start here |
|------|-------------|---------|------------|
| **A** | Curate MP4 videos, or PhysicalAI-AV multi-camera sessions | Cosmos Curator | [Path A](user-guide/getting-started.md#path-a-cosmos-curator-generic) |
| **B** | Generate embeddings and run nearest-neighbor selection | Data Mining | [Path B](user-guide/getting-started.md#path-b-data-mining) |
| **C** | Curate first, then mine the curated embeddings | Cosmos Curator, Data Mining | [Path C](user-guide/getting-started.md#path-c-curation-and-mining) |
| **D** | Curate first, then index the clips and search them by text | Cosmos Curator, Cosmos Dataset Search | [Path D](user-guide/getting-started.md#path-d-curation-and-dataset-search) |

## Documentation Map

### Run the Engines

| Page | Use it to |
|------|-----------|
| [Cosmos Curator](user-guide/operations-curator.md) | Configure and run video and image curation |
| [Data Mining](user-guide/operations-tao-mining.md) | Generate embeddings and run selection or matching |
| [Cosmos Dataset Search](user-guide/operations-cds.md) | Start Dataset Search, ingest Cosmos-Embed1 clips, and search |
| [VLM and LLM Endpoints](user-guide/vlm-llm-endpoints.md) | Connect captioning and language-model endpoints |

### Get Help

| Page | Use it to |
|------|-----------|
| [Troubleshooting](user-guide/troubleshooting.md) | Match a symptom to its fix |
| [User Guide overview](user-guide/README.md) | Find a page by goal |
| [Cookbooks](../cookbook/README.md) | Browse ready-to-run scenario configs |

### Contribute

| Page | Use it to |
|------|-----------|
| [Developer Docs](developer/README.md) | Understand the architecture and repository layout |
| [Contributing](../CONTRIBUTING.md) | Prepare and submit a change |

## Before You Begin

- **Host:** Ubuntu 22.04 or 24.04, Docker 20.10+, and the NVIDIA Container
  Toolkit. Path D needs an x86_64 host and does not support Blackwell GPUs.
- **Access:** run `docker login nvcr.io` with your NGC key before the first
  image pull.
- **Credentials:** keep endpoint keys in the environment or a gitignored
  `.env`. Never put them in Markdown, cookbooks, or logs.

Full host requirements: [Installation](user-guide/installation.md).

## Policies

[Project README](../README.md) · [Changelog](../CHANGELOG.md) ·
[Security Policy](../SECURITY.md) · [Contributing](../CONTRIBUTING.md)
