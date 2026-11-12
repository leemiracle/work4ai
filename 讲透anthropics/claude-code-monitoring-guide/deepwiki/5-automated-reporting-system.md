<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-code-monitoring-guide · page 5 Automated Reporting System · fetched 2026-10-26 -->

# Automated Reporting System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [report-generation-prompt.md](report-generation-prompt.md)
- [sample-report-output.md](sample-report-output.md)

</details>



## Purpose and Scope

The Automated Reporting System combines Claude Code usage metrics from Prometheus with project management data from Linear to generate comprehensive ROI and productivity reports. This system uses the Claude CLI with MCP (Model Context Protocol) integration to create automated, data-driven reports that analyze AI coding tool effectiveness and team productivity.

For real-time monitoring and visualization, see [Monitoring and Visualization](#4). For details on telemetry data collection, see [Telemetry Collection Pipeline](#3).

## System Architecture

The Automated Reporting System operates as the analysis and reporting layer of the Claude Code ROI measurement pipeline, consuming data from multiple sources to generate actionable insights.

```mermaid
graph TB
    subgraph "Data Sources"
        PROM["Prometheus API<br/>localhost:9090/api/v1/query"]
        LINEAR["Linear MCP Server<br/>mcp.linear.app/sse"]
        METRICS["Claude Code Telemetry<br/>Sessions, Costs, Tokens"]
    end
    
    subgraph "Report Generation Engine"
        CLI["claude CLI"]
        MCP["Linear MCP Client<br/>npx -y mcp-remote"]
        PROMPT["report-generation-prompt.md<br/>Template Engine"]
    end
    
    subgraph "Report Processing"
        COMBINE["Data Combination Logic"]
        ANALYZE["ROI Analysis Engine"]
        VIZ["Mermaid Diagram Generation"]
    end
    
    subgraph "Output Artifacts"
        MD["Markdown Reports<br/>sample-report-output.md"]
        CHARTS["Mermaid Visualizations<br/>Pie, Bar, Gantt Charts"]
        INSIGHTS["Actionable Recommendations"]
    end
    
    PROM -->|"HTTP GET /query"| CLI
    LINEAR -->|"SSE Stream"| MCP
    METRICS -->|"JSON Payload"| PROMPT
    
    CLI --> COMBINE
    MCP --> COMBINE
    PROMPT --> COMBINE
    
    COMBINE --> ANALYZE
    ANALYZE --> VIZ
    VIZ --> MD
    VIZ --> CHARTS
    ANALYZE --> INSIGHTS
```

Sources: [report-generation-prompt.md:1-81](), [sample-report-output.md:1-158]()

## Data Sources and Integration Points

The reporting system integrates three primary data sources to provide comprehensive analysis capabilities.

### Prometheus Metrics API Integration

The system queries Prometheus for Claude Code telemetry data using HTTP API calls to extract usage patterns and cost metrics.

```mermaid
sequenceDiagram
    participant SCRIPT as "weekly-report.sh"
    participant PROM as "Prometheus API<br/>:9090"
    participant CLAUDE as "claude CLI"
    participant REPORT as "Report Generator"
    
    SCRIPT->>PROM: "GET /api/v1/query?query=claude_code_sessions"
    PROM-->>SCRIPT: "JSON metrics response"
    SCRIPT->>PROM: "GET /api/v1/query?query=claude_code_cost_total"
    PROM-->>SCRIPT: "Cost data"
    SCRIPT->>CLAUDE: "claude -p 'report prompt with $METRICS'"
    CLAUDE->>REPORT: "Process metrics JSON payload"
    REPORT-->>SCRIPT: "Generated markdown report"
```

Sources: [report-generation-prompt.md:76-81]()

### Linear MCP Integration

The system uses Linear's MCP server to fetch real-time project management data including issue velocity, sprint metrics, and team productivity indicators.

| Integration Component | Configuration | Purpose |
|----------------------|---------------|---------|
| MCP Server | `mcp.linear.app/sse` | Linear API access via SSE |
| Client Command | `claude mcp add linear -s user -- npx -y mcp-remote` | MCP registration |
| Data Stream | Server-Sent Events | Real-time project updates |

Sources: [report-generation-prompt.md:7-10]()

## Report Generation Process

The report generation process combines the Claude CLI with structured prompts to create comprehensive productivity analyses.

### Command Structure and Data Flow

```mermaid
flowchart TD
    subgraph "Input Data Preparation"
        JSON["Metrics JSON Object<br/>claude_code_sessions<br/>total_cost<br/>token_usage<br/>tool_usage"]
        PROMPT_TEMPLATE["report-generation-prompt.md<br/>Template Structure"]
    end
    
    subgraph "Claude CLI Execution"
        CMD["claude -p command"]
        LINEAR_MCP["Linear MCP Integration<br/>npx -y mcp-remote"]
        PROCESSING["AI Analysis Engine"]
    end
    
    subgraph "Report Generation Logic"
        VELOCITY["Velocity Analysis<br/>Before/After Comparison"]
        COST_ANALYSIS["Cost Analysis<br/>Per Issue, Per User"]
        INSIGHTS["Pattern Recognition<br/>Tool Usage Optimization"]
        VISUALIZATIONS["Mermaid Diagram Creation<br/>Pie, Bar, Gantt Charts"]
    end
    
    subgraph "Output Generation"
        MARKDOWN["sample-report-output.md<br/>Structured Report"]
        RECOMMENDATIONS["Actionable Insights<br/>Training Suggestions"]
    end
    
    JSON --> CMD
    PROMPT_TEMPLATE --> CMD
    CMD --> LINEAR_MCP
    CMD --> PROCESSING
    
    PROCESSING --> VELOCITY
    PROCESSING --> COST_ANALYSIS
    PROCESSING --> INSIGHTS
    PROCESSING --> VISUALIZATIONS
    
    VELOCITY --> MARKDOWN
    COST_ANALYSIS --> MARKDOWN
    INSIGHTS --> RECOMMENDATIONS
    VISUALIZATIONS --> MARKDOWN
```

Sources: [report-generation-prompt.md:14-54](), [sample-report-output.md:1-158]()

### Metrics Data Structure

The system processes structured JSON metrics that include session data, cost attribution, and tool usage patterns:

```json
{
  "claude_code_sessions": 42,
  "total_cost": 103.45,
  "pull_requests": 23,
  "avg_session_duration": "28.5 minutes",
  "tool_usage": {
    "Edit": 356,
    "MultiEdit": 128,
    "Write": 73,
    "Read": 892,
    "Bash": 204
  },
  "tool_acceptance_rates": {
    "Edit": 0.81,
    "MultiEdit": 0.92,
    "Write": 0.65
  }
}
```

Sources: [report-generation-prompt.md:17-42]()

## Report Structure and Content

Generated reports follow a standardized structure that combines quantitative metrics with qualitative analysis and actionable recommendations.

### Report Sections and Components

| Section | Content Type | Data Sources |
|---------|-------------|--------------|
| Executive Summary | Velocity improvements, cost overview | Linear + Prometheus |
| Usage Metrics | Tool distribution, acceptance rates | Claude Code telemetry |
| Linear Integration Metrics | Issue completion, team velocity | Linear MCP |
| Cost Analysis | Token usage, cost per issue | Prometheus cost metrics |
| Actionable Insights | Usage patterns, optimization opportunities | Combined analysis |
| Recommendations | Training suggestions, process improvements | AI-generated insights |

Sources: [sample-report-output.md:7-131]()

### Visualization Generation

The system automatically generates Mermaid diagrams for data visualization:

```mermaid
graph LR
    subgraph "Chart Types"
        PIE["Pie Charts<br/>Tool Usage Distribution<br/>Token Usage Split"]
        BAR["Bar Charts<br/>Before/After Comparisons<br/>Feature Implementation Time"]
        GANTT["Gantt Charts<br/>Session Duration Distribution"]
        FLOWCHART["Flowcharts<br/>Productivity Comparisons"]
    end
    
    subgraph "Data Mapping"
        TOOLS["tool_usage JSON"] --> PIE
        VELOCITY["velocity metrics"] --> BAR
        SESSIONS["session_duration data"] --> GANTT
        COMPARISON["before/after data"] --> FLOWCHART
    end
    
    subgraph "Generated Output"
        MERMAID_CODE["Mermaid Code Blocks<br/>in Markdown"]
    end
    
    PIE --> MERMAID_CODE
    BAR --> MERMAID_CODE
    GANTT --> MERMAID_CODE
    FLOWCHART --> MERMAID_CODE
```

Sources: [sample-report-output.md:15-154]()

## Automation and Scheduling

The system supports automated report generation through shell scripts and cron jobs for regular ROI analysis.

### Automated Script Structure

The `weekly-report.sh` script demonstrates the automation pattern for regular report generation:

```bash
#!/bin/bash
# Gather metrics from Prometheus
METRICS=$(curl -s "http://localhost:9090/api/v1/query?query=..." | jq '...')

# Generate report
claude -p "Using the Linear MCP, analyze our team's velocity... $METRICS ..."
```

Sources: [report-generation-prompt.md:72-81]()

### Integration Points for Automation

```mermaid
graph TB
    subgraph "Scheduling Infrastructure"
        CRON["Cron Jobs<br/>weekly-report.sh"]
        CI_CD["CI/CD Pipelines<br/>Automated Triggers"]
    end
    
    subgraph "Data Collection"
        PROM_QUERY["curl prometheus API<br/>localhost:9090/api/v1/query"]
        JQ_PARSE["jq JSON processing<br/>Metrics extraction"]
    end
    
    subgraph "Report Execution"
        CLAUDE_CMD["claude CLI execution<br/>-p prompt flag"]
        LINEAR_INTEGRATION["Linear MCP connection<br/>Real-time project data"]
    end
    
    subgraph "Output Management"
        FILE_OUTPUT["Markdown file generation<br/>Timestamped reports"]
        NOTIFICATION["Team notifications<br/>Report delivery"]
    end
    
    CRON --> PROM_QUERY
    CI_CD --> PROM_QUERY
    PROM_QUERY --> JQ_PARSE
    JQ_PARSE --> CLAUDE_CMD
    CLAUDE_CMD --> LINEAR_INTEGRATION
    LINEAR_INTEGRATION --> FILE_OUTPUT
    FILE_OUTPUT --> NOTIFICATION
```

Sources: [report-generation-prompt.md:70-81]()

---

