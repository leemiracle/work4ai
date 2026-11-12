# skill-creator

## Overview

`skill-creator` is the built-in meta-skill for designing, scaffolding, validating, and packaging new skills.

It is the canonical reference in this repository for how skills should be structured.

## Repo path

```text
skills/skill-creator/
├── SKILL.md
├── scripts/
│   ├── init_skill.py
│   ├── package_skill.py
│   └── quick_validate.py
├── references/
│   ├── workflows.md
│   └── output-patterns.md
└── LICENSE.txt
```

## When to use it

- create a new skill
- improve an existing skill
- decide what belongs in `SKILL.md`, `scripts/`, `references/`, and `assets/`
- validate and package a distributable `.skill` file

## Core workflow it teaches

1. Understand the target use case.
2. Plan reusable scripts, references, and assets.
3. Initialize a skill scaffold.
4. Implement and refine the bundled resources.
5. Write or tighten `SKILL.md`.
6. Validate and package the final skill.

## Important resources

| Resource | Purpose |
|---|---|
| `scripts/init_skill.py` | Creates a new skill scaffold |
| `scripts/package_skill.py` | Packages a skill into a distributable artifact |
| `scripts/quick_validate.py` | Validates skill structure and quality quickly |
| `references/workflows.md` | Guidance for multi-step skill workflow design |
| `references/output-patterns.md` | Guidance for output formats and quality patterns |

## Why it matters

This built-in skill defines the best-practice model for authoring both custom skills and future built-in skills in DB-GPT.
