# funes-claude

A Claude Code plugin that gives Claude Code the funes read tools and keeps the memory current as
you work.

Claude Code has an MCP client, so the read tools are `funes mcp` registered user-wide with
`claude mcp add -s user`: a session sees whatever `tools/list` returns, the surface of the funes
binary on PATH. Claude Code has a plugin system, so the automation is a hooks-only plugin at
`~/.funes/agents/claude/claude-plugin`, registered with `claude plugin marketplace add` +
`claude plugin install`; Claude's loader activates its hooks — funes never edits your
`settings.json`. `Stop` and `SubagentStop` index the turn just completed; `SessionEnd` and
`SessionStart` publish with a memory bound. How the hooks work is in this repository's
[README](../README.md#how-the-bundles-automate).

## Install

Once `funes` is on your PATH:

```sh
funes add claude                   # local memory
funes add claude <org>/<repo>      # …bound to a memory it recalls from and publishes to
```

funes installs the plugin from its published release and brings it to the newest one on every run;
`funes add claude --from ./claude` installs this checkout's copy, which then runs as installed until
named again. Re-running `funes add claude` keeps the memory bound (`funes add claude local` unbinds
it) and refreshes the plugin — Claude keeps a plugin's content until it is reinstalled, so the
plugin is uninstalled and installed again. An install from before the registry, at
`~/.funes/integrations/claude-plugin`, is unregistered and deleted on sight.

## Remove

```sh
funes remove claude
```

Removes the plugin, its marketplace registration, the MCP registration, and the installed files.
Your memory and Claude Code's own transcripts are untouched.

## Requirements

- `funes` on `PATH` (set `FUNES_BIN` to override the binary path).
- `claude` on `PATH`; without it the files are installed and the commands to register them printed.
- A stock `jq`, 1.6 or newer: the converter is jq, and there is nothing to capture without it.
  macOS 15 and newer ship one; elsewhere `apt install jq`, `dnf install jq`, `apk add jq`.
  `funes add claude` checks that the jq on PATH converts a transcript the way funes reads it before
  it installs anything.
- A funes memory the binary can read — local, or a live `hf://` remote (needs network + an HF
  token for a private remote). Bind one with `funes add claude <memory>`.
