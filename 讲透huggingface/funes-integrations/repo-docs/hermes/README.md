# funes-hermes

A Hermes plugin that gives Hermes the funes read tools and keeps the memory current as you work.
Indexing is **beta**.

Hermes has an MCP client, so the read tools are `funes mcp` registered with `hermes mcp add`: a
session sees whatever `tools/list` returns, the surface of the funes binary on PATH. Hermes
discovers plugins under its own home, so the automation is a plugin at `~/.hermes/plugins/funes/`,
enabled with `hermes plugins enable funes`. Its lifecycle hooks convert each completed turn out of
Hermes's session store into funes's spool and index it (`post_llm_call`), and, with a memory bound,
publish at the session boundaries — `on_session_finalize` at the true end, `on_session_start` to
catch up whatever a missed end left behind. Plugin hooks are not shell hooks, so Hermes's consent
allowlist (`~/.hermes/shell-hooks-allowlist.json`) is not involved. How the hooks work is in this
repository's [README](../README.md#how-the-bundles-automate).

## Install

Once `funes` is on your PATH:

```sh
funes add hermes                   # local memory
funes add hermes <org>/<repo>      # …bound to a memory it recalls from and publishes to
```

funes installs the plugin from its published release and brings it to the newest one on every run;
`funes add hermes --from ./hermes` installs this checkout's copy, which then runs as installed until
named again. Re-running `funes add hermes` keeps the memory bound (`funes add hermes local` unbinds
it) and refreshes the plugin.

An install from before the plugin declared funes's hooks as shell hooks in your `config.yaml`.
`funes add hermes` clears it: those entries come out of the file — the one edit funes makes there;
your own hooks and everything else stay as they were — their approvals are revoked, and their
scripts deleted. A `hooks:` block funes cannot read is left whole, and the entries named for you to
delete.

## Remove

```sh
funes remove hermes
```

Disables and deletes the plugin, removes the MCP registration, and clears an install from before
the plugin the same way. Other hooks, approvals, and config keys remain; your memory and Hermes's
own session store are untouched.

## Requirements

- `funes` on `PATH` (set `FUNES_BIN` to override the binary path).
- `python3` on `PATH` at install, to convert the sessions Hermes has already recorded; without it
  they are converted as each session ends.
- A funes memory the binary can read — local, or a live `hf://` remote (needs network + an HF
  token for a private remote). Bind one with `funes add hermes <memory>`.
