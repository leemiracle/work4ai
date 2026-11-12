<!-- source: DeepWiki mcp.deepwiki.com · repo muratcankoylan/Agent-Skills-for-Context-Engineering · extra page Prompt Lab UI & Build Pipeline · fetched 2026-10-26 -->

# Prompt Lab UI & Build Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/long-horizon-prompt-lab/data/prompt-pairs.json](examples/long-horizon-prompt-lab/data/prompt-pairs.json)
- [examples/long-horizon-prompt-lab/screenshots/shot-approx-proof-full.png](examples/long-horizon-prompt-lab/screenshots/shot-approx-proof-full.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-approx-proof-scorecard.png](examples/long-horizon-prompt-lab/screenshots/shot-approx-proof-scorecard.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-approx-proof-split.png](examples/long-horizon-prompt-lab/screenshots/shot-approx-proof-split.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-hero.png](examples/long-horizon-prompt-lab/screenshots/shot-hero.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-ml-optimization-full.png](examples/long-horizon-prompt-lab/screenshots/shot-ml-optimization-full.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-ml-optimization-scorecard.png](examples/long-horizon-prompt-lab/screenshots/shot-ml-optimization-scorecard.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-ml-optimization-split.png](examples/long-horizon-prompt-lab/screenshots/shot-ml-optimization-split.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-security-audit-full.png](examples/long-horizon-prompt-lab/screenshots/shot-security-audit-full.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-security-audit-scorecard.png](examples/long-horizon-prompt-lab/screenshots/shot-security-audit-scorecard.png)
- [examples/long-horizon-prompt-lab/screenshots/shot-security-audit-split.png](examples/long-horizon-prompt-lab/screenshots/shot-security-audit-split.png)
- [examples/long-horizon-prompt-lab/scripts/build_lab.py](examples/long-horizon-prompt-lab/scripts/build_lab.py)
- [examples/long-horizon-prompt-lab/scripts/capture.mjs](examples/long-horizon-prompt-lab/scripts/capture.mjs)
- [examples/long-horizon-prompt-lab/ui/app.js](examples/long-horizon-prompt-lab/ui/app.js)
- [examples/long-horizon-prompt-lab/ui/data.js](examples/long-horizon-prompt-lab/ui/data.js)
- [examples/long-horizon-prompt-lab/ui/guide.html](examples/long-horizon-prompt-lab/ui/guide.html)
- [examples/long-horizon-prompt-lab/ui/index.html](examples/long-horizon-prompt-lab/ui/index.html)
- [examples/long-horizon-prompt-lab/ui/lab.html](examples/long-horizon-prompt-lab/ui/lab.html)
- [examples/long-horizon-prompt-lab/ui/references.html](examples/long-horizon-prompt-lab/ui/references.html)
- [examples/long-horizon-prompt-lab/ui/robots.txt](examples/long-horizon-prompt-lab/ui/robots.txt)
- [examples/long-horizon-prompt-lab/ui/sitemap.xml](examples/long-horizon-prompt-lab/ui/sitemap.xml)
- [examples/long-horizon-prompt-lab/ui/styles.css](examples/long-horizon-prompt-lab/ui/styles.css)

</details>



The purpose of this page is to document the technical implementation of the Long-Horizon Prompt Lab static user interface, build scripts, data contracts, rendering engine, 10-dimension rubric scoring mechanics, and automated screenshot capture pipelines. The Prompt Lab demonstrates how abstract prompt engineering techniques map into concrete, highly structured operational files without requiring a complex web application server or runtime build dependencies.

---

## 1. Static UI Architecture & Pages

The Prompt Lab interface is built as a zero-dependency, static multi-page application residing in `examples/long-horizon-prompt-lab/ui/`. It consists of four primary HTML entry points alongside styling and metadata sheets:

* `index.html`: The overview page defining the high-level taxonomy of long-horizon prompts, failure modes of long runs, and brief anatomy [examples/long-horizon-prompt-lab/ui/index.html:1-126].
* `guide.html`: The practical user guide detailing when to activate the skill, how to construct success predicates, persistence-verification pairing, and parallel search diversity [examples/long-horizon-prompt-lab/ui/guide.html:1-120].
* `lab.html`: The interactive before-and-after comparison workspace housing the prompt use-case tabs, split text viewer, structural audit scorecard, and residual risk disclosures [examples/long-horizon-prompt-lab/ui/lab.html:1-118].
* `references.html`: The evidence base and source notes incorporating case studies, preprints, vendor documentation, and repository provenance files [examples/long-horizon-prompt-lab/ui/references.html:1-103].
* `styles.css`: The complete design system enforcing a paper-and-ink visual theme (`--paper: #f5f3ee`, `--ink: #191918`, `--accent: #a34522`) using variable fonts and CSS grid layouts [examples/long-horizon-prompt-lab/ui/styles.css:1-15].

