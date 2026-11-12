<!-- source: DeepWiki mcp.deepwiki.com · repo lackeyjb/playwright-skill · page 8 Development and Contributing · fetched 2026-10-26 -->

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)

</details>



## Purpose and Scope

This page provides an overview of the development environment, architecture, and contribution process for the playwright-skill codebase. It covers the technical setup required to develop and extend the skill, key architectural patterns developers should understand, and the workflow for contributing changes.

For specific details on:
- Contributing guidelines and pull request process, see [Contributing Guidelines](#8.1)
- Repository organization and file structure, see [Project Structure](#8.2)
- Local development and testing procedures, see [Development Workflow](#8.3)
- Adding new helper functions and updating documentation, see [Extending the Skill](#8.4)

## Development Environment Overview

The playwright-skill repository uses a **nested plugin structure** that affects the development workflow. The repository root contains plugin metadata in [.claude-plugin/](), while the actual skill implementation resides in [skills/playwright-skill/](). This structure enables dual distribution as both a Claude Code Plugin and a standalone skill.

**Key Development Directories:**

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `.claude-plugin/` | Plugin metadata for distribution | `plugin.json`, `marketplace.json` |
| `skills/playwright-skill/` | Actual skill implementation | `SKILL.md`, `run.js`, `package.json` |
| `skills/playwright-skill/lib/` | Helper function library | `helpers.js` |
| Root directory | Repository-level documentation | `README.md`, `CONTRIBUTING.md`, `API_REFERENCE.md` |

**Development Dependencies:**

The skill requires Node.js >=14.0.0 and Playwright ^1.48.0. The [package.json:7-15]() defines these dependencies and provides setup scripts:

- `npm run setup` - Installs Playwright and Chromium browser
- `npm run install-all-browsers` - Installs Firefox and WebKit in addition to Chromium

Sources: [README.md:166-184](), [CONTRIBUTING.md:99-110]()

## Developer Architecture Overview

```mermaid
graph TB
    subgraph "Repository Root"
        CLONE["git clone<br/>lackeyjb/playwright-skill"]
        FORK["Fork & Branch<br/>feature/your-feature"]
    end
    
    subgraph "Development Files"
        SKILL_MD["skills/playwright-skill/SKILL.md<br/>Claude instructions<br/>~314 lines"]
        RUN_JS["skills/playwright-skill/run.js<br/>Universal executor<br/>Module resolution"]
        HELPERS["skills/playwright-skill/lib/helpers.js<br/>Utility functions<br/>detectDevServers, safeClick, etc."]
        PKG_JSON["skills/playwright-skill/package.json<br/>Dependencies & scripts"]
    end
    
    subgraph "Distribution Files"
        PLUGIN_JSON[".claude-plugin/plugin.json<br/>Plugin metadata<br/>v4.0.2"]
        MARKET_JSON[".claude-plugin/marketplace.json<br/>Marketplace listing<br/>entry v1.0.0, plugin v3.1.0"]
    end
    
    subgraph "Documentation Files"
        README["README.md<br/>User documentation"]
        API_REF["API_REFERENCE.md<br/>Playwright API reference<br/>630 lines"]
        CONTRIB["CONTRIBUTING.md<br/>Contribution guidelines"]
    end
    
    subgraph "Testing & Validation"
        LOCAL_TEST["Local Testing<br/>npm run setup<br/>Test with Claude"]
        FRESH_INSTALL["Fresh Install Test<br/>Verify nested structure"]
        EXAMPLE_TEST["Verify SKILL.md examples"]
    end
    
    CLONE --> FORK
    FORK --> SKILL_MD
    FORK --> RUN_JS
    FORK --> HELPERS
    FORK --> PKG_JSON
    FORK --> PLUGIN_JSON
    FORK --> MARKET_JSON
    FORK --> README
    FORK --> API_REF
    FORK --> CONTRIB
    
    SKILL_MD --> LOCAL_TEST
    RUN_JS --> LOCAL_TEST
    HELPERS --> LOCAL_TEST
    PKG_JSON --> LOCAL_TEST
    
    LOCAL_TEST --> FRESH_INSTALL
    FRESH_INSTALL --> EXAMPLE_TEST
    
    EXAMPLE_TEST --> PR["Pull Request<br/>Clear description<br/>Test results"]
```

**Developer Architecture: Fork to Pull Request**

This diagram shows the complete development lifecycle from forking the repository to submitting a pull request. Developers work with five categories of files: development files (the core skill implementation), distribution files (plugin metadata), documentation files (user and API reference), testing validation (local and fresh install testing), and the contribution workflow. Changes typically focus on `SKILL.md`, `run.js`, or `helpers.js`, with corresponding updates to documentation.

Sources: [CONTRIBUTING.md:1-136](), [README.md:216-218]()

## Component Dependencies and Extension Points

```mermaid
graph LR
    subgraph "Entry Points"
        CLAUDE["Claude AI<br/>Reads SKILL.md"]
        USER_CODE["User-Generated Code<br/>/tmp/playwright-test-*.js"]
    end
    
    subgraph "Core Execution: run.js"
        RUN_MAIN["run.js main()<br/>Parse arguments"]
        RUN_WRAP["wrapCode()<br/>Inject requires<br/>Add async wrapper"]
        RUN_EXEC["executeScript()<br/>Module resolution<br/>Error handling"]
        RUN_CHECK["checkPlaywright()<br/>Auto-install if missing"]
    end
    
    subgraph "Helper Library: lib/helpers.js"
        DETECT["detectDevServers()<br/>Scan ports 3000-9000"]
        SAFE_CLICK["safeClick(page, selector)<br/>Wait + retry logic"]
        SAFE_TYPE["safeType(page, selector, text)<br/>Clear + type + verify"]
        SCREENSHOT["takeScreenshot(page, name)<br/>Save to /tmp"]
        AUTH["authenticate(page, creds)<br/>Login flows"]
        COOKIE["handleCookieBanner(page)<br/>Dismiss popups"]
        TABLE["extractTableData(page, selector)<br/>Parse tables"]
    end
    
    subgraph "Execution Artifacts"
        TEMP_EXEC["/tmp/.temp-execution-*.js<br/>Wrapped code"]
        TEMP_SCREEN["/tmp/*.png<br/>Screenshots"]
    end
    
    subgraph "External Dependencies"
        PLAYWRIGHT["playwright module<br/>^1.48.0"]
        BROWSERS["Browser binaries<br/>Chromium default"]
    end
    
    CLAUDE --> SKILL_MD["SKILL.md<br/>Instructions & examples"]
    SKILL_MD --> USER_CODE
    USER_CODE --> RUN_MAIN
    
    RUN_MAIN --> RUN_CHECK
    RUN_CHECK --> PLAYWRIGHT
    PLAYWRIGHT --> BROWSERS
    
    RUN_MAIN --> RUN_WRAP
    RUN_WRAP --> RUN_EXEC
    
    RUN_EXEC --> TEMP_EXEC
    RUN_EXEC --> PLAYWRIGHT
    
    DETECT -.->|"Used by"| SKILL_MD
    SAFE_CLICK -.->|"Available to"| USER_CODE
    SAFE_TYPE -.->|"Available to"| USER_CODE
    SCREENSHOT -.->|"Available to"| USER_CODE
    AUTH -.->|"Available to"| USER_CODE
    COOKIE -.->|"Available to"| USER_CODE
    TABLE -.->|"Available to"| USER_CODE
    
    PLAYWRIGHT --> TEMP_SCREEN
```

**Component Dependencies: Code Entity Map**

This diagram maps the actual code entities and their dependencies. The `run.js` file contains four main functions: `main()` for argument parsing, `wrapCode()` for injecting imports and async wrappers, `executeScript()` for running the wrapped code, and `checkPlaywright()` for dependency validation. The `lib/helpers.js` module exports seven utility functions: `detectDevServers()`, `safeClick()`, `safeType()`, `takeScreenshot()`, `authenticate()`, `handleCookieBanner()`, and `extractTableData()`. These helpers are available for use in user-generated code but are optional. All execution artifacts flow to `/tmp/` for clean separation from the codebase.

Sources: [README.md:166-184](), [CONTRIBUTING.md:99-136]()

## Contribution Workflow

The contribution process follows a standard fork-and-pull-request model with specific requirements for this repository:

**1. Setup Local Development**

```bash
# Fork repository on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/playwright-skill.git
cd playwright-skill

# Create feature branch
git checkout -b feature/your-feature-name

# Install dependencies (from skill directory)
cd skills/playwright-skill
npm run setup
```

**2. Make Changes**

Focus changes on specific components based on the enhancement type:

| Change Type | Primary Files | Secondary Files |
|-------------|---------------|-----------------|
| New helper function | `lib/helpers.js` | `SKILL.md` (add example) |
| Fix execution bug | `run.js` | `SKILL.md` (update if needed) |
| Add documentation | `SKILL.md`, `API_REFERENCE.md` | `README.md` |
| Update plugin metadata | `.claude-plugin/plugin.json` | `.claude-plugin/marketplace.json` |

**3. Follow Code Style**

Per [CONTRIBUTING.md:66-72]():
- Use clear, descriptive variable names
- Add comments for complex logic
- Keep functions focused on single responsibility
- Follow existing patterns in codebase

**4. Update Documentation**

When modifying `SKILL.md` per [CONTRIBUTING.md:73-79]():
- Keep examples concise (8-15 lines)
- Always show `headless: false` by default
- Include error handling in examples
- Add `console.log` statements for visibility
- Reference `README.md` for advanced topics

**5. Commit with Conventional Format**

Per [CONTRIBUTING.md:82-96](), use these prefixes:

```bash
git commit -m "feat: add mobile device emulation helper"
git commit -m "fix: resolve module resolution issue in run.js"
git commit -m "docs: update installation instructions"
git commit -m "refactor: simplify code wrapping logic"
git commit -m "test: add validation for helper functions"
git commit -m "chore: update dependencies"
```

Sources: [CONTRIBUTING.md:25-63](), [CONTRIBUTING.md:82-96]()

## Testing and Validation

Before submitting changes, developers must validate across multiple dimensions:

### Local Testing Checklist

```mermaid
graph TD
    START["Start Testing"] --> SETUP["npm run setup<br/>Verify Playwright installs"]
    
    SETUP --> SKILL_EXAMPLES["Test SKILL.md Examples<br/>Verify all code samples work"]
    
    SKILL_EXAMPLES --> RUN_EDGE["Test run.js Edge Cases<br/>- File mode<br/>- Inline mode<br/>- Stdin mode"]
    
    RUN_EDGE --> BROWSER_VIS["Verify Browser Visibility<br/>headless: false by default"]
    
    BROWSER_VIS --> FRESH_TEST["Fresh Installation Test<br/>Clean environment validation"]
    
    FRESH_TEST --> HELPER_TEST["Test New Helpers<br/>If helpers.js modified"]
    
    HELPER_TEST --> DOC_VERIFY["Documentation Verification<br/>README.md accuracy<br/>SKILL.md examples<br/>API_REFERENCE.md completeness"]
    
    DOC_VERIFY --> PASS["All Tests Pass"]
    PASS --> SUBMIT["Submit Pull Request"]
    
    SKILL_EXAMPLES -->|"Failure"| FIX["Fix Issues"]
    RUN_EDGE -->|"Failure"| FIX
    BROWSER_VIS -->|"Failure"| FIX
    FRESH_TEST -->|"Failure"| FIX
    HELPER_TEST -->|"Failure"| FIX
    DOC_VERIFY -->|"Failure"| FIX
    
    FIX --> SETUP
```

**Testing Validation Flow**

Per [CONTRIBUTING.md:122-127](), before submitting:
1. Test with fresh installation
2. Verify examples in `SKILL.md` work
3. Check that `run.js` handles edge cases
4. Ensure browser opens in visible mode by default

### Fresh Installation Testing

To validate the nested structure extraction requirement:

```bash
# Test plugin installation path
mkdir -p ~/.claude/plugins/marketplaces/test-install/skills
cp -r skills/playwright-skill ~/.claude/plugins/marketplaces/test-install/skills/
cd ~/.claude/plugins/marketplaces/test-install/skills/playwright-skill
npm run setup

# Test standalone installation path
mkdir -p ~/.claude/skills/test-standalone
cp -r skills/playwright-skill/* ~/.claude/skills/test-standalone/
cd ~/.claude/skills/test-standalone
npm run setup

# Test project-specific installation
mkdir -p /tmp/test-project/.claude/skills
cp -r skills/playwright-skill /tmp/test-project/.claude/skills/
cd /tmp/test-project/.claude/skills/playwright-skill
npm run setup
```

Sources: [CONTRIBUTING.md:122-128](), [README.md:18-116]()

## Key Extension Points

### Adding Helper Functions

When adding functions to [lib/helpers.js](), follow this pattern from [CONTRIBUTING.md:113-119]():

1. **Add clear JSDoc comments** - Document parameters, return values, and usage
2. **Include error handling** - Use try-catch blocks and meaningful error messages
3. **Export the function** - Add to module.exports
4. **Update SKILL.md** - Add example usage showing the new helper
5. **Test thoroughly** - Verify the helper works in actual automation scenarios

### Modifying run.js

The [run.js]() universal executor is critical for proper module resolution. When modifying:

- Maintain the three execution modes: file, inline, and stdin
- Preserve the `cd $SKILL_DIR` context for module resolution
- Keep the code wrapping logic that injects `require()` statements
- Ensure temporary files use timestamped names to avoid conflicts
- Test with scripts that import from `lib/helpers.js`

### Updating SKILL.md

The [SKILL.md]() file provides instructions to Claude AI. Guidelines from [CONTRIBUTING.md:73-79]():

- **Keep it concise** - Target ~314 lines total
- **Show working examples** - 8-15 lines per example
- **Default to visible browser** - Always show `headless: false`
- **Include error handling** - Demonstrate robust patterns
- **Add console.log** - Make automation progress visible
- **Reference API_REFERENCE.md** - For advanced topics, point to comprehensive docs

### Version Management

The repository maintains three version numbers across different manifests:

| File | Version | Purpose |
|------|---------|---------|
| `.claude-plugin/plugin.json` | v4.0.2 | Plugin distribution version |
| `.claude-plugin/marketplace.json` | entry: v1.0.0<br/>plugin: v3.1.0 | Marketplace listing versions |
| `skills/playwright-skill/package.json` | v4.0.2 | npm package version |

When releasing new versions, update all three files to maintain consistency.

Sources: [CONTRIBUTING.md:113-119](), [README.md:166-184]()

## Pull Request Requirements

Before submitting a pull request per [CONTRIBUTING.md:57-62]():

**Required Information:**
- Clear description of changes
- Motivation for the changes
- Test results demonstrating the changes work
- Screenshots if UI/browser behavior is affected
- Links to relevant issues if applicable

**Code Quality:**
- All examples in `SKILL.md` must execute successfully
- Changes must work with both plugin and standalone installation methods
- Nested structure must be preserved for plugin distribution
- No hardcoded paths - use `$SKILL_DIR` for skill directory references
- Browser must default to visible mode (`headless: false`)

**Documentation:**
- Update `README.md` if user-facing functionality changes
- Update `API_REFERENCE.md` if Playwright API coverage changes
- Update `CONTRIBUTING.md` if development workflow changes
- Keep documentation concise and focused on technical details

Sources: [CONTRIBUTING.md:57-63](), [CONTRIBUTING.md:1-136]()

---

