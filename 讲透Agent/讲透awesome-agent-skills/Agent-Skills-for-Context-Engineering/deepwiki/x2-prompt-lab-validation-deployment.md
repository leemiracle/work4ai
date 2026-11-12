<!-- source: DeepWiki mcp.deepwiki.com · repo muratcankoylan/Agent-Skills-for-Context-Engineering · extra page Prompt Lab Validation & Deployment · fetched 2026-10-26 -->

# Prompt Lab Validation & Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/deploy-prompt-lab.yml](.github/workflows/deploy-prompt-lab.yml)
- [examples/long-horizon-prompt-lab/report/PROVENANCE.md](examples/long-horizon-prompt-lab/report/PROVENANCE.md)
- [examples/long-horizon-prompt-lab/report/cdc_prompt.pdf](examples/long-horizon-prompt-lab/report/cdc_prompt.pdf)
- [examples/long-horizon-prompt-lab/report/cdc_prompt.txt](examples/long-horizon-prompt-lab/report/cdc_prompt.txt)
- [examples/long-horizon-prompt-lab/report/cdc_proof.pdf](examples/long-horizon-prompt-lab/report/cdc_proof.pdf)
- [examples/long-horizon-prompt-lab/report/cdc_proof.txt](examples/long-horizon-prompt-lab/report/cdc_proof.txt)
- [examples/long-horizon-prompt-lab/scripts/fetch_report.sh](examples/long-horizon-prompt-lab/scripts/fetch_report.sh)
- [examples/long-horizon-prompt-lab/scripts/install_skill.sh](examples/long-horizon-prompt-lab/scripts/install_skill.sh)
- [examples/long-horizon-prompt-lab/scripts/test_site.mjs](examples/long-horizon-prompt-lab/scripts/test_site.mjs)
- [examples/long-horizon-prompt-lab/scripts/validate_site.py](examples/long-horizon-prompt-lab/scripts/validate_site.py)
- [examples/long-horizon-prompt-lab/scripts/verify_report.py](examples/long-horizon-prompt-lab/scripts/verify_report.py)

</details>



## Purpose and Scope
This document details the validation, end-to-end testing, continuous integration deployment, skill installation, and cryptographic provenance verification systems for the Long-Horizon Prompt Lab (`examples/long-horizon-prompt-lab/`) and the `long-horizon-prompting` skill. It covers static HTML analysis via `validate_site.py`, browser automation testing via `test_site.mjs`, GitHub Pages deployment via `deploy-prompt-lab.yml`, skill distribution via `install_skill.sh`, and provenance tracking via `fetch_report.sh`, `verify_report.py`, and `PROVENANCE.md`.

---

## 1. Static Analysis Gate: `validate_site.py`

The static analysis gate implemented in `examples/long-horizon-prompt-lab/scripts/validate_site.py` performs deterministic validation across all generated HTML pages, assets, navigation trees, and sitemaps in the static site.

### Implementation & Document Parser
The validation engine relies on `DocumentParser`, which inherits from Python's standard `HTMLParser` to collect HTML attributes, IDs, links, assets, script tags, headings, and metadata during a single-pass tokenization of each target file [examples/long-horizon-prompt-lab/scripts/validate_site.py:23-68]():

```python
class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.assets: list[str] = []
        self.scripts: list[str] = []
        self.h1_count = 0
        self.title = ""
        self.meta: dict[str, str] = {}
        self.current_title = False
        self.text_parts: list[str] = []
```

### Validation Rules
`validate()` checks the parsed document structures against strict structural and semantic criteria:
- **Heading & Title Integrity**: Asserts that every page contains exactly one `<h1>` element and a non-empty `<title>` [examples/long-horizon-prompt-lab/scripts/validate_site.py:104-107]().
- **ID Uniqueness**: Detects and reports duplicate element IDs within a document [examples/long-horizon-prompt-lab/scripts/validate_site.py:108-110]().
- **Primary Metadata**: Ensures primary pages (`index.html`, `guide.html`, `lab.html`, `references.html`) include required `description`, `content-security-policy`, `og:title`, `og:url`, and `og:image` meta tags, alongside a valid project-path canonical URL [examples/long-horizon-prompt-lab/scripts/validate_site.py:111-120]().
- **Link Integrity**: Resolves local links and asset paths, reporting broken references [examples/long-horizon-prompt-lab/scripts/validate_site.py:122-125]().
- **Navigation Consistency**: Verifies that every primary page contains complete navigation links to all required targets (`index.html`, `guide.html`, `lab.html`, `references.html`) [examples/long-horizon-prompt-lab/scripts/validate_site.py:127-151]().
- **Script Ordering**: Asserts that `lab.html` loads scripts in the exact sequence `site.js`, `data.js`, `app.js` [examples/long-horizon-prompt-lab/scripts/validate_site.py:152-154]().
- **External Evidence Caveats**: Scans `references.html` for a minimum of 25 external sources and mandatory evidentiary caveats such as `"unreviewed"`, `"no component ablation"`, `"vendor"`, and `"preprint"` [examples/long-horizon-prompt-lab/scripts/validate_site.py:156-170]().
- **Sitemap XML Parsing**: Parses `sitemap.xml` using `xml.etree.ElementTree` to verify location nodes match primary pages [examples/long-horizon-prompt-lab/scripts/validate_site.py:171-176]().

