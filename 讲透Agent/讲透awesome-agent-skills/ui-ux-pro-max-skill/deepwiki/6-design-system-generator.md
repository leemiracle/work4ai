<!-- source: DeepWiki mcp.deepwiki.com · repo nextlevelbuilder/ui-ux-pro-max-skill · page 6 Design System Generator · fetched 2026-10-26 -->

# Design System Generator

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/ui-ux-pro-max/scripts/design_system.py](.claude/skills/ui-ux-pro-max/scripts/design_system.py)
- [cli/assets/scripts/design_system.py](cli/assets/scripts/design_system.py)
- [src/ui-ux-pro-max/scripts/design_system.py](src/ui-ux-pro-max/scripts/design_system.py)

</details>



The Design System Generator is a module that aggregates multi-domain search results and applies reasoning rules to produce comprehensive design system recommendations. It synthesizes data from 5 knowledge domains (product categories, styles, colors, typography, landing patterns) and applies context-aware decision logic to generate project-specific design specifications with optional file persistence.

For information about the underlying search engine, see [Search Engine](#5). For information about the CLI interface, see [search.py CLI Interface](#5.2). For information about the Master + Overrides pattern implementation, see [Master + Overrides Pattern](#6.2).

**Sources:** [src/ui-ux-pro-max/scripts/design_system.py:1-16]()

## Architecture Overview

The Design System Generator operates as a coordinated pipeline between the BM25 search engine ([cli/assets/scripts/core.py:89-150]()), reasoning rules ([ui-reasoning.csv]()), and output formatters. The system accepts natural language queries and produces structured design specifications, including "Design Dials" for variance, motion, and density.

### Component Diagram

```mermaid
graph TB
    subgraph "Entry_Points"
        CLI["search.py CLI<br/>--design-system flag"]
        API["generate_design_system()<br/>function"]
    end
    
    subgraph "Core_Generator"
        DSG["DesignSystemGenerator<br/>class"]
        Generate["generate()<br/>method"]
        Dials["_resolve_dial()"]
    end
    
    subgraph "Search_Layer"
        MultiSearch["_multi_domain_search()"]
        SelectBest["_select_best_match()"]
        CoreSearch["core.search()"]
    end
    
    subgraph "Reasoning_Layer"
        LoadReasoning["_load_reasoning()"]
        FindRule["_find_reasoning_rule()"]
        ApplyReasoning["_apply_reasoning()"]
        ReasoningCSV["ui-reasoning.csv<br/>100 decision rules"]
    end
    
    subgraph "Output_Layer"
        FormatASCII["format_ascii_box()"]
        FormatMD["format_markdown()"]
        FormatMaster["format_master_md()"]
        FormatPage["format_page_override_md()"]
    end
    
    subgraph "Persistence_Layer"
        Persist["persist_design_system()"]
        GenOverrides["_generate_intelligent_overrides()"]
        FileSystem["design-system/project/MASTER.md + pages/*.md"]
    end
    
    CLI --> API
    API --> DSG
    DSG --> Generate
    Generate --> MultiSearch
    Generate --> LoadReasoning
    Generate --> ApplyReasoning
    Generate --> Dials
    
    MultiSearch --> CoreSearch
    MultiSearch --> SelectBest
    
    LoadReasoning --> ReasoningCSV
    ApplyReasoning --> FindRule
    FindRule --> ReasoningCSV
    
    Generate --> FormatASCII
    Generate --> FormatMD
    API --> Persist
    Persist --> FormatMaster
    Persist --> FormatPage
    FormatPage --> GenOverrides
    Persist --> FileSystem
```

**Sources:** [src/ui-ux-pro-max/scripts/design_system.py:37-237](), [cli/assets/scripts/design_system.py:37-237]()

## DesignSystemGenerator Class

The `DesignSystemGenerator` class ([src/ui-ux-pro-max/scripts/design_system.py:160-488]()) orchestrates the entire generation process. It initializes with reasoning rules from `ui-reasoning.csv` and provides methods for multi-domain search, rule matching, and result synthesis. It also handles "Design Dials" ([src/ui-ux-pro-max/scripts/design_system.py:68-87]())—1-10 sliders that bias search results for variance, motion, and density.

### Class Structure

| Method | Purpose | Returns |
|--------|---------|---------|
| `__init__()` | Load reasoning rules from CSV | None |
| `_load_reasoning()` | Parse `ui-reasoning.csv` into list of dicts | `list[dict]` |
| `_multi_domain_search(query, ...)` | Execute parallel searches across 5 domains | `dict` |
| `_find_reasoning_rule(category)` | Match product category to reasoning rule | `dict` |
| `_apply_reasoning(category, search_results)` | Extract style priorities, anti-patterns, effects | `dict` |
| `_select_best_match(results, priority_keywords)` | Score results by keyword match | `dict` |
| `generate(query, project_name, ...)` | Main orchestrator method | `dict` |

**Sources:** [src/ui-ux-pro-max/scripts/design_system.py:160-250]()

### Configuration Constants

```python
# Search configuration defines domains and result limits
SEARCH_CONFIG = {
    "product": {"max_results": 1},
    "style": {"max_results": 3},
    "color": {"max_results": 5},
    "landing": {"max_results": 2},
    "typography": {"max_results": 2}
}

# Semantic Color Mapping for CSS Variables
SEMANTIC_COLOR_ENTRIES = (
    ("Primary", "primary", "--color-primary"),
    ("Secondary", "secondary", "--color-secondary"),
    # ...
)
```

The `SEARCH_CONFIG` dictionary ([src/ui-ux-pro-max/scripts/design_system.py:40-46]()) controls which domains are queried and how many results to retrieve. `SEMANTIC_COLOR_ENTRIES` ([src/ui-ux-pro-max/scripts/design_system.py:48-65]()) maps palette keys to CSS variables for theme generation.

**Sources:** [src/ui-ux-pro-max/scripts/design_system.py:40-65]()

## Generation Pipeline

The generation process follows a 5-step pipeline that transforms a natural language query into a complete design system specification. For a detailed breakdown of the internal logic and keyword scoring, see [Generation Pipeline](#6.1).

### Pipeline Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Generator as DesignSystemGenerator
    participant Search as core.search()
    participant Reasoning as ui-reasoning.csv
    participant Formatter as Output Formatters
    
    User->>Generator: generate("SaaS dashboard", "MyApp")
    
    Note over Generator: Step 1: Product Search
    Generator->>Search: search(query, "product", 1)
    Search-->>Generator: {"results": [{"Product Type": "SaaS Dashboard"}]}
    
    Note over Generator: Step 2: Load Reasoning
    Generator->>Reasoning: _find_reasoning_rule("SaaS Dashboard")
    Reasoning-->>Generator: {"Style_Priority": "Minimalism + Flat", ...}
    
    Note over Generator: Step 3: Multi-Domain Search
    Generator->>Search: search(query + "Minimalism", "style", 3)
    Generator->>Search: search(query, "color", 5)
    Search-->>Generator: Results from all domains
    
    Note over Generator: Step 4: Select Best Matches
    Generator->>Generator: _select_best_match(style_results, style_priority)
    
    Note over Generator: Step 5: Synthesize
    Generator->>Generator: Build final design_system dict
    Generator-->>User: design_system dict
    
    User->>Formatter: format_ascii_box(design_system)
    Formatter-->>User: ASCII box output
```

**Sources:** [src/ui-ux-pro-max/scripts/design_system.py:382-488]()

## Master + Overrides Pattern

The system uses a hierarchical file structure to manage design guidelines. This allows for a global "Source of Truth" while permitting specific pages to deviate when necessary.

*   **MASTER.md**: Contains global rules for colors, typography, spacing, and standard components ([src/ui-ux-pro-max/scripts/design_system.py:794-1065]()).
*   **pages/*.md**: Contains overrides for specific page types (e.g., "Dashboard", "Settings") generated via intelligent context detection ([src/ui-ux-pro-max/scripts/design_system.py:1068-1177]()).

For details on the Markdown structure and override logic, see [Master + Overrides Pattern](#6.2).

**Sources:** [src/ui-ux-pro-max/scripts/design_system.py:743-791]()

## Persistence and File Structure

The `persist_design_system` function ([src/ui-ux-pro-max/scripts/design_system.py:743-791]()) handles the physical creation of the design system directory. It generates a project slug, creates the necessary folder hierarchy, and writes the Markdown files.

### Intelligent Override Generation
Instead of using static templates, the system uses `_generate_intelligent_overrides` ([src/ui-ux-pro-max/scripts/design_system.py:1180-1286]()) to perform targeted searches for the specific page being created. It detects the page type (e.g., "Authentication", "Dashboard") and infers layout rules based on search keywords.

For details on directory paths and the slug generation process, see [Persistence and File Structure](#6.3).

**Sources:** [src/ui-ux-pro-max/scripts/design_system.py:1180-1321]()

---

