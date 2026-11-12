# PLAN — `@browser_use/eve`

A one-install package that lets any Vercel **eve** agent browse the web with a
Browser Use **cloud browser**. Goal: turn the multi-hour manual integration
(which we did by hand in `~/Projects/lab/eve-lab`) into:

```bash
npm i @browser_use/eve && npx @browser_use/eve add
# set BROWSER_USE_API_KEY → agent can browse
```

## Patterns we're copying (both in-tree, verified)
- **`@vercel/connect`** — a third-party package that plugs into eve via
  **per-framework subpath exports** (`./eve`, `./mcp`, `./ai-sdk`, …), no scaffolder,
  users call a factory in a one-line file. This is our closest analog.
- **eve channels** — adapter lives in the package (`eve/channels/slack`), the user's
  file is `export default slackChannel({...})`, and a **catalog + `eve channels add`
  scaffolder** writes it. We copy the catalog/scaffolder UX for `@browser_use/eve add`.

## What ships (port the working lab code into a package)
Subpath exports, each a small factory:

| Subpath | Factory | Backed by (lab) |
|---|---|---|
| `@browser_use/eve/sandbox` | `browserUseSandbox(opts)` → `defineSandbox` | `agent/sandbox/sandbox.ts` |
| `@browser_use/eve/skill` | `browserUseSkill(opts)` → `defineSkill` | `agent/skills/browser-harness.md` |
| `@browser_use/eve/tools` | `openCloudBrowser` / `stopCloudBrowser` → `defineTool` | (new, hardened mode) |
| `@browser_use/eve/connection` | `browserUseConnection(opts)` → `defineMcpClientConnection` | (alt "mcp" mode) |
| `bin: @browser_use/eve` | `add` scaffolder + catalog | mirrors `eve channels add` |

Thin files the user ends up with (they own these; logic stays in the package):
```ts
// agent/sandbox/sandbox.ts
import { browserUseSandbox } from "@browser_use/eve/sandbox";
export default browserUseSandbox();
// agent/skills/browser-use.ts
export { default } from "@browser_use/eve/skill";
```

## Config surface (default zero-config; opt into depth)
`browserUseSandbox({ mode, proxyCountryCode, profile, timeoutMinutes,
stopOnSessionEnd, approval, networkPolicy, liveUrl })` — maps to real
`start_remote_daemon` options + eve HITL/network primitives. No args = sensible defaults.

## Build tooling
- TS, built with **tsup** (or unbuild) → dual ESM + per-subpath `.d.ts`; `files: ["dist"]`.
- **peerDependencies**: `eve`, `zod` (NOT bundled). Pin a tested compat range —
  we learned eve `ai@7-beta`/`@ai-sdk/provider@4-beta` alignment is load-bearing.
- `exports` map mirrors `@vercel/connect`.

## Testing (reuse what we already proved)
- Keep an `examples/minimal-agent/` eve app in the repo.
- Smoke test: boot `eve dev --no-ui`, POST a session ("open example.com, report title"),
  assert the agent used browser-harness + got the page. (This is literally the test we ran.)
- Optional: an `eve eval` suite as the CI gate.

## Publish & distribute
1. `npm publish` — unscoped `@browser_use/eve` (no org/scope needed), optionally `--provenance`.
2. README: 3-line quickstart + the config table.
3. Get listed in **eve's Integrations gallery** (coordinate w/ Vercel) — same slot as Linear/Notion.
4. Cross-link from Browser Use docs; `npx @browser_use/eve@latest add` works without pre-install.
5. Releases via **changesets**; document supported eve version range; CI matrix vs eve versions.

## Milestones
1. **MVP** — `sandbox` + `skill`, autospawn mode, manual file add. (≈ port lab code.)
2. **Hardened** — app-runtime provisioning + `BU_CDP_WS` (key out of sandbox) + open/stop tools + billing cleanup.
3. **Scaffolder** — `@browser_use/eve add` + catalog + `.env` reminder.
4. **MCP mode** — `connection` subpath + `add --mode mcp`.
5. **Ship** — npm publish + docs + gallery PR.

