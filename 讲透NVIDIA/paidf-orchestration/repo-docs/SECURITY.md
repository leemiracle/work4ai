<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Security Policy

## Reporting a Vulnerability

NVIDIA is committed to addressing security issues in this project responsibly. If you believe you have found a security vulnerability in **CDF Orchestration**, please report it to the NVIDIA Product Security Incident Response Team (PSIRT) rather than opening a public issue or pull request.

- **Email:** [psirt@nvidia.com](mailto:psirt@nvidia.com)
- **Web:** [https://www.nvidia.com/en-us/security/](https://www.nvidia.com/en-us/security/)

When reporting, include enough detail for the team to reproduce and triage the issue:

- A description of the issue and its potential impact.
- The DAG, plugin, script, or file affected (path within this repo).
- Steps to reproduce, expected behavior, and observed behavior.
- Any proof-of-concept, logs, or screenshots that help diagnose the issue.
- Your contact information for follow-up.

PSIRT will acknowledge receipt and coordinate disclosure with the maintainers of this project. Please do **not** disclose the issue publicly until NVIDIA has had a reasonable opportunity to investigate and remediate.

## Scope

This policy covers:

- Workflow code and plugin integrations under `airflow/dags/` and `airflow/plugins/`.
- Deployment and runtime assets under `deploy/`.
- Scripts and automation under `scripts/`, `make/`, and `nfs/`.
- Documentation and sample payloads under `docs/` and `payloads/`.

It does not cover third-party software, container images, or services referenced by this project. Vulnerabilities in those should be reported to their respective maintainers; please still notify PSIRT if the issue is exploitable through this project.

## Supported Versions

Security fixes are applied to actively maintained branches of this repository. Consumers should use the latest branch or release available to them; older snapshots may not be patched in place.

## Getting Help

For non-security questions about using this project, see [README.md](README.md) and the documentation under `docs/`.
