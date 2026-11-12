<!-- source: DeepWiki mcp.deepwiki.com · repo Imbad0202/academic-research-skills · page 13 SR-Screener Skill · fetched 2026-10-30 -->

# SR-Screener Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json)
- [.claude/CLAUDE.md](.claude/CLAUDE.md)
- [MODE_REGISTRY.md](MODE_REGISTRY.md)
- [README.ja-JP.md](README.ja-JP.md)
- [README.ko-KR.md](README.ko-KR.md)
- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [README.zh-TW.md](README.zh-TW.md)
- [academic-pipeline/SKILL.md](academic-pipeline/SKILL.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [scripts/check_spec_consistency.py](scripts/check_spec_consistency.py)
- [scripts/test_sr_screener_pipeline.py](scripts/test_sr_screener_pipeline.py)
- [sr-screener/scripts/srlib.py](sr-screener/scripts/srlib.py)

</details>



## Purpose and Scope
The `sr-screener` skill (`v1.0.0`) provides protocol-driven study screening for systematic, scoping, and rapid reviews [.claude/CLAUDE.md:13-13](), [.claude-plugin/marketplace.json:20-20](). Sitting operationally between `deep-research` and `academic-paper`, it bridges literature gathering and manuscript composition by ingesting database exports, executing dual blinded AI reviews alongside third-reviewer adjudication, and outputting PRISMA-compliant tracking metrics and corpus handoffs [.claude/CLAUDE.md:13-13]().

As a parent page, this document provides a high-level overview of the screening architecture. For granular specifications on operational modes, ordered exclusion codes, and quality control metrics, see [Screening Modes and Adjudication Protocol](#13.1). For implementation details regarding parser scripts, deduplication routines, and handoff schemas, see [Screening Scripts and Handoff Outputs](#13.2).

Sources: [.claude/CLAUDE.md:13-13](), [.claude-plugin/marketplace.json:20-20]()

---

## Architectural Mapping: Natural Language to Code Entity Space

The following diagram maps high-level user intents and screening workflows to the underlying codebase entities and script execution boundaries within the repository.

```mermaid
graph TD
    Intent[""User Screening Intent""] -->|"/ars-* command or keyword"| Router[""Routing Core (.claude/CLAUDE.md)""]
    Router -->|""Dispatch sr-screener""| SkillDef[""sr-screener/SKILL.md""]
    SkillDef -->|""Invoke Python Toolkit""| CoreLib[""sr-screener/scripts/srlib.py""]
    CoreLib -->|""Execute Test Suite""| TestRunner[""scripts/test_sr_screener_pipeline.py""]

    classDef default fill:none,stroke:#000,stroke-width:1px;
```

Sources: [.claude/CLAUDE.md:13-13](), [sr-screener/scripts/srlib.py:1-1](), [scripts/test_sr_screener_pipeline.py:1-1]()

---

## Screening Modes and Workflow Overview

The `sr-screener` skill supports 8 distinct operational modes governed by fidelity and oversight requirements [MODE_REGISTRY.md:58-70](). These modes cover the complete lifecycle of a screening task, from protocol generation and quick validation to dual title/abstract screening, full-text eligibility review, adjudication, exclusion auditing, and final reporting.

For detailed breakdowns of each mode, ordered exclusion codes, seed studies, inter-rater reliability metrics (kappa/PABAK), and PRISMA 2020 counting protocols, refer to [Screening Modes and Adjudication Protocol](#13.1).

Sources: [MODE_REGISTRY.md:58-70]()

---

## Data Flow and Handoff Architecture

The screening pipeline processes heterogeneous bibliographic imports, removes duplicates, executes batch evaluations, and culminates in a structured corpus output suitable for downstream academic writing.

```mermaid
graph TD
    Import[""Bibliographic Imports (RIS, .nbib, WoS, CSV)""] -->|""parse_ris / parse_csv""| ScriptLib[""sr-screener/scripts/srlib.py""]
    ScriptLib -->|""Deduplication & Batched Processing""| DualReview[""Dual Blinded AI Reviewers""]
    DualReview -->|""Conflict Detection""| Adjudicator[""Third-Reviewer Adjudicator""]
    Adjudicator -->|""Consensus Decision""| CorpusHandoff[""literature_corpus[] Handoff Artifact""]
    CorpusHandoff -->|""Input Port""| AcademicPaper[""academic-paper Skill""]

    classDef default fill:none,stroke:#000,stroke-width:1px;
```

Sources: [.claude/CLAUDE.md:24-24](), [sr-screener/scripts/srlib.py:1-1]()

For complete technical documentation on supported import formats, quoting rules (such as RFC 4180 CSV parsing), resumable batch logs, formula-neutralized spreadsheet exports, and the `literature_corpus[]` handoff mechanism to `academic-paper`, see [Screening Scripts and Handoff Outputs](#13.2).

Sources: [.claude/CLAUDE.md:18-24](), [sr-screener/scripts/srlib.py:1-1]()

---

