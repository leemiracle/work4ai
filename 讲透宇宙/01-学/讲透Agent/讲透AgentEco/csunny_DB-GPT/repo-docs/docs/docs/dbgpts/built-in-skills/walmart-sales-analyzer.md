# walmart-sales-analyzer

## Overview

`walmart-sales-analyzer` is a built-in analysis skill for Walmart sales datasets.

It focuses on trends between weekly sales and unemployment rates, then packages the findings into a business-facing HTML report.

## Repo path

```text
skills/walmart-sales-analyzer/
├── SKILL.md
├── scripts/
│   ├── generate_html_report.py
│   ├── generate_correlation_heatmap.py
│   ├── generate_sales_unemployment_scatter.py
│   ├── generate_time_series_trend.py
│   ├── generate_store_avg_comparison.py
│   └── font_setup.py
└── templates/
    └── report_template.html
```

## When to use it

- analyze Walmart sales CSV data
- explore sales vs unemployment relationships
- generate comparison charts and trends
- render a polished business HTML report

## Core workflow

1. Validate that the uploaded file contains Walmart sales data.
2. Run `generate_html_report.py` or the related chart scripts.
3. Pass the analysis text and titles into `html_interpreter`.
4. Render the final report with the bundled template.

## Important resources

| Resource | Purpose |
|---|---|
| `scripts/generate_html_report.py` | End-to-end report generation entry point |
| `scripts/generate_correlation_heatmap.py` | Correlation analysis chart |
| `scripts/generate_sales_unemployment_scatter.py` | Sales vs unemployment regression chart |
| `scripts/generate_time_series_trend.py` | Store trend tracking |
| `scripts/generate_store_avg_comparison.py` | Average store comparison |
| `templates/report_template.html` | Final responsive report template |

## Output expectations

This skill emphasizes:

- visual trend explanation
- business interpretation
- regional and store comparison
- executive summary and recommendations