```mermaid
title "Static Analysis Gate Architecture"
graph TD
    A["HTML Files (index.html, guide.html, lab.html, references.html, 404.html)"] --> B["DocumentParser (HTMLParser subclass)"]
    B --> C["validate_site.py Validation Engine"]
    C --> D["H1 & Title Checks"]
    C --> E["ID Uniqueness & Meta Tags"]
    C --> F["Local Link & Asset Resolution"]
    C --> G["Primary Navigation Completeness"]
    C --> H["Script Order (site.js, data.js, app.js)"]
    C --> I["References Count & Evidence Caveats"]
    C --> J["XML Sitemap Validation (sitemap.xml)"]
    D --> K["Error Accumulation & Exit Code"]
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
```
Sources: `examples/long-horizon-prompt-lab/scripts/validate_site.py`

---

## 2. Puppeteer E2E Test Suite: `test_site.mjs`

End-to-end browser validation is executed via `examples/long-horizon-prompt-lab/scripts/test_site.mjs`, utilizing `puppeteer-core` against a temporary static file server instance.

### Execution Flow & Responsiveness
1. **Server Initialization**: Spawns a Python HTTP server (`http.server`) bound to `127.0.0.1` on port `8765`, serving a temporary directory copy of the static site [examples/long-horizon-prompt-lab/scripts/test_site.mjs:42-55]().
2. **Browser Launch**: Resolves the local Chrome/Chromium binary via `findChrome()` and launches Puppeteer in headless mode with sandboxing disabled (`--no-sandbox`, `--disable-dev-shm-usage`) [examples/long-horizon-prompt-lab/scripts/test_site.mjs:14-27, 59-63]().
3. **Responsive Viewport Matrix**: Iterates across viewports of width `320px`, `390px`, `768px`, and `1480px`, loading each page and asserting:
   - HTTP status is `200` or `304` [examples/long-horizon-prompt-lab/scripts/test_site.mjs:74-78]().
   - Exactly one `h1` element and 4 navigation links are present [examples/long-horizon-prompt-lab/scripts/test_site.mjs:79-86]().
   - No horizontal scroll overflow exists (`scrollWidth <= clientWidth + 1`) [examples/long-horizon-prompt-lab/scripts/test_site.mjs:87-90]().
4. **Interactive Component Testing**:
   - Tests copy-to-clipboard buttons (`[data-copy-install]`, `[data-copy-target="brief-template"]`) and verifies status text updates ("Copied") [examples/long-horizon-prompt-lab/scripts/test_site.mjs:93-106]().
   - Validates prompt word counts (`183,836`) and checks for vertical clipping (`scrollHeight <= clientHeight + 1`) in `lab.html` [examples/long-horizon-prompt-lab/scripts/test_site.mjs:108-121]().
   - Tests keyboard tab navigation (`End` key focus movement) [examples/long-horizon-prompt-lab/scripts/test_site.mjs:123-130]().
   - Validates prompt download links and reference card counts (`>= 25`) [examples/long-horizon-prompt-lab/scripts/test_site.mjs:131-141]().
5. **No-JavaScript Fallback Validation**: Disables JavaScript execution on `lab.html` and asserts that all 8 static prompt `.txt` download links remain accessible inside `<noscript>` tags [examples/long-horizon-prompt-lab/scripts/test_site.mjs:142-150]().

