<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-infer · extra page ProgressTTLStrategy Decision Logic · fetched 2026-11-02 -->

# ProgressTTLStrategy Decision Logic

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agentinfer/scheduling/progress_ttl/builder.py](agentinfer/scheduling/progress_ttl/builder.py)
- [agentinfer/scheduling/progress_ttl/strategy.py](agentinfer/scheduling/progress_ttl/strategy.py)
- [tests/scheduling/test_progress_ttl_strategy.py](tests/scheduling/test_progress_ttl_strategy.py)

</details>



## Purpose and Scope
This page details the implementation, decision algorithms, and data flow of the `ProgressTTLStrategy` class (`[agentinfer/scheduling/progress_ttl/strategy.py:41-43]`). It covers admission control, continuous-growth reserve modeling, resume ordering, capacity repair, Time-To-Live (TTL) expiry, privilege handling, and batch-gain optimizations within the `agentinfer.scheduling.progress_ttl` subsystem.

---

## 1. Strategy Architecture and Initialization
`ProgressTTLStrategy` is a concrete implementation of the scheduling strategy protocol (`[agentinfer/scheduling/progress_ttl/strategy.py:41-43]`). It operates without direct side-effects, querying system snapshots and strategy factors to produce deterministic scheduling outcomes (`[agentinfer/scheduling/progress_ttl/strategy.py:47-51]`).

Strategy construction is handled by `build_progress_ttl_strategy()`, which pairs the strategy with empty global and program-level rolling statistics (`[agentinfer/scheduling/progress_ttl/builder.py:24-30]`).

```mermaid
graph TD
    A["ProgressTTLConfig"] --> B["ProgressTTLStrategy"]
    C["ProgressTTLGlobalFactors"] --> D["StrategyFactors"]
    B --> E["ProgressTTLComponents"]
    D --> E
    
    sub: "Code Entity Space"
    class B "ProgressTTLStrategy"
    class A "ProgressTTLConfig"
    class C "ProgressTTLGlobalFactors"
    class D "StrategyFactors"
    class E "ProgressTTLComponents"
```
*Figure 1: Component wiring mapping natural language configuration and factors to concrete strategy classes (`[agentinfer/scheduling/progress_ttl/builder.py:16-30]`).*

Sources: `[agentinfer/scheduling/progress_ttl/strategy.py:41-43]`, `[agentinfer/scheduling/progress_ttl/builder.py:16-30]()`.

---

## 2. Admission Control and Continuous-Growth Reserve
Admission decisions balance incoming prompt token requirements against available High Bandwidth Memory (HBM) KV cache tokens, factoring in historical input token growth and shared prefix freshness (`[agentinfer/scheduling/progress_ttl/strategy.py:53-121]`).

The strategy computes dynamic capacity reserves by projecting active token consumption across target segment rounds (`[agentinfer/scheduling/progress_ttl/strategy.py:55-65]`). The continuous-growth reserve ensures that active programs can complete their current segment without running out of KV cache capacity, preventing mid-computation thrashing.

```mermaid
graph TD
    SN[SchedulingSnapshot] --> DIAG[ProgressTTLStrategy.diagnostics]
    SF[StrategyFactors] --> DIAG
    DIAG --> RES[Projected Active Reserve Calculation]
    RES --> AC[Admission & Resume Capacity Check]
    
    sub: "Code Entity Space"
    class DIAG "ProgressTTLStrategy.diagnostics"
    class SN "SchedulingSnapshot"
    class SF "StrategyFactors"
```
*Figure 2: Diagnostic and reserve projection flow mapping `SchedulingSnapshot` and `StrategyFactors` to capacity evaluations (`[agentinfer/scheduling/progress_ttl/strategy.py:47-121]`).*

Sources: `[agentinfer/scheduling/progress_ttl/strategy.py:47-121]`, `[tests/scheduling/test_progress_ttl_strategy.py:178-191]()`.

---

## 3. Resume Ordering and Capacity Repair
When capacity frees up or paused programs request resumption, `ProgressTTLStrategy` dictates the precise queue order and priority (`[agentinfer/scheduling/progress_ttl/strategy.py:41-43]`).
- **Resume Ordering**: Pending reasoning programs take precedence over idle acting programs (`[agentinfer/scheduling/progress_ttl/strategy.py:3-8]`).
- **Capacity Repair**: If capacity is breached, the strategy identifies candidates for pausing based on segment-tenure priority, targeting programs that have exceeded their target segment duration or hold stale prefixes (`[agentinfer/scheduling/progress_ttl/strategy.py:3-8]`).

Sources: `[agentinfer/scheduling/progress_ttl/strategy.py:3-8]`, `[tests/scheduling/test_progress_ttl_strategy.py:178-191]()`.

---

## 4. TTL Expiry, Privilege, and Batch-Gain
To prevent resource starvation and guarantee progress, acting segments are bound by a Time-To-Live (TTL) expiry mechanism (`[agentinfer/scheduling/progress_ttl/strategy.py:123-132]`).

- **Forced Resume & TTL**: The internal dataclass `_ForceResumeTimeoutEstimate` calculates work-ahead estimates and arms force-resume deadlines based on request throughput and active remaining rounds (`[agentinfer/scheduling/progress_ttl/strategy.py:31-40]`).
- **Event Diagnostics**: `event_diagnostics()` evaluates newly armed acting TTLs and force-resume timeouts once their corresponding events are committed (`[agentinfer/scheduling/progress_ttl/strategy.py:123-132]`).
- **Privilege & Batch-Gain**: Programs within configured context token limits (`privileged_max_context_tokens`) receive preferential admission, while batch-gain logic groups similar prompt patterns to maximize vLLM batch efficiency (`[tests/scheduling/test_progress_ttl_strategy.py:165-176]`).

```mermaid
graph TD
    EV[SchedulingEvent] --> ED[ProgressTTLStrategy.event_diagnostics]
    SF[StrategyFactors] --> ED
    ED --> FRT[_ForceResumeTimeoutEstimate]
    FRT --> TTL[TTL Expiry & Force-Resume Arming]
    
    sub: "Code Entity Space"
    class ED "ProgressTTLStrategy.event_diagnostics"
    class FRT "_ForceResumeTimeoutEstimate"
    class EV "SchedulingEvent"
    class SF "StrategyFactors"
```
*Figure 3: Event diagnostic flow for force-resume timeouts and TTL management (`[agentinfer/scheduling/progress_ttl/strategy.py:31-40]`, `[agentinfer/scheduling/progress_ttl/strategy.py:123-132]`).*

Sources: `[agentinfer/scheduling/progress_ttl/strategy.py:31-40]`, `[agentinfer/scheduling/progress_ttl/strategy.py:123-132]`, `[tests/scheduling/test_progress_ttl_strategy.py:165-176]()`.

---

