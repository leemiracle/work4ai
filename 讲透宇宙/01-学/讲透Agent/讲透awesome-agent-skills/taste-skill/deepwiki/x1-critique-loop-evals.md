<!-- source: DeepWiki mcp.deepwiki.com · repo Leonxlnx/taste-skill · extra page Critique Loop & Evals · fetched 2026-10-26 -->

# Critique Loop & Evals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/taste-skill/evals/evals.json](skills/taste-skill/evals/evals.json)
- [skills/taste-skill/references/critique.md](skills/taste-skill/references/critique.md)
- [skills/taste-skill/scripts/lint.mjs](skills/taste-skill/scripts/lint.mjs)

</details>



The "Look" phase of the `taste-skill` pipeline is where the agent critically evaluates its own output. This page details the rubric used for self-critique, the iterative fix rounds, and the regression test suite that ensures consistent quality. The primary goal is to ensure the generated designs adhere to the "Taste Standard" and avoid common AI tells, as outlined in [2.1. AI Tells & Anti-Patterns]().

## The Critique Rubric

The agent reviews its generated screenshots against a detailed rubric defined in `references/critique.md` [skills/taste-skill/references/critique.md:1-182](). This rubric is designed to be applied to screenshots, not directly to the code, to prevent the agent from interpreting its intentions rather than what is actually rendered [skills/taste-skill/references/critique.md:3-5]().

The critique process involves fourteen distinct passes, each focusing on a different aspect of the design:

1.  **Focal Point & Purpose**: Assesses if the page has a clear focal point and if its purpose is immediately understandable [skills/taste-skill/references/critique.md:20-24]().
2.  **Visual Hierarchy (Squint Test)**: Evaluates the page's reduction to a few large masses, ensuring clear size differences and avoiding a "medium" feel [skills/taste-skill/references/critique.md:25-28]().
3.  **Idea & Brand Identity**: Checks if the design conveys a specific idea and is distinct from competitors, ensuring the core concept extends throughout the page [skills/taste-skill/references/critique.md:29-34]().
4.  **Alignment (Edges)**: Counts distinct horizontal alignment positions of text blocks, aiming for two or three for a composed page [skills/taste-skill/references/critique.md:35-37]().
5.  **Space and Frame**: Examines the use of negative space, distinguishing intentional rests from accidental holes, and checks for consistent margins and balanced sections [skills/taste-skill/references/critique.md:38-42]().
6.  **Typography**: Reviews type scale, number of font sizes, orphan words in headlines, paragraph width, and text alignment [skills/taste-skill/references/critique.md:43-46]().
7.  **Colour Proportions**: Identifies the dominant, supporting, and accent colours, and assesses the effectiveness of accent placement [skills/taste-skill/references/critique.md:47-49]().
8.  **Imagery**: Counts real pictures, checks for moving images, assesses image purpose, crop ratios, and consistency in photography style [skills/taste-skill/references/critique.md:50-55]().
9.  **Layout Variety (Sameness)**: Identifies repetitive section layouts, aiming for variety to avoid a templated feel [skills/taste-skill/references/critique.md:56-58]().
10. **Mobile Responsiveness**: Evaluates the mobile screen as an independent composition, not just a squeezed desktop version [skills/taste-skill/references/critique.md:59-61]().
11. **Visual Fullness**: Assesses if each screen functions as a composed poster, avoiding sparse layouts that resemble unfinished wireframes [skills/taste-skill/references/critique.md:62-66]().
12. **Substance & Information Delivery**: Checks if all requested information is present, readable, and if the primary action is clear and accessible [skills/taste-skill/references/critique.md:67-70]().
13. **Collisions & Overlaps**: Identifies any elements overlapping headlines, buttons, or running off-screen, especially on mobile [skills/taste-skill/references/critique.md:71-75]().
14. **Competitor & Live Thing**: A final check against a competitor's brand and the identification of the unique "live thing" or interactive element [skills/taste-skill/references/critique.md:69-71]().

