<!-- source: DeepWiki mcp.deepwiki.com · repo Leonxlnx/taste-skill · extra page inspect.mjs: Real-Browser Inspection · fetched 2026-10-26 -->

# inspect.mjs: Real-Browser Inspection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/taste-skill/scripts/inspect.mjs](skills/taste-skill/scripts/inspect.mjs)
- [skills/taste-skill/scripts/lib/probe.mjs](skills/taste-skill/scripts/lib/probe.mjs)

</details>



This page details `inspect.mjs`, a critical component of the taste-skill's Gate phase. Its purpose is to perform real-browser inspection of a generated web page or app screen. It launches a headless Chromium instance, serves local files via a throwaway HTTP server, iterates through various viewport sizes (1440px, 768px, 390px), records motion, checks for title visibility, captures scroll film strips, audits for reduced-motion compliance, and generates screenshots and a JSON report of findings.

## Overview of Operation

`inspect.mjs` orchestrates a series of browser interactions and measurements to evaluate a web page against the Taste Standard. It leverages the Chrome DevTools Protocol (CDP) via `cdp.mjs` to control the browser, inject measurement scripts (`probe.mjs`), and capture visual evidence. The process involves:

1.  **Local File Serving**: If the target is a local HTML file, a temporary HTTP server is spun up to serve the file and its assets, ensuring correct relative path resolution and `fetch()` behavior [skills/taste-skill/scripts/inspect.mjs:44-62]().
2.  **Browser Launch**: A new browser instance is launched using `Browser.launch()` [skills/taste-skill/scripts/inspect.mjs:69]().
3.  **Viewport Iteration**: The page is loaded and inspected across a set of predefined widths (defaulting to 1440, 768, 390 pixels) [skills/taste-skill/scripts/inspect.mjs:26]().
4.  **Motion Recording**: A script (`MOTION_RECORDER`) is injected to track CSS animations, transitions, and script-driven style changes to quantify page motion [skills/taste-skill/scripts/inspect.mjs:77-87]().
5.  **Page Measurement**: The `probe()` function from `probe.mjs` is executed within the page context to gather detailed information about layout, typography, colors, and other visual properties [skills/taste-skill/scripts/inspect.mjs:19]().
6.  **Rule Evaluation**: The collected data is then passed to `judge()`, `judgeLayout()`, and `judgeApp()` from `rules.mjs` to identify any violations of the Taste Standard [skills/taste-skill/scripts/inspect.mjs:20]().
7.  **Screenshot Capture**: Screenshots are taken at various stages: initial load, after scrolling, and for film strips, saved to `.taste-skill/inspect/` [skills/taste-skill/scripts/inspect.mjs:68]().
8.  **Reduced Motion Audit**: The page is re-evaluated with `prefers-reduced-motion` enabled to ensure graceful degradation [skills/taste-skill/scripts/inspect.mjs:209-215]().
9.  **JSON Reporting**: All findings, viewport details, and image paths are compiled into a JSON report [skills/taste-skill/scripts/inspect.mjs:71]().

Sources:
- [skills/taste-skill/scripts/inspect.mjs:1-303]()
- [skills/taste-skill/scripts/lib/cdp.mjs:1-200]()
- [skills/taste-skill/scripts/lib/probe.mjs:1-909]()
- [skills/taste-skill/scripts/lib/rules.mjs:1-243]()

### Inspection Data Flow

The following diagram illustrates the high-level data flow within `inspect.mjs`.

