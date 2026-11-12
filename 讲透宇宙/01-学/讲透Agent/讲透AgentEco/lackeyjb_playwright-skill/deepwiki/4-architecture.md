<!-- source: DeepWiki mcp.deepwiki.com · repo lackeyjb/playwright-skill · page 4 Architecture · fetched 2026-10-27 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/playwright-skill/run.js](skills/playwright-skill/run.js)

</details>



## Purpose and Scope

This document provides a technical overview of the playwright-skill architecture, explaining how components interact to enable Claude to autonomously write and execute browser automation code. It covers the overall system design, component relationships, execution flow, and module resolution strategy.

For detailed information about specific components, see:
- System components reference: [System Components](#4.1)
- run.js implementation details: [run.js: The Universal Executor](#4.2)
- Helper functions API: [Helper Functions Library](#4.3)
- SKILL.md structure: [SKILL.md: Instructions for Claude](#4.4)
- Artifact storage patterns: [Artifact Management](#4.5)
- Path resolution mechanics: [Path Resolution and $SKILL_DIR](#4.6)

For installation and distribution patterns, see [Distribution Model](#3.2).

---

## High-Level Component Architecture

The playwright-skill system consists of several layers that work together to enable autonomous browser automation through Claude Code.

### Component Overview Diagram

```mermaid
graph TB
    subgraph "Plugin Metadata Layer"
        PLUGIN_JSON["plugin.json<br/>.claude-plugin/plugin.json"]
        MARKET_JSON["marketplace.json<br/>.claude-plugin/marketplace.json"]
    end
    
    subgraph "Documentation Layer"
        SKILL_MD["SKILL.md<br/>skills/playwright-skill/SKILL.md<br/>314 lines"]
        API_REF["API_REFERENCE.md<br/>630 lines"]
        README["README.md"]
    end
    
    subgraph "Execution Layer"
        RUN_JS["run.js<br/>skills/playwright-skill/run.js<br/>Universal executor"]
        HELPERS_JS["helpers.js<br/>skills/playwright-skill/lib/helpers.js<br/>Utility functions"]
    end
    
    subgraph "Configuration Layer"
        PKG_JSON["package.json<br/>skills/playwright-skill/package.json<br/>Dependencies"]
        NODE_MODULES["node_modules/<br/>Playwright ^1.48.0"]
    end
    
    subgraph "Runtime Dependencies"
        PLAYWRIGHT["playwright module<br/>Browser control API"]
        CHROMIUM["Chromium binary<br/>Default browser engine"]
    end
    
    subgraph "Artifact Storage"
        TMP_SCRIPTS["/tmp/playwright-test-*.js<br/>User-generated scripts"]
        TEMP_EXEC["/tmp/.temp-execution-*.js<br/>Wrapped execution files"]
        SCREENSHOTS["/tmp/*.png<br/>Screenshot artifacts"]
    end
    
    PLUGIN_JSON -.->|"references"| SKILL_MD
    SKILL_MD -.->|"references for complex tasks"| API_REF
    
    RUN_JS -->|"requires"| PKG_JSON
    RUN_JS -->|"imports"| HELPERS_JS
    RUN_JS -->|"reads from"| TMP_SCRIPTS
    RUN_JS -->|"writes to"| TEMP_EXEC
    
    PKG_JSON -->|"npm install"| NODE_MODULES
    NODE_MODULES -->|"contains"| PLAYWRIGHT
    NODE_MODULES -->|"contains"| CHROMIUM
    
    HELPERS_JS -->|"uses"| PLAYWRIGHT
    PLAYWRIGHT -->|"saves to"| SCREENSHOTS
```

**Sources:** [README.md:166-184](), [skills/playwright-skill/run.js:1-209]()

### Core Components

| Component | Location | Purpose | Key Functions |
|-----------|----------|---------|---------------|
| `run.js` | `skills/playwright-skill/run.js` | Universal executor that handles module resolution and code execution | `checkPlaywrightInstalled()`, `installPlaywright()`, `getCodeToExecute()`, `wrapCodeIfNeeded()`, `cleanupOldTempFiles()` |
| `lib/helpers.js` | `skills/playwright-skill/lib/helpers.js` | Reusable automation patterns | `detectDevServers()`, `safeClick()`, `safeType()`, `takeScreenshot()`, `authenticate()`, `handleCookieBanner()`, `extractTableData()` |
| `SKILL.md` | `skills/playwright-skill/SKILL.md` | Instructions Claude reads for task execution | N/A (documentation) |
| `API_REFERENCE.md` | `API_REFERENCE.md` | Comprehensive Playwright API documentation | N/A (documentation) |
| `package.json` | `skills/playwright-skill/package.json` | Dependency manifest and setup scripts | N/A (configuration) |
| `plugin.json` | `.claude-plugin/plugin.json` | Plugin metadata for Claude Code | N/A (metadata) |
| `marketplace.json` | `.claude-plugin/marketplace.json` | Marketplace listing configuration | N/A (metadata) |

**Sources:** [README.md:166-184](), [skills/playwright-skill/run.js:1-11]()

---

## Execution Flow Architecture

The system follows a specific execution pipeline from Claude invocation to browser automation completion.

### End-to-End Execution Sequence

```mermaid
sequenceDiagram
    participant Claude as "Claude Model"
    participant SKILL_MD as "SKILL.md"
    participant detectDevServers as "helpers.detectDevServers()"
    participant TmpScript as "/tmp/playwright-test-*.js"
    participant run_js as "run.js main()"
    participant checkPlaywright as "run.js checkPlaywrightInstalled()"
    participant getCode as "run.js getCodeToExecute()"
    participant wrapCode as "run.js wrapCodeIfNeeded()"
    participant TempExec as "/tmp/.temp-execution-*.js"
    participant Playwright as "playwright library"
    participant Browser as "Chromium browser"
    
    Claude->>SKILL_MD: "Read instructions"
    SKILL_MD-->>Claude: "Workflow and examples"
    
    Claude->>detectDevServers: "node -e require('./lib/helpers').detectDevServers()"
    detectDevServers-->>Claude: "[{url, port}]"
    
    Claude->>Claude: "Generate custom Playwright code"
    Claude->>TmpScript: "Write script with TARGET_URL param"
    
    Claude->>run_js: "cd $SKILL_DIR && node run.js /tmp/playwright-test-*.js"
    activate run_js
    
    run_js->>checkPlaywright: "Call checkPlaywrightInstalled()"
    checkPlaywright-->>run_js: "true/false"
    
    alt "Playwright not installed"
        run_js->>run_js: "installPlaywright()"
        run_js->>run_js: "npm install && npx playwright install chromium"
    end
    
    run_js->>getCode: "Call getCodeToExecute()"
    getCode->>TmpScript: "Read file"
    getCode-->>run_js: "Raw code string"
    
    run_js->>wrapCode: "Call wrapCodeIfNeeded(code)"
    wrapCode-->>run_js: "Wrapped code with require() and async IIFE"
    
    run_js->>TempExec: "Write wrapped code"
    run_js->>TempExec: "require(.temp-execution-*.js)"
    
    TempExec->>Playwright: "require('playwright')"
    Playwright->>Browser: "chromium.launch({headless: false})"
    Browser->>Browser: "Execute automation"
    Browser-->>Playwright: "Results"
    Playwright-->>run_js: "Console output"
    
    deactivate run_js
    
    run_js-->>Claude: "Execution results"
    Claude-->>Claude: "Parse output and screenshots"
```

**Sources:** [skills/playwright-skill/run.js:162-208](), [skills/playwright-skill/run.js:23-30](), [skills/playwright-skill/run.js:35-47](), [skills/playwright-skill/run.js:52-81](), [skills/playwright-skill/run.js:109-157]()

### Key Execution Steps

1. **Skill Discovery**: Claude identifies browser automation need and loads `SKILL.md`
2. **Dev Server Detection**: Claude executes `detectDevServers()` via `node -e` command
3. **Code Generation**: Claude writes custom Playwright code with URL parameterization
4. **Artifact Creation**: Script written to `/tmp/playwright-test-*.js` to keep projects clean
5. **Execution Invocation**: Claude runs `cd $SKILL_DIR && node run.js /tmp/playwright-test-*.js`
6. **Module Resolution**: `run.js` changes directory to `__dirname` [skills/playwright-skill/run.js:18]()
7. **Dependency Check**: `checkPlaywrightInstalled()` verifies Playwright availability [skills/playwright-skill/run.js:23-30]()
8. **Code Loading**: `getCodeToExecute()` reads script from file path argument [skills/playwright-skill/run.js:52-81]()
9. **Code Wrapping**: `wrapCodeIfNeeded()` adds `require()` statements and async IIFE [skills/playwright-skill/run.js:109-157]()
10. **Temporary File Creation**: Wrapped code written to `.temp-execution-*.js` [skills/playwright-skill/run.js:181-185]()
11. **Execution**: `require(tempFile)` loads and executes the wrapped code [skills/playwright-skill/run.js:189]()
12. **Browser Automation**: Playwright controls browser with `headless: false` and `slowMo: 100`
13. **Cleanup**: Old temp files cleaned on next run [skills/playwright-skill/run.js:86-104]()

**Sources:** [skills/playwright-skill/run.js:162-208]()

---

## Module Resolution Strategy

The playwright-skill system uses a specific module resolution strategy to ensure `require('playwright')` and `require('./lib/helpers')` work correctly regardless of where scripts are written.

### Module Resolution Diagram

```mermaid
graph TB
    subgraph "User Script Location"
        UserScript["/tmp/playwright-test-*.js<br/>Generated by Claude<br/>Contains: require('playwright')"]
    end
    
    subgraph "Skill Directory"
        SkillDir["$SKILL_DIR<br/>~/.claude/skills/playwright-skill/<br/>OR ~/.claude/plugins/.../skills/playwright-skill/"]
        RunJS["run.js<br/>process.chdir(__dirname)"]
        NodeModules["node_modules/<br/>playwright installed here"]
        HelpersJS["lib/helpers.js"]
    end
    
    subgraph "Execution Process"
        TempExec[".temp-execution-*.js<br/>Written to $SKILL_DIR<br/>Contains wrapped code"]
        RequireCall["require(tempFile)<br/>Module resolution from CWD"]
    end
    
    subgraph "Module Search Path"
        CWD["process.cwd() = $SKILL_DIR"]
        NodeResolution["Node.js module resolution<br/>Searches from CWD upward"]
    end
    
    UserScript -->|"Passed as argument"| RunJS
    RunJS -->|"Line 18: process.chdir(__dirname)"| CWD
    RunJS -->|"Reads and wraps"| UserScript
    RunJS -->|"Writes to"| TempExec
    RunJS -->|"Executes"| RequireCall
    
    RequireCall -->|"Resolves from"| CWD
    CWD -->|"Finds"| NodeModules
    CWD -->|"Finds"| HelpersJS
    
    NodeModules -.->|"Available to"| TempExec
    HelpersJS -.->|"Available to"| TempExec
```

**Sources:** [skills/playwright-skill/run.js:14-18](), [skills/playwright-skill/run.js:181-189]()

### Why Module Resolution Matters

The challenge: Scripts are generated in `/tmp/` (to keep projects clean), but they need to `require('playwright')` which is installed in the skill directory's `node_modules/`.

The solution: `run.js` implements a three-step resolution strategy:

1. **Change Working Directory**: [skills/playwright-skill/run.js:18]() executes `process.chdir(__dirname)` to ensure the current working directory is the skill directory
2. **Create Temp File Locally**: [skills/playwright-skill/run.js:181]() writes `.temp-execution-*.js` to the skill directory (not `/tmp/`)
3. **Require with Local Resolution**: [skills/playwright-skill/run.js:189]() uses `require(tempFile)` which resolves modules from the current working directory

This allows scripts written to `/tmp/` to be wrapped and executed with proper access to both:
- `require('playwright')` → finds `node_modules/playwright`
- `require('./lib/helpers')` → finds `lib/helpers.js`

**Sources:** [skills/playwright-skill/run.js:14-18](), [skills/playwright-skill/run.js:181-189](), [README.md:200-202]()

---

## Code Wrapping Architecture

The `run.js` executor automatically wraps user code to add required infrastructure.

### Code Transformation Flow

```mermaid
flowchart TB
    Input["User Code Input<br/>await page.goto(url)<br/>await page.screenshot()"]
    
    Check1{"Has require() calls?"}
    Check2{"Has async IIFE wrapper?"}
    
    Template1["Add require() statements<br/>const {chromium} = require('playwright')<br/>const helpers = require('./lib/helpers')"]
    Template2["Add async IIFE wrapper<br/>(async () => { ... })()"]
    Template3["Add error handling<br/>try-catch with stack trace"]
    
    Output["Wrapped Code<br/>Complete executable script"]
    
    Input --> Check1
    Check1 -->|"No"| Template1
    Check1 -->|"Yes"| Check2
    Template1 --> Template2
    Check2 -->|"No"| Template2
    Check2 -->|"Yes"| Output
    Template2 --> Template3
    Template3 --> Output
```

**Sources:** [skills/playwright-skill/run.js:109-157]()

### Wrapping Patterns

The `wrapCodeIfNeeded()` function [skills/playwright-skill/run.js:109-157]() handles three scenarios:

#### Pattern 1: Bare Playwright Commands
```javascript
// Input code
await page.goto('https://example.com');
await page.screenshot({ path: 'screenshot.png' });

// Wrapped output
const { chromium, firefox, webkit, devices } = require('playwright');
const helpers = require('./lib/helpers');

(async () => {
  try {
    await page.goto('https://example.com');
    await page.screenshot({ path: 'screenshot.png' });
  } catch (error) {
    console.error('❌ Automation error:', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
})();
```

**Sources:** [skills/playwright-skill/run.js:120-136]()

#### Pattern 2: Has require() but No Async Wrapper
```javascript
// Input code
const { chromium } = require('playwright');
const browser = await chromium.launch();

// Wrapped output - adds only async IIFE and error handling
(async () => {
  try {
    const { chromium } = require('playwright');
    const browser = await chromium.launch();
  } catch (error) {
    console.error('❌ Automation error:', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
})();
```

**Sources:** [skills/playwright-skill/run.js:139-153]()

#### Pattern 3: Complete Script
```javascript
// Input code - already has require() and async wrapper
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
})();

// Output - returned as-is, no wrapping needed
```

**Sources:** [skills/playwright-skill/run.js:111-117]()

---

## Nested Directory Structure

The repository uses a nested structure to separate plugin concerns from skill implementation.

### Directory Structure Diagram

```mermaid
graph TB
    subgraph "Repository Root: playwright-skill/"
        Root["Repository<br/>github.com/lackeyjb/playwright-skill"]
        
        subgraph "Plugin Metadata: .claude-plugin/"
            PluginJSON["plugin.json<br/>v4.0.2<br/>Plugin definition"]
            MarketJSON["marketplace.json<br/>v1.0.0 entry<br/>v3.1.0 plugin"]
        end
        
        subgraph "Skill Container: skills/"
            SkillsDir["skills/<br/>Container directory"]
            
            subgraph "Skill Implementation: skills/playwright-skill/"
                SkillImpl["playwright-skill/<br/>The actual skill"]
                SKILL_MD_FILE["SKILL.md<br/>314 lines"]
                RUN_JS_FILE["run.js<br/>Universal executor"]
                PKG_JSON_FILE["package.json<br/>v4.0.2"]
                LibDir["lib/<br/>helpers.js"]
            end
        end
        
        API_REF_FILE["API_REFERENCE.md<br/>630 lines<br/>Root level"]
        README_FILE["README.md<br/>User docs"]
    end
    
    subgraph "Plugin Installation Path"
        PluginPath["~/.claude/plugins/marketplaces/playwright-skill/<br/>Preserves full structure"]
        PluginSkillPath["~/.claude/plugins/.../skills/playwright-skill/<br/>Skill execution path"]
    end
    
    subgraph "Standalone Installation Path"
        StandalonePath["~/.claude/skills/playwright-skill/<br/>Extract inner folder only"]
    end
    
    Root --> PluginJSON
    Root --> MarketJSON
    Root --> SkillsDir
    Root --> API_REF_FILE
    Root --> README_FILE
    
    SkillsDir --> SkillImpl
    SkillImpl --> SKILL_MD_FILE
    SkillImpl --> RUN_JS_FILE
    SkillImpl --> PKG_JSON_FILE
    SkillImpl --> LibDir
    
    Root -.->|"Full clone"| PluginPath
    PluginPath --> PluginSkillPath
    
    SkillImpl -.->|"Extract only this folder"| StandalonePath
```

**Sources:** [README.md:22-34](), [README.md:166-184]()

### Rationale for Nested Structure

| Level | Path | Purpose |
|-------|------|---------|
| Repository Root | `playwright-skill/` | Git repository and distribution package |
| Plugin Metadata | `.claude-plugin/` | Plugin system metadata (JSON manifests) |
| Skills Container | `skills/` | Allows plugins to contain multiple skills |
| Skill Implementation | `skills/playwright-skill/` | Actual skill code and documentation |

The nested structure serves two purposes:

1. **Plugin Distribution**: The full structure (including `.claude-plugin/`) is needed for Claude Code's plugin system
2. **Standalone Distribution**: The inner `skills/playwright-skill/` folder can be extracted for direct installation

When installed as a plugin, Claude discovers the skill at:
```
~/.claude/plugins/marketplaces/playwright-skill/skills/playwright-skill/
```

When installed standalone, Claude discovers the skill at:
```
~/.claude/skills/playwright-skill/
```

Both paths contain the same skill implementation, but the plugin path preserves the full repository structure.

**Sources:** [README.md:22-95]()

---

## Dependency Management Architecture

The system manages dependencies through a coordinated setup process.

### Dependency Installation Flow

```mermaid
flowchart LR
    User["User runs npm run setup"]
    
    subgraph "package.json Scripts"
        Setup["setup script<br/>npm install && npm run install-browsers"]
        NpmInstall["npm install<br/>Installs playwright ^1.48.0"]
        InstallBrowsers["install-browsers script<br/>npx playwright install chromium"]
    end
    
    subgraph "Installed Dependencies"
        NodeModules["node_modules/<br/>playwright module"]
        ChromiumBinary["Chromium binary<br/>~/.cache/ms-playwright/"]
    end
    
    subgraph "Runtime Access"
        RunJS["run.js<br/>checkPlaywrightInstalled()"]
        AutoInstall["Auto-install if missing<br/>npm install && npx playwright install chromium"]
    end
    
    User --> Setup
    Setup --> NpmInstall
    Setup --> InstallBrowsers
    
    NpmInstall --> NodeModules
    InstallBrowsers --> ChromiumBinary
    
    NodeModules --> RunJS
    RunJS -.->|"If missing"| AutoInstall
    AutoInstall -.-> NodeModules
    AutoInstall -.-> ChromiumBinary
```

**Sources:** [skills/playwright-skill/run.js:35-47](), [README.md:190-194]()

### Dependency Check Logic

The `checkPlaywrightInstalled()` function [skills/playwright-skill/run.js:23-30]() verifies Playwright availability:

```javascript
function checkPlaywrightInstalled() {
  try {
    require.resolve('playwright');
    return true;
  } catch (e) {
    return false;
  }
}
```

If Playwright is not found, `installPlaywright()` [skills/playwright-skill/run.js:35-47]() automatically installs it:

```javascript
function installPlaywright() {
  console.log('📦 Playwright not found. Installing...');
  try {
    execSync('npm install', { stdio: 'inherit', cwd: __dirname });
    execSync('npx playwright install chromium', { stdio: 'inherit', cwd: __dirname });
    console.log('✅ Playwright installed successfully');
    return true;
  } catch (e) {
    console.error('❌ Failed to install Playwright:', e.message);
    console.error('Please run manually: cd', __dirname, '&& npm run setup');
    return false;
  }
}
```

This ensures the skill works even if the user skips the `npm run setup` step during installation.

**Sources:** [skills/playwright-skill/run.js:23-47](), [skills/playwright-skill/run.js:168-174]()

---

## Artifact Storage Strategy

All generated files and screenshots are stored in `/tmp/` to maintain clean project directories.

### Artifact Flow Diagram

```mermaid
graph LR
    subgraph "Script Generation"
        Claude["Claude generates code"]
        UserScript["/tmp/playwright-test-*.js<br/>User-generated script<br/>Persists across runs"]
    end
    
    subgraph "Execution Artifacts"
        TempExec[".temp-execution-*.js<br/>Wrapped execution file<br/>In $SKILL_DIR<br/>Cleaned on next run"]
        Screenshots["/tmp/*.png<br/>Screenshot files<br/>Timestamped"]
    end
    
    subgraph "Cleanup Strategy"
        NextRun["Next run.js execution"]
        Cleanup["cleanupOldTempFiles()<br/>Deletes .temp-execution-*.js"]
        OSCleanup["OS handles /tmp cleanup<br/>No manual deletion needed"]
    end
    
    Claude --> UserScript
    UserScript --> TempExec
    TempExec --> Screenshots
    
    NextRun --> Cleanup
    Cleanup -.->|"Deletes"| TempExec
    Screenshots --> OSCleanup
```

**Sources:** [skills/playwright-skill/run.js:86-104](), [skills/playwright-skill/run.js:181-192]()

### Storage Locations

| Artifact Type | Location | Lifecycle | Purpose |
|---------------|----------|-----------|---------|
| User Scripts | `/tmp/playwright-test-*.js` | Persists (Claude manages) | Script written by Claude |
| Execution Files | `$SKILL_DIR/.temp-execution-*.js` | Cleaned on next run | Wrapped code with requires |
| Screenshots | `/tmp/*.png` | OS cleanup | Visual artifacts |

The cleanup function [skills/playwright-skill/run.js:86-104]() runs at the start of each execution:

```javascript
function cleanupOldTempFiles() {
  try {
    const files = fs.readdirSync(__dirname);
    const tempFiles = files.filter(f => f.startsWith('.temp-execution-') && f.endsWith('.js'));

    if (tempFiles.length > 0) {
      tempFiles.forEach(file => {
        const filePath = path.join(__dirname, file);
        try {
          fs.unlinkSync(filePath);
        } catch (e) {
          // Ignore errors - file might be in use or already deleted
        }
      });
    }
  } catch (e) {
    // Ignore directory read errors
  }
}
```

This strategy:
- Avoids race conditions with async operations (cleanup happens on *next* run, not during execution)
- Keeps the skill directory clean
- Allows temp files to exist long enough for long-running async operations
- Delegates `/tmp/` cleanup to the operating system

**Sources:** [skills/playwright-skill/run.js:86-104](), [skills/playwright-skill/run.js:165-166](), [skills/playwright-skill/run.js:191-192]()

---

## Progressive Disclosure Pattern

The documentation architecture implements progressive disclosure to minimize Claude's context window usage.

### Documentation Loading Strategy

```mermaid
flowchart TB
    Request["User Request"]
    
    TaskDetect["Claude detects<br/>browser automation need"]
    
    LoadSKILL["Load SKILL.md<br/>314 lines<br/>Concise instructions"]
    
    CheckComplexity{"Complex API<br/>needed?"}
    
    LoadAPI["Load API_REFERENCE.md<br/>630 lines<br/>Comprehensive docs"]
    
    GenerateCode["Generate Playwright code"]
    
    Execute["Execute via run.js"]
    
    Request --> TaskDetect
    TaskDetect --> LoadSKILL
    LoadSKILL --> CheckComplexity
    
    CheckComplexity -->|"Simple task"| GenerateCode
    CheckComplexity -->|"Complex selectors,<br/>network testing,<br/>authentication"| LoadAPI
    
    LoadAPI --> GenerateCode
    GenerateCode --> Execute
```

**Sources:** [README.md:14](), [README.md:187-188]()

### Documentation Hierarchy

| Document | Size | Purpose | When Loaded |
|----------|------|---------|-------------|
| `SKILL.md` | 314 lines | Concise workflow, examples, best practices | Always (first) |
| `API_REFERENCE.md` | 630 lines | Complete Playwright API, advanced patterns | On demand for complex tasks |
| `README.md` | User documentation | Installation, quick start, troubleshooting | Not loaded by Claude |

This pattern ensures:
1. Claude always reads the concise `SKILL.md` first
2. Comprehensive documentation is available when needed
3. Context window is not wasted on unused information
4. Simple tasks complete faster with less context

**Sources:** [README.md:14](), [README.md:166-184](), [README.md:187-188]()

---

