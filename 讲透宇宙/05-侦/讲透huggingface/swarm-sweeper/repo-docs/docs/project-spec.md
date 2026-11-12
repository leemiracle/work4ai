# Transformers PR De-slopping: Data Pipeline Spec

## Summary

This project exists to reduce review load on the `huggingface/transformers` repository by turning a noisy stream of issues and pull requests into a smaller set of high-signal candidate contributions. The working assumption is that many low-quality contributions are partially or heavily agent-generated, but the operational problem is broader than "AI vs human". The actual problem is that maintainers receive too many low-signal issues and PRs to triage manually, and the volume is growing.

The long-term approach is aggregative rather than purely classificatory. Instead of trying to decide whether each PR is "slop" in isolation, the system should identify clusters of duplicated or overlapping work, estimate the core underlying contribution or bug report those clusters are about, and rank the candidate issue/PR artifacts by a humanity-oriented prior and other quality signals. The desired end state is a short list of high-signal PRs worth human attention.

The immediate implementation goal is narrower: build a reproducible data processing pipeline that scrapes `huggingface/transformers` issues and pull requests from GitHub, normalizes the data into stable schemas, derives only lightweight linkage metadata, and publishes versioned snapshot datasets to the Hugging Face Hub. This v1 dataset is intended primarily for evaluation and manual analysis, while preserving enough provenance and text to support future training workflows.

## Problem Statement

`huggingface/transformers` is receiving a rising volume of low-signal issues and PRs. Many of these contributions appear to be generated or heavily assisted by long-horizon coding agents, often with little meaningful human review before submission. Some come from fully autonomous agent workflows; others likely come from genuine contributors using coding agents poorly. In both cases, maintainers still face the same triage problem:

- duplicated fixes for the same issue
- PRs targeting stale or already-addressed bugs
- verbose but low-quality change sets
- issue/PR descriptions that look polished but do not reflect real understanding
- wasted reviewer effort on work that should never have reached deep review

Several heuristics have been discussed internally, including account age, writing style, over-explanation, excessive work for a simple fix, targeting old issues, lack of awareness of existing PRs, and suspiciously polished commentary. Those signals are useful, but they are not sufficient on their own and they are not reliable enough to hard-code as a binary moderation rule. Some legitimate contributors will look suspicious on one or more of those dimensions, especially when they use LLMs to improve English phrasing.

This project therefore treats the moderation problem as an aggregation and ranking problem. The system should surface the likely core contribution in a cluster of duplicated or overlapping issues/PRs, then rank candidate artifacts by their likelihood of being the most human-grounded and review-worthy submission.

## Product Thesis

The key thesis is:

1. The most problematic low-quality contributions are not just "bad PRs"; they are often redundant or weak attempts at the same underlying problem.
2. Looking at contributions individually throws away useful structure, especially duplication, timing, reference patterns, and author behavior.
3. A provenance-rich dataset of issues, PRs, comments, reviews, and linkage events is the prerequisite for meaningful evaluation.
4. The first useful artifact is therefore not a model, but a high-quality dataset and pipeline that allow later work on deduplication, ranking, and evaluation.

This framing keeps the v1 work measurable. Before building ranking systems, moderation policies, or model-based filters, the project needs a stable corpus that captures enough repository history and metadata to support:

- manual inspection of duplicate contribution clusters
- creation of annotation sets
- evaluation of clustering and ranking systems
- later training data curation, if that becomes useful

## End Goal

The end goal is to produce a short list of high-signal PRs for maintainers by:

- identifying duplicated or overlapping issue/PR clusters
- estimating the core contribution or bug report those artifacts are about
- ranking issues and PRs by a humanity-oriented prior and related review-worthiness signals
- routing only the highest-signal artifacts to human review workflows

This project should be shareable with the open-source community to the extent that doing so does not compromise effectiveness. It should prefer open models and Hugging Face infrastructure where practical.

## Non-Goals For V1

The first implementation should not do any of the following:

- assign a final humanity score
- perform model-based slop detection
- auto-close PRs or issues
- implement moderation or access-control actions
- define production reviewer workflows
- optimize the dataset for direct training consumption
- collect every possible training signal immediately

V1 is a data foundation, not a classifier or enforcement system.

## Immediate Goal

Build a GitHub-to-Hub data processing pipeline for `huggingface/transformers` that:

- extracts issues, PRs, comments, reviews, and review comments from GitHub
- preserves enough metadata to reconstruct relationships between artifacts
- normalizes records into stable tabular schemas
- derives a small number of lightweight linkage features
- publishes periodic snapshot datasets to the Hugging Face Hub
- supports incremental refreshes without duplicating records

## Source Context

The motivating context from internal discussion is worth preserving because it shapes the dataset requirements:

- maintainers report that the volume of slop PRs is increasing quickly
- many suspicious PRs display strong stylistic tells, but those are noisy signals
- duplicate PRs on the same issue are common and operationally important
- old issues attract opportunistic agent-generated fixes
- some low-quality contributors are real humans using agents poorly, so a simple anti-bot framing is too narrow
- quality control matters more than coarse contributor restrictions
- any eventual solution should minimize collateral damage to genuine contributors

