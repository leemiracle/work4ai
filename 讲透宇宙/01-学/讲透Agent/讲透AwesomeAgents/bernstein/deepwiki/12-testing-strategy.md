<!-- source: DeepWiki mcp.deepwiki.com · repo sipyourdrink-ltd/bernstein · page 12 Testing Strategy · fetched 2026-10-26 -->

# Testing Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.coverage-baseline.json](.coverage-baseline.json)
- [.github/workflows/coverage-ratchet.yml](.github/workflows/coverage-ratchet.yml)
- [benchmarks/bench_orchestrator.py](benchmarks/bench_orchestrator.py)
- [benchmarks/bench_task_store.py](benchmarks/bench_task_store.py)
- [benchmarks/swe_bench/run.py](benchmarks/swe_bench/run.py)
- [docs/assets/ascii_logo.md](docs/assets/ascii_logo.md)
- [docs/contributing/testing.md](docs/contributing/testing.md)
- [docs/operations/coverage-ratchet.md](docs/operations/coverage-ratchet.md)
- [scripts/coverage_ratchet.py](scripts/coverage_ratchet.py)
- [src/bernstein/core/routes/api_v1.py](src/bernstein/core/routes/api_v1.py)
- [tests/chaos/README.md](tests/chaos/README.md)
- [tests/chaos/test_server_restart.py](tests/chaos/test_server_restart.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/integration/README.md](tests/integration/README.md)
- [tests/integration/conftest.py](tests/integration/conftest.py)
- [tests/integration/test_criterion_profile_routing.py](tests/integration/test_criterion_profile_routing.py)
- [tests/integration/test_full_lifecycle.py](tests/integration/test_full_lifecycle.py)
- [tests/integration/test_openclaw_bridge_flow.py](tests/integration/test_openclaw_bridge_flow.py)
- [tests/integration/test_plan_execution.py](tests/integration/test_plan_execution.py)
- [tests/unit/test_app_factory_isolation.py](tests/unit/test_app_factory_isolation.py)
- [tests/unit/test_coverage_ratchet.py](tests/unit/test_coverage_ratchet.py)
- [tests/unit/test_coverage_ratchet_workflow_yaml.py](tests/unit/test_coverage_ratchet_workflow_yaml.py)
- [tests/unit/test_post_ci_dispatcher_workflow_yaml.py](tests/unit/test_post_ci_dispatcher_workflow_yaml.py)

</details>



Bernstein employs a multi-layered testing strategy designed to ensure deterministic behavior in a multi-agent environment. Given the complexity of coordinating parallel agents and maintaining an audit-grade HMAC chain, the test suite ranges from high-speed unit tests to adversarial pentests and chaos simulations.

## The Test Pyramid

The codebase utilizes a diverse set of testing tools to catch specific bug classes, as mapped in the [Tool ↔ bug-class matrix](docs/contributing/testing.md:11-31).

| Layer | Tools | Purpose |
|:---|:---|:---|
| **Unit** | `pytest` | Validates core logic, state machines, and model schemas. |
| **Property-based** | `Hypothesis` | Detects edge cases in HMAC chains, signature roundtrips, and canonical-bytes drift [docs/contributing/testing.md:15-15](). |
| **Contract** | `Schemathesis` | Fuzzes REST API endpoints to ensure no 5xx leaks against fuzzed inputs [docs/contributing/testing.md:16-16](). |
| **Mutation** | `mutmut` | Measures test effectiveness by injecting faults into critical modules [docs/contributing/testing.md:18-20](). |
| **Integration** | `pytest` + Fake CLI | End-to-end orchestration, plan execution, and worktree lifecycle [tests/integration/conftest.py:31-36](). |
| **Hardening** | `Semgrep`, `Bandit` | Static analysis for security smells and architecture violations [docs/contributing/testing.md:21-23](). |

### Quality Gates
Bernstein implements a two-level coverage ratchet to prevent regression:
1.  **Level 1 (Diff Floor)**: Every PR's changed lines must hit a minimum diff coverage (default 85%) [docs/operations/coverage-ratchet.md:21-21]().
2.  **Level 2 (Total Ratchet)**: Total coverage may never drop below the committed high-water mark in `.coverage-baseline.json` [docs/operations/coverage-ratchet.md:22-23]().

