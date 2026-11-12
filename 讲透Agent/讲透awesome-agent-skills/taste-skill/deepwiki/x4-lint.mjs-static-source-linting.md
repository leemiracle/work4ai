<!-- source: DeepWiki mcp.deepwiki.com · repo Leonxlnx/taste-skill · extra page lint.mjs: Static Source Linting · fetched 2026-10-26 -->

# lint.mjs: Static Source Linting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/taste-skill/assets/base.css](skills/taste-skill/assets/base.css)
- [skills/taste-skill/evals/evals.json](skills/taste-skill/evals/evals.json)
- [skills/taste-skill/references/critique.md](skills/taste-skill/references/critique.md)
- [skills/taste-skill/references/tells.md](skills/taste-skill/references/tells.md)
- [skills/taste-skill/scripts/lint.mjs](skills/taste-skill/scripts/lint.mjs)

</details>



`lint.mjs` is a critical component of the Gate phase in the `taste-skill` pipeline, responsible for static analysis of source files. Its primary purpose is to identify and flag "tells" – banned patterns, stock phrases, and structural anti-patterns that make a page appear generically generated. This static scanning occurs *before* any rendering, catching issues that might not be visible in a rendered output, such as specific copy habits or motion values. The script can operate in an `--app` mode, which adjusts rule severity for app screens, and integrates with a shared set of rule IDs.

## Operation and Scope

The `lint.mjs` script is executed via the command line, accepting file paths or directories as arguments. It recursively walks through specified directories, identifying relevant source files based on their extensions.

**Command Line Usage:**
```bash
node lint.mjs [files or directories ...] [--app] [--json]
```
- `[files or directories ...]`: Specifies the paths to scan. If no paths are provided, it defaults to the current directory (`.`).
- `--app`: Activates "app mode," which modifies the severity of certain rules to accommodate the design principles of app screens [skills/taste-skill/scripts/lint.mjs:15]().
- `--json`: Outputs findings in JSON format.

The script processes files with extensions such as `.html`, `.htm`, `.css`, `.scss`, `.less`, `.js`, `.jsx`, `.ts`, `.tsx`, `.vue`, `.svelte`, `.astro`, and `.mdx` [skills/taste-skill/scripts/lint.mjs:20](). It skips common build and dependency directories like `node_modules`, `.git`, `dist`, and `.taste-skill` [skills/taste-skill/scripts/lint.mjs:21](). Files larger than 4MB are also skipped to prevent performance issues [skills/taste-skill/scripts/lint.mjs:27]().

If any `FAIL` level findings are detected, the script exits with a status code of `1` [skills/taste-skill/scripts/lint.mjs:7](), indicating a critical violation of the "Taste Standard."

### App Mode

App mode is specifically designed for app screens and dashboards, which have different design constraints compared to marketing pages. When `--app` is enabled, or if the `kind` property in `.taste-skill/direction.json` is set to `'app'`, certain rules are relaxed or their severity is downgraded from `FAIL` to `WARN` [skills/taste-skill/scripts/lint.mjs:15-17](). For example, `hairline`, `outlined-box`, and `default-font` rules are completely disabled (`null`), while `numbering`, `mono`, `shadow`, and `eyebrow` are downgraded to `WARN` [skills/taste-skill/scripts/lint.mjs:17](). This allows for design elements common in app interfaces, such as subtle borders or monospace data labels, without triggering a `FAIL`.

Sources:
- [skills/taste-skill/scripts/lint.mjs:1-34]()

## Data Flow and Key Functions

The `lint.mjs` script follows a straightforward data flow:

```mermaid
graph TD
    A[Start lint.mjs] --> B{Parse Command Line Arguments};
    B --> C{Determine Scan Roots};
    C --> D{Walk File System};
    D --> E{Filter Files by Extension and Size};
    E --> F{Read File Content Line by Line};
    F --> G{Apply Linting Rules};
    G{Apply Linting Rules} --> H{Collect Findings};
    H --> I{Output Findings (JSON or Console)};
    I --> J{Set Exit Code};
    J --> K[End];

    subgraph "File System Traversal"
        D -- "statSync(p)" --> D1[Check if Directory];
        D1 -- "isDirectory()" --> D2{Recurse for Subdirectories};
        D1 -- "isFile()" --> D3{Check Extension and Size};
        D3 -- "EXT.has(extname(p)) && st.size < 4MB" --> E;
        D3 -- "st.size >= 4MB" --> D4[Add to tooBig list];
    end

    subgraph "Linting Process"
        G -- "For each line" --> G1{Iterate through R (Rules)};
        G1 -- "regex.test(line)" --> G2{Match Found?};
        G2 -- "Yes" --> G3{Create Finding Object};
        G3 --> H;
    end
```
**Diagram: `lint.mjs` Data Flow**
Sources:
- [skills/taste-skill/scripts/lint.mjs:8-32]()
- [skills/taste-skill/scripts/lint.mjs:36-61]()

### `walk(p)` Function

