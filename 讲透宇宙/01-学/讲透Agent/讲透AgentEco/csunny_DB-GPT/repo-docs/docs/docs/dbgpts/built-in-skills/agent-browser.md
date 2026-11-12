# agent-browser

## Overview

`agent-browser` is a built-in browser automation skill for deterministic, agent-friendly web interaction.

Unlike screenshot-first browser flows, it relies on accessibility-tree snapshots and ref-based element selection.

## Repo path

```text
skills/agent-browser/
└── SKILL.md
```

## When to use it

- multi-step browser workflows
- complex single-page applications
- deterministic element targeting
- isolated sessions for repeated automation

## Core workflow

1. Open the target page.
2. Capture a snapshot with interactive refs.
3. Read the returned JSON structure.
4. Interact with elements using refs such as `@e2`.
5. Re-snapshot after navigation or DOM changes.

## Typical commands

```bash
agent-browser open https://example.com
agent-browser snapshot -i --json
agent-browser click @e2
agent-browser fill @e3 "text"
agent-browser wait --load networkidle
```

## What this skill documents

Because this skill is CLI-driven, its value is primarily in `SKILL.md`:

- navigation patterns
- snapshot strategy
- ref-based interactions
- wait patterns
- multi-session usage
- state save and restore

## Why it matters

This is the built-in skill to use when an agent needs reliable web automation without depending on fragile visual selectors.
