---
name: farmer-setup
description: Set up slop-farmer for a GitHub repository end-to-end. Use this whenever the user mentions slop-farmer setup, creating a repo config, choosing scrape limits, checking GitHub rate limits, cleaning PR template boilerplate, inspecting issue/PR title patterns with gh, installing or authenticating the Hugging Face hf CLI, publishing datasets, reproducing dashboards, or deploying the static dashboard to a Hugging Face Space. Be proactive even if the user only asks for one piece of the setup, because config, auth, dataset publishing, and dashboard deployment are tightly coupled here.
compatibility:
  tools: [Read, Write, Edit, Bash]
---

# Slop Farmer Setup

Help the user go from “I want to run slop-farmer on repo X” to a reproducible setup with:

- a working YAML config
- valid GitHub and Hugging Face authentication
- sensible scrape defaults
- repo-specific PR cleanup and suppression rules where possible
- a publishable dataset
- a reproducible static dashboard deployment to a Hugging Face Space

Use the bundled resources:

- Read `references/config-template.yaml` when drafting a config.
- Run `scripts/repo_setup_audit.py <owner/name>` when `gh` is available and the user wants repo-specific sizing or cleanup advice.
- Run `scripts/suggest_setup_config.py <owner/name>` when you want a stronger automated pass over repeated PR/issue body patterns, heuristic cleanup candidates, and an optional fast-agent synthesis branch.

## Important product truths

Be accurate about the current codebase:

- The preferred GitHub env var is `GITHUB_TOKEN`.
- `GH_TOKEN` and `GRAPHQL_TOKEN` are also accepted in code paths.
- If no env var is set, slop-farmer can often fall back to `gh auth token`.
- Hugging Face auth defaults to `HF_TOKEN`, otherwise an existing `hf auth login`.
- Repo-specific YAML config support already exists via `--config`.
- Built-in template cleanup is currently **PR-focused** via `pull-requests.template_cleanup`.
- There is **not** an equivalent first-class issue-body template cleanup setting in the current config. If the user wants issue boilerplate removed, identify likely patterns and clearly label them as manual guidance or future-work, not as a currently supported config knob unless you verify otherwise.
- `deploy-dashboard` publishes a **static dashboard** to a Hugging Face Space. That is different from running the whole pipeline continuously inside a Space.
- `gh api rate_limit` is valid because `gh api` can call arbitrary GitHub REST endpoints, including `/rate_limit`.

## Default response shape

Unless the user asks for something narrower, structure your answer like this:

1. **What I checked**
2. **Recommended config**
3. **Auth setup**
4. **Boilerplate / suppression recommendations**
5. **Run commands**
6. **Space + robustness plan**
7. **Open questions / follow-ups**

Always include a copy-pasteable YAML config and exact shell commands when possible.

## Workflow

### 1) Capture the minimum setup intent

Quickly determine:

- target repo (`owner/name`)
- whether this is a smoke test, recent-history bootstrap, or recurring production-ish run
- whether the user wants only local setup, or also dataset publishing and dashboard deployment
- whether `gh`, `hf`, `uv`, and `npm` are available
- whether they already have GitHub and Hugging Face tokens/logins

If the user already named a repo, move directly into inspection instead of asking generic questions.

### 2) Verify prerequisites

Prefer short, concrete checks.

Recommended checks:

```bash
uv --version
gh --version
hf version
npm --version
```

If `hf` is missing or old, recommend:

```bash
python -m pip install -U huggingface_hub
hf version
```

If the user prefers uv-managed tools, it is also reasonable to suggest:

```bash
uv tool install --upgrade huggingface_hub
```

Then confirm auth with one of:

```bash
hf auth whoami
printenv HF_TOKEN
```

If neither works, recommend:

```bash
hf auth login
```

For headless environments, prefer `HF_TOKEN` over interactive login.

### 3) Set up GitHub auth correctly

If the user says “GITHUB_ACCESS_TOKEN” or similar, clarify that the main supported variable here is:

```bash
export GITHUB_TOKEN=...
```

Useful verification commands:

```bash
printenv GITHUB_TOKEN
gh auth status
gh auth token >/dev/null && echo "gh token available"
gh api rate_limit
```

