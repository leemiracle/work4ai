# Codex launcher configuration

Connecting a credential and activating its administrator-reviewed authority are
separate prerequisites. Launcher settings do not grant authority. The default
plugin starts in credential-free `fixture` mode.

For Codex CLI, use the five non-secret environment settings in the
[plugin guide](../../../README.md) when starting a new session. The trust root
is a directory; the activation receipt is a file outside that directory.

## Clients that do not inherit your shell

A Desktop app started from the Dock does not inherit shell exports. Codex
0.144.3's per-plugin configuration supports tool policy and enablement, not
transport `env`, `cwd`, or `args` overrides. Use a separately named local MCP
entry when those values must be configured explicitly.

In your own editor, merge the following into your existing Codex configuration
(`~/.codex/config.toml` with the default Codex home). Do not replace the file or
edit the plugin cache. Replace every example path with an absolute local path.
Keep the same OS user that connected the credential.

```toml
# Keep the plugin's skills; disable only its bundled MCP launch.
[plugins."grafana-observability@community-plugins".mcp_servers."grafana-observability"]
enabled = false

[mcp_servers.grafana-observability-local]
command = "node"
args = ["./mcp/server.mjs", "--stdio"]
cwd = "/absolute/installed/plugin/root"
tool_timeout_sec = 3600

[mcp_servers.grafana-observability-local.env]
PRODUCTION_MONITORING_MODE = "live"
PRODUCTION_MONITORING_TRUST_ROOT = "/absolute/admin/grafana-authority"
PRODUCTION_MONITORING_ACTIVATION_RECEIPT = "/absolute/private/grafana-receipt.json"
PRODUCTION_MONITORING_ARTIFACT_ROOT = "/absolute/private/grafana-evidence"
PRODUCTION_MONITORING_STATE_ROOT = "/absolute/private/grafana-state"
```

With the default Codex home, this release's installed root is
`~/.codex/plugins/cache/community-plugins/grafana-observability/0.1.0`; expand `~` in
the `cwd` value. Check installed versions with
`codex plugin list --marketplace community-plugins --json`, and update `cwd` after a
plugin upgrade. If the client cannot find Node, set `command` to the absolute
path of your Node.js 22.19+ executable.

These settings contain no credential. Do not put tokens in the configuration,
launcher arguments, or chat. Restart the client, start a new task, and ask the
setup skill to check your exact activated profile alias. If startup or readiness
fails, stop and report the sanitized failure rather than bypassing authority or
credential checks.

Both the bundled launcher and this shared-configuration mechanism are exercised
through the actual Codex 0.144.3 installer and app-server in an isolated,
network-disabled container. That check verifies fixture startup and environment
handling; it is not a Desktop GUI or installed-client live-authentication test.