```mermaid
title "Puppeteer E2E Testing Pipeline"
graph TD
    A["Temporary Directory Setup"] --> B["Spawn python3 http.server on port 8765"]
    B --> C["Launch Headless Chrome via puppeteer-core"]
    C --> D["Responsive Viewport Loop (320, 390, 768, 1480px)"]
    D --> E["Page Load & HTTP Status Check"]
    E --> F["DOM Metrics Validation (h1, nav, horizontal overflow)"]
    F --> G["Interactive Tests (Clipboard Copy, Keyboard Tabs)"]
    G --> H["Prompt Content & Download Verification"]
    H --> I["Disable JavaScript & Verify <noscript> Fallback"]
    I --> J["Kill Server & Cleanup Temp Directory"]
```
Sources: `examples/long-horizon-prompt-lab/scripts/test_site.mjs`

---

## 3. GitHub Pages CI/CD Pipeline: `deploy-prompt-lab.yml`

The GitHub Actions workflow `.github/workflows/deploy-prompt-lab.yml` automates testing, validation, and deployment of the long-horizon prompt lab to GitHub Pages.

### Workflow Triggers & Concurrency
- **Triggers**: Executes on pushes and pull requests targeting the `main` branch when changes occur in `.github/workflows/deploy-prompt-lab.yml`, `skills/long-horizon-prompting/**`, `researcher/claims/index.jsonl`, or `examples/long-horizon-prompt-lab/**`. Also supports manual dispatch (`workflow_dispatch`) [.github/workflows/deploy-prompt-lab.yml:3-23]().
- **Concurrency**: Groups runs under `github-pages` with `cancel-in-progress: false` to prevent overlapping deployments [.github/workflows/deploy-prompt-lab.yml:25-28]().

### Build & Deploy Jobs
- **`build` Job**: Runs on `ubuntu-latest` with a 10-minute timeout.
  1. Checks out repository with persistence disabled [.github/workflows/deploy-prompt-lab.yml:36-40]().
  2. Sets up Node.js version `22` with npm caching [.github/workflows/deploy-prompt-lab.yml:41-47]().
  3. Installs dependencies via `npm ci` in `examples/long-horizon-prompt-lab` [.github/workflows/deploy-prompt-lab.yml:48-51]().
  4. Runs `npm test` and enforces git clean state checks on generated data files (`data/prompt-pairs.json`, `ui/data.js`, `ui/prompts/`) [.github/workflows/deploy-prompt-lab.yml:52-61]().
  5. Assembles static site into `_site/`, copying UI assets, social cards (`shot-hero.png`), and `.nojekyll` [.github/workflows/deploy-prompt-lab.yml:63-68]().
  6. Uploads the static artifact via `actions/upload-pages-artifact` [.github/workflows/deploy-prompt-lab.yml:70-74]().
- **`deploy` Job**: Triggered only on pushes to `main` (`if: github.ref == 'refs/heads/main'`), dependent on `build`. Configures GitHub Pages and deploys via `actions/deploy-pages` [.github/workflows/deploy-prompt-lab.yml:75-92]().

```mermaid
title "CI/CD Deployment Workflow"
graph TD
    A["Trigger: Push to main / PR / Dispatch"] --> B["Job: build (ubuntu-latest)"]
    B --> C["Checkout Repository"]
    C --> D["Setup Node.js v22 & Cache npm"]
    D --> E["npm ci (Install Tooling)"]
    E --> F["npm test (Validate Site & E2E)"]
    F --> G["Git Diff & Status Cleanliness Check"]
    G --> H["Assemble Static Artifact in _site/"]
    H --> I["Upload Pages Artifact (actions/upload-pages-artifact)"]
    I --> J["Job: deploy (if branch == main)"]
    J --> K["Configure Pages & Deploy to GitHub Pages"]
```
Sources: `.github/workflows/deploy-prompt-lab.yml`

---

## 4. Skill Installation: `install_skill.sh`

The shell script `examples/long-horizon-prompt-lab/scripts/install_skill.sh` provides a reproducible mechanism for installing the `long-horizon-prompting` skill into project-local IDE configurations [examples/long-horizon-prompt-lab/scripts/install_skill.sh:1-6]().