### Scoring

The critique culminates in a score based on four criteria, weighted similarly to an Awwwards juror [skills/taste-skill/references/critique.md:79-81]():

*   **Design (40%)**: Composition, typography, colour, imagery, craft [skills/taste-skill/references/critique.md:83-88]().
*   **Usability (30%)**: Orientation, readability, obvious actions, mobile experience [skills/taste-skill/references/critique.md:89-94]().
*   **Creativity (20%)**: The uniqueness and execution of the core idea [skills/taste-skill/references/critique.md:95-99]().
*   **Content (10%)**: Specificity, truthfulness, and editing of words and pictures [skills/taste-skill/references/critique.md:100-104]().

The overall score is calculated as: `0.4 * design + 0.3 * usability + 0.2 * creativity + 0.1 * content` [skills/taste-skill/references/critique.md:106-107]().

Sources:
* [skills/taste-skill/references/critique.md:1-182]()

## Fix Rounds

The `taste-skill` pipeline incorporates up to three fix rounds. After the initial generation and critique, if the output does not meet the desired standard, the agent attempts to rectify the issues identified by the critique. This iterative process allows for refinement and improvement of the generated design. The specific mechanisms for how the agent interprets and applies these critique findings to modify its code are part of the broader agent architecture, but the `critique.md` serves as the foundational document for this evaluation.

## Regression Testing with Evals

To ensure the quality and consistency of the `taste-skill`'s output, a set of regression tests is maintained in `evals/evals.json` [skills/taste-skill/evals/evals.json:1-76](). These evaluations define specific prompts and expected outputs, serving as benchmarks for the skill's performance.

### Evals Structure

Each evaluation in `evals.json` is an object with the following properties:

*   `id`: A unique identifier for the evaluation [skills/taste-skill/evals/evals.json:6]().
*   `name`: A descriptive name for the evaluation [skills/taste-skill/evals/evals.json:7]().
*   `prompt`: The natural language prompt given to the agent [skills/taste-skill/evals/evals.json:8]().
*   `expected_output`: A detailed description of the desired outcome, including adherence to "Taste Standard" rules and specific design elements [skills/taste-skill/evals/evals.json:9]().
*   `files`: An array of files, though typically empty in the provided examples [skills/taste-skill/evals/evals.json:10]().

### Running Evals

The `how_to_run` field in `evals.json` outlines the procedure for running these evaluations [skills/taste-skill/evals/evals.json:3-4]():

1.  **Agent Comparison**: The prompt for each eval is given to two fresh agents: one with the `design-taste-frontend` skill and one without (as a baseline).
2.  **Inspection**: Both agents' outputs are rendered and inspected using `scripts/inspect.mjs`.
3.  **Human Judging**: A human judge, unaware of which output came from which agent, scores the screenshots using the `references/critique.md` rubric.
4.  **FAIL Count**: The number of `inspect.mjs` FAILs is recorded for both outputs.
5.  **App Screen Evals**: Evals 7 to 10 are specifically for app screens and should be inspected with the `--app` flag for `inspect.mjs` and judged using the app-screen passes in `references/critique.md`. The `lint.mjs` script also adjusts its rules based on `appMode` [skills/taste-skill/scripts/lint.mjs:15-17]().

### Example Evals

The `evals.json` includes a variety of scenarios, covering different types of landing pages and app screens:

