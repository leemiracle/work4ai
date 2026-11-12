# GitHub repositories and custom instructions

## GitHub repositories

Two separate settings control repository access. They are easy to confuse:

1. **Repository permissions on an identity profile** — grants the session the
   *ability* to read (and optionally write) specific repos. This is **additive
   across every bound profile** (union).

2. **Default source repos on an agent scope** — which repos are *auto-cloned*
   into new sessions. This is **first-non-empty along the chain**: an agent scope that
   sets any value replaces its parent's list entirely; leave it empty to
   inherit.

A repo must be permitted by (1) before it can appear in (2). Listing a repo as
a default source does not by itself grant access to it.

**To add a repo:** install the Claude GitHub App on the repository, then add
the repo to an identity profile's repository permissions in admin settings.
After that you may optionally add it to an agent scope's default sources.

## Custom instructions

Custom instructions are free text appended to Claude's system prompt for
sessions under a given agent, agent scope, or profile.

They can be set on:

- the org-level agent
- a workspace agent scope
- a channel agent scope
- an identity profile (as an instructions addendum)

**Concatenation order at runtime:**

```
org-level agent  →  workspace agent scope  →  channel agent scope  →  each bound profile's addendum
```

Keep instructions scoped to where they belong: org-level for universal
conventions, channel-level for channel-specific context. **Don't duplicate** —
a channel automatically inherits the org's text, so repeating it just bloats
the prompt.