When advising on token creation:

- Prefer a fine-grained PAT when possible.
- For public repos, read access to repo contents/metadata, issues, and pull requests is usually the right starting point.
- For private repos, say the token must cover that repo.
- Do not imply write access is required for GitHub scraping.

### 4) Inspect the target repo before choosing defaults

If `gh` is available, audit the repo before finalizing config.

Preferred method:

```bash
uv run skills/farmer-setup/scripts/repo_setup_audit.py owner/name
```

For a richer automation pass that also inspects recent PR/issue bodies and can optionally prepare or run a fast-agent synthesis prompt:

```bash
uv run skills/farmer-setup/scripts/suggest_setup_config.py owner/name --prepare-fast-agent
```

If you do not use the script, gather equivalent information manually:

```bash
gh api rate_limit
gh api repos/OWNER/REPO
gh pr list -R OWNER/REPO --state all --limit 100 --json number,title,createdAt,url
gh issue list -R OWNER/REPO --state all --limit 100 --json number,title,createdAt,url
gh api repos/OWNER/REPO/contents/.github
```

For template discovery, also inspect the standard GitHub template locations on the default branch:

```bash
gh api repos/OWNER/REPO/contents/.github/PULL_REQUEST_TEMPLATE.md
gh api repos/OWNER/REPO/contents/.github/pull_request_template.md
gh api repos/OWNER/REPO/contents/PULL_REQUEST_TEMPLATE.md
gh api repos/OWNER/REPO/contents/docs/PULL_REQUEST_TEMPLATE.md
gh api repos/OWNER/REPO/contents/.github/PULL_REQUEST_TEMPLATE
gh api repos/OWNER/REPO/contents/.github/ISSUE_TEMPLATE
gh api repos/OWNER/REPO/contents/.github/ISSUE_TEMPLATE/config.yml
```

Also remember GitHub may inherit community health files from the owner-level `.github` repo. If repo-local templates are absent, check:

```bash
gh api repos/OWNER/.github/contents/.github/PULL_REQUEST_TEMPLATE.md
gh api repos/OWNER/.github/contents/.github/ISSUE_TEMPLATE
gh api repos/OWNER/.github/contents/.github/ISSUE_TEMPLATE/config.yml
```

Look for:

- remaining GitHub core rate limit
- how fast recent issues/PRs are arriving
- whether PR templates or issue templates exist locally or via owner-level community health defaults
- repeated PR title prefixes like `[foo]`, `release`, `docs`, `bump version`, `post-release`
- boilerplate headings in PR templates that should become cleanup patterns

### 5) Choose scrape defaults conservatively

Do **not** jump straight to an unbounded historical scrape unless the user explicitly wants it and has plenty of rate-limit headroom.

Use a staged recommendation:

#### Stage A: smoke test

Use this when auth is unverified, the repo is high-volume, or the user wants a quick first pass.

Typical recommendation:

```bash
uv run slop-farmer scrape \
  --repo OWNER/REPO \
  --output-dir runs/REPO/data \
  --max-issues 200 \
  --max-prs 50 \
  --fetch-timeline
```

#### Stage B: recent bootstrap

Use this for high-volume repos after the smoke test succeeds.

Typical recommendation:

- `fetch-timeline: true`
- `issue-max-age-days: 30` to `60`
- `pr-max-age-days: 14` to `30`
- optionally cap `max-issues` and `max-prs` for the first real run

#### Stage C: recurring incremental runs

Once the user has a healthy snapshot directory, recommend resuming from the watermark and dropping most manual caps unless the repo is extremely busy.

### 6) Config authoring rules

Start from `references/config-template.yaml`.

Good defaults to lean toward:

- `workspace: runs/<repo-slug>`
- `scrape.fetch-timeline: true`
- `dashboard.window_days: 60`
- `dashboard.contributor_window_days: 60`
- `dashboard.contributor_max_authors: 0`
- `analysis.max_clusters: 10`

For analysis backend:

- Prefer `deterministic` if the user has not configured a fast-agent/provider model key yet.
- Use `hybrid` only if the surrounding model setup is already in place or the user explicitly wants it.