### Execution Steps
1. Resolves repository and target paths [examples/long-horizon-prompt-lab/scripts/install_skill.sh:11-13]().
2. Locates the source skill at `$REPO/skills/long-horizon-prompting` [examples/long-horizon-prompt-lab/scripts/install_skill.sh:15]().
3. Copies the skill directory into `$TARGET/.cursor/skills/long-horizon-prompting`, ensuring clean staging [examples/long-horizon-prompt-lab/scripts/install_skill.sh:23-26]().
4. Prints installed file paths [examples/long-horizon-prompt-lab/scripts/install_skill.sh:28-29]().
5. If the reference CLI `agentskills` is available on `PATH`, executes `agentskills validate "$DEST"` to validate schema conformance; otherwise outputs guidance on installing `skills-ref` [examples/long-horizon-prompt-lab/scripts/install_skill.sh:31-37]().

---

## 5. Artifact Provenance, Fetching & Verification

To maintain strict alignment between the `long-horizon-prompting` skill and its foundational reference case study (OpenAI's Cycle Double Cover Conjecture prompt and proof), the repository includes automated fetching, text extraction, and cryptographic verification scripts [examples/long-horizon-prompt-lab/scripts/fetch_report.sh, examples/long-horizon-prompt-lab/scripts/verify_report.py, examples/long-horizon-prompt-lab/report/PROVENANCE.md]().

### Fetching & Text Extraction: `fetch_report.sh`
Downloads the official PDF reports from OpenAI's CDN, extracts raw text using `pypdf`, and records SHA-256 hashes [examples/long-horizon-prompt-lab/scripts/fetch_report.sh:12-35]():
- `cdc_prompt.pdf`: URL `https://cdn.openai.com/pdf/04d1d1e4-bc75-476a-97cf-49055cd98d31/cdc_prompt.pdf` [examples/long-horizon-prompt-lab/scripts/fetch_report.sh:12]()
- `cdc_proof.pdf`: URL `https://cdn.openai.com/pdf/04d1d1e4-bc75-476a-97cf-49055cd98d31/cdc_proof.pdf` [examples/long-horizon-prompt-lab/scripts/fetch_report.sh:13]()

### Deterministic Provenance Gate: `verify_report.py`
`examples/long-horizon-prompt-lab/scripts/verify_report.py` acts as a deterministic provenance gate. It re-extracts text from `cdc_prompt.pdf` (or `cdc_prompt.txt`), normalizes punctuation and whitespace, parses blockquotes from the skill's annotated reference (`skills/long-horizon-prompting/references/cdc-prompt-annotated.md`), and asserts that every quote fragment appears verbatim in the primary source [examples/long-horizon-prompt-lab/scripts/verify_report.py:29-93](). An exit code of `0` guarantees zero drift between the skill documentation and the published primary artifact.

### Provenance Registry: `PROVENANCE.md`
`examples/long-horizon-prompt-lab/report/PROVENANCE.md` permanently records file sizes, SHA-256 checksums, PDF creation metadata (`pdfTeX-1.40.28`), retrieval dates, and mandatory evidentiary caveats (e.g., absence of independent peer review for the proof, reliance on prompt structure rather than theorem validation) [examples/long-horizon-prompt-lab/report/PROVENANCE.md:1-41]().

```mermaid
title "Artifact Provenance & Verification Pipeline"
graph TD
    A["Official CDN (cdc_prompt.pdf, cdc_proof.pdf)"] --> B["fetch_report.sh (curl download)"]
    B --> C["pypdf Text Extraction (cdc_prompt.txt, cdc_proof.txt)"]
    C --> D["PROVENANCE.md (SHA-256 & Metadata Record)"]
    C --> E["verify_report.py (Provenance Gate)"]
    E --> F["Parse Blockquotes from cdc-prompt-annotated.md"]
    F --> G["Normalize Whitespace & Unicode Punctuation"]
    G --> H["Assert Verbatim Match in Source Prompt Text"]
    H --> I["Exit Code 0: Zero Drift Confirmed"]
```
Sources: `examples/long-horizon-prompt-lab/scripts/fetch_report.sh`, `examples/long-horizon-prompt-lab/scripts/verify_report.py`, `examples/long-horizon-prompt-lab/report/PROVENANCE.md`

---

## Sources
- `.github/workflows/deploy-prompt-lab.yml`
- `examples/long-horizon-prompt-lab/scripts/validate_site.py`
- `examples/long-horizon-prompt-lab/scripts/test_site.mjs`
- `examples/long-horizon-prompt-lab/scripts/install_skill.sh`
- `examples/long-horizon-prompt-lab/scripts/fetch_report.sh`
- `examples/long-horizon-prompt-lab/scripts/verify_report.py`
- `examples/long-horizon-prompt-lab/report/PROVENANCE.md`

---

