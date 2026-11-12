# deny-actions-registry

Org-wide guardrails for `huggingface/*` repos: blocks unsafe GitHub
Actions and compromised npm packages on every PR via a reusable
workflow.

## What it protects against

On every PR / push to `main`:

1. **Non-pinned actions** — `uses: foo/bar@v1` (mutable tag) rejected.
   Only 40-char commit SHAs accepted. Enforced by [pinact].
2. **Comment / SHA mismatch** — `uses: foo/bar@<sha>  # v1.2.3` where
   the comment lies about the version is rejected.
3. **Known-compromised actions** — anything listed in `denylist.yaml`
   is rejected.
4. **Known-compromised npm packages** — anything listed in
   `deny-packages.yaml`, or flagged by the OSV database, is rejected.

[pinact]: https://github.com/suzuki-shunsuke/pinact

## Files

| Path | Purpose |
|---|---|
| `denylist.yaml`                   | Blocked GitHub Actions SHAs |
| `deny-packages.yaml`              | Blocked npm package versions |
| `.github/workflows/security-gate.yml`  | Reusable workflow |
| `scripts/`                        | Check scripts |
| `.github/CODEOWNERS`              | Required reviewers for denylist edits |

## Adding an entry

Open a PR editing `denylist.yaml` or `deny-packages.yaml`. CODEOWNERS
will request review. See the YAML headers in each file for the schema.

## Caller usage

Repos in scope inherit the checks automatically via an Organization
Ruleset. Repos that opt in manually:

```yaml
name: security-validate
on: pull_request
permissions:
  contents: read
  pull-requests: write
jobs:
  security:
    uses: huggingface/deny-actions-registry/.github/workflows/security-gate.yml@<sha>
```

Pin to a SHA, not `@main`.

## Visibility

This repo is **public** — required so public `huggingface/*` repos can
consume the reusable workflow.