```mermaid
graph TD
    A["index.html"] -->|"Navigation"| B["guide.html"]
    A -->|"Navigation"| C["lab.html"]
    A -->|"Navigation"| D["references.html"]
    C -->|"Loads data"| E["data.js"]
    C -->|"Hydrates DOM"| F["app.js"]
    C -->|"Applies styles"| G["styles.css"]

    subgraph CodeSpace ["Code Entity Space"]
        E["examples/long-horizon-prompt-lab/ui/data.js"]
        F["examples/long-horizon-prompt-lab/ui/app.js"]
        G["examples/long-horizon-prompt-lab/ui/styles.css"]
    end

    Sources: examples/long-horizon-prompt-lab/ui/index.html:1-34, examples/long-horizon-prompt-lab/ui/lab.html:1-34, examples/long-horizon-prompt-lab/ui/styles.css:1-15
```

Sources: `examples/long-horizon-prompt-lab/ui/index.html:1-34`, `examples/long-horizon-prompt-lab/ui/lab.html:1-34`, `examples/long-horizon-prompt-lab/ui/styles.css:1-15`

---

## 2. The Build Pipeline & Data Generation

The single source of truth for all prompt lab data and evaluation scores is `build_lab.py`. This script aggregates prompt pairs, evaluates them against the 10-dimension pre-launch rubric, and outputs serialized artifacts.

### Build Script Execution Flow

```mermaid
graph TD
    subgraph NaturalLanguageSpace ["Natural Language Space"]
        T1["Task Brief Template rubric/skills"]
        T2["Before/After prompt text files"]
    end

    subgraph CodeEntitySpace ["Code Entity Space"]
        BS["python3 build_lab.py"] --> RS["score_block()"]
        RS --> JP["prompt-pairs.json"]
        RS --> DJ["ui/data.js"]
    end

    T1 --> BS
    T2 --> BS

    Sources: examples/long-horizon-prompt-lab/scripts/build_lab.py:1-65
```

The script defines the verbatim rubric dimensions and calculates quantitative scores (`score_block()`) mapping string scores (`"na"`, `0`, `1`, `2`) into aggregated percentage improvements (`gain_pp`) [examples/long-horizon-prompt-lab/scripts/build_lab.py:31-64]. It writes two identical synchronization targets:
1. `data/prompt-pairs.json` for machine consumers and CI analysis [examples/long-horizon-prompt-lab/data/prompt-pairs.json:1-15].
2. `ui/data.js` assigning the payload directly to `window.PROMPT_LAB_DATA` so the static site works locally via `file://` protocols without requiring an HTTP server [examples/long-horizon-prompt-lab/scripts/build_lab.py:1-9].

Sources: `examples/long-horizon-prompt-lab/scripts/build_lab.py:1-65`, `examples/long-horizon-prompt-lab/data/prompt-pairs.json:1-15`

---

## 3. The Client-Side Rendering Engine (`app.js`, `site.js`)

The dynamic parts of `lab.html` are powered by `app.js`, which reads `window.PROMPT_LAB_DATA` and hydrates the Document Object Model [examples/long-horizon-prompt-lab/ui/app.js:1-10]. 

### Key Rendering Functions

* `renderPair(pair)`: Constructs the DOM structure for a selected use case, setting up `role="tabpanel"` relationships and appending header metadata, split prompt panels, structural audit scorecards, and material change summaries [examples/long-horizon-prompt-lab/ui/app.js:72-123].
* `normalizePromptDisplay(text)`: Collapses soft-wrapped editor newlines mid-paragraph while preserving list items (`[-*]|\d+\.`), uppercase headers, and code formulas [examples/long-horizon-prompt-lab/ui/app.js:125-161].
* `promptPanel(kind, pair)`: Renders either the `"before"` or `"after"` prompt view, appending word counts, score blocks, copy buttons backed by `window.copySiteText()`, and `.txt` file download links [examples/long-horizon-prompt-lab/ui/app.js:163-186].
* Tab keyboard navigation handlers supporting `ArrowRight`, `ArrowLeft`, `Home`, and `End` keys [examples/long-horizon-prompt-lab/ui/app.js:53-66].

