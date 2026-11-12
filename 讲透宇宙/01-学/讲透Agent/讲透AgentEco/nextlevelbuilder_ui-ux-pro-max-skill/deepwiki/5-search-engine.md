<!-- source: DeepWiki mcp.deepwiki.com · repo nextlevelbuilder/ui-ux-pro-max-skill · page 5 Search Engine · fetched 2026-10-27 -->

# Search Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/ui-ux-pro-max/SKILL.md](.claude/skills/ui-ux-pro-max/SKILL.md)
- [.claude/skills/ui-ux-pro-max/scripts/core.py](.claude/skills/ui-ux-pro-max/scripts/core.py)
- [.claude/skills/ui-ux-pro-max/scripts/search.py](.claude/skills/ui-ux-pro-max/scripts/search.py)
- [cli/assets/scripts/core.py](cli/assets/scripts/core.py)
- [cli/assets/scripts/search.py](cli/assets/scripts/search.py)
- [src/ui-ux-pro-max/scripts/core.py](src/ui-ux-pro-max/scripts/core.py)
- [src/ui-ux-pro-max/scripts/search.py](src/ui-ux-pro-max/scripts/search.py)

</details>



The Search Engine is the core BM25-based retrieval system that powers all domain and stack queries in UI/UX Pro Max. It provides probabilistic ranking of design resources from CSV databases, automatic domain detection, and a unified interface for searching across 12 design domains and 22 technology stacks.

