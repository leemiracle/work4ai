<!-- Use a Conventional Commit-style title and keep it within 72 characters. -->

# Pull Request

## Why

- Explain the problem or need this change addresses.

## What changed

- Summarize the substantive changes.

## Review guide

- Tell reviewers where to start and identify the highest-risk or most
  important parts of the change.

## Compatibility impact

- Describe API, schema, wire-format, MSRV, or behavioral compatibility
  effects. Write `None` when there are none.

## Dependency and licensing impact

- Describe dependency, license, package-content, or third-party-notice
  effects. Write `None` when there are none.

## Related issue

- Link a related issue when one exists.

## Testing

- List the exact commands run and their results.

## Checklist

- [ ] I confirmed this belongs in the Rust implementation repository and is
  not a language-neutral specification change better handled in
  [yaml-sigil-spec](https://github.com/NVIDIA/yaml-sigil-spec).
- [ ] I confirmed this change does not bypass or conflict with the public API
  contract in
  [yaml-sigil-traits](https://github.com/NVIDIA/yaml-sigil-traits); any required
  traits changes are already available or tracked as coordinated work.
- [ ] I have the right to submit this contribution, and every commit includes a
  `Signed-off-by` trailer that exactly matches its Git author.
- [ ] I understand and can explain this change.
- [ ] I updated documentation or tests where needed.
- [ ] I reviewed `CONTRIBUTING.md` and `SECURITY.md`.
