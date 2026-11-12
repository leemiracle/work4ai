# Identity profiles

## What a profile is

An **identity profile** is a named, reusable bundle of policy:

- **Network rules** — ordered allow/deny entries for outbound traffic.
- **Credentials** — secrets (API keys, OAuth tokens) made available to the
  session's tools.
- **GitHub repository permissions** — read, and optionally write, access to
  specific repositories.
- **Plugins** — plugins attached to the profile load in every session it
  applies to.
- **Instructions addendum** — optional free text appended to the system prompt.

Profiles exist so that one policy bundle can be defined once and reused across
many places.

## Scopes and binding

Profiles are **bound to scopes**: the organization, a workspace agent scope,
or a channel agent scope.

- One profile can be bound to many scopes.
- One scope can have many profiles bound to it.

At session start, **every profile bound to any scope in the resolution chain is
applied, additively.** Profiles only *add* capabilities — binding a profile to a
channel agent scope cannot remove something an org-level profile already granted.

## Rules

Rules are ordered allow/deny entries for outbound network access, matched on
host, path, and port. When several profiles apply to the same session their
rules are **merged into a single ordered list**; the first matching rule wins
for each request.

## Credentials

Credentials are secrets the profile injects for the session's tools — for
example an API key for an MCP server, or an OAuth token created by a
connection. They are scoped to the session and not visible in chat.

## GitHub repository permissions

A profile can grant the session read (and optionally write) access to specific
GitHub repositories. The **effective set is the union** across every profile
that applies to the session. See `github-and-instructions.md` for how this
interacts with the agent scope's *default source repos*.

## Where to manage

claude.ai → admin settings → **Claude in Slack** → **Profiles**.
