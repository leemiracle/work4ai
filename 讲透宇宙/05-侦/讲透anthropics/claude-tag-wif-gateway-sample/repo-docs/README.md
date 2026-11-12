# Claude Tag Custom Gateway — Sample Implementation

**Sample code. Not maintained and not accepting contributions.** This
is a reference implementation of the gateway connection described in
the Claude Tag documentation under Federated cloud access, "Connect a
gateway". Federated cloud access is in public beta; an organization
Owner, or an admin with full Claude Tag management permission, connects
gateways in Claude Tag admin settings, with no Anthropic involvement. This code is meant to be read, adapted, and
reviewed against your own security requirements before any production
use. It is not a supported product.

## What it does

Anthropic calls your registered endpoint directly, attaching a Claude Tag
identity token to each request in the `Authorization` header as a bearer
token. This gateway:

1. **Validates** every incoming token — signature (ES256, against the
   published JWKS of the issuer the token names), exact match against
   the accepted issuers, your registered audience, and expiry. Anything
   that fails is rejected with a generic 401.
2. **Maps** the verified claims to a principal in your system, from a
   config file — exact-match on the token subject (preferred), an
   optional organization-wide mapping by subject prefix, and a
   `slack_channel_id`-based mapping shown as an alternative.
3. **Serves a discovery route** (`GET /list-services`) so the agent can
   learn at runtime what this gateway offers — one useful pattern for
   making a gateway discoverable to the model.
4. **Answers a readiness probe** at the root (`GET /` or `POST /`) that
   only confirms the caller's token is valid and maps to a principal.
5. **Proxies** requests to mapped downstream services
   (`/services/{name}/...`), injecting a downstream credential from an
   environment variable. The Claude Tag token itself is never forwarded
   downstream.
6. **Logs every authorization decision** as one JSON line with the
   verified subject, so you can read an agent's full subject from the
   log after its first request. The token itself is never logged.

## Layout

```
gateway/constants.py   Default issuer URL, discovery path, key age limit, algorithm allowlist, subject prefixes, control agent id
gateway/jwks.py        OIDC discovery -> jwks_uri -> key cache, refresh on unknown kid
gateway/auth.py        Accepted issuer list, bearer extraction, the four verify checks
gateway/mapping.py     Config-file claims -> principal -> allowed services
gateway/access_log.py  One JSON line per authorization decision, never the token
gateway/main.py        App factory, / readiness, /list-services, /services/{name}/{path} proxy
config.example.yaml    Example mapping config with deliberately fake IDs, plus the
                       reserved connection-check control subject
tests/                 Offline test harness with locally generated throwaway keys
```

## Quickstart

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest          # all tests run offline, no Anthropic dependency
cp config.example.yaml config.yaml  # then edit with your real values
.venv/bin/python -m uvicorn gateway.main:create_app --factory --port 8000
```

Or with Docker:

```bash
docker build -t claude-tag-gateway-sample .
docker run -p 8000:8000 \
  -v "$PWD/config.yaml:/app/config.yaml:ro" \
  -e EXAMPLE_API_TOKEN=... \
  claude-tag-gateway-sample
```

## How this maps to the documentation

Follow the "Connect a gateway" page with this code side by side.

### Step 1 — Choose your audience value

The audience is your gateway's public address: `https://` plus the host
name in lowercase, on the standard port, with no path, query string or
trailing slash, for example `https://gateway.example.com`. The console
accepts nothing else when you connect the gateway, and it is the exact
value every token's `aud` claim will carry. Put it in `config.yaml`
under `audience`. You register it yourself in Step 4; the console then
runs the connection check described under "The readiness route and
the connection check" below, unless you skip it with a recorded
reason. The console accepts only that address form whether or not you
skip the check.

### Step 2 — Validate tokens at your endpoint

`gateway/auth.py` and `gateway/jwks.py` implement four of the five
checks the documentation lists; the fifth, the subject check, is Step 3:

- **Signature** — keys are fetched from the `jwks_uri` named in the
  discovery document at `<issuer>/.well-known/openid-configuration`,
  for each accepted issuer (by default only
  `https://identity.anthropic.com/agents`). The key set is chosen by the
  token's `iss` claim, so a key published by one issuer never verifies
  a token that names another. Only ES256 is accepted. On an unknown key
  id the key cache refreshes once before rejecting, which absorbs key
  rotation (the documentation's troubleshooting advice, implemented).
- **Issuer** — exactly one of the accepted issuers; see "Accepted
  issuers" below.
- **Audience** — the value you registered. On the wire the audience claim
  is a JSON array with one element, which is standard JWT; the code uses
  the library's audience check rather than comparing raw claim text, as
  the documentation recommends.
- **Expiry** — tokens live 10 minutes. The documentation allows up to
  60 seconds of clock skew; this sample grants none (`leeway=0` in
  `gateway/auth.py`), so keep the gateway's clock synchronized.

The test suite (`tests/`) makes the documentation's verification list
runnable: it mints tokens with locally generated throwaway keys and verifies the
gateway rejects wrong-audience, bad-signature, and expired tokens (plus
wrong issuer, `alg=none`, unknown key id, and missing claims) and
accepts a valid token against a local JWKS. `tests/test_issuers.py`
covers the accepted issuer list: the default, one explicit issuer, two
issuers verified with their own keys, a token naming an issuer that is
not listed, and a token signed with another issuer's key. Everything
runs offline.

#### Accepted issuers

By default the gateway accepts tokens from
`https://identity.anthropic.com/agents` only. To accept a different
issuer, set the environment variable `CLAUDE_TAG_ISSUER`. To accept
several, set `CLAUDE_TAG_ISSUERS` to a comma-separated list of every
issuer to accept; it takes precedence over the singular variable.

Every entry must be an https URL with no trailing slash, and a token's
`iss` claim must equal an entry exactly. The gateway keeps a separate
key set per issuer, fetched from that issuer's own discovery document,
and refuses to start on a malformed list. With Docker, pass the variable
with `-e CLAUDE_TAG_ISSUERS=...` on the `docker run` line.

**Retired issuer.** Claude Tag tokens used to come from
`https://identity.anthropic.com/claude-tag`. That issuer is retired:
its discovery document and signing keys are no longer published.
Tokens from the current issuer are not affected. If you added the
retired issuer to `CLAUDE_TAG_ISSUERS` or `CLAUDE_TAG_ISSUER`, remove
it and restart the gateway.

### Step 3 — Map subjects to principals

The token subject identifies one agent:
`wimse://identity.anthropic.com/org/<YOUR_ORG_ID>/agent/<AGENT_ID>`.
The **Connect a gateway** dialog in Claude Tag admin settings shows your
organization's **Subject prefix**,
`wimse://identity.anthropic.com/org/<YOUR_ORG_ID>/agent/` (your
organization ID is the `org_` segment), and the **Control subject** the
connection check uses. The console does not list agent IDs (`cagt_`):
this gateway's authorization log records the subject of every request
whose token verified, including requests it rejects as unmapped, so you
can read an agent's full subject there after its first call. Check the subject in
this order:

1. **Pin the exact agent subjects** when your use case allows it. This
   is the default and the strongest check: put exact-match entries in
   `config.yaml` under `principals`. You update an entry when its
   channel is recreated (see the caveat below).
2. **Otherwise, at minimum require your organization.** Either require
   your organization's prefix on `sub`, which is the opt-in
   `organization_principals` entry described below, or check `iss`
   together with the `tenant` claim (your organization ID). This sample
   does not implement the `tenant` check.

A mapping keyed on the token's `slack_channel_id` claim is also shown,
commented out, under `channel_principals` — a custom endpoint can authorize on any
claim because it verifies the full token itself, but a channel mapping
checks neither the agent nor the organization, so it is the weakest
option; prefer the subject checks above. The claim is present only when
Claude is acting in one Slack channel; a token for a workspace-wide
request has none, and that token matches no `channel_principals` entry.

If you do not know an agent's ID yet, its first request is rejected with
403 and the gateway logs the full subject (see "Authorization log"
below); copy it into `config.yaml`.

To give every agent in your organization the same access without
pinning each one, add an `organization_principals` entry keyed by your
organization's subject prefix,
`wimse://identity.anthropic.com/org/<YOUR_ORG_ID>/agent/` — everything
in your agents' subjects up to and including `/agent/` (shown as
"Subject prefix" where you register the gateway). The example config has
a commented-out entry. The prefix must be complete and end in
`/agent/`; the gateway refuses to start on any other value, so one
organization ID can never match another that merely starts with the
same characters. Exact pins take precedence over the organization entry,
so a pinned agent keeps its own services; the organization entry in turn
takes precedence over `channel_principals`. The reserved
control agent of the connection check is never matched by an
organization entry, so it cannot inherit your organization's services;
keep its exact pin. A token for an agent in any other organization does
not match the prefix and is rejected with 403, which is what the
connection check's wrong-subject probe verifies.

