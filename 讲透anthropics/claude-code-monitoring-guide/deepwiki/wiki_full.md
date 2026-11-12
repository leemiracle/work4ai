# Page: Claude Code ROI Measurement System Overview

# Claude Code ROI Measurement System Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [claude_code_roi_full.md](claude_code_roi_full.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the Claude Code ROI Measurement System, which collects telemetry data from Claude Code CLI usage, processes it through an observability pipeline, and generates automated reports to measure developer productivity and return on investment. The system combines Claude Code usage metrics with project management data to provide data-driven insights for engineering leadership.

For detailed installation procedures, see [Installation and Setup](#2). For specific telemetry configuration, see [Telemetry Collection Pipeline](#3). For report generation and Linear integration, see [Automated Reporting System](#5).

## System Architecture Overview

The Claude Code ROI Measurement System consists of four primary subsystems that work together to provide comprehensive usage analytics and ROI measurement capabilities.

**System Architecture**

```mermaid
graph TB
    subgraph "Claude Code Telemetry Sources"
        CC["claude CLI"] 
        CCT["CLAUDE_CODE_ENABLE_TELEMETRY=1"]
        CCM["claude_code.cost.usage<br/>claude_code.token.usage<br/>claude_code.session.count"]
    end
    
    subgraph "Collection Pipeline"
        OC["otel-collector<br/>Port 4317 gRPC<br/>Port 4318 HTTP"]
        YAML1["otel-collector-config.yaml<br/>receivers/processors/exporters"]
    end
    
    subgraph "Storage and Query Layer"
        PROM["prometheus<br/>Port 9090<br/>TSDB Storage"]
        YAML2["prometheus.yml<br/>scrape_configs"]
    end
    
    subgraph "Visualization and Reporting"
        GR["grafana<br/>Port 3000<br/>Dashboard Provisioning"]
        DREP["Report Generation<br/>claude -p prompts<br/>Linear MCP Integration"]
    end
    
    subgraph "Infrastructure Orchestration"
        DC["docker-compose.yml<br/>Service Dependencies"]
        CFG["managed-settings.json<br/>Organizational Deployment"]
    end
    
    CC -->|"OTLP Export"| OC
    CCT --> CCM
    CCM --> OC
    OC -->|"Metrics Export"| PROM
    PROM -->|"PromQL Queries"| GR
    PROM -->|"HTTP API"| DREP
    
    YAML1 --> OC
    YAML2 --> PROM
    DC --> OC
    DC --> PROM
    DC --> GR
    
    style CC fill:#f9f9f9
    style PROM fill:#f9f9f9
    style DREP fill:#f9f9f9
```

Sources: [docker-compose.yml](), [otel-collector-config.yaml](), [prometheus.yml](), [claude_code_roi_full.md:66-82]()

## Core Components

### Claude Code CLI Telemetry

The Claude Code CLI serves as the primary data source, emitting OpenTelemetry metrics when `CLAUDE_CODE_ENABLE_TELEMETRY=1` is configured. The CLI exports metrics via OTLP protocol to the collection pipeline.

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| `claude` CLI | `OTEL_METRICS_EXPORTER=otlp` | Primary telemetry source |
| OTLP Endpoint | `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` | Export destination |
| Protocol | `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` | Transport mechanism |

### OpenTelemetry Collector Pipeline

The collector processes telemetry data through a configured pipeline defined in `otel-collector-config.yaml`. It receives OTLP data, applies processing, and exports to Prometheus.

**Telemetry Collection Pipeline**

```mermaid
flowchart LR
    subgraph "OTLP Receivers"
        GRPC["otlp/grpc<br/>Port 4317"]
        HTTP["otlp/http<br/>Port 4318"]
    end
    
    subgraph "Processors"
        MEM["memory_limiter<br/>512MiB limit"]
        BATCH["batch<br/>1024 items<br/>1s timeout"]
    end
    
    subgraph "Exporters"
        PROMEXP["prometheus<br/>Port 8889<br/>Metrics endpoint"]
    end
    
    subgraph "Prometheus Scraper"
        PROMSRV["prometheus server<br/>15s interval<br/>scrape_configs"]
    end
    
    GRPC --> MEM
    HTTP --> MEM
    MEM --> BATCH
    BATCH --> PROMEXP
    PROMEXP -->|"HTTP /metrics"| PROMSRV
    
    style PROMEXP fill:#f9f9f9
    style PROMSRV fill:#f9f9f9
```

Sources: [otel-collector-config.yaml](), [prometheus.yml](), [claude_code_roi_full.md:55-82]()

### Metrics Storage and Query Engine

Prometheus serves as the time-series database, storing Claude Code metrics and providing PromQL query capabilities for analysis and visualization.

### Visualization and Reporting Layer

Grafana provides real-time dashboards, while the automated reporting system uses the Claude CLI with Linear MCP integration to generate comprehensive ROI reports.

## Data Flow and Metric Types

The system collects and processes several categories of metrics from Claude Code sessions:

| Metric Name | Type | Labels | Purpose |
|-------------|------|--------|---------|
| `claude_code_cost_usage_USD_total` | Counter | `user.id`, `session.id`, `model` | Track costs per session |
| `claude_code_token_usage_tokens_total` | Counter | `type` (input/output/cache), `user_email`, `model` | Monitor token consumption |
| `claude_code_session_count` | Counter | `user.id` | Track tool adoption |
| `claude_code_pull_request_count` | Counter | `user.id` | Measure development output |
| `claude_code_code_edit_tool_decision` | Counter | `decision` (accept/reject) | Tool effectiveness |

**Metric Data Flow Architecture**

```mermaid
graph TD
    subgraph "Claude Code Session Events"
        A["User Session Start<br/>claude -p prompt"]
        B["Token Consumption<br/>Input/Output/Cache"]
        C["Cost Calculation<br/>Model-specific pricing"]
        D["Tool Interactions<br/>Edit/MultiEdit decisions"]
        E["Development Output<br/>Commits/PRs/LOC"]
    end
    
    subgraph "OTLP Export Pipeline"
        F["OpenTelemetry SDK<br/>Metric Collection"]
        G["OTLP Protocol<br/>gRPC/HTTP Transport"]
        H["otel-collector<br/>Batch Processing"]
    end
    
    subgraph "Storage and Analysis"
        I["Prometheus TSDB<br/>Time Series Storage"]
        J["PromQL Queries<br/>sum() by (labels)"]
        K["HTTP API<br/>/api/v1/query endpoint"]
    end
    
    subgraph "Consumption Layer"
        L["Grafana Dashboards<br/>Real-time Visualization"]
        M["Report Generation<br/>claude CLI + prompts"]
        N["Linear MCP Integration<br/>Project Context"]
    end
    
    A --> F
    B --> F
    C --> F
    D --> F
    E --> F
    
    F --> G
    G --> H
    H --> I
    
    I --> J
    J --> K
    
    K --> L
    K --> M
    N --> M
    
    style I fill:#f9f9f9
    style M fill:#f9f9f9
```

Sources: [claude_code_roi_full.md:94-121](), [claude_code_roi_full.md:200-217]()

## Integration Points

### Linear MCP Integration

The system integrates with Linear project management through the MCP (Model Context Protocol) to combine development metrics with project velocity data.

Configuration in `.claude.json`:
```json
{
  "mcpServers": {
    "linear": {
      "type": "stdio", 
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/sse"]
    }
  }
}
```

### Prometheus Query Interface

Key PromQL queries for ROI analysis:

| Query Purpose | PromQL Expression |
|---------------|-------------------|
| Total cost | `sum(claude_code_cost_usage_USD_total)` |
| Cost by model | `sum(claude_code_cost_usage_USD_total) by (model)` |
| Token efficiency | `sum(claude_code_token_usage_tokens_total) by (type)` |
| User adoption | `sum(claude_code_token_usage_tokens_total) by (user_email)` |

### Organizational Deployment

The system supports enterprise deployment through `managed-settings.json` configuration, enabling centralized telemetry collection across development teams with consistent OTLP endpoint configuration and authentication.

Sources: [claude_code_roi_full.md:410-437](), [claude_code_roi_full.md:504-528](), [README.md:17-22]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [claude_code_roi_full.md](claude_code_roi_full.md)
- [docker-compose.yml](docker-compose.yml)

</details>



## Purpose and Scope

This document describes the technical architecture of the Claude Code ROI Measurement System, including component relationships, data flow, and configuration structures. It covers the core infrastructure services (`otel-collector`, `prometheus`, `grafana`) and their integration with Claude Code CLI telemetry.

For setup and deployment procedures, see [Installation and Setup](#2). For specific telemetry configuration details, see [Telemetry Collection Pipeline](#3). For monitoring dashboards, see [Monitoring and Visualization](#4).

## Overview

The Claude Code ROI Measurement System implements a multi-tier observability architecture that collects telemetry from Claude Code CLI sessions, processes metrics through OpenTelemetry pipelines, stores time-series data in Prometheus, and provides visualization through Grafana dashboards. The system also supports automated report generation by combining telemetry data with Linear project management data via MCP integration.

## Core Architecture Components

### Infrastructure Orchestration

The system deploys as containerized services orchestrated by Docker Compose, with three primary infrastructure components and their dependencies:

```mermaid
graph TB
    subgraph "Docker Infrastructure"
        dc["docker-compose.yml"]
        
        subgraph "Core Services"
            otel["otel-collector<br/>Port 4317/4318/8889"]
            prom["prometheus<br/>Port 9090"]
            graf["grafana<br/>Port 3000"]
        end
        
        subgraph "Configuration Files"
            otelconfig["otel-collector-config.yaml"]
            promconfig["prometheus.yml"]
            grafconfig["grafana/provisioning/"]
        end
        
        subgraph "Persistent Storage"
            promdata["prometheus_data volume"]
            grafdata["grafana_data volume"]
        end
    end
    
    subgraph "External Integrations"
        claudecode["Claude Code CLI<br/>OTLP Export"]
        linear["Linear MCP<br/>Project Data"]
    end
    
    dc --> otel
    dc --> prom
    dc --> graf
    
    otelconfig --> otel
    promconfig --> prom
    grafconfig --> graf
    
    prom --> promdata
    graf --> grafdata
    
    claudecode -->|"OTLP gRPC/HTTP"| otel
    otel -->|"depends_on"| prom
    graf -->|"depends_on"| prom
    
    linear -->|"MCP Protocol"| claudecode
```

Sources: [docker-compose.yml:1-49](), [claude_code_roi_full.md:54-64]()

### Telemetry Data Flow Architecture

The telemetry pipeline processes Claude Code metrics through a multi-stage collection and storage architecture:

```mermaid
flowchart TD
    subgraph "Claude Code Session Layer"
        claudecli["claude CLI"]
        telemetry["CLAUDE_CODE_ENABLE_TELEMETRY=1"]
        metrics["claude_code.cost.usage<br/>claude_code.token.usage<br/>claude_code.session.count<br/>claude_code.pull_request.count"]
    end
    
    subgraph "OpenTelemetry Collection Layer"
        otlprecv["OTLP Receivers<br/>:4317 gRPC<br/>:4318 HTTP"]
        processors["Memory Limiter<br/>Batch Processor"]
        promexp["Prometheus Exporter<br/>:8889"]
    end
    
    subgraph "Storage and Query Layer"
        promserver["Prometheus Server<br/>:9090"]
        promapi["Prometheus HTTP API<br/>/api/v1/query"]
        tsdb["Time Series Database<br/>200h retention"]
    end
    
    subgraph "Visualization Layer"
        grafanaui["Grafana UI<br/>:3000"]
        dashboards["Dashboard JSON<br/>grafana/dashboards/"]
        provisioning["Grafana Provisioning<br/>grafana/provisioning/"]
    end
    
    subgraph "Reporting Layer"
        claudereports["Claude CLI<br/>Report Generation"]
        linearmcp["Linear MCP Server<br/>mcp.linear.app/sse"]
        reportoutput["sample-report-output.md"]
    end
    
    claudecli --> telemetry
    telemetry --> metrics
    metrics -->|"OTEL_EXPORTER_OTLP_ENDPOINT"| otlprecv
    
    otlprecv --> processors
    processors --> promexp
    promexp -->|"scrape_configs"| promserver
    
    promserver --> promapi
    promapi --> tsdb
    
    tsdb --> grafanaui
    provisioning --> dashboards
    dashboards --> grafanaui
    
    promapi -->|"Metrics Query"| claudereports
    linearmcp -->|"Project Data"| claudereports
    claudereports --> reportoutput
```

Sources: [claude_code_roi_full.md:66-82](), [docker-compose.yml:3-13](), [claude_code_roi_full.md:91-121]()

## Configuration Architecture

### Service Configuration Hierarchy

The system uses a layered configuration approach where Docker Compose orchestrates services, and each service loads its specific configuration files:

| Configuration File | Service Target | Key Settings | Purpose |
|-------------------|----------------|-------------|---------|
| `docker-compose.yml` | Docker Engine | Service definitions, port mappings, volumes | Orchestrates all infrastructure services |
| `otel-collector-config.yaml` | `otel-collector` | Receivers, processors, exporters | Defines telemetry pipeline processing |
| `prometheus.yml` | `prometheus` | Scrape configs, retention settings | Controls metrics collection and storage |
| `grafana/provisioning/` | `grafana` | Datasource configs, dashboard automation | Provisions visualization components |

Sources: [docker-compose.yml:1-49](), [claude_code_roi_full.md:54-64]()

### Claude Code Integration Points

The Claude Code CLI integrates with the telemetry infrastructure through environment variable configuration and OTLP export:

```mermaid
graph LR
    subgraph "Claude Code Configuration"
        envvars["Environment Variables<br/>CLAUDE_CODE_ENABLE_TELEMETRY<br/>OTEL_METRICS_EXPORTER<br/>OTEL_EXPORTER_OTLP_ENDPOINT"]
        
        mcpconfig[".claude.json<br/>mcpServers.linear"]
        
        managedconfig["managed-settings.json<br/>telemetry.enabled<br/>telemetry.endpoint"]
    end
    
    subgraph "Telemetry Export"
        otlpgrpc["OTLP gRPC<br/>localhost:4317"]
        otlphttp["OTLP HTTP<br/>localhost:4318"]
        console["Console Output<br/>Debug Mode"]
    end
    
    subgraph "MCP Integration"
        linearserver["Linear MCP Server<br/>npx mcp-remote"]
        sseconnection["SSE Connection<br/>https://mcp.linear.app/sse"]
    end
    
    envvars --> otlpgrpc
    envvars --> otlphttp
    envvars --> console
    
    mcpconfig --> linearserver
    linearserver --> sseconnection
    
    managedconfig -->|"Organization Deployment"| envvars
```

Sources: [claude_code_roi_full.md:19-24](), [claude_code_roi_full.md:66-82](), [claude_code_roi_full.md:414-436](), [claude_code_roi_full.md:508-527]()

## Metrics and Data Model

### Core Telemetry Metrics

The system collects and processes the following primary metrics from Claude Code sessions:

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `claude_code_cost_usage_USD_total` | Counter | `user.id`, `session.id`, `model` | Total cost per session in USD |
| `claude_code_token_usage_tokens_total` | Counter | `type` (`input`/`output`/`cacheCreation`/`cacheRead`) | Token consumption by type |
| `claude_code_session_count` | Counter | `user.account_uuid` | Number of CLI sessions initiated |
| `claude_code_pull_request_count` | Counter | `user.account_uuid` | PRs created during Claude sessions |
| `claude_code_commit_count` | Counter | `user.account_uuid` | Commits made with Claude assistance |
| `claude_code_code_edit_tool_decision` | Counter | `decision` (`accept`/`reject`) | Code editing tool permission decisions |

Sources: [claude_code_roi_full.md:95-121](), [claude_code_roi_full.md:200-217](), [claude_code_roi_full.md:26-52]()

### Prometheus Query Patterns

The system supports various PromQL query patterns for extracting business insights:

```mermaid
graph TD
    subgraph "Cost Analysis Queries"
        totalcost["sum(claude_code_cost_usage_USD_total)"]
        costbymodel["sum(claude_code_cost_usage_USD_total) by (model)"]
        costbyuser["sum(claude_code_cost_usage_USD_total) by (user_email)"]
    end
    
    subgraph "Usage Pattern Queries"
        tokenrate["rate(claude_code_token_usage_tokens_total[5m])"]
        tokensbytype["sum(claude_code_token_usage_tokens_total) by (type)"]
        acceptance["sum(claude_code_code_edit_tool_decision{decision=\"accept\"}) / sum(claude_code_code_edit_tool_decision)"]
    end
    
    subgraph "Productivity Metrics"
        costperpr["sum(claude_code_cost_usage_USD_total) / sum(claude_code_pull_request_count)"]
        sessionefficiency["sum(claude_code_pull_request_count) / sum(claude_code_session_count)"]
        commitrate["rate(claude_code_commit_count[1h])"]
    end
    
    subgraph "Business Intelligence"
        roicalc["(totalDevCost * productivityGain) - claudeCodeCost"]
        usagetrends["increase(claude_code_session_count[30d])"]
        adoptionrate["count(distinct user.account_uuid) by (time_period)"]
    end
```

Sources: [claude_code_roi_full.md:95-121](), [claude_code_roi_full.md:248-295]()

## Automated Reporting Architecture

### Report Generation Pipeline

The system supports automated report generation that combines Prometheus metrics with Linear project data through Claude CLI and MCP integration:

```mermaid
sequenceDiagram
    participant script as "fetch-claude-metrics.sh"
    participant promapi as "Prometheus API<br/>:9090/api/v1/query"
    participant claudecli as "claude CLI"
    participant linearmcp as "Linear MCP Server"
    participant reportgen as "Report Generator"
    participant output as "sample-report-output.md"
    
    script->>promapi: "GET sum(claude_code_cost_usage_USD_total)"
    promapi-->>script: "Total cost data"
    
    script->>promapi: "GET sum(claude_code_token_usage_tokens_total)"
    promapi-->>script: "Token usage data"
    
    script->>claudecli: "claude -p 'report prompt with metrics'"
    claudecli->>linearmcp: "Query team velocity, issues"
    linearmcp-->>claudecli: "Sprint data, completion metrics"
    
    claudecli->>reportgen: "Process combined data + prompt"
    reportgen->>reportgen: "Calculate ROI metrics<br/>Generate Mermaid diagrams<br/>Create recommendations"
    
    reportgen->>output: "Write Markdown report"
```

Sources: [claude_code_roi_full.md:458-477](), [claude_code_roi_full.md:414-436](), [claude_code_roi_full.md:482-500]()

## Deployment Architecture Patterns

### Development vs Production Configurations

The system supports multiple deployment patterns with different endpoint configurations:

| Environment | OTLP Endpoint | Use Case | Configuration Source |
|-------------|---------------|----------|---------------------|
| Local Development | `http://localhost:4317` | Individual developer testing | Environment variables |
| Kubernetes | `http://otel-collector.monitoring.svc.cluster.local:4317` | Clustered deployment | ConfigMap/Secret |
| Cloud Provider | Application Load Balancer endpoint | Managed infrastructure | Cloud-specific configuration |
| SaaS Integration | `https://otlp.datadoghq.com` or `https://api.honeycomb.io:443` | External observability platforms | Managed settings |

The system uses `managed-settings.json` for organization-wide deployment, ensuring consistent telemetry collection across all Claude Code installations without user-configurable overrides.

Sources: [claude_code_roi_full.md:84-90](), [claude_code_roi_full.md:508-527](), [docker-compose.yml:8-11]()

---

# Page: Key Features and Capabilities

# Key Features and Capabilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [sample-report-output.md](sample-report-output.md)

</details>



This document describes the core features and capabilities of the Claude Code ROI Measurement System, including telemetry collection, cost analysis, productivity tracking, and automated reporting functionalities. For system architecture and component relationships, see [System Architecture](#1.1). For installation and configuration procedures, see [Installation and Setup](#2).

## Core Telemetry Collection

The system provides comprehensive telemetry collection capabilities through OpenTelemetry integration, capturing real-time usage data from Claude Code sessions.

### Metric Collection Pipeline

```mermaid
flowchart TD
    CC["claude CLI"] --> OTEL["OpenTelemetry SDK"]
    OTEL --> OTLP_GRPC["OTLP gRPC :4317"]
    OTEL --> OTLP_HTTP["OTLP HTTP :4318"]
    OTEL --> CONSOLE["Console Exporter"]
    
    OTLP_GRPC --> OC["otel-collector"]
    OTLP_HTTP --> OC
    
    OC --> ML["memory_limiter"]
    ML --> BP["batch processor"]
    BP --> PE["prometheus exporter :8889"]
    
    PE --> PROM["prometheus :9090"]
    PROM --> GRAFANA["grafana :3000"]
```

**Core Metrics Collected:**

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `claude_code.cost.usage` | Counter | Cost per session in USD | `user.id`, `session.id`, `model` |
| `claude_code.token.usage` | Counter | Token consumption by type | `type` (input/output/cacheCreation/cacheRead), `user.email`, `model` |
| `claude_code.session.count` | Counter | Number of CLI sessions started | `user.id`, `session.duration` |
| `claude_code.code_edit_tool.decision` | Counter | Tool permission decisions | `decision` (accept/reject), `tool` (Edit/MultiEdit/Write/Read/Bash) |

Sources: [claude_code_roi_full.md:27-51](), [claude_code_roi_full.md:134-217]()

### Environment Configuration

The telemetry system is controlled through specific environment variables that configure collection and export behavior:

```mermaid
graph TB
    ENV_TEL["CLAUDE_CODE_ENABLE_TELEMETRY=1"] --> OTEL_SDK["OpenTelemetry SDK"]
    ENV_EXP["OTEL_METRICS_EXPORTER=otlp"] --> OTEL_SDK
    ENV_PROTO["OTEL_EXPORTER_OTLP_PROTOCOL=grpc"] --> OTLP_CONFIG["OTLP Configuration"]
    ENV_END["OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317"] --> OTLP_CONFIG
    ENV_HEAD["OTEL_EXPORTER_OTLP_HEADERS"] --> OTLP_CONFIG
    
    OTLP_CONFIG --> COLLECTOR["otel-collector-config.yaml"]
    OTEL_SDK --> METRICS["claude_code metrics"]
    
    COLLECTOR --> RECEIVERS["receivers: otlp/grpc, otlp/http"]
    COLLECTOR --> PROCESSORS["processors: memory_limiter, batch"]
    COLLECTOR --> EXPORTERS["exporters: prometheus"]
```

Sources: [claude_code_roi_full.md:68-82](), [claude_code_roi_full.md:511-527]()

## Cost Analysis and Optimization

The system provides detailed cost tracking and analysis capabilities for different Claude models and usage patterns.

### Multi-Model Cost Tracking

```mermaid
pie
    title "Cost Distribution by Model"
    "claude-opus-4-20250514" : 0.429
    "claude-3-5-haiku-20241022" : 0.0006
    "claude-4-sonnet-20250514" : 0.234
```

**Model Pricing Structure:**

| Model | Input Tokens (per 1M) | Output Tokens (per 1M) | Use Case |
|-------|----------------------|------------------------|----------|
| `claude-3-5-haiku-20241022` | $0.80 | $4.00 | Fast, cost-effective queries |
| `claude-4-sonnet-20250514` | $3.00 | $15.00 | Balanced performance |
| `claude-opus-4-20250514` | $15.00 | $75.00 | Most capable, complex analysis |

### Cost Analysis Queries

The system supports sophisticated cost analysis through PromQL queries:

```promql
# Total cost across all sessions
sum(claude_code_cost_usage_USD_total)

# Cost by model type  
sum(claude_code_cost_usage_USD_total) by (model)

# Token usage by type
sum(claude_code_token_usage_tokens_total) by (type)

# Cost per user
sum(claude_code_cost_usage_USD_total) by (user_email)
```

Sources: [claude_code_roi_full.md:91-121](), [claude_code_roi_full.md:168-173]()

## Productivity Measurement

The system tracks multiple productivity indicators to measure developer effectiveness and tool adoption.

### Tool Usage Tracking

```mermaid
graph LR
    EDIT["Edit Tool"] --> DECISION_EDIT["code_edit_tool.decision"]
    MULTIEDIT["MultiEdit Tool"] --> DECISION_MULTI["code_edit_tool.decision"]
    WRITE["Write Tool"] --> DECISION_WRITE["code_edit_tool.decision"]
    READ["Read Tool"] --> DECISION_READ["code_edit_tool.decision"]
    BASH["Bash Tool"] --> DECISION_BASH["code_edit_tool.decision"]
    
    DECISION_EDIT --> ACCEPT["decision=accept"]
    DECISION_EDIT --> REJECT["decision=reject"]
    DECISION_MULTI --> ACCEPT
    DECISION_MULTI --> REJECT
    DECISION_WRITE --> ACCEPT
    DECISION_WRITE --> REJECT
    DECISION_READ --> ACCEPT
    DECISION_READ --> REJECT
    DECISION_BASH --> ACCEPT
    DECISION_BASH --> REJECT
```

**Productivity Metrics Reliability:**

| Metric | Reliability | Use Case |
|--------|-------------|----------|
| `claude_code.pull_request.count` | High | Feature completion tracking |
| `claude_code.commit.count` | Medium | Development velocity (varies by team practices) |
| `claude_code.lines_of_code.count` | Low | Code volume (can be misleading) |
| `claude_code.code_edit_tool.decision` | High | Tool adoption and effectiveness |

Sources: [claude_code_roi_full.md:200-217](), [claude_code_roi_full.md:220-241]()

### Session Analysis

The system tracks session patterns to identify optimal usage scenarios:

```mermaid
graph TD
    SESSION_START["Session Start"] --> DURATION["Session Duration Tracking"]
    DURATION --> SHORT["< 5 minutes"]
    DURATION --> MEDIUM["5-30 minutes"] 
    DURATION --> LONG["> 30 minutes"]
    
    SHORT --> QUICK["Quick Questions/Fixes"]
    MEDIUM --> FEATURE["Feature Development"]
    LONG --> DEEP["Deep Work Sessions"]
    
    QUICK --> METRICS["claude_code.session.count"]
    FEATURE --> METRICS
    DEEP --> METRICS
```

Sources: [claude_code_roi_full.md:182-193]()

## Real-time Monitoring and Visualization

The system provides comprehensive real-time monitoring through Grafana dashboards connected to Prometheus time-series data.

### Monitoring Stack Configuration

```mermaid
graph TB
    DOCKER["docker-compose.yml"] --> PROM_SERVICE["prometheus service"]
    DOCKER --> GRAF_SERVICE["grafana service"]
    DOCKER --> OTEL_SERVICE["otel-collector service"]
    
    PROM_CONFIG["prometheus.yml"] --> PROM_SERVICE
    GRAF_PROV["grafana/provisioning/"] --> GRAF_SERVICE
    OTEL_CONFIG["otel-collector-config.yaml"] --> OTEL_SERVICE
    
    PROM_SERVICE --> SCRAPE[":9090 scrape_configs"]
    GRAF_SERVICE --> DASHBOARD[":3000 dashboards"]
    OTEL_SERVICE --> RECEIVE[":4317/:4318 receivers"]
    OTEL_SERVICE --> EXPORT[":8889 prometheus exporter"]
    
    EXPORT --> SCRAPE
    DASHBOARD --> SCRAPE
```

**Key Dashboard Visualizations:**

- Cost per model pie charts
- Token usage time series
- User activity tables sorted by cost
- Tool acceptance rate trends
- Session duration distributions

Sources: [claude_code_roi_full.md:54-64](), [claude_code_roi_full.md:123-128]()

## Automated Reporting System

The system generates comprehensive reports combining Claude Code metrics with project management data through Linear MCP integration.

### Linear MCP Integration Architecture

```mermaid
sequenceDiagram
    participant USER as "claude CLI"
    participant MCP as "Linear MCP Server"
    participant LINEAR as "Linear API"
    participant PROM as "Prometheus API"
    participant REPORT as "Report Generator"
    
    USER->>MCP: "mcp add linear"
    MCP->>LINEAR: "SSE connection"
    
    USER->>REPORT: "Generate report prompt"
    
    par "Fetch Claude Metrics"
        REPORT->>PROM: "GET /api/v1/query"
        PROM-->>REPORT: "Token usage, cost data"
    and "Fetch Project Data"
        REPORT->>MCP: "Query team velocity, issues"
        MCP->>LINEAR: "Project data request"
        LINEAR-->>MCP: "Sprint data, completion metrics"
        MCP-->>REPORT: "Linear metrics"
    end
    
    REPORT->>USER: "Markdown report with visualizations"
```

### Report Generation Configuration

The MCP integration is configured through `.claude.json`:

```json
{
  "mcpServers": {
    "linear": {
      "type": "stdio", 
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/sse"]
    }
  }
}
```

**Generated Report Components:**

- Executive summary with velocity improvements
- Mermaid visualizations for tool usage and costs
- Linear ticket analysis with priority breakdown
- Actionable recommendations based on usage patterns
- Cost breakdowns and ROI calculations

Sources: [claude_code_roi_full.md:410-453](), [claude_code_roi_full.md:424-436](), [sample-report-output.md:1-158]()

## Enterprise Deployment Features

The system supports enterprise-wide deployment through managed settings and centralized configuration.

### Managed Settings Configuration

```mermaid
graph TB
    MDM["MDM Solution"] --> MANAGED["managed-settings.json"]
    CONFIG_MGMT["Configuration Management"] --> MANAGED
    
    MANAGED --> TEL_CONFIG["telemetry.enabled: true"]
    MANAGED --> ENDPOINT["telemetry.endpoint"]
    MANAGED --> HEADERS["telemetry.headers"]
    MANAGED --> EXPORTERS["exporters.metrics: otlp"]
    
    TEL_CONFIG --> FORCE["Force telemetry enabled"]
    ENDPOINT --> CORP_OTEL["Corporate OTEL Collector"]
    HEADERS --> AUTH["Authorization: Bearer ${OTEL_TOKEN}"]
    
    CORP_OTEL --> CENTRAL["Centralized Monitoring"]
```

**Deployment Endpoints:**

| Environment | Endpoint | Protocol |
|-------------|----------|----------|
| Local Development | `http://localhost:4317` | gRPC |
| Kubernetes | `http://otel-collector.monitoring.svc.cluster.local:4317` | gRPC |
| AWS | Application Load Balancer endpoint | gRPC/HTTP |
| DataDog | `https://otlp.datadoghq.com` | OTLP |
| Honeycomb | `https://api.honeycomb.io:443` | OTLP |

Sources: [claude_code_roi_full.md:503-528](), [claude_code_roi_full.md:84-90]()

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [docker-compose.yml](docker-compose.yml)

</details>



This document provides a comprehensive guide for setting up the Claude Code ROI measurement system infrastructure. It covers the installation of the telemetry collection pipeline, configuration of Claude Code to emit metrics, and verification of the complete system.

For detailed telemetry configuration and pipeline management, see [Telemetry Collection Pipeline](#3). For monitoring dashboard setup, see [Grafana Dashboard Setup](#4.1). For troubleshooting installation issues, see [Troubleshooting Guide](#6.1).

## Prerequisites

Before installing the Claude Code ROI measurement system, ensure your environment meets these requirements:

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| **Docker** | Docker Engine 20.10+ | Container orchestration for monitoring stack |
| **Docker Compose** | v2.0+ | Service deployment and management |
| **Claude Code CLI** | Latest version | Source of telemetry data |
| **Network Access** | Ports 3000, 4317, 4318, 8889, 9090 | Service communication and web interfaces |
| **Storage** | 2GB minimum | Prometheus time-series data and Grafana dashboards |

## Infrastructure Deployment

### Docker Compose Stack Architecture

The monitoring infrastructure consists of three primary services orchestrated through Docker Compose:

```mermaid
graph TB
    subgraph "Docker Compose Services"
        CC["claude-code CLI"]
        OC["otel-collector<br/>:4317 gRPC<br/>:4318 HTTP<br/>:8889 metrics"]
        PROM["prometheus<br/>:9090"]
        GRAF["grafana<br/>:3000"]
    end
    
    subgraph "Configuration Files"
        DC["docker-compose.yml"]
        OTC["otel-collector-config.yaml"]
        PC["prometheus.yml"] 
        GC["grafana/provisioning/"]
    end
    
    subgraph "Data Volumes"
        PD["prometheus_data"]
        GD["grafana_data"]
    end
    
    CC -->|"OTLP Export"| OC
    OC -->|"Metrics Scrape"| PROM
    PROM -->|"Query API"| GRAF
    
    DC --> OC
    DC --> PROM
    DC --> GRAF
    
    OTC --> OC
    PC --> PROM
    GC --> GRAF
    
    PROM --> PD
    GRAF --> GD
```

Sources: [docker-compose.yml:1-49]()

### Deployment Steps

1. **Clone Configuration Repository**
   ```bash
   git clone https://github.com/anthropics/claude-code-monitoring-guide
   cd claude-code-monitoring-guide
   ```

2. **Deploy Infrastructure Stack**
   ```bash
   docker-compose up -d
   ```

3. **Verify Service Status**
   ```bash
   docker-compose ps
   ```

The [docker-compose.yml:1-49]() file defines three services with specific dependencies:
- `otel-collector` depends on `prometheus` [docker-compose.yml:12-13]()
- `grafana` depends on `prometheus` [docker-compose.yml:44-45]()
- Volumes `prometheus_data` and `grafana_data` provide persistent storage [docker-compose.yml:47-49]()

Sources: [docker-compose.yml:1-49]()

## Claude Code Telemetry Configuration

### Environment Variable Setup

Configure Claude Code to emit telemetry data to the monitoring infrastructure:

```mermaid
flowchart LR
    subgraph "Environment Configuration"
        ET["CLAUDE_CODE_ENABLE_TELEMETRY=1"]
        ME["OTEL_METRICS_EXPORTER=otlp"]
        EP["OTEL_EXPORTER_OTLP_ENDPOINT"]
        PR["OTEL_EXPORTER_OTLP_PROTOCOL=grpc"]
    end
    
    subgraph "OTLP Endpoints"
        LOCAL["http://localhost:4317"]
        K8S["http://otel-collector.monitoring.svc.cluster.local:4317"]
        CLOUD["https://otlp.datadoghq.com"]
    end
    
    subgraph "Claude Code Process"
        CLI["claude CLI"]
        TEL["Telemetry Export"]
    end
    
    ET --> CLI
    ME --> CLI
    EP --> CLI
    PR --> CLI
    
    EP -.-> LOCAL
    EP -.-> K8S
    EP -.-> CLOUD
    
    CLI --> TEL
    TEL -->|"OTLP gRPC :4317"| LOCAL
```

Sources: [claude_code_roi_full.md:68-82]()

### Basic Configuration

Set the following environment variables for local development:

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

For production deployments with authentication:
```bash
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"
```

### Endpoint Configuration Options

| Environment | OTLP Endpoint | Use Case |
|-------------|---------------|----------|
| **Local Development** | `http://localhost:4317` | Docker Compose stack |
| **Kubernetes** | `http://otel-collector.monitoring.svc.cluster.local:4317` | Cluster deployment |
| **DataDog** | `https://otlp.datadoghq.com` | SaaS integration |
| **Honeycomb** | `https://api.honeycomb.io:443` | SaaS integration |

Sources: [claude_code_roi_full.md:84-89]()

## Verification and Testing

### Console Output Verification

Before connecting to the full monitoring stack, verify telemetry is working with console output:

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console
export OTEL_METRIC_EXPORT_INTERVAL=1000
claude -p "hello world"
```

Expected output includes metric descriptors for:
- `claude_code.cost.usage` with attributes `user.id`, `session.id`, `model` [claude_code_roi_full.md:32-51]()
- Token usage metrics by type (`input`, `output`, `cacheCreation`, `cacheRead`)
- Cost values in USD

Sources: [claude_code_roi_full.md:16-52]()

### Service Health Checks

Verify each component is operational:

| Service | Health Check | Expected Response |
|---------|--------------|-------------------|
| **OpenTelemetry Collector** | `curl http://localhost:8889/metrics` | Prometheus format metrics |
| **Prometheus** | `curl http://localhost:9090/-/healthy` | HTTP 200 OK |
| **Grafana** | `curl http://localhost:3000/api/health` | JSON health status |

### End-to-End Data Flow Test

1. **Generate Test Data**
   ```bash
   # With OTLP configuration active
   claude -p "test telemetry data generation"
   ```

2. **Query Prometheus Metrics**
   ```bash
   curl -s "http://localhost:9090/api/v1/query?query=claude_code_cost_usage_USD_total"
   ```

3. **Verify Grafana Data Source**
   - Access Grafana at `http://localhost:3000`
   - Default credentials: `admin` / `admin` [docker-compose.yml:39]()
   - Confirm Prometheus data source connectivity

Sources: [claude_code_roi_full.md:91-121](), [docker-compose.yml:38-39]()

## Service Configuration Files

### OpenTelemetry Collector Configuration

The system requires `otel-collector-config.yaml` mounted at `/etc/otel-collector-config.yaml` [docker-compose.yml:7]() containing:
- OTLP receivers on ports 4317 (gRPC) and 4318 (HTTP)
- Memory limiter and batch processors
- Prometheus exporter on port 8889

### Prometheus Configuration

The `prometheus.yml` file [docker-compose.yml:22]() must include:
- Scrape configuration for OpenTelemetry Collector endpoint `:8889`
- Retention settings (default 200h) [docker-compose.yml:29]()
- Data storage path `/prometheus` [docker-compose.yml:26]()

### Grafana Provisioning

Grafana configuration includes:
- Provisioning directory mounted at `/etc/grafana/provisioning` [docker-compose.yml:42]()
- Dashboard directory at `/var/lib/grafana/dashboards` [docker-compose.yml:43]()
- Persistent data volume for configuration and dashboards

Sources: [docker-compose.yml:6-43]()

## Next Steps

After successful installation:

1. **Configure Advanced Telemetry**: See [OpenTelemetry Collector Configuration](#3.1) for pipeline optimization
2. **Set Up Monitoring Dashboards**: Follow [Grafana Dashboard Setup](#4.1) for visualization configuration  
3. **Enable Automated Reporting**: Configure [Linear MCP Integration](#5.2) for comprehensive reports
4. **Production Deployment**: Review [Security and Best Practices](#6.3) for production considerations

For troubleshooting installation issues, consult [Troubleshooting Guide](#6.1).

---

# Page: Docker Infrastructure Setup

# Docker Infrastructure Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker-compose.yml](docker-compose.yml)
- [otel-collector-config.yaml](otel-collector-config.yaml)
- [prometheus.yml](prometheus.yml)

</details>



This document covers the deployment and configuration of the observability stack using Docker Compose. The infrastructure consists of three core services: OpenTelemetry Collector for telemetry ingestion, Prometheus for metrics storage, and Grafana for visualization. For configuring Claude Code to send telemetry to this infrastructure, see [Claude Code Telemetry Configuration](#2.2). For details on the OpenTelemetry Collector's internal configuration, see [OpenTelemetry Collector Configuration](#3.1).

## Service Architecture

The Docker infrastructure provides a complete observability stack with well-defined service dependencies and communication patterns.

### Service Dependencies and Communication

```mermaid
graph TD
    CC["claude-code CLI"] --> OC
    OC["otel-collector:4317/4318<br/>OpenTelemetry Collector"] --> PROM
    PROM["prometheus:9090<br/>Prometheus Server"] --> GR
    GR["grafana:3000<br/>Grafana Dashboard"]
    
    OC -->|"metrics endpoint :8889"| PROM
    GR -->|"queries via HTTP API"| PROM
    
    subgraph "Docker Network"
        OC
        PROM  
        GR
    end
    
    subgraph "Host Network"
        CC
    end
```

Sources: [docker-compose.yml:1-49]()

The architecture implements a linear data flow where the `otel-collector` service depends on `prometheus` ([docker-compose.yml:12-13]()), and `grafana` depends on `prometheus` ([docker-compose.yml:44-45]()). This ensures proper startup ordering and prevents connection failures during initialization.

### Service Configuration Structure

```mermaid
graph LR
    DC["docker-compose.yml"] --> OC_SVC["otel-collector service"]
    DC --> PROM_SVC["prometheus service"] 
    DC --> GR_SVC["grafana service"]
    
    OC_CONFIG["otel-collector-config.yaml"] --> OC_SVC
    PROM_CONFIG["prometheus.yml"] --> PROM_SVC
    GR_PROV["grafana/provisioning/"] --> GR_SVC
    GR_DASH["grafana/dashboards/"] --> GR_SVC
```

Sources: [docker-compose.yml:7](), [docker-compose.yml:22](), [docker-compose.yml:42-43]()

## Service Definitions

### OpenTelemetry Collector Service

The `otel-collector` service runs the `otel/opentelemetry-collector-contrib:latest` image ([docker-compose.yml:4]()) and provides OTLP endpoints for receiving telemetry data from Claude Code.

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Image | `otel/opentelemetry-collector-contrib:latest` | Includes all receivers and exporters |
| Config File | `./otel-collector-config.yaml:/etc/otel-collector-config.yaml` | Pipeline configuration |
| OTLP gRPC Port | `4317:4317` | Receives OTLP gRPC telemetry |
| OTLP HTTP Port | `4318:4318` | Receives OTLP HTTP telemetry |  
| Metrics Port | `8889:8889` | Exposes Prometheus metrics |

Sources: [docker-compose.yml:3-13]()

The collector processes telemetry through a pipeline defined in `otel-collector-config.yaml` with `memory_limiter` and `batch` processors ([otel-collector-config.yaml:13-15](), [otel-collector-config.yaml:10-12]()) before exporting to Prometheus format.

### Prometheus Service

The `prometheus` service provides time-series storage and querying capabilities using the `prom/prometheus:latest` image ([docker-compose.yml:17]()).

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Container Name | `prometheus` | Service discovery reference |
| Port | `9090:9090` | Web UI and HTTP API |
| Config File | `./prometheus.yml:/etc/prometheus/prometheus.yml` | Scrape configuration |
| Data Volume | `prometheus_data:/prometheus` | Persistent storage |
| Retention | `--storage.tsdb.retention.time=200h` | Data retention period |

Sources: [docker-compose.yml:15-30]()

Prometheus scrapes metrics from the OpenTelemetry Collector at `otel-collector:8889` ([prometheus.yml:11-13]()) with a 15-second interval ([prometheus.yml:2]()).

### Grafana Service

The `grafana` service provides dashboard visualization using the `grafana/grafana:latest` image ([docker-compose.yml:34]()).

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Container Name | `grafana` | Service reference |
| Port | `3000:3000` | Web interface |
| Admin Password | `admin` | Default authentication |
| Data Volume | `grafana_data:/var/lib/grafana` | Dashboard persistence |
| Provisioning | `./grafana/provisioning:/etc/grafana/provisioning` | Automated configuration |
| Dashboards | `./grafana/dashboards:/var/lib/grafana/dashboards` | Dashboard definitions |

Sources: [docker-compose.yml:32-45]()

## Network and Port Configuration

### Port Mappings

```mermaid
graph LR
    subgraph "Host Ports"
        H4317["4317"]
        H4318["4318"] 
        H8889["8889"]
        H9090["9090"]
        H3000["3000"]
    end
    
    subgraph "Container Services"
        OC_GRPC["otel-collector:4317<br/>OTLP gRPC"]
        OC_HTTP["otel-collector:4318<br/>OTLP HTTP"]
        OC_METRICS["otel-collector:8889<br/>Prometheus Metrics"]
        PROM_API["prometheus:9090<br/>Web UI + API"]
        GR_UI["grafana:3000<br/>Dashboard UI"]
    end
    
    H4317 --> OC_GRPC
    H4318 --> OC_HTTP
    H8889 --> OC_METRICS
    H9090 --> PROM_API
    H3000 --> GR_UI
```

Sources: [docker-compose.yml:8-11](), [docker-compose.yml:19-20](), [docker-compose.yml:36-37]()

The port mappings expose all necessary endpoints for external access while maintaining internal service communication through Docker's network.

### Internal Service Communication

| Source Service | Target Service | Endpoint | Protocol |
|----------------|----------------|----------|----------|
| `prometheus` | `otel-collector` | `otel-collector:8889` | HTTP (scraping) |
| `grafana` | `prometheus` | `prometheus:9090` | HTTP (queries) |
| External | `otel-collector` | `localhost:4317/4318` | OTLP |

Sources: [prometheus.yml:13](), [docker-compose.yml:44-45]()

## Volume Management

### Persistent Storage

The infrastructure defines two named volumes for data persistence:

```mermaid
graph TD
    subgraph "Named Volumes"
        PROM_VOL["prometheus_data"]
        GR_VOL["grafana_data"]
    end
    
    subgraph "Mount Points"
        PROM_MOUNT["/prometheus<br/>TSDB storage"]
        GR_MOUNT["/var/lib/grafana<br/>Dashboard storage"]
    end
    
    subgraph "Configuration Bind Mounts"
        OC_CONFIG["./otel-collector-config.yaml"]
        PROM_CONFIG["./prometheus.yml"] 
        GR_PROV["./grafana/provisioning/"]
        GR_DASH["./grafana/dashboards/"]
    end
    
    PROM_VOL --> PROM_MOUNT
    GR_VOL --> GR_MOUNT
    
    OC_CONFIG --> OC_SVC["otel-collector:/etc/otel-collector-config.yaml"]
    PROM_CONFIG --> PROM_SVC["prometheus:/etc/prometheus/prometheus.yml"]
    GR_PROV --> GR_PROV_MOUNT["grafana:/etc/grafana/provisioning"]
    GR_DASH --> GR_DASH_MOUNT["grafana:/var/lib/grafana/dashboards"]
```

Sources: [docker-compose.yml:47-49](), [docker-compose.yml:21-23](), [docker-compose.yml:40-43]()

Named volumes ensure data persistence across container restarts, while bind mounts provide direct access to configuration files for easy modification.

## Deployment Commands

### Starting the Infrastructure

```bash
# Start all services in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up prometheus
```

### Service Management

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs otel-collector
docker-compose logs prometheus  
docker-compose logs grafana

# Restart specific service
docker-compose restart otel-collector

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Verification

After deployment, verify services are accessible:

- OpenTelemetry Collector: `curl http://localhost:8889/metrics`
- Prometheus: `http://localhost:9090` 
- Grafana: `http://localhost:3000` (admin/admin)

Sources: [docker-compose.yml:8-11](), [docker-compose.yml:19-20](), [docker-compose.yml:36-37]()

---

# Page: Claude Code Telemetry Configuration

# Claude Code Telemetry Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [troubleshooting.md](troubleshooting.md)

</details>



This document covers the configuration of the Claude Code CLI tool to emit telemetry data to the OpenTelemetry Collector. It focuses specifically on the client-side configuration required to enable metrics collection and export.

For Docker infrastructure setup of the monitoring stack, see [Docker Infrastructure Setup](#2.1). For OpenTelemetry Collector configuration details, see [OpenTelemetry Collector Configuration](#3.1). For information about available metrics and their structure, see [Available Metrics and Data Model](#3.3).

## Environment Variable Configuration

Claude Code telemetry is controlled through standard OpenTelemetry environment variables. The primary configuration involves enabling telemetry and specifying the export destination.

### Basic Telemetry Enablement

The fundamental requirement is enabling telemetry collection in the Claude Code CLI:

| Environment Variable | Value | Purpose |
|---------------------|-------|---------|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | `1` | Activates telemetry collection in Claude Code |
| `OTEL_METRICS_EXPORTER` | `otlp` or `console` | Specifies the export mechanism |
| `OTEL_METRIC_EXPORT_INTERVAL` | `1000` (milliseconds) | Controls export frequency |

### OTLP Protocol Configuration

For production deployments, the OTLP exporter connects Claude Code to the monitoring infrastructure:

| Environment Variable | Example Value | Description |
|---------------------|---------------|-------------|
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` | Transport protocol (`grpc` or `http/protobuf`) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | Collector endpoint URL |
| `OTEL_EXPORTER_OTLP_HEADERS` | `Authorization=Bearer token` | Authentication headers |

### Configuration Flow Diagram

```mermaid
graph TB
    subgraph "Claude Code CLI Process"
        CLI["claude command execution"]
        TELEM["CLAUDE_CODE_ENABLE_TELEMETRY=1"]
        METRICS["Metrics Collection Engine"]
    end
    
    subgraph "OpenTelemetry Configuration"
        EXPORTER["OTEL_METRICS_EXPORTER=otlp"]
        PROTOCOL["OTEL_EXPORTER_OTLP_PROTOCOL=grpc"]
        ENDPOINT["OTEL_EXPORTER_OTLP_ENDPOINT"]
        HEADERS["OTEL_EXPORTER_OTLP_HEADERS"]
    end
    
    subgraph "Export Destinations"
        CONSOLE["console output"]
        GRPC["gRPC :4317"]
        HTTP["HTTP :4318"]
    end
    
    CLI --> TELEM
    TELEM --> METRICS
    METRICS --> EXPORTER
    EXPORTER --> PROTOCOL
    PROTOCOL --> ENDPOINT
    ENDPOINT --> HEADERS
    
    EXPORTER --> CONSOLE
    PROTOCOL --> GRPC
    PROTOCOL --> HTTP
```

**Sources:** [claude_code_roi_full.md:20-82]()

## OTLP Endpoint Configuration

The `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable determines where Claude Code sends telemetry data. The endpoint configuration varies by infrastructure deployment.

### Endpoint Format and Protocols

Claude Code supports both gRPC and HTTP protocols for OTLP export:

| Protocol | Default Port | URL Format | Use Case |
|----------|-------------|------------|----------|
| `grpc` | `:4317` | `http://host:4317` | High-performance, binary protocol |
| `http/protobuf` | `:4318` | `http://host:4318/v1/metrics` | HTTP-based, firewall-friendly |

### Infrastructure-Specific Endpoints

Different deployment environments require specific endpoint configurations:

```mermaid
graph LR
    subgraph "Claude Code CLI"
        CC["claude process"]
        ENV["Environment Variables"]
    end
    
    subgraph "Local Development"
        LOCAL["localhost:4317"]
    end
    
    subgraph "Kubernetes Cluster"
        K8S["otel-collector.monitoring.svc.cluster.local:4317"]
    end
    
    subgraph "Cloud Infrastructure"
        AWS["ALB endpoint"]
        DATADOG["otlp.datadoghq.com"]
        HONEYCOMB["api.honeycomb.io:443"]
    end
    
    CC --> ENV
    ENV --> LOCAL
    ENV --> K8S
    ENV --> AWS
    ENV --> DATADOG
    ENV --> HONEYCOMB
```

**Sources:** [claude_code_roi_full.md:84-90]()

## Verification and Testing

Before configuring production endpoints, verify telemetry functionality using console output.

### Console Output Verification

Console export provides immediate feedback for telemetry validation:

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console
export OTEL_METRIC_EXPORT_INTERVAL=1000
claude -p "hello world"
```

Expected console output includes metric descriptors and data points with attributes like `user.id`, `session.id`, and `model`.

### Metric Data Structure

The console output reveals the telemetry data structure:

```mermaid
graph TB
    subgraph "Metric Output Structure"
        RESOURCE["Resource Attributes"]
        SERVICE["service.name: claude-code"]
        VERSION["service.version: 1.0.17"]
        
        DESCRIPTOR["Metric Descriptor"]
        NAME["name: claude_code.cost.usage"]
        TYPE["type: COUNTER"]
        UNIT["unit: USD"]
        
        DATAPOINT["Data Points"]
        USERID["user.id: hash"]
        SESSIONID["session.id: uuid"]
        MODEL["model: claude-4-sonnet-20250514"]
        VALUE["value: 0.000297"]
    end
    
    RESOURCE --> SERVICE
    RESOURCE --> VERSION
    DESCRIPTOR --> NAME
    DESCRIPTOR --> TYPE
    DESCRIPTOR --> UNIT
    DATAPOINT --> USERID
    DATAPOINT --> SESSIONID
    DATAPOINT --> MODEL
    DATAPOINT --> VALUE
```

**Sources:** [claude_code_roi_full.md:16-52]()

## Authentication and Headers

Production OTLP endpoints often require authentication through HTTP headers.

### Header Configuration

The `OTEL_EXPORTER_OTLP_HEADERS` environment variable supports multiple authentication schemes:

| Authentication Type | Header Format | Example |
|-------------------|---------------|---------|
| Bearer Token | `Authorization=Bearer token` | API key authentication |
| Custom Headers | `X-API-Key=key,X-Org=org` | Multiple header pairs |
| DataDog | `DD-API-KEY=key` | DataDog-specific authentication |

### Secure Configuration

For production deployments, avoid hardcoding credentials in environment variables:

```bash
# Use environment variable substitution
export OTEL_TOKEN="your-secure-token"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer ${OTEL_TOKEN}"
```

**Sources:** [claude_code_roi_full.md:77-78]()

## Common Infrastructure Endpoints

Different monitoring platforms provide OTLP-compatible endpoints with specific configuration requirements.

### Platform-Specific Configuration

| Platform | Endpoint | Protocol | Authentication |
|----------|----------|----------|----------------|
| Local Development | `http://localhost:4317` | gRPC | None |
| Kubernetes | `http://otel-collector.monitoring.svc.cluster.local:4317` | gRPC | Service mesh |
| DataDog | `https://otlp.datadoghq.com` | HTTPS | DD-API-KEY header |
| Honeycomb | `https://api.honeycomb.io:443` | HTTPS | x-honeycomb-team header |
| AWS Load Balancer | Custom ALB endpoint | gRPC/HTTPS | IAM or API key |

### Configuration Examples

Complete configuration examples for common scenarios:

```bash
# Local development
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Kubernetes deployment
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector.monitoring.svc.cluster.local:4317

# DataDog integration
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.datadoghq.com
export OTEL_EXPORTER_OTLP_HEADERS="DD-API-KEY=your-datadog-api-key"
```

**Sources:** [claude_code_roi_full.md:84-90]()

## Troubleshooting Configuration Issues

Common telemetry configuration problems and their resolution.

### Configuration Validation

Verify all required environment variables are set correctly:

```bash
echo $CLAUDE_CODE_ENABLE_TELEMETRY  # Should be 1
echo $OTEL_METRICS_EXPORTER          # Should be otlp
echo $OTEL_EXPORTER_OTLP_ENDPOINT    # Should be your collector endpoint
```

### Connectivity Testing

Test endpoint accessibility before configuring Claude Code:

```bash
# Test gRPC endpoint
curl -v http://localhost:4317

# Test HTTP endpoint  
curl -v http://localhost:4318/v1/metrics
```

### Common Issues and Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| No metrics in Prometheus | Empty dashboards | Verify `CLAUDE_CODE_ENABLE_TELEMETRY=1` |
| Claude Code hanging | Process unresponsive | Clean installation and config reset |
| Authentication failures | 401/403 errors | Verify `OTEL_EXPORTER_OTLP_HEADERS` format |
| Network connectivity | Connection timeouts | Check firewall rules and endpoint URL |

### Configuration Reset Process

For persistent issues, reset Claude Code configuration:

```bash
# Clean installation
npm uninstall -g @anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code

# Clear configuration cache
rm -rf ~/.config/claude-code/

# Restart with fresh configuration
claude
```

**Sources:** [troubleshooting.md:7-35](), [claude_code_roi_full.md:175]()

---

# Page: Telemetry Collection Pipeline

# Telemetry Collection Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [otel-collector-config.yaml](otel-collector-config.yaml)
- [prometheus.yml](prometheus.yml)

</details>



This document details the telemetry collection infrastructure that receives, processes, and stores metrics from Claude Code CLI sessions. The pipeline consists of an OpenTelemetry Collector that receives OTLP data and exports it to Prometheus for storage and querying.

For Claude Code CLI telemetry configuration, see [Claude Code Telemetry Configuration](#2.2). For visualization and dashboards, see [Monitoring and Visualization](#4). For automated report generation using collected metrics, see [Automated Reporting System](#5).

## Pipeline Architecture Overview

The telemetry collection pipeline implements a standard observability stack using OpenTelemetry and Prometheus components. Claude Code CLI exports metrics via OTLP protocol to the collector, which processes and forwards them to Prometheus for time-series storage.

### Core Pipeline Components

```mermaid
graph TB
    subgraph "Claude Code CLI"
        CLI["claude CLI"]
        OTLP_Client["OTLP Exporter"]
    end
    
    subgraph "OpenTelemetry Collector"
        OTLP_Receiver["otlp receiver<br/>:4317 gRPC<br/>:4318 HTTP"]
        Memory_Limiter["memory_limiter<br/>512 MiB limit"]
        Batch_Processor["batch processor<br/>1024 items/1s timeout"]
        Prom_Exporter["prometheus exporter<br/>:8889 endpoint"]
        Debug_Exporter["debug exporter<br/>detailed verbosity"]
    end
    
    subgraph "Prometheus Server"
        Scraper["prometheus scraper<br/>15s interval"]
        TSDB["prometheus TSDB<br/>metrics storage"]
    end
    
    CLI --> OTLP_Client
    OTLP_Client -->|"OTLP/gRPC :4317<br/>OTLP/HTTP :4318"| OTLP_Receiver
    OTLP_Receiver --> Memory_Limiter
    Memory_Limiter --> Batch_Processor
    Batch_Processor --> Prom_Exporter
    Batch_Processor --> Debug_Exporter
    Prom_Exporter -->|"HTTP :8889"| Scraper
    Scraper --> TSDB
```

**Sources:** [otel-collector-config.yaml:1-40](), [prometheus.yml:9-18]()

### Network Endpoints and Protocols

| Component | Endpoint | Protocol | Purpose |
|-----------|----------|----------|---------|
| `otlp` receiver | `0.0.0.0:4317` | gRPC | Primary OTLP ingestion |
| `otlp` receiver | `0.0.0.0:4318` | HTTP | Alternative OTLP ingestion |
| `prometheus` exporter | `0.0.0.0:8889` | HTTP | Metrics exposition |
| `prometheus` scraper | `otel-collector:8889` | HTTP | Metrics collection |
| `prometheus` server | `localhost:9090` | HTTP | Query interface |

**Sources:** [otel-collector-config.yaml:4-7, 18-19](), [prometheus.yml:13, 18]()

## OpenTelemetry Collector Configuration

The collector uses a pipeline architecture with receivers, processors, and exporters defined in [otel-collector-config.yaml]().

### Receiver Configuration

The `otlp` receiver accepts telemetry data from Claude Code CLI on dual protocols:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
```

**Sources:** [otel-collector-config.yaml:1-7]()

### Processing Pipeline

Two processors handle resource management and batching:

#### Memory Limiter Processor
Prevents memory exhaustion with a 512 MiB limit and 1-second check intervals:

```yaml
memory_limiter:
  check_interval: 1s
  limit_mib: 512
```

#### Batch Processor
Optimizes export efficiency by batching metrics with 1024-item batches or 1-second timeouts:

```yaml
batch:
  timeout: 1s
  send_batch_size: 1024
```

**Sources:** [otel-collector-config.yaml:9-15]()

### Export Configuration

The collector exports processed metrics to two destinations:

#### Prometheus Exporter
Exposes metrics in Prometheus format with OpenMetrics support and 180-minute expiration:

```yaml
prometheus:
  endpoint: "0.0.0.0:8889"
  send_timestamps: true
  metric_expiration: 180m
  enable_open_metrics: true
```

#### Debug Exporter
Provides detailed logging for troubleshooting with sampling configuration:

```yaml
debug:
  verbosity: detailed
  sampling_initial: 5
  sampling_thereafter: 200
```

**Sources:** [otel-collector-config.yaml:17-27]()

## Prometheus Integration

Prometheus scrapes metrics from the OpenTelemetry Collector's export endpoint and stores them in its time-series database.

### Scrape Configuration

```mermaid
graph LR
    subgraph "Prometheus Scraping"
        Prometheus["prometheus server"]
        Config["prometheus.yml"]
        Job_OTEL["job: otel-collector<br/>target: otel-collector:8889"]
        Job_Self["job: prometheus<br/>target: localhost:9090"]
    end
    
    subgraph "OpenTelemetry Collector"
        OTEL_Exporter["prometheus exporter<br/>:8889"]
    end
    
    Config --> Prometheus
    Prometheus -->|"15s interval"| Job_OTEL
    Prometheus -->|"15s interval"| Job_Self
    Job_OTEL -->|"HTTP GET /metrics"| OTEL_Exporter
```

The scrape configuration defines two jobs with 15-second intervals:

| Job Name | Target | Purpose |
|----------|--------|---------|
| `otel-collector` | `otel-collector:8889` | Scrape Claude Code metrics |
| `prometheus` | `localhost:9090` | Self-monitoring |

**Sources:** [prometheus.yml:1-3, 9-18]()

### Global Configuration

Prometheus uses consistent timing across scraping and evaluation:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
```

**Sources:** [prometheus.yml:1-3]()

## Data Flow and Processing

The complete data flow from Claude Code CLI to Prometheus storage follows this sequence:

```mermaid
sequenceDiagram
    participant CLI as "claude CLI"
    participant OTLP as "OTLP Client"
    participant Receiver as "otlp receiver"
    participant Memory as "memory_limiter"
    participant Batch as "batch processor"
    participant PromExp as "prometheus exporter"
    participant PromScrape as "prometheus scraper"
    participant TSDB as "prometheus TSDB"
    
    CLI->>OTLP: Generate metrics
    Note over CLI,OTLP: claude_code.cost.usage<br/>claude_code.token.usage<br/>claude_code.session.count
    
    OTLP->>Receiver: Export OTLP/gRPC :4317
    Note over Receiver: Receive metrics batch
    
    Receiver->>Memory: Forward metrics
    Memory->>Memory: Check 512 MiB limit
    
    Memory->>Batch: Process if under limit
    Batch->>Batch: Accumulate 1024 items<br/>or 1s timeout
    
    par Prometheus Export
        Batch->>PromExp: Export batch
        PromExp->>PromExp: Convert to Prometheus format
        Note over PromExp: Expose on :8889/metrics
    and Debug Export
        Batch->>Debug: Export batch
        Note over Debug: Log detailed metrics
    end
    
    PromScrape->>PromExp: Scrape every 15s
    PromExp-->>PromScrape: Return metrics
    PromScrape->>TSDB: Store time series
```

**Sources:** [otel-collector-config.yaml:29-34](), [prometheus.yml:11-13]()

### Pipeline Service Definition

The collector service pipeline connects components in sequence:

```yaml
service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus, debug]
```

Processing order ensures memory protection before batching, with parallel export to both Prometheus and debug outputs.

**Sources:** [otel-collector-config.yaml:29-34]()

### Telemetry Logging

The collector itself logs at debug level for troubleshooting pipeline issues:

```yaml
telemetry:
  logs:
    level: "debug"
```

**Sources:** [otel-collector-config.yaml:38-40]()

## Supported Metrics

The pipeline processes Claude Code metrics in standard OpenTelemetry format, converting them to Prometheus metrics for storage and querying. Key metric types include:

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|---------|
| `claude_code_cost_usage_USD_total` | Counter | Session cost in USD | `user.id`, `session.id`, `model` |
| `claude_code_token_usage_tokens_total` | Counter | Token consumption | `user.id`, `session.id`, `model`, `type` |
| `claude_code_session_count_total` | Counter | Session count | `user.id` |

Token types include `input`, `output`, `cacheCreation`, and `cacheRead` for detailed usage analysis.

**Sources:** [claude_code_roi_full.md:96-121]()

---

# Page: OpenTelemetry Collector Configuration

# OpenTelemetry Collector Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker-compose.yml](docker-compose.yml)
- [otel-collector-config.yaml](otel-collector-config.yaml)

</details>



This document covers the configuration and deployment of the OpenTelemetry Collector within the Claude Code ROI measurement system. The collector serves as the central telemetry processing hub, receiving OTLP data from Claude Code sessions and transforming it into Prometheus metrics for storage and analysis.

For information about Prometheus configuration and metrics storage, see [Prometheus Configuration and Metrics Storage](#3.2). For details about available metrics and their structure, see [Available Metrics and Data Model](#3.3).

## Architecture Overview

The OpenTelemetry Collector acts as a bridge between Claude Code's telemetry emission and the monitoring stack. It receives raw telemetry data via OTLP protocols and processes it through a configurable pipeline before exporting to Prometheus.

### Collector Data Flow

```mermaid
flowchart LR
    subgraph "Claude Code Sessions"
        CC["Claude Code CLI"]
        CCU["User Sessions"]
    end
    
    subgraph "OTEL Collector Pipeline"
        RECV["otlp receiver<br/>:4317 gRPC<br/>:4318 HTTP"]
        MEM["memory_limiter<br/>512 MiB"]
        BATCH["batch processor<br/>1024 items/1s"]
        PROM_EXP["prometheus exporter<br/>:8889"]
        DEBUG["debug exporter"]
    end
    
    subgraph "Storage"
        PROM["Prometheus<br/>:9090"]
    end
    
    CC --> CCU
    CCU -->|"OTLP Export"| RECV
    RECV --> MEM
    MEM --> BATCH
    BATCH --> PROM_EXP
    BATCH --> DEBUG
    PROM_EXP -->|"Metrics Scraping"| PROM
```

Sources: [otel-collector-config.yaml:1-40](), [docker-compose.yml:3-13]()

## Receiver Configuration

The collector is configured with OTLP receivers to accept telemetry data from Claude Code sessions on both gRPC and HTTP protocols.

### OTLP Protocol Support

| Protocol | Port | Endpoint | Usage |
|----------|------|----------|-------|
| gRPC | 4317 | `0.0.0.0:4317` | Primary telemetry ingestion |
| HTTP | 4318 | `0.0.0.0:4318` | Alternative telemetry ingestion |

The `otlp` receiver configuration accepts both protocols simultaneously:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
```

Sources: [otel-collector-config.yaml:1-7](), [docker-compose.yml:9-10]()

## Processing Pipeline

The collector implements a two-stage processing pipeline to manage memory usage and optimize batch export operations.

### Pipeline Components

```mermaid
flowchart TD
    subgraph "Processor Chain"
        INPUT["Raw OTLP Data"]
        MEM_LIM["memory_limiter<br/>check_interval: 1s<br/>limit_mib: 512"]
        BATCH_PROC["batch processor<br/>timeout: 1s<br/>send_batch_size: 1024"]
        OUTPUT["Processed Metrics"]
    end
    
    INPUT --> MEM_LIM
    MEM_LIM --> BATCH_PROC
    BATCH_PROC --> OUTPUT
```

### Memory Limiter

The `memory_limiter` processor prevents OOM conditions by monitoring memory usage:

- **Check Interval**: 1 second monitoring frequency
- **Memory Limit**: 512 MiB maximum memory usage
- **Behavior**: Drops data when limit approached

### Batch Processor  

The `batch` processor optimizes export efficiency:

- **Timeout**: 1 second maximum batch wait time
- **Batch Size**: 1024 items per batch
- **Purpose**: Reduces export overhead and improves throughput

Sources: [otel-collector-config.yaml:9-16]()

## Export Configuration

The collector exports processed metrics to two destinations: Prometheus for storage and debug output for troubleshooting.

### Prometheus Exporter

The `prometheus` exporter configuration exposes metrics for Prometheus scraping:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `endpoint` | `0.0.0.0:8889` | Metrics exposure endpoint |
| `send_timestamps` | `true` | Include original timestamps |
| `metric_expiration` | `180m` | Metric cleanup interval |
| `enable_open_metrics` | `true` | OpenMetrics format support |

### Debug Exporter

The `debug` exporter provides detailed logging for troubleshooting:

- **Verbosity**: Detailed output level
- **Sampling Initial**: First 5 messages logged
- **Sampling Thereafter**: Every 200th message logged

Sources: [otel-collector-config.yaml:17-28]()

## Service Pipeline Definition

The collector service defines how components connect in the metrics processing pipeline.

### Pipeline Architecture

```mermaid
flowchart LR
    subgraph "service.pipelines.metrics"
        RECEIVERS["receivers: [otlp]"]
        PROCESSORS["processors:<br/>[memory_limiter, batch]"]
        EXPORTERS["exporters:<br/>[prometheus, debug]"]
    end
    
    RECEIVERS --> PROCESSORS
    PROCESSORS --> EXPORTERS
```

The pipeline configuration explicitly defines the data flow:

```yaml
service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus, debug]
```

Sources: [otel-collector-config.yaml:29-35]()

## Docker Deployment

The collector is deployed as a Docker container with specific configuration and port mappings.

### Container Configuration

The `otel-collector` service in Docker Compose provides:

| Aspect | Configuration | Purpose |
|--------|---------------|---------|
| Image | `otel/opentelemetry-collector-contrib:latest` | Full feature collector distribution |
| Config Mount | `./otel-collector-config.yaml:/etc/otel-collector-config.yaml` | Configuration file binding |
| Dependencies | `depends_on: [prometheus]` | Startup ordering |

### Port Mappings

```mermaid
flowchart LR
    subgraph "Host System"
        HOST_4317["Host :4317"]
        HOST_4318["Host :4318"] 
        HOST_8889["Host :8889"]
    end
    
    subgraph "otel-collector Container"
        CONT_4317["Container :4317<br/>OTLP gRPC"]
        CONT_4318["Container :4318<br/>OTLP HTTP"]
        CONT_8889["Container :8889<br/>Prometheus metrics"]
    end
    
    HOST_4317 --> CONT_4317
    HOST_4318 --> CONT_4318
    HOST_8889 --> CONT_8889
```

Sources: [docker-compose.yml:3-13]()

## Telemetry and Logging

The collector itself emits telemetry about its operation and processing performance.

### Logging Configuration

Debug-level logging is enabled for troubleshooting:

```yaml
telemetry:
  logs:
    level: "debug"
```

This provides detailed information about:
- Data ingestion rates
- Processing pipeline performance  
- Export success/failure rates
- Memory usage patterns

Sources: [otel-collector-config.yaml:38-40]()

## Configuration Best Practices

### Memory Management

The 512 MiB memory limit is configured to handle typical Claude Code usage patterns while preventing resource exhaustion. Monitor memory usage and adjust based on actual telemetry volumes.

### Batch Processing

The 1-second timeout and 1024-item batch size balance latency with throughput. For high-volume environments, consider increasing batch sizes.

### Metric Retention

The 180-minute metric expiration prevents unbounded memory growth from stale metrics while maintaining reasonable freshness for dashboard queries.

Sources: [otel-collector-config.yaml:10-22]()

---

# Page: Prometheus Configuration and Metrics Storage

# Prometheus Configuration and Metrics Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [prometheus.yml](prometheus.yml)

</details>



This document covers the configuration of Prometheus as the time-series database for storing Claude Code telemetry metrics scraped from the OpenTelemetry Collector. It includes scrape configuration, storage settings, and essential queries for ROI analysis.

For OpenTelemetry Collector setup and pipeline configuration, see [OpenTelemetry Collector Configuration](#3.1). For detailed metric definitions and data models, see [Available Metrics and Data Model](#3.3).

## Configuration File Structure

Prometheus is configured through the `prometheus.yml` file which defines global settings, scrape targets, and storage behavior. The configuration follows a hierarchical structure with global defaults and job-specific overrides.

**Prometheus Configuration Architecture**
```mermaid
graph TB
    subgraph "prometheus.yml"
        global["global"]
        rule_files["rule_files"]
        scrape_configs["scrape_configs"]
    end
    
    subgraph "Global Settings"
        scrape_interval["scrape_interval: 15s"]
        evaluation_interval["evaluation_interval: 15s"]
    end
    
    subgraph "Scrape Jobs"
        otel_job["job_name: 'otel-collector'"]
        prom_job["job_name: 'prometheus'"]
    end
    
    subgraph "Target Endpoints"
        otel_target["targets: ['otel-collector:8889']"]
        prom_target["targets: ['localhost:9090']"]
    end
    
    global --> scrape_interval
    global --> evaluation_interval
    scrape_configs --> otel_job
    scrape_configs --> prom_job
    otel_job --> otel_target
    prom_job --> prom_target
```

Sources: [prometheus.yml:1-23]()

## Scrape Target Configuration

The primary scrape configuration targets the OpenTelemetry Collector's metrics endpoint where Claude Code telemetry is exported. The collector exposes metrics on port 8889 using the Prometheus exposition format.

| Configuration Key | Value | Purpose |
|------------------|-------|---------|
| `scrape_interval` | `15s` | Frequency of metric collection from targets |
| `evaluation_interval` | `15s` | Frequency of rule evaluation (if rules are configured) |
| `job_name: 'otel-collector'` | `otel-collector:8889` | Primary target for Claude Code metrics |
| `job_name: 'prometheus'` | `localhost:9090` | Self-monitoring of Prometheus instance |

The OpenTelemetry Collector target configuration uses Docker Compose service name resolution where `otel-collector` resolves to the collector container's internal IP address.

**Scrape Target Data Flow**
```mermaid
graph LR
    subgraph "Claude Code CLI"
        claude_sessions["claude sessions"]
        otlp_export["OTLP export :4317/:4318"]
    end
    
    subgraph "OpenTelemetry Collector"
        otlp_receiver["otlp receiver"]
        prometheus_exporter["prometheus exporter :8889"]
    end
    
    subgraph "Prometheus Server"
        scrape_job["otel-collector scrape job"]
        tsdb["Time Series Database"]
    end
    
    claude_sessions --> otlp_export
    otlp_export --> otlp_receiver
    otlp_receiver --> prometheus_exporter
    prometheus_exporter -->|"HTTP GET /metrics every 15s"| scrape_job
    scrape_job --> tsdb
```

Sources: [prometheus.yml:9-18](), [claude_code_roi_full.md:54-90]()

## Metrics Storage and Retention

Prometheus stores Claude Code metrics as time-series data with default retention policies. The storage engine uses a local time-series database optimized for high-cardinality metrics with label-based querying.

### Storage Characteristics

| Aspect | Configuration | Impact |
|--------|---------------|--------|
| **Retention Period** | Default 15 days | Configurable via `--storage.tsdb.retention.time` |
| **Scrape Frequency** | 15 seconds | Defined in `scrape_interval` |
| **Data Points per Day** | 5,760 per metric | (24 hours × 60 minutes × 4 scrapes/minute) |
| **Label Cardinality** | Variable | Based on user count, models, session IDs |

### Key Storage Considerations

- **High Cardinality**: Claude Code metrics include labels for `user.id`, `session.id`, and `model` which create unique time-series
- **Cost Tracking Precision**: USD values stored with sub-cent precision for accurate cost aggregation
- **Token Counting**: Large integer values for cumulative token usage across sessions

Sources: [prometheus.yml:1-4](), [claude_code_roi_full.md:91-121]()

## Key Claude Code Metrics in Prometheus

Claude Code exports several metric families that appear in Prometheus with specific naming conventions. The OTEL Collector transforms OTLP metrics into Prometheus-compatible format with appropriate suffixes.

### Primary Metric Families

| Prometheus Metric Name | Type | Labels | Purpose |
|----------------------|------|--------|---------|
| `claude_code_cost_usage_USD_total` | Counter | `user_email`, `model`, `session_id` | Cumulative cost tracking |
| `claude_code_token_usage_tokens_total` | Counter | `type`, `user_email`, `model` | Token consumption by type |
| `claude_code_session_count_total` | Counter | `user_email` | Session initiation tracking |
| `claude_code_pull_request_count_total` | Counter | `user_email` | Development velocity indicator |

### Label Dimensions

The metrics include several important label dimensions for segmentation:

- **`user_email`**: Identifies individual developers for per-user analysis
- **`model`**: Tracks usage across different Claude models (`claude-4-sonnet-20250514`, `claude-3-5-haiku-20241022`)
- **`type`**: For token metrics, distinguishes `input`, `output`, `cacheCreation`, `cacheRead`
- **`session_id`**: Unique identifier for individual Claude Code sessions

**Metrics Label Structure**
```mermaid
graph TB
    subgraph "claude_code_cost_usage_USD_total"
        cost_labels["user_email, model, session_id"]
    end
    
    subgraph "claude_code_token_usage_tokens_total"
        token_labels["type, user_email, model"]
        token_types["type: input|output|cacheCreation|cacheRead"]
    end
    
    subgraph "claude_code_session_count_total"
        session_labels["user_email"]
    end
    
    token_labels --> token_types
```

Sources: [claude_code_roi_full.md:95-121]()

## Essential Queries for ROI Analysis

Prometheus Query Language (PromQL) enables powerful aggregation and analysis of Claude Code usage patterns. These queries form the foundation for cost analysis, productivity measurement, and resource planning.

### Cost Analysis Queries

```promql
# Total organizational spend
sum(claude_code_cost_usage_USD_total)

# Cost breakdown by model
sum(claude_code_cost_usage_USD_total) by (model)

# Top spending users
topk(10, sum(claude_code_cost_usage_USD_total) by (user_email))

# Daily cost rate (requires time range)
rate(claude_code_cost_usage_USD_total[24h])
```

### Token Usage Analysis

```promql
# Total tokens by type
sum(claude_code_token_usage_tokens_total) by (type)

# Cache efficiency ratio
sum(claude_code_token_usage_tokens_total{type="cacheRead"}) / 
sum(claude_code_token_usage_tokens_total{type="cacheCreation"})

# Input vs output token ratio per user
sum(claude_code_token_usage_tokens_total{type="output"}) by (user_email) /
sum(claude_code_token_usage_tokens_total{type="input"}) by (user_email)
```

### Productivity Queries

```promql
# Sessions per user
sum(claude_code_session_count_total) by (user_email)

# Cost per session
sum(claude_code_cost_usage_USD_total) by (user_email) /
sum(claude_code_session_count_total) by (user_email)

# Active users in time window
count(count by (user_email) (rate(claude_code_session_count_total[7d])))
```

Sources: [claude_code_roi_full.md:95-121]()

## Integration with OTEL Collector Pipeline

Prometheus operates as the storage backend in the telemetry pipeline, receiving processed metrics from the OpenTelemetry Collector. The integration relies on the collector's Prometheus exporter which transforms OTLP metrics into Prometheus exposition format.

**Complete Pipeline Integration**
```mermaid
flowchart LR
    subgraph "Claude Code"
        sessions["Sessions with telemetry enabled"]
        otlp_client["OTLP client export"]
    end
    
    subgraph "OpenTelemetry Collector :4317/:4318"
        receivers["OTLP receivers"]
        processors["Memory limiter + Batch processor"]
        exporters["Prometheus exporter :8889"]
    end
    
    subgraph "Prometheus :9090"
        scraper["Scraper job: otel-collector"]
        storage["TSDB storage"]
        query_api["Query API /api/v1/query"]
    end
    
    subgraph "Downstream Consumers"
        grafana["Grafana dashboards"]
        report_gen["Report generation scripts"]
    end
    
    sessions --> otlp_client
    otlp_client -->|"gRPC/HTTP OTLP"| receivers
    receivers --> processors
    processors --> exporters
    exporters -->|"Prometheus metrics format"| scraper
    scraper --> storage
    storage --> query_api
    query_api --> grafana
    query_api --> report_gen
```

### Configuration Dependencies

The Prometheus configuration must align with the OpenTelemetry Collector's exporter configuration:

- **Exporter Endpoint**: Collector exposes metrics on `:8889` which matches the scrape target
- **Service Discovery**: Uses Docker Compose service name `otel-collector` for container-to-container communication
- **Metric Format**: Collector transforms OTLP metrics to Prometheus exposition format automatically

Sources: [prometheus.yml:10-14](), [claude_code_roi_full.md:54-90]()

## Storage Optimization and Scaling

For production deployments, Prometheus storage requires consideration of metric cardinality and retention policies. Claude Code metrics can generate high cardinality due to unique session IDs and user identifiers.

### Cardinality Management

- **Session ID Impact**: Each Claude Code session creates a unique `session_id` label value
- **User Scaling**: Label cardinality increases linearly with user count
- **Model Variants**: Different Claude models create additional label combinations

### Retention Strategies

```bash
# Configure retention via command line flags
--storage.tsdb.retention.time=200h   # Retain ~8 days of data
--storage.tsdb.retention.size=10GB   # Size-based retention limit
```

For large deployments, consider implementing recording rules to pre-aggregate frequently queried metrics and reduce query load.

Sources: [claude_code_roi_full.md:54-64]()

---

# Page: Available Metrics and Data Model

# Available Metrics and Data Model

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [grafana/dashboards/working-dashboard.json](grafana/dashboards/working-dashboard.json)

</details>



This document describes the complete data model and metric schema for Claude Code telemetry collection in the ROI measurement system. It covers the structure of OpenTelemetry metrics emitted by Claude Code CLI, their labels and dimensions, and how they're stored and queried in Prometheus.

For information about configuring telemetry collection, see [OpenTelemetry Collector Configuration](#3.1). For visualization and dashboard setup, see [Grafana Dashboard Setup](#4.1).

## Metric Naming Convention and Structure

Claude Code follows OpenTelemetry semantic conventions with a standardized naming pattern. All metrics use the `claude_code` prefix and are exported as counters to track cumulative values over time.

### Metric Name Pattern
```
claude_code.<domain>.<metric_name>_<unit>_total
```

The Prometheus exporter automatically appends `_total` suffix to counter metrics and converts units to standardized forms (e.g., `USD` for currency, `tokens` for token counts).

**Core Metric Domains:**
- `cost` - Financial tracking for API usage
- `token` - Token consumption and caching metrics  
- `session` - Session lifecycle and duration
- `lines_of_code` - Code modification tracking
- `pull_request` - Development productivity indicators
- `commit` - Version control activity
- `code_edit_tool` - Tool interaction and acceptance rates

Sources: [claude_code_roi_full.md:34-51](), [grafana/dashboards/working-dashboard.json:82-87]()

## Core Metrics Schema

### Cost Tracking Metrics

#### `claude_code_cost_usage_USD_total`
Cumulative cost counter tracking API usage charges in USD.

```promql
# Metric structure
claude_code_cost_usage_USD_total{
  user_id="7b673f5715f2da49af2cdd341e0cad17fb3274f32d4ceed00d57d53da4e76fb2",
  session_id="092d99fc-ac17-4ee7-b310-57d387777c91", 
  model="claude-4-sonnet-20250514",
  user_email="user@company.com"
}
```

**Labels:**
- `user_id` - SHA256 hash of user identifier for privacy
- `session_id` - UUID for individual Claude Code sessions
- `model` - Claude model used (haiku, sonnet, opus variants)
- `user_email` - User email for organizational reporting

Sources: [claude_code_roi_full.md:44-48](), [grafana/dashboards/working-dashboard.json:343-348]()

### Token Usage Metrics

#### `claude_code_token_usage_tokens_total`
Cumulative token counter with breakdown by usage type and caching efficiency.

```promql
# Token types and their meanings
claude_code_token_usage_tokens_total{type="input"}         # User prompt tokens
claude_code_token_usage_tokens_total{type="output"}        # Claude response tokens  
claude_code_token_usage_tokens_total{type="cacheCreation"} # New cache entries
claude_code_token_usage_tokens_total{type="cacheRead"}     # Cache hits
```

**Cache Efficiency Analysis:**
Cache efficiency can be calculated as `cacheRead / (cacheCreation + cacheRead)` ratio. High cache hit ratios (>90%) indicate effective prompt caching and cost optimization.

Sources: [claude_code_roi_full.md:101-105](), [grafana/dashboards/working-dashboard.json:411-416]()

### Development Productivity Metrics

#### `claude_code_lines_of_code_count_total`
Code modification tracking with operation type classification.

```promql
claude_code_lines_of_code_count_total{type="added"}    # New code lines
claude_code_lines_of_code_count_total{type="modified"} # Changed lines
claude_code_lines_of_code_count_total{type="deleted"}  # Removed lines
```

#### `claude_code_pull_request_count_total`
Pull request creation counter indicating feature completion velocity.

#### `claude_code_commit_count_total` 
Commit activity tracking for development workflow analysis.

Sources: [claude_code_roi_full.md:203-205](), [grafana/dashboards/working-dashboard.json:275-281]()

## Label Taxonomy and Cardinality

### High-Cardinality Labels
Labels that create many unique time series and require careful monitoring:

**User Dimensions:**
- `user_id` - Unique per developer (cardinality: number of active developers)
- `session_id` - Unique per CLI session (cardinality: sessions per day × retention period)
- `user_email` - For organizational reporting (cardinality: team size)

**Model Dimensions:**
- `model` - Claude model variants (cardinality: ~10-15 model versions)

### Low-Cardinality Labels
Stable dimensions suitable for grouping and filtering:

**Type Classifications:**
- `type` - Token types, edit operations, decision outcomes (cardinality: 2-5 per metric)

### Label Structure Diagram

```mermaid
graph TD
    subgraph "User Identity"
        UI["user_id"] 
        UE["user_email"]
    end
    
    subgraph "Session Context"
        SI["session_id"]
        ST["session.start_time"]
    end
    
    subgraph "Model & Cost"
        MD["model"]
        PR["pricing_tier"]
    end
    
    subgraph "Activity Type"
        TY["type"]
        OP["operation"]
        DC["decision"]
    end
    
    UI --> Cost["claude_code_cost_usage_USD_total"]
    UE --> Cost
    SI --> Cost
    MD --> Cost
    
    UI --> Tokens["claude_code_token_usage_tokens_total"]
    SI --> Tokens
    MD --> Tokens
    TY --> Tokens
    
    UI --> LOC["claude_code_lines_of_code_count_total"]
    SI --> LOC
    TY --> LOC
```

Sources: [claude_code_roi_full.md:44-48](), [grafana/dashboards/working-dashboard.json:343-348]()

## Data Collection Flow

### Telemetry Pipeline Architecture

```mermaid
flowchart TD
    subgraph "Claude Code CLI"
        CC["Claude Code Process"]
        TM["Telemetry Module"]
        OE["OTEL Exporter"]
    end
    
    subgraph "Collection Pipeline"
        GR["OTLP gRPC Receiver:4317"]
        HT["OTLP HTTP Receiver:4318"]
        MP["Memory Limiter"]
        BP["Batch Processor"]
        PE["Prometheus Exporter:8889"]
    end
    
    subgraph "Storage Layer"
        PS["Prometheus Server:9090"]
        TS["Time Series Storage"]
    end
    
    CC --> TM
    TM --> OE
    OE -->|"OTLP Protocol"| GR
    OE -->|"HTTP Fallback"| HT
    
    GR --> MP
    HT --> MP
    MP --> BP
    BP --> PE
    
    PE -->|"Scrape /metrics"| PS
    PS --> TS
```

Sources: [claude_code_roi_full.md:69-82]()

### Metric Emission Trigger Points

Claude Code emits metrics at specific lifecycle events:

**Session Metrics:**
- Session start: `claude_code_session_count_total`
- Session end: Duration and summary metrics

**Cost Metrics:**
- API request completion: `claude_code_cost_usage_USD_total`
- Token consumption: `claude_code_token_usage_tokens_total`

**Development Metrics:**
- Code edit tool usage: `claude_code_code_edit_tool_decision`
- File modifications: `claude_code_lines_of_code_count_total`
- Git operations: `claude_code_commit_count_total`, `claude_code_pull_request_count_total`

Sources: [claude_code_roi_full.md:214-217]()

## Common Query Patterns

### Cost Analysis Queries

```promql
# Total cost across all sessions
sum(claude_code_cost_usage_USD_total)

# Cost by model type
sum by (model)(claude_code_cost_usage_USD_total)

# Cost per user (top spenders)
sum by (user_email)(claude_code_cost_usage_USD_total)

# Cost rate over time (hourly spend)
rate(claude_code_cost_usage_USD_total[1h])
```

### Token Usage Analytics

```promql
# Token distribution by type
sum by (type)(claude_code_token_usage_tokens_total)

# Cache efficiency ratio
sum(claude_code_token_usage_tokens_total{type="cacheRead"}) / 
sum(claude_code_token_usage_tokens_total{type=~"cache.*"})

# Input vs output token ratio
sum(claude_code_token_usage_tokens_total{type="output"}) /
sum(claude_code_token_usage_tokens_total{type="input"})
```

### Productivity Metrics

```promql
# Active user count
count(count by (user_id)(claude_code_cost_usage_USD_total))

# Lines of code by operation type  
sum by (type)(claude_code_lines_of_code_count_total)

# Cost per pull request
sum(claude_code_cost_usage_USD_total) / 
sum(claude_code_pull_request_count_total)
```

Sources: [claude_code_roi_full.md:95-121](), [grafana/dashboards/working-dashboard.json:82-87]()

## Data Retention and Storage Considerations

### Prometheus Configuration
The system uses default Prometheus retention of 15 days with 15-second scrape intervals. For longer-term analysis, consider:

**Retention Policy:**
- Raw metrics: 15 days (default)
- Aggregated hourly: 90 days  
- Daily summaries: 1 year

**Cardinality Management:**
- Monitor `user_id` and `session_id` cardinality growth
- Use recording rules for frequently-queried aggregations
- Consider metric relabeling for high-cardinality cleanup

### Query Performance Optimization

**Recording Rules Example:**
```yaml
# Pre-computed cost aggregations
groups:
  - name: claude_code_aggregations
    interval: 60s
    rules:
      - record: claude_code:cost_by_user:rate5m
        expr: sum by (user_email)(rate(claude_code_cost_usage_USD_total[5m]))
      
      - record: claude_code:tokens_by_type:rate5m  
        expr: sum by (type)(rate(claude_code_token_usage_tokens_total[5m]))
```

Sources: [grafana/dashboards/working-dashboard.json:82-87](), [claude_code_roi_full.md:95-121]()

---

# Page: Monitoring and Visualization

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

# Page: Grafana Dashboard Setup

# Grafana Dashboard Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker-compose.yml](docker-compose.yml)
- [grafana/dashboards/working-dashboard.json](grafana/dashboards/working-dashboard.json)
- [grafana/provisioning/dashboards/dashboards.yaml](grafana/provisioning/dashboards/dashboards.yaml)

</details>



This document covers the configuration and setup of Grafana dashboards for visualizing Claude Code usage metrics, costs, and productivity data. The dashboard system provides real-time monitoring capabilities by querying metrics stored in Prometheus and presenting them through various visualization panels.

For information about configuring the underlying Prometheus metrics storage, see [Prometheus Configuration and Metrics Storage](#3.2). For details on interpreting the dashboard visualizations, see [Cost and Usage Visualizations](#4.2).

## System Integration Overview

Grafana serves as the visualization layer in the Claude Code ROI measurement pipeline, consuming metrics from Prometheus and presenting them through interactive dashboards.

```mermaid
flowchart TD
    subgraph "Docker Environment"
        CC["claude_code CLI"]
        OTC["otel-collector:4317/4318"]
        PROM["prometheus:9090"]
        GRAF["grafana:3000"]
    end
    
    subgraph "Grafana Configuration"
        PROVISION["/etc/grafana/provisioning"]
        DASHBOARDS["/var/lib/grafana/dashboards"]
        CONFIG["dashboards.yaml"]
    end
    
    subgraph "Dashboard Data Sources"
        PROMETHEUS_DS["Prometheus Datasource<br/>PBFA97CFB590B2093"]
        METRICS["claude_code_cost_usage_USD_total<br/>claude_code_token_usage_tokens_total<br/>claude_code_lines_of_code_count_total"]
    end
    
    CC -->|"OTLP Export"| OTC
    OTC -->|"Metrics"| PROM
    PROM -->|"PromQL Queries"| GRAF
    
    CONFIG --> PROVISION
    PROVISION --> GRAF
    DASHBOARDS --> GRAF
    
    GRAF --> PROMETHEUS_DS
    PROMETHEUS_DS --> METRICS
```

Sources: [docker-compose.yml:32-46](), [grafana/provisioning/dashboards/dashboards.yaml:1-12](), [grafana/dashboards/working-dashboard.json:26-28]()

## Docker Compose Configuration

The Grafana service is defined in the Docker Compose stack with specific volume mounts for provisioning and dashboard persistence.

```mermaid
graph TB
    subgraph "grafana service"
        IMG["grafana/grafana:latest"]
        PORT["3000:3000"]
        ENV["GF_SECURITY_ADMIN_PASSWORD=admin"]
    end
    
    subgraph "Volume Mounts"
        GRAFANA_DATA["grafana_data:/var/lib/grafana"]
        PROVISION_MOUNT["./grafana/provisioning:/etc/grafana/provisioning"]
        DASHBOARD_MOUNT["./grafana/dashboards:/var/lib/grafana/dashboards"]
    end
    
    subgraph "Dependencies"
        PROM_DEP["depends_on: prometheus"]
    end
    
    IMG --> PORT
    ENV --> IMG
    GRAFANA_DATA --> IMG
    PROVISION_MOUNT --> IMG
    DASHBOARD_MOUNT --> IMG
    PROM_DEP --> IMG
```

Sources: [docker-compose.yml:32-46]()

The key configuration elements include:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Image | `grafana/grafana:latest` | Official Grafana container |
| Port | `3000:3000` | Web interface access |
| Admin Password | `admin` | Default login credentials |
| Provisioning Mount | `./grafana/provisioning:/etc/grafana/provisioning` | Auto-configuration |
| Dashboard Mount | `./grafana/dashboards:/var/lib/grafana/dashboards` | Dashboard JSON files |

## Dashboard Provisioning

Dashboard provisioning is configured through the `dashboards.yaml` file, enabling automatic dashboard loading and updates.

```mermaid
graph LR
    subgraph "Provisioning Configuration"
        YAML["dashboards.yaml"]
        PROVIDER["claude-code-dashboards"]
        FOLDER["Claude Code"]
    end
    
    subgraph "File System"
        PATH["/var/lib/grafana/dashboards"]
        JSON["working-dashboard.json"]
    end
    
    subgraph "Grafana Runtime"
        ORG["orgId: 1"]
        UPDATE["updateIntervalSeconds: 10"]
        UI["allowUiUpdates: true"]
    end
    
    YAML --> PROVIDER
    PROVIDER --> FOLDER
    FOLDER --> PATH
    PATH --> JSON
    
    ORG --> PROVIDER
    UPDATE --> PROVIDER
    UI --> PROVIDER
```

Sources: [grafana/provisioning/dashboards/dashboards.yaml:1-12]()

The provisioning configuration includes:

- **Provider Name**: `claude-code-dashboards`
- **Organization**: `orgId: 1` 
- **Folder**: `Claude Code`
- **Update Interval**: `10 seconds`
- **UI Updates**: `allowUiUpdates: true`
- **Path**: `/var/lib/grafana/dashboards`

## Dashboard Structure and Panels

The main dashboard (`working-dashboard.json`) contains multiple visualization panels organized to provide comprehensive Claude Code usage insights.

```mermaid
graph TB
    subgraph "Dashboard Layout: claude-code-working"
        subgraph "Top Row Stats"
            TOTAL_COST["Total Cost<br/>claude_code_cost_usage_USD_total"]
            ACTIVE_USERS["Active Users<br/>count by user_id"]
            TOTAL_TOKENS["Total Tokens<br/>claude_code_token_usage_tokens_total"]
            LINES_CODE["Lines of Code<br/>claude_code_lines_of_code_count_total"]
        end
        
        subgraph "Middle Row Charts"
            COST_MODEL["Cost by Model<br/>sum by model"]
            TOKEN_TYPE["Token Usage by Type<br/>sum by type"]
        end
        
        subgraph "Bottom Row Tables"
            COST_USER["Cost by User<br/>sum by user_id"]
            LINES_TYPE["Lines of Code by Type<br/>sum by type"]
        end
    end
    
    subgraph "Data Source"
        PROMETHEUS["Prometheus<br/>PBFA97CFB590B2093"]
    end
    
    PROMETHEUS --> TOTAL_COST
    PROMETHEUS --> ACTIVE_USERS
    PROMETHEUS --> TOTAL_TOKENS
    PROMETHEUS --> LINES_CODE
    PROMETHEUS --> COST_MODEL
    PROMETHEUS --> TOKEN_TYPE
    PROMETHEUS --> COST_USER
    PROMETHEUS --> LINES_TYPE
```

Sources: [grafana/dashboards/working-dashboard.json:24-625]()

### Panel Configuration Details

| Panel | Type | Query | Grid Position |
|-------|------|-------|---------------|
| Total Cost | `stat` | `sum(increase(claude_code_cost_usage_USD_total[$__range]))` | `h:8, w:6, x:0, y:0` |
| Active Users | `stat` | `count(count by (user_id)(increase(claude_code_cost_usage_USD_total[$__range]) > 0))` | `h:8, w:6, x:6, y:0` |
| Total Tokens | `stat` | `sum(increase(claude_code_token_usage_tokens_total[$__range]))` | `h:8, w:6, x:12, y:0` |
| Lines of Code | `stat` | `sum(increase(claude_code_lines_of_code_count_total[$__range]))` | `h:8, w:6, x:18, y:0` |

Sources: [grafana/dashboards/working-dashboard.json:75-283]()

### Visualization Types

The dashboard employs several visualization types:

- **Stat Panels**: For key metrics display with currency/numeric formatting
- **Pie Charts**: For proportional data (cost by model, token usage by type)
- **Tables**: For detailed breakdowns with sorting capabilities
- **Donut Charts**: For token type distribution visualization

Sources: [grafana/dashboards/working-dashboard.json:314-419]()

## Dashboard Access and Configuration

### Access Credentials

- **URL**: `http://localhost:3000`
- **Username**: `admin`
- **Password**: `admin` (configured via `GF_SECURITY_ADMIN_PASSWORD`)

### Time Range Configuration

The dashboard is configured with:
- **Default Range**: `now-6h` to `now`
- **Refresh Rate**: `30s` auto-refresh
- **Timezone**: Uses browser default

Sources: [grafana/dashboards/working-dashboard.json:637-641](), [grafana/dashboards/working-dashboard.json:627]()

### Dashboard Metadata

| Property | Value |
|----------|-------|
| Title | `Claude Code - Working Dashboard` |
| UID | `claude-code-working` |
| Tags | `["claude-code", "working"]` |
| Schema Version | `37` |
| Style | `dark` |

Sources: [grafana/dashboards/working-dashboard.json:630-646]()

## Prometheus Data Source Integration

The dashboard connects to Prometheus using a pre-configured data source with UID `PBFA97CFB590B2093`. All panels query this data source using PromQL expressions to aggregate Claude Code metrics.

```mermaid
graph LR
    subgraph "PromQL Queries"
        COST_Q["sum(increase(claude_code_cost_usage_USD_total[$__range]))"]
        USER_Q["count(count by (user_id)(increase(...))"]
        TOKEN_Q["sum(increase(claude_code_token_usage_tokens_total[$__range]))"]
        MODEL_Q["sum by (model)(increase(claude_code_cost_usage_USD_total[$__range]))"]
    end
    
    subgraph "Metric Labels"
        USER_ID["user_id"]
        MODEL["model"]
        TYPE["type"]
    end
    
    subgraph "Dashboard Panels"
        STATS["Stat Panels"]
        PIES["Pie Charts"]
        TABLES["Table Views"]
    end
    
    COST_Q --> STATS
    USER_Q --> STATS
    TOKEN_Q --> STATS
    MODEL_Q --> PIES
    
    USER_ID --> TABLES
    MODEL --> PIES
    TYPE --> PIES
```

Sources: [grafana/dashboards/working-dashboard.json:82](), [grafana/dashboards/working-dashboard.json:343](), [grafana/dashboards/working-dashboard.json:501]()

---

# Page: Cost and Usage Visualizations

# Cost and Usage Visualizations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [screenshots/grafana_cost_per_model.png](screenshots/grafana_cost_per_model.png)
- [screenshots/graphan_dashboard_cost_tokens_cost_per_user.png](screenshots/graphan_dashboard_cost_tokens_cost_per_user.png)
- [screenshots/prometheus_cost_time_series.png](screenshots/prometheus_cost_time_series.png)

</details>



This document covers the cost and usage visualization capabilities in the Claude Code ROI measurement system. It explains how to understand and interpret the various dashboards, charts, and metrics displayed in Grafana for analyzing Claude Code usage patterns, costs, and productivity metrics.

For information about setting up Grafana dashboards, see [Grafana Dashboard Setup](#4.1). For dashboard provisioning and automated management, see [Dashboard Provisioning and Management](#4.3). For details on the underlying metrics data model, see [Available Metrics and Data Model](#3.3).

## Overview of Visualization Components

The visualization layer consists of Grafana dashboards that query Prometheus time-series data to display real-time and historical views of Claude Code usage patterns.

### Visualization Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        PROM["Prometheus TSDB<br/>:9090"]
        API["Prometheus API<br/>/api/v1/query"]
    end
    
    subgraph "Grafana Dashboards"
        COST["Cost Per Model<br/>Dashboard"]
        TOKEN["Token Usage<br/>Dashboard"] 
        USER["User Activity<br/>Dashboard"]
        PROD["Productivity<br/>Dashboard"]
    end
    
    subgraph "Chart Types"
        PIE["Pie Charts<br/>Distribution"]
        TS["Time Series<br/>Trends"]
        TABLE["Tables<br/>Rankings"]
        GAUGE["Gauges<br/>Current State"]
    end
    
    PROM --> API
    API --> COST
    API --> TOKEN
    API --> USER
    API --> PROD
    
    COST --> PIE
    COST --> TS
    TOKEN --> TS
    TOKEN --> TABLE
    USER --> TABLE
    USER --> GAUGE
    PROD --> TS
    PROD --> TABLE
```

Sources: `screenshots/grafana_cost_per_model.png`

## Cost Analysis Visualizations

### Cost Per Model Charts

The primary cost visualization shows spending breakdown across different Claude models (`claude-3-sonnet`, `claude-3-haiku`, etc.) used in code generation sessions.

```mermaid
graph LR
    subgraph "Cost Metrics Pipeline"
        CCU["claude_code_usage_total"] --> CALC["Cost Calculation"]
        PRICE["Model Pricing"] --> CALC
        CALC --> VIZ["Cost Visualizations"]
    end
    
    subgraph "Visualization Types"
        VIZ --> PIE_COST["Pie Chart<br/>Model Distribution"]
        VIZ --> TS_COST["Time Series<br/>Cost Trends"]
        VIZ --> TABLE_COST["Table<br/>User Rankings"]
    end
    
    subgraph "Dimensions"
        PIE_COST --> MODEL["By Model Type"]
        TABLE_COST --> USER_DIM["By User"]
        TS_COST --> TIME["Over Time"]
    end
```

#### Key Cost Metrics

| Metric | Description | Query Pattern |
|--------|-------------|---------------|
| `claude_code_cost_total` | Total cost attributed per session | `sum by (model) (claude_code_cost_total)` |
| `claude_code_tokens_total` | Token consumption for cost calculation | `sum by (model, user) (claude_code_tokens_total)` |
| Cost per user | User-specific spending analysis | `sum by (user) (claude_code_cost_total)` |

### Cost Trend Analysis

Time-series visualizations track cost patterns over configurable time windows, helping identify usage spikes and optimization opportunities.

Sources: `screenshots/grafana_cost_per_model.png`

## Token Usage Visualizations

### Token Distribution Charts

Token usage visualizations break down consumption across input tokens, output tokens, and cached tokens for each Claude model.

```mermaid
graph TB
    subgraph "Token Metrics"
        INPUT["claude_code_input_tokens"]
        OUTPUT["claude_code_output_tokens"] 
        CACHE["claude_code_cached_tokens"]
    end
    
    subgraph "Aggregation Dimensions"
        MODEL_AGG["By Model"]
        USER_AGG["By User"]
        SESSION_AGG["By Session"]
        TOOL_AGG["By Tool Usage"]
    end
    
    subgraph "Chart Types"
        STACKED["Stacked Area<br/>Token Types"]
        HEATMAP["Heatmap<br/>Usage Patterns"]
        BAR["Bar Chart<br/>Comparisons"]
    end
    
    INPUT --> MODEL_AGG
    OUTPUT --> USER_AGG
    CACHE --> SESSION_AGG
    
    MODEL_AGG --> STACKED
    USER_AGG --> HEATMAP
    SESSION_AGG --> BAR
    TOOL_AGG --> BAR
```

#### Token Efficiency Metrics

| Visualization | Purpose | PromQL Query Example |
|---------------|---------|---------------------|
| Input vs Output Ratio | Efficiency analysis | `claude_code_output_tokens / claude_code_input_tokens` |
| Cache Hit Rate | Caching effectiveness | `claude_code_cached_tokens / (claude_code_input_tokens + claude_code_cached_tokens)` |
| Token Velocity | Tokens per time unit | `rate(claude_code_tokens_total[5m])` |

Sources: `screenshots/grafana_cost_per_model.png`

## User Activity Visualizations

### User Rankings and Activity Tables

User activity dashboards rank users by various metrics including total cost, token consumption, and session frequency.

```mermaid
graph LR
    subgraph "User Metrics Collection"
        SESSIONS["claude_code_sessions_total"]
        USER_COST["claude_code_cost_total{user=*}"]
        USER_TOKENS["claude_code_tokens_total{user=*}"]
    end
    
    subgraph "Ranking Tables"
        TOP_COST["Top Users by Cost"]
        TOP_USAGE["Top Users by Usage"]
        TOP_SESSIONS["Most Active Users"]
    end
    
    subgraph "Activity Patterns"
        HOURLY["Hourly Usage Heatmap"]
        DAILY["Daily Activity Trends"]
        TOOL_PREF["Tool Preferences"]
    end
    
    USER_COST --> TOP_COST
    USER_TOKENS --> TOP_USAGE
    SESSIONS --> TOP_SESSIONS
    
    SESSIONS --> HOURLY
    SESSIONS --> DAILY
    USER_TOKENS --> TOOL_PREF
```

### Activity Pattern Analysis

- **Peak Usage Hours**: Heatmap showing when Claude Code is most actively used
- **Tool Preferences**: Distribution of `edit`, `write`, `read`, and `bash` tool usage by user
- **Session Duration**: Average session length and productivity correlation

Sources: Based on system architecture diagrams

## Productivity Metrics Visualizations  

### Code Generation Efficiency

Productivity visualizations combine Claude Code metrics with development workflow data to measure AI coding tool effectiveness.

```mermaid
graph TB
    subgraph "Productivity Inputs"
        TOOLS["Tool Usage Metrics<br/>edit/write/read/bash"]
        TIME["Session Duration"]
        OUTPUT["Code Generated"]
        QUALITY["Success Rates"]
    end
    
    subgraph "Efficiency Calculations"
        VELOCITY["Code Velocity<br/>Lines/Hour"]
        ACCURACY["Tool Success Rate<br/>%Successful Operations"]
        COST_EFF["Cost Efficiency<br/>$/Feature"]
    end
    
    subgraph "Trend Visualizations"
        PERF_TREND["Performance Over Time"]
        USER_COMP["User Comparisons"]
        TEAM_METRICS["Team Productivity"]
    end
    
    TOOLS --> VELOCITY
    TIME --> VELOCITY
    OUTPUT --> VELOCITY
    
    QUALITY --> ACCURACY
    TOOLS --> ACCURACY
    
    VELOCITY --> PERF_TREND
    ACCURACY --> USER_COMP
    COST_EFF --> TEAM_METRICS
```

#### Key Productivity Indicators

| KPI | Calculation | Interpretation |
|-----|-------------|----------------|
| Tool Efficiency | `successful_operations / total_operations` | Higher values indicate better prompt engineering |
| Cost per Feature | `total_cost / features_delivered` | Lower values show cost-effective usage |
| Token Efficiency | `output_tokens / input_tokens` | Measures prompt effectiveness |

Sources: Based on system overview and telemetry pipeline documentation

## Dashboard Navigation and Interpretation

### Reading Cost Visualizations

1. **Pie Charts**: Show distribution percentages across models or users
2. **Time Series**: Identify trends, spikes, and usage patterns over time  
3. **Tables**: Provide detailed breakdowns with sortable columns
4. **Gauges**: Display current usage against defined thresholds

### Filtering and Drilling Down

Grafana dashboards support filtering by:
- Time range (15m, 1h, 6h, 12h, 1d, 7d, 30d)
- User groups or individual users  
- Model types (`claude-3-sonnet`, `claude-3-haiku`, etc.)
- Tool types (`edit`, `write`, `read`, `bash`)

### Alert Thresholds

Key metrics have configurable alert thresholds:
- Cost per user per day
- Token consumption rate
- Failed operation percentages
- Unusual usage pattern detection

Sources: `screenshots/grafana_cost_per_model.png`, system architecture documentation

---

# Page: Dashboard Provisioning and Management

# Dashboard Provisioning and Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker-compose.yml](docker-compose.yml)
- [grafana/provisioning/dashboards/dashboards.yaml](grafana/provisioning/dashboards/dashboards.yaml)

</details>



This document covers the automated provisioning, configuration management, and updating procedures for Grafana dashboards in the Claude Code ROI measurement system. It focuses on the infrastructure-as-code approach used to manage dashboard definitions and their deployment lifecycle.

For information about dashboard content and visualization setup, see [Grafana Dashboard Setup](#4.1). For details about the specific metrics and charts displayed, see [Cost and Usage Visualizations](#4.2).

## Provisioning Architecture Overview

The system uses Grafana's built-in provisioning capabilities to automatically deploy and manage dashboards without manual intervention. This approach ensures consistent dashboard deployment across environments and enables version control of dashboard definitions.

### Grafana Provisioning Structure

```mermaid
graph TB
    subgraph "docker-compose.yml"
        grafana["grafana service"]
        vol1["./grafana/provisioning:/etc/grafana/provisioning"]
        vol2["./grafana/dashboards:/var/lib/grafana/dashboards"]
    end
    
    subgraph "Host Filesystem"
        prov_dir["./grafana/provisioning/"]
        dash_dir["./grafana/dashboards/"]
        yaml_file["dashboards.yaml"]
    end
    
    subgraph "Container Filesystem"
        etc_prov["/etc/grafana/provisioning/"]
        var_lib["/var/lib/grafana/dashboards/"]
        loaded_config["dashboards.yaml (loaded)"]
    end
    
    subgraph "Grafana Runtime"
        provider["claude-code-dashboards provider"]
        folder["Claude Code folder"]
        auto_scan["updateIntervalSeconds: 10"]
    end
    
    grafana --> vol1
    grafana --> vol2
    prov_dir --> yaml_file
    dash_dir --> |"JSON files"| var_lib
    
    vol1 --> etc_prov
    vol2 --> var_lib
    yaml_file --> loaded_config
    
    loaded_config --> provider
    provider --> folder
    provider --> auto_scan
    
    auto_scan -.-> |"scans every 10s"| var_lib
```

**Sources:** [docker-compose.yml:32-46](), [grafana/provisioning/dashboards/dashboards.yaml:1-12]()

## Dashboard Provider Configuration

The dashboard provisioning is configured through the `dashboards.yaml` file which defines how Grafana discovers and loads dashboard definitions.

### Provider Configuration Structure

| Configuration Key | Value | Purpose |
|------------------|-------|---------|
| `apiVersion` | `1` | Grafana provisioning API version |
| `name` | `claude-code-dashboards` | Unique provider identifier |
| `orgId` | `1` | Target Grafana organization |
| `folder` | `Claude Code` | Dashboard folder in Grafana UI |
| `type` | `file` | Filesystem-based provider |
| `disableDeletion` | `false` | Allow dashboard deletion |
| `updateIntervalSeconds` | `10` | Scan frequency for changes |
| `allowUiUpdates` | `true` | Permit manual dashboard edits |
| `options.path` | `/var/lib/grafana/dashboards` | Source directory path |

### Configuration Flow

```mermaid
sequenceDiagram
    participant startup as "Grafana Startup"
    participant config as "dashboards.yaml"
    participant provider as "claude-code-dashboards"
    participant scanner as "File Scanner"
    participant ui as "Grafana UI"
    
    startup->>config: "Load provisioning config"
    config->>provider: "Create provider instance"
    provider->>scanner: "Initialize with path=/var/lib/grafana/dashboards"
    
    loop "Every 10 seconds"
        scanner->>scanner: "Scan for .json files"
        scanner->>provider: "Report changes"
        provider->>ui: "Update Claude Code folder"
    end
    
    Note over ui: "allowUiUpdates: true enables manual edits"
    Note over provider: "disableDeletion: false allows removal"
```

**Sources:** [grafana/provisioning/dashboards/dashboards.yaml:1-12]()

## Volume Mounting and File Organization

The Docker Compose configuration establishes the file system mapping that enables dashboard provisioning to function.

### Volume Mount Configuration

The Grafana service mounts two critical directories:

```mermaid
graph LR
    subgraph "Host System"
        host_prov["./grafana/provisioning"]
        host_dash["./grafana/dashboards"]
    end
    
    subgraph "grafana container"
        cont_prov["/etc/grafana/provisioning"]
        cont_dash["/var/lib/grafana/dashboards"]
    end
    
    subgraph "Grafana Process"
        config_loader["Configuration Loader"]
        dashboard_provider["Dashboard Provider"]
        file_watcher["File Watcher"]
    end
    
    host_prov --> |"volume mount"| cont_prov
    host_dash --> |"volume mount"| cont_dash
    
    cont_prov --> config_loader
    cont_dash --> dashboard_provider
    dashboard_provider --> file_watcher
    
    file_watcher -.-> |"monitors"| cont_dash
```

**Sources:** [docker-compose.yml:40-43]()

### Directory Structure

The expected file system layout for dashboard management:

```
grafana/
├── provisioning/
│   └── dashboards/
│       └── dashboards.yaml       # Provider configuration
└── dashboards/                   # Dashboard JSON files
    ├── claude-cost-analysis.json # (example dashboard file)
    ├── token-usage-metrics.json  # (example dashboard file)
    └── productivity-overview.json # (example dashboard file)
```

## Update Management and Lifecycle

The provisioning system provides automated dashboard lifecycle management with configurable update behavior.

### Update Detection Mechanism

```mermaid
stateDiagram-v2
    [*] --> Scanning
    
    state "File System Scanner" as Scanning {
        [*] --> CheckInterval
        CheckInterval --> ScanDirectory
        ScanDirectory --> CompareChecksums
        CompareChecksums --> CheckInterval: "No changes"
        CompareChecksums --> ReloadDashboard: "Changes detected"
        ReloadDashboard --> CheckInterval
    }
    
    state "Dashboard States" as States {
        [*] --> Loaded
        Loaded --> Modified: "UI changes (allowUiUpdates: true)"
        Modified --> Overwritten: "File system change"
        Overwritten --> Loaded
        Loaded --> Deleted: "File removed (disableDeletion: false)"
        Deleted --> [*]
    }
    
    Scanning --> States: "updateIntervalSeconds: 10"
```

### Configuration Parameters Impact

| Parameter | Value | Behavior |
|-----------|-------|----------|
| `updateIntervalSeconds: 10` | 10 seconds | Dashboard changes detected within 10 seconds |
| `allowUiUpdates: true` | Enabled | Manual dashboard edits permitted but may be overwritten |
| `disableDeletion: false` | Disabled | Dashboards can be removed by deleting JSON files |

**Sources:** [grafana/provisioning/dashboards/dashboards.yaml:8-11]()

## Operational Procedures

### Adding New Dashboards

1. Create dashboard JSON file in `./grafana/dashboards/` directory
2. File will be automatically detected within 10 seconds
3. Dashboard appears in "Claude Code" folder in Grafana UI

### Updating Existing Dashboards

1. Modify JSON file in `./grafana/dashboards/` directory
2. Changes automatically applied within `updateIntervalSeconds` interval
3. Any manual UI changes are overwritten by file system version

### Dashboard Backup and Recovery

```mermaid
flowchart TD
    manual["Manual Dashboard Edit"] --> ui_state["UI State Changed"]
    ui_state --> backup_decision{"Backup Needed?"}
    
    backup_decision -->|"Yes"| export_json["Export JSON from UI"]
    backup_decision -->|"No"| continue["Continue with file system"]
    
    export_json --> save_file["Save to ./grafana/dashboards/"]
    save_file --> auto_reload["Auto-reload in 10s"]
    auto_reload --> synced["File System ↔ UI Synced"]
    
    continue --> file_update["Update JSON file"]
    file_update --> auto_reload
    
    file_delete["Delete JSON file"] --> dash_removed["Dashboard Removed"]
    dash_removed --> |"disableDeletion: false"| synced
```

**Sources:** [grafana/provisioning/dashboards/dashboards.yaml:8-11](), [docker-compose.yml:40-43]()

---

# Page: Automated Reporting System

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

# Page: Report Generation and Templates

# Report Generation and Templates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [report-generation-prompt.md](report-generation-prompt.md)

</details>



This page covers the automated report generation system that combines Claude Code telemetry metrics with Linear project management data to produce comprehensive ROI analysis reports. The system uses the Claude CLI with structured prompts to generate markdown reports with embedded visualizations.

For information about Linear MCP configuration details, see [Linear MCP Integration](#5.2). For sample reports and interpretation guidance, see [Report Examples and Interpretation](#5.3). For setting up automated scheduling, see [Automation and Scheduling](#5.4).

## Report Generation Architecture

The report generation system leverages multiple data sources and the Claude CLI to produce automated ROI reports. The architecture centers around template-based prompts that fetch live data from Prometheus and Linear.

```mermaid
graph TB
    subgraph "Data Sources"
        PROM["prometheus:9090<br/>Metrics API"]
        LINEAR["Linear MCP<br/>mcp.linear.app/sse"]
        GIT["Git Repository<br/>Commit History"]
    end
    
    subgraph "Template System"
        PROMPT["report-generation-prompt.md<br/>Template Structure"]
        METRICS["metrics JSON<br/>Live Data Fetching"]
        CUSTOM["Custom Templates<br/>Organization-specific"]
    end
    
    subgraph "Generation Engine"
        CLI["claude CLI<br/>-p prompt flag"]
        MCP["Linear MCP Server<br/>npx mcp-remote"]
        FETCH["fetch-claude-metrics.sh<br/>Prometheus Integration"]
    end
    
    subgraph "Output Generation"
        MD["Markdown Reports<br/>sample-report-output.md"]
        VIZ["Mermaid Diagrams<br/>Cost/Usage Charts"]
        EXEC["Executive Summaries<br/>ROI Analysis"]
    end
    
    PROM -->|"HTTP API Queries"| FETCH
    LINEAR -->|"MCP Protocol"| MCP
    GIT -->|"Commit Analysis"| METRICS
    
    FETCH -->|"Live Metrics"| METRICS
    PROMPT -->|"Template Structure"| CLI
    METRICS -->|"Data Injection"| CLI
    CUSTOM -->|"Customization"| CLI
    
    CLI -->|"Report Generation"| MD
    MCP -->|"Project Data"| CLI
    
    MD --> VIZ
    MD --> EXEC
```

Sources: [claude_code_roi_full.md:406-500](), [report-generation-prompt.md:1-80]()

## Template System Overview

The report generation system uses structured prompt templates that combine static analysis instructions with dynamic metric data. Templates are defined as markdown files containing Claude CLI prompts with JSON metric placeholders.

```mermaid
graph LR
    subgraph "Template Components"
        BASE["Base Template<br/>report-generation-prompt.md"]
        METRICS["Metrics Schema<br/>JSON Structure"]
        INSTRUCTIONS["Analysis Instructions<br/>Prompt Content"]
    end
    
    subgraph "Data Injection"
        LIVE["Live Prometheus Data<br/>curl API queries"]
        LINEAR_DATA["Linear Project Data<br/>MCP Integration"]
        CUSTOM_METRICS["Custom Metrics<br/>Organization-specific"]
    end
    
    subgraph "Generated Prompt"
        COMBINED["Combined Prompt<br/>Template + Data"]
        CLAUDE_CMD["claude -p command<br/>Execution"]
    end
    
    BASE -->|"Template Structure"| COMBINED
    METRICS -->|"Data Schema"| LIVE
    INSTRUCTIONS -->|"Analysis Framework"| COMBINED
    
    LIVE -->|"Runtime Values"| COMBINED
    LINEAR_DATA -->|"Project Context"| COMBINED
    CUSTOM_METRICS -->|"Domain-specific"| COMBINED
    
    COMBINED --> CLAUDE_CMD
```

The core template structure includes standardized metric categories and analysis instructions:

| Template Section | Purpose | Data Source |
|------------------|---------|-------------|
| Executive Summary | High-level ROI overview | Aggregated metrics |
| Usage Patterns | Developer engagement analysis | `claude_code_sessions`, `tool_acceptance_rates` |
| Cost Analysis | Financial impact breakdown | `total_cost`, `cost_per_pr` |
| Linear Integration | Project velocity metrics | Linear MCP data |
| Recommendations | Actionable optimization insights | Combined analysis |

Sources: [report-generation-prompt.md:12-54](), [claude_code_roi_full.md:440-453]()

## Prometheus Data Integration

The system fetches live metrics from Prometheus using HTTP API queries and injects them into report templates. This enables reports to reflect current usage patterns and costs.

```mermaid
sequenceDiagram
    participant SCRIPT as "fetch-claude-metrics.sh"
    participant PROM as "prometheus:9090/api/v1/query"
    participant TEMPLATE as "Report Template"
    participant CLAUDE as "claude CLI"
    
    Note over SCRIPT: "Automated Data Fetching"
    SCRIPT->>PROM: "GET sum(claude_code_cost_usage_USD_total)"
    PROM-->>SCRIPT: "total_cost value"
    
    SCRIPT->>PROM: "GET sum(claude_code_token_usage_tokens_total{type=\"input\"})"
    PROM-->>SCRIPT: "input_tokens value"
    
    SCRIPT->>PROM: "GET sum(claude_code_token_usage_tokens_total{type=\"output\"})"
    PROM-->>SCRIPT: "output_tokens value"
    
    Note over SCRIPT: "Data Processing"
    SCRIPT->>SCRIPT: "Calculate cost_per_token = total_cost / (input + output)"
    
    Note over SCRIPT: "Template Injection"
    SCRIPT->>TEMPLATE: "Inject live metrics into JSON structure"
    TEMPLATE->>CLAUDE: "claude -p with live data"
    
    Note over CLAUDE: "Report Generation"
    CLAUDE-->>SCRIPT: "Generated markdown report"
```

The fetch script uses `curl` and `jq` for metric extraction and calculation:

```bash
# Core metric fetching pattern from fetch-claude-metrics.sh
TOTAL_COST=$(curl -s "http://localhost:9090/api/v1/query?query=sum(claude_code_cost_usage_USD_total)" | jq -r '.data.result[0].value[1] // "0"')
INPUT_TOKENS=$(curl -s "http://localhost:9090/api/v1/query?query=sum(claude_code_token_usage_tokens_total{type=\"input\"})" | jq -r '.data.result[0].value[1] // "0"')
```

Sources: [claude_code_roi_full.md:456-477]()

## Linear MCP Integration

The Linear MCP server enables real-time access to project management data within report generation. This integration provides context about team velocity, issue completion, and development progress.

```mermaid
graph TB
    subgraph "MCP Configuration"
        CLAUDE_JSON[".claude.json<br/>MCP Server Config"]
        LINEAR_MCP["Linear MCP Server<br/>mcp.linear.app/sse"]
        NPX_CMD["npx -y mcp-remote<br/>Server Execution"]
    end
    
    subgraph "Data Access"
        TEAM_VEL["Team Velocity<br/>Sprint Analysis"]
        ISSUE_DATA["Issue Completion<br/>Ticket Status"]
        PROJECT_CTX["Project Context<br/>Development Progress"]
    end
    
    subgraph "Report Integration"
        PROMPT_CTX["Prompt Context<br/>Linear Data Integration"]
        ANALYSIS["Velocity Analysis<br/>ROI Correlation"]
        INSIGHTS["Actionable Insights<br/>Project-specific"]
    end
    
    CLAUDE_JSON -->|"Configuration"| LINEAR_MCP
    LINEAR_MCP -->|"SSE Connection"| NPX_CMD
    
    NPX_CMD -->|"Live Data Access"| TEAM_VEL
    NPX_CMD -->|"Issue Tracking"| ISSUE_DATA
    NPX_CMD -->|"Project Metrics"| PROJECT_CTX
    
    TEAM_VEL -->|"Sprint Context"| PROMPT_CTX
    ISSUE_DATA -->|"Completion Data"| ANALYSIS
    PROJECT_CTX -->|"Development State"| INSIGHTS
```

The Linear MCP integration is configured through the Claude CLI or direct JSON configuration:

| Configuration Method | Command/File | Purpose |
|---------------------|--------------|---------|
| CLI Setup | `claude mcp add linear -s user -- npx -y mcp-remote https://mcp.linear.app/sse` | Interactive setup |
| JSON Config | `.claude.json` mcpServers section | Persistent configuration |
| Verification | `claude mcp list` | Validate integration |

Sources: [claude_code_roi_full.md:410-436]()

## Template Customization

Organizations can customize report templates by modifying the JSON metrics structure and analysis instructions. The template system supports organization-specific metrics and custom analysis frameworks.

```mermaid
graph LR
    subgraph "Base Template Elements"
        METRICS_SCHEMA["Metrics JSON Schema<br/>Standard Fields"]
        ANALYSIS_PROMPT["Analysis Instructions<br/>Report Structure"]
        VIZ_SPEC["Visualization Specs<br/>Mermaid Diagrams"]
    end
    
    subgraph "Customization Points"
        CUSTOM_METRICS["Custom Metrics<br/>Organization-specific"]
        DOMAIN_ANALYSIS["Domain Analysis<br/>Industry-specific"]
        BRAND_FORMAT["Report Formatting<br/>Corporate Style"]
    end
    
    subgraph "Output Variants"
        EXEC_REPORT["Executive Reports<br/>High-level ROI"]
        TECH_REPORT["Technical Reports<br/>Detailed Metrics"]
        TEAM_REPORT["Team Reports<br/>Individual Analysis"]
    end
    
    METRICS_SCHEMA -->|"Extend"| CUSTOM_METRICS
    ANALYSIS_PROMPT -->|"Customize"| DOMAIN_ANALYSIS
    VIZ_SPEC -->|"Style"| BRAND_FORMAT
    
    CUSTOM_METRICS --> EXEC_REPORT
    DOMAIN_ANALYSIS --> TECH_REPORT
    BRAND_FORMAT --> TEAM_REPORT
```

Template customization involves modifying the metrics JSON structure and prompt instructions:

```json
{
  "claude_code_sessions": 42,
  "total_cost": 103.45,
  "pull_requests": 23,
  "avg_session_duration": "28.5 minutes",
  "tool_acceptance_rates": {
    "Edit": 0.81,
    "MultiEdit": 0.92,
    "Write": 0.65
  }
}
```

Sources: [report-generation-prompt.md:17-42](), [claude_code_roi_full.md:488-499]()

## Automation and Scheduling

The report generation system supports automated execution through shell scripts that combine metric fetching with template processing. These scripts can be scheduled for regular reporting intervals.

```mermaid
flowchart TD
    subgraph "Automation Components"
        WEEKLY_SCRIPT["weekly-report.sh<br/>Scheduled Execution"]
        METRIC_FETCH["Metric Fetching<br/>Prometheus Queries"]
        TEMPLATE_PROC["Template Processing<br/>Data Injection"]
    end
    
    subgraph "Scheduling Options"
        CRON["Cron Jobs<br/>Regular Intervals"]
        CI_CD["CI/CD Integration<br/>Pipeline Triggers"]
        MANUAL["Manual Execution<br/>On-demand Reports"]
    end
    
    subgraph "Output Management"
        FILE_OUT["File Output<br/>Timestamped Reports"]
        EMAIL_DIST["Email Distribution<br/>Stakeholder Delivery"]
        ARCHIVE["Report Archive<br/>Historical Analysis"]
    end
    
    WEEKLY_SCRIPT -->|"Data Collection"| METRIC_FETCH
    METRIC_FETCH -->|"Template Population"| TEMPLATE_PROC
    
    CRON -->|"Automated Trigger"| WEEKLY_SCRIPT
    CI_CD -->|"Pipeline Integration"| WEEKLY_SCRIPT
    MANUAL -->|"Ad-hoc Execution"| WEEKLY_SCRIPT
    
    TEMPLATE_PROC -->|"Generated Reports"| FILE_OUT
    FILE_OUT -->|"Distribution"| EMAIL_DIST
    FILE_OUT -->|"Storage"| ARCHIVE
```

The automation pattern follows a standard shell script structure that fetches metrics and generates reports:

```bash
#!/bin/bash
# weekly-report.sh pattern
# 1. Gather metrics from Prometheus
# 2. Process data through template
# 3. Execute Claude CLI for report generation
```

Sources: [report-generation-prompt.md:68-81](), [claude_code_roi_full.md:456-477]()

---

# Page: Linear MCP Integration

# Linear MCP Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [report-generation-prompt.md](report-generation-prompt.md)

</details>



This document covers the configuration and usage of Linear's Model Context Protocol (MCP) integration within the Claude Code ROI measurement system. The Linear MCP integration enables automated report generation by combining Claude Code telemetry metrics with real-time project management data from Linear, including team velocity, issue completion rates, and sprint analytics.

For general report generation templates and automation, see [Report Generation and Templates](#5.1). For interpreting the combined reports, see [Report Examples and Interpretation](#5.3).

## MCP Protocol Overview

The Model Context Protocol (MCP) provides a standardized way for Claude Code to access external data sources in real-time during conversation sessions. The Linear MCP server exposes Linear's project management data through a Server-Sent Events (SSE) interface that Claude Code can query directly.

### MCP Integration Architecture

```mermaid
graph TB
    subgraph "Claude Code CLI"
        CC["claude CLI process"]
        MCP_CLIENT["MCP Client"]
        REPORT_GEN["Report Generation Engine"]
    end
    
    subgraph "Linear MCP Server"
        SSE_ENDPOINT["https://mcp.linear.app/sse"]
        LINEAR_API["Linear GraphQL API"]
        DATA_ADAPTER["MCP Data Adapter"]
    end
    
    subgraph "Prometheus Metrics"
        PROM_API["Prometheus HTTP API :9090"]
        METRICS_DB["Claude Code Metrics TSDB"]
    end
    
    subgraph "Report Output"
        MARKDOWN["Generated Reports .md"]
        MERMAID["Embedded Diagrams"]
    end
    
    CC --> MCP_CLIENT
    MCP_CLIENT -->|"npx -y mcp-remote"| SSE_ENDPOINT
    SSE_ENDPOINT --> LINEAR_API
    LINEAR_API --> DATA_ADAPTER
    DATA_ADAPTER -->|"Issues, Velocity, Sprints"| MCP_CLIENT
    
    REPORT_GEN -->|"PromQL Queries"| PROM_API
    PROM_API --> METRICS_DB
    METRICS_DB -->|"Costs, Tokens, Sessions"| REPORT_GEN
    
    MCP_CLIENT -->|"Linear Data"| REPORT_GEN
    REPORT_GEN --> MARKDOWN
    REPORT_GEN --> MERMAID
```

Sources: [claude_code_roi_full.md:410-436](), [report-generation-prompt.md:7-10]()

## Linear MCP Server Configuration

### CLI-Based Setup

The recommended approach uses Claude Code's built-in MCP management commands to configure the Linear integration:

```bash
# Add Linear MCP server
claude mcp add linear -s user -- npx -y mcp-remote https://mcp.linear.app/sse

# Verify installation
claude mcp list

# Restart Claude Code to activate
```

### Manual Configuration

For advanced deployments or automation, configure the Linear MCP server directly in the Claude Code configuration file:

```json
{
  "mcpServers": {
    "linear": {
      "type": "stdio", 
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/sse"]
    }
  }
}
```

The configuration file location is `~/.claude.json` on Unix systems and `%APPDATA%\Claude\claude.json` on Windows.

### MCP Connection Flow

```mermaid
sequenceDiagram
    participant USER as "User/Automation"
    participant CLAUDE as "Claude CLI"
    participant NPX as "npx Process"
    participant MCP_SERVER as "Linear MCP Server"
    participant LINEAR as "Linear API"
    
    Note over USER: Initialize MCP Connection
    USER->>CLAUDE: "claude mcp add linear"
    CLAUDE->>NPX: "spawn npx -y mcp-remote"
    NPX->>MCP_SERVER: "Connect to https://mcp.linear.app/sse"
    MCP_SERVER->>LINEAR: "Authenticate & establish session"
    LINEAR-->>MCP_SERVER: "GraphQL endpoint access"
    MCP_SERVER-->>NPX: "MCP protocol handshake"
    NPX-->>CLAUDE: "Connection established"
    
    Note over USER: Query Linear Data
    USER->>CLAUDE: "Generate report with Linear data"
    CLAUDE->>MCP_SERVER: "MCP query: team velocity, issues"
    MCP_SERVER->>LINEAR: "GraphQL: query sprint metrics"
    LINEAR-->>MCP_SERVER: "JSON response: issues, estimates"
    MCP_SERVER-->>CLAUDE: "Structured MCP response"
    CLAUDE->>CLAUDE: "Combine with Prometheus metrics"
    CLAUDE-->>USER: "Generated report with Linear insights"
```

Sources: [claude_code_roi_full.md:414-422](), [claude_code_roi_full.md:424-436]()

## Data Access and Integration

### Available Linear Data

The Linear MCP integration provides access to the following project management data:

| Data Type | MCP Query | Use Case |
|-----------|-----------|----------|
| **Team Velocity** | Sprint completion metrics | Correlate with Claude Code session frequency |
| **Issue Tracking** | Open/closed issues, estimates | Calculate cost per feature/bug fix |
| **Sprint Analytics** | Burndown, cycle time | Measure productivity improvements |
| **Project Status** | Milestone progress | ROI attribution by project phase |

### Data Combination Strategy

The integration combines Linear project data with Claude Code telemetry through shared time windows and user attribution:

```mermaid
graph LR
    subgraph "Linear Project Data"
        ISSUES["Linear Issues<br/>KAS-10, KAS-14, etc."]
        VELOCITY["Sprint Velocity<br/>Story Points/Week"]
        CYCLE_TIME["Cycle Time<br/>Issue Open → Close"]
    end
    
    subgraph "Claude Code Metrics"
        SESSIONS["Session Count<br/>claude_code.session.count"]
        COSTS["Total Cost USD<br/>claude_code.cost.usage"]
        TOKENS["Token Usage<br/>input/output/cache"]
    end
    
    subgraph "Combined Analytics"
        COST_PER_ISSUE["Cost per Linear Issue"]
        VELOCITY_CORRELATION["Velocity vs Claude Usage"]
        ROI_CALCULATION["ROI per Sprint/Project"]
    end
    
    ISSUES --> COST_PER_ISSUE
    SESSIONS --> COST_PER_ISSUE
    
    VELOCITY --> VELOCITY_CORRELATION
    COSTS --> VELOCITY_CORRELATION
    
    CYCLE_TIME --> ROI_CALCULATION
    TOKENS --> ROI_CALCULATION
```

Sources: [claude_code_roi_full.md:442-454](), [report-generation-prompt.md:14-54]()

## Report Generation Integration

### Automated Metric Fetching

The integration supports automated report generation by combining live Prometheus metrics with Linear data:

```bash
#!/bin/bash
# Fetch live Claude Code metrics
TOTAL_COST=$(curl -s "http://localhost:9090/api/v1/query?query=sum(claude_code_cost_usage_USD_total)" | jq -r '.data.result[0].value[1] // "0"')
INPUT_TOKENS=$(curl -s "http://localhost:9090/api/v1/query?query=sum(claude_code_token_usage_tokens_total{type=\"input\"})" | jq -r '.data.result[0].value[1] // "0"')

# Generate report with Linear MCP integration
claude -p "Using the Linear MCP, analyze team velocity and combine with metrics..."
```

### Report Template Structure

The Linear MCP integration supports structured report generation with these components:

| Report Section | Data Source | Implementation |
|----------------|-------------|----------------|
| **Executive Summary** | Linear velocity + Claude costs | Sprint completion rate analysis |
| **Linear Issue Analysis** | MCP query: specific ticket IDs | Individual issue cost attribution |
| **Productivity Correlation** | Both Linear and Claude metrics | Statistical correlation analysis |
| **Actionable Insights** | Combined pattern analysis | Claude-generated recommendations |

### Real-Time Data Access Pattern

```mermaid
flowchart TD
    subgraph "Report Generation Session"
        PROMPT["User Report Prompt"]
        CLAUDE_PROCESS["Claude CLI Process"]
        PARALLEL_FETCH["Parallel Data Fetching"]
    end
    
    subgraph "Data Fetching"
        PROM_QUERY["Prometheus PromQL<br/>/api/v1/query"]
        LINEAR_MCP["Linear MCP Query<br/>SSE Connection"]
    end
    
    subgraph "Data Processing"
        METRIC_CORRELATION["Correlate Metrics<br/>by Time Window"]
        INSIGHT_GENERATION["Generate Insights<br/>Claude Analysis"]
    end
    
    subgraph "Output Generation"
        MARKDOWN_REPORT["Markdown Report"]
        MERMAID_DIAGRAMS["Embedded Visualizations"]
    end
    
    PROMPT --> CLAUDE_PROCESS
    CLAUDE_PROCESS --> PARALLEL_FETCH
    
    PARALLEL_FETCH --> PROM_QUERY
    PARALLEL_FETCH --> LINEAR_MCP
    
    PROM_QUERY --> METRIC_CORRELATION
    LINEAR_MCP --> METRIC_CORRELATION
    
    METRIC_CORRELATION --> INSIGHT_GENERATION
    INSIGHT_GENERATION --> MARKDOWN_REPORT
    INSIGHT_GENERATION --> MERMAID_DIAGRAMS
```

Sources: [claude_code_roi_full.md:456-479](), [report-generation-prompt.md:70-81]()

## Authentication and Security

### Linear API Access

The Linear MCP server handles authentication transparently through Linear's OAuth flow. No additional API keys or tokens are required in the Claude Code configuration.

### MCP Security Model

The MCP integration operates with the following security constraints:

- **Read-only access**: Cannot modify Linear data, only query
- **User-scoped**: Accesses only projects/teams visible to authenticated user
- **Session-based**: Authentication tied to Claude Code session lifecycle
- **No persistent storage**: Data queried fresh for each report generation

## Troubleshooting

### Common Integration Issues

| Issue | Symptom | Resolution |
|-------|---------|------------|
| **MCP Server Not Found** | `Error: Cannot connect to linear` | Verify `npx` is installed and accessible |
| **Authentication Failed** | Empty Linear data in reports | Check Linear account access and permissions |
| **SSE Connection Timeout** | Intermittent Linear data retrieval | Network connectivity or Linear service issues |
| **Stale Configuration** | Changes not reflected | Restart Claude Code after configuration changes |

### Diagnostic Commands

```bash
# Verify MCP server status
claude mcp list

# Test Linear connection
claude -p "Using Linear MCP, list my recent issues"

# Check npx process
ps aux | grep "mcp-remote"
```

### Integration Verification

Successful Linear MCP integration should enable queries like:

```bash
claude -p "Using Linear MCP, show me the velocity trend for our current sprint and correlate it with Claude Code usage patterns"
```

The response should include actual Linear issue IDs, sprint data, and project metrics combined with Claude Code telemetry data.

Sources: [claude_code_roi_full.md:414-422](), [report-generation-prompt.md:7-10]()

---

# Page: Report Examples and Interpretation

# Report Examples and Interpretation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [report-generation-prompt.md](report-generation-prompt.md)
- [sample-report-output.md](sample-report-output.md)

</details>



This document provides detailed guidance on interpreting Claude Code ROI reports generated by the automated reporting system. It covers the structure of generated reports, meaning of metrics, and how to extract actionable insights from productivity analysis.

For information about configuring report generation, see [Report Generation and Templates](#5.1). For setting up the Linear MCP integration that provides project data, see [Linear MCP Integration](#5.2).

## Report Structure and Data Sources

The automated reporting system combines multiple data sources to generate comprehensive ROI analysis. Each report follows a standardized structure with specific sections for different types of insights.

```mermaid
graph TB
    subgraph "Data Sources"
        PM[prometheus_metrics]
        LI[linear_mcp_data]
        TU[tool_usage_stats]
        CS[cost_statistics]
    end
    
    subgraph "Report Sections"
        ES[executive_summary]
        UM[usage_metrics]
        LIM[linear_integration_metrics]
        CA[cost_analysis]
        AI[actionable_insights]
        REC[recommendations]
    end
    
    subgraph "Visualization Types"
        PIE[pie_charts]
        BAR[bar_charts]
        GAN[gantt_diagrams]
        FLO[flowcharts]
    end
    
    PM --> ES
    PM --> UM
    PM --> CA
    LI --> LIM
    LI --> ES
    TU --> UM
    TU --> AI
    CS --> CA
    
    ES --> PIE
    UM --> PIE
    LIM --> BAR
    CA --> PIE
    AI --> FLO
    
    style PM fill:#f9f9f9
    style LI fill:#f9f9f9
    style ES fill:#e8f5e8
    style REC fill:#fff3e0
```

Sources: [sample-report-output.md:1-158](), [report-generation-prompt.md:44-53]()

## Executive Summary Interpretation

The executive summary provides high-level performance indicators derived from both telemetry and project management data. Key metrics to focus on include velocity improvements, cost per deliverable, and team adoption patterns.

### Velocity Metrics

The velocity improvement percentage represents the change in commit frequency and merge time after Claude Code adoption. In the sample report, the **17% improvement in commit velocity** indicates faster development cycles for teams with high tool acceptance rates (above 75%).

### Cost Efficiency Indicators

Cost per issue and cost per pull request provide direct ROI measurements. The sample shows **$2.46 per issue** and **$4.50 per pull request**, which should be compared against developer hourly rates to calculate net productivity gains.

```mermaid
flowchart LR
    subgraph "Cost Calculation Flow"
        TC[total_cost]
        II[issues_completed]
        PR[pull_requests]
        
        TC --> CPI[cost_per_issue]
        TC --> CPR[cost_per_pr]
        II --> CPI
        PR --> CPR
    end
    
    subgraph "ROI Derivation"
        CPI --> ROI[roi_percentage]
        CPR --> ROI
        DR[developer_rate] --> ROI
        TI[time_improvement] --> ROI
    end
    
    style TC fill:#f9f9f9
    style ROI fill:#e8f5e8
```

Sources: [sample-report-output.md:8-12](), [report-generation-prompt.md:18-22]()

## Usage Metrics Analysis

Usage metrics reveal tool adoption patterns and acceptance rates, which directly correlate with productivity improvements.

### Tool Distribution Patterns

The tool usage distribution shows which Claude Code capabilities are most utilized:
- **Read operations** (892 uses) indicate code exploration and understanding tasks
- **Edit operations** (356 uses) represent direct code modifications  
- **MultiEdit operations** (128 uses) suggest complex refactoring scenarios
- **Write operations** (73 uses) indicate new code generation
- **Bash operations** (204 uses) represent command execution and automation

### Acceptance Rate Analysis

Tool acceptance rates measure how often suggestions are accepted by developers:
- **MultiEdit: 92%** - Highest acceptance indicates effective complex editing
- **Edit: 81%** - Strong acceptance for code modifications
- **Write: 65%** - Lower acceptance suggests prompt optimization opportunities

```mermaid
graph TB
    subgraph "Tool Usage Pipeline"
        CCS[claude_code_sessions]
        TR[tool_requests]
        TA[tool_acceptance]
        AR[acceptance_rate]
    end
    
    subgraph "Performance Indicators"
        AR --> PI[productivity_improvement]
        SD[session_duration] --> PI
        TC[tool_count] --> PI
    end
    
    subgraph "Optimization Targets"
        PI --> OT[optimization_targets]
        AR --> OT
        LOW[low_acceptance_tools] --> OT
    end
    
    CCS --> TR
    TR --> TA
    TA --> AR
    
    style AR fill:#f9f9f9
    style PI fill:#e8f5e8
    style OT fill:#fff3e0
```

Sources: [sample-report-output.md:26-33](), [sample-report-output.md:15-23](), [report-generation-prompt.md:37-42]()

## Linear Integration Metrics

The Linear MCP integration provides project management context for Claude Code usage, enabling correlation between tool usage and delivery metrics.

### Issue Completion Analysis

Issue completion metrics show sprint progress and development velocity:
- **Completion Ratio: 60%** indicates healthy sprint progress
- **Average Issue Age: 1 day** suggests rapid issue creation and resolution
- **Active Development Tickets: 6** represents manageable work-in-progress

### Priority Distribution

Issue priority analysis reveals focus areas:
- **Urgent issues** (KAS-10, KAS-14) require immediate attention
- **High priority issues** (KAS-11, KAS-12, KAS-15) represent core feature work
- **Low priority issues** (KAS-13) indicate maintenance or enhancement tasks

Sources: [sample-report-output.md:34-57](), [report-generation-prompt.md:46-47]()

## Cost Analysis Interpretation

Cost analysis breaks down token usage and associated expenses to calculate true ROI of Claude Code adoption.

### Token Distribution

The token usage ratio provides insight into interaction patterns:
- **Input tokens: 3,245,670** ($32.46) represent prompts and context
- **Output tokens: 2,156,780** ($70.99) represent AI-generated code
- **Input/Output ratio: 1.5** indicates efficient prompt usage

### Cost Per Metric Calculations

Per-unit costs enable direct ROI comparison:
- **Cost per session**: $2.46 ($103.45 / 42 sessions)
- **Cost per tool use**: $0.06 ($103.45 / 1,653 total tool uses)
- **Cost per pull request**: $4.50 (total cost / 23 PRs)

```mermaid
pie
    title "Token Cost Distribution"
    "input_cost" : 32.46
    "output_cost" : 70.99
```

Sources: [sample-report-output.md:102-115](), [report-generation-prompt.md:24-29]()

## Productivity Comparison Metrics

Before/after comparisons quantify the impact of Claude Code adoption on development workflow efficiency.

### Key Performance Indicators

The productivity comparison reveals measurable improvements:
- **Commits per week**: +17.1% improvement (8.2 → 9.6)
- **Review cycles**: -12.5% reduction (2.4 → 2.1)  
- **Merge time**: -16.0% faster (7.5 → 6.3 hours)
- **Pull request size**: -12.1% smaller (165 → 145 LOC)

### Interpretation Guidelines

- **Increased commit frequency** indicates faster development iterations
- **Reduced review cycles** suggests higher code quality on first submission
- **Faster merge times** shows improved collaboration and less rework
- **Smaller PR size** indicates more focused, reviewable changes

Sources: [sample-report-output.md:67-100](), [sample-report-output.md:58-66]()

## Actionable Insights and Recommendations

The insights section translates metrics into specific actions for improving Claude Code adoption and ROI.

### Usage Pattern Insights

Key insights from the sample report include:
1. **MultiEdit underutilization** - High acceptance rate (92%) but low usage suggests training opportunities
2. **Edit rate optimization** - Teams above 80% acceptance show 16% faster PR merges
3. **Session duration sweet spot** - 25-35 minute sessions show optimal productivity

### Implementation Recommendations

Recommendations provide concrete next steps:
1. **Training programs** - Schedule MultiEdit workshops for complex editing scenarios
2. **Cost guardrails** - Set up alerts for sessions exceeding 5,000 tokens
3. **Prompt optimization** - Improve Write tool prompts to increase 65% acceptance rate

```mermaid
flowchart TD
    subgraph "Insight Generation"
        UM[usage_metrics] --> IN[insights]
        AR[acceptance_rates] --> IN
        CC[cost_comparison] --> IN
    end
    
    subgraph "Recommendation Types"
        IN --> TR[training_recommendations]
        IN --> CG[cost_guardrails]
        IN --> PO[prompt_optimization]
        IN --> WF[workflow_improvements]
    end
    
    subgraph "Implementation Actions"
        TR --> TS[training_sessions]
        CG --> AL[alerts_setup]
        PO --> PT[prompt_tuning]
        WF --> PC[process_changes]
    end
    
    style IN fill:#f9f9f9
    style TR fill:#e8f5e8
    style TS fill:#fff3e0
```

Sources: [sample-report-output.md:116-131](), [sample-report-output.md:132-154]()

## Visualization Guide

Reports include multiple Mermaid diagram types for different data representations:

### Pie Charts
Used for distribution analysis (tool usage, token costs, time allocation)

### Bar Charts  
Used for comparative metrics (before/after performance, team comparisons)

### Gantt Charts
Used for duration and frequency distributions (session lengths, sprint timelines)

### Flowcharts
Used for process improvements and recommendation workflows

Each visualization type serves specific analytical purposes and should be interpreted in context of the surrounding metrics and narrative.

Sources: [sample-report-output.md:15-23](), [sample-report-output.md:104-109](), [sample-report-output.md:134-154]()

---

# Page: Automation and Scheduling

# Automation and Scheduling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [report-generation-prompt.md](report-generation-prompt.md)

</details>



This page covers the automation and scheduling capabilities of the Claude Code ROI measurement system. It documents how to set up automated report generation, scheduled metric collection, and integration with CI/CD pipelines for regular ROI analysis.

For manual report generation and template customization, see [Report Generation and Templates](#5.1). For Linear MCP configuration details, see [Linear MCP Integration](#5.2).

## Automated Report Generation

The system provides automated report generation capabilities using the Claude CLI with Linear MCP integration and Prometheus metric queries.

### Report Generation Workflow

```mermaid
flowchart TD
    subgraph "Scheduled Triggers"
        CRON["cron: weekly-report.sh"]
        CI["CI/CD Pipeline"]
        MANUAL["Manual Execution"]
    end
    
    subgraph "Data Collection"
        PROM_API["prometheus:9090/api/v1/query"]
        LINEAR_MCP["linear MCP server"]
        METRICS_SCRIPT["fetch-claude-metrics.sh"]
    end
    
    subgraph "Report Generation"
        CLAUDE_CLI["claude -p report-prompt"]
        PROMPT_TEMPLATE["report-generation-prompt.md"]
        METRICS_JSON["metrics JSON payload"]
    end
    
    subgraph "Output Artifacts"
        MD_REPORT["sample-report-output.md"]
        MERMAID_CHARTS["Mermaid visualizations"]
        EXEC_SUMMARY["Executive summary"]
    end
    
    CRON --> METRICS_SCRIPT
    CI --> METRICS_SCRIPT
    MANUAL --> METRICS_SCRIPT
    
    METRICS_SCRIPT --> PROM_API
    METRICS_SCRIPT --> METRICS_JSON
    
    CLAUDE_CLI --> LINEAR_MCP
    CLAUDE_CLI --> PROMPT_TEMPLATE
    METRICS_JSON --> CLAUDE_CLI
    
    CLAUDE_CLI --> MD_REPORT
    MD_REPORT --> MERMAID_CHARTS
    MD_REPORT --> EXEC_SUMMARY
```

Sources: [claude_code_roi_full.md:458-477](), [report-generation-prompt.md:70-81]()

### Script-Based Metric Collection

The system includes automated metric fetching from Prometheus endpoints using shell scripts:

```mermaid
graph TD
    subgraph "Prometheus Queries"
        Q1["sum(claude_code_cost_usage_USD_total)"]
        Q2["sum(claude_code_token_usage_tokens_total{type=\"input\"})"]
        Q3["sum(claude_code_token_usage_tokens_total{type=\"output\"})"]
    end
    
    subgraph "fetch-claude-metrics.sh"
        CURL1["curl prometheus:9090/api/v1/query"]
        JQ_PARSE["jq -r '.data.result[0].value[1]'"]
        ENV_VARS["TOTAL_COST, INPUT_TOKENS, OUTPUT_TOKENS"]
    end
    
    subgraph "Report Template"
        JSON_PAYLOAD["Metrics JSON structure"]
        CLAUDE_PROMPT["claude -p with live data"]
    end
    
    Q1 --> CURL1
    Q2 --> CURL1  
    Q3 --> CURL1
    CURL1 --> JQ_PARSE
    JQ_PARSE --> ENV_VARS
    ENV_VARS --> JSON_PAYLOAD
    JSON_PAYLOAD --> CLAUDE_PROMPT
```

Sources: [claude_code_roi_full.md:458-477]()

## Scheduled Report Generation

### Cron-Based Automation

The system supports cron-based scheduling for regular report generation:

| Schedule Type | Cron Expression | Use Case |
|---------------|----------------|----------|
| Weekly Reports | `0 9 * * 1` | Monday 9 AM executive summaries |
| Daily Metrics | `0 8 * * *` | Daily cost tracking |
| Monthly Analysis | `0 10 1 * *` | Monthly ROI analysis |
| Sprint Reviews | Custom | Aligned with sprint cycles |

### Weekly Report Script Structure

```mermaid
sequenceDiagram
    participant CRON as "cron daemon"
    participant SCRIPT as "weekly-report.sh"
    participant PROM as "prometheus:9090"
    participant LINEAR as "Linear MCP"
    participant CLAUDE as "claude CLI"
    participant OUTPUT as "Report Files"
    
    CRON->>SCRIPT: "Execute weekly schedule"
    SCRIPT->>PROM: "GET /api/v1/query metrics"
    PROM-->>SCRIPT: "JSON response with values"
    SCRIPT->>SCRIPT: "Parse with jq, set env vars"
    SCRIPT->>CLAUDE: "claude -p with metrics JSON"
    CLAUDE->>LINEAR: "Query team velocity data"
    LINEAR-->>CLAUDE: "Sprint and issue data"
    CLAUDE->>CLAUDE: "Generate report with visualizations"
    CLAUDE->>OUTPUT: "Write sample-report-output.md"
    OUTPUT-->>SCRIPT: "Report generation complete"
```

Sources: [claude_code_roi_full.md:458-477](), [report-generation-prompt.md:70-81]()

## CI/CD Pipeline Integration

### GitHub Actions Integration

The system can be integrated into GitHub Actions workflows for automated reporting:

```mermaid
flowchart LR
    subgraph "GitHub Actions Workflow"
        TRIGGER["on: schedule / push"]
        SETUP["Setup environment"]
        METRICS["Fetch metrics step"]
        REPORT["Generate report step"]
        ARTIFACT["Upload artifacts"]
    end
    
    subgraph "External Services"
        PROM_SERVICE["Prometheus API"]
        LINEAR_SERVICE["Linear MCP server"]
    end
    
    subgraph "Generated Outputs"
        REPORT_MD["Weekly report.md"]
        METRICS_JSON["metrics-snapshot.json"]
        DASHBOARD_PNG["Dashboard screenshots"]
    end
    
    TRIGGER --> SETUP
    SETUP --> METRICS
    METRICS --> PROM_SERVICE
    METRICS --> REPORT
    REPORT --> LINEAR_SERVICE
    REPORT --> ARTIFACT
    
    ARTIFACT --> REPORT_MD
    ARTIFACT --> METRICS_JSON
    ARTIFACT --> DASHBOARD_PNG
```

Sources: [claude_code_roi_full.md:458-477]()

### Jenkins Pipeline Integration

For Jenkins-based CI/CD, the system provides pipeline-compatible scripts:

| Pipeline Stage | Script/Command | Purpose |
|----------------|----------------|---------|
| `collectMetrics` | `fetch-claude-metrics.sh` | Gather Prometheus data |
| `generateReport` | `claude -p report-prompt` | Create ROI analysis |
| `publishResults` | `cp *.md artifacts/` | Archive reports |
| `notifyTeam` | `slack-notify.sh` | Send executive summary |

## Deployment Automation

### Managed Settings Distribution

The system supports automated deployment of telemetry configuration across organizations:

```mermaid
graph TB
    subgraph "Configuration Management"
        MDM["MDM Solution"]
        CONFIG_MGMT["Configuration Management Tool"]
        MANAGED_JSON["managed-settings.json"]
    end
    
    subgraph "Target Endpoints"
        DEV_MACHINES["Developer Workstations"]
        CI_RUNNERS["CI/CD Runners"]
        BUILD_AGENTS["Build Agents"]
    end
    
    subgraph "Claude Code Instances"
        CC_TELEMETRY["CLAUDE_CODE_ENABLE_TELEMETRY=1"]
        OTLP_ENDPOINT["OTEL_EXPORTER_OTLP_ENDPOINT"]
        AUTH_HEADERS["OTEL_EXPORTER_OTLP_HEADERS"]
    end
    
    MANAGED_JSON --> MDM
    MANAGED_JSON --> CONFIG_MGMT
    
    MDM --> DEV_MACHINES
    CONFIG_MGMT --> CI_RUNNERS
    CONFIG_MGMT --> BUILD_AGENTS
    
    DEV_MACHINES --> CC_TELEMETRY
    CI_RUNNERS --> OTLP_ENDPOINT
    BUILD_AGENTS --> AUTH_HEADERS
```

Sources: [claude_code_roi_full.md:506-528]()

### Infrastructure as Code Integration

The Docker Compose infrastructure supports automated deployment through infrastructure as code:

| Component | Configuration File | Automation Target |
|-----------|-------------------|------------------|
| OpenTelemetry Collector | `otel-collector-config.yaml` | Kubernetes ConfigMaps |
| Prometheus | `prometheus.yml` | Helm chart values |
| Grafana | `grafana/provisioning/` | Terraform modules |
| Docker Services | `docker-compose.yml` | Docker Swarm/K8s |

### Metric Collection Scheduling

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> CollectMetrics: "Cron trigger"
    CollectMetrics --> QueryPrometheus: "fetch-claude-metrics.sh"
    QueryPrometheus --> ParseResponse: "jq processing"
    ParseResponse --> GenerateReport: "claude CLI execution"
    GenerateReport --> CallLinearMCP: "Team velocity query"
    CallLinearMCP --> RenderOutput: "Markdown generation"
    RenderOutput --> PublishArtifacts: "File output"
    PublishArtifacts --> Idle: "Complete"
    
    CollectMetrics --> ErrorHandler: "API failure"
    QueryPrometheus --> ErrorHandler: "Network timeout"
    GenerateReport --> ErrorHandler: "Claude API error"
    ErrorHandler --> Idle: "Log and retry"
```

Sources: [claude_code_roi_full.md:458-477](), [report-generation-prompt.md:70-81]()

## Configuration Management

### Environment Variable Automation

Automated deployment relies on consistent environment variable configuration across all Claude Code instances:

| Variable | Purpose | Automation Method |
|----------|---------|------------------|
| `CLAUDE_CODE_ENABLE_TELEMETRY=1` | Enable metrics collection | MDM/ConfigMgmt |
| `OTEL_METRICS_EXPORTER=otlp` | Set exporter type | Managed settings |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Collector endpoint | Environment-specific |
| `OTEL_EXPORTER_OTLP_HEADERS` | Authentication tokens | Secret management |

### Automated Health Checks

The system includes automated health monitoring for the telemetry pipeline:

```mermaid
flowchart TD
    subgraph "Health Check Automation"
        MONITOR["health-check.sh"]
        PROM_CHECK["Prometheus /metrics endpoint"]
        OTEL_CHECK["OpenTelemetry Collector :8889"]
        GRAFANA_CHECK["Grafana :3000/api/health"]
    end
    
    subgraph "Alert Conditions"
        NO_METRICS["No claude_code metrics in 1h"]
        COLLECTOR_DOWN["OTEL collector unreachable"]
        PROM_DOWN["Prometheus scrape failures"]
    end
    
    subgraph "Notification Channels"
        SLACK_ALERT["Slack webhook"]
        EMAIL_ALERT["SMTP notification"]
        PAGER_DUTY["PagerDuty integration"]
    end
    
    MONITOR --> PROM_CHECK
    MONITOR --> OTEL_CHECK
    MONITOR --> GRAFANA_CHECK
    
    PROM_CHECK --> NO_METRICS
    OTEL_CHECK --> COLLECTOR_DOWN
    PROM_CHECK --> PROM_DOWN
    
    NO_METRICS --> SLACK_ALERT
    COLLECTOR_DOWN --> EMAIL_ALERT
    PROM_DOWN --> PAGER_DUTY
```

Sources: [claude_code_roi_full.md:506-528]()

---

# Page: Operations and Maintenance

# Operations and Maintenance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [troubleshooting.md](troubleshooting.md)

</details>



This page provides operational guidance for maintaining, monitoring, and optimizing the Claude Code ROI measurement system in production environments. It covers system health monitoring, routine maintenance procedures, component lifecycle management, and operational workflows.

For specific troubleshooting procedures and solutions to common issues, see [Troubleshooting Guide](#6.1). For performance tuning and resource optimization guidance, see [Performance Optimization](#6.2). For security configurations and operational best practices, see [Security and Best Practices](#6.3).

## System Health Monitoring

### Service Status Verification

The ROI measurement system consists of multiple interconnected services that require coordinated monitoring. Use these commands to verify system health:

```bash
# Check all Docker services status
docker-compose ps

# Verify service endpoints
curl -f http://localhost:4317  # OTEL Collector gRPC
curl -f http://localhost:4318  # OTEL Collector HTTP  
curl -f http://localhost:9090  # Prometheus Web UI
curl -f http://localhost:3000  # Grafana Dashboard
curl -f http://localhost:8889/metrics  # OTEL Collector metrics
```

### Health Check Monitoring Architecture

```mermaid
graph TB
    subgraph "Health Check Endpoints"
        HC1["localhost:8889/metrics<br/>OTEL Collector Health"]
        HC2["localhost:9090/-/healthy<br/>Prometheus Health"]
        HC3["localhost:3000/api/health<br/>Grafana Health"]
    end
    
    subgraph "Service Dependencies"
        OC["otel-collector<br/>Container"]
        PROM["prometheus<br/>Container"]
        GR["grafana<br/>Container"]
    end
    
    subgraph "Data Flow Validation"
        DV1["claude_code_cost_usage_USD_total<br/>Metrics Presence"]
        DV2["claude_code_token_usage_tokens_total<br/>Token Metrics"]
        DV3["claude_code_session_count<br/>Session Tracking"]
    end
    
    HC1 --> OC
    HC2 --> PROM
    HC3 --> GR
    
    OC --> DV1
    PROM --> DV2
    GR --> DV3
    
    OC -.->|"depends_on"| PROM
    GR -.->|"depends_on"| PROM
```

**Sources**: [docker-compose.yml](), [troubleshooting.md:144-156]()

### Critical Metrics Monitoring

Monitor these key operational metrics to ensure system health:

| Metric | Threshold | Action |
|--------|-----------|--------|
| `up{job="otel-collector"}` | `< 1` | Restart OTEL Collector |
| `prometheus_tsdb_head_series` | `> 1M` | Review retention policy |
| `grafana_alerting_result_state` | `alerting` | Check dashboard alerts |
| Container memory usage | `> 80%` | Scale resources |
| Disk usage (`/prometheus`) | `> 85%` | Extend storage |

```bash
# Query critical metrics
curl -s 'http://localhost:9090/api/v1/query?query=up{job="otel-collector"}' | jq '.data.result[0].value[1]'
curl -s 'http://localhost:9090/api/v1/query?query=prometheus_tsdb_head_series' | jq '.data.result[0].value[1]'
```

**Sources**: [claude_code_roi_full.md:91-121](), [troubleshooting.md:144-156]()

## Routine Maintenance Procedures

### Configuration Management Workflow

```mermaid
sequenceDiagram
    participant Op as "Operations Team"
    participant Git as "Configuration Repo"
    participant DC as "docker-compose.yml"
    participant OC as "otel-collector-config.yaml"
    participant PC as "prometheus.yml"
    participant GC as "grafana/provisioning/"
    
    Op->>Git: "Pull latest configs"
    Git->>DC: "Update service definitions"
    Git->>OC: "Update OTLP pipeline config"
    Git->>PC: "Update scrape targets"
    Git->>GC: "Update dashboard configs"
    
    Op->>DC: "docker-compose down"
    Op->>DC: "docker-compose up -d"
    
    Note over Op: "Verify service health"
    Op->>OC: "Check OTLP receivers"
    Op->>PC: "Verify metrics ingestion"
    Op->>GC: "Validate dashboards"
```

**Sources**: [docker-compose.yml](), [otel-collector-config.yaml](), [prometheus.yml]()

### Data Retention Management

Configure appropriate data retention policies to balance storage costs with analytical needs:

```yaml
# prometheus.yml retention configuration
global:
  retention: "200h"  # ~8.3 days default
  retention_size: "15GB"  # Size-based limit
```

### Backup Procedures

Critical data backup includes Prometheus time-series data and Grafana dashboards:

```bash
# Backup Prometheus data
docker-compose exec prometheus tar -czf /prometheus/backup-$(date +%Y%m%d).tar.gz /prometheus/data

# Export Grafana dashboards
curl -s "http://admin:admin@localhost:3000/api/search?type=dash-db" | \
  jq -r '.[].uid' | \
  xargs -I {} curl -s "http://admin:admin@localhost:3000/api/dashboards/uid/{}" > grafana-backup-$(date +%Y%m%d).json
```

**Sources**: [claude_code_roi_full.md:54-89](), [grafana/provisioning/]()

## Component Lifecycle Management

### Service Update Procedures

```mermaid
flowchart TD
    subgraph "Update Process"
        START["Maintenance Window"]
        BACKUP["Create Data Backup"]
        PULL["docker-compose pull"]
        DOWN["docker-compose down"]
        UP["docker-compose up -d"]
        VERIFY["Health Check Validation"]
        ROLLBACK["Rollback if Failed"]
        END["Update Complete"]
    end
    
    subgraph "Validation Steps"
        CHECK1["Verify OTLP endpoints<br/>4317, 4318"]
        CHECK2["Validate Prometheus<br/>targets and scraping"]
        CHECK3["Confirm Grafana<br/>dashboard functionality"]
        CHECK4["Test metric ingestion<br/>claude_code_* metrics"]
    end
    
    START --> BACKUP
    BACKUP --> PULL
    PULL --> DOWN
    DOWN --> UP
    UP --> VERIFY
    VERIFY --> CHECK1
    CHECK1 --> CHECK2
    CHECK2 --> CHECK3
    CHECK3 --> CHECK4
    CHECK4 --> END
    
    VERIFY -.->|"Failure"| ROLLBACK
    ROLLBACK --> DOWN
```

**Sources**: [docker-compose.yml](), [troubleshooting.md:145-156]()

### Configuration Drift Detection

Monitor for configuration changes that may impact system performance:

```bash
# Check container configuration changes
docker-compose config --quiet && echo "Config valid" || echo "Config error"

# Verify environment variable consistency
docker-compose exec otel-collector env | grep OTEL_
docker-compose exec prometheus env | grep PROMETHEUS_
```

## Operational Workflows

### Daily Operations Checklist

| Task | Frequency | Command | Expected Result |
|------|-----------|---------|-----------------|
| Service health check | Daily | `docker-compose ps` | All services `Up` |
| Metric ingestion verification | Daily | Query `claude_code_cost_usage_USD_total` | Recent data present |
| Storage usage check | Daily | `df -h /var/lib/docker` | `< 80%` usage |
| Log rotation check | Weekly | `docker system df` | Reasonable log sizes |
| Dashboard functionality | Weekly | Access Grafana UI | All panels loading |

### Automated Monitoring Script

```bash
#!/bin/bash
# system-health-check.sh
set -e

# Check service status
if ! docker-compose ps | grep -q "Up"; then
    echo "ERROR: Services not running"
    exit 1
fi

# Verify metric availability
TOTAL_COST=$(curl -s "http://localhost:9090/api/v1/query?query=sum(claude_code_cost_usage_USD_total)" | jq -r '.data.result[0].value[1] // "0"')
if [[ "$TOTAL_COST" == "0" ]]; then
    echo "WARNING: No cost metrics found"
fi

# Check disk usage
DISK_USAGE=$(df /var/lib/docker | awk 'NR==2 {print $5}' | sed 's/%//')
if [[ "$DISK_USAGE" -gt 85 ]]; then
    echo "WARNING: Disk usage at ${DISK_USAGE}%"
fi

echo "System health check passed"
```

**Sources**: [claude_code_roi_full.md:91-121](), [troubleshooting.md:1-187]()

### Scaling Operations

Monitor system load and scale components as needed:

```yaml
# docker-compose.yml scaling configuration
services:
  otel-collector:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
  
  prometheus:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## Key Operational Metrics

### System Performance Indicators

Track these metrics to ensure optimal system operation:

```promql
# OTEL Collector performance
otelcol_processor_batch_batch_send_size_sum / otelcol_processor_batch_batch_send_size_count

# Prometheus ingestion rate
rate(prometheus_tsdb_head_samples_appended_total[5m])

# Memory usage patterns
container_memory_usage_bytes{name=~".*otel-collector.*|.*prometheus.*|.*grafana.*"}

# Query response times
histogram_quantile(0.95, rate(prometheus_http_request_duration_seconds_bucket[5m]))
```

### Business Metrics Validation

Ensure business-critical metrics are being collected correctly:

```promql
# Verify Claude Code metrics presence
up{job="otel-collector"} == 1
increase(claude_code_session_count[1h]) > 0
sum(claude_code_cost_usage_USD_total) by (model)
```

**Sources**: [claude_code_roi_full.md:91-121](), [prometheus.yml]()

## Integration Points

The Operations and Maintenance procedures interact with several system components:

- **Telemetry Collection**: Monitor OTLP endpoint health at `localhost:4317` and `localhost:4318`
- **Report Generation**: Ensure Prometheus API availability at `localhost:9090` for automated reporting
- **Dashboard Access**: Maintain Grafana service at `localhost:3000` for visualization
- **Configuration Management**: Track changes to `docker-compose.yml`, `prometheus.yml`, and `otel-collector-config.yaml`

For detailed troubleshooting of specific components, see [Troubleshooting Guide](#6.1). For performance tuning guidance, see [Performance Optimization](#6.2). For security and deployment best practices, see [Security and Best Practices](#6.3).

**Sources**: [claude_code_roi_full.md:1-537](), [troubleshooting.md:1-187]()

---

# Page: Troubleshooting Guide

# Troubleshooting Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker-compose.yml](docker-compose.yml)
- [troubleshooting.md](troubleshooting.md)

</details>



This document provides comprehensive troubleshooting guidance for the Claude Code ROI Measurement System, covering issues with telemetry collection, monitoring infrastructure, and automated reporting. It addresses problems that may occur across the entire observability pipeline from Claude Code CLI telemetry emission to final report generation.

For information about optimizing system performance, see [Performance Optimization](#6.2). For production security considerations, see [Security and Best Practices](#6.3).

## Troubleshooting Workflow

```mermaid
flowchart TD
    Issue["System Issue Detected"]
    
    subgraph "Diagnosis Phase"
        CheckLogs["Check Service Logs<br/>docker-compose logs"]
        CheckHealth["Verify Service Health<br/>HTTP endpoints"]
        CheckConfig["Validate Configuration<br/>YAML files"]
    end
    
    subgraph "Component-Specific Debugging"
        ClaudeIssues["Claude Code CLI<br/>claude /doctor"]
        OTELIssues["OpenTelemetry Collector<br/>:8889/metrics"]
        PromIssues["Prometheus<br/>:9090/targets"]
        GrafanaIssues["Grafana<br/>:3000/api/health"]
        LinearIssues["Linear MCP<br/>SSE connection"]
    end
    
    subgraph "Resolution Actions"
        RestartServices["docker-compose restart"]
        FixConfig["Update Configuration"]
        ClearData["Clear Cache/Data"]
        Reinstall["Reinstall Components"]
    end
    
    Issue --> CheckLogs
    Issue --> CheckHealth
    Issue --> CheckConfig
    
    CheckLogs --> ClaudeIssues
    CheckHealth --> OTELIssues
    CheckConfig --> PromIssues
    CheckLogs --> GrafanaIssues
    CheckHealth --> LinearIssues
    
    ClaudeIssues --> RestartServices
    OTELIssues --> FixConfig
    PromIssues --> ClearData
    GrafanaIssues --> RestartServices
    LinearIssues --> Reinstall
    
    RestartServices --> Issue
    FixConfig --> Issue
    ClearData --> Issue
    Reinstall --> Issue
```

Sources: [troubleshooting.md:1-187](), [docker-compose.yml:1-49]()

## Claude Code Telemetry Issues

### Telemetry Not Emitting

| Problem | Diagnostic Command | Solution |
|---------|-------------------|----------|
| No metrics in Prometheus | `echo $CLAUDE_CODE_ENABLE_TELEMETRY` | Set `CLAUDE_CODE_ENABLE_TELEMETRY=1` |
| OTLP endpoint unreachable | `curl -v http://localhost:4317` | Verify `otel-collector` container running |
| Console export not working | `export OTEL_METRICS_EXPORTER=console` | Check for console metric output |

**Environment Variable Verification:**
```bash
# Required telemetry configuration
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_METRIC_EXPORT_INTERVAL=1000
```

### Claude Code Hanging After Telemetry Enable

**Clean Installation Process:**
1. Uninstall and reinstall Claude Code CLI
2. Clear configuration directory: `rm -rf ~/.config/claude-code/`
3. Restart with fresh telemetry configuration

### Authentication and Permission Issues

**Linux NPM Permission Fix:**
```bash
# Create user-writable npm prefix
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g @anthropic-ai/claude-code
```

**Authentication Reset:**
```bash
claude /logout
rm -rf ~/.config/claude-code/auth.json
claude  # Will prompt for fresh authentication
```

Sources: [troubleshooting.md:7-107]()

## Infrastructure Component Troubleshooting

### Docker Compose Service Issues

```mermaid
graph TB
    subgraph "Service Dependencies"
        PrometheusService["prometheus<br/>Container"]
        OTELService["otel-collector<br/>depends_on: prometheus"]
        GrafanaService["grafana<br/>depends_on: prometheus"]
    end
    
    subgraph "Port Mappings"
        Port4317["4317:4317<br/>OTLP gRPC"]
        Port4318["4318:4318<br/>OTLP HTTP"]
        Port8889["8889:8889<br/>Prometheus metrics"]
        Port9090["9090:9090<br/>Prometheus UI"]
        Port3000["3000:3000<br/>Grafana UI"]
    end
    
    subgraph "Volume Mounts"
        OTELConfig["otel-collector-config.yaml<br/>/etc/otel-collector-config.yaml"]
        PromConfig["prometheus.yml<br/>/etc/prometheus/prometheus.yml"]
        GrafanaProvisioning["grafana/provisioning<br/>/etc/grafana/provisioning"]
    end
    
    PrometheusService --> Port9090
    OTELService --> Port4317
    OTELService --> Port4318
    OTELService --> Port8889
    GrafanaService --> Port3000
    
    OTELService --> OTELConfig
    PrometheusService --> PromConfig
    GrafanaService --> GrafanaProvisioning
```

**Service Health Verification:**
```bash
# Check all services are running
docker-compose ps

# View service logs
docker-compose logs otel-collector
docker-compose logs prometheus
docker-compose logs grafana

# Restart specific service
docker-compose restart otel-collector
```

### OpenTelemetry Collector Issues

**Common OTEL Collector Problems:**

| Issue | Check | Resolution |
|-------|-------|------------|
| Memory limiter triggered | `docker-compose logs otel-collector` | Increase memory limit in config |
| Batch processor timeout | OTLP metrics not arriving | Reduce `timeout` in processor config |
| Prometheus exporter unreachable | `curl http://localhost:8889/metrics` | Verify exporter endpoint configuration |

**OTEL Collector Endpoints:**
- OTLP gRPC: `localhost:4317`
- OTLP HTTP: `localhost:4318`
- Prometheus metrics: `localhost:8889/metrics`

### Prometheus Configuration Issues

**Target Health Check:**
1. Navigate to `http://localhost:9090/targets`
2. Verify `otel-collector:8889` target is UP
3. Check scrape interval and last scrape time

**Common Prometheus Issues:**

| Problem | Symptom | Solution |
|---------|---------|----------|
| No OTEL metrics | Empty Prometheus UI | Verify `prometheus.yml` scrape config |
| Storage issues | Data not persisting | Check `prometheus_data` volume mount |
| Query performance | Slow PromQL queries | Reduce retention time or optimize queries |

### Grafana Dashboard Problems

**Dashboard Loading Issues:**
1. Check provisioning directory: `./grafana/provisioning`
2. Verify dashboard JSON files in `./grafana/dashboards`
3. Restart Grafana: `docker-compose restart grafana`

**Data Source Configuration:**
- Prometheus URL: `http://prometheus:9090`
- Default credentials: `admin/admin`

Sources: [docker-compose.yml:3-45]()

## Report Generation Troubleshooting

### Linear MCP Integration Issues

**MCP Connection Problems:**
```bash
# Test Linear MCP connection
claude mcp add linear
# Should establish SSE connection without errors
```

**Common Linear Integration Issues:**

| Problem | Diagnostic | Solution |
|---------|------------|----------|
| SSE connection failed | Check Linear API token | Refresh authentication |
| No project data | Verify team access | Check Linear permissions |
| Rate limiting | API calls blocked | Reduce query frequency |

### Automated Report Generation Failures

**Report Generation Workflow Issues:**

```mermaid
sequenceDiagram
    participant CLI as "claude CLI"
    participant Prom as "prometheus:9090"
    participant Linear as "Linear MCP"
    participant Report as "Report Output"
    
    Note over CLI: Troubleshooting Points
    
    CLI->>Prom: "GET /api/v1/query"
    Note right of Prom: Check: Prometheus API accessible
    Prom-->>CLI: "Metrics data"
    
    CLI->>Linear: "Query project data"
    Note right of Linear: Check: MCP connection active
    Linear-->>CLI: "Project metrics"
    
    CLI->>Report: "Generate markdown report"
    Note right of Report: Check: File write permissions
```

**Common Report Issues:**

| Issue | Check Command | Resolution |
|-------|---------------|------------|
| Empty metrics | `curl http://localhost:9090/api/v1/query?query=claude_code_total_cost` | Verify telemetry data exists |
| Linear data missing | `claude mcp status` | Reconnect Linear MCP |
| File write errors | Check directory permissions | Set appropriate file permissions |

Sources: [troubleshooting.md:140-187]()

## Diagnostic Commands and Health Checks

### System Health Verification

```bash
# Docker infrastructure
docker-compose ps
docker-compose logs --tail=50

# Service endpoints
curl http://localhost:4318/v1/metrics  # OTLP HTTP
curl http://localhost:8889/metrics     # OTEL metrics
curl http://localhost:9090/-/healthy   # Prometheus health
curl http://localhost:3000/api/health  # Grafana health

# Claude Code diagnostics
claude /doctor
claude /bug
```

### Metrics Verification

**Prometheus Query Testing:**
```bash
# Total cost metrics
curl "http://localhost:9090/api/v1/query?query=claude_code_total_cost"

# Token usage by model
curl "http://localhost:9090/api/v1/query?query=claude_code_token_usage"

# User activity metrics
curl "http://localhost:9090/api/v1/query?query=claude_code_user_sessions"
```

### Log Analysis Patterns

**Critical Log Patterns to Monitor:**

| Component | Log Pattern | Indicates |
|-----------|-------------|-----------|
| OTEL Collector | `memory limiter` | Memory pressure |
| Prometheus | `scrape failed` | Target unreachable |
| Grafana | `database locked` | SQLite contention |
| Claude Code | `telemetry disabled` | Configuration issue |

### Configuration Validation

**Configuration File Checks:**
1. YAML syntax validation: `yamllint otel-collector-config.yaml`
2. Prometheus config test: `promtool check config prometheus.yml`
3. Docker Compose validation: `docker-compose config`

Sources: [troubleshooting.md:170-187](), [docker-compose.yml:8-11]()

## Advanced Troubleshooting

### Performance Issues

**Memory and Resource Problems:**

| Symptom | Component | Action |
|---------|-----------|--------|
| High memory usage | Claude Code | Use `/compact` command regularly |
| Container OOM kills | OTEL Collector | Increase memory limits |
| Slow queries | Prometheus | Optimize PromQL queries |
| Dashboard timeouts | Grafana | Reduce time range |

### Network and Connectivity

**Port Conflict Resolution:**
```bash
# Check port usage
netstat -tlnp | grep -E "(3000|4317|4318|8889|9090)"

# Kill conflicting processes
lsof -ti:4317 | xargs kill -9
```

**Firewall Configuration:**
- Ensure ports 3000, 4317, 4318, 8889, 9090 are accessible
- Check corporate firewall rules for OTLP traffic
- Verify Docker network connectivity

### Data Integrity Issues

**Metrics Validation:**
1. Compare Claude Code session data with Prometheus metrics
2. Verify cost calculations against billing APIs
3. Cross-reference Linear project data with generated reports

**Data Recovery:**
```bash
# Clear corrupted Prometheus data
docker-compose down
docker volume rm $(docker volume ls -q | grep prometheus)
docker-compose up -d

# Reset Grafana dashboards
docker volume rm $(docker volume ls -q | grep grafana)
# Dashboards will be reprovisioned on restart
```

Sources: [troubleshooting.md:108-138]()

---

# Page: Performance Optimization

# Performance Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [otel-collector-config.yaml](otel-collector-config.yaml)
- [prometheus.yml](prometheus.yml)
- [troubleshooting.md](troubleshooting.md)

</details>



This document covers performance optimization strategies for the Claude Code ROI Measurement System. It focuses on optimizing the telemetry collection pipeline, storage systems, and monitoring infrastructure to handle high-volume Claude Code usage efficiently.

For troubleshooting performance issues, see [Troubleshooting Guide](#6.1). For production deployment considerations, see [Security and Best Practices](#6.3).

## System Performance Overview

The Claude Code ROI measurement system consists of multiple performance-critical components that must be optimized for efficient telemetry collection and analysis.

### Performance Optimization Pipeline

```mermaid
flowchart TD
    subgraph "Claude Code Performance"
        CC["Claude Code CLI"]
        TG["Telemetry Generation"]
        BF["Buffering & Batching"]
    end
    
    subgraph "Collection Layer Optimization"
        ML["memory_limiter<br/>512 MiB Protection"]
        BP["batch processor<br/>1024 items/1s timeout"]
        EP["OTLP Endpoints<br/>4317 gRPC, 4318 HTTP"]
    end
    
    subgraph "Storage Layer Optimization"
        SI["scrape_interval<br/>15s Configuration"]
        ME["metric_expiration<br/>180m Retention"]
        TS["Time Series Storage<br/>Optimization"]
    end
    
    subgraph "Visualization Layer Optimization"
        QO["Query Optimization<br/>PromQL Efficiency"]
        DP["Dashboard Performance<br/>Panel Optimization"]
        RT["Real-time Updates<br/>Refresh Intervals"]
    end
    
    CC --> TG
    TG --> BF
    BF --> ML
    ML --> BP
    BP --> EP
    EP --> SI
    SI --> ME
    ME --> TS
    TS --> QO
    QO --> DP
    DP --> RT
```

Sources: [otel-collector-config.yaml:9-15](), [prometheus.yml:1-3]()

## OpenTelemetry Collector Optimization

The OpenTelemetry Collector is the primary bottleneck in the telemetry pipeline and requires careful optimization for high-throughput scenarios.

### Memory Management

The `memory_limiter` processor prevents memory exhaustion during high-volume telemetry collection:

| Parameter | Current Value | Optimization Range | Impact |
|-----------|---------------|-------------------|---------|
| `limit_mib` | 512 | 256-2048 | Memory protection threshold |
| `check_interval` | 1s | 0.5s-5s | Memory check frequency |

```mermaid
graph TD
    subgraph "Memory Limiter Configuration"
        ML_CI["check_interval: 1s<br/>Memory Check Frequency"]
        ML_LM["limit_mib: 512<br/>Memory Protection Limit"]
        ML_SP["spike_limit_mib<br/>(Optional Spike Protection)"]
    end
    
    subgraph "Batch Processor Optimization"
        BP_TO["timeout: 1s<br/>Batch Timeout"]
        BP_SB["send_batch_size: 1024<br/>Batch Size Limit"]
        BP_MD["send_batch_max_size<br/>(Optional Max Size)"]
    end
    
    subgraph "Performance Tuning"
        HT["High Throughput<br/>Increase batch_size to 2048"]
        LM["Low Memory<br/>Decrease limit_mib to 256"]
        LL["Low Latency<br/>Decrease timeout to 500ms"]
    end
    
    ML_CI --> HT
    ML_LM --> LM
    BP_TO --> LL
    BP_SB --> HT
```

Sources: [otel-collector-config.yaml:10-15]()

### Batch Processing Optimization

The `batch` processor configuration directly impacts throughput and latency:

**High Throughput Configuration:**
- `send_batch_size`: 2048-4096
- `timeout`: 2s-5s
- `send_batch_max_size`: 8192

**Low Latency Configuration:**
- `send_batch_size`: 512-1024
- `timeout`: 500ms-1s
- `send_batch_max_size`: 2048

**Memory Constrained Configuration:**
- `send_batch_size`: 256-512
- `timeout`: 1s-2s
- Memory limiter: 256-512 MiB

Sources: [otel-collector-config.yaml:10-12]()

### Endpoint Performance

The OTLP receivers support both gRPC and HTTP protocols with different performance characteristics:

| Protocol | Endpoint | Performance | Use Case |
|----------|----------|-------------|----------|
| gRPC | `0.0.0.0:4317` | Higher throughput, lower latency | Production environments |
| HTTP | `0.0.0.0:4318` | Better firewall compatibility | Development, restricted networks |

Sources: [otel-collector-config.yaml:2-7]()

## Prometheus Storage Optimization

Prometheus performance depends on efficient metric scraping, storage, and query execution.

### Scrape Configuration Optimization

```mermaid
graph TD
    subgraph "Scrape Interval Optimization"
        SI_15["scrape_interval: 15s<br/>Current Configuration"]
        SI_5["5s interval<br/>High Resolution"]
        SI_30["30s interval<br/>Resource Efficient"]
        SI_60["60s interval<br/>Long-term Storage"]
    end
    
    subgraph "Target Configuration"
        TC_OC["otel-collector:8889<br/>Primary Metrics"]
        TC_PR["prometheus:9090<br/>Self Monitoring"]
        TC_APP["Additional Targets<br/>Application Metrics"]
    end
    
    subgraph "Performance Impact"
        PI_DS["Data Storage<br/>Volume Impact"]
        PI_QP["Query Performance<br/>Resolution Trade-off"]
        PI_NW["Network Usage<br/>Scraping Overhead"]
    end
    
    SI_15 --> PI_DS
    SI_5 --> PI_QP
    SI_30 --> PI_NW
    TC_OC --> SI_15
```

Sources: [prometheus.yml:2-3](), [prometheus.yml:11-13]()

### Storage Retention and Capacity

Prometheus storage optimization involves balancing retention time with storage capacity:

**Retention Strategies:**
- Default: 15 days local storage
- Long-term: Configure external storage (Thanos, Cortex)
- Short-term: 7 days for development environments

**Storage Sizing:**
- Base requirement: ~1KB per metric per scrape interval
- Claude Code metrics: ~50-100 series per active user
- Estimated storage: 1GB per 1000 active user-hours

Sources: [otel-collector-config.yaml:21]()

## Resource Scaling and Capacity Planning

### Container Resource Allocation

Recommended resource allocation for different deployment scales:

| Component | Small (1-10 users) | Medium (10-100 users) | Large (100+ users) |
|-----------|-------------------|----------------------|-------------------|
| **OpenTelemetry Collector** |  |  |  |
| CPU | 0.1-0.5 cores | 0.5-1.0 cores | 1.0-2.0 cores |
| Memory | 256-512 MB | 512-1024 MB | 1-2 GB |
| **Prometheus** |  |  |  |
| CPU | 0.2-0.5 cores | 0.5-1.0 cores | 1.0-4.0 cores |
| Memory | 512 MB-1 GB | 1-2 GB | 2-8 GB |
| Storage | 5-10 GB | 10-50 GB | 50-200 GB |
| **Grafana** |  |  |  |
| CPU | 0.1-0.2 cores | 0.2-0.5 cores | 0.5-1.0 cores |
| Memory | 128-256 MB | 256-512 MB | 512 MB-1 GB |

### Horizontal Scaling Strategies

```mermaid
graph TD
    subgraph "Single Instance Deployment"
        SI_OC["Single OTEL Collector<br/>otel-collector:8889"]
        SI_PR["Single Prometheus<br/>prometheus:9090"]
        SI_GR["Single Grafana<br/>grafana:3000"]
    end
    
    subgraph "Load Balanced Deployment"
        LB_LB["Load Balancer<br/>OTLP Traffic Distribution"]
        LB_OC1["OTEL Collector 1<br/>Instance A"]
        LB_OC2["OTEL Collector 2<br/>Instance B"]
        LB_PR["Federated Prometheus<br/>Multi-instance"]
    end
    
    subgraph "High Availability Deployment"
        HA_OC["OTEL Collector Cluster<br/>Auto-scaling"]
        HA_PR1["Prometheus HA Pair<br/>Primary"]
        HA_PR2["Prometheus HA Pair<br/>Secondary"]
        HA_TS["External Time Series<br/>Thanos/Cortex"]
    end
    
    SI_OC --> LB_OC1
    SI_PR --> LB_PR
    LB_OC1 --> HA_OC
    LB_PR --> HA_PR1
```

Sources: [prometheus.yml:11-18]()

## Query Performance Optimization

### PromQL Query Optimization

Efficient PromQL queries are essential for responsive Grafana dashboards:

**High-Performance Query Patterns:**
- Use recording rules for complex calculations
- Leverage metric relabeling for dimension reduction
- Implement query result caching
- Optimize time range selections

**Query Optimization Examples:**
- Avoid high-cardinality grouping operations
- Use `rate()` instead of `increase()` for better performance
- Implement efficient aggregation strategies
- Cache frequently accessed dashboard queries

### Dashboard Performance

Grafana dashboard performance optimization focuses on query efficiency and update frequencies:

**Panel Optimization:**
- Limit time series per panel (< 100 series)
- Use appropriate visualization types
- Optimize refresh intervals (30s-5m)
- Implement query result caching

**Dashboard-Level Optimization:**
- Minimize concurrent panel queries
- Use template variables efficiently
- Implement progressive data loading
- Cache dashboard JSON definitions

Sources: [otel-collector-config.yaml:21]()

## Network and Connectivity Optimization

### OTLP Endpoint Configuration

Network optimization for telemetry collection involves protocol selection and connection pooling:

```mermaid
graph TD
    subgraph "Protocol Selection"
        PS_GRPC["gRPC Protocol<br/>Port 4317"]
        PS_HTTP["HTTP Protocol<br/>Port 4318"]
        PS_PERF["Performance Comparison<br/>gRPC > HTTP"]
    end
    
    subgraph "Connection Optimization"
        CO_POOL["Connection Pooling<br/>Reuse Connections"]
        CO_COMP["Compression<br/>gzip/deflate"]
        CO_BATCH["Batch Transmission<br/>Reduce Round Trips"]
    end
    
    subgraph "Firewall Configuration"
        FC_4317["Allow gRPC:4317<br/>Primary Protocol"]
        FC_4318["Allow HTTP:4318<br/>Fallback Protocol"]
        FC_8889["Allow Metrics:8889<br/>Prometheus Scraping"]
        FC_9090["Allow Prometheus:9090<br/>Query Interface"]
    end
    
    PS_GRPC --> CO_POOL
    PS_HTTP --> CO_COMP
    CO_BATCH --> FC_4317
```

Sources: [otel-collector-config.yaml:4-7](), [otel-collector-config.yaml:19]()

### Bandwidth and Compression

Optimize network usage through compression and efficient data serialization:

**Compression Settings:**
- OTLP gRPC: Built-in compression enabled
- Prometheus metrics: gzip compression for HTTP endpoints
- Dashboard assets: Enable browser caching

**Data Reduction Strategies:**
- Metric sampling for high-frequency data
- Selective metric collection
- Efficient label usage
- Delta encoding for counter metrics

Sources: [otel-collector-config.yaml:18-22]()

## Monitoring Performance Metrics

### System Health Monitoring

Monitor the monitoring system itself to ensure optimal performance:

**Key Performance Indicators:**
- OTLP ingestion rate (metrics/second)
- Memory usage percentage
- Query response times
- Storage growth rate
- Dashboard rendering times

**Alert Thresholds:**
- Memory usage > 80% of limit
- Query response time > 5 seconds
- Storage usage > 85% capacity
- OTLP ingestion errors > 1%

### Performance Debugging

Use built-in debugging capabilities for performance analysis:

**OTEL Collector Debug Output:**
- `debug` exporter with `verbosity: detailed`
- `sampling_initial: 5` for startup debugging
- `sampling_thereafter: 200` for ongoing monitoring

**Prometheus Query Analysis:**
- Query execution time monitoring
- Index usage analysis
- Memory consumption tracking
- Query result caching effectiveness

Sources: [otel-collector-config.yaml:24-27](), [otel-collector-config.yaml:38-40]()

---

# Page: Security and Best Practices

# Security and Best Practices

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [troubleshooting.md](troubleshooting.md)

</details>



This document covers security considerations, authentication mechanisms, and operational best practices for deploying the Claude Code ROI measurement system in production environments. It addresses data privacy, network security, access controls, and compliance requirements specific to telemetry collection and analysis.

For general troubleshooting of authentication issues, see [Troubleshooting Guide](#6.1). For performance optimization and resource management, see [Performance Optimization](#6.2).

## Telemetry Data Security

### Sensitive Data in Metrics

The Claude Code telemetry system collects several types of data that require security consideration:

| Data Type | Sensitivity Level | Security Implications |
|-----------|------------------|----------------------|
| `user.account_uuid` | High | Unique user identifier that can link activities |
| `session.id` | Medium | Session tracking across requests |
| `model` | Low | Model usage patterns |
| `cost.usage` | Medium | Financial data requiring confidentiality |
| `user_prompt` content | High | May contain proprietary code, business logic |

**Security Architecture for Data Collection**

```mermaid
graph TB
    subgraph "Client Environment"
        CC["claude-code CLI"]
        ENV["Environment Variables<br/>CLAUDE_CODE_ENABLE_TELEMETRY<br/>OTEL_EXPORTER_OTLP_HEADERS"]
    end
    
    subgraph "Transport Security"
        TLS["TLS 1.3 Encryption"]
        AUTH["Bearer Token Authentication"]
        HEADERS["Authorization Headers"]
    end
    
    subgraph "Collection Infrastructure"
        OC["otel-collector<br/>:4317 gRPC :4318 HTTP"]
        PROC["memory_limiter<br/>batch processor"]
        EXP["prometheus exporter<br/>:8889"]
    end
    
    subgraph "Storage Security"
        PROM["prometheus TSDB<br/>local filesystem"]
        GRAF["grafana dashboards<br/>user authentication"]
    end
    
    CC --> ENV
    ENV --> TLS
    TLS --> AUTH
    AUTH --> HEADERS
    HEADERS --> OC
    OC --> PROC
    PROC --> EXP
    EXP --> PROM
    PROM --> GRAF
    
    style CC fill:#f9f9f9
    style OC fill:#f9f9f9
    style PROM fill:#f9f9f9
```

Sources: [claude_code_roi_full.md:67-89](), [claude_code_roi_full.md:514-527]()

### User Prompt Data Protection

The system can optionally collect user prompt content via `OTEL_LOG_USER_PROMPTS=1`. This represents the highest security risk as prompts may contain:

- Proprietary source code
- Business logic and algorithms  
- Customer data references
- Infrastructure details
- Security credentials

**Recommendation**: Disable prompt logging in production unless explicitly required for analysis and approved by security teams.

```bash
# Secure configuration - disable prompt collection
export OTEL_LOG_USER_PROMPTS=0
export CLAUDE_CODE_ENABLE_TELEMETRY=1
```

Sources: [claude_code_roi_full.md:340-389]()

## Network Security and Transport

### OTLP Endpoint Security

The OpenTelemetry Protocol (OTLP) endpoints require proper security configuration:

**Secure Transport Configuration**

```mermaid
flowchart LR
    subgraph "Claude Code Client"
        CLI["claude CLI process"]
        OTEL_CONFIG["OTEL_EXPORTER_OTLP_ENDPOINT<br/>OTEL_EXPORTER_OTLP_HEADERS<br/>OTEL_EXPORTER_OTLP_PROTOCOL"]
    end
    
    subgraph "Network Security"
        FW["Corporate Firewall<br/>Port 4317/4318"]
        LB["Load Balancer<br/>SSL Termination"]
        VPN["VPN/Private Network"]
    end
    
    subgraph "Collection Service"
        COLLECTOR["otel-collector-config.yaml<br/>receivers.otlp.protocols.grpc<br/>receivers.otlp.protocols.http"]
    end
    
    CLI --> OTEL_CONFIG
    OTEL_CONFIG --> FW
    FW --> LB
    LB --> VPN
    VPN --> COLLECTOR
    
    style OTEL_CONFIG fill:#f9f9f9
    style COLLECTOR fill:#f9f9f9
```

**Production Endpoint Examples:**
- **Local development**: `http://localhost:4317` (development only)
- **Kubernetes**: `https://otel-collector.monitoring.svc.cluster.local:4317` 
- **AWS ALB**: `https://telemetry.company.com:4317`
- **Managed services**: `https://otlp.datadoghq.com` with API keys

Sources: [claude_code_roi_full.md:84-89](), [claude_code_roi_full.md:72-78]()

### Authentication Token Management

OTLP authentication uses bearer tokens in headers:

```bash
# Secure token configuration
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer ${OTEL_TOKEN}"
```

**Token Security Requirements:**
- Rotate tokens every 90 days minimum
- Store tokens in secure credential management systems
- Use environment variables, never hardcode in configuration files
- Implement token validation and expiration checking

Sources: [claude_code_roi_full.md:77-78](), [claude_code_roi_full.md:516-517]()

## Authentication and Authorization

### Grafana Access Control

Grafana dashboards contain sensitive cost and usage data requiring proper access controls:

**Role-Based Access Model**

| Role | Permissions | Justification |
|------|-------------|---------------|
| **Viewer** | Read dashboards only | Developers, managers viewing team metrics |
| **Editor** | Modify dashboards | DevOps, analytics teams |
| **Admin** | Full system access | Security, infrastructure teams |

**Grafana Authentication Configuration:**
- Enable OIDC/SAML integration with corporate identity provider
- Disable anonymous access in production
- Implement session timeout policies
- Enable audit logging for dashboard access

### Prometheus Query Security

Prometheus exposes sensitive metrics via HTTP API at `:9090`. Secure this endpoint:

```bash
# Example queries that expose sensitive data
curl "http://localhost:9090/api/v1/query?query=sum(claude_code_cost_usage_USD_total)by(user_email)"
curl "http://localhost:9090/api/v1/query?query=claude_code_token_usage_tokens_total"
```

**Security Controls:**
- Place Prometheus behind authentication proxy
- Implement query rate limiting
- Restrict network access to monitoring subnet
- Enable TLS for all connections

Sources: [claude_code_roi_full.md:96-121](), [claude_code_roi_full.md:462-464]()

## Configuration Security

### Managed Settings Deployment

Enterprise deployments use `managed-settings.json` for centralized configuration:

**Secure Configuration Management**

```mermaid
graph TD
    subgraph "Configuration Sources"
        MDM["Mobile Device Management"]
        CM["Configuration Management<br/>Ansible/Puppet/Chef"]
        K8S["Kubernetes ConfigMaps/Secrets"]
    end
    
    subgraph "Security Controls"
        VAULT["HashiCorp Vault<br/>Secret Management"]
        ENC["Encrypted Configuration<br/>managed-settings.json"]
        RBAC["Role-Based Access Control"]
    end
    
    subgraph "Client Deployment"
        CLIENT["Claude Code Client<br/>~/.config/claude-code/"]
        RESTRICT["User Cannot Disable<br/>Telemetry Settings"]
    end
    
    MDM --> VAULT
    CM --> VAULT
    K8S --> VAULT
    VAULT --> ENC
    ENC --> RBAC
    RBAC --> CLIENT
    CLIENT --> RESTRICT
    
    style VAULT fill:#f9f9f9
    style CLIENT fill:#f9f9f9
```

**Configuration Security Best Practices:**
- Encrypt configuration files at rest
- Use secret management systems for tokens
- Implement configuration drift detection
- Audit configuration changes
- Validate configuration syntax before deployment

Sources: [claude_code_roi_full.md:508-528]()

### Environment Variable Security

Claude Code telemetry relies on environment variables that may contain sensitive data:

```bash
# Sensitive environment variables
CLAUDE_CODE_ENABLE_TELEMETRY=1
OTEL_EXPORTER_OTLP_ENDPOINT=https://collector.company.com:4317
OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer secret-token"
```

**Security Requirements:**
- Never log environment variables in debugging output
- Use `.env` files with restricted permissions (600)
- Implement environment variable scanning in CI/CD
- Rotate authentication tokens regularly

Sources: [claude_code_roi_full.md:68-78](), [troubleshooting.md:31-35]()

## Container and Infrastructure Security

### Docker Compose Security Hardening

The system uses Docker Compose for orchestration. Security considerations:

**Container Security Architecture**

```mermaid
graph TB
    subgraph "Docker Host Security"
        HOST["Docker Host<br/>Security Updates<br/>User Namespaces"]
        NET["Network Isolation<br/>docker-compose networks"]
        VOL["Volume Security<br/>Read-only mounts"]
    end
    
    subgraph "Container Security"
        OC_SEC["otel-collector<br/>Non-root user<br/>Resource limits"]
        PROM_SEC["prometheus<br/>File permissions<br/>Data encryption"]
        GRAF_SEC["grafana<br/>Security headers<br/>Session management"]
    end
    
    subgraph "Runtime Security"
        SCAN["Image Vulnerability Scanning"]
        MON["Runtime Monitoring"]
        LOG["Centralized Logging"]
    end
    
    HOST --> NET
    NET --> VOL
    VOL --> OC_SEC
    OC_SEC --> PROM_SEC
    PROM_SEC --> GRAF_SEC
    GRAF_SEC --> SCAN
    SCAN --> MON
    MON --> LOG
    
    style HOST fill:#f9f9f9
    style SCAN fill:#f9f9f9
```

**Security Hardening Checklist:**
- Run containers as non-root users
- Implement resource limits in `docker-compose.yml`
- Use read-only root filesystems where possible
- Scan container images for vulnerabilities
- Enable Docker security options (`--security-opt`)
- Implement network segmentation

Sources: Inferred from system architecture diagrams

### Prometheus Data Security

Prometheus stores time-series data containing sensitive usage and cost information:

**Data Protection Requirements:**
- Encrypt Prometheus data directory at rest
- Implement retention policies to limit data exposure
- Secure backup and restore procedures
- Monitor for unauthorized data access
- Implement data anonymization for non-production environments

Configuration: [prometheus.yml:retention policies]()

## Data Privacy and Retention

### PII and Sensitive Data Handling

The telemetry system collects potentially sensitive information:

**Data Classification and Handling**

| Data Element | Classification | Retention | Access Control |
|--------------|----------------|-----------|----------------|
| `user.account_uuid` | PII | 90 days | Need-to-know |
| `user_email` | PII | 90 days | Manager+ only |
| `session.id` | Sensitive | 30 days | Automated systems |
| `cost.usage` | Confidential | 1 year | Finance+ only |
| `user_prompt` | Highly Sensitive | Disabled | Security approval |

**Privacy Protection Measures:**
- Implement data anonymization pipelines
- Hash user identifiers where possible
- Regular data purging based on retention policies
- Audit data access and exports
- Provide data deletion mechanisms for user requests

### Compliance Considerations

**GDPR Compliance:**
- Implement right to be forgotten (data deletion)
- Provide data export capabilities
- Maintain data processing records
- Implement consent management for optional telemetry

**SOX/Financial Compliance:**
- Secure cost and financial metrics
- Implement audit trails for all data access
- Separate financial data access controls
- Regular compliance audits

Sources: [claude_code_roi_full.md:247-295]()

## Operational Security Practices

### Authentication Troubleshooting Security

Common authentication issues can create security vulnerabilities:

**Secure Troubleshooting Procedures:**

```mermaid
sequenceDiagram
    participant DEV as "Developer"
    participant CLAUDE as "claude CLI"
    participant AUTH as "Authentication System"
    participant LOGS as "Audit Logs"
    
    DEV->>CLAUDE: "claude /logout"
    CLAUDE->>AUTH: "Revoke session tokens"
    AUTH->>LOGS: "Log authentication event"
    
    Note over DEV: "Clear local auth data securely"
    DEV->>CLAUDE: "rm ~/.config/claude-code/auth.json"
    
    DEV->>CLAUDE: "claude (re-authenticate)"
    CLAUDE->>AUTH: "New authentication flow"
    AUTH->>LOGS: "Log new session creation"
    AUTH-->>CLAUDE: "New session tokens"
```

**Security Requirements:**
- Always use `/logout` before clearing auth files
- Monitor authentication failures for brute force attempts  
- Implement account lockout policies
- Log all authentication events for audit

Sources: [troubleshooting.md:93-106]()

### Monitoring Security Events

Implement security monitoring for the telemetry infrastructure:

**Security Event Monitoring:**
- Failed authentication attempts to Grafana/Prometheus
- Unusual data access patterns
- Configuration changes
- Container runtime security events
- Network connection anomalies

**Alerting Configuration:**
- Set up alerts for authentication failures
- Monitor for data exfiltration patterns
- Track configuration drift
- Alert on container security violations

### Incident Response Procedures

**Security Incident Response:**
1. **Detection**: Automated monitoring and alerting
2. **Containment**: Isolate affected components
3. **Investigation**: Analyze logs and access patterns
4. **Recovery**: Restore from secure backups
5. **Lessons Learned**: Update security controls

**Data Breach Response:**
- Immediately disable telemetry collection
- Assess scope of data exposure
- Notify stakeholders per company policy
- Implement additional security controls
- Document incident for compliance reporting

This comprehensive security framework ensures the Claude Code ROI measurement system meets enterprise security requirements while maintaining operational effectiveness.