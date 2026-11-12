<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-code-monitoring-guide · page 4 Monitoring and Visualization · fetched 2026-10-26 -->

# Monitoring and Visualization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [grafana/dashboards/working-dashboard.json](grafana/dashboards/working-dashboard.json)
- [grafana/provisioning/dashboards/dashboards.yaml](grafana/provisioning/dashboards/dashboards.yaml)

</details>



This document covers the real-time monitoring and visualization capabilities of the Claude Code ROI measurement system. It explains how to access, interpret, and customize the Grafana dashboards that provide insights into Claude Code usage patterns, costs, and productivity metrics.

For information about setting up the underlying telemetry collection infrastructure, see [Telemetry Collection Pipeline](#3). For details on automated report generation, see [Automated Reporting System](#5).

## Monitoring Infrastructure Overview

The monitoring and visualization system provides real-time insights into Claude Code usage through a Grafana-based dashboard system. The infrastructure automatically provisions dashboards and connects to Prometheus for time-series data visualization.

```mermaid
flowchart TD
    subgraph "Data Sources"
        prometheus["prometheus:9090<br/>Time-Series Database"]
        metrics["claude_code_cost_usage_USD_total<br/>claude_code_token_usage_tokens_total<br/>claude_code_lines_of_code_count_total"]
    end
    
    subgraph "Grafana Infrastructure"
        grafana["grafana:3000<br/>Visualization Server"]
        provisioning["dashboards.yaml<br/>Auto-Provisioning"]
        dashboard["working-dashboard.json<br/>Panel Definitions"]
    end
    
    subgraph "Dashboard Components"
        stats["Stat Panels<br/>Total Cost, Users, Tokens, LOC"]
        charts["Chart Panels<br/>Cost by Model, Token Distribution"]
        tables["Table Panels<br/>Cost by User, LOC by Type"]
    end
    
    prometheus --> grafana
    metrics --> prometheus
    provisioning --> grafana
    dashboard --> grafana
    
    grafana --> stats
    grafana --> charts
    grafana --> tables
```

Sources: [grafana/dashboards/working-dashboard.json:1-647](), [grafana/provisioning/dashboards/dashboards.yaml:1-12]()

## Dashboard Architecture and Components

The system uses a working dashboard that provides comprehensive monitoring of Claude Code usage across multiple dimensions. The dashboard is automatically provisioned and refreshes every 30 seconds to provide near real-time insights.

```mermaid
graph TB
    subgraph "Dashboard Structure"
        dashboard["claude-code-working<br/>Main Dashboard"]
        timerange["Time Range: now-6h to now<br/>Refresh: 30s"]
        datasource["Prometheus Datasource<br/>PBFA97CFB590B2093"]
    end
    
    subgraph "Summary Panels Row 1"
        totalcost["Panel ID: 1<br/>Total Cost (USD)<br/>claude_code_cost_usage_USD_total"]
        activeusers["Panel ID: 2<br/>Active Users Count<br/>count by user_id"]
        totaltokens["Panel ID: 3<br/>Total Tokens<br/>claude_code_token_usage_tokens_total"]
        linesofcode["Panel ID: 4<br/>Lines of Code<br/>claude_code_lines_of_code_count_total"]
    end
    
    subgraph "Distribution Panels Row 2"
        costmodel["Panel ID: 5<br/>Cost by Model (Pie)<br/>sum by model"]
        tokentype["Panel ID: 6<br/>Token Usage by Type (Donut)<br/>sum by type"]
    end
    
    subgraph "Detail Tables Row 3"
        costuser["Panel ID: 7<br/>Cost by User (Table)<br/>Sorted by Total Cost DESC"]
        loctype["Panel ID: 8<br/>LOC by Type (Table)<br/>Grouped by Type"]
    end
    
    dashboard --> timerange
    dashboard --> datasource
    datasource --> totalcost
    datasource --> activeusers
    datasource --> totaltokens
    datasource --> linesofcode
    datasource --> costmodel
    datasource --> tokentype
    datasource --> costuser
    datasource --> loctype
```

Sources: [grafana/dashboards/working-dashboard.json:59-89](), [grafana/dashboards/working-dashboard.json:120-157](), [grafana/dashboards/working-dashboard.json:637-640]()

## Metrics and Visualization Types

The dashboard leverages multiple Claude Code metrics to provide different analytical perspectives. Each visualization type serves specific monitoring and analysis purposes.

### Key Metrics Tracked

| Metric Name | Purpose | Query Pattern | Units |
|-------------|---------|---------------|-------|
| `claude_code_cost_usage_USD_total` | Track spending across users and models | `sum(increase(...[$__range]))` | USD Currency |
| `claude_code_token_usage_tokens_total` | Monitor token consumption by type | `sum by (type)(increase(...))` | Token Count |
| `claude_code_lines_of_code_count_total` | Measure code generation productivity | `sum by (type)(increase(...))` | Line Count |

### Visualization Components

```mermaid
graph LR
    subgraph "Stat Visualizations"
        stat1["Total Cost<br/>currencyUSD unit<br/>lastNotNull calc"]
        stat2["Active Users<br/>count() aggregation<br/>short unit"]
        stat3["Total Tokens<br/>sum() aggregation<br/>short unit"]
        stat4["Lines of Code<br/>sum() aggregation<br/>short unit"]
    end
    
    subgraph "Distribution Charts"
        pie1["Cost by Model<br/>Pie Chart<br/>legend: table placement"]
        pie2["Token Usage by Type<br/>Donut Chart<br/>palette-classic colors"]
    end
    
    subgraph "Detailed Tables"
        table1["Cost by User<br/>Sort by Value DESC<br/>Transform: organize columns"]
        table2["LOC by Type<br/>Group by type label<br/>Rename columns"]
    end
    
    stat1 --> pie1
    stat3 --> pie2
    stat1 --> table1
    stat4 --> table2
```

Sources: [grafana/dashboards/working-dashboard.json:76-87](), [grafana/dashboards/working-dashboard.json:336-348](), [grafana/dashboards/working-dashboard.json:494-507]()

## Query Patterns and Data Aggregation

The dashboard uses specific PromQL query patterns to aggregate Claude Code metrics across different dimensions. Understanding these patterns helps in customizing and extending the monitoring capabilities.

### Core Query Patterns

| Panel Type | Query Pattern | Purpose |
|------------|---------------|---------|
| Total Cost | `sum(increase(claude_code_cost_usage_USD_total[$__range]))` | Aggregate all costs over time range |
| Active Users | `count(count by (user_id)(increase(claude_code_cost_usage_USD_total[$__range]) > 0))` | Count unique users with activity |
| Cost by Model | `sum by (model)(increase(claude_code_cost_usage_USD_total[$__range]))` | Group costs by Claude model |
| Token Distribution | `sum by (type)(increase(claude_code_token_usage_tokens_total[$__range]))` | Breakdown tokens by input/output/cache |

### Table Transformations

The dashboard applies data transformations to improve readability:

```mermaid
flowchart TD
    subgraph "Raw Prometheus Data"
        rawdata["Time, __name__, job, instance<br/>user_id, model, type<br/>Value"]
    end
    
    subgraph "Transform: organize"
        exclude["excludeByName:<br/>Time, __name__, job, instance"]
        rename["renameByName:<br/>user_id → User ID<br/>Value → Total Cost"]
    end
    
    subgraph "Final Table Output"
        clean["User ID | Total Cost<br/>Sorted DESC by cost"]
    end
    
    rawdata --> exclude
    exclude --> rename
    rename --> clean
```

Sources: [grafana/dashboards/working-dashboard.json:510-527](), [grafana/dashboards/working-dashboard.json:606-623]()

## Dashboard Provisioning and Management

The system uses automated dashboard provisioning to ensure consistent deployment and updates. The provisioning configuration allows for version-controlled dashboard management.

### Provisioning Configuration

The dashboard provisioning is configured through [grafana/provisioning/dashboards/dashboards.yaml:1-12]() with the following settings:

| Setting | Value | Purpose |
|---------|--------|---------|
| `name` | `claude-code-dashboards` | Provider identifier |
| `folder` | `Claude Code` | Grafana folder organization |
| `updateIntervalSeconds` | `10` | Check for updates every 10 seconds |
| `allowUiUpdates` | `true` | Enable manual dashboard editing |
| `path` | `/var/lib/grafana/dashboards` | Dashboard JSON file location |

### Dashboard Metadata

```mermaid
graph TB
    subgraph "Dashboard Identity"
        uid["UID: claude-code-working<br/>Title: Claude Code - Working Dashboard"]
        tags["Tags: claude-code, working<br/>Version: 0"]
        schema["Schema Version: 37<br/>Style: dark"]
    end
    
    subgraph "Time Configuration"
        timerange["Default: now-6h to now<br/>Refresh: 30s"]
        timezone["Timezone: (system default)<br/>Week Start: (default)"]
    end
    
    subgraph "Interactive Features"
        editable["editable: true<br/>Live Now: false"]
        templating["Templating: empty list<br/>Variables: none configured"]
    end
    
    uid --> timerange
    tags --> timezone
    schema --> editable
    timerange --> templating
```

Sources: [grafana/dashboards/working-dashboard.json:18-19](), [grafana/dashboards/working-dashboard.json:627-647]()

## Real-time Monitoring Capabilities

The monitoring system provides near real-time visibility into Claude Code usage patterns with automatic refresh capabilities and responsive data updates.

### Refresh and Update Behavior

- **Automatic Refresh**: Every 30 seconds for live monitoring
- **Default Time Range**: Last 6 hours of activity  
- **Query Range Variable**: `$__range` adapts to selected time window
- **Data Freshness**: Depends on Prometheus scrape interval (typically 15 seconds)

### Threshold and Alert Configuration

While the current dashboard focuses on visualization, it includes threshold configurations that can be extended for alerting:

```mermaid
graph TD
    subgraph "Threshold Configuration"
        green["Green Threshold<br/>value: null (default)"]
        red["Red Threshold<br/>value: 80 (warning level)"]
    end
    
    subgraph "Visual Indicators"
        colors["Color Mode: thresholds<br/>Applied to stat panels"]
        units["Unit Formatting<br/>currencyUSD, short"]
    end
    
    subgraph "Future Extensions"
        alerts["Grafana Alerting<br/>(not currently configured)"]
        notifications["Notification Channels<br/>(extensible)"]
    end
    
    green --> colors
    red --> colors
    colors --> alerts
    units --> notifications
```

Sources: [grafana/dashboards/working-dashboard.json:36-50](), [grafana/dashboards/working-dashboard.json:104-116]()

---