**Sources:** [docs/contributing/testing.md:11-34](), [docs/operations/coverage-ratchet.md:17-29](), [.coverage-baseline.json:1-8]().

---

## Test Infrastructure and Patterns

Bernstein provides a robust set of fixtures and mocks to simulate the complex environment of agent orchestration without requiring live LLM API keys.

### Core Fixtures
The `tests/conftest.py` system provides several automatic isolation mechanisms:
*   **Memory Guard**: Aborts the suite if RSS exceeds 2GB to prevent runner exhaustion [tests/conftest.py:59-124]().
*   **Audit Isolation**: Redirects HMAC keys to temporary directories via `BERNSTEIN_AUDIT_KEY_PATH` to prevent home directory pollution [tests/conftest.py:148-166]().
*   **Auth Bypass**: Disables authentication by default for unit tests using `BERNSTEIN_AUTH_DISABLED=1` [tests/conftest.py:169-184]().
*   **Adaptive Parallelism**: Forces deterministic CPU percentage reporting (0.0%) so tests are not flaky under ambient load [tests/conftest.py:137-146]().

For details, see **[Test Infrastructure and Patterns](#12.1)**.

**Sources:** [tests/conftest.py:1-201](), [scripts/coverage_ratchet.py:1-73](), [tests/unit/test_coverage_ratchet_workflow_yaml.py:1-52]().

---

## Integration, Chaos, and Pentest Suites

The integration layer focuses on the interaction between the `Orchestrator`, `TaskServer`, and `AgentSpawner`.

### Integration Flow: Code Entity Mapping
The following diagram illustrates how integration tests bridge natural language requirements to code entities using the `IntegrationMockAdapter`.

**Integration Test Component Interaction**
```mermaid
graph TD
    subgraph "Test Harness"
        [test_client] -- "FastAPI TestClient" --> [create_app]
        [fake_cli_fixture] -- "Subprocess" --> [CLIAdapter]
    end

    subgraph "Bernstein Core Space"
        [create_app] -- "Routes" --> [api_v1.py]
        [api_v1.py] -- "Updates" --> [TaskStore]
        [Orchestrator] -- "Polls" --> [TaskStore]
        [Orchestrator] -- "Triggers" --> [AgentSpawner]
    end

    subgraph "Execution Space"
        [AgentSpawner] -- "Spawns" --> [IntegrationMockAdapter]
        [IntegrationMockAdapter] -- "Writes" --> [DONE_marker_file]
        [IntegrationMockAdapter] -- "Executes" --> [git_commit_cmd]
    end

    [TaskStore] -- "Persistence" --> [tasks.jsonl]
```
**Sources:** [tests/integration/conftest.py:42-145](), [src/bernstein/core/routes/api_v1.py:42-54](), [tests/integration/conftest.py:148-185]().

### Adversarial and Chaos Testing
*   **Chaos Tests**: Simulate infrastructure failures like `server_restart` to verify that the `Orchestrator` resumes correctly from the `.sdd` state [tests/chaos/test_server_restart.py]().
*   **Routing Integration**: Verifies that `criterion_profile` metadata correctly diverts `route_task` logic (e.g., "safety-first" routing to `opus`) [tests/integration/test_criterion_profile_routing.py:61-73]().

For details, see **[Integration, Chaos, and Pentest Suites](#12.2)**.

**Sources:** [tests/integration/test_criterion_profile_routing.py:1-17](), [tests/chaos/README.md]().

---

## Benchmarking and Performance

Performance is tracked via dedicated scripts in the `benchmarks/` directory to detect latency regressions in core persistence and scheduling loops.

### Task Store Latency
The `bench_task_store.py` script measures the throughput of the `TaskStore` [benchmarks/bench_task_store.py:10-10](). It benchmarks:
1.  **Creation**: Throughput of `store.create(req)` [benchmarks/bench_task_store.py:27-50]().
2.  **Claiming**: Latency for `store.claim_next(role)` [benchmarks/bench_task_store.py:53-61]().
3.  **Flush Latency**: Time taken to commit the internal `_BUFFER_MAX` to disk [benchmarks/bench_task_store.py:71-81]().

**Sources:** [benchmarks/bench_task_store.py:1-87](), [benchmarks/swe_bench/run.py]().

---