```mermaid
graph TD
    A[Start inspect.mjs] --> B{Is target a local file?};
    B -- Yes --> C[Create HTTP Server];
    B -- No --> D[Use target URL directly];
    C --> E[Get URL from server];
    D --> E;
    E --> F[Launch Browser (cdp.mjs)];
    F --> G[Initialize Report Object];
    G --> H{For each viewport width};
    H --> I[Set Viewport Size];
    I --> J[Inject MOTION_RECORDER];
    J --> K[Navigate to URL];
    K --> L[Wait for Load & Motion Sample];
    L --> M[Execute probe() in page];
    M --> N[Get page data];
    N --> O[Execute judge() rules];
    O --> P[Capture Screenshots];
    P --> Q[Perform Scroll Film Strip (if enabled)];
    Q --> R[Audit Reduced Motion];
    R --> S[Add findings to report];
    H -- All viewports done --> T[Write JSON Report];
    T --> U[Cleanup (close browser, stop server)];
    U --> V[Exit with status code];

    subgraph "Browser Context"
        J -- Injects --> MOTION_RECORDER_SCRIPT[MOTION_RECORDER Script];
        M -- Executes --> PROBE_FUNCTION[probe() function];
    end

    subgraph "Node.js Context"
        A; B; C; D; E; F; G; H; I; K; L; N; O; P; Q; R; S; T; U; V;
    end
```
**Diagram: inspect.mjs High-Level Data Flow**

Sources:
- [skills/taste-skill/scripts/inspect.mjs:44-62]()
- [skills/taste-skill/scripts/inspect.mjs:69-71]()
- [skills/taste-skill/scripts/inspect.mjs:92-220]()
- [skills/taste-skill/scripts/inspect.mjs:77-87]()
- [skills/taste-skill/scripts/lib/probe.mjs:5-909]()
- [skills/taste-skill/scripts/lib/rules.mjs:1-243]()

## Key Components and Implementation Details

### Local HTTP Server

When `inspect.mjs` is given a local file path, it sets up a minimal HTTP server to serve the file and its associated assets. This is crucial for ensuring that relative paths, `fetch()` requests, and module scripts behave as they would in a hosted environment, avoiding potential sandbox issues or file system discrepancies [skills/taste-skill/scripts/inspect.mjs:44-62]().

-   **Root Directory**: The server determines the root directory for serving files. If the target file is within the current working directory, the CWD is used; otherwise, the target file's directory becomes the root [skills/taste-skill/scripts/inspect.mjs:48-49]().
-   **MIME Types**: A `MIME` object maps common file extensions to their respective content types [skills/taste-skill/scripts/inspect.mjs:50]().
-   **Request Handling**: The server handles requests by resolving the requested path relative to its root, checking for directory access violations, and streaming the file content with appropriate headers [skills/taste-skill/scripts/inspect.mjs:51-58]().

Sources:
- [skills/taste-skill/scripts/inspect.mjs:44-62]()

### Viewport Iteration and Screenshots

The inspection process iterates through a configurable list of viewport widths, defaulting to `1440, 768, 390` [skills/taste-skill/scripts/inspect.mjs:26](). For each width, a corresponding height is selected from the `HEIGHT` map [skills/taste-skill/scripts/inspect.mjs:63]().

For each viewport:
1.  The browser page is resized using `page.setViewport()` [skills/taste-skill/scripts/inspect.mjs:95]().
2.  A screenshot of the initial fold is captured (e.g., `desktop-fold.jpg`) [skills/taste-skill/scripts/inspect.mjs:100]().
3.  The entire page is scrolled, and screenshots are taken at intervals (e.g., `desktop-page-01.jpg`, `desktop-page-02.jpg`) to capture the full vertical extent [skills/taste-skill/scripts/inspect.mjs:104-115]().

Sources:
- [skills/taste-skill/scripts/inspect.mjs:26]()
- [skills/taste-skill/scripts/inspect.mjs:63]()
- [skills/taste-skill/scripts/inspect.mjs:95]()
- [skills/taste-skill/scripts/inspect.mjs:100]()
- [skills/taste-skill/scripts/inspect.mjs:104-115]()

### Motion Recording

A JavaScript snippet, `MOTION_RECORDER`, is injected into the page before any of its own scripts execute [skills/taste-skill/scripts/inspect.mjs:93](). This script monitors for various types of motion:
-   **CSS Animations**: `animationstart` event listener [skills/taste-skill/scripts/inspect.mjs:80]().
-   **CSS Transitions**: `transitionrun` event listener [skills/taste-skill/scripts/inspect.mjs:81]().
-   **Script-driven Changes**: A `MutationObserver` watches for `style` attribute changes that affect `transform`, `opacity`, `scale`, `rotate`, or `clip-path` [skills/taste-skill/scripts/inspect.mjs:82-84]().
-   **Web Animations API**: `document.getAnimations()` is sampled to catch animations not covered by events [skills/taste-skill/scripts/inspect.mjs:85]().

