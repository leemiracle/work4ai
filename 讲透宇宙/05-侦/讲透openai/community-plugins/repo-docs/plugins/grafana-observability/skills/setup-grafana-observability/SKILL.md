---
name: setup-grafana-observability
description: Guide setup for and verify a reviewed, read-only Grafana Observability profile and its activated capability packs. Use when a user asks to set up Grafana access, verify profile readiness, discover available infrastructure, APM, log, IoT or business KPI packs, or troubleshoot why a Grafana pack cannot run.
---

# Set Up Grafana Observability

Guide a shared-credential connection through the human terminal flow when needed, then verify an independently activated monitoring profile without handling its credential or exposing provider configuration.

## Safety contract

- Use only `grafana_profile_status` and `grafana_list_packs`. The other Grafana tools are for a subsequent evidence workflow.
- Accept a `profileAlias` only. Never ask for or receive a token, password, header, Grafana URL, datasource identifier, query, dashboard JSON, or credential reference.
- Do not use HTTP, a browser, shell commands, provider CLIs, or another monitoring plugin as a fallback.
- Do not create, edit, or delete dashboards, alerts, datasources, deployments, or runtime state.
- Treat `LIVE`, `REPLAY`, and `SIMULATED` as distinct origins. A name such as `prod` does not grant permission to contact a live system.
- If a required tool is unavailable, report that the plugin may be missing, disabled, unbuilt, or unable to start. Never imitate a successful tool response.

## Workflow

1. Ask whether the user already has an administrator-activated profile alias. Do not enumerate or guess aliases. If they need a new alias, have the human choose one common contract-safe value before connecting: lowercase, at most 80 characters, and matching `^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$` (for example, `grafana-prod`).
2. If the user has no alias, stop before calling MCP tools. On a supported macOS build, tell the user to run this from the installed plugin root in their own interactive terminal, substituting the origin and the contract-safe alias locally without pasting either the credential or command output into chat:

   ```sh
   node ./scripts/observabilityctl.mjs grafana connect --url <grafana-origin> --profile <profile-alias>
   ```

   The terminal flow prompts for the Grafana read credential with no echo, discovers only bounded read permissions and certified datasources, prints a non-secret preview, and stores nothing until the user types `ACTIVATE`. It stores the shared profile and keychain credential only; it does not create monitoring authority. A role named Viewer is not proof of read-only access: some Grafana versions grant Viewers dashboard-annotation creation, editing, or deletion. If discovery reports over-privileged access, ask the administrator for an identity with those mutating grants removed; never suggest bypassing the permission check.
3. Explain the separate human administrator step. A saved panel is only one field in the strict enrollment envelope; a raw dashboard export is rejected. The exact Prometheus and PostgreSQL envelope examples are bundled at `./skills/setup-grafana-observability/references/saved-panel-enrollment.md`. After reviewing and replacing every example value, the operator may run `node ./scripts/grafana-authorityctl.mjs saved-panel enroll --input <absolute-enrollment-json> --output <absolute-proposal-json>` from the installed plugin root. This offline command accepts one bounded regular JSON file, compiles exactly target A through the certified datasource validators, and emits one hash-pinned proposal without contacting Grafana or activating anything. PostgreSQL enrollment additionally requires `postgresMaxRows` and the exact hash-bound `postgresReadOnlyIdentity: { roleIdentitySha256: "<64-lowercase-hex>", privilegeModel: "SELECT_ONLY" }` attestation. A separately provisioned organizational authority bundle and reviewed distribution path are prerequisites. This plugin validates and activates that bundle; it does not assemble or sign trust roots. If no reviewed bundle or distribution path exists, stop and request one from the organizational monitoring administrator.
4. Before activation, the human operator must provision a real owner-only (`0700`) receipt parent directory outside both the inspected checkout and trust root; the CLI does not create that parent. The operator validates the assembled root with `node ./scripts/grafana-authorityctl.mjs trust-root validate --root <absolute-admin-root>`, reviews the exact returned root-manifest and trust-bundle digests, and only then runs `node ./scripts/grafana-authorityctl.mjs trust-root activate --root <absolute-admin-root> --receipt <absolute-owner-only-receipt> --expected-root-manifest-sha256 <reviewed-digest> --expected-trust-bundle-sha256 <reviewed-digest>`. The operator configures the local MCP launcher with `PRODUCTION_MONITORING_MODE=live` plus absolute `PRODUCTION_MONITORING_TRUST_ROOT` and `PRODUCTION_MONITORING_ACTIVATION_RECEIPT` paths, then restarts the worker. Never run shell commands or perform or imply this human activation from the skill.
   The bundled launcher forwards only the five reviewed non-secret mode, authority, receipt, artifact, and state settings. A Desktop app started from the Dock does not inherit terminal exports. Refer the human operator to `./skills/setup-grafana-observability/references/client-launch.md` for the tested explicit Codex configuration; do not change their client configuration from this skill.
5. This 0.1.0 release supports seamless native setup only on macOS arm64. macOS x64, Linux, Windows, and musl fail closed because their native credential assets are not included. A separately administered headless Linux trust root may use an enterprise broker or named environment reference, but that is outside this interactive shared-profile flow and receives no seamless-keychain claim. If the CLI reports that the credential store is unavailable, report this platform or assembly limitation and do not solicit or retry through files, environment secrets, or shell credential helpers.
6. After the user confirms both credential connection and administrator activation, obtain the exact non-secret `profileAlias` and call `grafana_profile_status({profileAlias})`.
7. Report readiness, origin modes, check statuses, and limitations. Stop if the result is `ERROR` or readiness is `BLOCKED`.
8. Call `grafana_list_packs({profileAlias})`.
9. List the exact returned pack IDs, revisions, use cases, and required/optional operation counts. Do not infer a pack that was not returned.

The supported pack IDs are `grafana.infrastructure`, `grafana.apm`, `grafana.logs`, `grafana.iot-edge`, and `grafana.business-kpis`, but only activated entries returned by `grafana_list_packs` are usable.

## Interpret status exactly

- `COMPLETE`: the requested check or list completed; it is not proof that later evidence is healthy.
- `EMPTY`: no activated packs were returned; do not describe setup as ready for collection.
- `PARTIAL`: some readiness checks or evidence are missing or mixed; name the limitation.
- `ERROR`: the request failed or was rejected; report only a returned sanitized error code, when present, and stop. Never invent a code for a blocked status object.

## Completion format

Return the profile alias, readiness and result status, available origin modes, activated packs, failed or warning checks, active safety constraints, and the smallest next action. Never call the profile connected or ready unless the real status response supports that statement.
