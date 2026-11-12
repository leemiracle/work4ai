# PR scope clustering

`slop_farmer.pr_scope` clusters open pull requests that look similar in code
scope and touched areas.

This is intentionally softer than duplicate-PR detection. The goal is to group
open PRs that likely belong to the same subsystem or review bucket, even when
they do not touch the exact same file list.

## Inputs

The module uses data the pipeline already materializes:

- `pull_requests.parquet`
- `pr_files.parquet`

The public entrypoints are:

- `build_pr_scope_clusters(pull_requests, pr_files)`
- `build_pr_scope_clusters_from_snapshot(snapshot)`
- `run_pr_scope_report(options)`

There is also a CLI command:

```bash
uv run slop-farmer pr-scope \
  --snapshot-dir data/snapshots/20260324T150154Z
```

By default that writes `pr-scope-clusters.json` next to the snapshot.

## Algorithm

For each open, non-draft PR:

1. Build a sparse scope vector from:
   - exact filenames
   - directory prefixes
   - coarse file chunks inferred from unified-diff hunk headers
2. Weight features by inverse PR frequency across the current open queue.
   Common files and directories therefore contribute less than rare ones.
3. Compute pairwise similarity from:
   - weighted content cosine similarity
   - size similarity
   - breadth similarity
   - concentration similarity
4. Build a mutual k-nearest-neighbor graph from those scores.
5. Keep only strong edges or edges with local neighbor support.
6. Split graph components greedily around local medoids to avoid long,
   weakly-connected chains.

The output is a list of `PrScopeCluster` objects with:

- clustered PR numbers
- a representative PR number
- average similarity
- shared filenames
- shared directories
- pairwise similarity breakdowns within the cluster

## Why this is holistic

Raw pairwise Jaccard treats every shared file equally. This approach uses the
whole open queue at once:

- common files get downweighted
- directory-level overlap can connect related PRs even without exact file match
- cluster edges depend on each PR's neighborhood, not only a single threshold

## Intended use

Use these clusters for:

- similar-review routing
- finding competing implementations in the same area
- spotting bursts of work in one subsystem

Do not treat them as strict duplicate evidence without additional checks.
