<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/lumos · page 5 Project Documentation Site · fetched 2026-10-26 -->

# Project Documentation Site

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/index.html](docs/index.html)
- [docs/static/css/bulma.min.css](docs/static/css/bulma.min.css)
- [docs/static/images/lumos_annotation.png](docs/static/images/lumos_annotation.png)
- [docs/static/images/lumos_architecture.png](docs/static/images/lumos_architecture.png)
- [docs/static/images/lumos_formulation.png](docs/static/images/lumos_formulation.png)
- [docs/static/images/lumos_results_1.png](docs/static/images/lumos_results_1.png)
- [docs/static/images/lumos_results_2.png](docs/static/images/lumos_results_2.png)
- [docs/static/images/lumos_results_3.png](docs/static/images/lumos_results_3.png)
- [docs/static/images/lumos_results_4.png](docs/static/images/lumos_results_4.png)
- [docs/static/js/index.js](docs/static/js/index.js)

</details>



The Lumos project documentation site, located at `docs/index.html`, serves as the primary public-facing technical overview for the research community. It utilizes the **Bulma CSS** framework to provide a responsive, modular presentation of the Lumos architecture, unified data formats, and multi-domain evaluation results [docs/index.html:25-31]().

## Website Architecture and Tech Stack

The documentation site is a static single-page application designed for high readability and technical depth.

*   **CSS Framework:** Bulma (v0.9.1) for layout and UI components [docs/static/css/bulma.min.css:1-1]().
*   **Interactivity:** jQuery (v3.5.1) and custom JavaScript in `docs/static/js/index.js` for handling UI events like navbar toggles and image carousels [docs/index.html:34-38]().
*   **Visual Components:**
    *   **Bulma Carousel:** Used for rotating result visualizations [docs/static/js/index.js:42-50]().
    *   **Bulma Slider:** Integrated for interactive data comparisons [docs/static/js/index.js:76-76]().
    *   **Academic Icons:** FontAwesome and Academicons for linking to the ArXiv paper, HuggingFace models, and GitHub repository [docs/index.html:28-30](), [docs/index.html:123-173]().

### Visual Assets to Code Mapping
The site includes several key diagrams that bridge the conceptual "Natural Language Space" (research goals) with the "Code Entity Space" (implementation).

#### System Architecture Visualization
The site visualizes the core Lumos pipeline, mapping the three-module design to specific logic handled in the evaluation scripts.

**Lumos Pipeline Flow Diagram**
```mermaid
graph LR
    subgraph "Natural Language Space"
        Task["User Task / Question"]
    end

    subgraph "Code Entity Space (Lumos Modules)"
        Planning["Planning Module (Llama-2 FT)"]
        Grounding["Grounding Module (Llama-2 FT)"]
        Execution["Execution Module (Tool Dispatcher)"]
    end

    Task --> Planning
    Planning -- "Subgoal (unified_format)" --> Grounding
    Grounding -- "Action (domain_vocab)" --> Execution
    Execution -- "Observation (inter_results)" --> Planning

    Sources: [docs/static/images/lumos_architecture.png](), [docs/index.html:91-112]()
```

#### Results and Formulation
The site provides detailed visualizations of Lumos' performance across diverse benchmarks (Complex QA, Maths, Web Agents) [docs/static/images/lumos_results_1.png](), [docs/static/images/lumos_results_2.png](). It specifically highlights the difference between **Lumos-Iterative** (Lumos-I) and **Lumos-Onetime** (Lumos-O) formulations [docs/static/images/lumos_formulation.png]().

**Formulation Logic Diagram**
```mermaid
graph TD
    subgraph "Lumos-I (Iterative Loop)"
        LumosI["run_eval.py (Iterative)"]
        Loop["While (not finished)"]
        StepPlan["Planning Module"]
        StepGround["Grounding Module"]
        StepExec["Execution Module"]
        
        LumosI --> Loop
        Loop --> StepPlan --> StepGround --> StepExec --> Loop
    end

    subgraph "Lumos-O (One-time Generation)"
        LumosO["run_eval.py (Onetime)"]
        FullPlan["Planning Module (Generate All Subgoals)"]
        FullGround["Grounding Module (Generate All Actions)"]
        BatchExec["Execution Module (Sequential Run)"]
        
        LumosO --> FullPlan --> FullGround --> BatchExec
    end

    Sources: [docs/static/images/lumos_formulation.png](), [docs/index.html:182-186]()
```

## Key Technical Sections

### 1. Research Overview
The `hero` section introduces Lumos as a framework for learning agents with unified data and modular design using open-source LLMs (specifically Llama-2) [docs/index.html:86-112]().

### 2. Result Visualizations
The site hosts high-resolution plots comparing Lumos against baseline models (CoT, Direct, GPT-4) across:
*   **Complex QA:** HotpotQA and StrategyQA [docs/static/images/lumos_results_1.png]().
*   **Math Reasoning:** GSM8K and SVAMP [docs/static/images/lumos_results_2.png]().
*   **Web Navigation:** Mind2Web and WebShop [docs/static/images/lumos_results_3.png]().

### 3. Annotation Examples
A dedicated visual section explains the unified data format used for training. It shows how raw benchmark data is transformed into structured subgoal/action pairs, which are then processed by the `prompt_conversion.py` and `process_for_train.py` scripts [docs/static/images/lumos_annotation.png]().

## Implementation Details

The site utilizes a standard Bulma template structure. The `navbar-burger` logic in `index.js` ensures mobile compatibility by toggling the `is-active` class on the `navbar-menu` [docs/static/js/index.js:25-30](). Result carousels are initialized with specific options (3 slides visible, infinite loop) to showcase the breadth of benchmark performance [docs/static/js/index.js:32-42]().

Sources:
*   [docs/index.html:1-180]()
*   [docs/static/js/index.js:23-78]()
*   [docs/static/css/bulma.min.css:1-1]()
*   [docs/static/images/lumos_architecture.png]()
*   [docs/static/images/lumos_formulation.png]()
*   [docs/static/images/lumos_annotation.png]()
*   [docs/static/images/lumos_results_1.png]()
*   [docs/static/images/lumos_results_2.png]()

---

