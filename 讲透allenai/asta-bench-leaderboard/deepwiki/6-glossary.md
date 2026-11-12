<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/asta-bench-leaderboard · page 6 Glossary · fetched 2026-11-09 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [aliases.py](aliases.py)
- [content.py](content.py)
- [leaderboard_transformer.py](leaderboard_transformer.py)
- [ui_components.py](ui_components.py)

</details>



## Purpose and Scope

This glossary defines key domain-specific concepts, architectural classes, and transformation primitives used across the AstaBench leaderboard codebase. It bridges natural language descriptions of scientific AI agent metrics and taxonomies with their precise Python code entities, classes, and helper functions.

Sources: `aliases.py:1-24`, `leaderboard_transformer.py:1-180`, `ui_components.py:1-162`

---

## 1. Taxonomy & Metadata Terms

### Openness
A classification system defining the accessibility of an agent's underlying source code and machine learning model weights. AstaBench categorizes agents into four canonical openness tiers:
1. **Open Source + Open Weights**: Both code and models are fully accessible.
2. **Open Source**: Code is open, but uses closed-weight models.
3. **API Available**: No code access; interaction is restricted to public APIs.
4. **Closed (UI Only)**: No code or API access; interaction restricted to user interfaces.

These tiers are imported from `agenteval.config` and mapped to human-readable labels via `aliases.OPENNESS_ALIASES` in `aliases.py:12-17`, and translated into visual asset paths via `OPENNESS_SVG_MAP` in `ui_components.py:76-93`.

### Tooling (Agent Tooling)
Categorizes the environment interaction limits and tools available to an agent during benchmark execution:
1. **Standard**: Uses only explicit tools provided in `state.tools`.
2. **Custom with Standard Search**: Custom tools built to access an equivalent underlying environment.
3. **Fully Custom**: Uses tools beyond the standard or custom interface constraints.

Defined via canonical constants in `agenteval.config` and mapped in `aliases.TOOL_USAGE_ALIASES` (`aliases.py:19-23`), these are paired with openness in `COMBINED_ICON_MAP` (`ui_components.py:40-61`).

### Split
Refers to the evaluation subset partition (`validation` or `test`) against which agent runs are benchmarked. Splits are encoded directly in raw dataset column names and mapped to formal benchmark names through `INFORMAL_TO_FORMAL_NAME_MAP` (`leaderboard_transformer.py:13-66`).

```mermaid
graph TD
    sub: "NaturalLanguageSpace"
    sub -->|"Open Source + Open Weights"| canon1["CANONICAL_OPENNESS_OPEN_SOURCE_OPEN_WEIGHTS"]
    sub -->|"Custom with Standard Search"| canon2["CANONICAL_TOOL_USAGE_CUSTOM_INTERFACE"]
    sub -->|"Validation Split String"| canon3["sqa_dev / sqa_test"]

    sub: "CodeEntitySpace"
    canon1 ==>|"aliases.py:12-17"| map1["OPENNESS_ALIASES"]
    canon2 ==>|"aliases.py:19-23"| map2["TOOL_USAGE_ALIASES"]
    canon3 ==>|"leaderboard_transformer.py:23-42"| map3["INFORMAL_TO_FORMAL_NAME_MAP"]
```
*Diagram 1: Natural Language Taxonomy to Code Entity Space for Metadata and Splits.*

Sources: `aliases.py:1-24`, `ui_components.py:40-107`, `leaderboard_transformer.py:13-66`

---

## 2. Analytical & Mathematical Terms

### Pareto Frontier (Pareto Optimality)
A set of agents that achieve the best performance (score) for a given cost budget. An agent is Pareto optimal if no other agent achieves a strictly higher score at an equal or lower cost, or an equal score at a strictly lower cost. 

This calculation is implemented in `get_pareto_df` within `leaderboard_transformer.py`, handling missing cost values and preserving full metric precision prior to UI formatting.

### Tag Map
A dictionary structure mapping category and benchmark keys to lists of available metadata tags or filter values. The raw tag map is cleaned and sorted according to custom priority arrays using `create_pretty_tag_map` (`leaderboard_transformer.py:136-165`).

Sources: `leaderboard_transformer.py:1-180`

---

## 3. Core Architectural & Data Classes

### DataTransformer
The data transformation suite and namespace in `leaderboard_transformer.py` responsible for converting raw HuggingFace dataset frames into clean, structured tables. It handles column renaming via `_pretty_column_name` (`leaderboard_transformer.py:90-134`), tag mapping via `create_pretty_tag_map` (`leaderboard_transformer.py:136-165`), and core frame sanitization via `transform_raw_dataframe` (`leaderboard_transformer.py:168-180`).

### LeaderboardViewer
An upstream view rendering and management class imported from `agenteval.leaderboard.view` (`ui_components.py:7`) that coordinates interaction state, filtering, and data view persistence across Gradio components.

```mermaid
graph TD
    sub: "NaturalLanguageSpace"
    sub -->|"Raw Dataset DataFrame"| rawdf["Raw DataFrame"]
    sub -->|"View Management State"| vstate["Viewer State"]

    sub: "CodeEntitySpace"
    rawdf ==>|"leaderboard_transformer.py:168-180"| tdf["transform_raw_dataframe()"]
    tdf ==>|"leaderboard_transformer.py:90-134"| pcol["_pretty_column_name()"]
    vstate ==>|"ui_components.py:7"| lview["LeaderboardViewer"]
```
*Diagram 2: Natural Language Space to Code Entity Space for Data Transformation and Viewing.*

Sources: `ui_components.py:1-35`, `leaderboard_transformer.py:1-180`