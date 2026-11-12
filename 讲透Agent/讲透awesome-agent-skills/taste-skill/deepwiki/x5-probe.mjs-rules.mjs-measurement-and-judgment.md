<!-- source: DeepWiki mcp.deepwiki.com · repo Leonxlnx/taste-skill · extra page probe.mjs & rules.mjs: Measurement and Judgment · fetched 2026-10-26 -->

# probe.mjs & rules.mjs: Measurement and Judgment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/taste-skill/scripts/lib/probe.mjs](skills/taste-skill/scripts/lib/probe.mjs)
- [skills/taste-skill/scripts/lib/rules.mjs](skills/taste-skill/scripts/lib/rules.mjs)

</details>



This page details the in-page measurement functions provided by `probe.mjs` and the rule evaluation logic within `rules.mjs`. These modules are critical components of the "Gate" phase of the `taste-skill` pipeline, responsible for programmatically assessing the generated UI against a set of design standards and identifying "tells" or anti-patterns. `probe.mjs` executes directly within the browser context to gather detailed metrics about the rendered page, while `rules.mjs` processes these metrics to generate findings, categorizing them as `FAIL` (blocking issues) or `WARN` (advisory issues).

## `probe.mjs`: In-Page Measurement

The `probe.mjs` module contains the `probe()` function, which is designed to run directly within the browser's page context. It collects a comprehensive set of metrics about the page's visual and structural characteristics. This function is self-contained, meaning it has no external imports and does not rely on closures over module scope, making it suitable for serialization and execution via the Chrome DevTools Protocol (CDP).

The `probe()` function gathers data on:
*   **Color Normalization**: Converts various color formats (e.g., `oklch()`, `color()`, named colors) to RGBA, HEX, HSL, and calculates luminance and contrast ratios [skills/taste-skill/scripts/lib/probe.mjs:9-34]().
*   **Monospace Detection**: Determines if a font family is monospace by measuring character widths, rather than relying on font names [skills/taste-skill/scripts/lib/probe.mjs:36-45]().
*   **Element Collection**: Iterates through DOM elements, filtering out scripts, styles, and hidden elements, and collects information about their dimensions, computed styles, and text content [skills/taste-skill/scripts/lib/probe.mjs:57-88]().
*   **Heading Blocks**: Identifies logical heading blocks by climbing the DOM tree from large text nodes, ensuring that a "headline" is treated as a single unit [skills/taste-skill/scripts/lib/probe.mjs:90-112]().
*   **Line Counting**: Accurately counts the number of lines a text element occupies, ignoring inline media or images [skills/taste-skill/scripts/lib/probe.mjs:114-123]().

The output of `probe()` is a detailed JavaScript object containing various measurements, including:
*   `viewport`: Width and height of the viewport.
*   `page`: General page metrics like scroll position, emoji usage, and background color.
*   `headings`: An array of detected headings with properties like text, size, line count, font family, and kind (e.g., 'headline', 'statement').
*   `hero`: Information about the main hero headline.
*   `eyebrows`: Details about "eyebrow" or "kicker" labels.
*   `numbered`: Instances of decorative index numbers.
*   `type`: Type-related metrics such as monospace usage, micro-labels, and font families.
*   `surfaces`: Data on gradients, shadows, outlines, and blurred elements.
*   `buttons`: Button styling, including gradients and shadows.
*   `layout`: Layout-specific measurements like section counts, grid usage, and spacing.
*   `app`: Metrics specific to app screens, such as sidebar presence and panel styles.
*   `colourShare`: Proportions of different colors used on the page.
*   `palette`: The dominant color palette extracted from the page.

```mermaid
graph TD
    A[CDP Client (cdp.mjs)] --> B{Execute probe() in browser context};
    B --> C[DOM Traversal & Element Collection];
    C --> D[Computed Style Analysis];
    C --> E[Text Content Extraction];
    D --> F[Color Normalization & Contrast Calculation];
    D --> G[Font Measurement & Monospace Detection];
    E --> H[Heading Block Identification];
    E --> I[Line Counting for Text Elements];
    F --> J[ColourShare & Palette Extraction];
    G --> K[Type Metrics (mono, micro-labels)];
    H --> L[Headline Metrics (lines, words)];
    I --> L;
    C --> M[Surface Metrics (gradients, shadows, outlines)];
    C --> N[Button Metrics];
    C --> O[Layout Metrics (sections, grids)];
    C --> P[App-specific Metrics (sidebars, panels)];
    B --> Q[Return Comprehensive Measurement Object];
    Q --> R[rules.mjs (for judgment)];

    subgraph "probe.mjs Execution"
        B; C; D; E; F; G; H; I; J; K; L; M; N; O; P; Q;
    end
```
**Diagram: `probe.mjs` Data Flow**

