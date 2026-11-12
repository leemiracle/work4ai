# Built-in Skills Overview

DB-GPT ships with built-in skills under the project-level `skills/` directory.

This subsection mirrors the repository structure and gives each built-in skill its own page.

## Repo mapping

```text
skills/
├── agent-browser/
├── csv-data-analysis/
├── financial-report-analyzer/
├── skill-creator/
└── walmart-sales-analyzer/
```

## What built-in skills provide

Built-in skills package repeatable workflows into reusable units.

- `SKILL.md` defines when the skill should be used and how it should work
- `scripts/` contains executable helpers when deterministic processing is needed
- `references/` stores deeper domain guidance that can be loaded on demand
- `templates/` or `assets/` provide output resources such as HTML report templates

## Current built-in skills

| Skill | Primary use | Key bundled resources |
|------|--------------|-----------------------|
| `agent-browser` | Browser automation for agents | command-driven workflow in `SKILL.md` |
| `csv-data-analysis` | CSV / Excel / TSV analysis | `scripts/csv_analyzer.py`, `templates/report_template.html`, `references/reference.md` |
| `financial-report-analyzer` | Financial report extraction and reporting | extraction, ratio, and chart scripts plus financial references and templates |
| `skill-creator` | Creating and packaging new skills | `init_skill.py`, `package_skill.py`, design references |
| `walmart-sales-analyzer` | Walmart sales trend analysis and reporting | report-generation scripts and `templates/report_template.html` |

## How to read this section

Each built-in skill page includes:

- the skill's purpose
- when to use it
- its core workflow
- the important scripts, references, and templates bundled with it
- practical output expectations

## Next step

Open the individual pages in this Built-in Skills section to see how each shipped skill maps to the repository's `skills/` folder.
