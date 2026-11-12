You are synthesizing a canonical pull request for duplicate open pull requests in `{{REPO}}`.

Read these staged context files before making any edits:

- Selected cluster metadata: `{{SELECTED_CLUSTER_PATH}}`
- Cluster context summary: `{{CLUSTER_CONTEXT_PATH}}`
- Per-PR context directory: `{{PR_CONTEXT_DIR}}`
- Target issue context: `{{ISSUE_CONTEXT_PATH}}`

Open source PR numbers for this synthesis: `{{SOURCE_PR_NUMBERS}}`
Cluster id: `{{CLUSTER_ID}}`

Constraints:

1. Work only from the open source PRs listed above. Ignore closed or merged PRs even if they appear in the broader cluster metadata.
2. Synthesize a fresh patch against the current checked-out `{{REPO}}:{{DEFAULT_BRANCH}}` worktree state. Do not cherry-pick source branches blindly.
3. Use the staged PR diffs, file lists, comments, reviews, and review comments as evidence. Read files from disk as needed.
4. Produce one clean commit in this worktree if you can produce a valid canonical patch.
5. Keep the patch as small as possible. Prefer implementation changes first, and add only the minimum tests required to validate the fix.
6. {{FILE_POLICY_INSTRUCTION}}
7. Keep comments to the bare minimum required for readability. Remove explanatory churn rather than adding more.
8. Run targeted validation for the files you change. If the most relevant tests fail, do not hide that fact.
9. Do not push, create a fork, or open a pull request. The surrounding Python workflow handles publication deterministically.

When you are done, return JSON that matches the provided output schema. Requirements for the JSON:

- `status` must be `success` or `failed`
- `cluster_id` must be `{{CLUSTER_ID}}`
- `source_pr_numbers` must be a subset of the listed open source PRs and should include only the PRs whose concrete changes are reflected in the synthesized patch
- `commit_message` must match the commit you created when `status=success`
- `pr_title` must be suitable for a ready-for-review pull request against `{{REPO}}:{{DEFAULT_BRANCH}}`
- `tests_run` must list the exact validation commands you executed
- `summary` should be brief and concrete

If you cannot produce a valid canonical patch, return `status="failed"` with a concise explanation in `summary`.
