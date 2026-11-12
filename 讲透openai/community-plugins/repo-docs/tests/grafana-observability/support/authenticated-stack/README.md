# Disposable authenticated Grafana tests

Run `npm run test:grafana:auth` (or `GRAFANA_E2E_AUTH=1 node --test tests/grafana-observability/authenticated.test.mjs`) from the repository root. Ordinary `npm test` skips this Docker-only suite.

The checked-in topology starts a fresh local Grafana, Prometheus, and synthetic metric exporter. Grafana alone is published, on a dynamically allocated `127.0.0.1` port. A random local administrator password exists only in the runner's memory and disposable container environment. The runner creates its own ten-minute service-account tokens, revokes them, removes its service accounts, and destroys the project and tmpfs database. It never reads or changes an existing Grafana instance, user profile registry, or OS credential-store item. Raw authentication responses and secrets are excluded from diagnostics.

## What is real

- Grafana `12.1.0` supplies the negative compatibility case: its default Viewer role grants dashboard-annotation creation, updates, and deletion. The shipped connection-discovery policy must reject that identity as over-privileged, despite the Viewer role name. The [tagged role definition](https://github.com/grafana/grafana/blob/v12.1.0/pkg/api/accesscontrol.go#L319) retains these writes for backwards compatibility.
- Grafana `12.4.0` supplies the positive strictly read-only Viewer case, plus invalid, Admin, and revoked credentials. Its [tagged role definitions](https://github.com/grafana/grafana/blob/v12.4.0/pkg/api/accesscontrol.go#L269) remove the legacy Viewer annotation-writer role.
- The integrity-verified shipped CLI performs real bounded HTTP discovery and evaluates Grafana's actual permission map. A copied MCP package then activates a test-signed authority root, starts the shipped signed worker, executes all four infrastructure operations against real Prometheus through Grafana, retrieves sealed evidence and source links, and rejects a fresh collection after token revocation.
- The provider doctor is still expected to report its read-authorization warning: a successful health request is not an independent permission proof. The test proves permissions through connection discovery and proves query access through actual collection instead of changing that warning.

The test uses only the fixed `GRAFANA_E2E_DISPOSABLE_BEARER` credential reference, a strict IPv4-loopback endpoint, and `SIMULATED` evidence. It does not enable arbitrary URLs, queries, or production origins.

Recorded local qualification on 2026-08-20: **2 passed, 0 failed, 0 skipped**, in 23.39 seconds on macOS arm64 with local Docker 29.2.1. This covers the two pinned cases above, not every Grafana minor release. The earlier first-time `12.4.0` image download timed out; an explicit image pull completed, and the final cached-image run passed. No product policy was relaxed.

## Explicit test seams and remaining boundary

The shipped CLI source is verified against its release manifest before loading. Only that private compiled module receives a temporary `node:os.homedir` implementation, guarded filesystem writes, scripted TTY input, and an in-memory credential backend. Global built-ins, `HOME`, and `CODEX_HOME` are unchanged; loading a real native addon is forbidden in this harness. The actual raw-input/confirmation and profile lifecycle code runs, but **this is not an automated real-terminal → OS Keychain → shared-profile broker → MCP test**. The MCP worker uses the separately enrolled test environment reference.

Run `npm run test:grafana:keychain` separately for the opt-in native macOS broker roundtrip. `npm run test:grafana:handoff` exercises the real terminal, Keychain, shared profile, and MCP together; it requires an absent real shared-profile store and explicitly creates/deletes one disposable profile. See the [test guide](../../README.md) for its safety conditions and recorded results. The anonymous five-pack/provider-version qualification remains `npm run test:grafana:matrix`.

For deployments, inspect actual permissions instead of trusting a role label. Grafana's [service-account API](https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/api-legacy/serviceaccount/) documents token creation and revocation; its [RBAC action reference](https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/access-control/custom-role-actions-scopes/) distinguishes annotation writes from read permissions. Use a genuinely read-only identity or a reviewed Grafana role configuration. Do not weaken the plugin's admission policy to accept a legacy Viewer with mutation grants.
