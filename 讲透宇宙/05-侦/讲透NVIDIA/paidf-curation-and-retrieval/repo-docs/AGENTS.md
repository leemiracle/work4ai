<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Agent instructions

This repository works with any coding-agent harness. Project rules live in
one place; this file only routes the harness to them.

## Canonical project instructions

Read [`CLAUDE.md`](CLAUDE.md) first. That file is the operator and
development guide (Make, images, configuration, conventions).

## Skill pack

The product skill lives in `skills/` (`SKILL.md` plus `references/`).
Harness-specific skill directories are symlinks to that tree:

| Harness | Reads first | Skill path |
|---------|-------------|------------|
| Codex | `AGENTS.md` | `.codex/skills` |
| Claude Code | `CLAUDE.md` | `.claude/skills` |
| Cursor / other agents | `AGENTS.md` | `.agents/skills` |

When operating Cosmos Curator or CDF Data Mining in this repo, load
`cdf-curation-and-retrieval` from those skill paths.