## Locked decisions (signed off)
1. **Name/scope:** `@browser_use/eve`.
2. **Driver:** **TS-native** — `browser-harness-js` (Bun CLI) in the sandbox + `browser-use-sdk` (Cloud SDK) in the app runtime. No `uv`/Python.
3. **Default mode:** **hardened** (key out of sandbox); autospawn-style opt-in later.
4. **v1 scope:** harness-in-sandbox only; MCP mode fast-follow.
5. **Home:** prototype in `~/Projects/lab/browser-use-eve`, move to a `browser-use` org repo to publish.

## Architecture — TS-native hardened (verified against the repos)
The key (`BROWSER_USE_API_KEY`) lives ONLY in the app runtime. The sandbox only ever sees a scoped WebSocket URL.

1. **Provision (app runtime, `onSession`).** `const b = await new BrowserUse().browsers.create(opts)` → `{ id, cdpUrl, liveUrl }`. (`browser-use-sdk` `BrowserUse`, `client.browsers.create` → `POST /api/v2/browsers`; `cdpUrl` is `string|null`, poll `browsers.get(id)` if null.)
2. **Resolve wss.** `cdpUrl` is HTTPS; `browser-harness-js` needs `wss`. Fetch `GET <cdpUrl>/json/version` → `webSocketDebuggerUrl`.
3. **Inject.** Write the wss (NOT the key) into the sandbox at `/workspace/.bu-cdp`. Keep `b.id` app-side for teardown.
4. **Driver in sandbox.** `bootstrap` installs `browser-harness-js`: obtain the CLI, symlink onto PATH, first call auto-installs Bun (`BROWSER_HARNESS_SKIP_BUN_INSTALL` to control). The package ships a tiny `bh` wrapper that auto-`session.connect({ wsUrl: <contents of /workspace/.bu-cdp> })` on first use, so the skill's ergonomics stay "just run bh".
5. **Drive.** Agent runs CDP snippets: `bh 'await session.Page.navigate({url})'`, `bh 'await session.use(...)'`, etc. (Raw typed CDP — no helper layer.)
6. **Teardown (billing).** `await client.browsers.stop(b.id)` (`PATCH /browsers/{id} {action:"stop"}`) — via a `stop_cloud_browser` tool and/or an eve teardown hook; also set a cloud-browser timeout as a backstop.

### Known gaps to handle in code
- HTTPS `cdpUrl` → `wss` resolution via `/json/version` (don't pass HTTPS to `WebSocket`).
- `cdpUrl` may be `null` while provisioning → poll `browsers.get(id)`.
- Bun must exist in the sandbox (auto-install on first call, or pre-bake into the image).
- `stop(id)` must be idempotent and run in a `finally`/teardown; cloud browsers bill until timeout.
- `browser-harness-js` has NO url env/flag — template the wss into the `connect()` snippet (the `bh` wrapper does this).

### Skill ergonomics (raw CDP, no helpers)
Because `browser-harness-js` exposes raw typed CDP (`session.Domain.method`), the skill teaches the model the 4–5 routing primitives it needs: `listPageTargets()`, `session.use(targetId)`, `session.Page.navigate`, `session.Runtime.evaluate`, `session.waitFor(...)`. (Different from the Python harness's `new_tab/page_info` helpers.)

## Milestones (updated)
1. **Skeleton** ✅ — package.json (exports map mirrors `@vercel/connect`), tsconfig, tsup, peerDeps `eve`+`zod`, dep `browser-use-sdk`.
2. **Core** ✅ — `@browser_use/eve/sandbox` (install + PATH) and `@browser_use/eve/skill` (raw-CDP, async-IIFE output pattern).
3. **Tools** ✅ — `open_cloud_browser` (provision via SDK → resolve wss → inject → connect, enables Page/Runtime) / `stop_cloud_browser` (teardown + billing).
4. **Scaffolder** ✅ — `@browser_use/eve add` (idempotent, `--force`, dep/key nudges).
5. **Test** ✅ — validated against eve-lab via `eve dev --no-ui` + HTTP session: agent opened a cloud browser, read "Example Domain", stopped it. (Still TODO: commit an `examples/minimal-agent` + automate as CI/eval.)
6. **Ship** — repo `browser-use/eve` (private) done; TODO: `npm publish` as `@browser_use/eve`, README, gallery PR.

## Config passthrough (TODO, fast-follow)
`proxyCountryCode` / `profileId` / `timeout` from `browserUseSandbox(opts)` → the
`open_cloud_browser` tool's `createCloudBrowser(opts)` (the SDK + `CloudBrowserOptions`
already accept them; just need to thread config from the factory to the tool).
