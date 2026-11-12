<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/rl-env-use · page 2 Environment Build Pipeline · fetched 2026-10-30 -->

# Environment Build Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



The Environment Build Pipeline automates the translation of a high-level domain specification into a verified, un-saturated set of reinforcement learning tasks [README.md:9-12](). It orchestrates autonomous browser agents to harvest real-world materials [README.md:24](), synthesizes deterministic grading logic, runs multi-model frontier evaluations, and hardens tasks against memorization and leakage [README.md:25-26]().

```mermaid
graph TD
    Spec[""spec.json (Natural Language Spec)""] --> Scout[""scout.py / browse.py (Mining Missions)""]
    Scout --> KB[""kb.json (Cases & Materials)""]
    KB --> Look[""look (HTTP Browser Edge)""]
    Look --> Synth[""tasks.py (Task Synthesis)""]
    Synth --> Graders[""graders.py (Gold & Checks)""]
    Graders --> Verify[""verify.py (Critic & Panel)""]
    Verify --> Harden[""harden (All-Pass Capping)""]
    Harden --> Tasks[""tasks.jsonl (Verified Task Set)""]
```
Sources: `SKILL.md:18-23` [SKILL.md:18-23](), `SKILL.md:32-40` [SKILL.md:40]().

---

## 2.1. Mining with Browser Use Agents

The initial stage of the pipeline uses autonomous browser agents to explore target URLs defined in the domain specification. Missions extract source materials and quote-verified outcome facts, persisting them into `kb.json` [SKILL.md:18-20](). Following extraction, the `look` stage measures what plain HTTP scrapers would have observed, isolating the value added by full browser navigation (the browser edge).

For details, see [Mining with Browser Use Agents](#2.1).

```mermaid
graph LR
    MissionSpec[""spec.json Sources""] --> ScoutModule[""scout.py""]
    ScoutModule --> AgentRun[""Browser Use Agents""]
    AgentRun --> KBFile[""kb.json (Materials & Facts)""]
    KBFile --> LookCheck[""look Stage (HTTP Edge Analysis)""]
```
Sources: `SKILL.md:18-21` [SKILL.md:18-21](), `SKILL.md:36-40` [SKILL.md:36-40]().

---

## 2.2. Task Synthesis and Grading Checks

Once raw cases and materials are stored in `kb.json`, the synthesis engine derives evaluation tasks [SKILL.md:21](). Tasks are structured either as derived computations over tabular data or future forecasts [SKILL.md:37-39](). The `tasks.py` and `graders.py` modules assign gold answers and configure validation checks across multiple check types (`number`, `date`, `set`, `exact`, `contains`, `prob`), filtering out ambiguous or low-quality prompts [README.md:25]().

For details, see [Task Synthesis and Grading Checks](#2.2).

```mermaid
graph LR
    KBData[""kb.json Materials""] --> SynthModule[""tasks.py (Derive / Forecast)""]
    SynthModule --> GraderModule[""graders.py (Gold & Checks)""]
    GraderModule --> FilterRules[""Task Keep / Filter Rules""]
    FilterRules --> DraftTasks[""tasks.jsonl (Draft Tasks)""]
```
Sources: `SKILL.md:21` [SKILL.md:21](), `SKILL.md:37-41` [SKILL.md:41](), `README.md:25-27` [README.md:27]().

---

## 2.3. Verification, Frontier Panel and Hardening

Synthesized tasks undergo rigorous verification via `verify.py` [SKILL.md:38-40](). This stage subjects drafts to critic evaluations, live checks, and closed-book memorizability tests [README.md:25-26](). A frontier panel of advanced models evaluates task difficulty; tasks solved universally by the panel trigger all-pass capping and are returned to the generator to be made harder [SKILL.md:38-40]().

For details, see [Verification, Frontier Panel and Hardening](#2.3).

```mermaid
graph LR
    Drafts[""tasks.jsonl (Drafts)""] --> VerifyModule[""verify.py (Critic & Live Checks)""]
    VerifyModule --> PanelEval[""Frontier Panel (Difficulty Calibration)""]
    PanelEval --> AllPassCheck{""All-Pass Solved?""}
    AllPassCheck -- Yes --> HardenLoop[""Task Hardening Loop""]
    AllPassCheck -- No --> FinalVerify[""Verified Task Set""]
    HardenLoop --> SynthModule[""tasks.py""]
```
Sources: `SKILL.md:38-42` [SKILL.md:42](), `README.md:25-27` [README.md:27]().

---