The recorder counts distinct moving elements and categorizes them. This data is later retrieved via `window.__motion()` to assess the page's motion characteristics [skills/taste-skill/scripts/inspect.mjs:102]().

Sources:
- [skills/taste-skill/scripts/inspect.mjs:77-87]()
- [skills/taste-skill/scripts/inspect.mjs:93]()
- [skills/taste-skill/scripts/inspect.mjs:102]()

### `probe()`: In-Page Measurement

The `probe()` function, defined in `probe.mjs`, is serialized and executed within the browser's page context [skills/taste-skill/scripts/inspect.mjs:19](). It is self-contained and has no external dependencies. `probe()` gathers a comprehensive set of data points about the page's visual characteristics:

-   **Color Normalization**: Functions `rgba()`, `hex()`, `lum()`, `contrast()`, `hsl()` normalize and analyze colors [skills/taste-skill/scripts/lib/probe.mjs:9-34]().
-   **Monospace Detection**: `isMono()` determines if a font family is monospace by measuring character widths [skills/taste-skill/scripts/lib/probe.mjs:36-45]().
-   **Element Collection**: Iterates through all visible elements, filtering out scripts, styles, and hidden content. It collects text nodes, their computed styles (font family, size, weight, letter spacing, line height, color, etc.), and bounding box information [skills/taste-skill/scripts/lib/probe.mjs:58-87]().
-   **Heading Block Analysis**: Identifies logical heading blocks and counts lines within them [skills/taste-skill/scripts/lib/probe.mjs:90-123]().
-   **Layout Metrics**: Measures grid usage, spacing, element overlaps, and visual hierarchy [skills/taste-skill/scripts/lib/probe.mjs:125-200]() (and beyond).
-   **Color Share**: Calculates the proportion of screen area covered by different colors [skills/taste-skill/scripts/lib/probe.mjs:800-830]().
-   **Specific Tell Detection**: Contains logic to detect various "AI tells" and anti-patterns, such as specific shadow types, gradients, and common placeholder text [skills/taste-skill/scripts/lib/probe.mjs:202-798]() (and beyond).

The data returned by `probe()` is a rich JSON object used by the rule evaluators.

Sources:
- [skills/taste-skill/scripts/lib/probe.mjs:1-909]()
- [skills/taste-skill/scripts/inspect.mjs:19]()

### Rule Evaluation (`judge`, `judgeLayout`, `judgeApp`)

After `probe()` returns its data, `inspect.mjs` calls functions from `rules.mjs` to evaluate the page against the Taste Standard:

-   **`judge(data, allow, appMode, dealtFonts)`**: The primary function that evaluates general design rules, typography, color usage, and common anti-patterns. It takes the `probe()` output, a list of allowed rule IDs, the `appMode` flag, and `dealtFonts` to check for font fallbacks [skills/taste-skill/scripts/lib/rules.mjs:10-243]().
-   **`judgeLayout(data, allow)`**: Focuses specifically on layout-related rules, such as grid alignment, spacing consistency, and element positioning [skills/taste-skill/scripts/lib/rules.mjs:243]() (example range).
-   **`judgeApp(data, allow)`**: Applied when `appMode` is true, this function evaluates rules specific to app screens and dashboards, which have different aesthetic requirements than marketing pages [skills/taste-skill/scripts/lib/rules.mjs:243]() (example range).

Findings are categorized as `FAIL` or `WARN` and include a rule ID, message, and relevant data points. `FAIL` findings result in a non-zero exit code for `inspect.mjs` [skills/taste-skill/scripts/inspect.mjs:230]().

Sources:
- [skills/taste-skill/scripts/lib/rules.mjs:1-243]()
- [skills/taste-skill/scripts/inspect.mjs:20]()
- [skills/taste-skill/scripts/inspect.mjs:230]()

### Film Strip Scroll Capture

When the `--film` flag is enabled (or automatically by a direction that dealt scroll scenes), `inspect.mjs` captures a "film strip" of the page as it scrolls [skills/taste-skill/scripts/inspect.mjs:6](). This is crucial for evaluating scroll scenes and motion design.

