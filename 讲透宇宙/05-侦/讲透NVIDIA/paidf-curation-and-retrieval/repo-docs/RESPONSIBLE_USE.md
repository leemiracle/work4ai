<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Responsible Use of AI Models

This project does **not host or distribute AI model weights**. It orchestrates
pinned NVIDIA runtime images (Cosmos Curator and TAO Data Services) that
download, load, or call external models (for example video embeddings,
captioning VLMs, CLIP/SigLIP image-text encoders, and optional remote VLM/LLM
endpoints). Users are solely responsible for obtaining, configuring, and
deploying those models in a safe, ethical, and secure manner.

AI models generate outputs based on statistical methods. Those outputs may be
inaccurate, incomplete, or otherwise unsuitable for your use case. By
downloading or invoking a model through this software, you assume the risk of
any harm arising from model responses or outputs. Use of this software and any
linked models is subject to the applicable licenses, acceptable-use policies,
and privacy terms of those models and services. Refer to
[Cosmos Curator](docs/user-guide/operations-curator.md) and
[Installation](docs/user-guide/installation.md) for models referenced by this
repository.

## Guidelines for Responsible Use

- Do not use models to process personal, sensitive, or confidential data unless
  you have a lawful basis and appropriate controls.
- Be aware of and mitigate potential biases or harmful outputs in model
  results.
- Follow security best practices when handling models, inputs, outputs, and
  credentials (API keys, NGC tokens, endpoint URLs).
- Ensure compliance with all relevant laws, licenses, and third-party terms of
  service for every model and endpoint you enable.

## Disclaimer

> This project and its maintainers **do not provide AI model weights** with
> this repository and make **no warranties or guarantees** regarding the use
> of third-party models or cloud endpoints.
>
> You are solely responsible for the use, deployment, and compliance of any
> models integrated with this project. Ensure that all usage follows
> appropriate legal, ethical, and security standards.