For details on the BM25 algorithm parameters and scoring implementation, see [BM25 Algorithm Implementation](#5.1). For command-line usage and flags, see [search.py CLI Interface](#5.2). For domain routing logic, see [Domain Detection and Configuration](#5.3).

## Architecture Overview

The search engine consists of three main components: the `BM25` class for probabilistic ranking, configuration dictionaries that map domains to CSV files, and search functions that orchestrate the retrieval pipeline.

**Core Components and Their Relationships**

```mermaid
graph TB
    subgraph "core.py Module"
        BM25Class["BM25 class"]
        CSVConfig["CSV_CONFIG dict"]
        StackConfig["STACK_CONFIG dict"]
        DetectDomain["detect_domain()"]
        SearchFunc["search()"]
        SearchStack["search_stack()"]
        LoadCSV["_load_csv()"]
        SearchCSV["_search_csv()"]
    end
    
    subgraph "Configuration"
        DataDir["DATA_DIR = Path(__file__).parent.parent / 'data'"]
        MaxResults["MAX_RESULTS = 3"]
    end
    
    subgraph "Data Layer"
        StylesCSV["data/styles.csv"]
        ColorsCSV["data/colors.csv"]
        ProductsCSV["data/products.csv"]
        StackCSV["data/stacks/*.csv"]
    end
    
    SearchFunc --> DetectDomain
    SearchFunc --> CSVConfig
    SearchFunc --> SearchCSV
    SearchStack --> StackConfig
    SearchStack --> SearchCSV
    SearchCSV --> LoadCSV
    SearchCSV --> BM25Class
    
    CSVConfig --> StylesCSV
    CSVConfig --> ColorsCSV
    CSVConfig --> ProductsCSV
    StackConfig --> StackCSV
    
    DataDir --> LoadCSV
    MaxResults --> SearchFunc
    MaxResults --> SearchStack
```

Sources: [src/ui-ux-pro-max/scripts/core.py:1-254]()

## Configuration Dictionaries

The search engine uses two dictionaries to map logical domains to physical CSV files and define which columns to search and return.

### CSV_CONFIG Structure

The `CSV_CONFIG` dictionary defines 12 domain mappings (updated in v2.5.0) with `search_cols` (fields to index) and `output_cols` (fields to return):

| Domain | File | Search Columns | Output Columns | Use Case |
|--------|------|----------------|----------------|----------|
| `style` | `styles.csv` | Style Category, Keywords, Best For, Type, AI Prompt Keywords | 21 columns including Primary Colors, Effects, Framework Compatibility, Implementation Checklist | UI style recommendations |
| `color` | `colors.csv` | Product Type, Notes | Primary/Secondary/Accent/Background/Card/Muted/Border hex codes | Color palette selection |
| `chart` | `charts.csv` | Data Type, Keywords, Best Chart Type, Accessibility Notes | Chart type, library recommendation, interactivity, A11y fallback | Data visualization guidance |
| `landing` | `landing.csv` | Pattern Name, Keywords, Conversion Optimization, Section Order | Section order, CTA placement, color strategy | Landing page structure |
| `product` | `products.csv` | Product Type, Keywords, Primary Style Recommendation, Key Considerations | Style recommendations, color palette focus | Product-based style routing |
| `ux` | `ux-guidelines.csv` | Category, Issue, Description, Platform | Do/Don't, Code Examples, Severity | UX best practices |
| `typography` | `typography.csv` | Font Pairing Name, Category, Mood/Style Keywords, Best For, Heading/Body Font | Google Fonts URL, CSS Import, Tailwind Config | Font pairing selection |
| `icons` | `icons.csv` | Category, Icon Name, Keywords, Best For | Library, Import Code, Usage, Style | Icon recommendations |
| `gsap` | `motion.csv` | Category, Intensity Tier, Keywords, Trigger | Duration, Easing, GSAP Snippet, Do/Don't | Animation presets |
| `react` | `react-performance.csv` | Category, Issue, Keywords, Description | Do/Don't, Code Examples, Severity | React-specific performance |
| `web` | `app-interface.csv` | Category, Issue, Keywords, Description | Do/Don't, Code Examples, Severity | Web interface guidelines |
| `google-fonts` | `google-fonts.csv` | Family, Category, Stroke, Classifications, Keywords | Styles, Variable Axes, Popularity Rank | Direct font metadata search |

Sources: [src/ui-ux-pro-max/scripts/core.py:18-79]()

### STACK_CONFIG Structure

The `STACK_CONFIG` dictionary maps 22 technology stacks to their CSV files. All stacks share common column definitions stored in `_STACK_COLS`:

```python
STACK_CONFIG = {
    "react":            {"file": "stacks/react.csv"},
    "nextjs":           {"file": "stacks/nextjs.csv"},
    "vue":              {"file": "stacks/vue.csv"},
    "svelte":           {"file": "stacks/svelte.csv"},
    "astro":            {"file": "stacks/astro.csv"},
    "swiftui":          {"file": "stacks/swiftui.csv"},
    "react-native":     {"file": "stacks/react-native.csv"},
    "flutter":          {"file": "stacks/flutter.csv"},
    "nuxtjs":           {"file": "stacks/nuxtjs.csv"},
    "nuxt-ui":          {"file": "stacks/nuxt-ui.csv"},
    "html-tailwind":    {"file": "stacks/html-tailwind.csv"},
    "shadcn":           {"file": "stacks/shadcn.csv"},
    "jetpack-compose":  {"file": "stacks/jetpack-compose.csv"},
    "threejs":          {"file": "stacks/threejs.csv"},
    "angular":          {"file": "stacks/angular.csv"},
    "laravel":          {"file": "stacks/laravel.csv"},
    "javafx":           {"file": "stacks/javafx.csv"},
    "wpf":              {"file": "stacks/wpf.csv"},
    "winui":            {"file": "stacks/winui.csv"},
    "avalonia":         {"file": "stacks/avalonia.csv"},
    "uno":              {"file": "stacks/uno.csv"},
    "uwp":              {"file": "stacks/uwp.csv"},
}

_STACK_COLS = {
    "search_cols": ["Category", "Guideline", "Description", "Do", "Don't", "Code Good", "Code Bad"],
    "output_cols": ["Category", "Guideline", "Description", "Do", "Don't", "Code Good", "Code Bad", "Severity", "Docs URL", "Applies To", "Status", "Verified At"]
}
```

Sources: [src/ui-ux-pro-max/scripts/core.py:89-121]()

## BM25 Implementation

The `BM25` class implements the BM25 (Best Match 25) probabilistic ranking algorithm with configurable parameters `k1=1.5` (term frequency saturation) and `b=0.75` (document length normalization).

### Class Structure

| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `__init__(k1, b)` | Initialize with tuning parameters | `k1=1.5`, `b=0.75` | None |
| `tokenize(text)` | Lowercase, split, filter stopwords | `text: str` | `List[str]` |
| `fit(documents)` | Build IDF index from corpus | `documents: List[str]` | None |
| `score(query)` | Rank all documents against query | `query: str` | `List[Tuple[int, float]]` |

**Tokenization Logic** ([src/ui-ux-pro-max/scripts/core.py:145-148]()):
- Remove non-alphanumeric characters: `re.sub(r'[^\w\s]', ' ', str(text).lower())`
- Filter tokens shorter than 3 characters
- Return lowercase tokens

**IDF Calculation** ([src/ui-ux-pro-max/scripts/core.py:166-167]()):
```python
self.idf[word] = log((self.N - freq + 0.5) / (freq + 0.5) + 1)
```
Where `N` is corpus size and `freq` is document frequency of term.

**BM25 Scoring Formula** ([src/ui-ux-pro-max/scripts/core.py:185-187]()):
```python
numerator = tf * (self.k1 + 1)
denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
score += idf * numerator / denominator
```

Sources: [src/ui-ux-pro-max/scripts/core.py:132-192]()

## Search Functions

The module exposes primary search functions that orchestrate the retrieval pipeline.

### search() Function Flow

```mermaid
sequenceDiagram
    participant Caller
    participant search
    participant detect_domain
    participant CSV_CONFIG
    participant _search_csv
    participant BM25
    participant CSV_File
    
    Caller->>search: search(query, domain=None, max_results=3)
    
    alt domain is None
        search->>detect_domain: detect_domain(query)
        detect_domain-->>search: detected_domain
    end
    
    search->>CSV_CONFIG: CSV_CONFIG.get(domain)
    CSV_CONFIG-->>search: config dict with file, search_cols, output_cols
    
    search->>_search_csv: _search_csv(filepath, search_cols, output_cols, query, max_results)
    
    _search_csv->>CSV_File: _load_csv(filepath)
    CSV_File-->>_search_csv: List[Dict] rows
    
    _search_csv->>_search_csv: Build documents from search_cols
    
    _search_csv->>BM25: bm25 = BM25()
    _search_csv->>BM25: bm25.fit(documents)
    _search_csv->>BM25: bm25.score(query)
    BM25-->>_search_csv: ranked indices with scores
    
    _search_csv->>_search_csv: Filter score > 0, limit to max_results
    _search_csv-->>search: List[Dict] results with output_cols
    
    search-->>Caller: {"domain": str, "query": str, "file": str, "count": int, "results": List[Dict]}
```

Sources: [src/ui-ux-pro-max/scripts/core.py:249-268]()

### search_stack() Function

The `search_stack()` function provides specialized search for technology stack guidelines:

```python
def search_stack(query, stack, max_results=MAX_RESULTS):
    """Search stack-specific guidelines"""
    if stack not in STACK_CONFIG:
        return {"error": f"Unknown stack: {stack}. Available: {', '.join(AVAILABLE_STACKS)}"}
    
    filepath = DATA_DIR / STACK_CONFIG[stack]["file"]
    results = _search_csv(filepath, _STACK_COLS["search_cols"], _STACK_COLS["output_cols"], query, max_results)
    
    return {
        "domain": "stack",
        "stack": stack,
        "query": query,
        "file": STACK_CONFIG[stack]["file"],
        "count": len(results),
        "results": results
    }
```

Sources: [src/ui-ux-pro-max/scripts/core.py:271-290]()

## Domain Detection System

The `detect_domain()` function uses keyword scoring to automatically route queries to the most appropriate domain.

**Keyword Mapping Examples** ([src/ui-ux-pro-max/scripts/core.py:231-242]()):

| Domain | Trigger Keywords |
|--------|------------------|
| `color` | color, palette, hex, #, rgb |
| `chart` | chart, graph, visualization, trend, bar, pie, heatmap |
| `landing` | landing, page, cta, conversion, hero, testimonial |
| `product` | saas, ecommerce, fintech, healthcare, gaming, crypto |
| `style` | style, design, ui, minimalism, glassmorphism, neumorphism |
| `ux` | ux, usability, accessibility, wcag, touch, scroll |
| `typography` | font, typography, heading, serif, sans |
| `icons` | icon, icons, lucide, heroicons, symbol |
| `react` | react, next.js, suspense, memo, usecallback, rsc |
| `web` | aria, focus, outline, semantic, virtualize, form |

**Scoring Algorithm** ([src/ui-ux-pro-max/scripts/core.py:244-246]()):
```python
scores = {domain: sum(1 for kw in keywords if kw in query_lower) 
          for domain, keywords in domain_keywords.items()}
best = max(scores, key=scores.get)
return best if scores[best] > 0 else "style"  # Default to style
```

Sources: [src/ui-ux-pro-max/scripts/core.py:227-247]()

## Integration with CLI

The `search.py` CLI script imports and orchestrates the core search functions.

**Module Imports and Function Delegation**

```mermaid
graph LR
    subgraph "search.py CLI"
        ArgParse["argparse.ArgumentParser"]
        FormatOutput["format_output()"]
        MainBlock["if __name__ == '__main__'"]
    end
    
    subgraph "core.py Imports"
        ImportConfig["from core import CSV_CONFIG"]
        ImportStacks["from core import AVAILABLE_STACKS"]
        ImportMaxRes["from core import MAX_RESULTS"]
        ImportSearch["from core import search"]
        ImportSearchStack["from core import search_stack"]
    end
    
    subgraph "design_system.py Imports"
        ImportGenDS["from design_system import generate_design_system"]
    end
    
    MainBlock --> ArgParse
    ArgParse --> |"args.domain"| ImportSearch
    ArgParse --> |"args.stack"| ImportSearchStack
    ArgParse --> |"args.design_system"| ImportGenDS
    
    ImportSearch --> FormatOutput
    ImportSearchStack --> FormatOutput
    
    ImportConfig --> ArgParse
    ImportStacks --> ArgParse
    ImportMaxRes --> ArgParse
```

**Command-Line Arguments** ([src/ui-ux-pro-max/scripts/search.py:97-117]()):

| Argument | Type | Purpose | Example |
|----------|------|---------|---------|
| `query` | str | Search query (positional) | `"glassmorphism dark mode"` |
| `--domain`, `-d` | choice | Force specific domain | `--domain style` |
| `--stack`, `-s` | choice | Search stack guidelines | `--stack react` |
| `--max-results`, `-n` | int | Limit results (default: 3) | `-n 5` |
| `--json` | flag | Output JSON format | `--json` |
| `--design-system`, `-ds` | flag | Generate full design system | `--design-system` |
| `--persist` | flag | Save to filesystem (Master/Overrides) | `--persist` |
| `--page` | str | Create page override | `--page "dashboard"` |

Sources: [src/ui-ux-pro-max/scripts/search.py:1-119]()

## Usage Examples

### Domain Search
```bash
# Auto-detect domain
python3 search.py "glassmorphism dark mode"

# Force specific domain
python3 search.py "elegant serif" --domain typography

# JSON output
python3 search.py "saas dashboard" --domain product --json
```

### Stack Search
```bash
# Search React guidelines
python3 search.py "memo usecallback" --stack react

# Search Shadcn patterns
python3 search.py "dialog accessibility" --stack shadcn

# Search Flutter widgets
python3 search.py "stateless vs stateful" --stack flutter
```

Sources: [src/ui-ux-pro-max/scripts/search.py:5-15]()

---

