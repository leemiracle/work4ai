<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Developer Docs

Documentation for people **changing** this repository: architecture,
code layout, and contributor setup.

To **run** Curator or Data Mining as a customer, use the
[User Guide](../user-guide/README.md). Complete that product path once, then
return here.

## Architecture

- [Architecture](architecture.md): Make, code layers, engines, S/B mining, data flow

## Contributor setup

This project is currently not accepting public contributions. See
[`CONTRIBUTING.md`](../../CONTRIBUTING.md).

```bash
uv sync --extra dev
uv run pytest tests/unit -q
```

## Related

- [User Guide](../user-guide/README.md)
- [`CLAUDE.md`](../../CLAUDE.md)
- [Skills](../../skills/cdf-curation-and-retrieval/)
