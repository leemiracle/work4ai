# Issue / PR clustering

`slop_farmer.reports.analysis` clusters related issues and pull requests into
issue-centered "meta-bug" groups.

This is stricter than PR scope clustering. The goal is not just to group work in
the same subsystem, but to find:

- duplicate or near-duplicate issues
- duplicate or competing PRs
- mixed issue + PR clusters that appear to describe the same underlying problem

The analysis supports two ranking modes:

- `deterministic`: heuristic-only soft-edge acceptance
- `hybrid`: the same deterministic pipeline plus bounded LLM review of
  ambiguous soft edges

## Inputs

The module uses snapshot data the pipeline already materializes:

- `issues.parquet`
- `pull_requests.parquet`
- `comments.parquet`
- `reviews.parquet`
- `review_comments.parquet`
- `pr_files.parquet`
- `pr_diffs.parquet`
- `links.parquet`
- `events.parquet` when timeline fetching is enabled

The public entrypoint is:

- `run_analysis(options)`

There is also a CLI command:

```bash
uv run slop-farmer analyze \
  --snapshot-dir data/snapshots/20260324T150154Z
```

By default that writes `analysis-report.json` next to the snapshot.

## Algorithm

For a snapshot:

1. Load issues, PRs, comments, reviews, review comments, diffs, files, links,
   and optional timeline events.
2. Optionally suppress routine PR families before clustering, for example
   post-release churn or version-bump maintenance PRs.
3. Build artifact features for issues and PRs from:
   - titles and bodies
   - comment and review activity
   - explicit issue targets
   - filenames, diff size, and diff previews
4. Build explicit link evidence from:
   - stored link rows
   - text-derived references found in issue, PR, comment, and review bodies
5. Generate hard and soft candidate pairs:
   - issue hard pairs from explicit duplicate evidence
   - issue soft pairs from BM25 text similarity
   - PR soft pairs from BM25 text similarity
   - PR soft pairs from shared explicit issue targets
6. Decide which soft pairs to keep:
   - deterministic mode keeps only heuristic accepts
   - hybrid mode reviews bounded candidate packets with an LLM and keeps or
     rejects soft pairs based on the analyst result
7. Build issue clusters and PR clusters from connected components of the
   accepted graph.
8. Attach PR clusters to issue anchors when they clearly converge on the same
   target issue.
9. Rank the resulting meta-bug clusters and emit:
   - `meta_bugs`
   - `duplicate_issues`
   - `duplicate_prs`
   - `best_issue`
   - `best_pr`

## Feature construction

For each issue, the analysis computes features such as:

- tokenized title + body
- title token set
- title/body lengths
- discussion activity
- inbound reference count

For each PR, the analysis computes features such as:

- tokenized title + cleaned body
- title token set
- discussion + review activity
- explicit linked issue targets
- diff size
- touched filenames
- diff preview
- patch-derived tokens and ranges

The PR body cleanup step is configurable. It can:

- merge repo-specific template rules with the built-in defaults
- replace the defaults entirely
- be disabled

That makes the same clustering logic reusable across repos with different PR
templates.

## Deterministic soft-edge generation

### Issues

Issue soft candidates are generated from BM25 similarity over issue tokens.
Candidates are filtered to require meaningful overlap, and very old pairs need
stronger title agreement.

Issue hard pairs come from explicit duplicate-type evidence such as duplicate
references.

### Pull requests

PR soft candidates come from two sources.

1. **BM25 text similarity**
   - same `base_ref`
   - recent enough in time
   - minimum token-overlap threshold

2. **Shared explicit issue targets**
   - multiple PRs closing or targeting the same issue
   - strengthened by text overlap and shared filenames

Some PR soft pairs are accepted deterministically when the heuristic signal is
already strong enough.

## Hybrid LLM review

Hybrid mode does not replace the deterministic pipeline. It reuses the same
feature extraction and candidate generation, then reviews ambiguous soft edges.

For each of the two domains, issues first and PRs second:

1. Build a candidate graph from:
   - hard pairs
   - all soft candidates
2. Split that graph into connected components.
3. Package each component into a structured review packet containing:
   - nodes
   - per-node summaries
   - pair evidence
   - soft pairs to judge
4. Estimate packet size and:
   - split oversized packets with token-aware soft-pair batching
   - trim filenames and diff previews
   - skip packets that still exceed budget
5. Reuse cached review results when available.
6. Otherwise call the analyst model, and sometimes an evaluator model, to
   decide which soft pairs to keep.

Hybrid review concurrency is bounded by `hybrid_llm_concurrency`:

- `1` minimizes provider pressure
- higher values allow independent review units to run in parallel
- issue and PR review passes share the same concurrency budget
- cache hits still bypass provider calls

The LLM is therefore reviewing a bounded deterministic candidate set, not
inventing clusters from scratch.

## Why issue anchors matter

The final output is not just a bag of connected components.

Issue clusters become preferred anchors. PR clusters are then attached to those
anchors when their explicit target issues concentrate strongly enough on one
issue-centered bucket. This keeps the final output issue-centered when the
evidence supports that shape.

Clusters that cannot be attached to an issue anchor can still survive as PR-only
clusters.

## Output

The analysis report contains:

- ranked `meta_bugs`
- duplicate issue records
- duplicate PR records
- best issue / best PR selections
- confidence, summary, and canonical-reason fields per cluster

In hybrid mode, the run may also write `analysis-report.llm-reviews.json`
containing the structured soft-edge review records.

## Intended use

Use these clusters for:

- duplicate issue triage
- duplicate or competing PR detection
- identifying issue-centered bursts of related work
- surfacing the best current issue or PR representative

Do not treat soft-similarity edges as ground truth without checking the evidence
mix. The algorithm is designed to be conservative, especially in deterministic
mode, but it still benefits from human review on borderline cases.