The `walk(p)` function is a recursive helper that traverses the file system to find source files [skills/taste-skill/scripts/lint.mjs:24]().
- It takes a path `p` as input.
- It uses `statSync(p)` to determine if `p` is a directory or a file.
- If `p` is a directory, it reads its contents using `readdirSync(p)` and recursively calls `walk()` for each item, skipping directories in the `SKIP` set and hidden files/directories (starting with `.`) [skills/taste-skill/scripts/lint.mjs:25]().
- If `p` is a file, it checks if its extension is in the `EXT` set and if its size is less than 4MB. Valid files are added to the `files` array; oversized files are added to `tooBig` [skills/taste-skill/scripts/lint.mjs:26-27]().

Sources:
- [skills/taste-skill/scripts/lint.mjs:24-28]()

## Linting Rules (`R`)

The core of `lint.mjs` is the `R` array, which defines all the linting rules [skills/taste-skill/scripts/lint.mjs:37](). Each rule is an array with four elements:
1.  **Level**: `'FAIL'` or `'WARN'`. A `FAIL` will cause the script to exit with an error code.
2.  **ID**: A unique identifier for the rule (e.g., `'mono'`, `'gradient'`, `'eyebrow'`).
3.  **Regex**: A regular expression used to scan each line of the source file.
4.  **Message**: A human-readable explanation of the violation and, often, a suggestion for remediation.

These rules are applied line by line to the content of each scanned file. The `APP_LEVEL` object defines how rule severities are adjusted in app mode [skills/taste-skill/scripts/lint.mjs:17]().

### Example Rules and Their Rationale

The rules are derived from the "Tells" documented in `references/tells.md` and the "Critique" guidelines in `references/critique.md`. They aim to enforce the "Taste Standard" by banning common AI-generated patterns and promoting thoughtful design.

| Rule ID | Level (Default) | Regex Example | Rationale (from `lint.mjs` message) | Related Tell/Critique |
| :------ | :-------------- | :------------ | :---------------------------------- | :-------------------- |
| `mono` | `FAIL` | `/\bfont-mono\b|.../i` | Monospace type. Only literal code may be monospace. | `references/tells.md` "Monospace micro-labels, mono as a 'technical' voice, mono captions" |
| `gradient` | `FAIL` | `/(linear|radial|conic)-gradient\(|.../` | Gradient fill. Use a flat colour or a real image. | `references/tells.md` "Violet / indigo gradients on hero, buttons and glows" |
| `shadow` | `FAIL` | `/box-shadow\s*:\s*(?!none|...)/` | Shadow. Elements at rest carry none; only real overlays may. | `references/tells.md` "Soft grey drop shadow under every card" |
| `numbering` | `FAIL` | `/>\s*[(\[]?0[1-9][)\]]?\.?\s*</i` | Decorative index numbering (01 / 02 / 03). | `references/tells.md` "Index numbering: 01 / 02 / 03" |
| `eyebrow` | `FAIL` | `/\b(eyebrow|kicker|overline|...)\b/i` | Eyebrow / kicker label above a heading. | `references/tells.md` "Eyebrow / kicker: tiny tracked uppercase label above every heading" |
| `purple` | `FAIL` | `/\b(bg|text|from|to|via|border|...)-(purple|violet|indigo|fuchsia)-\d{2,3}\b|.../i` | Indigo / violet — the generated-page accent. | `references/tells.md` "Violet / indigo gradients" |
| `lorem` | `FAIL` | `/lorem ipsum|dolor sit amet/i` | Placeholder copy shipped. | `references/tells.md` "lorem ipsum" |
| `hairline` | `FAIL` | `/<hr\b|\bdivide-[xy](-\d|\b)|.../` | Thin rule / divider line. Separate with space, tone or scale. | `references/tells.md` "Thin rules: hairline dividers" |
| `copy` | `WARN` | `/\b(unlock|unleash|supercharge|...)\b/i` | Stock marketing phrase. Say the specific thing the product does. | `references/tells.md` "Copy tells" |
| `default-font` | `WARN` | `/family=(Inter|Poppins|Montserrat|...)\b|.../` | A default typeface. Use the faces named by the drawn direction. | `references/tells.md` "The same typeface on every generated page" |
| `h-screen` | `WARN` | `/\bh-screen\b|height\s*:\s*100vh/` | 100vh jumps on mobile. Use 100svh / 100dvh. | `references/critique.md` "Phone" (implied mobile responsiveness) |

Sources:
- [skills/taste-skill/scripts/lint.mjs:37-61]()
- [skills/taste-skill/references/tells.md]()
- [skills/taste-skill/references/critique.md]()

## Integration with the Shared Rule IDs

The rule IDs used in `lint.mjs` (e.g., `mono`, `gradient`, `eyebrow`) are consistent with the "Tells" documented in `references/tells.md`. This ensures a unified understanding of what constitutes a "tell" across the `taste-skill` codebase and its documentation. The `evals/evals.json` also references these rules, for example, in the `expected_output` field for evaluation prompts, explicitly stating that generated pages should avoid "no monospace, no index numbering, no thin rules, no gradients or shadows" [skills/taste-skill/evals/evals.json:9]().

This consistency allows for clear communication between the automated linting process and human review, as described in `references/critique.md`, which guides the judgment of rendered pages.

Sources:
- [skills/taste-skill/scripts/lint.mjs:37-61]()
- [skills/taste-skill/references/tells.md]()
- [skills/taste-skill/evals/evals.json:9]()

---

