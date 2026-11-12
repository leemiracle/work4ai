<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Versioning

Use exact versions to reproduce an installation, and the [changelog](../CHANGELOG.md) to check compatibility before upgrading.

## Compatibility before 1.0

Minor releases in the `0.x` series may change APIs. Patch releases within a minor line are intended for backward-compatible fixes.

Pin a release in a requirements or constraints file:

```text
warp-simdata==0.2.0
```

For a reproducible environment, also pin dependencies such as Warp, NumPy, and optional runtimes. A package pin alone does not pin these dependencies.

## Artifact identity

Public `main` advances by one commit per release. Each release has an immutable tag, such as `v0.2.0`, and matching release notes and a wheel on [GitHub Releases](https://github.com/NVIDIA/warp-simdata/releases).

For `v0.2.0`, the wheel is `warp_simdata-0.2.0-py3-none-any.whl`. Its metadata and `warp_simdata.__version__` both report `0.2.0`.