Sources:
*   [skills/taste-skill/scripts/lib/probe.mjs:1-5]()
*   [skills/taste-skill/scripts/lib/probe.mjs:9-34]()
*   [skills/taste-skill/scripts/lib/probe.mjs:36-45]()
*   [skills/taste-skill/scripts/lib/probe.mjs:57-88]()
*   [skills/taste-skill/scripts/lib/probe.mjs:90-112]()
*   [skills/taste-skill/scripts/lib/probe.mjs:114-123]()

## `rules.mjs`: Judgment and Findings

The `rules.mjs` module takes the detailed measurement object produced by `probe()` and applies a set of predefined rules to identify design "tells" or non-compliant patterns. It exports the `judge()` function, which is the primary entry point for evaluating the measurements [skills/taste-skill/scripts/lib/rules.mjs:24]().

The `judge()` function iterates through various categories of design rules, generating "findings" for each violation. A finding is an object with the following shape:
```javascript
{
  level: 'FAIL' | 'WARN', // Severity of the finding
  id: string,             // Unique identifier for the rule
  width: number,          // Viewport width at which the finding occurred
  message: string,        // Descriptive message about the violation
  fix: string             // Suggested fix or explanation
}
```

**Major Failure Codes and Categories:**

The `rules.mjs` module defines numerous rules, categorized as `FAIL` or `WARN`:

*   **`FAIL`**: Indicates a banned "tell" or a broken page. These issues must be resolved for the work to be considered complete [skills/taste-skill/scripts/lib/rules.mjs:2-3]().
    *   `headline-lines`: Headlines wrapping past two lines [skills/taste-skill/scripts/lib/rules.mjs:37]().
    *   `eyebrow`: Presence of eyebrow/kicker labels above headings [skills/taste-skill/scripts/lib/rules.mjs:50]().
    *   `mono`: Monospace type used outside of code blocks [skills/taste-skill/scripts/lib/rules.mjs:54]().
    *   `numbering`: Decorative index numbers (e.g., "01", "02") [skills/taste-skill/scripts/lib/rules.mjs:58]().
    *   `micro-label`: Excessive tiny uppercase letter-spaced labels [skills/taste-skill/scripts/lib/rules.mjs:62]().
    *   `emoji`: Emoji present in the page content [skills/taste-skill/scripts/lib/rules.mjs:64]().
    *   `gradient`: Gradient fills used on surfaces [skills/taste-skill/scripts/lib/rules.mjs:68]().
    *   `gradient-text`: Gradient-filled text [skills/taste-skill/scripts/lib/rules.mjs:69]().
    *   `shadow`: Box-shadows on elements at rest [skills/taste-skill/scripts/lib/rules.mjs:70]().
    *   `text-shadow`: Text-shadows [skills/taste-skill/scripts/lib/rules.mjs:71]().
    *   `button-fx`: Buttons with gradient fills or shadows/glows [skills/taste-skill/scripts/lib/rules.mjs:72]().
    *   `hairline`: Excessive thin rules/divider lines [skills/taste-skill/scripts/lib/rules.mjs:73]().
    *   `outlined-box`: Excessive boxes drawn with a 1px outline [skills/taste-skill/scripts/lib/rules.mjs:74]().
    *   `ai-purple`: Use of the "AI purple" color family, which is considered a generated-page signature [skills/taste-skill/scripts/lib/rules.mjs:13]().
    *   `cream`: Use of the "cream" color family, another generated-page signature [skills/taste-skill/scripts/lib/rules.mjs:11]().
    *   `terracotta`: Use of the "terracotta" color family, another generated-page signature [skills/taste-skill/scripts/lib/rules.mjs:12]().
    *   `layout-grid-gap`: Inconsistent or excessive grid gaps [skills/taste-skill/scripts/lib/rules.mjs:100]().
    *   `layout-grid-columns`: Inconsistent grid column counts [skills/taste-skill/scripts/lib/rules.mjs:101]().
    *   `layout-section-spacing`: Inconsistent vertical spacing between sections [skills/taste-skill/scripts/lib/rules.mjs:102]().
    *   `layout-section-variety`: Lack of variety in section layouts [skills/taste-skill/scripts/lib/rules.mjs:103]().
    *   `layout-max-width`: Page content exceeding a maximum width [skills/taste-skill/scripts/lib/rules.mjs:104]().
    *   `layout-min-width`: Page content falling below a minimum width [skills/taste-skill/scripts/lib/rules.mjs:105]().
    *   `layout-horizontal-scroll`: Horizontal scrolling detected [skills/taste-skill/scripts/lib/rules.mjs:106]().
    *   `layout-sticky-footer`: Sticky footer covering content [skills/taste-skill/scripts/lib/rules.mjs:107]().
    *   `layout-fixed-header`: Fixed header covering content [skills/taste-skill/scripts/lib/rules.mjs:108]().
    *   `layout-overlap`: Overlapping elements [skills/taste-skill/scripts/lib/rules.mjs:109]().
    *   `layout-empty-space`: Excessive empty space [skills/taste-skill/scripts/lib/rules.mjs:110]().
    *   `layout-off-grid`: Elements not aligning to the grid [skills/taste-skill/scripts/lib/rules.mjs:111]().
    *   `layout-misaligned`: Misaligned elements [skills/taste-skill/scripts/lib/rules.mjs:112]().
    *   `layout-z-index`: Z-index issues [skills/taste-skill/scripts/lib/rules.mjs:113]().
    *   `layout-responsive-break`: Responsive layout breaking [skills/taste-skill/scripts/lib/rules.mjs:114]().
    *   `layout-text-overflow`: Text overflowing its container [skills/taste-skill/scripts/lib/rules.mjs:115]().
    *   `layout-image-crop`: Poor image cropping [skills/taste-skill/scripts/lib/rules.mjs:116]().
    *   `layout-aspect-ratio`: Incorrect aspect ratios for media [skills/taste-skill/scripts/lib/rules.mjs:117]().
    *   `layout-contrast`: Insufficient color contrast [skills/taste-skill/scripts/lib/rules.mjs:118]().
    *   `layout-font-size`: Inconsistent or too small font sizes [skills/taste-skill/scripts/lib/rules.mjs:119]().
    *   `layout-line-height`: Inconsistent line heights [skills/taste-skill/scripts/lib/rules.mjs:120]().
    *   `layout-letter-spacing`: Inconsistent letter spacing [skills/taste-skill/scripts/lib/rules.mjs:121]().
    *   `layout-word-spacing`: Inconsistent word spacing [skills/taste-skill/scripts/lib/rules.mjs:122]().
    *   `layout-text-align`: Inconsistent text alignment [skills/taste-skill/scripts/lib/rules.mjs:123]().
    *   `layout-whitespace`: Inconsistent whitespace usage [skills/taste-skill/scripts/lib/rules.mjs:124]().
    *   `layout-padding`: Inconsistent padding [skills/taste-skill/scripts/lib/rules.mjs:125]().
    *   `layout-margin`: Inconsistent margins [skills/taste-skill/scripts/lib/rules.mjs:126]().
    *   `layout-border-radius`: Inconsistent border-radius [skills/taste-skill/scripts/lib/rules.mjs:127]().
    *   `layout-shadow-spread`: Excessive shadow spread [skills/taste-skill/scripts/lib/rules.mjs:128]().
    *   `layout-opacity`: Inconsistent opacity [skills/taste-skill/scripts/lib/rules.mjs:129]().
    *   `layout-transform`: Inconsistent transforms [skills/taste-skill/scripts/lib/rules.mjs:130]().
    *   `layout-transition`: Inconsistent transitions [skills/taste-skill/scripts/lib/rules.mjs:131]().
    *   `layout-animation`: Inconsistent animations [skills/taste-skill/scripts/lib/rules.mjs:132]().
    *   `layout-cursor`: Inconsistent cursor styles [skills/taste-skill/scripts/lib/rules.mjs:133]().
    *   `layout-pointer-events`: Inconsistent pointer-events [skills/taste-skill/scripts/lib/rules.mjs:134]().
    *   `layout-user-select`: Inconsistent user-select [skills/taste-skill/scripts/lib/rules.mjs:135]().
    *   `layout-overflow`: Inconsistent overflow [skills/taste-skill/scripts/lib/rules.mjs:136]().
    *   `layout-clip`: Inconsistent clip [skills/taste-skill/scripts/lib/rules.mjs:137]().
    *   `layout-visibility`: Inconsistent visibility [skills/taste-skill/scripts/lib/rules.mjs:138]().
    *   `layout-display`: Inconsistent display properties [skills/taste-skill/scripts/lib/rules.mjs:139]().
    *   `layout-position`: Inconsistent positioning [skills/taste-skill/scripts/lib/rules.mjs:140]().
    *   `layout-float`: Inconsistent floats [skills/taste-skill/scripts/lib/rules.mjs:141]().
    *   `layout-clear`: Inconsistent clears [skills/taste-skill/scripts/lib/rules.mjs:142]().
    *   `layout-direction`: Inconsistent text direction [skills/taste-skill/scripts/lib/rules.mjs:143]().
    *   `layout-writing-mode`: Inconsistent writing mode [skills/taste-skill/scripts/lib/rules.mjs:144]().
    *   `layout-text-orientation`: Inconsistent text orientation [skills/taste-skill/scripts/lib/rules.mjs:145]().
    *   `layout-vertical-align`: Inconsistent vertical alignment [skills/taste-skill/scripts/lib/rules.mjs:146]().
    *   `layout-white-space`: Inconsistent white-space handling [skills/taste-skill/scripts/lib/rules.mjs:147]().
    *   `layout-word-break`: Inconsistent word-break [skills/taste-skill/scripts/lib/rules.mjs:148]().
    *   `layout-hyphens`: Inconsistent hyphens [skills/taste-skill/scripts/lib/rules.mjs:149]().
    *   `layout-text-transform`: Inconsistent text-transform [skills/taste-skill/scripts/lib/rules.mjs:150]().
    *   `layout-text-decoration`: Inconsistent text-decoration [skills/taste-skill/scripts/lib/rules.mjs:151]().
    *   `layout-text-indent`: Inconsistent text-indent [skills/taste-skill/scripts/lib/rules.mjs:152]().
    *   `layout-text-overflow-ellipsis`: Inconsistent text-overflow ellipsis [skills/taste-skill/scripts/lib/rules.mjs:153]().
    *   `layout-text-rendering`: Inconsistent text-rendering [skills/taste-skill/scripts/lib/rules.mjs:154]().
    *   `layout-font-variant`: Inconsistent font-variant [skills/taste-skill/scripts/lib/rules.mjs:155]().
    *   `layout-font-feature-settings`: Inconsistent font-feature-settings [skills/taste-skill/scripts/lib/rules.mjs:156]().
    *   `layout-font-kerning`: Inconsistent font-kerning [skills/taste-skill/scripts/lib/rules.mjs:157]().
    *   `layout-font-stretch`: Inconsistent font-stretch [skills/taste-skill/scripts/lib/rules.mjs:158]().
    *   `layout-font-style`: Inconsistent font-style [skills/taste-skill/scripts/lib/rules.mjs:159]().
    *   `layout-font-weight`: Inconsistent font-weight [skills/taste-skill/scripts/lib/rules.mjs:160]().
    *   `layout-font-family`: Inconsistent font-family [skills/taste-skill/scripts/lib/rules.mjs:161]().
    *   `layout-color`: Inconsistent color usage [skills/taste-skill/scripts/lib/rules.mjs:162]().
    *   `layout-background-color`: Inconsistent background-color usage [skills/taste-skill/scripts/lib/rules.mjs:163]().
    *   `layout-border-color`: Inconsistent border-color usage [skills/taste-skill/scripts/lib/rules.mjs:164]().
    *   `layout-outline-color`: Inconsistent outline-color usage [skills/taste-skill/scripts/lib/rules.mjs:165]().
    *   `layout-box-shadow`: Inconsistent box-shadow usage [skills/taste-skill/scripts/lib/rules.mjs:166]().
    *   `layout-text-shadow`: Inconsistent text-shadow usage [skills/taste-skill/scripts/lib/rules.mjs:167]().
    *   `layout-filter`: Inconsistent filter usage [skills/taste-skill/scripts/lib/rules.mjs:168]().
    *   `layout-backdrop-filter`: Inconsistent backdrop-filter usage [skills/taste-skill/scripts/lib/rules.mjs:169]().
    *   `layout-mask`: Inconsistent mask usage [skills/taste-skill/scripts/lib/rules.mjs:170]().
    *   `layout-clip-path`: Inconsistent clip-path usage [skills/taste-skill/scripts/lib/rules.mjs:171]().
    *   `layout-shape-outside`: Inconsistent shape-outside usage [skills/taste-skill/scripts/lib/rules.mjs:172]().
    *   `layout-object-fit`: Inconsistent object-fit usage [skills/taste-skill/scripts/lib/rules.mjs:173]().
    *   `layout-object-position`: Inconsistent object-position usage [skills/taste-skill/scripts/lib/rules.mjs:174]().
    *   `layout-image-rendering`: Inconsistent image-rendering [skills/taste-skill/scripts/lib/rules.mjs:175]().
    *   `layout-fill`: Inconsistent SVG fill [skills/taste-skill/scripts/lib/rules.mjs:176]().
    *   `layout-stroke`: Inconsistent SVG stroke [skills/taste-skill/scripts/lib/rules.mjs:177]().
    *   `layout-stroke-width`: Inconsistent SVG stroke-width [skills/taste-skill/scripts/lib/rules.mjs:178]().
    *   `layout-stroke-linecap`: Inconsistent SVG stroke-linecap [skills/taste-skill/scripts/lib/rules.mjs:179]().
    *   `layout-stroke-linejoin`: Inconsistent SVG stroke-linejoin [skills/taste-skill/scripts/lib/rules.mjs:180]().
    *   `layout-stroke-dasharray`: Inconsistent SVG stroke-dasharray [skills/taste-skill/scripts/lib/rules.mjs:181]().
    *   `layout-stroke-dashoffset`: Inconsistent SVG stroke-dashoffset [skills/taste-skill/scripts/lib/rules.mjs:182]().
    *   `layout-marker`: Inconsistent SVG marker [skills/taste-skill/scripts/lib/rules.mjs:183]().
    *   `layout-vector-effect`: Inconsistent SVG vector-effect [skills/taste-skill/scripts/lib/rules.mjs:184]().
    *   `layout-paint-order`: Inconsistent SVG paint-order [skills/taste-skill/scripts/lib/rules.mjs:185]().
    *   `layout-dominant-baseline`: Inconsistent SVG dominant-baseline [skills/taste-skill/scripts/lib/rules.mjs:186]().
    *   `layout-alignment-baseline`: Inconsistent SVG alignment-baseline [skills/taste-skill/scripts/lib/rules.mjs:187]().
    *   `layout-baseline-shift`: Inconsistent SVG baseline-shift [skills/taste-skill/scripts/lib/rules.mjs:188]().
    *   `layout-text-anchor`: Inconsistent SVG text-anchor [skills/taste-skill/scripts/lib/rules.mjs:189]().
    *   `layout-writing-mode-svg`: Inconsistent SVG writing-mode [skills/taste-skill/scripts/lib/rules.mjs:190]().
    *   `layout-glyph-orientation-vertical`: Inconsistent SVG glyph-orientation-vertical [skills/taste-skill/scripts/lib/rules.mjs:191]().
    *   `layout-glyph-orientation-horizontal`: Inconsistent SVG glyph-orientation-horizontal [skills/taste-skill/scripts/lib/rules.mjs:192]().
    *   `layout-direction-svg`: Inconsistent SVG direction [skills/taste-skill/scripts/lib/rules.mjs:193]().
    *   `layout-unicode-bidi`: Inconsistent SVG unicode-bidi [skills/taste-skill/scripts/lib/rules.mjs:194]().
    *   `layout-shape-rendering`: Inconsistent SVG shape-rendering [skills/taste-skill/scripts/lib/rules.mjs:195]().
    *   `layout-text-rendering-svg`: Inconsistent SVG text-rendering [skills/taste-skill/scripts/lib/rules.mjs:196]().
    *   `layout-color-interpolation`: Inconsistent SVG color-interpolation [skills/taste-skill/scripts/lib/rules.mjs:197]().
    *   `layout-color-interpolation-filters`: Inconsistent SVG color-interpolation-filters [skills/taste-skill/scripts/lib/rules.mjs:198]().
    *   `layout-flood-color`: Inconsistent SVG flood-color [skills/taste-skill/scripts/lib/rules.mjs:199]().
    *   `layout-flood-opacity`: Inconsistent SVG flood-opacity [skills/taste-skill/scripts/lib/rules.mjs:200]().
    *   `layout-lighting-color`: Inconsistent SVG lighting-color [skills/taste-skill/scripts/lib/rules.mjs:201]().
    *   `layout-stop-color`: Inconsistent SVG stop-color [skills/taste-skill/scripts/lib/rules.mjs:202]().
    *   `layout-stop-opacity`: Inconsistent SVG stop-opacity [skills/taste-skill/scripts/lib/rules.mjs:203]().
    *   `layout-enable-background`: Inconsistent SVG enable-background [skills/taste-skill/scripts/lib/rules.mjs:204]().
    *   `layout-clip-rule`: Inconsistent SVG clip-rule [skills/taste-skill/scripts/lib/rules.mjs:205]().
    *   `layout-fill-rule`: Inconsistent SVG fill-rule [skills/taste-skill/scripts/lib/rules.mjs:206]().
    *   `layout-mask-type`: Inconsistent SVG mask-type [skills/taste-skill/scripts/lib/rules.mjs:207]().
    *   `layout-pointer-events-svg`: Inconsistent SVG pointer-events [skills/taste-skill/scripts/lib/rules.mjs:208]().
    *   `layout-shape-image-threshold`: Inconsistent SVG shape-image-threshold [skills/taste-skill/scripts/lib/rules.mjs:209]().
    *   `layout-text-decoration-line`: Inconsistent SVG text-decoration-line [skills/taste-skill/scripts/lib/rules.mjs:210]().
    *   `layout-text-decoration-style`: Inconsistent SVG text-decoration-style [skills/taste-skill/scripts/lib/rules.mjs:211]().
    *   `layout-text-decoration-color`: Inconsistent SVG text-decoration-color [skills/taste-skill/scripts/lib/rules.mjs:212]().
    *   `layout-text-underline-position`: Inconsistent SVG text-underline-position [skills/taste-skill/scripts/lib/rules.mjs:213]().
    *   `layout-text-emphasis-style`: Inconsistent SVG text-emphasis-style [skills/taste-skill/scripts/lib/rules/rules.mjs:214]().
    *   `layout-text-emphasis-color`: Inconsistent SVG text-emphasis-color [skills/taste-skill/scripts/lib/rules.mjs:215]().
    *   `layout-text-emphasis-position`: Inconsistent SVG text-emphasis-position [skills/taste-skill/scripts/lib/rules.mjs:216]().
    *   `layout-text-combine-upright`: Inconsistent SVG text-combine-upright [skills/taste-skill/scripts/lib/rules.mjs:217]().
    *   `layout-text-orientation-svg`: Inconsistent SVG text-orientation [skills/taste-skill/scripts/lib/rules.mjs:218]().
    *   `layout-dominant-baseline-svg`: Inconsistent SVG dominant-baseline [skills/taste-skill/scripts/lib/rules.mjs:219]().
    *   `layout-alignment-baseline-svg`: Inconsistent SVG alignment-baseline [skills/taste-skill/scripts/lib/rules.mjs:220]().
    *   `layout-baseline-shift-svg`: Inconsistent SVG baseline-shift [skills/taste-skill/scripts/lib/rules.mjs:221]().
    *   `layout-text-anchor-svg`: Inconsistent SVG text-anchor [skills/taste-skill/scripts/lib/rules.mjs:222]().
    *   `layout-word-spacing-svg`: Inconsistent SVG word-spacing [skills/taste-skill/scripts/lib/rules.mjs:223]().
    *   `layout-letter-spacing-svg`: Inconsistent SVG letter-spacing [skills/taste-skill/scripts/lib/rules.mjs:224]().
    *   `layout-font-size-svg`: Inconsistent SVG font-size [skills/taste-skill/scripts/lib/rules.mjs:225]().
    *   `layout-font-family-svg`: Inconsistent SVG font-family [skills/taste-skill/scripts/lib/rules.mjs:226]().
    *   `layout-font-weight-svg`: Inconsistent SVG font-weight [skills/taste-skill/scripts/lib/rules.mjs:227]().
    *   `layout-font-style-svg`: Inconsistent SVG font-style [skills/taste-skill/scripts/lib/rules.mjs:228]().
    *   `layout-font-variant-svg`: Inconsistent SVG font-variant [skills/taste-skill/scripts/lib/rules.mjs:229]().
    *   `layout-font-stretch-svg`: Inconsistent SVG font-stretch [skills/taste-skill/scripts/lib/rules.mjs:230]().
    *   `layout-font-feature-settings-svg`: Inconsistent SVG font-feature-settings [skills/taste-skill/scripts/lib/rules.mjs:231]().
    *   `layout-font-kerning-svg`: Inconsistent SVG font-kerning [skills/taste-skill/scripts/lib/rules.mjs:232]().
    *   `layout-text-rendering-svg`: Inconsistent SVG text-rendering [skills/taste-skill/scripts/lib/rules.mjs:233]().
    *   `layout-color-svg`: Inconsistent SVG color [skills/taste-skill/scripts/lib/rules.mjs:234]().
    *   `layout-fill-svg`: Inconsistent SVG fill [skills/taste-skill/scripts/lib/rules.mjs:235]().
    *   `layout-stroke-svg`: Inconsistent SVG stroke [skills/taste-skill/scripts/lib/rules.mjs:236]().
    *   `layout-stroke-width-svg`: Inconsistent SVG stroke-width [skills/taste-skill/scripts/lib/rules.mjs:237]().
    *   `layout-stroke-linecap-svg`: Inconsistent SVG stroke-linecap [skills/taste-skill/scripts/lib/rules.mjs:238]().
    *   `layout-stroke-linejoin-svg`: Inconsistent SVG stroke-linejoin [skills/taste-skill/scripts/lib/rules.mjs:239]().
    *   `layout-stroke-dasharray-svg`: Inconsistent SVG stroke-dasharray [skills/taste-skill/scripts/lib/rules.mjs:240]().
    *   `layout-stroke-dashoffset-svg`: Inconsistent SVG stroke-dashoffset [skills/taste-skill/scripts/lib/rules.mjs:241]().
    *   `layout-marker-svg`: Inconsistent SVG marker [skills/taste-skill/scripts/lib/rules.mjs:242]().
    *   `layout-vector-effect-svg`: Inconsistent SVG vector-effect [skills/taste-skill/scripts/lib/rules.mjs:243]().
    *   `layout-paint-order-svg`: Inconsistent SVG paint-order [skills/taste-skill/scripts/lib/rules.mjs:243]().