These observations imply that the dataset should preserve:

- raw text
- review and discussion context
- temporal ordering
- issue/PR linkage
- author-level metadata available from GitHub
- enough provenance to manually inspect why a contribution looked suspicious or useful

## V1 Pipeline Scope

The v1 pipeline will ingest repository data from GitHub for `huggingface/transformers` and publish normalized snapshots to the Hugging Face Hub.

### Entities To Ingest

- issues
- pull requests
- issue comments
- pull request reviews
- pull request review comments
- labels attached to issues and PRs
- author metadata available in top-level GitHub responses
- timestamps, state, and closure/merge metadata
- issue and PR cross-references when available
- timeline or event/linkage signals needed later for duplicate detection and contribution grouping

### Required Metadata

Each entity family should preserve, where applicable:

- GitHub numeric ID
- GitHub node ID
- repository owner and name
- issue or PR number
- URL and API URL
- title and body text
- author login, user ID, and type
- created, updated, closed, merged timestamps
- state and state reason
- labels and assignees
- linked issue or PR references extracted from text or event data
- review decision or review state
- comment positions and file paths for review comments
- crawl metadata such as snapshot date and extraction timestamp

### Pipeline Stages

The implementation should be structured in five stages.

#### 1. Extract

Use the GitHub API to fetch data for `huggingface/transformers`. The extractor should support:

- full historical bootstrap
- incremental sync based on `updated_at` or equivalent stable change markers
- pagination and retry handling
- authenticated access to avoid low rate limits
- persistent run metadata so refreshes are reproducible

The extractor should gather both top-level issue/PR records and the attached conversational/review data needed for later evaluation.

#### 2. Normalize

Normalize the raw GitHub payloads into stable record schemas suitable for tabular storage. The normalization layer should:

- flatten nested structures where useful
- preserve raw text fields
- standardize timestamp formats
- maintain explicit foreign keys between entity tables
- separate issue and PR records into distinct datasets, even though GitHub models PRs as issues internally
- retain provenance fields so any normalized row can be traced back to its source artifact

#### 3. Derive Lightweight Linkage Features

Only lightweight, transparent derived features should be created in v1. Examples:

- issue-to-PR references extracted from text or API fields
- PR-to-issue closing references
- candidate duplicate-link edges from shared issue targets or overlapping references
- account age at time of issue/PR creation when available from GitHub user metadata
- body length, title length, comment count, and review count
- temporal ordering features such as first-seen and relative submission timing

The derivation stage should not implement clustering, scoring, moderation decisions, or opaque model features.

#### 4. Publish

Publish versioned snapshots to a Hugging Face Hub dataset repository. Each snapshot should:

- contain Parquet-backed normalized tables
- include enough metadata to reproduce the crawl
- be documented by a dataset card
- be easy to load for manual analysis, evaluation, and future curation

#### 5. Refresh Incrementally

The pipeline should support recurring refresh runs that:

- fetch newly created or updated records
- upsert without duplicate GitHub IDs
- emit a new snapshot version
- preserve a clear boundary between source-of-truth records and lightweight derived features

## Dataset Design

The Hub output should be a snapshot-style dataset rather than a training-packed corpus.

### Snapshot Format

Each publish should create a versioned snapshot, ideally one logical snapshot per run, backed by Parquet files. The snapshot should be appendable over time and re-runnable from source without requiring manual repair.

### Logical Tables

At minimum, the dataset should expose these normalized tables or splits:

- `issues`
- `pull_requests`
- `comments`
- `reviews`
- `review_comments`
- `links` or `events` for extracted references and timeline/linkage records

If implementation convenience requires separate issue comments and PR comments internally, that is acceptable, but the public dataset should remain clear and stable.

### Minimum Table Semantics

#### `issues`

One row per GitHub issue that is not a pull request. Include identifiers, title/body, author, labels, timestamps, state, comment counts, and provenance.

#### `pull_requests`

One row per pull request. Include identifiers, title/body, author, labels, timestamps, merge status, draft status, linked issue references if available, and provenance.

#### `comments`

One row per issue or PR discussion comment. Include parent artifact identifiers, author, body, timestamps, and provenance.

#### `reviews`

One row per PR review. Include PR identifiers, reviewer, state, submitted timestamp, body, and provenance.

#### `review_comments`

One row per inline PR review comment. Include PR identifiers, review identifiers, file path, diff position metadata when available, author, body, timestamps, and provenance.

#### `links` or `events`

One row per extracted or observed linkage signal, such as:

- PR references issue
- PR closes issue
- issue mentions PR
- two PRs target the same issue
- timeline event indicating cross-reference or state transition

These rows should make it easy to reconstruct candidate duplicate clusters later without rescanning all raw text.

### Stable IDs And Provenance

Every table should include:

- stable GitHub IDs
- repository identifier
- snapshot version
- extraction timestamp
- source API endpoint or source type

The normalized data should be traceable back to the raw GitHub artifact even if raw payload blobs are not published in full.

### Lightweight Derived Fields

Include only fields that support evaluation and manual review directly. Recommended derived fields:

- extracted issue and PR references
- normalized counts for comments, reviews, and review comments
- text presence flags and text length metrics
- account age at submission time, if user metadata is available
- relative ordering features such as "days since issue opened" or "PR order for linked issue"

Do not add speculative labels such as `is_slop`, `is_human`, or `is_duplicate_cluster_best` in v1.

### Text Preservation

Raw textual content should be preserved wherever available:

- issue titles and bodies
- PR titles and bodies
- issue comments
- PR reviews
- PR review comments

Text should be stored in a form that remains suitable for downstream model evaluation and later annotation.

## Dataset Publishing Expectations

The published dataset should behave like a reproducible data product.

### Hub Publishing Requirements

- publish to a Hugging Face dataset repository owned by the team or org
- use versioned snapshots rather than silently mutating a single undifferentiated dump
- provide a dataset card with provenance, intended use, limitations, and refresh policy
- document that scores and labels are not yet ground truth
- make it straightforward to load the dataset from `datasets`

### Dataset Card Requirements

The dataset card should describe:

- source repository: `huggingface/transformers`
- collection method and APIs used
- entity coverage
- known blind spots or missing metadata
- intended uses for evaluation and manual review
- non-intended uses, especially direct automated moderation
- privacy and attribution considerations

### Incremental Update Requirements

The pipeline must be re-runnable. Each incremental run should:

- discover changed or new records
- avoid duplicate entity rows keyed by GitHub IDs
- produce a new snapshot version or revision
- keep the published dataset consistent enough for downstream consumers to compare snapshots

## How V1 Supports Later Phases

The v1 dataset is a foundation for later work, not the final system.

### Evaluation

The dataset should support future benchmarks for:

- duplicate-PR grouping
- core-contribution identification
- humanity-score or review-worthiness ranking
- maintainers' manual triage simulation on sampled clusters

### Training Later

The same dataset can later be extended into training corpora, but that is a separate phase. Training-oriented curation, labeling, example packing, and negative sampling should be deferred until the raw dataset quality is validated.

### Manual Review Set Creation

The dataset should make it easy to sample:

- multiple PRs that target the same issue
- suspicious PRs against stale issues
- issue/PR groups with rich review discussion
- contrasting examples where polished writing does and does not correlate with contribution quality

These sample sets will be useful for annotation and for defining measurable evaluation tasks.

## Public Interfaces And Outputs

The v1 implementation should expose these interfaces clearly.

### Input

- GitHub repository: `huggingface/transformers`
- authenticated GitHub API access for repository metadata, issues, PRs, reviews, comments, and relevant events

### Primary Output

- a Hugging Face Hub dataset repository containing normalized snapshot tables for issues, PRs, comments, reviews, review comments, and linkage/event records

### Secondary Output

- pipeline run metadata including crawl time, source API version assumptions, snapshot version, and extraction provenance

### Explicitly Out Of Scope

- no user-facing moderation API
- no production classifier service
- no automatic PR closure or reviewer assignment logic

## Suggested Implementation Shape

The code is not part of this document deliverable, but the pipeline should be implemented so that it can later be evaluated and operated cleanly. A reasonable structure is:

- extraction layer for GitHub API reads
- normalization layer that writes typed intermediate tables
- feature derivation layer for transparent linkage fields
- publishing layer for Parquet export and Hub upload
- run manifest or metadata layer for snapshot bookkeeping

This keeps future evaluation code separate from raw data collection.

## Test Plan

The implementation based on this spec should satisfy the following checks.

### End-To-End Scrape

- a full scrape of `huggingface/transformers` completes successfully
- all expected entity tables are written
- row counts are non-zero for expected high-volume tables

### Idempotency

- re-running the same scrape does not create duplicate rows for the same GitHub IDs
- repeated normalization preserves stable primary keys and foreign keys

### Incremental Refresh

- an incremental run after the initial scrape picks up newly created or updated issues and PRs
- unchanged historical records are not duplicated
- refresh metadata records what window or cursor was used

### Relationship Preservation

- PR-to-issue references survive normalization
- review metadata remains attached to the correct PRs
- comment and review-comment parent relationships remain intact

### Hub Usability

- a small sampled slice can be loaded from the published Hub dataset
- a user can inspect candidate duplicate PRs from the published snapshot without needing the raw scraper outputs
- the dataset card documents provenance and known limitations

## Assumptions And Defaults

- the immediate deliverable is a single project spec document
- the first implementation optimizes for evaluation readiness, not direct training readiness
- issues plus PR-adjacent review metadata must be included in v1 because later aggregation depends on both
- derived features remain lightweight and transparent in v1
- the default publish target is a Hugging Face Hub dataset repo owned by the team or org
- future humanity scoring, clustering, moderation policy, and training curation will be implemented as separate layers on top of this dataset

## Near-Term Next Steps

After this document, the next implementation steps should be:

1. scaffold the pipeline repository structure
2. choose the GitHub extraction method and auth setup
3. define concrete schemas for each normalized table
4. implement a historical bootstrap scrape for `huggingface/transformers`
5. publish the first snapshot dataset and dataset card to the Hugging Face Hub

