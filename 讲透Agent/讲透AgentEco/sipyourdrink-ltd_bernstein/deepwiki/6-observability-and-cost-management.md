<!-- source: DeepWiki mcp.deepwiki.com · repo sipyourdrink-ltd/bernstein · page 6 Observability and Cost Management · fetched 2026-10-27 -->

# Observability and Cost Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cursor/rules/directory-context.mdc](.cursor/rules/directory-context.mdc)
- [docs/observability/trends.md](docs/observability/trends.md)
- [src/bernstein/adapters/AGENTS.md](src/bernstein/adapters/AGENTS.md)
- [src/bernstein/adapters/mock.py](src/bernstein/adapters/mock.py)
- [src/bernstein/cli/AGENTS.md](src/bernstein/cli/AGENTS.md)
- [src/bernstein/core/knowledge/agents_md_generator.py](src/bernstein/core/knowledge/agents_md_generator.py)
- [src/bernstein/core/lineage/AGENTS.md](src/bernstein/core/lineage/AGENTS.md)
- [src/bernstein/core/routes/observability.py](src/bernstein/core/routes/observability.py)
- [src/bernstein/core/routes/status_dashboard.py](src/bernstein/core/routes/status_dashboard.py)
- [tests/unit/test_agents_md_generator.py](tests/unit/test_agents_md_generator.py)
- [tests/unit/test_audit_004_guards_removed.py](tests/unit/test_audit_004_guards_removed.py)
- [tests/unit/test_cli_demo.py](tests/unit/test_cli_demo.py)
- [tests/unit/test_lifecycle_transitions.py](tests/unit/test_lifecycle_transitions.py)
- [tests/unit/test_mock_adapter.py](tests/unit/test_mock_adapter.py)
- [tests/unit/test_queue_depth_tracking.py](tests/unit/test_queue_depth_tracking.py)
- [tests/unit/test_quickstart_poll.py](tests/unit/test_quickstart_poll.py)
- [tests/unit/test_status_dashboard_task_rows.py](tests/unit/test_status_dashboard_task_rows.py)
- [tests/unit/test_task_store_property.py](tests/unit/test_task_store_property.py)
- [tests/unit/test_tick_concurrency.py](tests/unit/test_tick_concurrency.py)
- [tests/unit/test_timeout_behavior.py](tests/unit/test_timeout_behavior.py)

</details>



Bernstein provides a comprehensive observability and cost management stack designed for high-concurrency multi-agent environments. The system balances deep operational visibility with strict financial controls, ensuring that autonomous agent swarms remain within budget and performant.

The observability architecture is divided into two primary domains:
1.  **Operational Health**: Real-time monitoring of task lifecycles, agent heartbeats, and system bottlenecks via the `/observability` and `/status` endpoints.
2.  **Cost Stewardship**: Precise tracking of token usage and USD spend, integrated with the orchestrator to provide hard-stop safety rails via the `CostTracker`.

## System Interaction Map

The following diagram illustrates how observability and cost components bridge the gap between high-level orchestration and low-level execution, specifically focusing on how runtime state is surfaced to the dashboard.

### Observability and Dashboard Data Flow
```mermaid
graph TD
    subgraph "Orchestration Layer"
        ORCH["Orchestrator Tick Loop"]
        CT["CostTracker"]
        monitor["HeartbeatMonitor"]
    end

    subgraph "Execution Layer (Code Entities)"
        ADAPTER["CLIAdapter"]
        AGG["AgentLogAggregator"]
        SCORER["EffectivenessScorer"]
    end

    subgraph "API Layer (src/bernstein/core/routes/)"
        OBS_ROUTE["observability.py"]
        STATUS_ROUTE["status_dashboard.py"]
    end

    ORCH -->| "report_usage" | CT
    monitor -->| "check(session_id)" | OBS_ROUTE
    AGG -->| "parse_log(session_id)" | OBS_ROUTE
    SCORER -->| "recent(50)" | OBS_ROUTE
    CT -->| "_load_live_costs" | STATUS_ROUTE
    ADAPTER -->| "lineage write boundary" | CT
```
Sources: [src/bernstein/core/routes/observability.py:90-110](), [src/bernstein/core/routes/status_dashboard.py:43-50](), [src/bernstein/adapters/base.py:24-26]()

## Metrics, Tracing, and Alerting