```mermaid
graph TD
    A["window.PROMPT_LAB_DATA"] --> B["app.js initialization"]
    B --> C["renderTabs()"]
    B --> D["renderHeroStats()"]
    C --> E["select(pair.id)"]
    E --> F["renderPair()"]
    F --> G["normalizePromptDisplay()"]
    F --> H["scorecard()"]

    Sources: examples/long-horizon-prompt-lab/ui/app.js:1-123
```

Sources: `examples/long-horizon-prompt-lab/ui/app.js:1-186`

---

##  4. The 10-Dimension Rubric & Scoring Mechanics

The structural audit engine scores prompts across ten rigorous dimensions derived from the long-horizon prompting skill's specification template (`skills/long-horizon-prompting/references/task-brief-template.md`) [examples/long-horizon-prompt-lab/scripts/build_lab.py:31-52].

| Dimension ID | Name | Adversary-Proof Standard (Score: 2) |
| :--- | :--- | :--- |
| `predicate` | Success predicate | An adversarial reader can decide unambiguously whether an artifact satisfies it; quantifiers and scope explicit. |
| `definitions` | Definitions | Every load-bearing term defined, degenerate cases settled. |
| `non_counting` | Non-counting outcomes | The plausible near misses for this specific problem are excluded by name. |
| `auditor` | Auditor checklist | Enumerated, domain-specific failure modes including the circularity analogue. |
| `persistence_gate` | Persistence-verification pairing | Every persistence instruction has a matching verification gate. |
| `return_condition` | Return condition | A predicate over the artifact; fallback scoped to external budget exhaustion only. |
| `diversity` | Diversity policy (parallel) | Early independence, idea-keyed registry, blocked-route rules, late cross-pollination. |
| `reporting` | Reporting contract | Concrete artifacts required; claims must trace to session evidence. |
| `contamination` | Contamination guards | Retrieval scope stated wherever result independence matters. |
| `harness` | Harness separation | No hard constraint lives only in the prompt; budgets and permissions enforced outside. |

The scoring calculation ignores `"na"` entries, aggregates numeric scores (`0`, `1`, `2`), computes the total percentage against the maximum possible score, and displays comparative badges in the UI [examples/long-horizon-prompt-lab/scripts/build_lab.py:58-63, examples/long-horizon-prompt-lab/ui/app.js:21-24].

Sources: `examples/long-horizon-prompt-lab/scripts/build_lab.py:31-63`, `examples/long-horizon-prompt-lab/ui/app.js:21-24`

---

## 5. Automation, Screenshots & Metadata

To ensure documentation fidelity and support continuous integration, the lab includes automation scripts and search metadata in `ui/` and `scripts/`.

* `capture.mjs`: Uses `puppeteer-core` driving the system Chrome installation to capture targeted screenshots of specific DOM elements (`shot-<id>-split.png`, `shot-<id>-scorecard.png`) and full-page layouts (`shot-<id>-full.png`) [examples/long-horizon-prompt-lab/scripts/capture.mjs:1-11].
* `sitemap.xml`: Declares standard XML sitemap entries for GitHub Pages deployment (`index.html`, `guide.html`, `lab.html`, `references.html`) with priority weighting [examples/long-horizon-prompt-lab/ui/sitemap.xml:1-24].
* `robots.txt`: Instructs web crawlers on sitemap discovery and root accessibility [examples/long-horizon-prompt-lab/ui/robots.txt:1-5].

```mermaid
graph TD
    A["scripts/capture.mjs"] --> B["puppeteer.launch()"]
    B --> C["Load lab.html#id"]
    C --> D["clipElement('.page-hero')"]
    C --> E["clipElement('#pair-split')"]
    C --> F["clipElement('#scorecard')"]
    D --> G["screenshots/shot-hero.png"]
    E --> H["screenshots/shot-<id>-split.png"]
    F --> I["screenshots/shot-<id>-scorecard.png"]

    Sources: examples/long-horizon-prompt-lab/scripts/capture.mjs:1-110
```

Sources: `examples/long-horizon-prompt-lab/scripts/capture.mjs:1-112`, `examples/long-horizon-prompt-lab/ui/sitemap.xml:1-24`, `examples/long-horizon-prompt-lab/ui/robots.txt:1-5`

---

