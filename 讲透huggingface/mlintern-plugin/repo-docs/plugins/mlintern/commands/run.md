---
description: Run an ml-intern task and manage background jobs
argument-hint: '[--model id] [--background|--wait|--status [job-id]|--result [job-id]|--cancel [job-id]] [prompt]'
disable-model-invocation: true
allowed-tools: Bash(node:*)
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/mlintern-companion.mjs" run $ARGUMENTS
```

Return stdout exactly as produced.
