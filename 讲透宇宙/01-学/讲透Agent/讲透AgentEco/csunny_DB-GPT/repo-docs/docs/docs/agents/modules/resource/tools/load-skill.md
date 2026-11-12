# load_skill

## Overview

`load_skill` loads the content of a skill, usually the instructions from `SKILL.md`, by skill name and file path.

Use it when the agent should follow a packaged workflow instead of improvising the whole execution process.

## Parameters

```json
{
  "skill_name": "skill name",
  "file_path": "skill file path"
}
```

## What it does

- resolves the skill from the registry
- reads the skill instructions or prompt template
- returns the loaded workflow content back to the agent

## When to use it

- the task matches a reusable skill
- the skill contains curated business logic
- the workflow should be standardized before execution starts

## Example

```json
{
  "skill_name": "financial-report-analyzer",
  "file_path": "skills/financial-report-analyzer/SKILL.md"
}
```

## Notes

- `load_skill` loads instructions; it does not execute the workflow itself
- once loaded, the agent should follow the skill's required tools and steps