-   The page is scrolled incrementally using `page.wheel()` to simulate real user input [skills/taste-skill/scripts/inspect.mjs:150-151]().
-   Screenshots are taken at regular intervals (e.g., every third of a screen height) [skills/taste-skill/scripts/inspect.mjs:152]().
-   These images (e.g., `desktop-film-01.jpg`, `desktop-film-02.jpg`) provide a visual sequence of the scroll experience.

Sources:
- [skills/taste-skill/scripts/inspect.mjs:6]()
- [skills/taste-skill/scripts/inspect.mjs:150-152]()

### Reduced Motion Audit

To ensure accessibility and compliance with user preferences, `inspect.mjs` performs an audit with `prefers-reduced-motion` enabled [skills/taste-skill/scripts/inspect.mjs:209-215]().

1.  The browser's `prefersReducedMotion` preference is set to `reduce` [skills/taste-skill/scripts/inspect.mjs:210]().
2.  The page is reloaded [skills/taste-skill/scripts/inspect.mjs:211]().
3.  `probe()` is executed again, and the motion data is re-evaluated.
4.  Findings related to motion (e.g., `MOTION_TOO_MUCH`) are checked to ensure they are mitigated when reduced motion is preferred [skills/taste-skill/scripts/inspect.mjs:213-214]().

Sources:
- [skills/taste-skill/scripts/inspect.mjs:209-215]()

### `inspect.mjs` Core Logic Flow

```mermaid
graph TD
    A[inspect.mjs CLI Entry] --> B{Parse Arguments};
    B --> C{Load direction.json allowances};
    C --> D{Setup HTTP Server (if local file)};
    D --> E[Launch Browser (Browser.launch)];
    E --> F[Create Helper Page];
    F --> G[Initialize Report Object];

    subgraph "Viewport Iteration Loop"
        H{For each width in widths[]};
        H --> I[Set Viewport (page.setViewport)];
        I --> J[Inject MOTION_RECORDER];
        J --> K[Navigate to URL (page.goto)];
        K --> L[Wait for load & motion sample];
        L --> M[Capture Fold Screenshot];
        M --> N[Scroll & Capture Page Screenshots];
        N --> O[Execute probe() in page (page.evaluate)];
        O --> P[Evaluate Rules (judge, judgeLayout, judgeApp)];
        P --> Q[Perform Title Seen Check];
        Q --> R{If film mode enabled};
        R -- Yes --> S[Capture Film Strip (page.wheel, page.screenshot)];
        R -- No --> T[Continue];
        S --> T;
        T --> U[Audit Reduced Motion];
        U --> V[Add Viewport Results to Report];
        H -- End Loop --> W[Finalize Report];
    end

    W --> X[Write report.json];
    X --> Y[Cleanup (browser.close, server.close)];
    Y --> Z[Exit (process.exit)];

    subgraph "External Modules"
        Browser[cdp.mjs::Browser.launch];
        probe[probe.mjs::probe];
        judge[rules.mjs::judge];
        judgeLayout[rules.mjs::judgeLayout];
        judgeApp[rules.mjs::judgeApp];
    end

    E -- Uses --> Browser;
    O -- Calls --> probe;
    P -- Calls --> judge;
    P -- Calls --> judgeLayout;
    P -- Calls --> judgeApp;
    U -- Calls --> judge;
```
**Diagram: `inspect.mjs` Detailed Execution Flow**

Sources:
- [skills/taste-skill/scripts/inspect.mjs:22-42]()
- [skills/taste-skill/scripts/inspect.mjs:38-41]()
- [skills/taste-skill/scripts/inspect.mjs:44-62]()
- [skills/taste-skill/scripts/inspect.mjs:69-71]()
- [skills/taste-skill/scripts/inspect.mjs:92-220]()
- [skills/taste-skill/scripts/lib/cdp.mjs:1-200]()
- [skills/taste-skill/scripts/lib/probe.mjs:1-909]()
- [skills/taste-skill/scripts/lib/rules.mjs:1-243]()

---

