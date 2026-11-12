# funes-pi

A [pi](https://github.com/earendil-works/pi) extension that gives pi the funes
read tools and keeps the memory current as you work.

pi has no MCP client, so the extension *is* one: it spawns `funes mcp` once over
stdio, keeps it warm for the session, and forwards each call as an MCP
`tools/call`. Same `funes mcp` surface every other agent integration consumes —
just fronted by a thin pi tool. Which tools those are isn't listed here: it
registers whatever `tools/list` returns, so a pi session sees exactly the surface
of the funes binary on PATH.

pi exposes its lifecycle to extensions, so the automation rides in the same
extension: `turn_end` converts the turn just completed and indexes it, and — with
a memory bound — `session_shutdown` publishes, as does `session_start` when the
process is fresh (its other starts follow a shutdown that just published).
Nothing outside `~/.funes/agents/pi` is configured. How the hooks work is in
this repository's [README](../README.md#how-the-bundles-automate).

## Install

Once `funes` is on your PATH, one command extracts this extension to a fixed
`~/.funes/agents/pi` and registers it with pi, user-wide:

```sh
funes add pi
```

funes installs the extension from its published release and brings it to the
newest one on every run; `funes add pi --from ./pi` installs this checkout's
copy, which then runs as installed until named again. Re-running `funes add pi`
keeps the memory bound; `funes add pi local` unbinds it.

For development you can also install the package directly with `pi install ./pi`,
or load it for a single run with `pi -e ./pi`.

## Remove

```sh
funes remove pi
```

Unregisters the extension and takes the whole install with it. Your memory and
pi's own sessions are untouched.

## Requirements

- `funes` on `PATH` (set `FUNES_BIN` to override the binary path).
- pi >= 0.84.0, which is where pi validates the nullable-union arguments the funes tool schemas
  declare. `funes add pi` refuses to register the extension on an older pi rather than leave you
  with tools that reject their own calls.
- A funes memory the binary can read — local, or a live `hf://` remote (needs network + an HF
  token for a private remote). Bind one with `funes add pi <memory>`, or set `FUNES_MEMORY` to pin
  it explicitly — forwarded as the `funes mcp <memory>` positional, and used as the publish target.

The extension declares no dependencies: it talks to `funes mcp` over stdio and to pi through the
extension API pi's loader provides.