*   **`WARN`**: Indicates something that is "usually wrong" and should only be kept with a strong design justification [skills/taste-skill/scripts/lib/rules.mjs:3]().
    *   `statement-length`: Large-set statements running past a certain number of lines [skills/taste-skill/scripts/lib/rules.mjs:41]().
    *   `hero-words`: Hero headline exceeding a typical word count [skills/taste-skill/scripts/lib/rules.mjs:46]().
    *   `mixed-font-headline`: Headlines switching typeface or to italic mid-line [skills/taste-skill/scripts/lib/rules.mjs:47]().
    *   `micro-label`: A small number of tiny uppercase letter-spaced labels [skills/taste-skill/scripts/lib/rules.mjs:63]().
    *   `hairline`: A small number of thin rules/divider lines [skills/taste-skill/scripts/lib/rules.mjs:73]().
    *   `outlined-box`: A small number of boxes drawn with a 1px outline [skills/taste-skill/scripts/lib/rules.mjs:75]().
    *   `dashed`: Dashed/dotted borders [skills/taste-skill/scripts/lib/rules.mjs:76]().
    *   `glass`: Multiple backdrop-blur surfaces (glassmorphism) [skills/taste-skill/scripts/lib/rules.mjs:77]().

The `rules.mjs` module also includes helper functions like `colourFamily()` to identify specific color ranges associated with "AI tells" [skills/taste-skill/scripts/lib/rules.mjs:8-15]().