When you generate config, explain each non-obvious field in one line.

### 7) Boilerplate cleanup and suppression guidance

Separate three different things clearly:

1. **PR body cleanup** — currently supported via `pull-requests.template_cleanup`
2. **PR cluster suppression** — currently supported via `pull-requests.cluster_suppression_rules`
3. **Issue boilerplate cleanup** — currently mostly advisory/manual unless you verify code support

For PR cleanup:

- Convert template headings into regexes for `section_patterns` or `line_patterns`
- Do **not** strip `Summary` by default just because it is common. In some repos, including OpenClaw, the summary section carries the most PR-specific signal and stripping it can worsen PR-text over-clustering.
- Prefer stripping low-signal checklist/compliance sections like change-type, scope, review/verification, risk, migration, and recovery blocks before removing substantive summary/problem text.
- Keep `mode: merge_defaults` unless the repo needs a total replacement
- Keep `strip_html_comments: true`
- Keep `trim_closing_reference_prefix: true`

For suppression rules:

- Use repeated low-signal routine categories from recent PR titles
- Examples: release workflow churn, version bumps, routine docs sweeps, mechanical post-release PRs
- Prefer precise title patterns over broad catchalls

For issues:

- Inspect issue templates and recent issue titles
- Call out repetitive prefixes or canned text
- If issue forms (`.yml`) or `config.yml` exist, summarize them because they help identify the effective issue intake flow
- Be explicit that this is for manual review or future implementation if there is no config hook yet

### 7.5) Optional fast-agent synthesis branch

If `fast-agent` is installed and the relevant model secret is present, you can upgrade the heuristic pass into a model-assisted synthesis pass.

Recommended flow:

1. Run the deterministic extractor first:

```bash
uv run skills/farmer-setup/scripts/suggest_setup_config.py owner/name --prepare-fast-agent
```

2. If the model requires `HF_TOKEN` and it is present, run:

```bash
uv run skills/farmer-setup/scripts/suggest_setup_config.py owner/name --use-fast-agent --fast-agent-model kimi25
```

Notes:

- The script uses `fast-agent check models --for-model <model> --json` to discover required secret env var names.
- The synthesis flow now writes a JSON Schema artifact and runs `fast-agent go --no-env --model kimi25 --prompt-file ... --json-schema ... --quiet`.
- This is cleaner and more reliable than prompt-only “please emit JSON” guidance because fast-agent validates the output shape before returning it.
- `--shell` is optional and usually unnecessary here because the script has already collected the evidence.
- Prefer the deterministic branch as the source of truth and use the model branch for regex/rule synthesis.

### 8) Hugging Face setup guidance

For local interactive usage:

```bash
python -m pip install -U huggingface_hub
hf auth login
hf auth whoami
```

For CI/headless/Space-style usage:

```bash
export HF_TOKEN=...
hf auth whoami
```

If the user wants both dataset publishing and dashboard deployment, remind them they need:

- a dataset repo id like `USER/repo-pr`
- a Space id like `USER/repo-dashboard`
- and, for non-static Spaces, secrets/env vars can be provisioned with the HF CLI at repo creation time

### 7.6) Tuning pass: use deterministic analysis to catch over-clustering

After you draft repo-specific PR cleanup rules, do a tuning pass before treating the config as production-ready.

Recommended loop:

1. Scrape a recent bootstrap snapshot.
2. Run deterministic analysis on that snapshot.
3. Inspect the largest meta-bug clusters.
4. If you see a very large **PR-only** cluster dominated by `soft_similarity`, check whether it is:
   - missing a corresponding `pr-scope` code cluster
   - weakly or misleadingly anchored on an issue target
   - full of generic PR-template sections rather than shared code or issue linkage
5. Tighten `pull-requests.template_cleanup` and rerun deterministic analysis before switching back to hybrid for publishing.

Useful commands:

```bash
uv run slop-farmer --config configs/REPO.yaml scrape
uv run slop-farmer --config configs/REPO.yaml analyze --ranking-backend deterministic
uv run slop-farmer --config configs/REPO.yaml pr-scope
```

