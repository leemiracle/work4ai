<!-- source: DeepWiki mcp.deepwiki.com · repo Eronred/aso-skills · page 3 ASO Core Skills · fetched 2026-10-26 -->

# ASO Core Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [reference/skills-overview.mdx](reference/skills-overview.mdx)
- [skills/aso-audit.mdx](skills/aso-audit.mdx)

</details>



The ASO Core Skills group represents the foundational organic-growth engine within the `aso-skills` repository. This collection of specialist AI agent skills automates App Store Optimization (ASO) workflows—ranging from full-listing diagnostics and deep keyword extraction to competitor gap analyses and platform-specific optimizations for Apple App Store and Google Play [reference/skills-overview.mdx:43-66](). 

As a parent page, this document provides a high-level architectural overview of the core organic-growth skills. For deep implementation details, rubrics, and output schemas, refer to the respective child pages below.

```mermaid
graph TD
    UserQuery[""Natural Language Query: /aso-audit or /keyword-research""] --> Router[""Router Dispatcher: /aso-router""]
    Router --> CoreGroup[""Core Skill Group: reference/skills-overview.mdx""]
    CoreGroup --> AuditSkill[""Auditing & Scoring: skills/aso-audit.mdx""]
    CoreGroup --> KeywordSkill[""Keyword & Metadata: reference/skills-overview.mdx""]

    Sources: [reference/skills-overview.mdx:43-66](), [skills/aso-audit.mdx:1-35]()
```

## 3.1 aso-audit: Scoring Framework

The `aso-audit` skill evaluates an application's store presence across ten weighted factors, producing a unified 0–100 score card, actionable quick wins, and structured remediation tiers [skills/aso-audit.mdx:7-44](). The framework weighs factors based on their direct impact on search visibility and conversion rates, allocating high priority to the title (20%), keyword field (15%), screenshots (15%), ratings & reviews (15%), and subtitle (15%) [skills/aso-audit.mdx:41-92]().

Before execution, the skill inspects the shared workspace environment for any existing `app-marketing-context.md` configuration to inherit app positioning details automatically [skills/aso-audit.mdx:15-17](). For detailed factor breakdowns, scoring rubrics, and the complete multi-tier remediation roadmap, see [aso-audit: Scoring Framework](#3.1).

Sources: [skills/aso-audit.mdx:1-124]()

## 3.2 keyword-research & metadata-optimization

The keyword research and metadata optimization sub-group handles quantitative keyword discovery and qualitative text generation. The `keyword-research` skill scores target terms using a volume × difficulty × relevance formula, grouping outcomes into primary, secondary, and long-tail tiers with distinct Opportunity Scores [reference/skills-overview.mdx:51-53](). 

The `metadata-optimization` skill consumes these keywords to generate three distinct text variants for titles, subtitles, keyword fields, and descriptions, complete with character counts and keyword coverage matrices [reference/skills-overview.mdx:54-56](). For information on volume indexing parameters and variant generation rules, see [keyword-research & metadata-optimization](#3.2).

```mermaid
graph TD
    InputContext[""app-marketing-context.md""] --> KW[""Keyword Discovery: keyword-research""]
    KW --> Score[""Opportunity Scoring Matrix""]
    Score --> Meta[""Metadata Generation: metadata-optimization""]
    Meta --> Variants[""3x Title/Subtitle/Field Variants""]

    Sources: [reference/skills-overview.mdx:51-56]()
```

Sources: [reference/skills-overview.mdx:51-56]()

## 3.3 Competitor Analysis & Positioning

The competitor analysis module identifies market blind spots by performing automated keyword gap analysis, creative asset teardowns, and visual positioning maps [reference/skills-overview.mdx:57-59](). By comparing an app's indexed keyword footprint against direct competitors, the skill surfaces exploitable ranking opportunities and differentiators in feature sets or pricing structures. 

For full methodologies on benchmarking competitors and constructing multi-dimensional position maps, see [Competitor Analysis & Positioning](#3.3).

Sources: [reference/skills-overview.mdx:57-59]()

## 3.4 Platform & Seasonal Variants

App Store Optimization differs fundamentally between ecosystems and temporal windows. The platform and seasonal group covers Google Play-specific ranking signals (`android-aso`), indexable long descriptions, Play Store Experiments, and localized keyword strategies [reference/skills-overview.mdx:60-65](). 

Additionally, `seasonal-aso` manages calendar-driven metadata swaps and cultural event optimization [reference/skills-overview.mdx:60-62](). For details on cross-platform algorithm variances and seasonal keyword calendars, see [Platform & Seasonal Variants](#3.4).

Sources: [reference/skills-overview.mdx:60-66]()

---

