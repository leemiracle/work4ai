<!-- source: DeepWiki mcp.deepwiki.com · repo smixs/creative-director-skill · page 1 Overview · fetched 2026-10-27 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [NOTICE](NOTICE)
- [README.md](README.md)
- [README.ru.md](README.ru.md)
- [creative-director/SKILL.md](creative-director/SKILL.md)

</details>



This page describes what the Creative Director Skill repository is, what problem it solves, and how its components fit together at a high level. For detailed documentation of any specific phase or module, follow the links in the relevant sections below.

---

## Purpose

The Creative Director Skill v2.0 is a structured, AI-executable creative process implemented entirely in markdown files. It accepts a brief in any format — text, voice transcript, PDF, raw notes — and runs a five-phase pipeline that produces scored, refined advertising concepts in a presentation-ready format.

It is not a general brainstorming prompt. It enforces the workflow discipline used by top-tier advertising agencies (Droga5, Wieden+Kennedy, Mother): insight before ideas, structured methodology over free association, and **calibration against the canon** of 571 legendary campaigns to ensure originality.

The repository is platform-agnostic. The entire logic lives in markdown files with no runtime dependencies. It works with Claude Projects, Claude Code, Cursor, Windsurf, or any AI agent that accepts structured instructions. For details on integration and invocation, see [Getting Started](#1.1).

Sources: [README.md:1-16](), [creative-director/SKILL.md:1-16]()

---

## What's New in v2.0

Version 2.0 introduces a massive expansion of the underlying data and evaluation frameworks:

*   **571-Case Library:** A structured database of legendary campaigns (1950–2025) used for pattern calibration and originality benchmarking [README.md:35]().
*   **17-Axis Schema:** Every card in the library is tagged across 17 axes (pattern, industry, emotion, budget, etc.) [README.md:36]().
*   **6 MOCs (Maps of Content):** Automated indices for fast lookup by pattern, emotion, format, industry, budget, and chronology [README.md:37]().
*   **Pollard 7-Level Taxonomy:** Replaces the 3-level system to precisely define idea scope (Business, Brand, Tagline, Advertising, Campaign, Non-advertising, Execution) [README.md:40]().
*   **3-Tier Emotion Hierarchy:** A system for moving from generic "happy" ads to Tier 3 complex, contradictory emotions like "bittersweet pride" [README.md:41]().
*   **Activation Toolkit:** Specific logic for non-advertising ideas and PR stunts with a "remove the campaign" diagnostic test [README.md:42]().
*   **Empirical Originality Cap:** If 3+ canonical cases use the same mechanic, the originality score is capped at 7 to prevent AI hallucination of "newness" [README.md:57]().
*   **Case-Soaking RESTART:** A recovery loop for when ideation plateaus, requiring the system to read 8-12 canonical cards to reset its standards [README.md:58]().
*   **Pre-Mortem:** A final failure-simulation step before delivery to surface likely risks [README.md:43]().

Sources: [README.md:33-43]()

---

## Repository File Structure

**Diagram: File tree mapped to system roles**

```mermaid
graph TD
    ROOT["creative-director-skill/"]
    ROOT --> SKILL["creative-director/SKILL.md\n(Phase router + core instructions)"]
    ROOT --> ASSETS["assets/\n(Output templates)"]
    ROOT --> SCRIPTS["scripts/\n(Python maintenance: uv)"]
    ROOT --> REFS["references/"]

    SCRIPTS --> VS["validate_schema.py\nFrontmatter check"]
    SCRIPTS --> GM["generate_mocs.py\nBuilds 6 MOCs"]
    SCRIPTS --> GL["generate_links.py\nWikilink graph"]

    REFS --> TS["tag-schema.md\n17-axis contract"]
    REFS --> IT["idea-taxonomy.md\nPollard 7-level scope"]
    REFS --> EH["emotion-hierarchy.md\n3-tier complexity"]
    REFS --> AT["activation-toolkit.md\n9 activation formats"]
    REFS --> LP["legendary-patterns.md\nP01-P18 mechanics"]
    REFS --> MC["methods-catalog.md\n20+ ideation methodologies"]
    REFS --> LC["legendary-campaigns/\n571-case library"]
    
    LC --> MOCS["MOC-index.md, MOC-pattern.md,\nMOC-emotion.md, MOC-format.md,\nMOC-industry.md, MOC-budget.md"]
```

Sources: [README.md:81-97](), [README.ru.md:81-97]()

`SKILL.md` is the sole orchestration point [creative-director/SKILL.md:27-37](). It sequences operations and delegates to reference modules. The `scripts/` directory contains Python tools managed via `uv` to maintain the integrity of the campaign library and its MOCs [README.md:39](). For a detailed map of all reference files, see [Reference Files Guide](#7.1). For details on the maintenance scripts, see [Maintenance Scripts](#7.2).

---

## The Five-Phase Pipeline

**Diagram: Phase sequence with Canon Calibration**

```mermaid
flowchart TD
    BRIEF(["User Brief\n(text / voice / PDF / notes)"])
    
    P1["PHASE 1: INTAKE\ncreative-director/SKILL.md\nPollard 7-level check\nActivation diagnostic"]
    
    P2["PHASE 2: INSIGHT\nreferences/insight-mining.md\n7 techniques: Pollard 4-points,\nJTBD, Tension Spotting"]
    
    P3["PHASE 3: IDEATION\nreferences/methods-catalog.md\nPRIME: Scan 5-7 cases from MOCs\n3 methods x 8-12 ideas"]
    
    P4["PHASE 4: EVALUATE + REFINE\nreferences/scoring-calibration.md\nOriginality Cap via Library\nRESTART: Case-soaking loop"]
    
    P5["PHASE 5: ARTICULATE\nassets/output-templates.md\nPre-Mortem Failure Simulation"]
    
    OUTPUT(["Final Deliverable"])

    BRIEF --> P1
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 -- "Score < 9 or Plateau" --> RESTART["RESTART: Case-Soaking\nRead 8-12 canonical cards"]
    RESTART --> P3
    P4 -- "Score >= 9" --> P5
    P5 --> OUTPUT
```

Sources: [README.md:50-59](), [creative-director/SKILL.md:27-133]()

### Phase Summary

| Phase | Core Logic File | Key V2.0 Addition |
|---|---|---|
| **1 · Intake** | `SKILL.md` | Pollard 7-level `idea_type` classification [creative-director/SKILL.md:52-62]() |
| **2 · Insight** | `references/insight-mining.md` | Cultural/Category/Human Tension spotting [creative-director/SKILL.md:78-81]() |
| **3 · Ideation** | `references/methods-catalog.md` | **Canon Priming**: Scanning relevant MOCs before generating [creative-director/SKILL.md:99]() |
| **4 · Evaluate** | `references/scoring-calibration.md` | **Originality Cap**: 3+ existing cases = max score 7 [README.md:57]() |
| **5 · Articulate** | `assets/output-templates.md` | **Pre-Mortem**: Simulate failure before final delivery [README.md:43]() |

For a high-level description of the entire creative pipeline, see [Creative Process](#2). Each phase is detailed in its respective child page (e.g., [Phase 1: Intake](#2.1)).

---

## Evaluation & Originality Calibration

**Diagram: Empirical Originality and Scoring**

```mermaid
graph TD
    IDEA["Generated Concept"]
    LIB["legendary-campaigns/ (571 cases)"]
    
    IDEA --> PATTERN["Identify Pattern (P01-P18)"]
    PATTERN --> SCAN["Scan MOC-pattern.md"]
    SCAN -- "3+ Matches Found" --> CAP["Originality Cap: 7/10"]
    SCAN -- "Novel Variant" --> NO_CAP["Full Score Potential"]
    
    IDEA --> RUBRIC["references/scoring-calibration.md\n6 Weighted Criteria"]
    IDEA --> TIER["references/emotion-hierarchy.md\nTier 3 Complexity Check"]
    
    CAP --> TOTAL["Final Quality Score"]
    NO_CAP --> TOTAL
    TIER -- "Tier 1 (Generic)" --> T1_CAP["Emotional Score <= 6"]
    TIER -- "Tier 3 (Complex)" --> T3_POTENTIAL["Emotional Score 8-10"]
```

Sources: [README.md:57](), [creative-director/SKILL.md:143-149]()

The system uses three parallel scoring approaches:
1.  **6 Weighted Criteria:** Originality (0.25), Strategic Fit (0.20), Emotional Response (0.20), Feasibility (0.15), Scalability (0.10), Simplicity (0.10) [creative-director/SKILL.md:143-149]().
2.  **HumanKind Scale:** 1–10 scale measuring human impact [README.md:57]().
3.  **Grey Scale:** 1–10 scale measuring creative "heat" [README.md:57]().

For a detailed reference on scoring and calibration, see [Evaluation System](#4).

---

## Methodology Credits

The system is built on published methodologies from named practitioners:

*   **SIT / TRIZ** — Jacob Goldenberg / Genrich Altshuller
*   **Lateral Thinking / PO** — Edward de Bono
*   **7-Level Taxonomy / Four Points** — Mark Pollard [creative-director/SKILL.md:77]()
*   **JTBD** — Clayton Christensen [creative-director/SKILL.md:78]()
*   **Storytelling** — Nancy Duarte (Sparkline), Pixar (Story Spine)
*   **Creative Constitution** — Voskresensky / IKRA

Sources: [README.md:26-27](), [creative-director/SKILL.md:77-78]()

---

## License

The Creative Director Skill is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license [LICENSE:1-2](). Any use, copy, or derivative of this skill, including the 571-case legendary campaigns library, must credit Serge Shima as the author [NOTICE:4-9](). For full details, see [Licensing and Attribution](#1.2).

Sources: [LICENSE:1-2](), [NOTICE:4-9]()

---

