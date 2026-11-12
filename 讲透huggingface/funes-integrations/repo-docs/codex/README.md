# funes-codex

A Codex plugin that gives Codex the funes read tools and keeps the memory current as you work.

Codex has an MCP client, so the read tools are `funes mcp` registered with `codex mcp add`: a
session sees whatever `tools/list` returns, the surface of the funes binary on PATH. Codex has a
plugin system, so the automation is one plugin at `~/.funes/agents/codex/codex-plugin` — a
marketplace root whose one plugin is `plugins/funes` — registered with
`codex plugin marketplace add` + `codex plugin add`. It carries the hooks and a small skill, which
is what lets Codex recognize funes as memory before it loads any of its tools. Codex writes its own
`config.toml` — funes never does — and nothing of funes's goes into Codex's own `hooks.json`.
`Stop` indexes the turn just completed; `SessionEnd` and `SessionStart` publish with a memory
bound. How the hooks work is in this repository's [README](../README.md#how-the-bundles-automate).

**Codex runs a hook only once you have trusted it.** After installing — and again after any change
to a funes hook — run `/hooks` in Codex and review them; until then Codex skips them and nothing is
indexed or published ([Codex docs](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks)).

## Install

Once `funes` is on your PATH:

```sh
funes add codex                    # local memory
funes add codex <org>/<repo>       # …bound to a memory it recalls from and publishes to
```

funes installs the plugin from its published release and brings it to the newest one on every run;
`funes add codex --from ./codex` installs this checkout's copy, which then runs as installed until
named again. Re-running `funes add codex` keeps the memory bound (`funes add codex local` unbinds
it) and refreshes the plugin. A Codex too old to have plugins stops the install rather than leaving
it silently unpublished.

An install from before the plugin is cleared on sight: its skill and scripts go, and its entries
come out of Codex's own `hooks.json` — hooks of your own in that file stay, and the file goes only
once nothing is left in it. Without `jq` to do that, the file is left as it is and named.

## Remove

```sh
funes remove codex
```

Removes the plugin, its marketplace registration, the MCP registration, and the skill, and clears
an install from before the plugin the same way. Your memory and Codex's own rollouts are untouched.

## Requirements

- `funes` on `PATH` (set `FUNES_BIN` to override the binary path).
- `codex` on `PATH`, with plugins; without it the files are installed and the commands to register
  them printed.
- A stock `jq`, 1.6 or newer: the converter is jq, and there is nothing to capture without it.
  macOS 15 and newer ship one; elsewhere `apt install jq`, `dnf install jq`, `apk add jq`.
  `funes add codex` checks that the jq on PATH converts a rollout the way funes reads it before it
  installs anything.
- A funes memory the binary can read — local, or a live `hf://` remote (needs network + an HF
  token for a private remote). Bind one with `funes add codex <memory>`.
