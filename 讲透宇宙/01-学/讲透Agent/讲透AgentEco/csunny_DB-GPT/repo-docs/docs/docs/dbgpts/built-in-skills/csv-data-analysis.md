# csv-data-analysis

## Overview

`csv-data-analysis` is a built-in deep analysis skill for CSV, Excel, and TSV files.

It combines statistical extraction, anomaly discovery, chart-ready structured data, and HTML report generation.

## Repo path

```text
skills/csv-data-analysis/
├── SKILL.md
├── scripts/
│   └── csv_analyzer.py
├── references/
│   └── reference.md
└── templates/
    └── report_template.html
```

## When to use it

- analyze uploaded CSV files
- analyze Excel workbooks
- compute statistics and detect anomalies
- generate polished interactive analysis reports

## Core workflow

1. Run `scripts/csv_analyzer.py` with `execute_skill_script_file`.
2. Read the returned statistical summary.
3. Use `html_interpreter` with `csv-data-analysis/templates/report_template.html`.
4. Fill the required textual placeholders only.
5. Let the backend inject chart marker data automatically.

## Important resources

| Resource | Purpose |
|---|---|
| `scripts/csv_analyzer.py` | Extracts statistics, quality signals, and chart marker data |
| `references/reference.md` | Supplemental usage guidance for the skill |
| `templates/report_template.html` | Final interactive report template |

## Output expectations

This skill is designed to produce a report with:

- executive summary
- data quality review
- distribution analysis
- correlation analysis
- categorical and structural analysis
- anomaly overview
- conclusions and recommendations

## Notes

The template is part of the skill contract. The agent should use the bundled HTML template instead of hand-writing report rendering logic.
