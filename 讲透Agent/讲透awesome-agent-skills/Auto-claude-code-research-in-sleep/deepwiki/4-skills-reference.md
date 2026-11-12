<!-- source: DeepWiki mcp.deepwiki.com · repo wanshuiyin/Auto-claude-code-research-in-sleep · page 4 Skills Reference · fetched 2026-10-26 -->

# Skills Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENT_GUIDE.md](AGENT_GUIDE.md)
- [docs/ARIS_INTRO.html](docs/ARIS_INTRO.html)
- [docs/ARIS_INTRO.md](docs/ARIS_INTRO.md)
- [docs/SKILLS_CATALOG.md](docs/SKILLS_CATALOG.md)
- [skills/skills-codex/README.md](skills/skills-codex/README.md)
- [skills/skills-codex/README_CN.md](skills/skills-codex/README_CN.md)

</details>



This page provides a high-level reference for the 82+ composable skills in the ARIS system [AGENT_GUIDE.md:27](). Each skill is a modular unit of research automation invoked via slash commands in Claude Code, Cursor, or Codex CLI, or chained together to form end-to-end pipelines [AGENT_GUIDE.md:5-32]().

For configuration details, see [Codex MCP (OpenAI Models)](#5.1). For workflow orchestration details, see [Research Workflows](#3). 

## Overview of Skill Ecosystem

ARIS skills operate across two independent control axes: **Axis 1 (`effort`)** which controls execution depth and resource budgets (`lite | balanced | max | beast`), and **Axis 2 (`assurance`)** which controls audit strictness (`draft | polished | conference-ready | submission`) [AGENT_GUIDE.md:34-52](). 

The following diagram bridges natural language intents to the underlying `SKILL.md` code entities in the repository.

```mermaid
graph TB
    subgraph "NaturalLanguageSpace"
        intent_lit[""FindpapersonX"""]
        intent_exp[""Runmytraining"""]
        intent_loop[""Improvethispaper"""]
        intent_overleaf[""SyncOverleaf"""]
    end

    subgraph "CodeEntitySpace"
        research_pipeline[""/research-pipeline<br/>(skills/research-pipeline/SKILL.md)""]
        auto_review_loop[""/auto-review-loop<br/>(skills/auto-review-loop/SKILL.md)""]
        resubmit_pipeline[""/resubmit-pipeline<br/>(skills/resubmit-pipeline/SKILL.md)""]
        research_lit[""/research-lit<br/>(skills/research-lit/SKILL.md)""]
        run_experiment[""/run-experiment<br/>(skills/run-experiment/SKILL.md)""]
        overleaf_sync[""/overleaf-sync<br/>(skills/overleaf-sync/SKILL.md)""]
        citation_audit[""/citation-audit<br/>(skills/citation-audit/SKILL.md)""]
    end

    intent_lit --> research_lit
    intent_exp --> run_experiment
    intent_loop --> auto_review_loop
    intent_overleaf --> overleaf_sync
    
    research_pipeline --> research_lit
    research_pipeline --> auto_review_loop
    
    resubmit_pipeline --> citation_audit
    resubmit_pipeline --> overleaf_sync
```

Sources: [AGENT_GUIDE.md:34-84](), [docs/SKILLS_CATALOG.md:21-41]()

---

## Skill Categories

ARIS skills are categorized by their function in the research lifecycle. Because this is a parent page, each section provides a high-level summary and links to its respective child page for arguments, allowed tools, and detailed usage examples.

### 4.1 Literature & Analysis Skills
These skills handle multi-source paper retrieval, novelty verification, and domain-specific literature surveys across arXiv, Semantic Scholar, OpenAlex, and Exa [docs/SKILLS_CATALOG.md:48-61]().
- **Key Skills:** `/research-lit`, `/novelty-check`, `/arxiv`, `/semantic-scholar`, `/gemini-search`, `/openalex`, `/exa-search`, `/deepxiv`, `/alphaxiv`, `/comm-lit-review`.
- **For details, see [Literature & Analysis Skills](#4.1)**

Sources: [docs/SKILLS_CATALOG.md:48-61]()

### 4.2 Idea & Review Skills
Automates brainstorming, proposal structuring, method refinement, and experiment planning prior to code implementation [docs/SKILLS_CATALOG.md:66-73]().
- **Key Skills:** `/idea-creator`, `/research-review`, `/research-refine`, `/research-refine-pipeline`, `/experiment-plan`, `/idea-discovery-robot`.
- **For details, see [Idea & Review Skills](#4.2)**

Sources: [docs/SKILLS_CATALOG.md:66-73]()

### 4.3 Experiment Execution Skills
Manages GPU job deployment, remote execution via SSH or serverless backends (Modal, Vast.ai), and monitoring via `watchdog.py`.
- **Key Skills:** `/run-experiment`, `/monitor-experiment`, `/training-check`, `/result-to-claim`, `/ablation-planner`, `/experiment-queue`, `/vast-gpu`, `/serverless-modal`, `/qzcli`.
- **For details, see [Experiment Execution Skills](#4.3)**

Sources: [docs/SKILLS_CATALOG.md:74-95]()

### 4.4 Paper Generation Skills
Automates LaTeX compilation, figure generation, poster layout, slide decks, and two-way Overleaf synchronization [docs/SKILLS_CATALOG.md:96-120]().
- **Key Skills:** `/paper-plan`, `/paper-figure`, `/paper-write`, `/paper-compile`, `/paper-illustration`, `/figure-spec`, `/paper-poster`, `/paper-poster-html`, `/paper-slides`, `/slides-polish`, `/overleaf-sync`, `/mermaid-diagram`.
- **For details, see [Paper Generation Skills](#4.4)**

Sources: [docs/SKILLS_CATALOG.md:96-120]()

### 4.5 Workflow Orchestration Skills
High-level orchestrators that chain atomic skills into robust end-to-end research pipelines, managing state persistence and review loops [docs/SKILLS_CATALOG.md:21-43]().
- **Key Skills:** `/research-pipeline`, `/idea-discovery`, `/auto-review-loop`, `/paper-writing`, `/experiment-bridge`, `/rebuttal`, `/resubmit-pipeline`, `/paper-talk`, `/patent-pipeline`, `/dse-loop`.
- **For details, see [Workflow Orchestration Skills](#4.5)**

Sources: [docs/SKILLS_CATALOG.md:21-43]()

### 4.6 Utility & Specialized Skills
Domain-specific helpers for formula derivations, proof writing, HTML rendering, feishu notifications, and system profiling [docs/SKILLS_CATALOG.md:121-150]().
- **Key Skills:** `/pixel-art`, `/feishu-notify`, `/grant-proposal`, `/proof-writer`, `/formula-derivation`, `/system-profile`, `/render-html`, `/interview-cheatsheet`, `/writing-systems-papers`, `/web-debug-search`.
- **For details, see [Utility & Specialized Skills](#4.6)**

Sources: [docs/SKILLS_CATALOG.md:121-150]()

### 4.7 Research Wiki & Meta-Optimize Skills
Manages persistent knowledge graphs (`research_wiki.py`) and outer-loop self-optimization (`/meta-optimize` and `/meta-apply`) [docs/SKILLS_CATALOG.md:41-43]() [AGENT_GUIDE.md:1-20]().
- **Key Skills:** `/research-wiki`, `/wiki-enrich`, `/meta-optimize`, `/meta-apply`.
- **For details, see [Research Wiki & Meta-Optimize Skills](#4.7)**

Sources: [docs/SKILLS_CATALOG.md:41-43]()

### 4.8 Assurance & Audit Skills
The multi-layer cross-model audit chain ensuring experiment honesty, claim validity, and rigorous citation checks before final submission [AGENT_GUIDE.md:98-112]().
- **Key Skills:** `/experiment-audit`, `/result-to-claim`, `/paper-claim-audit`, `/citation-audit`, `/kill-argument`, `/proof-checker`, `/integrity-forensics`.
- **For details, see [Assurance & Audit Skills](#4.8)**

Sources: [AGENT_GUIDE.md:98-112]()

### 4.9 Patent Pipeline Skills
Specialized sub-skills for drafting patent-ready specifications, prior art searches, novelty checks, and multi-jurisdiction formatting (CN/US/EP) [docs/SKILLS_CATALOG.md:39]().
- **Key Skills:** `/patent-pipeline`, `/prior-art-search`, `/patent-novelty-check`, `/invention-structuring`, `/claims-drafting`, `/specification-writing`, `/patent-review`, `/jurisdiction-format`, `/embodiment-description`, `/figure-description`.
- **For details, see [Patent Pipeline Skills](#4.9)**

Sources: [docs/SKILLS_CATALOG.md:39]()

---

## Infrastructure Resource Mapping

The following diagram associates system infrastructure components with the code entities responsible for interacting with them.

```mermaid
graph LR
    subgraph "InfrastructureLayer"
        GPU[""RemoteGPUorModal<br/>(SSH/serverless)""]
        OVERLEAF[""OverleafGitBridge<br/>(git.overleaf.com)""]
        WIKI[""ResearchWiki<br/>(research-wiki/*.md)""]
        AUDIT_SH[""AuditScripts<br/>(tools/overleaf_audit.sh)""]
    end

    subgraph "CodeEntitySpace"
        run_exp[""run-experiment<br/>(skills/run-experiment/SKILL.md)""]
        overleaf_skill[""overleaf-sync<br/>(skills/overleaf-sync/SKILL.md)""]
        wiki_skill[""research-wiki<br/>(skills/research-wiki/SKILL.md)""]
        cit_audit[""citation-audit<br/>(skills/citation-audit/SKILL.md)""]
    end

    run_exp -->|"Deploys to"| GPU
    overleaf_skill -->|"Syncs with"| OVERLEAF
    wiki_skill -->|"Manages"| WIKI
    cit_audit -->|"Verified by"| AUDIT_SH
    overleaf_skill -->|"Verified by"| AUDIT_SH
```

Sources: [docs/SKILLS_CATALOG.md:21-41](), [AGENT_GUIDE.md:98-112]()

---

