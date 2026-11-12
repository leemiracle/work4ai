<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# About Curation and Retrieval

How to run Cosmos Data Factory (CDF) Curation and Retrieval version
1.2.0: install it, pick a cookbook, pull images, and read the outputs.

This guide is for external customers. If you are changing the code, follow
this guide once so you can run a cookbook, then switch to
[Developer Docs](../developer/README.md).

The public interface is Make. A helper CLI exists for contributors; you do
not need it for the customer path.

1. [About Curation and Retrieval](README.md)
2. [Installation](installation.md)
3. [Samples and Cookbooks](samples-and-cookbooks.md)
4. [Get Started](getting-started.md)
5. [Cosmos Curator](operations-curator.md)
6. [Data Mining](operations-tao-mining.md)
7. [Cosmos Dataset Search](operations-cds.md)
8. [VLM and LLM Endpoints](vlm-llm-endpoints.md)
9. [Troubleshooting](troubleshooting.md)

Read the pages in this order the first time. After that, use the table as a
lookup.

1. [Installation](installation.md): clone, host requirements, pull images
2. [Samples and Cookbooks](samples-and-cookbooks.md): download Video Search and
   Summarization (VSS) clips when you run Path A
3. [Get Started](getting-started.md): Path A Curator, Path B mining, Path C
   curation and mining, Path D Cosmos Dataset Search (CDS)

If something fails, use [Troubleshooting](troubleshooting.md).

## Start Here by Goal

| Goal | Page |
|------|------|
| First end-to-end run | [Get Started](getting-started.md) |
| Clone, sync, host requirements, and limitations | [Installation](installation.md) |
| Download sample clips and pick a cookbook | [Samples and Cookbooks](samples-and-cookbooks.md) |
| Run Cosmos Curator | [Cosmos Curator](operations-curator.md) |
| Run embeddings and Data Mining | [Data Mining](operations-tao-mining.md) |
| Index Cosmos-Embed1 (CE1) clips and search | [Cosmos Dataset Search](operations-cds.md) |
| Wire vision-language model (VLM) and large language model (LLM) endpoints | [VLM and LLM Endpoints](vlm-llm-endpoints.md) |
| Fix a failed run | [Troubleshooting](troubleshooting.md) |

## What You Can Run from This Guide

- Cosmos Curator video and image curation, including PhysicalAI-AV
- Image and text embeddings
- Data Mining nearest-neighbor selection
- Data Mining unique-neighbor matching
- Cosmos Dataset Search Path D on local Compose (CE1 ingest and text search
  using `make search`); public generally available (GA) 1.2.0; not supported
  on Blackwell GPUs; refer to [Cosmos Dataset Search](operations-cds.md)

## Related Material

- Repository hub: [Project README](../../README.md)
- Changing the code: [Developer Docs](../developer/README.md)
- Cookbook index: [Cookbooks](../../cookbook/README.md)
- Release history: [Changelog](../../CHANGELOG.md)
