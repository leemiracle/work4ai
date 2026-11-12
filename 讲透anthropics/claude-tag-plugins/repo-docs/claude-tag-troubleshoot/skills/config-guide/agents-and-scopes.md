# Agents and agent scopes

## Concepts

- An **agent** is the unit of identity for @Claude. It owns sessions and
  carries configuration: the model, skills, plugins, default GitHub repos,
  default environment, and custom instructions.

- Every organization has exactly one **org-level agent**. This is what a bare
  `@Claude` mention resolves to when no narrower agent scope matches.

- An **agent scope** is an agent overlay bound to a specific Slack surface:
  - A **workspace agent scope** applies to every channel in one Slack workspace.
  - A **channel agent scope** applies to exactly one channel.

## Resolution chain

When `@Claude` is mentioned, configuration is resolved along this chain:

```
channel agent scope  →  workspace agent scope  →  org-level agent
(if one exists)  (if one exists)     (always exists)
```

The most specific scope is consulted first, falling back toward the org-level
agent for anything it leaves unset.

## Per-field inheritance

Inheritance is **per-field**, not all-or-nothing. Different fields combine
along the chain in different ways:

| Field | Behavior along the chain |
|---|---|
| Custom instructions | **Concatenated**, org → workspace → channel. A channel agent scope's instructions are *appended after* its parents', never replace them. |
| Skills | **Union.** An agent scope can add skills but cannot remove a parent's. |
| Plugins | **Union.** Same as skills. |
| Default GitHub repos | **First-non-empty.** An agent scope that sets *any* repos replaces the parent's list entirely. Leave empty to inherit. |
| Default environment | **First-non-empty.** |
| Default model | **First-non-empty.** |
| Identity profiles | Resolved separately — every profile bound to any scope in the chain applies (**additive union**). |
| Memory | **Per-agent scope, never inherited.** Each agent scope has its own isolated memory store. |

## Practical implications

- To give **one channel** a different repo set, set repos on that channel's
  agent scope. Because repos are first-non-empty, this fully overrides the parent.
- To add a skill or plugin **everywhere**, add it to the org-level agent (or to
  an identity profile bound at org scope). Children inherit it automatically.
- You cannot use a child agent scope to *remove* a skill, plugin, or instruction that
  a parent provides — union and concatenation only add.
