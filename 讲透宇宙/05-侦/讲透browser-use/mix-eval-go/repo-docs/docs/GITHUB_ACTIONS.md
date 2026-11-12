# GitHub Actions Integration

Mix-Eval-Go includes a GitHub Actions workflow that integrates with the evaluation-platform for automated, distributed evaluations.

## How It Works

1. **Evaluation-platform** triggers evaluation via GitHub API dispatch
2. **GitHub Actions** spawns runner jobs with parameters
3. **mix-eval-go** executes tasks and posts results back to Convex
4. **Platform UI** displays real-time results

## Setup

### 1. Add Repository Secrets

In GitHub Settings → Secrets and variables → Actions, add:

```
CONVEX_URL
CONVEX_SECRET_KEY
ANTHROPIC_API_KEY
BROWSERBASE_API_KEY
BROWSERBASE_PROJECT_ID
BRIGHTDATA_USER
BRIGHTDATA_PASS
# ... other browser provider API keys
```

### 2. Automatic Triggers

The evaluation-platform will automatically dispatch workflows when you start a run.

### 3. Monitor Progress

- **GitHub Actions**: `https://github.com/your-org/mix-eval-go/actions`
- **Evaluation Platform UI**: Real-time task results

## Manual Trigger (Testing)

For manual testing, you can trigger workflows using the GitHub API:

```bash
gh api repos/your-org/mix-eval-go/dispatches \
  -X POST \
  -F event_type=run-eval \
  -F client_payload='{"ref":"main","script_args":{"dataset":"PostHog_Cleaned_020226","run_id":"test-123","start_index":0,"end_index":9}}'
```

**Note**: Use `dataset` parameter (not `test_case`) with updated CLI syntax.