**Channel lifecycle caveat:** an agent's identity is tied to its
channel. Deleting and recreating a channel — even with the same name —
creates a new agent with a new subject, and pinned mappings stop
matching with no other warning. If that happens, read the new subject
from the authorization log (the recreated channel's first request is
logged as `unmapped_subject`) and update `config.yaml`. An organization
mapping keeps working across recreation.

### Step 4 — Connect the gateway in the console and verify end to end

In Claude Tag admin settings (`claude.ai/admin-settings/claude-tag`),
open **Federated cloud access** and, in the **Gateways** section, click
**Connect a gateway**. Enter the address from Step 1 in **Gateway
address**, select the **This gateway checks that each token's subject
belongs to your organization** checkbox, and click **Run check and
connect**. Select that checkbox only if the gateway rejects every
subject outside your organization: this sample does so through
`principals` and `organization_principals`; leave the optional
`channel_principals` mapping commented out (as the example config ships
it), because that mapping accepts a matching channel ID from any
organization. The check sends the two
probe requests described under "The readiness route and the connection
check" below, and both must get the expected answer.

Then add the gateway to an Access bundle attached to the scope of the
channels that should use it, and name the gateway in that scope's custom
instructions so Claude knows it exists, for example: "Internal APIs are
behind https://gateway.example.com. Call GET /list-services there to see
what is available." Anthropic does not review your configuration; the
connection check and your own verification are the safeguards.

To verify, start a new thread in a channel under that scope and ask
"@Claude call GET /list-services on https://gateway.example.com and
tell me what it returns", then confirm the authorization log shows an
accepted token whose subject mapped to the expected principal. Rejection
of wrong audiences, issuers, signatures and expired tokens is what the
test suite covers.

## The discovery route

Your gateway is most useful when the model can learn what it wraps and
how to use it. One useful pattern, served by this sample, is
`GET /list-services`, returning the services the calling agent's
principal may use. Name the gateway and the route in the custom
instructions of the scope whose bundle holds the gateway (Step 4 shows
an example line) so the agent reads it at runtime. An OpenAPI spec is an
equally valid shape.

## The readiness route and the connection check

`GET /` and `POST /` run the same token validation and principal mapping
as every other route and return `{"ok": true}` for a mapped agent, 403
for a valid token with no mapping, and 401 for any other token failure
(503 if the issuer's key set cannot be fetched). The request body is
ignored and nothing is forwarded. It reveals nothing a caller cannot
already learn from `GET /list-services`. It is not an unauthenticated
health check: a probe without a token gets 401.

The console's connection check (the code calls it the registration
test) posts to the gateway address with an empty body twice: once with a
token for a control agent in your organization, which must get 2xx, and
once with a token whose subject names another organization, which must
get 401 or 403. This route is what answers it, but two configuration
points are also required:

- The audience is the gateway's https root URL, with no path or query
  string; the check sends its requests to that address itself. The
  console accepts only that address form, whether or not you skip the
  check; skipping is for a gateway not yet reachable from the internet,
  and then no check runs.
- Add a `principals` entry for the control subject, with
  `allowed_services: []`, so the control token maps to a principal
  without reaching any service. Use the **Control subject** shown in the
  **Connect a gateway** dialog: a reserved test agent, the same in every
  organization, under your organization's prefix,
  `wimse://identity.anthropic.com/org/<YOUR_ORG_ID>/agent/cagt_01YcVfxkQb6JRzqk5kF2tNLh`.
  The example config carries it with a placeholder organization ID, so
  replace that ID with yours. Without this entry the control token gets
  403 and the check reports that the gateway rejects everything. An
  `organization_principals` entry never matches the reserved control
  agent, so this exact pin is still required when you use one.

Passing the check registers the gateway; Claude uses it once it is in an
Access bundle attached to a channel's scope and that scope's custom
instructions name its address (Step 4).

## Authorization log

