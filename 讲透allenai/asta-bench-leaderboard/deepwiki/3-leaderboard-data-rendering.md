<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/asta-bench-leaderboard · page 3 Leaderboard Data & Rendering · fetched 2026-11-09 -->

# Leaderboard Data & Rendering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [leaderboard_transformer.py](leaderboard_transformer.py)
- [ui_components.py](ui_components.py)

</details>



## Purpose & Scope
This section covers the end-to-end data pipeline responsible for fetching raw evaluation results from HuggingFace datasets, transforming column names and metadata, executing Pareto frontier calculations, and rendering interactive Gradio tables, detail cards, and Plotly visualizations. 

As a parent page, this section provides a high-level overview of the data architecture. For granular implementation details, refer to the child pages:
- [Data Transformation Pipeline](#3.1)
- [UI Components & Plots](#3.2)
- [Icons, SVG Assets & Legends](#3.3)

```mermaid
Title: Data Pipeline Transformation Flow
graph TD
    RawData["HuggingFace Results Dataset"] -->|Input| TransformFunc["transform_raw_dataframe() in leaderboard_transformer.py"]
    TransformFunc -->|Pretty Names & Full Precision| TransformerClass["DataTransformer in leaderboard_transformer.py"]
    TransformerClass -->|Pareto Calculation| ParetoFunc["get_pareto_df() in leaderboard_transformer.py"]
    TransformerClass -->|UI Rendering| ViewerClass["LeaderboardViewer in agenteval/leaderboard/view.py"]
    ViewerClass -->|Table & Plots| GradioUI["Gradio UI Components in ui_components.py"]
```
Sources: `[leaderboard_transformer.py:168-180]`, `[ui_components.py:7-21]`

---

## 3.1 Data Transformation Pipeline
The data transformation pipeline ingests raw pandas DataFrames and normalizes column headers, handles missing values, and builds tag maps for filtering. The core transformation logic resides in `transform_raw_dataframe`, which maps internal database column names to user-facing formal names using `INFORMAL_TO_FORMAL_NAME_MAP` and `_pretty_column_name` `[leaderboard_transformer.py:13-134, 168-180]()`. 

Numerical precision for metrics like scores and costs is strictly preserved during renaming to ensure downstream calculations remain accurate `[leaderboard_transformer.py:169-175]()`. Tag maps are generated dynamically via `create_pretty_tag_map`, sorting filter keys and values according to custom ordering defined in `ORDER_MAP` `[leaderboard_transformer.py:67-87, 136-165]()`.

### 3.1.1 Pareto Frontier & Cost/Score Metrics
Efficiency frontiers are calculated to highlight Pareto-optimal agents across cost and performance axes. The `get_pareto_df` function isolates non-dominated entries, handling edge cases such as missing cost figures while maintaining full data type precision.

For deep technical details on dataframe transformations, sorting rules, and cost formatting helpers, see [Data Transformation Pipeline](#3.1).

Sources: `[leaderboard_transformer.py:13-180]()`

---

## 3.2 UI Components & Plots
The UI rendering layer (`ui_components.py`) bridges transformed dataframes with Gradio interactive components. It implements viewer caching mechanisms to optimize performance across user sessions, structures leaderboard table columns with embedded HTML icons, constructs benchmark detail cards, and manages sub-navigation layouts `[ui_components.py:1-161]()`.

Additionally, interactive visualization relies on Plotly wrappers such as `_plot_scatter_plotly` to render cost-vs-performance scatter plots complete with disclaimers and tooltips `[ui_components.py:16-21, 34]()`.

For deep technical details on layout composition, caching policies, and scatter plot configurations, see [UI Components & Plots](#3.2).

Sources: `[ui_components.py:1-161]()`

---

## 3.3 Icons, SVG Assets & Legends
To provide visual indicators for agent openness and tool usage categories, the application maps raw taxonomy values to vector assets. The `COMBINED_ICON_MAP` structure merges openness categories (`aliases.py`) with tool usage types, resolving aliases and associating them with specific SVG files under `assets/` `[ui_components.py:40-74]()`.

Performance is optimized at startup by pre-loading and base64-encoding these SVG assets via `get_svg_as_data_uri` into `PRELOADED_URI_MAP` `[ui_components.py:109-126]`. The resulting data URIs are embedded directly into Gradio dataframes using `get_combined_icon_html` and `create_svg_html` `[ui_components.py:128-161]()`.

```mermaid
Title: Asset Rendering and Icon Mapping Architecture
graph TD
    Aliases["alias definitions in aliases.py"] -->|Lookup| CombinedMap["COMBINED_ICON_MAP in ui_components.py"]
    CombinedMap -->|Base64 Conversion| DataURI["get_svg_as_data_uri() in ui_components.py"]
    DataURI -->|Caching| PreloadedMap["PRELOADED_URI_MAP in ui_components.py"]
    PreloadedMap -->|HTML Generation| IconHTML["get_combined_icon_html() in ui_components.py"]
    IconHTML -->|Render| GradioTable["gr.DataFrame in ui_components.py"]
```
Sources: `[ui_components.py:40-141]`

For deep technical details on SVG mappings, legend tooltip structures, and category icon definitions, see [Icons, SVG Assets & Legends](#3.3).

Sources: `[ui_components.py:40-161]()`

---

