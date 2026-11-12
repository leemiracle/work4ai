---
name: config-guide
description: Reference guide for configuring @Claude agents — agents, agent scopes, identity profiles, presets, connections, rules, GitHub repositories, and custom instructions. Explains the inheritance model and configuration best practices.
when_to_use: A user asks how to set up @Claude, how agent scopes/agents/profiles work, how configuration inherits across workspace and channels, how to add a GitHub repo or connection, or what the best practice is for read vs write access.
allowed-tools: Read
---

# @Claude — Configuration Guide

@Claude is configured through a small set of layered objects in the claude.ai
admin settings: **agents**, **agent scopes**, **identity profiles**, and the
**presets / connections / repos / instructions** attached to them. The
layering decides what any given session can see and do.

This guide is currently written for the **Slack** surface.

This skill is an **index**. Read the relevant reference file below for the
topic the user is asking about — each is short and self-contained.

| Topic | Reference file |
|---|---|
| Agents, agent scopes, the resolution chain, and per-field inheritance | `agents-and-scopes.md` |
| Identity profiles, scopes, rules, credentials, repo permissions | `identity-profiles.md` |
| Presets, connections (OAuth / MCP), how to install one | `connections-and-presets.md` |
| GitHub repositories and custom instructions | `github-and-instructions.md` |
| Best practices: profile layout, read-only vs read/write, rollout | `best-practices.md` |

All reference files live alongside this `SKILL.md` in the same directory.

After explaining configuration, you can suggest the user run the
`debug-plugins` skill in a **new** Slack thread to confirm the change actually
took effect inside the container.