Heuristic for likely PR-template over-clustering:

- a huge PR-only meta-bug cluster from deterministic analysis
- `evidence_types` dominated by `soft_similarity`
- no comparable `pr-scope` cluster
- many PRs sharing compliance/checklist sections but not code areas

If that happens:

- keep the real problem summary text when possible
- do **not** strip `Summary` blindly
- strip lower-signal sections first:
  - change type / scope
  - regression / verification
  - review conversations
  - compatibility / migration
  - failure recovery
  - risks / mitigations

Verified useful HF Space commands:

```bash
hf repos create USER/my-space --type space --space-sdk static --exist-ok
hf repos create USER/my-space --type space --space-sdk docker --secrets HF_TOKEN --secrets GITHUB_TOKEN
hf repos create USER/my-space --type space --space-sdk docker --secrets-file .space.secrets --env-file .space.env
hf spaces info USER/my-space --format json
hf upload USER/my-space ./dist . --repo-type space
```

Useful API-Space volume/bootstrap commands:

```bash
python - <<'PY'
from huggingface_hub import HfApi
api = HfApi()
api.create_bucket("USER/my-api-space-data", exist_ok=True)
PY

hf spaces volumes set USER/my-api-space -v hf://buckets/USER/my-api-space-data:/data
hf spaces volumes ls USER/my-api-space
```

Important notes:

- HF buckets are **not** created with `hf repo create`; use `HfApi.create_bucket(...)`.
- For writable bucket mounts, use `hf://buckets/USER/bucket-name:/mount/path`.
- Dataset repo remains canonical published state; mounted bucket is mutable operational cache only.

### 9) Reliable deployment architecture

Recommend this as the default robust setup:

- **Runner:** local cron, GitHub Actions, or another scheduler
- **Source of truth:** Hugging Face dataset repo published by `refresh-dataset` plus `publish-analysis-artifacts`
- **Presentation:** static Hugging Face Space deployed by `deploy-dashboard`
- **Optional read API:** Docker Space backed by the same dataset repo, with an optional writable HF bucket at `/data`

Explain why this is better than “run everything inside a Space”:

- Spaces are best as published app artifacts
- dataset repos preserve durable snapshots
- scheduled scraping and dashboard rebuilds are easier to reason about outside the serving layer

If the user specifically insists on running the pipeline inside a Space, be honest:

- it is possible with a Docker/custom Space plus secrets and startup scripting
- HF CLI supports `--secrets`, `--secrets-file`, `--env`, and `--env-file` when creating a Space
- but it is less robust as a recurring data pipeline than external scheduling + dataset + static Space

### 10) Command sequences you should prefer

#### Config-driven local workflow

```bash
uv run slop-farmer --config configs/my-repo.yaml refresh-dataset
uv run slop-farmer --config configs/my-repo.yaml analyze
uv run slop-farmer --config configs/my-repo.yaml publish-analysis-artifacts \
  --analysis-id hybrid-gpt54mini-v3 \
  --canonical
uv run slop-farmer --config configs/my-repo.yaml pr-scope
uv run slop-farmer --config configs/my-repo.yaml new-contributor-report
uv run slop-farmer --config configs/my-repo.yaml deploy-dashboard --refresh-contributors
```

Dashboard default note:

- if `--analysis-input` is omitted, dashboard export now prefers published `analysis/current/`
- snapshot-local analysis is only a fallback when canonical current analysis is absent

## Output requirements

When producing a setup answer, include:

- the exact env var names: `GITHUB_TOKEN` and `HF_TOKEN`
- a ready-to-save YAML config
- at least one recommended smoke-test command
- at least one recommended recurring/deployment command
- an explicit note if issue cleanup guidance is advisory rather than currently configurable

## Avoid

- Do not invent unsupported config keys for issue cleanup.
- Do not say GitHub write access is needed for scraping.
- Do not recommend fully unbounded historical scraping by default on busy repos.
- Do not blur together “publish dataset” and “deploy dashboard”; they are separate steps.
- Do not describe Spaces as the only robust place to run scheduled data collection.
- Do not claim template discovery is always repo-local; owner-level `.github` community health files may be the effective source.
