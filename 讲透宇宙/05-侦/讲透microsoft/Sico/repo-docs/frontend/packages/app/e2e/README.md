# E2E Tests

Playwright end-to-end tests for `@sico/app`, running on **two tracks**:

- **mock** (default, hermetic) — backend faked via `page.route`; `webServer`
  runs `vite preview`. Exercises the real built bundle against controlled API
  responses — fast, deterministic, covers the **full path** including error /
  loading / boundary states.
- **real** (`@real`) — the same core flows against the **live backend**,
  verifying front↔back wiring. Structural assertions only, so they survive
  real-data drift.

A single **unified** run shows and executes both tracks in one `--ui` tree — see
[Run modes](#running-tests-run-modes).

> Isolated component/hook logic (form validation, password toggle, error-branch
> splitting) is covered by **unit tests** (`@sico/shared/test`); route guards /
> loaders / search params by **route tests** (`app/test/routes`). E2E owns full
> user flows, URL contracts, and wiring rather than exhaustively repeating those
> matrices. Auth keeps one invalid submission per form to lock the browser-level
> "no API request" boundary. Backend *contract* correctness lives in
> `packages/shared/contract/`.

## Layered by theme (tags)

Every test carries one or more **theme tags** so a run can be sliced by concern
instead of by feature file. Files stay organised by feature; tags cut across
them.

| Tag | Theme | What it guards | When to run |
|-----|-------|----------------|-------------|
| `@reachable` | **Reachability** | every route opens and renders its landmark (no white screen / 500) | fastest health probe |
| `@core` | **Core path** | key **front↔back read/write** flows a release must not break: login → home → send message → project → create/delete → logout | release smoke (must be green) |
| `@key` | **Key features** | secondary interactions & front-end contracts: register, studio, tab/route navigation, empty states, param persistence | release regression |
| `@loading` | **Loading states** | skeletons, spinners, pagination in-flight | UI stability |
| `@error` | **Error handling** | 500s, failed saves, reconnect, graceful degradation | resilience |
| `@a11y` | **Accessibility** | component-level a11y — keyboard reach, alt text, aria-current (lives in the owning feature spec) | independent track |

**`@core` ⇄ `@real` rule:** `@core` marks **complete end-to-end flows** that
exercise the backend (login→land, send→conversation→reply, create→toast→delete,
drop→reconnect→recover) — **not isolated render points** ("the header rendered").
Each `@core` gets a **mock and a real twin** (1:1). Two allowed asymmetries:
- a real *write* with no clean teardown → gate behind a self-delete loop, or keep
  the twin mock-only;
- a **real-only** flow a live backend alone can stage (reconnect via
  page-switch / reload; multi-account RBAC) → `@real` `@core` with no mock twin,
  by design.

Pure front-end behaviour (routing, history, param persistence, tab switches,
empty states) is **not `@core`** — it's `@key`.

A test may hold both a **theme** tag and a **module** tag (`@auth`, `@dw`,
`@project`, `@studio`, `@team`, `@knowledge`, `@sandbox`). Theme tags drive the
run matrix; module tags help local filtering.

### Track tag: `@real`

A third axis marks which **track** a test runs on:

- **`@real`** — runs against the live backend. Declared **once on the describe
  title** (`test.describe("<feature> @real", …)`) and inherited by its tests.
- **No `@real` = mock.** There is deliberately **no `@mock` tag** — gating only
  needs `@real` to tell the two tracks apart, so a second tag would be redundant.

The "prefer real where meaningful" rule:

- `@core` (core happy path) → **mock + a `@real` twin**.
- `@error` / `@key` / `@loading` → **mock only** (real can't stage these).
- Real **write** ops → only with a self-create→self-delete loop (e.g. knowledge
  tag); otherwise mock-only, to avoid polluting the shared environment.

## Running tests (run modes)

Keyed on env vars — the config picks the track and where the browser points:

| Mode | Trigger | baseURL | Runs | Backend |
|------|---------|---------|------|---------|
| **MOCK** | (default) | `localhost:4173` | everything except `@real` | none (`page.route`) |
| **REAL** | `SICO_E2E_URL=…` | that URL | only `@real` | direct |
| **UNIFIED** | `E2E_PREVIEW_PROXY_TARGET=…` | `localhost:4173` | **everything** | real via preview proxy |

UNIFIED runs both tracks under one baseURL: mock specs' `page.route` intercepts
never leave the browser, while `@real` specs fall through the preview proxy to
the live backend. The proxy rewrites `/api/sico` → `/api/dwp`
(`E2E_API_REWRITE_PREFIX`) because test.sico still mounts the API under
`/api/dwp`; drop the rewrite once `/api/sico` is live.

### Package scripts

```sh
pnpm --filter @sico/app e2e          # MOCK full suite (builds first)
pnpm --filter @sico/app e2e:smoke    # MOCK, @reachable + @core only
pnpm --filter @sico/app e2e:real     # REAL, only @real (needs .env.test.local creds)
```

### Filtering by tag (`--grep`)

`--grep` matches a test's title **or** tags; combine with the run mode above.

```sh
# MOCK track, sliced by theme / module:
pnpm --filter @sico/app e2e -- --grep @error          # only error handling
pnpm --filter @sico/app e2e -- --grep "@core|@key"    # release regression
pnpm --filter @sico/app e2e -- --grep @dw             # only digital-worker module
pnpm --filter @sico/app e2e -- e2e/auth-login-happy.spec.ts   # one feature

# REAL track, one module:
SICO_E2E_URL=https://test.sico.microsoft.com \
  pnpm exec playwright test --grep "@real" e2e/auth-login-happy.spec.ts
```

> `@real` interacts with the run mode: in MOCK mode `@real` tests are gated OUT
> (so `--grep @auth` yields only mock auth); in REAL/UNIFIED they're gated IN.
> `--grep @real` alone under MOCK selects nothing.

### UI mode — see the whole tree, run either track

```sh
# MOCK only (real cases hidden by gating):
pnpm exec playwright test --ui --grep @auth

# UNIFIED — mock + real in ONE tree, both runnable:
E2E_PREVIEW_PROXY_TARGET=https://test.sico.microsoft.com \
  pnpm exec playwright test --ui --grep @auth
```

### Watching a run live

```sh
--headed              # open a real browser window
--headed --workers=1  # serial, one window, easier to follow
--debug               # Playwright Inspector, step through manually
--trace on            # record; replay with: pnpm exec playwright show-trace <zip>
```

## Core critical path (`@core`)

The spine a release must not break. Two main branches (DW conversation / project
assets) plus the login–logout loop. **Studio and registration are NOT core** —
they are one-time / low-frequency actions and live in `@key`.

| Step | Route | Assertion |
|------|-------|-----------|
| unauthenticated → login | `/digital-worker` | redirects to `/login?code=401&next=…` |
| login lands home | `/login` → `/digital-worker` | valid creds navigate to home |
| home renders roster | `/digital-worker` | DW card grid renders |
| enter conversation | card → `/…/collaboration/$id` | click card navigates |
| **send from home** | `/digital-worker/$id` | typing + send creates a conversation and navigates |
| streamed reply | `/…/collaboration/$id` | assistant reply streams in |
| project list | `/project` | project cards render |
| project workspace | `/project/$id` | name + assets toolbar render |
| **create project** | `/project` | new project → "Project created" toast |
| logout | sidebar | clears auth, returns to clean `/login` with no expiry toast |

## File organisation

Two orthogonal axes — **files** group by *route/surface*, **tags** cut *across*
files by theme (see below). A file's boundary is a **reusable mock context**:
tests that can share one `beforeEach` mock setup live together; conflicting
setups split (that's why `auth-login-happy` and `auth-login-sad` are separate —
success vs failure need different backend mocks).

Naming: business specs are `<domain>-<surface>` (`project-workspace`,
`dw-collaboration`, `auth-login-sad`); cross-cutting contract specs — those not
owned by a single route — take an `x-` prefix (`x-reachability`, `x-sidebar`).
Generic router/auth-guard behaviour is hosted on the route it exercises (e.g.
routing-persistence lives in `dw-list` under a `describe`; the unauth→login
redirect lives in `auth-login-sad`).

## Coverage matrix (current files)

| Module | File | Cases | `@real` twins |
|--------|------|-------|:---:|
| Auth | `auth-login-happy` / `auth-login-sad` / `auth-register` | 16 | ✅ (login/sad) |
| Digital Worker list + routing | `dw-list` | 14 | ✅ |
| DW home | `dw-home` | 6 | ✅ |
| Chat / collaboration | `dw-collaboration` | 19 | ✅¹ |
| Project list | `project-list` | 12 | ✅ |
| Project workspace | `project-workspace` | 25 | ✅ |
| Asset detail | `project-asset-detail` | 14 | ✅ |
| Knowledge tags | `project-knowledge-tags` | 11 | ✅ (self-clean) |
| Team | `project-team` | 16 | ✅ |
| Sandbox | `project-sandbox` | 6 | ⬜ mock-only² |
| Studio | `studio` | 9 | ⬜ mock-only³ |
| Reachability sweep (x-cut) | `x-reachability` | 11 | ✅ |
| Sidebar / logout (x-cut) | `x-sidebar` | 8 | ✅ |

¹ Chat has 6 `@real` twins: send→streamed reply, history hydration, and the
in-flight reconnect arcs (page-switch / reload). The plan card and network-drop
toast are `test.skip`-guarded — they need a sustained plan stream the default
real worker doesn't guarantee, and are deterministically covered by the mock
plan-card / SSE-drop tests. Deterministic error/replay injection stays mock-only.
² Sandbox device states depend on live provisioning → inherently non-deterministic;
locking live data would be flaky.
³ A real Studio create is a write with no clean teardown (agents can't self-delete
here), so per the follow-up principle Studio stays mock-only.

## Test inventory (every case)

`R` = `@real`, `s` = `test.skip`. Counts use Playwright runtime registrations
from `playwright test --list`: parameterized loops are expanded and declared
skips are included. The unified tree has **167 cases** (**138 mock**, **29 real**),
including **36 `@core`**, **72 `@key`**, and **34 `@error`** registrations. Real
twins exist for every standardized core feature incl. chat/collaboration (6).
The specs and `--list` output are the source of truth for exact counts.

### auth — `@auth`

**`auth-login-happy.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@core` | user signs in with valid credentials → `/digital-worker` |
| m | `@core` | safe `?next=/project` lands on the Projects page |
| m | `@core` | malicious `?next` preserves the trusted origin and lands on `/digital-worker` |
| m | `@key` | already-authed visit to `/login` bounces to `/digital-worker` |
| m | `@key` | developer-mode sign-in lands on `/studio` |
| R | `@core` | signs in for real → `/digital-worker` |
| R | `@core` | real `?next=/project` lands on the Projects page |
| R | `@core` | real malicious `?next` preserves the trusted origin |

**`auth-login-sad.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@error` | incorrect credentials → inline error, stays on `/login` |
| m | `@error` | client-side zod failure → inline error, no API request |
| m | `@core` | unauthenticated `/digital-worker` → auth signal + toast → cleaned `/login?next=…` |
| R | `@core` | real unauthenticated `/digital-worker` → `/login` |

**`auth-register.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@key` | valid signup → "Account Created" toast → `/login` |
| m | `@error` | invalid input → inline error, no request |
| m | `@error` | server conflict → inline error, stays on `/register` |
| m | `@error` | transport failure → network-error copy, not rejected copy |

### digital worker — `@dw`

**`dw-list.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@core` | renders cards; clicking first opens the worker's home |
| m | `@a11y` | first card keyboard reachable (Tab → Enter) |
| m | `@a11y` | every grid img has an alt attribute |
| m | `@loading` | skeleton while first page in flight |
| m | `@key` | empty state when no digital workers |
| m | `@error` | error view + Try again on 500 |
| m | `@key` | infinite scroll loads more via sentinel |
| m | `@key` | 'Show inactive' refetches without status filter, swaps roster |
| m | `@core` | hard-reload on `/digital-worker` stays put (no `/me`) |
| m | `@core` | back/forward across `<Link>` preserves history |
| m | `@core` | deep-link `?foo=bar` preserves search params |
| m | `@key` | add digital worker: dialog save → success toast |
| R | `@core` | real `/digital-worker` renders the roster shell |
| R | `@core` | real: opening first worker navigates to its conversation |

**`dw-home.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@core` | sending a message creates a conversation and navigates |
| m | `@error` | a failed create keeps the draft and toasts |
| m | `@key` | selecting a suggested task prefills the composer |
| R | `@core` | real: first worker's home renders its composer |

**`dw-collaboration.spec.ts`** *(mock-only — see footnote 1)*
| | tags | case |
|:-:|------|------|
| m | `@loading` | header skeleton while agent detail in flight |
| m | `@loading` | message-area spinner while history loads |
| m | `@core` | renders header + composer once agent detail resolves |
| m | `@error` | error view + Try again on detail 500 |
| m | `@loading` | request-pending control while send in flight |
| m | `@core` | renders streamed assistant reply on success |
| m | `@error` | failure toast when send returns HTTP error |
| m | `@key` | cancels in-flight send on Stop |
| m | `@key` | hydrates + renders a history page on mount |
| m | `@key` | renders a completed history plan card with step rows |
| m | `@error` | Reconnecting toast on SSE drop, clears on resume |
| m | `@error` | replays resumed turn's content on reconnect (#191) |
| m | `@key` | switching conversation loads its own history |

### project — `@project` / `@knowledge` / `@team` / `@sandbox`

**`project-list.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@core` | renders first page of projects |
| m | `@loading` | skeleton while first page in flight |
| m | `@key` | empty state when no projects |
| m | `@error` | error view + Try again on 500 |
| m | `@key` | infinite scroll loads more via sentinel |
| m | `@core` | create project → success toast |
| m | `@core` | clicking a project card navigates to its workspace |
| m | `@error` | create project: failed save → error toast |
| m | `@key` | empty-state 'Create Project' CTA opens the dialog |
| R | `@core` | real `/project` renders the list shell |

**`project-workspace.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@core` | renders project name + assets toolbar |
| m | `@loading` | direct load `/project/$id` → full-page skeleton |
| m | `@loading` | direct load of a category sub-route → same skeleton |
| m | `@loading` | in-table skeleton once shell up, rows loading |
| m | `@error` | full-page error view + Try again on detail 500 |
| m | `@key` | assets empty state on empty category |
| m | `@error` | in-table error view on assets list 500 |
| m | `@knowledge` | Add Knowledge: link import → success toast |
| m | `@core` | navigating a knowledge row opens its detail page |
| m | `@knowledge` | editing a knowledge row saves + toasts |
| m | `@key` | Experience tab loads only playbook rows |
| m | `@key` | Deliverable tab loads only deliverable rows |
| m | `@key` | direct load `/experience` selects the tab + rows |
| m | `@key` | searching filters rows + syncs `?q` |
| m | `@key` | toggling CREATED TIME flips sort + syncs `?sort` |
| m | `@key` | collapsing the drawer hides + restore brings it back |
| m | `@key` | editing project from the drawer toasts + closes |
| m | `@key` | deleting project from drawer menu confirms + toasts |
| m | `@key` | a viewer with no role sees no manage affordances |
| m | `@error` | a failed-extraction knowledge row shows failure state |
| m | `@loading` | an extracting row shows a shimmer, not a nav link |
| R | `@key` | read-only `/project/80` renders its real assets shell |

**`project-knowledge-tags.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@key` | renders the knowledge-tags table |
| m | `@loading` | skeleton while query in flight |
| m | `@error` | error view + Try again on list 500 |
| m | `@key` | empty state when no tags |
| m | `@key` | add tag → success toast |
| m | `@key` | delete tag → success toast |
| m | `@key` | edit tag → dialog pre-fills, saving toasts |
| m | `@error` | failed save keeps dialog open + toasts |
| m | `@error` | failed delete keeps confirm open + toasts |
| m | `@key` | Name input hard-caps at 20 chars |
| R | `@key` | create a knowledge tag then delete only that tag |

**`project-asset-detail.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@key` | renders the knowledge detail panel once loaded |
| m | `@loading` | asset skeleton while detail query in flight |
| m | `@error` | error view + Try again on document 500 |
| m | `@key` | delete knowledge: confirm → success toast |
| m | `@error` | drops only the tag area when tag source fails |
| m | `@key` | experience detail renders with a Detail panel |
| m | `@key` | experience Back lands on the owning project (deep-link) |
| m | `@key` | deliverable detail renders file card + Download |
| m | `@core` | a non-ready knowledge asset redirects back to its project |
| m | `@error` | experience detail 500s into the shared error view |
| m | `@error` | deliverable detail 500s into the shared error view |
| m | `@key` | a viewer without rights sees Delete gated |
| m | `@key` | a deliverable with no published file offers no Download |
| R | `@key` | real: opening the first asset row renders its Detail panel |

**`project-team.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@key` | operators tab renders merged roster |
| m | `@key` | removing a member confirms + toasts |
| m | `@key` | inviting a registered user → success toast |
| m | `@error` | inviting an unregistered email aborts + toasts |
| m | `@key` | changing a member's role → success toast |
| m | `@key` | digital-workers tab renders agent roster |
| m | `@key` | dismissing a digital worker confirms + toasts |
| m | `@key` | reassigning a digital worker to a member → toast |
| m | `@error` | operators tab error view when roster fails |
| m | `@core` | bare `/project/$id/team` redirects to operators tab |
| m | `@core` | switching to Digital Workers tab swaps roster + URL |
| m | `@core` | operators tab empty state on empty roster |
| m | `@key` | a non-admin sees no Invite menu / per-row actions |
| m | `@key` | the owner row is immutable even for an admin |
| m | `@error` | digital-workers tab error view when its roster fails |
| R | `@key` | real `/project/80` operators roster renders without crashing |

**`project-sandbox.spec.ts`** *(mock-only — see footnote 2)*
| | tags | case |
|:-:|------|------|
| m | `@loading` | spinner while device list loading |
| m | `@key` | renders device grid on success |
| m | `@error` | error state + retry on list failure |
| m | `@key` | empty state when no live devices |
| m | `@key` | renders the device grid for the project |
| m | `@error` | a non-numeric projectId hits the notFound guard |

### studio — `@studio` *(mock-only — see footnote 3)*

**`studio.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@core` | list: renders agent cards, Create navigates to setup |
| m | `@key` | list: empty state when no agents |
| m | `@error` | list: error view + Try again on 500 |
| m | `@key` | creating a digital worker saves + navigates to edit |
| m | `@error` | a failed create keeps the form + toasts |
| m | `@key` | edit: saving Basic Info → success toast |
| m | `@key` | deploy: confirming posts deploy + toasts |
| m | `@error` | deploy: a failed deploy keeps the dialog open + toasts |
| m | `@key` | operator-mode visit to `/studio` redirected by ModeGuard |

### cross-cutting — `x-` prefix

**`x-reachability.spec.ts`**
| | tags | case |
|:-:|------|------|
| m | `@reachable` | each public/authed route renders `h1`, no error fallback |
| m | `@reachable` | `/` renders the landing page (hero h1 SICO) |
| m | `@reachable` | authed routes reachable in their required mode |
| m | `@reachable` | unknown path renders 404 (not a crash) |
| R | `@reachable` | real `/digital-worker` `/project` `/profile` reachable |

**`x-sidebar.spec.ts`**
| | tags | case |
|:-:|------|------|
| s | `@a11y` | DW nav has aria-current on first paint *(awaits F3)* |
| m | `@key` | collapse toggle changes width + persists across reload |
| m | `@key` | collapsed sidebar reveals toggle on Logo hover |
| s | `@dw` | DW preview list renders ≤ 5 *(awaits F3)* |
| m | `@core @auth` | logout posts bearer token → clean `/login`, no expiry toast + replaced history |
| m | `@error @auth` | logout 500 still clears auth → clean `/login`, no expiry toast |
| m | `@error @auth` | logout 401 is idempotent completion → clean `/login`, no expiry toast |
| R | `@core @auth` | real logout returns to clean `/login` |

## Standardization status (auth is the benchmark)

Every feature now meets the layering bar: mock covers the full path
(`@core`/`@key`/`@loading`/`@error`); `@real` twins exist for every `@core`
read-only / navigation flow, real writes are gated behind self-cleanup, and
`@error`/`@loading`/boundary stay mock-only.

**✅ Standardized with `@real` twins:** `auth-*`, `dw-list` (roster + first-card
nav), `dw-home` (composer mounts), `project-list` (list shell), `project-team`
(`/project/80` operators roster), `project-asset-detail` (first-asset detail),
`project-workspace`, `project-knowledge-tags` (create→self-delete),
`x-reachability`, `x-sidebar` (real logout).

**⬜ Standardized mock-only (rationale in the file header + footnotes above):**
`dw-collaboration`, `project-sandbox`, `studio`.


## Gaps tracked for backfill

Prioritised list of cases not yet covered. `@core` gaps are highest priority.

**P0 — core / creation spine**
- [x] DW home: send message creates a conversation and navigates (`@core @dw`)
- [x] Project: create happy path → toast (`@core @project`)
- [x] Register: valid signup, invalid input (no request), server conflict, transport/network failure (`@key`/`@error @auth`)
- [x] Studio: create + configure a digital worker, save failure keeps form (`@key @studio`)
- [x] Project: delete with confirm — asset delete (`@key @knowledge`)

**P1 — key features**
- [x] Team: invite / remove / toggle admin / reassign DW (`@key @team`)
- [x] Team: permission gating (non-admin hidden, owner immutable), tab switch, empty rosters, DW-roster 500 (`@key`/`@core`/`@error @team`)
- [x] DW list: add digital worker into a project (`@key @dw`); Show/Hide inactive toggle (`@key @dw`)
- [x] DW home: suggested-task prefill (`@key @dw`)
- [x] Studio: list renders / empty / error, deploy-failure, ModeGuard redirect (`@core`/`@key`/`@error @studio`)
- [x] Project list: card→workspace nav, create-failure toast, empty-state CTA (`@core`/`@error`/`@key @project`)
- [x] Asset detail: experience/deliverable 500, Delete gated for non-admin, deliverable no-download (`@error`/`@key`)
- [x] Sandbox: dedicated `/project/$id/sandbox` route grid + notFound guard (`@key`/`@error @sandbox`)
- [ ] Knowledge: upload lifecycle, extraction failure, download (`@key @knowledge`)
- [ ] Profile: renders core info, editable fields save (`@key`)

**P2 — boundaries & permissions**
- [x] Permission-gated actions hidden without rights — team + asset-detail (`@key`)
- [x] Chat: multi-conversation switch resets state (`@dw`)


## Writing a test

- Seed auth with `seedAuth(page)`; install the catch-all with `mockSicoApi(page)`;
  override specific endpoints with `page.route` (most-recent match wins).
- Build response bodies with `makeOkEnvelope(...)` from `@sico/shared/schemas/api`.
- Assert via `getByRole` (heading / link / button / status) — keeps tests
  accessibility-aligned.
- For every cross-route flow, assert both the URL contract and an exact visible
  destination landmark (normally the route-level h1). Same-page validation and
  error cases should assert their relevant UI state instead of a redundant h1.
- Tag every test: `test("…", { tag: ["@core", "@dw"] }, async ({ page }) => {…})`.

## Fixtures

| File | Purpose |
|------|---------|
| `fixtures/seed-auth.ts` | `seedAuth` (logged-in LS), `mockSicoApi` (catch-all stub) |
| `fixtures/login-api.ts` | `mockLoginSuccess`, `mockLoginCredentialsError` |
| `fixtures/project-fixtures.ts` | project/asset payload builders |