*   **SaaS Invoicing (ID 1)**: Tests a landing page for an invoicing tool, expecting a clear idea, specific headline rules, and adherence to general "Taste Standard" rules [skills/taste-skill/evals/evals.json:5-11]().
*   **Restaurant (ID 2)**: Focuses on a one-page restaurant website, emphasizing typographic menu design and atmospheric imagery [skills/taste-skill/evals/evals.json:12-18]().
*   **Portfolio (ID 3)**: Evaluates a product designer's portfolio homepage, requiring a finished look even without project images [skills/taste-skill/evals/evals.json:19-25]().
*   **Product Ceramics (ID 4)**: Tests a product launch page without product photography, focusing on honest representation and clear purchase actions [skills/taste-skill/evals/evals.json:26-32]().
*   **Guesthouse (ID 5)**: A website for a guesthouse, emphasizing a clear hero section and easy-to-find booking information [skills/taste-skill/evals/evals.json:33-39]().
*   **Conference (ID 6)**: A landing page for a design conference, requiring strong typographic or colour ideas and structured text for line-up and schedule [skills/taste-skill/evals/evals.json:40-46]().
*   **App Budget Overview (ID 7)**: An app screen for a budgeting tool, expecting a quiet shell, clear titles, aligned numbers, and data-focused colour usage [skills/taste-skill/evals/evals.json:47-53]().
*   **App Deploy Dashboard (ID 8)**: A dashboard for a deployment platform, focusing on a dense, readable dark theme with clear data presentation [skills/taste-skill/evals/evals.json:54-60]().
*   **App Settings Billing (ID 9)**: A settings screen with billing information, requiring clear label-field relationships, consistent control heights, and quiet borders [skills/taste-skill/evals/evals.json:61-65]().

### Bridging Natural Language to Code Entities

The `evals.json` file serves as a direct bridge between natural language prompts and the expected code-generated output, which is then evaluated against the `critique.md` rubric.

```mermaid
graph TD
    A[Natural Language Prompt] --> B(Agent with taste-skill);
    B --> C{Code Generation};
    C --> D[Rendered Screenshots];
    D --> E[scripts/inspect.mjs "Inspection"];
    E -- "FAIL/WARN counts" --> F[Human Judge];
    F -- "Scores (Design, Usability, Creativity, Content)" --> G[references/critique.md "Rubric"];
    G --> H{Evaluation Result};
    H -- "If unsatisfactory" --> B;
    H -- "Regression Test Set" --> I[evals/evals.json];

    subgraph "Critique Loop"
        D -- "Visual Output" --> G;
        G -- "Feedback" --> B;
    end

    subgraph "Regression Testing"
        I -- "Defines Expected Output" --> H;
    end
```
**Diagram: Critique Loop and Evals Data Flow**

Sources:
* [skills/taste-skill/evals/evals.json:1-76]()
* [skills/taste-skill/references/critique.md:1-182]()
* [skills/taste-skill/scripts/lint.mjs:15-17]()

### `lint.mjs` and App Mode Integration

The `lint.mjs` script, responsible for static source linting, also integrates with the concept of "app mode" [skills/taste-skill/scripts/lint.mjs:2-3](). When `appMode` is enabled (either via the `--app` flag or if `direction.json` indicates an 'app' kind), certain rules are adjusted or nullified [skills/taste-skill/scripts/lint.mjs:15-17, 62-63](). This reflects the different design standards for app screens compared to marketing pages, as detailed in `references/app-screens.md`. For instance, app screens might allow for certain elements like subtle shadows or specific font treatments that would be flagged as "tells" in a marketing page context.

```mermaid
graph TD
    A[User Input / Agent Decision] --> B{Check for --app flag};
    B -- "Yes" --> C[appMode = true];
    B -- "No" --> D{Read .taste-skill/direction.json};
    D -- "kind === 'app'" --> C;
    D -- "kind !== 'app'" --> E[appMode = false];
    C --> F[Apply APP_LEVEL adjustments to rules R];
    E --> F;
    F --> G[scripts/lint.mjs "Static Linting"];
    G --> H[Generated Code];

    subgraph "App Mode Logic"
        B; D; C; E; F;
    end
```
**Diagram: `lint.mjs` App Mode Integration**

Sources:
* [skills/taste-skill/scripts/lint.mjs:2-3]()
* [skills/taste-skill/scripts/lint.mjs:15-17]()
* [skills/taste-skill/scripts/lint.mjs:62-63]()

---

