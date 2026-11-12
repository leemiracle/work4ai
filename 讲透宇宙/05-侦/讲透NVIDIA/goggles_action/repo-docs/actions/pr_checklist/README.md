# PR Checklist Validator

This action validates task list items (checklists) in pull request bodies.

## Behavior

- **Default**: Fails the workflow if any task list item in the PR body remains unchecked
- **With enforcement**: Optionally requires that at least one checklist item exists
- A task is considered resolved when it is either checked (`[x]` or `[X]`) or the **entire** task text is struck through using `~~` markers (partial strikethrough does not resolve the task)

It works seamlessly with pull request templates: any checklist items
that the template populates must be explicitly checked or struck
through before the workflow will pass.

## Inputs

- `PR_BODY`: The pull request description. Defaults to
  `${{ github.event.pull_request.body }}`.

- `ENFORCE_PR_HAS_CHECKLIST`: Enforce that the PR body contains at least one checklist item.
  - Set to `"true"` to require at least one checklist item in the PR body
  - Defaults to `"false"` (backward compatible - PRs without checklists will pass)
  - When enabled, the action will fail if no checklist items are found

## Example Usage

### Basic Usage (Default Behavior)
```yaml
name: 'Validate PR Checklist'
on:
  pull_request:
    # Include `edited` so the job re-runs when the PR description changes
    types: [opened, edited, synchronize]

jobs:
  checklist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: poweiw/goggles_action/actions/pr_checklist@main
```

### With Checklist Enforcement
```yaml
name: 'Validate PR Checklist'
on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  checklist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: poweiw/goggles_action/actions/pr_checklist@main
        with:
          ENFORCE_PR_HAS_CHECKLIST: 'true'
```

## Behavior Examples

### Default Behavior (`ENFORCE_PR_HAS_CHECKLIST: 'false'`)
- ✅ **Pass**: PR with no checklist items
- ✅ **Pass**: PR with all checklist items completed (`[x]`)
- ❌ **Fail**: PR with incomplete checklist items (`[ ]`)

### With Enforcement (`ENFORCE_PR_HAS_CHECKLIST: 'true'`)
- ❌ **Fail**: PR with no checklist items
- ✅ **Pass**: PR with all checklist items completed (`[x]`)
- ❌ **Fail**: PR with incomplete checklist items (`[ ]`)
