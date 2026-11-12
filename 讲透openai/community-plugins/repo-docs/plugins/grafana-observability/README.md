# Grafana Observability for Codex

Investigate infrastructure, application performance, logs, edge devices, and business KPIs using administrator-approved, read-only Grafana evidence.

[![Watch the Grafana production-monitoring demo](../../docs/media/grafana-production-monitoring-demo.png)](../../docs/media/grafana-production-monitoring-demo-8x.mp4)

**[Watch the 23-second demo · 8× speed](../../docs/media/grafana-production-monitoring-demo-8x.mp4)** · [Full walkthrough · 3 minutes](../../docs/media/grafana-production-monitoring-demo.mp4)

The recording illustrates a local production-monitoring workflow, including a separately approved code patch. This plugin collects evidence; it does **not** patch, deploy, restart services, or change Grafana. The recording is not an installed-package test.

## What it does

| Reviewed pack | Evidence |
| --- | --- |
| `grafana.infrastructure` | CPU, memory, disk space, system load |
| `grafana.apm` | Request and error rates, error codes, p95 latency, slow traces |
| `grafana.logs` | Log events, error rates, security markers |
| `grafana.iot-edge` | Device telemetry and freshness |
| `grafana.business-kpis` | Revenue, conversion, operational KPIs |

Only packs activated by your administrator are available. Runs use bounded time windows and can compare an equal-duration, non-overlapping baseline. Results include explicit freshness/failure states, normalized evidence, source links, and a distinction between signed-rule findings and observed deviations. Missing data is not reported as healthy.

## Install

Requires **Node.js 22.19+**. Installation and MCP startup are tested with **Codex CLI 0.144.3**. From a reviewed local checkout:

```sh
codex plugin marketplace add .
codex plugin add grafana-observability@community-plugins
```

Run the first command from the repository root, then start a new Codex task.
The GitHub-backed marketplace can be added with
`codex plugin marketplace add tonyloehr/community-plugins --ref main`.

Start with:

```text
Use $setup-grafana-observability to check the fixture profile and available packs.
```

The default launcher is a **credential-free fixture**, not a production connection. Its `fixture` profile is ready for a protocol check but deliberately has no activated Grafana packs.
That is intentional: the five investigation skills stop until an administrator
activates the exact reviewed packs and scopes, so a canned demo cannot be
mistaken for customer evidence.

## Connect a real Grafana instance

Use an identity whose **effective permissions** are read-only. A role named
Viewer is not sufficient: some Grafana releases grant dashboard-annotation
writes to Viewers, and this plugin correctly rejects those credentials. Have
the administrator remove mutating grants; do not bypass the check. See
[Grafana's permission definitions](https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/access-control/custom-role-actions-scopes/).

1. On macOS arm64, run the following from the installed plugin root in your own interactive terminal. With the default Codex home, that root is `~/.codex/plugins/cache/community-plugins/grafana-observability/0.1.0`. The credential is entered at a hidden prompt; never paste it into chat.

   ```sh
   node ./scripts/observabilityctl.mjs grafana connect --url <grafana-origin> --profile <profile-alias>
   ```

2. Have your monitoring administrator provide a reviewed, signed authority bundle containing the exact endpoints, scopes, frozen operations, and packs. Connecting a credential does **not** create that authority. See the [complete enrollment and activation procedure](skills/setup-grafana-observability/SKILL.md) and [saved-panel examples](skills/setup-grafana-observability/references/saved-panel-enrollment.md).
3. Validate and activate the bundle with the included `grafana-authorityctl.mjs`. Start a **new Codex CLI session** with the non-secret settings below, replacing every example path. The trust root is a directory; the receipt is the file created by activation.

   ```sh
   PRODUCTION_MONITORING_MODE=live \
   PRODUCTION_MONITORING_TRUST_ROOT=/absolute/admin/grafana-authority \
   PRODUCTION_MONITORING_ACTIVATION_RECEIPT=/absolute/private/grafana-receipt.json \
   PRODUCTION_MONITORING_ARTIFACT_ROOT=/absolute/private/grafana-evidence \
   PRODUCTION_MONITORING_STATE_ROOT=/absolute/private/grafana-state \
   codex
   ```

   The plugin forwards only these five settings, not token variables or arbitrary environment values. Check your exact activated profile alias with the setup skill. For clients that do not inherit shell exports, use the [explicit launcher configuration](skills/setup-grafana-observability/references/client-launch.md); do not assume a Dock-launched Desktop app receives this CLI environment.

Version 0.1.0 ships a hash-pinned **macOS arm64** native credential broker. Other native platforms fail closed. Separately reviewed headless credential arrangements are possible, but are not the interactive Keychain setup described above.

## Safety and tool surface

The five MCP tools are `grafana_profile_status`, `grafana_list_packs`, `grafana_run_pack`, `grafana_get_evidence`, and `grafana_resolve_link`. Model-controlled input is limited to aliases, pack IDs, time windows, and opaque references—not tokens, URLs, datasource IDs, SQL, PromQL, LogQL, or TraceQL. Provider access is read-only. A pack run writes only plugin-owned local audit, run, checkpoint, and evidence state.

## Verify or contribute

From the repository root:

```sh
npm run validate
npm run test:grafana
npm run verify:grafana:source
```

The tests launch an isolated copy of the actual package, not a development server. `npm run test:grafana:live` starts a disposable real Grafana stack; `npm run test:grafana:keychain` creates and removes one disposable macOS Keychain item. Neither uses production credentials. See the [test guide](../../tests/grafana-observability/README.md) for coverage, results, and limitations. The [source/build notes](../../docs/grafana-observability-source.md) explain how to reproduce the integrity-pinned runtime. Do not edit generated source shards by hand.