The `judgeLayout()` and `judgeApp()` functions are specialized rule evaluators for layout and app-specific metrics, respectively. `APP_SKIP` is a list of rule IDs that are exempted when evaluating app screens, as app designs often have different conventions than marketing pages. `RULE_IDS` is a comprehensive list of all defined rule identifiers.

```mermaid
graph TD
    A[Measurement Object (from probe.mjs)] --> B{judge(m, options)};

    subgraph "Rule Evaluation (rules.mjs)"
        B --> C{Headline Rules};
        B --> D{Banned Furniture Rules};
        B --> E{Surface Rules};
        B --> F{Colour Rules};
        B --> G{Layout Rules (judgeLayout)};
        B --> H{App Rules (judgeApp)};
    end

    C --> C1[headline-lines FAIL];
    C --> C2[statement-length WARN];
    C --> C3[hero-words WARN];
    C --> C4[mixed-font-headline WARN];

    D --> D1[eyebrow FAIL];
    D --> D2[mono FAIL];
    D --> D3[numbering FAIL];
    D --> D4[micro-label FAIL/WARN];
    D --> D5[emoji FAIL];

    E --> E1[gradient FAIL];
    E --> E2[gradient-text FAIL];
    E --> E3[shadow FAIL];
    E --> E4[text-shadow FAIL];
    E --> E5[button-fx FAIL];
    E --> E6[hairline FAIL/WARN];
    E --> E7[outlined-box FAIL/WARN];
    E --> E8[dashed WARN];
    E --> E9[glass WARN];

    F --> F1[ai-purple FAIL];
    F --> F2[cream FAIL];
    F --> F3[terracotta FAIL];

    G --> G1[layout-* FAIL/WARN];
    H --> H1[app-* FAIL/WARN];

    B --> I[Array of Finding Objects];
    I --> J[Gate Phase Output];
```
**Diagram: `rules.mjs` Judgment Flow**

