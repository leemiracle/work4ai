# Best practices

- **Put plugins on identity profiles, not directly on agent scopes.** A profile bound
  at org scope makes the plugin available everywhere in one step. Attaching the
  same plugin per agent scope means re-adding it for every new channel and keeping all
  of them in sync by hand.

- **Use separate profiles for read-only vs read/write access.** Create one
  profile with read-only GitHub permissions and broad network rules, and bind
  it at org scope so every session can *read*. Create a second profile with
  write permissions and bind it **only** to the specific agent scopes (channels) where
  Claude should be allowed to push or merge. This limits blast radius — a
  misconfigured or experimental channel can't accidentally write to production
  repos.

- **Prefer workspace agent scopes over per-channel agent scopes for shared config.** If ten
  channels need the same setup, configure one workspace agent scope. Create channel
  agent scopes only for genuine per-channel differences (a different default repo, a
  channel-specific instruction).

- **Config changes apply to new sessions only.** After changing profiles,
  plugins, repos, or instructions, start a **fresh Slack thread** to pick them
  up. Existing threads keep the configuration they were started with for their
  entire lifetime.

- **Verify with the debug skill.** After any configuration change, ask Claude
  in a new thread to run the `debug-plugins` skill and confirm what actually
  loaded inside the container.
