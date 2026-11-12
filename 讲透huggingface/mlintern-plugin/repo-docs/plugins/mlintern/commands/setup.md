---
description: Check whether ml-intern is installed and usable
argument-hint: '[--json]'
disable-model-invocation: true
allowed-tools: Bash(node:*)
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/mlintern-companion.mjs" setup $ARGUMENTS
```

Return stdout exactly as produced.
