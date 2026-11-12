---
pretty_name: Transformers PR Slop Dataset
---

# Transformers PR Slop Dataset

Normalized snapshots of issues, pull requests, comments, reviews, and linkage data from `huggingface/transformers`.

Files:
- `issues.parquet`
- `pull_requests.parquet`
- `comments.parquet`
- `reviews.parquet`
- `review_comments.parquet`
- `links.parquet`
- `events.parquet`

Use:
- duplicate PR and issue analysis
- triage and ranking experiments
- eval set creation

Notes:
- updated daily
- built from the public GitHub API
- raw data only; no labels or moderation decisions