Bernstein uses a dedicated `MetricsCollector` and the `HeartbeatMonitor` to track system-wide telemetry. Key metrics include task queue depth, agent stall profiles, and model effectiveness trends.

*   **Heartbeat and Stall Detection**: The `HeartbeatMonitor` tracks agent activity, while `compute_stall_profile` determines if an agent has hung and requires a restart [src/bernstein/core/routes/observability.py:97-111]().
*   **Effectiveness Scoring**: The `EffectivenessScorer` tracks the quality of agent outputs over time, classifying trends as "improving", "declining", or "stable" [src/bernstein/core/routes/observability.py:75-87]().
*   **Prometheus Integration**: Metrics are exposed via the task server for integration with Grafana and external alerting systems [src/bernstein/core/prometheus.py:18-20]().

For details, see [Metrics, Tracing, and Alerting](#6.1).

| Metric Category | Source Entity | Description |
| :--- | :--- | :--- |
| **Agent Health** | `HeartbeatMonitor` | Age, phase, and progress percentage of active sessions. |
| **Log Summary** | `AgentLogAggregator` | Error counts, warnings, and rate-limit hits per agent. |
| **Effectiveness** | `EffectivenessScorer` | Rolling average of task success and best model configs. |
| **Vulnerabilities** | `observability/trends.md` | Sparklines for critical, high, and medium alerts. |

Sources: [src/bernstein/core/routes/observability.py:127-146](), [src/bernstein/core/routes/observability.py:158-183](), [docs/observability/trends.md:9-21]()

## Cost Tracking and Budget Enforcement

Cost management is handled by the `CostTracker` and enforced during the task lifecycle. The system prevents "retry spirals" by tracking lineage and ensuring failed tasks do not inflate perceived progress.

*   **Budget Thresholds**: The `CompletionBudget` and `CostTracker` monitor live spend against seeded totals. The system issues warnings and triggers hard stops at 100% of the allocated budget.
*   **Retry Lineage**: To ensure accurate reporting, every task row in the status dashboard carries a `lineage_id` (the `original_task_id`), preventing retries from being double-counted as new work [tests/unit/test_status_dashboard_task_rows.py:18-30]().
*   **Preflight Estimation**: The `bernstein demo` and `run` commands perform preflight checks to estimate potential costs before spawning agents [tests/unit/test_cli_demo.py:33-49]().

For details, see [Cost Tracking and Budget Enforcement](#6.2).

### Cost and Lifecycle Code Entities
```mermaid
graph LR
    subgraph "src/bernstein/core/"
        CB["CompletionBudget (Class)"]
        TS["TaskStore (Class)"]
        WAL["WALWriter (Class)"]
    end

    subgraph "src/bernstein/core/lifecycle.py"
        TRANS["transition_task (Function)"]
    end

    TS -->| "list_tasks" | CB
    TRANS -->| "records event" | WAL
    WAL -->| "committed=False" | REC["WALRecovery"]
```
Sources: [src/bernstein/core/routes/observability.py:93-99](), [tests/unit/test_lifecycle_transitions.py:28-30](), [tests/unit/test_tick_concurrency.py:123-135]()

## Operational Commands

The CLI provides direct access to observability and cost data through the `bernstein cost` and `bernstein doctor` commands.

*   **`bernstein cost`**: Aggregates spend visibility across all recorded metrics, providing summaries of USD usage [tests/unit/test_cli_demo.py:118-125]().
*   **`bernstein doctor observe`**: Generates JSON snapshots of system health, including vulnerability counts and open alerts used for trend analysis [docs/observability/trends.md:5-15]().
*   **`bernstein stop`**: Initiates a graceful shutdown, ensuring agent sessions are transitioned to a "dead" status and final metrics are flushed [src/bernstein/core/routes/observability.py:113-119]().

| Command | File Context | Purpose |
| :--- | :--- | :--- |
| `bernstein cost` | `cli/run_confirm.py` | Render spend summaries and task outcomes. |
| `bernstein doctor` | `observability/trends.md` | Generate health snapshots and sparklines. |
| `bernstein audit` | `test_cli_demo.py` | Verify audit chain integrity using `--merkle-only`. |

Sources: [tests/unit/test_cli_demo.py:104-116](), [docs/observability/trends.md:5-10](), [src/bernstein/core/routes/status_dashboard.py:143-159]()

---

