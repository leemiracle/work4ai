# claude-tag-troubleshoot

A Claude Code plugin that helps you **set up** and **debug** @Claude — the
agent that responds when you tag `@Claude` in a connected chat surface,
backed by remote Claude Code sessions.

It does two things:

1. Explains the configuration model (agents, agent scopes, identity profiles,
   connections, GitHub repos, custom instructions) and how settings inherit
   from organization → workspace → channel.
2. Diagnoses, from **inside a running session**, why a plugin or skill you
   configured in admin settings isn't loading — and tells you how to fix it.

## What's included

### Skills

| Skill | Purpose |
|---|---|
| `config-guide` | Reference for agents, agent scopes, identity profiles, presets, connections, rules, GitHub repos, and custom instructions — including the inheritance table and best practices. |
| `debug-plugins` | Step-by-step in-container diagnostic: inspects mount directories, the launch command, and startup logs to determine which configured plugins/skills loaded, which failed, and why. |

### Commands

| Command | Purpose |
|---|---|
| `/claude-tag-troubleshoot:debug-plugins` (short form: `/debug-plugins`) | Runs the `debug-plugins` skill against the current session and reports findings with specific fixes. |

## License

Apache 2.0
