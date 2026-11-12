# Security boundaries

Report a potential vulnerability privately to the repository owner before publishing customer data, credentials or weaponized CAD files. Never attach real customer models to a public issue. This implementation is undergoing qualification; it makes no compliance certification or physical safety claim.

The protected path is the typed facade: versioned inputs, explicit document/tenant scope, reviewed handler code, expiring grants, state/asset binding, durable intent/idempotency, bounded results and quarantined outputs. Model text, imported properties, tool descriptions, documents, filenames and provider errors are untrusted data. They cannot grant permission or select arbitrary Python/API/REST/GraphQL entry points.

The trusted computing base includes Codex's tool policy, the OS account, Node/Fusion runtimes, plugin/add-in bytes, administered profiles, reviewed templates/posts/machines/tools/recipes, OS credential storage and explicitly installed enterprise adapters. An enterprise adapter is privileged deployment code. A signature or source hash establishes an artifact binding, not that its code or manufacturing parameters are safe.

| Threat | Implemented control | Remaining boundary |
| --- | --- | --- |
| Wrong/stale design or split entity | Explicit opaque document/entity handles; source fingerprints; no first-match token fallback | No provider document lock; missing state becomes a blocker |
| Replayed mutation or lost acknowledgment | Durable intent, lease, idempotency conflicts, unknown-outcome retention | Autodesk effects are not rolled back by a timeout or process exit |
| Code/method/URL injection | Fixed handler registry; typed data; fixed cloud documents and scoped routes | Assisted native tools and administered extensions deliberately have broader authority |
| Local endpoint takeover/browser request | Literal loopback, no redirects/scanning; enrolled native schema; add-in HMAC/session/nonce and browser-header rejection | Native MCP has no authentication. Local request confidentiality and same-user processes require host controls |
| Token theft/confused deputy | Provider-owned PKCE, resource/scope/tenant checks, OS vault, per-grant refresh lease, no token passthrough | OS account/credential service compromise is outside the facade |
| File exfiltration/overwrite/hostile parser | Approved roots/assets, unique private staging, no traversal/UNC/device paths, alias checks and immutable hashes | New documents do not sandbox Autodesk parsers; only trusted inputs are enabled |
| Unsafe NC or altered tooling | Complete approved tool/holder definitions; pinned post/machine/library; exact state/order; Fail posting; quarantine | No qualified generic machine collision result or machine release/control |
| Cloud overspend or ambiguous job | Scoped recipes, recorded intent, admission accounting, retained unknown reservations, explicit reconciliation | An estimate is not a hard provider ceiling; Open Network and real residency must be qualified |

MCP annotations and skill instructions are usability aids, not authorization enforcement. Strong managed deployments must prevent alternate tool/network/configuration paths when that guarantee is required. Do not add a model-controlled approval boolean, profile editor, raw code runner, arbitrary URL fetch, token reader, unconditional retry or automatic machine-transfer tool.

The automated tests use synthetic data and protocol/API doubles. Code review, dependency review, licensed kernel tests, supported-OS ACL checks, representative tenant isolation and manufacturing engineer review remain separate gates. Preview/Insider APIs must not be promoted because they appeared in an installed workspace or in a mock.

Native credential source, patch, Cargo lock, toolchain inputs, target receipts and collected dependency notices are included. The community patch distinguishes a missing credential from vault failures; partial deletion remains retryable and visible. Original npm binaries are withheld. Build receipts bind bytes but do not authenticate their builder or replace signing, independent dependency review, supported-OS vault tests or deployment controls. See the [native build guide](docs/native-builds.md).