Sources:
*   [skills/taste-skill/scripts/lib/rules.mjs:1-3]()
*   [skills/taste-skill/scripts/lib/rules.mjs:8-15]()
*   [skills/taste-skill/scripts/lib/rules.mjs:24]()
*   [skills/taste-skill/scripts/lib/rules.mjs:37]()
*   [skills/taste-skill/scripts/lib/rules.mjs:41]()
*   [skills/taste-skill/scripts/lib/rules.mjs:46]()
*   [skills/taste-skill/scripts/lib/rules.mjs:47]()
*   [skills/taste-skill/scripts/lib/rules.mjs:50]()
*   [skills/taste-skill/scripts/lib/rules.mjs:54]()
*   [skills/taste-skill/scripts/lib/rules.mjs:58]()
*   [skills/taste-skill/scripts/lib/rules.mjs:62]()
*   [skills/taste-skill/scripts/lib/rules.mjs:63]()
*   [skills/taste-skill/scripts/lib/rules.mjs:64]()
*   [skills/taste-skill/scripts/lib/rules.mjs:68]()
*   [skills/taste-skill/scripts/lib/rules.mjs:69]()
*   [skills/taste-skill/scripts/lib/rules.mjs:70]()
*   [skills/taste-skill/scripts/lib/rules.mjs:71]()
*   [skills/taste-skill/scripts/lib/rules.mjs:72]()
*   [skills/taste-skill/scripts/lib/rules.mjs:73]()
*   [skills/taste-skill/scripts/lib/rules.mjs:74]()
*   [skills/taste-skill/scripts/lib/rules.mjs:75]()
*   [skills/taste-skill/scripts/lib/rules.mjs:76]()
*   [skills/taste-skill/scripts/lib/rules.mjs:77]()
*   [skills/taste-skill/scripts/lib/rules.mjs:100-243]()

---