Every authorization decision writes one JSON line to standard error
through Python's `logging` module, logger name `gateway.access`.
Accepted requests log at INFO with the verified subject and principal;
rejections log at WARNING with a reason: `invalid_token` (missing,
malformed, or failed verification; no subject is logged, because an
unverified token's claims cannot be trusted), `verification_unavailable`
(the issuer's key set could not be fetched, so the response was 503),
`unmapped_subject` (with the verified subject, so you can pin it), or
`service_not_allowed` (with the subject, principal, and service; this
line follows the request's accepted line, because the token and mapping
passed before the service check failed). The token is never written. If
your process already configures logging, the gateway adds no handler of
its own; its lines go through your handlers, with the `gateway.access`
logger set to INFO.

## Security properties of this sample

- Fails closed everywhere: no token, bad token, unmapped agent, unknown
  service, or a missing downstream credential all reject the request.
- ES256 only; `alg=none` and algorithm-confusion attempts are rejected
  before key lookup.
- Signing keys are kept per issuer and chosen by the token's `iss`
  claim, which must exactly equal an accepted issuer; a token naming any
  other issuer is rejected before key lookup, and a token is never
  checked against another issuer's keys.
- An issuer's fetched signing keys are trusted for at most one hour
  after the last successful fetch (the key age limit,
  `MAX_KEY_AGE_SECONDS` in `gateway/constants.py`). After that the
  gateway answers 503 for that issuer's tokens until a fetch succeeds, so
  an issuer outage cannot keep a withdrawn key accepted indefinitely.
  The gateway fetches only when a request arrives, so one that has been
  idle for longer than the limit refetches on its next request and
  answers 503 if that fetch fails.
- Error responses are generic and never echo token contents, and the
  authorization log records subjects only from tokens that verified.
- FastAPI's interactive documentation and OpenAPI routes (`/docs`,
  `/redoc`, `/openapi.json`) are turned off, so the gateway does not
  publish its route list.
- Request headers are forwarded on an allowlist (`Accept`,
  `Accept-Language`, `Content-Type`) and the `Authorization` header is
  replaced with the downstream credential, so the Claude Tag token is
  never forwarded to downstream services — and neither is
  caller-supplied trust context (`X-Forwarded-For`, `X-Real-IP`,
  `Forwarded`, and similar), which would otherwise arrive on the
  gateway's credentialed connection and let an authorized agent spoof
  its network identity to your services.
- Proxied path segments are decoded, checked for traversal (including
  multiply encoded forms), and re-encoded to one unambiguous encoding
  before the upstream URL is built. The check is deliberately
  conservative: it also rejects every character some class of upstream
  server is known to rewrite back into a traversal sequence, including
  ":" (stripped with the rest of an NTFS alternate data stream suffix
  on Windows/IIS-style servers). If a service you proxy legitimately
  uses ":" in paths (some APIs do, for example `resource:action`
  method names), remove `":"` from the rejection list in
  `sanitize_downstream_path` in `gateway/main.py` for your
  deployment; in exchange you accept the traversal risk on any upstream
  that strips a colon suffix, so only loosen this when no such server
  can sit behind the gateway.
- No secrets in config: downstream credentials come from environment
  variables named in the config, never values in it.
- Dependencies are pinned exactly in `requirements.txt`.
- All claim comparisons happen on signature-verified data via the JWT
  library, so no manual secret comparison exists in this code. If you add
  your own shared-secret check (for example an extra header), compare it
  with `hmac.compare_digest`, not `==`.

## Accepted known limitations

Known gaps, deliberately accepted in this sample; review them against
your own requirements before any production use:

- The optional channel-based agent mapping does not check the agent's
  organization. The cross-organization barrier in this gateway is the
  subject check, a pin on your own organization in `sub` (an exact pin
  or an `organization_principals` entry); the audience check is not
  one, because tokens minted for another organization can carry your
  gateway's audience. A channel mapping bypasses that barrier, so prefer
  subject pins.
- The key-set URL named by the issuer's discovery document is fetched
  wherever it points (any HTTPS host); it is not pinned to the
  issuer's own host.
- An issuer emptying its published key set does not take effect at
  once: previously fetched keys keep verifying tokens until they reach
  the key age limit above, and then that issuer's tokens get 503 until
  it publishes a usable key.

## Before production

At minimum: terminate TLS in front of the gateway, add rate limiting, ship
the authorization log somewhere you can search it, set the key age limit
(`MAX_KEY_AGE_SECONDS` in `gateway/constants.py`) to suit your own risk
(a shorter limit cuts how long a withdrawn key stays accepted while the
issuer cannot be reached; a longer one keeps the gateway answering
through a longer outage), pin your container base image by digest,
consider hash-pinned dependency
installs (`requirements.lock.txt` pins the full dependency tree with
hashes: `pip install --require-hashes -r requirements.lock.txt`), and
run your own security review. The subject prefix (`wimse://`) is the Workload
Identifier URI form defined by the IETF WIMSE working group
(draft-ietf-wimse-identifier) — it is a single named constant in
`gateway/constants.py`. The gateway checks that scheme, and a subject pin
matches the full identifier exactly, as that draft specifies. The
optional `organization_principals` mapping is a deliberate policy
exception to that: it matches one organization's complete prefix,
anchored at `/agent/`. The optional channel mapping in Step 3 does not
match the identifier at all.
