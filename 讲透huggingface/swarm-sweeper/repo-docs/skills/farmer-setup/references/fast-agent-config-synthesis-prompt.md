You are helping generate slop-farmer setup suggestions for the repository `__REPO__`.

You are given deterministic evidence collected from GitHub via the `gh` CLI.

Return a single structured response that matches the provided JSON Schema.

Your job is to:

1. Propose `pull-requests.template_cleanup.section_patterns`
2. Propose `pull-requests.template_cleanup.line_patterns`
3. Propose `pull-requests.cluster_suppression_rules` only when supported by concrete title-pattern evidence
4. Propose **issue cleanup candidates** as advisory only

Important constraints:

- Do not invent unsupported slop-farmer config keys
- PR cleanup is supported
- PR cluster suppression is supported
- Issue cleanup is **not** currently a first-class config setting in slop-farmer, so issue suggestions must be marked `advisory_only: true`
- Prefer narrow regexes over broad ones
- Every non-empty suggestion must include brief evidence
- If evidence is weak, return an empty list
- Keep notes short and repo-specific

Evidence JSON follows.

__EVIDENCE_JSON__
