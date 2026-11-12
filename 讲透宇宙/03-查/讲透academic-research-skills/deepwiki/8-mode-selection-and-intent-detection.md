<!-- source: DeepWiki mcp.deepwiki.com · repo Imbad0202/academic-research-skills · page 8 Mode Selection and Intent Detection · fetched 2026-10-30 -->

# Mode Selection and Intent Detection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [academic-paper-reviewer/SKILL.md](academic-paper-reviewer/SKILL.md)
- [academic-paper/SKILL.md](academic-paper/SKILL.md)
- [deep-research/SKILL.md](deep-research/SKILL.md)
- [docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)
- [shared/references/routing_core.md](shared/references/routing_core.md)
- [tests/fixtures/issue_133_routing/CALIBRATION_LOG.md](tests/fixtures/issue_133_routing/CALIBRATION_LOG.md)
- [tests/fixtures/issue_133_routing/README.md](tests/fixtures/issue_133_routing/README.md)

</details>



## Purpose and Scope

This page documents the **two-layer routing architecture** that determines how user requests are matched to skills and modes within the Academic Research Skills system. Layer 1 handles skill-level activation using bilingual keyword matching, while Layer 2 handles mode-specific routing using semantic intent detection and the shared routing core [shared/references/routing_core.md:1-3]().

This is a **PARENT page**. For deep technical details, see the child pages:
- [Layer 1: Skill Activation Keywords](#8.1) — Multilingual trigger keywords and `MODE_REGISTRY.md` as the single source of truth [shared/references/routing_core.md:1-11]().
- [Layer 2: Intent-Based Mode Routing](#8.2) — The shared routing core, escape hatch `[direct-mode]`, clarification steps, and `issue_133_routing` calibration fixtures [tests/fixtures/issue_133_routing/README.md:1-25]().

Sources: [shared/references/routing_core.md:1-3](), [tests/fixtures/issue_133_routing/README.md:1-25]()

---

## Two-Layer Routing Architecture

The system uses a **two-layer trigger architecture** that separates framework-level skill activation from semantic mode selection. This design enables the system to work reliably across languages while maintaining high matching confidence [shared/references/routing_core.md:1-3]().

### Architecture Overview

```mermaid
graph TD
    title "Figure 1: Two-Layer Routing Architecture Mapping Natural Language to Code Entities"
    NL_Input["UserInput: 'Write a paper on AI'"] --> L1_Match["Framework Match: academic-paper/SKILL.md"]
    
    subgraph "Layer 1: Skill Activation"
        L1_Match --> SKILL_MD["SKILL.md metadata & description"]
        SKILL_MD --> REGISTRY["MODE_REGISTRY.md single source of truth"]
    end
    
    REGISTRY --> L2_Eval["Routing Core: shared/references/routing_core.md"]
    
    subgraph "Layer 2: Intent Routing"
        L2_Eval --> ESCAPE["Escape Hatch Check: [direct-mode]"]
        ESCAPE --> STEP1["Explicit Intent Step 1"]
        ESCAPE --> STEP2["Cross-Phase Materials Step 2"]
        ESCAPE --> STEP3["Ambiguous Intent Step 3"]
    end
    
    STEP1 --> ROUTE_EXEC["Execute Mode: academic-paper:full"]
    STEP2 --> CLARIFY["Intent Clarification Protocol"]
    STEP3 --> CLARIFY
```

Sources: [academic-paper/SKILL.md:24-45](), [shared/references/routing_core.md:1-32]()

---

## Layer 1: Skill Activation Keywords

Layer 1 determines **which skill** should handle the user's request via framework-level string matching and bilingual trigger keywords [shared/references/routing_core.md:1-10](). 

For full details on multilingual trigger keywords and `MODE_REGISTRY.md`, see [Layer 1: Skill Activation Keywords](#8.1).

Sources: [shared/references/routing_core.md:1-10](), [academic-paper/SKILL.md:1-15]()

---

## Layer 2: Intent-Based Mode Routing

Layer 2 determines **which mode** within an activated skill should handle the request using semantic intent detection, the shared routing core, and safety guardrails like the `[direct-mode]` escape hatch [shared/references/routing_core.md:14-32]().

### Natural Language to Code Routing Flow

```mermaid
graph LR
    title "Figure 2: Natural Language Space to Code Entity Routing Flow"
    
    subgraph "Natural Language Space"
        NL_A["'Can you help me structure my chapter?'"]
        NL_B["'Review this manuscript'"]
        NL_C["'[direct-mode] run bibliography_agent'"]
    end
    
    subgraph "Code Entity Space"
        CE_Core["shared/references/routing_core.md"]
        CE_Escape["Step 0: [direct-mode] Escape Hatch"]
        CE_Explicit["Step 1: Explicit Intent Routing"]
        CE_Clarify["Step 2-3: intent_clarification_protocol.md"]
        CE_Fixtures["tests/fixtures/issue_133_routing/"]
    end
    
    NL_A --> CE_Core
    NL_B --> CE_Core
    NL_C --> CE_Escape
    
    CE_Core --> CE_Escape
    CE_Escape --> CE_Explicit
    CE_Core --> CE_Clarify
    CE_Explicit --> CE_Fixtures
```

For full details on the shared routing core, escape hatch handling, clarification steps, and calibration fixtures, see [Layer 2: Intent-Based Mode Routing](#8.2).

Sources: [shared/references/routing_core.md:13-32](), [tests/fixtures/issue_133_routing/README.md:1-52]()

---

## Related Pages

- **[Layer 1: Skill Activation Keywords](#8.1)** — Detailed bilingual keyword lists and `MODE_REGISTRY.md` mapping.
- **[Layer 2: Intent-Based Mode Routing](#8.2)** — Routing core specification, escape hatch rules, and `issue_133_routing` test suite.
- **[Integration and Handoffs](#9)** — Inter-skill data transfer and handoff schemas.

---

