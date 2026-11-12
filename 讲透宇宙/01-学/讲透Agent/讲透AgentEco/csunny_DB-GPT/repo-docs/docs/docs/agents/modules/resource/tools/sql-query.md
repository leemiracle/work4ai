# sql_query

## Overview

`sql_query` executes a read-only SQL query against the selected database.

It is the fastest way to inspect structured data before deeper analysis.

## Parameters

```json
{
  "sql": "SELECT statement"
}
```

## What it does

- executes safe read-only SQL
- formats the result as markdown table output
- truncates large results to the first 50 rows

## When to use it

- inspect schemas and sample rows
- answer business questions from structured data
- fetch data before Python analysis

## Example

```json
{
  "sql": "SELECT product_category, SUM(revenue) AS total_revenue FROM sales GROUP BY product_category ORDER BY total_revenue DESC"
}
```

## Notes

- only read operations are allowed
- statements like `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, and `CREATE` are blocked
- use it for retrieval, not mutation
