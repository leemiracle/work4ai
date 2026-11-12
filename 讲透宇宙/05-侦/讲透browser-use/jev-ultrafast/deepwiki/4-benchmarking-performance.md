<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/jev-ultrafast · page 4 Benchmarking & Performance · fetched 2026-10-30 -->

# 4. Benchmarking & Performance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/full-speed-measurement.json](docs/full-speed-measurement.json)
- [docs/launch-draft.md](docs/launch-draft.md)
- [docs/performance.md](docs/performance.md)

</details>



This page provides an overview of how speed claims, browser interactions, and model latencies are measured, verified, and optimized in `jev-ultrafast`. Speed comparisons evaluate real-world web tasks—such as finding a flight on Google Flights [docs/performance.md:1-3]()—comparing baseline iterations against heavily optimized runtime loops [docs/performance.md:7-20]().

Below is an architectural map bridging natural-language benchmarking goals to the underlying measurement scripts, report schemas, and code components.

```mermaid
graph TD
  subgraph "Natural Language Space"
    NL_Goal[""Google Flights Task Goal""]
    NL_Tweet[""Launch Draft & Media""]
  end

  subgraph "Code Entity Space"
    Script_Measure[""scripts/measure_flights.py""]
    Script_Smoke[""scripts/smoke.py""]
    JSON_Report[""docs/full-speed-measurement.json""]
    Snap_Reader[""snapshot.js (DOM Reader)""]
    Browser_Mod[""browser.py (CDP Engine)""]
  end

  NL_Goal --> Script_Measure
  NL_Tweet --> JSON_Report
  Script_Measure --> JSON_Report
  Script_Smoke --> Snap_Reader
  Snap_Reader --> Browser_Mod
```
*Sources: [docs/performance.md:1-6](), [docs/full-speed-measurement.json:1-17]()*

---

## 4.1 Measurement Scripts

Performance evaluation relies on a suite of benchmarking and recording scripts under `scripts/`. These tools automate end-to-end task flows (such as Google Flights and Wikipedia lookups) while capturing detailed metrics like timing intervals, token usage, CDP call counts, and independent verification results [docs/performance.md:34-41]().

For detailed usage, parameter options, and instructions on running individual measurement loops, see [Measurement Scripts](#4.1).

*Sources: [docs/performance.md:34-41]()`*

---

## 4.2 Results & Measurement Reports

Performance claims are backed by structured JSON measurement reports (e.g., `docs/full-speed-measurement.json`) that record side-by-side performance across baseline and candidate arms [docs/performance.md:7-21](). Measurements track metrics such as median task duration, decision request latencies, and total CDP protocol calls (e.g., reductions in `Accessibility.getFullAXTree` and `DOM.resolveNode` usage) [docs/full-speed-measurement.json:4-17]().

For a full breakdown of the measurement JSON schema, baseline vs. candidate performance comparisons, and verification checks, see [Results & Measurement Reports](#4.2).

*Sources: [docs/full-speed-measurement.json:1-17](), [docs/performance.md:7-21]()*

---

## 4.3 Optimization History

Achieving sub-7.5-second execution times on complex dynamic web apps requires removing redundant DOM traversals and minimizing round-trips to the browser [docs/performance.md:7-18](). Key architectural enhancements include replacing repetitive accessibility tree calls with an atomic DOM snapshot reader (`snapshot.js`), implementing event-based combobox waits, fixing native select-all text replacements, and utilizing scoped click guards [docs/performance.md:22-28]().

For a detailed history of design iterations, performance bottlenecks, and the launch narrative, see [Optimization History](#4.3).

*Sources: [docs/performance.md:22-33](), [docs/launch-draft.md:1-19]()*

---

