# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of Claude Bootstrap, an AI-native development system designed to add TDD-first guardrails to Claude Code. It explains the system architecture, core components, and how they interact to enable iterative, quality-enforced development workflows.

For detailed information about specific subsystems:
- Installation and setup procedures: see [Installation](#2.1)
- TDD workflow mechanics: see [TDD Workflow](#3.2)
- Ralph loop iteration engine: see [Ralph Loop](#4.1)
- Skills system details: see [Skills Architecture](#5.1)
- Team coordination features: see [Multi-Developer Coordination](#8.1)

**Sources:** [README.md:1-50]()

---

## What is Claude Bootstrap?

Claude Bootstrap is a project initialization and development workflow system that transforms Claude Code from a powerful but unpredictable tool into a structured, quality-enforced development environment. It addresses a fundamental challenge: **AI can generate infinite code, but humans still need to comprehend, review, and maintain it.**

The system implements three core mechanisms:

1. **Mandatory TDD** - Tests must fail before implementation proves they validate requirements
2. **Iterative Loops** - Self-referential refinement cycles continue until quality gates pass
3. **Complexity Constraints** - Hard limits (20 lines/function, 200 lines/file) prevent unmaintainable code

These guardrails are encoded as a modular skills system that adapts to project type (web, mobile, backend, AI-native) while maintaining consistent development patterns.

**Sources:** [README.md:1-50]()

---

## System Architecture

The following diagram shows the complete system architecture from installation through deployment, using actual file and directory names from the codebase.

### Architecture Overview

```mermaid
graph TB
    subgraph "Installation Layer"
        INSTALL["install.sh"]
        HOME_SKILLS["~/.claude/skills/<br/>(41 skill files)"]
        HOME_COMMANDS["~/.claude/commands/<br/>(command scripts)"]
        HOOKS["~/.claude/hooks/<br/>(git hooks)"]
    end
    
    subgraph "Project Initialization"
        INIT_CMD["/initialize-project command"]
        VERIFY_TOOLS["verify-tooling.sh"]
        SELECT_SKILLS["skill selection logic"]
        GEN_STRUCTURE["structure generation"]
    end
    
    subgraph "Project Structure"
        CLAUDE_SKILLS[".claude/skills/<br/>(selected skills)"]
        CLAUDE_MD["CLAUDE.md<br/>(instructions)"]
        PROJECT_SPECS["_project_specs/<br/>(features, todos, team)"]
        GITHUB_WF[".github/workflows/<br/>(quality.yml, security.yml)"]
        SCRIPTS_DIR["scripts/<br/>(verify, security)"]
    end
    
    subgraph "Development Workflow"
        RALPH["/ralph-loop command<br/>(iterative engine)"]
        CODE_REVIEW["/code-review command<br/>(quality gate)"]
        CHECK_CONTRIB["/check-contributors command<br/>(team sync)"]
        UPDATE_INDEX["/update-code-index command<br/>(deduplication)"]
    end
    
    subgraph "Quality Enforcement"
        PREHOOK["pre-commit hook<br/>(security-check.sh)"]
        PUSHOOK["pre-push hook<br/>(code-review.sh)"]
        CI_QUALITY["quality.yml workflow<br/>(tests, coverage)"]
        CI_SECURITY["security.yml workflow<br/>(secrets, deps)"]
    end
    
    subgraph "External Integrations"
        GH_CLI["gh CLI<br/>(repo mgmt)"]
        VERCEL_CLI["vercel CLI<br/>(deployment)"]
        SUPABASE_CLI["supabase CLI<br/>(database)"]
        ACCESS_TXT["~/Documents/Access.txt<br/>(credentials)"]
    end
    
    INSTALL --> HOME_SKILLS
    INSTALL --> HOME_COMMANDS
    INSTALL --> HOOKS
    
    INIT_CMD --> VERIFY_TOOLS
    VERIFY_TOOLS --> GH_CLI
    VERIFY_TOOLS --> VERCEL_CLI
    VERIFY_TOOLS --> SUPABASE_CLI
    
    INIT_CMD --> SELECT_SKILLS
    SELECT_SKILLS --> HOME_SKILLS
    SELECT_SKILLS --> CLAUDE_SKILLS
    
    INIT_CMD --> GEN_STRUCTURE
    GEN_STRUCTURE --> CLAUDE_MD
    GEN_STRUCTURE --> PROJECT_SPECS
    GEN_STRUCTURE --> GITHUB_WF
    GEN_STRUCTURE --> SCRIPTS_DIR
    
    INIT_CMD --> ACCESS_TXT
    ACCESS_TXT --> GEN_STRUCTURE
    
    CLAUDE_SKILLS --> RALPH
    CLAUDE_SKILLS --> CODE_REVIEW
    CLAUDE_SKILLS --> CHECK_CONTRIB
    CLAUDE_SKILLS --> UPDATE_INDEX
    
    RALPH --> PREHOOK
    PREHOOK --> PUSHOOK
    PUSHOOK --> CODE_REVIEW
    CODE_REVIEW --> CI_QUALITY
    CI_QUALITY --> CI_SECURITY
```

**Sources:** [README.md:52-70](), [README.md:296-317]()

---

## Installation to Initialization Flow

This diagram shows the exact sequence from running `install.sh` to having a fully initialized project, using actual file paths and command names.

### Installation Flow

```mermaid
sequenceDiagram
    participant User
    participant install_sh as "install.sh"
    participant home_claude as "~/.claude/"
    participant project_dir as "project directory"
    participant init_cmd as "/initialize-project"
    participant verify_sh as "verify-tooling.sh"
    participant skills_src as "~/.claude/skills/"
    participant skills_dest as ".claude/skills/"
    
    User->>install_sh: "./install.sh"
    install_sh->>home_claude: "create ~/.claude/ structure"
    install_sh->>home_claude: "copy skills/ (41 files)"
    install_sh->>home_claude: "copy commands/"
    install_sh->>home_claude: "copy hooks/"
    install_sh->>User: "Installation complete"
    
    User->>project_dir: "cd my-project"
    User->>init_cmd: "claude > /initialize-project"
    
    init_cmd->>verify_sh: "execute verify-tooling.sh"
    verify_sh->>verify_sh: "check gh CLI"
    verify_sh->>verify_sh: "check vercel CLI"
    verify_sh->>verify_sh: "check supabase CLI"
    verify_sh->>init_cmd: "return tool status"
    
    init_cmd->>User: "ask: language? (Python/TypeScript)"
    User->>init_cmd: "TypeScript"
    
    init_cmd->>User: "ask: framework? (React/Next.js/Node backend)"
    User->>init_cmd: "Next.js"
    
    init_cmd->>User: "ask: AI-first? (y/n)"
    User->>init_cmd: "yes"
    
    init_cmd->>User: "ask: database? (Supabase/PostgreSQL/none)"
    User->>init_cmd: "Supabase"
    
    init_cmd->>skills_src: "read skill files"
    init_cmd->>init_cmd: "select skills based on answers"
    init_cmd->>skills_dest: "copy base.md"
    init_cmd->>skills_dest: "copy security.md"
    init_cmd->>skills_dest: "copy typescript.md"
    init_cmd->>skills_dest: "copy react-web.md"
    init_cmd->>skills_dest: "copy agentic-development.md"
    init_cmd->>skills_dest: "copy supabase-nextjs.md"
    
    init_cmd->>project_dir: "create CLAUDE.md"
    init_cmd->>project_dir: "create _project_specs/"
    init_cmd->>project_dir: "create .github/workflows/"
    init_cmd->>project_dir: "create scripts/"
    
    init_cmd->>User: "Project initialized. Ready for development."
```

**Sources:** [README.md:52-70](), [README.md:296-317]()

---

## Core Skills Loading System

This diagram shows how the modular skills system loads different skill files based on project configuration, using actual skill file names.

### Skills Selection Logic

```mermaid
graph TB
    subgraph "Always Loaded (Core)"
        BASE["base.md"]
        SECURITY["security.md"]
        CREDENTIALS["credentials.md"]
        SESSION["session-management.md"]
        CODE_REVIEW_SKILL["code-review.md"]
        COMMIT_HYG["commit-hygiene.md"]
        DEDUP["code-deduplication.md"]
        TEAM_COORD["team-coordination.md"]
        ITER_DEV["iterative-development.md"]
        PROJECT_TOOL["project-tooling.md"]
    end
    
    subgraph "Language Selection"
        LANG_Q{"Language?"}
        PYTHON["python.md"]
        TYPESCRIPT["typescript.md"]
    end
    
    subgraph "Framework Selection"
        FW_Q{"Framework?"}
        REACT_WEB["react-web.md"]
        REACT_NATIVE["react-native.md"]
        NODEJS_BACKEND["nodejs-backend.md"]
        FASTAPI["fastapi.md"]
    end
    
    subgraph "Database Selection"
        DB_Q{"Database?"}
        SUPABASE["supabase.md"]
        SUPABASE_NEXTJS["supabase-nextjs.md"]
        SUPABASE_PYTHON["supabase-python.md"]
        SUPABASE_NODE["supabase-node.md"]
        DB_SCHEMA["database-schema.md"]
    end
    
    subgraph "UI Selection"
        UI_Q{"UI Platform?"}
        UI_WEB["ui-web.md"]
        UI_MOBILE["ui-mobile.md"]
        UI_TESTING["ui-testing.md"]
        PLAYWRIGHT["playwright-testing.md"]
        USER_JOURNEYS["user-journeys.md"]
        PWA["pwa-development.md"]
    end
    
    subgraph "AI Selection"
        AI_Q{"AI-First?"}
        AGENTIC["agentic-development.md"]
        LLM_PATTERNS["llm-patterns.md"]
        AI_MODELS["ai-models.md"]
    end
    
    subgraph "Integration Selection"
        INT_Q{"Integrations?"}
        WEB_PAYMENTS["web-payments.md"]
        POSTHOG["posthog-analytics.md"]
        REDDIT_API["reddit-api.md"]
        REDDIT_ADS["reddit-ads.md"]
        SHOPIFY["shopify-apps.md"]
        WOOCOMMERCE["woocommerce.md"]
        MEDUSA["medusa.md"]
        KLAVIYO["klaviyo.md"]
        MS_TEAMS["ms-teams-apps.md"]
        WEB_CONTENT["web-content.md"]
        AEO["aeo-optimization.md"]
        SITE_ARCH["site-architecture.md"]
    end
    
    subgraph "Destination"
        DEST[".claude/skills/<br/>(project copy)"]
    end
    
    LANG_Q -->|"Python"| PYTHON
    LANG_Q -->|"TypeScript"| TYPESCRIPT
    
    FW_Q -->|"React"| REACT_WEB
    FW_Q -->|"React Native"| REACT_NATIVE
    FW_Q -->|"Node backend"| NODEJS_BACKEND
    FW_Q -->|"FastAPI"| FASTAPI
    
    DB_Q -->|"Supabase + Next.js"| SUPABASE_NEXTJS
    DB_Q -->|"Supabase + Python"| SUPABASE_PYTHON
    DB_Q -->|"Supabase + Node"| SUPABASE_NODE
    DB_Q -->|"Any database"| DB_SCHEMA
    DB_Q --> SUPABASE
    
    UI_Q -->|"Web"| UI_WEB
    UI_Q -->|"Mobile"| UI_MOBILE
    UI_Q -->|"E2E Testing"| PLAYWRIGHT
    UI_Q --> UI_TESTING
    UI_Q --> USER_JOURNEYS
    UI_Q -->|"PWA"| PWA
    
    AI_Q -->|"Yes"| AGENTIC
    AI_Q -->|"Yes"| LLM_PATTERNS
    AI_Q -->|"Yes"| AI_MODELS
    
    INT_Q -->|"Stripe"| WEB_PAYMENTS
    INT_Q -->|"PostHog"| POSTHOG
    INT_Q -->|"Reddit"| REDDIT_API
    INT_Q -->|"Reddit Ads"| REDDIT_ADS
    INT_Q -->|"Shopify"| SHOPIFY
    INT_Q -->|"WooCommerce"| WOOCOMMERCE
    INT_Q -->|"Medusa"| MEDUSA
    INT_Q -->|"Klaviyo"| KLAVIYO
    INT_Q -->|"Teams"| MS_TEAMS
    INT_Q -->|"SEO"| WEB_CONTENT
    INT_Q -->|"SEO"| AEO
    INT_Q -->|"SEO"| SITE_ARCH
    
    BASE --> DEST
    SECURITY --> DEST
    CREDENTIALS --> DEST
    SESSION --> DEST
    CODE_REVIEW_SKILL --> DEST
    COMMIT_HYG --> DEST
    DEDUP --> DEST
    TEAM_COORD --> DEST
    ITER_DEV --> DEST
    PROJECT_TOOL --> DEST
    
    PYTHON --> DEST
    TYPESCRIPT --> DEST
    REACT_WEB --> DEST
    REACT_NATIVE --> DEST
    NODEJS_BACKEND --> DEST
    FASTAPI --> DEST
    SUPABASE --> DEST
    SUPABASE_NEXTJS --> DEST
    SUPABASE_PYTHON --> DEST
    SUPABASE_NODE --> DEST
    DB_SCHEMA --> DEST
    UI_WEB --> DEST
    UI_MOBILE --> DEST
    UI_TESTING --> DEST
    PLAYWRIGHT --> DEST
    USER_JOURNEYS --> DEST
    PWA --> DEST
    AGENTIC --> DEST
    LLM_PATTERNS --> DEST
    AI_MODELS --> DEST
    WEB_PAYMENTS --> DEST
    POSTHOG --> DEST
    REDDIT_API --> DEST
    REDDIT_ADS --> DEST
    SHOPIFY --> DEST
    WOOCOMMERCE --> DEST
    MEDUSA --> DEST
    KLAVIYO --> DEST
    MS_TEAMS --> DEST
    WEB_CONTENT --> DEST
    AEO --> DEST
    SITE_ARCH --> DEST
```

**Sources:** [README.md:396-466]()

---

## Development Workflow Pipeline

This diagram illustrates the complete development flow from feature specification to deployment, showing actual commands and file locations.

### End-to-End Development Flow

```mermaid
graph LR
    subgraph "Specification Phase"
        SPEC_CREATE["Create feature spec<br/>_project_specs/features/"]
        TODO_CREATE["Break into todos<br/>_project_specs/todos/active.md"]
    end
    
    subgraph "Implementation Phase"
        RALPH_EXEC["/ralph-loop<br/>(auto or manual)"]
        TDD_RED["RED: Write failing tests"]
        TDD_GREEN["GREEN: Implement minimum"]
        TDD_VALIDATE["VALIDATE: lint + types + coverage"]
        TODO_MOVE["Move to completed<br/>active.md → completed.md"]
    end
    
    subgraph "Pre-Commit Phase"
        GIT_ADD["git add ."]
        PREHOOK_EXEC["pre-commit hook<br/>scripts/security-check.sh"]
        LINT_CHECK["lint + typecheck"]
        UNIT_TESTS["unit tests (changed files)"]
        SECRET_SCAN["secret scanning"]
    end
    
    subgraph "Pre-Push Phase"
        GIT_COMMIT["git commit -m '...'"]
        SIZE_CHECK["commit size tracking<br/>(commit-hygiene.md)"]
        GIT_PUSH["git push"]
        PUSHOOK_EXEC["pre-push hook<br/>scripts/code-review.sh"]
        REVIEW_EXEC["/code-review"]
        SEVERITY_CHECK["severity check<br/>(Critical/High = block)"]
    end
    
    subgraph "CI/CD Phase"
        GH_ACTIONS["GitHub Actions trigger"]
        QUALITY_WF["quality.yml workflow"]
        FULL_TESTS["full test suite"]
        COVERAGE_CHECK["coverage >= 80%"]
        SECURITY_WF["security.yml workflow"]
        TRUFFLEHOG["TruffleHog secret scan"]
        DEP_AUDIT["npm audit / safety"]
    end
    
    subgraph "Deployment Phase"
        MERGE["merge to main"]
        VERCEL_DEPLOY["vercel deploy"]
        SUPABASE_MIG["supabase db push"]
        PRODUCTION["production"]
    end
    
    SPEC_CREATE --> TODO_CREATE
    TODO_CREATE --> RALPH_EXEC
    
    RALPH_EXEC --> TDD_RED
    TDD_RED --> TDD_GREEN
    TDD_GREEN --> TDD_VALIDATE
    TDD_VALIDATE --> TODO_MOVE
    TODO_MOVE --> GIT_ADD
    
    GIT_ADD --> PREHOOK_EXEC
    PREHOOK_EXEC --> LINT_CHECK
    LINT_CHECK --> UNIT_TESTS
    UNIT_TESTS --> SECRET_SCAN
    SECRET_SCAN --> GIT_COMMIT
    
    GIT_COMMIT --> SIZE_CHECK
    SIZE_CHECK --> GIT_PUSH
    GIT_PUSH --> PUSHOOK_EXEC
    PUSHOOK_EXEC --> REVIEW_EXEC
    REVIEW_EXEC --> SEVERITY_CHECK
    SEVERITY_CHECK --> GH_ACTIONS
    
    GH_ACTIONS --> QUALITY_WF
    QUALITY_WF --> FULL_TESTS
    FULL_TESTS --> COVERAGE_CHECK
    COVERAGE_CHECK --> SECURITY_WF
    SECURITY_WF --> TRUFFLEHOG
    TRUFFLEHOG --> DEP_AUDIT
    DEP_AUDIT --> MERGE
    
    MERGE --> VERCEL_DEPLOY
    MERGE --> SUPABASE_MIG
    VERCEL_DEPLOY --> PRODUCTION
    SUPABASE_MIG --> PRODUCTION
    
    TDD_VALIDATE -->|"tests fail"| TDD_RED
    SEVERITY_CHECK -->|"Critical/High"| TDD_RED
    DEP_AUDIT -->|"fail"| TDD_RED
```

**Sources:** [README.md:71-100](), [README.md:176-210](), [README.md:516-530]()

---

## Project File Structure

When `/initialize-project` completes, it creates the following directory structure with specific files:

### Generated Directory Structure

| Path | Purpose | Created By |
|------|---------|------------|
| `.claude/skills/` | Project-specific skill files copied from `~/.claude/skills/` | `/initialize-project` |
| `.claude/skills/base.md` | Core TDD patterns, simplicity rules, atomic todos | Always copied |
| `.claude/skills/security.md` | OWASP patterns, secrets management | Always copied |
| `.claude/skills/credentials.md` | Access.txt integration, .env generation | Always copied |
| `.claude/skills/[language].md` | Language-specific patterns (python.md or typescript.md) | Based on selection |
| `.claude/skills/[framework].md` | Framework patterns (react-web.md, fastapi.md, etc.) | Based on selection |
| `CLAUDE.md` | Master instruction file for Claude Code | `/initialize-project` |
| `_project_specs/` | Specification and state management directory | `/initialize-project` |
| `_project_specs/overview.md` | Project vision and architecture | `/initialize-project` |
| `_project_specs/features/` | Feature specification files | `/initialize-project` |
| `_project_specs/todos/active.md` | Current work items with test cases | `/initialize-project` |
| `_project_specs/todos/completed.md` | Completed todos with TDD logs | Moved from active.md |
| `_project_specs/session/` | Session management files | Session work |
| `_project_specs/session/current-state.md` | Current session state | Session checkpoints |
| `_project_specs/session/decisions.md` | Architectural decisions | During development |
| `_project_specs/session/code-landmarks.md` | Key code locations | Session work |
| `_project_specs/team/` | Team coordination (multi-dev only) | `/check-contributors --team` |
| `_project_specs/team/state.md` | Active sessions, claimed todos, conflicts | Team updates |
| `_project_specs/team/contributors.md` | Team members, ownership areas | `/check-contributors --team` |
| `_project_specs/team/handoffs/` | Context transfer notes | Developer handoffs |
| `_project_specs/CODE_INDEX.md` | Semantic capability index | `/update-code-index` |
| `.github/workflows/quality.yml` | Lint, type-check, test with 80% coverage | `/initialize-project` |
| `.github/workflows/security.yml` | TruffleHog secret scan, dependency audit | `/initialize-project` |
| `scripts/verify-tooling.sh` | Validate gh, vercel, supabase CLIs | `/initialize-project` |
| `scripts/security-check.sh` | Pre-commit secret scanning | `/initialize-project` |
| `.husky/pre-commit` or `.git/hooks/pre-commit` | Runs security-check.sh, lint, unit tests | Hook installation |
| `.husky/pre-push` or `.git/hooks/pre-push` | Runs /code-review, blocks on Critical/High | Hook installation |

**Sources:** [README.md:296-317]()

---

## Command Reference

Claude Bootstrap provides five primary commands that drive the development workflow:

### Core Commands

| Command | Location | Purpose | When to Use |
|---------|----------|---------|-------------|
| `/initialize-project` | `~/.claude/commands/` | Initialize or update project structure, copy skills, create specs | New projects or skill updates |
| `/ralph-loop` | Plugin (ralph-loop@claude-plugins-official) | Execute iterative TDD cycles with stop-hook mechanism | Auto-invoked or manual for specific tasks |
| `/code-review` | `~/.claude/commands/` | Analyze changes for security, performance, architecture issues | Before every push (enforced by pre-push hook) |
| `/check-contributors` | `~/.claude/commands/` | Check team state, detect solo vs. team mode, convert projects | Start of each session, before claiming todos |
| `/update-code-index` | `~/.claude/commands/` | Regenerate CODE_INDEX.md semantic capability index | After significant code additions |
| `/cancel-ralph` | Plugin | Interrupt running ralph-loop iterations | When loop needs to be stopped |

**Sources:** [README.md:52-70](), [README.md:71-100](), [README.md:176-210](), [README.md:211-253](), [README.md:255-295]()

---

## Quality Enforcement Layers

The system implements five layers of quality enforcement, each with specific tools and mechanisms:

### Defense-in-Depth Quality Gates

```mermaid
graph TB
    subgraph "Layer 1: Development"
        L1_ACCESS["Access.txt credential mgmt<br/>(credentials.md)"]
        L1_ENV[".env generation<br/>(no secrets in code)"]
        L1_PATTERN["pattern validation<br/>(auto-detect API keys)"]
        L1_CLIENT["client env check<br/>(VITE_*, NEXT_PUBLIC_*)"]
    end
    
    subgraph "Layer 2: Pre-Commit"
        L2_HOOK["pre-commit hook"]
        L2_SECURITY["security-check.sh<br/>(scan for secrets)"]
        L2_LINT["lint + typecheck"]
        L2_UNIT["unit tests<br/>(changed files)"]
        L2_ENV_CHECK["check .env not staged"]
    end
    
    subgraph "Layer 3: Pre-Push"
        L3_HOOK["pre-push hook"]
        L3_REVIEW["/code-review command"]
        L3_ANALYZE["analyze changes<br/>(security, perf, arch)"]
        L3_SEVERITY["severity classification<br/>(Critical, High, Medium, Low)"]
        L3_BLOCK["block on Critical/High"]
    end
    
    subgraph "Layer 4: CI/CD"
        L4_QUALITY["quality.yml"]
        L4_TESTS["full test suite"]
        L4_COVERAGE["coverage >= 80%"]
        L4_SECURITY["security.yml"]
        L4_TRUFFLEHOG["TruffleHog scan"]
        L4_DEPS["npm audit / safety"]
    end
    
    subgraph "Layer 5: Monitoring"
        L5_SIZE["commit size tracking"]
        L5_OK["OK: ≤5 files, ≤200 lines"]
        L5_WARN["WARN: 6-10 files, 201-400 lines"]
        L5_STOP["STOP: >10 files, >400 lines"]
    end
    
    CODE["Developer Code"] --> L1_ACCESS
    L1_ACCESS --> L1_ENV
    L1_ENV --> L1_PATTERN
    L1_PATTERN --> L1_CLIENT
    
    L1_CLIENT --> L2_HOOK
    L2_HOOK --> L2_SECURITY
    L2_SECURITY --> L2_LINT
    L2_LINT --> L2_UNIT
    L2_UNIT --> L2_ENV_CHECK
    
    L2_ENV_CHECK --> L5_SIZE
    L5_SIZE --> L5_OK
    L5_SIZE --> L5_WARN
    L5_SIZE --> L5_STOP
    
    L5_OK --> L3_HOOK
    L5_WARN --> L3_HOOK
    L5_STOP --> L3_HOOK
    
    L3_HOOK --> L3_REVIEW
    L3_REVIEW --> L3_ANALYZE
    L3_ANALYZE --> L3_SEVERITY
    L3_SEVERITY --> L3_BLOCK
    
    L3_BLOCK -->|"pass"| L4_QUALITY
    L4_QUALITY --> L4_TESTS
    L4_TESTS --> L4_COVERAGE
    L4_COVERAGE --> L4_SECURITY
    L4_SECURITY --> L4_TRUFFLEHOG
    L4_TRUFFLEHOG --> L4_DEPS
    
    L3_BLOCK -->|"Critical/High"| CODE
    L4_DEPS -->|"fail"| CODE
```

**Sources:** [README.md:119-147](), [README.md:176-210](), [README.md:516-530]()

---

## Credentials Management Flow

The system uses centralized credentials management to prevent secrets from entering the codebase:

### Access.txt Integration

```mermaid
sequenceDiagram
    participant User
    participant init_cmd as "/initialize-project"
    participant access_txt as "~/Documents/Access.txt"
    participant patterns as "credentials.md patterns"
    participant project_env as "project .env"
    participant gitignore as ".gitignore"
    participant security_check as "security-check.sh"
    
    User->>init_cmd: "run initialization"
    init_cmd->>User: "Where is Access.txt?"
    User->>init_cmd: "~/Documents/Access.txt"
    
    init_cmd->>access_txt: "read file"
    access_txt->>init_cmd: "raw text content"
    
    init_cmd->>patterns: "load detection patterns"
    patterns->>init_cmd: "OpenAI API: sk-proj-<br/>Stripe: sk_test_<br/>Supabase url: https://"
    
    init_cmd->>init_cmd: "match patterns to lines"
    init_cmd->>User: "Found: OpenAI, Stripe, Supabase<br/>Include all? (y/n)"
    User->>init_cmd: "yes"
    
    init_cmd->>project_env: "write .env file"
    project_env->>project_env: "OPENAI_API_KEY=sk-proj-xxx<br/>STRIPE_SECRET_KEY=sk_test_xxx<br/>SUPABASE_URL=https://xxx"
    
    init_cmd->>gitignore: "append .env"
    init_cmd->>gitignore: "append .env.*"
    
    User->>User: "development work"
    User->>security_check: "git commit (triggers hook)"
    
    security_check->>security_check: "check if .env staged"
    security_check->>security_check: "scan for API key patterns"
    security_check->>User: "BLOCK: .env file in staging area"
```

**Sources:** [README.md:358-379]()

---

## Ralph Loop Iterative Engine

The Ralph loop is the core automation engine. This diagram shows the actual command flow and file interactions:

### Ralph Loop Execution

```mermaid
stateDiagram-v2
    [*] --> CheckAutomatic: "User request received"
    
    CheckAutomatic --> ExtractReq: "Parse natural language"
    CheckAutomatic --> Manual: "Opt-out phrase detected"
    
    ExtractReq --> StructureTDD: "Extract requirements"
    StructureTDD --> InvokeRalph: "Structure as TDD loop"
    InvokeRalph --> LoadState: "/ralph-loop --max-iterations 20"
    
    Manual --> [*]: "No loop execution"
    
    LoadState --> WriteTests: "Read current file state<br/>Read git history"
    
    WriteTests --> RunTests1: "Write tests in test file"
    
    RunTests1 --> VerifyRed: "npm test / pytest"
    
    VerifyRed --> FixTests: "Tests pass (invalid!)"
    VerifyRed --> Implement: "Tests fail (RED confirmed)"
    
    FixTests --> WriteTests
    
    Implement --> RunTests2: "Write implementation"
    
    RunTests2 --> ClassifyError: "Tests fail"
    RunTests2 --> RunLint: "Tests pass (GREEN confirmed)"
    
    ClassifyError --> DetermineType: "Analyze error"
    
    DetermineType --> Implement: "Code/Type/Logic error"
    DetermineType --> BlockerReport: "Access/Network/Env error"
    
    RunLint --> RunCoverage: "npm run lint<br/>tsc --noEmit"
    
    RunCoverage --> CheckCoverage: "npm test -- --coverage"
    
    CheckCoverage --> AddTests: "coverage < 80%"
    CheckCoverage --> UpdateTodo: "coverage >= 80%<br/>(VALIDATE confirmed)"
    
    AddTests --> RunTests2
    
    UpdateTodo --> OutputPromise: "Move active.md → completed.md"
    
    OutputPromise --> Success: "<promise>DONE</promise> output"
    OutputPromise --> CheckIterations: "No promise output"
    
    CheckIterations --> LoadState: "iterations < max<br/>Feed SAME prompt"
    CheckIterations --> MaxReached: "iterations >= max"
    
    Success --> [*]: "Exit: Complete"
    MaxReached --> [*]: "Exit: Max iterations"
    BlockerReport --> [*]: "Exit: Blocker<br/>Human action required"
```

**Sources:** [README.md:71-118](), [README.md:579-612]()

---

## Team Coordination System

For multi-developer projects, the system provides state management through `_project_specs/team/`:

### Team State Management

```mermaid
graph TB
    subgraph "Developer A Workflow"
        A1["git pull"]
        A2["/check-contributors"]
        A3["read state.md"]
        A4["claim todo<br/>(update state.md)"]
        A5["active work"]
        A6["checkpoint<br/>(update state.md)"]
        A7["complete & push<br/>(update state.md)"]
    end
    
    subgraph "Developer B Workflow"
        B1["git pull"]
        B2["/check-contributors"]
        B3["read state.md"]
        B4["see A's claimed todo"]
        B5["choose different todo"]
        B6["claim todo<br/>(update state.md)"]
        B7["active work"]
    end
    
    subgraph "Shared State Files"
        STATE["_project_specs/team/state.md"]
        CONTRIB["_project_specs/team/contributors.md"]
        HANDOFFS["_project_specs/team/handoffs/"]
        DECISIONS["_project_specs/session/decisions.md"]
    end
    
    subgraph "Conflict Detection"
        MONITOR["monitor state.md"]
        DETECT["detect file overlap"]
        WARN["warn on conflict"]
        COORDINATE["coordinate handoff"]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> STATE
    A3 --> A4
    A4 --> STATE
    A4 --> A5
    A5 --> A6
    A6 --> STATE
    A6 --> A5
    A5 --> A7
    A7 --> STATE
    
    B1 --> B2
    B2 --> B3
    B3 --> STATE
    B3 --> B4
    B4 --> B5
    B5 --> B6
    B6 --> STATE
    B6 --> B7
    B7 --> STATE
    
    A4 --> CONTRIB
    B6 --> CONTRIB
    A6 --> DECISIONS
    B7 --> DECISIONS
    A7 --> HANDOFFS
    
    STATE --> MONITOR
    MONITOR --> DETECT
    DETECT --> WARN
    WARN --> COORDINATE
    COORDINATE --> HANDOFFS
```

**Sources:** [README.md:211-253]()

---

## Complexity Constraints

The system enforces measurable complexity limits defined in `base.md`:

### Enforced Constraints

| Constraint | Limit | Enforcement Point | Violates? |
|------------|-------|-------------------|-----------|
| Lines per function | 20 max | Code review, manual check | Stop development, refactor immediately |
| Parameters per function | 3 max | Code review, manual check | Stop development, refactor immediately |
| Nesting depth | 2 levels max | Code review, manual check | Stop development, flatten logic |
| Lines per file | 200 max | Code review, manual check | Stop development, split file |
| Test coverage | 80% min | CI/CD quality.yml workflow | Block merge |
| Files per commit | 10 max (warning at 6) | commit-hygiene.md monitoring | Advisory at 6, strong warning at 10 |
| Lines changed per commit | 400 max (warning at 200) | commit-hygiene.md monitoring | Advisory at 200, strong warning at 400 |

**Protocol when limit exceeded:**
1. Development **stops immediately**
2. Refactor to meet constraint
3. Verify tests still pass
4. Resume development

**Sources:** [README.md:344-357](), [README.md:119-147]()

---

## Integration with External Tools

The system integrates with three primary CLIs validated during initialization:

### CLI Tool Integration

| Tool | Command | Validated By | Used For | Configuration File |
|------|---------|--------------|----------|-------------------|
| GitHub CLI | `gh` | `verify-tooling.sh` | Repository creation, PR management | `~/.config/gh/hosts.yml` |
| Vercel CLI | `vercel` | `verify-tooling.sh` | Deployment, environment variables | `.vercel/project.json` |
| Supabase CLI | `supabase` | `verify-tooling.sh` | Database migrations, Edge Functions | `supabase/config.toml` |

Additional integrations based on selected skills:

| Integration | Skill File | Configuration Method |
|-------------|-----------|---------------------|
| Stripe | `web-payments.md` | API keys from Access.txt → .env |
| PostHog | `posthog-analytics.md` | Project API key → .env |
| Reddit Ads | `reddit-ads.md` | OAuth credentials → .env |
| Klaviyo | `klaviyo.md` | Private API key → .env |
| WooCommerce | `woocommerce.md` | Consumer key/secret → .env |
| Medusa | `medusa.md` | Database URL → .env |

**Sources:** [README.md:497-513]()

---

## Session Management

The system preserves context across sessions using files in `_project_specs/session/`:

### Session Context Files

| File | Purpose | Updated When | Content Structure |
|------|---------|--------------|-------------------|
| `current-state.md` | Current session state, active work, next steps | Checkpoint triggers, end of work | What's done, what's in progress, blockers, next actions |
| `decisions.md` | Architectural decisions with rationale | Major design choices | Decision, context, alternatives considered, rationale |
| `code-landmarks.md` | Important code locations and patterns | New major components | File paths, key functions, patterns used |
| `CODE_INDEX.md` | Semantic capability index | `/update-code-index` | Organized by what code does, not where it lives |

**Checkpoint triggers:**
- Every 30 minutes of continuous work
- Before switching contexts
- At natural breakpoints (feature complete, tests passing)
- When complexity threshold approached

**Sources:** [README.md:255-295]()

---

## TDD Workflow Execution

Every feature and bug follows the RED-GREEN-VALIDATE pattern enforced by `base.md`:

### TDD Phase Execution

| Phase | Feature Development | Bug Fixing | Validation |
|-------|---------------------|------------|------------|
| **RED** | Write tests based on acceptance criteria | Write test that reproduces bug | Tests MUST fail |
| **GREEN** | Write minimum implementation | Fix the bug | Tests MUST pass |
| **VALIDATE** | Lint + TypeCheck + Coverage ≥80% | Lint + TypeCheck + Full suite | All checks MUST pass |

**Commands executed:**

```
# RED phase
npm test                                    # Must fail
pytest                                      # Must fail

# GREEN phase  
npm test                                    # Must pass
pytest                                      # Must pass

# VALIDATE phase
npm run lint && npm run typecheck          # Must pass
npm test -- --coverage                     # Must be ≥80%
```

**Anti-patterns prevented:**
- Tests written after implementation
- Bug fixes without new test
- Todos marked complete with failing tests
- Skipping validation phase

**Sources:** [README.md:320-343](), [README.md:531-578]()

---

## Key Design Decisions

### Why Stop Hooks Instead of Explicit Loops

The Ralph loop uses a "stop hook" mechanism that intercepts Claude's exit attempts. When Claude tries to finish, the system feeds the **identical prompt** back with updated file states visible. This creates a self-referential loop where Claude sees its own changes and continues refining until tests pass or completion criteria are met.

**Alternative considered:** Explicit loop command invocation requiring user to repeatedly run `/ralph-loop`.

**Rationale:** Stop hooks enable natural language interaction ("add email validation") without requiring users to understand loop mechanics.

### Why File-Based Team Coordination

Team coordination uses files (`state.md`, `contributors.md`) checked into git rather than external databases or services.

**Alternative considered:** Dedicated coordination service or database.

**Rationale:** 
- Zero infrastructure dependencies
- Works offline
- Visible in standard git workflow
- No additional authentication required
- Full audit trail through git history

### Why 80% Coverage Threshold

The system enforces minimum 80% test coverage in CI/CD.

**Alternative considered:** Lower thresholds (60-70%) or no enforcement.

**Rationale:**
- Industry data shows 80%+ correlates with significant defect reduction
- High enough to ensure critical paths tested
- Low enough to avoid diminishing returns
- Enforced at CI level, not local development

### Why Centralized Access.txt

All credentials stored in single file (e.g., `~/Documents/Access.txt`) with auto-detection.

**Alternative considered:** Per-project `.env.example` files, 1Password CLI, environment variables.

**Rationale:**
- Single source of truth for developer
- Pattern-based auto-detection reduces manual mapping
- Works across all projects without setup
- Still generates project-specific `.env`

**Sources:** [README.md:358-379]()

---

## System Boundaries and Limitations

### What Claude Bootstrap Does

- Provides TDD guardrails and iterative workflow automation
- Enforces complexity constraints and quality gates
- Manages credentials and security scanning
- Coordinates multi-developer work through shared state
- Adapts skills based on project type

### What Claude Bootstrap Does NOT Do

- Replace code review by humans (augments, doesn't replace)
- Guarantee bug-free code (reduces defects, doesn't eliminate)
- Make architectural decisions (enforces constraints, requires human judgment)
- Work without installed CLIs (requires gh, vercel, supabase)
- Support languages beyond Python/TypeScript (skill-limited)

### Known Edge Cases

- Ralph loop may hit max iterations on truly complex problems → requires human decomposition
- Multi-developer conflicts detected but not auto-resolved → requires human coordination  
- Secret detection is pattern-based → can have false positives/negatives
- Coverage threshold can be met with poor quality tests → requires code review

**Sources:** [README.md:615-695]()

---

## Related Documentation

For deeper understanding of specific subsystems:

- Installation and first-time setup: [Installation](#2.1)
- Project initialization walkthrough: [Initializing Your First Project](#2.2)
- TDD workflow mechanics: [TDD Workflow (RED-GREEN-VALIDATE)](#3.2)
- Ralph loop implementation details: [Ralph Loop: Iterative Development](#4.1)
- Skills system architecture: [Skills Architecture](#5.1)
- Security implementation: [Security Architecture](#6.1)
- Team features: [Multi-Developer Coordination](#8.1)
- Command reference: [Commands Reference](#9.1)
- Extending the system: [Extending Claude Bootstrap](#9.3)

**Sources:** [README.md:1-713]()

---

# Page: Quick Start

# Quick Start

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [install.sh](install.sh)

</details>



This page provides a streamlined path to installing Claude Bootstrap and initializing your first project. It covers the essential steps from cloning the repository to running your first TDD loop.

For detailed installation instructions, see [Installation](#2.1). For comprehensive project initialization guidance, see [Initializing Your First Project](#2.2). For understanding the underlying development philosophy, see [Core Concepts](#3).

---

## Prerequisites

Before installing Claude Bootstrap, ensure the following CLI tools are installed and authenticated:

| Tool | Installation | Authentication |
|------|--------------|----------------|
| **GitHub CLI** | `brew install gh` | `gh auth login` |
| **Vercel CLI** | `npm i -g vercel` | `vercel login` |
| **Supabase CLI** | `brew install supabase/tap/supabase` | `supabase login` |

The `/initialize-project` command validates these CLIs during project setup. Missing tools trigger warnings with installation instructions.

**Sources:** [README.md:499-513]()

---

## Installation Overview

### Step 1: Clone and Run Installer

```bash
git clone https://github.com/alinaqi/claude-bootstrap.git ~/.claude-bootstrap
cd ~/.claude-bootstrap && ./install.sh
```

The `install.sh` script copies files to `~/.claude/`:

| Source | Destination | Contents |
|--------|-------------|----------|
| `commands/*.md` | `~/.claude/commands/` | Command definitions |
| `skills/*.md` | `~/.claude/skills/` | 41+ skill files |
| `hooks/*` | `~/.claude/hooks/` | Git hook templates |
| `scripts/install-hooks.sh` | `~/.claude/install-hooks.sh` | Hook installer |

**Installation Flow Diagram**

```mermaid
graph TB
    REPO["~/.claude-bootstrap/<br/>(Git Repository)"]
    INSTALL["install.sh"]
    
    subgraph "Installation Targets"
        COMMANDS["~/.claude/commands/<br/>initialize-project.md<br/>check-contributors.md<br/>code-review.md<br/>update-code-index.md"]
        SKILLS["~/.claude/skills/<br/>base.md<br/>security.md<br/>python.md<br/>typescript.md<br/>(41+ total files)"]
        HOOKS["~/.claude/hooks/<br/>pre-commit<br/>pre-push"]
        INSTALLER["~/.claude/install-hooks.sh"]
    end
    
    REPO -->|Execute| INSTALL
    INSTALL -->|"cp commands/*.md"| COMMANDS
    INSTALL -->|"cp skills/*.md"| SKILLS
    INSTALL -->|"cp hooks/*"| HOOKS
    INSTALL -->|"cp scripts/install-hooks.sh"| INSTALLER
    
    INSTALL -->|Check| PLUGIN["Ralph Loop Plugin<br/>~/.claude/plugins/.../ralph-loop/"]
```

After installation, commands become available globally in any Claude Code session via the `/` prefix (e.g., `/initialize-project`, `/check-contributors`).

**Sources:** [install.sh:1-66](), [README.md:54-63]()

---

## Project Initialization Overview

### Step 2: Initialize Project

In any project directory (new or existing):

```bash
claude
> /initialize-project
```

The initialization command executes a multi-phase setup process:

**Initialization Flow Diagram**

```mermaid
graph LR
    START["/initialize-project"]
    
    subgraph "Phase 1: Validation"
        CLI["Validate CLIs<br/>gh, vercel, supabase"]
        CREDS["Check Access.txt<br/>(Optional)"]
    end
    
    subgraph "Phase 2: Configuration"
        QUESTIONS["Interactive Questions<br/>Language?<br/>Framework?<br/>AI-first?<br/>Database?"]
        SELECT["Skill Selection<br/>Base on answers"]
    end
    
    subgraph "Phase 3: Repository"
        GHCHECK["GitHub Repo Check"]
        GHCREATE["Create/Connect Repo"]
    end
    
    subgraph "Phase 4: Structure"
        COPYSKILLS["Copy Skills<br/>~/.claude/skills/<br/>→ .claude/skills/"]
        CREATESPECS["Create _project_specs/<br/>features/<br/>todos/<br/>team/"]
        CREATECI["Create .github/workflows/<br/>quality.yml<br/>security.yml"]
        CREATEMD["Generate CLAUDE.md"]
    end
    
    START --> CLI
    CLI --> CREDS
    CREDS --> QUESTIONS
    QUESTIONS --> SELECT
    SELECT --> GHCHECK
    GHCHECK --> GHCREATE
    GHCREATE --> COPYSKILLS
    COPYSKILLS --> CREATESPECS
    CREATESPECS --> CREATECI
    CREATECI --> CREATEMD
```

**Sources:** [README.md:64-69]()

---

## Generated Project Structure

After initialization, the project contains:

```
your-project/
├── .claude/
│   └── skills/              # Project-specific skills
│       ├── base.md
│       ├── security.md
│       ├── credentials.md
│       ├── [language].md    # python.md or typescript.md
│       └── [framework].md   # react-web.md, fastapi.md, etc.
├── .github/
│   └── workflows/
│       ├── quality.yml      # Lint + Type + Test (80% coverage)
│       └── security.yml     # TruffleHog + Dependency audit
├── _project_specs/
│   ├── overview.md          # Project vision
│   ├── features/            # Feature specifications
│   ├── todos/
│   │   ├── active.md        # Current work items
│   │   └── completed.md     # Finished work items
│   └── team/                # Team coordination (if needed)
│       ├── state.md
│       ├── contributors.md
│       └── handoffs/
├── scripts/
│   ├── verify-tooling.sh    # CLI validation
│   └── security-check.sh    # Pre-commit security
└── CLAUDE.md                # Claude instructions
```

**Project Structure Creation Mapping**

```mermaid
graph TB
    INIT["/initialize-project"]
    
    subgraph "Skill Selection Logic"
        LANG["Language?<br/>→ python.md OR typescript.md"]
        FW["Framework?<br/>→ react-web.md<br/>→ fastapi.md<br/>→ nodejs-backend.md"]
        AI["AI-first?<br/>→ agentic-development.md<br/>→ llm-patterns.md"]
        DB["Database?<br/>→ supabase.md<br/>→ database-schema.md"]
    end
    
    subgraph "Always Copied"
        CORE["Core Skills<br/>base.md<br/>security.md<br/>credentials.md<br/>session-management.md<br/>code-review.md<br/>commit-hygiene.md<br/>code-deduplication.md<br/>team-coordination.md<br/>project-tooling.md"]
    end
    
    subgraph "Project Files Created"
        PROJSKILLS[".claude/skills/"]
        SPECS["_project_specs/<br/>overview.md<br/>features/<br/>todos/active.md<br/>todos/completed.md"]
        CI[".github/workflows/<br/>quality.yml<br/>security.yml"]
        CLAUDEMD["CLAUDE.md"]
    end
    
    INIT --> LANG
    INIT --> FW
    INIT --> AI
    INIT --> DB
    INIT --> CORE
    
    LANG --> PROJSKILLS
    FW --> PROJSKILLS
    AI --> PROJSKILLS
    DB --> PROJSKILLS
    CORE --> PROJSKILLS
    
    INIT --> SPECS
    INIT --> CI
    INIT --> CLAUDEMD
```

**Sources:** [README.md:296-317]()

---

## Skill Loading by Project Type

The initialization command selects skills based on your answers:

| Question | Answer | Skills Loaded |
|----------|--------|---------------|
| **Language?** | Python | `python.md` |
| | TypeScript | `typescript.md` |
| **Framework?** | React | `react-web.md` + `ui-web.md` |
| | React Native | `react-native.md` + `ui-mobile.md` |
| | Next.js | `react-web.md` + `supabase-nextjs.md` |
| | FastAPI | `python.md` + `fastapi.md` + `supabase-python.md` |
| | Node.js Backend | `nodejs-backend.md` + `supabase-node.md` |
| **AI-first?** | Yes | `agentic-development.md` + `llm-patterns.md` + `ai-models.md` |
| **E2E Testing?** | Yes | `playwright-testing.md` + `ui-testing.md` |
| **Integrations?** | Stripe | `web-payments.md` |
| | PostHog | `posthog-analytics.md` |
| | Reddit Ads | `reddit-api.md` + `reddit-ads.md` |

All projects receive the 10 core skills: `base.md`, `security.md`, `credentials.md`, `session-management.md`, `code-review.md`, `commit-hygiene.md`, `code-deduplication.md`, `team-coordination.md`, `project-tooling.md`, `iterative-development.md`.

**Sources:** [README.md:397-466]()

---

## First Workflow: Feature Development

After initialization, start your first feature:

**First Feature Development Flow**

```mermaid
graph TB
    INIT["Project Initialized<br/>CLAUDE.md + Skills loaded"]
    
    subgraph "Define Feature"
        DESC["Describe Feature<br/>'Add user authentication'"]
        SPEC["Claude creates<br/>_project_specs/features/auth.md"]
        TODO["Claude creates<br/>_project_specs/todos/active.md<br/>with atomic todos"]
    end
    
    subgraph "TDD Loop (Automatic)"
        RED["RED Phase<br/>Write failing tests<br/>test/auth.test.ts"]
        VERIFY["Verify tests fail<br/>npm test"]
        GREEN["GREEN Phase<br/>Implement minimum code<br/>src/auth.ts"]
        PASS["Run tests again<br/>npm test"]
        VALIDATE["VALIDATE Phase<br/>npm run lint<br/>npm run typecheck<br/>coverage ≥ 80%"]
    end
    
    subgraph "Completion"
        MOVE["Move todo<br/>active.md → completed.md"]
        REVIEW["/code-review<br/>Pre-push validation"]
        PUSH["git push"]
    end
    
    INIT --> DESC
    DESC --> SPEC
    SPEC --> TODO
    TODO --> RED
    RED --> VERIFY
    VERIFY -->|"Tests fail ✓"| GREEN
    VERIFY -->|"Tests pass ✗"| RED
    GREEN --> PASS
    PASS -->|"Tests pass ✓"| VALIDATE
    PASS -->|"Tests fail"| GREEN
    VALIDATE -->|"Pass"| MOVE
    VALIDATE -->|"Fail"| GREEN
    MOVE --> REVIEW
    REVIEW -->|"Critical/High issues"| GREEN
    REVIEW -->|"Clean"| PUSH
```

### Example First Request

After initialization, simply describe what you want:

```
Add email validation to the signup form
```

Claude automatically:
1. Creates feature spec in `_project_specs/features/signup-validation.md`
2. Generates atomic todos in `_project_specs/todos/active.md`
3. Runs `/ralph-loop` with TDD phases
4. Iterates until tests pass + lint clean + coverage ≥ 80%
5. Moves completed todos to `_project_specs/todos/completed.md`

You do **not** need to manually invoke `/ralph-loop`. The `iterative-development.md` skill configures Claude to automatically structure work as iterative TDD loops.

**Sources:** [README.md:71-100](), [README.md:321-343]()

---

## Verification Commands

After initialization, verify the setup:

| Check | Command | Expected Output |
|-------|---------|-----------------|
| **Skills loaded** | `ls .claude/skills/` | Lists 10+ skill files |
| **Commands available** | In Claude: `/` | Shows `/initialize-project`, `/code-review`, etc. |
| **GitHub connected** | `git remote -v` | Shows GitHub repository URL |
| **CI configured** | `ls .github/workflows/` | Shows `quality.yml`, `security.yml` |
| **Specs created** | `ls _project_specs/` | Shows `overview.md`, `features/`, `todos/` |

**Sources:** [README.md:296-317]()

---

## Next Steps

| Goal | Action |
|------|--------|
| **Start first feature** | Describe what you want Claude to build |
| **Understand TDD workflow** | See [TDD Workflow (RED-GREEN-VALIDATE)](#3.2) |
| **Learn Ralph loops** | See [Ralph Loop: Iterative Development](#4.1) |
| **Configure team coordination** | See [Multi-Developer Coordination](#8.1) |
| **Add integrations** | See [Integration Skills](#7) |
| **Customize skills** | See [Extending Claude Bootstrap](#9.3) |

For detailed installation troubleshooting, see [Installation](#2.1). For step-by-step project initialization, see [Initializing Your First Project](#2.2).

**Sources:** [README.md:467-496]()

---

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [install.sh](install.sh)

</details>



## Purpose and Scope

This document covers the installation of Claude Bootstrap's global files and commands onto your local system. Installation is a one-time setup that copies skills, commands, and git hooks to `~/.claude/` for use across all projects. For guidance on initializing individual projects after installation, see [Initializing Your First Project](#2.2).

---

## Prerequisites

Before running the installer, ensure the following CLI tools are installed and authenticated. Claude Bootstrap validates these during project initialization to configure deployments and repository management.

### Required CLI Tools

| Tool | Installation | Authentication | Purpose |
|------|-------------|----------------|---------|
| **GitHub CLI** (`gh`) | `brew install gh` | `gh auth login` | Repository creation, PR management |
| **Vercel CLI** | `npm i -g vercel` | `vercel login` | Frontend deployment automation |
| **Supabase CLI** | `brew install supabase/tap/supabase` | `supabase login` | Database migrations, Edge Functions |

The [scripts/verify-tooling.sh]() script checks for these tools during project initialization. Missing tools trigger warnings but do not block installation.

**Sources:** [README.md:497-513]()

---

## Installation Process

### Step 1: Clone Repository

```bash
git clone https://github.com/alinaqi/claude-bootstrap.git ~/.claude-bootstrap
cd ~/.claude-bootstrap
```

The repository must be cloned to `~/.claude-bootstrap` as the installer script uses this path as the source directory.

### Step 2: Run Installer

```bash
./install.sh
```

The installer is idempotent—running it multiple times is safe and overwrites existing files with the latest versions.

### Installation Flow Diagram

```mermaid
graph TB
    START["User runs ./install.sh"]
    DETECT["Detect SCRIPT_DIR<br/>$(pwd)"]
    MKDIR["Create directories:<br/>~/.claude/commands<br/>~/.claude/skills<br/>~/.claude/hooks<br/>~/.claude/plugins"]
    
    COPY_CMD["Copy commands/*.md<br/>→ ~/.claude/commands/"]
    COPY_SKILLS["Copy skills/*.md<br/>→ ~/.claude/skills/"]
    COPY_HOOKS["Copy hooks/*<br/>→ ~/.claude/hooks/<br/>chmod +x"]
    COPY_INSTALLER["Copy scripts/install-hooks.sh<br/>→ ~/.claude/install-hooks.sh<br/>chmod +x"]
    
    CHECK_RALPH["Check for ralph-loop plugin<br/>~/.claude/plugins/marketplaces/"]
    RALPH_FOUND{{"Plugin exists?"}}
    MSG_FOUND["✓ Ralph Loop available"]
    MSG_MISSING["⚠ Update marketplace first"]
    
    COMPLETE["✓ Installation complete"]
    
    START --> DETECT
    DETECT --> MKDIR
    MKDIR --> COPY_CMD
    COPY_CMD --> COPY_SKILLS
    COPY_SKILLS --> COPY_HOOKS
    COPY_HOOKS --> COPY_INSTALLER
    COPY_INSTALLER --> CHECK_RALPH
    CHECK_RALPH --> RALPH_FOUND
    RALPH_FOUND -->|Yes| MSG_FOUND
    RALPH_FOUND -->|No| MSG_MISSING
    MSG_FOUND --> COMPLETE
    MSG_MISSING --> COMPLETE
```

**Sources:** [install.sh:1-66]()

---

## Directory Structure Created

The installer creates the following structure in your home directory:

```
~/.claude/
├── commands/           # Custom slash commands
│   ├── initialize-project.md
│   ├── check-contributors.md
│   ├── code-review.md
│   ├── update-code-index.md
│   └── [additional commands]
├── skills/            # Global skill repository
│   ├── base.md
│   ├── security.md
│   ├── python.md
│   ├── typescript.md
│   └── [41 total skills]
├── hooks/             # Git hook templates
│   ├── pre-commit
│   └── pre-push
└── install-hooks.sh   # Per-project hook installer
```

### Commands Installed

The following slash commands become globally available in Claude Code after installation:

| Command | File | Purpose |
|---------|------|---------|
| `/initialize-project` | [commands/initialize-project.md]() | Project scaffolding and setup |
| `/check-contributors` | [commands/check-contributors.md]() | Team coordination state check |
| `/code-review` | [commands/code-review.md]() | Pre-push code analysis |
| `/update-code-index` | [commands/update-code-index.md]() | Regenerate semantic capability index |

**Sources:** [install.sh:19-22](), [README.md:58-62]()

### File Copy Operations

```mermaid
graph LR
    subgraph "Source: ~/.claude-bootstrap"
        SRC_CMD["commands/*.md"]
        SRC_SKILLS["skills/*.md"]
        SRC_HOOKS["hooks/*"]
        SRC_SCRIPT["scripts/install-hooks.sh"]
    end
    
    subgraph "Destination: ~/.claude"
        DEST_CMD["commands/"]
        DEST_SKILLS["skills/"]
        DEST_HOOKS["hooks/"]
        DEST_ROOT["./"]
    end
    
    SRC_CMD -->|"cp"| DEST_CMD
    SRC_SKILLS -->|"cp"| DEST_SKILLS
    SRC_HOOKS -->|"cp + chmod +x"| DEST_HOOKS
    SRC_SCRIPT -->|"cp + chmod +x"| DEST_ROOT
```

**Sources:** [install.sh:19-35]()

---

## Ralph Loop Plugin Installation

The Ralph Loop plugin provides the iterative TDD loop system. It is distributed separately through the Claude Code marketplace.

### Installation Steps

1. **Update Marketplace** (if first time):
   ```
   /update-marketplace
   ```

2. **Install Plugin**:
   ```
   /plugin install ralph-loop@claude-plugins-official
   ```

### Troubleshooting: Source Path Error

If you encounter `Source path does not exist: .../ralph-wiggum`, this indicates a cache mismatch between the old plugin name and the new marketplace name.

**Fix with symlink:**
```bash
ln -s ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop \
      ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-wiggum
```

Then retry the installation command.

**Sources:** [README.md:101-117]()

---

## Verification

After installation completes, verify the setup:

### 1. Check Directory Structure

```bash
ls -la ~/.claude/
# Should show: commands/, skills/, hooks/, install-hooks.sh
```

### 2. Count Installed Files

```bash
# Commands (8 expected)
ls -1 ~/.claude/commands/*.md | wc -l

# Skills (41 expected)
ls -1 ~/.claude/skills/*.md | wc -l
```

### 3. Verify Command Availability

Open Claude Code in any directory and type `/` to see available commands. You should see:
- `/initialize-project`
- `/check-contributors`
- `/code-review`
- `/update-code-index`

### 4. Check Hook Executability

```bash
test -x ~/.claude/install-hooks.sh && echo "✓ Hook installer executable"
test -x ~/.claude/hooks/pre-commit && echo "✓ Pre-commit hook executable"
test -x ~/.claude/hooks/pre-push && echo "✓ Pre-push hook executable"
```

**Sources:** [install.sh:21-31]()

---

## Updating Installation

To update Claude Bootstrap to the latest version:

```bash
cd ~/.claude-bootstrap
git pull
./install.sh
```

The installer overwrites existing files in `~/.claude/` with the latest versions. This does not affect existing project configurations—projects use their local `.claude/skills/` directories copied during initialization.

To propagate updates to existing projects, run `/initialize-project` again in each project directory. See [Initializing Your First Project](#2.2) for details on project-level setup.

**Sources:** [README.md:485-495]()

---

## Installation Output Example

Successful installation produces the following output:

```
Installing Claude Bootstrap...

✓ Installed commands:
  - /initialize-project
  - /check-contributors
  - /code-review
  - /update-code-index
  - /ralph-loop
  - /cancel-ralph
  - /audit-duplicates
  
✓ Installed 41 skills
✓ Installed git hooks (templates)

✓ Ralph Loop plugin available in marketplace
  To install: /install-plugin ralph-loop (in Claude Code)

════════════════════════════════════════════════════════════════
  Installation complete!
════════════════════════════════════════════════════════════════

Usage:
  1. Open any project folder
  2. Run: claude
  3. Type: /initialize-project

Commands installed:
  /initialize-project   - Full project setup
  /check-contributors   - Team coordination
  /update-code-index    - Regenerate code index

Git Hooks (per-project):
  cd your-project && ~/.claude/install-hooks.sh
```

**Sources:** [install.sh:48-65]()

---

## Next Steps

After successful installation:

1. **Initialize a project** - See [Initializing Your First Project](#2.2)
2. **Review core concepts** - See [Development Philosophy](#3.1)
3. **Understand TDD workflow** - See [TDD Workflow (RED-GREEN-VALIDATE)](#3.2)

The global installation is now complete. Commands and skills are available for use in any project through the `/initialize-project` command, which copies selected skills to individual project directories based on language, framework, and feature selections.

---

# Page: Initializing Your First Project

# Initializing Your First Project

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [commands/initialize-project.md](commands/initialize-project.md)

</details>



This document guides you through the `/initialize-project` command, which sets up Claude Bootstrap in any project directory. This command handles project detection, skill selection, security configuration, and repository setup. For information about installing Claude Bootstrap itself, see [Installation](#2.1). For the development philosophy and TDD workflow that govern initialized projects, see [Development Philosophy](#3.1) and [TDD Workflow](#3.2).

## Overview

The `/initialize-project` command is idempotent and works for both new and existing projects. It performs five main operations:

| Operation | New Project | Existing Project |
|-----------|-------------|------------------|
| **Project Detection** | Identifies as new, creates full structure | Detects existing setup, offers update |
| **CLI Validation** | Checks `gh`, `vercel`, `supabase` authentication | Checks authentication, skips if already configured |
| **Skill Selection** | Asks questions to determine skills | Auto-detects from existing files, asks for updates |
| **Structure Creation** | Creates `.claude/skills/`, `_project_specs/`, scripts | Adds missing directories, preserves existing files |
| **Repository Setup** | Creates GitHub repo, configures deployment | Skips if already configured |

**Sources:** [commands/initialize-project.md:1-30](), [README.md:52-69]()

## Prerequisites Verification

Before initialization begins, the command validates required CLI tools:

```bash
# GitHub CLI authentication check
gh auth status

# Vercel CLI authentication check
vercel whoami

# Supabase CLI authentication check
supabase projects list
```

If authentication fails, the command displays installation instructions and offers to skip that tool. This validation is implemented in [commands/initialize-project.md:40-57]().

**Validation Script Generated:** The initialization creates `scripts/verify-tooling.sh` which re-runs these checks on demand [commands/initialize-project.md:217-263]().

**Sources:** [commands/initialize-project.md:38-57](), [commands/initialize-project.md:217-263]()

## Initialization Flow

### Phase Execution Sequence

```mermaid
graph TB
    START["Start: /initialize-project"]
    
    DETECT["Phase 1: Detect Project State"]
    CHECK_CLAUDE["Check .claude/skills/"]
    CHECK_GIT["Check git remote"]
    CHECK_PKG["Check package.json / pyproject.toml"]
    CLASSIFY["Classify: New | Existing+Skills | Existing+Code"]
    
    VALIDATE["Phase 2: Validate CLI Tools"]
    GH_CHECK["gh auth status"]
    VERCEL_CHECK["vercel whoami"]
    SUPA_CHECK["supabase projects list"]
    
    QUESTIONS["Phase 3: Project Questions"]
    Q_DESC["What are you building?"]
    Q_LANG["Language/runtime?"]
    Q_TYPE["Project type?"]
    Q_AI["AI-first?"]
    Q_FW["Framework?"]
    Q_DB["Database?"]
    Q_DEPLOY["Deployment?"]
    Q_REPO["Repository setup?"]
    
    SETUP["Phase 4: Execute Setup"]
    DIRS["Create directory structure"]
    SKILLS["Copy skills from ~/.claude/skills/"]
    GITIGNORE["Create/update .gitignore"]
    ENV["Create .env.example"]
    SCRIPTS["Create verify-tooling.sh, security-check.sh"]
    CLAUDE_MD["Create/update CLAUDE.md"]
    SPECS["Create _project_specs/ files"]
    WORKFLOWS["Create GitHub Actions workflows"]
    HOOKS["Install pre-commit + pre-push hooks"]
    REPO_SETUP["GitHub repository setup"]
    DEPLOY_INIT["Initialize deployment (Vercel/Supabase)"]
    
    SUMMARY["Phase 5: Summary"]
    SHOW_CREATED["Display created files"]
    SHOW_UPDATED["Display updated files"]
    SHOW_UNCHANGED["Display preserved files"]
    
    NEXT["Phase 6: Next Steps"]
    NEW_PROMPT["Prompt for first feature"]
    EXISTING_PROMPT["Offer continue/review options"]
    
    START --> DETECT
    DETECT --> CHECK_CLAUDE --> CHECK_GIT --> CHECK_PKG --> CLASSIFY
    CLASSIFY --> VALIDATE
    
    VALIDATE --> GH_CHECK --> VERCEL_CHECK --> SUPA_CHECK --> QUESTIONS
    
    QUESTIONS --> Q_DESC --> Q_LANG --> Q_TYPE --> Q_AI --> Q_FW --> Q_DB --> Q_DEPLOY --> Q_REPO
    Q_REPO --> SETUP
    
    SETUP --> DIRS --> SKILLS --> GITIGNORE --> ENV --> SCRIPTS --> CLAUDE_MD --> SPECS --> WORKFLOWS --> HOOKS --> REPO_SETUP --> DEPLOY_INIT
    DEPLOY_INIT --> SUMMARY
    
    SUMMARY --> SHOW_CREATED --> SHOW_UPDATED --> SHOW_UNCHANGED --> NEXT
    
    NEXT --> NEW_PROMPT
    NEXT --> EXISTING_PROMPT
```

**Sources:** [commands/initialize-project.md:9-36](), [commands/initialize-project.md:60-128](), [commands/initialize-project.md:131-726]()

### Project State Detection

The command first determines the current project state by checking for existing files:

```mermaid
graph LR
    CHECK_START["Check Project Files"]
    
    HAS_SKILLS{"Has .claude/skills/?"}
    HAS_CLAUDEMD{"Has CLAUDE.md?"}
    HAS_CODE{"Has package.json or pyproject.toml?"}
    HAS_REMOTE{"Has git remote?"}
    
    NEW["Classification: NEW"]
    EXISTING_SKILLS["Classification: EXISTING_SKILLS"]
    EXISTING_CODE["Classification: EXISTING_CODE"]
    
    ACTION_NEW["Action: Full setup"]
    ACTION_UPDATE["Action: Update skills"]
    ACTION_ADD["Action: Add Claude setup"]
    
    CHECK_START --> HAS_SKILLS
    HAS_SKILLS -->|No| HAS_CLAUDEMD
    HAS_SKILLS -->|Yes| EXISTING_SKILLS
    
    HAS_CLAUDEMD -->|No| HAS_CODE
    HAS_CLAUDEMD -->|Yes| EXISTING_SKILLS
    
    HAS_CODE -->|No| NEW
    HAS_CODE -->|Yes| EXISTING_CODE
    
    NEW --> ACTION_NEW
    EXISTING_SKILLS --> ACTION_UPDATE
    EXISTING_CODE --> ACTION_ADD
```

The command displays its classification to the user:

- **New project**: "Detected new project - will do full setup"
- **Existing with skills**: "Detected existing Claude project - will update skills and add any missing structure"
- **Existing codebase**: "Detected existing codebase - will add Claude setup while preserving your code"

**Sources:** [commands/initialize-project.md:9-35]()

## Project Configuration Questions

The command asks a series of questions to determine which skills and configurations to apply. For existing projects with `CLAUDE.md`, it reads current configuration first and asks what to update.

### Question Flow and Auto-Detection

```mermaid
graph TB
    Q1["Q1: What are you building?<br/>1-2 sentence description"]
    SKIP_Q1["Skip if CLAUDE.md exists<br/>Show current, ask if update"]
    
    Q2["Q2: Language/Runtime?<br/>Python | TypeScript | JavaScript | Multiple"]
    DETECT_Q2["Auto-detect from package.json<br/>or pyproject.toml"]
    
    Q3["Q3: Project Type?<br/>Backend API | Frontend Web | Mobile | Full Stack | CLI | Library"]
    DETECT_Q3["Auto-detect from dependencies"]
    
    Q4["Q4: AI-first application?<br/>Yes (LLMs handle core logic) | No"]
    DETECT_Q4["Check for anthropic/openai<br/>in dependencies"]
    
    Q5["Q5: Framework?<br/>Based on previous answers"]
    DETECT_Q5["Auto-detect from dependencies"]
    Q5_BACKEND["Backend:<br/>FastAPI | Flask | Django<br/>Express | Fastify | Hono"]
    Q5_FRONTEND["Frontend Web:<br/>React (Vite) | Next.js"]
    Q5_MOBILE["Mobile:<br/>React Native | Expo"]
    
    Q6["Q6: Database?<br/>Supabase (Postgres) | None/SQLite | Other"]
    SKIP_Q6["Skip if supabase/ exists"]
    
    Q7["Q7: Deployment?<br/>Vercel | Render | Other"]
    SKIP_Q7["Skip if vercel.json or<br/>render.yaml exists"]
    
    Q8["Q8: Repository Setup?<br/>Create new | Connect existing | Skip"]
    SKIP_Q8["Skip if git remote configured"]
    Q8_CREATE["If creating:<br/>- Repo name?<br/>- Public or private?"]
    
    Q1 --> SKIP_Q1
    SKIP_Q1 --> Q2
    Q2 --> DETECT_Q2 --> Q3
    Q3 --> DETECT_Q3 --> Q4
    Q4 --> DETECT_Q4 --> Q5
    Q5 --> DETECT_Q5
    Q5 --> Q5_BACKEND
    Q5 --> Q5_FRONTEND
    Q5 --> Q5_MOBILE
    Q5_BACKEND --> Q6
    Q5_FRONTEND --> Q6
    Q5_MOBILE --> Q6
    Q6 --> SKIP_Q6 --> Q7
    Q7 --> SKIP_Q7 --> Q8
    Q8 --> SKIP_Q8
    Q8 --> Q8_CREATE
```

**Sources:** [commands/initialize-project.md:60-128]()

### Skill Selection Logic

Based on the answers, the command copies specific skills from `~/.claude/skills/` to `.claude/skills/`:

```mermaid
graph TB
    MASTER["~/.claude/skills/<br/>Master Skill Repository"]
    
    CORE["Core Skills<br/>(Always copied)"]
    CORE_FILES["base.md<br/>security.md<br/>project-tooling.md<br/>session-management.md<br/>code-review.md<br/>commit-hygiene.md<br/>code-deduplication.md<br/>team-coordination.md<br/>credentials.md<br/>iterative-development.md"]
    
    LANG["Language Skills<br/>(Based on Q2)"]
    LANG_PY["python.md"]
    LANG_TS["typescript.md"]
    
    TYPE["Framework Skills<br/>(Based on Q3, Q5)"]
    TYPE_RN["React Native:<br/>typescript.md +<br/>react-native.md"]
    TYPE_RW["React Web:<br/>typescript.md +<br/>react-web.md"]
    TYPE_NB["Node Backend:<br/>typescript.md +<br/>nodejs-backend.md"]
    TYPE_FS["Full Stack:<br/>typescript.md +<br/>nodejs-backend.md +<br/>react-web.md"]
    
    AI["AI Skills<br/>(If Q4 = Yes)"]
    AI_FILES["agentic-development.md<br/>llm-patterns.md<br/>ai-models.md"]
    
    UI["UI Skills<br/>(Based on Q3)"]
    UI_WEB["ui-web.md<br/>ui-testing.md"]
    UI_MOBILE["ui-mobile.md<br/>ui-testing.md"]
    UI_E2E["playwright-testing.md<br/>(if E2E needed)"]
    
    DB["Database Skills<br/>(Based on Q6)"]
    DB_SUPA["supabase.md<br/>+ supabase-[framework].md"]
    
    PROJECT[".claude/skills/<br/>Project Skills<br/>(Overwritten on each init)"]
    
    MASTER --> CORE --> CORE_FILES --> PROJECT
    MASTER --> LANG --> LANG_PY --> PROJECT
    LANG --> LANG_TS --> PROJECT
    MASTER --> TYPE --> TYPE_RN --> PROJECT
    TYPE --> TYPE_RW --> PROJECT
    TYPE --> TYPE_NB --> PROJECT
    TYPE --> TYPE_FS --> PROJECT
    MASTER --> AI --> AI_FILES --> PROJECT
    MASTER --> UI --> UI_WEB --> PROJECT
    UI --> UI_MOBILE --> PROJECT
    UI --> UI_E2E --> PROJECT
    MASTER --> DB --> DB_SUPA --> PROJECT
```

**Key Behaviors:**
- Core skills are **always copied** and **overwritten** with latest versions
- Skills are copied based on logical combinations (e.g., React Native gets both `typescript.md` AND `react-native.md`)
- Full Stack projects receive multiple framework skills
- Skills in `.claude/skills/` are overwritten on each initialization to propagate updates

**Sources:** [commands/initialize-project.md:145-167](), [README.md:296-317]()

## Generated Project Structure

### Directory Structure

The command creates the following structure:

```mermaid
graph TB
    ROOT["your-project/"]
    
    CLAUDE_DIR[".claude/"]
    SKILLS["skills/"]
    SKILL_FILES["base.md<br/>security.md<br/>project-tooling.md<br/>session-management.md<br/>[language].md<br/>[framework].md"]
    
    GITHUB_DIR[".github/"]
    WORKFLOWS["workflows/"]
    QUALITY["quality.yml"]
    SECURITY["security.yml"]
    
    SPECS_DIR["_project_specs/"]
    FEATURES["features/"]
    TODOS["todos/"]
    TODOS_FILES["active.md<br/>backlog.md<br/>completed.md"]
    SESSION["session/"]
    SESSION_FILES["current-state.md<br/>decisions.md<br/>code-landmarks.md<br/>archive/"]
    PROMPTS["prompts/"]
    TEAM["team/<br/>(created by /check-contributors)"]
    TEAM_FILES["state.md<br/>contributors.md<br/>handoffs/"]
    
    DOCS["docs/"]
    
    SCRIPTS["scripts/"]
    SCRIPT_FILES["verify-tooling.sh<br/>security-check.sh"]
    
    ROOT_FILES["CLAUDE.md<br/>.gitignore<br/>.env.example"]
    
    ROOT --> CLAUDE_DIR
    CLAUDE_DIR --> SKILLS
    SKILLS --> SKILL_FILES
    
    ROOT --> GITHUB_DIR
    GITHUB_DIR --> WORKFLOWS
    WORKFLOWS --> QUALITY
    WORKFLOWS --> SECURITY
    
    ROOT --> SPECS_DIR
    SPECS_DIR --> FEATURES
    SPECS_DIR --> TODOS
    TODOS --> TODOS_FILES
    SPECS_DIR --> SESSION
    SESSION --> SESSION_FILES
    SPECS_DIR --> PROMPTS
    SPECS_DIR --> TEAM
    TEAM --> TEAM_FILES
    
    ROOT --> DOCS
    ROOT --> SCRIPTS
    SCRIPTS --> SCRIPT_FILES
    ROOT --> ROOT_FILES
```

**Sources:** [commands/initialize-project.md:133-143](), [README.md:296-317]()

### Key Files and Their Purposes

| File Path | Purpose | When Created |
|-----------|---------|--------------|
| `.claude/skills/*.md` | Coding guardrails and patterns | Always copied from `~/.claude/skills/` |
| `CLAUDE.md` | Main instructions for Claude, skill references | Created if missing, updated if exists |
| `.gitignore` | Security-critical entries (`.env`, secrets) | Created if missing, appended if incomplete |
| `.env.example` | Template for environment variables | Created based on project type |
| `scripts/verify-tooling.sh` | CLI authentication verification | Always created/overwritten |
| `scripts/security-check.sh` | Pre-commit secret scanning | Always created/overwritten |
| `.github/workflows/quality.yml` | Lint, type-check, test, coverage enforcement | Created based on language |
| `.github/workflows/security.yml` | TruffleHog secret scan, dependency audit | Always created |
| `_project_specs/overview.md` | Project vision, goals, success metrics | Created if missing, never overwritten |
| `_project_specs/todos/active.md` | Current work in progress | Created if missing, never overwritten |
| `_project_specs/session/current-state.md` | Live session state tracking | Created if missing, never overwritten |
| `_project_specs/session/decisions.md` | Architectural decision log (append-only) | Created if missing, never overwritten |

**Preservation Policy:** Files in `_project_specs/` are **never overwritten**. Only missing files are created. This ensures your work is preserved when updating skills.

**Sources:** [commands/initialize-project.md:145-267](), [commands/initialize-project.md:439-617]()

### CLAUDE.md Structure

The generated `CLAUDE.md` file serves as the primary instruction file for Claude:

```markdown
# CLAUDE.md

## Skills
Read and follow these skills before writing any code:
- .claude/skills/base.md
- .claude/skills/security.md
- .claude/skills/project-tooling.md
- .claude/skills/session-management.md
- .claude/skills/[language].md
- .claude/skills/[framework].md (if applicable)
- .claude/skills/llm-patterns.md (if AI-first)

## Project Overview
[Description from question 1]

## Tech Stack
- Language: [X]
- Framework: [X]
- Database: [X]
- Deployment: [X]
- Testing: [X]

## Key Commands
[Language/framework-specific commands]

## Documentation
- `docs/` - Technical documentation
- `_project_specs/` - Project specifications and todos

## Atomic Todos
All work is tracked in `_project_specs/todos/`:
- `active.md` - Current work
- `backlog.md` - Future work
- `completed.md` - Done (for reference)

## Session Management
[Session management instructions from session-management.md skill]

## Project-Specific Patterns
[Any specific patterns for this project]
```

For existing projects, the command:
- Preserves **Project Overview**, **Tech Stack**, and **Project-Specific Patterns** sections
- Updates **Skills** list to reflect current `.claude/skills/` contents
- Updates **Key Commands** section with latest commands

**Sources:** [commands/initialize-project.md:320-438]()

### Security Configuration Files

#### .gitignore Security Entries

The command ensures these entries exist in `.gitignore` [commands/initialize-project.md:168-200]():

```gitignore
# Environment files - NEVER commit
.env
.env.*
!.env.example

# Secrets
*.pem
*.key
*.p12
credentials.json
secrets.json
service-account*.json

# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build outputs
dist/
build/

# IDE
.idea/
.vscode/settings.json
.DS_Store
```

#### .env.example Template

Created based on project type [commands/initialize-project.md:202-214]():

```bash
# .env.example - Copy to .env and fill in values
# Server-side only (NEVER prefix with VITE_ or NEXT_PUBLIC_)
DATABASE_URL=
ANTHROPIC_API_KEY=

# Client-side safe (public, non-sensitive)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

**Sources:** [commands/initialize-project.md:168-214]()

### GitHub Actions Workflows

#### quality.yml

Created based on the selected language. Enforces:
- Linting with auto-fix
- Type checking
- Test suite execution
- **80% coverage minimum** (CI fails below threshold)

#### security.yml

Always created, runs [commands/initialize-project.md:619-668]():

```yaml
name: Security

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday

jobs:
  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Detect secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./

  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node
        if: hashFiles('package.json') != ''
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: NPM Audit
        if: hashFiles('package.json') != ''
        run: npm audit --audit-level=high
      - name: Setup Python
        if: hashFiles('pyproject.toml') != ''
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Safety check
        if: hashFiles('pyproject.toml') != ''
        run: pip install safety && safety check
```

**Sources:** [commands/initialize-project.md:619-668]()

### Pre-Commit and Pre-Push Hooks

The initialization installs two types of hooks:

#### Pre-Commit Hooks

**For Python projects** [commands/initialize-project.md:670-676]():
- Creates `.pre-commit-config.yaml` with ruff, mypy, pytest

**For TypeScript/JavaScript projects** [commands/initialize-project.md:675-676]():
- Sets up Husky + lint-staged

#### Pre-Push Hook (Code Review)

**Always installed** [commands/initialize-project.md:678-698]():

```bash
# Copied from ~/.claude/hooks/pre-push to .git/hooks/pre-push
# Behavior:
# - Runs /code-review before every git push
# - Blocks push if Critical (🔴) or High (🟠) severity issues found
# - Allows push with advisory for Medium (🟡) and Low (🟢) issues
```

To disable: `rm .git/hooks/pre-push`

**Sources:** [commands/initialize-project.md:670-698](), [README.md:176-209]()

## Repository and Deployment Setup

### GitHub Repository Creation

If repository setup was selected and not already configured:

**Create new repository** [commands/initialize-project.md:700-707]():
```bash
git init  # if needed
git add .
git commit -m "Initial project setup"
gh repo create [repo-name] --[public|private] --source=. --remote=origin --push
```

**Connect to existing** [commands/initialize-project.md:709-713]():
```bash
git remote add origin https://github.com/[owner]/[repo].git
git push -u origin main
```

### Deployment Initialization

**Vercel** (if `vercel.json` missing) [commands/initialize-project.md:715-720]():
```bash
vercel link
```

**Supabase** (if `supabase/` directory missing) [commands/initialize-project.md:722-725]():
```bash
supabase init
```

**Sources:** [commands/initialize-project.md:699-726]()

## Understanding the Output

### Update Summary (Existing Project)

For projects that already have Claude Bootstrap setup:

```
Updated:
✓ Skills updated to latest versions
  - base.md (updated)
  - typescript.md (updated)
  - react-web.md (updated)
✓ Pre-push code review hook (installed/updated)

Added:
✓ llm-patterns.md (new skill added)
✓ _project_specs/prompts/ (new directory)

Unchanged:
- CLAUDE.md (preserved your customizations)
- _project_specs/todos/ (preserved your todos)
- Git repository (already configured)
```

### New Project Summary

For newly initialized projects:

```
Created:
✓ .claude/skills/ with 5 skill files
✓ CLAUDE.md
✓ _project_specs/ structure
✓ scripts/verify-tooling.sh
✓ .github/workflows/quality.yml
✓ Pre-commit hooks configured
✓ Pre-push code review hook (blocks on Critical/High issues)
✓ GitHub repository: https://github.com/[owner]/[repo]

Quick Start:
# Verify setup
./scripts/verify-tooling.sh

# Install dependencies
[appropriate command]

# Start development
[appropriate command]
```

**Sources:** [commands/initialize-project.md:729-775]()

## Next Steps After Initialization

The command provides different prompts based on project type:

### For New Projects

```
Project initialized! Ready to start building.

Would you like to start defining your first feature? I'll help you:
1. Create a feature spec in `_project_specs/features/`
2. Break it down into atomic todos with validation and test cases
3. Add them to `_project_specs/todos/active.md`

What's the first feature you want to build?
```

This transitions into the spec-driven development workflow. See [Atomic Todos and Project Specs](#3.4) for the todo format.

### For Existing Projects

```
Project updated with latest skills!

What would you like to do?
1. Review changes to skills (see what's new)
2. Add a new feature spec
3. Continue working on existing todos
4. Something else
```

**Sources:** [commands/initialize-project.md:777-798](), [README.md:52-69]()

## Updating Skills System-Wide

To update skills globally and propagate to all projects:

```bash
# Pull latest skills from repository
cd ~/.claude-bootstrap
git pull

# Reinstall to ~/.claude/
./install.sh
```

Then in any existing project:

```bash
claude
> /initialize-project
```

The command will:
- Overwrite all skills in `.claude/skills/` with latest versions from `~/.claude/skills/`
- Preserve `CLAUDE.md` customizations
- Preserve all `_project_specs/` files
- Add any new skills or directories introduced since last initialization

**Sources:** [commands/initialize-project.md:802-821](), [README.md:485-495]()

## Common Scenarios

### Scenario 1: Brand New Project

```bash
mkdir my-app && cd my-app
claude
> /initialize-project
```

Command performs:
1. Detects empty directory → classifies as NEW
2. Validates CLI tools
3. Asks all 8 configuration questions
4. Creates full directory structure
5. Copies skills based on answers
6. Creates GitHub repository
7. Initializes deployment
8. Prompts for first feature spec

### Scenario 2: Existing Codebase Without Claude

```bash
cd existing-app  # Has package.json, src/, etc.
claude
> /initialize-project
```

Command performs:
1. Detects code but no `.claude/` → classifies as EXISTING_CODE
2. Auto-detects language from `package.json`
3. Auto-detects framework from dependencies
4. Asks only non-detectable questions
5. Adds `.claude/skills/`, `_project_specs/`, scripts
6. Preserves all existing code and configuration
7. Offers to continue with existing todos or add new features

### Scenario 3: Updating Skills in Claude Project

```bash
cd my-claude-project  # Has .claude/skills/
claude
> /initialize-project
```

Command performs:
1. Detects `.claude/skills/` → classifies as EXISTING_SKILLS
2. Reads current `CLAUDE.md` configuration
3. Asks which configuration to update
4. **Overwrites all skills** in `.claude/skills/` with latest from `~/.claude/skills/`
5. Adds any new skills introduced since last init
6. Preserves `CLAUDE.md` customizations
7. Preserves all `_project_specs/` files
8. Updates hooks if changed

**Sources:** [commands/initialize-project.md:9-36](), [README.md:467-495]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



This page introduces the fundamental principles that underpin Claude Bootstrap: **test-driven development as mandatory workflow**, **simplicity rules enforced at the file/function level**, **atomic work units tracked through todos**, and **session management for context preservation**. These four pillars work together to create an AI-native development system that keeps code comprehensible and verifiable.

For detailed implementation workflows, see [Development Workflow](#4). For specific skill modules that implement these concepts, see [Skills System](#5).

---

## The Four Pillars

Claude Bootstrap is built on four non-negotiable principles:

| Pillar | Enforcement Mechanism | Exit Condition |
|--------|----------------------|----------------|
| **TDD-First** | Tests must fail before implementation | All tests passing + 80% coverage |
| **Simplicity Limits** | Pre-commit validation blocks violations | ≤20 lines/function, ≤200 lines/file |
| **Atomic Todos** | Tracked in `_project_specs/todos/active.md` | Moved to `completed.md` after validation |
| **Session Context** | Checkpoint triggers preserve state | `current-state.md` updated after major tasks |

These principles address the fundamental problem: **AI can generate infinite code, but humans must comprehend it**. The bottleneck has shifted from generation to comprehension, and these guardrails keep complexity manageable.

**Sources:** [README.md:3-40](), [skills/base.md:1-10]()

---

## Test-Driven Development: RED-GREEN-VALIDATE

Every feature and bug fix follows a mandatory three-phase workflow. Tests are written first, must fail initially, then implementation makes them pass, followed by quality validation.

### TDD Workflow Diagram

```mermaid
stateDiagram-v2
    [*] --> RED: "Write Tests First"
    
    RED --> RunTests1: "Execute test command"
    
    RunTests1 --> VerifyFail: "Check results"
    
    VerifyFail --> FixTests: "Tests pass (INVALID)"
    VerifyFail --> GREEN: "Tests fail ✓ (proves validity)"
    
    FixTests --> RED: "Rewrite tests"
    
    GREEN --> Implement: "Write minimum code"
    
    Implement --> RunTests2: "Execute test command"
    
    RunTests2 --> GREEN: "Tests still fail"
    RunTests2 --> VALIDATE: "Tests pass ✓"
    
    VALIDATE --> Lint: "npm run lint"
    
    Lint --> TypeCheck: "Pass"
    Lint --> GREEN: "Fail"
    
    TypeCheck --> Coverage: "npm run typecheck"
    TypeCheck --> GREEN: "Fail"
    
    Coverage --> CheckThreshold: "npm test -- --coverage"
    Coverage --> GREEN: "Fail"
    
    CheckThreshold --> Complete: "Coverage ≥ 80% ✓"
    CheckThreshold --> AddTests: "Coverage < 80%"
    
    AddTests --> RunTests2
    
    Complete --> MoveTodo: "Update TDD Execution Log"
    
    MoveTodo --> [*]: "active.md → completed.md"
```

### Phase Breakdown

| Phase | Commands (Node.js) | Commands (Python) | Exit Criteria |
|-------|-------------------|-------------------|---------------|
| **RED** | `npm test -- --grep "feature"` | `pytest -k "feature" -v` | All tests FAIL |
| **GREEN** | `npm test -- --grep "feature"` | `pytest -k "feature" -v` | All tests PASS |
| **VALIDATE** | `npm run lint && npm run typecheck && npm test -- --coverage` | `ruff check . && mypy . && pytest --cov --cov-fail-under=80` | Lint clean, types valid, coverage ≥80% |

**Why tests must fail first:** If tests pass immediately, they don't validate the requirement. For bug fixes, a passing test proves it wouldn't have caught the bug. The RED phase validates test validity before implementation begins.

**Sources:** [skills/base.md:186-214](), [skills/base.md:216-253](), [README.md:321-342]()

---

## TDD Execution Tracking

Every todo includes a `TDD Execution Log` table that documents each phase:

```markdown
### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| RED | `npm test -- --grep "email validation"` | 5 tests failed ✓ | 2024-01-15 14:23 |
| GREEN | `npm test -- --grep "email validation"` | 5 tests passed ✓ | 2024-01-15 14:45 |
| VALIDATE | `npm run lint && npm run typecheck && npm test -- --coverage` | Pass, 84% ✓ | 2024-01-15 14:47 |
| COMPLETE | Moved to completed.md | ✓ | 2024-01-15 14:48 |
```

This provides an audit trail proving TDD workflow was followed.

**Sources:** [skills/base.md:172-178](), [skills/base.md:377-384]()

---

## Bug Fix Workflow: Test Gap Analysis

Bug fixes follow a specialized TDD workflow that identifies why existing tests didn't catch the issue:

```mermaid
flowchart TD
    BugReport["Bug Reported"]
    
    Diagnose["1. DIAGNOSE<br/>Run existing tests"]
    
    CheckTests{"Do any<br/>tests fail?"}
    
    GapAnalysis["Test Gap Analysis<br/>Document what was missed"]
    
    WriteTest["2. RED<br/>Write failing test<br/>that reproduces bug"]
    
    VerifyFails{"New test<br/>FAILS?"}
    
    FixBug["3. GREEN<br/>Fix the bug"]
    
    RunAgain["Run new test"]
    
    CheckPass{"Test<br/>PASSES?"}
    
    Validate["4. VALIDATE<br/>Full test suite<br/>Lint + TypeCheck"]
    
    Complete["Mark bug fixed<br/>Move to completed.md"]
    
    BugReport --> Diagnose
    Diagnose --> CheckTests
    
    CheckTests -->|"Yes"| FixBug
    CheckTests -->|"No (gap!)"| GapAnalysis
    
    GapAnalysis --> WriteTest
    WriteTest --> VerifyFails
    
    VerifyFails -->|"No"| WriteTest
    VerifyFails -->|"Yes ✓"| FixBug
    
    FixBug --> RunAgain
    RunAgain --> CheckPass
    
    CheckPass -->|"No"| FixBug
    CheckPass -->|"Yes ✓"| Validate
    
    Validate --> Complete
    Complete --> End["[*]"]
```

### Test Gap Analysis Format

```markdown
### Test Gap Analysis
- Existing test coverage: `signup.test.ts` - only tested valid emails
- Gap identified: Missing test for email without domain
- New test needed: Add case for partial emails ("user@")
```

**Anti-patterns blocked:**
- ❌ Fixing bug without writing test first
- ❌ Writing test after fix (can't prove it catches bug)
- ❌ Skipping gap analysis (misses systemic issue)

**Sources:** [skills/base.md:272-297](), [skills/base.md:299-334]()

---

## Simplicity Rules: Hard Constraints

Complexity is measured through quantifiable limits enforced at every file modification. These are not guidelines—they are blocking conditions.

### Constraint Hierarchy Diagram

```mermaid
graph TB
    subgraph Function["Function Level"]
        F1["max_lines: 20"]
        F2["max_params: 3"]
        F3["max_nesting: 2"]
        F4["single_responsibility: true"]
    end
    
    subgraph File["File Level"]
        FL1["max_lines: 200"]
        FL2["max_functions: 10"]
        FL3["one_export_focus: true"]
    end
    
    subgraph Module["Module Level"]
        M1["max_directory_depth: 3"]
        M2["clear_boundaries: true"]
        M3["no_circular_deps: true"]
    end
    
    Function --> File
    File --> Module
    
    F1 -.->|"Enforced by"| PreCommit["Pre-commit Hook"]
    F2 -.->|"Enforced by"| PreCommit
    F3 -.->|"Enforced by"| PreCommit
    FL1 -.->|"Enforced by"| PreCommit
    FL2 -.->|"Enforced by"| PreCommit
    M3 -.->|"Enforced by"| TypeChecker["Type Checker"]
```

### Enforcement Protocol

Before completing ANY file, Claude must execute this check:

```markdown
1. Count total lines - if > 200, STOP and split
2. Count functions - if > 10, STOP and split
3. Check each function length - if any > 20 lines, STOP and decompose
4. Check parameter counts - if any > 3, STOP and refactor
```

If limits are exceeded, this blocking message appears:

```
⚠️ FILE SIZE VIOLATION DETECTED

src/auth/handlers.ts has 247 lines (limit: 200)

Splitting into:
- src/auth/handlers/login.ts - Login flow
- src/auth/handlers/signup.ts - Signup flow
- src/auth/handlers/password-reset.ts - Password reset
```

**Never defer refactoring.** The system stops and refactors immediately.

**Sources:** [skills/base.md:9-50](), [README.md:344-357]()

---

## Constraint Reference Table

| Constraint | Limit | Violation Action | Rationale |
|------------|-------|------------------|-----------|
| **Lines per function** | 20 max | Decompose immediately | Function should fit in viewport |
| **Parameters per function** | 3 max | Use options object or decompose | Reduces cognitive load |
| **Nesting depth** | 2 levels max | Flatten with early returns | Reduces complexity |
| **Lines per file** | 200 max | Split by responsibility | File should be comprehensible in one read |
| **Functions per file** | 10 max | Split by domain | Maintains focus |
| **Directory depth** | 3 levels max | Flatten structure | Easier navigation |
| **Test coverage** | 80% min | Block CI merge | Ensures validation |

**Sources:** [skills/base.md:13-23](), [README.md:349-357]()

---

## Atomic Work Units: The Todo System

All work is tracked as atomic todos in `_project_specs/todos/`. Each todo is self-contained, testable, and moves through a state machine from `active.md` to `completed.md`.

### Todo State Machine

```mermaid
stateDiagram-v2
    [*] --> Backlog: "Feature spec created"
    
    Backlog --> Active: "Todo claimed by developer"
    
    Active --> InProgress: "Work started"
    
    InProgress --> Blocked: "Blocker encountered"
    
    Blocked --> InProgress: "Blocker resolved"
    
    InProgress --> Validation: "Implementation complete"
    
    Validation --> InProgress: "Tests fail"
    Validation --> InProgress: "Lint errors"
    Validation --> InProgress: "Coverage < 80%"
    
    Validation --> Completed: "All gates pass ✓"
    
    Completed --> [*]: "Moved to completed.md"
    
    note right of Validation
        Gates:
        - All tests pass
        - Lint clean
        - TypeCheck pass
        - Coverage ≥ 80%
    end note
```

### Todo File Structure Mapping

```mermaid
graph LR
    FeatureSpec["_project_specs/features/<br/>feature-name.md"]
    
    Backlog["_project_specs/todos/<br/>backlog.md"]
    
    Active["_project_specs/todos/<br/>active.md"]
    
    Completed["_project_specs/todos/<br/>completed.md"]
    
    FeatureSpec -->|"Break down into"| Backlog
    Backlog -->|"Claim & move"| Active
    Active -->|"Complete & move"| Completed
    
    Active -.->|"Referenced in"| CurrentState["_project_specs/session/<br/>current-state.md"]
    
    Active -.->|"Logs tracked in"| TDDLog["TDD Execution Log<br/>(embedded in todo)"]
```

### Todo Format Structure

Every todo follows this mandatory format:

```markdown
## [TODO-042] Add email validation to signup form

**Status:** pending | in-progress | blocked | done
**Priority:** high | medium | low
**Estimate:** XS | S | M | L | XL

### Description
One paragraph describing what needs to be done.

### Acceptance Criteria
- [ ] Email field shows error for invalid format
- [ ] Form cannot submit with invalid email

### Test Cases
| Input | Expected Output | Notes |
|-------|-----------------|-------|
| user@example.com | Valid | Standard email |
| notanemail | Invalid, show error | No @ symbol |

### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| RED | `npm test -- --grep "email validation"` | 5 tests failed ✓ | - |
| GREEN | `npm test -- --grep "email validation"` | 5 tests passed ✓ | - |
| VALIDATE | `npm run lint && npm test -- --coverage` | Pass, 84% ✓ | - |
```

**Key fields:**
- **Test Cases table**: Defines expected behavior before writing tests
- **TDD Execution Log**: Audit trail proving TDD was followed
- **Dependencies**: Links to blocking/blocked todos

**Sources:** [skills/base.md:138-178](), [skills/base.md:343-384](), [README.md:531-558]()

---

## Todo Rules and Sizing

| Rule | Description | Enforcement |
|------|-------------|-------------|
| **Atomic** | Single, completable unit of work | If requires "and" in description, split |
| **Testable** | Has validation criteria and test cases | Blocking condition for completion |
| **Sized** | Estimated as XS/S/M/L/XL | If > M, decompose into smaller todos |
| **Independent** | Minimize dependencies | Document in Dependencies section |
| **Tracked** | Moves through active.md → completed.md | Never delete, always move |

**Anti-patterns blocked:**
- ❌ Marking complete with failing tests
- ❌ Skipping TDD Execution Log
- ❌ Oversized todos (> M estimate)
- ❌ Deleting completed todos (lose history)

**Sources:** [skills/base.md:180-185](), [README.md:531-558]()

---

## Project Specs Directory Structure

The `_project_specs/` directory provides the organizational framework for all project context:

```
_project_specs/
├── overview.md              # Project vision and goals
├── features/                # Feature specifications
│   ├── feature-a.md
│   └── feature-b.md
├── todos/                   # Atomic work tracking
│   ├── active.md            # Current sprint/focus
│   ├── backlog.md           # Future work
│   └── completed.md         # Done items (reference)
├── session/                 # Session state
│   ├── current-state.md     # Live session context
│   ├── decisions.md         # Key decisions log
│   ├── code-landmarks.md    # Important code locations
│   └── archive/             # Past session summaries
├── team/                    # Multi-developer coordination
│   ├── state.md             # Active sessions, claimed todos
│   ├── contributors.md      # Team members, focus areas
│   └── handoffs/            # Context transfer notes
└── prompts/                 # LLM prompt specs (AI-first projects)
```

**Separation of concerns:**
- `docs/` directory: Technical code documentation (architecture, API reference)
- `_project_specs/` directory: Business requirements, features, work tracking
- `CLAUDE.md`: Claude-specific instructions and skill references

**Sources:** [skills/base.md:99-135](), [templates/CLAUDE.md:1-113]()

---

## Session Management and Context Preservation

Session management ensures Claude can resume work from any point with full context. The system uses tiered checkpointing based on work significance.

### Checkpoint Trigger Matrix

```mermaid
flowchart TD
    TaskComplete["Task Completed"]
    
    CheckDecision{"Architectural<br/>decision made?"}
    CheckToolCalls{"Tool calls<br/>> 10?"}
    CheckMajor{"Major feature<br/>completed?"}
    
    LogDecision["Log to<br/>decisions.md"]
    
    FullCheckpoint["Full checkpoint to<br/>current-state.md"]
    
    ArchiveSession["Archive to<br/>session/archive/"]
    
    QuickUpdate["Quick update to<br/>current-state.md"]
    
    TaskComplete --> CheckDecision
    
    CheckDecision -->|"Yes"| LogDecision
    CheckDecision -->|"No"| CheckToolCalls
    
    LogDecision --> CheckToolCalls
    
    CheckToolCalls -->|"Yes"| FullCheckpoint
    CheckToolCalls -->|"No"| CheckMajor
    
    FullCheckpoint --> CheckMajor
    
    CheckMajor -->|"Yes"| ArchiveSession
    CheckMajor -->|"No"| QuickUpdate
    
    ArchiveSession --> End["Continue"]
    QuickUpdate --> End
```

### Session Files and Their Roles

| File | Purpose | Update Frequency | Content Type |
|------|---------|------------------|--------------|
| `current-state.md` | Live session context | After every task | Current todos, recent changes, next steps |
| `decisions.md` | Architectural decisions log | On major decisions | Why choices were made, alternatives considered |
| `code-landmarks.md` | Important code locations | When structure changes | Key files, entry points, critical functions |
| `archive/*.md` | Historical sessions | On major feature completion | Archived session summaries |

**Session start protocol:**
1. Read `_project_specs/session/current-state.md`
2. Check `_project_specs/todos/active.md`
3. Review `decisions.md` for recent architectural choices
4. Continue from documented "Next Steps"

**Session end protocol:**
1. Archive current session if major feature complete
2. Update `current-state.md` with handoff notes
3. Ensure next steps are specific and actionable
4. Log any architectural decisions made

**Sources:** [skills/base.md:457-478](), [skills/base.md:118-122]()

---

## How the Four Pillars Work Together

The four core concepts form a reinforcing system where each pillar supports the others:

```mermaid
graph TB
    TDD["TDD Workflow<br/>(RED-GREEN-VALIDATE)"]
    Simplicity["Simplicity Rules<br/>(20/200 line limits)"]
    Atomic["Atomic Todos<br/>(tracked work units)"]
    Session["Session Management<br/>(context preservation)"]
    
    TDD -->|"Validates"| Simplicity
    TDD -->|"Completion criteria for"| Atomic
    TDD -->|"Test logs captured in"| Session
    
    Simplicity -->|"Keeps tests"| TDD
    Simplicity -->|"Keeps todos"| Atomic
    Simplicity -->|"Keeps context"| Session
    
    Atomic -->|"Defines scope for"| TDD
    Atomic -->|"Enforces size via"| Simplicity
    Atomic -->|"Tracked in"| Session
    
    Session -->|"Preserves TDD logs from"| TDD
    Session -->|"Records violations of"| Simplicity
    Session -->|"Tracks progress of"| Atomic
    
    Result["Result:<br/>Maintainable,<br/>Comprehensible,<br/>AI-friendly Codebase"]
    
    TDD --> Result
    Simplicity --> Result
    Atomic --> Result
    Session --> Result
```

**Reinforcement examples:**

1. **TDD validates Simplicity**: Tests are easier to write for simple functions. If a function is hard to test, it's too complex—simplicity rules catch this before implementation.

2. **Simplicity keeps Todos atomic**: A 20-line function limit naturally constrains todo scope. Oversized todos violate simplicity rules during implementation, forcing decomposition.

3. **Atomic Todos define TDD scope**: Each todo's test cases table directly maps to the RED phase. The TDD Execution Log provides completion audit trail.

4. **Session Management captures all three**: `current-state.md` tracks active todos, `decisions.md` logs simplicity refactorings, TDD logs preserved for resumability.

**Why this matters for AI**: Large Language Models lose coherence as context grows. These four pillars keep the system within Claude's comprehension window—any engineer (or AI) can understand the entire system in one session.

**Sources:** [README.md:3-40](), [README.md:42-50](), [skills/base.md:1-10]()

---

## Default Behavior: Automatic Iterative TDD

With Claude Bootstrap skills loaded, Claude automatically transforms implementation requests into iterative TDD loops via the Ralph Wiggum system (see [Ralph Loop: Iterative Development](#4.1)).

### Auto-Invocation Rules

| User Request Type | Claude Action | Example |
|-------------------|---------------|---------|
| Feature implementation | Invoke `/ralph-loop` with TDD workflow | "Add email validation" → Auto-loop until tests pass |
| Bug fix | Invoke `/ralph-loop` with test gap analysis | "Fix login bug" → Find gap, write test, loop until fixed |
| Refactoring | Invoke `/ralph-loop` with test safety net | "Refactor auth module" → Loop with existing tests as guard |
| Explanation/question | Normal response (no loop) | "Explain how auth works" → Direct answer |
| One-line fix | Normal response (no loop) | "Fix typo in error message" → Direct fix |

### Opt-Out Phrases

Users can explicitly skip automatic loops:
- "Just explain..." → Explanation only
- "Quick fix..." → One-liner without loop
- "Don't loop..." → Explicit opt-out
- "Help me understand..." → Learning/discussion

**Sources:** [skills/base.md:499-579](), [templates/CLAUDE.md:10-62](), [README.md:71-100]()

---

## Integration with CLAUDE.md

Every project includes a `CLAUDE.md` file that configures Claude's default behavior:

```markdown
## Default Behavior: Automatic Iterative TDD

For any implementation task, automatically use Ralph Wiggum loops with TDD.

### Auto-Invoke Rules
When I ask you to implement something:
1. DO NOT just start coding
2. DO automatically invoke /ralph-loop with:
   - Requirements extracted from my request
   - TDD workflow (write failing tests first)
   - Clear completion criteria
   - --max-iterations 25
   - --completion-promise based on task
```

This file lives at the project root and is read by Claude on every session start.

**Sources:** [templates/CLAUDE.md:10-62]()

---

# Page: Development Philosophy

# Development Philosophy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



## Purpose and Scope

This page explains the core philosophy underlying Claude Bootstrap: why it exists, what problems it solves, and the guiding principles that inform its design. This document focuses on the **rationale and motivation** behind the system's constraints and workflows.

For detailed implementation of the TDD workflow, see [TDD Workflow (RED-GREEN-VALIDATE)](#3.2). For enforcement mechanisms of complexity limits, see [Simplicity Rules and Enforcement](#3.3). For the practical workflow of breaking work into units, see [Atomic Todos and Project Specs](#3.4).

---

## The Problem: Code Comprehension is the Bottleneck

Claude Bootstrap exists because **the bottleneck in AI-assisted development has shifted from code generation to code comprehension**. AI can generate infinite code, but humans still need to review, understand, and maintain it.

```mermaid
graph LR
    subgraph "Traditional Development"
        T1["Human Writes Code"]
        T2["Slow but Understandable"]
        T3["Manual Review"]
    end
    
    subgraph "AI-Assisted Without Guardrails"
        A1["AI Generates Code"]
        A2["Fast but Unstructured"]
        A3["Human Cannot Comprehend"]
        A4["Technical Debt Accumulates"]
    end
    
    subgraph "AI-Assisted With Claude Bootstrap"
        C1["AI Generates Code"]
        C2["Fast AND Constrained"]
        C3["Human Can Comprehend"]
        C4["Maintainable System"]
    end
    
    T1 --> T2 --> T3
    A1 --> A2 --> A3 --> A4
    C1 --> C2 --> C3 --> C4
    
    style A4 fill:#f9f9f9
    style C4 fill:#f9f9f9
```

**The fundamental insight**: After hundreds of AI-assisted projects across Node, React, Python, and React Native, three patterns emerged:

1. **Engineers struggle with Claude Code not because of the tool, but because of how they instruct it** - The delta is in the guardrails
2. **Complexity has a ceiling** - There's a point where AI loses coherent understanding of the system. That's a signal, not a failure
3. **Restart is a feature, not failure** - When fixing something increases complexity, restart with learnings. Each iteration is faster

Sources: [README.md:42-50]()

---

## Core Principles

Claude Bootstrap enforces five non-negotiable principles. Each principle addresses a specific failure mode in AI-assisted development.

### Principle Hierarchy

```mermaid
graph TB
    subgraph "1. Iterative Loops by Default"
        P1A["Every task runs in self-referential loop"]
        P1B["Claude iterates autonomously"]
        P1C["Powered by Ralph Wiggum"]
    end
    
    subgraph "2. Tests First, Always"
        P2A["Features: Write tests → Fail → Implement → Pass"]
        P2B["Bugs: Find test gap → Write failing test → Fix → Pass"]
        P2C["No code ships without test that failed first"]
    end
    
    subgraph "3. Simplicity is Non-Negotiable"
        P3A["20 lines per function"]
        P3B["200 lines per file"]
        P3C["3 parameters max"]
    end
    
    subgraph "4. Security by Default"
        P4A["No secrets in code"]
        P4B["No secrets in client env vars"]
        P4C["Dependency scanning + Pre-commit hooks"]
    end
    
    subgraph "5. Code Reviews are Mandatory"
        P5A["Every commit requires /code-review"]
        P5B["Critical + High = blocked"]
        P5C["AI catches what humans miss"]
    end
    
    P1C --> P2C
    P2C --> P3C
    P3C --> P4C
    P4C --> P5C
```

Sources: [README.md:9-39]()

### 1. Iterative Loops by Default

**Principle**: Every task runs in a self-referential loop until tests pass. Claude iterates autonomously. Developers describe **what**, not **how**.

**Rationale**: AI-generated code often requires multiple refinement passes. Without loops, developers must manually re-prompt, breaking flow and losing context. Automatic iteration treats refinement as the default, not an exception.

**Enforcement**: The `ralph-loop` plugin implements stop-hook interception that feeds the same prompt back with updated file states until completion criteria are met.

Sources: [README.md:11-15](), [skills/base.md:499-578]()

### 2. Tests First, Always

**Principle**: Features require tests that fail before implementation. Bug fixes require tests that reproduce the bug before fixing.

**Rationale**: AI can generate tests that always pass (false positives). Requiring tests to fail first proves they actually validate the requirement. For bugs, failing tests prove the test would have caught the issue.

**Enforcement**: The TDD execution log in atomic todos tracks RED (tests fail), GREEN (tests pass), and VALIDATE (quality gates) phases.

Sources: [README.md:17-21](), [skills/base.md:187-214]()

### 3. Simplicity is Non-Negotiable

**Principle**: Hard limits on function length (20 lines), file length (200 lines), and parameter count (3 max). If you can't understand the whole system in one session, it's too complex.

**Rationale**: Complexity correlates with defect rates. Large functions and files reduce AI's ability to maintain coherent context. Measurable constraints prevent the gradual accumulation of incomprehensible code.

**Enforcement**: Pre-completion checks count lines and parameters. Claude must stop and refactor on violations before continuing.

Sources: [README.md:23-27](), [skills/base.md:9-50]()

### 4. Security by Default

**Principle**: No secrets in code, no secrets in client-exposed environment variables, dependency scanning on every PR.

**Rationale**: AI doesn't inherently understand security boundaries. Without explicit rules, it will place API keys in client-side code or commit secrets to version control.

**Enforcement**: Multi-layer defense including `Access.txt` centralized credentials, pre-commit secret scanning, code review checks, and CI validation.

Sources: [README.md:29-32](), [skills/base.md:414-437]()

### 5. Code Reviews are Mandatory

**Principle**: Every commit requires `/code-review` before push. Critical and High severity issues block the push.

**Rationale**: AI catches patterns humans miss (security vulnerabilities, N+1 queries). Humans catch what AI misses (business logic, architectural coherence).

**Enforcement**: Pre-push hooks run `/code-review` and block on Critical/High issues. GitHub Actions run the same check in CI.

Sources: [README.md:34-38]()

---

## Philosophy to Implementation Mapping

The following diagram maps each philosophical principle to the concrete files and systems that enforce it:

```mermaid
graph TB
    subgraph "Philosophical Principles"
        PHIL1["Iterative Loops"]
        PHIL2["Tests First"]
        PHIL3["Simplicity"]
        PHIL4["Security"]
        PHIL5["Code Reviews"]
    end
    
    subgraph "Skills (.claude/skills/)"
        S1["iterative-development.md"]
        S2["base.md TDD Workflow"]
        S3["base.md Simplicity Rules"]
        S4["security.md"]
        S5["credentials.md"]
        S6["code-review.md"]
    end
    
    subgraph "Commands (commands/)"
        C1["/ralph-loop"]
        C2["/code-review"]
    end
    
    subgraph "Automation (scripts/)"
        A1["Pre-commit hooks"]
        A2["Pre-push hooks"]
        A3["security-check.sh"]
    end
    
    subgraph "CI/CD (.github/workflows/)"
        CI1["quality.yml"]
        CI2["security.yml"]
    end
    
    subgraph "State Management (_project_specs/)"
        ST1["todos/active.md"]
        ST2["session/current-state.md"]
        ST3["session/decisions.md"]
    end
    
    PHIL1 --> S1
    PHIL1 --> C1
    S1 --> C1
    
    PHIL2 --> S2
    S2 --> ST1
    
    PHIL3 --> S3
    S3 --> A1
    
    PHIL4 --> S4
    PHIL4 --> S5
    S4 --> A3
    S5 --> A3
    A3 --> A1
    
    PHIL5 --> S6
    S6 --> C2
    C2 --> A2
    
    A1 --> CI1
    A2 --> CI2
    A3 --> CI2
    
    ST1 --> ST2
    ST2 --> ST3
```

Sources: [README.md:296-317](), [skills/base.md:1-50]()

---

## Why AI-Native Development Needs Guardrails

Traditional software development wisdom assumes humans write code slowly with deliberate thought. AI-assisted development inverts this:

| Aspect | Human-Written | AI-Generated Without Guardrails | AI-Generated With Guardrails |
|--------|---------------|----------------------------------|------------------------------|
| **Generation Speed** | Slow | Fast | Fast |
| **Initial Quality** | Variable | Variable | Constrained |
| **Comprehensibility** | High (human wrote it) | Low (no structure) | High (enforced structure) |
| **Test Coverage** | Often skipped | Often missing | Mandatory (TDD-first) |
| **Security** | Manual review needed | High risk | Multi-layer enforcement |
| **Maintainability** | Depends on discipline | Degrades quickly | Preserved by constraints |

### The Comprehension Problem

Without guardrails, AI generates code faster than humans can review it. The system becomes a black box where:
- Functions exceed cognitive load limits (>20 lines)
- Files become scrolling documents (>200 lines)
- Tests are written after implementation (if at all)
- Complexity accumulates invisibly

**Claude Bootstrap's solution**: Measurable constraints that keep code within human comprehension limits. Not "write clean code" (vague), but "20 lines per function" (measurable).

Sources: [README.md:3-6](), [skills/base.md:1-8]()

---

## Architectural Philosophy: Functional Core, Imperative Shell

Claude Bootstrap enforces a specific architectural pattern derived from functional programming principles:

```mermaid
graph TB
    subgraph "Imperative Shell (Side Effects at Boundaries)"
        API["API Routes/Handlers"]
        DB["Database Operations"]
        FS["File System"]
        EXTERNAL["External APIs"]
    end
    
    subgraph "Functional Core (Pure Business Logic)"
        VALIDATE["Validation Functions"]
        TRANSFORM["Data Transformations"]
        COMPUTE["Business Calculations"]
        DECIDE["Decision Logic"]
    end
    
    API --> VALIDATE
    VALIDATE --> TRANSFORM
    TRANSFORM --> COMPUTE
    COMPUTE --> DECIDE
    DECIDE --> DB
    DECIDE --> EXTERNAL
    
    API --> FS
    
    VALIDATE -.->|"Pure: No side effects"| TRANSFORM
    TRANSFORM -.->|"Pure: No side effects"| COMPUTE
    COMPUTE -.->|"Pure: No side effects"| DECIDE
```

**Key principles**:
- **Pure functions for business logic**: No side effects, deterministic, easy to test
- **Side effects only at boundaries**: API calls, database, file system at edges
- **Data in, data out**: Functions transform data, they don't mutate state

**Testing implications**:
- Core functions: 100% coverage, unit tests with no mocks
- Shell functions: Integration tests with real dependencies or stubs

Sources: [skills/base.md:54-69]()

---

## Restart as a Feature, Not Failure

**Counter-intuitive principle**: When fixing a bug increases complexity, restart the implementation with learnings from the first attempt.

### The Complexity Ceiling

There exists a point in every project where AI loses coherent understanding of the system. This manifests as:
- Repetitive fixes that don't solve the root cause
- New bugs introduced while fixing old bugs
- Increasing time per task as complexity grows

**Traditional response**: Push through, refactor later
**Claude Bootstrap response**: Restart is a feature

### Restart Workflow

```mermaid
stateDiagram-v2
    [*] --> FirstAttempt
    FirstAttempt --> WorksWell: Complexity < Ceiling
    FirstAttempt --> HitsWall: Complexity > Ceiling
    
    WorksWell --> [*]: Continue
    
    HitsWall --> DocumentLearnings
    DocumentLearnings --> RestartFresh
    RestartFresh --> SecondAttempt
    
    SecondAttempt --> WorksWell: Faster (has learnings)
    
    note right of DocumentLearnings
        Log to session/decisions.md:
        - What worked
        - What didn't
        - Simplified architecture
    end note
    
    note right of RestartFresh
        New repo with:
        - Same skills
        - Simplified design
        - 2-3x faster
    end note
```

**When to restart**:
1. Fixes take longer than initial implementation
2. New features break existing tests repeatedly
3. Codebase exceeds comprehension in one session

**Learnings to preserve**:
- Architectural decisions (what worked)
- API designs (keep stable interfaces)
- Test cases (business requirements)
- Integration patterns (external services)

Sources: [README.md:42-50]()

---

## Anti-Patterns Explicitly Prevented

Claude Bootstrap's philosophy codifies common failure modes as anti-patterns with automated prevention:

| Anti-Pattern | Why It Happens | How Claude Bootstrap Prevents |
|--------------|----------------|-------------------------------|
| **Tests after implementation** | AI generates working code first, tests feel redundant | TDD execution log requires RED phase before GREEN |
| **Fixing bugs without tests** | Pressure to ship quickly | Bug fix workflow requires test gap analysis first |
| **Large PRs (>400 lines)** | AI generates code fast, commits lag behind | Commit hygiene tracking warns at thresholds |
| **Secrets in code** | AI doesn't understand security boundaries | Multi-layer scanning (pre-commit, code review, CI) |
| **God objects** | Incremental feature additions bloat files | 200-line file limit enforced before completion |
| **Deep nesting** | Natural code structure without constraints | 2-level nesting max, enforced by base.md rules |
| **Missing type safety** | TypeScript/Python type hints are optional | Type checking in VALIDATE phase blocks completion |
| **Silent failures** | AI generates defensive code that swallows errors | Error handling rules: fail fast, fail loud |

Sources: [skills/base.md:82-96](), [skills/base.md:254-263](), [skills/base.md:336-341]()

---

## Measurable Constraints Over Vague Guidance

Traditional code review comments:
- ❌ "This function is too complex"
- ❌ "Add more tests"
- ❌ "Improve error handling"

Claude Bootstrap constraints:
- ✅ "Function exceeds 20 lines (currently 34), decompose"
- ✅ "Coverage at 72% (minimum 80%), add test cases for X, Y"
- ✅ "Error swallowed at line 15, throw or log explicitly"

**Why this matters for AI**: AI cannot improve against vague guidance. Measurable constraints provide clear success criteria that both AI and humans can verify.

### Constraint Enforcement Flow

```mermaid
graph LR
    WRITE["Write/Modify Code"]
    CHECK["Count Lines/Params/Coverage"]
    PASS["Within Limits?"]
    CONTINUE["Continue"]
    STOP["STOP: Refactor"]
    SPLIT["Split File/Function"]
    EXTRACT["Extract Parameters"]
    ADDTEST["Add Test Cases"]
    
    WRITE --> CHECK
    CHECK --> PASS
    PASS -->|Yes| CONTINUE
    PASS -->|No| STOP
    STOP --> SPLIT
    STOP --> EXTRACT
    STOP --> ADDTEST
    SPLIT --> CHECK
    EXTRACT --> CHECK
    ADDTEST --> CHECK
```

Sources: [skills/base.md:9-50]()

---

## Summary: Philosophy in Practice

Claude Bootstrap's development philosophy rests on one core insight: **AI can generate infinite code, but humans have finite comprehension**. Every principle and constraint exists to keep AI-generated code within human understanding limits.

The five principles work together as a system:
1. **Iterative loops** ensure refinement happens automatically
2. **TDD** proves code works and tests are valid
3. **Simplicity rules** keep code comprehensible
4. **Security enforcement** prevents common vulnerabilities
5. **Code reviews** catch what automated checks miss

For implementation details of each principle, see the following pages:
- [TDD Workflow (RED-GREEN-VALIDATE)](#3.2) - The mechanics of test-first development
- [Simplicity Rules and Enforcement](#3.3) - How constraints are checked and enforced
- [Atomic Todos and Project Specs](#3.4) - Breaking work into verifiable units

Sources: [README.md:1-50](), [skills/base.md:1-96]()

---

# Page: TDD Workflow (RED-GREEN-VALIDATE)

# TDD Workflow (RED-GREEN-VALIDATE)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



**Purpose:** This document details the mandatory Test-Driven Development workflow enforced by Claude Bootstrap. It covers the three-phase TDD cycle (RED-GREEN-VALIDATE), execution commands for different technology stacks, error classification that controls loop behavior, and the specialized workflow for bug fixes.

**Scope:** This page focuses on the mechanical workflow of TDD execution. For the philosophical rationale behind TDD-first development, see [Development Philosophy](#3.1). For the Ralph loop automation that executes this workflow iteratively, see [Ralph Loop: Iterative Development](#4.1).

---

## Overview

Claude Bootstrap enforces a strict TDD workflow for all feature development and bug fixes. The workflow consists of three mandatory phases executed in order, with specific validation criteria that must be met before proceeding.

**Core Principle:** Tests must fail before implementation begins. This proves the test validates the requirement and prevents false confidence from tests that always pass.

**Non-Negotiable Rules:**
- Tests are written before any implementation code
- Tests must fail on first execution (RED phase verification)
- Implementation proceeds only after RED phase confirmation
- No todo marked complete without passing all three phases

**Sources:** [skills/base.md:187-214](), [README.md:321-343]()

---

## The Three Phases

### Phase 1: RED - Write Failing Tests

The RED phase establishes test validity by ensuring tests fail before implementation exists.

**Workflow:**

```mermaid
graph TD
    Start["Start Task<br/>(Feature or Bug)"] --> ParseCriteria["Parse Acceptance<br/>Criteria"]
    ParseCriteria --> WriteTests["Write Test Cases<br/>from Test Cases table"]
    WriteTests --> RunTests["Execute: npm test<br/>or pytest"]
    RunTests --> CheckFail{"All Tests<br/>FAIL?"}
    CheckFail -->|Yes| RedConfirmed["✓ RED Phase Complete<br/>Tests validate requirements"]
    CheckFail -->|No| AnalyzePass["Analyze: Why passing?"]
    AnalyzePass --> FixTests["Fix Tests:<br/>- Incorrect assertion?<br/>- Missing setup?<br/>- Wrong test target?"]
    FixTests --> RunTests
    RedConfirmed --> ProceedGreen["Proceed to<br/>GREEN Phase"]
```

**File Locations:**
- Test files follow naming convention: `*.test.ts`, `*.spec.ts`, `test_*.py`
- Tests organized by module: `src/components/__tests__/`, `tests/unit/`

**RED Phase Commands:**

| Stack | Command | Expected Output |
|-------|---------|----------------|
| Node.js/TypeScript | `npm test -- --grep "feature-name"` | All tests fail with specific assertions |
| Python | `pytest -k "feature_name" -v` | All tests fail with traceback |
| React/Next.js | `npm test -- --testPathPattern="ComponentName"` | All component tests fail |

**Why Tests Must Fail First:**
1. **Proves test validity** - A test that passes without implementation doesn't validate anything
2. **Catches test bugs** - Wrong assertions or setup errors surface immediately
3. **Establishes baseline** - Clear "before" state to compare against
4. **For bugs:** Demonstrates the test would have caught the defect

**Anti-Pattern Prevention:**
- ❌ Tests that always pass (tautologies)
- ❌ Tests written after implementation
- ❌ Skipping RED verification
- ❌ Proceeding with partial test failures

**Sources:** [skills/base.md:192-196](), [README.md:327-336]()

---

### Phase 2: GREEN - Minimum Implementation

The GREEN phase implements the simplest code that makes all tests pass, adhering to complexity constraints.

**Workflow:**

```mermaid
graph TD
    RedComplete["RED Phase<br/>Complete"] --> WriteCode["Write Implementation<br/>Minimum code to pass tests"]
    WriteCode --> CheckConstraints{"Meets Simplicity<br/>Rules?"}
    CheckConstraints -->|No| Refactor["Refactor:<br/>- Split long functions (>20 lines)<br/>- Reduce params (>3)<br/>- Extract nested logic (>2 levels)"]
    Refactor --> WriteCode
    CheckConstraints -->|Yes| RunTests["Execute: npm test<br/>or pytest"]
    RunTests --> CheckPass{"All Tests<br/>PASS?"}
    CheckPass -->|No| ClassifyError["Classify Error Type<br/>(See Error Classification)"]
    ClassifyError --> CheckFixable{"Fixable by<br/>Code Change?"}
    CheckFixable -->|Yes - Code Error| WriteCode
    CheckFixable -->|No - Access/Env Error| BlockReport["Generate Blocker Report<br/>Exit loop with action items"]
    CheckPass -->|Yes| GreenConfirmed["✓ GREEN Phase Complete<br/>All tests passing"]
    GreenConfirmed --> ProceedValidate["Proceed to<br/>VALIDATE Phase"]
```

**Simplicity Rules Enforced:**

| Constraint | Limit | Action if Exceeded |
|------------|-------|-------------------|
| Lines per function | 20 | STOP and decompose immediately |
| Parameters per function | 3 | STOP and refactor to options object |
| Nesting depth | 2 levels | STOP and flatten with early returns |
| Lines per file | 200 | STOP and split by responsibility |

**GREEN Phase Commands:**

| Stack | Command | Expected Output |
|-------|---------|----------------|
| Node.js/TypeScript | `npm test -- --grep "feature-name"` | All tests pass (green checkmarks) |
| Python | `pytest -k "feature_name" -v` | All tests pass with PASSED status |
| React/Next.js | `npm test -- --testPathPattern="ComponentName"` | All component tests pass |

**Implementation Guidelines:**
- Write minimum code required - no premature features
- Follow single responsibility principle
- Use descriptive names over comments
- Extract complexity into small functions
- No dead code or commented-out code

**Sources:** [skills/base.md:198-201](), [skills/base.md:9-50](), [README.md:329]()

---

### Phase 3: VALIDATE - Quality Gates

The VALIDATE phase runs comprehensive quality checks: linting, type checking, and coverage verification.

**Workflow:**

```mermaid
graph TD
    GreenComplete["GREEN Phase<br/>Complete"] --> RunLint["Execute Linter<br/>eslint / ruff"]
    RunLint --> CheckLint{"Lint<br/>Clean?"}
    CheckLint -->|No| AutoFix["Attempt Auto-Fix<br/>--fix flag"]
    AutoFix --> CheckFixed{"Fixed?"}
    CheckFixed -->|No| ManualFix["Manual Fix Required<br/>Return to GREEN"]
    CheckFixed -->|Yes| RunTypeCheck["Execute Type Checker<br/>tsc / mypy"]
    CheckLint -->|Yes| RunTypeCheck
    RunTypeCheck --> CheckTypes{"Type Check<br/>Pass?"}
    CheckTypes -->|No| FixTypes["Fix Type Errors<br/>Return to GREEN"]
    CheckTypes -->|Yes| RunCoverage["Execute Coverage Analysis<br/>--coverage flag"]
    RunCoverage --> CheckCoverage{"Coverage<br/>>= 80%?"}
    CheckCoverage -->|No| AddTests["Add Missing Tests<br/>Return to RED"]
    CheckCoverage -->|Yes| ValidateComplete["✓ VALIDATE Phase Complete<br/>Ready to mark done"]
    ValidateComplete --> UpdateTodo["Update TDD Execution Log<br/>Move to completed.md"]
```

**VALIDATE Phase Commands:**

| Stack | Full Validation Command | Components |
|-------|------------------------|------------|
| Node.js/TypeScript | `npm run lint && npm run typecheck && npm test -- --coverage` | eslint → tsc → jest/vitest |
| Python | `ruff check . && mypy . && pytest --cov --cov-fail-under=80` | ruff → mypy → pytest-cov |
| React/Next.js | `npm run lint && npm run typecheck && npm test -- --coverage --watchAll=false` | eslint → tsc → jest |

**Quality Gates:**

```mermaid
graph LR
    subgraph "Quality Gate 1: Linting"
        L1["Code Style<br/>Consistency"]
        L2["Auto-fixable<br/>Issues"]
        L3["Manual<br/>Violations"]
    end
    
    subgraph "Quality Gate 2: Type Safety"
        T1["Type Coverage<br/>100% strict mode"]
        T2["No implicit any"]
        T3["No type errors"]
    end
    
    subgraph "Quality Gate 3: Test Coverage"
        C1["Overall Coverage<br/>>= 80%"]
        C2["Statement Coverage"]
        C3["Branch Coverage"]
        C4["Function Coverage"]
    end
    
    L1 --> L2 --> L3
    L3 --> T1
    T1 --> T2 --> T3
    T3 --> C1
    C1 --> C2 --> C3 --> C4
```

**Coverage Threshold Enforcement:**
- **Minimum 80%** overall coverage required
- CI blocks merges below threshold
- Business logic (core/) should aim for 100%
- Integration tests cover boundaries (API, database)

**Blocking Conditions:**

Tests passing but validation fails:

| Failure Type | Action | Can Complete? |
|--------------|--------|---------------|
| Lint errors | Fix immediately | ❌ No |
| Lint warnings | Advisory only | ✅ Yes (with note) |
| Type errors | Fix immediately | ❌ No |
| Coverage < 80% | Add tests (return to RED) | ❌ No |
| Coverage 75-79% | Add 1-2 tests | ❌ No |
| Coverage >= 80% | Proceed | ✅ Yes |

**Sources:** [skills/base.md:203-207](), [skills/base.md:254-270](), [README.md:516-530]()

---

## Execution Commands by Technology Stack

### Node.js / TypeScript Projects

**Project Structure:**
```
src/
├── components/
│   ├── Button.tsx
│   └── __tests__/
│       └── Button.test.tsx
├── utils/
│   ├── validation.ts
│   └── __tests__/
│       └── validation.test.ts
```

**Commands:**

```bash
# Phase 1: RED - Run specific test
npm test -- --grep "email validation"
npm test -- --testPathPattern="Button"

# Phase 2: GREEN - Run same test
npm test -- --grep "email validation"

# Phase 3: VALIDATE - Full suite
npm run lint          # eslint
npm run typecheck     # tsc --noEmit
npm test -- --coverage --watchAll=false

# Combined validation
npm run lint && npm run typecheck && npm test -- --coverage
```

**Test Framework:** Jest or Vitest
**Linter:** ESLint
**Type Checker:** TypeScript (`tsc`)

**Sources:** [skills/base.md:218-228]()

---

### Python Projects

**Project Structure:**
```
src/
├── services/
│   ├── auth.py
│   └── validation.py
tests/
├── unit/
│   ├── test_auth.py
│   └── test_validation.py
```

**Commands:**

```bash
# Phase 1: RED - Run specific test
pytest -k "email_validation" -v
pytest tests/unit/test_validation.py::test_email_format -v

# Phase 2: GREEN - Run same test
pytest -k "email_validation" -v

# Phase 3: VALIDATE - Full suite
ruff check .          # Linter
mypy .                # Type checker
pytest --cov --cov-fail-under=80

# Combined validation
ruff check . && mypy . && pytest --cov --cov-fail-under=80
```

**Test Framework:** pytest
**Linter:** ruff
**Type Checker:** mypy or pyright

**Sources:** [skills/base.md:230-240]()

---

### React / Next.js Projects

**Project Structure:**
```
src/
├── app/
│   ├── login/
│   │   ├── page.tsx
│   │   └── page.test.tsx
├── components/
│   ├── Form/
│   │   ├── EmailInput.tsx
│   │   └── EmailInput.test.tsx
```

**Commands:**

```bash
# Phase 1: RED - Run component test
npm test -- --testPathPattern="EmailInput"
npm test -- --testPathPattern="page"

# Phase 2: GREEN - Run same test
npm test -- --testPathPattern="EmailInput"

# Phase 3: VALIDATE - Full suite
npm run lint          # eslint
npm run typecheck     # tsc
npm test -- --coverage --watchAll=false

# Combined validation
npm run lint && npm run typecheck && npm test -- --coverage --watchAll=false
```

**Test Framework:** Jest + React Testing Library
**Linter:** ESLint (Next.js config)
**Type Checker:** TypeScript

**Sources:** [skills/base.md:242-252]()

---

## Error Classification and Loop Control

The Ralph loop uses error classification to determine whether to continue iterating or stop and report a blocker.

### Error Classification Logic

```mermaid
graph TD
    TestFail["Test Execution<br/>Failed"] --> ParseError["Parse Error Message<br/>and Stack Trace"]
    ParseError --> ClassifyType{"Error Type?"}
    
    ClassifyType -->|Code Error| CodeError["Logic Bug<br/>Wrong Assertion<br/>Type Mismatch"]
    ClassifyType -->|Access Error| AccessError["Missing API Key<br/>DB Connection Refused<br/>Auth Failed (401)"]
    ClassifyType -->|Environment Error| EnvError["Missing Package<br/>Wrong Node/Python Version<br/>Service Not Running"]
    ClassifyType -->|Network Error| NetError["Timeout<br/>DNS Resolution Failed<br/>Connection Refused"]
    
    CodeError --> Fixable["✓ FIXABLE by Claude<br/>Continue Loop"]
    AccessError --> Unfixable["✗ UNFIXABLE by Claude<br/>Generate Blocker Report"]
    EnvError --> Unfixable
    NetError --> Unfixable
    
    Fixable --> ImplementFix["Modify Code<br/>Update Tests<br/>Fix Types"]
    ImplementFix --> ReturnGreen["Return to<br/>GREEN Phase"]
    
    Unfixable --> GenerateReport["Generate Report:<br/>- Error type<br/>- Root cause<br/>- Action items<br/>- Fix command"]
    GenerateReport --> ExitLoop["Exit Loop<br/>Human Action Required"]
```

**Error Classification Table:**

| Error Type | Examples | Claude Fixes? | Action |
|------------|----------|---------------|--------|
| **Code Error** | Logic bug, wrong assertion, type mismatch, undefined variable | ✅ Yes | Continue loop, fix code |
| **Test Error** | Incorrect test setup, wrong mock, missing fixture | ✅ Yes | Continue loop, fix test |
| **Type Error** | Type annotation wrong, missing import, incompatible types | ✅ Yes | Continue loop, fix types |
| **Logic Error** | Off-by-one, wrong operator, incorrect algorithm | ✅ Yes | Continue loop, reimplement |
| **Access Error** | Missing API key, 401 Unauthorized, DB credentials wrong | ❌ No | Stop, report blocker |
| **Network Error** | ECONNREFUSED, DNS failure, timeout | ❌ No | Stop, report blocker |
| **Environment Error** | MODULE_NOT_FOUND, wrong version, service not running | ❌ No | Stop, report blocker |

**Sources:** [README.md:579-612](), [skills/base.md:187-214]()

---

### Blocker Report Format

When Claude encounters an unfixable error, it generates a structured blocker report and exits the loop:

```markdown
🛑 LOOP BLOCKED - Human Action Required

**Error Type:** Access Error
**Error Message:** ECONNREFUSED 127.0.0.1:5432

**Root Cause:**
PostgreSQL database is not running or not accepting connections.

**Required Actions:**
1. Start PostgreSQL: `brew services start postgresql`
2. Verify connection: `psql -U postgres -c "SELECT 1"`
3. Check DATABASE_URL in .env matches running instance
4. Confirm PostgreSQL is listening on port 5432

**After Fixing:**
Run `/ralph-loop` again with the same prompt to resume.

**Context:**
- Currently in GREEN phase (tests failing)
- Test file: `tests/unit/test_user_repository.py`
- Last working state: RED phase confirmed (tests failed as expected)
```

**Common Blockers:**

| Error Message | Cause | Fix Command |
|---------------|-------|-------------|
| `ECONNREFUSED :5432` | PostgreSQL not running | `brew services start postgresql` |
| `ECONNREFUSED :6379` | Redis not running | `brew services start redis` |
| `401 Unauthorized` | Bad API key | Check `.env` file for correct key |
| `MODULE_NOT_FOUND: 'xyz'` | Missing package | `npm install xyz` or `pip install xyz` |
| `Error: spawn tsc ENOENT` | TypeScript not installed | `npm install -D typescript` |

**Sources:** [README.md:589-612]()

---

## Bug Fix Workflow

Bug fixes follow a specialized TDD workflow that includes test gap analysis as the first step.

### Bug Fix Phases

```mermaid
stateDiagram-v2
    [*] --> Diagnose: Bug Reported
    
    Diagnose --> AnalyzeTests: Run Existing Tests
    
    AnalyzeTests --> CheckOutcome: All tests pass?
    
    CheckOutcome --> TestGap: Yes → Test Gap Exists
    CheckOutcome --> TestFails: No → Test Catches Bug
    
    TestGap --> DocumentGap: Document:<br/>- Which tests exist<br/>- What they missed<br/>- Why gap exists
    
    TestFails --> GoodTests: Tests working correctly<br/>No gap
    
    DocumentGap --> WriteFailingTest: RED Phase:<br/>Write test that<br/>reproduces bug
    
    GoodTests --> FixBug: GREEN Phase:<br/>Fix the bug
    
    WriteFailingTest --> RunTest1: Execute new test
    
    RunTest1 --> VerifyFail: Test fails?
    
    VerifyFail --> TestValid: Yes → Test proves<br/>it catches bug
    VerifyFail --> FixTest: No → Test is wrong<br/>Fix test
    
    FixTest --> RunTest1
    
    TestValid --> FixBug
    
    FixBug --> RunTest2: Execute test again
    
    RunTest2 --> VerifyPass: Test passes?
    
    VerifyPass --> FixIncomplete: No → Bug not fixed<br/>Continue fixing
    VerifyPass --> ValidateFull: Yes → Bug fixed
    
    FixIncomplete --> FixBug
    
    ValidateFull --> RunFullSuite: VALIDATE Phase:<br/>Run ALL tests
    
    RunFullSuite --> CheckRegression: Any failures?
    
    CheckRegression --> FixRegression: Yes → Fix broke<br/>something else
    CheckRegression --> QualityGates: No → All tests pass
    
    FixRegression --> FixBug
    
    QualityGates --> RunLint: Lint + TypeCheck
    
    RunLint --> CheckCoverage: Coverage check
    
    CheckCoverage --> Complete: >= 80%
    CheckCoverage --> AddTests: < 80%<br/>Add tests
    
    AddTests --> WriteFailingTest
    
    Complete --> [*]: Bug fixed ✓
```

**Why Test Gap Analysis Matters:**
- If tests pass but bug exists, tests are incomplete
- Documents what the test suite missed
- Prevents similar bugs in the future
- Proves new test would have caught the bug

**Sources:** [skills/base.md:272-296](), [README.md:560-577]()

---

### Bug Report Todo Format

Bug fixes use an extended todo format with test gap analysis:

```markdown
## [BUG-007] Email validation accepts "user@"

**Status:** pending
**Priority:** high
**Reported:** User reported via signup form - partial emails accepted

### Bug Description
**Current Behavior:** Email validation accepts "user@" without domain
**Expected Behavior:** Should reject emails without valid domain

### Reproduction Steps
1. Navigate to signup form
2. Enter "user@" in email field
3. Observe: No validation error shown
4. Expected: Error message "Invalid email format"

### Test Gap Analysis
- **Existing test coverage:** `tests/unit/test_validation.test.ts`
- **Gap identified:** Tests only covered valid emails and completely invalid formats
- **What was missed:** Partial emails (has @ but missing domain)
- **New test needed:** Test case for emails with @ but no domain portion

### Test Cases for Bug
| Input | Current (Bug) | Expected (Fixed) |
|-------|---------------|------------------|
| user@example.com | Valid ✓ | Valid ✓ |
| user@ | Valid ✗ (BUG) | Invalid, show error |
| @example.com | Valid ✗ (BUG) | Invalid, show error |
| user | Invalid ✓ | Invalid ✓ |

### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| DIAGNOSE | `npm test -- --grep "email validation"` | All pass (gap!) | 2024-01-15 10:30 |
| RED | `npm test -- --grep "partial email"` | 2 tests failed ✓ | 2024-01-15 10:35 |
| GREEN | `npm test -- --grep "partial email"` | 2 tests passed ✓ | 2024-01-15 10:42 |
| VALIDATE | `npm run lint && npm test -- --coverage` | Pass, 83% ✓ | 2024-01-15 10:45 |
```

**Bug Fix Anti-Patterns:**
- ❌ Fixing without a test - Bug will likely return
- ❌ Writing test after fix - Can't prove test catches the bug
- ❌ Skipping test gap analysis - Misses why tests didn't catch it
- ❌ Only testing the fix - Must run full test suite for regressions

**Sources:** [skills/base.md:299-341]()

---

## TDD Execution Log Tracking

Every todo and bug fix maintains a TDD execution log showing each phase's command and result.

### Log Format

```markdown
### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| RED | `npm test -- --grep "email validation"` | 5 tests failed ✓ | 2024-01-15 09:00 |
| GREEN | `npm test -- --grep "email validation"` | 5 tests passed ✓ | 2024-01-15 09:15 |
| VALIDATE | `npm run lint && npm run typecheck && npm test -- --coverage` | Pass, 84% ✓ | 2024-01-15 09:20 |
| COMPLETE | Moved to completed.md | ✓ | 2024-01-15 09:21 |
```

**Why Logging Matters:**
- **Audit trail** - Shows TDD process was followed
- **Debug failures** - Understand where loop got stuck
- **Time tracking** - See how long each phase took
- **Coverage progression** - Track coverage improvements

**Log Entry Requirements:**
- Command must be exact (copy-pasteable)
- Result must be concrete (not "passed", but "5 tests passed")
- Timestamp for phase progression tracking
- For failures: include error summary in notes

**Sources:** [skills/base.md:172-177](), [README.md:552-558]()

---

## Integration with Ralph Loop

The TDD workflow is executed automatically by the Ralph loop system. See [Ralph Loop: Iterative Development](#4.1) for the automation mechanism.

### Auto-Transformation Example

**User Request:**
```
"Add email validation to signup form"
```

**Claude Auto-Invokes:**
```bash
/ralph-loop "
## Task: Add email validation to signup form

### Requirements (extracted from user request)
- Validate email format on client side
- Show inline error for invalid emails
- Prevent form submission with invalid email
- Clear error when user corrects email

### TDD Workflow
1. RED: Write failing tests for email validation
2. Verify tests FAIL (proves tests validate requirement)
3. GREEN: Implement email validation logic
4. Verify tests PASS
5. VALIDATE: Run lint + typecheck + coverage
6. Repeat if any phase fails

### Completion Criteria
- [ ] All email validation tests passing
- [ ] Coverage >= 80%
- [ ] Lint clean
- [ ] No type errors

### Exit Condition
<promise>EMAIL VALIDATION COMPLETE</promise>
" --completion-promise "EMAIL VALIDATION COMPLETE" --max-iterations 20
```

The Ralph loop then:
1. Executes RED phase (write tests, verify they fail)
2. Executes GREEN phase (implement, verify tests pass)
3. Executes VALIDATE phase (lint, typecheck, coverage)
4. Returns identical prompt with updated file state if failures
5. Exits when `<promise>EMAIL VALIDATION COMPLETE</promise>` is output

**Sources:** [skills/base.md:499-578](), [README.md:71-100]()

---

## Summary

The TDD workflow enforced by Claude Bootstrap ensures:

**Quality Through Process:**
- Tests written first prove requirements are testable
- Tests must fail to prove they validate requirements
- Minimum implementation reduces complexity
- Quality gates catch issues before commit

**Error Resilience:**
- Error classification prevents infinite loops
- Blocker reports provide clear action items
- Fixable errors continue loop automatically

**Bug Prevention:**
- Test gap analysis documents coverage holes
- New tests prove they would have caught the bug
- Full test suite run prevents regressions

**Automation:**
- Ralph loop executes TDD workflow automatically
- User describes what, not how
- Loop continues until all phases pass

The three-phase workflow (RED-GREEN-VALIDATE) is the foundation that enables autonomous, iterative development while maintaining code quality and preventing defects.

---

# Page: Simplicity Rules and Enforcement

# Simplicity Rules and Enforcement

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



## Purpose and Scope

This document defines the strict complexity limits enforced throughout Claude Bootstrap and the mechanisms that automatically detect and block violations. These rules prevent technical debt accumulation by establishing hard boundaries on code size and structure. The enforcement protocol stops development when limits are exceeded, requiring immediate refactoring before work continues.

For the TDD workflow that invokes these rules during the VALIDATE phase, see [TDD Workflow (RED-GREEN-VALIDATE)](#3.2). For the Ralph loop's automatic enforcement during iterative development, see [Ralph Loop: Iterative Development](#4.1). For commit hygiene rules that complement these file-level constraints, see [Quality Gates and Code Review](#4.3).

---

## The Simplicity Hierarchy

Claude Bootstrap enforces complexity limits at three nested levels: function, file, and module. Each level has specific constraints that must be validated before code is considered complete.

### Three-Level Enforcement Model

```mermaid
graph TB
    subgraph "Module Level"
        M1["Max 3 directory levels"]
        M2["Clear module boundaries"]
        M3["No circular dependencies"]
    end
    
    subgraph "File Level"
        F1["Max 200 lines per file"]
        F2["Max 10 functions per file"]
        F3["One export focus"]
    end
    
    subgraph "Function Level"
        FN1["Max 20 lines per function"]
        FN2["Max 3 parameters"]
        FN3["Max 2 nesting levels"]
        FN4["Single responsibility"]
    end
    
    CODE["Code Implementation"] --> FN1
    CODE --> FN2
    CODE --> FN3
    CODE --> FN4
    
    FN1 --> F1
    FN2 --> F1
    FN3 --> F1
    FN4 --> F1
    
    F1 --> M1
    F2 --> M1
    F3 --> M2
    
    F1 -.->|"Sum of function lines"| FN1
    F2 -.->|"Count of functions"| FN1
    
    M1 --> PASS["✓ Passes All Constraints"]
    M2 --> PASS
    M3 --> PASS
```

**Sources:** [skills/base.md:9-29]()

---

## Function Level Constraints

Function-level rules ensure each unit of logic remains comprehensible and testable in isolation. These are the most frequently checked constraints during development.

### Constraint Definitions

| Constraint | Limit | Rationale |
|------------|-------|-----------|
| **Lines per function** | 20 maximum | Forces decomposition, keeps logic visible on one screen |
| **Parameters per function** | 3 maximum | High parameter counts indicate missing abstractions |
| **Nesting levels** | 2 maximum | Deep nesting creates cognitive load, flatten with early returns |
| **Responsibility** | Single | Each function does exactly one thing |
| **Documentation** | Names over comments | If a comment is needed to explain "what", rename the function |

### Function Constraint Enforcement

```mermaid
stateDiagram-v2
    [*] --> CountLines: "Function implementation complete"
    
    CountLines --> CheckParams: "Lines <= 20?"
    CountLines --> ViolationLines: "Lines > 20"
    
    CheckParams --> CheckNesting: "Params <= 3?"
    CheckParams --> ViolationParams: "Params > 3"
    
    CheckNesting --> CheckResponsibility: "Nesting <= 2?"
    CheckNesting --> ViolationNesting: "Nesting > 2"
    
    CheckResponsibility --> FunctionValid: "Single responsibility?"
    CheckResponsibility --> ViolationResponsibility: "Multiple responsibilities"
    
    FunctionValid --> [*]: "✓ Function passes all checks"
    
    ViolationLines --> DecomposeFunction: "STOP: Decompose function"
    ViolationParams --> RefactorOptions: "STOP: Use options object or decompose"
    ViolationNesting --> FlattenLogic: "STOP: Extract functions or use early returns"
    ViolationResponsibility --> SplitFunction: "STOP: Split into focused functions"
    
    DecomposeFunction --> CountLines
    RefactorOptions --> CountLines
    FlattenLogic --> CountLines
    SplitFunction --> CountLines
    
    note right of ViolationLines
        Example violation message:
        ⚠️ FUNCTION LENGTH VIOLATION
        processUserData() has 32 lines (limit: 20)
        
        Split into:
        - validateUserData() - validation logic
        - transformUserData() - transformation
        - saveUserData() - persistence
    end note
```

**Sources:** [skills/base.md:13-18]()

---

## File Level Constraints

File-level rules prevent god objects and maintain manageable cognitive load. These constraints are checked before any file is marked complete.

### Constraint Definitions

| Constraint | Limit | Rationale |
|------------|-------|-----------|
| **Lines per file** | 200 maximum | Keeps entire file visible without scrolling, forces modular design |
| **Functions per file** | 10 maximum | Prevents feature creep within single files |
| **Export focus** | One primary export | A file should have one clear purpose |

### File Size Enforcement Protocol

The enforcement protocol executes before completing any file, checking all constraints in sequence. Violations trigger immediate decomposition.

```mermaid
flowchart TD
    START["File implementation complete"] --> COUNT_LINES["Count total lines"]
    
    COUNT_LINES --> CHECK_200{"Lines <= 200?"}
    CHECK_200 -->|No| VIOLATION_FILE["⚠️ FILE SIZE VIOLATION"]
    CHECK_200 -->|Yes| COUNT_FUNCTIONS["Count functions"]
    
    COUNT_FUNCTIONS --> CHECK_10{"Functions <= 10?"}
    CHECK_10 -->|No| VIOLATION_FUNCTIONS["⚠️ FUNCTION COUNT VIOLATION"]
    CHECK_10 -->|Yes| CHECK_EACH_FN["Check each function length"]
    
    CHECK_EACH_FN --> ANY_OVER_20{"Any function > 20 lines?"}
    ANY_OVER_20 -->|Yes| VIOLATION_FN_LENGTH["⚠️ FUNCTION LENGTH VIOLATION"]
    ANY_OVER_20 -->|No| CHECK_PARAMS["Check parameter counts"]
    
    CHECK_PARAMS --> ANY_OVER_3{"Any function > 3 params?"}
    ANY_OVER_3 -->|Yes| VIOLATION_PARAMS["⚠️ PARAMETER COUNT VIOLATION"]
    ANY_OVER_3 -->|No| VALID["✓ File passes all checks"]
    
    VIOLATION_FILE --> SPLIT_FILE["Split file by responsibility"]
    VIOLATION_FUNCTIONS --> SPLIT_FILE
    VIOLATION_FN_LENGTH --> DECOMPOSE["Decompose functions"]
    VIOLATION_PARAMS --> REFACTOR_PARAMS["Refactor to options objects"]
    
    SPLIT_FILE --> OUTPUT_PLAN["Output split plan:<br/>- fileA.ts: Responsibility A<br/>- fileB.ts: Responsibility B"]
    OUTPUT_PLAN --> START
    
    DECOMPOSE --> START
    REFACTOR_PARAMS --> START
    
    VALID --> NEXT["Proceed to next phase"]
```

**Sources:** [skills/base.md:20-24](), [skills/base.md:30-49]()

---

## Module Level Constraints

Module-level rules maintain architectural clarity across the codebase, preventing deep hierarchies and circular dependencies.

### Constraint Definitions

| Constraint | Limit | Rationale |
|------------|-------|-----------|
| **Directory nesting** | 3 levels maximum | Flat structures are easier to navigate, deep nesting indicates over-engineering |
| **Module boundaries** | Single public interface | Each module exposes one clear API |
| **Circular dependencies** | None allowed | Circular imports create fragile, tightly-coupled systems |

### Example Directory Structure Validation

```
✓ VALID (2 levels):
project/
├── src/
│   ├── auth/          ← Level 1
│   │   ├── login.ts   ← Level 2
│   │   └── signup.ts
│   └── api/
│       ├── users.ts
│       └── posts.ts

✓ VALID (3 levels):
project/
├── src/
│   ├── features/       ← Level 1
│   │   ├── auth/       ← Level 2
│   │   │   ├── login.ts    ← Level 3
│   │   │   └── signup.ts
│   │   └── posts/
│   │       ├── create.ts
│   │       └── list.ts

❌ INVALID (4 levels):
project/
├── src/
│   ├── features/       ← Level 1
│   │   ├── user/       ← Level 2
│   │   │   ├── profile/    ← Level 3
│   │   │   │   ├── view.ts     ← Level 4 (TOO DEEP)
│   │   │   │   └── edit.ts
```

**Sources:** [skills/base.md:25-28]()

---

## Enforcement Protocol

The enforcement protocol defines when and how violations are detected, blocking development until resolved. This happens at multiple checkpoints throughout the development workflow.

### Enforcement Checkpoints

```mermaid
graph LR
    subgraph "Development Phase"
        WRITE["Write code"]
        SELF_CHECK["Developer self-check"]
    end
    
    subgraph "TDD VALIDATE Phase"
        LINT["Run linter"]
        TYPE["Run type checker"]
        TEST["Run tests + coverage"]
    end
    
    subgraph "Pre-Commit Hook"
        HOOK_LINT["Lint check"]
        HOOK_TYPE["Type check"]
        HOOK_TEST["Run unit tests"]
    end
    
    subgraph "Code Review"
        REVIEW_CMD["/code-review command"]
        ANALYZE["Analyze complexity"]
        SEVERITY["Severity classification"]
    end
    
    subgraph "CI/CD"
        CI_LINT["Full lint"]
        CI_TYPE["Full type check"]
        CI_TEST["Full test suite"]
        CI_COVERAGE["Coverage threshold"]
    end
    
    WRITE --> SELF_CHECK
    SELF_CHECK -.->|"Checkpoint 1"| CHECK1["Check file constraints"]
    
    SELF_CHECK --> LINT
    LINT --> TYPE
    TYPE --> TEST
    TEST -.->|"Checkpoint 2"| CHECK2["Validate phase enforcement"]
    
    TEST --> HOOK_LINT
    HOOK_LINT --> HOOK_TYPE
    HOOK_TYPE --> HOOK_TEST
    HOOK_TEST -.->|"Checkpoint 3"| CHECK3["Pre-commit enforcement"]
    
    HOOK_TEST --> REVIEW_CMD
    REVIEW_CMD --> ANALYZE
    ANALYZE --> SEVERITY
    SEVERITY -.->|"Checkpoint 4"| CHECK4["Code review enforcement"]
    
    SEVERITY --> CI_LINT
    CI_LINT --> CI_TYPE
    CI_TYPE --> CI_TEST
    CI_TEST --> CI_COVERAGE
    CI_COVERAGE -.->|"Checkpoint 5"| CHECK5["CI/CD enforcement"]
    
    CHECK1 -.->|Violation| BLOCK1["STOP: Refactor immediately"]
    CHECK2 -.->|Violation| BLOCK2["STOP: Fix before continue"]
    CHECK3 -.->|Violation| BLOCK3["STOP: Commit blocked"]
    CHECK4 -.->|Critical/High| BLOCK4["STOP: Push blocked"]
    CHECK5 -.->|Violation| BLOCK5["STOP: Merge blocked"]
    
    BLOCK1 --> WRITE
    BLOCK2 --> WRITE
    BLOCK3 --> WRITE
    BLOCK4 --> WRITE
    BLOCK5 --> WRITE
```

**Sources:** [skills/base.md:30-49](), [skills/base.md:487-492]()

---

## Violation Messages and Resolution

When violations are detected, the system outputs structured messages with clear remediation steps.

### File Size Violation Output Format

```
⚠️ FILE SIZE VIOLATION DETECTED

[filename].ts has [X] lines (limit: 200)

Splitting into:
- [filename-a].ts - [responsibility A description]
- [filename-b].ts - [responsibility B description]
```

### Function Length Violation Output Format

```
⚠️ FUNCTION LENGTH VIOLATION DETECTED

functionName() has [X] lines (limit: 20)

Decomposing into:
- validateInput() - input validation logic
- processData() - core processing
- formatOutput() - output formatting
```

### Parameter Count Violation Output Format

```
⚠️ PARAMETER COUNT VIOLATION DETECTED

functionName(a, b, c, d, e) has 5 parameters (limit: 3)

Refactor options:
1. Use options object: functionName({ a, b, c, d, e })
2. Decompose into smaller functions with fewer concerns
```

**Sources:** [skills/base.md:38-47]()

---

## Integration with TDD Workflow

Simplicity rules are checked during the VALIDATE phase of the RED-GREEN-VALIDATE cycle. If violations exist, the todo cannot be marked complete until resolved.

### VALIDATE Phase Enforcement Flow

```mermaid
stateDiagram-v2
    [*] --> GreenPhase: "Tests passing (GREEN)"
    
    GreenPhase --> ValidatePhase: "Enter VALIDATE phase"
    
    ValidatePhase --> RunLint: "Run linter"
    RunLint --> RunTypeCheck: "Lint passes?"
    RunLint --> BlockLint: "Lint errors"
    
    RunTypeCheck --> RunCoverage: "Type check passes?"
    RunTypeCheck --> BlockType: "Type errors"
    
    RunCoverage --> CheckSimplicity: "Coverage >= 80%?"
    RunCoverage --> BlockCoverage: "Coverage too low"
    
    CheckSimplicity --> CountFileLines: "Check file constraints"
    
    CountFileLines --> CheckFileFunctions: "Lines <= 200?"
    CountFileLines --> BlockFileSize: "File too large"
    
    CheckFileFunctions --> CheckFunctionSizes: "Functions <= 10?"
    CheckFileFunctions --> BlockFileCount: "Too many functions"
    
    CheckFunctionSizes --> CheckParams: "Each function <= 20 lines?"
    CheckFunctionSizes --> BlockFnSize: "Function too long"
    
    CheckParams --> ValidateComplete: "Each function <= 3 params?"
    CheckParams --> BlockParams: "Too many parameters"
    
    ValidateComplete --> MarkComplete: "✓ All validations pass"
    MarkComplete --> [*]: "Move to completed.md"
    
    BlockLint --> RefactorCode: "STOP: Fix violations"
    BlockType --> RefactorCode
    BlockCoverage --> AddTests: "STOP: Add tests"
    BlockFileSize --> SplitFile: "STOP: Split file"
    BlockFileCount --> SplitFile
    BlockFnSize --> DecomposeFn: "STOP: Decompose function"
    BlockParams --> RefactorParams: "STOP: Refactor parameters"
    
    RefactorCode --> GreenPhase
    AddTests --> GreenPhase
    SplitFile --> GreenPhase
    DecomposeFn --> GreenPhase
    RefactorParams --> GreenPhase
    
    note right of BlockFileSize
        Cannot mark todo complete
        until all constraints satisfied.
        
        Blocking conditions:
        - File > 200 lines
        - File > 10 functions
        - Any function > 20 lines
        - Any function > 3 params
    end note
```

**Sources:** [skills/base.md:203-214](), [skills/base.md:254-263]()

---

## Automatic Enforcement in Ralph Loop

The Ralph Wiggum loop automatically enforces simplicity rules during iterative development. Each iteration checks constraints and blocks progression on violations.

### Ralph Loop Constraint Checking

```mermaid
flowchart TD
    START["Ralph iteration starts"] --> IMPLEMENT["Implement code changes"]
    
    IMPLEMENT --> RUN_TESTS["Run tests"]
    
    RUN_TESTS --> TESTS_PASS{"Tests pass?"}
    TESTS_PASS -->|No| CLASSIFY["Classify error type"]
    TESTS_PASS -->|Yes| VALIDATE["Enter VALIDATE phase"]
    
    CLASSIFY --> IS_FIXABLE{"Code/Type/Logic error?"}
    IS_FIXABLE -->|Yes| IMPLEMENT
    IS_FIXABLE -->|No| BLOCKER["Exit: BLOCKER REPORT"]
    
    VALIDATE --> RUN_LINT["Run lint"]
    RUN_LINT --> LINT_PASS{"Lint passes?"}
    LINT_PASS -->|No| IMPLEMENT
    LINT_PASS -->|Yes| RUN_TYPE["Run type check"]
    
    RUN_TYPE --> TYPE_PASS{"Type check passes?"}
    TYPE_PASS -->|No| IMPLEMENT
    TYPE_PASS -->|Yes| CHECK_COVERAGE["Run coverage"]
    
    CHECK_COVERAGE --> COV_PASS{"Coverage >= 80%?"}
    COV_PASS -->|No| ADD_TESTS["Add tests"]
    COV_PASS -->|Yes| CHECK_SIMPLICITY["Check simplicity rules"]
    
    ADD_TESTS --> RUN_TESTS
    
    CHECK_SIMPLICITY --> FILE_SIZE{"File <= 200 lines?"}
    FILE_SIZE -->|No| REPORT_VIOLATION["Report: File too large"]
    FILE_SIZE -->|Yes| FILE_FNS{"File <= 10 functions?"}
    
    FILE_FNS -->|No| REPORT_VIOLATION
    FILE_FNS -->|Yes| FN_SIZES{"All functions <= 20 lines?"}
    
    FN_SIZES -->|No| REPORT_VIOLATION
    FN_SIZES -->|Yes| FN_PARAMS{"All functions <= 3 params?"}
    
    FN_PARAMS -->|No| REPORT_VIOLATION
    FN_PARAMS -->|Yes| COMPLETE["✓ Iteration complete"]
    
    REPORT_VIOLATION --> SPLIT_CODE["Split/decompose code"]
    SPLIT_CODE --> IMPLEMENT
    
    COMPLETE --> CHECK_PROMISE{"Completion promise found?"}
    CHECK_PROMISE -->|Yes| SUCCESS["Exit: Success"]
    CHECK_PROMISE -->|No| CHECK_MAX{"Max iterations reached?"}
    
    CHECK_MAX -->|Yes| INCOMPLETE["Exit: Incomplete"]
    CHECK_MAX -->|No| NEXT_ITERATION["Next iteration (same prompt)"]
    NEXT_ITERATION --> IMPLEMENT
```

**Sources:** [skills/base.md:499-578]()

---

## Never Defer Refactoring

A core principle of the enforcement system is immediate remediation. When violations are detected, development stops until they are resolved. Deferring refactoring creates technical debt that compounds over time.

### Enforcement Timing Rules

| Situation | Action | Rationale |
|-----------|--------|-----------|
| **During development** | STOP immediately, refactor before continuing | Prevents accumulation of violations |
| **Before marking todo complete** | VALIDATE phase must pass all checks | Ensures completed work meets standards |
| **In code review** | Block Critical/High severity issues | Last gate before merge |
| **In CI/CD** | Fail build on violations | Defense in depth |

### The Refactoring Priority

```
❌ ANTI-PATTERN:
"TODO: Refactor this later when file exceeds 200 lines"
"FIXME: Split this function when we have time"

✓ CORRECT PATTERN:
[Detect violation] → [STOP] → [Refactor immediately] → [Continue]
```

**Sources:** [skills/base.md:49](), [skills/base.md:495]()

---

## Flagging Complexity Warnings

During development, Claude must proactively flag when code approaches complexity limits, even before violations occur. This creates awareness and prevents surprise refactoring.

### Warning Thresholds

| Metric | Warning Threshold | Violation Threshold |
|--------|------------------|---------------------|
| File lines | 180 lines (90%) | 200 lines |
| Functions per file | 9 functions (90%) | 10 functions |
| Function lines | 18 lines (90%) | 20 lines |
| Parameters | At 3 parameters | More than 3 parameters |

### Warning Message Format

```
⚠️ COMPLEXITY WARNING

[filename].ts approaching file size limit:
- Current: 185 lines
- Limit: 200 lines
- Margin: 15 lines remaining

Consider splitting soon to avoid mid-feature refactoring.
```

**Sources:** [skills/base.md:487-492]()

---

## Code Review Integration

The `/code-review` command analyzes code for simplicity violations as part of its multi-dimensional analysis. Violations are classified by severity and can block pushes.

### Code Review Simplicity Checks

```mermaid
graph TB
    START["/code-review command"] --> ANALYZE["Analyze changed files"]
    
    ANALYZE --> CHECK_FILES["Check each modified file"]
    
    CHECK_FILES --> FILE_METRICS["Calculate metrics:<br/>- Total lines<br/>- Function count<br/>- Function sizes<br/>- Parameter counts"]
    
    FILE_METRICS --> VIOLATIONS{"Violations found?"}
    
    VIOLATIONS -->|No| CHECK_OTHER["Continue with other analysis"]
    VIOLATIONS -->|Yes| CLASSIFY["Classify severity"]
    
    CLASSIFY --> CRITICAL{"File > 250 lines OR<br/>Function > 30 lines?"}
    CRITICAL -->|Yes| MARK_CRITICAL["Mark as CRITICAL"]
    
    CRITICAL -->|No| HIGH{"File > 200 lines OR<br/>Function > 20 lines OR<br/>> 3 params?"}
    HIGH -->|Yes| MARK_HIGH["Mark as HIGH"]
    
    HIGH -->|No| MEDIUM["Mark as MEDIUM"]
    
    MARK_CRITICAL --> BLOCK["Block push"]
    MARK_HIGH --> BLOCK
    MEDIUM --> WARN["Allow with warning"]
    
    BLOCK --> OUTPUT["Output violation report:<br/>- File: [path]<br/>- Violation: [type]<br/>- Current: [value]<br/>- Limit: [limit]<br/>- Severity: [level]"]
    WARN --> OUTPUT
    
    CHECK_OTHER --> OUTPUT
```

**Sources:** Reference from overall system architecture, code review is mentioned in [skills/base.md:440-453]()

---

## Anti-Patterns

Common mistakes developers make when attempting to circumvent simplicity rules.

### Violation Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **Adding comments to justify size** | Comments don't reduce complexity | Split the code |
| **Counting only "real" lines** | All lines count, including whitespace structure | Refactor to reduce total lines |
| **Extracting to helper file in same directory** | Doesn't fix cognitive load, just moves it | Proper modularization by responsibility |
| **Using one-liner functions to game metrics** | Creates different complexity (too many functions) | Meaningful decomposition |
| **Disabling linter rules** | Defeats the purpose of enforcement | Fix the underlying issue |
| **"Just this once" exceptions** | Exceptions become the norm | No exceptions, refactor immediately |

### Example: Wrong vs Right Decomposition

```
❌ WRONG (gaming the system):
// file-a.ts (195 lines)
function processUserData(user) {
  return helperA(helperB(helperC(user)));
}

// file-a-helpers.ts (in same directory, 180 lines)
function helperA(data) { /* 60 lines */ }
function helperB(data) { /* 60 lines */ }
function helperC(data) { /* 60 lines */ }

✓ RIGHT (proper modularization):
// user-validation.ts (120 lines)
export function validateUser(user) { /* focused validation */ }

// user-transformation.ts (85 lines)
export function transformUser(user) { /* focused transformation */ }

// user-persistence.ts (95 lines)
export function saveUser(user) { /* focused persistence */ }

// user-service.ts (45 lines)
export function processUser(user) {
  const validated = validateUser(user);
  const transformed = transformUser(validated);
  return saveUser(transformed);
}
```

**Sources:** [skills/base.md:82-96]()

---

## Summary of Enforcement Points

The simplicity rules are enforced at five distinct checkpoints, creating defense-in-depth:

1. **Self-Check**: Developer/AI checks before completing file ([skills/base.md:30-37]())
2. **TDD VALIDATE Phase**: Automatic check during todo completion ([skills/base.md:203-214]())
3. **Pre-Commit Hook**: Local validation before commit ([skills/base.md:447-453]())
4. **Code Review**: Manual review with `/code-review` command before push ([skills/base.md:440-453]())
5. **CI/CD**: Final automated validation in GitHub Actions

This layered approach ensures violations are caught early and resolved immediately, preventing technical debt accumulation and maintaining codebase simplicity throughout the development lifecycle.

---

# Page: Atomic Todos and Project Specs

# Atomic Todos and Project Specs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



## Purpose and Scope

This document explains the atomic todo system and project specifications structure in Claude Bootstrap. It covers the standardized todo format, the `_project_specs/` directory organization, the `active.md` → `completed.md` workflow, and TDD execution tracking.

For the TDD workflow mechanics (RED-GREEN-VALIDATE phases), see [TDD Workflow](#3.2). For team coordination features using these specs, see [Multi-Developer Coordination](#8.1).

---

## Project Specs Directory Structure

The `_project_specs/` directory separates business requirements from code documentation, providing a single source of truth for project state.

### Directory Anatomy

```
_project_specs/
├── overview.md              # Project vision and high-level goals
├── features/                # Feature specifications
│   ├── feature-auth.md      # Individual feature specs
│   ├── feature-payments.md
│   └── feature-analytics.md
├── todos/                   # Atomic work tracking
│   ├── active.md            # Current sprint/focus work
│   ├── backlog.md           # Future work queue
│   └── completed.md         # Archived completed work
├── session/                 # Session state management
│   ├── current-state.md     # Live session context
│   ├── decisions.md         # Architectural decisions log
│   ├── code-landmarks.md    # Key code location map
│   └── archive/             # Historical session summaries
├── team/                    # Multi-developer coordination
│   ├── state.md             # Active sessions and claims
│   ├── contributors.md      # Team member registry
│   └── handoffs/            # Context transfer notes
└── prompts/                 # LLM prompt specifications (AI-first projects)
```

**Sources:** [skills/base.md:99-135](), [README.md:296-317]()

---

## Separation of Concerns

The `_project_specs/` directory maintains strict separation between specifications and documentation:

| Location | Content Type | Purpose |
|----------|--------------|---------|
| `_project_specs/` | Business requirements, features, todos | What needs to be built |
| `docs/` | Technical documentation, API references | How the system works |
| `_project_specs/session/` | Session state, decisions, context | Current development state |
| `CLAUDE.md` | Claude-specific instructions | AI agent configuration |

This separation ensures that project requirements remain independent of implementation details, enabling easier refactoring and system rewrites while preserving business context.

**Sources:** [skills/base.md:126-135]()

---

## Atomic Todo Format

Each todo is a self-contained, testable unit of work with explicit validation criteria. The format enforces TDD discipline through structured execution logging.

### Todo Structure Diagram

```mermaid
graph TB
    subgraph TODO["Todo Document Structure"]
        HEADER["Header Block<br/>[TODO-XXX] Title<br/>Status | Priority | Estimate"]
        DESC["Description Section<br/>One paragraph context"]
        ACCEPT["Acceptance Criteria<br/>Checkboxes for completion"]
        VALID["Validation Section<br/>Manual + Automated verification"]
        TESTS["Test Cases Table<br/>Input | Expected | Notes"]
        DEPS["Dependencies<br/>Blocks/Depends on other todos"]
        LOG["TDD Execution Log<br/>RED | GREEN | VALIDATE | COMPLETE"]
    end
    
    HEADER --> DESC
    DESC --> ACCEPT
    ACCEPT --> VALID
    VALID --> TESTS
    TESTS --> DEPS
    DEPS --> LOG
```

**Sources:** [skills/base.md:138-178](), [README.md:531-558]()

---

### Required Fields

Every atomic todo must include these fields:

```markdown
## [TODO-001] Short descriptive title

**Status:** pending | in-progress | blocked | done
**Priority:** high | medium | low
**Estimate:** XS | S | M | L | XL

### Description
One paragraph describing what needs to be done.

### Acceptance Criteria
- [ ] Criterion 1 - specific, measurable
- [ ] Criterion 2 - specific, measurable

### Validation
How to verify this is complete:
- Manual: [steps to manually test]
- Automated: [test file/command that validates this]

### Test Cases
| Input | Expected Output | Notes |
|-------|-----------------|-------|
| ... | ... | ... |

### Dependencies
- Depends on: [TODO-xxx] (if any)
- Blocks: [TODO-yyy] (if any)

### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| RED | `[test command]` | - | - |
| GREEN | `[test command]` | - | - |
| VALIDATE | `[lint && typecheck && test --coverage]` | - | - |
| COMPLETE | Moved to completed.md | - | - |
```

**Sources:** [skills/base.md:142-178]()

---

### Todo Sizing Guidelines

| Estimate | Scope | Max Duration | Decomposition Trigger |
|----------|-------|--------------|----------------------|
| **XS** | Single function, < 50 lines | 1 hour | - |
| **S** | Single file, 1-3 functions | 2-4 hours | - |
| **M** | 2-3 files, < 10 functions | 1 day | Split if dependencies grow |
| **L** | Multiple files, cross-cutting | 2-3 days | **Must decompose** |
| **XL** | Multiple modules | > 3 days | **Invalid - always split** |

**Rule:** If a todo is larger than "M", it must be broken into smaller todos before work begins. Large todos indicate insufficient planning.

**Sources:** [skills/base.md:180-185]()

---

## TDD Execution Log

The execution log provides an audit trail of the TDD workflow, proving that tests were written first and validating the development process.

### Execution Log Workflow Diagram

```mermaid
stateDiagram-v2
    [*] --> RED: Write tests first
    
    RED --> RunTestsRed: Execute test command
    RunTestsRed --> CheckRed: Tests fail?
    
    CheckRed --> FixTests: No - tests invalid
    CheckRed --> GREEN: Yes - RED confirmed ✓
    
    FixTests --> RED
    
    GREEN --> Implement: Write minimum code
    Implement --> RunTestsGreen: Execute tests again
    
    RunTestsGreen --> CheckGreen: Tests pass?
    CheckGreen --> DebugGreen: No - fix code
    CheckGreen --> VALIDATE: Yes - GREEN confirmed ✓
    
    DebugGreen --> Implement
    
    VALIDATE --> Lint: npm run lint
    Lint --> TypeCheck: npm run typecheck
    TypeCheck --> Coverage: npm test --coverage
    
    Coverage --> CheckCoverage: Coverage >= 80%?
    CheckCoverage --> AddTests: No - insufficient
    CheckCoverage --> COMPLETE: Yes - VALIDATE ✓
    
    AddTests --> RunTestsGreen
    
    COMPLETE --> MoveTodo: Move to completed.md
    MoveTodo --> Checkpoint: Update session state
    Checkpoint --> [*]
    
    note right of RED
        Log command + result
        Update TDD Execution Log table
    end note
    
    note right of GREEN
        Log command + result
        Ensure all tests pass
    end note
    
    note right of VALIDATE
        Log final validation
        Must meet all quality gates
    end note
```

**Sources:** [skills/base.md:187-214](), [README.md:531-558]()

---

### Stack-Specific Execution Commands

The TDD Execution Log records the actual commands run at each phase:

#### Node.js/TypeScript Projects

```bash
# RED Phase - Expect failures
npm test -- --grep "todo-description"

# GREEN Phase - Expect pass
npm test -- --grep "todo-description"

# VALIDATE Phase - Full quality check
npm run lint && npm run typecheck && npm test -- --coverage
```

#### Python Projects

```bash
# RED Phase - Expect failures
pytest -k "todo_description" -v

# GREEN Phase - Expect pass
pytest -k "todo_description" -v

# VALIDATE Phase - Full quality check
ruff check . && mypy . && pytest --cov --cov-fail-under=80
```

#### React/Next.js Projects

```bash
# RED Phase - Expect failures
npm test -- --testPathPattern="ComponentName"

# GREEN Phase - Expect pass
npm test -- --testPathPattern="ComponentName"

# VALIDATE Phase - Full quality check
npm run lint && npm run typecheck && npm test -- --coverage --watchAll=false
```

**Sources:** [skills/base.md:216-253]()

---

## Complete Todo Example

This example shows a fully populated todo with all required sections:

```markdown
## [TODO-042] Add email validation to signup form

**Status:** pending
**Priority:** high
**Estimate:** S

### Description
Validate email format on the signup form before submission. Show inline error if invalid.

### Acceptance Criteria
- [ ] Email field shows error for invalid format
- [ ] Error clears when user fixes the email
- [ ] Form cannot submit with invalid email
- [ ] Valid emails pass through without error

### Validation
- Manual: Enter "notanemail" in signup form, verify error appears
- Automated: `npm test -- --grep "email validation"`

### Test Cases
| Input | Expected Output | Notes |
|-------|-----------------|-------|
| user@example.com | Valid, no error | Standard email |
| user@sub.example.com | Valid, no error | Subdomain |
| notanemail | Invalid, show error | No @ symbol |
| user@ | Invalid, show error | No domain |
| @example.com | Invalid, show error | No local part |

### Dependencies
- Depends on: [TODO-041] Signup form component
- Blocks: [TODO-045] Signup flow integration test

### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| RED | `npm test -- --grep "email validation"` | 5 tests failed ✓ | 2024-01-15 10:23 |
| GREEN | `npm test -- --grep "email validation"` | 5 tests passed ✓ | 2024-01-15 10:45 |
| VALIDATE | `npm run lint && npm run typecheck && npm test -- --coverage` | Pass, 84% coverage ✓ | 2024-01-15 10:52 |
| COMPLETE | Moved to completed.md | ✓ | 2024-01-15 10:55 |
```

**Sources:** [skills/base.md:343-384](), [README.md:535-558]()

---

## Bug Fix Todo Format

Bug fixes follow a modified todo structure that emphasizes test gap analysis and reproduction steps.

### Bug Todo Structure Diagram

```mermaid
graph TB
    subgraph BUG["Bug Todo Structure"]
        BUG_HEADER["Header<br/>[BUG-XXX] Description<br/>Status | Priority | Reported"]
        BUG_DESC["Bug Description<br/>Actual vs Expected"]
        REPRO["Reproduction Steps<br/>Numbered sequence"]
        GAP["Test Gap Analysis<br/>What tests missed"]
        BUG_TESTS["Test Cases Table<br/>Current Bug vs Fixed"]
        BUG_LOG["TDD Execution Log<br/>DIAGNOSE | RED | GREEN | VALIDATE"]
    end
    
    BUG_HEADER --> BUG_DESC
    BUG_DESC --> REPRO
    REPRO --> GAP
    GAP --> BUG_TESTS
    BUG_TESTS --> BUG_LOG
```

**Sources:** [skills/base.md:272-334](), [README.md:560-577]()

---

### Bug Fix Template

```markdown
## [BUG-001] Short description of the bug

**Status:** pending
**Priority:** high
**Reported:** [how user reported it / reproduction steps]

### Bug Description
What is happening vs. what should happen.

### Reproduction Steps
1. Step one
2. Step two
3. Observe: [incorrect behavior]
4. Expected: [correct behavior]

### Test Gap Analysis
- Existing test coverage: [list relevant test files]
- Gap identified: [what the tests missed]
- New test needed: [describe the test to add]

### Test Cases for Bug
| Input | Current (Bug) | Expected (Fixed) |
|-------|---------------|------------------|
| ... | ... | ... |

### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| DIAGNOSE | `npm test` | All pass (gap!) | - |
| RED | `npm test -- --grep "bug description"` | 1 test failed ✓ | - |
| GREEN | `npm test -- --grep "bug description"` | 1 test passed ✓ | - |
| VALIDATE | `npm run lint && npm run typecheck && npm test -- --coverage` | Pass ✓ | - |
```

The **DIAGNOSE** phase is unique to bug fixes - it confirms that existing tests pass despite the bug, proving a test gap exists.

**Sources:** [skills/base.md:299-334]()

---

## Active to Completed Workflow

Todos move through a lifecycle from specification to completion, with state tracked in markdown files.

### Todo Lifecycle Diagram

```mermaid
stateDiagram-v2
    [*] --> backlog.md: New todo created
    
    backlog.md --> active.md: Claim for current work
    
    active.md --> InProgress: Status: in-progress
    
    InProgress --> Blocked: Missing dependency
    InProgress --> InProgress: TDD iteration
    InProgress --> Done: All criteria met
    
    Blocked --> InProgress: Dependency resolved
    
    Done --> completed.md: Move entire todo
    
    completed.md --> [*]: Archived for reference
    
    note right of backlog.md
        Future work queue
        Prioritized but not started
    end note
    
    note right of active.md
        Current sprint focus
        In-progress todos only
    end note
    
    note right of completed.md
        Historical reference
        Never deleted
    end note
```

**Sources:** [skills/base.md:180-185](), [README.md:393-395]()

---

### File Locations and Purposes

| File | Location | Purpose | Typical Size |
|------|----------|---------|--------------|
| `active.md` | `_project_specs/todos/` | Current sprint work | 3-10 todos |
| `backlog.md` | `_project_specs/todos/` | Prioritized future work | 20-50 todos |
| `completed.md` | `_project_specs/todos/` | Historical archive | Growing indefinitely |

**Sources:** [skills/base.md:109-117]()

---

### Workflow Rules

1. **Atomic Movement**: Move entire todo markdown block, including all sections
2. **Never Delete**: Completed todos archived to `completed.md`, never deleted
3. **Single Active File**: All current work tracked in single `active.md` file
4. **Backlog Priority**: Todos in `backlog.md` ordered by priority
5. **Status Updates**: Update status field before moving between files

**Sources:** [skills/base.md:180-185]()

---

## Blocking Conditions

Todos cannot be marked complete or moved to `completed.md` under these conditions:

### Blocking Scenarios

| Condition | Reason | Action Required |
|-----------|--------|-----------------|
| Tests not written first | Skipped RED phase | Write tests, verify they fail |
| Tests didn't fail initially | Invalid tests | Fix tests to catch requirement |
| Any test failing | Incomplete implementation | Fix code until tests pass |
| Linter errors present | Code quality violation | Fix lint errors (warnings acceptable) |
| Type checker errors | Type safety violation | Fix type errors |
| Coverage below threshold | Insufficient testing | Add tests until ≥80% coverage |

When blocked, add blocking information to the todo:

```markdown
## [TODO-042] - BLOCKED

**Blocking Reason:** Lint error in src/utils/validate.ts:42
**Action Required:** Fix undefined variable 'emailPattern'
```

**Sources:** [skills/base.md:254-271]()

---

## Todo Execution Anti-Patterns

These patterns violate the atomic todo discipline and must be avoided:

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| ❌ Fixing bugs without tests | Bug will likely return | Write failing test first (DIAGNOSE + RED) |
| ❌ Writing tests after code | Can't prove tests catch requirement | Write tests first, verify they fail |
| ❌ Skipping test gap analysis | Miss root cause of bug | Document what existing tests missed |
| ❌ Only testing the fix | May introduce regressions | Run full test suite (VALIDATE phase) |
| ❌ Marking done with failing tests | Incomplete work | Fix all failures before completion |
| ❌ Deleting completed todos | Loss of context | Archive to completed.md |

**Sources:** [skills/base.md:336-342]()

---

## Integration with Ralph Loop

Atomic todos integrate with the Ralph Wiggum iterative loop system. When using `/ralph-loop`, the todo structure provides:

1. **Completion Criteria**: Acceptance criteria define loop exit condition
2. **Validation Commands**: Test cases translate to test commands
3. **Execution Tracking**: Ralph loop updates TDD Execution Log automatically
4. **Error Classification**: Ralph loop determines if failures are fixable or blockers

The Ralph loop reads the todo structure and iterates until all acceptance criteria are met and validation passes.

For Ralph loop mechanics, see [Ralph Loop: Iterative Development](#4.1).

**Sources:** [skills/base.md:499-579](), [README.md:71-117]()

---

## Relationship to Session Management

Todos interact with session management through checkpoint triggers:

| Event | Session Action |
|-------|----------------|
| Todo moved to `completed.md` | Checkpoint to `current-state.md` |
| Todo blocked | Log blocker to `current-state.md` |
| Major todo completed | Archive session to `session/archive/` |
| Todo decision made | Log to `session/decisions.md` |

This ensures that todo progress is preserved across sessions and development can resume from last checkpoint.

For session management details, see [Session Management](#4.2).

**Sources:** [skills/base.md:457-478]()

---

## Summary

The atomic todo system provides:

- **Standardized Format**: Required fields ensure completeness
- **TDD Enforcement**: Execution log proves test-first discipline
- **Audit Trail**: Full history from specification to completion
- **State Tracking**: Clear workflow from backlog → active → completed
- **Integration**: Works with Ralph loops and session management
- **Team Coordination**: Todos can be claimed in multi-developer projects

This structure transforms vague requirements into verifiable, trackable work units that maintain quality through mandatory TDD and validation gates.

**Sources:** [skills/base.md:138-385](), [README.md:389-395](), [README.md:531-577]()

---

# Page: Development Workflow

# Development Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/iterative-development.md](skills/iterative-development.md)

</details>



## Purpose and Scope

This page describes the end-to-end development workflow in Claude Bootstrap, from receiving a feature request to deploying code. It covers the TDD-first methodology, atomic todo management, and how the various system components integrate during active development.

For deep dives into specific workflow components, see:
- [Ralph Loop: Iterative Development](#4.1) - Details on autonomous TDD iteration
- [Session Management](#4.2) - Context preservation and checkpoint mechanisms
- [Quality Gates and Code Review](#4.3) - Multi-layer validation enforcement

## Overview

Claude Bootstrap enforces a structured development workflow built around three core principles:

1. **Test-Driven Development (TDD)** - Tests must be written first and must fail before implementation
2. **Iterative Loops** - Features are developed through self-referential cycles until completion criteria are met
3. **Quality Gates** - Multiple validation layers prevent defective code from progressing

The workflow transforms natural language requests into validated, tested code through a series of automated phases.

**Sources:** [README.md:1-40](), [skills/iterative-development.md:1-30]()

---

## The TDD Workflow: RED-GREEN-VALIDATE

### Three-Phase Cycle

Every feature, bug fix, and refactoring follows a mandatory three-phase cycle:

```mermaid
stateDiagram-v2
    [*] --> RED: "Write Tests"
    RED --> VerifyFail: "Run Tests"
    VerifyFail --> RED: "Tests pass (wrong!)"
    VerifyFail --> GREEN: "Tests fail (correct)"
    GREEN --> Implement: "Write minimum code"
    Implement --> RunTests: "Run tests again"
    RunTests --> GREEN: "Tests still fail"
    RunTests --> VALIDATE: "All tests pass"
    VALIDATE --> Lint: "Run linter"
    Lint --> TypeCheck: "Lint passes"
    TypeCheck --> Coverage: "Types valid"
    Coverage --> Complete: "Coverage >= 80%"
    Coverage --> AddTests: "Coverage < 80%"
    AddTests --> RunTests
    Lint --> FixLint: "Errors found"
    FixLint --> Implement
    TypeCheck --> FixTypes: "Errors found"
    FixTypes --> Implement
    Complete --> [*]
```

### Phase 1: RED - Write Failing Tests

Tests must be written **before** any implementation code. The tests must fail on first execution to prove they validate the requirements.

**For Features:**
```markdown
1. Read acceptance criteria from _project_specs/todos/active.md
2. Write test cases covering all criteria
3. Run: npm test (or pytest, etc.)
4. Verify: Tests FAIL with expected error messages
5. If tests pass: Fix tests, they're wrong
```

**For Bugs:**
```markdown
1. Reproduce the bug
2. Identify the test gap (why didn't existing tests catch this?)
3. Write a test that reproduces the bug
4. Run: npm test -- --grep "bug description"
5. Verify: Test FAILS (proves it catches the bug)
```

**Sources:** [README.md:321-343](), [skills/iterative-development.md:76-106]()

### Phase 2: GREEN - Minimum Implementation

Write the simplest code that makes tests pass. No premature optimization, no extra features.

```markdown
1. Implement the minimum code to pass tests
2. Run: npm test
3. If tests fail: Debug and fix
4. Repeat until all tests pass
5. Do NOT proceed to VALIDATE until tests are green
```

**Sources:** [README.md:324-331]()

### Phase 3: VALIDATE - Quality Enforcement

Once tests pass, validate code quality:

```markdown
1. Run linter: npm run lint (or ruff check)
2. Run type checker: tsc --noEmit (or mypy)
3. Run coverage: npm test -- --coverage
4. Verify: Coverage >= 80%
5. If any failures: Fix and re-run tests
```

**Sources:** [README.md:324-331](), [README.md:515-529]()

### TDD Execution Log

All todos track the TDD execution in structured tables:

```markdown
### TDD Execution Log
| Phase | Command | Result |
|-------|---------|--------|
| RED | `npm test -- --grep "email validation"` | 2 tests failed ✓ |
| GREEN | `npm test -- --grep "email validation"` | 2 tests passed ✓ |
| VALIDATE | `npm run lint && npm run typecheck && npm test -- --coverage` | Pass, 84% ✓ |
```

**Sources:** [README.md:552-558]()

---

## Atomic Todo System

### Todo File Structure

Development work is tracked through atomic todos stored in `_project_specs/todos/`:

```
_project_specs/
└── todos/
    ├── active.md          # Current work
    ├── completed.md       # Finished work (never deleted)
    └── backlog.md         # Future work
```

**Sources:** [README.md:308-312]()

### Todo Format

```markdown
## [TODO-042] Add email validation to signup form

**Status:** in-progress
**Priority:** high
**Estimate:** S

### Acceptance Criteria
- [ ] Email field shows error for invalid format
- [ ] Form cannot submit with invalid email
- [ ] Error clears when user fixes input

### Test Cases
| Input | Expected |
|-------|----------|
| user@example.com | Valid |
| notanemail | Error: "Invalid email format" |
| user@ | Error: "Invalid email format" |

### TDD Execution Log
| Phase | Command | Result |
|-------|---------|--------|
| RED | `npm test -- email-validation` | 3 tests failed ✓ |
| GREEN | `npm test -- email-validation` | 3 tests passed ✓ |
| VALIDATE | `npm run lint && npm test -- --coverage` | Pass, 82% ✓ |
```

**Sources:** [README.md:533-558]()

### Todo Lifecycle

```mermaid
graph LR
    Backlog["backlog.md"] --> Active["active.md"]
    Active --> InProgress["Status: in-progress"]
    InProgress --> TDD["Execute TDD Cycle"]
    TDD --> TDD
    TDD --> Review["Pass All Phases"]
    Review --> Complete["completed.md"]
    Complete --> Reference["Reference for<br/>future work"]
```

**Key Rules:**
- Todos move from `active.md` to `completed.md`, never deleted
- Each todo is atomic (completable in one session)
- Test cases must be defined before starting
- Completion requires all TDD phases to pass

**Sources:** [README.md:389-395](), [README.md:533-577]()

---

## Development Session Flow

### Typical Session Structure

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Claude as "Claude Code"
    participant Active as "_project_specs/todos/active.md"
    participant Ralph as "/ralph-loop"
    participant Tests as "Test Suite"
    participant State as "_project_specs/current-state.md"
    
    Dev->>Claude: "Add email validation"
    Claude->>Active: Read todo [TODO-042]
    Claude->>Ralph: Auto-invoke loop
    
    loop Ralph Iterations
        Ralph->>Tests: Write failing tests
        Tests-->>Ralph: RED: Tests fail ✓
        Ralph->>Tests: Implement feature
        Tests-->>Ralph: GREEN: Tests pass ✓
        Ralph->>Tests: Run lint + coverage
        Tests-->>Ralph: VALIDATE: Pass ✓
    end
    
    Ralph->>Active: Move to completed.md
    Ralph->>State: Update session state
    Ralph-->>Claude: <promise>DONE</promise>
    Claude->>Dev: "Feature complete"
```

**Sources:** [README.md:71-94](), [skills/iterative-development.md:50-68]()

### Workflow Phases

| Phase | Activities | Files Modified | Exit Criteria |
|-------|-----------|----------------|---------------|
| **1. Planning** | Select todo, read specs | `active.md` (status update) | Todo claimed |
| **2. RED** | Write failing tests | Test files created/modified | Tests fail |
| **3. GREEN** | Implement minimum code | Source files modified | Tests pass |
| **4. VALIDATE** | Lint, typecheck, coverage | Config files may update | All checks pass |
| **5. Complete** | Move todo, update state | `completed.md`, `current-state.md` | Todo archived |

**Sources:** [README.md:321-331]()

---

## File Structure During Development

### Core Development Files

```mermaid
graph TB
    subgraph "Project Specs (_project_specs/)"
        Active["todos/active.md<br/>(Current work)"]
        Completed["todos/completed.md<br/>(History)"]
        CurrentState["current-state.md<br/>(Session context)"]
        Decisions["decisions.md<br/>(Architecture choices)"]
        CodeIndex["CODE_INDEX.md<br/>(Semantic capabilities)"]
    end
    
    subgraph "Skills (.claude/skills/)"
        Base["base.md<br/>(TDD rules)"]
        Iterative["iterative-development.md<br/>(Ralph integration)"]
        Review["code-review.md<br/>(Quality gates)"]
    end
    
    subgraph "Quality Gates"
        PreCommit[".git/hooks/pre-commit<br/>(Local validation)"]
        PrePush[".git/hooks/pre-push<br/>(Code review)"]
        CI[".github/workflows/quality.yml<br/>(CI enforcement)"]
    end
    
    Active --> Base
    Base --> Iterative
    Iterative --> Active
    Active --> CurrentState
    
    Completed --> CurrentState
    Decisions --> CurrentState
    
    Base --> PreCommit
    Review --> PrePush
    PrePush --> CI
    
    CodeIndex --> Base
```

**Sources:** [README.md:296-317]()

### Session State Files

| File | Purpose | Updated When |
|------|---------|--------------|
| `_project_specs/current-state.md` | Current session context, progress, blockers | After each major change |
| `_project_specs/decisions.md` | Architecture and design decisions | When making technical choices |
| `_project_specs/CODE_INDEX.md` | Semantic capability index | After adding new functions |
| `_project_specs/todos/active.md` | Active work tracking | When claiming, updating, or completing todos |

**Sources:** [README.md:308-317]()

---

## Workflow Automation

### Automatic Ralph Loop Invocation

Claude automatically transforms natural language requests into iterative TDD loops:

```mermaid
graph TD
    Request["Developer: 'Add email validation'"]
    Parse["Claude: Parse request"]
    Extract["Extract requirements"]
    Structure["Structure as TDD loop"]
    Invoke["/ralph-loop invoked automatically"]
    Iterate["Iterate until tests pass"]
    Complete["Output: Feature complete"]
    
    Request --> Parse
    Parse --> Extract
    Extract --> Structure
    Structure --> Invoke
    Invoke --> Iterate
    Iterate --> Iterate
    Iterate --> Complete
```

**No manual `/ralph-loop` invocation needed.** Claude recognizes feature requests and automatically:
1. Extracts requirements
2. Identifies test cases
3. Structures as a TDD loop
4. Runs iterations until completion

**Opt-out phrases** (when you don't want loops):
- "Just explain..."
- "Quick fix..."
- "Don't loop..."

**Sources:** [README.md:71-100]()

### Commit Hygiene Monitoring

Claude automatically tracks changes and advises when to commit:

```mermaid
stateDiagram-v2
    [*] --> OK: "Start work"
    OK --> WARN: "6-10 files OR 201-400 lines"
    WARN --> STOP: "11+ files OR 401+ lines"
    OK --> Commit: "≤5 files, ≤200 lines"
    WARN --> Commit: "Good time to commit"
    STOP --> ForceCommit: "⚠️ Commit NOW"
    Commit --> [*]
    ForceCommit --> [*]
```

**Thresholds:**
- 🟢 **OK:** ≤ 5 files, ≤ 200 lines
- 🟡 **WARN:** 6-10 files, 201-400 lines → "Commit soon"
- 🔴 **STOP:** > 10 files, > 400 lines → "Commit NOW"

**Why this matters:**
- PRs < 200 lines: 15% defect rate
- PRs 200-400 lines: 23% defect rate
- PRs > 400 lines: 40%+ defect rate

**Sources:** [README.md:119-147]()

---

## Error Classification and Handling

### Error Types in Workflow

Not all failures require iteration. Claude classifies errors before deciding how to proceed:

```mermaid
graph TB
    Error["Test/Lint Failure"]
    Classify["Classify Error Type"]
    
    Code["Code/Logic Error<br/>(Wrong algorithm, bad assertion)"]
    Type["Type Error<br/>(Missing properties, wrong types)"]
    Access["Access Error<br/>(Missing API key, DB refused)"]
    Env["Environment Error<br/>(Missing dependency, wrong version)"]
    
    Fix["Fix and Continue Loop"]
    Blocker["STOP: Output Blocker Report"]
    
    Error --> Classify
    Classify --> Code
    Classify --> Type
    Classify --> Access
    Classify --> Env
    
    Code --> Fix
    Type --> Fix
    Access --> Blocker
    Env --> Blocker
    
    Fix --> Error
```

**Sources:** [skills/iterative-development.md:293-331]()

### Blocker Report Format

When Claude detects an unfixable error, it stops immediately:

```markdown
## 🛑 LOOP BLOCKED - Human Action Required

**Error Type:** Access/Environment (cannot be fixed by code changes)

**Error Message:**
ECONNREFUSED 127.0.0.1:5432 - Connection refused

**Root Cause:**
PostgreSQL database is not running or not accessible.

**Required Human Actions:**
1. [ ] Start PostgreSQL: `brew services start postgresql`
2. [ ] Verify connection: `psql -U postgres -c "SELECT 1"`
3. [ ] Check DATABASE_URL in .env matches running instance

**After Fixing:**
Run `/ralph-loop` again with the same prompt.

<promise>BLOCKED ENVIRONMENT</promise>
```

**Sources:** [skills/iterative-development.md:333-359](), [README.md:579-612]()

### Common Blockers

| Error Pattern | Likely Cause | Human Fix |
|---------------|--------------|-----------|
| `ECONNREFUSED :5432` | PostgreSQL not running | `brew services start postgresql` |
| `ECONNREFUSED :6379` | Redis not running | `brew services start redis` |
| `401 Unauthorized` | Invalid/missing API key | Check `.env` file |
| `MODULE_NOT_FOUND` | Missing npm package | Run `npm install` |
| `ENOENT .env` | Missing .env file | Create from `.env.example` |

**Sources:** [skills/iterative-development.md:361-373](), [README.md:604-612]()

---

## Integration with Quality Gates

### Multi-Layer Validation

The development workflow integrates with three quality gate layers:

```mermaid
graph TB
    Dev["Write Code<br/>(TDD Cycle)"]
    Commit["git commit"]
    Push["git push"]
    
    PreCommit["Pre-commit Hook<br/>(.git/hooks/pre-commit)"]
    PrePush["Pre-push Hook<br/>(.git/hooks/pre-push)"]
    CI["GitHub Actions<br/>(.github/workflows/)"]
    
    LintLocal["Lint + Type Check"]
    TestLocal["Unit Tests (changed files)"]
    SecretLocal["Secret Scan"]
    
    CodeReview["/code-review command"]
    SeverityCheck["Severity Classification"]
    
    FullTests["Full Test Suite"]
    Coverage["80% Coverage Check"]
    SecretCI["TruffleHog Scan"]
    DepsCI["Dependency Audit"]
    
    Dev --> Commit
    Commit --> PreCommit
    PreCommit --> LintLocal
    PreCommit --> TestLocal
    PreCommit --> SecretLocal
    
    SecretLocal --> Push
    Push --> PrePush
    PrePush --> CodeReview
    CodeReview --> SeverityCheck
    
    SeverityCheck --> CI
    CI --> FullTests
    CI --> Coverage
    CI --> SecretCI
    CI --> DepsCI
```

**Gate Behaviors:**
- **Pre-commit:** Fast checks on changed files only
- **Pre-push:** Full code review with severity-based blocking
- **CI:** Comprehensive validation with 80% coverage enforcement

For detailed information on each gate, see [Quality Gates and Code Review](#4.3).

**Sources:** [README.md:175-209](), [README.md:515-529]()

---

## Workflow Commands Reference

### Core Development Commands

| Command | Purpose | Typical Usage |
|---------|---------|---------------|
| `/initialize-project` | Set up project structure and skills | First time in new project |
| `/ralph-loop "prompt" --max-iterations N` | Manually invoke iterative loop | Complex multi-step features |
| `/cancel-ralph` | Stop active Ralph loop | Loop stuck or needs human input |
| `/code-review` | Run mandatory code review | Before pushing (auto-invoked by pre-push hook) |
| `/check-contributors` | Check team state and conflicts | Start of session in team projects |
| `/update-code-index` | Regenerate semantic capability index | After adding new functions |

**Sources:** [README.md:52-62](), [skills/iterative-development.md:52-68]()

### Ralph Loop State Management

```bash
# Check current iteration
grep '^iteration:' .claude/ralph-loop.local.md

# View full state
head -10 .claude/ralph-loop.local.md

# Cancel active loop
/cancel-ralph
```

**State file:** `.claude/ralph-loop.local.md` (gitignored, session-specific)

**Sources:** [skills/iterative-development.md:446-468]()

---

## Best Practices

### Session Start Checklist

```markdown
- [ ] Pull latest changes: `git pull`
- [ ] Check team state: `/check-contributors` (if team project)
- [ ] Review current-state.md for context
- [ ] Select todo from active.md
- [ ] Update todo status to "in-progress"
- [ ] Read acceptance criteria and test cases
```

**Sources:** [README.md:243-246]()

### During Development

```markdown
- [ ] Follow RED-GREEN-VALIDATE cycle strictly
- [ ] Monitor commit size (stay under 5 files, 200 lines if possible)
- [ ] Check CODE_INDEX.md before creating new functions
- [ ] Update current-state.md after major changes
- [ ] Document decisions in decisions.md
- [ ] Watch for blocker errors (stop and report)
```

**Sources:** [README.md:256-295](), [skills/iterative-development.md:576-595]()

### Session End Checklist

```markdown
- [ ] All tests passing
- [ ] Lint clean, types valid
- [ ] Coverage >= 80%
- [ ] Todo moved to completed.md
- [ ] current-state.md updated with progress
- [ ] Changes committed with atomic message
- [ ] Code review passed (if pushing)
```

**Sources:** [README.md:389-395](), [skills/iterative-development.md:576-595]()

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Writing implementation before tests | No proof tests validate requirements | Write tests first, verify they fail |
| Tests that always pass | False confidence | Run tests before implementation, must fail |
| Skipping VALIDATE phase | Quality issues slip through | Always run lint, typecheck, coverage |
| Fixing bugs without test first | Bug can recur | Write test that reproduces bug, then fix |
| Large commits (>10 files, >400 lines) | High defect rate, hard to review | Commit frequently at green states |
| Ignoring blocker reports | Loop wastes iterations | Stop immediately, fix environment |
| Manual loop exit without completion | Incomplete work | Let loop complete or hit max iterations |

**Sources:** [README.md:338-343](), [skills/iterative-development.md:519-527]()

---

## Summary

The Claude Bootstrap development workflow enforces a rigorous, automated TDD methodology:

1. **Atomic todos** define work with clear acceptance criteria and test cases
2. **RED-GREEN-VALIDATE** cycle ensures tests drive implementation
3. **Automatic iteration** via Ralph loops eliminates manual intervention
4. **Error classification** distinguishes fixable code issues from environment blockers
5. **Quality gates** enforce standards at commit, push, and CI levels
6. **Session management** preserves context and enables resumability

This workflow transforms natural language feature requests into production-ready code through a series of automated, validated phases, with human intervention required only for environment setup and architectural decisions.

**Sources:** [README.md:1-80](), [README.md:319-395](), [skills/iterative-development.md:1-595]()

---

# Page: Ralph Loop: Iterative Development

# Ralph Loop: Iterative Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/iterative-development.md](skills/iterative-development.md)

</details>



## Purpose and Scope

This document describes the Ralph Wiggum loop system, the core iterative development engine in Claude Bootstrap. The Ralph loop implements self-referential TDD cycles where Claude autonomously iterates on a task until completion criteria are met, with automatic error classification to distinguish between code errors (fixable by iteration) and environment/access errors (requiring human intervention).

For information about the broader development philosophy and TDD principles, see [Development Philosophy](#3.1) and [TDD Workflow](#3.2). For session management and context preservation between work sessions, see [Session Management](#4.2). For quality gates that run after loop completion, see [Quality Gates and Code Review](#4.3).

**Sources:** [README.md:71-117](), [skills/iterative-development.md:1-9]()

---

## Core Mechanism: The Stop Hook

The Ralph loop operates through a "stop hook" mechanism that intercepts Claude's exit attempts and feeds the identical prompt back with updated file state, creating a self-referential improvement cycle.

### State Machine Flow

```mermaid
stateDiagram-v2
    [*] --> InitializeLoop: "/ralph-loop prompt<br/>--max-iterations N<br/>--completion-promise text"
    
    InitializeLoop --> ReadCurrentState: "Load file state<br/>and git history"
    
    ReadCurrentState --> ExecuteTask: "Claude works on task<br/>(same prompt each iteration)"
    
    ExecuteTask --> AttemptExit: "Claude tries to exit"
    
    AttemptExit --> CheckPromise: "Stop hook intercepts"
    
    CheckPromise --> ExitSuccess: "Promise detected:<br/><promise>DONE</promise>"
    CheckPromise --> CheckIterations: "No promise yet"
    
    CheckIterations --> ExitMaxReached: "iterations >= max"
    CheckIterations --> FeedbackLoop: "iterations < max"
    
    FeedbackLoop --> ReadCurrentState: "Feed SAME prompt<br/>with modified files visible"
    
    ExitSuccess --> [*]: "Loop complete"
    ExitMaxReached --> [*]: "Incomplete, manual review needed"
    
    note right of ReadCurrentState
        Key insight: Prompt never changes
        Only file state evolves
        Claude sees own previous work
        via file modifications and git history
    end note
    
    note right of CheckPromise
        Exit detection via XML tags:
        <promise>COMPLETION_TEXT</promise>
        Must match --completion-promise flag
    end note
```

**Sources:** [skills/iterative-development.md:49-71](), [README.md:71-85]()

### File State Persistence

The loop maintains state in `.claude/ralph-loop.local.md`, which tracks:

| Field | Purpose |
|-------|---------|
| `iteration` | Current iteration count (1 to max) |
| `prompt` | Original task prompt (unchanged) |
| `max_iterations` | Hard limit to prevent infinite loops |
| `completion_promise` | Exit condition text to detect |

**File Location:** [.claude/ralph-loop.local.md]() (gitignored, session-specific)

**Sources:** [skills/iterative-development.md:464-468](), [skills/iterative-development.md:486-492]()

---

## TDD Integration: The Three Phases

Every Ralph loop enforces the RED-GREEN-VALIDATE TDD cycle as its completion criteria.

### TDD Phase State Machine

```mermaid
stateDiagram-v2
    [*] --> WriteTests: "TDD Phase 1: RED"
    
    WriteTests --> RunTests1: "Execute test command"
    
    RunTests1 --> VerifyRed: "Check results"
    
    VerifyRed --> FixTests: "Tests pass<br/>(should fail first)"
    VerifyRed --> ImplementCode: "Tests fail ✓<br/>RED confirmed"
    
    FixTests --> WriteTests: "Adjust test logic"
    
    ImplementCode --> RunTests2: "TDD Phase 2: GREEN<br/>Execute tests again"
    
    RunTests2 --> ClassifyError: "Some tests fail"
    RunTests2 --> ValidateLint: "All tests pass ✓<br/>TDD Phase 3: VALIDATE"
    
    ClassifyError --> ErrorType: "Determine error category"
    
    ErrorType --> ImplementCode: "Code/Type/Logic error<br/>(fixable)"
    ErrorType --> OutputBlocker: "Access/Network/Env error<br/>(unfixable)"
    
    ValidateLint --> RunTypeCheck: "npm run lint<br/>or ruff check"
    
    RunTypeCheck --> CheckCoverage: "tsc --noEmit<br/>or mypy"
    
    CheckCoverage --> VerifyCoverage: "npm run test:coverage<br/>or pytest --cov"
    
    VerifyCoverage --> AddTests: "Coverage < 80%"
    VerifyCoverage --> Complete: "Coverage >= 80%<br/>VALIDATE ✓"
    
    AddTests --> RunTests2: "Write additional tests"
    
    Complete --> [*]: "Output:<br/><promise>DONE</promise>"
    
    OutputBlocker --> [*]: "Output blocker report<br/><promise>BLOCKED</promise>"
    
    note right of VerifyRed
        Tests MUST fail first
        Proves test actually validates
        the requirement
    end note
    
    note right of ErrorType
        Critical decision point:
        Not all errors are fixable
        by code changes
    end note
```

**Sources:** [skills/iterative-development.md:76-106](), [README.md:17-21]()

### Completion Criteria Structure

Every Ralph prompt must include explicit completion criteria:

```markdown
### Completion Criteria
- [ ] All tests passing
- [ ] Coverage >= 80%
- [ ] Lint clean (no errors)
- [ ] TypeScript/type check passing

### Exit Condition
When ALL criteria above are TRUE, output:
<promise>ALL TESTS PASSING AND LINT CLEAN</promise>
```

**Sources:** [skills/iterative-development.md:96-105](), [skills/iterative-development.md:225-240]()

---

## Error Classification System

The loop distinguishes between errors Claude can fix through iteration and blockers requiring human intervention.

### Error Type Decision Tree

```mermaid
graph TB
    TestFail["Test execution fails"]
    
    TestFail --> Classify["Examine error message"]
    
    Classify --> CodeError{"Code/Logic Error?"}
    Classify --> TypeErrorCheck{"Type Error?"}
    Classify --> AccessError{"Access Error?"}
    Classify --> EnvError{"Environment Error?"}
    Classify --> NetworkError{"Network Error?"}
    
    CodeError -->|"AssertionError<br/>Logic bug<br/>Wrong algorithm"| ContinueLoop["CONTINUE LOOP<br/>Fix code and iterate"]
    
    TypeErrorCheck -->|"TypeError<br/>Wrong types<br/>Missing properties"| ContinueLoop
    
    AccessError -->|"ECONNREFUSED<br/>401 Unauthorized<br/>EACCES"| StopLoop["STOP LOOP<br/>Output blocker report"]
    
    EnvError -->|"MODULE_NOT_FOUND<br/>ENOENT<br/>Version mismatch"| StopLoop
    
    NetworkError -->|"Connection timeout<br/>Service unreachable<br/>DNS failure"| StopLoop
    
    ContinueLoop --> NextIteration["iteration++<br/>Feed same prompt"]
    
    StopLoop --> BlockerReport["Generate blocker report<br/>with required actions"]
    
    BlockerReport --> ExitLoop["Output promise:<br/><promise>BLOCKED</promise>"]
```

**Sources:** [skills/iterative-development.md:293-331](), [README.md:579-612]()

### Error Classification Table

| Error Type | Examples | Claude Can Fix? | Action |
|------------|----------|-----------------|--------|
| **Code Error** | Logic bug, wrong assertion, missing validation | ✅ Yes | Continue loop, fix implementation |
| **Type Error** | Wrong types, missing properties, type mismatch | ✅ Yes | Continue loop, fix types |
| **Test Error** | Wrong assertion, incomplete test coverage | ✅ Yes | Continue loop, fix tests |
| **Access Error** | Missing API key, DB connection refused, 401/403 | ❌ No | STOP + report blocker |
| **Permission Error** | File access denied (EACCES), auth failed | ❌ No | STOP + report blocker |
| **Environment Error** | Missing dependency (MODULE_NOT_FOUND), wrong version | ❌ No | STOP + report blocker |
| **Network Error** | Service unreachable (ECONNREFUSED), timeout | ❌ No | STOP + report blocker |

**Sources:** [skills/iterative-development.md:296-307]()

### Blocker Detection Patterns

Common error patterns that trigger blocker reports:

| Error Pattern | Likely Cause | Required Human Action |
|---------------|--------------|----------------------|
| `ECONNREFUSED :5432` | PostgreSQL not running | `brew services start postgresql` |
| `ECONNREFUSED :6379` | Redis not running | `brew services start redis` |
| `ECONNREFUSED :27017` | MongoDB not running | `brew services start mongodb` |
| `401 Unauthorized` | Invalid/missing API key | Check `.env` file for correct key |
| `403 Forbidden` | Wrong permissions/scopes | Verify API key permissions |
| `ENOENT .env` | Missing `.env` file | Create from `.env.example` |
| `MODULE_NOT_FOUND` | Missing npm package | Run `npm install` |
| `ENOMEM` | Out of memory | Close other apps, increase swap |

**Sources:** [skills/iterative-development.md:362-372]()

---

## Prompt Structure and Templates

Effective Ralph prompts follow a standardized structure with explicit TDD workflow and completion criteria.

### Feature Development Template

```bash
/ralph-loop "
## Task: [Feature Name]

### Requirements
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

### TDD Workflow (MUST FOLLOW)
1. Write failing tests based on requirements
2. Run tests - verify they FAIL (RED phase)
3. Implement minimum code to pass tests
4. Run tests - verify they PASS (GREEN phase)
5. Run lint and typecheck
6. If any failures, debug and fix
7. Repeat until all green

### Completion Criteria
- [ ] All tests passing
- [ ] Coverage >= 80%
- [ ] Lint clean (no errors)
- [ ] TypeScript/type check passing

### Exit Condition
When ALL criteria above are TRUE, output:
<promise>ALL TESTS PASSING AND LINT CLEAN</promise>
" --completion-promise "ALL TESTS PASSING AND LINT CLEAN" --max-iterations 30
```

**Sources:** [skills/iterative-development.md:76-106]()

### Bug Fix Template with Test Gap Analysis

```bash
/ralph-loop "
## Bug: [Bug Description]

### Reproduction
1. [Step 1]
2. [Step 2]
3. Observe: [Wrong behavior]
4. Expected: [Correct behavior]

### TDD Bug Fix Workflow (MUST FOLLOW)
1. Run existing tests - note if any catch the bug
2. Write a failing test that reproduces the bug
3. Run test - verify it FAILS (proves test catches bug)
4. Fix the bug with minimum code change
5. Run test - verify it PASSES
6. Run FULL test suite for regressions
7. Run lint and typecheck
8. If any failures, debug and fix
9. Repeat until all green

### Completion Criteria
- [ ] New test for bug exists
- [ ] New test passes
- [ ] All existing tests pass
- [ ] No regressions
- [ ] Lint clean

### Exit Condition
When ALL criteria are TRUE, output:
<promise>BUG FIXED WITH TEST</promise>
" --completion-promise "BUG FIXED WITH TEST" --max-iterations 25
```

**Sources:** [skills/iterative-development.md:108-142](), [README.md:560-577]()

### Refactoring Template (Safety-First)

```bash
/ralph-loop "
## Refactor: [What to refactor]

### Goals
- [Goal 1: e.g., Extract function, reduce complexity]
- [Goal 2: e.g., Improve naming]
- [Goal 3: e.g., Split file if > 200 lines]

### Safety Constraints
- All existing tests MUST continue to pass
- No behavior changes (refactor only)
- Coverage must not decrease

### Workflow
1. Run all tests - establish baseline (must pass)
2. Make ONE refactoring change
3. Run tests - must still pass
4. Run lint and typecheck
5. If failures, REVERT and try different approach
6. Commit working refactor
7. Repeat for next change

### Completion Criteria
- [ ] All refactoring goals met
- [ ] All tests passing
- [ ] Coverage same or higher
- [ ] Lint clean

### Exit Condition
<promise>REFACTOR COMPLETE ALL TESTS GREEN</promise>
" --completion-promise "REFACTOR COMPLETE ALL TESTS GREEN" --max-iterations 20
```

**Sources:** [skills/iterative-development.md:144-178]()

### API Development Template

```bash
/ralph-loop "
## Task: Build [API Name] API

### Endpoints Required
- POST /api/resource - Create
- GET /api/resource - List
- GET /api/resource/:id - Get one
- PUT /api/resource/:id - Update
- DELETE /api/resource/:id - Delete

### Requirements
- Input validation (Zod/Pydantic)
- Error handling with proper status codes
- Tests for each endpoint
- OpenAPI/Swagger docs

### TDD Workflow
1. Write integration tests for each endpoint
2. Run tests - all should FAIL
3. Implement endpoints one by one
4. Run tests after each endpoint
5. Continue until all pass
6. Add validation and error handling
7. Run full test suite
8. Generate API docs

### Completion Criteria
- [ ] All endpoint tests passing
- [ ] Input validation working
- [ ] Error responses correct
- [ ] Coverage >= 80%
- [ ] Lint clean

### Exit Condition
<promise>API COMPLETE WITH TESTS</promise>
" --completion-promise "API COMPLETE WITH TESTS" --max-iterations 40
```

**Sources:** [skills/iterative-development.md:180-219]()

---

## Blocker Detection and Reporting

When Claude encounters an unfixable error, it generates a structured blocker report and exits the loop.

### Blocker Report Structure

```mermaid
graph LR
    DetectError["Access/Environment<br/>error detected"]
    
    DetectError --> StopIteration["Stop iteration<br/>immediately"]
    
    StopIteration --> GenerateReport["Generate blocker report"]
    
    GenerateReport --> ErrorType["Identify error type"]
    GenerateReport --> RootCause["Analyze root cause"]
    GenerateReport --> Actions["List required actions"]
    
    ErrorType --> FormatReport["Format markdown report"]
    RootCause --> FormatReport
    Actions --> FormatReport
    
    FormatReport --> OutputPromise["Output:<br/><promise>BLOCKED</promise>"]
    
    OutputPromise --> ExitLoop["Exit loop,<br/>return control to user"]
```

**Sources:** [skills/iterative-development.md:333-359]()

### Blocker Report Format

```markdown
## 🛑 LOOP BLOCKED - Human Action Required

**Error Type:** Access/Environment (cannot be fixed by code changes)

**Error Message:**
```
ECONNREFUSED 127.0.0.1:5432 - Connection refused
```

**Root Cause:**
PostgreSQL database is not running or not accessible.

**Required Human Actions:**
1. [ ] Start PostgreSQL: `brew services start postgresql`
2. [ ] Verify connection: `psql -U postgres -c "SELECT 1"`
3. [ ] Check DATABASE_URL in .env matches running instance

**After Fixing:**
Run `/ralph-loop` again with the same prompt, or tell me to continue.

<promise>BLOCKED ENVIRONMENT</promise>
```

**Sources:** [skills/iterative-development.md:333-359](), [README.md:589-602]()

---

## Monitoring and Control

### Loop State Inspection

Check current iteration count:

```bash
grep '^iteration:' .claude/ralph-loop.local.md
```

View full loop state:

```bash
head -10 .claude/ralph-loop.local.md
```

**Sources:** [skills/iterative-development.md:445-457]()

### Cancelling Active Loop

```bash
/cancel-ralph
```

This command terminates the current loop immediately, regardless of iteration count or completion status.

**Sources:** [skills/iterative-development.md:459-462]()

### Safety Mechanisms

| Mechanism | Purpose | Configuration |
|-----------|---------|---------------|
| `--max-iterations` | Hard limit to prevent infinite loops | Required parameter, typically 20-40 |
| Error classification | Stops loop on unfixable errors | Automatic, based on error patterns |
| Blocker detection | Reports when human action needed | Automatic, outputs structured report |

**Sources:** [README.md:635-642](), [skills/iterative-development.md:242-250]()

---

## Integration with Project Structure

The Ralph loop integrates with Claude Bootstrap's project structure and workflow.

### File System Integration

```mermaid
graph TB
    ProjectRoot["Project Root"]
    
    ProjectRoot --> ClaudeDir[".claude/"]
    ProjectRoot --> SpecsDir["_project_specs/"]
    
    ClaudeDir --> LoopState[".claude/ralph-loop.local.md<br/>(gitignored, active state)"]
    
    SpecsDir --> RalphPrompts["_project_specs/ralph-prompts/"]
    SpecsDir --> TodosDir["_project_specs/todos/"]
    
    RalphPrompts --> FeatureTemplate["feature-template.md<br/>(reusable prompts)"]
    RalphPrompts --> BugFixTemplate["bug-fix-template.md"]
    RalphPrompts --> RefactorTemplate["refactor-template.md"]
    
    TodosDir --> ActiveTodos["active.md<br/>(tracks Ralph loops)"]
    TodosDir --> CompletedTodos["completed.md<br/>(loop execution logs)"]
    
    ActiveTodos --> TodoEntry["[TODO-042] Email validation<br/>Status: in-progress<br/>Method: Ralph loop"]
    
    TodoEntry --> ExecutionLog["TDD Execution Log<br/>iteration | tests | lint | status"]
```

**Sources:** [skills/iterative-development.md:472-485](), [skills/iterative-development.md:495-515]()

### Todo Integration Pattern

When a todo is executed via Ralph loop, it tracks the execution:

```markdown
## [TODO-042] Add email validation

**Status:** in-progress
**Method:** Ralph loop

### Ralph Prompt
/ralph-loop "..." --max-iterations 20 --completion-promise "..."

### TDD Execution Log
| Iteration | Tests | Lint | Status |
|-----------|-------|------|--------|
| 1 | 0/5 pass | errors | RED |
| 2 | 2/5 pass | errors | RED |
| 3 | 5/5 pass | clean | GREEN ✓ |

### Completion
- Iterations used: 3/20
- Promise detected: <promise>ALL TESTS PASSING</promise>
```

**Sources:** [skills/iterative-development.md:495-515](), [README.md:532-558]()

### Gitignore Configuration

The loop state file must be excluded from version control:

```gitignore
# Ralph loop state (session-specific)
.claude/ralph-loop.local.md
```

**Sources:** [skills/iterative-development.md:488-492]()

---

## Use Cases and Anti-Patterns

### Appropriate Use Cases

| Use Case | Why Ralph Loop Works | Typical Max Iterations |
|----------|---------------------|----------------------|
| **TDD feature development** | Tests provide clear pass/fail feedback | 20-30 |
| **Bug fixes with test gaps** | Clear reproduction → test → fix cycle | 15-25 |
| **Refactoring with test safety net** | Tests ensure no regressions during changes | 15-20 |
| **API endpoint development** | Each endpoint independently testable | 30-40 |
| **Greenfield projects** | Can iterate without breaking existing code | 20-30 |
| **Getting failing tests to pass** | Clear success criteria (all tests green) | 10-20 |

**Sources:** [skills/iterative-development.md:419-431]()

### Inappropriate Use Cases

| Use Case | Why Ralph Loop Fails | Alternative Approach |
|----------|---------------------|---------------------|
| **Subjective design decisions** | No clear "done" criteria, will loop forever | Manual iteration with human judgment |
| **UI/UX work** | Requires human aesthetic judgment | Manual development with design review |
| **One-shot operations** | No need for iteration (e.g., simple config) | Direct implementation without loop |
| **Unclear requirements** | Cannot determine completion, loops indefinitely | Define requirements first, then loop |
| **Production debugging** | Needs human oversight for live systems | Manual debugging with monitoring |

**Sources:** [skills/iterative-development.md:433-441]()

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| ❌ No `--max-iterations` flag | Loop runs forever on unclear requirements | Always set `--max-iterations` (typically 20-40) |
| ❌ Vague completion criteria | Cannot determine when done, loops indefinitely | Define explicit, measurable criteria |
| ❌ No TDD in prompt | No objective success metric | Include full TDD workflow in prompt |
| ❌ Outputting false promise to exit | Lies to escape loop, work incomplete | Let loop complete or cancel explicitly |
| ❌ Manual intervention mid-loop | Breaks autonomous iteration | Let loop complete or cancel and restart |
| ❌ Skipping test failure verification | Tests might not validate requirements | Always verify tests FAIL before implementing |

**Sources:** [skills/iterative-development.md:519-527]()

---

## Automatic Loop Invocation

Claude Bootstrap skills configure Claude to automatically invoke Ralph loops for natural language requests without explicit `/ralph-loop` commands.

### Automatic Detection Pattern

| User Request | Claude Interprets As | Auto-Loop Behavior |
|--------------|---------------------|-------------------|
| "Add email validation to signup" | Feature request with clear requirements | Automatically structures as TDD loop with completion criteria |
| "Fix the login bug" | Bug fix request | Identifies test gap → writes test → loops until fixed |
| "Build a REST API for todos" | API development | Loops until all endpoint tests pass |
| "Refactor the auth module" | Refactoring request | Loops with tests as safety net |

**Sources:** [README.md:71-95]()

### Opt-Out Phrases

To prevent automatic loop invocation for quick tasks:

| Phrase | Effect |
|--------|--------|
| "Just explain..." | Explanation only, no loop |
| "Quick fix..." | One-liner implementation, no loop |
| "Don't loop..." | Explicit opt-out from iteration |
| "Show me how..." | Educational response, no loop |

**Sources:** [README.md:96-99](), [README.md:629-635]()

---

## Example: Complete Ralph Loop Session

### Real TDD Session with Email Validation

```bash
/ralph-loop "
## Task: Add email validation to signup form

### Requirements
- Email field shows error for invalid format
- Error clears when user fixes email
- Form cannot submit with invalid email
- Valid emails pass without error

### Test Cases
| Input | Expected |
|-------|----------|
| user@example.com | Valid |
| user@sub.example.com | Valid |
| notanemail | Error |
| user@ | Error |
| @example.com | Error |

### TDD Workflow
1. Create test file: signup-validation.test.ts
2. Write tests for ALL test cases above
3. Run: npm test -- --grep 'email validation'
4. Verify: All 5 tests FAIL (RED)
5. Implement: validateEmail function
6. Run: npm test -- --grep 'email validation'
7. Verify: All 5 tests PASS (GREEN)
8. Run: npm run lint && npm run typecheck
9. If any errors, fix and re-run
10. When all green, output completion

### Completion Criteria
- [ ] 5 tests exist for email validation
- [ ] All 5 tests passing
- [ ] Lint clean
- [ ] TypeCheck passing

### Exit Condition
<promise>EMAIL VALIDATION COMPLETE</promise>
" --completion-promise "EMAIL VALIDATION COMPLETE" --max-iterations 15
```

### Expected Loop Progression

| Iteration | Action | Tests | Lint | TypeCheck | Status |
|-----------|--------|-------|------|-----------|--------|
| 1 | Write 5 failing tests | 0/5 pass | clean | pass | RED phase ✓ |
| 2 | Implement `validateEmail()` | 2/5 pass | errors | fail | Fixing implementation |
| 3 | Fix regex pattern | 4/5 pass | clean | pass | Almost there |
| 4 | Handle edge case | 5/5 pass | clean | pass | GREEN phase ✓ |
| 5 | Run final validation | 5/5 pass | clean | pass | VALIDATE phase ✓ → Exit |

**Exit Output:**
```
<promise>EMAIL VALIDATION COMPLETE</promise>
```

**Sources:** [skills/iterative-development.md:530-573]()

---

## Installation and Setup

### Installing Ralph Loop Plugin

Via official marketplace (in Claude Code):

```bash
/plugin install ralph-loop@claude-plugins-official
```

### Troubleshooting: "Source path does not exist"

If you encounter the error about `ralph-wiggum` not found, create a symlink:

```bash
ln -s ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop \
      ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-wiggum
```

Then retry the plugin installation.

**Sources:** [README.md:101-117](), [skills/iterative-development.md:34-44]()

---

## Checklist for Ralph Loop Sessions

### Before Starting Loop

- [ ] Clear completion criteria defined with measurable outcomes
- [ ] `--max-iterations` set to appropriate limit (safety net)
- [ ] `--completion-promise` set to match exit condition
- [ ] Full TDD workflow included in prompt
- [ ] Test cases defined with expected inputs/outputs
- [ ] Error classification logic included if complex

### During Loop Execution

- [ ] Monitor iteration count via `.claude/ralph-loop.local.md`
- [ ] Check test results each iteration for progress
- [ ] Watch for repeating patterns (indicates stuck)
- [ ] Look for blocker reports in output

### After Loop Completion

- [ ] Verify all tests actually pass (run test suite)
- [ ] Run full test suite to check for regressions
- [ ] Check coverage meets threshold (≥80%)
- [ ] Review and commit changes
- [ ] Update todo status: `active.md` → `completed.md`

**Sources:** [skills/iterative-development.md:576-595]()

---

# Page: Session Management

# Session Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/base.md](skills/base.md)
- [skills/session-management.md](skills/session-management.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



## Purpose and Scope

Session Management provides context preservation across long development cycles and enables seamless resumption after breaks or context limit resets. This system maintains state through a structured file hierarchy in `_project_specs/session/`, implements a three-tier checkpoint strategy based on work significance, and integrates with the Ralph loop iteration system and atomic todo workflow.

For information about the Ralph loop's iterative development cycles, see [Ralph Loop: Iterative Development](#4.1). For details on atomic todos and the `_project_specs/` directory structure, see [Atomic Todos and Project Specs](#3.4).

**Sources:** [skills/session-management.md:1-14](), [skills/base.md:456-478]()

---

## Core Principle: Tiered Checkpointing

The session management system uses a three-tier checkpoint strategy that balances documentation overhead with context preservation needs. Each tier has specific triggers and update requirements.

### Checkpoint Decision Tree

```mermaid
flowchart TD
    TaskComplete["Task Completed"]
    DecisionMade{"Decision<br/>Made?"}
    ToolCallCheck{">10 Tool<br/>Calls?"}
    MajorFeature{"Major Feature<br/>Complete?"}
    SessionEnd{"Ending<br/>Session?"}
    
    QuickUpdate["Tier 1: Quick Update<br/>current-state.md only"]
    FullCheckpoint["Tier 2: Full Checkpoint<br/>current-state.md + decisions.md"]
    Archive["Tier 3: Archive<br/>archive/*.md + full checkpoint"]
    
    TaskComplete --> DecisionMade
    DecisionMade -->|Yes| LogDecision["Log to<br/>decisions.md"]
    LogDecision --> ToolCallCheck
    DecisionMade -->|No| ToolCallCheck
    
    ToolCallCheck -->|Yes| FullCheckpoint
    ToolCallCheck -->|No| MajorFeature
    
    MajorFeature -->|Yes| Archive
    MajorFeature -->|No| SessionEnd
    
    SessionEnd -->|Yes| Archive
    SessionEnd -->|No| QuickUpdate
```

**Sources:** [skills/session-management.md:17-60]()

### Tier Specifications

| Tier | Trigger Conditions | Files Updated | Time Cost |
|------|-------------------|---------------|-----------|
| **Tier 1: Quick Update** | After completing small task/todo | `current-state.md` (Active Task, Progress, Next Steps) | ~30 seconds |
| **Tier 2: Full Checkpoint** | After feature completion, architectural decision, ~20 tool calls, or context switch | `current-state.md` (all sections) + `decisions.md` | ~2-3 minutes |
| **Tier 3: Session Archive** | End of session, major milestone, or ~50+ tool calls | `archive/YYYY-MM-DD[-topic].md` + full checkpoint + `code-landmarks.md` | ~5 minutes |

**Sources:** [skills/session-management.md:17-48]()

---

## Session State Files

The session management system maintains four primary file types in the `_project_specs/session/` directory.

### Directory Structure

```mermaid
graph TB
    subgraph "_project_specs/session/"
        CurrentState["current-state.md<br/>(Live session state)"]
        Decisions["decisions.md<br/>(Append-only decision log)"]
        Landmarks["code-landmarks.md<br/>(Code navigation)"]
        ArchiveDir["archive/<br/>(Historical records)"]
        
        Archive1["2025-01-15.md"]
        Archive2["2025-01-14-auth.md"]
        Archive3["2025-01-12.md"]
        
        ArchiveDir --> Archive1
        ArchiveDir --> Archive2
        ArchiveDir --> Archive3
    end
```

**Sources:** [skills/session-management.md:64-76](), [skills/base.md:118-122]()

### File Purposes

| File | Update Frequency | Purpose | Format |
|------|------------------|---------|--------|
| `current-state.md` | Every task completion (Tier 1+) | Live session state, active task tracking, next steps | Structured markdown with status tables |
| `decisions.md` | When architectural/library decisions made (Tier 2+) | Append-only decision log with reasoning and trade-offs | Dated entries with context and references |
| `code-landmarks.md` | When new patterns introduced (Tier 3) | Navigation map for important code locations and patterns | Tables of entry points, core logic, configurations |
| `archive/*.md` | End of session or major feature (Tier 3) | Historical record of completed work | Session summary with tasks, changes, stats |

**Sources:** [skills/session-management.md:514-521]()

---

## Current State File Format

The `current-state.md` file is the primary live state document, updated at every checkpoint tier. It uses a structured format optimized for quick scanning and resumption.

### Template Structure

```markdown
# Current Session State

*Last updated: 2025-01-15 14:32*

## Active Task
[One sentence: what are we working on right now]

## Current Status
- **Phase**: [exploring | planning | implementing | testing | debugging | refactoring]
- **Progress**: [X of Y steps complete, or percentage]
- **Blocking Issues**: [None, or describe blockers]

## Context Summary
[2-3 sentences summarizing the current state of work]

## Files Being Modified
| File | Status | Notes |
|------|--------|-------|
| src/auth/middleware.ts | Done | JWT verification |
| src/auth/refresh.ts | In Progress | Token rotation |

## Next Steps
1. [ ] Complete refresh token rotation in refresh.ts
2. [ ] Add token blacklist for logout
3. [ ] Write integration tests for auth flow

## Key Context to Preserve
- Using RS256 algorithm (not HS256) per security requirements
- Refresh tokens stored in HttpOnly cookies
- Access tokens: 15 min, Refresh tokens: 7 days

## Resume Instructions
To continue this work:
1. Read src/auth/refresh.ts - currently at line 45
2. The rotateRefreshToken() function needs error handling
3. Check decisions.md for why we chose RS256 over HS256
```

**Sources:** [skills/session-management.md:80-128]()

### Update Requirements by Tier

```mermaid
stateDiagram-v2
    [*] --> Tier1_QuickUpdate
    
    Tier1_QuickUpdate: Tier 1: Quick Update
    note right of Tier1_QuickUpdate
        Update sections:
        - Active Task
        - Current Status (Progress)
        - Next Steps
    end note
    
    Tier1_QuickUpdate --> Tier2_FullCheckpoint: Decision made OR<br/>20+ tool calls OR<br/>context switch
    
    Tier2_FullCheckpoint: Tier 2: Full Checkpoint
    note right of Tier2_FullCheckpoint
        Update all sections:
        - All Tier 1 sections
        - Context Summary
        - Files Being Modified (full table)
        - Key Context to Preserve
        - Resume Instructions
    end note
    
    Tier2_FullCheckpoint --> Tier3_Archive: Session end OR<br/>major feature OR<br/>50+ tool calls
    
    Tier3_Archive: Tier 3: Archive
    note right of Tier3_Archive
        Actions:
        - Create archive/YYYY-MM-DD.md
        - Full checkpoint of current-state.md
        - Update code-landmarks.md
        - Clear verbose notes from current-state.md
    end note
    
    Tier3_Archive --> [*]
```

**Sources:** [skills/session-management.md:17-48]()

---

## Decision Log Format

The `decisions.md` file is an append-only log of architectural and implementation decisions. This file never has entries removed, preserving the full decision history.

### Entry Template

```markdown
## [YYYY-MM-DD] Decision Title

**Decision**: Brief statement of the choice made

**Context**: What situation prompted this decision

**Options Considered**:
1. Option A - Description
2. Option B - Description
3. Option C - Description

**Choice**: Option B

**Reasoning**:
- Reason 1 for this choice
- Reason 2 for this choice
- Reason 3 for this choice

**Trade-offs**:
- Negative aspect 1
- Negative aspect 2

**References**:
- src/path/to/implementation - Implementation location
- docs/architecture.md - Related documentation
```

**Sources:** [skills/session-management.md:132-191]()

### Integration with Ralph Loop

When the Ralph loop makes architectural decisions during iterative development, those decisions are logged to `decisions.md` as part of the Tier 2 checkpoint triggered by significant progress.

```mermaid
sequenceDiagram
    participant Ralph as "/ralph-loop"
    participant Code as "Code Files"
    participant Decision as "decisions.md"
    participant State as "current-state.md"
    
    Ralph->>Code: Implement feature
    Code->>Ralph: Tests pass
    Ralph->>Ralph: Check: Decision made?
    Ralph->>Decision: Append decision entry
    Decision->>State: Reference decision
    State->>Ralph: Checkpoint complete
```

**Sources:** [skills/session-management.md:407-410](), [skills/base.md:462-466]()

---

## Code Landmarks File

The `code-landmarks.md` file provides a navigation map for the codebase, updated when new patterns are introduced (typically during Tier 3 archives).

### Structure

The file is organized into sections that map conceptual areas to concrete file locations:

| Section | Purpose | Example Entries |
|---------|---------|-----------------|
| **Entry Points** | Main application entry locations | `src/index.ts`, `src/api/routes.ts`, `src/workers/index.ts` |
| **Core Business Logic** | Primary domain logic locations | `src/core/auth/`, `src/core/billing/`, `src/core/workflows/` |
| **Configuration** | Configuration file locations | `src/config/index.ts`, `drizzle.config.ts` |
| **Key Patterns** | Architectural pattern implementations | Service layer, Repository pattern, Middleware |
| **Testing** | Test organization | `tests/unit/`, `tests/integration/`, `tests/e2e/` |
| **Gotchas & Non-Obvious Behavior** | Important caveats | Timezone handling, auth bypass rules, connection limits |

**Sources:** [skills/session-management.md:195-246]()

### Example Entry Format

```markdown
## Core Business Logic
| Location | Purpose |
|----------|---------|
| src/core/auth/ | Authentication system |
| src/core/billing/ | Payment processing |
| src/core/workflows/ | Main workflow engine |

## Gotchas & Non-Obvious Behavior
| Location | Issue | Notes |
|----------|-------|-------|
| src/utils/date.ts | Timezone handling | Always use UTC internally |
| src/api/middleware.ts:45 | Auth bypass | Skip auth for health checks |
```

**Sources:** [skills/session-management.md:211-246]()

---

## Session Archive Format

Session archives are created during Tier 3 checkpoints and stored in `_project_specs/session/archive/`. The filename format is `YYYY-MM-DD[-optional-topic].md`.

### Archive Template

```markdown
# Session Archive: [Date] - [Topic]

## Summary
[Paragraph summarizing what was accomplished]

## Tasks Completed
- [TODO-XXX] Description - Done
- [TODO-YYY] Description - Done

## Key Decisions
- [Reference decisions.md entries made this session]

## Code Changes
| File | Change Type | Description |
|------|-------------|-------------|
| src/auth/login.ts | Created | Login endpoint |
| src/auth/types.ts | Modified | Added RefreshToken type |

## Tests Added
- tests/auth/login.test.ts - Login flow tests
- tests/auth/refresh.test.ts - Token refresh tests

## Open Items Carried Forward
- [Anything not finished, now in active.md]

## Session Stats
- Duration: ~3 hours
- Tool calls: ~120
- Files modified: 8
- Tests added: 12
```

**Sources:** [skills/session-management.md:345-383]()

### Compression Strategy

When creating archives, verbose details are compressed while preserving actionable information:

| Keep in Active Context | Archive/Summarize |
|------------------------|-------------------|
| Current task and immediate next steps | Exploration paths that didn't work |
| Active file list with status | Detailed debugging traces (keep conclusion) |
| Blocking issues | Verbose error messages (keep root cause) |
| Key decisions affecting current work | Research notes (keep recommendations) |

**Sources:** [skills/session-management.md:298-342]()

---

## Checkpoint Trigger Integration

Session management integrates with multiple system components to trigger checkpoints at appropriate times.

### Integration with Todo System

```mermaid
flowchart LR
    subgraph "Todo Workflow"
        ActiveTodo["active.md<br/>[TODO-XXX] In Progress"]
        Complete["Todo Completed"]
        CompletedMd["completed.md<br/>[TODO-XXX] Done"]
    end
    
    subgraph "Session Management"
        QuickUpdate["Quick Update<br/>current-state.md"]
        DecisionCheck{"Decision<br/>Made?"}
        LogDecision["Log to<br/>decisions.md"]
        FullCheckpoint["Full Checkpoint"]
        UpdateLandmarks["Update<br/>code-landmarks.md"]
    end
    
    ActiveTodo --> Complete
    Complete --> QuickUpdate
    QuickUpdate --> DecisionCheck
    DecisionCheck -->|Yes| LogDecision
    DecisionCheck -->|No| CompletedMd
    LogDecision --> FullCheckpoint
    FullCheckpoint --> UpdateLandmarks
    UpdateLandmarks --> CompletedMd
```

**Sources:** [skills/session-management.md:387-410](), [skills/base.md:209-213]()

### Integration with Ralph Loop

The Ralph loop automatically triggers checkpoints based on iteration count and completion status:

| Ralph Loop Event | Session Management Action |
|------------------|--------------------------|
| Every 10 iterations | Check if ~20 tool calls → Tier 2 checkpoint if threshold reached |
| Decision made during iteration | Log to `decisions.md` + Tier 2 checkpoint |
| Loop completion (promise fulfilled) | Tier 2 checkpoint + update `active.md` |
| Loop max iterations reached | Tier 3 archive (session likely ending due to complexity) |

**Sources:** [skills/session-management.md:24-30]()

### Integration with CLAUDE.md

The `CLAUDE.md` file includes session management rules that Claude reads at project initialization:

```markdown
## Session Management

**IMPORTANT**: Follow session-management.md skill. Update session state at natural breakpoints.

### After Every Task Completion
Ask yourself:
1. Was a decision made? → Log to `decisions.md`
2. Did this take >10 tool calls? → Full checkpoint to `current-state.md`
3. Is a major feature complete? → Create archive entry
4. Otherwise → Quick update to `current-state.md`

### Session Start Protocol
When beginning work:
1. Read `_project_specs/session/current-state.md`
2. Check `_project_specs/todos/active.md`
3. Review recent `decisions.md` entries if needed
4. Continue from "Next Steps"
```

**Sources:** [skills/session-management.md:250-294](), [templates/CLAUDE.md:108-113]()

---

## Enforcement Mechanisms

The session management system uses multiple enforcement mechanisms to ensure checkpoints occur reliably.

### Self-Check Protocol

After completing any task, Claude executes this self-check:

```mermaid
flowchart TD
    TaskDone["Task Completed"]
    Q1{"Decision<br/>Made?"}
    Q2{">10 Tool<br/>Calls?"}
    Q3{"Feature<br/>Complete?"}
    Q4{"Ending/<br/>Switching?"}
    
    A1["✓ Log to decisions.md"]
    A2["✓ Full Checkpoint"]
    A3["✓ Archive"]
    A4["✓ Archive + Handoff"]
    A5["✓ Quick Update"]
    
    TaskDone --> Q1
    Q1 -->|Yes| A1
    Q1 -->|No| Q2
    Q2 -->|Yes| A2
    Q2 -->|No| Q3
    Q3 -->|Yes| A3
    Q3 -->|No| Q4
    Q4 -->|Yes| A4
    Q4 -->|No| A5
```

**Sources:** [skills/session-management.md:455-463]()

### File Header Reminders

Session files include enforcement reminders in their headers:

```markdown
<!--
CHECKPOINT RULES (from session-management.md):
- Quick update: After any todo completion
- Full checkpoint: After ~20 tool calls or decisions
- Archive: End of session or major feature complete
-->
```

**Sources:** [skills/session-management.md:443-454]()

### Session Start Verification

When starting a session, Claude must verify state files exist and report their contents:

1. Check if `current-state.md` exists
2. Read and parse the file
3. Announce: "Resuming from: [last state summary]"
4. Confirm next steps before proceeding

**Sources:** [skills/session-management.md:465-469]()

### Periodic Self-Audit

Every ~20 tool calls during active development, Claude performs a self-audit:

- Is `current-state.md` up to date?
- Are there unlogged decisions?
- Is context getting heavy (approaching 50+ tool calls)?
- Should compression/archiving occur?

**Sources:** [skills/session-management.md:471-475]()

---

## Session Lifecycle

The complete session lifecycle from initialization through archival demonstrates how all components work together.

### Session Flow

```mermaid
stateDiagram-v2
    [*] --> SessionStart
    
    SessionStart: Session Start
    note right of SessionStart
        1. Read current-state.md
        2. Check active.md todos
        3. Review recent decisions.md
        4. Announce resume point
    end note
    
    SessionStart --> ActiveWork
    
    ActiveWork: Active Development
    note right of ActiveWork
        Working on tasks
        Making changes
        Running tests
    end note
    
    ActiveWork --> CheckpointDecision: Task completed
    
    CheckpointDecision: Evaluate Checkpoint Tier
    
    CheckpointDecision --> Tier1: Simple task
    CheckpointDecision --> Tier2: Decision OR 20+ calls
    CheckpointDecision --> Tier3: Feature done OR session end
    
    Tier1: Quick Update
    note right of Tier1
        Update current-state.md:
        - Active Task
        - Progress
        - Next Steps
    end note
    
    Tier2: Full Checkpoint
    note right of Tier2
        Update:
        - Full current-state.md
        - decisions.md (if decision)
        - Files table
    end note
    
    Tier3: Archive
    note right of Tier3
        Create:
        - archive/YYYY-MM-DD.md
        - Update code-landmarks.md
        - Compress current-state.md
    end note
    
    Tier1 --> ContinueCheck: More work?
    Tier2 --> ContinueCheck: More work?
    Tier3 --> ContinueCheck: More work?
    
    ContinueCheck --> ActiveWork: Yes
    ContinueCheck --> [*]: No (Session End)
```

**Sources:** [skills/session-management.md:280-294]()

---

## Anti-Patterns and Common Mistakes

The session management skill documents anti-patterns to avoid:

| Anti-Pattern | Consequence | Correct Approach |
|-------------|-------------|------------------|
| No state tracking | Can't resume sessions, context lost | Always maintain `current-state.md` |
| Overly verbose state | Files become unreadable | Keep scannable, use archives for detail |
| Stale state files | Files become useless, misleading | Update at every checkpoint tier |
| Missing decisions | Future sessions don't understand "why" | Log all decisions to `decisions.md` |
| No code landmarks | Time wasted re-discovering code structure | Update landmarks when patterns change |
| Never archiving | Session files become cluttered | Archive at Tier 3 triggers |
| Ignoring compression signals | Context overload degrades quality | Archive when approaching 50+ tool calls |
| Skipping checkpoint after decisions | Key context lost forever | Decisions always trigger Tier 2 |
| No handoff at session end | Next session starts blind | Always create archive at session end |

**Sources:** [skills/session-management.md:486-497]()

---

## Command Aliases

The session management skill recommends adding command aliases for quick access:

```bash
# Show current session state
alias session-status="cat _project_specs/session/current-state.md"

# Quick edit session state
alias session-edit="$EDITOR _project_specs/session/current-state.md"

# View recent decisions
alias decisions="tail -100 _project_specs/session/decisions.md"

# Create session archive
session-archive() {
  cp _project_specs/session/current-state.md \
     "_project_specs/session/archive/$(date +%Y-%m-%d).md"
  echo "Archived to _project_specs/session/archive/$(date +%Y-%m-%d).md"
}
```

**Sources:** [skills/session-management.md:413-434]()

---

# Page: Quality Gates and Code Review

# Quality Gates and Code Review

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



## Purpose and Scope

This document describes Claude Bootstrap's multi-layer quality enforcement system that prevents defective code from progressing through the development pipeline. The system implements defense-in-depth validation through local pre-commit hooks, mandatory code review via `/code-review`, commit hygiene monitoring, and CI/CD validation with coverage enforcement.

For information about the iterative TDD workflow that produces code validated by these gates, see [Ralph Loop: Iterative Development](#4.1). For session context preservation after passing quality gates, see [Session Management](#4.2).

---

## Multi-Layer Enforcement Architecture

Claude Bootstrap implements five progressive layers of quality validation. Each layer catches different classes of issues, and failure at any layer triggers feedback to the development loop.

### Defense-in-Depth Layers

| Layer | Stage | Validation Type | Blocks On |
|-------|-------|----------------|-----------|
| **1. Pre-Commit Hooks** | `git commit` | Lint, type check, unit tests, secret scan | Any failure |
| **2. Commit Hygiene** | During development | PR size tracking | Advisory warnings |
| **3. Pre-Push Review** | `git push` | `/code-review` analysis | Critical/High issues |
| **4. CI/CD Validation** | GitHub Actions | Full test suite, coverage, security | Any failure |
| **5. Deployment Gates** | Production release | Final validation | Below 80% coverage |

**Sources:** [README.md:515-529](), [README.md:176-209]()

---

## Layer 1: Pre-Commit Hooks

Pre-commit hooks execute fast local validation on every commit attempt, providing immediate feedback before code enters version control.

### Pre-Commit Validation Pipeline

```mermaid
graph LR
    A["git commit"]
    B["pre-commit hook"]
    C["Lint<br/>(auto-fix)"]
    D["Type Check"]
    E["Unit Tests<br/>(changed files)"]
    F["Secret Scan<br/>(security-check.sh)"]
    G["Check .env<br/>not staged"]
    H["Commit Allowed"]
    I["Commit Blocked"]
    J["Fix Issues"]
    
    A --> B
    B --> C
    C -->|Pass| D
    C -->|Fail| I
    D -->|Pass| E
    D -->|Fail| I
    E -->|Pass| F
    E -->|Fail| I
    F -->|Pass| G
    F -->|Fail| I
    G -->|Pass| H
    G -->|Fail| I
    I --> J
    J --> A
```

**Sources:** [README.md:517-523]()

### Installation

Pre-commit hooks are installed via a script in the global Claude installation:

```bash
~/.claude/install-hooks.sh
```

This script creates or updates `.git/hooks/pre-commit` in the current repository.

**Sources:** [README.md:190-192]()

### Validation Commands by Stack

**Node.js/TypeScript:**
```bash
# Pre-commit runs:
npm run lint          # ESLint with auto-fix
npm run typecheck     # TypeScript compiler (tsc --noEmit)
npm test -- --onlyChanged --bail  # Jest/Vitest on changed files
./scripts/security-check.sh       # Secret detection
```

**Python:**
```bash
# Pre-commit runs:
ruff check . --fix    # Linting with auto-fix
mypy .                # Type checking
pytest tests/ --exitfirst  # Tests on changed modules
./scripts/security-check.sh
```

**Sources:** [base.md:217-253]()

### Blocking Conditions

The pre-commit hook blocks when:

| Condition | Severity | Action |
|-----------|----------|--------|
| Linter errors | Error | Block (warnings may pass) |
| Type check failures | Error | Block |
| Test failures | Error | Block |
| Secrets detected | Critical | Block |
| `.env` file staged | Critical | Block |

**Sources:** [base.md:448-452](), [README.md:360-364]()

---

## Layer 2: Commit Hygiene Monitoring

Claude automatically tracks changes during development and advises when to commit, preventing oversized PRs that correlate with higher defect rates.

### Commit Size Thresholds

```mermaid
graph TB
    subgraph "PR Size Impact on Defect Rate"
        A["🟢 OK<br/>≤5 files<br/>≤200 lines<br/>15% defect rate"]
        B["🟡 WARN<br/>6-10 files<br/>201-400 lines<br/>23% defect rate"]
        C["🔴 STOP<br/>>10 files<br/>>400 lines<br/>40%+ defect rate"]
    end
    
    D["Claude monitors<br/>git status"]
    E["Advises:<br/>Tests passing.<br/>Good time to commit!"]
    F["Advises:<br/>Approaching threshold.<br/>Consider committing."]
    G["Advises:<br/>Changes too large!<br/>Commit NOW."]
    
    D --> A
    D --> B
    D --> C
    
    A --> E
    B --> F
    C --> G
```

**Sources:** [README.md:119-147]()

### Automatic Tracking

Claude checks commit size after completing todos or when running quality checks:

| Files Changed | Lines Changed | Status | Claude Action |
|---------------|---------------|--------|---------------|
| ≤5 | ≤200 | 🟢 OK | "Good time to commit!" |
| 6-10 | 201-400 | 🟡 WARN | "Approaching threshold. Consider committing." |
| >10 | >400 | 🔴 STOP | "Changes too large! Commit now." |

### Atomic Commit Principle

If describing a commit requires the word "and", it should be split into multiple commits:

- ❌ "Add authentication and fix bug in signup"
- ✅ "Add authentication" + "Fix signup validation bug"

**Sources:** [README.md:119-147](), [skills/commit-hygiene.md]() (referenced but not provided)

---

## Layer 3: Pre-Push Code Review

Every push requires code review analysis via the `/code-review` command, which blocks pushes containing Critical or High severity issues.

### Code Review Command Flow

```mermaid
graph TB
    A["Developer runs<br/>git push"]
    B["pre-push hook<br/>triggers"]
    C["/code-review<br/>command"]
    D["Analyze Changes:<br/>- Security<br/>- Performance<br/>- Architecture<br/>- Code Quality"]
    E["Classify Issues<br/>by Severity"]
    F["🔴 Critical/<br/>🟠 High"]
    G["🟡 Medium/<br/>🟢 Low"]
    H["Push BLOCKED"]
    I["Push ALLOWED<br/>(with warnings)"]
    J["Fix Issues"]
    K["GitHub Actions"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    F --> H
    G --> I
    H --> J
    J --> A
    I --> K
```

**Sources:** [README.md:176-209]()

### Severity Classification

The code review system classifies issues into four severity levels:

| Level | Symbol | Description | Push Allowed? | Required Action |
|-------|--------|-------------|---------------|-----------------|
| **Critical** | 🔴 | Security vulnerabilities, data loss risks | ❌ BLOCKED | Must fix now |
| **High** | 🟠 | Performance issues, architectural violations | ❌ BLOCKED | Must fix now |
| **Medium** | 🟡 | Code quality, maintainability concerns | ✅ Advisory | Fix soon |
| **Low** | 🟢 | Style suggestions, nice-to-haves | ✅ Advisory | Optional |

**Sources:** [README.md:194-201]()

### Issue Categories Detected

**Security (Critical/High):**
- SQL injection vulnerabilities
- XSS attack vectors
- Hardcoded secrets or API keys
- Insecure authentication patterns
- Missing input validation

**Performance (High/Medium):**
- N+1 query patterns
- Memory leaks
- Inefficient algorithms
- Missing database indexes

**Architecture (High/Medium):**
- Tight coupling between modules
- SOLID principle violations
- Circular dependencies
- God objects/files (>200 lines)

**Code Quality (Medium/Low):**
- Complexity violations (>20 lines/function)
- Missing type annotations
- Code duplication
- Missing test coverage

**Sources:** [README.md:203-207]()

### Pre-Push Hook Integration

To enable automatic code review on push:

```bash
~/.claude/install-hooks.sh
```

This creates `.git/hooks/pre-push` that invokes `/code-review` before allowing the push.

**Sources:** [README.md:189-192]()

### Manual Code Review

Developers can manually trigger code review at any time:

```bash
claude
> /code-review
```

This analyzes all uncommitted changes and provides the same severity-based feedback without blocking any operations.

**Sources:** [README.md:184-186]()

---

## Layer 4: CI/CD Validation

GitHub Actions workflows provide comprehensive validation on every push, enforcing quality requirements that cannot be bypassed.

### CI/CD Workflow Architecture

```mermaid
graph TB
    A["git push<br/>(passed local gates)"]
    B["GitHub Actions<br/>Triggered"]
    C["quality.yml<br/>workflow"]
    D["security.yml<br/>workflow"]
    
    subgraph "quality.yml Pipeline"
        E["Full Lint"]
        F["Full Type Check"]
        G["Full Test Suite"]
        H["Coverage Report"]
        I["Coverage ≥ 80%?"]
    end
    
    subgraph "security.yml Pipeline"
        J["TruffleHog<br/>Secret Scanning"]
        K["npm audit /<br/>safety check"]
        L["Dependency<br/>Vulnerabilities?"]
    end
    
    M["All Pass"]
    N["CI Failed"]
    O["Merge Approved"]
    P["Fix Issues"]
    
    A --> B
    B --> C
    B --> D
    
    C --> E --> F --> G --> H --> I
    D --> J --> K --> L
    
    I -->|"Yes"| M
    I -->|"No"| N
    L -->|"None"| M
    L -->|"Found"| N
    
    M --> O
    N --> P
    P --> A
```

**Sources:** [README.md:525-529]()

### quality.yml Workflow

The quality workflow enforces code standards:

**Location:** `.github/workflows/quality.yml`

**Stages:**
1. **Lint** - Full codebase linting (no auto-fix in CI)
2. **Type Check** - Complete type validation
3. **Test Suite** - All tests executed
4. **Coverage** - Must be ≥80% or build fails

**Example (Node.js):**
```yaml
- name: Run tests with coverage
  run: npm test -- --coverage --coverageReporters=text-summary
  
- name: Check coverage threshold
  run: |
    coverage=$(npm test -- --coverage --coverageReporters=json | jq '.total.lines.pct')
    if (( $(echo "$coverage < 80" | bc -l) )); then
      echo "Coverage $coverage% is below 80% threshold"
      exit 1
    fi
```

**Sources:** [README.md:525-528]()

### security.yml Workflow

The security workflow scans for vulnerabilities:

**Location:** `.github/workflows/security.yml`

**Stages:**
1. **TruffleHog** - Scans git history for secrets
2. **Dependency Audit** - Checks for known vulnerabilities
3. **Pattern Detection** - Searches for common secret patterns

**Example:**
```yaml
- name: Run TruffleHog scan
  run: |
    docker run --rm -v "$(pwd):/src" \
      trufflesecurity/trufflehog:latest \
      filesystem /src --fail

- name: Audit dependencies
  run: npm audit --audit-level=moderate
```

**Sources:** [README.md:529](), [README.md:364]()

### Coverage Enforcement Mechanism

```mermaid
graph LR
    A["Test Suite<br/>Execution"]
    B["Coverage Report<br/>Generated"]
    C["Calculate<br/>Total %"]
    D["Coverage ≥ 80%"]
    E["Coverage < 80%"]
    F["Build Pass"]
    G["Build FAIL"]
    
    A --> B
    B --> C
    C --> D
    C --> E
    D --> F
    E --> G
```

**Coverage Targets by Code Type:**

| Code Type | Coverage Target | Rationale |
|-----------|----------------|-----------|
| Business logic (core/) | 100% | Critical functionality |
| API endpoints | ≥90% | High user impact |
| Utilities | ≥85% | Reused across codebase |
| UI components | ≥80% | Minimum threshold |
| Configuration | ≥70% | Lower complexity |

**Sources:** [base.md:440-445](), [README.md:356]()

---

## Layer 5: TDD Execution Validation

The quality gates system validates that TDD workflow was followed correctly, not just that tests pass at the end.

### TDD Execution Log Requirement

Every todo must document its TDD execution phases:

```markdown
### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| RED | `npm test -- --grep "email validation"` | 2 tests failed ✓ | 2024-01-15 10:30 |
| GREEN | `npm test -- --grep "email validation"` | 2 tests passed ✓ | 2024-01-15 10:45 |
| VALIDATE | `npm run lint && npm run typecheck && npm test -- --coverage` | Pass, 84% ✓ | 2024-01-15 10:50 |
```

**Sources:** [base.md:172-177](), [README.md:533-577]()

### Validation Phase Commands

**Full validation command pattern:**

```bash
# Node.js/TypeScript
npm run lint && npm run typecheck && npm test -- --coverage

# Python
ruff check . && mypy . && pytest --cov --cov-fail-under=80

# React/Next.js
npm run lint && npm run typecheck && npm test -- --coverage --watchAll=false
```

**Sources:** [base.md:226-252]()

### Quality Gate Blocking Conditions

Tests and code cannot be marked complete if:

| Blocking Condition | Reason | Action Required |
|-------------------|--------|-----------------|
| Tests not written first | Skipped RED phase | Write tests before implementation |
| Tests didn't fail initially | Invalid test | Fix test to properly validate requirement |
| Any test failing | Implementation incomplete | Fix code until tests pass |
| Linter errors | Code quality violation | Fix lint errors |
| Type check errors | Type safety violation | Fix type errors |
| Coverage < 80% | Insufficient testing | Add tests for uncovered branches |

**Sources:** [base.md:254-263]()

---

## Integration with Ralph Loop

The Ralph Wiggum loop automatically integrates quality gates into its iterative TDD cycles.

### Ralph Loop with Quality Gates

```mermaid
stateDiagram-v2
    [*] --> WriteTests: "RED Phase"
    
    WriteTests --> RunTestsRed: "Execute tests"
    
    RunTestsRed --> VerifyFail: "Tests MUST fail"
    
    VerifyFail --> Implement: "RED ✓<br/>Continue"
    VerifyFail --> FixTests: "Tests pass<br/>(Invalid!)"
    
    FixTests --> WriteTests
    
    Implement --> RunTestsGreen: "GREEN Phase<br/>Execute tests"
    
    RunTestsGreen --> Validate: "Tests pass ✓"
    RunTestsGreen --> Implement: "Tests fail<br/>(Fix code)"
    
    Validate --> Lint: "VALIDATE Phase<br/>Run lint"
    
    Lint --> TypeCheck: "Lint pass"
    Lint --> Implement: "Lint fail<br/>(Fix)"
    
    TypeCheck --> Coverage: "Type check pass"
    TypeCheck --> Implement: "Type fail<br/>(Fix)"
    
    Coverage --> CheckThreshold: "Run coverage"
    
    CheckThreshold --> Complete: "≥80% ✓"
    CheckThreshold --> AddTests: "<80%"
    
    AddTests --> RunTestsGreen
    
    Complete --> [*]: "Quality gates<br/>passed"
```

**Sources:** [base.md:189-214](), Diagram 4 from context

### Error Classification in Quality Gates

Ralph loop classifies validation errors to determine whether to continue iterating or stop:

| Error Type | Examples | Ralph Action | Reason |
|------------|----------|--------------|--------|
| **Code Error** | Logic bug, wrong assertion, missing case | Continue loop | Claude can fix |
| **Type Error** | Type mismatch, missing property | Continue loop | Claude can fix |
| **Lint Error** | Complexity violation, unused variable | Continue loop | Claude can fix |
| **Coverage Error** | Missing test cases | Continue loop | Claude can fix |
| **Access Error** | DB connection refused, API 401 | Stop + report | Requires human |
| **Environment Error** | Missing package, wrong version | Stop + report | Requires human |

**Sources:** [README.md:579-612]()

### Blocker Report Format

When Ralph loop encounters an unfixable error:

```
🛑 LOOP BLOCKED - Human Action Required

Error: ECONNREFUSED 127.0.0.1:5432

Required Actions:
1. Start PostgreSQL: brew services start postgresql
2. Verify connection: psql -U postgres -c "SELECT 1"
3. Check DATABASE_URL in .env

After fixing, run /ralph-loop again.
```

**Sources:** [README.md:589-602]()

---

## Quality Gate Commands Reference

### Core Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/code-review` | Run code review analysis | Before push, or manually anytime |
| `npm run lint` | Lint codebase | Before commit |
| `npm run typecheck` | Type checking | Before commit |
| `npm test -- --coverage` | Full test suite with coverage | Before push, in CI |
| `./scripts/security-check.sh` | Secret scanning | Pre-commit hook |

### Stack-Specific Validation

**Node.js/TypeScript:**
```bash
# Full validation
npm run lint && npm run typecheck && npm test -- --coverage

# Changed files only (pre-commit)
npm test -- --onlyChanged --bail
```

**Python:**
```bash
# Full validation
ruff check . && mypy . && pytest --cov --cov-fail-under=80

# Changed files only (pre-commit)
pytest tests/ --exitfirst
```

**React/Next.js:**
```bash
# Full validation
npm run lint && npm run typecheck && npm test -- --coverage --watchAll=false

# Specific component
npm test -- --testPathPattern="ComponentName"
```

**Sources:** [base.md:217-253]()

---

## Security Validation Patterns

### Secret Detection Patterns

The `security-check.sh` script scans for:

| Pattern | Env Var Type | Risk | Action |
|---------|-------------|------|--------|
| `sk-proj-*` | OpenAI API key | Critical | Block commit |
| `sk-ant-*` | Claude API key | Critical | Block commit |
| `VITE_*` with secret | Client-exposed secret | Critical | Block commit |
| `NEXT_PUBLIC_*` with secret | Client-exposed secret | Critical | Block commit |
| `.env` file staged | Environment file | High | Block commit |

**Sources:** [README.md:360-364](), [base.md:418-426]()

### Client-Side Environment Variable Check

Special validation for client-exposed variables:

```bash
# Check for secrets in client env vars (dangerous!)
grep -r "VITE_.*sk-" .env*
grep -r "NEXT_PUBLIC_.*sk-" .env*
```

These patterns indicate API keys are exposed to the browser, which is a critical security violation.

**Sources:** [README.md:31](), [README.md:361]()

---

## Coverage Requirements and Enforcement

### Coverage Thresholds

```mermaid
graph TB
    A["Code Type"]
    B["Business Logic<br/>(core/*)"]
    C["API Endpoints<br/>(api/*, routes/*)"]
    D["Utilities<br/>(utils/*, lib/*)"]
    E["UI Components<br/>(components/*)"]
    F["Configuration<br/>(config/*)"]
    
    G["100% Required"]
    H["90% Required"]
    I["85% Required"]
    J["80% Required"]
    K["70% Acceptable"]
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    
    B --> G
    C --> H
    D --> I
    E --> J
    F --> K
```

**Sources:** [base.md:440-445]()

### Coverage Calculation

Coverage is calculated across four dimensions:

| Metric | Description | Weight |
|--------|-------------|--------|
| **Line Coverage** | % of lines executed | Primary |
| **Branch Coverage** | % of if/else branches taken | Secondary |
| **Function Coverage** | % of functions called | Tertiary |
| **Statement Coverage** | % of statements executed | Primary |

**CI Enforcement:**
```bash
# Check total coverage
npm test -- --coverage --coverageReporters=text-summary

# Fail if below threshold
if [[ $coverage < 80 ]]; then
  echo "Coverage ${coverage}% is below 80% threshold"
  exit 1
fi
```

**Sources:** [README.md:527-528](), [base.md:442-445]()

---

## Pre-Commit Hook Installation

### Installation Script Location

```
~/.claude/install-hooks.sh
```

This script is installed globally during Claude Bootstrap setup via `install.sh`.

### Hook Installation Process

```mermaid
graph LR
    A["Developer runs<br/>~/.claude/install-hooks.sh"]
    B["Script checks<br/>.git directory"]
    C["Creates<br/>.git/hooks/pre-commit"]
    D["Creates<br/>.git/hooks/pre-push"]
    E["Makes hooks<br/>executable"]
    F["Hooks active<br/>for repo"]
    
    A --> B
    B --> C
    B --> D
    C --> E
    D --> E
    E --> F
```

### Hook Script Contents

**pre-commit hook:**
```bash
#!/bin/bash
npm run lint || exit 1
npm run typecheck || exit 1
npm test -- --onlyChanged --bail || exit 1
./scripts/security-check.sh || exit 1
```

**pre-push hook:**
```bash
#!/bin/bash
claude --command /code-review || exit 1
```

**Sources:** [README.md:189-192]()

---

## Quality Gate Metrics and Reporting

### Metrics Tracked

Claude Bootstrap tracks quality metrics throughout development:

| Metric | Source | Threshold | Action on Violation |
|--------|--------|-----------|---------------------|
| Test coverage | Coverage report | ≥80% | Block CI |
| Files changed per commit | `git diff --stat` | ≤5 (warning at 6-10) | Advisory |
| Lines changed per commit | `git diff --stat` | ≤200 (warning at 201-400) | Advisory |
| Lines per function | Static analysis | ≤20 | Block completion |
| Lines per file | Line count | ≤200 | Block completion |
| Critical/High issues | `/code-review` | 0 | Block push |

**Sources:** [base.md:9-49](), [README.md:119-147](), [README.md:194-201]()

### Reporting Format

Quality gate results are reported in standardized format:

```markdown
## Quality Gate Results

### Pre-Commit Validation
✅ Lint: Pass
✅ Type Check: Pass
✅ Tests: 12 passed
✅ Secret Scan: No secrets detected

### Code Review Analysis
⚠️ Medium Issues: 2
- Complexity: Function `processData` has 25 lines (limit: 20)
- Duplication: Similar logic in auth.ts and session.ts

🟢 Low Issues: 1
- Style: Consider using const for immutable variables

### Coverage Report
Current: 84.2%
Threshold: 80%
Status: ✅ PASS
```

**Sources:** [README.md:203-207]()

---

## Summary

Claude Bootstrap's quality gates implement defense-in-depth validation:

1. **Pre-commit hooks** catch issues before they enter version control
2. **Commit hygiene monitoring** prevents oversized PRs with high defect correlation
3. **Pre-push code review** blocks Critical/High severity issues from reaching CI
4. **CI/CD validation** provides comprehensive automated testing and security scanning
5. **Coverage enforcement** ensures minimum 80% test coverage across the codebase

This multi-layer approach ensures that if one gate fails to catch an issue, subsequent gates provide additional protection. The system integrates seamlessly with the Ralph Loop TDD workflow to provide automatic, iterative quality validation.

**Sources:** [README.md:176-209](), [README.md:515-529](), [base.md:440-453](), Diagram 5 from context

---

# Page: Skills System

# Skills System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [install.sh](install.sh)

</details>



## Purpose and Scope

The Skills System is the modular knowledge architecture that powers Claude Bootstrap. It provides domain-specific coding patterns, tooling configurations, and development guardrails through a library of 41+ markdown files that Claude Code reads as contextual instructions. This document explains how skills are organized, stored, loaded, and applied to projects based on technology stack and project requirements.

For implementation details of specific skill categories, see:
- Core skills implementation: [Core Skills](#5.2)
- Language and framework-specific patterns: [Language and Framework Skills](#5.3)
- UI development patterns: [UI Development and Testing](#5.4)
- E2E testing configuration: [E2E Testing with Playwright](#5.5)
- AI-native development patterns: [AI and Agentic Development](#5.6)

For the integration skills (Stripe, PostHog, etc.), see [Integration Skills](#7).

---

## Skills Architecture Overview

Skills are markdown files containing structured instructions that Claude Code reads as contextual knowledge. The system implements a **two-tier storage model** with a master repository and project-specific copies, enabling centralized updates while maintaining project isolation.

### Master-Copy Distribution Model

```mermaid
graph TB
    subgraph "Global Installation"
        REPO["~/.claude-bootstrap/<br/>(Git Repository)"]
        INSTALL["install.sh"]
        MASTER["~/.claude/skills/<br/>(Master Copy)<br/>41 skill files"]
    end
    
    subgraph "Project Initialization"
        INIT["/initialize-project<br/>Command"]
        SELECT["Skill Selection Logic<br/>Based on project answers"]
        PROJECT1[".claude/skills/<br/>(Project A)<br/>Subset of skills"]
        PROJECT2[".claude/skills/<br/>(Project B)<br/>Different subset"]
    end
    
    subgraph "Update Cycle"
        PULL["git pull<br/>(Update bootstrap)"]
        REINSTALL["./install.sh<br/>(Refresh master)"]
        REINIT["/initialize-project<br/>(Refresh projects)"]
    end
    
    REPO -->|"Copies"| INSTALL
    INSTALL -->|"cp skills/*.md"| MASTER
    
    MASTER -->|"Reads & filters"| INIT
    INIT --> SELECT
    SELECT -->|"Copies relevant skills"| PROJECT1
    SELECT -->|"Copies relevant skills"| PROJECT2
    
    PULL --> REINSTALL
    REINSTALL --> MASTER
    MASTER --> REINIT
    REINIT -->|"Overwrites"| PROJECT1
    REINIT -->|"Overwrites"| PROJECT2
```

**Diagram: Skills distribution flow from repository to projects**

**Sources:** [install.sh:1-66](), [README.md:52-62](), [README.md:486-495]()

### Storage Locations and Purposes

| Location | Purpose | Persistence | Modified By |
|----------|---------|-------------|-------------|
| `~/.claude-bootstrap/skills/` | Source repository | Git-controlled | Developer (via git) |
| `~/.claude/skills/` | Master copy (all skills) | Persists across projects | `install.sh` |
| `.claude/skills/` | Project-specific skills | Project-local | `/initialize-project` |

The master copy at `~/.claude/skills/` contains all 41 skills and serves as the source of truth for skill selection. Each project receives only the skills relevant to its technology stack.

**Sources:** [install.sh:8-26](), [README.md:299-317]()

---

## Skills Selection and Loading

### Selection Logic During Initialization

Skills are conditionally loaded based on answers to the `/initialize-project` questionnaire. The selection follows a hierarchical pattern: core skills always load, then language-specific skills, then framework skills, and finally integration skills.

```mermaid
graph TB
    START["/initialize-project<br/>Interactive questionnaire"]
    
    subgraph "Always Selected"
        CORE["Core Skills (10 files)<br/>base.md, security.md,<br/>session-management.md, etc."]
    end
    
    subgraph "Conditional: Language"
        LANG_Q{"What language?"}
        PYTHON["python.md<br/>ruff, mypy, pytest"]
        TYPESCRIPT["typescript.md<br/>eslint, strict mode"]
    end
    
    subgraph "Conditional: Framework"
        FW_Q{"What framework?"}
        REACT_WEB["react-web.md<br/>Hooks, React Query"]
        REACT_NATIVE["react-native.md<br/>Platform-specific"]
        NODEJS["nodejs-backend.md<br/>Express/Fastify"]
        FASTAPI["fastapi.md<br/>Python backend"]
        NEXTJS["supabase-nextjs.md<br/>Full-stack Next.js"]
    end
    
    subgraph "Conditional: UI Type"
        UI_Q{"UI type?"}
        WEB_UI["ui-web.md<br/>WCAG 2.1 AA"]
        MOBILE_UI["ui-mobile.md<br/>44pt touch targets"]
        UI_TEST["ui-testing.md<br/>Pre-flight checklist"]
    end
    
    subgraph "Conditional: Testing"
        E2E_Q{"E2E testing?"}
        PLAYWRIGHT["playwright-testing.md<br/>Page Object Model"]
    end
    
    subgraph "Conditional: AI-First"
        AI_Q{"AI-first app?"}
        AGENTIC["agentic-development.md<br/>Pydantic AI, Claude SDK"]
        LLM["llm-patterns.md<br/>AI testing patterns"]
        MODELS["ai-models.md<br/>Model reference"]
    end
    
    subgraph "Conditional: Integrations"
        INT_Q{"Integrations?"}
        STRIPE["web-payments.md<br/>Stripe"]
        POSTHOG["posthog-analytics.md<br/>Analytics"]
        REDDIT["reddit-api.md<br/>reddit-ads.md"]
        ECOMM["medusa.md<br/>klaviyo.md<br/>woocommerce.md"]
    end
    
    START --> CORE
    START --> LANG_Q
    
    LANG_Q -->|"Python"| PYTHON
    LANG_Q -->|"TypeScript/JavaScript"| TYPESCRIPT
    
    PYTHON --> FW_Q
    TYPESCRIPT --> FW_Q
    
    FW_Q -->|"React Web"| REACT_WEB
    FW_Q -->|"React Native"| REACT_NATIVE
    FW_Q -->|"Node.js Backend"| NODEJS
    FW_Q -->|"FastAPI"| FASTAPI
    FW_Q -->|"Next.js"| NEXTJS
    
    FW_Q --> UI_Q
    UI_Q -->|"Web"| WEB_UI
    UI_Q -->|"Mobile"| MOBILE_UI
    UI_Q -->|"Yes"| UI_TEST
    
    START --> E2E_Q
    E2E_Q -->|"Yes"| PLAYWRIGHT
    
    START --> AI_Q
    AI_Q -->|"Yes"| AGENTIC
    AI_Q -->|"Yes"| LLM
    AI_Q -->|"Yes"| MODELS
    
    START --> INT_Q
    INT_Q -->|"Selected"| STRIPE
    INT_Q -->|"Selected"| POSTHOG
    INT_Q -->|"Selected"| REDDIT
    INT_Q -->|"Selected"| ECOMM
```

**Diagram: Skills selection decision tree during project initialization**

**Sources:** [README.md:396-466](), [README.md:64-69]()

### Skill File Format

Each skill is a markdown file with a consistent structure:

```markdown
# Skill Name

## Purpose
Brief description of what this skill provides

## Patterns
Code patterns and best practices

## Tooling
Required tools and configurations

## Examples
Working code examples

## Anti-patterns
What to avoid
```

Skills use declarative language (rules, constraints, patterns) rather than imperative instructions. Claude Code interprets these as contextual knowledge when generating code.

**Sources:** [README.md:299-317](), [README.md:652-663]()

---

## Skills Categories and Organization

The 41 skills are organized into 7 categories, each serving a distinct purpose in the development workflow.

### Category Overview Table

| Category | Skill Count | Selection Criteria | Purpose |
|----------|-------------|-------------------|---------|
| **Core** | 10 | Always loaded | Universal patterns, TDD, security, session management |
| **Language** | 2+ | Language selection | Language-specific tooling and patterns |
| **Framework** | 5+ | Framework selection | Framework-specific architecture and patterns |
| **UI** | 5+ | UI type selection | Platform-specific UI patterns and accessibility |
| **AI & Agentic** | 3 | AI-first flag | AI agent development patterns |
| **Database & Backend** | 5+ | Database selection | Schema management, ORM patterns |
| **Integration** | 10+ | Integration selection | Third-party service patterns |

**Sources:** [README.md:396-466]()

### Core Skills (Always Loaded)

Core skills provide foundational patterns that apply to all projects regardless of technology stack:

```mermaid
graph LR
    subgraph "Core Skills Layer"
        BASE["base.md<br/>TDD workflow<br/>Complexity limits<br/>Atomic todos"]
        ITER["iterative-development.md<br/>Ralph Wiggum loops<br/>Stop hook mechanism"]
        SEC["security.md<br/>OWASP patterns<br/>Secret scanning"]
        CRED["credentials.md<br/>Access.txt management<br/>Env var generation"]
        SESSION["session-management.md<br/>Context preservation<br/>Checkpointing"]
        REVIEW["code-review.md<br/>Pre-push validation<br/>Severity classification"]
        COMMIT["commit-hygiene.md<br/>PR size limits<br/>Atomic commits"]
        DEDUP["code-deduplication.md<br/>CODE_INDEX.md<br/>Semantic search"]
        TEAM["team-coordination.md<br/>Multi-developer state<br/>Conflict detection"]
        TOOLS["project-tooling.md<br/>CLI validation<br/>Deployment setup"]
    end
    
    BASE -.->|"Enforces"| ITER
    BASE -.->|"Requires"| SEC
    BASE -.->|"Defines"| COMMIT
    SESSION -.->|"Enables"| TEAM
    REVIEW -.->|"Uses"| SEC
    DEDUP -.->|"Prevents"| BASE
```

**Diagram: Core skills and their relationships**

**Sources:** [README.md:398-410]()

### Conditional Skills Loading Pattern

Conditional skills only load when their trigger criteria are met:

| Skill File | Trigger Question | Condition | Related Files |
|-----------|------------------|-----------|---------------|
| `python.md` | "What language?" | Answer: Python | `ruff.toml`, `pyproject.toml` |
| `typescript.md` | "What language?" | Answer: TypeScript | `tsconfig.json`, `.eslintrc.json` |
| `react-web.md` | "What framework?" | Answer: React (Web) | `package.json`, React components |
| `react-native.md` | "What framework?" | Answer: React Native | `app.json`, native modules |
| `playwright-testing.md` | "E2E testing?" | Answer: Yes | `playwright.config.ts` |
| `agentic-development.md` | "AI-first app?" | Answer: Yes | AI agent implementations |
| `web-payments.md` | "Integrations?" | Stripe selected | Stripe SDK integration |

**Sources:** [README.md:412-466]()

---

## Skills Lifecycle Management

### Installation Flow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Git as "~/.claude-bootstrap<br/>(Git Repo)"
    participant Install as "install.sh"
    participant Master as "~/.claude/skills/"
    participant Cmd as "~/.claude/commands/"
    
    Dev->>Git: git clone
    Dev->>Install: ./install.sh
    
    Install->>Master: mkdir -p ~/.claude/skills
    Install->>Cmd: mkdir -p ~/.claude/commands
    
    Install->>Master: cp skills/*.md
    Note over Install,Master: Copies all 41 skills
    
    Install->>Cmd: cp commands/*.md
    Note over Install,Cmd: /initialize-project<br/>/check-contributors<br/>/update-code-index
    
    Install-->>Dev: ✓ Installation complete<br/>Run /initialize-project
```

**Diagram: Skills installation sequence**

**Sources:** [install.sh:1-66]()

### Project Initialization Flow

When `/initialize-project` runs, it reads from the master copy and writes a filtered subset to the project:

```mermaid
sequenceDiagram
    participant Claude as "Claude Code"
    participant Init as "/initialize-project<br/>Command"
    participant Master as "~/.claude/skills/"
    participant Project as ".claude/skills/<br/>(Project)"
    participant Config as "CLAUDE.md"
    
    Claude->>Init: Execute command
    Init->>Claude: Ask questions<br/>(language, framework, etc.)
    Claude-->>Init: Answers
    
    Init->>Master: Read all skill files
    Init->>Init: Apply selection logic
    
    Note over Init: Filter based on:<br/>- Core (always)<br/>- Language match<br/>- Framework match<br/>- Integration selection
    
    Init->>Project: mkdir -p .claude/skills
    Init->>Project: Copy selected skills
    
    Note over Init,Project: Only copies relevant subset<br/>(10-20 skills typically)
    
    Init->>Config: Generate CLAUDE.md
    Note over Init,Config: Includes skills reference:<br/>".claude/skills/*.md"
    
    Init-->>Claude: ✓ Project initialized<br/>Skills loaded
```

**Diagram: Skills selection and project initialization sequence**

**Sources:** [README.md:52-62](), [README.md:64-69]()

### Update and Propagation Pattern

The overwrite-on-init pattern ensures all projects can receive skill updates:

```mermaid
stateDiagram-v2
    [*] --> MasterOutdated: Skills exist in master
    
    MasterOutdated --> GitPull: Developer runs git pull
    GitPull --> InstallRun: Developer runs ./install.sh
    InstallRun --> MasterUpdated: Master copy refreshed
    
    MasterUpdated --> ProjectOutdated: Projects still have old skills
    
    ProjectOutdated --> ReinitProject: Developer runs /initialize-project
    ReinitProject --> SelectionLogic: Selection logic executes
    SelectionLogic --> OverwriteSkills: cp selected skills to .claude/skills/
    
    OverwriteSkills --> ProjectUpdated: Project skills refreshed
    ProjectUpdated --> [*]: All projects can be updated
    
    note right of OverwriteSkills
        Existing .claude/skills/ files
        are overwritten, not merged.
        This ensures clean propagation.
    end note
```

**Diagram: Skills update propagation workflow**

**Sources:** [README.md:486-495]()

---

## Skills and Project Configuration Integration

### CLAUDE.md Skills Reference

When `/initialize-project` generates `CLAUDE.md`, it includes a reference to the skills directory:

```markdown
# Project Instructions for Claude

## Skills
Reference the following skills for coding patterns:
- .claude/skills/*.md

## Project Specifics
[Project-specific instructions]
```

Claude Code automatically loads all `.md` files referenced in `CLAUDE.md`, making skills available as contextual knowledge throughout the session.

**Sources:** [README.md:316]()

### Skills Directory Structure

```
.claude/
├── skills/                      # Project-specific skills
│   ├── base.md                 # Always present
│   ├── security.md             # Always present
│   ├── typescript.md           # If TypeScript project
│   ├── react-web.md           # If React web project
│   └── playwright-testing.md   # If E2E testing enabled
└── commands/                    # Not project-specific
    └── [managed globally]
```

The `.claude/skills/` directory is project-local and can be committed to version control, allowing team members to share the same skill configuration.

**Sources:** [README.md:299-317]()

---

## Skills Count by Category

The following table shows the complete skill distribution across all categories:

| Category | Skills | Files |
|----------|--------|-------|
| **Core Skills** | 10 | `base.md`, `iterative-development.md`, `security.md`, `credentials.md`, `session-management.md`, `code-review.md`, `commit-hygiene.md`, `code-deduplication.md`, `team-coordination.md`, `project-tooling.md` |
| **Language Skills** | 2 | `python.md`, `typescript.md` |
| **Framework Skills** | 5 | `nodejs-backend.md`, `react-web.md`, `react-native.md`, FastAPI (mentioned), Next.js (in `supabase-nextjs.md`) |
| **UI Skills** | 5 | `ui-web.md`, `ui-mobile.md`, `ui-testing.md`, `playwright-testing.md`, `user-journeys.md`, `pwa-development.md` |
| **AI & Agentic Skills** | 3 | `agentic-development.md`, `llm-patterns.md`, `ai-models.md` |
| **Database & Backend Skills** | 5 | `database-schema.md`, `supabase.md`, `supabase-nextjs.md`, `supabase-python.md`, `supabase-node.md` |
| **Content & SEO Skills** | 3 | `aeo-optimization.md`, `web-content.md`, `site-architecture.md` |
| **Integration Skills** | 10 | `web-payments.md`, `reddit-api.md`, `reddit-ads.md`, `ms-teams-apps.md`, `posthog-analytics.md`, `shopify-apps.md`, `woocommerce.md`, `medusa.md`, `klaviyo.md` |
| **Total** | 41+ | |

**Sources:** [README.md:396-466](), [install.sh:25-26]()

---

## Extending the Skills System

### Adding Custom Skills

Developers can add custom skills in two ways:

**1. Project-Local Skills** (not propagated):
- Add `.md` files to `.claude/skills/`
- Reference in `CLAUDE.md` if needed
- Persists only in this project

**2. Global Skills** (propagated to all projects):
- Add `.md` file to `~/.claude-bootstrap/skills/`
- Run `git commit` and `git push` to share
- Run `./install.sh` to copy to master
- Modify `/initialize-project` selection logic if conditional

**Sources:** [README.md:652-663]()

### Skills Validation

The `install.sh` script provides basic validation:

```bash
# Counts skills after installation
ls -1 "$CLAUDE_DIR/skills/"*.md | wc -l
```

This verifies that skills were successfully copied from the repository to the master location.

**Sources:** [install.sh:25-26]()

---

## Technical Implementation Details

### Installation Script Logic

The `install.sh` script implements the master copy creation:

```bash
# Key implementation from install.sh
CLAUDE_DIR="$HOME/.claude"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$CLAUDE_DIR/skills"
cp "$SCRIPT_DIR/skills/"*.md "$CLAUDE_DIR/skills/"
```

This copies all `.md` files from the repository's `skills/` directory to the global `~/.claude/skills/` location.

**Sources:** [install.sh:7-26]()

### Skills Persistence Model

| Operation | Effect on Master | Effect on Project |
|-----------|------------------|-------------------|
| `git pull` | No change | No change |
| `./install.sh` | Overwritten | No change |
| `/initialize-project` (new) | No change | Created |
| `/initialize-project` (existing) | No change | Overwritten |

This model ensures:
- Master copy stays synchronized with repository
- Projects can be refreshed independently
- No automatic propagation (explicit opt-in via re-init)

**Sources:** [README.md:486-495]()

---

## Skills System Benefits

### Modularity and Composability

The skills system enables precise knowledge loading:
- **Small projects**: ~10-12 skills (core + language + basic framework)
- **Full-stack projects**: ~20-25 skills (core + language + multiple frameworks + UI + testing)
- **Enterprise projects**: ~30-35 skills (all of the above + integrations + team coordination)

This prevents context bloat while ensuring relevant patterns are always available.

### Update Propagation

The master-copy architecture enables:
1. **Immediate availability**: New skills added to master are available to all new projects
2. **Opt-in updates**: Existing projects update only when re-initialized
3. **Consistent versioning**: All projects using same skill version after update

**Sources:** [README.md:486-495]()

### Team Synchronization

Since `.claude/skills/` is project-local, teams can:
- Commit skills to version control
- Share exact skill configuration
- Ensure all developers use same patterns

**Sources:** [README.md:299-317]()

---

## Summary

The Skills System provides modular, selectable coding knowledge through 41+ markdown files organized in a two-tier architecture. Skills are stored globally at `~/.claude/skills/` and copied selectively to `.claude/skills/` during project initialization based on technology stack. This architecture enables centralized updates, project-specific skill sets, and team synchronization while preventing context overload.

For detailed information about specific skill categories:
- [Core Skills](#5.2) - TDD, security, session management patterns
- [Language and Framework Skills](#5.3) - Language/framework-specific patterns
- [UI Development and Testing](#5.4) - UI patterns and accessibility
- [E2E Testing with Playwright](#5.5) - End-to-end testing configuration
- [AI and Agentic Development](#5.6) - AI agent development patterns

**Sources:** [README.md:1-713](), [install.sh:1-66]()

---

# Page: Skills Architecture

# Skills Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [commands/initialize-project.md](commands/initialize-project.md)
- [install.sh](install.sh)

</details>



This document explains the technical architecture of the skills system: how skills are stored in two locations, the selection logic that determines which skills are copied to a project, and the overwrite-on-init pattern that ensures updates propagate automatically. For information about the content of specific skills, see [Core Skills](#5.2), [Language and Framework Skills](#5.3), [UI Development and Testing](#5.4), [E2E Testing with Playwright](#5.5), and [AI and Agentic Development](#5.6).

---

## Overview

The skills system implements a two-tier architecture with a master repository and project-local copies. Skills are markdown files that provide coding guardrails, patterns, and constraints. The system automatically selects and copies relevant skills during project initialization based on language, framework, and project type.

**Key architectural principles:**

| Principle | Implementation |
|-----------|----------------|
| **Single Source of Truth** | `~/.claude/skills/` is the master repository |
| **Project Isolation** | Each project has its own `.claude/skills/` copy |
| **Overwrite on Init** | Skills are always copied fresh, never merged |
| **Conditional Loading** | Only relevant skills are copied to each project |
| **Update Propagation** | Re-running `/initialize-project` updates all skills |

Sources: [README.md:1-713](), [install.sh:1-66](), [commands/initialize-project.md:1-821]()

---

## Two-Tier Storage Architecture

The skills system maintains skills in two distinct locations with different purposes.

### Storage Hierarchy Diagram

```mermaid
graph TB
    subgraph "Global Storage ~/.claude/"
        MASTER["~/.claude/skills/<br/>Master Repository<br/>41 skill files"]
        COMMANDS["~/.claude/commands/<br/>Command definitions"]
        HOOKS["~/.claude/hooks/<br/>Git hook templates"]
    end
    
    subgraph "Installation Process"
        REPO["claude-bootstrap/<br/>Git Repository"]
        INSTALL["install.sh"]
    end
    
    subgraph "Project 1 (React Web)"
        P1_SKILLS[".claude/skills/<br/>base.md<br/>security.md<br/>typescript.md<br/>react-web.md<br/>ui-web.md"]
        P1_CLAUDE["CLAUDE.md"]
    end
    
    subgraph "Project 2 (Python CLI)"
        P2_SKILLS[".claude/skills/<br/>base.md<br/>security.md<br/>python.md"]
        P2_CLAUDE["CLAUDE.md"]
    end
    
    subgraph "Project 3 (Full Stack AI)"
        P3_SKILLS[".claude/skills/<br/>base.md<br/>security.md<br/>typescript.md<br/>nodejs-backend.md<br/>react-web.md<br/>llm-patterns.md<br/>agentic-development.md"]
        P3_CLAUDE["CLAUDE.md"]
    end
    
    REPO -->|"./install.sh"| INSTALL
    INSTALL -->|"Copy all skills"| MASTER
    INSTALL -->|"Copy commands"| COMMANDS
    INSTALL -->|"Copy templates"| HOOKS
    
    MASTER -.->|"/initialize-project<br/>Select & Copy"| P1_SKILLS
    MASTER -.->|"/initialize-project<br/>Select & Copy"| P2_SKILLS
    MASTER -.->|"/initialize-project<br/>Select & Copy"| P3_SKILLS
    
    P1_SKILLS -->|"Referenced by"| P1_CLAUDE
    P2_SKILLS -->|"Referenced by"| P2_CLAUDE
    P3_SKILLS -->|"Referenced by"| P3_CLAUDE
```

**Two-Tier Storage Locations and Purposes**

Sources: [install.sh:8-26](), [commands/initialize-project.md:146-166]()

### Global Storage: `~/.claude/`

The global storage serves as the master repository for all skills, commands, and templates.

**Directory Structure:**

```
~/.claude/
├── skills/                    # Master skill repository (41 files)
│   ├── base.md
│   ├── security.md
│   ├── python.md
│   ├── typescript.md
│   ├── react-web.md
│   ├── react-native.md
│   ├── nodejs-backend.md
│   ├── llm-patterns.md
│   ├── agentic-development.md
│   └── [38 more skills]
├── commands/                  # Command definitions
│   ├── initialize-project.md
│   ├── check-contributors.md
│   ├── code-review.md
│   └── update-code-index.md
├── hooks/                     # Git hook templates
│   └── pre-push
└── install-hooks.sh           # Hook installer script
```

**Installation Process:**

The global repository is populated by [install.sh:1-66]():
- Line 14-17: Creates directory structure
- Line 20: Copies all commands from source
- Line 25: Copies all skill files from source
- Line 29-30: Copies hook templates

**Update Mechanism:**

```bash
# Update global skills repository
cd ~/.claude-bootstrap
git pull
./install.sh
```

This overwrites all files in `~/.claude/skills/` with the latest versions.

Sources: [install.sh:1-66](), [README.md:486-495]()

### Project Storage: `.claude/skills/`

Each project receives a curated subset of skills copied from the global repository.

**Directory Structure (Example React Web Project):**

```
project-root/.claude/skills/
├── base.md                    # Universal patterns, TDD, atomic todos
├── security.md                # Security requirements, OWASP patterns
├── project-tooling.md         # CLI tools (gh, vercel, supabase)
├── session-management.md      # Context preservation
├── typescript.md              # TypeScript-specific patterns
├── react-web.md               # React web patterns
└── ui-web.md                  # Web UI, accessibility
```

**Characteristics:**

| Property | Behavior |
|----------|----------|
| **Selective** | Only skills relevant to the project are copied |
| **Overwritten** | Never merged; always replaced on `/initialize-project` |
| **Referenced** | Listed in `CLAUDE.md` for Claude to read |
| **Versioned** | Can be committed to git for project-specific history |

**Copy Trigger:**

Skills are copied from `~/.claude/skills/` to `.claude/skills/` when:
1. Running `/initialize-project` for the first time (new project)
2. Running `/initialize-project` in an existing project (update)

Sources: [commands/initialize-project.md:134-166](), [README.md:299-317]()

---

## Skill Selection Logic

The system selects which skills to copy based on project configuration. Selection happens during `/initialize-project` based on user responses or auto-detection.

### Selection Decision Tree

```mermaid
graph TB
    START["Project Initialization<br/>/initialize-project"]
    
    START --> CORE["Always Copy Core Skills:<br/>base.md<br/>security.md<br/>project-tooling.md<br/>session-management.md<br/>code-review.md<br/>commit-hygiene.md<br/>code-deduplication.md<br/>team-coordination.md<br/>credentials.md<br/>iterative-development.md"]
    
    CORE --> LANG_DETECT["Detect/Ask Language"]
    
    LANG_DETECT -->|"Python"| PY["Copy python.md"]
    LANG_DETECT -->|"TypeScript/JS"| TS["Copy typescript.md"]
    LANG_DETECT -->|"Multiple"| BOTH["Copy both"]
    
    PY --> PROJ_TYPE["Detect/Ask Project Type"]
    TS --> PROJ_TYPE
    BOTH --> PROJ_TYPE
    
    PROJ_TYPE -->|"Backend API (Python)"| FASTAPI["Copy FastAPI patterns"]
    PROJ_TYPE -->|"Backend API (Node)"| NODE_BACK["Copy nodejs-backend.md"]
    PROJ_TYPE -->|"Frontend Web"| REACT_WEB["Copy react-web.md<br/>ui-web.md"]
    PROJ_TYPE -->|"Mobile App"| REACT_NATIVE["Copy react-native.md<br/>ui-mobile.md"]
    PROJ_TYPE -->|"Full Stack"| FULLSTACK["Copy nodejs-backend.md<br/>react-web.md<br/>ui-web.md"]
    PROJ_TYPE -->|"CLI Tool"| CLI_ONLY["No framework skills"]
    
    FASTAPI --> AI_FIRST
    NODE_BACK --> AI_FIRST
    REACT_WEB --> AI_FIRST
    REACT_NATIVE --> AI_FIRST
    FULLSTACK --> AI_FIRST
    CLI_ONLY --> AI_FIRST
    
    AI_FIRST["AI-First Application?"]
    
    AI_FIRST -->|"Yes"| AI_SKILLS["Copy agentic-development.md<br/>llm-patterns.md<br/>ai-models.md"]
    AI_FIRST -->|"No"| DATABASE
    
    AI_SKILLS --> DATABASE
    
    DATABASE["Database Selection"]
    
    DATABASE -->|"Supabase + Python"| SUPA_PY["Copy supabase.md<br/>supabase-python.md"]
    DATABASE -->|"Supabase + Node"| SUPA_NODE["Copy supabase.md<br/>supabase-node.md"]
    DATABASE -->|"Supabase + Next.js"| SUPA_NEXT["Copy supabase.md<br/>supabase-nextjs.md"]
    DATABASE -->|"None"| INTEGRATIONS
    
    SUPA_PY --> INTEGRATIONS
    SUPA_NODE --> INTEGRATIONS
    SUPA_NEXT --> INTEGRATIONS
    
    INTEGRATIONS["Integration Skills<br/>User-selected"]
    
    INTEGRATIONS -.->|"If payment processing"| STRIPE["Copy web-payments.md"]
    INTEGRATIONS -.->|"If analytics"| POSTHOG["Copy posthog-analytics.md"]
    INTEGRATIONS -.->|"If e-commerce"| ECOM["Copy medusa.md<br/>klaviyo.md<br/>woocommerce.md"]
    INTEGRATIONS -.->|"If Reddit APIs"| REDDIT["Copy reddit-api.md<br/>reddit-ads.md"]
    INTEGRATIONS -.->|"If E2E testing"| PLAYWRIGHT["Copy playwright-testing.md"]
    
    STRIPE --> COMPLETE
    POSTHOG --> COMPLETE
    ECOM --> COMPLETE
    REDDIT --> COMPLETE
    PLAYWRIGHT --> COMPLETE
    INTEGRATIONS --> COMPLETE
    
    COMPLETE["Write to .claude/skills/<br/>Generate CLAUDE.md references"]
```

**Skill Selection Decision Tree**

Sources: [commands/initialize-project.md:60-166]()

### Selection Implementation

The selection logic is implemented in [commands/initialize-project.md:146-166]():

**Core Skills (Always Copied):**

```markdown
Always copy (overwrite with latest):
- base.md → .claude/skills/base.md
- security.md → .claude/skills/security.md
- project-tooling.md → .claude/skills/project-tooling.md
- session-management.md → .claude/skills/session-management.md
```

**Language-Based Selection:**

```markdown
Based on language:
- Python → copy python.md
- TypeScript/JavaScript → copy typescript.md
```

**Project Type Selection:**

```markdown
Based on project type:
- React Native → copy typescript.md AND react-native.md
- React Web → copy typescript.md AND react-web.md
- Node Backend → copy typescript.md AND nodejs-backend.md
- Full Stack (Node + React) → copy typescript.md, nodejs-backend.md, AND react-web.md
```

**Conditional Features:**

```markdown
If AI-first:
- Copy llm-patterns.md
```

Sources: [commands/initialize-project.md:146-166]()

### Auto-Detection Logic

The system attempts to auto-detect project configuration before asking questions:

| Detection Method | Code Location | What it Detects |
|------------------|---------------|-----------------|
| **package.json presence** | Line 23 | TypeScript/JavaScript project |
| **pyproject.toml presence** | Line 23 | Python project |
| **dependencies scan** | Line 76 | Framework (react, fastapi, express, etc.) |
| **anthropic/openai in deps** | Line 92 | AI-first application |
| **supabase/ directory** | Line 112 | Supabase already configured |
| **vercel.json presence** | Line 119 | Vercel deployment configured |
| **git remote -v** | Line 20 | GitHub repository connected |

Sources: [commands/initialize-project.md:9-130]()

---

## Copy and Update Mechanism

Skills are copied using an overwrite strategy, ensuring projects always receive the latest skill versions.

### Copy Flow During Initialization

```mermaid
sequenceDiagram
    participant User
    participant InitCmd as "/initialize-project"
    participant Global as "~/.claude/skills/"
    participant Project as ".claude/skills/"
    participant CLAUDE as "CLAUDE.md"
    
    User->>InitCmd: "Run /initialize-project"
    
    InitCmd->>Project: "Check if .claude/skills/ exists"
    
    alt First-time initialization
        Project-->>InitCmd: "Directory does not exist"
        InitCmd->>User: "New project detected - full setup"
    else Re-initialization
        Project-->>InitCmd: "Directory exists with X skills"
        InitCmd->>User: "Existing project - will UPDATE skills"
    end
    
    InitCmd->>User: "Ask project questions<br/>(language, framework, AI-first, etc.)"
    User-->>InitCmd: "Answers"
    
    InitCmd->>InitCmd: "Run selection logic<br/>(decision tree)"
    
    loop For each selected skill
        InitCmd->>Global: "Read skill file content"
        Global-->>InitCmd: "Skill markdown content"
        InitCmd->>Project: "Write/overwrite .claude/skills/[name].md"
        Note over Project: Existing files are overwritten<br/>No merging occurs
    end
    
    InitCmd->>CLAUDE: "Update CLAUDE.md with skill references"
    
    InitCmd->>User: "Summary: X skills copied/updated"
```

**Copy Flow During Project Initialization**

Sources: [commands/initialize-project.md:132-166]()

### Overwrite-on-Init Pattern

The system uses a strict overwrite strategy with no merging:

**Behavior:**

| Scenario | Action | Rationale |
|----------|--------|-----------|
| **Skill exists in project** | Overwrite completely | Ensures latest patterns propagate |
| **Skill removed from global** | Remains in project | Preserves backward compatibility |
| **New skill added to global** | Not copied until re-init | Explicit opt-in for new patterns |
| **User edits project skill** | Edits lost on re-init | Skills are source code, not config |

**Implementation:**

From [commands/initialize-project.md:146-166]():

```
Step 2: Update skill files from ~/.claude/skills/

Always copy (overwrite with latest):
- base.md → .claude/skills/base.md
- security.md → .claude/skills/security.md
...

Note: Skills are always overwritten with the latest version from ~/.claude/skills/.
This ensures updates propagate when user updates their global skills.
```

**Implications for Users:**

- ✅ Run `/initialize-project` anytime to get latest skill updates
- ✅ Can commit `.claude/skills/` to git for project history
- ❌ Don't edit skills in `.claude/skills/` (edits will be lost)
- ✅ Add project-specific patterns to `CLAUDE.md` instead

Sources: [commands/initialize-project.md:146-166](), [commands/initialize-project.md:320-325]()

---

## Skill Categories and Organization

The 41 skills are organized into 7 functional categories, each serving a distinct purpose in the development workflow.

### Category Overview

```mermaid
graph TB
    subgraph "Core Skills - Always Loaded"
        CORE1["base.md<br/>Universal patterns, TDD, simplicity rules"]
        CORE2["security.md<br/>OWASP, secrets management"]
        CORE3["iterative-development.md<br/>Ralph loop, TDD cycles"]
        CORE4["session-management.md<br/>Context preservation"]
        CORE5["code-review.md<br/>Mandatory review process"]
        CORE6["commit-hygiene.md<br/>Atomic commits, PR size"]
        CORE7["code-deduplication.md<br/>Prevent semantic bloat"]
        CORE8["team-coordination.md<br/>Multi-person projects"]
        CORE9["credentials.md<br/>Access.txt management"]
        CORE10["project-tooling.md<br/>CLI validation"]
    end
    
    subgraph "Language Skills - Conditional"
        LANG1["python.md<br/>ruff, mypy, pytest"]
        LANG2["typescript.md<br/>strict mode, eslint"]
    end
    
    subgraph "Framework Skills - Conditional"
        FW1["react-web.md<br/>Hooks, React Query"]
        FW2["react-native.md<br/>Platform-specific code"]
        FW3["nodejs-backend.md<br/>Express/Fastify patterns"]
        FW4["FastAPI patterns"]
    end
    
    subgraph "UI Skills - Conditional"
        UI1["ui-web.md<br/>WCAG 2.1 AA, glassmorphism"]
        UI2["ui-mobile.md<br/>44pt touch targets"]
        UI3["ui-testing.md<br/>Visual regression"]
        UI4["playwright-testing.md<br/>E2E cross-browser"]
        UI5["user-journeys.md<br/>UX flows"]
        UI6["pwa-development.md<br/>Service workers, offline"]
    end
    
    subgraph "AI Skills - Conditional"
        AI1["agentic-development.md<br/>Pydantic AI, Claude SDK"]
        AI2["llm-patterns.md<br/>AI-first testing"]
        AI3["ai-models.md<br/>Model reference guide"]
    end
    
    subgraph "Database Skills - Conditional"
        DB1["database-schema.md<br/>Schema awareness"]
        DB2["supabase.md<br/>CLI, migrations, RLS"]
        DB3["supabase-nextjs.md<br/>Next.js + Drizzle"]
        DB4["supabase-python.md<br/>FastAPI + SQLAlchemy"]
        DB5["supabase-node.md<br/>Express/Hono + Drizzle"]
    end
    
    subgraph "Integration Skills - Conditional"
        INT1["web-payments.md<br/>Stripe integration"]
        INT2["posthog-analytics.md<br/>Product analytics"]
        INT3["reddit-api.md<br/>PRAW/Snoowrap"]
        INT4["reddit-ads.md<br/>Ads API + optimizer"]
        INT5["shopify-apps.md<br/>Remix, Admin API"]
        INT6["woocommerce.md<br/>REST API"]
        INT7["medusa.md<br/>Headless commerce"]
        INT8["klaviyo.md<br/>Email/SMS marketing"]
        INT9["ms-teams-apps.md<br/>Bots, AI agents"]
    end
    
    subgraph "Content/SEO Skills - Conditional"
        SEO1["aeo-optimization.md<br/>AI Engine Optimization"]
        SEO2["web-content.md<br/>SEO + AI discovery"]
        SEO3["site-architecture.md<br/>Technical SEO"]
    end
```

**Seven Skill Categories and Their Members**

Sources: [README.md:396-466]()

### Category Loading Rules

| Category | When Loaded | Example Trigger |
|----------|-------------|-----------------|
| **Core Skills (10)** | Always | Every project |
| **Language Skills (2)** | Based on language | `pyproject.toml` detected → `python.md` |
| **Framework Skills (4+)** | Based on framework | `"react"` in dependencies → `react-web.md` |
| **UI Skills (6)** | Based on project type | "Frontend Web" selected → `ui-web.md` |
| **AI Skills (3)** | Based on AI-first flag | "AI-first: Yes" → `agentic-development.md` |
| **Database Skills (5)** | Based on database | "Supabase" selected → `supabase.md` |
| **Integration Skills (9)** | User-selected | "PostHog" selected → `posthog-analytics.md` |
| **Content/SEO Skills (3)** | User-selected | Content site project → `web-content.md` |

Sources: [README.md:396-466](), [commands/initialize-project.md:146-166]()

---

## Update Propagation

The system provides a straightforward mechanism for propagating skill updates from the global repository to all projects.

### Update Flow

```mermaid
graph LR
    subgraph "Update Cycle"
        UPSTREAM["claude-bootstrap<br/>Git Repository<br/>(GitHub)"]
        LOCAL["~/.claude-bootstrap/<br/>Local Clone"]
        GLOBAL["~/.claude/skills/<br/>Global Repository"]
        P1[".claude/skills/<br/>Project 1"]
        P2[".claude/skills/<br/>Project 2"]
        P3[".claude/skills/<br/>Project 3"]
    end
    
    UPSTREAM -->|"1. git pull"| LOCAL
    LOCAL -->|"2. ./install.sh"| GLOBAL
    GLOBAL -->|"3. /initialize-project"| P1
    GLOBAL -->|"3. /initialize-project"| P2
    GLOBAL -->|"3. /initialize-project"| P3
    
    note1["User Actions:<br/>cd ~/.claude-bootstrap<br/>git pull<br/>./install.sh"]
    note2["Per-Project Actions:<br/>cd project<br/>claude<br/>/initialize-project"]
    
    LOCAL -.-> note1
    GLOBAL -.-> note2
```

**Update Propagation Flow from Upstream to Projects**

Sources: [README.md:486-495](), [commands/initialize-project.md:802-821]()

### Update Commands

**Step 1: Update Global Repository**

```bash
# Navigate to local clone
cd ~/.claude-bootstrap

# Pull latest from GitHub
git pull

# Reinstall to ~/.claude/
./install.sh
```

This updates `~/.claude/skills/` with the latest versions from the repository.

**Step 2: Update Individual Projects**

```bash
# Navigate to any project
cd ~/projects/my-app

# Open Claude Code
claude

# Run initialization command
/initialize-project
```

This copies the latest skills from `~/.claude/skills/` to `.claude/skills/`, overwriting existing files.

Sources: [README.md:486-495](), [commands/initialize-project.md:802-821]()

### Preservation During Updates

When running `/initialize-project` on an existing project, certain elements are preserved:

| Element | Update Behavior | Rationale |
|---------|----------------|-----------|
| **Skills in `.claude/skills/`** | Overwritten completely | Skills are source code, not configuration |
| **CLAUDE.md** | Skill list updated, custom sections preserved | Allows project-specific documentation |
| **`_project_specs/` contents** | Fully preserved | Todos, features, and sessions are user data |
| **Source code** | Never touched | Initialization only affects Claude configuration |
| **Git configuration** | Preserved | Repository connection maintained |
| **`.env` files** | Preserved | Credentials never overwritten |

From [commands/initialize-project.md:320-325]():

```markdown
If CLAUDE.md exists:
- Preserve Project Overview, Tech Stack, and Project-Specific Patterns sections
- Update Skills list to reference current .claude/skills/ contents
- Update Key Commands section with latest
```

Sources: [commands/initialize-project.md:320-438](), [commands/initialize-project.md:732-750]()

---

## CLAUDE.md Integration

The `CLAUDE.md` file serves as the entry point that references skills, providing Claude with the instruction to read them before coding.

### CLAUDE.md Structure

From [commands/initialize-project.md:327-438]():

```markdown
# CLAUDE.md

## Skills
Read and follow these skills before writing any code:
- .claude/skills/base.md
- .claude/skills/security.md
- .claude/skills/project-tooling.md
- .claude/skills/session-management.md
- .claude/skills/[language].md
- .claude/skills/[framework].md (if applicable)
- .claude/skills/llm-patterns.md (if AI-first)

## Project Overview
[Description]

## Tech Stack
[Stack details]

## Project-Specific Patterns
[Custom patterns]
```

**Skill Loading Mechanism:**

1. Claude reads `CLAUDE.md` as the project instruction file
2. `CLAUDE.md` lists all skills in `.claude/skills/` to read
3. Claude loads and internalizes each skill before coding
4. Skills provide guardrails that Claude follows during development

Sources: [commands/initialize-project.md:320-438](), [README.md:299-317]()

### Reference Generation

During initialization, the skill reference list in `CLAUDE.md` is automatically generated based on which skills were copied to `.claude/skills/`:

```markdown
## Skills
Read and follow these skills before writing any code:
```

For each file in `.claude/skills/`:
```markdown
- .claude/skills/[filename].md
```

This ensures the reference list always matches the actual skills present in the project.

Sources: [commands/initialize-project.md:327-339]()

---

## File System Layout

### Complete Directory Structure

```
~/.claude-bootstrap/          # Git clone of repository
├── install.sh                # Global installer
├── commands/
│   ├── initialize-project.md
│   ├── check-contributors.md
│   ├── code-review.md
│   └── update-code-index.md
├── skills/                   # Master skill files (41 files)
│   ├── base.md
│   ├── security.md
│   ├── [39 more skills]
└── hooks/
    └── pre-push

~/.claude/                    # Global installation
├── skills/                   # Copy of all skills
│   └── [41 .md files]
├── commands/                 # Copy of all commands
│   └── [4 .md files]
├── hooks/                    # Git hook templates
│   └── pre-push
└── install-hooks.sh          # Per-project hook installer

project-root/                 # Individual project
├── .claude/
│   └── skills/               # Subset of skills (4-15 files typically)
│       ├── base.md
│       ├── security.md
│       ├── [language].md
│       ├── [framework].md
│       └── [integration].md
├── CLAUDE.md                 # References .claude/skills/
└── _project_specs/           # Project specs (preserved during updates)
    ├── overview.md
    ├── features/
    ├── todos/
    └── session/
```

Sources: [install.sh:1-66](), [commands/initialize-project.md:134-143](), [README.md:296-317]()

---

## Summary

The skills architecture implements a three-layer system:

1. **Source Layer:** Git repository (`claude-bootstrap/`) contains authoritative skill files
2. **Global Layer:** User installation (`~/.claude/skills/`) provides master copy for all projects
3. **Project Layer:** Individual projects (`.claude/skills/`) receive curated subsets

The overwrite-on-init pattern ensures that running `/initialize-project` always updates projects with the latest skill versions from the global repository, while preserving project-specific configuration and user data. Skill selection is conditional based on project type, enabling the system to adapt from simple CLI tools to complex full-stack AI applications by loading only relevant skills.

Sources: [README.md:1-713](), [install.sh:1-66](), [commands/initialize-project.md:1-821]()

---

# Page: Core Skills

# Core Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



This document describes the 10 core skills that are loaded for every project initialized with Claude Bootstrap, regardless of language, framework, or project type. These skills establish the fundamental development patterns, quality gates, and workflows that all projects must follow.

For information about language-specific skills (Python, TypeScript) and framework skills (React, FastAPI, etc.), see [Language and Framework Skills](#5.3). For skills related to building AI agents and agentic systems, see [AI and Agentic Development](#5.6).

---

## Overview

Core skills are mandatory skills that define the baseline behavior and constraints for all Claude Bootstrap projects. They are stored in `~/.claude/skills/` after installation and copied to `.claude/skills/` during project initialization.

### Core Skills vs. Conditional Skills

| Skill Type | Load Condition | Example Skills |
|------------|---------------|----------------|
| **Core Skills** | Always loaded | `base.md`, `security.md`, `session-management.md` |
| **Conditional Skills** | Based on project type | `python.md`, `react-web.md`, `playwright-testing.md` |

Core skills establish:
- **TDD workflow enforcement** - RED-GREEN-VALIDATE cycle
- **Complexity constraints** - 20 lines/function, 200 lines/file, 3 params max
- **Security requirements** - No secrets in code, client-side env var checks
- **Quality gates** - 80% coverage minimum, mandatory code review
- **Session management** - Context preservation and resumability
- **Team coordination** - Multi-developer workflow patterns

**Sources:** [README.md:396-410](), [skills/base.md:1-579]()

---

## Core Skills Architecture

**Diagram: Core Skills Loading and Interaction**

```mermaid
graph TB
    subgraph Installation["~/.claude/skills/ (Master Repository)"]
        BASE["base.md<br/>Universal Patterns"]
        ITER["iterative-development.md<br/>Ralph Loop"]
        SECURITY["security.md<br/>OWASP Patterns"]
        CREDS["credentials.md<br/>API Key Mgmt"]
        SESSION["session-management.md<br/>Context Preservation"]
        REVIEW["code-review.md<br/>Mandatory Review"]
        HYGIENE["commit-hygiene.md<br/>PR Size Limits"]
        DEDUP["code-deduplication.md<br/>Semantic Index"]
        TEAM["team-coordination.md<br/>Multi-Dev State"]
        TOOLING["project-tooling.md<br/>CLI Setup"]
    end
    
    subgraph Project[".claude/skills/ (Project Copy)"]
        P_BASE["base.md"]
        P_ITER["iterative-development.md"]
        P_SECURITY["security.md"]
        P_CREDS["credentials.md"]
        P_SESSION["session-management.md"]
        P_REVIEW["code-review.md"]
        P_HYGIENE["commit-hygiene.md"]
        P_DEDUP["code-deduplication.md"]
        P_TEAM["team-coordination.md"]
        P_TOOLING["project-tooling.md"]
    end
    
    subgraph Enforcement["Enforcement Points"]
        RALPH["/ralph-loop<br/>Iterative Execution"]
        HOOKS["Pre-commit/Pre-push Hooks<br/>scripts/security-check.sh"]
        CI["GitHub Actions<br/>quality.yml + security.yml"]
        SPECS["_project_specs/<br/>Session State + Todos"]
    end
    
    BASE --> P_BASE
    ITER --> P_ITER
    SECURITY --> P_SECURITY
    CREDS --> P_CREDS
    SESSION --> P_SESSION
    REVIEW --> P_REVIEW
    HYGIENE --> P_HYGIENE
    DEDUP --> P_DEDUP
    TEAM --> P_TEAM
    TOOLING --> P_TOOLING
    
    P_BASE --> RALPH
    P_ITER --> RALPH
    P_SECURITY --> HOOKS
    P_SECURITY --> CI
    P_SESSION --> SPECS
    P_REVIEW --> HOOKS
    P_HYGIENE --> SPECS
    P_DEDUP --> SPECS
    P_TEAM --> SPECS
```

**Sources:** [README.md:52-70](), [README.md:296-317]()

---

## The 10 Core Skills

### base.md - Universal Patterns and TDD

`base.md` is the foundational skill that establishes the core development philosophy, complexity constraints, and mandatory TDD workflow.

**Key Enforcement Rules:**

| Constraint | Limit | Enforcement Point |
|------------|-------|-------------------|
| Lines per function | 20 max | Pre-completion check |
| Parameters per function | 3 max | Pre-completion check |
| Nesting depth | 2 levels max | Pre-completion check |
| Lines per file | 200 max | Pre-completion check, auto-split |
| Functions per file | 10 max | Pre-completion check |
| Test coverage | 80% minimum | CI/CD validation |

**TDD Workflow Phases:**

```mermaid
stateDiagram-v2
    [*] --> RED: "Write tests first"
    RED --> VerifyFail: "Run tests"
    VerifyFail --> RED: "Tests pass → Invalid test"
    VerifyFail --> GREEN: "Tests fail ✓"
    GREEN --> VerifyPass: "Implement feature"
    VerifyPass --> GREEN: "Tests fail → Fix code"
    VerifyPass --> VALIDATE: "Tests pass ✓"
    VALIDATE --> CheckLint: "Run linter"
    CheckLint --> CheckType: "Auto-fix if possible"
    CheckType --> CheckCoverage: "Run type checker"
    CheckCoverage --> AddTests: "Coverage < 80%"
    CheckCoverage --> Complete: "Coverage ≥ 80% ✓"
    AddTests --> VerifyPass
    Complete --> [*]: "Mark todo done"
```

**Atomic Todo Format:**

Every work item follows the structure defined at [skills/base.md:143-179](). The todo includes:
- Status, priority, estimate
- Acceptance criteria (specific, testable)
- Test cases table
- TDD execution log tracking RED → GREEN → VALIDATE phases

**Anti-Patterns Blocked:**

```
❌ Fixing bugs without adding test first
❌ Writing tests after implementation
❌ Marking todos complete with failing tests
❌ Skipping lint/typecheck before completion
❌ Global state
❌ Deep nesting (>2 levels)
❌ Large PRs (>400 lines)
```

**File Structure Conventions:**

The skill mandates separation of code documentation from project specifications at [skills/base.md:99-136]():
- `docs/` - Technical documentation (architecture, API, setup)
- `_project_specs/` - Business requirements (features, todos, sessions)
- `_project_specs/session/` - Session state for resumability
- `CLAUDE.md` - Claude-specific instructions

**Sources:** [skills/base.md:1-579](), [README.md:320-357]()

---

### iterative-development.md - Ralph Wiggum Loop

`iterative-development.md` enables automatic iterative TDD cycles through the Ralph Wiggum loop mechanism. The skill transforms natural language requests into self-correcting implementation loops.

**Auto-Invocation Logic:**

| User Request Type | Action |
|-------------------|--------|
| "Add email validation" | Auto-invoke `/ralph-loop` with TDD template |
| "Fix the login bug" | Auto-invoke `/ralph-loop` with bug fix template |
| "Build REST API for todos" | Auto-invoke `/ralph-loop` with API template |
| "Just explain..." | Skip loop, provide explanation |
| "Quick fix..." | Skip loop, one-liner change |

**Automatic Transformation Example:**

When user says: `"Add forgot password feature"`

Claude automatically structures as:
```markdown
## Task: Add forgot password feature

### Requirements (extracted from user request)
- User can request password reset via email
- Reset link sent to registered email
- Link expires after 24 hours
- User can set new password via link

### TDD Workflow
1. Write failing tests for each requirement
2. Verify tests FAIL (RED)
3. Implement feature
4. Verify tests PASS (GREEN)
5. Run lint + typecheck
6. Repeat if failures

### Completion Criteria
- [ ] All tests passing
- [ ] Coverage >= 80%
- [ ] Lint clean
- [ ] Security review (no token in URL params)

<promise>FORGOT PASSWORD COMPLETE</promise>
```

And invokes: `/ralph-loop [prompt] --completion-promise "FORGOT PASSWORD COMPLETE" --max-iterations 25`

**Error Classification:**

The skill defines error types that determine loop continuation vs. exit:

| Error Type | Examples | Claude Fixes? | Action |
|------------|----------|---------------|--------|
| **Code Error** | Logic bug, wrong assertion | ✅ Yes | Continue loop |
| **Type Error** | Type mismatch, missing property | ✅ Yes | Continue loop |
| **Access Error** | Missing API key, DB refused | ❌ No | Stop + blocker report |
| **Environment Error** | Missing package, wrong version | ❌ No | Stop + blocker report |

**Sources:** [skills/base.md:499-578](), [README.md:71-118](), [README.md:579-612]()

---

### security.md - Security Patterns and Enforcement

`security.md` establishes mandatory security requirements and provides patterns for common vulnerabilities. It integrates with pre-commit hooks, code review, and CI/CD validation.

**Essential Security Checks:**

```markdown
1. No secrets in code - Use environment variables
2. .env in .gitignore - Always, no exceptions
3. No secrets in client-exposed env vars - Never VITE_*, NEXT_PUBLIC_*
4. Validate all input - Use Zod/Pydantic at API boundaries
5. Parameterized queries only - No string concatenation for SQL
6. Hash passwords properly - bcrypt with 12+ rounds
7. Dependency scanning - npm audit / safety check must pass
```

**Required Security Files:**

| File | Purpose | Location |
|------|---------|----------|
| `.gitignore` | Block secrets patterns | Project root |
| `.env.example` | Document required vars (no values) | Project root |
| `scripts/security-check.sh` | Pre-commit validation | Project `scripts/` |
| `.github/workflows/security.yml` | CI secret scanning | GitHub Actions |

**Client-Side Environment Variable Check:**

The skill enforces that secrets never appear in client-exposed environment variables:
- `VITE_*` prefix - Vite bundles into client JavaScript
- `NEXT_PUBLIC_*` prefix - Next.js exposes to browser
- Any secret in these variables = blocker

**Sources:** [skills/base.md:413-437](), [README.md:358-365]()

---

### credentials.md - Centralized API Key Management

`credentials.md` implements the centralized credentials workflow using a single `Access.txt` file to store all API keys, with automatic detection, validation, and `.env` generation.

**Workflow Steps:**

```mermaid
graph LR
    ASK["Ask for Access.txt location<br/>(e.g., ~/Documents/Access.txt)"]
    READ["Read and parse file<br/>Pattern matching"]
    VALIDATE["Validate keys are working<br/>Test API calls"]
    CREATE["Create project .env<br/>with found keys"]
    REPORT["Report missing keys<br/>+ where to get them"]
    
    ASK --> READ --> VALIDATE --> CREATE --> REPORT
```

**Key Pattern Detection:**

| Service | Pattern | Env Variable | Validation Command |
|---------|---------|--------------|-------------------|
| OpenAI | `sk-proj-*` | `OPENAI_API_KEY` | `curl` with bearer token |
| Claude | `sk-ant-*` | `ANTHROPIC_API_KEY` | `curl` with x-api-key header |
| Render | `rnd_*` | `RENDER_API_KEY` | `curl /v1/owners` |
| Replicate | `r8_*` | `REPLICATE_API_TOKEN` | `curl` with token header |
| Stripe | `sk_test_*`, `sk_live_*` | `STRIPE_SECRET_KEY` | Stripe CLI verify |
| Supabase | URL + key format | `SUPABASE_URL`, `SUPABASE_ANON_KEY` | `curl /rest/v1/` |

**Access.txt Format Example:**

```
OpenAI API: sk-proj-xxx
Claude API: sk-ant-xxx
Stripe: sk_test_xxx
Supabase url: https://xxx.supabase.co
Anon key: eyJxxx
```

**Sources:** [skills/base.md:388-410](), [README.md:366-379]()

---

### session-management.md - Context Preservation

`session-management.md` enables resumability by maintaining session state across Claude conversations. It defines when and how to checkpoint work to prevent context loss.

**Checkpoint Triggers:**

```mermaid
graph TD
    EVENT[Session Event]
    
    EVENT --> Q1{Decision made?}
    Q1 -->|Yes| LOG_DEC["Log to decisions.md"]
    
    EVENT --> Q2{>10 tool calls?}
    Q2 -->|Yes| CHECKPOINT["Full checkpoint to current-state.md"]
    
    EVENT --> Q3{Major feature done?}
    Q3 -->|Yes| ARCHIVE["Archive to session/archive/"]
    
    EVENT --> Q4{Otherwise}
    Q4 -->|Yes| UPDATE["Quick update to current-state.md"]
    
    LOG_DEC --> CONTINUE
    CHECKPOINT --> CONTINUE
    ARCHIVE --> CONTINUE
    UPDATE --> CONTINUE
    
    CONTINUE[Continue Work]
```

**Session Files Structure:**

```
_project_specs/session/
├── current-state.md       # Live session state, next steps
├── decisions.md           # Key architectural decisions log
├── code-landmarks.md      # Important code locations/patterns
└── archive/               # Past session summaries
    ├── 2024-01-15-auth.md
    └── 2024-01-16-api.md
```

**Session Start Protocol:**
1. Read `_project_specs/session/current-state.md`
2. Check `_project_specs/todos/active.md`
3. Continue from documented "Next Steps"

**Session End Protocol:**
1. Archive current session to `session/archive/YYYY-MM-DD-topic.md`
2. Update `current-state.md` with handoff notes
3. Ensure next steps are specific and actionable

**Sources:** [skills/base.md:456-478](), [README.md:308-312]()

---

### code-review.md - Mandatory Code Review

`code-review.md` enforces mandatory code review before every push through the `/code-review` command and pre-push hooks. Reviews analyze security, performance, architecture, and code quality.

**Severity Levels and Actions:**

| Level | Icon | Action | Push Allowed? | Example Issues |
|-------|------|--------|---------------|----------------|
| Critical | 🔴 | Must fix now | ❌ BLOCKED | SQL injection, exposed secrets |
| High | 🟠 | Must fix now | ❌ BLOCKED | XSS vulnerability, N+1 queries |
| Medium | 🟡 | Fix soon | ✅ Advisory | Missing error handling, complexity |
| Low | 🟢 | Nice to have | ✅ Advisory | Minor optimization, style |

**Review Categories:**

```
Security: SQL injection, XSS, secrets in code, weak auth
Performance: N+1 queries, memory leaks, inefficient algorithms
Architecture: SOLID violations, coupling, circular dependencies
Code Quality: Complexity violations, duplication, missing types
```

**Enforcement Points:**

1. **Manual:** Developer runs `/code-review` before commit
2. **Pre-push hook:** `~/.claude/install-hooks.sh` enables automatic blocking
3. **GitHub Actions:** CI runs review on all PRs
4. **Pre-merge:** Blocks merge if Critical/High issues found

**Sources:** [README.md:176-210](), [README.md:34-39]()

---

### commit-hygiene.md - Atomic Commits and PR Size Management

`commit-hygiene.md` monitors commit size and advises when PRs become too large, based on research showing defect rates correlate with PR size.

**Commit Size Thresholds:**

| Status | Files | Lines | Action | Defect Rate |
|--------|-------|-------|--------|-------------|
| 🟢 OK | ≤ 5 | ≤ 200 | Continue working | ~15% |
| 🟡 WARN | 6-10 | 201-400 | Consider committing | ~23% |
| 🔴 STOP | > 10 | > 400 | Commit NOW | 40%+ |

**Automatic Monitoring:**

Claude automatically checks git status after completing tasks and advises:

| Changes | Claude Says |
|---------|-------------|
| 3 files, 95 lines | ✅ Tests passing. Good time to commit! |
| 7 files, 225 lines | 💡 Approaching threshold. Consider committing. |
| 12 files, 400 lines | ⚠️ Changes too large! Commit now before continuing. |

**Atomic Commit Principle:**

```
If you need "and" to describe your commit, split it.

❌ "Add auth and fix navigation bug"
✅ "Add user authentication"
✅ "Fix navigation bug on mobile"
```

**Sources:** [README.md:119-147]()

---

### code-deduplication.md - Semantic Capability Index

`code-deduplication.md` prevents semantic duplication by maintaining a capability index (`CODE_INDEX.md`) organized by what functions DO, not their names. AI tends to reimplement rather than reuse, creating duplicate purpose.

**Check-Before-Write Protocol:**

```
Before creating ANY new function:
1. Check CODE_INDEX.md for existing capabilities
2. Search codebase for similar functionality
3. Extend existing if possible
4. Only create new if nothing suitable exists
```

**CODE_INDEX.md Structure:**

```markdown
## Validation
| Function | Location | Does What |
|----------|----------|-----------|
| isEmail() | utils/validate.ts | Validates email format |
| isPhone() | utils/validate.ts | Validates phone number |

## Date/Time
| Function | Location | Does What |
|----------|----------|-----------|
| formatRelative() | utils/dates.ts | "2 days ago" format |
| parseDate() | utils/dates.ts | Parse ISO string to Date |
```

**Commands:**

```bash
/update-code-index      # Regenerate index from codebase
/audit-duplicates       # Find semantic duplicates to merge
```

**Example Prevention:**

Developer wants to add email validation. Before writing `validateEmail()`:
1. Check `CODE_INDEX.md` → finds `isEmail()` exists in `utils/validate.ts`
2. Use existing function instead of creating duplicate
3. If existing doesn't meet needs, extend it rather than create new

**Optional Integration:**

For codebases >100 files, the skill supports vector DB integration (ChromaDB/LanceDB) for semantic search beyond simple grep.

**Sources:** [README.md:255-294]()

---

### team-coordination.md - Multi-Developer State Management

`team-coordination.md` enables multiple developers to use Claude Code on the same repository simultaneously without conflicts through file-based state management.

**Team Coordination Flow:**

```mermaid
sequenceDiagram
    participant DevA as "Developer A"
    participant State as "_project_specs/team/state.md"
    participant DevB as "Developer B"
    
    DevA->>State: git pull + /check-contributors
    State-->>DevA: Show: Solo project, no active sessions
    DevA->>State: Claim TODO-042 (email validation)
    DevA->>State: Update active session (working on auth.ts)
    
    DevB->>State: git pull + /check-contributors
    State-->>DevB: Show: DevA active on TODO-042, working auth.ts
    DevB->>State: Claim TODO-045 (different area)
    DevB->>State: Update active session (working on api.ts)
    
    Note over State: Conflict detection: auth.ts vs api.ts = OK
    
    DevA->>State: Complete TODO-042, clear session
    DevB->>State: Complete TODO-045, clear session
```

**Team State Structure:**

```
_project_specs/team/
├── state.md              # Active sessions, claimed todos, conflicts
├── contributors.md       # Team members, ownership, focus areas
├── handoffs/             # Context transfer when passing work
│   └── 2024-01-15-auth-handoff.md
└── decisions.md          # Shared architectural decisions
```

**state.md Format:**

```markdown
## Active Sessions
| Developer | Todo | Files Touched | Status | Last Updated |
|-----------|------|---------------|--------|--------------|
| Alice | TODO-042 | src/auth.ts, src/auth.test.ts | Active | 2024-01-15 10:30 |
| Bob | TODO-045 | src/api.ts | Active | 2024-01-15 10:45 |

## Claimed Todos (Not Yet Started)
| Developer | Todo | Claimed At |
|-----------|------|------------|
| Charlie | TODO-050 | 2024-01-15 09:00 |

## Conflict Warnings
⚠️ Alice and Bob may conflict on src/types.ts
```

**Workflow Commands:**

```bash
/check-contributors          # Check state, offer conversion
/check-contributors --status # Quick status only
/check-contributors --team   # Convert solo → team project
```

**Conflict Detection:**

The system monitors `state.md` for file overlap and warns when multiple developers touch the same files, enabling coordination before merge conflicts occur.

**Sources:** [README.md:211-254]()

---

### project-tooling.md - CLI Configuration

`project-tooling.md` handles validation and configuration of external CLIs used for project scaffolding and deployment: `gh` (GitHub), `vercel` (Vercel), `supabase` (Supabase), and `render` (Render).

**Required CLIs:**

| CLI | Purpose | Install Command | Auth Command |
|-----|---------|----------------|--------------|
| `gh` | GitHub repo management | `brew install gh` | `gh auth login` |
| `vercel` | Vercel deployment | `npm i -g vercel` | `vercel login` |
| `supabase` | Supabase DB/Edge Functions | `brew install supabase/tap/supabase` | `supabase login` |
| `render` | Render deployment | `brew install renderinc/tap/render` | `render login` |

**Validation During Initialization:**

```mermaid
graph LR
    INIT["/initialize-project"]
    CHECK["Check CLI availability<br/>gh --version, vercel --version"]
    AUTH["Check authentication<br/>gh auth status, vercel whoami"]
    PROMPT["Prompt for login<br/>if not authenticated"]
    SETUP["Configure project<br/>repos, deployments"]
    
    INIT --> CHECK
    CHECK --> AUTH
    AUTH --> PROMPT
    PROMPT --> SETUP
```

**Setup Actions:**

1. **GitHub:** Create repo, add secrets, configure branch protection
2. **Vercel:** Link project, set env vars, configure domains
3. **Supabase:** Link project, create local config, setup migrations
4. **Render:** Create service, set env vars, configure build

**Sources:** [README.md:497-514]()

---

## Skills Loading Mechanism

**Diagram: Skills Copy Process During Initialization**

```mermaid
graph TB
    INSTALL["install.sh<br/>Copies skills to ~/.claude/"]
    HOME["~/.claude/skills/<br/>Master Repository"]
    INIT["/initialize-project<br/>In project directory"]
    SELECT["Select Skills Based On:<br/>- Language (always)<br/>- Framework (always)<br/>- Integrations (conditional)<br/>- AI-first flag (conditional)"]
    COPY["Copy Selected Skills<br/>to .claude/skills/"]
    CLAUDEMD["Generate CLAUDE.md<br/>references loaded skills"]
    
    INSTALL --> HOME
    INIT --> SELECT
    SELECT --> HOME
    HOME --> COPY
    COPY --> CLAUDEMD
    
    subgraph AlwaysLoaded["Always Loaded (10 Core Skills)"]
        C1["base.md"]
        C2["iterative-development.md"]
        C3["security.md"]
        C4["credentials.md"]
        C5["session-management.md"]
        C6["code-review.md"]
        C7["commit-hygiene.md"]
        C8["code-deduplication.md"]
        C9["team-coordination.md"]
        C10["project-tooling.md"]
    end
    
    HOME --> AlwaysLoaded
    AlwaysLoaded --> COPY
```

**Re-Initialization Behavior:**

Running `/initialize-project` in an existing project:
- **Overwrites** all skills in `.claude/skills/` with latest from `~/.claude/skills/`
- **Preserves** existing project configuration (`.env`, `package.json`, etc.)
- **Updates** `CLAUDE.md` to reference current skill set
- **Adds** new skills if project answers changed (e.g., adding Playwright)

**Sources:** [README.md:52-70](), [README.md:469-495]()

---

## Core Skills Integration

**Diagram: How Core Skills Interact Throughout Development Cycle**

```mermaid
graph TB
    REQUEST["Developer Request<br/>'Add email validation'"]
    
    subgraph AutoTransform["Auto-Transform (iterative-development.md)"]
        PARSE["Extract requirements"]
        TEMPLATE["Structure TDD workflow"]
        INVOKE["Invoke /ralph-loop"]
    end
    
    subgraph RalphLoop["Ralph Loop Execution"]
        RED["RED: Write failing tests<br/>(base.md TDD rules)"]
        GREEN["GREEN: Implement<br/>(base.md complexity limits)"]
        VALIDATE["VALIDATE: Lint + Coverage<br/>(base.md 80% minimum)"]
    end
    
    subgraph QualityGates["Quality Gates"]
        PRECOMMIT["Pre-commit Hook<br/>(security.md secret scan)"]
        REVIEW["Code Review<br/>(code-review.md severity check)"]
        SIZE["Commit Size Check<br/>(commit-hygiene.md thresholds)"]
    end
    
    subgraph StateManagement["State Management"]
        TODO["Update todos/<br/>(base.md atomic todos)"]
        SESSION["Checkpoint session/<br/>(session-management.md)"]
        TEAM["Update team/state.md<br/>(team-coordination.md)"]
        DEDUP["Check CODE_INDEX.md<br/>(code-deduplication.md)"]
    end
    
    REQUEST --> PARSE --> TEMPLATE --> INVOKE
    INVOKE --> RED --> GREEN --> VALIDATE
    VALIDATE --> DEDUP
    DEDUP --> PRECOMMIT
    PRECOMMIT --> REVIEW
    REVIEW --> SIZE
    SIZE --> TODO --> SESSION --> TEAM
```

**Skill Dependencies:**

| Primary Skill | Depends On | Reason |
|---------------|------------|--------|
| `iterative-development.md` | `base.md` | Uses TDD workflow and todo format |
| `code-review.md` | `security.md` | Security checks in review |
| `commit-hygiene.md` | `base.md` | Atomic todo principle |
| `team-coordination.md` | `session-management.md` | Uses session state format |
| `code-deduplication.md` | `base.md` | Check-before-write enforcement |

**Enforcement Layers:**

```
Layer 1: Development-Time (base.md)
  └─ Complexity checks before file completion
  └─ TDD workflow enforcement
  └─ 80% coverage requirement

Layer 2: Pre-Commit (security.md)
  └─ Secret scanning
  └─ .env validation
  └─ Lint + type check

Layer 3: Pre-Push (code-review.md)
  └─ Mandatory review
  └─ Critical/High blocks push
  └─ Medium/Low advisory

Layer 4: CI/CD (security.md + base.md)
  └─ Full test suite
  └─ TruffleHog secret scan
  └─ Dependency audit
  └─ Coverage validation

Layer 5: Session End (session-management.md)
  └─ Checkpoint state
  └─ Archive decisions
  └─ Update handoffs
```

**Sources:** [README.md:10-40](), [skills/base.md:1-579](), [templates/CLAUDE.md:1-113]()

---

# Page: Language and Framework Skills

# Language and Framework Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/playwright-testing.md](skills/playwright-testing.md)
- [skills/react-web.md](skills/react-web.md)

</details>



## Purpose and Scope

This document covers the language-specific and framework-specific skills in Claude Bootstrap. These skills provide technology stack patterns, tooling configurations, and coding standards that enforce TDD-first development, strict type safety, and maintainable architecture.

For the overall skills architecture and loading mechanism, see [Skills Architecture](#5.1). For core skills that apply to all projects, see [Core Skills](#5.2). For UI-specific patterns and accessibility requirements, see [UI Development and Testing](#5.4).

**Coverage:**
- Language skills: Python, TypeScript
- Backend frameworks: Node.js (Express/Fastify), FastAPI
- Frontend frameworks: React (Web), Next.js, React Native
- Tool configurations: linters, formatters, type checkers, test runners
- Skill selection logic during project initialization

---

## Skills Hierarchy and Selection

### Language and Framework Skill Tree

```mermaid
graph TB
    INIT["/initialize-project"]
    
    subgraph "Language Selection"
        LANG_Q["Language choice?"]
        PYTHON["python.md"]
        TYPESCRIPT["typescript.md"]
    end
    
    subgraph "Python Stack"
        PY_FRAME["Framework?"]
        FASTAPI["FastAPI"]
        FLASK["Flask/Express patterns"]
        PY_TOOLS["ruff + mypy + pytest"]
    end
    
    subgraph "TypeScript Stack"
        TS_FRAME["Framework?"]
        REACT_WEB["react-web.md"]
        REACT_NATIVE["react-native.md"]
        NEXTJS["Next.js patterns"]
        NODE_BACKEND["nodejs-backend.md"]
        TS_TOOLS["eslint + tsc --strict + jest/vitest"]
    end
    
    subgraph "Backend Skills"
        BE_PATTERNS["Repository pattern<br/>Service layer<br/>API routes"]
        BE_DB["Supabase integration"]
    end
    
    subgraph "Frontend Skills"
        FE_PATTERNS["Component patterns<br/>Hooks<br/>State management"]
        FE_ROUTING["React Router<br/>Next.js routing"]
        FE_QUERY["React Query<br/>Zustand"]
    end
    
    INIT --> LANG_Q
    
    LANG_Q -->|"Python"| PYTHON
    LANG_Q -->|"TypeScript"| TYPESCRIPT
    
    PYTHON --> PY_FRAME
    PY_FRAME --> FASTAPI
    PY_FRAME --> FLASK
    PYTHON --> PY_TOOLS
    
    TYPESCRIPT --> TS_FRAME
    TS_FRAME -->|"Web"| REACT_WEB
    TS_FRAME -->|"Mobile"| REACT_NATIVE
    TS_FRAME -->|"Full-stack"| NEXTJS
    TS_FRAME -->|"Backend"| NODE_BACKEND
    TYPESCRIPT --> TS_TOOLS
    
    FASTAPI --> BE_PATTERNS
    NODE_BACKEND --> BE_PATTERNS
    BE_PATTERNS --> BE_DB
    
    REACT_WEB --> FE_PATTERNS
    REACT_NATIVE --> FE_PATTERNS
    NEXTJS --> FE_PATTERNS
    NEXTJS --> BE_PATTERNS
    
    FE_PATTERNS --> FE_ROUTING
    FE_PATTERNS --> FE_QUERY
```

**Sources:** [README.md:396-465](), Diagram 3 from system architecture

### Skill Loading Matrix

| Project Type | Language Skill | Framework Skill(s) | Additional Skills |
|--------------|----------------|-------------------|-------------------|
| Python Backend | `python.md` | `supabase-python.md` | `database-schema.md` |
| Python FastAPI | `python.md` | FastAPI patterns | `supabase-python.md` |
| TypeScript Backend | `typescript.md` | `nodejs-backend.md`, `supabase-node.md` | `database-schema.md` |
| React Web | `typescript.md` | `react-web.md` | `ui-web.md`, `playwright-testing.md` |
| React Native | `typescript.md` | `react-native.md` | `ui-mobile.md`, `ui-testing.md` |
| Next.js Full-Stack | `typescript.md` | `react-web.md`, `supabase-nextjs.md` | `ui-web.md`, `database-schema.md` |

**Sources:** [README.md:412-420](), [README.md:438-446]()

---

## Python Language Skill

### Tool Configuration

The Python skill enforces modern Python tooling with strict type checking and formatting:

**Toolchain:**
- **ruff**: Linting and auto-formatting (replaces Black, isort, flake8)
- **mypy**: Static type checking with strict mode
- **pytest**: Test framework with coverage reporting

### Project Structure

```
project/
├── src/
│   ├── core/              # Business logic
│   ├── api/               # FastAPI routes
│   ├── services/          # Service layer
│   ├── repositories/      # Data access
│   └── models/            # Pydantic models
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml         # Tool configuration
├── mypy.ini
└── pytest.ini
```

### Tool Configuration Files

**pyproject.toml:**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
fixable = ["ALL"]

[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"
```

### Type Safety Patterns

```python
# Strict typing enforced
from typing import Protocol, TypedDict, Literal

class UserRepository(Protocol):
    def get_by_id(self, user_id: str) -> User | None:
        ...

# Pydantic for validation
from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None
```

**Sources:** [README.md:415]()

---

## TypeScript Language Skill

### Tool Configuration

The TypeScript skill enforces strict type checking and modern ESLint rules:

**Toolchain:**
- **TypeScript**: Strict mode (`strict: true`) in `tsconfig.json`
- **ESLint**: Code quality and consistency rules
- **Jest/Vitest**: Test framework with coverage
- **Prettier**: Code formatting (optional)

### TypeScript Strict Mode Requirements

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
```

### ESLint Configuration

```javascript
// eslint.config.js
export default [
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/explicit-function-return-type': 'warn',
      '@typescript-eslint/no-unused-vars': 'error',
      'no-console': ['warn', { allow: ['error', 'warn'] }],
      'max-lines-per-function': ['error', { max: 20 }],
      'max-lines': ['error', { max: 200 }],
      'max-params': ['error', 3],
      'complexity': ['error', 5]
    }
  }
];
```

### Interface and Type Patterns

```typescript
// Explicit interfaces required
interface UserProps {
  id: string;
  email: string;
  name?: string;
}

// Type guards for narrowing
function isUser(value: unknown): value is User {
  return typeof value === 'object' && value !== null && 'id' in value;
}

// Discriminated unions
type Result<T> = 
  | { success: true; data: T }
  | { success: false; error: string };
```

**Sources:** [README.md:416]()

---

## React Web Framework Skill

### Test-First Development (Mandatory)

The React Web skill enforces strict test-first development where tests must be written before implementation.

```mermaid
stateDiagram-v2
    [*] --> CreateTest: "Create Button.test.tsx"
    CreateTest --> RunTest1: "npm test -- Button"
    RunTest1 --> TestFails: "Tests MUST fail"
    TestFails --> CreateImpl: "Create Button.tsx"
    CreateImpl --> RunTest2: "npm test -- Button"
    RunTest2 --> TestPasses: "Tests pass"
    TestPasses --> AddStyles: "Create Button.module.css"
    AddStyles --> [*]
    
    TestPasses --> RefactorIfNeeded: "Optional refactor"
    RefactorIfNeeded --> RunTest2: "Tests ensure safety"
```

**Sources:** [skills/react-web.md:9-138]()

### Component Development Order

| Step | File | Action | Command |
|------|------|--------|---------|
| 1 | `Button.test.tsx` | Write all test cases | - |
| 2 | - | Run tests (must fail) | `npm test -- Button` |
| 3 | `Button.tsx` | Implement component | - |
| 4 | - | Run tests (must pass) | `npm test -- Button` |
| 5 | `Button.module.css` | Add styles | - |

### Project Structure

```
src/
├── core/                      # Pure business logic (no React)
│   ├── types.ts
│   └── services/
├── components/                # Reusable UI components
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   ├── Button.module.css
│   │   └── index.ts
│   └── index.ts
├── pages/                     # Route-level components
│   ├── Home/
│   │   ├── HomePage.tsx
│   │   ├── useHome.ts        # Page-specific hook
│   │   └── index.ts
│   └── index.ts
├── hooks/                     # Shared custom hooks
├── store/                     # State management (Zustand)
├── api/                       # React Query hooks
└── utils/
```

**Sources:** [skills/react-web.md:142-176]()

### Component Patterns

```mermaid
graph TB
    COMPONENT["Component.tsx"]
    TEST["Component.test.tsx"]
    HOOK["useComponent.ts"]
    STORE["useAppStore (Zustand)"]
    QUERY["useQuery (React Query)"]
    
    subgraph "Component Layer"
        COMPONENT
        TEST
    end
    
    subgraph "Logic Layer"
        HOOK
    end
    
    subgraph "State Layer"
        STORE
        QUERY
    end
    
    TEST -->|"Tests"| COMPONENT
    COMPONENT -->|"Uses"| HOOK
    HOOK -->|"Global state"| STORE
    HOOK -->|"Server state"| QUERY
    
    COMPONENT -->|"Props interface"| INTERFACE["ComponentProps"]
    COMPONENT -->|"Returns"| JSX["JSX.Element"]
```

**Functional Components Only:**
```typescript
// Explicit props interface required
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}

export function Button({
  label,
  onClick,
  disabled = false,
  variant = 'primary'
}: ButtonProps): JSX.Element {
  return (
    <button
      className={styles[variant]}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
}
```

**Sources:** [skills/react-web.md:180-208]()

### State Management Stack

| State Type | Tool | Use Case |
|------------|------|----------|
| Local | `useState` | Component-only state |
| Global UI | Zustand | Theme, user preferences, UI state |
| Server | React Query | API data, caching, mutations |
| Form | React Hook Form | Form state and validation |

**Zustand Global State:**
```typescript
// store/useAppStore.ts
import { create } from 'zustand';

interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  setUser: (user: User | null) => void;
  toggleTheme: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  theme: 'light',
  setUser: (user) => set({ user }),
  toggleTheme: () => set((state) => ({
    theme: state.theme === 'light' ? 'dark' : 'light'
  })),
}));
```

**React Query Server State:**
```typescript
// api/queries/useItems.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useItems() {
  return useQuery({
    queryKey: ['items'],
    queryFn: itemsApi.getAll,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: itemsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}
```

**Sources:** [skills/react-web.md:260-314]()

### Testing Patterns

**Component Test Structure:**
```typescript
// Button.test.tsx - Create BEFORE Button.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  describe('rendering', () => {
    it('renders with label', () => {
      render(<Button label="Click me" onClick={() => {}} />);
      expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
    });
  });

  describe('interactions', () => {
    it('calls onClick when clicked', () => {
      const onClick = vi.fn();
      render(<Button label="Click me" onClick={onClick} />);
      fireEvent.click(screen.getByRole('button'));
      expect(onClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('accessibility', () => {
    it('has correct aria attributes when disabled', () => {
      render(<Button label="Click" onClick={() => {}} disabled />);
      expect(screen.getByRole('button')).toHaveAttribute('aria-disabled', 'true');
    });
  });
});
```

**Sources:** [skills/react-web.md:37-81](), [skills/react-web.md:433-464]()

---

## Node.js Backend Framework Skill

### Architecture Pattern

```mermaid
graph TB
    ROUTE["API Routes<br/>(Express/Fastify)"]
    SERVICE["Service Layer<br/>(Business Logic)"]
    REPO["Repository Layer<br/>(Data Access)"]
    DB["Supabase Client<br/>(Database)"]
    VALIDATION["Zod Validation<br/>(Request/Response)"]
    
    CLIENT["HTTP Client"] --> ROUTE
    ROUTE --> VALIDATION
    VALIDATION --> SERVICE
    SERVICE --> REPO
    REPO --> DB
    
    SERVICE -->|"Error handling"| ERROR["Custom Errors"]
    ERROR --> ROUTE
    
    ROUTE -->|"Response"| CLIENT
```

### Project Structure

```
src/
├── routes/                    # API endpoints
│   ├── users.ts
│   └── index.ts
├── services/                  # Business logic
│   ├── user.service.ts
│   └── user.service.test.ts
├── repositories/              # Data access
│   ├── user.repository.ts
│   └── user.repository.test.ts
├── schemas/                   # Zod validation schemas
│   ├── user.schema.ts
│   └── index.ts
├── middleware/                # Express/Fastify middleware
│   ├── auth.ts
│   └── error-handler.ts
├── db/                        # Database client
│   └── supabase.ts
└── server.ts                  # App entry point
```

### Layer Separation Pattern

**Route Layer (Express):**
```typescript
// routes/users.ts
import { Router } from 'express';
import { createUserSchema } from '../schemas/user.schema';
import { userService } from '../services/user.service';

const router = Router();

router.post('/users', async (req, res, next) => {
  try {
    const data = createUserSchema.parse(req.body);
    const user = await userService.createUser(data);
    res.status(201).json(user);
  } catch (error) {
    next(error);
  }
});

export default router;
```

**Service Layer:**
```typescript
// services/user.service.ts
import { userRepository } from '../repositories/user.repository';
import type { CreateUserData, User } from '../types';

export const userService = {
  async createUser(data: CreateUserData): Promise<User> {
    // Validation and business logic
    if (await userRepository.existsByEmail(data.email)) {
      throw new ConflictError('Email already exists');
    }
    return userRepository.create(data);
  },

  async getUserById(id: string): Promise<User | null> {
    return userRepository.findById(id);
  }
};
```

**Repository Layer:**
```typescript
// repositories/user.repository.ts
import { supabase } from '../db/supabase';
import type { CreateUserData, User } from '../types';

export const userRepository = {
  async create(data: CreateUserData): Promise<User> {
    const { data: user, error } = await supabase
      .from('users')
      .insert(data)
      .select()
      .single();

    if (error) throw new DatabaseError(error.message);
    return user;
  },

  async findById(id: string): Promise<User | null> {
    const { data, error } = await supabase
      .from('users')
      .select()
      .eq('id', id)
      .single();

    if (error && error.code !== 'PGRST116') {
      throw new DatabaseError(error.message);
    }
    return data;
  },

  async existsByEmail(email: string): Promise<boolean> {
    const { count } = await supabase
      .from('users')
      .select('id', { count: 'exact', head: true })
      .eq('email', email);

    return (count ?? 0) > 0;
  }
};
```

### Request Validation with Zod

```typescript
// schemas/user.schema.ts
import { z } from 'zod';

export const createUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().optional(),
});

export const updateUserSchema = z.object({
  name: z.string().optional(),
  bio: z.string().max(500).optional(),
});

export type CreateUserData = z.infer<typeof createUserSchema>;
export type UpdateUserData = z.infer<typeof updateUserSchema>;
```

**Sources:** [README.md:418]()

---

## React Native Framework Skill

### Platform-Specific Patterns

```mermaid
graph TB
    COMPONENT["Component.tsx"]
    IOS["Platform.OS === 'ios'"]
    ANDROID["Platform.OS === 'android'"]
    SHARED["Shared Logic"]
    
    COMPONENT --> SHARED
    COMPONENT --> IOS
    COMPONENT --> ANDROID
    
    IOS -->|"SafeAreaView"| IOS_UI["iOS-specific UI"]
    ANDROID -->|"StatusBar"| ANDROID_UI["Android-specific UI"]
    
    subgraph "Platform Detection"
        IOS
        ANDROID
    end
    
    subgraph "Platform UI"
        IOS_UI
        ANDROID_UI
    end
```

### Project Structure

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.ios.tsx        # iOS-specific
│   │   ├── Button.android.tsx    # Android-specific
│   │   └── Button.test.tsx
│   └── index.ts
├── screens/                       # Navigation screens
│   ├── Home/
│   │   ├── HomeScreen.tsx
│   │   └── useHome.ts
│   └── index.ts
├── navigation/
│   ├── AppNavigator.tsx
│   └── types.ts
├── hooks/
├── store/
└── utils/
```

### Platform-Specific Code

**File Extension Pattern:**
```typescript
// Button.ios.tsx - iOS implementation
import { StyleSheet, TouchableOpacity } from 'react-native';

export function Button({ label, onPress }: ButtonProps) {
  return (
    <TouchableOpacity style={styles.button} onPress={onPress}>
      <Text style={styles.text}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#007AFF', // iOS blue
    borderRadius: 8,
    paddingVertical: 12,
  },
});
```

```typescript
// Button.android.tsx - Android implementation
import { StyleSheet, TouchableNativeFeedback } from 'react-native';

export function Button({ label, onPress }: ButtonProps) {
  return (
    <TouchableNativeFeedback onPress={onPress}>
      <View style={styles.button}>
        <Text style={styles.text}>{label}</Text>
      </View>
    </TouchableNativeFeedback>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#6200EE', // Material purple
    borderRadius: 4,
    elevation: 2,
  },
});
```

**Inline Platform Detection:**
```typescript
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.OS === 'ios' ? 44 : 0,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
      },
      android: {
        elevation: 4,
      },
    }),
  },
});
```

### Navigation Patterns (React Navigation)

```typescript
// navigation/types.ts
export type RootStackParamList = {
  Home: undefined;
  Profile: { userId: string };
  Settings: undefined;
};

// navigation/AppNavigator.tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator<RootStackParamList>();

export function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Profile" component={ProfileScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// screens/Home/HomeScreen.tsx
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Home'>;

export function HomeScreen({ navigation }: Props) {
  return (
    <Button
      label="Go to Profile"
      onPress={() => navigation.navigate('Profile', { userId: '123' })}
    />
  );
}
```

**Sources:** [README.md:419]()

---

## FastAPI Framework Skill

### Project Structure

```
src/
├── api/
│   ├── routes/               # API endpoints
│   │   ├── users.py
│   │   └── __init__.py
│   ├── dependencies.py       # FastAPI dependencies
│   └── main.py               # FastAPI app
├── core/
│   ├── config.py             # Settings with pydantic
│   └── security.py           # Auth utilities
├── services/                 # Business logic
│   ├── user_service.py
│   └── __init__.py
├── repositories/             # Data access
│   ├── user_repository.py
│   └── __init__.py
├── models/                   # Pydantic models
│   ├── user.py
│   └── __init__.py
└── db/
    ├── supabase.py
    └── __init__.py
```

### FastAPI Route Patterns

```python
# api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.user import CreateUser, User
from services.user_service import UserService
from api.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: CreateUser,
    service: UserService = Depends(get_user_service)
) -> User:
    """Create a new user."""
    existing = await service.get_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    return await service.create(user_data)

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
) -> User:
    """Get user by ID."""
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
```

### Pydantic Models for Validation

```python
# models/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class CreateUser(BaseModel):
    """Request model for creating a user."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str | None = Field(None, max_length=100)

class User(BaseModel):
    """Response model for user data."""
    id: str
    email: EmailStr
    name: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy models

class UpdateUser(BaseModel):
    """Request model for updating a user."""
    name: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=500)
```

### Dependency Injection

```python
# api/dependencies.py
from fastapi import Depends
from db.supabase import get_supabase_client
from services.user_service import UserService
from repositories.user_repository import UserRepository
from supabase import Client

def get_user_repository(
    client: Client = Depends(get_supabase_client)
) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(client)

def get_user_service(
    repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    """Get user service instance."""
    return UserService(repo)
```

### Service Layer Pattern

```python
# services/user_service.py
from repositories.user_repository import UserRepository
from models.user import CreateUser, User, UpdateUser

class UserService:
    """Business logic for user operations."""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def create(self, data: CreateUser) -> User:
        """Create a new user with hashed password."""
        hashed_password = hash_password(data.password)
        user_data = data.dict(exclude={'password'})
        user_data['password_hash'] = hashed_password
        return await self.repository.create(user_data)
    
    async def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        return await self.repository.find_by_id(user_id)
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return await self.repository.find_by_email(email)
```

**Sources:** [README.md:415]()

---

## Next.js Full-Stack Pattern

### Project Structure

Next.js projects combine frontend and backend in a single codebase:

```
project/
├── app/                       # App Router (Next.js 13+)
│   ├── (auth)/               # Route group
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── dashboard/
│   │   ├── page.tsx
│   │   └── layout.tsx
│   ├── api/                  # API routes
│   │   ├── users/
│   │   │   └── route.ts
│   │   └── auth/
│   │       └── route.ts
│   ├── layout.tsx
│   └── page.tsx
├── components/                # React components
├── lib/                       # Utilities
│   ├── supabase/
│   │   ├── client.ts         # Client-side Supabase
│   │   └── server.ts         # Server-side Supabase
│   └── api/                   # API client hooks
├── hooks/
└── types/
```

### Server vs Client Components

```typescript
// app/dashboard/page.tsx - Server Component (default)
import { createServerSupabaseClient } from '@/lib/supabase/server';

export default async function DashboardPage() {
  const supabase = createServerSupabaseClient();
  const { data: items } = await supabase.from('items').select();
  
  return <ItemList items={items} />;
}

// components/InteractiveButton.tsx - Client Component
'use client';

import { useState } from 'react';

export function InteractiveButton() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

### API Route Handlers

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase/server';
import { z } from 'zod';

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().optional(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const data = createUserSchema.parse(body);
    
    const supabase = createServerSupabaseClient();
    const { data: user, error } = await supabase
      .from('users')
      .insert(data)
      .select()
      .single();
    
    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 400 }
      );
    }
    
    return NextResponse.json(user, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: error.errors },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  const supabase = createServerSupabaseClient();
  const { data: users, error } = await supabase
    .from('users')
    .select();
  
  if (error) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
  
  return NextResponse.json(users);
}
```

### Server Actions (Next.js 14+)

```typescript
// app/actions/user.ts
'use server';

import { createServerSupabaseClient } from '@/lib/supabase/server';
import { revalidatePath } from 'next/cache';

export async function createUser(formData: FormData) {
  const email = formData.get('email') as string;
  const name = formData.get('name') as string;
  
  const supabase = createServerSupabaseClient();
  const { data, error } = await supabase
    .from('users')
    .insert({ email, name })
    .select()
    .single();
  
  if (error) {
    return { error: error.message };
  }
  
  revalidatePath('/users');
  return { data };
}

// app/users/CreateUserForm.tsx
'use client';

import { createUser } from '../actions/user';
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create User'}
    </button>
  );
}

export function CreateUserForm() {
  return (
    <form action={createUser}>
      <input name="email" type="email" required />
      <input name="name" type="text" />
      <SubmitButton />
    </form>
  );
}
```

**Sources:** [README.md:416](), [README.md:443]()

---

## Tool Configuration Reference

### Python Stack Configuration

**pyproject.toml:**
```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
  "fastapi>=0.104.0",
  "uvicorn[standard]>=0.24.0",
  "pydantic>=2.5.0",
  "supabase>=2.0.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=7.4.0",
  "pytest-cov>=4.1.0",
  "pytest-asyncio>=0.21.0",
  "mypy>=1.7.0",
  "ruff>=0.1.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"
select = [
  "E",   # pycodestyle errors
  "F",   # pyflakes
  "I",   # isort
  "N",   # pep8-naming
  "W",   # pycodestyle warnings
  "UP",  # pyupgrade
  "B",   # flake8-bugbear
]

[tool.mypy]
strict = true
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
  "--cov=src",
  "--cov-report=term-missing",
  "--cov-report=html",
  "--cov-fail-under=80",
]
asyncio_mode = "auto"
```

### TypeScript Stack Configuration

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowJs": false,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "build"]
}
```

**package.json scripts:**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src --ext ts,tsx",
    "lint:fix": "eslint src --ext ts,tsx --fix",
    "typecheck": "tsc --noEmit"
  }
}
```

### Vitest Configuration

**vitest.config.ts:**
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
        '**/index.ts',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

**Sources:** [README.md:515-530]()

---

## Framework Skill Interaction Matrix

```mermaid
graph TB
    subgraph "Language Layer"
        PYTHON["python.md<br/>ruff + mypy + pytest"]
        TYPESCRIPT["typescript.md<br/>eslint + tsc + vitest"]
    end
    
    subgraph "Backend Frameworks"
        FASTAPI["FastAPI<br/>Pydantic validation<br/>async/await"]
        NODE_BACKEND["nodejs-backend.md<br/>Express/Fastify<br/>Zod validation"]
        NEXTJS_API["Next.js API Routes<br/>Server Actions"]
    end
    
    subgraph "Frontend Frameworks"
        REACT_WEB["react-web.md<br/>Hooks + React Query<br/>Zustand"]
        REACT_NATIVE["react-native.md<br/>Platform-specific<br/>Navigation"]
        NEXTJS_UI["Next.js App Router<br/>Server Components"]
    end
    
    subgraph "Database Layer"
        SUPA_PY["supabase-python.md"]
        SUPA_NODE["supabase-node.md"]
        SUPA_NEXTJS["supabase-nextjs.md"]
        DB_SCHEMA["database-schema.md"]
    end
    
    PYTHON --> FASTAPI
    PYTHON --> SUPA_PY
    
    TYPESCRIPT --> NODE_BACKEND
    TYPESCRIPT --> REACT_WEB
    TYPESCRIPT --> REACT_NATIVE
    TYPESCRIPT --> NEXTJS_API
    TYPESCRIPT --> NEXTJS_UI
    
    FASTAPI --> SUPA_PY
    NODE_BACKEND --> SUPA_NODE
    NEXTJS_API --> SUPA_NEXTJS
    NEXTJS_UI --> SUPA_NEXTJS
    
    SUPA_PY --> DB_SCHEMA
    SUPA_NODE --> DB_SCHEMA
    SUPA_NEXTJS --> DB_SCHEMA
    
    REACT_WEB -.->|"Full-stack"| NODE_BACKEND
    NEXTJS_UI -.->|"Same codebase"| NEXTJS_API
```

**Sources:** [README.md:412-446](), [README.md:667-678]()

---

## Anti-Patterns and Violations

### Common Violations Across All Skills

| Anti-Pattern | Detection | Enforcement |
|--------------|-----------|-------------|
| **Implementation before tests** | No `.test.ts` file exists | `⚠️ TEST-FIRST VIOLATION` - Must create test file first |
| **Any type in TypeScript** | ESLint `@typescript-eslint/no-explicit-any` | Blocks commit in pre-commit hook |
| **Missing type annotations** | TypeScript strict mode | Build fails |
| **Functions > 20 lines** | ESLint `max-lines-per-function` | Lint error |
| **Files > 200 lines** | ESLint `max-lines` | Lint error |
| **> 3 function parameters** | ESLint `max-params` | Lint error |
| **Untyped Pydantic models** | mypy strict mode | Type check fails |
| **Missing test coverage < 80%** | pytest/vitest coverage check | CI blocks merge |

### React-Specific Anti-Patterns

```typescript
// ❌ WRONG: Inline function in JSX
<button onClick={() => handleClick(id)}>Click</button>

// ✅ CORRECT: useCallback
const handleClick = useCallback((id: string) => {
  // handle click
}, []);
<button onClick={() => handleClick(id)}>Click</button>

// ❌ WRONG: Logic in component
export function UserList() {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    fetch('/api/users').then(r => r.json()).then(setUsers);
  }, []);
  return <div>{/* render */}</div>;
}

// ✅ CORRECT: Extract to hook
function useUsers() {
  return useQuery({ queryKey: ['users'], queryFn: fetchUsers });
}
export function UserList() {
  const { data: users } = useUsers();
  return <div>{/* render */}</div>;
}

// ❌ WRONG: Index as key
{items.map((item, index) => <Item key={index} item={item} />)}

// ✅ CORRECT: Stable ID as key
{items.map(item => <Item key={item.id} item={item} />)}
```

**Sources:** [skills/react-web.md:535-549]()

### Backend Anti-Patterns

```python
# ❌ WRONG: Business logic in route
@router.post("/users")
async def create_user(user_data: CreateUser):
    # Mixing validation, business logic, and data access
    if not user_data.email:
        raise HTTPException(400)
    hashed = hash_password(user_data.password)
    user = await supabase.from('users').insert({...}).execute()
    return user

# ✅ CORRECT: Layered architecture
@router.post("/users")
async def create_user(
    user_data: CreateUser,
    service: UserService = Depends(get_user_service)
):
    return await service.create(user_data)
```

```typescript
// ❌ WRONG: No error handling
router.post('/users', async (req, res) => {
  const user = await userService.createUser(req.body);
  res.json(user);
});

// ✅ CORRECT: Try-catch with proper error handling
router.post('/users', async (req, res, next) => {
  try {
    const data = createUserSchema.parse(req.body);
    const user = await userService.createUser(data);
    res.status(201).json(user);
  } catch (error) {
    next(error);
  }
});
```

**Sources:** [README.md:338-342]()

---

## Quick Reference: Skills by Project Type

| Project Type | Initialize With | Skills Loaded |
|--------------|-----------------|---------------|
| **Python CLI** | `/initialize-project` → Python | `base.md`, `python.md`, `security.md`, `credentials.md` |
| **FastAPI Backend** | `/initialize-project` → Python + FastAPI | Above + `supabase-python.md`, `database-schema.md` |
| **React SPA** | `/initialize-project` → TypeScript + React | `base.md`, `typescript.md`, `react-web.md`, `ui-web.md` |
| **React Native App** | `/initialize-project` → TypeScript + React Native | `base.md`, `typescript.md`, `react-native.md`, `ui-mobile.md` |
| **Node.js API** | `/initialize-project` → TypeScript + Backend | `base.md`, `typescript.md`, `nodejs-backend.md`, `supabase-node.md` |
| **Next.js Full-Stack** | `/initialize-project` → TypeScript + Next.js | `base.md`, `typescript.md`, `react-web.md`, `supabase-nextjs.md`, `ui-web.md` |

**Test Requirements (All Projects):**
- Unit tests: `pytest` (Python) or `vitest` (TypeScript)
- E2E tests: `playwright` (web/mobile)
- Coverage: ≥80% enforced in CI
- TDD: Tests written before implementation

**Sources:** [README.md:667-678]()

---

# Page: UI Development and Testing

# UI Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/ui-mobile.md](skills/ui-mobile.md)
- [skills/ui-testing.md](skills/ui-testing.md)
- [skills/ui-web.md](skills/ui-web.md)

</details>



## Purpose and Scope

This page documents the UI development and testing system within Claude Bootstrap's skills architecture. It covers the mandatory WCAG 2.1 AA accessibility standards, platform-specific patterns for web and mobile interfaces, and the pre-flight checklist workflow that ensures UI compliance before shipping.

**Scope**: This page focuses on UI design patterns, accessibility enforcement, and visual verification. For end-to-end testing with Playwright, see [5.5](#5.5). For framework-specific implementation details, see [5.3](#5.3).

---

## UI Skills Architecture

Claude Bootstrap provides three UI-focused skill files that load conditionally based on project type:

| Skill File | Loads When | Purpose |
|------------|------------|---------|
| `ui-web.md` | Web projects (React, Next.js) | WCAG 2.1 AA compliance, Tailwind patterns, glassmorphism, dark mode |
| `ui-mobile.md` | Mobile projects (React Native) | Touch targets (44pt minimum), platform differences (iOS/Android), native patterns |
| `ui-testing.md` | Any project with UI | Pre-flight checklist, contrast verification, common fix patterns |

**Skills Loading Diagram**

```mermaid
graph TB
    INIT["/initialize-project"]
    PROJECT_TYPE{Project Type?}
    
    WEB[Web Project]
    MOBILE[Mobile Project]
    
    LOAD_WEB["Load ui-web.md"]
    LOAD_MOBILE["Load ui-mobile.md"]
    LOAD_TESTING["Load ui-testing.md"]
    
    PROJECT_SKILLS[".claude/skills/"]
    
    INIT --> PROJECT_TYPE
    
    PROJECT_TYPE -->|"React, Next.js"| WEB
    PROJECT_TYPE -->|"React Native"| MOBILE
    
    WEB --> LOAD_WEB
    WEB --> LOAD_TESTING
    
    MOBILE --> LOAD_MOBILE
    MOBILE --> LOAD_TESTING
    
    LOAD_WEB --> PROJECT_SKILLS
    LOAD_MOBILE --> PROJECT_SKILLS
    LOAD_TESTING --> PROJECT_SKILLS
    
    PROJECT_SKILLS --> CLAUDEMD["CLAUDE.md<br/>Skills active in session"]
```

Sources: [README.md:420-429](), [skills/ui-web.md:1-3](), [skills/ui-mobile.md:1-3](), [skills/ui-testing.md:1-3]()

---

## Mandatory Accessibility Standards (NON-NEGOTIABLE)

### WCAG 2.1 AA Requirements

Both `ui-web.md` and `ui-mobile.md` enforce identical mandatory rules that block development if violated. These are marked as **CRITICAL** and **NON-NEGOTIABLE** in the skill files.

**WCAG 2.1 AA Enforcement Flow**

```mermaid
graph TB
    CREATE["Developer: Create UI Component"]
    
    CHECK_CONTRAST["Check Color Contrast<br/>WCAG 2.1 AA: 4.5:1 minimum"]
    CHECK_TOUCH["Check Touch Targets<br/>Minimum 44px/pt"]
    CHECK_VISIBILITY["Check Visibility<br/>All buttons have boundaries"]
    CHECK_FOCUS["Check Focus States<br/>Visible focus indicators"]
    CHECK_LABELS["Check Accessibility Labels<br/>Screen reader support"]
    
    CONTRAST_PASS{Contrast ≥ 4.5:1?}
    TOUCH_PASS{Touch ≥ 44px?}
    VISIBILITY_PASS{Boundaries visible?}
    FOCUS_PASS{Focus visible?}
    LABELS_PASS{Labels present?}
    
    BLOCK_DEV["❌ BLOCK DEVELOPMENT<br/>Must fix before proceeding"]
    
    PASS["✅ Component Approved"]
    
    CREATE --> CHECK_CONTRAST
    CHECK_CONTRAST --> CONTRAST_PASS
    
    CONTRAST_PASS -->|No| BLOCK_DEV
    CONTRAST_PASS -->|Yes| CHECK_TOUCH
    
    CHECK_TOUCH --> TOUCH_PASS
    TOUCH_PASS -->|No| BLOCK_DEV
    TOUCH_PASS -->|Yes| CHECK_VISIBILITY
    
    CHECK_VISIBILITY --> VISIBILITY_PASS
    VISIBILITY_PASS -->|No| BLOCK_DEV
    VISIBILITY_PASS -->|Yes| CHECK_FOCUS
    
    CHECK_FOCUS --> FOCUS_PASS
    FOCUS_PASS -->|No| BLOCK_DEV
    FOCUS_PASS -->|Yes| CHECK_LABELS
    
    CHECK_LABELS --> LABELS_PASS
    LABELS_PASS -->|No| BLOCK_DEV
    LABELS_PASS -->|Yes| PASS
```

Sources: [skills/ui-web.md:7-47](), [skills/ui-mobile.md:7-106]()

### Color Contrast Standards

The skills define specific forbidden and safe color combinations with exact contrast ratios:

**Forbidden Combinations** (from [skills/ui-web.md:19-23]()):
- `gray-400` on `white` (#9CA3AF on #FFFFFF = 2.6:1) - **FAILS**
- `gray-500` on `white` (#6B7280 on #FFFFFF = 4.6:1) - **BARELY PASSES**
- White on yellow - **FAILS**
- Light blue on white - **USUALLY FAILS**

**Safe Combinations** (from [skills/ui-web.md:25-29]()):
- `gray-700` on `white` (#374151 on #FFFFFF = 9.2:1)
- `gray-600` on `white` (#4B5563 on #FFFFFF = 6.4:1)
- `gray-900` on `white` (#111827 on #FFFFFF = 16:1)
- White on `gray-900`, `blue-600`, `green-700`

**Tailwind Color Contrast Reference** (from [skills/ui-testing.md:62-79]()):

| Light Mode (on white bg) | Contrast Ratio | Status |
|--------------------------|----------------|---------|
| `text-gray-900` (#111827) | 16:1 | ✓ Safe |
| `text-gray-800` (#1F2937) | 12:1 | ✓ Safe |
| `text-gray-700` (#374151) | 9:1 | ✓ Safe |
| `text-gray-600` (#4B5563) | 6:1 | ✓ Safe |
| `text-gray-500` (#6B7280) | 4.6:1 | ✗ Barely passes |
| `text-gray-400` (#9CA3AF) | 2.6:1 | ✗ **FAILS** |

| Dark Mode (on gray-900 bg) | Contrast Ratio | Status |
|----------------------------|----------------|---------|
| `text-white` (#FFFFFF) | 16:1 | ✓ Safe |
| `text-gray-100` (#F3F4F6) | 13:1 | ✓ Safe |
| `text-gray-200` (#E5E7EB) | 11:1 | ✓ Safe |
| `text-gray-300` (#D1D5DB) | 8:1 | ✓ Safe |
| `text-gray-400` (#9CA3AF) | 5:1 | ✗ Barely passes |
| `text-gray-500` (#6B7280) | 3:1 | ✗ **FAILS** |

Sources: [skills/ui-testing.md:62-79](), [skills/ui-web.md:11-30]()

### Touch Target Requirements

**Minimum Touch Target Sizes** (from [skills/ui-mobile.md:12-35]()):

```typescript
// MANDATORY: 44x44 points for ALL interactive elements
const MINIMUM_TOUCH_SIZE = 44;

// EVERY button, link, icon button must meet this
const styles = StyleSheet.create({
  button: {
    minHeight: MINIMUM_TOUCH_SIZE,
    minWidth: MINIMUM_TOUCH_SIZE,
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  iconButton: {
    width: MINIMUM_TOUCH_SIZE,
    height: MINIMUM_TOUCH_SIZE,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

// NEVER DO THIS:
style={{ height: 30 }}  // ✗ TOO SMALL
style={{ padding: 4 }}  // ✗ RESULTS IN TINY TARGET
```

For web, the equivalent minimum is 44px height with adequate padding ([skills/ui-web.md:37-38]()).

Sources: [skills/ui-mobile.md:11-35](), [skills/ui-web.md:37-38]()

### Visibility Rules

**All Interactive Elements Must Have Visible Boundaries**

From [skills/ui-web.md:49-68]() and [skills/ui-mobile.md:59-105]():

```tsx
// PRIMARY: Solid background with contrasting text
<button className="bg-gray-900 text-white px-4 py-3 rounded-lg">
  Primary
</button>

// SECONDARY: Visible background
<button className="bg-gray-100 text-gray-900 px-4 py-3 rounded-lg">
  Secondary
</button>

// GHOST: MUST have visible border
<button className="border border-gray-300 text-gray-700 px-4 py-3 rounded-lg">
  Ghost
</button>

// ✗ FORBIDDEN: No visible boundary
<button className="text-gray-500">Invisible Button</button>
```

Sources: [skills/ui-web.md:49-68](), [skills/ui-mobile.md:59-105]()

### Focus State Requirements

Every interactive element requires visible focus indicators ([skills/ui-web.md:71-78]()):

```tsx
// EVERY interactive element needs visible focus
className="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"

// ✗ NEVER remove focus without replacement
className="outline-none" // FORBIDDEN
```

Sources: [skills/ui-web.md:71-78](), [skills/ui-testing.md:109-118]()

---

## Pre-Flight Checklist System

The `ui-testing.md` skill provides a systematic checklist that runs **before shipping ANY UI component**. This checklist integrates with the TDD workflow to catch accessibility violations during development.

**Pre-Flight Checklist Execution Flow**

```mermaid
stateDiagram-v2
    [*] --> ComponentCreated: Component implemented
    
    ComponentCreated --> RunChecklist: Run Pre-Flight Checklist
    
    RunChecklist --> VisibilityCheck: 1. Visibility Check
    VisibilityCheck --> TouchTargets: All pass
    VisibilityCheck --> FixIssues: Failures detected
    
    TouchTargets --> StatesCheck: 2. Touch/Click Targets
    StatesCheck --> DarkModeCheck: All pass
    StatesCheck --> FixIssues: Failures detected
    
    DarkModeCheck --> ResponsiveCheck: 3. States (hover/focus/disabled)
    ResponsiveCheck --> ContrastCheck: All pass
    ResponsiveCheck --> FixIssues: Failures detected
    
    ContrastCheck --> AllPassed: 4. Contrast Check
    ContrastCheck --> FixIssues: Contrast < 4.5:1
    
    FixIssues --> ComponentCreated: Apply fixes
    
    AllPassed --> TestPassing: Write/run tests
    TestPassing --> [*]: Ship component
```

Sources: [skills/ui-testing.md:10-43]()

### Checklist Contents

From [skills/ui-testing.md:15-43]():

```markdown
## Visibility Check
- [ ] All buttons have visible background OR border
- [ ] No text is same color as its background
- [ ] All text meets 4.5:1 contrast ratio
- [ ] Ghost/text buttons have visible borders

## Touch/Click Targets
- [ ] All buttons are minimum 44px height
- [ ] Icon buttons are minimum 44x44px
- [ ] Adequate spacing between clickable elements

## States
- [ ] Hover states visible (web)
- [ ] Pressed states visible (mobile)
- [ ] Focus rings on keyboard navigation
- [ ] Disabled states visually distinct (opacity 0.5)
- [ ] Loading states show indicators

## Dark Mode (if applicable)
- [ ] Text readable on dark backgrounds
- [ ] Borders visible in dark mode
- [ ] No gray-400 text on dark backgrounds

## Responsive (web)
- [ ] No horizontal scroll on mobile (320px)
- [ ] Content readable at all breakpoints
- [ ] Touch targets adequate on mobile
```

Sources: [skills/ui-testing.md:15-43]()

### Quick Contrast Verification

The skill provides browser DevTools instructions and online tool recommendations ([skills/ui-testing.md:48-79]()):

**Browser DevTools Method**:
1. Right-click element → Inspect
2. In Styles panel, click on color value
3. Look for contrast ratio display
4. Must show ✓ for AA compliance (4.5:1 for text)

**Online Tools**:
- https://webaim.org/resources/contrastchecker/
- https://coolors.co/contrast-checker

Sources: [skills/ui-testing.md:48-79]()

### Common Fixes

The skill documents fix patterns for frequent violations ([skills/ui-testing.md:83-137]()):

**Fix Pattern: Invisible Button**
```tsx
// PROBLEM: No visible boundary
<button className="text-gray-500">Click</button>

// FIX: Add background OR border
<button className="bg-gray-100 text-gray-900 px-4 py-3 rounded-lg">
  Click
</button>
```

**Fix Pattern: Low Contrast Text**
```tsx
// PROBLEM: Light gray on white
<p className="text-gray-400">Secondary text</p>

// FIX: Use darker gray
<p className="text-gray-600">Secondary text</p>
```

**Fix Pattern: Small Touch Target**
```tsx
// PROBLEM: Too small for fingers
<button className="p-1 text-sm">×</button>

// FIX: Minimum 44px
<button className="w-11 h-11 flex items-center justify-center">×</button>
```

Sources: [skills/ui-testing.md:83-137]()

---

## Web UI Patterns

The `ui-web.md` skill ([skills/ui-web.md:1-629]()) defines comprehensive patterns for web applications using Tailwind CSS.

### Component Pattern Hierarchy

```mermaid
graph TB
    DESIGN_SYSTEM["Design System<br/>(ui-web.md)"]
    
    CORE_PATTERNS["Core Patterns"]
    LAYOUT_PATTERNS["Layout Patterns"]
    INTERACTION_PATTERNS["Interaction Patterns"]
    
    BUTTONS["Button Variants<br/>PrimaryButton, SecondaryButton, GhostButton"]
    CARDS["Card Variants<br/>Card, GlassCard, InteractiveCard"]
    INPUTS["Input Components<br/>Input, TextField"]
    
    CONTAINER["Container<br/>max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"]
    SECTION["Section<br/>py-16 md:py-24"]
    GRID["Grid Systems<br/>Feature Grid, Bento Grid"]
    
    TRANSITIONS["Transitions<br/>duration-150/200/300"]
    HOVER_EFFECTS["Hover Effects<br/>scale, translate, glow"]
    LOADING_STATES["Loading States<br/>Skeleton, Spinner"]
    
    DESIGN_SYSTEM --> CORE_PATTERNS
    DESIGN_SYSTEM --> LAYOUT_PATTERNS
    DESIGN_SYSTEM --> INTERACTION_PATTERNS
    
    CORE_PATTERNS --> BUTTONS
    CORE_PATTERNS --> CARDS
    CORE_PATTERNS --> INPUTS
    
    LAYOUT_PATTERNS --> CONTAINER
    LAYOUT_PATTERNS --> SECTION
    LAYOUT_PATTERNS --> GRID
    
    INTERACTION_PATTERNS --> TRANSITIONS
    INTERACTION_PATTERNS --> HOVER_EFFECTS
    INTERACTION_PATTERNS --> LOADING_STATES
```

Sources: [skills/ui-web.md:1-629]()

### Button Implementations

From [skills/ui-web.md:262-318]():

**`PrimaryButton`** - Bold, high-contrast primary action:
```tsx
const PrimaryButton = ({ children, ...props }) => (
  <button
    className="
      px-6 py-3
      bg-gray-900 dark:bg-white
      text-white dark:text-gray-900
      font-medium
      rounded-xl
      transition-all duration-200
      hover:bg-gray-800 dark:hover:bg-gray-100
      hover:shadow-lg hover:shadow-gray-900/20
      active:scale-[0.98]
      disabled:opacity-50 disabled:cursor-not-allowed
    "
    {...props}
  >
    {children}
  </button>
);
```

**`SecondaryButton`** - Subtle, lower-contrast secondary action:
```tsx
const SecondaryButton = ({ children, ...props }) => (
  <button
    className="
      px-6 py-3
      bg-gray-100 dark:bg-gray-800
      text-gray-900 dark:text-white
      font-medium
      rounded-xl
      transition-all duration-200
      hover:bg-gray-200 dark:hover:bg-gray-700
      active:scale-[0.98]
    "
    {...props}
  >
    {children}
  </button>
);
```

**`GhostButton`** - Minimal, text-style action with visible hover state:
```tsx
const GhostButton = ({ children, ...props }) => (
  <button
    className="
      px-4 py-2
      text-gray-600 dark:text-gray-400
      font-medium
      rounded-lg
      transition-colors duration-200
      hover:text-gray-900 dark:hover:text-white
      hover:bg-gray-100 dark:hover:bg-gray-800
    "
    {...props}
  >
    {children}
  </button>
);
```

Sources: [skills/ui-web.md:260-318]()

### Glassmorphism Implementation

From [skills/ui-web.md:144-197]():

**`GlassCard` Base Component**:
```tsx
const GlassCard = ({ children, className = '' }) => (
  <div className={`
    backdrop-blur-xl
    bg-white/10
    border border-white/20
    rounded-2xl
    shadow-xl
    shadow-black/5
    ${className}
  `}>
    {children}
  </div>
);
```

**Usage Guidelines** ([skills/ui-web.md:199-211]()):
- ✓ Hero sections with image backgrounds
- ✓ Floating cards over gradients
- ✓ Modal overlays
- ✗ Every card (overuse kills the effect)
- ✗ Forms (reduces contrast)
- ✗ Data tables

Sources: [skills/ui-web.md:144-211]()

### Spacing and Typography Systems

**8px Grid Spacing System** ([skills/ui-web.md:114-127]()):

| Tailwind Class | Pixels | Usage |
|----------------|--------|-------|
| `p-1` | 4px | Tight internal spacing |
| `p-2` | 8px | Compact spacing |
| `p-4` | 16px | Default spacing |
| `p-6` | 24px | Comfortable spacing |
| `p-8` | 32px | Spacious spacing |
| `p-12` | 48px | Section gaps |

**Typography Scale** ([skills/ui-web.md:129-141]()):

| Name | Classes | Usage |
|------|---------|-------|
| `hero` | `text-4xl md:text-5xl font-bold tracking-tight` | Landing page headlines |
| `heading` | `text-2xl md:text-3xl font-semibold` | Section headers |
| `subheading` | `text-lg md:text-xl font-medium` | Card titles |
| `body` | `text-base leading-relaxed` | Body text |
| `caption` | `text-sm text-gray-500` | Metadata, timestamps |

Sources: [skills/ui-web.md:114-141]()

---

## Mobile UI Patterns

The `ui-mobile.md` skill ([skills/ui-mobile.md:1-947]()) provides React Native-specific patterns with iOS and Android platform differences.

### Platform-Specific Implementations

**Platform Detection and Styling** ([skills/ui-mobile.md:172-193]()):

```typescript
import { Platform } from 'react-native';

// Platform-specific values
const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 8,
    },
    android: {
      elevation: 4,
    },
  }),
  
  // iOS uses SF Pro, Android uses Roboto
  text: {
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
});
```

**Design Language Differences** ([skills/ui-mobile.md:196-213]()):

| iOS (Human Interface Guidelines) | Android (Material Design 3) |
|----------------------------------|----------------------------|
| Flat design with subtle depth | Material You dynamic color |
| SF Symbols for icons | Outlined/filled icons |
| Large titles (34pt) | Medium titles (22pt) |
| Rounded corners (10-14pt) | Rounded corners (12-28pt) |
| Blue as default tint | Primary color from theme |

Sources: [skills/ui-mobile.md:169-213]()

### React Native Component Patterns

**Touch Feedback Implementation** ([skills/ui-mobile.md:407-436]()):

```tsx
import { Pressable } from 'react-native';

// iOS-style opacity feedback
const Button = ({ children, onPress }) => (
  <Pressable
    onPress={onPress}
    style={({ pressed }) => [
      styles.button,
      pressed && { opacity: 0.7 },
    ]}
  >
    {children}
  </Pressable>
);

// Android-style ripple
const AndroidButton = ({ children, onPress }) => (
  <Pressable
    onPress={onPress}
    android_ripple={{
      color: 'rgba(0, 0, 0, 0.1)',
      borderless: false,
    }}
    style={styles.button}
  >
    {children}
  </Pressable>
);
```

**Card with Platform-Specific Shadow** ([skills/ui-mobile.md:442-466]()):

```tsx
const Card = ({ children, style }) => (
  <View style={[styles.card, style]}>
    {children}
  </View>
);

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.08,
        shadowRadius: 8,
      },
      android: {
        elevation: 2,
      },
    }),
  },
});
```

Sources: [skills/ui-mobile.md:407-466]()

### Accessibility Implementation

**VoiceOver / TalkBack Support** ([skills/ui-mobile.md:107-137]()):

```tsx
// Button with full accessibility
<Pressable
  accessible={true}
  accessibilityRole="button"
  accessibilityLabel="Submit form"
  accessibilityHint="Double tap to submit your information"
>
  <Text>Submit</Text>
</Pressable>

// Icon button (NO visible text = MUST have label)
<Pressable
  accessible={true}
  accessibilityRole="button"
  accessibilityLabel="Close menu"
>
  <CloseIcon />
</Pressable>

// Image with description
<Image
  accessible={true}
  accessibilityRole="image"
  accessibilityLabel="User profile photo"
  source={...}
/>
```

**Dynamic Type Support** ([skills/ui-mobile.md:868-880]()):

```tsx
import { PixelRatio } from 'react-native';

// Scale fonts with system settings
const fontScale = PixelRatio.getFontScale();
const scaledFontSize = (size: number) => size * fontScale;

// Or use allowFontScaling
<Text allowFontScaling={true} style={{ fontSize: 17 }}>
  This text scales with system settings
</Text>
```

Sources: [skills/ui-mobile.md:107-137](), [skills/ui-mobile.md:868-880]()

### Safe Area Handling

**Safe Area Implementation** ([skills/ui-mobile.md:239-257]()):

```tsx
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const Screen = ({ children }) => {
  const insets = useSafeAreaInsets();
  
  return (
    <View style={{
      flex: 1,
      paddingTop: insets.top,
      paddingBottom: insets.bottom,
      paddingLeft: Math.max(insets.left, 16),
      paddingRight: Math.max(insets.right, 16),
    }}>
      {children}
    </View>
  );
};
```

Sources: [skills/ui-mobile.md:239-257]()

---

## Integration with TDD Workflow

The UI development system integrates with Claude Bootstrap's core TDD workflow ([README.md:319-342]()) to enforce quality gates at each phase.

**UI Development TDD Integration**

```mermaid
stateDiagram-v2
    [*] --> RED_Phase: Write UI tests
    
    RED_Phase --> WriteTests: 1. Write component tests
    WriteTests --> RunTests: 2. Execute tests
    RunTests --> VerifyFail: Tests must fail
    VerifyFail --> GREEN_Phase: Tests fail ✓
    
    GREEN_Phase --> ImplementComponent: 3. Implement component
    ImplementComponent --> ApplyAccessibility: 4. Apply WCAG 2.1 AA rules
    ApplyAccessibility --> RunTestsAgain: 5. Execute tests
    RunTestsAgain --> TestsPass: All tests pass
    
    TestsPass --> VALIDATE_Phase: Tests pass ✓
    
    VALIDATE_Phase --> RunPreFlight: 6. Run Pre-Flight Checklist
    RunPreFlight --> CheckContrast: Visibility + Touch + States
    CheckContrast --> CheckBrowserDevTools: Use DevTools contrast checker
    CheckBrowserDevTools --> AllChecksPassed: All checks pass
    
    AllChecksPassed --> RunLint: 7. Lint + TypeCheck
    RunLint --> [*]: Component shipped ✓
    
    CheckContrast --> FixViolations: Violations detected
    FixViolations --> ImplementComponent: Apply fixes
    
    note right of RunPreFlight
        Pre-Flight Checklist from ui-testing.md
        Mandatory before marking todo complete
    end note
    
    note right of CheckContrast
        Enforces WCAG 2.1 AA:
        - Contrast ≥ 4.5:1
        - Touch targets ≥ 44px
        - Visible boundaries
        - Focus indicators
    end note
```

Sources: [README.md:319-342](), [skills/ui-testing.md:10-43]()

### Example TDD Execution Log

From [README.md:534-558](), adapted for UI development:

```markdown
## [TODO-042] Add accessible login form

**Status:** in-progress
**Priority:** high
**Estimate:** S

### Acceptance Criteria
- [ ] Email and password inputs with visible labels
- [ ] Submit button meets 44px minimum height
- [ ] Form error states have 4.5:1 contrast
- [ ] Focus indicators visible on all inputs
- [ ] Works with keyboard navigation

### Test Cases
| Input | Expected |
|-------|----------|
| Valid credentials | Form submits |
| Invalid email | Error with sufficient contrast |
| Tab navigation | Focus visible on all elements |

### TDD Execution Log
| Phase | Command | Result |
|-------|---------|--------|
| RED | `npm test -- LoginForm.test.tsx` | 5 tests failed ✓ |
| GREEN | `npm test -- LoginForm.test.tsx` | 5 tests passed ✓ |
| VALIDATE | Pre-Flight Checklist (ui-testing.md) | All checks passed ✓ |
| VALIDATE | `npm run lint && npm test -- --coverage` | Pass, 87% ✓ |
```

Sources: [README.md:534-558]()

---

## Automated Accessibility Checks (Optional)

While the pre-flight checklist is the primary enforcement mechanism, `ui-testing.md` documents optional automated tools for larger projects.

### ESLint Integration

From [skills/ui-testing.md:142-152]():

```bash
npm install -D eslint-plugin-jsx-a11y
```

```json
// .eslintrc
{
  "extends": ["plugin:jsx-a11y/recommended"]
}
```

### Playwright Quick Test

From [skills/ui-testing.md:154-165]():

```typescript
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('no accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

**When to Use Full Testing** ([skills/ui-testing.md:169-177]()):
- Building a component library
- Multiple developers on UI
- Frequent UI changes
- Design system enforcement needed

For solo projects or MVPs, the pre-flight checklist is sufficient.

Sources: [skills/ui-testing.md:140-177]()

---

## Anti-Patterns and Common Mistakes

### Web Anti-Patterns

From [skills/ui-web.md:573-603]():

**Never Do**:
- More than 3 font sizes on a page
- Random spacing values (use 8px grid)
- Pure black (#000) on pure white (#fff)
- Colored text on colored backgrounds without checking contrast
- Animations longer than 500ms for UI elements
- Glassmorphism everywhere
- Removing focus indicators
- Gray text below 4.5:1 contrast
- Tiny click targets (< 44px)

**Common Mistakes**:
```tsx
// ✗ Too many shadows
className="shadow-sm shadow-md shadow-lg" // Pick ONE

// ✗ Inconsistent rounding
className="rounded-sm rounded-lg rounded-2xl" // Use system

// ✗ Competing focal points
// One primary CTA per viewport
```

Sources: [skills/ui-web.md:573-603]()

### Mobile Anti-Patterns

From [skills/ui-mobile.md:883-920]():

**Never Do**:
- Touch targets smaller than 44pt
- Text smaller than 12pt
- Hover states (no hover on mobile)
- Fixed heights that break with large text
- Ignoring safe areas
- Heavy shadows on Android (use elevation)
- White text on light backgrounds without checking contrast
- Non-native animations (JS-driven transforms)
- Ignoring platform conventions (iOS vs Android)

**Common Mistakes**:
```tsx
// ✗ Hardcoded dimensions that break accessibility
style={{ height: 40 }}  // Text might be larger

// ✓ Minimum height with padding
style={{ minHeight: 44, paddingVertical: 12 }}

// ✗ Shadow on Android (won't render)
shadowColor: '#000'

// ✓ Platform-specific
...Platform.select({
  ios: { shadowColor: '#000', ... },
  android: { elevation: 4 },
})
```

Sources: [skills/ui-mobile.md:883-920]()

---

## Quick Reference

### Web Defaults

From [skills/ui-web.md:607-615]():

- Border radius: 12-16px (`rounded-xl` to `rounded-2xl`)
- Shadow: subtle (`shadow-sm` to `shadow-md`)
- Font: Inter, SF Pro, system-ui
- Primary: Near-black or brand color
- Transitions: 200ms ease-out
- Spacing: 8px grid (Tailwind default)

### Mobile Defaults

From [skills/ui-mobile.md:924-932]():

- Touch targets: 44pt minimum
- Font sizes: 12pt min, 17pt body, 34pt large title
- Border radius: 10-14pt (iOS), 12-28pt (Android)
- Spacing: 4/8/16/24/32 grid
- Animations: 200-300ms, native driver
- Shadow: iOS shadowOpacity 0.08-0.15, Android elevation 2-8

### Premium Feel Checklist

Combined from [skills/ui-web.md:617-628]() and [skills/ui-mobile.md:934-946]():

- [ ] All touch targets 44pt/px+
- [ ] Consistent spacing (8px/4pt grid)
- [ ] Platform-appropriate styling
- [ ] Safe area handling
- [ ] Smooth transitions on all interactions
- [ ] Proper loading states
- [ ] Dark mode support
- [ ] Accessibility labels
- [ ] High-quality imagery
- [ ] Micro-interactions on hover/focus

Sources: [skills/ui-web.md:606-628](), [skills/ui-mobile.md:922-946]()

---

# Page: E2E Testing with Playwright

# E2E Testing with Playwright

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/playwright-testing.md](skills/playwright-testing.md)
- [skills/react-web.md](skills/react-web.md)

</details>



## Purpose

This document covers end-to-end testing with Playwright in Claude Bootstrap projects. Playwright provides cross-browser automated testing that validates complete user journeys from the browser perspective. Unlike unit tests that verify individual components, E2E tests verify that all system layers work together correctly.

For component-level testing patterns, see [UI Development and Testing](#5.4). For the overall TDD workflow that E2E tests integrate into, see [TDD Workflow (RED-GREEN-VALIDATE)](#3.2).

**Sources:** [skills/playwright-testing.md:1-10]()

---

## When to Use E2E Tests

E2E tests serve specific purposes in the testing pyramid:

| Test Type | Validates | Speed | When to Use |
|-----------|-----------|-------|-------------|
| Unit | Component logic | Fast (ms) | Business logic, edge cases |
| Integration | API contracts | Medium (100ms) | Service boundaries |
| E2E | User journeys | Slow (seconds) | Critical flows, cross-browser |

**E2E tests are mandatory for:**
- Authentication flows (login, logout, session)
- Payment/checkout processes
- Multi-step wizards
- Dead link detection (every project)
- Critical user paths (signup → activation → first use)

**Sources:** [skills/playwright-testing.md:1-10](), [README.md:423-428]()

---

## Setup and Configuration

### Installation

```bash
# New project
npm init playwright@latest

# Existing project
npm install -D @playwright/test
npx playwright install
```

**Sources:** [skills/playwright-testing.md:14-22]()

### Configuration Structure

The `playwright.config.ts` file defines test execution behavior:

```mermaid
graph TB
    subgraph "Configuration Layers"
        CONFIG["playwright.config.ts"]
        TESTDIR["testDir: './e2e'"]
        USE["use: baseURL, trace, screenshots"]
        PROJECTS["projects: [setup, chromium, firefox, webkit, mobile]"]
        WEBSERVER["webServer: Start dev server"]
    end
    
    subgraph "Test Execution"
        SETUP["Setup Project<br/>auth.setup.ts"]
        CHROME["Chromium Tests<br/>depends on setup"]
        FIREFOX["Firefox Tests<br/>depends on setup"]
        WEBKIT["WebKit Tests<br/>depends on setup"]
    end
    
    CONFIG --> TESTDIR
    CONFIG --> USE
    CONFIG --> PROJECTS
    CONFIG --> WEBSERVER
    
    PROJECTS --> SETUP
    SETUP --> CHROME
    SETUP --> FIREFOX
    SETUP --> WEBKIT
    
    WEBSERVER --> SETUP
```

**Key configuration sections:**

| Section | Purpose | Example |
|---------|---------|---------|
| `testDir` | Test file location | `./e2e` |
| `fullyParallel` | Run tests in parallel | `true` |
| `retries` | Retry flaky tests in CI | `process.env.CI ? 2 : 0` |
| `use.baseURL` | Default navigation URL | `http://localhost:3000` |
| `use.trace` | Record execution traces | `'on-first-retry'` |
| `projects` | Browser configurations | chromium, firefox, webkit, mobile |
| `webServer` | Start app before tests | `npm run dev` |

**Sources:** [skills/playwright-testing.md:24-89]()

### Project Structure

```
project/
├── e2e/
│   ├── fixtures/
│   │   ├── auth.fixture.ts      # Auth state fixtures
│   │   └── test.fixture.ts      # Extended test context
│   ├── pages/
│   │   ├── base.page.ts         # Base Page Object
│   │   ├── login.page.ts        # Login Page Object
│   │   ├── dashboard.page.ts    # Dashboard Page Object
│   │   └── index.ts             # Barrel exports
│   ├── tests/
│   │   ├── auth.spec.ts         # Authentication tests
│   │   ├── dashboard.spec.ts    # Dashboard tests
│   │   └── checkout.spec.ts     # Checkout flow tests
│   ├── utils/
│   │   ├── helpers.ts           # Test utilities
│   │   └── test-data.ts         # Data factories
│   └── auth.setup.ts            # Global auth setup
├── playwright.config.ts
└── .auth/                        # Stored auth state (gitignored)
```

**Sources:** [skills/playwright-testing.md:93-117]()

---

## Locator Strategy

Playwright uses a priority-based locator strategy that mirrors how users interact with the page. This makes tests resilient to implementation changes while catching accessibility issues.

### Locator Priority Order

```mermaid
graph LR
    subgraph "BEST: Role-Based"
        ROLE1["getByRole('button')"]
        ROLE2["getByRole('textbox')"]
        ROLE3["getByRole('link')"]
    end
    
    subgraph "GOOD: User-Facing Text"
        LABEL["getByLabel('Email')"]
        PLACEHOLDER["getByPlaceholder('Enter email')"]
        TEXT["getByText('Welcome')"]
    end
    
    subgraph "GOOD: Test IDs"
        TESTID["getByTestId('submit-btn')"]
    end
    
    subgraph "AVOID: CSS Selectors"
        CSS["locator('.btn-primary')"]
    end
    
    subgraph "NEVER: XPath"
        XPATH["locator('//div[@class]')"]
    end
    
    BEST --> GOOD
    GOOD --> TESTID
    TESTID -.-> |"Last resort"| CSS
    CSS -.-> |"Extremely brittle"| XPATH
```

**Examples:**

```typescript
// ✅ BEST: Role-based (accessible, resilient)
page.getByRole('button', { name: 'Submit' })
page.getByRole('textbox', { name: 'Email' })

// ✅ GOOD: User-facing text
page.getByLabel('Email address')
page.getByPlaceholder('Enter your email')

// ✅ GOOD: Test IDs (stable, explicit)
page.getByTestId('submit-button')

// ⚠️ AVOID: CSS selectors (brittle)
page.locator('.btn-primary')

// ❌ NEVER: XPath (extremely brittle)
page.locator('//div[@class="container"]/button[1]')
```

**Sources:** [skills/playwright-testing.md:119-162]()

---

## Page Object Model

The Page Object Model (POM) encapsulates page structure and interactions into reusable classes. This prevents duplication and makes tests readable.

### Architecture

```mermaid
graph TB
    subgraph "Base Layer"
        BASEPAGE["BasePage<br/>base.page.ts"]
    end
    
    subgraph "Page Objects"
        LOGIN["LoginPage<br/>login.page.ts"]
        DASHBOARD["DashboardPage<br/>dashboard.page.ts"]
        CHECKOUT["CheckoutPage<br/>checkout.page.ts"]
    end
    
    subgraph "Test Specs"
        AUTHSPEC["auth.spec.ts"]
        DASHSPEC["dashboard.spec.ts"]
        CHECKSPEC["checkout.spec.ts"]
    end
    
    subgraph "Page Components"
        LOCATORS["Locators<br/>emailInput, submitButton"]
        ACTIONS["Actions<br/>login(), logout()"]
        ASSERTIONS["Assertions<br/>expectLoggedIn()"]
    end
    
    BASEPAGE --> LOGIN
    BASEPAGE --> DASHBOARD
    BASEPAGE --> CHECKOUT
    
    LOGIN --> LOCATORS
    LOGIN --> ACTIONS
    LOGIN --> ASSERTIONS
    
    LOGIN --> AUTHSPEC
    DASHBOARD --> DASHSPEC
    CHECKOUT --> CHECKSPEC
```

### Base Page Pattern

The `BasePage` class provides shared functionality for all pages:

```typescript
// e2e/pages/base.page.ts
export abstract class BasePage {
  constructor(protected page: Page) {}

  async navigate(path: string = '/') {
    await this.page.goto(path);
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  // Common elements
  get header() {
    return this.page.getByRole('banner');
  }

  get footer() {
    return this.page.getByRole('contentinfo');
  }

  // Common actions
  async clickNavLink(name: string) {
    await this.header.getByRole('link', { name }).click();
  }
}
```

**Sources:** [skills/playwright-testing.md:165-198]()

### Page Implementation

Each page extends `BasePage` and defines its specific locators and actions:

```typescript
// e2e/pages/login.page.ts
export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.navigate('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }

  async expectLoggedIn() {
    await expect(this.page).toHaveURL(/.*dashboard/);
  }
}
```

**Page Object Structure:**

| Component | Purpose | Example |
|-----------|---------|---------|
| `readonly` locators | Define page elements in constructor | `this.emailInput = page.getByLabel('Email')` |
| `goto()` method | Navigate to page | `await this.navigate('/login')` |
| Action methods | Encapsulate interactions | `async login(email, password)` |
| Assertion methods | Verify page state | `async expectLoggedIn()` |

**Sources:** [skills/playwright-testing.md:200-281]()

### Usage in Tests

```typescript
// e2e/tests/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages';

test.describe('Authentication', () => {
  test('successful login redirects to dashboard', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');
    await loginPage.expectLoggedIn();
  });

  test('invalid credentials show error', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login('wrong@example.com', 'wrongpass');
    await loginPage.expectError('Invalid email or password');
  });
});
```

**Sources:** [skills/playwright-testing.md:350-389]()

---

## Authentication

Authentication state management prevents tests from logging in repeatedly. The setup project runs once before all tests and stores authentication state.

### Global Authentication Flow

```mermaid
sequenceDiagram
    participant CI as "CI/CD Trigger"
    participant SETUP as "auth.setup.ts<br/>(setup project)"
    participant APP as "Application"
    participant FILE as ".auth/user.json"
    participant TESTS as "Test Specs<br/>(chromium, firefox, webkit)"

    CI->>SETUP: Run setup project first
    SETUP->>APP: Navigate to /login
    SETUP->>APP: Fill credentials
    SETUP->>APP: Submit form
    APP-->>SETUP: Redirect to /dashboard
    SETUP->>FILE: Save storage state
    Note over FILE: Cookies, localStorage,<br/>sessionStorage
    
    FILE->>TESTS: Load storage state
    Note over TESTS: All tests start<br/>authenticated
    TESTS->>APP: Navigate to protected routes
    APP-->>TESTS: Already logged in
```

### Implementation

**Setup file:**

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  // Go to login page
  await page.goto('/login');

  // Login with test credentials
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Wait for auth to complete
  await expect(page).toHaveURL(/.*dashboard/);

  // Save auth state for reuse
  await page.context().storageState({ path: authFile });
});
```

**Configuration:**

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/user.json',  // Load saved state
      },
      dependencies: ['setup'],  // Run setup first
    },
  ],
});
```

**Tests without auth (public pages):**

```typescript
// e2e/tests/public.spec.ts
test.use({ storageState: { cookies: [], origins: [] } });

test('homepage loads for anonymous users', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
});
```

**Sources:** [skills/playwright-testing.md:284-344]()

---

## Writing Test Patterns

### Basic Test Structure

Tests follow the Arrange-Act-Assert pattern:

```typescript
test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Navigate, clear state, etc.
  });

  test('describes expected behavior', async ({ page }) => {
    // Arrange: Setup test data
    const loginPage = new LoginPage(page);

    // Act: Perform actions
    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');

    // Assert: Verify outcome
    await loginPage.expectLoggedIn();
  });
});
```

**Sources:** [skills/playwright-testing.md:350-389]()

### User Flow Tests

Complex flows test multiple steps in sequence:

```typescript
// e2e/tests/checkout.spec.ts
test('complete purchase flow', async ({ page }) => {
  // 1. Browse products
  await page.goto('/products');
  await page.getByTestId('product-card')
    .filter({ hasText: 'Pro Plan' })
    .getByRole('button', { name: 'Add to cart' })
    .click();

  // 2. View cart
  await page.getByRole('link', { name: 'Cart' }).click();
  await expect(page.getByText('Pro Plan')).toBeVisible();
  await expect(page.getByTestId('cart-total')).toContainText('$29.99');

  // 3. Checkout
  await page.getByRole('button', { name: 'Checkout' }).click();

  // 4. Fill payment (Stripe test card)
  const stripeFrame = page.frameLocator('iframe[name*="stripe"]');
  await stripeFrame.getByPlaceholder('Card number').fill('4242424242424242');
  await stripeFrame.getByPlaceholder('MM / YY').fill('12/30');
  await stripeFrame.getByPlaceholder('CVC').fill('123');

  // 5. Complete purchase
  await page.getByRole('button', { name: 'Pay now' }).click();

  // 6. Verify success
  await expect(page).toHaveURL(/.*success/);
  await expect(page.getByRole('heading', { name: 'Thank you' })).toBeVisible();
});
```

**Sources:** [skills/playwright-testing.md:391-428]()

### Assertions

Playwright assertions auto-wait and retry:

```typescript
// ✅ Web-first assertions (auto-wait)
await expect(page.getByRole('button')).toBeVisible();
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByRole('button')).toHaveText('Submit');
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle(/Dashboard/);

// ❌ Avoid manual waits
await page.waitForTimeout(3000);  // NEVER do this
```

**Common assertions:**

| Category | Assertion | Use Case |
|----------|-----------|----------|
| Visibility | `toBeVisible()`, `toBeHidden()` | Element visibility |
| Text | `toHaveText()`, `toContainText()` | Content verification |
| State | `toBeEnabled()`, `toBeDisabled()`, `toBeChecked()` | Input state |
| URL | `toHaveURL()`, `toHaveTitle()` | Navigation verification |
| Count | `toHaveCount(n)` | List length |

**Sources:** [skills/playwright-testing.md:430-484]()

### Network Mocking

Mock API responses for controlled testing:

```typescript
test('shows error when API fails', async ({ page }) => {
  // Mock API to return error
  await page.route('**/api/users', (route) => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Server error' }),
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Failed to load users')).toBeVisible();
});

test('wait for API call', async ({ page }) => {
  await page.goto('/contact');
  
  // Fill form
  await page.getByLabel('Name').fill('John');
  
  // Wait for API response
  const responsePromise = page.waitForResponse('**/api/contact');
  await page.getByRole('button', { name: 'Send' }).click();
  
  const response = await responsePromise;
  expect(response.status()).toBe(200);
});
```

**Sources:** [skills/playwright-testing.md:486-546]()

---

## Dead Link Detection (REQUIRED)

**Every Claude Bootstrap project MUST include dead link detection tests.** Dead links harm user experience and SEO. These tests run on every deployment to catch broken links before users do.

### Why Dead Link Detection is Mandatory

| Problem | Impact | Solution |
|---------|--------|----------|
| External links break | Users hit 404s, bounce rate increases | Automated link checking |
| Internal routes change | Site navigation breaks | Crawl entire site |
| Images 404 | Visual design fails | Validate image URLs |
| CDN failures | Assets don't load | Check external resources |

### Detection Architecture

```mermaid
graph TB
    subgraph "Test Entry Points"
        PAGES["PAGES_TO_CHECK<br/>['/',''/about'', '/pricing']"]
        CRAWLER["Site Crawler<br/>Discovers all pages"]
    end
    
    subgraph "Link Extraction"
        LOCATOR["page.locator('a[href]')"]
        FILTER["Filter:<br/>- Skip mailto:<br/>- Skip tel:<br/>- Skip anchors #"]
        UNIQUE["Deduplicate URLs"]
    end
    
    subgraph "Link Validation"
        REQUEST["request.get(url)"]
        STATUS["Check status code"]
        SUCCESS["200-399: OK"]
        FAIL["400+: Dead link"]
    end
    
    subgraph "Results"
        REPORT["Report dead links:<br/>url, status, foundOn"]
        BLOCK["Fail test if dead links found"]
    end
    
    PAGES --> LOCATOR
    CRAWLER --> LOCATOR
    LOCATOR --> FILTER
    FILTER --> UNIQUE
    UNIQUE --> REQUEST
    REQUEST --> STATUS
    STATUS --> SUCCESS
    STATUS --> FAIL
    FAIL --> REPORT
    REPORT --> BLOCK
```

### Basic Link Validator

```typescript
// e2e/tests/links.spec.ts
import { test, expect } from '@playwright/test';

const PAGES_TO_CHECK = ['/', '/about', '/pricing', '/blog', '/contact'];

test.describe('Dead Link Detection', () => {
  for (const pagePath of PAGES_TO_CHECK) {
    test(`no dead links on ${pagePath}`, async ({ page, request }) => {
      await page.goto(pagePath);

      // Get all links on the page
      const links = await page.locator('a[href]').all();
      const hrefs = await Promise.all(
        links.map(link => link.getAttribute('href'))
      );

      // Filter to internal and absolute external links
      const uniqueLinks = [...new Set(hrefs.filter(Boolean))] as string[];

      for (const href of uniqueLinks) {
        // Skip mailto, tel, and anchor links
        if (href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('#')) {
          continue;
        }

        // Build full URL
        const url = href.startsWith('http') ? href : new URL(href, page.url()).href;

        // Check link status
        const response = await request.get(url, {
          timeout: 10000,
          ignoreHTTPSErrors: true,
        });

        expect(
          response.ok(),
          `Dead link found on ${pagePath}: ${href} returned ${response.status()}`
        ).toBeTruthy();
      }
    });
  }
});
```

**Sources:** [skills/playwright-testing.md:708-757]()

### Site Crawler

For comprehensive coverage, crawl the entire site and check every discovered link:

```typescript
// e2e/tests/site-links.spec.ts
interface LinkResult {
  url: string;
  status: number;
  foundOn: string;
}

async function checkAllLinks(
  page: Page,
  request: APIRequestContext,
  startUrl: string
): Promise<LinkResult[]> {
  const visited = new Set<string>();
  const results: LinkResult[] = [];
  const toVisit = [startUrl];
  const baseUrl = new URL(startUrl).origin;

  while (toVisit.length > 0) {
    const currentUrl = toVisit.pop()!;
    if (visited.has(currentUrl)) continue;
    visited.add(currentUrl);

    try {
      await page.goto(currentUrl);
      const links = await page.locator('a[href]').all();

      for (const link of links) {
        const href = await link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('mailto:')) {
          continue;
        }

        const fullUrl = href.startsWith('http') ? href : new URL(href, currentUrl).href;

        // Check link
        const response = await request.get(fullUrl, {
          timeout: 10000,
          ignoreHTTPSErrors: true,
        });

        results.push({
          url: fullUrl,
          status: response.status(),
          foundOn: currentUrl,
        });

        // Add internal links to queue
        if (fullUrl.startsWith(baseUrl) && !visited.has(fullUrl)) {
          toVisit.push(fullUrl);
        }
      }
    } catch (error) {
      results.push({
        url: currentUrl,
        status: 0,
        foundOn: 'navigation',
      });
    }
  }

  return results;
}

test('no dead links on entire site', async ({ page, request, baseURL }) => {
  const results = await checkAllLinks(page, request, baseURL!);
  const deadLinks = results.filter(r => r.status >= 400 || r.status === 0);

  if (deadLinks.length > 0) {
    console.error('Dead links found:');
    deadLinks.forEach(link => {
      console.error(`  ${link.url} (${link.status}) - found on ${link.foundOn}`);
    });
  }

  expect(deadLinks, `Found ${deadLinks.length} dead links`).toHaveLength(0);
});
```

**Sources:** [skills/playwright-testing.md:759-840]()

### Image Link Validation

Verify that all images load and are actually images:

```typescript
// e2e/tests/images.spec.ts
test('no broken images on homepage', async ({ page, request }) => {
  await page.goto('/');

  const images = await page.locator('img[src]').all();

  for (const img of images) {
    const src = await img.getAttribute('src');
    if (!src) continue;

    const url = src.startsWith('http') ? src : new URL(src, page.url()).href;

    // Skip data URLs
    if (url.startsWith('data:')) continue;

    const response = await request.get(url);
    expect(response.ok(), `Broken image: ${src}`).toBeTruthy();

    // Verify it's actually an image
    const contentType = response.headers()['content-type'];
    expect(
      contentType?.startsWith('image/'),
      `${src} is not an image (${contentType})`
    ).toBeTruthy();
  }
});
```

**Sources:** [skills/playwright-testing.md:842-876]()

---

## CI/CD Integration

Playwright integrates into the quality gates enforcement pipeline. Tests run automatically on every push and pull request.

### CI/CD Pipeline Position

```mermaid
graph LR
    subgraph "Phase 3: Quality Verification"
        PRECOMMIT["Pre-commit Hooks<br/>Lint + Type + Unit"]
        REVIEW["/code-review<br/>Pre-push"]
    end
    
    subgraph "Phase 4: CI/CD Validation"
        TRIGGER["GitHub Actions Trigger"]
        UNIT["Unit Tests<br/>80% coverage"]
        E2E["E2E Tests<br/>Playwright"]
        LINKCHECK["Dead Link Check<br/>playwright links.spec.ts"]
        SECURITY["Security Scan<br/>TruffleHog"]
    end
    
    subgraph "Phase 5: Deployment"
        DEPLOY["Deploy to Vercel"]
        PROD["Production"]
    end
    
    PRECOMMIT --> REVIEW
    REVIEW --> TRIGGER
    TRIGGER --> UNIT
    TRIGGER --> E2E
    TRIGGER --> LINKCHECK
    TRIGGER --> SECURITY
    
    UNIT --> DEPLOY
    E2E --> DEPLOY
    LINKCHECK --> DEPLOY
    SECURITY --> DEPLOY
    
    DEPLOY --> PROD
```

### GitHub Actions Workflow

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: Run E2E tests
        run: npx playwright test --project=chromium
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          TEST_USER_EMAIL: ${{ secrets.TEST_USER_EMAIL }}
          TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
```

**Sources:** [skills/playwright-testing.md:567-611]()

### Scheduled Link Checking

Run dead link detection weekly to catch external link rot:

```yaml
# .github/workflows/link-check.yml
name: Link Check

on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday
  push:
    branches: [main]

jobs:
  link-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install chromium
      - run: npx playwright test e2e/tests/links.spec.ts --project=chromium
        env:
          BASE_URL: ${{ secrets.PRODUCTION_URL }}
```

**Sources:** [skills/playwright-testing.md:878-904]()

### Running Tests Locally

| Command | Purpose |
|---------|---------|
| `npx playwright test` | Run all tests |
| `npx playwright test --headed` | Run with visible browser |
| `npx playwright test --project=chromium` | Run specific browser |
| `npx playwright test --grep @critical` | Run tagged tests |
| `npx playwright test --debug` | Debug mode with inspector |
| `npx playwright show-report` | View HTML report |
| `npx playwright show-trace trace.zip` | View execution trace |
| `npx playwright codegen localhost:3000` | Generate test code |

**Sources:** [skills/playwright-testing.md:613-636]()

---

## TDD Integration

E2E tests integrate into the RED-GREEN-VALIDATE workflow as validation gates:

### TDD Phase Mapping

```mermaid
graph TB
    subgraph "RED Phase"
        WRITETEST["Write E2E test<br/>Define user journey"]
        RUNTEST1["Run test<br/>npx playwright test"]
        FAIL["Test FAILS<br/>Feature not implemented"]
    end
    
    subgraph "GREEN Phase"
        IMPLEMENT["Implement feature<br/>Backend + Frontend"]
        RUNTEST2["Run test again"]
        PASS["Test PASSES<br/>Journey works"]
    end
    
    subgraph "VALIDATE Phase"
        LINT["Lint + Type Check"]
        UNIT["Unit Tests<br/>80% coverage"]
        E2EALL["All E2E Tests"]
        LINKS["Dead Link Check"]
    end
    
    subgraph "COMPLETE"
        COMMIT["Commit<br/>Mark todo complete"]
    end
    
    WRITETEST --> RUNTEST1
    RUNTEST1 --> FAIL
    FAIL --> IMPLEMENT
    IMPLEMENT --> RUNTEST2
    RUNTEST2 --> PASS
    PASS --> LINT
    LINT --> UNIT
    UNIT --> E2EALL
    E2EALL --> LINKS
    LINKS --> COMMIT
```

**E2E tests in the TDD workflow:**

| Phase | E2E Test Role | Example |
|-------|---------------|---------|
| RED | Define acceptance criteria | Write checkout flow test that fails |
| GREEN | Verify feature works end-to-end | Test passes after implementation |
| VALIDATE | Regression prevention | Full suite confirms no breakage |

**When to write E2E tests:**

- **Before implementation:** For new critical user journeys (checkout, signup)
- **After bug fix:** When bug affected multi-step flows
- **For dead links:** Always, on every page

**Sources:** [README.md:321-342](), [skills/playwright-testing.md:1-10]()

---

## Anti-Patterns

Avoid these common E2E testing mistakes:

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoded waits | `await page.waitForTimeout(3000)` | Use auto-waiting assertions |
| CSS/XPath selectors | Brittle, breaks on styling changes | Use role/text/testid locators |
| Testing third-party sites | Unreliable, slow | Mock external dependencies |
| Shared state between tests | Tests depend on execution order | Each test must be isolated |
| Missing awaits | Race conditions, flaky tests | Use ESLint `no-floating-promises` |
| Flaky time-based tests | Fail randomly | Mock dates/times |
| Testing implementation details | Couples tests to code structure | Test user-visible behavior |
| Huge test files | Hard to maintain | Split by feature/page |
| No error messages | Hard to debug failures | Include descriptive expect messages |

**Sources:** [skills/playwright-testing.md:907-918]()

---

## Quick Reference

### Essential Commands

```bash
# Install
npm init playwright@latest

# Run tests
npx playwright test                    # All tests
npx playwright test --headed           # Visible browser
npx playwright test --project=chromium # Specific browser
npx playwright test --grep @smoke      # Tagged tests

# Debug
npx playwright test --debug            # Debug mode
npx playwright show-report             # HTML report
npx playwright show-trace trace.zip    # Trace viewer

# Generate tests
npx playwright codegen localhost:3000  # Record actions
```

### Package.json Scripts

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:report": "playwright show-report",
    "test:e2e:codegen": "playwright codegen"
  }
}
```

**Sources:** [skills/playwright-testing.md:920-954]()

---

# Page: AI and Agentic Development

# AI and Agentic Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/agentic-development.md](skills/agentic-development.md)

</details>



## Purpose and Scope

This document covers skills and patterns for building autonomous AI agents that perform multi-step tasks using tools and reasoning. It focuses on two primary frameworks: **Pydantic AI** (Python default) and **Claude Agent SDK** (Node.js default). These agents follow an Explore-Plan-Execute-Verify workflow with built-in guardrails and structured output validation.

For general LLM integration patterns and testing approaches, see [LLM Patterns](#5.7). For available model specifications and capabilities, see [AI Models Reference](#5.8).

**Sources:** [skills/agentic-development.md:1-8]()

---

## Framework Selection by Language

Claude Bootstrap defaults to framework choices optimized for type safety and production readiness:

| Language/Framework | Default Framework | Key Benefits |
|-------------------|------------------|--------------|
| **Python** | Pydantic AI | Type-safe results, Pydantic validation, multi-model support, production-ready |
| **Node.js / Next.js** | Claude Agent SDK | Official Anthropic SDK, native tool support, multi-agent coordination, streaming |

### Python: Pydantic AI Architecture

The Pydantic AI framework provides type-safe agent construction with automatic validation:

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class SearchResult(BaseModel):
    title: str
    url: str
    summary: str

agent = Agent(
    'claude-sonnet-4-20250514',
    result_type=list[SearchResult],
    system_prompt='You are a research assistant.',
)

result = await agent.run('Find articles about AI agents')
for item in result.data:
    print(f"{item.title}: {item.url}")
```

### Node.js: Claude SDK Agentic Loop

The Claude SDK implements the agentic pattern through explicit tool handling:

```typescript
const tools: Anthropic.Tool[] = [{
  name: "web_search",
  description: "Search the web for information",
  input_schema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Search query" },
    },
    required: ["query"],
  },
}];

while (true) {
  const response = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 4096,
    tools,
    messages,
  });

  if (response.stop_reason === "tool_use") {
    // Execute tool and continue loop
  } else {
    return response.content;
  }
}
```

**Sources:** [skills/agentic-development.md:11-93]()

---

## Agent Architecture and Project Structure

### Agent Component Model

```mermaid
graph TB
    subgraph AgentCore["Agent (OpenAI Model)"]
        Brain["Model<br/>(LLM Reasoning)"]
        Arms["Tools<br/>(APIs, Functions, External Systems)"]
        Rules["Instructions<br/>(System Prompts, Boundaries)"]
    end
    
    subgraph ProjectStructure["Project Organization"]
        AgentsDir["agents/"]
        Orchestrator["orchestrator.ts/py<br/>Main coordinator"]
        Specialized["specialized/<br/>researcher.ts, coder.ts, reviewer.ts"]
        BaseAgent["base.ts/py<br/>Shared interface"]
    end
    
    subgraph ToolsLayer["Tools Layer"]
        ToolDefs["definitions/<br/>Tool schemas (Zod/Pydantic)"]
        ToolImpl["implementations/<br/>Tool logic"]
        Registry["registry.ts/py<br/>Tool discovery"]
    end
    
    subgraph MemoryLayer["Memory & State"]
        ConvMem["conversation.ts/py<br/>Short-term context"]
        PersistMem["persistent.ts/py<br/>Long-term storage"]
    end
    
    Brain --> Arms
    Brain --> Rules
    
    Orchestrator --> Specialized
    Specialized --> BaseAgent
    
    Arms --> ToolDefs
    ToolDefs --> ToolImpl
    ToolImpl --> Registry
    
    Brain --> ConvMem
    Brain --> PersistMem
```

**Directory Structure**

The recommended project layout separates concerns by agent type, tool definitions, and memory management:

```
project/
├── src/
│   ├── agents/
│   │   ├── orchestrator.ts        # Main agent coordinator
│   │   ├── specialized/           # Task-specific agents
│   │   │   ├── researcher.ts      # Research agent
│   │   │   ├── coder.ts           # Coding agent
│   │   │   └── reviewer.ts        # Review agent
│   │   └── base.ts                # Shared agent interface
│   ├── tools/
│   │   ├── definitions/           # Tool schemas
│   │   ├── implementations/       # Tool logic
│   │   └── registry.ts            # Tool discovery
│   ├── prompts/
│   │   ├── system/                # Agent instructions
│   │   └── templates/             # Task templates
│   └── memory/
│       ├── conversation.ts        # Short-term context
│       └── persistent.ts          # Long-term storage
├── tests/
│   ├── agents/                    # Agent behavior tests
│   ├── tools/                     # Tool unit tests
│   └── evals/                     # End-to-end evaluations
```

**Sources:** [skills/agentic-development.md:106-154]()

---

## Explore-Plan-Execute-Verify Workflow

The core agent workflow enforces planning before action and verification after execution. This pattern prevents premature execution and ensures quality at each step.

### Workflow State Diagram

```mermaid
stateDiagram-v2
    [*] --> Explore: Task received
    
    Explore --> Plan: "Context gathered"
    
    state Explore {
        [*] --> searchCodebase
        searchCodebase --> analyzePatterns
        analyzePatterns --> identifyDependencies
        identifyDependencies --> [*]
    }
    
    Plan --> Execute: "Plan validated"
    
    state Plan {
        [*] --> createSteps
        createSteps --> defineSuccessCriteria
        defineSuccessCriteria --> identifyRisks
        identifyRisks --> [*]
    }
    
    Execute --> Verify: "Step completed"
    
    state Execute {
        [*] --> executeStep
        executeStep --> checkResult
        checkResult --> selfCorrect: Failed
        selfCorrect --> executeStep
        checkResult --> [*]: Success
    }
    
    Verify --> Execute: "More steps"
    Verify --> [*]: "All complete"
    
    state Verify {
        [*] --> runTests
        runTests --> llmVerify
        llmVerify --> [*]
    }
```

### Explore Phase Implementation

The explore phase gathers context before taking action. This prevents blind execution and ensures informed decisions.

```typescript
// agents/base.ts
async function explore(task: Task): Promise<Context> {
  const relevantFiles = await agent.searchCodebase(task.query);
  const existingPatterns = await agent.analyzePatterns(relevantFiles);
  const dependencies = await agent.identifyDependencies(task);

  return { relevantFiles, existingPatterns, dependencies };
}
```

**Key Functions:**
- `searchCodebase(query: string)`: Locate relevant files using semantic search
- `analyzePatterns(files: File[])`: Identify existing code patterns
- `identifyDependencies(task: Task)`: Map task dependencies

### Plan Phase Implementation

Planning creates explicit, verifiable steps with success criteria. The LLM must output structured plans before execution.

```typescript
// agents/base.ts
async function plan(task: Task, context: Context): Promise<Plan> {
  const prompt = `
    Task: ${task.description}
    Context: ${JSON.stringify(context)}

    Create a step-by-step plan. For each step:
    1. What action to take
    2. What tools to use
    3. How to verify success
    4. What could go wrong

    Output JSON with steps array.
  `;

  return await llmCall({ prompt, schema: PlanSchema });
}
```

**Key Schemas:**
- `PlanSchema`: Zod/Pydantic schema defining plan structure
- `StepSchema`: Individual step with action, tools, verification, risks

### Execute Phase Implementation

Execution proceeds incrementally with verification after each step. Failed steps trigger self-correction or escalation.

```typescript
// agents/base.ts
async function execute(plan: Plan): Promise<Result[]> {
  const results: Result[] = [];

  for (const step of plan.steps) {
    const result = await executeStep(step);

    if (!await verify(step, result)) {
      const corrected = await selfCorrect(step, result);
      if (!corrected.success) {
        return handleFailure(step, results);
      }
    }

    results.push(result);
  }

  return results;
}
```

### Verify Phase Implementation

Independent verification prevents overfitting to immediate results. Tests and LLM validation both run.

```typescript
// agents/base.ts
async function verify(step: Step, result: Result): Promise<boolean> {
  // Run tests if available
  if (step.testCommand) {
    const testResult = await runCommand(step.testCommand);
    if (!testResult.success) return false;
  }

  // Use LLM to verify against criteria
  const verification = await llmCall({
    prompt: `
      Step: ${step.description}
      Expected: ${step.successCriteria}
      Actual: ${JSON.stringify(result)}

      Does the result satisfy the success criteria?
      Respond with { "passes": boolean, "reasoning": string }
    `,
    schema: VerificationSchema
  });

  return verification.passes;
}
```

**Sources:** [skills/agentic-development.md:156-243]()

---

## Tool Design Patterns

Tools are the agent's interface to external systems. Proper tool design includes schemas, risk levels, and confirmation requirements.

### Tool Definition to Implementation Flow

```mermaid
graph LR
    subgraph ToolDef["Tool Definition"]
        ReadFileTool["ReadFileTool<br/>name: 'read_file'<br/>riskLevel: 'low'"]
        WriteFileTool["WriteFileTool<br/>name: 'write_file'<br/>riskLevel: 'medium'<br/>requiresConfirmation: true"]
    end
    
    subgraph Schema["Schema Layer"]
        ReadParams["z.object()<br/>path, startLine, endLine"]
        WriteParams["z.object()<br/>path, content"]
    end
    
    subgraph Impl["Implementation"]
        readFile["async readFile()<br/>fs.readFile()<br/>returns ToolResult"]
        writeFile["async writeFile()<br/>fs.writeFile()<br/>returns ToolResult"]
    end
    
    subgraph Registry["Registry"]
        toolRegistry["toolRegistry.register()<br/>Maps tool names to handlers"]
    end
    
    ReadFileTool --> ReadParams
    WriteFileTool --> WriteParams
    
    ReadParams --> readFile
    WriteParams --> writeFile
    
    readFile --> toolRegistry
    writeFile --> toolRegistry
```

### Tool Definition Pattern

Tool definitions specify schemas, risk levels, and confirmation requirements:

```typescript
// tools/definitions/file-operations.ts
import { z } from 'zod';

export const ReadFileTool = {
  name: 'read_file',
  description: 'Read contents of a file. Use before modifying any file.',
  parameters: z.object({
    path: z.string().describe('Absolute path to the file'),
    startLine: z.number().optional().describe('Start line (1-indexed)'),
    endLine: z.number().optional().describe('End line (1-indexed)'),
  }),
  riskLevel: 'low' as const,
};

export const WriteFileTool = {
  name: 'write_file',
  description: 'Write content to a file. Always read first to understand context.',
  parameters: z.object({
    path: z.string().describe('Absolute path to the file'),
    content: z.string().describe('Complete file content'),
  }),
  riskLevel: 'medium' as const,
  requiresConfirmation: true,
};
```

### Tool Implementation Pattern

Implementations return structured `ToolResult` objects with success/error states:

```typescript
// tools/implementations/file-operations.ts
export async function readFile(
  params: z.infer<typeof ReadFileTool.parameters>
): Promise<ToolResult> {
  try {
    const content = await fs.readFile(params.path, 'utf-8');
    const lines = content.split('\n');

    const start = (params.startLine ?? 1) - 1;
    const end = params.endLine ?? lines.length;

    return {
      success: true,
      data: lines.slice(start, end).join('\n'),
      metadata: { totalLines: lines.length }
    };
  } catch (error) {
    return {
      success: false,
      error: `Failed to read file: ${error.message}`
    };
  }
}
```

### Risk Levels and Confirmation

Tools categorized by risk level determine whether human approval is required:

| Risk Level | Examples | Requires Confirmation? | Action |
|-----------|----------|----------------------|--------|
| `low` | `read_file`, `web_search` | No | Execute immediately |
| `medium` | `write_file`, `database_query` | Optional | Request approval for sensitive contexts |
| `high` | `delete_file`, `execute_command` | Yes | Always require human approval |

**Sources:** [skills/agentic-development.md:247-319]()

---

## Multi-Agent Coordination Patterns

Multiple agents enable specialization but add complexity. Use single agents by default and add multi-agent patterns only when needed.

### Multi-Agent Pattern Types

```mermaid
graph TB
    subgraph SingleAgent["Single Agent (Default)"]
        SA["Agent<br/>General purpose<br/>Multiple tools"]
    end
    
    subgraph AgentAsTool["Agent-as-Tool Pattern"]
        MainAgent["Main Agent"]
        ResearchTool["research_topic tool"]
        ResearchAgent["Research Agent<br/>(Called as tool)"]
        
        MainAgent --> ResearchTool
        ResearchTool --> ResearchAgent
    end
    
    subgraph HandoffPattern["Handoff Pattern"]
        CustomerService["Customer Service Agent"]
        TransferTool["transfer_to_billing tool"]
        BillingAgent["Billing Agent<br/>(Receives handoff)"]
        
        CustomerService --> TransferTool
        TransferTool --> BillingAgent
    end
    
    subgraph Orchestrator["Orchestrator Pattern"]
        OrchestratorAgent["Orchestrator"]
        PlannerAgent["Planner"]
        ExecutorAgent["Executor"]
        ReviewerAgent["Reviewer"]
        
        OrchestratorAgent --> PlannerAgent
        OrchestratorAgent --> ExecutorAgent
        OrchestratorAgent --> ReviewerAgent
    end
```

### Agent-as-Tool Pattern

Specialized agents exposed as callable tools to a main agent:

```typescript
// agents/specialized/researcher.ts
const researchAgent = createAgent({
  name: 'researcher',
  instructions: 'You research topics and return structured findings.',
  tools: [webSearchTool, documentReadTool],
});

// agents/orchestrator.ts
const mainAgent = createAgent({
  tools: [
    {
      type: 'function',
      function: {
        name: 'research_topic',
        description: 'Delegate research to specialized agent',
        parameters: ResearchQuerySchema,
        handler: async (query) => researchAgent.run(query),
      },
    },
  ],
});
```

**Key Functions:**
- `createAgent(config)`: Initialize agent with tools and instructions
- `researchAgent.run(query)`: Execute research agent as tool
- `ResearchQuerySchema`: Zod schema for research parameters

### Handoff Pattern

One-way transfer between agents with context preservation:

```typescript
// agents/customer-service.ts
const customerServiceAgent = createAgent({
  tools: [
    {
      name: 'transfer_to_billing',
      description: 'Transfer to billing specialist for payment issues',
      handler: async (context) => {
        return { handoff: 'billing_agent', context };
      },
    },
  ],
});
```

### Pydantic AI Multi-Agent Orchestration

Python multi-agent coordination using Pydantic AI:

```python
from pydantic_ai import Agent

# Specialized agents
planner = Agent('claude-sonnet-4-20250514', system_prompt='Create detailed plans.')
executor = Agent('claude-sonnet-4-20250514', system_prompt='Execute tasks precisely.')
reviewer = Agent('claude-sonnet-4-20250514', system_prompt='Review and verify work.')

async def orchestrate(task: str):
    # 1. Plan
    plan = await planner.run(f"Create a plan for: {task}")

    # 2. Execute each step
    results = []
    for step in plan.data.steps:
        result = await executor.run(f"Execute: {step}")
        results.append(result.data)

    # 3. Review
    review = await reviewer.run(
        f"Review the results:\nTask: {task}\nResults: {results}"
    )

    return review.data
```

**When to Use Multiple Agents:**
- Separate task domains with non-overlapping tools
- Different authorization levels needed
- Complex workflows with clear handoff points
- Parallel execution of independent subtasks

**Sources:** [skills/agentic-development.md:321-373](), [skills/agentic-development.md:682-707]()

---

## Memory and State Management

Agents maintain state across tool calls and sessions through conversation memory and persistent storage.

### Memory Architecture

```mermaid
graph TB
    subgraph ConversationMem["Conversation Memory (Short-term)"]
        Messages["messages: Message[]"]
        MaxTokens["maxTokens: number"]
        AddMsg["add(message: Message)"]
        GetContext["getContext(): Message[]"]
        Summarize["summarize(): Promise<string>"]
    end
    
    subgraph AgentState["Agent State"]
        ThoughtSig["thoughtSignature<br/>(Encrypted reasoning state)"]
        ConvId["conversationId<br/>(Shared memory reference)"]
        CurrentPlan["currentPlan: Plan"]
        CompletedSteps["completedSteps: Step[]"]
    end
    
    subgraph PersistentMem["Persistent Memory (Long-term)"]
        Store["store(key, value): Promise<void>"]
        Retrieve["retrieve(key): Promise<any>"]
        Search["search(query, limit): Promise<Memory[]>"]
    end
    
    AgentState --> Messages
    AgentState --> ThoughtSig
    
    Messages --> AddMsg
    AddMsg --> GetContext
    GetContext --> Summarize
    
    AgentState --> CurrentPlan
    CurrentPlan --> CompletedSteps
    
    CompletedSteps --> Store
    Store --> PersistentMem
    PersistentMem --> Search
```

### Conversation Memory Interface

Short-term memory for active agent sessions:

```typescript
// memory/conversation.ts
interface ConversationMemory {
  messages: Message[];
  maxTokens: number;

  add(message: Message): void;
  getContext(): Message[];
  summarize(): Promise<string>;
}
```

### Agent State Interface

State preserved across tool calls, especially for reasoning models:

```typescript
// agents/base.ts
interface AgentState {
  thoughtSignature?: string;  // Encrypted reasoning state (Gemini)
  conversationId: string;     // For shared memory
  currentPlan?: Plan;
  completedSteps: Step[];
}
```

**Key Properties:**
- `thoughtSignature`: Required for Gemini function calling with reasoning preserved
- `conversationId`: Links messages across sessions
- `currentPlan`: Active execution plan
- `completedSteps`: Audit trail of completed actions

### Persistent Memory Interface

Long-term storage with semantic search:

```typescript
// memory/persistent.ts
interface PersistentMemory {
  // Store learnings across sessions
  store(key: string, value: any): Promise<void>;
  retrieve(key: string): Promise<any>;

  // Semantic search over past interactions
  search(query: string, limit: number): Promise<Memory[]>;
}
```

**Sources:** [skills/agentic-development.md:377-412]()

---

## Guardrails and Safety Mechanisms

Multi-layer protection prevents unsafe agent behavior through input validation, tool risk assessment, and human-in-the-loop approvals.

### Guardrail Execution Flow

```mermaid
graph TB
    Input["User Input"] --> InputCheck["inputClassifier()<br/>Check input safety"]
    
    InputCheck --> Blocked1["Blocked:<br/>Unsafe input"]
    InputCheck --> ToolMonitor["Execute with<br/>beforeTool() hooks"]
    
    ToolMonitor --> RiskCheck["Check tool.riskLevel"]
    
    RiskCheck --> Low["low → Execute"]
    RiskCheck --> Medium["medium → Execute with logging"]
    RiskCheck --> High["high → requestHumanApproval()"]
    
    High --> Denied["Approval denied"]
    High --> Execute["Approval granted<br/>Execute tool"]
    
    Low --> Execute
    Medium --> Execute
    
    Execute --> OutputCheck["outputValidator()<br/>Check output safety"]
    
    OutputCheck --> Blocked2["Blocked:<br/>Unsafe output"]
    OutputCheck --> Result["Return result"]
    
    Blocked1 --> End["End"]
    Denied --> End
    Blocked2 --> End
    Result --> End["End"]
```

### Guardrail Configuration

The `GuardrailConfig` interface defines multi-layer protection:

```typescript
// guards/index.ts
interface GuardrailConfig {
  // Input validation
  inputClassifier: (input: string) => Promise<SafetyResult>;

  // Output validation
  outputValidator: (output: string) => Promise<SafetyResult>;

  // Tool risk assessment
  toolRiskLevels: Record<string, 'low' | 'medium' | 'high'>;

  // Actions requiring human approval
  humanInTheLoop: string[];
}
```

### Execution with Guardrails

The `executeWithGuardrails` function wraps agent execution with safety checks:

```typescript
// guards/index.ts
async function executeWithGuardrails(
  agent: Agent,
  input: string,
  config: GuardrailConfig
): Promise<Result> {
  // 1. Check input safety
  const inputCheck = await config.inputClassifier(input);
  if (!inputCheck.safe) {
    return { blocked: true, reason: inputCheck.reason };
  }

  // 2. Execute with tool monitoring
  const result = await agent.run(input, {
    beforeTool: async (tool, params) => {
      const risk = config.toolRiskLevels[tool.name];
      if (risk === 'high' || config.humanInTheLoop.includes(tool.name)) {
        return await requestHumanApproval(tool, params);
      }
      return { approved: true };
    },
  });

  // 3. Validate output
  const outputCheck = await config.outputValidator(result.output);
  if (!outputCheck.safe) {
    return { blocked: true, reason: outputCheck.reason };
  }

  return result;
}
```

### Scope Enforcement

System prompts define hard boundaries for agent behavior:

```typescript
const agentInstructions = `
You are a customer service agent for Acme Corp.

SCOPE BOUNDARIES (non-negotiable):
- Only answer questions about Acme products and services
- Never provide legal, medical, or financial advice
- Never access or modify data outside your authorized scope
- If a request is out of scope, politely decline and explain why

If you cannot complete a task within scope, notify the user
and request explicit approval before proceeding.
`;
```

**Sources:** [skills/agentic-development.md:415-481]()

---

## Testing Agent Behavior

Agent testing spans three levels: unit tests for tools, behavior tests for agent decisions, and evaluation tests for accuracy.

### Test Pyramid for Agents

```mermaid
graph TB
    subgraph EvaluationTests["Evaluation Tests (Nightly)"]
        Evals["End-to-end task completion<br/>loadTestCases()<br/>Accuracy validation"]
    end
    
    subgraph BehaviorTests["Behavior Tests"]
        Planning["runWithTrace()<br/>Verify planning before execution"]
        ToolOrder["Check tool call sequence<br/>Read before write"]
        SelfCorrect["Verify self-correction<br/>Error recovery"]
    end
    
    subgraph UnitTests["Unit Tests (Fast)"]
        ToolUnit["Tool implementations<br/>readFile(), writeFile()"]
        SchemaValid["Schema validation<br/>Zod/Pydantic"]
        ErrorCases["Error handling<br/>Missing files, permissions"]
    end
    
    EvaluationTests --> BehaviorTests
    BehaviorTests --> UnitTests
```

### Unit Tests for Tools

Fast tests validating individual tool implementations:

```typescript
// tests/tools/file-operations.test.ts
describe('readFile tool', () => {
  it('reads file content correctly', async () => {
    const result = await readFile({ path: '/test/file.txt' });
    expect(result.success).toBe(true);
    expect(result.data).toContain('expected content');
  });

  it('handles missing files gracefully', async () => {
    const result = await readFile({ path: '/nonexistent.txt' });
    expect(result.success).toBe(false);
    expect(result.error).toContain('Failed to read file');
  });
});
```

### Behavior Tests for Agent Decisions

Tests validating agent decision-making patterns:

```typescript
// tests/agents/planning.test.ts
describe('agent planning', () => {
  it('creates plan before executing file modifications', async () => {
    const trace = await agent.runWithTrace('Refactor the auth module');

    // Verify planning happened first
    const firstToolCall = trace.toolCalls[0];
    expect(firstToolCall.name).toBe('read_file');

    // Verify no writes without reads
    const writeIndex = trace.toolCalls.findIndex(t => t.name === 'write_file');
    const readIndex = trace.toolCalls.findIndex(t => t.name === 'read_file');
    expect(readIndex).toBeLessThan(writeIndex);
  });
});
```

**Key Functions:**
- `agent.runWithTrace(prompt)`: Execute with detailed trace of tool calls
- `trace.toolCalls`: Array of tools called with parameters
- `findIndex()`: Verify execution order

### Evaluation Tests

Long-running accuracy tests using predefined test cases:

```typescript
// tests/evals/coding-tasks.test.ts
describe('Agent Accuracy (Eval)', () => {
  const testCases = loadTestCases('./evals/coding-tasks.json');

  it.each(testCases)('completes $name correctly', async (testCase) => {
    const result = await agent.run(testCase.input);

    // Verify against expected outcomes
    expect(result.filesModified).toEqual(testCase.expectedFiles);
    expect(await runTests(testCase.testCommand)).toBe(true);
  }, 120000); // 2 minute timeout
});
```

### Pydantic AI Testing with TestModel

Mock model for deterministic agent testing:

```python
# tests/test_agents.py
import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

@pytest.fixture
def test_agent():
    return Agent(
        TestModel(),  # Mock model for testing
        result_type=str,
    )

async def test_agent_response(test_agent):
    result = await test_agent.run('Test prompt')
    assert result.data is not None

# Test with specific responses
async def test_with_mock_response():
    model = TestModel()
    model.seed_response('Expected output')

    agent = Agent(model)
    result = await agent.run('Any prompt')
    assert result.data == 'Expected output'
```

**Key Classes:**
- `TestModel`: Mock model with predictable responses
- `seed_response(output)`: Set expected output for testing

**Sources:** [skills/agentic-development.md:530-575](), [skills/agentic-development.md:726-750]()

---

## Model Selection and Configuration

Different models optimize for different agent tasks. Select based on complexity, latency requirements, and reasoning depth.

### Model Selection Matrix

| Task Complexity | Recommended Model | Use Case |
|----------------|-------------------|----------|
| Simple, fast | `gpt-5-mini`, `claude-haiku` | Quick queries, low latency tasks |
| General purpose | `gpt-4.1`, `claude-sonnet` | Standard agent operations |
| Complex reasoning | `o4-mini`, `claude-opus` | Multi-step planning, complex logic |
| Deep planning | `gpt-5 + reasoning`, `ultrathink` | Research, strategic planning |

### Claude Thinking Modes

Claude supports extended thinking through prompt keywords:

```typescript
// agents/orchestrator.ts
const thinkingLevels = {
  'think': 'standard analysis',
  'think hard': 'deeper reasoning',
  'think harder': 'extensive analysis',
  'ultrathink': 'maximum reasoning budget',
};

const prompt = `
Think hard about this problem before proposing a solution.

Task: ${task.description}
`;
```

**Thinking Triggers:**
- `"think"` → Standard analysis
- `"think hard"` → Deeper reasoning
- `"think harder"` → Extensive analysis
- `"ultrathink"` → Maximum reasoning

### Gemini Configuration

Gemini requires specific configuration for reasoning and function calling:

```typescript
// agents/gemini-agent.ts
const response = await gemini.generate({
  model: 'gemini-3',
  thinking_level: 'high',  // For complex planning
  temperature: 1.0,        // Keep at 1.0 for reasoning engine
});

// Preserve thought state across tool calls (REQUIRED)
const nextResponse = await gemini.generate({
  thoughtSignature: response.thoughtSignature,  // Pass back for function calling
  // ... rest of params
});
```

**Critical Settings:**
- `thinking_level`: `'high'` | `'low'` - Controls reasoning depth
- `temperature`: Always `1.0` for reasoning models
- `thoughtSignature`: **Must** pass back for function calling to preserve reasoning state

**Sources:** [skills/agentic-development.md:485-527]()

---

## Pydantic AI Implementation Patterns

Python projects default to Pydantic AI for type-safe agent development with automatic validation.

### Agent with Typed Dependencies

Dependencies inject context and services into tools:

```python
# src/agents/researcher.py
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from httpx import AsyncClient

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

class ResearchDeps(BaseModel):
    http_client: AsyncClient
    api_key: str

research_agent = Agent(
    'claude-sonnet-4-20250514',
    deps_type=ResearchDeps,
    result_type=list[SearchResult],
    system_prompt='You are a research assistant. Use tools to find information.',
)

@research_agent.tool
async def web_search(ctx: RunContext[ResearchDeps], query: str) -> list[dict]:
    """Search the web for information."""
    response = await ctx.deps.http_client.get(
        'https://api.search.com/search',
        params={'q': query},
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    return response.json()['results']
```

**Key Classes:**
- `Agent(model, deps_type, result_type, system_prompt)`: Initialize agent
- `RunContext[ResearchDeps]`: Type-safe dependency injection
- `@research_agent.tool`: Decorator for tool registration

### Structured Output with Validation

Pydantic models provide automatic validation:

```python
# src/models/schemas.py
from pydantic import BaseModel, Field
from pydantic_ai import Agent

class CodeReview(BaseModel):
    summary: str = Field(description="Brief summary of the review")
    issues: list[str] = Field(description="List of issues found")
    suggestions: list[str] = Field(description="Improvement suggestions")
    approval: bool = Field(description="Whether code is approved")
    confidence: float = Field(ge=0, le=1, description="Confidence score")

review_agent = Agent(
    'claude-sonnet-4-20250514',
    result_type=CodeReview,
    system_prompt='Review code for quality, security, and best practices.',
)

# Result is validated Pydantic model
result = await review_agent.run(f"Review this code:\n```python\n{code}\n```")
if result.data.approval:
    print("Code approved!")
else:
    for issue in result.data.issues:
        print(f"Issue: {issue}")
```

### Streaming Responses

Stream responses for real-time feedback:

```python
# src/agents/streaming.py
from pydantic_ai import Agent

agent = Agent('claude-sonnet-4-20250514')

async def stream_response(prompt: str):
    async with agent.run_stream(prompt) as response:
        async for chunk in response.stream():
            print(chunk, end='', flush=True)

    # Get final structured result
    result = await response.get_data()
    return result
```

**Key Methods:**
- `agent.run_stream(prompt)`: Start streaming execution
- `response.stream()`: Async iterator for chunks
- `response.get_data()`: Final structured result after streaming completes

**Sources:** [skills/agentic-development.md:579-723]()

---

## Skills Pattern (Anthropic)

The Anthropic skills pattern organizes agent capabilities as self-contained modules with instructions, scripts, and resources.

### Skills Directory Structure

```
skills/
└── code-review/
    ├── instructions.md      # How to perform code reviews
    ├── scripts/
    │   └── run-linters.sh   # Supporting scripts
    └── resources/
        └── checklist.md     # Review checklist
```

### Instructions Format

Each skill defines when to use it, the process, and output format:

```markdown
# Code Review Skill

## When to Use
Activate this skill when asked to review code, PRs, or diffs.

## Process
1. Read the changed files completely
2. Run linters: `./scripts/run-linters.sh`
3. Check against resources/checklist.md
4. Provide structured feedback

## Output Format
- Summary (1-2 sentences)
- Issues found (severity: critical/major/minor)
- Suggestions for improvement
- Approval recommendation
```

### Dynamic Skill Loading

Load skills at runtime based on task requirements:

```typescript
// agents/skill-loader.ts
async function loadSkill(skillName: string): Promise<Skill> {
  const skillPath = `./skills/${skillName}`;
  const instructions = await fs.readFile(`${skillPath}/instructions.md`, 'utf-8');
  const scripts = await glob(`${skillPath}/scripts/*`);
  const resources = await glob(`${skillPath}/resources/*`);

  return {
    name: skillName,
    instructions,
    scripts: scripts.map(s => ({ name: path.basename(s), path: s })),
    resources: await Promise.all(resources.map(loadResource)),
  };
}
```

**Sources:** [skills/agentic-development.md:753-802]()

---

## Anti-Patterns to Avoid

Common mistakes that reduce agent effectiveness:

| Anti-Pattern | Impact | Solution |
|-------------|--------|----------|
| **No planning before execution** | More errors, wasted tool calls | Implement explore-plan-execute-verify |
| **Monolithic agents** | Confused with 50+ tools | Split by domain or use agent-as-tool pattern |
| **No verification** | Silent failures, wrong outputs | Add verify() after each step |
| **Hardcoded tool sequences** | Inflexible, breaks on edge cases | Let model decide tool order |
| **Missing guardrails** | Unsafe behavior, out-of-scope actions | Add multi-layer protection |
| **No state management** | Lose context across tool calls | Use ConversationMemory + AgentState |
| **Testing only happy paths** | Production failures | Test failures, errors, edge cases |
| **Ignoring model differences** | Poor reasoning model usage | Configure thinking_level, thoughtSignature |
| **No cost tracking** | Budget overruns | Monitor token usage per run |
| **Full automation without oversight** | Dangerous actions | Human-in-the-loop for high-risk operations |

**Sources:** [skills/agentic-development.md:806-818]()

---

## Quick Reference

### Agent Development Checklist

- [ ] Define clear agent scope and boundaries
- [ ] Design tools with explicit schemas and risk levels
- [ ] Implement explore-plan-execute-verify workflow
- [ ] Add multi-layer guardrails
- [ ] Set up conversation and persistent memory
- [ ] Write behavior and evaluation tests
- [ ] Configure appropriate model for task complexity
- [ ] Add human-in-the-loop for high-risk operations
- [ ] Monitor token usage and costs
- [ ] Document skills and instructions

### Framework Quick Start

**Python (Pydantic AI):**
```python
from pydantic_ai import Agent
agent = Agent('claude-sonnet-4-20250514', result_type=MyModel)
result = await agent.run('task description')
```

**Node.js (Claude SDK):**
```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  tools: [...],
  messages: [...],
});
```

### Thinking Triggers (Claude)

| Keyword | Effect |
|---------|--------|
| `"think"` | Standard analysis |
| `"think hard"` | Deeper reasoning |
| `"think harder"` | Extensive analysis |
| `"ultrathink"` | Maximum reasoning budget |

### Gemini Configuration

```typescript
{
  thinking_level: "high" | "low",
  temperature: 1.0,  // Keep at 1.0 for reasoning
  thoughtSignature: "<pass back for function calling>"
}
```

**Sources:** [skills/agentic-development.md:820-849]()

---

# Page: Security and Credentials

# Security and Credentials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/credentials.md](skills/credentials.md)
- [skills/posthog-analytics.md](skills/posthog-analytics.md)
- [skills/web-payments.md](skills/web-payments.md)

</details>



## Purpose and Scope

This document explains Claude Bootstrap's defense-in-depth security architecture and centralized credentials management system. It covers how API keys are securely stored, validated, and injected into projects without ever committing them to version control. For information about the specific code review process, see [Quality Gates and Code Review](#4.3). For details on CI/CD security validation, see [Quality Gates](#4.3).

**Core Principles:**
- No secrets in code, ever
- No secrets in client-exposed environment variables (`VITE_*`, `NEXT_PUBLIC_*`)
- Centralized credential storage prevents duplication and exposure
- Multiple validation layers catch secrets before they reach production
- Pattern-based detection catches both accidental and intentional leaks

---

## Defense-in-Depth Security Architecture

Claude Bootstrap implements five layers of security enforcement, ensuring that if one layer fails, subsequent layers provide backup protection.

### Five-Layer Security Model

```mermaid
graph TB
    subgraph Layer1["Layer 1: Development-Time Prevention"]
        L1A["Access.txt<br/>Centralized Storage"]
        L1B[".env Generation<br/>+ .gitignore"]
        L1C["Pattern Validation<br/>Auto-detect Keys"]
        L1D["Client Var Check<br/>VITE_*, NEXT_PUBLIC_*"]
    end
    
    subgraph Layer2["Layer 2: Pre-Commit Enforcement"]
        L2A["Pre-commit Hooks"]
        L2B["security-check.sh<br/>Secret Scanner"]
        L2C["Lint + TypeCheck"]
        L2D["Unit Tests<br/>Changed Files"]
        L2E["Check .env<br/>Not Staged"]
    end
    
    subgraph Layer3["Layer 3: Pre-Push Code Review"]
        L3A["/code-review Command"]
        L3B["Security Analysis<br/>SQL, XSS, Secrets"]
        L3C["Severity Classification<br/>Critical/High/Medium/Low"]
        L3D["Block on Critical/High"]
    end
    
    subgraph Layer4["Layer 4: CI/CD Validation"]
        L4A["GitHub Actions<br/>quality.yml, security.yml"]
        L4B["Full Test Suite<br/>80% Coverage"]
        L4C["TruffleHog<br/>Secret Scanning"]
        L4D["Dependency Audit<br/>npm/pip"]
    end
    
    subgraph Layer5["Layer 5: Runtime Protection"]
        L5A["Environment Isolation"]
        L5B["Server-Only Secrets"]
        L5C["Client-Safe Public Keys"]
    end
    
    CODE[Developer Code] --> L1A --> L1B --> L1C --> L1D
    L1D --> COMMIT[git commit]
    COMMIT --> L2A --> L2B --> L2C --> L2D --> L2E
    L2E --> PUSH[git push]
    PUSH --> L3A --> L3B --> L3C --> L3D
    L3D -->|Pass| L4A --> L4B --> L4C --> L4D
    L4D -->|Pass| DEPLOY[Deploy]
    DEPLOY --> L5A --> L5B --> L5C --> PROD[Production]
    
    L2E -->|Fail| FIX[Fix Issues]
    L3D -->|Fail| FIX
    L4D -->|Fail| FIX
    FIX --> CODE
```

**Sources:** [README.md:29-39](), [README.md:358-365]()

### Layer Responsibilities

| Layer | Timing | Purpose | Failure Mode |
|-------|--------|---------|--------------|
| **Layer 1** | Development | Prevent secrets from entering code | Developer bypasses Access.txt |
| **Layer 2** | Pre-commit | Catch accidental hardcoding | Developer commits with `--no-verify` |
| **Layer 3** | Pre-push | Human+AI review for security issues | Developer pushes with `--no-verify` |
| **Layer 4** | CI/CD | Comprehensive scanning of all code | All local hooks bypassed |
| **Layer 5** | Runtime | Isolate secrets to server environment | Misconfigured deployment |

**Key Insight:** Each layer assumes the previous layer failed, providing redundant protection.

**Sources:** [README.md:516-530]()

---

## Centralized Credentials Management

### Access.txt: Single Source of Truth

Claude Bootstrap uses a centralized credentials file (typically `~/Documents/Access.txt`) to store all API keys in one location. This prevents:
- Secrets scattered across multiple `.env` files
- Duplicate keys for the same service
- Accidental commits of credentials
- Lost keys when switching projects

```mermaid
graph LR
    subgraph User["User's File System"]
        ACCESS["~/Documents/Access.txt<br/>or ~/Access.txt<br/>or ~/.secrets/keys.txt"]
    end
    
    subgraph Bootstrap["Claude Bootstrap"]
        INIT["/initialize-project"]
        PARSE["parse_credentials_file()<br/>credentials.md:93-138"]
        VALIDATE["Validation Commands<br/>credentials.md:175-222"]
    end
    
    subgraph Project["Project Directory"]
        ENV[".env<br/>Generated File"]
        GITIGNORE[".gitignore<br/>Auto-Updated"]
    end
    
    ACCESS -->|Read| INIT
    INIT --> PARSE
    PARSE --> VALIDATE
    VALIDATE -->|Valid Keys| ENV
    ENV -->|Add Entry| GITIGNORE
    
    ACCESS -.->|Never Copied| Project
    ENV -.->|Never Committed| Git[Git Repository]
```

**Sources:** [README.md:366-379](), [skills/credentials.md:1-27]()

### Supported File Formats

The credential parser accepts three flexible formats to accommodate different user preferences:

#### Format 1: Colon-Separated (Informal)
```
OpenAI API: sk-proj-xxxxx
Claude API: sk-ant-xxxxx
Reddit client id: Y1FgKALKmb6f6UxFtyMXfA
Reddit secret: -QLoYdxMqOJkYrgk5KeGPa6Ps6vIiQ
Supabase url: https://xxx.supabase.co
Anon key: eyJxxx
```

#### Format 2: Key=Value (Formal)
```
OPENAI_API_KEY=sk-proj-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
REDDIT_CLIENT_ID=Y1FgKALKmb6f6UxFtyMXfA
REDDIT_CLIENT_SECRET=-QLoYdxMqOJkYrgk5KeGPa6Ps6vIiQ
```

#### Format 3: Mixed/Narrative
```
Reddit api access:
client id Y1FgKALKmb6f6UxFtyMXfA
and secret is -QLoYdxMqOJkYrgk5KeGPa6Ps6vIiQ

Stripe keys from dashboard:
sk_test_51HxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxQ
```

**Sources:** [skills/credentials.md:30-56]()

---

## Pattern-Based Key Detection

Claude Bootstrap uses regex patterns to automatically identify API keys in Access.txt, eliminating manual configuration.

### Key Identification Patterns

```mermaid
graph TB
    subgraph Input["Access.txt Content"]
        RAW["Unstructured Text<br/>Multiple Formats"]
    end
    
    subgraph Patterns["Pattern Matchers<br/>credentials.md:59-81"]
        P1["OpenAI: /sk-proj-[A-Za-z0-9_-]+/"]
        P2["Anthropic: /sk-ant-[A-Za-z0-9_-]+/"]
        P3["Render: /rnd_[A-Za-z0-9]+/"]
        P4["GitHub: /ghp_[A-Za-z0-9]+/"]
        P5["Stripe: /sk_(live|test)_[A-Za-z0-9]+/"]
        P6["PostHog: /phc_[A-Za-z0-9]+/"]
        P7["Replicate: /r8_[A-Za-z0-9]+/"]
        P8["Supabase: /https://[a-z0-9]+\\.supabase\\.co/<br/>+ /eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+/"]
    end
    
    subgraph Output["Environment Variables"]
        ENV1["OPENAI_API_KEY"]
        ENV2["ANTHROPIC_API_KEY"]
        ENV3["RENDER_API_KEY"]
        ENV4["GITHUB_TOKEN"]
        ENV5["STRIPE_SECRET_KEY"]
        ENV6["POSTHOG_API_KEY"]
        ENV7["REPLICATE_API_TOKEN"]
        ENV8["SUPABASE_URL<br/>SUPABASE_ANON_KEY"]
    end
    
    RAW --> P1 --> ENV1
    RAW --> P2 --> ENV2
    RAW --> P3 --> ENV3
    RAW --> P4 --> ENV4
    RAW --> P5 --> ENV5
    RAW --> P6 --> ENV6
    RAW --> P7 --> ENV7
    RAW --> P8 --> ENV8
```

**Sources:** [skills/credentials.md:59-81]()

### Pattern Matching Implementation

The system uses two implementations (Python and TypeScript) that share the same regex patterns:

**Python Parser:**
- Location: [skills/credentials.md:88-138]()
- Function: `parse_credentials_file(file_path: str) -> dict[str, str]`
- Special handling for Reddit (client_id + secret pairs) and Supabase (URL + JWT tokens)

**TypeScript Parser:**
- Location: [skills/credentials.md:140-171]()
- Function: `parseCredentialsFile(content: string): Record<string, string>`
- Same patterns as Python version for consistency

### Supported Services Pattern Reference

| Service | Prefix Pattern | Environment Variable | Example |
|---------|----------------|---------------------|---------|
| OpenAI | `sk-proj-*` | `OPENAI_API_KEY` | `sk-proj-abc123...` |
| Anthropic | `sk-ant-*` | `ANTHROPIC_API_KEY` | `sk-ant-api03-xyz...` |
| Render | `rnd_*` | `RENDER_API_KEY` | `rnd_A1b2C3d4...` |
| Replicate | `r8_*` | `REPLICATE_API_TOKEN` | `r8_xyz123...` |
| Eleven Labs | `sk_*` (not ant/proj) | `ELEVEN_LABS_API_KEY` | `sk_a1b2c3d4...` |
| GitHub | `ghp_*` or `github_pat_*` | `GITHUB_TOKEN` | `ghp_abc123XYZ...` |
| Stripe (Test) | `sk_test_*` | `STRIPE_SECRET_KEY` | `sk_test_51H...` |
| Stripe (Live) | `sk_live_*` | `STRIPE_SECRET_KEY` | `sk_live_51H...` |
| Stripe Webhook | `whsec_*` | `STRIPE_WEBHOOK_SECRET` | `whsec_abc...` |
| PostHog | `phc_*` | `POSTHOG_API_KEY` | `phc_xyz123...` |
| Supabase URL | `https://*.supabase.co` | `SUPABASE_URL` | `https://abc.supabase.co` |
| Supabase JWT | `eyJ*` (JWT) | `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1...` |

**Sources:** [skills/credentials.md:59-81](), [skills/posthog-analytics.md:203-217](), [skills/web-payments.md:18-28]()

---

## Credential Validation Workflow

### Discovery and Validation Process

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Claude as Claude Code
    participant Access as Access.txt
    participant Validation as Validation API
    participant Project as Project .env
    
    Dev->>Claude: /initialize-project
    Claude->>Dev: Need API keys. Access file path?
    Dev->>Claude: ~/Documents/Access.txt
    
    Claude->>Access: Read file
    Access-->>Claude: File content
    
    Claude->>Claude: parse_credentials_file()<br/>Extract keys via regex
    
    Note over Claude: Found:<br/>ANTHROPIC_API_KEY: sk-ant-xxx...<br/>REDDIT_CLIENT_ID: Y1Fg...<br/>REDDIT_CLIENT_SECRET: -QLo...
    
    Claude->>Dev: Found 3 credentials<br/>Validating...
    
    Claude->>Validation: curl -H "x-api-key: sk-ant-xxx"<br/>anthropic.com/v1/models
    Validation-->>Claude: 200 OK
    
    Claude->>Validation: curl -u client_id:secret<br/>reddit.com/api/v1/access_token
    Validation-->>Claude: 200 OK
    
    Claude->>Dev: ✓ ANTHROPIC_API_KEY: Valid<br/>✓ REDDIT_CLIENT_ID: Valid<br/>✗ SUPABASE_URL: Not found
    
    Claude->>Project: Create .env<br/>ANTHROPIC_API_KEY=sk-ant-xxx<br/>REDDIT_CLIENT_ID=Y1Fg...
    
    Claude->>Project: Update .gitignore<br/>Add .env
    
    Claude->>Dev: Missing: SUPABASE_URL<br/>Get from: supabase.com/dashboard
```

**Sources:** [skills/credentials.md:226-280]()

### Validation Commands by Service

The system validates each extracted key by making a minimal API call:

**OpenAI Validation:**
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
# 200 = valid
```

**Anthropic/Claude Validation:**
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  https://api.anthropic.com/v1/models
# 200 = valid
```

**Render Validation:**
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services
# 200 = valid
```

**Reddit Validation:**
```bash
TOKEN=$(curl -s -X POST \
  -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
  -d "grant_type=client_credentials" \
  -A "CredentialTest/1.0" \
  https://www.reddit.com/api/v1/access_token | jq -r '.access_token')
# Non-null token = valid
```

**Sources:** [skills/credentials.md:175-222]()

---

## Environment Variable Generation

### .env File Creation

After validating credentials, Claude Bootstrap generates a `.env` file with proper security annotations:

**Generated .env Structure:**
```bash
# Auto-generated from ~/Documents/Access.txt
# DO NOT COMMIT THIS FILE

# === AI Services ===
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# === Database ===
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# === Payments ===
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# === Analytics ===
POSTHOG_API_KEY=phc_xxxxxxxxxxxxx

# === Client-Safe (Exposed to Browser) ===
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

**Sources:** [skills/credentials.md:259-271]()

### Client vs Server Environment Variables

```mermaid
graph TB
    subgraph Server["Server-Side Only"]
        S1["STRIPE_SECRET_KEY<br/>Never exposed to client"]
        S2["ANTHROPIC_API_KEY<br/>Server-only LLM calls"]
        S3["SUPABASE_SERVICE_ROLE_KEY<br/>Admin operations"]
        S4["Database credentials"]
    end
    
    subgraph Client["Client-Safe (Public)"]
        C1["NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY<br/>Safe for browser"]
        C2["NEXT_PUBLIC_POSTHOG_KEY<br/>Analytics tracking"]
        C3["VITE_SUPABASE_URL<br/>Public endpoint"]
        C4["VITE_SUPABASE_ANON_KEY<br/>Row-level security"]
    end
    
    subgraph Framework["Framework Prefixes"]
        F1["Next.js: NEXT_PUBLIC_*"]
        F2["Vite: VITE_*"]
        F3["Create React App: REACT_APP_*"]
    end
    
    Server -.->|"❌ NEVER"| Client
    Framework --> Client
    
    style Server fill:#fff
    style Client fill:#fff
```

**Key Rules:**
- **Server-only:** `STRIPE_SECRET_KEY`, `ANTHROPIC_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, database passwords
- **Client-safe:** Anything with `NEXT_PUBLIC_*`, `VITE_*`, `REACT_APP_*` prefix
- **PostHog Example:** Backend uses `POSTHOG_API_KEY`, frontend uses `NEXT_PUBLIC_POSTHOG_KEY` (same value, different usage)
- **Stripe Example:** Backend uses `STRIPE_SECRET_KEY`, frontend uses `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` (different keys)

**Sources:** [skills/posthog-analytics.md:203-217](), [skills/web-payments.md:18-28]()

### .gitignore Enforcement

The system automatically ensures `.env` files are never committed:

**Auto-Generated .gitignore Entry:**
```bash
# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Also ignore
.env.*
!.env.example
```

**Pre-commit Hook Check:**
```bash
# Check if .env is staged
if git diff --cached --name-only | grep -q "^\.env"; then
    echo "❌ ERROR: .env file is staged for commit"
    echo "Run: git reset HEAD .env"
    exit 1
fi
```

**Sources:** [skills/credentials.md:307-315]()

---

## Secret Scanning and Prevention

### Pre-Commit Secret Detection

Claude Bootstrap implements multiple secret detection mechanisms that run before commits are allowed.

```mermaid
graph TB
    subgraph Commit["git commit"]
        FILES["Changed Files"]
    end
    
    subgraph Hooks["Pre-Commit Hook<br/>scripts/security-check.sh"]
        H1["Check .env not staged"]
        H2["Scan for API key patterns"]
        H3["Check client env vars<br/>VITE_*, NEXT_PUBLIC_*"]
        H4["Verify no hardcoded secrets"]
    end
    
    subgraph Patterns["Detection Patterns"]
        P1["sk-proj-[A-Za-z0-9_-]+"]
        P2["sk-ant-[A-Za-z0-9_-]+"]
        P3["sk_test_[A-Za-z0-9]+"]
        P4["ghp_[A-Za-z0-9]+"]
        P5["eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"]
    end
    
    subgraph Client["Client Var Validator"]
        CV1["NEXT_PUBLIC_STRIPE_SECRET_KEY"]
        CV2["VITE_ANTHROPIC_API_KEY"]
        CV3["Flag as ERROR"]
    end
    
    FILES --> H1
    H1 -->|Pass| H2
    H2 --> P1
    H2 --> P2
    H2 --> P3
    H2 --> P4
    H2 --> P5
    
    P1 -->|Found| BLOCK[❌ Block Commit]
    P2 -->|Found| BLOCK
    P3 -->|Found| BLOCK
    P4 -->|Found| BLOCK
    P5 -->|Found| BLOCK
    
    H2 -->|Clean| H3
    H3 --> CV1
    H3 --> CV2
    CV1 --> CV3 --> BLOCK
    CV2 --> CV3
    
    H3 -->|Clean| H4
    H4 -->|Clean| ALLOW[✅ Allow Commit]
```

**Sources:** [README.md:516-523]()

### Dangerous Client Variable Detection

The system prevents secrets from being exposed via client-side environment variables:

**Dangerous Patterns (Auto-Blocked):**
```bash
# ❌ These will block commits
NEXT_PUBLIC_STRIPE_SECRET_KEY=sk_test_xxx
NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-xxx
VITE_OPENAI_API_KEY=sk-proj-xxx
REACT_APP_DATABASE_PASSWORD=xxx
```

**Safe Patterns (Allowed):**
```bash
# ✅ These are safe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
NEXT_PUBLIC_POSTHOG_KEY=phc_xxx
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJxxx  # Protected by RLS
```

**Validation Logic:**
```typescript
// Check for dangerous client var patterns
const dangerousPatterns = [
  /NEXT_PUBLIC_.*SECRET/i,
  /NEXT_PUBLIC_.*_KEY.*(?!PUBLISHABLE|PUBLIC)/i,
  /VITE_.*(?:SECRET|PASSWORD|PRIVATE)/i,
  /REACT_APP_.*(?:SECRET|PASSWORD|API_KEY)/i,
];

function validateClientVars(envContent: string): string[] {
  const errors: string[] = [];
  const lines = envContent.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('#')) continue;
    
    for (const pattern of dangerousPatterns) {
      if (pattern.test(line)) {
        errors.push(`Dangerous client var: ${line.split('=')[0]}`);
      }
    }
  }
  
  return errors;
}
```

**Sources:** [skills/credentials.md:307-315]()

### TruffleHog CI/CD Integration

Layer 4 security uses TruffleHog for comprehensive secret scanning in CI/CD:

**GitHub Actions Workflow:**
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for TruffleHog
      
      - name: TruffleHog Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified
```

**What TruffleHog Detects:**
- AWS credentials
- Database connection strings
- Private keys (RSA, SSH)
- API keys from 700+ services
- OAuth tokens
- JWT secrets

**Sources:** [README.md:525-530]()

---

## Security Enforcement Flow

### Complete Security Pipeline

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Code as Code Changes
    participant PreCommit as Pre-Commit Hook
    participant PrePush as Pre-Push Hook
    participant CI as CI/CD Pipeline
    participant Prod as Production
    
    Dev->>Code: Write code with env vars
    Dev->>Code: git add .
    Dev->>PreCommit: git commit
    
    PreCommit->>PreCommit: Check .env not staged
    PreCommit->>PreCommit: Scan for secret patterns
    PreCommit->>PreCommit: Validate client vars
    
    alt Secrets Found
        PreCommit-->>Dev: ❌ BLOCKED: Secret detected
        Dev->>Code: Remove hardcoded secret
        Dev->>PreCommit: git commit (retry)
    end
    
    PreCommit-->>Dev: ✅ Commit allowed
    
    Dev->>PrePush: git push
    PrePush->>PrePush: /code-review command
    PrePush->>PrePush: Analyze security issues
    PrePush->>PrePush: Check SQL injection, XSS
    
    alt Critical/High Issues
        PrePush-->>Dev: ❌ BLOCKED: Security issues
        Dev->>Code: Fix vulnerabilities
        Dev->>PrePush: git push (retry)
    end
    
    PrePush-->>CI: ✅ Push allowed
    
    CI->>CI: Run full test suite
    CI->>CI: TruffleHog secret scan
    CI->>CI: npm audit / safety check
    CI->>CI: Coverage validation (80%)
    
    alt CI Fails
        CI-->>Dev: ❌ BLOCKED: CI checks failed
        Dev->>Code: Fix issues
        Dev->>CI: Re-push
    end
    
    CI-->>Prod: ✅ Deploy approved
```

**Sources:** [README.md:176-209](), [README.md:516-530]()

### Enforcement Point Summary

| Enforcement Point | What It Checks | Block Condition | Bypass Method |
|------------------|----------------|-----------------|---------------|
| **Pre-commit** | `.env` staged, hardcoded secrets, client vars | Any violation | `git commit --no-verify` |
| **Pre-push** | Security vulnerabilities, code review | Critical/High severity | `git push --no-verify` |
| **CI/CD** | Full secret scan, dependency audit, tests | Any failure | Cannot bypass |
| **Runtime** | Environment isolation | N/A | Misconfigured deployment |

**Key Defense:** Even if developers bypass local hooks with `--no-verify`, CI/CD provides mandatory enforcement.

**Sources:** [README.md:516-530]()

---

## Security Best Practices

### Non-Negotiable Rules

1. **Never commit secrets** - Use Access.txt → .env workflow
2. **Never expose secrets to client** - Check `NEXT_PUBLIC_*`, `VITE_*` prefixes
3. **Always validate webhooks** - Verify signatures before processing
4. **Always mask secrets in logs** - Show only first 8 and last 4 characters
5. **Always add .env to .gitignore** - Automated during initialization

**Sources:** [skills/credentials.md:307-315](), [skills/web-payments.md:509-532]()

### Secret Masking for Logging

```typescript
// lib/security.ts
export function maskSecret(secret: string): string {
  if (secret.length <= 12) return '***';
  const start = secret.slice(0, 8);
  const end = secret.slice(-4);
  return `${start}...${end}`;
}

// Usage
console.log('API Key:', maskSecret(apiKey)); // "sk-proj-...b2C3"
```

**Sources:** [skills/credentials.md:243-248]()

### Webhook Signature Verification

Critical security pattern for payment and API webhooks:

```typescript
// app/api/webhooks/stripe/route.ts
export async function POST(request: Request) {
  const body = await request.text();
  const signature = headers().get('stripe-signature')!;
  
  try {
    // ✅ Always verify before processing
    const event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
    
    // Process event only after verification
    await processEvent(event);
  } catch (err) {
    // ❌ Invalid signature = reject
    return new Response('Invalid signature', { status: 400 });
  }
}
```

**Sources:** [skills/web-payments.md:236-286]()

---

## Quick Reference

### Commands

```bash
# Validate credentials file
cat ~/Documents/Access.txt | grep -E "(sk-|rnd_|phc_)"

# Install pre-commit hooks
~/.claude/install-hooks.sh

# Test webhook signature verification
stripe trigger checkout.session.completed

# Scan for secrets locally
git diff HEAD | grep -E "(sk-proj-|sk-ant-|ghp_)"
```

### Critical Files

| File | Purpose | Security Level |
|------|---------|----------------|
| `Access.txt` | Centralized credentials | **NEVER COMMIT** |
| `.env` | Project-specific env vars | **NEVER COMMIT** |
| `.gitignore` | Prevents .env commits | Auto-generated |
| `security-check.sh` | Pre-commit scanner | Local enforcement |
| `.github/workflows/security.yml` | CI/CD scanner | Mandatory enforcement |

### Pattern Detection Reference

```regex
# OpenAI
sk-proj-[A-Za-z0-9_-]{32,}

# Anthropic
sk-ant-[A-Za-z0-9_-]{32,}

# GitHub Personal Access Token
ghp_[A-Za-z0-9]{36}

# Stripe Secret Key
sk_(live|test)_[A-Za-z0-9]{24,}

# Supabase JWT
eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+

# Generic Private Key
-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----
```

**Sources:** [skills/credentials.md:59-81]()

### Environment Variable Prefixes

| Framework | Client-Safe Prefix | Example |
|-----------|-------------------|---------|
| Next.js | `NEXT_PUBLIC_*` | `NEXT_PUBLIC_POSTHOG_KEY` |
| Vite | `VITE_*` | `VITE_SUPABASE_URL` |
| Create React App | `REACT_APP_*` | `REACT_APP_API_URL` |
| Expo | `EXPO_PUBLIC_*` | `EXPO_PUBLIC_API_KEY` |

**Sources:** [skills/posthog-analytics.md:203-217]()

---

# Page: Security Architecture

# Security Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/credentials.md](skills/credentials.md)
- [skills/posthog-analytics.md](skills/posthog-analytics.md)
- [skills/web-payments.md](skills/web-payments.md)

</details>



## Purpose and Scope

This document describes the security architecture of Claude Bootstrap: a five-layer defense-in-depth system that prevents secrets from entering the codebase, validates API credentials, and enforces security checks at every stage of the development lifecycle. 

For credential management patterns and Access.txt format, see [Credentials Management](#6.2). For secret detection patterns and scanning tools, see [Secret Scanning and Prevention](#6.3).

**Sources:** [README.md:29-39](), [README.md:358-365]()

---

## Core Security Philosophy

Claude Bootstrap implements **defense-in-depth**: if one security layer fails, subsequent layers provide backup protection. No single point of failure can expose secrets or vulnerable code.

**Three non-negotiable rules:**

1. **No secrets in code** - API keys, tokens, passwords never appear in source files
2. **No secrets in client environment variables** - `VITE_*`, `NEXT_PUBLIC_*`, `EXPO_PUBLIC_*` vars are publicly exposed
3. **Validation at every stage** - Pre-commit, pre-push, and CI/CD all run independent checks

**Sources:** [README.md:358-365]()

---

## Five-Layer Defense Architecture

### Layer Overview

```mermaid
graph TB
    subgraph "Layer 1: Development-Time Prevention"
        L1A["Access.txt<br/>(~/Documents/)"]
        L1B[".env Generation<br/>+ .gitignore"]
        L1C["Pattern Validation<br/>Auto-detect API keys"]
        L1D["Client Env Var Check<br/>VITE_*, NEXT_PUBLIC_*"]
    end
    
    subgraph "Layer 2: Pre-Commit Enforcement"
        L2A["Husky/pre-commit Hooks<br/>(.husky/pre-commit)"]
        L2B["security-check.sh<br/>Scan for secrets"]
        L2C["Lint + TypeCheck<br/>(eslint, mypy)"]
        L2D["Unit Tests<br/>Changed files only"]
        L2E["Check .env not staged<br/>(git diff --cached)"]
    end
    
    subgraph "Layer 3: Pre-Push Code Review"
        L3A["/code-review Command<br/>Mandatory review"]
        L3B["Analyze Changes<br/>Security, Performance, Architecture"]
        L3C["Severity Classification<br/>Critical, High, Medium, Low"]
        L3D["Block Push<br/>Critical/High issues"]
    end
    
    subgraph "Layer 4: CI/CD Validation"
        L4A["GitHub Actions<br/>(.github/workflows/)"]
        L4B["quality.yml<br/>Full Test Suite"]
        L4C["80% Coverage<br/>Enforcement"]
        L4D["security.yml<br/>Secrets + Dependencies"]
        L4E["TruffleHog<br/>Secret scanning"]
        L4F["npm audit / safety<br/>Dependency vulnerabilities"]
    end
    
    subgraph "Layer 5: Commit Hygiene Monitoring"
        L5A["Track Commit Size<br/>Files + Lines changed"]
        L5B["OK: ≤5 files, ≤200 lines"]
        L5C["WARN: 6-10 files, 201-400 lines"]
        L5D["STOP: >10 files, >400 lines"]
    end
    
    CODE["Developer Code"] --> L1A
    L1A --> L1B --> L1C --> L1D
    
    L1D --> COMMIT["git commit"]
    COMMIT --> L2A --> L2B --> L2C --> L2D --> L2E
    
    L2E --> L5A
    L5A --> L5B
    L5A --> L5C
    L5A --> L5D
    
    L5B --> PUSH["git push"]
    L5C --> PUSH
    L5D --> PUSH
    
    PUSH --> L3A --> L3B --> L3C --> L3D
    
    L3D -->|"Block"| FIX["Fix Issues"]
    L3D -->|"Allow"| L4A
    
    FIX --> CODE
    
    L4A --> L4B --> L4C --> L4D --> L4E --> L4F
    
    L4F -->|"Pass"| MERGE["Merge Approved"]
    L4F -->|"Fail"| FIX
    
    L2E -->|"Fail"| FIX
```

**Sources:** [README.md:515-529](), Diagram 5 from high-level overview

---

## Layer 1: Development-Time Prevention

### Centralized Credentials (Access.txt)

All API keys are stored in a single file outside the repository, preventing accidental commits.

**Credentials Flow:**

```mermaid
graph LR
    subgraph "User Storage"
        ACCESS["~/Documents/Access.txt<br/>or ~/Access.txt"]
    end
    
    subgraph "Project Initialization"
        INIT["/initialize-project"]
        PARSE["parse_credentials_file()<br/>(credentials.md)"]
        VALIDATE["Validation Commands<br/>(curl tests)"]
    end
    
    subgraph "Project Files"
        ENV[".env<br/>(gitignored)"]
        GITIGNORE[".gitignore"]
    end
    
    subgraph "Application Runtime"
        SERVER["Server-Side Code<br/>process.env.*"]
        CLIENT["Client-Side Code<br/>NEXT_PUBLIC_*"]
    end
    
    ACCESS -->|"1. Read"| INIT
    INIT --> PARSE
    PARSE -->|"2. Extract patterns"| VALIDATE
    VALIDATE -->|"3. Generate"| ENV
    ENV -->|"4. Add"| GITIGNORE
    
    ENV -->|"5. Load"| SERVER
    ENV -->|"5. Load (safe only)"| CLIENT
```

**File format examples (Access.txt):**

[skills/credentials.md:34-56]()

**Pattern detection:**

The system automatically identifies API keys by their prefixes:

| Service | Pattern | Environment Variable |
|---------|---------|---------------------|
| OpenAI | `sk-proj-*` | `OPENAI_API_KEY` |
| Anthropic/Claude | `sk-ant-*` | `ANTHROPIC_API_KEY` |
| Stripe (Test) | `sk_test_*`, `pk_test_*` | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` |
| PostHog | `phc_*` | `POSTHOG_API_KEY` |
| GitHub | `ghp_*` or `github_pat_*` | `GITHUB_TOKEN` |
| Supabase | URL + `eyJ*` (JWT) | `SUPABASE_URL`, `SUPABASE_ANON_KEY` |

**Sources:** [skills/credentials.md:59-81](), [skills/credentials.md:84-138]()

### Environment Variable Classification

**Critical distinction: Client-exposed vs Server-only**

```mermaid
graph TB
    subgraph "SAFE for Client (Publicly Exposed)"
        SAFE1["NEXT_PUBLIC_*"]
        SAFE2["VITE_*"]
        SAFE3["EXPO_PUBLIC_*"]
        SAFE4["REACT_APP_*"]
    end
    
    subgraph "Examples: Safe Client Vars"
        EX1["NEXT_PUBLIC_POSTHOG_KEY<br/>(Analytics tracking)"]
        EX2["NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY<br/>(pk_test_* or pk_live_*)"]
        EX3["NEXT_PUBLIC_SUPABASE_URL<br/>(Public API endpoint)"]
        EX4["NEXT_PUBLIC_SUPABASE_ANON_KEY<br/>(Row-level security protected)"]
    end
    
    subgraph "UNSAFE for Client (Server-Only)"
        UNSAFE1["STRIPE_SECRET_KEY<br/>(sk_test_* or sk_live_*)"]
        UNSAFE2["ANTHROPIC_API_KEY<br/>(sk-ant-*)"]
        UNSAFE3["OPENAI_API_KEY<br/>(sk-proj-*)"]
        UNSAFE4["SUPABASE_SERVICE_ROLE_KEY<br/>(Bypasses RLS)"]
        UNSAFE5["STRIPE_WEBHOOK_SECRET<br/>(whsec_*)"]
        UNSAFE6["DATABASE_URL<br/>(Connection string)"]
    end
    
    SAFE1 --> EX1
    SAFE1 --> EX2
    SAFE1 --> EX3
    SAFE1 --> EX4
```

**Validation during initialization:**

The system checks for dangerous patterns:

```typescript
// ❌ CRITICAL ERROR - Will block initialization
NEXT_PUBLIC_STRIPE_SECRET_KEY=sk_test_xxx  // Secret key in client var!
VITE_ANTHROPIC_API_KEY=sk-ant-xxx         // API key in client var!

// ✅ CORRECT
STRIPE_SECRET_KEY=sk_test_xxx              // Server-only
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx  // Safe for client
```

**Sources:** [README.md:361](), [skills/credentials.md:307-314](), [skills/posthog-analytics.md:203-211](), [skills/web-payments.md:19-28]()

### .gitignore Enforcement

During project initialization, critical files are automatically added to `.gitignore`:

```bash
# Auto-generated by /initialize-project
.env
.env.local
.env.*.local
Access.txt
*.pem
*.key
```

**Sources:** [skills/credentials.md:269]()

---

## Layer 2: Pre-Commit Enforcement

### Hook Installation

Hooks are installed via `~/.claude/install-hooks.sh`:

```bash
# From project root
~/.claude/install-hooks.sh
```

This creates:
- `.husky/pre-commit` - Runs on every `git commit`
- `.husky/pre-push` - Runs on every `git push`

**Sources:** [README.md:189-192]()

### Pre-Commit Execution Flow

```mermaid
graph TD
    START["git commit"] --> CHECK1["Check: .env staged?"]
    
    CHECK1 -->|"Yes"| BLOCK1["❌ BLOCK<br/>Remove .env from staging"]
    CHECK1 -->|"No"| CHECK2["Run: security-check.sh"]
    
    CHECK2 --> SCAN1["Scan for patterns:<br/>sk-*, ghp_*, eyJ*"]
    SCAN1 -->|"Secrets found"| BLOCK2["❌ BLOCK<br/>Remove secrets from code"]
    SCAN1 -->|"Clean"| CHECK3["Run: Linter"]
    
    CHECK3 -->|"Errors"| BLOCK3["❌ BLOCK<br/>Fix lint errors"]
    CHECK3 -->|"Pass"| CHECK4["Run: Type Check"]
    
    CHECK4 -->|"Errors"| BLOCK4["❌ BLOCK<br/>Fix type errors"]
    CHECK4 -->|"Pass"| CHECK5["Run: Unit Tests<br/>(changed files)"]
    
    CHECK5 -->|"Failures"| BLOCK5["❌ BLOCK<br/>Fix failing tests"]
    CHECK5 -->|"Pass"| SUCCESS["✅ COMMIT ALLOWED"]
    
    BLOCK1 --> END["Commit aborted"]
    BLOCK2 --> END
    BLOCK3 --> END
    BLOCK4 --> END
    BLOCK5 --> END
```

### security-check.sh

Located in `scripts/security-check.sh`, this script scans for:

**1. Hardcoded secrets:**
```bash
# Regex patterns checked
sk-[a-zA-Z0-9]{20,}          # API keys (OpenAI, Anthropic)
ghp_[a-zA-Z0-9]{36}          # GitHub tokens
pk_[a-z]+_[a-zA-Z0-9]{24,}   # Stripe publishable keys
sk_[a-z]+_[a-zA-Z0-9]{24,}   # Stripe secret keys
eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+  # JWT tokens
```

**2. Staged .env files:**
```bash
git diff --cached --name-only | grep -E '^\.env'
```

**3. Client-side secret exposure:**
```bash
# Check for dangerous patterns in client env vars
grep -r "NEXT_PUBLIC_.*sk-" src/
grep -r "VITE_.*SECRET" src/
```

**Sources:** [README.md:519-523]()

---

## Layer 3: Pre-Push Code Review

### /code-review Command

The `/code-review` command provides mandatory security analysis before pushing code.

**Execution context:**

```mermaid
graph LR
    subgraph "Developer Workflow"
        DEV1["Write Code"]
        DEV2["Run Tests"]
        DEV3["git commit"]
        DEV4["git push"]
    end
    
    subgraph "/code-review Execution"
        CR1["Analyze git diff"]
        CR2["Security Analysis"]
        CR3["Performance Analysis"]
        CR4["Architecture Analysis"]
        CR5["Severity Classification"]
    end
    
    subgraph "Severity Levels"
        SEV1["🔴 Critical"]
        SEV2["🟠 High"]
        SEV3["🟡 Medium"]
        SEV4["🟢 Low"]
    end
    
    subgraph "Enforcement"
        ENF1["BLOCK Push"]
        ENF2["ALLOW Push<br/>(Advisory)"]
    end
    
    DEV1 --> DEV2 --> DEV3 --> DEV4
    DEV4 -->|"Pre-push hook"| CR1
    CR1 --> CR2 --> CR3 --> CR4 --> CR5
    
    CR5 --> SEV1
    CR5 --> SEV2
    CR5 --> SEV3
    CR5 --> SEV4
    
    SEV1 --> ENF1
    SEV2 --> ENF1
    SEV3 --> ENF2
    SEV4 --> ENF2
```

**Sources:** [README.md:176-209]()

### Security Issues Detected

| Category | Examples | Severity |
|----------|----------|----------|
| **Secrets Exposure** | Hardcoded API keys, credentials in client code | 🔴 Critical |
| **Injection Vulnerabilities** | SQL injection, XSS, command injection | 🔴 Critical |
| **Authentication Bypass** | Missing auth checks, weak session management | 🟠 High |
| **Sensitive Data Leaks** | Logging passwords, exposing PII | 🟠 High |
| **Insecure Dependencies** | Known CVEs in packages | 🟡 Medium |
| **Missing Input Validation** | Unvalidated user input | 🟡 Medium |
| **Rate Limiting** | Missing or weak rate limits | 🟢 Low |

**Sources:** [README.md:203-208]()

### Pre-Push Hook Integration

The pre-push hook in `.husky/pre-push` automatically runs `/code-review`:

```bash
#!/bin/sh
# Auto-generated by install-hooks.sh

# Run code review
claude --command /code-review

# Exit code determines if push proceeds
if [ $? -ne 0 ]; then
  echo "❌ Push blocked due to Critical/High severity issues"
  exit 1
fi
```

---

## Layer 4: CI/CD Validation

### GitHub Actions Workflows

**quality.yml** - Full test suite with coverage enforcement:

```yaml
# .github/workflows/quality.yml
name: Quality Gates

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint
        run: npm run lint
      
      - name: Type check
        run: npm run typecheck
      
      - name: Test with coverage
        run: npm test -- --coverage
      
      - name: Enforce 80% coverage
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "❌ Coverage $COVERAGE% is below 80% threshold"
            exit 1
          fi
```

**security.yml** - Secret scanning and dependency auditing:

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for TruffleHog
      
      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
  
  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: npm audit
        run: npm audit --audit-level=moderate
      
      # For Python projects
      - name: Safety check
        run: |
          pip install safety
          safety check --json
```

**Sources:** [README.md:525-529]()

### CI/CD Enforcement Flow

```mermaid
graph TD
    PR["Pull Request Created"] --> TRIGGER["GitHub Actions Triggered"]
    
    TRIGGER --> PARALLEL{{"Parallel Execution"}}
    
    PARALLEL --> QUALITY["quality.yml"]
    PARALLEL --> SECURITY["security.yml"]
    
    subgraph "Quality Pipeline"
        Q1["Lint (eslint/ruff)"]
        Q2["Type Check (tsc/mypy)"]
        Q3["Full Test Suite"]
        Q4["Coverage Check ≥80%"]
    end
    
    subgraph "Security Pipeline"
        S1["TruffleHog Scan<br/>(All commits)"]
        S2["npm audit / safety<br/>(Dependencies)"]
        S3["Check for .env in commits"]
    end
    
    QUALITY --> Q1 --> Q2 --> Q3 --> Q4
    SECURITY --> S1 --> S2 --> S3
    
    Q4 -->|"Pass"| MERGE_CHECK["Check Both Pipelines"]
    S3 -->|"Pass"| MERGE_CHECK
    
    Q4 -->|"Fail"| BLOCK["❌ Block PR"]
    S3 -->|"Fail"| BLOCK
    
    MERGE_CHECK -->|"Both Pass"| ALLOW["✅ Allow Merge"]
```

**Sources:** [README.md:525-529]()

---

## Layer 5: Commit Hygiene Monitoring

### PR Size Thresholds

Claude Bootstrap tracks commit size to prevent oversized PRs, which correlate with higher defect rates.

**Thresholds:**

| Status | Files | Lines | Action |
|--------|-------|-------|--------|
| 🟢 OK | ≤5 | ≤200 | Normal review |
| 🟡 WARNING | 6-10 | 201-400 | Advise to commit soon |
| 🔴 STOP | >10 | >400 | Force commit immediately |

**Statistical backing:**

- PRs < 200 lines: **15% defect rate**
- PRs 200-400 lines: **23% defect rate**
- PRs > 400 lines: **40%+ defect rate** (often rubber-stamped)

**Sources:** [README.md:119-146]()

### Atomic Commit Principle

**Rule:** If you need "and" to describe your commit, split it.

```bash
# ❌ Bad: Multiple concerns
git commit -m "Add user auth and refactor database and fix bug in payment"

# ✅ Good: Atomic commits
git commit -m "Add user authentication flow"
git commit -m "Refactor database connection pooling"
git commit -m "Fix race condition in payment processing"
```

---

## Security Patterns in Practice

### Webhook Signature Verification

**Example from Stripe integration:**

```mermaid
graph LR
    subgraph "Stripe Server"
        STRIPE["Stripe Event<br/>(payment_succeeded)"]
        SIGN["Sign with webhook secret"]
    end
    
    subgraph "Your Server"
        WEBHOOK["/api/webhooks/stripe"]
        VERIFY["stripe.webhooks.constructEvent()"]
        PROCESS["Process Event"]
        DB["Update Database"]
    end
    
    STRIPE --> SIGN
    SIGN -->|"POST with signature header"| WEBHOOK
    WEBHOOK --> VERIFY
    VERIFY -->|"Signature valid"| PROCESS
    VERIFY -->|"Invalid signature"| REJECT["❌ 400 Bad Request"]
    PROCESS --> DB
```

**Code reference:**

[skills/web-payments.md:236-255]() shows webhook verification:

```typescript
// Verify signature before processing
try {
  event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
} catch (err) {
  console.error("Webhook signature verification failed");
  return new Response("Invalid signature", { status: 400 });
}
```

**Why this matters:** Without signature verification, attackers could send fake payment success events to provision free access.

**Sources:** [skills/web-payments.md:229-303]()

### Idempotent Event Processing

**Pattern to prevent duplicate webhook processing:**

```typescript
// Example from webhook handler
const processedEvents = new Set<string>(); // Use Redis in production

export async function POST(request: Request) {
  // ... verify signature ...
  
  // Skip duplicate events
  if (processedEvents.has(event.id)) {
    return new Response("Already processed", { status: 200 });
  }
  processedEvents.add(event.id);
  
  // Process event...
}
```

**Sources:** [skills/web-payments.md:519-532]()

### Sanitizing Analytics Properties

**Example from PostHog integration:**

```typescript
// Prevent sensitive data from being tracked
const SENSITIVE_KEYS = ['password', 'token', 'secret', 'credit', 'ssn'];

function sanitizeProperties(props: Record<string, any>): Record<string, any> {
  return Object.fromEntries(
    Object.entries(props).filter(([key]) =>
      !SENSITIVE_KEYS.some(sensitive => key.toLowerCase().includes(sensitive))
    )
  );
}
```

**Sources:** [skills/posthog-analytics.md:788-802]()

---

## Security Checklist for New Projects

When initializing a project with `/initialize-project`, the system enforces these security measures:

### Initialization Checklist

- [ ] Access.txt file provided and validated
- [ ] .env file generated with required credentials
- [ ] .env added to .gitignore
- [ ] Client env vars validated (no secrets in NEXT_PUBLIC_*, VITE_*)
- [ ] Pre-commit hooks installed (security-check.sh)
- [ ] Pre-push hooks installed (/code-review)
- [ ] GitHub Actions workflows created (quality.yml, security.yml)
- [ ] Webhook secrets generated (if applicable)
- [ ] TruffleHog configured for CI
- [ ] Dependency audit enabled (npm audit / safety)

### Runtime Security Checklist

- [ ] All API calls use server-side credentials
- [ ] Webhook signatures verified before processing
- [ ] Event processing is idempotent (no duplicate processing)
- [ ] Sensitive data never logged or tracked
- [ ] Rate limiting implemented on public endpoints
- [ ] Input validation on all user-provided data
- [ ] Error messages don't leak sensitive information

**Sources:** [skills/credentials.md:226-280](), [README.md:358-365]()

---

## Anti-Patterns and Common Mistakes

### Critical Mistakes (Always Block)

| Anti-Pattern | Why It's Dangerous | Detection Layer |
|--------------|-------------------|-----------------|
| Hardcoded API keys in code | Exposed in git history forever | Layer 2 (pre-commit) |
| Secrets in NEXT_PUBLIC_* vars | Bundled into client JavaScript | Layer 1 (validation) |
| Skipping webhook verification | Attackers can forge events | Layer 3 (code review) |
| .env committed to git | Credentials exposed to all collaborators | Layer 2 (pre-commit) |
| Using floating-point for currency | Rounding errors cause financial loss | Layer 3 (code review) |
| Processing webhooks twice | Duplicate charges/provisions | Layer 3 (code review) |

### Warning Signs (Review Required)

| Pattern | Risk Level | Review Action |
|---------|-----------|---------------|
| Client-side payment creation | 🟠 High | Move to server-side |
| Missing error handling on API calls | 🟡 Medium | Add try-catch blocks |
| Logging user input without sanitization | 🟡 Medium | Sanitize before logging |
| No rate limiting on endpoints | 🟢 Low | Add rate limiting middleware |

**Sources:** [skills/web-payments.md:612-622]()

---

## Quick Reference

### Security Command Reference

```bash
# Install security hooks
~/.claude/install-hooks.sh

# Run manual code review
/code-review

# Test webhook signature verification (local)
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Scan for secrets manually
grep -r "sk-" src/
grep -r "ghp_" src/

# Check .env not staged
git diff --cached --name-only | grep -E '^\.env'

# Validate Access.txt patterns
cat ~/Documents/Access.txt | grep -E "(sk-ant-|sk-proj-|ghp_)"
```

### File Path Reference

| Security Component | File Path |
|-------------------|-----------|
| Credentials skill | `skills/credentials.md` |
| Security skill | `skills/security.md` |
| Pre-commit hook | `.husky/pre-commit` |
| Pre-push hook | `.husky/pre-push` |
| Security check script | `scripts/security-check.sh` |
| Quality workflow | `.github/workflows/quality.yml` |
| Security workflow | `.github/workflows/security.yml` |
| Git ignore | `.gitignore` |
| Environment vars | `.env` (never committed) |

### Environment Variable Prefixes

**Safe for client (public):**
- `NEXT_PUBLIC_*` (Next.js)
- `VITE_*` (Vite)
- `EXPO_PUBLIC_*` (Expo/React Native)
- `REACT_APP_*` (Create React App)

**Server-only (private):**
- No prefix required
- Never use client prefixes for secrets

**Sources:** [skills/credentials.md:1-349](), [skills/posthog-analytics.md:203-217](), [skills/web-payments.md:19-28]()

---

# Page: Credentials Management

# Credentials Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/credentials.md](skills/credentials.md)
- [skills/posthog-analytics.md](skills/posthog-analytics.md)
- [skills/web-payments.md](skills/web-payments.md)

</details>



## Purpose and Scope

This page documents the centralized credentials management system that uses `Access.txt` as a single source of truth for API keys. The system handles credential discovery, pattern-based identification, validation, and `.env` file generation for new projects.

For information about secret scanning and enforcement mechanisms, see [Secret Scanning and Prevention](#6.3). For the broader security architecture, see [Security Architecture](#6.1).

---

## The Access.txt System

Claude Bootstrap implements a centralized credential management pattern where developers maintain a single `Access.txt` file containing all API keys, rather than manually copying credentials into each project's `.env` file.

### File Discovery

When initializing a project that requires API keys, Claude Bootstrap checks default locations and prompts the user:

```
I need API credentials for [service]. Do you have a centralized access keys file?

Please provide the path (e.g., ~/Documents/Access.txt) or type 'manual' to enter keys directly.
```

**Default locations checked:**
- `~/Documents/Access.txt`
- `~/Access.txt`
- `~/.secrets/keys.txt`
- `~/.credentials.txt`

The system never commits the path or file to git, preserving user privacy and security.

**Sources:** [skills/credentials.md:9-26]()

---

## Supported File Formats

The credentials file parser handles three format styles to accommodate different user preferences:

### Format 1: Colon-Separated (Informal)

```
Render API: rnd_xxxxx
OpenAI API: sk-proj-xxxxx
Claude API: sk-ant-xxxxx
Reddit client id: xxxxx
Reddit secret: xxxxx
```

### Format 2: Key=Value (Environment Variable Style)

```
RENDER_API_KEY=rnd_xxxxx
OPENAI_API_KEY=sk-proj-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Format 3: Mixed/Informal (Natural Language)

```
Reddit api access:
client id Y1FgKALKmb6f6UxFtyMXfA
and secret is -QLoYdxMqOJkYrgk5KeGPa6Ps6vIiQ
```

The parser uses regex pattern matching to extract credentials regardless of format, making the system flexible and user-friendly.

**Sources:** [skills/credentials.md:30-56]()

---

## Key Identification Patterns

The system identifies API keys by their prefix patterns. Each service uses a distinct format that can be matched with regex:

| Service | Pattern | Env Variable | Example |
|---------|---------|--------------|---------|
| OpenAI | `sk-proj-*` or `sk-*` | `OPENAI_API_KEY` | `sk-proj-abc123...` |
| Anthropic/Claude | `sk-ant-*` | `ANTHROPIC_API_KEY` | `sk-ant-xyz789...` |
| Render | `rnd_*` | `RENDER_API_KEY` | `rnd_abc123` |
| Eleven Labs | `sk_*` (40+ hex chars) | `ELEVEN_LABS_API_KEY` | `sk_a1b2c3d4e5...` |
| Replicate | `r8_*` | `REPLICATE_API_TOKEN` | `r8_xyz789` |
| GitHub | `ghp_*` or `github_pat_*` | `GITHUB_TOKEN` | `ghp_abc123...` |
| Stripe (Test) | `sk_test_*`, `pk_test_*` | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` | `sk_test_abc123...` |
| Stripe (Live) | `sk_live_*`, `pk_live_*` | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` | `sk_live_xyz789...` |
| Stripe Webhook | `whsec_*` | `STRIPE_WEBHOOK_SECRET` | `whsec_abc123...` |
| PostHog | `phc_*` | `POSTHOG_API_KEY` | `phc_xyz789...` |
| Supabase | `https://[id].supabase.co` + JWT | `SUPABASE_URL`, `SUPABASE_ANON_KEY` | URL + `eyJ...` |
| Reddit | client_id + secret pair | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` | (paired values) |

### Pattern Matching Diagram

```mermaid
graph TB
    ACCESS["Access.txt File"]
    
    subgraph "Pattern Matchers"
        SIMPLE["Simple Prefix Match<br/>(sk-ant-, rnd_, phc_)"]
        JWT["JWT Token Match<br/>(eyJ[A-Za-z0-9_-]+...)"]
        PAIR["Paired Credentials<br/>(client_id + secret)"]
        URL["URL + Token<br/>(Supabase)"]
    end
    
    subgraph "Extracted Credentials"
        ENV1["OPENAI_API_KEY"]
        ENV2["ANTHROPIC_API_KEY"]
        ENV3["SUPABASE_URL"]
        ENV4["SUPABASE_ANON_KEY"]
        ENV5["REDDIT_CLIENT_ID"]
        ENV6["REDDIT_CLIENT_SECRET"]
    end
    
    ACCESS --> SIMPLE
    ACCESS --> JWT
    ACCESS --> PAIR
    ACCESS --> URL
    
    SIMPLE --> ENV1
    SIMPLE --> ENV2
    JWT --> ENV4
    PAIR --> ENV5
    PAIR --> ENV6
    URL --> ENV3
    URL --> ENV4
```

**Sources:** [skills/credentials.md:59-81]()

---

## Parsing Logic

The system implements parsing in both Python and TypeScript to support different project types.

### Python Implementation

The `parse_credentials_file()` function uses regex patterns to extract credentials:

```mermaid
graph LR
    subgraph "parse_credentials_file Function"
        READ["Read file from<br/>expanduser path"]
        PATTERNS["Apply regex patterns<br/>from patterns dict"]
        SPECIAL["Handle special cases<br/>(Supabase, Reddit)"]
        RETURN["Return dict of<br/>env_var: value"]
    end
    
    FILE["~/Documents/Access.txt"] --> READ
    READ --> PATTERNS
    PATTERNS --> SPECIAL
    SPECIAL --> RETURN
    RETURN --> CREDS["credentials: dict[str, str]"]
```

**Key patterns from implementation:**
- `OPENAI_API_KEY`: `r'sk-proj-[A-Za-z0-9_-]+'`
- `ANTHROPIC_API_KEY`: `r'sk-ant-[A-Za-z0-9_-]+'`
- `RENDER_API_KEY`: `r'rnd_[A-Za-z0-9]+'`
- `STRIPE_SECRET_KEY`: `r'sk_(live|test)_[A-Za-z0-9]+'`
- `POSTHOG_API_KEY`: `r'phc_[A-Za-z0-9]+'`

**Special handling:**
- **Supabase**: Extracts URL (`https://[id].supabase.co`) and searches for JWT tokens labeled with "anon" or "service role"
- **Reddit**: Extracts paired `client_id` and `secret` by searching for contextual labels

**Sources:** [skills/credentials.md:88-138]()

### TypeScript Implementation

The TypeScript version mirrors the Python logic with identical pattern matching:

```typescript
function parseCredentialsFile(content: string): Record<string, string>
```

Patterns are defined as `Record<string, RegExp>` and applied sequentially. Reddit credentials receive special paired extraction logic.

**Sources:** [skills/credentials.md:140-171]()

---

## Validation Workflow

After extraction, the system validates keys by making test API calls to each service:

```mermaid
graph TB
    EXTRACT["parse_credentials_file()<br/>Extract keys from Access.txt"]
    
    subgraph "Validation"
        OPENAI["OpenAI: GET /v1/models"]
        ANTHROPIC["Anthropic: GET /v1/models"]
        RENDER["Render: GET /v1/services"]
        REDDIT["Reddit: POST /api/v1/access_token"]
        REPLICATE["Replicate: GET /v1/models"]
    end
    
    subgraph "Results"
        VALID["✓ OPENAI_API_KEY: Valid"]
        INVALID["✗ SUPABASE_URL: Not found"]
        REPORT["Validation Report"]
    end
    
    EXTRACT --> OPENAI
    EXTRACT --> ANTHROPIC
    EXTRACT --> RENDER
    EXTRACT --> REDDIT
    EXTRACT --> REPLICATE
    
    OPENAI --> VALID
    ANTHROPIC --> VALID
    RENDER --> VALID
    REDDIT --> VALID
    REPLICATE --> INVALID
    
    VALID --> REPORT
    INVALID --> REPORT
```

### Validation Commands

**OpenAI:**
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
# 200 = valid
```

**Anthropic/Claude:**
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  https://api.anthropic.com/v1/models
# 200 = valid
```

**Render:**
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services
# 200 = valid
```

**Reddit (OAuth token test):**
```bash
TOKEN=$(curl -s -X POST \
  -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
  -d "grant_type=client_credentials" \
  -A "CredentialTest/1.0" \
  https://www.reddit.com/api/v1/access_token | jq -r '.access_token')
# Non-null token = valid
```

The system outputs masked results (first 8 + last 4 characters) to prevent credential leakage during validation.

**Sources:** [skills/credentials.md:175-221]()

---

## Project Setup Workflow

The credential system integrates with `/initialize-project` to automate `.env` file creation:

```mermaid
sequenceDiagram
    participant User
    participant InitProject as "/initialize-project"
    participant Parser as "parse_credentials_file()"
    participant Validator as "Validation Commands"
    participant EnvGen as ".env Generator"
    participant Git as ".gitignore"
    
    User->>InitProject: Start project initialization
    InitProject->>User: "Provide Access.txt path"
    User->>InitProject: "~/Documents/Access.txt"
    
    InitProject->>Parser: Read and parse file
    Parser->>Parser: Apply regex patterns
    Parser->>InitProject: Return credentials dict
    
    InitProject->>User: Show found credentials (masked)
    InitProject->>Validator: Validate each key
    
    Validator->>Validator: curl test calls
    Validator->>InitProject: Validation results
    
    InitProject->>User: "✓ Valid / ✗ Missing"
    InitProject->>EnvGen: Create .env with valid keys
    EnvGen->>EnvGen: Write key=value pairs
    
    EnvGen->>Git: Add .env to .gitignore
    Git->>Git: Ensure .env not tracked
    
    InitProject->>User: "Missing: SUPABASE_URL<br/>Get from supabase.com/dashboard"
```

### Step-by-Step Process

#### Step 1: Prompt for Credentials File

```
This project needs the following API keys:
- ANTHROPIC_API_KEY (for Claude)
- SUPABASE_URL and SUPABASE_ANON_KEY

Do you have an access keys file? Please provide the path:
```

#### Step 2: Read and Parse

```python
credentials = parse_credentials_file("~/Documents/Access.txt")

# Show what was found (masked)
print("Found credentials:")
for key, value in credentials.items():
    masked = value[:8] + "..." + value[-4:]
    print(f"  {key}: {masked}")
```

#### Step 3: Validate Keys

```
Validating credentials...
✓ ANTHROPIC_API_KEY: Valid
✓ REDDIT_CLIENT_ID: Valid
✗ SUPABASE_URL: Not found in file
```

#### Step 4: Create .env File

```bash
cat > .env << EOF
# Auto-generated from ~/Documents/Access.txt
ANTHROPIC_API_KEY=sk-ant-xxx...
REDDIT_CLIENT_ID=xxx...
REDDIT_CLIENT_SECRET=xxx...
EOF

# Add to .gitignore if not present
echo ".env" >> .gitignore
```

#### Step 5: Report Missing Keys

```
Missing credentials that need manual setup:
- SUPABASE_URL: Get from supabase.com/dashboard/project/[ref]/settings/api
- SUPABASE_ANON_KEY: Same location as above

Would you like me to open these URLs?
```

**Sources:** [skills/credentials.md:226-280]()

---

## Service-Specific Handling

### Reddit (Paired Credentials)

Reddit requires both `client_id` and `client_secret` as a pair:

```
Found in your access file:
- REDDIT_CLIENT_ID: Y1FgKA...
- REDDIT_CLIENT_SECRET: -QLoYd...

Also needed (add to Access.txt or enter manually):
- REDDIT_USER_AGENT: YourApp/1.0 by YourUsername
```

The parser uses contextual search to find paired values:
```python
reddit_id = re.search(r'client.?id[:\s]+([A-Za-z0-9_-]+)', content, re.I)
reddit_secret = re.search(r'secret[:\s]+([A-Za-z0-9_-]+)', content, re.I)
```

**Sources:** [skills/credentials.md:129-136](), [skills/credentials.md:285-294]()

### Supabase (Project-Specific)

Supabase credentials are project-specific and typically not stored in `Access.txt`:

```
Supabase credentials are project-specific. Get them from:
https://supabase.com/dashboard/project/[your-ref]/settings/api

Required:
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY (for admin operations)
```

The system detects Supabase URLs and JWT tokens in the file, but prompts for manual entry if missing.

**Sources:** [skills/credentials.md:296-304]()

### Stripe (Environment-Specific Keys)

Stripe uses different key prefixes for test vs. live mode:

| Environment | Secret Key | Publishable Key |
|-------------|------------|-----------------|
| Test | `sk_test_*` | `pk_test_*` |
| Live | `sk_live_*` | `pk_live_*` |

The system extracts both and prompts the user to confirm which environment to use for the project.

**Sources:** [skills/credentials.md:74-76]()

---

## Integration with Skills

The credential patterns are referenced across multiple skills:

### PostHog Analytics

```python
# Pattern added to credentials.md
'POSTHOG_API_KEY': r'phc_[A-Za-z0-9]+',
```

PostHog uses the `phc_` prefix for API keys. The system extracts and validates these for analytics-enabled projects.

**Sources:** [skills/posthog-analytics.md:209-217](), [skills/credentials.md:109]()

### Stripe Payments

```python
# Patterns for Stripe keys
'STRIPE_SECRET_KEY': r'sk_(live|test)_[A-Za-z0-9]+',
'STRIPE_PUBLISHABLE_KEY': r'pk_(live|test)_[A-Za-z0-9]+',
'STRIPE_WEBHOOK_SECRET': r'whsec_[A-Za-z0-9]+',
```

The system detects all three Stripe key types (secret, publishable, webhook) and validates the secret key against the Stripe API.

**Sources:** [skills/web-payments.md:19-28](), [skills/credentials.md:106-108]()

---

## Security Rules

### Non-Negotiable Rules

1. **NEVER commit Access.txt or its path to git**
   - The file path is stored in memory only during initialization
   - No references to the path appear in committed files

2. **NEVER log full API keys - always mask**
   ```python
   masked = value[:8] + "..." + value[-4:]
   print(f"{key}: {masked}")
   ```

3. **ALWAYS add .env to .gitignore**
   - Automatically enforced during `.env` generation
   - Checked by pre-commit hooks (see [Secret Scanning](#6.3))

4. **ALWAYS use environment variables, never hardcode keys**
   - Credentials only flow to `.env`, never directly into code
   - Pattern detection catches accidental hardcoding

5. **VALIDATE keys before using them in production setup**
   - All keys tested against their respective APIs
   - Invalid keys reported before project setup completes

**Sources:** [skills/credentials.md:308-315]()

---

## Quick Reference

### Prompt Template

```
I need API credentials for this project.

Do you have a centralized access keys file (like ~/Documents/Access.txt)?

If yes, provide the path and I'll:
1. Read and parse your keys
2. Validate they're working
3. Set up your project's .env file
4. Tell you which keys are missing
```

### Common Environment Variable Names

```bash
# LLM Providers
OPENAI_API_KEY
ANTHROPIC_API_KEY
REPLICATE_API_TOKEN
ELEVEN_LABS_API_KEY

# Deployment
RENDER_API_KEY
VERCEL_TOKEN
GITHUB_TOKEN

# Database
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY

# Payment
STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET

# Analytics
POSTHOG_API_KEY
NEXT_PUBLIC_POSTHOG_KEY

# Advertising
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET
```

### File Check Command

```bash
# Check if credentials file exists
ls -la ~/Documents/Access.txt
```

**Sources:** [skills/credentials.md:318-349]()

---

## Workflow Summary

```mermaid
graph TB
    START["Project Initialization"]
    ASK["Prompt: 'Provide Access.txt path'"]
    READ["Read file content"]
    PARSE["Apply regex patterns<br/>parse_credentials_file()"]
    EXTRACT["Extract credentials dict"]
    VALIDATE["Validate via API calls"]
    MASK["Display masked results"]
    ENV["Generate .env file"]
    GIT["Add .env to .gitignore"]
    REPORT["Report missing keys"]
    DONE["Setup Complete"]
    
    START --> ASK
    ASK --> READ
    READ --> PARSE
    PARSE --> EXTRACT
    EXTRACT --> VALIDATE
    VALIDATE --> MASK
    MASK --> ENV
    ENV --> GIT
    VALIDATE --> REPORT
    REPORT --> DONE
    GIT --> DONE
```

**Sources:** [skills/credentials.md:226-280]()

---

# Page: Secret Scanning and Prevention

# Secret Scanning and Prevention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/credentials.md](skills/credentials.md)
- [skills/posthog-analytics.md](skills/posthog-analytics.md)
- [skills/web-payments.md](skills/web-payments.md)

</details>



**Purpose**: This document covers the technical implementation of secret detection and prevention mechanisms in Claude Bootstrap. It details pattern-based detection for API keys, client-side environment variable validation, pre-commit hooks, TruffleHog integration, and the blocker mechanisms that prevent secrets from entering the codebase.

**Related pages**: For the overall security architecture, see [Security Architecture](#6.1). For credentials management and Access.txt configuration, see [Credentials Management](#6.2).

---

## Overview: Multi-Layer Secret Detection

Claude Bootstrap implements a defense-in-depth approach to prevent secrets from entering version control. Detection occurs at four distinct layers, each with progressively broader scope and enforcement.

```mermaid
graph TB
    subgraph "Layer 1: Development-Time Detection"
        L1A["Pattern Validation<br/>(credentials.md patterns)"]
        L1B["Client Env Var Check<br/>(VITE_*, NEXT_PUBLIC_*)"]
        L1C[".env Generation<br/>+ .gitignore enforcement"]
    end
    
    subgraph "Layer 2: Pre-Commit Hook"
        L2A["security-check.sh"]
        L2B["Scan staged files<br/>for secret patterns"]
        L2C["Check .env not staged"]
        L2D["Validate .gitignore"]
    end
    
    subgraph "Layer 3: Pre-Push Hook"
        L3A["/code-review"]
        L3B["Security analysis<br/>of diff"]
        L3C["Block on Critical/High<br/>security issues"]
    end
    
    subgraph "Layer 4: CI/CD (GitHub Actions)"
        L4A["security.yml workflow"]
        L4B["TruffleHog<br/>full history scan"]
        L4C["Dependency audit<br/>(npm audit / safety)"]
    end
    
    CODE["Developer writes code<br/>with API keys"] --> L1A
    L1A --> L1B --> L1C
    L1C --> COMMIT["git add + git commit"]
    COMMIT --> L2A --> L2B --> L2C --> L2D
    L2D -->|Pass| PUSH["git push"]
    L2D -->|Fail| BLOCK1["❌ COMMIT BLOCKED"]
    PUSH --> L3A --> L3B --> L3C
    L3C -->|Pass| L4A
    L3C -->|Fail| BLOCK2["❌ PUSH BLOCKED"]
    L4A --> L4B --> L4C
    L4C -->|Pass| MERGE["✅ Merge allowed"]
    L4C -->|Fail| BLOCK3["❌ CI FAILED"]
    
    BLOCK1 --> FIX["Fix: Move to .env"]
    BLOCK2 --> FIX
    BLOCK3 --> FIX
    FIX --> CODE
```

**Sources**: [README.md:520-530](), [README.md:29-32](), [Diagram 5 from system overview]()

---

## Pattern-Based Secret Detection

### Supported Secret Patterns

Claude Bootstrap detects secrets using regex patterns that match known API key formats. These patterns are used across all detection layers.

| Service | Pattern | Example Match | Env Variable |
|---------|---------|---------------|--------------|
| OpenAI | `sk-proj-[A-Za-z0-9_-]+` | `sk-proj-abc123...` | `OPENAI_API_KEY` |
| Anthropic/Claude | `sk-ant-[A-Za-z0-9_-]+` | `sk-ant-xyz789...` | `ANTHROPIC_API_KEY` |
| Render | `rnd_[A-Za-z0-9]+` | `rnd_12345...` | `RENDER_API_KEY` |
| Replicate | `r8_[A-Za-z0-9]+` | `r8_abcde...` | `REPLICATE_API_TOKEN` |
| Eleven Labs | `sk_[a-f0-9]{40,}` | `sk_abc123def456...` | `ELEVEN_LABS_API_KEY` |
| GitHub | `ghp_[A-Za-z0-9]+` | `ghp_token123...` | `GITHUB_TOKEN` |
| Stripe (Test) | `sk_test_[A-Za-z0-9]+` | `sk_test_4eC39...` | `STRIPE_SECRET_KEY` |
| Stripe (Live) | `sk_live_[A-Za-z0-9]+` | `sk_live_4eC39...` | `STRIPE_SECRET_KEY` |
| Stripe Webhook | `whsec_[A-Za-z0-9]+` | `whsec_abc123...` | `STRIPE_WEBHOOK_SECRET` |
| PostHog | `phc_[A-Za-z0-9]+` | `phc_project123...` | `POSTHOG_API_KEY` |
| Supabase JWT | `eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` | `eyJhbGc...` | `SUPABASE_ANON_KEY` |
| Reddit Client ID | `[A-Za-z0-9_-]{14,}` | `Y1FgKALKmb6f6U...` | `REDDIT_CLIENT_ID` |
| Reddit Secret | `[A-Za-z0-9_-]{27,}` | `-QLoYdxMqOJkYr...` | `REDDIT_CLIENT_SECRET` |

**Sources**: [credentials.md:59-80](), [credentials.md:99-138]()

### Pattern Detection Flow

```mermaid
graph LR
    FILE["Source File<br/>(*.ts, *.py, *.js)"] --> SCAN["Scan file content"]
    SCAN --> REGEX["Apply regex patterns"]
    REGEX --> MATCH{Match found?}
    MATCH -->|Yes| CLASSIFY["Classify secret type"]
    MATCH -->|No| PASS["✅ No secrets"]
    
    CLASSIFY --> CHECK_CONTEXT["Check context"]
    CHECK_CONTEXT --> IN_COMMENT{In comment or<br/>example?}
    IN_COMMENT -->|Yes| WARN["⚠️ Warning only"]
    IN_COMMENT -->|No| CHECK_STRING{In string<br/>literal?}
    CHECK_STRING -->|Yes| BLOCK["❌ BLOCK commit"]
    CHECK_STRING -->|No| CHECK_VAR{Variable<br/>assignment?}
    CHECK_VAR -->|Yes| BLOCK
    CHECK_VAR -->|No| PASS
    
    BLOCK --> REPORT["Report:<br/>File, line, secret type"]
```

**Sources**: [credentials.md:88-138](), [credentials.md:307-314]()

### Implementation Example

The pattern detection logic follows this structure:

```mermaid
graph TB
    subgraph "Pattern Registry"
        PATTERNS["patterns = {<br/>'OPENAI_API_KEY': r'sk-proj-[A-Za-z0-9_-]+',<br/>'ANTHROPIC_API_KEY': r'sk-ant-[A-Za-z0-9_-]+',<br/>'STRIPE_SECRET_KEY': r'sk_(live|test)_[A-Za-z0-9]+',<br/>...}"]
    end
    
    subgraph "Detection Function"
        SCAN["scan_file(path)"]
        SCAN --> READ["content = read_file(path)"]
        READ --> ITERATE["for env_var, pattern in patterns.items()"]
        ITERATE --> SEARCH["match = re.search(pattern, content)"]
        SEARCH --> FOUND{match?}
        FOUND -->|Yes| EXTRACT["key = match.group(0)"]
        EXTRACT --> MASK["masked = key[:8] + '...' + key[-4:]"]
        MASK --> LOG["log: Found {env_var}: {masked}"]
        LOG --> RETURN_FAIL["return False"]
        FOUND -->|No| CONTINUE["continue"]
        CONTINUE --> ITERATE
        ITERATE -->|Done| RETURN_PASS["return True"]
    end
    
    PATTERNS --> SCAN
```

**Sources**: [credentials.md:88-172]()

---

## Client-Side Environment Variable Protection

### The Client-Side Secret Problem

Build tools like Vite and Next.js expose environment variables with specific prefixes to the client bundle. This creates a critical security risk: secrets in these variables become publicly accessible in the browser.

| Framework | Client-Exposed Prefix | Server-Only |
|-----------|----------------------|-------------|
| Next.js | `NEXT_PUBLIC_*` | All others |
| Vite | `VITE_*` | All others |
| Create React App | `REACT_APP_*` | All others |

**Critical rule**: Secret keys (API keys, database credentials, webhook secrets) must **never** use client-exposed prefixes.

**Sources**: [posthog-analytics.md:203-217](), [web-payments.md:18-28]()

### Safe vs Unsafe Environment Variables

```mermaid
graph TB
    subgraph "✅ SAFE: Client-Exposed (Public)"
        SAFE1["NEXT_PUBLIC_POSTHOG_KEY=phc_xxx<br/>✅ Analytics tracking ID"]
        SAFE2["NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx<br/>✅ Stripe publishable key"]
        SAFE3["VITE_API_URL=https://api.example.com<br/>✅ Public API endpoint"]
        SAFE4["NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co<br/>✅ Public database URL"]
        SAFE5["NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...<br/>✅ Row-level security enforced"]
    end
    
    subgraph "❌ UNSAFE: Server-Only (Secret)"
        UNSAFE1["NEXT_PUBLIC_OPENAI_API_KEY=sk-proj-xxx<br/>❌ API key exposed to browser"]
        UNSAFE2["VITE_STRIPE_SECRET_KEY=sk_test_xxx<br/>❌ Payment processing secret"]
        UNSAFE3["NEXT_PUBLIC_DATABASE_URL=postgresql://...<br/>❌ Database credentials"]
        UNSAFE4["VITE_WEBHOOK_SECRET=whsec_xxx<br/>❌ Webhook signature key"]
        UNSAFE5["NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-xxx<br/>❌ LLM API key"]
    end
    
    SAFE1 --> BROWSER["Compiled into<br/>client bundle"]
    SAFE2 --> BROWSER
    SAFE3 --> BROWSER
    SAFE4 --> BROWSER
    SAFE5 --> BROWSER
    
    UNSAFE1 --> EXPOSED["⚠️ SECURITY BREACH<br/>Anyone can extract<br/>from JS bundle"]
    UNSAFE2 --> EXPOSED
    UNSAFE3 --> EXPOSED
    UNSAFE4 --> EXPOSED
    UNSAFE5 --> EXPOSED
```

**Sources**: [posthog-analytics.md:203-217](), [web-payments.md:18-28](), [README.md:359-365]()

### Client-Side Variable Validation

The validation process checks for patterns indicating secrets in client-exposed variables:

```mermaid
graph TD
    ENV[".env file"] --> PARSE["Parse environment variables"]
    PARSE --> FILTER["Filter client-exposed<br/>(VITE_*, NEXT_PUBLIC_*, REACT_APP_*)"]
    FILTER --> CHECK_EACH["For each client-exposed variable"]
    
    CHECK_EACH --> CHECK_NAME{Variable name<br/>contains secret keyword?}
    CHECK_NAME -->|Yes: *KEY, *SECRET, *TOKEN, *PASSWORD| FAIL1["❌ FAIL: Name indicates secret"]
    CHECK_NAME -->|No| CHECK_PATTERN{"Value matches<br/>secret pattern?"}
    
    CHECK_PATTERN -->|Yes: sk-*, rnd_*, whsec_*, etc.| FAIL2["❌ FAIL: Value is secret"]
    CHECK_PATTERN -->|No| SAFE["✅ SAFE: Public value"]
    
    FAIL1 --> REPORT["Report violation:<br/>- Variable name<br/>- Pattern matched<br/>- Remediation steps"]
    FAIL2 --> REPORT
    
    REPORT --> BLOCK["Block commit"]
```

**Sources**: [credentials.md:59-80](), [README.md:359-365]()

---

## Pre-Commit Secret Scanning

### security-check.sh Script

The pre-commit hook executes `security-check.sh` to scan staged files before commit. This script is the first blocker mechanism.

```mermaid
graph TB
    HOOK["pre-commit hook<br/>(.git/hooks/pre-commit)"] --> EXEC["Execute security-check.sh"]
    
    EXEC --> CHECK1["Check 1: .env not staged"]
    CHECK1 --> STAGED{".env in<br/>git diff --cached?"}
    STAGED -->|Yes| FAIL1["❌ BLOCK: .env must not be committed"]
    STAGED -->|No| CHECK2["Check 2: .gitignore contains .env"]
    
    CHECK2 --> IGNORED{".env in<br/>.gitignore?"}
    IGNORED -->|No| FAIL2["❌ BLOCK: Add .env to .gitignore"]
    IGNORED -->|Yes| CHECK3["Check 3: Scan staged files for secrets"]
    
    CHECK3 --> DIFF["git diff --cached --name-only"]
    DIFF --> FILES["Filter: *.ts, *.js, *.py, *.tsx, *.jsx"]
    FILES --> SCAN["For each file:<br/>Apply secret patterns"]
    SCAN --> FOUND{Secrets found?}
    FOUND -->|Yes| FAIL3["❌ BLOCK: Secrets detected"]
    FOUND -->|No| CHECK4["Check 4: Validate env var names"]
    
    CHECK4 --> ENV_CHECK["Parse .env.local, .env.development"]
    ENV_CHECK --> CLIENT_VARS["Extract VITE_*, NEXT_PUBLIC_*"]
    CLIENT_VARS --> VALIDATE["Validate against secret patterns"]
    VALIDATE --> BAD_VAR{Secret in<br/>client var?}
    BAD_VAR -->|Yes| FAIL4["❌ BLOCK: Secret in client variable"]
    BAD_VAR -->|No| PASS["✅ All checks passed<br/>Commit allowed"]
    
    FAIL1 --> EXIT["Exit code 1<br/>Commit aborted"]
    FAIL2 --> EXIT
    FAIL3 --> EXIT
    FAIL4 --> EXIT
    PASS --> COMMIT["Commit proceeds"]
```

**Sources**: [README.md:520-523](), [Diagram 5 from system overview]()

### Pre-Commit Hook Installation

The hook is installed via `~/.claude/install-hooks.sh`:

```mermaid
graph LR
    SCRIPT["install-hooks.sh"] --> CHECK["Check .git directory exists"]
    CHECK --> COPY["Copy pre-commit hook<br/>to .git/hooks/pre-commit"]
    COPY --> CHMOD["chmod +x<br/>.git/hooks/pre-commit"]
    CHMOD --> LINK["Link to security-check.sh<br/>in project scripts/"]
    LINK --> VERIFY["Test hook execution"]
    VERIFY --> DONE["✅ Hook installed"]
```

**Sources**: [README.md:189-192]()

---

## CI/CD Secret Scanning with TruffleHog

### TruffleHog Integration

TruffleHog performs deep secret scanning in the CI/CD pipeline, checking the entire git history for secrets. This catches secrets that may have bypassed local checks.

```mermaid
graph TB
    subgraph "GitHub Actions: security.yml"
        TRIGGER["Trigger: push to main<br/>pull_request to main"]
        TRIGGER --> CHECKOUT["actions/checkout@v3<br/>fetch-depth: 0<br/>(full history)"]
        CHECKOUT --> TRUFFLEHOG["Run TruffleHog"]
    end
    
    subgraph "TruffleHog Execution"
        TRUFFLEHOG --> CONFIG["Load .trufflehog.yml<br/>or use defaults"]
        CONFIG --> SCAN_HISTORY["Scan entire git history<br/>git log --all"]
        SCAN_HISTORY --> SCAN_FILES["Scan file contents<br/>for entropy + patterns"]
        SCAN_FILES --> VERIFY["Verify detected secrets<br/>(API validation)"]
    end
    
    subgraph "Detection Methods"
        VERIFY --> ENTROPY["High entropy strings<br/>(randomness analysis)"]
        VERIFY --> PATTERNS["Regex patterns<br/>(API key formats)"]
        VERIFY --> VERIFICATION["API verification<br/>(test if key works)"]
    end
    
    ENTROPY --> FOUND{Secrets<br/>found?}
    PATTERNS --> FOUND
    VERIFICATION --> FOUND
    
    FOUND -->|Yes| REPORT["Generate report:<br/>- File path<br/>- Line number<br/>- Secret type<br/>- Commit hash"]
    FOUND -->|No| SUCCESS["✅ CI passes"]
    
    REPORT --> FAIL["❌ CI fails<br/>Block PR merge"]
```

**Sources**: [README.md:528](), [Diagram 5 from system overview]()

### TruffleHog Configuration

TruffleHog uses pattern matching and entropy analysis to detect secrets:

| Detection Method | Description | False Positive Rate |
|------------------|-------------|---------------------|
| **Regex patterns** | Matches known API key formats (sk-*, ghp_*, etc.) | Low |
| **Entropy analysis** | Detects high-randomness strings (base64, hex) | Medium |
| **API verification** | Tests if detected key works against actual API | Very Low |

**Sources**: [README.md:528]()

### GitHub Actions Workflow

The `security.yml` workflow configuration:

```mermaid
graph LR
    WORKFLOW["security.yml"] --> JOB1["Job: secret-scan"]
    JOB1 --> STEP1["Checkout code<br/>(full history)"]
    STEP1 --> STEP2["Install TruffleHog"]
    STEP2 --> STEP3["Run scan:<br/>trufflehog git file://. --only-verified"]
    STEP3 --> RESULT{Exit code}
    RESULT -->|0| PASS["✅ No secrets"]
    RESULT -->|Non-zero| FAIL["❌ Secrets found"]
    FAIL --> BLOCK["Block PR merge"]
```

**Sources**: [README.md:525-530]()

---

## Blocker Mechanisms

### Commit Blocker (Pre-Commit)

When the pre-commit hook detects secrets, it prevents the commit with detailed error output:

```mermaid
graph TB
    COMMIT_ATTEMPT["Developer runs:<br/>git commit -m 'message'"] --> HOOK["Pre-commit hook triggers"]
    HOOK --> SECURITY_CHECK["Execute security-check.sh"]
    
    SECURITY_CHECK --> DETECT["Detect secret in file:<br/>src/api/client.ts:15"]
    DETECT --> ANALYZE["Pattern matched:<br/>OPENAI_API_KEY: sk-proj-xxx..."]
    
    ANALYZE --> OUTPUT["Output to terminal:<br/>⚠️ SECURITY VIOLATION DETECTED<br/><br/>File: src/api/client.ts:15<br/>Secret: OPENAI_API_KEY<br/>Pattern: sk-proj-xyz...abc<br/><br/>❌ Commit blocked<br/><br/>Fix:<br/>1. Move key to .env file<br/>2. Add .env to .gitignore<br/>3. Use process.env.OPENAI_API_KEY"]
    
    OUTPUT --> EXIT_CODE["Exit with code 1"]
    EXIT_CODE --> ABORT["Commit aborted<br/>Working directory unchanged"]
```

**Sources**: [README.md:520-523]()

### Push Blocker (Pre-Push + Code Review)

The `/code-review` command analyzes security issues before push:

```mermaid
graph TB
    PUSH_ATTEMPT["Developer runs:<br/>git push"] --> PRE_PUSH["Pre-push hook triggers"]
    PRE_PUSH --> CODE_REVIEW["/code-review command"]
    
    CODE_REVIEW --> ANALYZE_DIFF["Analyze git diff origin/main...HEAD"]
    ANALYZE_DIFF --> SECURITY_SCAN["Security analysis:<br/>- Hardcoded secrets<br/>- SQL injection patterns<br/>- XSS vulnerabilities"]
    
    SECURITY_SCAN --> CLASSIFY["Classify severity"]
    CLASSIFY --> CRITICAL{Critical or<br/>High issues?}
    
    CRITICAL -->|Yes| REPORT_HIGH["Report:<br/>🔴 CRITICAL: API key in code<br/>File: src/config.ts:8<br/>Issue: ANTHROPIC_API_KEY hardcoded<br/><br/>🟠 HIGH: Database URL exposed<br/>File: src/db.ts:3<br/><br/>❌ PUSH BLOCKED"]
    CRITICAL -->|No| REPORT_LOW["Report:<br/>🟡 MEDIUM: Consider env var<br/>File: src/config.ts:12<br/><br/>✅ Push allowed"]
    
    REPORT_HIGH --> EXIT_1["Exit code 1"]
    EXIT_1 --> PUSH_BLOCKED["Push aborted"]
    
    REPORT_LOW --> EXIT_0["Exit code 0"]
    EXIT_0 --> PUSH_ALLOWED["Push proceeds"]
```

**Sources**: [README.md:176-209](), [Diagram 5 from system overview]()

### CI Blocker (GitHub Actions)

The CI/CD pipeline blocks PR merges when secrets are detected:

```mermaid
graph TB
    PR["Pull Request opened"] --> CI_TRIGGER["GitHub Actions triggered"]
    CI_TRIGGER --> QUALITY["quality.yml workflow"]
    CI_TRIGGER --> SECURITY["security.yml workflow"]
    
    SECURITY --> TRUFFLEHOG["TruffleHog scan"]
    TRUFFLEHOG --> AUDIT["npm audit / safety check"]
    
    TRUFFLEHOG --> RESULT1{Secrets<br/>found?}
    RESULT1 -->|Yes| FAIL_SECURITY["❌ security.yml fails"]
    RESULT1 -->|No| PASS_SECURITY["✅ security.yml passes"]
    
    QUALITY --> TESTS["Run tests"]
    TESTS --> COVERAGE["Check coverage ≥ 80%"]
    COVERAGE --> PASS_QUALITY["✅ quality.yml passes"]
    
    FAIL_SECURITY --> MERGE_BLOCKED["Status check failed<br/>❌ Merge blocked"]
    PASS_SECURITY --> ALL_CHECKS{"All workflows<br/>passed?"}
    PASS_QUALITY --> ALL_CHECKS
    
    ALL_CHECKS -->|Yes| MERGE_ALLOWED["✅ Merge allowed"]
    ALL_CHECKS -->|No| MERGE_BLOCKED
```

**Sources**: [README.md:525-530](), [Diagram 5 from system overview]()

---

## Common Secret Detection Scenarios

### Scenario 1: Hardcoded API Key in Source Code

```mermaid
graph LR
    CODE["File: src/api/openai.ts<br/><br/>const apiKey = 'sk-proj-abc123...'"] --> COMMIT["git commit"]
    COMMIT --> PRE_COMMIT["Pre-commit hook"]
    PRE_COMMIT --> SCAN["Scan src/api/openai.ts"]
    SCAN --> MATCH["Pattern matched:<br/>sk-proj-[A-Za-z0-9_-]+"]
    MATCH --> BLOCK["❌ BLOCKED<br/><br/>Move to .env:<br/>OPENAI_API_KEY=sk-proj-abc123...<br/><br/>Update code:<br/>const apiKey = process.env.OPENAI_API_KEY"]
```

**Sources**: [credentials.md:59-80]()

### Scenario 2: Secret in Client-Exposed Variable

```mermaid
graph LR
    ENV["File: .env.local<br/><br/>NEXT_PUBLIC_STRIPE_SECRET_KEY=sk_test_abc"] --> VALIDATE["Pre-commit validation"]
    VALIDATE --> CHECK_NAME["Name check:<br/>STRIPE_SECRET_KEY<br/>contains 'SECRET'"]
    CHECK_NAME --> CHECK_PREFIX["Prefix check:<br/>NEXT_PUBLIC_<br/>(client-exposed)"]
    CHECK_PREFIX --> CHECK_PATTERN["Pattern check:<br/>sk_test_<br/>(Stripe secret key)"]
    CHECK_PATTERN --> BLOCK["❌ BLOCKED<br/><br/>Secret key exposed to client!<br/><br/>Fix:<br/>1. Remove NEXT_PUBLIC_ prefix<br/>2. Use server-side only<br/><br/>For publishable key, use:<br/>NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xyz"]
```

**Sources**: [web-payments.md:18-28](), [posthog-analytics.md:203-217]()

### Scenario 3: .env File Accidentally Staged

```mermaid
graph LR
    STAGE["git add .env"] --> COMMIT["git commit"]
    COMMIT --> HOOK["Pre-commit hook"]
    HOOK --> CHECK["Check staged files"]
    CHECK --> FOUND[".env found in<br/>git diff --cached"]
    FOUND --> BLOCK["❌ BLOCKED<br/><br/>.env must never be committed<br/><br/>Fix:<br/>1. git reset HEAD .env<br/>2. Add to .gitignore<br/>3. Commit again"]
```

**Sources**: [README.md:520-523]()

### Scenario 4: Secret in Git History

```mermaid
graph LR
    HISTORY["Old commit:<br/>Added GITHUB_TOKEN=ghp_abc123<br/>(since removed)"] --> PR["Open pull request"]
    PR --> CI["CI runs TruffleHog"]
    CI --> SCAN_HISTORY["Scan all commits<br/>in PR branch"]
    SCAN_HISTORY --> FOUND["Found in commit abc123:<br/>GITHUB_TOKEN=ghp_abc123"]
    FOUND --> BLOCK["❌ CI BLOCKED<br/><br/>Secret in git history!<br/><br/>Fix:<br/>1. git rebase -i<br/>2. Remove secret from history<br/>3. Force push<br/>4. Rotate compromised key"]
```

**Sources**: [README.md:528]()

---

## Anti-Patterns and Remediation

### Common Mistakes

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|--------------|----------------|-----------------|
| `const key = "sk-proj-abc123"` | Hardcoded secret in source | `const key = process.env.OPENAI_API_KEY` |
| `NEXT_PUBLIC_API_KEY="secret"` | Secret exposed to client | `API_KEY="secret"` (server-only) |
| Committing `.env` file | Secrets in git history | Add `.env` to `.gitignore` |
| Commented-out secrets | Still detectable by scanners | Remove entirely, use examples |
| Secrets in test files | Test code gets committed | Use mocks or test-specific keys |
| Rotating key, not history | Old key still in git | Rewrite history with `git filter-branch` |

**Sources**: [credentials.md:307-314](), [README.md:359-365]()

### Remediation Workflow

```mermaid
graph TB
    DETECTED["Secret detected<br/>in commit or PR"] --> IMMEDIATE["IMMEDIATE:<br/>1. Rotate compromised key"]
    IMMEDIATE --> ASSESS["ASSESS EXPOSURE:<br/>- In git history?<br/>- Already pushed?<br/>- PR opened?"]
    
    ASSESS --> LOCAL{Only in<br/>local commits?}
    LOCAL -->|Yes| REBASE["Fix:<br/>git rebase -i<br/>Remove secret from commit"]
    LOCAL -->|No| REMOTE{Pushed to<br/>remote?}
    
    REMOTE -->|Yes| FORCE_PUSH["Fix:<br/>1. Rewrite history<br/>2. git push --force<br/>3. Notify team"]
    REMOTE -->|No| REBASE
    
    REBASE --> MOVE_ENV["Move secret to .env"]
    FORCE_PUSH --> MOVE_ENV
    
    MOVE_ENV --> UPDATE_CODE["Update code to use<br/>process.env.SECRET_NAME"]
    UPDATE_CODE --> VERIFY["Verify:<br/>1. No patterns matched<br/>2. .env in .gitignore<br/>3. Tests pass"]
    VERIFY --> COMMIT_CLEAN["Commit clean version"]
```

**Sources**: [credentials.md:307-314]()

---

## Quick Reference

### Secret Pattern Regex

```markdown
| Service | Regex Pattern |
|---------|---------------|
| OpenAI | `sk-proj-[A-Za-z0-9_-]+` |
| Anthropic | `sk-ant-[A-Za-z0-9_-]+` |
| GitHub | `ghp_[A-Za-z0-9]+` |
| Stripe Secret | `sk_(live|test)_[A-Za-z0-9]+` |
| Stripe Webhook | `whsec_[A-Za-z0-9]+` |
```

**Sources**: [credentials.md:59-80]()

### Client-Exposed Prefixes (NEVER for secrets)

- `NEXT_PUBLIC_*` (Next.js)
- `VITE_*` (Vite)
- `REACT_APP_*` (Create React App)

**Sources**: [posthog-analytics.md:203-217]()

### Validation Commands

```bash
# Check for secrets in staged files
git diff --cached | grep -E "sk-proj-|sk-ant-|ghp_|whsec_"

# Check for .env in staging area
git diff --cached --name-only | grep "^\.env$"

# Scan with TruffleHog locally
trufflehog git file://. --only-verified

# Test pre-commit hook
.git/hooks/pre-commit
```

**Sources**: [credentials.md:175-223]()

### Hook Installation

```bash
# Install pre-commit and pre-push hooks
~/.claude/install-hooks.sh

# Verify installation
ls -la .git/hooks/pre-commit .git/hooks/pre-push
```

**Sources**: [README.md:189-192]()

---

# Page: Integration Skills

# Integration Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/credentials.md](skills/credentials.md)
- [skills/posthog-analytics.md](skills/posthog-analytics.md)
- [skills/web-payments.md](skills/web-payments.md)

</details>



## Purpose and Scope

Integration Skills provide standardized patterns for connecting Claude Bootstrap projects to external services. These skills cover API authentication, error handling, testing strategies, and service-specific best practices for analytics platforms, payment processors, e-commerce systems, and advertising APIs.

This page provides an overview of the integration skills architecture and credential management system. For detailed implementation guides, see:
- [Analytics with PostHog](#7.1)
- [Payment Processing with Stripe](#7.2)
- [E-commerce Platforms](#7.3)
- [Reddit Ads Integration](#7.4)

For general skills system architecture, see [Skills Architecture](#5.1).

---

## Integration Skills in the Skills System

Integration skills are conditionally loaded during project initialization based on user selections and detected project requirements. Unlike core skills (which load for every project) or language skills (which load based on technology stack), integration skills are opt-in selections for specific third-party services.

**Skills Hierarchy: Integration Skills Layer**

```mermaid
graph TB
    subgraph "Skills Loading Flow"
        INIT["initialize-project command"]
        DETECT["Detect Stack<br/>Language + Framework"]
        PROMPT["Prompt for Integrations<br/>Analytics? Payments? Ads?"]
        SELECT["Select Integration Skills"]
    end
    
    subgraph "Core Skills (Always Loaded)"
        BASE["base.md"]
        SECURITY["security.md"]
        CREDS["credentials.md"]
    end
    
    subgraph "Language Skills (Conditional)"
        PYTHON["python.md"]
        TYPESCRIPT["typescript.md"]
    end
    
    subgraph "Integration Skills (Opt-in)"
        POSTHOG["posthog-analytics.md"]
        STRIPE["web-payments.md"]
        REDDIT["reddit-api.md<br/>reddit-ads.md"]
        ECOM["medusa.md<br/>klaviyo.md<br/>woocommerce.md"]
        SUPA["supabase*.md"]
    end
    
    subgraph "Project Skills Directory"
        PROJECT[".claude/skills/<br/>Copied & Active"]
    end
    
    INIT --> DETECT
    DETECT --> PROMPT
    PROMPT --> SELECT
    
    BASE --> PROJECT
    SECURITY --> PROJECT
    CREDS --> PROJECT
    
    PYTHON --> PROJECT
    TYPESCRIPT --> PROJECT
    
    SELECT -->|If PostHog| POSTHOG
    SELECT -->|If Payments| STRIPE
    SELECT -->|If Reddit Ads| REDDIT
    SELECT -->|If E-commerce| ECOM
    SELECT -->|If Supabase| SUPA
    
    POSTHOG --> PROJECT
    STRIPE --> PROJECT
    REDDIT --> PROJECT
    ECOM --> PROJECT
    SUPA --> PROJECT
```

**Sources:** [README.md:396-466](), [skills/credentials.md:1-349]()

---

## Centralized Credential Management

Integration skills rely on the centralized credential system defined in `credentials.md`. Instead of manually creating `.env` files, users maintain a single access file (typically `~/Documents/Access.txt`) containing all API keys.

**Credential Flow: Access.txt to Project .env**

```mermaid
graph LR
    subgraph "User's System"
        ACCESS["~/Documents/Access.txt<br/>Centralized Keys"]
    end
    
    subgraph "Initialization Process"
        ASK["initialize-project<br/>asks for access file path"]
        PARSE["parse_credentials_file()<br/>Extract keys by pattern"]
        VALIDATE["Validation Commands<br/>curl to test APIs"]
        DETECT["Auto-detect Service<br/>by key pattern"]
    end
    
    subgraph "Project Files"
        ENV[".env<br/>Project-specific keys"]
        GITIGNORE[".gitignore<br/>Ensure .env excluded"]
    end
    
    ACCESS --> ASK
    ASK --> PARSE
    PARSE --> DETECT
    DETECT --> VALIDATE
    VALIDATE --> ENV
    ENV --> GITIGNORE
```

**Sources:** [skills/credentials.md:9-27](), [skills/credentials.md:59-139]()

### Key Identification Patterns

The credential parsing system uses regex patterns to auto-detect services:

| Service | Pattern | Environment Variable |
|---------|---------|---------------------|
| **PostHog** | `phc_[A-Za-z0-9]+` | `POSTHOG_API_KEY`, `NEXT_PUBLIC_POSTHOG_KEY` |
| **Stripe (Test)** | `sk_test_*`, `pk_test_*` | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` |
| **Stripe (Live)** | `sk_live_*`, `pk_live_*` | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` |
| **Stripe Webhook** | `whsec_*` | `STRIPE_WEBHOOK_SECRET` |
| **Reddit** | client_id + secret pair | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` |
| **OpenAI** | `sk-proj-*` or `sk-*` | `OPENAI_API_KEY` |
| **Anthropic/Claude** | `sk-ant-*` | `ANTHROPIC_API_KEY` |
| **Supabase** | URL + `eyJ*` (JWT) | `SUPABASE_URL`, `SUPABASE_ANON_KEY` |

**Sources:** [skills/credentials.md:59-81](), [skills/posthog-analytics.md:213-217](), [skills/web-payments.md:19-28]()

### Validation Workflow

After extracting keys, the system validates them before generating `.env`:

```mermaid
graph TB
    EXTRACT["Extracted Keys<br/>from Access.txt"]
    
    subgraph "Validation by Service"
        V_POSTHOG["curl POST /v1/models<br/>200 = valid"]
        V_STRIPE["curl GET /v1/customers<br/>200 = valid"]
        V_REDDIT["curl POST /api/v1/access_token<br/>token present = valid"]
        V_OPENAI["curl GET /v1/models<br/>200 = valid"]
    end
    
    REPORT["Validation Report<br/>✓ Valid | ✗ Missing"]
    GENERATE[".env Generation<br/>with validated keys"]
    MISSING["Missing Keys Report<br/>URLs to obtain them"]
    
    EXTRACT --> V_POSTHOG
    EXTRACT --> V_STRIPE
    EXTRACT --> V_REDDIT
    EXTRACT --> V_OPENAI
    
    V_POSTHOG --> REPORT
    V_STRIPE --> REPORT
    V_REDDIT --> REPORT
    V_OPENAI --> REPORT
    
    REPORT --> GENERATE
    REPORT --> MISSING
```

**Sources:** [skills/credentials.md:175-223](), [skills/credentials.md:226-280]()

---

## Available Integration Skills

Claude Bootstrap includes integration skills across four categories:

### Analytics

| Skill | Service | Key Features |
|-------|---------|--------------|
| `posthog-analytics.md` | PostHog | Event tracking, feature flags, user identification, dashboards |

**Core capabilities:**
- Client/server-side event tracking
- User lifecycle analytics (acquisition → activation → retention → revenue)
- A/B testing with feature flags
- Project-specific dashboard templates
- GDPR compliance patterns

**Sources:** [skills/posthog-analytics.md:1-950](), [README.md:461]()

### Payments

| Skill | Service | Key Features |
|-------|---------|--------------|
| `web-payments.md` | Stripe | Checkout, subscriptions, webhooks, customer portal |

**Core capabilities:**
- Stripe Checkout (hosted and embedded)
- Subscription management with trials
- Webhook verification and idempotency
- Customer billing portal
- Test card patterns

**Sources:** [skills/web-payments.md:1-659](), [README.md:457]()

### E-commerce

| Skill | Service | Key Features |
|-------|---------|--------------|
| `medusa.md` | Medusa | Headless commerce, modules, workflows |
| `klaviyo.md` | Klaviyo | Email/SMS marketing, profiles, events, flows |
| `woocommerce.md` | WooCommerce | REST API, products, orders, webhooks |
| `shopify-apps.md` | Shopify | App development, Remix, Admin API, GDPR |

**Core capabilities:**
- Product and order management APIs
- Webhook handling for order events
- Customer segmentation and marketing automation
- Cart abandonment flows
- GDPR data export/deletion

**Sources:** [README.md:462-465]()

### Advertising

| Skill | Service | Key Features |
|-------|---------|--------------|
| `reddit-api.md` | Reddit API | PRAW (Python), Snoowrap (Node.js), OAuth |
| `reddit-ads.md` | Reddit Ads API | Campaigns, targeting, conversions, agentic optimizer |

**Core capabilities:**
- Campaign hierarchy (Account → Campaign → Ad Group → Ad)
- Audience targeting and conversion tracking
- Automated bid optimization
- Agentic service for multi-campaign management
- Budget pacing and creative rotation

**Sources:** [README.md:458-459](), [README.md:149-174]()

---

## Integration Skill Selection

During `initialize-project`, Claude prompts for integration needs and copies relevant skills to `.claude/skills/`:

**Integration Selection Decision Flow**

```mermaid
graph TB
    START["initialize-project"]
    STACK["Stack Questions<br/>Language, Framework, DB"]
    
    Q_ANALYTICS{"Need Analytics?"}
    Q_PAYMENTS{"Need Payments?"}
    Q_ECOM{"E-commerce Platform?"}
    Q_ADS{"Advertising Platform?"}
    
    COPY_POSTHOG["Copy posthog-analytics.md"]
    COPY_STRIPE["Copy web-payments.md"]
    COPY_MEDUSA["Copy medusa.md"]
    COPY_KLAVIYO["Copy klaviyo.md"]
    COPY_WOO["Copy woocommerce.md"]
    COPY_REDDIT["Copy reddit-api.md<br/>reddit-ads.md"]
    
    CREDS["Prompt for Access.txt"]
    VALIDATE["Validate & Generate .env"]
    COMPLETE["Skills Loaded"]
    
    START --> STACK
    STACK --> Q_ANALYTICS
    
    Q_ANALYTICS -->|Yes| COPY_POSTHOG
    Q_ANALYTICS -->|No| Q_PAYMENTS
    COPY_POSTHOG --> Q_PAYMENTS
    
    Q_PAYMENTS -->|Yes| COPY_STRIPE
    Q_PAYMENTS -->|No| Q_ECOM
    COPY_STRIPE --> Q_ECOM
    
    Q_ECOM -->|Medusa| COPY_MEDUSA
    Q_ECOM -->|WooCommerce| COPY_WOO
    Q_ECOM -->|Marketing| COPY_KLAVIYO
    Q_ECOM -->|None| Q_ADS
    COPY_MEDUSA --> Q_ADS
    COPY_WOO --> Q_ADS
    COPY_KLAVIYO --> Q_ADS
    
    Q_ADS -->|Reddit| COPY_REDDIT
    Q_ADS -->|None| CREDS
    COPY_REDDIT --> CREDS
    
    CREDS --> VALIDATE
    VALIDATE --> COMPLETE
```

**Sources:** [README.md:64-69](), [skills/credentials.md:226-280]()

---

## Common Integration Patterns

Integration skills share architectural patterns for authentication, error handling, testing, and security.

### Authentication Architecture

All integration skills follow a consistent authentication pattern:

```mermaid
graph TB
    subgraph "Server-Side (Secure)"
        SECRET["Environment Variables<br/>*_SECRET_KEY, *_API_KEY"]
        SERVER["Backend API Routes<br/>/api/checkout, /api/webhooks"]
        VALIDATE["API Call Validation<br/>Signature verification"]
    end
    
    subgraph "Client-Side (Public)"
        PUBLIC["Public Environment Variables<br/>NEXT_PUBLIC_*, VITE_*"]
        CLIENT["Frontend Components<br/>CheckoutButton, AnalyticsProvider"]
        SDK["Client SDKs<br/>@stripe/stripe-js, posthog-js"]
    end
    
    subgraph "External Service"
        API["Service API<br/>Stripe, PostHog, Reddit"]
    end
    
    SECRET --> SERVER
    SERVER --> VALIDATE
    VALIDATE --> API
    
    PUBLIC --> CLIENT
    CLIENT --> SDK
    SDK --> API
    
    API -->|Webhooks| SERVER
```

**Key principles:**
- Secret keys (`STRIPE_SECRET_KEY`, `POSTHOG_API_KEY`) only on server
- Public keys (`NEXT_PUBLIC_*`, `VITE_*`) safe for client
- All critical operations server-side with validation
- Webhook signature verification mandatory

**Sources:** [skills/web-payments.md:19-28](), [skills/posthog-analytics.md:203-217](), [skills/credentials.md:308-315]()

### Error Classification

Integration skills implement consistent error handling:

| Error Type | Examples | Auto-Retry? | Action |
|------------|----------|-------------|--------|
| **Transient** | Rate limit, network timeout | Yes | Exponential backoff |
| **Client Error** | Invalid parameters, malformed request | No | Fix and retry |
| **Auth Error** | Invalid key, expired token | No | Validate credentials |
| **Service Error** | API down, maintenance | Yes | Alert and queue |

**Sources:** [README.md:579-612](), [skills/web-payments.md:613-622]()

### Testing Patterns

#### Test Mode Keys

All integrations provide test mode credentials:

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_xxx  # Server
STRIPE_PUBLISHABLE_KEY=pk_test_xxx  # Client

# PostHog
POSTHOG_API_KEY=phc_xxx  # Same key, filter by environment
```

**Sources:** [skills/web-payments.md:455-477](), [skills/posthog-analytics.md:809-817]()

#### Integration Test Patterns

```typescript
// Mock external service in E2E tests
test.extend({
  page: async ({ page }, use) => {
    await page.addInitScript(() => {
      window.posthog = {
        capture: (event, props) => {
          window.capturedEvents.push({ event, props });
        },
      };
    });
    await use(page);
  },
});
```

**Sources:** [skills/posthog-analytics.md:820-854]()

#### Webhook Testing

```bash
# Stripe CLI for local webhook testing
stripe listen --forward-to localhost:3000/api/webhooks/stripe
stripe trigger checkout.session.completed
```

**Sources:** [skills/web-payments.md:463-477]()

### Security Requirements

Integration skills enforce these non-negotiable security rules:

1. **No secrets in client environment variables**
   - ❌ `VITE_STRIPE_SECRET_KEY` (never expose)
   - ✅ `VITE_STRIPE_PUBLISHABLE_KEY` (safe, intended for client)

2. **Always verify webhooks**
   ```typescript
   // Verify signature before processing
   const event = stripe.webhooks.constructEvent(
     body, 
     signature, 
     webhookSecret
   );
   ```

3. **Idempotent webhook handlers**
   - Store processed event IDs
   - Skip duplicate deliveries
   - Use database transactions

4. **Input sanitization**
   ```typescript
   const SENSITIVE_KEYS = ['password', 'token', 'secret'];
   function sanitizeProperties(props: Record<string, any>) {
     return Object.fromEntries(
       Object.entries(props).filter(([key]) =>
         !SENSITIVE_KEYS.some(s => key.toLowerCase().includes(s))
       )
     );
   }
   ```

**Sources:** [skills/web-payments.md:508-533](), [skills/posthog-analytics.md:766-803](), [skills/credentials.md:308-315]()

---

## Integration Skill File Structure

Integration skill files follow a consistent format:

```markdown
# [Service Name] Skill

*Load with: base.md + [framework].md*

Purpose statement and official docs links

---

## Setup
- Installation commands
- Environment variables
- Initial configuration

## Core Patterns
- Authentication
- Common operations
- Error handling

## Testing
- Test mode setup
- Test data/cards
- E2E patterns

## Security
- Secret management
- Validation requirements
- Common vulnerabilities

## Quick Reference
- Command cheat sheet
- Key endpoints/methods
- Troubleshooting
```

**Example files:**
- [skills/posthog-analytics.md:1-950]()
- [skills/web-payments.md:1-659]()

---

## Adding New Integration Skills

To add a new integration skill to Claude Bootstrap:

### 1. Create Skill File

Create `skills/[service-name].md` following the standard structure:

```markdown
# [Service] Integration Skill

*Load with: base.md + [framework].md*

For integrating [service] - [brief description].

**Sources:** [Official Docs Link]

---

## Setup
[Installation and configuration]

## Authentication
[How to get and use API keys]

## Core Patterns
[Common use cases with code examples]

## Testing
[Test mode, fixtures, E2E]

## Security
[Service-specific security rules]

## Quick Reference
[Command/API cheat sheet]
```

### 2. Add Credential Patterns

Update `credentials.md` to auto-detect the service's API keys:

```python
# Add to patterns dict
patterns = {
    'SERVICE_API_KEY': r'service-key-pattern',
}
```

**Sources:** [skills/credentials.md:88-138]()

### 3. Add Validation Command

Add validation endpoint check:

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $SERVICE_API_KEY" \
  https://api.service.com/v1/verify
```

**Sources:** [skills/credentials.md:175-223]()

### 4. Update Initialization Prompt

Add service to integration selection prompts in initialization workflow.

### 5. Document in README

Add to the Integration Skills table:

```markdown
| `[service].md` | [Service] | [Key features] |
```

**Sources:** [README.md:454-466]()

---

## Quick Reference

### Integration Skills by Category

| Category | Skills | API Key Pattern |
|----------|--------|-----------------|
| **Analytics** | `posthog-analytics.md` | `phc_*` |
| **Payments** | `web-payments.md` | `sk_test_*`, `pk_test_*`, `whsec_*` |
| **E-commerce** | `medusa.md`, `klaviyo.md`, `woocommerce.md`, `shopify-apps.md` | Service-specific |
| **Advertising** | `reddit-api.md`, `reddit-ads.md` | client_id + secret |

### Common Commands

```bash
# Update integration skills globally
cd ~/.claude-bootstrap && git pull && ./install.sh

# Re-initialize project with new integrations
claude
> /initialize-project

# Validate credentials
ls -la ~/Documents/Access.txt

# Test webhooks locally (Stripe)
stripe listen --forward-to localhost:3000/api/webhooks/stripe
```

### Environment Variable Prefixes

| Prefix | Exposure | Use Case |
|--------|----------|----------|
| `NEXT_PUBLIC_*` | Client-safe | Next.js public keys |
| `VITE_*` | Client-safe | Vite public keys |
| `REACT_APP_*` | Client-safe | CRA public keys |
| _(no prefix)_ | Server-only | Secret keys, tokens |

**Sources:** [skills/credentials.md:308-315](), [skills/posthog-analytics.md:203-217](), [skills/web-payments.md:19-28]()

---

# Page: Analytics with PostHog

# Analytics with PostHog

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/credentials.md](skills/credentials.md)
- [skills/posthog-analytics.md](skills/posthog-analytics.md)
- [skills/web-payments.md](skills/web-payments.md)

</details>



## Purpose and Scope

This document covers PostHog analytics integration within Claude Bootstrap projects. PostHog provides product analytics, feature flags, and session replay capabilities. The skill enforces event tracking conventions, privacy-first defaults, and project-specific dashboard creation patterns.

For payment analytics integration, see [Payment Processing with Stripe](#7.2). For general credentials management including PostHog API keys, see [Credentials Management](#6.2).

**Sources:** [skills/posthog-analytics.md:1-950]()

---

## Integration Architecture

PostHog integrates as both a client-side tracker (for user interactions) and server-side tracker (for backend events). The system supports Next.js App Router, React (Vite/CRA), Python (FastAPI), and Node.js backends.

### PostHog System Overview

```mermaid
graph TB
    subgraph "Client-Side Tracking"
        INIT["initPostHog()<br/>lib/posthog.ts"]
        PROVIDER["PostHogProvider<br/>app/providers.tsx"]
        CAPTURE["posthog.capture()"]
        IDENTIFY["posthog.identify()"]
        FLAGS["useFeatureFlagEnabled()"]
    end
    
    subgraph "Server-Side Tracking"
        NODE["PostHog Node Client<br/>posthog-node"]
        PYTHON["PostHog Python Client<br/>get_posthog()"]
        TRACK["trackEvent()"]
        SERVER_ID["identifyUser()"]
    end
    
    subgraph "Configuration"
        ENV_PUBLIC["NEXT_PUBLIC_POSTHOG_KEY<br/>phc_*"]
        ENV_PRIVATE["POSTHOG_API_KEY<br/>phc_*"]
        ACCESS["Access.txt<br/>Credential Source"]
        CREDS["credentials.md<br/>Pattern: phc_[A-Za-z0-9]+"]
    end
    
    subgraph "PostHog Cloud"
        API["PostHog API<br/>us.i.posthog.com"]
        DASHBOARDS["Dashboards"]
        FEATURES["Feature Flags"]
        EVENTS["Event Storage"]
    end
    
    INIT --> PROVIDER
    PROVIDER --> CAPTURE
    PROVIDER --> IDENTIFY
    PROVIDER --> FLAGS
    
    ACCESS --> CREDS
    CREDS --> ENV_PUBLIC
    CREDS --> ENV_PRIVATE
    
    ENV_PUBLIC --> INIT
    ENV_PRIVATE --> NODE
    ENV_PRIVATE --> PYTHON
    
    NODE --> TRACK
    NODE --> SERVER_ID
    
    CAPTURE --> API
    IDENTIFY --> API
    TRACK --> API
    SERVER_ID --> API
    FLAGS --> API
    
    API --> EVENTS
    API --> FEATURES
    EVENTS --> DASHBOARDS
```

**Sources:** [skills/posthog-analytics.md:27-103](), [skills/posthog-analytics.md:131-197](), [skills/credentials.md:80]()

---

## Installation and Configuration

### Package Installation

PostHog requires different packages depending on the environment:

| Environment | Package | Purpose |
|-------------|---------|---------|
| Next.js/React | `posthog-js` | Client-side tracking |
| Python | `posthog` | Server-side tracking |
| Node.js | `posthog-node` | Server-side tracking |

**Sources:** [skills/posthog-analytics.md:27-31](), [skills/posthog-analytics.md:132-135](), [skills/posthog-analytics.md:164-167]()

### Environment Variables

The system requires separate API keys for client and server contexts:

```bash
# Client-side (SAFE - meant to be public)
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com

# Server-side (PRIVATE)
POSTHOG_API_KEY=phc_xxxxxxxxxxxxxxxxxxxx
POSTHOG_HOST=https://us.i.posthog.com
```

The credential pattern `phc_[A-Za-z0-9]+` is recognized by the credentials management system and can be auto-extracted from `Access.txt`.

**Sources:** [skills/posthog-analytics.md:203-217](), [skills/credentials.md:80](), [skills/credentials.md:109]()

### Next.js Initialization

The initialization pattern uses a singleton client with manual pageview tracking for SPA routing:

```typescript
// lib/posthog.ts structure
export function initPostHog() {
  if (typeof window !== 'undefined' && !posthog.__loaded) {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
      person_profiles: 'identified_only',  // GDPR-friendly: only track identified users
      capture_pageview: false,             // Manual control for SPA
      capture_pageleave: true,
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') {
          posthog.debug();
        }
      },
    });
  }
  return posthog;
}
```

The `PostHogProvider` component handles automatic pageview tracking on route changes using Next.js navigation hooks.

**Sources:** [skills/posthog-analytics.md:34-103]()

### Backend Initialization

Server-side clients require explicit shutdown handling:

| Backend | Initialization Pattern | Shutdown |
|---------|----------------------|----------|
| **Python** | `@lru_cache()` decorator on `get_posthog()` | Automatic |
| **Node.js** | Singleton with `new PostHog()` | `process.on('SIGTERM')` |

**Sources:** [skills/posthog-analytics.md:137-161](), [skills/posthog-analytics.md:169-196]()

---

## Event Tracking System

### Event Flow Architecture

```mermaid
sequenceDiagram
    participant U as "User Action"
    participant C as "Component<br/>CheckoutButton"
    participant H as "useTrack()<br/>hooks/useTrack.ts"
    participant P as "posthog.capture()"
    participant A as "PostHog API"
    participant D as "Dashboard"
    
    U->>C: Click "Subscribe"
    C->>H: track('checkout_started')
    H->>H: Add timestamp
    H->>P: capture(event, properties)
    P->>A: Send event payload
    A->>D: Update insights
    
    Note over C,H: Frontend Tracking
    Note over P,A: SDK Layer
    Note over A,D: PostHog Cloud
```

**Sources:** [skills/posthog-analytics.md:414-451]()

### Event Naming Convention

The system enforces `[object]_[action]` format with snake_case and past tense:

| ✅ Valid | ❌ Invalid | Reason |
|---------|-----------|---------|
| `user_signed_up` | `click` | Too vague |
| `feature_created` | `ButtonClick` | Not snake_case |
| `subscription_upgraded` | `user signup` | Contains spaces |
| `onboarding_completed` | `creatingFeature` | Not past tense |

**Sources:** [skills/posthog-analytics.md:296-317]()

### Core Event Categories

The skill defines standard events by user lifecycle stage:

```mermaid
graph LR
    AUTH["Authentication Events<br/>user_signed_up<br/>user_logged_in<br/>user_logged_out"]
    ONBOARD["Onboarding Events<br/>onboarding_started<br/>onboarding_step_completed<br/>onboarding_completed"]
    FEATURE["Feature Usage<br/>feature_used<br/>[resource]_created<br/>[resource]_updated"]
    BILLING["Billing Events<br/>checkout_started<br/>subscription_upgraded<br/>subscription_cancelled"]
    ERROR["Error Tracking<br/>error_occurred"]
    
    AUTH --> ONBOARD
    ONBOARD --> FEATURE
    FEATURE --> BILLING
    FEATURE --> ERROR
```

**Sources:** [skills/posthog-analytics.md:319-410]()

### React Tracking Hook

The `useTrack()` hook provides a consistent interface with automatic timestamp enrichment:

```typescript
// hooks/useTrack.ts pattern
export function useTrack() {
  const track = useCallback((event: string, properties?: Record<string, any>) => {
    posthog.capture(event, {
      ...properties,
      timestamp: new Date().toISOString(),
    });
  }, []);
  return { track };
}
```

Usage in components follows try-catch pattern with error tracking:

```typescript
const { track } = useTrack();

const handleCreate = async () => {
  track('project_creation_started');
  try {
    const project = await createProject();
    track('project_created', { project_id: project.id });
  } catch (error) {
    track('project_creation_failed', { error_message: error.message });
  }
};
```

**Sources:** [skills/posthog-analytics.md:414-451]()

---

## User Identification

### Identification Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Anonymous: "Initial Visit"
    Anonymous --> Identified: "posthog.identify(user.id, props)"
    Identified --> Identified: "posthog.capture('$set', props)"
    Identified --> Anonymous: "posthog.reset()"
    Anonymous --> [*]: "Session End"
    
    note right of Identified
        Properties tracked:
        - email, name
        - plan, created_at
        - onboarding_completed
        - feature_count
    end note
```

The system identifies users at three critical points:

| Trigger | Action | Properties |
|---------|--------|------------|
| **Signup** | `posthog.identify(user.id, {...})` | `email`, `name`, `created_at`, `plan: 'free'`, `signup_method` |
| **Login** | `posthog.identify(user.id, {...})` | `email`, `name`, `plan`, `last_login` |
| **Logout** | `posthog.reset()` | Clears identity |

**Sources:** [skills/posthog-analytics.md:220-289]()

### Property Updates

User properties are updated using the `$set` event:

```typescript
// Update properties when they change
posthog.capture('$set', {
  $set: { plan: 'pro' },
});
```

The `UserProperties` interface defines standard trackable properties:

- **Identity**: `email`, `name`
- **Lifecycle**: `created_at`, `plan`
- **Engagement**: `onboarding_completed`, `feature_count`
- **Business**: `company_name`, `company_size`, `industry`

**Sources:** [skills/posthog-analytics.md:262-289]()

---

## Feature Flags

### Client-Side Flag Usage

PostHog feature flags enable A/B testing and gradual rollouts:

```mermaid
graph LR
    CHECK["useFeatureFlagEnabled()<br/>'new-dashboard-ui'"]
    PAYLOAD["useFeatureFlagPayload()<br/>'pricing-experiment'"]
    RENDER_NEW["NewDashboard Component"]
    RENDER_OLD["OldDashboard Component"]
    CONFIG["Pricing Config<br/>{ price: 29, showAnnual: true }"]
    
    CHECK -->|true| RENDER_NEW
    CHECK -->|false| RENDER_OLD
    PAYLOAD --> CONFIG
```

**Sources:** [skills/posthog-analytics.md:456-481]()

### Server-Side Flags (Next.js)

Server components can evaluate flags before rendering:

```typescript
// app/dashboard/page.tsx pattern
async function getFeatureFlags(userId: string) {
  const posthog = new PostHog(process.env.POSTHOG_API_KEY!);
  const flags = await posthog.getAllFlags(userId);
  await posthog.shutdown();  // Critical: prevent memory leaks
  return flags;
}
```

**Sources:** [skills/posthog-analytics.md:485-512]()

### A/B Testing Pattern

Experiments must track exposure events:

```typescript
const variant = useFeatureFlagEnabled('checkout-experiment');

useEffect(() => {
  posthog.capture('experiment_viewed', {
    experiment: 'checkout-experiment',
    variant: variant ? 'test' : 'control',
  });
}, [variant]);
```

**Sources:** [skills/posthog-analytics.md:514-530]()

---

## Dashboard Creation

### Project-Specific Dashboard Templates

The skill provides dashboard blueprints for different project types:

| Project Type | Essential Dashboards |
|--------------|---------------------|
| **SaaS** | Acquisition, Activation, Engagement, Retention, Revenue |
| **E-Commerce** | Conversion Funnel, Product Performance, Customer LTV |
| **Content/Media** | Consumption, Engagement, Growth |
| **AI/LLM** | Usage, Quality, Cost |
| **Mobile App** | Installs, Onboarding, DAU/MAU, Crashes |

**Sources:** [skills/posthog-analytics.md:927-934]()

### SaaS Dashboard Blueprint

```mermaid
graph TB
    subgraph "Acquisition Dashboard"
        ACQ1["Signups by source<br/>daily/weekly trend"]
        ACQ2["Signup conversion rate<br/>by landing page"]
        ACQ3["Time from first visit<br/>to signup"]
        ACQ4["Signup funnel:<br/>Visit → Page → Form → Complete"]
    end
    
    subgraph "Activation Dashboard"
        ACT1["Onboarding completion rate"]
        ACT2["Time to first key action"]
        ACT3["Activation rate<br/>% reaching aha moment in 7d"]
        ACT4["Drop-off by onboarding step"]
    end
    
    subgraph "Engagement Dashboard"
        ENG1["DAU/WAU/MAU trends"]
        ENG2["Feature usage heatmap"]
        ENG3["Session duration distribution"]
        ENG4["Actions per session"]
    end
    
    subgraph "Retention Dashboard"
        RET1["Retention cohorts<br/>D1, D7, D30"]
        RET2["Churn rate by plan"]
        RET3["Reactivation rate"]
        RET4["Last action before churn"]
    end
    
    subgraph "Revenue Dashboard"
        REV1["MRR trend"]
        REV2["Upgrades vs downgrades"]
        REV3["Trial to paid conversion"]
        REV4["LTV by acquisition source"]
    end
```

**Sources:** [skills/posthog-analytics.md:536-589]()

### Dashboard Creation Workflow

The PostHog MCP (Model Context Protocol) enables programmatic dashboard creation:

```mermaid
sequenceDiagram
    participant M as "MCP Client"
    participant D as "dashboard-create"
    participant Q as "query-run"
    participant I as "insight-create-from-query"
    participant A as "add-insight-to-dashboard"
    
    M->>D: Create "Activation Metrics" dashboard
    D-->>M: dashboard { id, name }
    
    M->>Q: Test funnel query
    Q-->>M: Query results
    
    M->>I: Save as "Signup to Activation Funnel"
    I-->>M: insight { id, name }
    
    M->>A: Add insight to dashboard
    A-->>M: Success
```

Example workflow:

```typescript
// 1. Create dashboard
const dashboard = await mcp_posthog_dashboard_create({
  name: "Activation Metrics",
  description: "Track new user activation and onboarding",
  tags: ["saas", "activation"],
});

// 2. Create funnel query
const signupFunnel = await mcp_posthog_query_run({
  query: {
    kind: "InsightVizNode",
    source: {
      kind: "FunnelsQuery",
      series: [
        { kind: "EventsNode", event: "user_signed_up", name: "Signed Up" },
        { kind: "EventsNode", event: "onboarding_started", name: "Started Onboarding" },
        { kind: "EventsNode", event: "onboarding_completed", name: "Completed Onboarding" },
      ],
      dateRange: { date_from: "-30d" },
    },
  },
});

// 3. Save and add to dashboard
const insight = await mcp_posthog_insight_create_from_query({
  name: "Signup to Activation Funnel",
  query: signupFunnel.query,
});

await mcp_posthog_add_insight_to_dashboard({
  insightId: insight.id,
  dashboardId: dashboard.id,
});
```

**Sources:** [skills/posthog-analytics.md:673-737]()

---

## Privacy and GDPR Compliance

### Privacy-First Configuration

The initialization uses `person_profiles: 'identified_only'` to comply with GDPR by default:

```typescript
posthog.init(key, {
  person_profiles: 'identified_only',      // Only track identified users
  opt_out_capturing_by_default: true,      // Require explicit opt-in
  respect_dnt: true,                        // Respect Do Not Track
});
```

**Sources:** [skills/posthog-analytics.md:38-43](), [skills/posthog-analytics.md:759-762]()

### Consent Management

```mermaid
stateDiagram-v2
    [*] --> OptedOut: "Default State"
    OptedOut --> OptedIn: "handleCookieConsent(true)"
    OptedIn --> OptedOut: "handleCookieConsent(false)"
    OptedOut --> [*]
    OptedIn --> [*]
    
    note right of OptedIn
        posthog.opt_in_capturing()
        Tracking active
    end note
    
    note right of OptedOut
        posthog.opt_out_capturing()
        No tracking
    end note
```

The consent handling function:

```typescript
export function handleCookieConsent(consent: boolean) {
  if (consent) {
    posthog.opt_in_capturing();
  } else {
    posthog.opt_out_capturing();
  }
}
```

**Sources:** [skills/posthog-analytics.md:744-763]()

### Property Sanitization

The system blocks sensitive data from tracking:

| ❌ Never Track | ✅ Safe to Track |
|---------------|-----------------|
| `password`, `token`, `secret` | `country`, `plan` |
| `credit_card`, `ssn` | `feature_used` |
| `medical_info` | `product_category` |
| `full_address` | General usage metrics |

Sanitization function:

```typescript
const SENSITIVE_KEYS = ['password', 'token', 'secret', 'credit', 'ssn'];

function sanitizeProperties(props: Record<string, any>): Record<string, any> {
  return Object.fromEntries(
    Object.entries(props).filter(([key]) =>
      !SENSITIVE_KEYS.some(sensitive => key.toLowerCase().includes(sensitive))
    )
  );
}

export function safeCapture(event: string, properties?: Record<string, any>) {
  posthog.capture(event, sanitizeProperties(properties || {}));
}
```

**Sources:** [skills/posthog-analytics.md:766-802]()

---

## Testing Analytics

### Development Mode Handling

PostHog tracking is disabled in development to prevent test data pollution:

```typescript
if (process.env.NODE_ENV === 'development') {
  posthog.opt_out_capturing();
  // Or use debug mode to see events without sending
  posthog.debug();
}
```

**Sources:** [skills/posthog-analytics.md:809-817]()

### E2E Testing with Playwright

Tests mock PostHog to capture events without external API calls:

```typescript
// playwright/fixtures.ts pattern
export const test = base.extend({
  page: async ({ page }, use) => {
    await page.addInitScript(() => {
      window.capturedEvents = [];
      window.posthog = {
        capture: (event, props) => {
          window.capturedEvents.push({ event, props });
        },
        identify: () => {},
        reset: () => {},
      };
    });
    await use(page);
  },
});

// Test assertion
test('tracks signup event', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('[name=email]', 'test@example.com');
  await page.click('button[type=submit]');

  const events = await page.evaluate(() => window.capturedEvents);
  expect(events).toContainEqual({
    event: 'user_signed_up',
    props: expect.objectContaining({ signup_method: 'email' }),
  });
});
```

**Sources:** [skills/posthog-analytics.md:819-854]()

### Event Debugging

The `_onCapture` callback logs events in development:

```typescript
posthog.init(key, {
  _onCapture: (eventName, eventData) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('PostHog Event:', eventName, eventData);
    }
  },
});
```

**Sources:** [skills/posthog-analytics.md:876-886]()

---

## Quick Reference

### Must-Track Events by Lifecycle

| Stage | Events |
|-------|--------|
| **Acquisition** | `page_viewed`, `user_signed_up`, `user_logged_in` |
| **Activation** | `onboarding_started`, `onboarding_step_completed`, `onboarding_completed`, `first_[key_action]` |
| **Engagement** | `[feature]_used`, `[resource]_created`, `search_performed`, `invite_sent` |
| **Revenue** | `pricing_page_viewed`, `checkout_started`, `subscription_upgraded`, `subscription_cancelled` |
| **Retention** | `session_started`, `feature_[x]_used` |

**Sources:** [skills/posthog-analytics.md:893-923]()

### Auto-Enriched Properties

PostHog automatically adds these properties to all events:

- `$current_url` - Current page URL
- `$browser` - Browser type
- `$device_type` - Desktop/mobile/tablet
- `$os` - Operating system

Custom properties to always include:

- `user_plan` - `'free'` | `'pro'` | `'enterprise'`
- `user_role` - `'admin'` | `'member'`
- `company_id` - For B2B products
- `feature_context` - Where in the app the action occurred

**Sources:** [skills/posthog-analytics.md:936-949]()

### Environment Variable Checklist

```bash
# Client-side (public)
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com

# Server-side (private)
POSTHOG_API_KEY=phc_xxxxxxxxxxxxxxxxxxxx
POSTHOG_HOST=https://us.i.posthog.com

# Vite projects
VITE_POSTHOG_KEY=phc_xxxxxxxxxxxxxxxxxxxx
VITE_POSTHOG_HOST=https://us.i.posthog.com
```

**Sources:** [skills/posthog-analytics.md:203-217]()

### Key API Methods

| Method | Purpose | Context |
|--------|---------|---------|
| `posthog.init(key, options)` | Initialize client | Client-side once |
| `posthog.capture(event, props)` | Track event | Any time |
| `posthog.identify(userId, props)` | Set user identity | Signup/login |
| `posthog.reset()` | Clear identity | Logout |
| `posthog.opt_in_capturing()` | Enable tracking | After consent |
| `posthog.opt_out_capturing()` | Disable tracking | Reject consent |
| `useFeatureFlagEnabled(flag)` | Check flag | React components |
| `posthog.getAllFlags(userId)` | Get all flags | Server-side |

**Sources:** [skills/posthog-analytics.md:34-55](), [skills/posthog-analytics.md:224-260](), [skills/posthog-analytics.md:461-512](), [skills/posthog-analytics.md:744-763]()

---

# Page: Payment Processing with Stripe

# Payment Processing with Stripe

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/credentials.md](skills/credentials.md)
- [skills/posthog-analytics.md](skills/posthog-analytics.md)
- [skills/web-payments.md](skills/web-payments.md)

</details>



This document covers integration patterns for Stripe payment processing in web applications, including one-time payments, subscriptions, webhook handling, and security best practices. The Stripe integration skill (`web-payments.md`) provides patterns for both hosted Checkout flows and embedded payment forms, with emphasis on server-side verification and idempotent webhook processing.

For general credentials management including Stripe API key patterns, see [Credentials Management](#6.2). For tracking payment conversion events, see [Analytics with PostHog](#7.1). For e-commerce platform integrations that use Stripe, see [E-commerce Platforms](#7.3).

---

## Integration Architecture

The Stripe integration follows a server-side-first architecture where all payment creation and verification occurs on the backend, with client-side components only handling UI rendering and redirects. This ensures API secrets never reach the browser and all payment state changes are verified via cryptographically signed webhooks.

**Stripe Integration Architecture**

```mermaid
graph TB
    subgraph "Client Layer"
        CheckoutButton["CheckoutButton component"]
        EmbeddedCheckout["EmbeddedCheckout component"]
        SuccessPage["Success page"]
        PortalButton["Customer Portal button"]
    end
    
    subgraph "API Routes (Server)"
        CheckoutRoute["POST /api/checkout/route.ts<br/>stripe.checkout.sessions.create()"]
        EmbeddedRoute["POST /api/checkout/embedded/route.ts<br/>ui_mode: 'embedded'"]
        PortalRoute["POST /api/portal/route.ts<br/>stripe.billingPortal.sessions.create()"]
        WebhookRoute["POST /api/webhooks/stripe/route.ts<br/>stripe.webhooks.constructEvent()"]
    end
    
    subgraph "Webhook Handlers"
        CheckoutCompleteHandler["handleCheckoutComplete()<br/>Update user subscription status"]
        SubscriptionUpdateHandler["handleSubscriptionUpdate()<br/>Update plan in DB"]
        SubscriptionCancelHandler["handleSubscriptionCanceled()<br/>Revoke access"]
        PaymentFailedHandler["handlePaymentFailed()<br/>Notify user"]
    end
    
    subgraph "Stripe Services"
        StripeCheckout["Stripe Checkout<br/>Hosted payment page"]
        StripeWebhooks["Stripe Webhook Delivery<br/>Event notifications"]
        StripeDashboard["Stripe Dashboard<br/>Product/Price management"]
    end
    
    subgraph "Database"
        UserTable["User table<br/>stripeCustomerId<br/>stripeSubscriptionId<br/>subscriptionStatus"]
    end
    
    subgraph "Environment"
        SecretKey["STRIPE_SECRET_KEY<br/>sk_test_* / sk_live_*<br/>Server-side only"]
        PublishableKey["NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY<br/>pk_test_* / pk_live_*<br/>Client-safe"]
        WebhookSecret["STRIPE_WEBHOOK_SECRET<br/>whsec_*<br/>Signature verification"]
    end
    
    CheckoutButton -->|"POST { priceId }"| CheckoutRoute
    CheckoutRoute -->|"sessionId, url"| CheckoutButton
    CheckoutButton -->|"window.location.href = url"| StripeCheckout
    
    EmbeddedCheckout -->|"POST { priceId }"| EmbeddedRoute
    EmbeddedRoute -->|"clientSecret"| EmbeddedCheckout
    
    PortalButton -->|"POST { customerId }"| PortalRoute
    
    StripeCheckout -->|"Payment completed"| StripeWebhooks
    StripeWebhooks -->|"POST event + signature"| WebhookRoute
    
    WebhookRoute -->|"checkout.session.completed"| CheckoutCompleteHandler
    WebhookRoute -->|"customer.subscription.updated"| SubscriptionUpdateHandler
    WebhookRoute -->|"customer.subscription.deleted"| SubscriptionCancelHandler
    WebhookRoute -->|"invoice.payment_failed"| PaymentFailedHandler
    
    CheckoutCompleteHandler --> UserTable
    SubscriptionUpdateHandler --> UserTable
    SubscriptionCancelHandler --> UserTable
    
    CheckoutRoute -.->|"uses"| SecretKey
    WebhookRoute -.->|"uses"| SecretKey
    WebhookRoute -.->|"verifies with"| WebhookSecret
    CheckoutButton -.->|"uses"| PublishableKey
    
    StripeDashboard -->|"Create products/prices"| CheckoutRoute
```

**Sources:** [skills/web-payments.md:1-659]()

---

## Credential Management

Stripe requires three types of API credentials, each with distinct security requirements and usage patterns. The credentials system automatically detects and extracts these keys from the centralized access file.

### API Key Types

| Key Type | Pattern | Environment Variable | Scope |
|----------|---------|---------------------|-------|
| Secret Key (Test) | `sk_test_*` | `STRIPE_SECRET_KEY` | Server-side only |
| Secret Key (Live) | `sk_live_*` | `STRIPE_SECRET_KEY` | Server-side only |
| Publishable Key (Test) | `pk_test_*` | `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Client-safe |
| Publishable Key (Live) | `pk_live_*` | `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Client-safe |
| Webhook Secret | `whsec_*` | `STRIPE_WEBHOOK_SECRET` | Server-side only |

### Automatic Detection

The credentials parsing system identifies Stripe keys using regex patterns:

```python
patterns = {
    'STRIPE_SECRET_KEY': r'sk_(live|test)_[A-Za-z0-9]+',
    'STRIPE_PUBLISHABLE_KEY': r'pk_(live|test)_[A-Za-z0-9]+',
    'STRIPE_WEBHOOK_SECRET': r'whsec_[A-Za-z0-9]+',
}
```

The system reads the centralized `Access.txt` file and automatically extracts Stripe credentials, generating appropriate `.env` entries for both server-side (`STRIPE_SECRET_KEY`) and client-side (`NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`) usage.

**Sources:** [skills/credentials.md:59-81](), [skills/credentials.md:99-138]()

---

## Integration Options

The Stripe integration skill supports three primary integration methods, each with different tradeoffs between ease of implementation and customization.

**Integration Method Comparison**

```mermaid
graph LR
    subgraph "Hosted Checkout"
        HC_Client["Client redirects<br/>to Stripe domain"]
        HC_Stripe["Stripe-hosted page<br/>Complete payment UI"]
        HC_Success["Redirect to<br/>success_url"]
    end
    
    subgraph "Embedded Checkout"
        EC_Client["Client renders<br/>iframe on site"]
        EC_Stripe["Stripe Checkout<br/>in iframe"]
        EC_Return["Stay on site<br/>return_url"]
    end
    
    subgraph "Payment Element"
        PE_Client["Custom form UI"]
        PE_Element["Payment Element<br/>component"]
        PE_Intent["PaymentIntent<br/>confirmation"]
    end
    
    HC_Client --> HC_Stripe --> HC_Success
    EC_Client --> EC_Stripe --> EC_Return
    PE_Client --> PE_Element --> PE_Intent
    
    HC_Success -.->|"Complexity: Low<br/>Customization: Low"| Note1[" "]
    EC_Return -.->|"Complexity: Low<br/>Customization: Medium"| Note2[" "]
    PE_Intent -.->|"Complexity: Medium<br/>Customization: High"| Note3[" "]
```

The recommended approach is **Hosted Checkout** for initial implementations, migrating to Embedded Checkout or Payment Element only when specific customization requirements emerge. Hosted Checkout requires minimal code and provides automatic PCI compliance, fraud prevention, and support for multiple payment methods.

**Sources:** [skills/web-payments.md:40-51]()

---

## Checkout Session Creation

The checkout flow begins server-side with session creation, which generates a secure payment URL or client secret. The server validates the request, retrieves pricing information, and configures the session with success/cancel URLs and metadata for tracking.

**Checkout Session Flow (Code Entities)**

```mermaid
sequenceDiagram
    participant Client as "CheckoutButton.tsx"
    participant API as "api/checkout/route.ts"
    participant Stripe as "Stripe API"
    participant DB as "Database"
    
    Client->>API: POST /api/checkout<br/>{ priceId, mode }
    
    API->>API: new Stripe(STRIPE_SECRET_KEY)
    
    API->>Stripe: stripe.checkout.sessions.create({<br/>  mode: "payment" | "subscription",<br/>  line_items: [{ price, quantity: 1 }],<br/>  success_url: "/success?session_id={CHECKOUT_SESSION_ID}",<br/>  cancel_url: "/canceled",<br/>  metadata: { userId, source }<br/>})
    
    Stripe-->>API: { id, url, client_secret }
    
    API-->>Client: { sessionId, url }
    
    Client->>Client: window.location.href = url
    
    Client->>Stripe: User redirected to Checkout
    
    Stripe->>Stripe: User completes payment
    
    Stripe->>API: POST /api/webhooks/stripe<br/>Event: checkout.session.completed<br/>Signature: stripe-signature header
    
    API->>API: stripe.webhooks.constructEvent(<br/>  body, signature, STRIPE_WEBHOOK_SECRET)
    
    API->>API: handleCheckoutComplete(session)
    
    API->>DB: UPDATE users SET<br/>  stripeCustomerId = session.customer,<br/>  stripeSubscriptionId = session.subscription,<br/>  subscriptionStatus = "active"<br/>WHERE id = session.metadata.userId
    
    API-->>Stripe: HTTP 200 OK
```

### Server-Side Implementation

The session creation route (`app/api/checkout/route.ts`) creates a Stripe Checkout session with line items, URLs, and metadata:

```typescript
const session = await stripe.checkout.sessions.create({
  mode: mode as "payment" | "subscription",
  payment_method_types: ["card"],
  line_items: [{ price: priceId, quantity: 1 }],
  success_url: `${process.env.NEXT_PUBLIC_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${process.env.NEXT_PUBLIC_URL}/canceled`,
  metadata: { userId: "user_123", source: "pricing_page" },
});
```

### Client-Side Redirect

The client component (`CheckoutButton.tsx`) calls the API route and redirects to the returned Checkout URL:

```typescript
const response = await fetch("/api/checkout", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ priceId }),
});
const { url } = await response.json();
window.location.href = url;
```

**Sources:** [skills/web-payments.md:59-98](), [skills/web-payments.md:139-166]()

---

## Webhook Event Processing

Webhooks are the primary mechanism for verifying payment state changes. The webhook endpoint must verify event signatures to prevent spoofing, implement idempotency to prevent duplicate processing, and handle events asynchronously to return HTTP 200 quickly.

**Webhook Processing Pipeline**

```mermaid
graph TB
    StripeWebhook["Stripe Webhook Delivery<br/>POST /api/webhooks/stripe"]
    
    subgraph "Verification Stage"
        ExtractSignature["Extract stripe-signature header"]
        ConstructEvent["stripe.webhooks.constructEvent(<br/>  body, signature, webhookSecret)"]
        VerifyFail["Signature invalid<br/>Return HTTP 400"]
    end
    
    subgraph "Idempotency Check"
        CheckProcessed["Check event.id in processedEvents"]
        SkipDuplicate["Already processed<br/>Return HTTP 200"]
        AddToSet["Add event.id to processedEvents"]
    end
    
    subgraph "Event Router"
        SwitchType["Switch on event.type"]
    end
    
    subgraph "Event Handlers"
        CheckoutComplete["checkout.session.completed<br/>→ handleCheckoutComplete()"]
        SubCreated["customer.subscription.created<br/>→ handleSubscriptionUpdate()"]
        SubUpdated["customer.subscription.updated<br/>→ handleSubscriptionUpdate()"]
        SubDeleted["customer.subscription.deleted<br/>→ handleSubscriptionCanceled()"]
        InvoiceFailed["invoice.payment_failed<br/>→ handlePaymentFailed()"]
        UnhandledEvent["Unhandled event type<br/>Log and continue"]
    end
    
    subgraph "Database Operations"
        UpdateUser["UPDATE users<br/>SET subscription fields"]
        RevokeAccess["UPDATE users<br/>SET subscriptionStatus = 'canceled'"]
        NotifyUser["INSERT notification<br/>Payment failed message"]
    end
    
    StripeWebhook --> ExtractSignature
    ExtractSignature --> ConstructEvent
    ConstructEvent -->|"Valid"| CheckProcessed
    ConstructEvent -->|"Invalid"| VerifyFail
    
    CheckProcessed -->|"Duplicate"| SkipDuplicate
    CheckProcessed -->|"New"| AddToSet
    AddToSet --> SwitchType
    
    SwitchType --> CheckoutComplete
    SwitchType --> SubCreated
    SwitchType --> SubUpdated
    SwitchType --> SubDeleted
    SwitchType --> InvoiceFailed
    SwitchType --> UnhandledEvent
    
    CheckoutComplete --> UpdateUser
    SubCreated --> UpdateUser
    SubUpdated --> UpdateUser
    SubDeleted --> RevokeAccess
    InvoiceFailed --> NotifyUser
    
    UpdateUser --> Return200["Return HTTP 200"]
    RevokeAccess --> Return200
    NotifyUser --> Return200
    UnhandledEvent --> Return200
    SkipDuplicate --> Return200
```

### Signature Verification

The webhook route (`app/api/webhooks/stripe/route.ts`) verifies the signature before processing:

```typescript
const body = await request.text();
const signature = headers().get("stripe-signature")!;

let event: Stripe.Event;
try {
  event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
} catch (err) {
  console.error("Webhook signature verification failed");
  return new Response("Invalid signature", { status: 400 });
}
```

### Event Handler Dispatch

The webhook router switches on `event.type` to dispatch to specific handlers:

```typescript
switch (event.type) {
  case "checkout.session.completed": {
    const session = event.data.object as Stripe.Checkout.Session;
    await handleCheckoutComplete(session);
    break;
  }
  case "customer.subscription.deleted": {
    const subscription = event.data.object as Stripe.Subscription;
    await handleSubscriptionCanceled(subscription);
    break;
  }
}
```

### Critical Events

| Event | Trigger | Required Action |
|-------|---------|-----------------|
| `checkout.session.completed` | Payment successful | Store `customer` and `subscription` IDs, set status to `active` |
| `customer.subscription.created` | New subscription | Store `subscription` ID and plan details |
| `customer.subscription.updated` | Plan change or renewal | Update plan and `current_period_end` in database |
| `customer.subscription.deleted` | Cancellation or non-payment | Set status to `canceled`, revoke access |
| `invoice.payment_failed` | Payment method declined | Notify user, attempt retry logic |
| `invoice.paid` | Successful renewal | Extend access, update `current_period_end` |

### Idempotency Pattern

The webhook handler must track processed event IDs to prevent duplicate processing:

```typescript
const processedEvents = new Set<string>(); // Use Redis in production

export async function POST(request: Request) {
  const event = stripe.webhooks.constructEvent(/*...*/);
  
  if (processedEvents.has(event.id)) {
    return new Response("Already processed", { status: 200 });
  }
  processedEvents.add(event.id);
  
  // Process event...
}
```

**Sources:** [skills/web-payments.md:229-303](), [skills/web-payments.md:305-349](), [skills/web-payments.md:517-532]()

---

## Subscription Management

The subscription system manages recurring billing cycles, trials, plan changes, and cancellations. Subscriptions are created during checkout with optional trial periods and are updated via webhooks as billing events occur.

### Creating Subscriptions with Trials

The checkout session can include trial configuration:

```typescript
const session = await stripe.checkout.sessions.create({
  mode: "subscription",
  line_items: [{ price: priceId, quantity: 1 }],
  subscription_data: {
    trial_period_days: 14,
    trial_settings: {
      end_behavior: { missing_payment_method: "cancel" },
    },
  },
  success_url: successUrl,
  cancel_url: cancelUrl,
});
```

### Subscription Status Checking

The `getSubscriptionStatus()` helper retrieves the current subscription state:

```typescript
export async function getSubscriptionStatus(customerId: string) {
  const subscriptions = await stripe.subscriptions.list({
    customer: customerId,
    status: "all",
    limit: 1,
  });
  
  const subscription = subscriptions.data[0];
  return {
    status: subscription.status,
    plan: subscription.items.data[0].price.id,
    currentPeriodEnd: new Date(subscription.current_period_end * 1000),
    cancelAtPeriodEnd: subscription.cancel_at_period_end,
  };
}
```

### Customer Portal

The Customer Portal allows users to manage their subscriptions without custom UI:

```typescript
// app/api/portal/route.ts
export async function POST(request: Request) {
  const { customerId } = await request.json();
  
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_URL}/settings`,
  });
  
  return NextResponse.json({ url: session.url });
}
```

Configure portal features at `https://dashboard.stripe.com/settings/billing/portal`.

**Sources:** [skills/web-payments.md:408-449](), [skills/web-payments.md:387-405]()

---

## Testing Patterns

Stripe provides test mode credentials, test card numbers, and a CLI for local webhook testing. All testing should occur in test mode (keys prefixed with `sk_test_` and `pk_test_`) to prevent accidental charges.

### Test Card Numbers

| Card Number | Scenario |
|-------------|----------|
| `4242424242424242` | Successful payment |
| `4000000000000002` | Card declined |
| `4000002500003155` | Requires 3D Secure authentication |
| `4000000000009995` | Insufficient funds error |

### Local Webhook Testing

The Stripe CLI forwards webhook events to local development servers:

```bash
# Install CLI
brew install stripe/stripe-cli/stripe

# Authenticate
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Trigger specific test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.deleted
stripe trigger invoice.payment_failed
```

The CLI outputs a webhook signing secret (`whsec_*`) for local testing, which should be set as `STRIPE_WEBHOOK_SECRET` in development `.env`.

### Analytics Integration

Payment events should be tracked in PostHog for conversion funnel analysis:

```typescript
import { posthog } from '@/lib/posthog';

async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  // Update database...
  
  // Track conversion event
  posthog.capture('subscription_upgraded', {
    from_plan: 'free',
    to_plan: 'pro',
    mrr_change: 29,
  });
}
```

**Sources:** [skills/web-payments.md:453-478](), [skills/posthog-analytics.md:374-401]()

---

## Security Best Practices

The Stripe integration enforces multiple security layers to prevent credential exposure, payment fraud, and duplicate processing. These patterns are non-negotiable for production deployments.

### Security Requirements

1. **Server-side secrets only**: `STRIPE_SECRET_KEY` must never be exposed to client-side code. Only `STRIPE_PUBLISHABLE_KEY` (prefixed with `NEXT_PUBLIC_` or `VITE_`) can be used in browsers.

2. **Webhook signature verification**: Every webhook must verify the `stripe-signature` header using `stripe.webhooks.constructEvent()` before processing. Unsigned webhooks must return HTTP 400.

3. **Idempotency enforcement**: Track processed webhook event IDs (using Redis in production, in-memory for development) to prevent duplicate processing if Stripe retries delivery.

4. **Metadata tracking**: Include `userId` and `source` in session metadata for debugging and associating payments with users.

5. **Cents-based arithmetic**: Always use integer cents for amounts to avoid floating-point precision errors:

```typescript
const toCents = (dollars: number) => Math.round(dollars * 100);
const toDollars = (cents: number) => cents / 100;

const priceInCents = 2999; // $29.99
```

### Credential Storage

The credentials system handles Stripe API key detection and `.env` generation:

- **Test mode**: Keys automatically extracted from `Access.txt` during initialization
- **Production mode**: Use environment variables configured in deployment platform
- **Webhook secret**: Generated by Stripe CLI for local development, configured in Stripe Dashboard for production

### Route Protection

Subscription status should gate access to premium features:

```typescript
// middleware.ts
export async function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith("/pro")) {
    const { status } = await getSubscriptionStatus(session.stripeCustomerId);
    
    if (status !== "active" && status !== "trialing") {
      return NextResponse.redirect(new URL("/pricing", request.url));
    }
  }
}
```

**Sources:** [skills/web-payments.md:508-549](), [skills/web-payments.md:593-609](), [skills/credentials.md:308-315]()

---

## Project Structure

The recommended file organization separates API routes, webhook handlers, client components, and utility functions:

```
project/
├── app/
│   ├── api/
│   │   ├── checkout/
│   │   │   ├── route.ts              # stripe.checkout.sessions.create()
│   │   │   └── embedded/
│   │   │       └── route.ts          # Embedded checkout sessions
│   │   ├── portal/
│   │   │   └── route.ts              # stripe.billingPortal.sessions.create()
│   │   └── webhooks/
│   │       └── stripe/
│   │           └── route.ts          # stripe.webhooks.constructEvent()
│   ├── pricing/
│   │   └── page.tsx                  # Pricing page with CheckoutButton
│   ├── success/
│   │   └── page.tsx                  # Post-checkout success handler
│   └── settings/
│       └── page.tsx                  # Subscription management
├── components/
│   ├── CheckoutButton.tsx            # Triggers checkout flow
│   └── EmbeddedCheckout.tsx          # Embedded checkout form
├── lib/
│   ├── stripe.ts                     # Stripe client initialization
│   └── subscription.ts               # getSubscriptionStatus() helper
└── .env.local                        # STRIPE_SECRET_KEY, etc.
```

### Handler Organization

Webhook handlers should be extracted into separate functions:

```typescript
// app/api/webhooks/stripe/route.ts
async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  const userId = session.metadata?.userId;
  await db.user.update({
    where: { id: userId },
    data: {
      stripeCustomerId: session.customer as string,
      stripeSubscriptionId: session.subscription as string,
      subscriptionStatus: "active",
    },
  });
}

async function handleSubscriptionCanceled(subscription: Stripe.Subscription) {
  const customerId = subscription.customer as string;
  await db.user.update({
    where: { stripeCustomerId: customerId },
    data: { subscriptionStatus: "canceled" },
  });
}
```

**Sources:** [skills/web-payments.md:480-504](), [skills/web-payments.md:287-303]()

---

## Anti-Patterns

The following patterns violate security requirements and must be avoided:

| Anti-Pattern | Risk | Correct Approach |
|--------------|------|------------------|
| Hardcoding API keys in code | Keys committed to git | Use environment variables |
| Client-side PaymentIntent creation | Secret key exposure | Create on server, return client secret |
| Skipping webhook signature verification | Spoofed payment events | Always call `constructEvent()` |
| No idempotency tracking | Duplicate database updates | Track event IDs |
| Floating-point currency math | Precision errors ($29.999) | Use integer cents (2999) |
| Trusting client-submitted prices | User sets price to $0.01 | Fetch price from Stripe/database |
| Ignoring `invoice.payment_failed` | Silent subscription lapses | Send notification, attempt recovery |
| No error handling on Stripe API calls | Crashes on network errors | Wrap in try-catch, return error responses |

**Sources:** [skills/web-payments.md:612-622]()

---

## Quick Reference

### Installation

```bash
npm install stripe @stripe/stripe-js @stripe/react-stripe-js
```

### Environment Variables

```bash
# Server-side only
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Client-safe (Next.js)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx

# Client-safe (Vite)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

### Key API Routes

| Route | Purpose | Method |
|-------|---------|--------|
| `/api/checkout` | Create checkout session | `stripe.checkout.sessions.create()` |
| `/api/checkout/embedded` | Create embedded session | `stripe.checkout.sessions.create({ ui_mode: 'embedded' })` |
| `/api/portal` | Customer billing portal | `stripe.billingPortal.sessions.create()` |
| `/api/webhooks/stripe` | Handle webhook events | `stripe.webhooks.constructEvent()` |

### Stripe CLI Commands

```bash
stripe login                        # Authenticate
stripe listen --forward-to URL      # Forward webhooks to local server
stripe trigger EVENT_TYPE           # Trigger test events
stripe products list                # List products
stripe prices list                  # List prices
```

**Sources:** [skills/web-payments.md:625-659](), [skills/credentials.md:74-76]()

---

# Page: E-commerce Platforms

# E-commerce Platforms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/klaviyo.md](skills/klaviyo.md)
- [skills/medusa.md](skills/medusa.md)
- [skills/woocommerce.md](skills/woocommerce.md)

</details>



This page documents integration patterns for e-commerce platforms and marketing automation tools provided as conditional skills in Claude Bootstrap. These skills enable building headless e-commerce backends (Medusa), integrating with WordPress stores (WooCommerce), and automating customer engagement (Klaviyo).

For payment processing patterns, see [Payment Processing with Stripe](#7.2). For product analytics, see [Analytics with PostHog](#7.1).

---

## Overview

Claude Bootstrap provides three e-commerce integration skills that load conditionally during project initialization:

| Skill File | Platform | Purpose | Load Condition |
|------------|----------|---------|----------------|
| `medusa.md` | Medusa | Headless e-commerce backend | Selected during initialization |
| `woocommerce.md` | WooCommerce | WordPress store integration | Selected during initialization |
| `klaviyo.md` | Klaviyo | Email/SMS marketing automation | Selected during initialization |

These skills integrate with Claude Bootstrap's core patterns:
- **TDD Workflow**: All integration code follows RED-GREEN-VALIDATE cycles
- **Credentials Management**: API keys managed via `Access.txt` ([6.2](#6.2))
- **Security Scanning**: Pre-commit hooks detect hardcoded secrets ([6.3](#6.3))
- **Session Management**: Integration state tracked in `_project_specs/` ([4.2](#4.2))

**Sources:** [skills/medusa.md:1-760](), [skills/woocommerce.md:1-774](), [skills/klaviyo.md:1-803]()

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Client Applications"
        STOREFRONT["Storefront<br/>(Next.js/React)"]
        MOBILE["Mobile App<br/>(React Native)"]
        ADMIN_UI["Admin Dashboard"]
    end
    
    subgraph "Integration Layer"
        MEDUSA_API["Medusa Backend<br/>src/api/store/<br/>src/api/admin/"]
        WC_API["WooCommerce REST API<br/>/wp-json/wc/v3/"]
        KLAVIYO_API["Klaviyo API<br/>/profiles, /events, /lists"]
    end
    
    subgraph "Business Logic"
        MODULES["Medusa Modules<br/>src/modules/"]
        WORKFLOWS["Medusa Workflows<br/>createWorkflow()"]
        SUBSCRIBERS["Event Subscribers<br/>src/subscribers/"]
        WC_WEBHOOKS["WooCommerce Webhooks<br/>verifyWooCommerceWebhook()"]
        KLAVIYO_EVENTS["Klaviyo Events<br/>trackEvent()"]
    end
    
    subgraph "Data Layer"
        POSTGRES["PostgreSQL<br/>(Medusa)"]
        WORDPRESS_DB["WordPress DB<br/>(WooCommerce)"]
        KLAVIYO_PROFILES["Klaviyo Profiles<br/>Customer Data"]
    end
    
    subgraph "Credentials Management"
        ACCESS_TXT["Access.txt"]
        ENV["Environment Variables<br/>WC_CONSUMER_KEY<br/>KLAVIYO_PRIVATE_KEY<br/>DATABASE_URL"]
    end
    
    STOREFRONT --> MEDUSA_API
    STOREFRONT --> WC_API
    MOBILE --> MEDUSA_API
    ADMIN_UI --> MEDUSA_API
    ADMIN_UI --> WC_API
    
    MEDUSA_API --> MODULES
    MEDUSA_API --> WORKFLOWS
    MEDUSA_API --> SUBSCRIBERS
    MEDUSA_API --> KLAVIYO_EVENTS
    
    WC_API --> WC_WEBHOOKS
    WC_WEBHOOKS --> KLAVIYO_EVENTS
    
    MODULES --> POSTGRES
    WORKFLOWS --> POSTGRES
    WC_API --> WORDPRESS_DB
    KLAVIYO_EVENTS --> KLAVIYO_PROFILES
    
    ACCESS_TXT --> ENV
    ENV --> MEDUSA_API
    ENV --> WC_API
    ENV --> KLAVIYO_API
```

**Sources:** [skills/medusa.md:66-90](), [skills/woocommerce.md:33-52](), [skills/klaviyo.md:26-45]()

---

## Medusa: Headless E-commerce Backend

Medusa is an open-source, Node.js-native e-commerce backend with built-in admin dashboard and modular architecture.

### Project Structure

The Medusa skill defines a specific project structure that aligns with framework conventions:

```
medusa-store/
├── src/
│   ├── admin/                    # Admin UI customizations
│   │   ├── widgets/              # Dashboard widgets
│   │   └── routes/               # Custom admin pages
│   ├── api/                      # Custom API routes
│   │   ├── store/                # Public storefront APIs
│   │   └── admin/                # Admin APIs
│   ├── jobs/                     # Scheduled tasks
│   ├── modules/                  # Custom business logic
│   ├── workflows/                # Multi-step processes
│   ├── subscribers/              # Event listeners
│   └── links/                    # Module relationships
├── medusa-config.ts              # Configuration
└── .env                          # Credentials
```

**Sources:** [skills/medusa.md:66-90]()

### Configuration Pattern

Medusa projects use `medusa-config.ts` with centralized environment variable loading:

```mermaid
graph LR
    ACCESS_TXT["Access.txt<br/>DATABASE_URL<br/>REDIS_URL<br/>JWT_SECRET"]
    ENV_FILE[".env"]
    CONFIG["medusa-config.ts<br/>defineConfig()"]
    MODULES["Custom Modules<br/>src/modules/"]
    ADMIN["Admin Dashboard<br/>admin.backendUrl"]
    HTTP["HTTP Config<br/>CORS settings"]
    
    ACCESS_TXT -->|"credentials.md validation"| ENV_FILE
    ENV_FILE -->|"loadEnv()"| CONFIG
    CONFIG --> MODULES
    CONFIG --> ADMIN
    CONFIG --> HTTP
```

The configuration structure is defined at [skills/medusa.md:98-121]():
- `projectConfig.databaseUrl`: PostgreSQL connection
- `projectConfig.http`: CORS configuration for store/admin/auth
- `projectConfig.redisUrl`: Redis for session management
- `admin.backendUrl`: Backend URL for admin dashboard
- `modules`: Array of custom module registrations

**Sources:** [skills/medusa.md:94-141]()

### API Route Patterns

Medusa provides two API route types with automatic routing conventions:

| Route Location | URL Pattern | Authentication | Purpose |
|----------------|-------------|----------------|---------|
| `src/api/store/` | `/store/*` | Optional (customer) | Public storefront APIs |
| `src/api/admin/` | `/admin/*` | Required (user) | Protected admin APIs |

**Store API Example** ([skills/medusa.md:148-162]()):
```typescript
// src/api/store/hello/route.ts
export async function GET(req: MedusaRequest, res: MedusaResponse) {
  res.json({ message: "Hello from custom store API!" });
}
// Accessible at: GET /store/hello
```

**Admin API Example** ([skills/medusa.md:167-195]()):
```typescript
// src/api/admin/analytics/route.ts
export async function GET(req: MedusaRequest, res: MedusaResponse) {
  const orderService = req.scope.resolve(Modules.ORDER);
  const orders = await orderService.listOrders({
    created_at: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
  });
  const totalRevenue = orders.reduce((sum, order) => sum + (order.total || 0), 0);
  res.json({ orderCount: orders.length, totalRevenue });
}
// Accessible at: GET /admin/analytics (requires auth)
```

**Sources:** [skills/medusa.md:143-256]()

### Module System

Modules encapsulate custom business logic with dependency injection:

```mermaid
graph TB
    MODULE_DEF["Module Definition<br/>src/modules/reviews/index.ts<br/>Module(REVIEW_MODULE)"]
    SERVICE["Service Class<br/>ReviewModuleService<br/>extends MedusaService"]
    METHODS["Service Methods<br/>createReview()<br/>getProductReviews()<br/>getAverageRating()"]
    CONFIG_REG["medusa-config.ts<br/>modules: [resolve, options]"]
    API_USAGE["API Route Usage<br/>req.scope.resolve(REVIEW_MODULE)"]
    
    MODULE_DEF --> SERVICE
    SERVICE --> METHODS
    MODULE_DEF --> CONFIG_REG
    CONFIG_REG --> API_USAGE
    API_USAGE --> METHODS
```

The module pattern is implemented at [skills/medusa.md:264-329]():
1. Define module with `Module(REVIEW_MODULE, { service: ReviewModuleService })`
2. Implement service extending `MedusaService`
3. Register in `medusa-config.ts` modules array
4. Resolve in API routes via `req.scope.resolve(REVIEW_MODULE)`

**Sources:** [skills/medusa.md:260-329]()

### Workflow System

Workflows implement multi-step processes with automatic rollback on failure:

```mermaid
stateDiagram-v2
    [*] --> CreateOrder: "createOrderStep"
    CreateOrder --> SendNotification: "StepResponse(order, order.id)"
    CreateOrder --> Rollback: "Error"
    SendNotification --> Complete: "StepResponse({ sent: true })"
    SendNotification --> Rollback: "Error"
    Rollback --> DeleteOrder: "Compensation function<br/>orderService.deleteOrders()"
    DeleteOrder --> [*]
    Complete --> [*]
    
    note right of CreateOrder
        createStep("create-order", async (input, { container }) => {
            const orderService = container.resolve(Modules.ORDER);
            const order = await orderService.createOrders(input);
            return new StepResponse(order, order.id);
        }, compensationFn)
    end note
```

Workflow implementation at [skills/medusa.md:337-401]():
- `createWorkflow()`: Defines workflow with input type
- `createStep()`: Defines individual steps with compensation (rollback)
- `StepResponse`: Returns data and compensation context
- Automatic rollback if any step fails

**Sources:** [skills/medusa.md:333-401]()

### Event Subscribers

Subscribers listen to system events and trigger side effects:

| Event | Trigger | Example Use Case |
|-------|---------|------------------|
| `order.placed` | New order created | Send confirmation email |
| `order.updated` | Order modified | Update inventory |
| `order.canceled` | Order cancelled | Process refund |
| `order.completed` | Order fulfilled | Request review |
| `customer.created` | New customer registered | Add to mailing list |
| `product.created` | New product added | Sync to search index |
| `inventory.updated` | Stock changed | Send low-stock alert |

Subscriber implementation at [skills/medusa.md:409-429]():
```typescript
// src/subscribers/order-placed.ts
export default async function orderPlacedHandler({ event, container }: SubscriberArgs) {
  const orderId = event.data.id;
  const notificationService = container.resolve("notificationService");
  await notificationService.sendOrderConfirmation(orderId);
}
export const config: SubscriberConfig = { event: "order.placed" };
```

**Sources:** [skills/medusa.md:405-443]()

### Scheduled Jobs

Jobs run on cron schedules for recurring tasks:

```typescript
// src/jobs/sync-inventory.ts
export default async function syncInventoryJob(container: MedusaContainer) {
  const inventoryService = container.resolve("inventoryService");
  console.log("Running inventory sync...");
  await inventoryService.syncFromExternalSource();
}
export const config = {
  name: "sync-inventory",
  schedule: "0 */6 * * *", // Every 6 hours
};
```

**Sources:** [skills/medusa.md:447-466]()

---

## WooCommerce: WordPress Store Integration

WooCommerce provides REST API integration for WordPress-based stores with comprehensive product, order, and customer management.

### API Client Setup

WooCommerce uses Basic Authentication with consumer key/secret pairs:

```mermaid
graph LR
    WP_ADMIN["WordPress Admin<br/>WooCommerce → Settings<br/>→ Advanced → REST API"]
    GEN_KEY["Generate API Key<br/>Consumer Key: ck_...<br/>Consumer Secret: cs_..."]
    ACCESS_TXT["Access.txt<br/>WC_CONSUMER_KEY<br/>WC_CONSUMER_SECRET"]
    ENV[".env"]
    CLIENT["WooCommerceRestApi<br/>new WooCommerceRestApi()"]
    METHODS["API Methods<br/>api.get()<br/>api.post()<br/>api.put()<br/>api.delete()"]
    
    WP_ADMIN --> GEN_KEY
    GEN_KEY --> ACCESS_TXT
    ACCESS_TXT --> ENV
    ENV --> CLIENT
    CLIENT --> METHODS
```

Client initialization at [skills/woocommerce.md:86-98]():
```typescript
// lib/woocommerce.ts
import WooCommerceRestApi from "@woocommerce/woocommerce-rest-api";

const api = new WooCommerceRestApi({
  url: process.env.WC_STORE_URL!,
  consumerKey: process.env.WC_CONSUMER_KEY!,
  consumerSecret: process.env.WC_CONSUMER_SECRET!,
  version: "wc/v3",
  queryStringAuth: false, // Set true for HTTP (dev only)
});
```

**Sources:** [skills/woocommerce.md:23-98]()

### Resource Operations

WooCommerce API follows RESTful conventions with consistent patterns:

| Resource | Endpoint | List | Get | Create | Update | Delete |
|----------|----------|------|-----|--------|--------|--------|
| Products | `/products` | `api.get("products")` | `api.get("products/:id")` | `api.post("products")` | `api.put("products/:id")` | `api.delete("products/:id")` |
| Orders | `/orders` | `api.get("orders")` | `api.get("orders/:id")` | `api.post("orders")` | `api.put("orders/:id")` | N/A |
| Customers | `/customers` | `api.get("customers")` | `api.get("customers/:id")` | `api.post("customers")` | `api.put("customers/:id")` | N/A |
| Categories | `/products/categories` | `api.get("products/categories")` | N/A | `api.post("products/categories")` | N/A | N/A |
| Coupons | `/coupons` | `api.get("coupons")` | `api.get("coupons/:id")` | `api.post("coupons")` | N/A | N/A |

**Product Operations** ([skills/woocommerce.md:123-216]()):
```typescript
// List products with filters
async function searchProducts(search: string, category?: number) {
  const response = await api.get("products", {
    search,
    category: category || undefined,
    orderby: "popularity",
    order: "desc",
  });
  return response.data;
}

// Create product
async function createProduct(data: ProductInput) {
  const response = await api.post("products", {
    name: data.name,
    type: "simple", // simple, variable, grouped, external
    regular_price: data.price.toString(),
    categories: data.categoryIds.map(id => ({ id })),
    images: data.images.map(url => ({ src: url })),
    manage_stock: true,
    stock_quantity: data.stockQuantity,
  });
  return response.data;
}
```

**Order Operations** ([skills/woocommerce.md:269-369]()):
```typescript
// Create order
async function createOrder(data: OrderInput) {
  const response = await api.post("orders", {
    payment_method: "stripe",
    billing: { /* billing address */ },
    shipping: { /* shipping address */ },
    line_items: data.items.map(item => ({
      product_id: item.productId,
      variation_id: item.variationId,
      quantity: item.quantity,
    })),
  });
  return response.data;
}

// Update order status
async function updateOrderStatus(orderId: number, status: OrderStatus) {
  const response = await api.put(`orders/${orderId}`, { status });
  return response.data;
}
```

**Sources:** [skills/woocommerce.md:122-446]()

### Order Status Workflow

```mermaid
stateDiagram-v2
    [*] --> pending: "Order Created"
    pending --> processing: "Payment Received<br/>api.put(orders/:id, {status: 'processing'})"
    pending --> failed: "Payment Failed"
    pending --> on_hold: "Awaiting Action"
    on_hold --> processing: "Issue Resolved"
    processing --> completed: "Order Fulfilled<br/>api.put(orders/:id, {status: 'completed'})"
    processing --> cancelled: "Cancelled by Admin"
    completed --> refunded: "Refund Processed<br/>api.put(orders/:id, {status: 'refunded'})"
    [*] --> cancelled: "Cancelled by Customer"
    failed --> [*]
    cancelled --> [*]
    refunded --> [*]
```

**Sources:** [skills/woocommerce.md:372-382]()

### Webhook Integration

WooCommerce webhooks notify external systems of store events:

```mermaid
graph TB
    WC_EVENT["WooCommerce Event<br/>order.created<br/>order.updated<br/>product.created"]
    WC_WEBHOOK["Webhook Dispatcher"]
    DELIVERY["POST to delivery_url<br/>Headers:<br/>X-WC-Webhook-Topic<br/>X-WC-Webhook-Signature"]
    HANDLER["Express Handler<br/>/webhooks/woocommerce"]
    VERIFY["verifyWooCommerceWebhook()<br/>HMAC SHA-256 signature"]
    PROCESS["Process Event<br/>handleNewOrder()<br/>handleOrderUpdate()"]
    RESPONSE["200 OK<br/>{received: true}"]
    
    WC_EVENT --> WC_WEBHOOK
    WC_WEBHOOK --> DELIVERY
    DELIVERY --> HANDLER
    HANDLER --> VERIFY
    VERIFY -->|"Valid"| PROCESS
    VERIFY -->|"Invalid"| REJECT["401 Unauthorized<br/>{error: 'Invalid signature'}"]
    PROCESS --> RESPONSE
```

Webhook verification at [skills/woocommerce.md:484-522]():
```typescript
import crypto from "crypto";

function verifyWooCommerceWebhook(req: Request): boolean {
  const signature = req.headers["x-wc-webhook-signature"] as string;
  const payload = JSON.stringify(req.body);
  
  const expectedSignature = crypto
    .createHmac("sha256", process.env.WC_WEBHOOK_SECRET!)
    .update(payload)
    .digest("base64");
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// Route handler
app.post("/webhooks/woocommerce", (req, res) => {
  if (!verifyWooCommerceWebhook(req)) {
    return res.status(401).json({ error: "Invalid signature" });
  }
  
  const topic = req.headers["x-wc-webhook-topic"];
  // Process webhook based on topic
});
```

**Webhook Topics** ([skills/woocommerce.md:467-479]()):
- `order.created`: New order placed
- `order.updated`: Order status/details changed
- `product.created`: New product added
- `product.updated`: Product modified
- `customer.created`: New customer registered

**Sources:** [skills/woocommerce.md:449-556]()

### Pagination Pattern

WooCommerce uses header-based pagination for large datasets:

```typescript
async function getAllProducts() {
  const allProducts = [];
  let page = 1;
  const perPage = 100;
  
  while (true) {
    const response = await api.get("products", { page, per_page: perPage });
    allProducts.push(...response.data);
    
    // Check headers for total pages
    const totalPages = parseInt(response.headers["x-wp-totalpages"]);
    if (page >= totalPages) break;
    page++;
  }
  return allProducts;
}
```

**Pagination Headers:**
- `X-WP-Total`: Total number of items
- `X-WP-TotalPages`: Total number of pages

**Sources:** [skills/woocommerce.md:645-677]()

---

## Klaviyo: Email & SMS Marketing Automation

Klaviyo provides event-driven marketing automation with customer profile management and campaign orchestration.

### Dual API Architecture

Klaviyo uses separate APIs for server-side and client-side operations:

| API Type | Base URL | Authentication | Use Case |
|----------|----------|----------------|----------|
| Server-side (Private) | `https://a.klaviyo.com/api` | `Klaviyo-API-Key pk_...` | Profile management, event tracking |
| Client-side (Public) | `https://a.klaviyo.com/client` | Query param `company_id=XXXXXX` | Browser-based tracking |

**Server-Side Client** ([skills/klaviyo.md:66-75]()):
```typescript
// lib/klaviyo.ts
import { ApiClient, EventsApi, ProfilesApi, ListsApi } from "klaviyo-api";

const client = new ApiClient();
client.setApiKey(process.env.KLAVIYO_PRIVATE_KEY!);

export const eventsApi = new EventsApi(client);
export const profilesApi = new ProfilesApi(client);
export const listsApi = new ListsApi(client);
```

**Client-Side Tracking** ([skills/klaviyo.md:352-378]()):
```html
<script async src="https://static.klaviyo.com/onsite/js/klaviyo.js?company_id=XXXXXX"></script>
<script>
  klaviyo.identify({ email: "customer@example.com", first_name: "John" });
  klaviyo.track("Viewed Product", { ProductID: "prod_123", Price: 29.99 });
</script>
```

**Sources:** [skills/klaviyo.md:23-123]()

### Profile Management

Profiles represent customers with email/phone identifiers and custom properties:

```mermaid
graph TB
    CUSTOMER["Customer Event<br/>Signup/Purchase"]
    UPSERT["upsertProfile()<br/>/profiles POST"]
    PROFILE["Klaviyo Profile<br/>email/phone_number<br/>first_name, last_name<br/>properties{}"]
    UPDATE["updateProfileProperties()<br/>/profiles/:id PATCH"]
    PROPERTIES["Custom Properties<br/>lifetime_value<br/>plan<br/>total_orders<br/>vip_status"]
    LIST["addToList()<br/>/lists/:id/relationships/profiles"]
    SEGMENT["Dynamic Segments<br/>Behavioral targeting"]
    
    CUSTOMER --> UPSERT
    UPSERT --> PROFILE
    PROFILE --> UPDATE
    UPDATE --> PROPERTIES
    PROFILE --> LIST
    LIST --> SEGMENT
```

**Profile Creation** ([skills/klaviyo.md:130-157]()):
```typescript
async function upsertProfile(data: ProfileInput) {
  return klaviyoRequest("/profiles", "POST", {
    data: {
      type: "profile",
      attributes: {
        email: data.email,
        phone_number: data.phone, // E.164 format: +1234567890
        first_name: data.firstName,
        last_name: data.lastName,
        properties: {
          lifetime_value: data.ltv,
          plan: data.plan,
          signup_source: data.source,
        },
        location: {
          city: data.city,
          region: data.state,
          country: data.country,
        },
      },
    },
  });
}
```

**Profile Updates** ([skills/klaviyo.md:193-216]()):
```typescript
async function updateProfileProperties(profileId: string, properties: Record<string, any>) {
  return klaviyoRequest(`/profiles/${profileId}`, "PATCH", {
    data: {
      type: "profile",
      id: profileId,
      attributes: { properties },
    },
  });
}

// Usage: Track customer behavior
await updateProfileProperties("profile_id", {
  last_purchase_date: new Date().toISOString(),
  total_orders: 5,
  vip_status: true,
});
```

**Sources:** [skills/klaviyo.md:126-216]()

### Event Tracking System

Events drive marketing automation flows and customer segmentation:

```mermaid
graph TB
    ECOMMERCE["E-Commerce Events"]
    TRACK["trackEvent()<br/>/events POST"]
    EVENT_DATA["Event Attributes<br/>profile{email}<br/>metric{name}<br/>properties{}<br/>value (revenue)<br/>unique_id"]
    FLOWS["Trigger Flows<br/>Abandoned Cart<br/>Post-Purchase<br/>Winback"]
    SEGMENTS["Build Segments<br/>Behavior-based<br/>Property-based"]
    CAMPAIGNS["Campaign Targeting<br/>Email/SMS"]
    
    ECOMMERCE --> TRACK
    TRACK --> EVENT_DATA
    EVENT_DATA --> FLOWS
    EVENT_DATA --> SEGMENTS
    SEGMENTS --> CAMPAIGNS
    FLOWS --> CAMPAIGNS
```

**Standard E-commerce Events** ([skills/klaviyo.md:258-347]()):

| Event Name | Trigger | Required Properties |
|------------|---------|---------------------|
| `Viewed Product` | Product page view | `ProductID`, `ProductName`, `Price`, `ProductURL`, `ImageURL` |
| `Added to Cart` | Add to cart button | `ProductID`, `Quantity`, `Price`, `CartTotal`, `ItemNames` |
| `Started Checkout` | Checkout initiated | `CheckoutURL`, `ItemCount`, `Categories`, `ItemNames` |
| `Placed Order` | Order confirmation | `OrderId`, `Items[]`, `BillingAddress`, `ShippingAddress` |
| `Fulfilled Order` | Order shipped | `OrderId`, `TrackingNumber`, `TrackingURL`, `Carrier` |
| `Cancelled Order` | Order cancelled | `OrderId`, `Reason`, negative `$value` |

**Event Implementation** ([skills/klaviyo.md:224-254]()):
```typescript
async function trackEvent(data: EventInput) {
  return klaviyoRequest("/events", "POST", {
    data: {
      type: "event",
      attributes: {
        profile: {
          data: {
            type: "profile",
            attributes: { email: data.email },
          },
        },
        metric: {
          data: {
            type: "metric",
            attributes: { name: data.eventName },
          },
        },
        properties: data.properties,
        value: data.value, // For revenue tracking
        unique_id: data.uniqueId, // Deduplication
        time: data.timestamp || new Date().toISOString(),
      },
    },
  });
}
```

**Order Event Example** ([skills/klaviyo.md:302-324]()):
```typescript
await trackEvent({
  email: customer.email,
  eventName: "Placed Order",
  properties: {
    OrderId: order.id,
    ItemCount: order.itemCount,
    Items: order.items.map(i => ({
      ProductID: i.productId,
      ProductName: i.name,
      Quantity: i.quantity,
      Price: i.price,
    })),
    BillingAddress: order.billingAddress,
    ShippingAddress: order.shippingAddress,
  },
  value: order.total,
  uniqueId: order.id, // Prevent duplicate orders
});
```

**Sources:** [skills/klaviyo.md:220-348]()

### List & Segment Management

Lists are static collections; segments are dynamic queries:

```typescript
// Add profiles to list
async function addToList(listId: string, emails: string[]) {
  return klaviyoRequest(`/lists/${listId}/relationships/profiles`, "POST", {
    data: emails.map(email => ({
      type: "profile",
      attributes: { email },
    })),
  });
}

// Remove from list
async function removeFromList(listId: string, profileId: string) {
  return klaviyoRequest(`/lists/${listId}/relationships/profiles`, "DELETE", {
    data: [{ type: "profile", id: profileId }],
  });
}

// Create new list
async function createList(name: string) {
  return klaviyoRequest("/lists", "POST", {
    data: {
      type: "list",
      attributes: { name },
    },
  });
}
```

**Sources:** [skills/klaviyo.md:383-445]()

### Flow Automation Triggers

Flows are automated multi-step email/SMS campaigns triggered by events:

| Flow Type | Trigger Event | Timing Condition |
|-----------|---------------|------------------|
| Welcome Series | Added to List | Immediate |
| Abandoned Cart | Added to Cart + No Purchase | 1 hour, 24 hours |
| Browse Abandon | Viewed Product + No Cart | 2 hours |
| Post-Purchase | Placed Order | 1 day, 7 days |
| Winback | No Order in X Days | 30 days, 60 days |
| Review Request | Fulfilled Order | 7 days |

**Sources:** [skills/klaviyo.md:477-501]()

### Webhook System

Klaviyo webhooks notify external systems of profile and event changes:

```mermaid
graph TB
    KLAVIYO_EVENT["Klaviyo Event<br/>profile.created<br/>event.created<br/>list.member.added"]
    WEBHOOK["Webhook POST"]
    SIGNATURE["X-Klaviyo-Webhook-Signature<br/>HMAC SHA-256"]
    HANDLER["Express Handler<br/>/webhooks/klaviyo"]
    VERIFY["verifyKlaviyoWebhook()<br/>crypto.timingSafeEqual()"]
    PROCESS["Process Event<br/>handleNewProfile()<br/>handleNewEvent()"]
    
    KLAVIYO_EVENT --> WEBHOOK
    WEBHOOK --> SIGNATURE
    SIGNATURE --> HANDLER
    HANDLER --> VERIFY
    VERIFY -->|"Valid"| PROCESS
    VERIFY -->|"Invalid"| REJECT["401 Unauthorized"]
```

**Webhook Verification** ([skills/klaviyo.md:536-577]()):
```typescript
import crypto from "crypto";

function verifyKlaviyoWebhook(payload: string, signature: string, secret: string): boolean {
  const expectedSignature = crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest("base64");
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// Express handler
app.post("/webhooks/klaviyo", (req, res) => {
  const signature = req.headers["klaviyo-webhook-signature"] as string;
  
  if (!verifyKlaviyoWebhook(JSON.stringify(req.body), signature, WEBHOOK_SECRET)) {
    return res.status(401).json({ error: "Invalid signature" });
  }
  
  const { type, data } = req.body;
  // Process based on type (profile.created, event.created, etc.)
  res.status(200).json({ received: true });
});
```

**Webhook Topics** ([skills/klaviyo.md:525-534]()):
- `profile.created`: New profile created
- `profile.updated`: Profile properties changed
- `event.created`: New event tracked
- `list.member.added`: Profile added to list
- `list.member.removed`: Profile removed from list

**Sources:** [skills/klaviyo.md:503-577]()

---

## Integration Patterns

### E-commerce Order Sync to Klaviyo

Common pattern for syncing WooCommerce/Medusa orders to Klaviyo for marketing automation:

```mermaid
sequenceDiagram
    participant Store as "E-commerce Store<br/>(WooCommerce/Medusa)"
    participant Webhook as "Webhook Handler"
    participant Klaviyo as "Klaviyo API"
    
    Store->>Webhook: "POST /webhooks/order-created<br/>{order}"
    Webhook->>Webhook: "Verify signature"
    Webhook->>Klaviyo: "upsertProfile()<br/>{email, name, phone}"
    Klaviyo-->>Webhook: "{profile_id}"
    Webhook->>Klaviyo: "updateProfileProperties()<br/>{last_order_date, total_orders, ltv}"
    Webhook->>Klaviyo: "trackEvent('Placed Order')<br/>{OrderId, Items, value}"
    Klaviyo-->>Webhook: "Event recorded"
    Note over Klaviyo: "Triggers:<br/>- Post-purchase flow<br/>- Revenue tracking<br/>- Segments update"
    Webhook-->>Store: "200 OK"
```

**Implementation** ([skills/klaviyo.md:689-723]()):
```typescript
async function syncOrderToKlaviyo(order: Order) {
  // 1. Upsert customer profile
  await upsertProfile({
    email: order.customerEmail,
    firstName: order.customerFirstName,
    lastName: order.customerLastName,
    phone: order.customerPhone,
  });
  
  // 2. Update lifetime metrics
  await updateProfileProperties(
    await getProfileIdByEmail(order.customerEmail),
    {
      last_order_date: new Date().toISOString(),
      total_orders: order.customerOrderCount,
      lifetime_value: order.customerLifetimeValue,
    }
  );
  
  // 3. Track order event
  await trackEvent({
    email: order.customerEmail,
    eventName: "Placed Order",
    properties: {
      OrderId: order.id,
      Items: order.items, // Required for product recommendations
      // ...
    },
    value: order.total,
    uniqueId: order.id, // Prevent duplicates
  });
}
```

**Sources:** [skills/klaviyo.md:685-723](), [skills/woocommerce.md:484-522]()

### Subscription Status Synchronization

Pattern for syncing subscription changes from application to Klaviyo:

```typescript
// When subscription changes
async function syncSubscriptionStatus(user: User, status: string) {
  await updateProfileProperties(user.klaviyoProfileId, {
    subscription_status: status,
    subscription_plan: user.plan,
    subscription_updated_at: new Date().toISOString(),
  });
  
  await trackEvent({
    email: user.email,
    eventName: `Subscription ${status}`,
    properties: {
      plan: user.plan,
      mrr: user.mrr,
    },
    value: status === "cancelled" ? -user.mrr : user.mrr,
  });
}
```

**Sources:** [skills/klaviyo.md:728-746]()

### Rate Limit Handling

All three platforms implement rate limiting with retry logic:

**Klaviyo Rate Limits** ([skills/klaviyo.md:583-587]()):
- Burst: 75 requests/second
- Steady: 700 requests/minute

**Retry Pattern** ([skills/klaviyo.md:590-623]()):
```typescript
async function klaviyoRequestWithRetry(
  endpoint: string,
  method: string,
  body?: object,
  retries = 3
): Promise<any> {
  for (let attempt = 0; attempt < retries; attempt++) {
    const response = await fetch(`${KLAVIYO_BASE_URL}${endpoint}`, {
      method,
      headers: { /* ... */ },
      body: body ? JSON.stringify(body) : undefined,
    });
    
    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get("Retry-After") || "5");
      await new Promise(r => setTimeout(r, retryAfter * 1000));
      continue;
    }
    
    if (!response.ok) {
      throw new Error(`Klaviyo error: ${response.status}`);
    }
    
    return response.json();
  }
  throw new Error("Max retries exceeded");
}
```

**Sources:** [skills/klaviyo.md:579-623](), [skills/woocommerce.md:682-717]()

---

## Environment Variables & Credentials

All e-commerce integrations use centralized credential management via `Access.txt`:

| Platform | Environment Variables | Pattern Validation |
|----------|----------------------|-------------------|
| Medusa | `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `COOKIE_SECRET` | Database connection strings |
| WooCommerce | `WC_STORE_URL`, `WC_CONSUMER_KEY`, `WC_CONSUMER_SECRET`, `WC_WEBHOOK_SECRET` | `ck_[a-f0-9]{40}`, `cs_[a-f0-9]{40}` |
| Klaviyo | `KLAVIYO_PRIVATE_KEY`, `KLAVIYO_PUBLIC_KEY`, `KLAVIYO_WEBHOOK_SECRET` | `pk_[a-f0-9]{32}`, `[A-Z0-9]{6}` |

**WooCommerce Credentials** ([skills/woocommerce.md:723-735]()):
```bash
# .env
WC_STORE_URL=https://your-store.com
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WC_WEBHOOK_SECRET=your_webhook_secret
```

**Klaviyo Credentials** ([skills/klaviyo.md:752-763]()):
```bash
# .env
KLAVIYO_PRIVATE_KEY=pk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
KLAVIYO_PUBLIC_KEY=XXXXXX
KLAVIYO_WEBHOOK_SECRET=your_webhook_secret
```

**Medusa Credentials** ([skills/medusa.md:125-140]()):
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/medusa
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-super-secret-jwt-key
COOKIE_SECRET=your-super-secret-cookie-key
```

The credential management system follows the pattern documented in [Credentials Management](#6.2), with automatic validation against regex patterns defined in `credentials.md`.

**Sources:** [skills/medusa.md:123-141](), [skills/woocommerce.md:722-735](), [skills/klaviyo.md:750-763]()

---

## Common Anti-Patterns

### Across All Platforms

| Anti-Pattern | Impact | Correct Approach |
|--------------|--------|------------------|
| Hardcoded API keys in code | Security vulnerability, detected by pre-commit hooks | Use `Access.txt` → `.env` pattern |
| Missing webhook signature verification | Security vulnerability, allows forged requests | Always verify signatures with HMAC |
| Ignoring rate limits | API throttling, failed requests | Implement retry with exponential backoff |
| Synchronous processing in webhooks | Timeout errors, lost events | Queue events for async processing |
| Missing unique IDs for events | Duplicate tracking, inflated metrics | Use order IDs as `unique_id` |

### Medusa-Specific

- **Editing `.medusa/` folder** - Auto-generated, will be overwritten ([skills/medusa.md:755]())
- **Direct database access** - Use services and modules for consistency ([skills/medusa.md:756]())
- **Skipping workflows for complex ops** - Workflows provide automatic rollback ([skills/medusa.md:757]())

### WooCommerce-Specific

- **Plain permalinks** - API won't work without pretty permalinks ([skills/woocommerce.md:768]())
- **HTTP in production** - HTTPS required for Basic Auth ([skills/woocommerce.md:769]())
- **Large single requests** - Use pagination for bulk operations ([skills/woocommerce.md:771]())

### Klaviyo-Specific

- **Missing email/phone** - Every profile needs at least one identifier ([skills/klaviyo.md:796]())
- **Missing Items array** - Required for product recommendations in flows ([skills/klaviyo.md:798]())
- **Client-side only tracking** - Server-side tracking is more reliable ([skills/klaviyo.md:799]())
- **Missing revenue tracking** - Include `$value` for ROI attribution ([skills/klaviyo.md:802]())

**Sources:** [skills/medusa.md:753-760](), [skills/woocommerce.md:766-774](), [skills/klaviyo.md:794-803]()

---

## Testing Checklist

### Medusa

Setup verification:
- [ ] PostgreSQL database configured ([skills/medusa.md:731]())
- [ ] Redis configured (optional but recommended) ([skills/medusa.md:732]())
- [ ] Admin user created via `npx medusa user` ([skills/medusa.md:733]())
- [ ] CORS origins configured for storefront and admin ([skills/medusa.md:734]())
- [ ] JWT/Cookie secrets set ([skills/medusa.md:735]())

Customization testing:
- [ ] Custom modules registered and resolvable ([skills/medusa.md:739]())
- [ ] Custom API routes accessible ([skills/medusa.md:740]())
- [ ] Subscribers responding to events ([skills/medusa.md:741]())
- [ ] Workflows executing with rollback on errors ([skills/medusa.md:742]())

### WooCommerce

Pre-integration:
- [ ] HTTPS enabled on store ([skills/woocommerce.md:744]())
- [ ] Permalinks set to non-Plain setting ([skills/woocommerce.md:745]())
- [ ] API keys generated with appropriate permissions ([skills/woocommerce.md:746]())
- [ ] Webhook secret configured ([skills/woocommerce.md:747]())

Testing:
- [ ] API connection successful ([skills/woocommerce.md:758]())
- [ ] Product CRUD operations working ([skills/woocommerce.md:759]())
- [ ] Order creation/updates functional ([skills/woocommerce.md:760]())
- [ ] Webhook delivery verified ([skills/woocommerce.md:761]())
- [ ] Pagination working for large datasets ([skills/woocommerce.md:762]())

### Klaviyo

Setup:
- [ ] Private API key generated ([skills/klaviyo.md:772]())
- [ ] Public API key noted (company ID) ([skills/klaviyo.md:773]())
- [ ] API revision set in headers (`2024-10-15`) ([skills/klaviyo.md:774]())

Integration:
- [ ] Profile sync on signup/update ([skills/klaviyo.md:778]())
- [ ] Key events tracked (view, cart, order) ([skills/klaviyo.md:779]())
- [ ] Order events include Items array ([skills/klaviyo.md:780]())
- [ ] Revenue tracked with `$value` ([skills/klaviyo.md:781]())
- [ ] Unique IDs used for deduplication ([skills/klaviyo.md:782]())

Testing:
- [ ] Profile creation verified in dashboard ([skills/klaviyo.md:786]())
- [ ] Events appearing in Klaviyo dashboard ([skills/klaviyo.md:787]())
- [ ] Webhook delivery successful ([skills/klaviyo.md:788]())
- [ ] Rate limit handling functional ([skills/klaviyo.md:789]())

**Sources:** [skills/medusa.md:728-750](), [skills/woocommerce.md:739-763](), [skills/klaviyo.md:767-790]()

---

# Page: Reddit Ads Integration

# Reddit Ads Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/reddit-ads.md](skills/reddit-ads.md)

</details>



**Purpose:** This document covers Reddit Ads API integration patterns for programmatically creating, managing, and optimizing advertising campaigns on Reddit. It includes OAuth2 authentication, API client implementations, campaign management workflows, conversion tracking, reporting, and an AI-powered agentic optimization service that automatically scales winners and pauses poor performers.

For general integration patterns and credential management, see [Security and Credentials](#6). For other advertising and analytics platforms, see [Analytics with PostHog](#7.1).

---

## Overview

The Reddit Ads integration enables automated campaign management through a hierarchical structure: Account → Campaign → Ad Group → Ad. The system provides both imperative API clients for direct control and a declarative agentic optimizer service that uses Claude to make optimization decisions autonomously.

**Sources:** [skills/reddit-ads.md:1-30]()

### Campaign Hierarchy

```mermaid
graph TB
    Account["Account<br/>(t2_xxxxx)"]
    Campaign["Campaign<br/>objective, budget, schedule"]
    AdGroup["Ad Group<br/>targeting, bidding, placement"]
    Ad["Ad<br/>creative, headline, CTA"]
    Audiences["Custom Audiences<br/>customer lists, lookalikes"]
    Conversions["Conversions API<br/>server-side event tracking"]
    
    Account --> Campaign
    Campaign --> AdGroup
    AdGroup --> Ad
    Account --> Audiences
    Account --> Conversions
    
    AdGroup -.->|"targets"| Audiences
    Conversions -.->|"attributes to"| Ad
```

**Campaign Properties:**
- Objective: `BRAND_AWARENESS`, `TRAFFIC`, `CONVERSIONS`, `VIDEO_VIEWS`, `APP_INSTALLS`
- Budget: `DAILY` (average per day) or `LIFETIME` (total spend)
- Amount: Specified in micros (1 USD = 1,000,000 micros)

**Ad Group Properties:**
- Bidding: `LOWEST_COST`, `COST_CAP`, `MANUAL`
- Targeting: Communities (subreddits), interests, keywords, geo, devices, custom audiences
- Goal: `CLICKS`, `IMPRESSIONS`, `CONVERSIONS`

**Ad Properties:**
- Type: `LINK`, `TEXT`, `VIDEO`, `CAROUSEL`, `PRODUCT`
- Call-to-action: `SHOP_NOW`, `SIGN_UP`, `LEARN_MORE`, `DOWNLOAD`, etc.
- Creative: Headline (300 chars max), body, thumbnail, video

**Sources:** [skills/reddit-ads.md:12-29](), [skills/reddit-ads.md:460-506](), [skills/reddit-ads.md:524-596](), [skills/reddit-ads.md:627-708]()

---

## Authentication

### OAuth2 Flow

Reddit Ads uses OAuth2 with three-step authorization:

1. **Authorization URL Generation** - Redirect user to Reddit with required scopes
2. **Code Exchange** - Trade authorization code for access/refresh tokens
3. **Token Refresh** - Use refresh token to obtain new access tokens before expiry

```mermaid
sequenceDiagram
    participant App as "Application"
    participant User as "User Browser"
    participant Reddit as "Reddit OAuth"
    participant AdsAPI as "Ads API"
    
    App->>User: "Redirect to authorization URL"
    User->>Reddit: "GET /api/v1/authorize"
    Reddit->>User: "Login & consent screen"
    User->>Reddit: "Approve access"
    Reddit->>App: "Redirect with auth code"
    App->>Reddit: "POST /api/v1/access_token<br/>(exchange code)"
    Reddit->>App: "access_token + refresh_token"
    App->>AdsAPI: "API requests with Bearer token"
    
    Note over App,AdsAPI: "Token expires in 3600s"
    
    App->>Reddit: "POST /api/v1/access_token<br/>(refresh token)"
    Reddit->>App: "New access_token"
```

**Required Environment Variables:**

| Variable | Purpose | Format |
|----------|---------|--------|
| `REDDIT_ADS_CLIENT_ID` | OAuth client ID | Alphanumeric string |
| `REDDIT_ADS_CLIENT_SECRET` | OAuth client secret | Base64-encodable string |
| `REDDIT_ADS_ACCOUNT_ID` | Ads account identifier | `t2_xxxxx` format |
| `REDDIT_ADS_ACCESS_TOKEN` | Current bearer token | JWT-like string |
| `REDDIT_ADS_REFRESH_TOKEN` | Long-lived refresh token | Opaque string |

**Required Scopes:**

| Scope | Access Level |
|-------|--------------|
| `adsread` | Read campaigns, ad groups, ads, reports |
| `adsedit` | Create/update campaigns, ad groups, ads |
| `history` | Access account history |

**Sources:** [skills/reddit-ads.md:33-184](), [skills/reddit-ads.md:986-995]()

### Token Management Implementation

**JavaScript/TypeScript:**
- Authorization URL: [skills/reddit-ads.md:54-63]()
- Code exchange: [skills/reddit-ads.md:66-87]()
- Token refresh: [skills/reddit-ads.md:90-109]()

**Python:**
- Authorization URL: [skills/reddit-ads.md:124-135]()
- Code exchange: [skills/reddit-ads.md:137-155]()
- Token refresh: [skills/reddit-ads.md:157-174]()

---

## API Client Architecture

### RedditAdsClient Structure

Both Node.js and Python implementations provide identical method signatures for consistent cross-language usage.

```mermaid
graph TB
    subgraph "RedditAdsClient Class"
        Config["RedditAdsConfig<br/>accessToken, accountId"]
        Request["_request()<br/>HTTP wrapper with auth"]
        
        subgraph "Account Methods"
            GetAccount["getAccount()"]
        end
        
        subgraph "Campaign Methods"
            GetCampaigns["getCampaigns()"]
            GetCampaign["getCampaign(id)"]
            CreateCampaign["createCampaign(data)"]
            UpdateCampaign["updateCampaign(id, data)"]
        end
        
        subgraph "Ad Group Methods"
            GetAdGroups["getAdGroups(campaignId?)"]
            GetAdGroup["getAdGroup(id)"]
            CreateAdGroup["createAdGroup(data)"]
            UpdateAdGroup["updateAdGroup(id, data)"]
        end
        
        subgraph "Ad Methods"
            GetAds["getAds(adGroupId?)"]
            CreateAd["createAd(data)"]
            UpdateAd["updateAd(id, data)"]
        end
        
        subgraph "Reporting & Audiences"
            GetReport["getReport(request)"]
            GetAudiences["getCustomAudiences()"]
            CreateAudience["createCustomAudience(data)"]
        end
        
        Config --> Request
        Request --> GetAccount
        Request --> GetCampaigns
        Request --> GetCampaign
        Request --> CreateCampaign
        Request --> UpdateCampaign
        Request --> GetAdGroups
        Request --> GetAdGroup
        Request --> CreateAdGroup
        Request --> UpdateAdGroup
        Request --> GetAds
        Request --> CreateAd
        Request --> UpdateAd
        Request --> GetReport
        Request --> GetAudiences
        Request --> CreateAudience
    end
    
    API["Reddit Ads API<br/>https://ads-api.reddit.com/api/v2.0"]
    
    GetAccount --> API
    GetCampaigns --> API
    CreateCampaign --> API
    GetAdGroups --> API
    CreateAdGroup --> API
    GetAds --> API
    CreateAd --> API
    GetReport --> API
    GetAudiences --> API
```

**Node.js Implementation:**
- Class definition: [skills/reddit-ads.md:192-307]()
- Constructor: [skills/reddit-ads.md:203-206]()
- Request wrapper: [skills/reddit-ads.md:208-231]()
- Campaign methods: [skills/reddit-ads.md:238-253]()
- Ad Group methods: [skills/reddit-ads.md:255-273]()
- Ad methods: [skills/reddit-ads.md:275-289]()
- Reporting: [skills/reddit-ads.md:291-294]()
- Custom audiences: [skills/reddit-ads.md:296-303]()

**Python Implementation:**
- Class definition: [skills/reddit-ads.md:312-400]()
- Constructor: [skills/reddit-ads.md:325-333]()
- Request wrapper: [skills/reddit-ads.md:335-344]()
- Campaign methods: [skills/reddit-ads.md:351-361]()
- Ad Group methods: [skills/reddit-ads.md:364-376]()
- Ad methods: [skills/reddit-ads.md:378-388]()
- Reporting: [skills/reddit-ads.md:390-392]()
- Custom audiences: [skills/reddit-ads.md:394-399]()

**Sources:** [skills/reddit-ads.md:187-400]()

### API Endpoint Mapping

```mermaid
graph LR
    subgraph "Client Methods"
        GetCampaigns["getCampaigns()"]
        CreateCampaign["createCampaign()"]
        UpdateCampaign["updateCampaign()"]
        CreateAdGroup["createAdGroup()"]
        CreateAd["createAd()"]
        GetReport["getReport()"]
    end
    
    subgraph "HTTP Endpoints"
        GetCampaignsEP["GET /accounts/{id}/campaigns"]
        CreateCampaignEP["POST /accounts/{id}/campaigns"]
        UpdateCampaignEP["PUT /accounts/{id}/campaigns/{cid}"]
        CreateAdGroupEP["POST /accounts/{id}/ad_groups"]
        CreateAdEP["POST /accounts/{id}/ads"]
        GetReportEP["POST /accounts/{id}/reports"]
    end
    
    GetCampaigns --> GetCampaignsEP
    CreateCampaign --> CreateCampaignEP
    UpdateCampaign --> UpdateCampaignEP
    CreateAdGroup --> CreateAdGroupEP
    CreateAd --> CreateAdEP
    GetReport --> GetReportEP
```

**Base URL:** `https://ads-api.reddit.com/api/v2.0`  
**Rate Limit:** 1 request per second  
**Authentication:** Bearer token in `Authorization` header

**Complete endpoint reference:**
- Account endpoints: [skills/reddit-ads.md:406-411]()
- Campaign endpoints: [skills/reddit-ads.md:413-421]()
- Ad Group endpoints: [skills/reddit-ads.md:423-431]()
- Ad endpoints: [skills/reddit-ads.md:433-441]()
- Custom audience endpoints: [skills/reddit-ads.md:443-450]()
- Report endpoints: [skills/reddit-ads.md:452-456]()

**Sources:** [skills/reddit-ads.md:404-457]()

---

## Campaign Management Workflow

### Complete Campaign Creation

The typical workflow creates entities in sequence: Campaign → Ad Group → Ad. Each entity requires the parent's ID.

```mermaid
sequenceDiagram
    participant Client as "RedditAdsClient"
    participant API as "Reddit Ads API"
    
    Note over Client,API: "Step 1: Create Campaign"
    Client->>API: "createCampaign({<br/>objective: 'TRAFFIC',<br/>budget: 50M micros<br/>})"
    API-->>Client: "campaign_id: 'camp_123'"
    
    Note over Client,API: "Step 2: Create Ad Group"
    Client->>API: "createAdGroup({<br/>campaign_id: 'camp_123',<br/>targeting: {...}<br/>})"
    API-->>Client: "ad_group_id: 'ag_456'"
    
    Note over Client,API: "Step 3: Create Ad"
    Client->>API: "createAd({<br/>ad_group_id: 'ag_456',<br/>headline: '...',<br/>thumbnail_url: '...'<br/>})"
    API-->>Client: "ad_id: 'ad_789'"
    
    Note over Client,API: "Campaign ready to enable"
```

**Implementation example:** [skills/reddit-ads.md:1070-1140]()

**Sources:** [skills/reddit-ads.md:1068-1140]()

### Campaign Configuration

**CampaignCreate Interface:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Campaign name | `"Q1 2025 Traffic Campaign"` |
| `objective` | enum | Campaign goal | `"TRAFFIC"` |
| `is_enabled` | boolean | Active status | `false` (start paused) |
| `budget_type` | enum | Budget model | `"DAILY"` |
| `budget_total_amount_micros` | number | Budget in micros | `50_000_000` ($50) |
| `start_time` | ISO 8601 | Campaign start | `"2025-01-15T00:00:00Z"` |
| `end_time` | ISO 8601 | Campaign end (optional) | `"2025-03-31T23:59:59Z"` |

**Objective options:** [skills/reddit-ads.md:463-471]()  
**Budget types:** [skills/reddit-ads.md:473-478]()  
**Example payload:** [skills/reddit-ads.md:494-505]()

**Sources:** [skills/reddit-ads.md:460-520]()

### Ad Group Configuration

**AdGroupCreate Interface:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Ad group name |
| `campaign_id` | string | Parent campaign ID |
| `is_enabled` | boolean | Active status |
| `bid_strategy` | enum | `LOWEST_COST`, `COST_CAP`, `MANUAL` |
| `goal_type` | enum | `CLICKS`, `IMPRESSIONS`, `CONVERSIONS` |
| `targeting` | object | Targeting configuration |
| `targeting.communities` | string[] | Subreddit names (without `r/`) |
| `targeting.interests` | string[] | Interest categories |
| `targeting.keywords` | string[] | Keyword targets |
| `targeting.geo_locations` | object | Geographic targeting |
| `targeting.devices` | enum[] | `DESKTOP`, `MOBILE`, `TABLET` |
| `targeting.custom_audience_ids` | string[] | Custom audience IDs |

**Bidding strategies:** [skills/reddit-ads.md:526-532]()  
**Targeting options:** [skills/reddit-ads.md:534-543]()  
**Example payload:** [skills/reddit-ads.md:572-596]()

**Sources:** [skills/reddit-ads.md:522-623]()

### Ad Configuration

**AdCreate Interface:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Ad name |
| `ad_group_id` | string | Parent ad group ID |
| `is_enabled` | boolean | Active status |
| `type` | enum | `LINK`, `TEXT`, `VIDEO`, `CAROUSEL`, `PRODUCT` |
| `headline` | string | Ad headline (max 300 chars) |
| `body` | string | Ad body text (optional) |
| `url` | string | Landing page URL |
| `display_url` | string | Display URL (optional) |
| `call_to_action` | string | CTA button text |
| `thumbnail_url` | string | Image URL (for image/video ads) |
| `video_url` | string | Video URL (for video ads) |

**Ad types:** [skills/reddit-ads.md:629-637]()  
**CTA options:** [skills/reddit-ads.md:639-655]() (13 options including `SHOP_NOW`, `SIGN_UP`, `LEARN_MORE`)  
**Example payload:** [skills/reddit-ads.md:674-688]()

**Sources:** [skills/reddit-ads.md:625-707]()

---

## Conversion Tracking

### Conversions API

Server-side event tracking for accurate attribution and optimization. Events are sent to Reddit's Conversions API endpoint with hashed PII data.

**Event Types:**

| Event Type | Description | Use Case |
|------------|-------------|----------|
| `PAGE_VISIT` | Page view | Track landing page visits |
| `VIEW_CONTENT` | Product/content view | Track product page views |
| `SEARCH` | Search action | Track site search usage |
| `ADD_TO_CART` | Add to cart | E-commerce funnel tracking |
| `ADD_TO_WISHLIST` | Add to wishlist | Intent tracking |
| `PURCHASE` | Completed purchase | Revenue attribution |
| `LEAD` | Lead submission | Lead generation tracking |
| `SIGN_UP` | Account creation | User acquisition |
| `CUSTOM` | Custom event | Domain-specific events |

**Sources:** [skills/reddit-ads.md:714-725]()

### ConversionEvent Structure

```mermaid
graph TB
    Event["ConversionEvent"]
    
    subgraph "Required Fields"
        EventAt["event_at<br/>(Unix timestamp ms)"]
        EventType["event_type<br/>(tracking_type + custom_event_name)"]
    end
    
    subgraph "User Identity (Hashed)"
        Email["email<br/>(SHA256)"]
        Phone["phone_number<br/>(SHA256)"]
        ExtID["external_id"]
        IP["ip_address"]
        UA["user_agent"]
        AAID["aaid<br/>(Android)"]
        IDFA["idfa<br/>(iOS)"]
    end
    
    subgraph "Event Metadata"
        ConvID["conversion_id<br/>(unique)"]
        Value["value_decimal"]
        Currency["currency"]
        Items["item_count"]
        Products["products[]"]
    end
    
    subgraph "Attribution"
        ClickID["click_id<br/>(rdt_cid param)"]
    end
    
    Event --> EventAt
    Event --> EventType
    Event --> Email
    Event --> Phone
    Event --> ExtID
    Event --> IP
    Event --> UA
    Event --> AAID
    Event --> IDFA
    Event --> ConvID
    Event --> Value
    Event --> Currency
    Event --> Items
    Event --> Products
    Event --> ClickID
```

**Interface definition:** [skills/reddit-ads.md:728-757]()

**PII Hashing Rules:**
- Algorithm: SHA256
- Normalization: Lowercase, trim whitespace
- Email: Hash after normalization
- Phone: E.164 format before hashing

**JavaScript hashing:** [skills/reddit-ads.md:765-770]()  
**Python hashing:** [skills/reddit-ads.md:827-829]()

**Constraints:**
- Events must occur within **last 7 days**
- Maximum **500 events per batch**
- Include `click_id` when available for attribution
- Use `test_mode: true` for testing

**Sources:** [skills/reddit-ads.md:710-885]()

### Sending Conversion Events

**JavaScript Implementation:**

Endpoint: `POST https://ads-api.reddit.com/api/v2.0/conversions/events/{pixel_id}`

Request body structure:
```
{
  events: ConversionEvent[],
  test_mode: boolean
}
```

**Implementation:** [skills/reddit-ads.md:772-820]()

**Python Implementation:**

Same endpoint and structure, different HTTP client.

**Implementation:** [skills/reddit-ads.md:831-876]()

**Sources:** [skills/reddit-ads.md:760-885]()

---

## Custom Audiences

### Audience Types

| Type | Description | Minimum Size |
|------|-------------|--------------|
| `CUSTOMER_LIST` | Upload hashed emails/phone/MAIDs | 1,000 matched users |
| `WEBSITE_VISITORS` | Pixel-based retargeting | Varies |
| `LOOKALIKE` | Similar to source audience | Source must have 1,000+ |

**CustomAudienceCreate Interface:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Audience name |
| `type` | enum | `CUSTOMER_LIST`, `WEBSITE_VISITORS`, `LOOKALIKE` |
| `description` | string | Optional description |
| `users` | array | User identifiers (hashed) |
| `users[].email_sha256` | string | Hashed email address |
| `users[].maid_sha256` | string | Hashed mobile advertising ID |

**Example:** [skills/reddit-ads.md:911-921]()

**Match Rates:**
- Displayed as ranges for privacy (e.g., "1,000 - 5,000")
- 1,000 matched users minimum to be targetable
- Higher match rates improve campaign performance

**Sources:** [skills/reddit-ads.md:887-928]()

---

## Reporting

### Report Request Structure

**ReportRequest Interface:**

| Field | Type | Description |
|-------|------|-------------|
| `start_date` | string | Start date (YYYY-MM-DD) |
| `end_date` | string | End date (YYYY-MM-DD) |
| `level` | enum | `ACCOUNT`, `CAMPAIGN`, `AD_GROUP`, `AD` |
| `metrics` | string[] | Metrics to include |
| `dimensions` | string[] | Breakdown dimensions (e.g., `date`) |
| `filters` | object | Optional filters |
| `filters.campaign_ids` | string[] | Filter by campaign IDs |
| `filters.ad_group_ids` | string[] | Filter by ad group IDs |

**Example request:** [skills/reddit-ads.md:948-965]()

**Sources:** [skills/reddit-ads.md:930-965]()

### Available Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| `impressions` | Total impressions | Count |
| `clicks` | Total clicks | Count |
| `spend` | Total spend | Account currency |
| `ctr` | Click-through rate | Percentage |
| `cpc` | Cost per click | Currency |
| `cpm` | Cost per 1,000 impressions | Currency |
| `conversions` | Total conversions | Count |
| `conversion_rate` | Conversions / Clicks | Percentage |
| `cpa` | Cost per acquisition | Currency |
| `video_views` | Video view count | Count |
| `video_completions` | Videos watched to completion | Count |

**Full metrics table:** [skills/reddit-ads.md:967-981]()

**Sources:** [skills/reddit-ads.md:967-981]()

---

## Agentic Optimization Service

### Architecture Overview

The agentic optimizer is a background service that automatically optimizes Reddit Ads campaigns using Claude AI to analyze performance data and execute optimizations. It runs on a scheduled interval (default: every 4-6 hours) and implements a feedback loop: Fetch → Analyze → Execute.

```mermaid
graph TB
    subgraph "RedditAdsOptimizerService"
        Cron["CronJob<br/>Schedule trigger"]
        
        subgraph "Data Collection"
            FetchPerf["fetchPerformanceData()<br/>Last 24h metrics"]
            GetReport["client.getReport()<br/>Ad-level data"]
        end
        
        subgraph "AI Analysis"
            AnalyzeAgent["analyzeWithAgent()<br/>Claude Sonnet 4"]
            Prompt["Performance data +<br/>Thresholds +<br/>Optimization goal"]
            Recommendations["OptimizationRecommendation[]<br/>PAUSE, SCALE, ADJUST_BID,<br/>KEEP, ROTATE_CREATIVE"]
        end
        
        subgraph "Execution"
            Execute["executeOptimizations()"]
            UpdateAd["client.updateAd()<br/>Pause poor performers"]
            UpdateAdGroup["client.updateAdGroup()<br/>Scale winners, adjust bids"]
            FlagCreative["flagForCreativeRefresh()<br/>Queue rotation"]
        end
        
        subgraph "Monitoring"
            LogResults["logOptimizationResults()"]
            SendAlerts["sendAlert()<br/>On failures"]
        end
    end
    
    Cron -->|"Every N hours"| FetchPerf
    FetchPerf --> GetReport
    GetReport --> AnalyzeAgent
    AnalyzeAgent --> Prompt
    Prompt --> Recommendations
    Recommendations --> Execute
    Execute --> UpdateAd
    Execute --> UpdateAdGroup
    Execute --> FlagCreative
    Execute --> LogResults
    Execute --> SendAlerts
```

**Service lifecycle:**
1. **Start:** Initialize CronJob with configured interval
2. **Fetch:** Query last 24h performance data at ad-level granularity
3. **Analyze:** Send performance data to Claude with optimization thresholds
4. **Execute:** Apply AI recommendations via Reddit Ads API
5. **Log:** Record actions taken and performance impact
6. **Alert:** Notify on failures or critical issues

**Sources:** [skills/reddit-ads.md:1207-1230]()

### RedditAdsOptimizerService Class

**Node.js Implementation:**

```mermaid
graph TB
    subgraph "RedditAdsOptimizerService Class"
        Config["OptimizationConfig<br/>Thresholds & settings"]
        Client["RedditAdsClient<br/>API operations"]
        Anthropic["Anthropic SDK<br/>Claude integration"]
        CronJob["CronJob<br/>Scheduler"]
        
        subgraph "Public Methods"
            Start["start()<br/>Begin optimization loop"]
            Stop["stop()<br/>Halt service"]
        end
        
        subgraph "Core Cycle"
            RunCycle["runOptimizationCycle()<br/>Main workflow"]
            Fetch["fetchPerformanceData()<br/>Returns PerformanceData[]"]
            Analyze["analyzeWithAgent()<br/>Returns OptimizationRecommendation[]"]
            ExecuteOpts["executeOptimizations()<br/>Apply recommendations"]
            LogOpts["logOptimizationResults()<br/>Record actions"]
        end
        
        Config --> Client
        Config --> Anthropic
        Config --> CronJob
        
        Start --> CronJob
        CronJob --> RunCycle
        RunCycle --> Fetch
        Fetch --> Analyze
        Analyze --> ExecuteOpts
        ExecuteOpts --> LogOpts
        
        Stop --> CronJob
    end
```

**Class structure:** [skills/reddit-ads.md:1234-1281]()  
**Constructor:** [skills/reddit-ads.md:1274-1281]()  
**Start method:** [skills/reddit-ads.md:1283-1294]()  
**Main cycle:** [skills/reddit-ads.md:1304-1322]()

**OptimizationConfig Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `accountId` | string | Required | Reddit Ads account ID |
| `accessToken` | string | Required | Current bearer token |
| `refreshToken` | string | Required | Refresh token |
| `minCTR` | number | 0.005 | Pause ads below 0.5% CTR |
| `maxCPA` | number | 50 | Pause ads above $50 CPA |
| `minImpressions` | number | 1000 | Min impressions before decisions |
| `budgetScaleFactor` | number | 1.5 | Scale winners by 1.5x |
| `optimizationGoal` | enum | `CONVERSIONS` | `CLICKS`, `CONVERSIONS`, `ROAS` |
| `checkIntervalHours` | number | 4 | Hours between optimization runs |

**Config interface:** [skills/reddit-ads.md:1243-1252]()

**Python Implementation:**

Same architecture with Python-specific libraries (`schedule` instead of `cron`, `anthropic` Python SDK).

**Class structure:** [skills/reddit-ads.md:1545-1577]()  
**Config dataclass:** [skills/reddit-ads.md:1511-1521]()  
**Start method:** [skills/reddit-ads.md:1555-1572]()  
**Entry point:** [skills/reddit-ads.md:1756-1772]()

**Sources:** [skills/reddit-ads.md:1232-1772]()

### Performance Data Collection

The optimizer fetches last 24 hours of ad-level performance data to make decisions.

**PerformanceData Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `campaignId` | string | Campaign identifier |
| `adGroupId` | string | Ad group identifier |
| `adId` | string | Ad identifier |
| `impressions` | number | Total impressions |
| `clicks` | number | Total clicks |
| `spend` | number | Total spend (dollars) |
| `conversions` | number | Total conversions |
| `ctr` | number | Click-through rate |
| `cpc` | number | Cost per click |
| `cpa` | number | Cost per acquisition |
| `roas` | number | Return on ad spend |

**JavaScript implementation:** [skills/reddit-ads.md:1324-1352]()  
**Python implementation:** [skills/reddit-ads.md:1600-1630]()

**Report configuration:**
- Date range: Last 24 hours
- Level: `AD` (most granular)
- Metrics: `impressions`, `clicks`, `spend`, `conversions`, `ctr`, `cpc`, `cpa`, `conversion_value`

**Sources:** [skills/reddit-ads.md:1254-1266](), [skills/reddit-ads.md:1324-1352](), [skills/reddit-ads.md:1600-1630]()

### AI-Powered Analysis

Claude analyzes performance data and returns structured recommendations. The prompt includes performance data, optimization configuration, and decision criteria.

**Prompt Structure:**

1. **Performance Data:** JSON array of `PerformanceData` objects
2. **Optimization Configuration:** Thresholds and goals from `OptimizationConfig`
3. **Task Instructions:** Analyze each ad and recommend one action
4. **Action Types:**
   - `PAUSE`: Poor performers (low CTR, high CPA, no conversions)
   - `SCALE`: Winners (high CTR, low CPA, good ROAS)
   - `ADJUST_BID`: Moderate performers needing bid adjustment
   - `KEEP`: Insufficient data or acceptable performance
   - `ROTATE_CREATIVE`: Good targeting but creative fatigue
5. **Output Format:** JSON array of `OptimizationRecommendation` objects

**OptimizationRecommendation Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `adId` | string | Ad identifier |
| `adGroupId` | string | Ad group identifier |
| `action` | enum | `PAUSE`, `SCALE`, `ADJUST_BID`, `KEEP`, `ROTATE_CREATIVE` |
| `reason` | string | Explanation for action |
| `newBidMicros` | number? | New bid amount (for `ADJUST_BID`) |
| `budgetMultiplier` | number? | Budget multiplier (for `SCALE`) |

**JavaScript implementation:** [skills/reddit-ads.md:1354-1404]()  
**Python implementation:** [skills/reddit-ads.md:1632-1695]()

**Model used:** `claude-sonnet-4-20250514` with 4096 max tokens

**Sources:** [skills/reddit-ads.md:1354-1404](), [skills/reddit-ads.md:1476-1483](), [skills/reddit-ads.md:1632-1695]()

### Optimization Execution

The service executes AI recommendations by calling Reddit Ads API methods.

```mermaid
graph TB
    Recs["OptimizationRecommendation[]"]
    
    subgraph "Action Handlers"
        Pause["PAUSE<br/>client.updateAd(id, {is_enabled: false})"]
        Scale["SCALE<br/>client.updateAdGroup(id, {<br/>budget_total_amount_micros: current * multiplier<br/>})"]
        AdjustBid["ADJUST_BID<br/>client.updateAdGroup(id, {<br/>bid_amount_micros: newBidMicros<br/>})"]
        Rotate["ROTATE_CREATIVE<br/>flagForCreativeRefresh(adId)"]
        Keep["KEEP<br/>No action"]
    end
    
    Recs -->|"action: PAUSE"| Pause
    Recs -->|"action: SCALE"| Scale
    Recs -->|"action: ADJUST_BID"| AdjustBid
    Recs -->|"action: ROTATE_CREATIVE"| Rotate
    Recs -->|"action: KEEP"| Keep
    
    Pause -->|"Protects budget"| Done["Log result"]
    Scale -->|"Increases spend on winners"| Done
    AdjustBid -->|"Fine-tunes performance"| Done
    Rotate -->|"Queues refresh"| Done
    Keep --> Done
```

**Execution logic:**

1. **PAUSE:** Set `is_enabled: false` on ad to stop spending on poor performers
2. **SCALE:** Get current ad group budget, multiply by `budgetMultiplier` (default 1.5x), update ad group
3. **ADJUST_BID:** Update ad group with new bid amount (for `COST_CAP` or `MANUAL` strategies)
4. **ROTATE_CREATIVE:** Flag ad for creative refresh (implementation-specific)
5. **KEEP:** No action, log for monitoring

**JavaScript implementation:** [skills/reddit-ads.md:1406-1449]()  
**Python implementation:** [skills/reddit-ads.md:1697-1727]()

**Error handling:** Each action wrapped in try-catch to prevent single failure from blocking entire cycle.

**Sources:** [skills/reddit-ads.md:1406-1449](), [skills/reddit-ads.md:1697-1727]()

### Optimization Strategies

The agentic optimizer implements multiple strategies based on performance thresholds:

**1. Performance-Based Pausing**
```
IF impressions > minImpressions AND ctr < minCTR → PAUSE
IF impressions > (minImpressions / 2) AND conversions = 0 → PAUSE
IF cpa > maxCPA → PAUSE
```

**2. Winner Scaling**
```
IF ctr > (minCTR * 2) AND cpa < maxCPA AND conversions > 5 → SCALE
Cap at 3x original budget to manage risk
```

**3. Bid Optimization**
```
IF position low AND ctr good → INCREASE bid 10-20%
IF cpa high but converting → DECREASE bid 10-15%
```

**4. Creative Fatigue Detection**
```
IF ctr declining 3 consecutive days → ROTATE_CREATIVE
IF frequency > 3 → ROTATE_CREATIVE
```

**5. Budget Reallocation**
```
Move budget from paused ads to scaled winners
Maintain total daily budget cap
```

**Strategy documentation:** [skills/reddit-ads.md:1816-1850]()

**Sources:** [skills/reddit-ads.md:1816-1850]()

### Multi-Agent Optimization Pattern

Advanced implementation using multiple specialized Claude agents working in sequence.

```mermaid
graph LR
    Data["Performance Data"]
    
    subgraph "Agent Pipeline"
        PA["Performance Analyst<br/>Identifies winners/losers"]
        BS["Budget Strategist<br/>Optimizes allocation"]
        CD["Creative Director<br/>Evaluates creative fatigue"]
        RM["Risk Manager<br/>Validates safety"]
    end
    
    Final["Final Recommendations"]
    
    Data --> PA
    PA --> BS
    BS --> CD
    CD --> RM
    RM --> Final
```

**Agent Roles:**

| Agent | System Prompt Focus | Output |
|-------|---------------------|--------|
| **Performance Analyst** | Identify top/poor performers, trends | Structured analysis with confidence scores |
| **Budget Strategist** | Optimize budget allocation | Budget increase/decrease recommendations |
| **Creative Director** | Evaluate creative performance | Creative refresh recommendations |
| **Risk Manager** | Ensure optimization safety | Approve/modify/reject recommendations |

**Each agent:**
1. Receives previous agents' outputs as context
2. Performs specialized analysis
3. Adds structured recommendations
4. Passes enriched context to next agent

**Implementation:** [skills/reddit-ads.md:1852-1933]()

**MultiAgentOptimizer workflow:**
```typescript
async runAgentPipeline(performanceData) {
  let context = { performanceData };
  
  for (const agent of AGENTS) {
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      system: agent.systemPrompt,
      messages: [{
        role: 'user',
        content: `Previous context:\n${JSON.stringify(context)}\n\nProvide your analysis.`
      }]
    });
    
    context[agent.name] = response.content[0];
  }
  
  return context;
}
```

**Sources:** [skills/reddit-ads.md:1852-1933]()

### Deployment Configuration

**Docker Deployment:**

Dockerfile structure:
- Base image: Python 3.11 slim
- Install dependencies from `requirements.txt`
- Copy application code
- Run optimizer service

**Docker Compose configuration:**

```yaml
services:
  reddit-ads-optimizer:
    build: .
    container_name: reddit-ads-optimizer
    restart: unless-stopped
    environment:
      - REDDIT_ADS_CLIENT_ID
      - REDDIT_ADS_CLIENT_SECRET
      - REDDIT_ADS_ACCOUNT_ID
      - REDDIT_ADS_ACCESS_TOKEN
      - REDDIT_ADS_REFRESH_TOKEN
      - ANTHROPIC_API_KEY
    volumes:
      - ./logs:/app/logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Dockerfile:** [skills/reddit-ads.md:1777-1789]()  
**Docker Compose:** [skills/reddit-ads.md:1791-1814]()

**Environment variables required:**
- Reddit Ads credentials (5 variables)
- `ANTHROPIC_API_KEY` for Claude access

**Restart policy:** `unless-stopped` ensures service recovers from failures

**Logging:** JSON file driver with 10MB rotation, 3 file retention

**Sources:** [skills/reddit-ads.md:1775-1814]()

### Monitoring and Observability

**OptimizationStats Interface:**

| Field | Type | Description |
|-------|------|-------------|
| `period` | string | Time period analyzed |
| `totalOptimizations` | number | Total recommendations executed |
| `actionBreakdown` | object | Count by action type |
| `actionBreakdown.paused` | number | Ads paused |
| `actionBreakdown.scaled` | number | Ad groups scaled |
| `actionBreakdown.bidAdjusted` | number | Bids adjusted |
| `actionBreakdown.creativeRotated` | number | Creatives flagged for rotation |
| `performanceImpact` | object | Before/after metrics |
| `performanceImpact.ctrChange` | number | CTR delta percentage |
| `performanceImpact.cpaChange` | number | CPA delta percentage |
| `performanceImpact.roasChange` | number | ROAS delta percentage |
| `performanceImpact.spendEfficiency` | number | Efficiency improvement |
| `budgetSaved` | number | Total budget saved by pausing |
| `revenueIncreased` | number | Total revenue from scaling |

**Logging implementation:**

JavaScript: [skills/reddit-ads.md:1455-1469]()  
Python: [skills/reddit-ads.md:1735-1747]()

**Log output example:**
```json
{
  "timestamp": "2025-01-15T14:30:00Z",
  "totalRecommendations": 47,
  "actions": {
    "paused": 12,
    "scaled": 5,
    "bidAdjusted": 8,
    "creativeRotation": 3,
    "kept": 19
  }
}
```

**Stats API interface:** [skills/reddit-ads.md:1936-1966]()

**Sources:** [skills/reddit-ads.md:1455-1469](), [skills/reddit-ads.md:1735-1747](), [skills/reddit-ads.md:1936-1966]()

---

## Best Practices

### Campaign Structure

Recommended hierarchy for maintainability and optimization:

```
Campaign (by objective/product line)
├── Ad Group: Subreddit Targeting - Tech
│   ├── Ad: Headline A + Image 1
│   └── Ad: Headline B + Image 1
├── Ad Group: Subreddit Targeting - Business
│   ├── Ad: Headline A + Image 1
│   └── Ad: Headline B + Image 1
└── Ad Group: Interest Targeting - Entrepreneurs
    ├── Ad: Headline A + Image 2
    └── Ad: Headline B + Image 2
```

**Principles:**
- Separate ad groups by targeting type (subreddits vs. interests vs. keywords)
- Test 2-3 ad variations per ad group
- Use clear, consistent naming conventions
- Keep campaigns focused on single objective

**Structure diagram:** [skills/reddit-ads.md:1003-1023]()

**Sources:** [skills/reddit-ads.md:999-1023]()

### Naming Conventions

**Campaign:** `[Objective] - [Product/Brand] - [Date Range]`  
Example: `TRAFFIC - ProductX - Q1-2025`

**Ad Group:** `[Targeting Type] - [Audience Description]`  
Example: `Subreddits - Tech Enthusiasts`

**Ad:** `[Headline Type] - [Creative Version]`  
Example: `Problem-Solution - Image-A`

**Sources:** [skills/reddit-ads.md:1025-1036]()

### Rate Limiting

**Constraint:** 1 request per second

**Implementation with exponential backoff:**

```typescript
async function rateLimitedRequest<T>(
  fn: () => Promise<T>,
  retries = 3
): Promise<T> {
  for (let i = 0; i < retries; i++) {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 sec delay
      return await fn();
    } catch (error: any) {
      if (error.status === 429 && i < retries - 1) {
        const delay = Math.pow(2, i) * 1000; // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      throw error;
    }
  }
  throw new Error('Max retries exceeded');
}
```

**Pattern:**
1. Wait 1 second before each request (rate limit compliance)
2. On 429 error, implement exponential backoff: 1s, 2s, 4s, etc.
3. Retry up to 3 times before failing
4. Batch operations where possible

**Implementation:** [skills/reddit-ads.md:1044-1064]()

**Sources:** [skills/reddit-ads.md:1038-1064]()

---

## Testing

### Test Checklist

| Category | Test Item | Validation |
|----------|-----------|------------|
| **Authentication** | OAuth flow completes | Access token received |
| **Authentication** | Token refresh works | New token before expiry |
| **Campaign Management** | Campaign creates with correct budget | Budget in micros correct |
| **Targeting** | Ad group targeting applied correctly | Subreddits/interests saved |
| **Creative** | Ad creative displays properly | Thumbnail/headline render |
| **Conversion Tracking** | Events tracked (test mode) | Events appear in reports |
| **Reporting** | Reports return expected metrics | All metrics present |
| **Rate Limiting** | Rate limiting handled gracefully | No 429 errors cascade |
| **Error Handling** | Error responses handled | Proper error messages |

**Full checklist:** [skills/reddit-ads.md:1144-1157]()

**Sources:** [skills/reddit-ads.md:1144-1157]()

### Mock API for Development

Using MSW (Mock Service Worker) for development and testing:

**Mock handlers:**
- `POST /api/v1/access_token` → Return mock tokens
- `GET /accounts/:accountId` → Return mock account data
- `POST /accounts/:accountId/campaigns` → Return mock campaign with ID

**Implementation:** [skills/reddit-ads.md:1159-1189]()

**Pattern:** Mock returns request body with generated ID, enabling full workflow testing without API calls.

**Sources:** [skills/reddit-ads.md:1159-1189]()

---

## Troubleshooting

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Invalid/expired token | Refresh access token using refresh token |
| `403 Forbidden` | Account not whitelisted | Contact Reddit Ads support for API access |
| `429 Too Many Requests` | Rate limit exceeded | Implement exponential backoff, reduce request rate |
| `400 Bad Request` | Invalid payload | Check required fields, data types, value ranges |
| `Audience too small` | < 1,000 matched users | Add more users to custom audience |

**Error handling in client:**
- All errors throw with `Reddit Ads API Error:` prefix
- Error response body included in message
- HTTP status available for conditional handling

**Client error handling:** [skills/reddit-ads.md:225-228]()

**Sources:** [skills/reddit-ads.md:1193-1201](), [skills/reddit-ads.md:225-228]()

---

## Resources

- [Reddit Ads API Documentation](https://ads-api.reddit.com/docs/)
- [Reddit Developer Portal](https://www.reddit.com/prefs/apps/)
- [Reddit Ads Help Center](https://business.reddithelp.com/s/article/Reddit-Ads-API)
- [OAuth2 Documentation](https://www.reddit.com/dev/api/oauth/)

**Sources:** [skills/reddit-ads.md:1970-1975]()

---

# Page: Team Collaboration

# Team Collaboration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document explains how multiple developers coordinate work on the same repository when using Claude Code. The system provides file-based state management, todo claiming, active session tracking, and conflict detection to prevent duplicate work and merge conflicts.

For implementation details of the coordination commands, see [Multi-Developer Coordination](#8.1). For details about the shared state file structures, see [Shared State Management](#8.2).

## The Coordination Problem

When multiple developers use Claude Code (or Claude Desktop) on the same repository, several coordination challenges arise:

- **Duplicate work**: Two developers unknowingly implement the same todo
- **Merge conflicts**: Multiple developers modify the same files simultaneously
- **Context loss**: Developer B doesn't know what Developer A is currently working on
- **Decision drift**: Architectural decisions made by one developer are invisible to others

Claude Bootstrap solves this with a file-based state management system that tracks active sessions, claimed todos, and file ownership through standard git workflows.

**Sources:** [README.md:211-253]()

## System Architecture

```mermaid
graph TB
    subgraph "Developer Workflow"
        DEV_A["Developer A<br/>Claude Code Session"]
        DEV_B["Developer B<br/>Claude Code Session"]
    end
    
    subgraph "Coordination Commands"
        CHECK["/check-contributors"]
        STATUS["/check-contributors --status"]
        TEAM["/check-contributors --team"]
    end
    
    subgraph "State Files (_project_specs/team/)"
        STATE["state.md<br/>Active sessions<br/>Claimed todos<br/>File ownership"]
        CONTRIB["contributors.md<br/>Team roster<br/>Focus areas<br/>Ownership"]
        HANDOFFS["handoffs/<br/>Context transfer<br/>Work notes"]
        DECISIONS["../decisions.md<br/>Shared decisions"]
    end
    
    subgraph "Conflict Detection"
        DETECT["Monitor file overlap"]
        WARN["⚠️ Conflict warnings"]
    end
    
    DEV_A --> CHECK
    DEV_B --> CHECK
    
    CHECK --> STATE
    CHECK --> CONTRIB
    STATUS --> STATE
    TEAM --> STATE
    TEAM --> CONTRIB
    
    STATE --> DETECT
    CONTRIB --> DETECT
    DETECT --> WARN
    
    DEV_A -.->|"Update on checkpoint"| STATE
    DEV_B -.->|"Update on checkpoint"| STATE
    
    DEV_A -.->|"Handoff notes"| HANDOFFS
    DEV_B -.->|"Read context"| HANDOFFS
    
    STATE -.->|"Log decisions"| DECISIONS
```

**Diagram: Team Collaboration System Components**

The system uses three primary state files in `_project_specs/team/` that are committed to git, enabling coordination through standard pull/push workflows without requiring external infrastructure.

**Sources:** [README.md:225-231](), [README.md:235-242]()

## Core Workflow Pattern

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Git as "git"
    participant Check as "/check-contributors"
    participant State as "state.md"
    participant Todos as "todos/active.md"
    participant Claude as "Claude Code"
    
    Dev->>Git: git pull
    Note over Git: Get latest state
    
    Dev->>Check: Run command
    Check->>State: Read current state
    Check->>Dev: Show active sessions<br/>Show claimed todos<br/>Show conflicts
    
    Dev->>State: Claim todo<br/>Update active session
    Dev->>Git: git add state.md<br/>git commit -m "Claim TODO-042"<br/>git push
    
    Dev->>Claude: Work on feature
    Note over Claude: Active development
    
    Dev->>State: Checkpoint update<br/>Log file changes
    Dev->>Git: git add state.md<br/>git commit & push
    
    Dev->>Claude: Continue work
    
    Dev->>State: Mark complete<br/>Clear active session
    Dev->>Todos: Move to completed.md
    Dev->>Git: git commit & push
```

**Diagram: Standard Team Collaboration Workflow**

The workflow enforces explicit state updates at key checkpoints: claiming work (start), progress updates (during), and completion (end). This creates visibility without requiring real-time communication.

**Sources:** [README.md:243-246]()

## The `/check-contributors` Command

The `/check-contributors` command is the primary entry point for team coordination. It detects whether a project is solo or team-based and offers appropriate actions.

**Command Variants:**

| Command | Purpose | Output |
|---------|---------|--------|
| `/check-contributors` | Full analysis and conversion | Detect mode, show state, offer conversion |
| `/check-contributors --status` | Quick status check | Show active sessions and claimed todos only |
| `/check-contributors --team` | Force team conversion | Create team structure immediately |

**Sources:** [README.md:249-253]()

### Detection Logic

```mermaid
flowchart TD
    START["Run /check-contributors"]
    
    CHECK_TEAM["Check _project_specs/team/<br/>directory exists?"]
    
    SOLO["Solo Project Mode"]
    TEAM["Team Project Mode"]
    
    OFFER["Offer conversion:<br/>'This looks like solo project.<br/>Convert to team?'"]
    
    CONVERT["Create team structure:<br/>- state.md<br/>- contributors.md<br/>- handoffs/"]
    
    SHOW_STATE["Show current state:<br/>- Active sessions<br/>- Claimed todos<br/>- File ownership<br/>- Conflict warnings"]
    
    START --> CHECK_TEAM
    CHECK_TEAM -->|"No"| SOLO
    CHECK_TEAM -->|"Yes"| TEAM
    
    SOLO --> OFFER
    OFFER -->|"Yes"| CONVERT
    OFFER -->|"No"| END["Continue solo"]
    
    CONVERT --> SHOW_STATE
    TEAM --> SHOW_STATE
    
    SHOW_STATE --> END
```

**Diagram: Project Mode Detection and Conversion**

**Sources:** [README.md:215-222]()

## State File Structure

### state.md Format

The `_project_specs/team/state.md` file tracks real-time project state:

```markdown
# Project State

Last updated: 2024-01-15 14:30 UTC

## Active Sessions

| Developer | Working On | Files | Started | Last Update |
|-----------|------------|-------|---------|-------------|
| alice | TODO-042: Email validation | src/auth/signup.ts, tests/signup.test.ts | 2024-01-15 13:00 | 2024-01-15 14:30 |
| bob | TODO-038: API rate limiting | src/middleware/ratelimit.ts | 2024-01-15 12:00 | 2024-01-15 14:15 |

## Claimed Todos

| ID | Title | Claimed By | Claimed At |
|----|-------|------------|------------|
| TODO-042 | Add email validation | alice | 2024-01-15 13:00 |
| TODO-038 | Implement rate limiting | bob | 2024-01-15 12:00 |

## File Ownership (Current Session)

| File Path | Owner | Purpose |
|-----------|-------|---------|
| src/auth/signup.ts | alice | Email validation |
| tests/signup.test.ts | alice | Validation tests |
| src/middleware/ratelimit.ts | bob | Rate limiter |

## Conflict Warnings

⚠️ No conflicts detected
```

**Key sections:**

- **Active Sessions**: Who's working on what right now (in-memory state)
- **Claimed Todos**: Reserved work items (prevents duplicate work)
- **File Ownership**: Current file modification ownership (for conflict detection)
- **Conflict Warnings**: Alerts when multiple developers touch overlapping files

**Sources:** [README.md:227-230]()

### contributors.md Format

The `_project_specs/team/contributors.md` file maintains team roster and ownership:

```markdown
# Team Contributors

## Active Contributors

| Developer | Role | Focus Areas | Since |
|-----------|------|-------------|-------|
| alice | Backend Lead | Auth, API, Database | 2024-01-01 |
| bob | Frontend Lead | UI, Components, State | 2024-01-05 |
| carol | Full Stack | Features, Integration | 2024-01-10 |

## Code Ownership

| Area | Primary | Backup |
|------|---------|--------|
| Authentication | alice | carol |
| UI Components | bob | carol |
| Database Schema | alice | - |
| API Routes | alice | carol |

## Communication

- Stand-ups: Daily 10am EST (async via state.md updates)
- Handoffs: Use _project_specs/team/handoffs/ directory
- Decisions: Log in _project_specs/decisions.md
```

**Sources:** [README.md:229]()

### handoffs/ Directory

The `_project_specs/team/handoffs/` directory contains context transfer notes when passing work between developers:

```
_project_specs/team/handoffs/
├── 2024-01-15-alice-to-bob-auth-module.md
├── 2024-01-14-bob-to-carol-ui-refactor.md
└── README.md
```

**Handoff note format:**

```markdown
# Handoff: Auth Module Refactor

**From:** alice  
**To:** bob  
**Date:** 2024-01-15  
**Context:** TODO-042 Email validation

## Current State
- Email validation logic in src/auth/signup.ts:45-67
- Tests passing but need edge case coverage
- Found bug with internationalized email addresses

## Remaining Work
- [ ] Add test cases for IDN emails (user@münchen.de)
- [ ] Update validation regex to support RFC 6531
- [ ] Check mobile app compatibility

## Important Context
- Don't modify validatePhone() - it's used by 3 other modules
- Database schema expects lowercase emails (normalize before save)
- See decision DOC-012 about email normalization strategy

## Files Modified
- src/auth/signup.ts
- tests/auth/signup.test.ts

## Branch
- alice/email-validation (pushed, not merged)
```

**Sources:** [README.md:230]()

## Todo Claiming Mechanism

```mermaid
stateDiagram-v2
    [*] --> Unclaimed: "Todo in<br/>active.md"
    
    Unclaimed --> Checking: "/check-contributors"
    
    Checking --> Unclaimed: "No claim"
    Checking --> Claimed: "Developer claims"
    
    Claimed --> InProgress: "Start work"
    
    InProgress --> InProgress: "Checkpoint updates<br/>to state.md"
    
    InProgress --> Complete: "Finish & test"
    
    Complete --> [*]: "Move to<br/>completed.md"
    
    Claimed --> Unclaimed: "Unclaim<br/>(abandon work)"
    
    note right of Claimed
        state.md updated:
        - Claimed Todos section
        - Developer name
        - Timestamp
    end note
    
    note right of InProgress
        state.md tracks:
        - Active session
        - Files being modified
        - Last update time
    end note
```

**Diagram: Todo Claim Lifecycle**

**Claiming prevents duplicate work:**

1. Developer runs `/check-contributors`
2. System shows unclaimed todos from `_project_specs/todos/active.md`
3. Developer claims by updating `state.md`
4. Commit and push claim (atomic reservation)
5. Other developers see claimed status after `git pull`

**Sources:** [README.md:237]()

## Conflict Detection Logic

```mermaid
graph TB
    subgraph "Input: state.md"
        ALICE_SESSION["Alice working on:<br/>src/auth/signup.ts<br/>tests/signup.test.ts"]
        BOB_SESSION["Bob working on:<br/>src/auth/signup.ts<br/>src/auth/login.ts"]
    end
    
    subgraph "Conflict Analysis"
        EXTRACT["Extract file lists<br/>per developer"]
        INTERSECT["Find file overlaps"]
        CLASSIFY["Classify conflict type"]
    end
    
    subgraph "Conflict Types"
        DIRECT["Direct Conflict<br/>Same exact file"]
        ADJACENT["Adjacent Conflict<br/>Same module area"]
        SAFE["No Conflict<br/>Separate areas"]
    end
    
    subgraph "Output: Warnings"
        WARN_HIGH["⚠️ HIGH: Alice & Bob<br/>both editing signup.ts<br/>Coordinate immediately"]
        WARN_MED["💡 MEDIUM: Alice & Bob<br/>both in auth module<br/>Watch for coupling"]
        NO_WARN["✅ No warnings"]
    end
    
    ALICE_SESSION --> EXTRACT
    BOB_SESSION --> EXTRACT
    
    EXTRACT --> INTERSECT
    INTERSECT --> CLASSIFY
    
    CLASSIFY --> DIRECT
    CLASSIFY --> ADJACENT
    CLASSIFY --> SAFE
    
    DIRECT --> WARN_HIGH
    ADJACENT --> WARN_MED
    SAFE --> NO_WARN
```

**Diagram: Conflict Detection Algorithm**

**Conflict severity levels:**

| Level | Condition | Action |
|-------|-----------|--------|
| **HIGH** | Same exact file | Immediate coordination required |
| **MEDIUM** | Same directory/module | Awareness, watch for coupling |
| **LOW** | Related files (imports) | Informational only |
| **NONE** | Separate areas | No action needed |

**Sources:** [README.md:239]()

## Converting Solo to Team Projects

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Cmd as "/check-contributors"
    participant FS as "File System"
    participant State as "state.md"
    participant Contrib as "contributors.md"
    
    Dev->>Cmd: Run in solo project
    Cmd->>FS: Check _project_specs/team/
    FS-->>Cmd: Directory not found
    
    Cmd->>Dev: "Solo project detected.<br/>Convert to team project?"
    Dev->>Cmd: Yes
    
    Cmd->>FS: Create _project_specs/team/
    Cmd->>State: Generate initial state.md
    Note over State: Empty active sessions<br/>Empty claimed todos
    
    Cmd->>Contrib: Generate contributors.md
    Note over Contrib: Current developer as first member<br/>Infer ownership from git history
    
    Cmd->>FS: Create handoffs/ directory
    Cmd->>FS: Create handoffs/README.md
    
    Cmd->>Dev: "Team structure created.<br/>Commit and push."
    
    Dev->>FS: git add _project_specs/team/
    Dev->>FS: git commit -m "Convert to team project"
    Dev->>FS: git push
```

**Diagram: Solo to Team Conversion Process**

**Conversion steps:**

1. Detect no `_project_specs/team/` directory exists
2. Offer conversion to team mode
3. Create directory structure
4. Generate initial `state.md` with empty sessions
5. Generate `contributors.md` from git history
6. Create `handoffs/` directory with README
7. Prompt commit and push

**Sources:** [README.md:218-222]()

## State Update Triggers

The system defines specific checkpoints when developers should update `state.md`:

| Trigger | When | What to Update |
|---------|------|----------------|
| **Claim** | Before starting work | Add to Claimed Todos |
| **Start** | Begin active development | Add to Active Sessions with files |
| **Checkpoint** | Every 1-2 hours during work | Update Last Update timestamp, add new files |
| **Break** | Before ending session | Update status to "Paused" |
| **Handoff** | Passing work to another dev | Create handoff note, update File Ownership |
| **Complete** | Todo finished and tested | Remove from Active Sessions, remove claim |

**Sources:** [README.md:243-246]()

## Integration with Session Management

Team collaboration integrates with the session management system (see [Session Management](#4.2)):

```mermaid
graph LR
    subgraph "Solo Project Files"
        SOLO_STATE["_project_specs/<br/>current-state.md"]
        SOLO_DECISIONS["_project_specs/<br/>decisions.md"]
    end
    
    subgraph "Team Project Files"
        TEAM_STATE["_project_specs/team/<br/>state.md"]
        TEAM_CONTRIB["_project_specs/team/<br/>contributors.md"]
        SHARED_DECISIONS["_project_specs/<br/>decisions.md<br/>(shared)"]
    end
    
    SOLO_STATE -.->|"Personal context"| SOLO_DECISIONS
    TEAM_STATE -.->|"Team context"| SHARED_DECISIONS
    TEAM_CONTRIB -.->|"Ownership context"| SHARED_DECISIONS
    
    TEAM_STATE -->|"Replaces for<br/>coordination"| SOLO_STATE
```

**Diagram: Solo vs. Team State Management**

In team projects, `_project_specs/team/state.md` supplements (not replaces) individual session state. Developers still maintain personal `current-state.md` for their own context, but coordination state lives in the shared `team/state.md`.

**Key difference:**

- **Solo**: `current-state.md` tracks "what am I working on"
- **Team**: `team/state.md` tracks "what is everyone working on"

**Sources:** [README.md:227-230]()

## Example: Two Developer Workflow

**Scenario:** Alice and Bob working on authentication module

### 1. Alice Claims Todo

```bash
# Alice's session
git pull
claude
> /check-contributors
```

**Claude shows:**
```
Project Status: Team Project (2 contributors)

Active Sessions: None
Claimed Todos: None

Available Todos:
- TODO-042: Add email validation (unclaimed)
- TODO-038: Add rate limiting (unclaimed)

Would you like to claim a todo?
```

Alice claims TODO-042, updates `state.md`:

```markdown
## Claimed Todos
| ID | Title | Claimed By | Claimed At |
|----|-------|------------|------------|
| TODO-042 | Add email validation | alice | 2024-01-15 13:00 |
```

Commits: `git commit -m "Claim TODO-042"`

### 2. Bob Checks State

```bash
# Bob's session (after Alice pushed)
git pull
claude
> /check-contributors --status
```

**Claude shows:**
```
Claimed Todos:
- TODO-042: Email validation (alice, claimed 1 hour ago)

Available Todos:
- TODO-038: Add rate limiting (unclaimed)
```

Bob claims TODO-038, different area → no conflict.

### 3. Alice Starts Work

Alice updates `state.md` when beginning active work:

```markdown
## Active Sessions
| Developer | Working On | Files | Started |
|-----------|------------|-------|---------|
| alice | TODO-042 | src/auth/signup.ts, tests/signup.test.ts | 13:00 |
```

### 4. Bob Accidentally Modifies Same File

Bob starts work on rate limiting but mistakenly edits `signup.ts`. When Bob runs `/check-contributors`:

**Claude detects:**
```
⚠️ CONFLICT WARNING

You are modifying: src/auth/signup.ts
Alice is also working on: src/auth/signup.ts (active since 13:00)

Recommendation: Coordinate with alice before continuing.
Consider:
1. Different files for rate limiting logic
2. Wait for alice to complete
3. Coordinate on Slack/handoff note
```

### 5. Alice Completes and Hands Off

Alice finishes email validation but found an edge case that needs attention:

Creates `_project_specs/team/handoffs/2024-01-15-alice-to-bob-email.md`:

```markdown
# Email Validation Edge Case

## Context
Completed basic email validation for TODO-042, but discovered that
internationalized domain names (IDN) need special handling.

## What's Done
- Basic RFC 5322 email validation
- Tests for common cases
- Integration with signup form

## What's Needed
- [ ] Support for IDN emails (münchen.de, etc.)
- [ ] Update regex or use library like `validator.js`
- [ ] Add test cases for IDN

## Files
- src/auth/signup.ts:45-67 (validation logic)
- tests/auth/signup.test.ts (add IDN tests here)
```

Updates `state.md`:
```markdown
## Active Sessions
(empty - alice completed)

## Claimed Todos
(TODO-042 moved to completed)
```

**Sources:** [README.md:243-246]()

## Command Reference Quick Guide

| Command | Use Case | When to Run |
|---------|----------|-------------|
| `/check-contributors` | Start of work session | Before claiming or starting new work |
| `/check-contributors --status` | Quick check during work | Periodically to see team status |
| `/check-contributors --team` | Convert solo project | When adding second developer |

**Sources:** [README.md:249-253]()

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|--------------|------------------|
| Skip state updates | Team loses visibility, conflicts arise | Update state.md at every checkpoint |
| Claim without pushing | Other devs don't see claim, duplicate work | Always commit and push claims immediately |
| Modify files without claiming | No conflict detection | Claim todo first, then start work |
| Skip handoff notes | Context lost between developers | Always create handoff when passing work |
| Work offline for days | State becomes stale, conflicts increase | Pull frequently, push state updates |

**Sources:** [README.md:235-242]()

## State Management Best Practices

1. **Pull before you start**: Always `git pull` before running `/check-contributors`
2. **Claim atomically**: Commit and push claims immediately to reserve work
3. **Checkpoint frequently**: Update state.md every 1-2 hours during active work
4. **Handoff explicitly**: Create handoff notes even for "obvious" context
5. **Check before commit**: Run `/check-contributors` before pushing to detect conflicts early
6. **Clear on completion**: Remove yourself from active sessions when done

**Sources:** [README.md:243-246]()

---

# Page: Multi-Developer Coordination

# Multi-Developer Coordination

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document covers the coordination mechanisms for multiple developers using Claude Code on the same repository simultaneously. The system uses file-based state management to prevent duplicate work, detect conflicts, and enable structured handoffs between team members.

For details on individual developer session management, see [Session Management](#4.2). For implementation details of the shared state files, see [Shared State Management](#8.2).

**Sources:** [README.md:211-253]()

---

## Overview

When multiple developers use Claude Code on the same codebase, coordination becomes critical to prevent:

- **Duplicate work** - Two people implementing the same todo
- **Merge conflicts** - Multiple developers editing the same files simultaneously
- **Lost context** - No visibility into what others are working on
- **Decision divergence** - Making conflicting architectural choices

Claude Bootstrap addresses these challenges through a file-based coordination system that operates entirely through git, requiring no external services or infrastructure.

**Sources:** [README.md:211-224]()

---

## State Management Architecture

The coordination system uses a dedicated directory structure to track team activity:

```
_project_specs/team/
├── state.md           # Active sessions, claimed todos, file ownership
├── contributors.md    # Team member profiles, roles, focus areas
└── handoffs/          # Context transfer notes
    ├── feature-auth-handoff.md
    └── bug-fix-validation-handoff.md
```

### State File Structure

The `state.md` file serves as the central coordination point, tracking real-time developer activity:

```markdown
# Team State

**Last Updated:** 2025-01-15 14:30 UTC
**Active Developers:** 2

## Active Sessions

### Developer A (@alice)
- **Status:** Active
- **Working On:** [TODO-042] Add email validation
- **Files Being Modified:**
  - src/components/SignupForm.tsx
  - src/utils/validation.ts
  - tests/signup.test.ts
- **Started:** 2025-01-15 13:00 UTC
- **Last Update:** 2025-01-15 14:30 UTC

### Developer B (@bob)
- **Status:** Active
- **Working On:** [TODO-043] Implement password strength checker
- **Files Being Modified:**
  - src/components/PasswordInput.tsx
  - src/utils/password.ts
  - tests/password.test.ts
- **Started:** 2025-01-15 14:00 UTC
- **Last Update:** 2025-01-15 14:15 UTC

## Claimed Todos

| Todo ID | Claimed By | Claimed At | Status |
|---------|------------|------------|--------|
| TODO-042 | @alice | 2025-01-15 13:00 | in-progress |
| TODO-043 | @bob | 2025-01-15 14:00 | in-progress |

## File Ownership (Current Session)

| File Path | Owner | Since |
|-----------|-------|-------|
| src/components/SignupForm.tsx | @alice | 13:00 |
| src/utils/validation.ts | @alice | 13:00 |
| src/components/PasswordInput.tsx | @bob | 14:00 |
| src/utils/password.ts | @bob | 14:00 |

## Conflict Warnings

⚠️ **No active conflicts detected**

## Recent Handoffs

| Date | From | To | Topic | Notes |
|------|------|----|----|-------|
| 2025-01-14 | @alice | @bob | Auth module | See handoffs/auth-handoff.md |
```

**Sources:** [README.md:226-231]()

---

## Multi-Developer Workflow

```mermaid
graph TB
    Start["Developer starts work session"]
    Pull["git pull origin main"]
    Check["/check-contributors"]
    ReadState["Read state.md"]
    SelectTodo["Select unclaimed todo"]
    ClaimTodo["Claim todo in state.md"]
    CheckOverlap["Check file overlap with others"]
    Decision{"Files overlap?"}
    Coordinate["Coordinate with other dev"]
    Work["Implement feature"]
    UpdateState["Update state.md checkpoint"]
    Complete["Complete todo"]
    UpdateCompleted["Move to completed.md"]
    ClearState["Clear from state.md"]
    Push["git push"]
    
    Start --> Pull
    Pull --> Check
    Check --> ReadState
    ReadState --> SelectTodo
    SelectTodo --> ClaimTodo
    ClaimTodo --> CheckOverlap
    CheckOverlap --> Decision
    Decision -->|"Yes"| Coordinate
    Decision -->|"No"| Work
    Coordinate --> Work
    Work --> UpdateState
    UpdateState --> Work
    Work --> Complete
    Complete --> UpdateCompleted
    UpdateCompleted --> ClearState
    ClearState --> Push
    
    style Decision fill:#f9f9f9
    style Coordinate fill:#fff4e6
```

**Workflow Steps:**

1. **Start session** - Begin development work
2. **git pull** - Sync latest changes
3. **Check state** - Run `/check-contributors` to view team activity
4. **Select todo** - Choose an unclaimed todo from `_project_specs/todos/active.md`
5. **Claim todo** - Update `state.md` with claim before starting
6. **Check overlap** - Review which files others are working on
7. **Coordinate** - If files overlap, coordinate with other developers
8. **Work** - Implement the feature
9. **Update state** - Periodically update `state.md` with progress
10. **Complete** - Finish the todo
11. **Move todo** - Transfer to `completed.md`
12. **Clear state** - Remove from active sessions in `state.md`
13. **Push** - Commit and push changes

**Sources:** [README.md:243-246]()

---

## Todo Claiming System

### Claiming Process

Developers must claim todos **before** starting work to prevent duplicate effort:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant State as "state.md"
    participant Todos as "todos/active.md"
    
    Dev->>State: Read current claims
    Dev->>Todos: Select unclaimed todo
    Dev->>State: Add claim entry
    Note over State: TODO-042 claimed by @alice
    Dev->>State: git commit "Claim TODO-042"
    Dev->>State: git push
    Note over Dev: Now safe to start work
```

### Claim Format

Claims are recorded in the `state.md` file:

| Field | Description |
|-------|-------------|
| **Todo ID** | The unique identifier (e.g., `TODO-042`) |
| **Claimed By** | GitHub username or identifier |
| **Claimed At** | Timestamp in UTC |
| **Status** | `claimed`, `in-progress`, `blocked`, `completed` |

**Example:**

```markdown
## Claimed Todos

| Todo ID | Claimed By | Claimed At | Status |
|---------|------------|------------|--------|
| TODO-042 | @alice | 2025-01-15 13:00 | in-progress |
| TODO-043 | @bob | 2025-01-15 14:00 | in-progress |
| TODO-044 | @charlie | 2025-01-15 15:00 | claimed |
```

### Claim Rules

1. **Check before claiming** - Always run `/check-contributors` first
2. **Claim atomically** - Commit and push the claim immediately
3. **Update status** - Move from `claimed` → `in-progress` when starting work
4. **Release on abandon** - Remove claim if not starting work within 1 hour
5. **Clear on complete** - Remove from claims when moving to `completed.md`

**Sources:** [README.md:235-241]()

---

## Active Session Tracking

### Session Information

Active sessions provide real-time visibility into developer activity:

```markdown
### Developer A (@alice)
- **Status:** Active
- **Working On:** [TODO-042] Add email validation
- **Files Being Modified:**
  - src/components/SignupForm.tsx
  - src/utils/validation.ts
  - tests/signup.test.ts
- **Started:** 2025-01-15 13:00 UTC
- **Last Update:** 2025-01-15 14:30 UTC
- **Checkpoint:** 3 of 5 test cases passing
```

### Session Fields

| Field | Purpose | Update Frequency |
|-------|---------|------------------|
| **Status** | `Active`, `Away`, `Paused`, `Blocked` | On state change |
| **Working On** | Current todo being implemented | When starting new todo |
| **Files Being Modified** | List of files in scope | When editing new files |
| **Started** | Session start timestamp | Once per session |
| **Last Update** | Most recent activity | Every checkpoint (15-30 min) |
| **Checkpoint** | Progress summary | During periodic updates |

### Update Triggers

Sessions should be updated at these points:

1. **Session start** - When beginning work
2. **File changes** - When editing a new file
3. **Checkpoints** - Every 15-30 minutes during active work
4. **Blocking issues** - When encountering a blocker
5. **Session end** - When completing or pausing work

**Sources:** [README.md:235-241]()

---

## Conflict Detection

The system monitors for conflicts where multiple developers work on overlapping areas.

### File Overlap Detection

```mermaid
graph LR
    StateFile["state.md<br/>Active Sessions"]
    DevA["Developer A<br/>Editing file X"]
    DevB["Developer B<br/>Editing file X"]
    Detector["Conflict Detector"]
    Warning["⚠️ Conflict Warning"]
    
    StateFile --> Detector
    DevA --> StateFile
    DevB --> StateFile
    Detector --> Warning
    Warning --> DevA
    Warning --> DevB
```

### Conflict Warning Format

When the system detects file overlap:

```markdown
## Conflict Warnings

⚠️ **CONFLICT DETECTED**

**File:** `src/utils/validation.ts`
**Developers:**
- @alice (claimed at 13:00, last active 14:30)
- @bob (claimed at 14:15, last active 14:20)

**Recommended Action:**
- Coordinate immediately via Slack/Teams
- Decide who continues, who pauses
- Consider splitting the file if both changes are needed
- Update state.md with resolution

**Risk Level:** 🔴 HIGH - Same file, overlapping time
```

### Conflict Severity Levels

| Level | Criteria | Action Required |
|-------|----------|----------------|
| 🔴 **High** | Same file, both active now | Coordinate immediately |
| 🟡 **Medium** | Same directory, related files | Check for logical conflicts |
| 🟢 **Low** | Same module, different files | Awareness, no immediate action |

### Automatic Detection Logic

The `/check-contributors` command scans `state.md` for conflicts:

1. **Parse active sessions** - Extract file lists from each developer
2. **Compare file paths** - Identify exact matches or directory overlaps
3. **Check timestamps** - Determine if sessions are concurrent
4. **Calculate risk** - Classify conflict severity
5. **Generate warnings** - Add to `state.md` conflict section

**Sources:** [README.md:235-241]()

---

## The `/check-contributors` Command

### Command Syntax

```bash
/check-contributors [--status|--team]
```

### Options

| Flag | Purpose | Output |
|------|---------|--------|
| (none) | Full check with conversion prompt | Shows state, offers team conversion |
| `--status` | Quick status only | Shows who's working on what, exits |
| `--team` | Force team conversion | Creates team structure without prompting |

### Command Flow

```mermaid
stateDiagram-v2
    [*] --> CheckTeamDir
    CheckTeamDir --> HasTeamStructure: _project_specs/team/ exists?
    CheckTeamDir --> NoTeamStructure: _project_specs/team/ missing
    
    HasTeamStructure --> ReadState
    ReadState --> ShowStatus
    ShowStatus --> DetectConflicts
    DetectConflicts --> DisplayWarnings
    DisplayWarnings --> [*]
    
    NoTeamStructure --> OfferConversion
    OfferConversion --> UserDecision
    UserDecision --> CreateTeamStructure: User accepts
    UserDecision --> ExitSolo: User declines
    
    CreateTeamStructure --> GenerateStateFile
    GenerateStateFile --> GenerateContributorsFile
    GenerateContributorsFile --> CreateHandoffsDir
    CreateHandoffsDir --> ShowStatus
    
    ExitSolo --> [*]
```

### Output Format

**Status Display:**

```
📊 Team Status - Updated 2025-01-15 14:30 UTC

Active Developers: 2

👤 @alice
   Working on: [TODO-042] Add email validation
   Files: 3 (src/components/SignupForm.tsx, ...)
   Status: Active (last update 14:30)

👤 @bob
   Working on: [TODO-043] Password strength checker
   Files: 3 (src/components/PasswordInput.tsx, ...)
   Status: Active (last update 14:15)

⚠️ Warnings:
   - No conflicts detected

📋 Available Todos: 12 unclaimed in _project_specs/todos/active.md
```

### Solo Project Detection

If `_project_specs/team/` doesn't exist, the command prompts:

```
🔍 Project Structure Analysis

Current setup: Solo project (no team coordination)

Would you like to convert this to a team project?

Team features:
✓ Shared state tracking (who's working on what)
✓ Todo claiming (prevent duplicate work)
✓ Conflict detection (file overlap warnings)
✓ Handoff support (context transfer between devs)

Convert to team project? [y/N]
```

**Sources:** [README.md:217-253]()

---

## Converting Solo to Team Projects

### Conversion Process

```mermaid
graph TD
    Solo["Solo Project<br/>No team/ directory"]
    Detect["/check-contributors"]
    Prompt["Conversion prompt"]
    Accept["User accepts"]
    CreateDir["mkdir -p _project_specs/team/"]
    GenState["Generate state.md template"]
    GenContrib["Generate contributors.md"]
    CreateHandoffs["mkdir handoffs/"]
    InitState["Initialize empty state"]
    Commit["git commit 'Initialize team structure'"]
    TeamProject["Team Project<br/>Ready for multi-dev"]
    
    Solo --> Detect
    Detect --> Prompt
    Prompt --> Accept
    Accept --> CreateDir
    CreateDir --> GenState
    GenState --> GenContrib
    GenContrib --> CreateHandoffs
    CreateHandoffs --> InitState
    InitState --> Commit
    Commit --> TeamProject
```

### Generated Files

**state.md Template:**

```markdown
# Team State

**Last Updated:** 2025-01-15 14:30 UTC
**Active Developers:** 0

## Active Sessions

_No active sessions_

## Claimed Todos

| Todo ID | Claimed By | Claimed At | Status |
|---------|------------|------------|--------|
| _No claimed todos_ | | | |

## File Ownership (Current Session)

| File Path | Owner | Since |
|-----------|-------|-------|
| _No active file locks_ | | |

## Conflict Warnings

✅ **No active conflicts**

## Recent Handoffs

| Date | From | To | Topic | Notes |
|------|------|----|----|-------|
| _No handoffs yet_ | | | | |
```

**contributors.md Template:**

```markdown
# Project Contributors

**Last Updated:** 2025-01-15

## Team Members

### @current-user (You)
- **Role:** Developer
- **Focus Areas:** TBD
- **Join Date:** 2025-01-15
- **Active:** Yes

## Adding New Contributors

When a new team member joins:

1. Add entry to this file
2. Update state.md if they claim a todo
3. Run /check-contributors to verify team structure
4. Share project documentation and Access.txt location

## Communication Channels

- **Primary:** TBD
- **Urgent:** TBD
- **Async:** GitHub comments, state.md updates
```

### Migration Checklist

When converting from solo to team:

- [ ] Run `/check-contributors --team` to create structure
- [ ] Review and customize `contributors.md` with team info
- [ ] Communicate workflow to team members
- [ ] Ensure all developers have Access.txt location
- [ ] Test claiming a todo in `state.md`
- [ ] Commit team structure to shared repository
- [ ] Document communication channels in `contributors.md`

**Sources:** [README.md:217-253]()

---

## Handoff Patterns

Handoffs occur when one developer passes work to another. The `handoffs/` directory stores structured context transfer documents.

### Handoff Structure

```markdown
# Handoff: Email Validation Feature

**From:** @alice
**To:** @bob
**Date:** 2025-01-15
**Status:** In Progress → Paused

## What's Done

- [x] Validation utility functions (src/utils/validation.ts)
- [x] Unit tests for validation logic (tests/validation.test.ts)
- [x] SignupForm integration (partial)

## What's Remaining

- [ ] Complete SignupForm error handling
- [ ] Add error messages to UI
- [ ] Integration tests for full signup flow
- [ ] Update documentation

## Current State

**Files Modified:**
- src/utils/validation.ts (complete)
- src/components/SignupForm.tsx (70% done)
- tests/signup.test.ts (needs integration tests)

**Test Status:**
- Unit tests: 15/15 passing
- Integration tests: 2/5 implemented

**Known Issues:**
- Form doesn't show validation errors yet (lines 45-60 in SignupForm.tsx)
- Need to wire up validation.validateEmail() to form state

## Context You Need

**Key Decisions:**
1. Using Zod for schema validation (see decisions.md entry 2025-01-14)
2. Validation runs on blur, not on change (UX decision)
3. Server-side validation duplicates client-side (security requirement)

**Important Files:**
- docs/validation-strategy.md - Overall approach
- .claude/skills/security.md - Validation requirements

**Dependencies:**
- zod@3.22.4 (already installed)
- react-hook-form@7.49.0 (for form state)

## Next Steps

1. Open SignupForm.tsx
2. Review TODO comments (search for "ALICE:")
3. Implement error message display (see design in Figma)
4. Add remaining integration tests
5. Run /ralph-loop for TDD completion

## Questions for You

- Do we want real-time validation or just on submit? (Currently on blur)
- Should we add debouncing to the validation? (Not implemented yet)

## How to Continue

```bash
git pull origin main
git checkout feature/email-validation
/check-contributors  # Claim TODO-042
# Continue at line 45 in SignupForm.tsx
```
```

### Handoff Triggers

Create a handoff document when:

1. **Developer unavailable** - Must stop work for extended period (>1 day)
2. **Task blocked** - Waiting on external dependency, another dev can help
3. **Expertise transfer** - Passing work to specialist (e.g., backend → frontend)
4. **Planned rotation** - Team policy to rotate ownership
5. **Context risk** - Work complex enough that context loss is a concern

### Handoff Checklist

Before creating a handoff:

- [ ] Commit all work in progress
- [ ] Push to feature branch
- [ ] Run tests and document status
- [ ] Create handoff document in `handoffs/`
- [ ] Update `state.md` with handoff reference
- [ ] Tag the other developer in commit message
- [ ] Update todo status to `blocked` or `in-handoff`

**Sources:** [README.md:235-241]()

---

## Coordination Workflow Example

### Scenario: Two Developers, One Feature

```mermaid
sequenceDiagram
    participant Alice as "Developer A<br/>(@alice)"
    participant State as "state.md"
    participant Bob as "Developer B<br/>(@bob)"
    
    Note over Alice: Session Start
    Alice->>State: git pull
    Alice->>State: /check-contributors
    State-->>Alice: Show: No active sessions
    Alice->>State: Claim TODO-042
    Alice->>State: Add active session
    Alice->>State: git push
    
    Note over Alice: Working (30 min)
    Alice->>State: Update checkpoint
    
    Note over Bob: Session Start
    Bob->>State: git pull
    Bob->>State: /check-contributors
    State-->>Bob: Show: Alice working on TODO-042
    Bob->>State: Claim TODO-043
    Bob->>State: Add active session
    Bob->>State: git push
    
    Note over Bob: Working (15 min)
    
    Note over State: Conflict Detection
    State-->>Alice: ⚠️ Both editing validation.ts
    State-->>Bob: ⚠️ Both editing validation.ts
    
    Note over Alice,Bob: Coordinate via Slack
    
    Alice->>Bob: "I'll finish validation.ts, you take password.ts"
    Bob->>State: Update session (remove validation.ts)
    Bob->>State: git push
    
    Note over Alice: Complete work
    Alice->>State: Remove active session
    Alice->>State: Move TODO-042 to completed
    Alice->>State: git push
    
    Note over Bob: Complete work
    Bob->>State: Remove active session
    Bob->>State: Move TODO-043 to completed
    Bob->>State: git push
```

### Step-by-Step Workflow

**Developer A (Alice):**

1. `git pull origin main`
2. `/check-contributors` - See no one else working
3. Edit `state.md` - Claim TODO-042, add active session
4. `git commit -m "Claim TODO-042: Email validation"`
5. `git push`
6. Work on feature for 30 minutes
7. Edit `state.md` - Update checkpoint
8. `git commit -m "Checkpoint: 3/5 tests passing"`
9. `git push`
10. Notice conflict warning about Bob
11. Coordinate with Bob via Slack
12. Continue work after agreement
13. Complete feature
14. Edit `state.md` - Remove active session
15. Move TODO-042 from `active.md` to `completed.md`
16. `git commit -m "Complete TODO-042: Email validation"`
17. `git push`

**Developer B (Bob):**

1. `git pull origin main`
2. `/check-contributors` - See Alice working on TODO-042
3. Select different todo (TODO-043)
4. Edit `state.md` - Claim TODO-043, add active session
5. `git commit -m "Claim TODO-043: Password strength"`
6. `git push`
7. Work on feature for 15 minutes
8. Notice conflict warning about Alice
9. Coordinate with Alice via Slack
10. Update `state.md` - Remove validation.ts from file list
11. `git commit -m "Update session: Remove validation.ts conflict"`
12. `git push`
13. Complete feature
14. Edit `state.md` - Remove active session
15. Move TODO-043 from `active.md` to `completed.md`
16. `git commit -m "Complete TODO-043: Password strength"`
17. `git push`

**Sources:** [README.md:243-246]()

---

## Best Practices

### Communication Patterns

| Situation | Communication Method | Response Time |
|-----------|---------------------|----------------|
| **Conflict detected** | Immediate sync (Slack/Teams) | < 5 minutes |
| **Claiming todo** | Commit message + state.md | Async |
| **Checkpoint updates** | state.md commit | Async |
| **Handoff** | Handoff document + mention | < 24 hours |
| **Architecture decisions** | decisions.md + team meeting | Before implementation |

### State Update Frequency

| Activity | Update Frequency | Method |
|----------|------------------|--------|
| **Todo claims** | Immediately before starting | Edit state.md, commit, push |
| **Active sessions** | Every 15-30 minutes | Edit state.md, commit, push |
| **File changes** | When editing new file | Update active session entry |
| **Blocking issues** | Immediately when blocked | Update status field |
| **Session end** | When completing/pausing | Remove from active sessions |

### Conflict Resolution Protocol

1. **Detect** - System flags overlap in state.md
2. **Communicate** - Developers sync immediately
3. **Decide** - Who continues, who pivots, or split work
4. **Update** - Winner updates state.md, loser removes file
5. **Commit** - Both push updated state
6. **Monitor** - Check for new conflicts in next update

### Common Pitfalls

| Pitfall | Prevention | Recovery |
|---------|-----------|----------|
| **Forgetting to claim** | Always run `/check-contributors` first | Apologize, merge carefully |
| **Stale state.md** | Update every 15-30 min | Pull before trusting state |
| **Large file overlap** | Check state before starting | Split the work, create handoff |
| **Merge conflicts** | Commit state.md changes separately | Manual merge, update both versions |
| **Lost handoffs** | Use handoffs/ directory | Recreate from git history + Slack |

**Sources:** [README.md:235-246]()

---

## Integration with Other Systems

### Session Management Integration

The multi-developer coordination system extends individual session management (see [Session Management](#4.2)):

| File | Solo Project | Team Project |
|------|--------------|--------------|
| `current-state.md` | Individual session state | Per-developer state |
| `decisions.md` | Personal decisions | Shared team decisions |
| `state.md` | N/A | Team coordination state |
| `contributors.md` | N/A | Team member directory |

### Todo System Integration

The claiming system integrates with the atomic todo workflow (see [Atomic Todos and Project Specs](#3.4)):

```
_project_specs/todos/active.md
    ↓ (claim via state.md)
Developer A working
    ↓ (complete)
_project_specs/todos/completed.md
    ↓ (clear from state.md)
Available for reference
```

### Code Review Integration

When working in teams, code review (see [Quality Gates and Code Review](#4.3)) includes coordination checks:

1. **Pre-commit** - Check if claimed in state.md
2. **Pre-push** - Verify no active conflicts
3. **CI/CD** - Validate state.md is up-to-date
4. **Merge** - Ensure active session cleared

**Sources:** [README.md:211-253]()

---

# Page: Shared State Management

# Shared State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skills/session-management.md](skills/session-management.md)

</details>



## Purpose and Scope

This page documents the shared state management system that enables multiple developers to coordinate when using Claude Code on the same repository. It covers the file structures, formats, and update patterns for team coordination state.

For information about the `/check-contributors` command and overall coordination patterns, see [Multi-Developer Coordination](#8.1). For single-developer session state tracking, see [Session Management](#4.2).

---

## Team State Directory Structure

When a project is converted to team mode (either manually or via `/check-contributors --team`), Claude Bootstrap creates a dedicated team state directory:

```
_project_specs/
└── team/
    ├── state.md           # Active sessions, claimed todos, conflicts
    ├── contributors.md    # Team member profiles and ownership
    ├── decisions.md       # Shared architectural decisions
    └── handoffs/          # Context transfer notes
        ├── 2025-01-15-auth-refactor.md
        └── 2025-01-16-api-migration.md
```

**Sources:** [README.md:225-231]()

### Directory Purpose Table

| File | Update Frequency | Primary Purpose | Read By |
|------|------------------|-----------------|---------|
| `state.md` | Every session start/end + checkpoints | Track who's working on what right now | All team members before claiming work |
| `contributors.md` | On team member changes | Team roster and ownership areas | All team members at session start |
| `decisions.md` | When architectural decisions made | Log shared design choices | Team members before making similar decisions |
| `handoffs/*.md` | When passing work between developers | Preserve context across handoffs | Developer receiving work |

**Sources:** [README.md:225-242]()

---

## state.md Format and Updates

The `state.md` file is the central coordination point for active development sessions. It tracks who is currently working on what, which todos are claimed, and potential conflicts.

### File Structure

```markdown
# Team State

*Last updated: 2025-01-15 16:45 by @alice*

## Active Sessions

| Developer | Status | Working On | Files Being Modified | Started |
|-----------|--------|------------|---------------------|---------|
| @alice | 🟢 Active | [TODO-042] Email validation | src/auth/validate.ts, src/auth/types.ts | 2025-01-15 14:00 |
| @bob | 🟡 Checkpoint | [TODO-038] API rate limiting | src/middleware/ratelimit.ts | 2025-01-15 09:30 |
| @carol | 🔴 Ended | [TODO-035] User profile page | Complete - pushed to main | 2025-01-15 11:00 |

## Claimed Todos

| Todo ID | Claimed By | Claimed At | Status | Notes |
|---------|------------|------------|--------|-------|
| TODO-042 | @alice | 2025-01-15 14:00 | in-progress | Email validation, ETA 2h |
| TODO-043 | @bob | 2025-01-15 15:30 | claimed | Starting after rate limiting done |
| TODO-044 | - | - | available | Needs PostHog integration skill |

## Potential Conflicts

| Warning | Developers | Files | Detected | Resolution |
|---------|-----------|-------|----------|------------|
| ⚠️ Overlap | @alice, @bob | src/auth/types.ts | 2025-01-15 15:00 | Coordinating in Slack |

## Recent Completions

| Todo ID | Completed By | Completed At | Pushed To |
|---------|--------------|--------------|-----------|
| TODO-035 | @carol | 2025-01-15 13:45 | main |
| TODO-037 | @alice | 2025-01-15 10:30 | main |
```

**Sources:** [README.md:228-229]()

### Session Status Indicators

| Status | Symbol | Meaning | Update Required |
|--------|--------|---------|-----------------|
| Active | 🟢 | Currently working, making changes | Update every 30-60 minutes |
| Checkpoint | 🟡 | Paused, preserved state, may resume | Update when pausing work |
| Ended | 🔴 | Session complete, work pushed | Update immediately after push |

### Update Triggers

The `state.md` file must be updated at these points in the workflow:

**At Session Start:**
```markdown
1. git pull origin main
2. Read _project_specs/team/state.md
3. Check for conflicts with your planned work
4. Claim todo by adding row to "Claimed Todos"
5. Add yourself to "Active Sessions"
6. git add _project_specs/team/state.md
7. git commit -m "chore: claim TODO-XXX"
8. git push origin main
```

**During Active Work (every ~1 hour or after significant changes):**
```markdown
1. Update "Files Being Modified" column
2. Update timestamp in header
3. Commit: "chore: update team state checkpoint"
```

**At Session End:**
```markdown
1. Change status to 🔴 Ended
2. Move todo from "Claimed" to "Recent Completions"
3. Remove potential conflicts if resolved
4. Commit: "chore: end session TODO-XXX"
```

**Sources:** [README.md:244-246]()

---

## State Update Workflow Diagram

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Git as "git"
    participant State as "state.md"
    participant Todos as "todos/active.md"
    
    Dev->>Git: "git pull origin main"
    Git-->>State: "Fetch latest state"
    Dev->>State: "Read active sessions"
    Dev->>State: "Check for conflicts"
    
    alt No Conflicts
        Dev->>Todos: "Select available todo"
        Dev->>State: "Add to Claimed Todos"
        Dev->>State: "Add to Active Sessions (🟢)"
        Dev->>Git: "Commit + push state.md"
        
        loop Active Work
            Dev->>Dev: "Work on feature"
            Note over Dev: "Every ~1 hour"
            Dev->>State: "Update files list"
            Dev->>State: "Update timestamp"
            Dev->>Git: "Commit checkpoint"
        end
        
        Dev->>Git: "Push feature work"
        Dev->>State: "Change status to 🔴 Ended"
        Dev->>State: "Move to Recent Completions"
        Dev->>Git: "Commit + push state.md"
    else Conflict Detected
        Dev->>State: "Add to Potential Conflicts"
        Dev->>Dev: "Coordinate with other dev"
        Dev->>State: "Update when resolved"
    end
```

**Sources:** [README.md:244-246]()

---

## contributors.md Format

The `contributors.md` file maintains team member information, ownership areas, and focus patterns. It's less frequently updated than `state.md` but provides essential context for coordination.

### File Structure

```markdown
# Contributors

## Team Members

| GitHub Handle | Name | Role | Primary Focus | Join Date |
|---------------|------|------|---------------|-----------|
| @alice | Alice Chen | Full Stack | Auth, API | 2025-01-10 |
| @bob | Bob Smith | Backend | Database, Workers | 2025-01-10 |
| @carol | Carol Lee | Frontend | UI, Components | 2025-01-12 |

## Ownership Areas

| Area | Primary Owner | Secondary | Notes |
|------|---------------|-----------|-------|
| Authentication | @alice | @bob | OAuth, JWT, session management |
| Database Schema | @bob | @alice | Migrations, RLS, indexes |
| UI Components | @carol | - | Design system, accessibility |
| API Layer | @alice | @bob | REST endpoints, validation |
| Background Jobs | @bob | - | Cron, queues, workers |
| Frontend State | @carol | - | Zustand, React Query |

## Communication

| Channel | Purpose | Members |
|---------|---------|---------|
| #claude-dev | Daily coordination | All |
| #architecture | Design discussions | All |
| Slack DM | Conflict resolution | As needed |

## Working Hours (UTC)

| Developer | Timezone | Typical Hours | Availability |
|-----------|----------|---------------|--------------|
| @alice | UTC-5 | 13:00-21:00 UTC | Weekdays |
| @bob | UTC+1 | 08:00-16:00 UTC | Weekdays |
| @carol | UTC-8 | 16:00-00:00 UTC | Weekdays |

## Expertise Matrix

| Skill | @alice | @bob | @carol |
|-------|--------|------|--------|
| TypeScript | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Python | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| React | ⭐⭐ | ⭐ | ⭐⭐⭐ |
| PostgreSQL | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Supabase | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
```

**Sources:** [README.md:229]()

### When to Update contributors.md

| Trigger | Update Required | Example |
|---------|-----------------|---------|
| New team member joins | Add to Team Members table | Developer onboarding |
| Ownership changes | Update Ownership Areas | Primary owner leaves |
| Expertise grows | Update Expertise Matrix | Team member learns new skill |
| Communication channels change | Update Communication table | New Slack channel created |

---

## Team State File Relationships Diagram

```mermaid
graph TB
    subgraph "Team Coordination Hub"
        State["state.md<br/>Active Sessions<br/>Claimed Todos<br/>Conflicts"]
        Contributors["contributors.md<br/>Team Roster<br/>Ownership<br/>Expertise"]
        Decisions["decisions.md<br/>Architectural Choices<br/>Design Rationale"]
        Handoffs["handoffs/<br/>Context Transfer<br/>Work Notes"]
    end
    
    subgraph "Individual Developer"
        Dev["Developer @alice"]
        Session["_project_specs/session/<br/>current-state.md"]
        Todos["_project_specs/todos/<br/>active.md"]
    end
    
    Dev -->|"Session Start:<br/>git pull → read"| State
    State -->|"Claim todo"| Dev
    Dev -->|"Checkpoint:<br/>update every ~1h"| State
    Dev -->|"Session End:<br/>mark complete"| State
    
    Dev -->|"Check ownership<br/>before starting"| Contributors
    Dev -->|"Check before<br/>deciding"| Decisions
    Dev -->|"Write when<br/>passing work"| Handoffs
    Dev -->|"Read when<br/>receiving work"| Handoffs
    
    State -.->|"Detects conflicts<br/>using"| Contributors
    Session -.->|"Personal state<br/>separate from"| State
    Todos -.->|"Todo status<br/>synced with"| State
    
    Decisions -.->|"Referenced by"| Handoffs
```

**Sources:** [README.md:225-242](), [skills/session-management.md:66-76]()

---

## Handoffs Directory

The `handoffs/` directory contains context transfer notes created when passing work between developers. Each handoff file preserves the mental model, open questions, and continuation points.

### When to Create Handoffs

| Scenario | Handoff Required | Reason |
|----------|------------------|--------|
| Mid-feature transition | ✅ Yes | Preserve context for next developer |
| Work blocked by external dependency | ✅ Yes | Document blocker and next steps |
| Developer going on leave | ✅ Yes | Enable others to continue |
| Feature complete but needs follow-up | ⚠️ Optional | Use if future work likely |
| Bug investigation incomplete | ✅ Yes | Document findings and hypotheses |

### Handoff File Naming Convention

```
handoffs/YYYY-MM-DD-brief-description.md

Examples:
handoffs/2025-01-15-auth-refactor.md
handoffs/2025-01-16-payment-webhook-debug.md
handoffs/2025-01-17-mobile-navigation-blocked.md
```

### Handoff File Structure

```markdown
# Handoff: [Feature/Bug Name]

**From:** @alice  
**To:** @bob (or "Team - Anyone can pick up")  
**Date:** 2025-01-15  
**Related Todo:** [TODO-042]  
**Status:** In Progress - ~60% complete  

## Context

[2-3 paragraphs explaining what this work is about, why it's being done, 
and what the current state is]

Example: We're refactoring the authentication system to use RS256 JWT instead 
of HS256. This provides better security for token verification across 
microservices. Currently completed the token generation side, but refresh 
token rotation is incomplete.

## What's Complete

- ✅ JWT token generation with RS256
- ✅ Public/private key pair management in src/auth/keys/
- ✅ Login endpoint updated to use new tokens
- ✅ Unit tests for token signing

## What's Remaining

- [ ] Refresh token rotation logic in src/auth/refresh.ts
- [ ] Token blacklist for logout (prevent replay attacks)
- [ ] Integration tests for full auth flow
- [ ] Update API middleware to verify RS256 tokens

## Current Blocker (if any)

None - Ready to continue

OR

Blocked: Waiting for infrastructure team to provision key storage service. 
Expected resolution: 2025-01-17

## Key Decisions & Context

- **Why RS256?** See _project_specs/team/decisions.md entry [2025-01-15]
- **Token expiry times:** Access 15 min, Refresh 7 days
- **Storage:** Refresh tokens in HttpOnly cookies (NOT localStorage)

## Code Locations

| File | Status | Notes |
|------|--------|-------|
| src/auth/keys/generate.ts | Complete | Key pair generation |
| src/auth/tokens.ts | Complete | Token signing functions |
| src/auth/refresh.ts | 60% done | Lines 1-45 done, need 46-end |
| src/auth/middleware.ts | Not started | Token verification |
| src/auth/types.ts | Complete | TokenPayload interface |

## Test Files

| File | Status | Coverage |
|------|--------|----------|
| tests/auth/tokens.test.ts | Complete | 95% |
| tests/auth/refresh.test.ts | Incomplete | 40% - need rotation tests |
| tests/integration/auth.test.ts | Not started | 0% |

## How to Continue

1. Start with src/auth/refresh.ts line 46
2. Implement `rotateRefreshToken()` function
3. Add error handling for expired refresh tokens
4. Write tests in tests/auth/refresh.test.ts
5. Refer to decisions.md for token expiry policy

## Questions & Uncertainties

- Should we implement token fingerprinting? (device tracking)
- Do we need rate limiting on refresh endpoint?
- What's the policy for concurrent sessions per user?

## Related PRs/Issues

- PR #123 (merged) - Initial RS256 setup
- Issue #456 - Parent issue for auth refactor

## Local Dev Setup

```bash
# Generate test keys
npm run generate-keys:dev

# Run auth tests
npm test -- tests/auth

# Start with refresh tokens enabled
ENABLE_REFRESH=true npm run dev
```

## Additional Resources

- Documentation: docs/auth-architecture.md
- Slack thread: #architecture (search "RS256 migration")
- Design doc: https://notion.so/auth-refactor-spec
```

**Sources:** [README.md:230]()

### Handoff Update Protocol

1. **Creating handoff:** Developer A creates file before ending session
2. **Claiming handoff:** Developer B adds comment at top: `**Claimed by:** @bob on 2025-01-16`
3. **During work:** Developer B updates progress in comments
4. **Completing handoff:** Developer B adds final comment: `**Completed:** 2025-01-17 - Merged in PR #789`

---

## Active Session Tracking

Active session tracking in `state.md` provides real-time visibility into who is working on what, enabling conflict prevention and coordination.

### Session Lifecycle States

```mermaid
stateDiagram-v2
    [*] --> Claimed: "Claim todo in state.md"
    Claimed --> Active: "Start work, mark 🟢 Active"
    Active --> Active: "Checkpoint updates<br/>every ~1 hour"
    Active --> Checkpoint: "Pause work, mark 🟡"
    Checkpoint --> Active: "Resume work"
    Active --> Ended: "Complete work, mark 🔴"
    Ended --> [*]: "Move to Recent Completions"
    Claimed --> Released: "Unclaim if blocked"
    Released --> [*]: "Remove from Claimed Todos"
```

**Sources:** [README.md:236-241]()

### Session Information Tracked

For each active session, `state.md` maintains:

| Field | Purpose | Update Frequency | Example |
|-------|---------|------------------|---------|
| Developer | Who is working | Once at claim | `@alice` |
| Status | Current state | Every checkpoint | `🟢 Active` |
| Working On | Todo being addressed | Once at claim | `[TODO-042] Email validation` |
| Files Being Modified | Conflict detection | Every checkpoint | `src/auth/validate.ts` |
| Started | Session start time | Once at start | `2025-01-15 14:00` |

### Conflict Detection Logic

The system detects potential conflicts by comparing file lists across active sessions:

```
IF Developer A files ∩ Developer B files ≠ ∅
THEN Add to "Potential Conflicts" table
```

**Example scenario:**
- @alice working on `src/auth/validate.ts, src/auth/types.ts`
- @bob starts work on `src/auth/types.ts, src/auth/middleware.ts`
- System detects overlap on `src/auth/types.ts`
- Adds warning to Potential Conflicts table

**Sources:** [README.md:238]()

---

## Converting Solo to Team Projects

The `/check-contributors` command automatically detects whether a project is solo or team-based and offers conversion.

### Detection Logic

```mermaid
flowchart TD
    Start["Command: /check-contributors"]
    
    CheckDir["Check for<br/>_project_specs/team/"]
    
    DirExists{"Directory<br/>exists?"}
    
    CheckContrib["Check contributors.md<br/>for multiple developers"]
    
    MultiDev{"More than<br/>1 developer?"}
    
    TeamMode["TEAM MODE<br/>Show current state"]
    
    SoloMode["SOLO MODE<br/>Offer conversion"]
    
    UserChoice{"User wants<br/>to convert?"}
    
    Convert["Run conversion:<br/>Create team/ structure<br/>Generate initial files"]
    
    Done["Done"]
    
    Start --> CheckDir
    CheckDir --> DirExists
    
    DirExists -->|Yes| CheckContrib
    DirExists -->|No| SoloMode
    
    CheckContrib --> MultiDev
    
    MultiDev -->|Yes| TeamMode
    MultiDev -->|No| SoloMode
    
    SoloMode --> UserChoice
    
    UserChoice -->|Yes| Convert
    UserChoice -->|No| Done
    
    TeamMode --> Done
    Convert --> Done
```

**Sources:** [README.md:219-222]()

### Conversion Process

When converting from solo to team, the system:

1. **Creates team directory structure:**
```bash
mkdir -p _project_specs/team/handoffs
```

2. **Generates initial state.md:**
```markdown
# Team State

*Last updated: [timestamp] by [username]*

## Active Sessions

| Developer | Status | Working On | Files Being Modified | Started |
|-----------|--------|------------|---------------------|---------|

## Claimed Todos

| Todo ID | Claimed By | Claimed At | Status | Notes |
|---------|------------|------------|--------|-------|

## Potential Conflicts

| Warning | Developers | Files | Detected | Resolution |
|---------|-----------|-------|----------|------------|

## Recent Completions

| Todo ID | Completed By | Completed At | Pushed To |
|---------|--------------|--------------|-----------|
```

3. **Generates contributors.md:**
```markdown
# Contributors

## Team Members

| GitHub Handle | Name | Role | Primary Focus | Join Date |
|---------------|------|------|---------------|-----------|
| @[current-user] | [from git config] | Developer | Full Stack | [today] |

## Ownership Areas

[To be filled in by team]
```

4. **Migrates relevant decisions:**
   - If `_project_specs/session/decisions.md` exists
   - Copy to `_project_specs/team/decisions.md`
   - Add note about source

5. **Updates CLAUDE.md:**
   - Adds team coordination instructions
   - References state.md update requirements

**Sources:** [README.md:249-253]()

---

## Workflow Integration with Git

The team state system integrates tightly with the git workflow to ensure state synchronization.

### Standard Team Workflow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Local as "Local Repo"
    participant Remote as "Remote (GitHub)"
    participant State as "state.md"
    
    Note over Dev: "Start of Work Session"
    Dev->>Remote: "git pull origin main"
    Remote-->>Local: "Latest state.md"
    Dev->>State: "Read active sessions"
    Dev->>State: "Check for conflicts"
    
    alt No Conflicts
        Dev->>State: "Claim todo"
        Dev->>Local: "git add state.md"
        Dev->>Local: "git commit -m 'chore: claim TODO-XXX'"
        Dev->>Remote: "git push origin main"
        
        loop Development Work
            Dev->>Local: "Work on feature"
            Dev->>Local: "Write tests, implement, commit"
            
            Note over Dev: "Every ~1 hour"
            Dev->>State: "Update files list"
            Dev->>Local: "git add state.md"
            Dev->>Local: "git commit -m 'chore: state checkpoint'"
            Dev->>Remote: "git push origin main"
        end
        
        Note over Dev: "Feature Complete"
        Dev->>State: "Mark 🔴 Ended"
        Dev->>State: "Move to Recent Completions"
        Dev->>Local: "git add state.md"
        Dev->>Local: "git commit -m 'chore: complete TODO-XXX'"
        Dev->>Remote: "git push origin main"
    else Conflict Detected
        Dev->>Dev: "Coordinate with team"
        Dev->>State: "Log in Potential Conflicts"
    end
```

**Sources:** [README.md:244-246]()

### Handling Merge Conflicts in state.md

Since `state.md` is frequently updated, merge conflicts can occur. Resolution pattern:

```bash
# If pull fails due to conflict
git pull origin main
# CONFLICT in _project_specs/team/state.md

# Manual resolution:
# 1. Keep both active sessions (merge the tables)
# 2. Keep all claimed todos (merge the tables)
# 3. Resolve "Last updated" to latest timestamp
# 4. Keep all potential conflicts

# After manual edit:
git add _project_specs/team/state.md
git commit -m "chore: merge team state"
git push origin main
```

### Race Condition Handling

| Scenario | Risk | Mitigation |
|----------|------|------------|
| Two developers claim same todo | 🔴 High | First push wins, second sees error and picks different todo |
| Two developers update state simultaneously | 🟡 Medium | Git merge conflict forces manual resolution |
| Developer forgets to update end state | 🟢 Low | Stale sessions visible in state.md, team cleanup periodically |

**Best practice:** Always `git pull` before claiming todos and before updating state.

---

## State File Synchronization Patterns

### Pull-Before-Claim Protocol

```markdown
ALWAYS follow this sequence:

1. git pull origin main                    # Get latest state
2. cat _project_specs/team/state.md        # Read current state
3. Choose available todo                   # From active.md
4. Update state.md (claim todo)            # Add to Claimed Todos
5. git add _project_specs/team/state.md
6. git commit -m "chore: claim TODO-XXX"
7. git push origin main                    # Publish claim

IF push fails:
  - Someone else pushed state changes
  - git pull --rebase origin main
  - Verify your claim is still valid
  - git push origin main
```

### Checkpoint Commit Pattern

```bash
# Every ~1 hour or after significant progress
git add _project_specs/team/state.md
git commit -m "chore: update team state checkpoint"
git push origin main

# Separate from feature commits
git add src/auth/validate.ts tests/auth/validate.test.ts
git commit -m "feat: add email validation"
git push origin main
```

### State Cleanup Protocol

Teams should periodically clean stale entries:

```markdown
Weekly cleanup (assign to rotating team member):

1. Review "Active Sessions" table
   - Sessions >24 hours old with no updates → Mark as 🔴 Ended
   - Contact developer if unclear

2. Review "Claimed Todos" table
   - Claims >48 hours old with no progress → Release
   - Contact developer before releasing

3. Review "Potential Conflicts" table
   - Resolved conflicts → Remove from table
   - Update resolution notes

4. Archive "Recent Completions"
   - Keep last 10 completions
   - Move older to _project_specs/team/archive/completions-YYYY-MM.md
```

**Sources:** [README.md:244-246]()

---

## Integration with Session Management

The team state system (page 8.2) works alongside individual session management (see [Session Management](#4.2)) but serves different purposes:

| Aspect | Team State (_project_specs/team/) | Session State (_project_specs/session/) |
|--------|-----------------------------------|----------------------------------------|
| **Purpose** | Coordinate between multiple developers | Track individual developer's work state |
| **Audience** | Entire team | Single developer + future self |
| **Update Trigger** | Session start/end, checkpoints | After tasks, decisions, context shifts |
| **Scope** | What files/todos are claimed | Detailed progress, decisions, next steps |
| **Conflict Focus** | Prevent overlapping work | Preserve mental model across sessions |

### When Both Exist

For team projects, developers maintain both:

```
_project_specs/
├── session/                 # Personal state
│   ├── current-state.md     # "I'm 60% done with email validation"
│   └── decisions.md         # "I chose Zod because..."
└── team/                    # Shared state
    ├── state.md             # "@alice working on email validation"
    └── contributors.md      # "@alice owns auth system"
```

**Update pattern:**
1. Start session → Update `team/state.md` (claim todo)
2. Work → Update `session/current-state.md` (personal progress)
3. Make decision → Log to both `session/decisions.md` AND `team/decisions.md` if architectural
4. Checkpoint → Update both `session/current-state.md` and `team/state.md`
5. End session → Update `team/state.md` (mark complete)

**Sources:** [README.md:228-229](), [skills/session-management.md:66-76]()

---

## Command Reference

### /check-contributors Flags

```bash
# Check status and offer conversion if solo
/check-contributors

# Show quick status without prompts
/check-contributors --status

# Force conversion to team mode
/check-contributors --team
```

**Output example (solo project):**
```
📊 Project Status: SOLO MODE

_project_specs/team/ does not exist.

Would you like to convert this to a team project?
This will create:
  - _project_specs/team/state.md
  - _project_specs/team/contributors.md
  - _project_specs/team/handoffs/

[y/n]
```

**Output example (team project):**
```
📊 Project Status: TEAM MODE

Active Sessions:
  🟢 @alice: [TODO-042] Email validation (started 2h ago)
  🟡 @bob: [TODO-038] API rate limiting (checkpoint 1h ago)

Claimed Todos: 2
Potential Conflicts: 0

Recent Activity:
  ✅ @carol completed [TODO-035] User profile page (30m ago)
```

**Sources:** [README.md:249-253]()

---

## Anti-Patterns and Common Mistakes

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Not pulling before claiming** | Claim same todo as someone else | Always `git pull` then read state.md first |
| **Never updating state** | Team blind to your work | Update state.md at session start/checkpoints/end |
| **Claiming multiple todos** | Blocks others unnecessarily | Claim one at a time, only claim next when current done |
| **Ignoring conflict warnings** | Duplicate work or merge nightmares | Coordinate immediately when conflict detected |
| **Not writing handoffs** | Context loss on transition | Create handoff before ending incomplete work |
| **Stale session status** | Team can't tell if you're active | Mark 🔴 Ended when done or 🟡 Checkpoint when pausing |
| **Committing state with feature code** | Makes state changes less visible | Separate commits for state.md updates |
| **Not reading contributors.md** | Work on someone else's area without asking | Check ownership before starting work in new area |

---

## Quick Reference

### State Update Checklist

```markdown
✅ At Session Start:
- [ ] git pull origin main
- [ ] Read _project_specs/team/state.md
- [ ] Check for conflicts with planned work
- [ ] Claim todo in state.md
- [ ] Add to Active Sessions (🟢)
- [ ] Commit and push state.md

✅ During Work (every ~1 hour):
- [ ] Update "Files Being Modified"
- [ ] Update timestamp in header
- [ ] Commit state.md separately

✅ At Session End:
- [ ] Change status to 🔴 Ended
- [ ] Move todo to Recent Completions
- [ ] Remove from Claimed Todos
- [ ] Create handoff if work incomplete
- [ ] Commit and push state.md
```

### File Location Summary

| File | Location | Purpose |
|------|----------|---------|
| Team state | `_project_specs/team/state.md` | Active coordination |
| Contributors | `_project_specs/team/contributors.md` | Team roster |
| Shared decisions | `_project_specs/team/decisions.md` | Architectural choices |
| Handoffs | `_project_specs/team/handoffs/*.md` | Context transfer |
| Personal state | `_project_specs/session/current-state.md` | Individual progress |
| Personal decisions | `_project_specs/session/decisions.md` | Personal choices |

**Sources:** [README.md:225-231](), [skills/session-management.md:66-76]()

---

# Page: Reference

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [commands/initialize-project.md](commands/initialize-project.md)

</details>



This page provides technical reference documentation for Claude Bootstrap's commands, configuration files, and system internals. Use this as a quick lookup guide when working with Claude Bootstrap projects.

For step-by-step workflows, see [Quick Start](#2). For architectural concepts and philosophy, see [Core Concepts](#3). For extending the system with custom skills and commands, see [Extending Claude Bootstrap](#9.3).

---

## Command Overview

Claude Bootstrap provides six core commands accessible through Claude Code's command interface.

### Command Quick Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/initialize-project` | Set up or update project structure, skills, and tooling | First time setup, updating skills, adding missing configuration |
| `/check-contributors` | View team state, detect conflicts, convert solo→team | Start of session, before claiming todos, checking for conflicts |
| `/code-review` | Analyze changes for security, performance, architecture issues | Before commits, enforced by pre-push hook |
| `/update-code-index` | Regenerate semantic capability index from codebase | After adding/removing major functionality, periodic maintenance |
| `/ralph-loop` | Run iterative TDD loop until completion criteria met | Manual iteration when automatic loops disabled |
| `/cancel-ralph` | Stop currently running Ralph loop | Emergency stop, when loop is stuck |

**Note:** Detailed syntax, options, and examples for each command are covered in [Commands Reference](#9.1).

**Sources:** [README.md:467-495](), [commands/initialize-project.md:1-821]()

---

## Project Structure

Claude Bootstrap creates a standardized directory structure that supports TDD workflows, session management, and team coordination.

### Directory Structure Diagram

```mermaid
graph TB
    subgraph "Project Root"
        ROOT["/"]
    end
    
    subgraph ".claude/ - Skills & Configuration"
        SKILLS[".claude/skills/"]
        BASE["base.md"]
        SECURITY["security.md"]
        LANG["python.md / typescript.md"]
        FRAMEWORK["react-web.md / fastapi.md"]
    end
    
    subgraph "_project_specs/ - State & Specifications"
        SPECS["_project_specs/"]
        OVERVIEW["overview.md"]
        FEATURES["features/"]
        TODOS["todos/"]
        ACTIVE["todos/active.md"]
        BACKLOG["todos/backlog.md"]
        COMPLETED["todos/completed.md"]
        SESSION["session/"]
        CURRENT["session/current-state.md"]
        DECISIONS["session/decisions.md"]
        LANDMARKS["session/code-landmarks.md"]
        ARCHIVE["session/archive/"]
        PROMPTS["prompts/"]
        TEAM["team/"]
        STATE["team/state.md"]
        CONTRIB["team/contributors.md"]
        HANDOFFS["team/handoffs/"]
    end
    
    subgraph "scripts/ - Automation"
        SCRIPTS["scripts/"]
        VERIFY["verify-tooling.sh"]
        SECCHECK["security-check.sh"]
    end
    
    subgraph ".github/ - CI/CD"
        GITHUB[".github/workflows/"]
        QUALITY["quality.yml"]
        SECURITYWF["security.yml"]
    end
    
    subgraph "Configuration Files"
        CLAUDEMD["CLAUDE.md"]
        GITIGNORE[".gitignore"]
        ENVEXAMPLE[".env.example"]
        ENV[".env - NEVER COMMIT"]
    end
    
    ROOT --> SKILLS
    ROOT --> SPECS
    ROOT --> SCRIPTS
    ROOT --> GITHUB
    ROOT --> CLAUDEMD
    ROOT --> GITIGNORE
    ROOT --> ENVEXAMPLE
    ROOT --> ENV
    
    SKILLS --> BASE
    SKILLS --> SECURITY
    SKILLS --> LANG
    SKILLS --> FRAMEWORK
    
    SPECS --> OVERVIEW
    SPECS --> FEATURES
    SPECS --> TODOS
    SPECS --> SESSION
    SPECS --> PROMPTS
    SPECS --> TEAM
    
    TODOS --> ACTIVE
    TODOS --> BACKLOG
    TODOS --> COMPLETED
    
    SESSION --> CURRENT
    SESSION --> DECISIONS
    SESSION --> LANDMARKS
    SESSION --> ARCHIVE
    
    TEAM --> STATE
    TEAM --> CONTRIB
    TEAM --> HANDOFFS
    
    SCRIPTS --> VERIFY
    SCRIPTS --> SECCHECK
    
    GITHUB --> QUALITY
    GITHUB --> SECURITYWF
```

**Sources:** [README.md:296-318](), [commands/initialize-project.md:134-143]()

### Core Directories

| Directory | Purpose | Created By | Overwritten on Re-init? |
|-----------|---------|------------|-------------------------|
| `.claude/skills/` | Coding guardrails and patterns | `/initialize-project` | Yes - always updated with latest |
| `_project_specs/` | Project state, todos, session management | `/initialize-project` | No - preserved |
| `_project_specs/features/` | Feature specifications | User/Claude | No |
| `_project_specs/todos/` | Atomic todos (active, backlog, completed) | `/initialize-project` | No - todos preserved |
| `_project_specs/session/` | Session state, decisions, landmarks | `/initialize-project` | No - state preserved |
| `_project_specs/team/` | Team coordination (state, contributors, handoffs) | `/check-contributors --team` | No |
| `scripts/` | Automation scripts (verify, security) | `/initialize-project` | Yes - scripts updated |
| `.github/workflows/` | CI/CD pipelines | `/initialize-project` | Yes if missing |
| `docs/` | Technical documentation | `/initialize-project` | No |

**Sources:** [commands/initialize-project.md:134-617]()

---

## Configuration Files

### CLAUDE.md

The primary instruction file that Claude reads on project load. Contains skills list, project overview, tech stack, and key commands.

**Structure:**
```markdown
## Skills
- .claude/skills/base.md
- .claude/skills/security.md
- [other skills]

## Project Overview
[Description]

## Tech Stack
[Stack details]

## Key Commands
[Project commands]

## Atomic Todos
[Todo workflow]

## Session Management
[Session state tracking rules]

## Project-Specific Patterns
[Custom patterns]
```

**Location:** `CLAUDE.md` (project root)

**Created by:** `/initialize-project`

**Preservation:** Existing `CLAUDE.md` is preserved and updated, not overwritten

**Sources:** [commands/initialize-project.md:320-438]()

### .gitignore

Security-critical file that prevents secrets from being committed.

**Key entries:**
```gitignore
.env
.env.*
!.env.example
*.pem
*.key
credentials.json
secrets.json
service-account*.json
node_modules/
__pycache__/
```

**Location:** `.gitignore` (project root)

**Created by:** `/initialize-project`

**Enforcement:** `scripts/security-check.sh` validates before commits

**Sources:** [commands/initialize-project.md:168-200]()

### .env.example

Template for environment variables. Developers copy to `.env` and fill in actual values.

**Pattern:**
```bash
# .env.example - Copy to .env and fill in values
# Server-side only (NEVER prefix with VITE_ or NEXT_PUBLIC_)
DATABASE_URL=
ANTHROPIC_API_KEY=

# Client-side safe (public, non-sensitive)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

**Security rules:**
- Server secrets: NO `VITE_*` or `NEXT_PUBLIC_*` prefix
- Client vars: Only non-sensitive values
- Never commit `.env` (only `.env.example`)

**Sources:** [commands/initialize-project.md:203-214](), [README.md:29-32]()

### verify-tooling.sh

Validates CLI tools are installed and authenticated.

**Checks:**
- GitHub CLI: `gh auth status`
- Vercel CLI: `vercel whoami`
- Supabase CLI: `supabase projects list`

**Location:** `scripts/verify-tooling.sh`

**Usage:** `./scripts/verify-tooling.sh`

**Sources:** [commands/initialize-project.md:217-267]()

### security-check.sh

Pre-commit security validation script.

**Checks:**
1. `.env` not staged for commit
2. Common secret patterns in staged files
3. `VITE_*` secrets (client-exposed)
4. Dependency vulnerabilities (`npm audit`, `safety check`)

**Location:** `scripts/security-check.sh`

**Enforcement:** Pre-commit hooks, GitHub Actions

**Sources:** [commands/initialize-project.md:270-318]()

---

## Skills System

### Skills Loading Flow

```mermaid
graph LR
    subgraph "Installation"
        INSTALL["install.sh"]
        HOME["~/.claude/skills/<br/>Master Repository"]
    end
    
    subgraph "Project Initialization"
        INITCMD["/initialize-project"]
        DETECT["Detect Project Type"]
        SELECT["Select Skills"]
    end
    
    subgraph "Project Skills"
        PROJSKILLS[".claude/skills/"]
        PROJBASE["base.md"]
        PROJSEC["security.md"]
        PROJLANG["python.md"]
        PROJFMWK["react-web.md"]
    end
    
    subgraph "CLAUDE.md Reference"
        CLAUDEMD["CLAUDE.md"]
        SKILLSLIST["## Skills<br/>List of .claude/skills/*"]
    end
    
    INSTALL --> HOME
    
    INITCMD --> DETECT
    DETECT --> SELECT
    SELECT --> HOME
    
    HOME --> PROJSKILLS
    PROJSKILLS --> PROJBASE
    PROJSKILLS --> PROJSEC
    PROJSKILLS --> PROJLANG
    PROJSKILLS --> PROJFMWK
    
    PROJSKILLS --> CLAUDEMD
    CLAUDEMD --> SKILLSLIST
    SKILLSLIST --> PROJBASE
    SKILLSLIST --> PROJSEC
    SKILLSLIST --> PROJLANG
    SKILLSLIST --> PROJFMWK
```

**Sources:** [commands/initialize-project.md:145-166](), [README.md:396-466]()

### Skill Categories and File Names

| Category | File Names | Selection Criteria |
|----------|------------|-------------------|
| **Core** (always loaded) | `base.md`, `security.md`, `credentials.md`, `session-management.md`, `project-tooling.md`, `code-review.md`, `commit-hygiene.md`, `code-deduplication.md`, `team-coordination.md`, `iterative-development.md` | Always copied |
| **Language** | `python.md`, `typescript.md` | Based on language selection |
| **Framework** | `react-web.md`, `react-native.md`, `nodejs-backend.md`, `fastapi.md` | Based on framework selection |
| **UI** | `ui-web.md`, `ui-mobile.md`, `ui-testing.md`, `playwright-testing.md` | If web or mobile project |
| **AI & Agentic** | `agentic-development.md`, `llm-patterns.md`, `ai-models.md` | If `--ai-first` flag set |
| **Database** | `database-schema.md`, `supabase.md`, `supabase-nextjs.md`, `supabase-python.md`, `supabase-node.md` | If Supabase selected |
| **Integration** | `web-payments.md`, `posthog-analytics.md`, `reddit-api.md`, `reddit-ads.md`, `ms-teams-apps.md`, `shopify-apps.md`, `woocommerce.md`, `medusa.md`, `klaviyo.md` | If integration selected |
| **Content & SEO** | `aeo-optimization.md`, `web-content.md`, `site-architecture.md` | If content/SEO focus |
| **User Experience** | `user-journeys.md`, `pwa-development.md` | If UX or PWA focus |

**Sources:** [README.md:398-466](), [commands/initialize-project.md:145-166]()

---

## Git Hooks System

### Hook Installation Flow

```mermaid
graph TB
    subgraph "Global Installation"
        INSTALL["~/.claude-bootstrap/install.sh"]
        HOOKS["~/.claude/hooks/"]
        PREPUSH["~/.claude/hooks/pre-push"]
    end
    
    subgraph "Project Hook Setup"
        INITPROJ["/initialize-project"]
        CHECKHOOKS["Check if .git/ exists"]
        COPYHOOK["Copy pre-push to<br/>.git/hooks/pre-push"]
        CHMOD["chmod +x"]
    end
    
    subgraph "Git Operations"
        COMMIT["git commit"]
        PRECOMMIT[".git/hooks/pre-commit"]
        SECCHECK["scripts/security-check.sh"]
        PUSH["git push"]
        PUSHEXEC[".git/hooks/pre-push"]
    end
    
    subgraph "Pre-Push Actions"
        REVIEW["/code-review"]
        SEVERITY["Check Severity"]
        BLOCK["Block if Critical/High"]
        ALLOW["Allow if Medium/Low"]
    end
    
    INSTALL --> HOOKS
    HOOKS --> PREPUSH
    
    INITPROJ --> CHECKHOOKS
    CHECKHOOKS --> COPYHOOK
    COPYHOOK --> CHMOD
    PREPUSH --> COPYHOOK
    
    COMMIT --> PRECOMMIT
    PRECOMMIT --> SECCHECK
    
    PUSH --> PUSHEXEC
    PUSHEXEC --> REVIEW
    REVIEW --> SEVERITY
    SEVERITY --> BLOCK
    SEVERITY --> ALLOW
```

**Sources:** [commands/initialize-project.md:678-698](), [README.md:176-209]()

### Hook Locations

| Hook | Location | Purpose | Enforcement Level |
|------|----------|---------|-------------------|
| `pre-commit` | `.git/hooks/pre-commit` | Lint, type-check, unit tests, security scan | Blocks commit on failure |
| `pre-push` | `.git/hooks/pre-push` | `/code-review` - blocks on Critical/High issues | Blocks push on Critical/High |

**Manual installation:** Run `~/.claude/install-hooks.sh` in any project

**Disable hooks:** `rm .git/hooks/pre-push` or `rm .git/hooks/pre-commit`

**Sources:** [commands/initialize-project.md:678-698](), [README.md:188-192]()

---

## CI/CD Workflows

### GitHub Actions Files

| File | Triggers | Checks | Failure Action |
|------|----------|--------|----------------|
| `.github/workflows/quality.yml` | Push to main, PRs | Lint, type-check, tests, 80% coverage | Blocks merge |
| `.github/workflows/security.yml` | Push to main, PRs, weekly schedule | TruffleHog secret scan, `npm audit`, `safety check` | Blocks merge |

### Security Workflow Structure

```yaml
name: Security
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 9 * * 1'  # Weekly

jobs:
  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: trufflesecurity/trufflehog@main

  dependency-audit:
    runs-on: ubuntu-latest
    steps:
      - name: NPM Audit
        run: npm audit --audit-level=high
      - name: Safety check
        run: pip install safety && safety check
```

**Sources:** [commands/initialize-project.md:619-668]()

---

## Session State Files

### State File Mapping

```mermaid
graph TB
    subgraph "Session Files"
        CURRENT["_project_specs/session/<br/>current-state.md"]
        DECISIONS["_project_specs/session/<br/>decisions.md"]
        LANDMARKS["_project_specs/session/<br/>code-landmarks.md"]
        ARCHIVE["_project_specs/session/<br/>archive/"]
    end
    
    subgraph "Update Triggers"
        TODOCOMPLETE["Todo Completed"]
        TOOLCALLS["15-20 Tool Calls"]
        CONTEXTSHIFT["Context Shift"]
        BLOCKER["Blocker Encountered"]
        DECISION["Architectural Decision"]
        NEWPATTERN["New Pattern Added"]
    end
    
    subgraph "Usage Patterns"
        RESUME["Resume Session:<br/>Read current-state.md"]
        HANDOFF["Handoff Work:<br/>Update current-state.md"]
        COMPRESS["Compress Context:<br/>Move to archive/"]
    end
    
    TODOCOMPLETE --> CURRENT
    TOOLCALLS --> CURRENT
    CONTEXTSHIFT --> CURRENT
    BLOCKER --> CURRENT
    
    DECISION --> DECISIONS
    
    NEWPATTERN --> LANDMARKS
    
    CURRENT --> RESUME
    CURRENT --> HANDOFF
    CURRENT --> COMPRESS
    COMPRESS --> ARCHIVE
```

**Sources:** [commands/initialize-project.md:395-427](), [commands/initialize-project.md:495-617]()

### File Update Rules

| File | Update Frequency | Content | Append-Only? |
|------|------------------|---------|--------------|
| `current-state.md` | After todo completion, every 15-20 tool calls, before context shift | Active task, status, files modified, next steps | No - overwrites |
| `decisions.md` | When making architectural/security decisions | Decision, context, options, choice, reasoning, trade-offs | Yes |
| `code-landmarks.md` | When adding entry points, patterns, gotchas | Entry points, business logic, config locations, patterns | No - updates sections |
| `archive/*.md` | End of session or major feature | Historical session summaries | Yes - new files |

**Sources:** [commands/initialize-project.md:495-617]()

---

## Todo File Format

### Todo Structure

```markdown
## [TODO-042] Add email validation to signup form

**Status:** in-progress
**Priority:** high
**Estimate:** S

### Acceptance Criteria
- [ ] Email field shows error for invalid format
- [ ] Form cannot submit with invalid email

### Test Cases
| Input | Expected |
|-------|----------|
| user@example.com | Valid |
| notanemail | Error |

### TDD Execution Log
| Phase | Command | Result |
|-------|---------|--------|
| RED | `npm test -- --grep "email validation"` | 2 tests failed ✓ |
| GREEN | `npm test -- --grep "email validation"` | 2 tests passed ✓ |
| VALIDATE | `npm run lint && npm run typecheck` | Pass, 84% ✓ |
```

**Sources:** [README.md:533-577]()

### Todo Workflow States

| File | Contains | State Transitions |
|------|----------|-------------------|
| `_project_specs/todos/active.md` | Currently in progress | New → Active |
| `_project_specs/todos/backlog.md` | Future work, prioritized | Backlog → Active (when started) |
| `_project_specs/todos/completed.md` | Done items for reference | Active → Completed (when done) |

**Move operations:** Cut from source file, paste into destination file (never delete)

**Sources:** [README.md:384-394](), [commands/initialize-project.md:462-493]()

---

## Atomic Commit Thresholds

### Commit Size Guidelines

```mermaid
graph TB
    subgraph "Monitoring"
        GITSTATUS["git status"]
        COUNTFILES["Count Changed Files"]
        COUNTLINES["Count Changed Lines"]
    end
    
    subgraph "Thresholds"
        OK["🟢 OK<br/>≤ 5 files<br/>≤ 200 lines"]
        WARN["🟡 WARN<br/>6-10 files<br/>201-400 lines"]
        STOP["🔴 STOP<br/>> 10 files<br/>> 400 lines"]
    end
    
    subgraph "Actions"
        CONTINUE["Continue Working"]
        CONSIDER["Consider Committing Soon"]
        COMMITNOW["Commit NOW"]
    end
    
    GITSTATUS --> COUNTFILES
    GITSTATUS --> COUNTLINES
    
    COUNTFILES --> OK
    COUNTFILES --> WARN
    COUNTFILES --> STOP
    
    COUNTLINES --> OK
    COUNTLINES --> WARN
    COUNTLINES --> STOP
    
    OK --> CONTINUE
    WARN --> CONSIDER
    STOP --> COMMITNOW
```

**Rationale:**
- PRs < 200 lines: 15% defect rate
- PRs 200-400 lines: 23% defect rate
- PRs > 400 lines: 40%+ defect rate (often rubber-stamped)

**Atomic commit principle:** If you need "and" to describe your commit, split it.

**Sources:** [README.md:119-146]()

---

## Access.txt Credential Format

Centralized credential storage outside the repository.

**Format:**
```
OpenAI API: sk-proj-xxx
Claude API: sk-ant-xxx
Stripe: sk_test_xxx
Supabase url: https://xxx.supabase.co
Anon key: eyJxxx
```

**Location:** User-specified (e.g., `~/Documents/Access.txt`)

**Detection patterns:**
- `OpenAI API:` → Extracts `OPENAI_API_KEY`
- `Claude API:` → Extracts `ANTHROPIC_API_KEY`
- `Stripe:` → Extracts `STRIPE_SECRET_KEY`
- `Supabase url:` → Extracts `SUPABASE_URL`
- `Anon key:` → Extracts `SUPABASE_ANON_KEY`

**Workflow:**
1. `/initialize-project` asks for Access.txt location
2. Reads and parses credentials
3. Validates keys (API calls with test values)
4. Generates `.env` with validated keys
5. Adds `.env` to `.gitignore`

**Sources:** [README.md:367-378]()

---

## Quick Reference Tables

### Environment Variable Patterns

| Pattern | Exposure | Usage | Example |
|---------|----------|-------|---------|
| `DATABASE_URL` | Server-only | Database connection | ✅ Safe for secrets |
| `ANTHROPIC_API_KEY` | Server-only | API authentication | ✅ Safe for secrets |
| `VITE_*` | **Client-exposed** | Vite frontend env vars | ⚠️ NO SECRETS |
| `NEXT_PUBLIC_*` | **Client-exposed** | Next.js frontend env vars | ⚠️ NO SECRETS |
| `VITE_SUPABASE_URL` | Client-safe | Public Supabase URL | ✅ Safe (non-sensitive) |
| `VITE_POSTHOG_KEY` | Client-safe | Public analytics key | ✅ Safe (non-sensitive) |

**Security rule:** Any `VITE_*` or `NEXT_PUBLIC_*` variable is visible to all users in browser. Never use for secrets.

**Sources:** [README.md:29-32](), [commands/initialize-project.md:203-214]()

### Coverage and Quality Gates

| Gate | Threshold | Enforcement | Failure Action |
|------|-----------|-------------|----------------|
| Test Coverage | ≥ 80% | CI, pre-push | Blocks merge/push |
| Lint | 0 errors | Pre-commit, CI | Blocks commit/merge |
| Type Check | 0 errors | Pre-commit, CI | Blocks commit/merge |
| Secret Scan | 0 secrets | Pre-commit, CI | Blocks commit/merge |
| Dependency Audit | 0 high/critical | CI, weekly | Blocks merge |
| Code Review Severity | No Critical/High | Pre-push | Blocks push |

**Sources:** [README.md:515-529](), [commands/initialize-project.md:619-668]()

### Complexity Constraints

| Constraint | Limit | Enforcement | Violation Action |
|------------|-------|-------------|------------------|
| Lines per function | 20 | `base.md` skill | STOP - refactor required |
| Parameters per function | 3 | `base.md` skill | STOP - refactor required |
| Nesting depth | 2 levels | `base.md` skill | STOP - refactor required |
| Lines per file | 200 | `base.md` skill | STOP - split file |
| Test coverage | 80% minimum | CI pipeline | Blocks merge |

**STOP protocol:** Development pauses until violation is fixed. No "TODO" comments allowed.

**Sources:** [README.md:344-357]()

---

## Additional Reference Material

For detailed command syntax, parameters, and examples, see [Commands Reference](#9.1).

For complete file format specifications and configuration options, see [Configuration and Project Structure](#9.2).

For creating custom skills, commands, and modifying initialization, see [Extending Claude Bootstrap](#9.3).

---

# Page: Commands Reference

# Commands Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [commands/initialize-project.md](commands/initialize-project.md)
- [install.sh](install.sh)

</details>



This document provides a complete technical reference for all custom commands available in Claude Bootstrap. Commands are installed to `~/.claude/commands/` and are invoked in Claude Code using the `/command-name` syntax.

For information about the skills system that these commands interact with, see [Skills Architecture](#5.1). For details on the development workflow that these commands support, see [Ralph Loop: Iterative Development](#4.1).

---

## Command Overview

All commands are markdown files stored in `~/.claude/commands/` and copied during installation via [install.sh:19-22]().

| Command | Purpose | Primary Use Case | Blocking Behavior |
|---------|---------|------------------|-------------------|
| `/initialize-project` | Project setup and configuration | First-time setup, skill updates | No |
| `/check-contributors` | Team coordination and state management | Multi-developer projects | No |
| `/code-review` | Automated code review analysis | Pre-push validation | Yes (Critical/High issues) |
| `/update-code-index` | Regenerate semantic capability index | Prevent duplicate code | No |
| `/ralph-loop` | Iterative TDD execution engine | Feature development, bug fixes | No |
| `/cancel-ralph` | Stop active Ralph loop | Cancel runaway iterations | No |
| `/audit-duplicates` | Find semantic code duplication | Code cleanup | No |

Sources: [README.md:52-62](), [README.md:248-253](), [install.sh:19-22]()

---

## Command Invocation Architecture

### Diagram: Command Installation and Execution Flow

```mermaid
graph TB
    subgraph "Installation Phase"
        REPO["~/.claude-bootstrap/<br/>Repository"]
        INSTALL["install.sh"]
        GLOBAL["~/.claude/commands/<br/>Global Commands"]
    end
    
    subgraph "Project Initialization"
        INIT["/initialize-project"]
        PROJECT_SKILLS[".claude/skills/<br/>Project Skills"]
        PROJECT_SPECS["_project_specs/<br/>Project State"]
    end
    
    subgraph "Runtime Execution"
        USER["Developer in<br/>Claude Code"]
        COMMAND_INVOKE["Command Invocation<br/>/command-name"]
        COMMAND_LOGIC["Command Logic<br/>Markdown file"]
    end
    
    subgraph "Command Types by Data Flow"
        READ_ONLY["/check-contributors<br/>/update-code-index"]
        WRITE_STATE["/initialize-project<br/>/ralph-loop"]
        VALIDATION["/code-review<br/>/audit-duplicates"]
    end
    
    REPO -->|"cp commands/*.md"| INSTALL
    INSTALL -->|"install.sh:19-22"| GLOBAL
    
    USER --> COMMAND_INVOKE
    COMMAND_INVOKE --> COMMAND_LOGIC
    COMMAND_LOGIC --> READ_ONLY
    COMMAND_LOGIC --> WRITE_STATE
    COMMAND_LOGIC --> VALIDATION
    
    INIT -->|"Copies from ~/.claude/skills/"| PROJECT_SKILLS
    INIT -->|"Creates structure"| PROJECT_SPECS
    
    WRITE_STATE -->|"Modifies"| PROJECT_SPECS
    READ_ONLY -->|"Reads"| PROJECT_SPECS
```

Sources: [install.sh:1-66](), [commands/initialize-project.md:1-821]()

---

## /initialize-project

**Purpose:** Full project setup with Claude coding guardrails, security configuration, and skill installation. Idempotent - can be run multiple times to update skills or add missing structure.

### Syntax

```bash
/initialize-project
```

No command-line options. All configuration is performed through interactive questions.

### Execution Phases

The command executes in five sequential phases as defined in [commands/initialize-project.md:9-799]():

#### Phase 1: Detect Project State

Determines whether this is a new project, existing project with Claude setup, or existing codebase without Claude.

**Detection Logic:**
- Checks for `.claude/skills/` directory
- Checks for `CLAUDE.md` file
- Checks for `_project_specs/` directory
- Checks for git remote configuration
- Checks for `package.json` or `pyproject.toml`

**Outcomes:**
- New project: Full setup
- Existing with skills: Update mode (preserves customizations)
- Existing codebase: Add mode (preserves code)

Sources: [commands/initialize-project.md:9-35]()

#### Phase 2: Validate CLI Tools

Verifies authentication status of required CLIs:

```bash
# GitHub CLI check
gh auth status

# Vercel CLI check
vercel whoami

# Supabase CLI check
supabase projects list
```

If tools are missing or unauthenticated, offers to skip or provides installation instructions.

Sources: [commands/initialize-project.md:37-57]()

#### Phase 3: Interactive Project Questions

Collects project configuration through sequential questions:

| Question | Purpose | Auto-Detection |
|----------|---------|----------------|
| What are you building? | Project description | Reads existing `CLAUDE.md` |
| Language/runtime? | Determines skill files | Checks `package.json`, `pyproject.toml` |
| Project type? | Selects framework skills | Analyzes dependencies |
| AI-first application? | Loads LLM skills | Checks for `anthropic`, `openai` packages |
| Framework? | Framework-specific patterns | Dependency analysis |
| Database? | Database integration | Checks for `supabase/` directory |
| Deployment platform? | CI/CD configuration | Checks for `vercel.json`, `render.yaml` |
| Repository setup? | GitHub integration | Checks `git remote -v` |

Sources: [commands/initialize-project.md:60-130]()

#### Phase 4: Execute Setup

Creates directory structure and installs configuration files:

**Directory Structure Created:**
```
.claude/skills/          # Skill files
docs/                    # Documentation
_project_specs/
  ├── features/          # Feature specifications
  ├── todos/             # Active, backlog, completed
  ├── prompts/           # Prompt templates
  └── session/           # Session state management
      └── archive/       # Historical sessions
scripts/                 # Utility scripts
```

**Skills Installation Logic:**

```mermaid
graph TB
    GLOBAL["~/.claude/skills/<br/>Global Repository"]
    
    subgraph "Always Copied (Overwritten)"
        CORE["base.md<br/>security.md<br/>project-tooling.md<br/>session-management.md"]
    end
    
    subgraph "Conditional by Language"
        PYTHON["python.md"]
        TYPESCRIPT["typescript.md"]
    end
    
    subgraph "Conditional by Project Type"
        REACT_NATIVE["typescript.md +<br/>react-native.md"]
        REACT_WEB["typescript.md +<br/>react-web.md"]
        NODE_BACKEND["typescript.md +<br/>nodejs-backend.md"]
        FULLSTACK["typescript.md +<br/>nodejs-backend.md +<br/>react-web.md"]
    end
    
    subgraph "Conditional by Flags"
        AI_FIRST["llm-patterns.md<br/>agentic-development.md<br/>ai-models.md"]
    end
    
    PROJECT[".claude/skills/<br/>Project Directory"]
    
    GLOBAL --> CORE
    GLOBAL --> PYTHON
    GLOBAL --> TYPESCRIPT
    GLOBAL --> REACT_NATIVE
    GLOBAL --> REACT_WEB
    GLOBAL --> NODE_BACKEND
    GLOBAL --> FULLSTACK
    GLOBAL --> AI_FIRST
    
    CORE --> PROJECT
    PYTHON --> PROJECT
    TYPESCRIPT --> PROJECT
    REACT_NATIVE --> PROJECT
    REACT_WEB --> PROJECT
    NODE_BACKEND --> PROJECT
    FULLSTACK --> PROJECT
    AI_FIRST --> PROJECT
```

**Key Files Generated:**

| File | Purpose | Overwrite Behavior |
|------|---------|-------------------|
| `CLAUDE.md` | Main instruction file | Preserves customizations if exists |
| `.gitignore` | Security-critical entries | Appends missing entries |
| `.env.example` | Environment template | Creates if missing |
| `scripts/verify-tooling.sh` | CLI validation | Always overwrites |
| `scripts/security-check.sh` | Pre-commit security | Always overwrites |
| `.github/workflows/quality.yml` | CI/CD quality gates | Creates based on language |
| `.github/workflows/security.yml` | Security scanning | Always creates |

Sources: [commands/initialize-project.md:132-669]()

#### Phase 5: Post-Setup Actions

**GitHub Repository Setup:**
- Creates new repository via `gh repo create` if requested
- Connects to existing repository via `git remote add`

**Deployment Initialization:**
- Vercel: Runs `vercel link` if `vercel.json` missing
- Supabase: Runs `supabase init` if `supabase/` missing

**Hook Installation:**
Pre-push code review hook installed to `.git/hooks/pre-push` from [~/.claude/hooks/pre-push]().

Sources: [commands/initialize-project.md:699-726]()

### Output Summary

**For New Projects:**
```
Created:
✓ .claude/skills/ with 5 skill files
✓ CLAUDE.md
✓ _project_specs/ structure
✓ scripts/verify-tooling.sh
✓ .github/workflows/quality.yml
✓ Pre-commit hooks configured
✓ Pre-push code review hook (blocks on Critical/High issues)
✓ GitHub repository: https://github.com/[owner]/[repo]
```

**For Updates:**
```
Updated:
✓ Skills updated to latest versions
✓ Pre-push code review hook (installed/updated)

Added:
✓ llm-patterns.md (new skill added)

Unchanged:
- CLAUDE.md (preserved your customizations)
- _project_specs/todos/ (preserved your todos)
```

Sources: [commands/initialize-project.md:729-763]()

### State Management

The command reads and preserves existing state from:
- `CLAUDE.md`: Project-specific patterns and tech stack
- `_project_specs/todos/`: All todo files (active, backlog, completed)
- `_project_specs/session/`: Session state and decisions
- `.git/config`: Repository configuration

Sources: [commands/initialize-project.md:320-438]()

---

## /check-contributors

**Purpose:** Team coordination for multi-developer Claude Code projects. Detects team vs. solo projects and manages shared state.

### Syntax

```bash
/check-contributors                # Interactive mode
/check-contributors --status       # Quick status only
/check-contributors --team         # Convert to team project
```

### Behavior

**Solo Project Detection:**
- No `_project_specs/team/` directory exists
- Offers to convert to team project structure

**Team Project Detection:**
- `_project_specs/team/state.md` exists
- Displays current team state

### Team State Structure

When converting to team project, creates:

```
_project_specs/team/
├── state.md           # Active sessions, claimed todos, conflicts
├── contributors.md    # Team roster, ownership, focus areas
└── handoffs/          # Context transfer notes
```

### State File Format

**state.md Schema:**

| Section | Content |
|---------|---------|
| Active Sessions | Who is working right now, on which files |
| Claimed Todos | Reserved work items (prevents duplication) |
| File Conflicts | Warning when multiple devs edit same files |
| Last Updated | Timestamp for staleness detection |

**contributors.md Schema:**

| Section | Content |
|---------|---------|
| Team Members | Name, contact, timezone |
| Ownership Areas | Primary responsibility assignments |
| Focus Areas | Current focus per developer |

Sources: [README.md:211-253]()

### Team Coordination Workflow

```mermaid
stateDiagram-v2
    [*] --> GitPull: "Start Session"
    
    GitPull --> CheckContributors: "/check-contributors"
    
    CheckContributors --> ReadState: "Read state.md"
    
    ReadState --> CheckConflicts: "Analyze claimed todos<br/>and active files"
    
    CheckConflicts --> Warning: "Conflict detected:<br/>Multiple devs same area"
    CheckConflicts --> ClaimTodo: "No conflicts"
    
    Warning --> ResolveConflict: "Coordinate with team"
    ResolveConflict --> ClaimTodo
    
    ClaimTodo --> UpdateState: "Update state.md:<br/>Claim todo + files"
    
    UpdateState --> Work: "Active development"
    
    Work --> Checkpoint: "Periodic updates<br/>(every N tool calls)"
    
    Checkpoint --> UpdateState2: "Update state.md:<br/>Progress, files touched"
    
    UpdateState2 --> Work
    
    Work --> Complete: "Todo finished"
    
    Complete --> UpdateStateComplete: "Update state.md:<br/>Release claim"
    
    UpdateStateComplete --> GitPush: "git push"
    
    GitPush --> [*]
```

Sources: [README.md:232-246]()

### Conflict Detection

The command detects conflicts by analyzing:
- **Todo conflicts:** Same todo claimed by multiple developers
- **File conflicts:** Same file being modified by multiple active sessions
- **Stale state:** `state.md` not updated in > 4 hours (warns of potentially stale data)

Sources: [README.md:236-240]()

---

## /code-review

**Purpose:** Automated code review analysis that blocks pushes on Critical/High severity issues. Enforces security, performance, and architecture standards.

### Syntax

```bash
/code-review
```

No options. Analyzes all uncommitted changes via `git diff`.

### Integration Points

**Pre-Push Hook:**
Automatically invoked by `.git/hooks/pre-push` installed via [commands/initialize-project.md:676-698]().

**CI/CD:**
Referenced in GitHub Actions workflows for remote validation.

### Severity Classification

| Severity | Symbol | Action | Push Allowed? |
|----------|--------|--------|---------------|
| Critical | 🔴 | Must fix immediately | ❌ BLOCKED |
| High | 🟠 | Must fix immediately | ❌ BLOCKED |
| Medium | 🟡 | Fix soon | ✅ Advisory |
| Low | 🟢 | Nice to have | ✅ Advisory |

Sources: [README.md:194-201]()

### Analysis Categories

The command analyzes code across multiple dimensions:

```mermaid
graph LR
    DIFF["git diff<br/>(staged + unstaged)"]
    
    subgraph "Analysis Dimensions"
        SEC["Security Analysis"]
        PERF["Performance Analysis"]
        ARCH["Architecture Analysis"]
        QUALITY["Code Quality"]
    end
    
    subgraph "Security Checks"
        SEC1["SQL Injection"]
        SEC2["XSS Vulnerabilities"]
        SEC3["Hardcoded Secrets"]
        SEC4["Client-Exposed Secrets<br/>(VITE_*, NEXT_PUBLIC_*)"]
    end
    
    subgraph "Performance Checks"
        PERF1["N+1 Queries"]
        PERF2["Memory Leaks"]
        PERF3["Inefficient Algorithms"]
    end
    
    subgraph "Architecture Checks"
        ARCH1["Tight Coupling"]
        ARCH2["SOLID Violations"]
        ARCH3["Separation of Concerns"]
    end
    
    subgraph "Quality Checks"
        QUAL1["Complexity Violations<br/>(>20 lines/function)"]
        QUAL2["Code Duplication"]
        QUAL3["Missing Types"]
    end
    
    DIFF --> SEC
    DIFF --> PERF
    DIFF --> ARCH
    DIFF --> QUALITY
    
    SEC --> SEC1
    SEC --> SEC2
    SEC --> SEC3
    SEC --> SEC4
    
    PERF --> PERF1
    PERF --> PERF2
    PERF --> PERF3
    
    ARCH --> ARCH1
    ARCH --> ARCH2
    ARCH --> ARCH3
    
    QUALITY --> QUAL1
    QUALITY --> QUAL2
    QUALITY --> QUAL3
```

Sources: [README.md:203-207]()

### Blocking Behavior

**When Critical/High Issues Found:**
```bash
# Pre-push hook behavior
.git/hooks/pre-push  # Runs /code-review
# If Critical/High found:
# - Displays issues
# - Exits with code 1
# - Push cancelled
```

**Exit Codes:**
- `0`: No Critical/High issues (push allowed)
- `1`: Critical/High issues found (push blocked)

Sources: [README.md:176-209]()

### Output Format

```
Code Review Results
===================

🔴 CRITICAL: SQL injection vulnerability
  File: src/api/users.ts:42
  Issue: Unparameterized query with user input
  Fix: Use parameterized queries or ORM

🟠 HIGH: Performance issue
  File: src/services/orders.ts:78
  Issue: N+1 query in loop (fetches user per order)
  Fix: Use JOIN or batch loading

🟡 MEDIUM: Code complexity
  File: src/utils/validator.ts:12
  Issue: Function exceeds 20 line limit (currently 35)
  Fix: Split into smaller functions

Push BLOCKED due to 1 Critical and 1 High severity issue(s)
```

Sources: [README.md:176-209]()

---

## /update-code-index

**Purpose:** Regenerates `CODE_INDEX.md` semantic capability index to prevent duplicate code creation.

### Syntax

```bash
/update-code-index
```

No options. Scans entire codebase.

### Indexing Logic

**Capability Organization:**
Functions are grouped by what they DO, not where they are:

```markdown
## Validation
| Function | Location | Does What |
|----------|----------|-----------|
| `isEmail()` | utils/validate.ts | Validates email format |
| `isPhone()` | utils/validate.ts | Validates phone number |

## Date/Time
| Function | Location | Does What |
|----------|----------|-----------|
| `formatRelative()` | utils/dates.ts | "2 days ago" format |
| `parseISODate()` | utils/dates.ts | Parse ISO 8601 strings |
```

**Semantic Categories:**
- Validation
- Date/Time manipulation
- String formatting
- Data transformation
- HTTP requests
- Database queries
- Authentication/Authorization
- File operations

Sources: [README.md:255-294]()

### Workflow Integration

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Claude as "Claude Code"
    participant Index as "CODE_INDEX.md"
    participant Code as "Codebase"
    
    Dev->>Claude: "Add email validation"
    Claude->>Index: "Search for validation<br/>capabilities"
    
    alt "Existing function found"
        Index-->>Claude: "Found: isEmail() at<br/>utils/validate.ts"
        Claude->>Code: "Use isEmail()"
        Claude-->>Dev: "Using existing isEmail()<br/>function"
    else "No existing function"
        Index-->>Claude: "No email validation<br/>found"
        Claude->>Code: "Create new<br/>validateEmail()"
        Claude->>Index: "Update CODE_INDEX.md"
        Claude-->>Dev: "Created validateEmail()<br/>and updated index"
    end
```

Sources: [README.md:255-294]()

### Large Codebase Optimization

For projects with 100+ files, optional vector database integration:

**Supported Backends:**
- ChromaDB
- LanceDB

**Query Flow:**
1. Convert capability description to embedding
2. Semantic search in vector DB
3. Return top-K similar functions
4. Claude evaluates relevance

Sources: [README.md:294]()

---

## /ralph-loop

**Purpose:** Iterative TDD execution engine that runs autonomous RED-GREEN-VALIDATE cycles until tests pass or max iterations reached.

### Syntax

```bash
/ralph-loop --max-iterations 20 --completion-promise "DONE"
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--max-iterations` | 20 | Maximum loop iterations before exit |
| `--completion-promise` | "DONE" | String to output when complete |

### Execution Flow

The Ralph loop implements a state machine with error classification:

```mermaid
stateDiagram-v2
    [*] --> Initialize: "/ralph-loop<br/>--max-iterations 20"
    
    Initialize --> ReadState: "Load git history<br/>and file state"
    
    ReadState --> WriteTests: "TDD: RED Phase"
    
    WriteTests --> RunTests1: "Execute tests"
    
    RunTests1 --> VerifyRed: "All tests fail?"
    
    VerifyRed --> FixTests: "Tests pass<br/>(should fail first)"
    VerifyRed --> Implement: "Tests fail ✓<br/>RED confirmed"
    
    FixTests --> WriteTests: "Rewrite tests<br/>to fail properly"
    
    Implement --> RunTests2: "TDD: GREEN Phase"
    
    RunTests2 --> ClassifyError: "Some tests fail"
    RunTests2 --> Validate: "All tests pass ✓"
    
    ClassifyError --> CheckType: "Determine error type"
    
    CheckType --> Implement: "Code/Type/Logic<br/>(Fixable)"
    CheckType --> BlockerReport: "Access/Network/Env<br/>(Unfixable)"
    
    Validate --> RunLint: "TDD: VALIDATE"
    
    RunLint --> RunCoverage: "Lint + TypeCheck ✓"
    
    RunCoverage --> CheckCoverage: "Coverage ≥ 80%?"
    
    CheckCoverage --> AddTests: "Coverage < 80%"
    CheckCoverage --> Complete: "Coverage ≥ 80% ✓"
    
    AddTests --> RunTests2
    
    Complete --> UpdateTodo: "Mark todo complete<br/>active.md → completed.md"
    
    UpdateTodo --> CheckPromise: "Output completion<br/>promise?"
    
    CheckPromise --> Success: "Yes →<br/><promise>DONE</promise>"
    CheckPromise --> CheckMax: "No"
    
    CheckMax --> MaxReached: "iterations ≥ max"
    CheckMax --> ReadState: "iterations < max<br/>Feed SAME PROMPT"
    
    MaxReached --> [*]: "Exit: Incomplete"
    
    BlockerReport --> [*]: "Exit: BLOCKER REPORT<br/>Human action required"
    
    Success --> [*]: "Exit: Success ✓"
```

Sources: [README.md:71-118](), Diagram 4 in system overview

### Stop Hook Mechanism

**Key Innovation:** The prompt NEVER changes. Only the file state evolves through git commits and modifications.

**Mechanism:**
1. Claude attempts to exit (signal completion or give up)
2. Stop hook intercepts the exit
3. Same prompt fed back to Claude
4. Claude sees updated file state (its own previous work)
5. Self-referential improvement loop continues

**Termination Conditions:**
- Completion promise output: `<promise>DONE</promise>`
- Max iterations reached
- Unfixable blocker detected

Sources: Diagram 4 in system overview, [README.md:71-94]()

### Error Classification

The loop distinguishes between fixable and unfixable errors:

| Error Type | Examples | Claude Fixes? | Action |
|------------|----------|---------------|--------|
| Code Error | Logic bug, wrong assertion, type mismatch | ✅ Yes | Continue loop |
| Type Error | TypeScript type errors | ✅ Yes | Continue loop |
| Test Error | Wrong test expectation | ✅ Yes | Continue loop |
| Access Error | Missing API key, DB connection refused | ❌ No | Stop + report |
| Network Error | Service unavailable, DNS failure | ❌ No | Stop + report |
| Environment Error | Missing package, wrong Node version | ❌ No | Stop + report |

**Blocker Report Format:**
```
🛑 LOOP BLOCKED - Human Action Required

Error: ECONNREFUSED 127.0.0.1:5432

Classification: Access Error (Database)

Required Actions:
1. Start PostgreSQL: brew services start postgresql
2. Verify connection: psql -U postgres -c "SELECT 1"
3. Check DATABASE_URL in .env

After fixing, run /ralph-loop again.
```

Sources: [README.md:579-612]()

### Automatic Invocation

With Claude Bootstrap skills loaded, Ralph loops are invoked automatically for most development requests:

**Triggers:**
- "Add [feature]"
- "Fix [bug]"
- "Implement [functionality]"
- "Build [component]"

**Opt-Out Phrases:**
- "Just explain..."
- "Quick fix..."
- "Don't loop..."

Sources: [README.md:73-99]()

---

## /cancel-ralph

**Purpose:** Stop an active Ralph loop iteration.

### Syntax

```bash
/cancel-ralph
```

No options.

### Behavior

- Terminates current loop immediately
- Does not rollback changes (git state preserved)
- Outputs current loop iteration count
- Safe to run - no data loss

**Use Cases:**
- Loop stuck on unfixable issue
- Wrong completion criteria specified
- Need to modify approach before continuing

Sources: [README.md:62]()

---

## /audit-duplicates

**Purpose:** Find semantic code duplication (functions with similar purpose but different names/implementations).

### Syntax

```bash
/audit-duplicates
```

No options. Scans entire codebase.

### Detection Logic

**Semantic Similarity Analysis:**
1. Parse all function signatures and bodies
2. Extract semantic purpose from:
   - Function name
   - Parameter names
   - Return type
   - Comments/docstrings
3. Compare purposes using embeddings (if vector DB available) or pattern matching
4. Report functions with >80% semantic similarity

**Output Format:**
```
Potential Duplicate Functions
==============================

Group 1: Email Validation
  - isValidEmail() at utils/validate.ts:12
  - validateEmail() at services/auth.ts:45
  - checkEmailFormat() at api/users.ts:78
  Recommendation: Keep isValidEmail(), remove others

Group 2: Date Formatting
  - formatDate() at utils/dates.ts:23
  - dateToString() at components/DatePicker.tsx:102
  Recommendation: Keep formatDate(), remove dateToString()
```

Sources: [README.md:255-294]()

### Merge Recommendations

For each duplicate group, provides:
- Which function to keep (most comprehensive, best named)
- Which functions to remove
- Required refactoring (update call sites)

---

## Command File Structure

All commands follow a standardized markdown format:

```markdown
# Command Name

Brief description and purpose.

---

## Phase 1: [Phase Name]

Description of phase behavior.

### Code blocks
```bash
# Command examples
```

### Sub-sections
Detailed specifications.

---

## Phase 2: [Phase Name]

...
```

**Common Sections:**
- Purpose statement
- Syntax/options
- Execution phases
- Output format
- Error handling
- Integration points

Sources: [commands/initialize-project.md:1-821]()

---

## Command Execution Context

Commands execute within Claude Code's environment with access to:

**Environment Variables:**
- `HOME`: User home directory
- `PWD`: Current working directory
- Git environment variables (when in repository)

**Filesystem Access:**
- Read: Entire project directory
- Write: Project directory (not `~/.claude/`)
- Execute: Shell commands via subprocess

**Git Integration:**
- Can execute `git` commands
- Access to `git diff`, `git log`, `git status`
- Can modify `.git/hooks/`

Sources: [commands/initialize-project.md:13-24](), [install.sh:1-66]()

---

## Error Handling Patterns

All commands implement consistent error handling:

**CLI Tool Validation:**
```bash
# Pattern used across commands
if command -v gh &> /dev/null; then
  if gh auth status &> /dev/null; then
    echo "✓ GitHub CLI authenticated"
  else
    echo "✗ GitHub CLI not authenticated. Run: gh auth login"
    exit 1
  fi
else
  echo "⚠ GitHub CLI not installed. Run: brew install gh"
fi
```

**Graceful Degradation:**
- Missing optional tools: Warn and continue
- Missing required tools: Error and stop
- Invalid configuration: Prompt for correction

Sources: [commands/initialize-project.md:40-57](), [commands/initialize-project.md:216-263]()

---

## Command Interaction Matrix

Some commands depend on or complement each other:

```mermaid
graph TB
    INIT["/initialize-project"]
    CHECK["/check-contributors"]
    REVIEW["/code-review"]
    INDEX["/update-code-index"]
    RALPH["/ralph-loop"]
    CANCEL["/cancel-ralph"]
    AUDIT["/audit-duplicates"]
    
    INIT -->|"Creates .git/hooks/pre-push"| REVIEW
    INIT -->|"Creates _project_specs/team/"| CHECK
    INIT -->|"Creates CODE_INDEX.md"| INDEX
    
    RALPH -->|"Can be stopped by"| CANCEL
    RALPH -->|"Updates todos in"| INIT
    
    INDEX -->|"Prevents duplication found by"| AUDIT
    
    CHECK -->|"Reads state created by"| INIT
    
    REVIEW -->|"Validates code from"| RALPH
```

**Dependencies:**
- `/check-contributors` requires `/initialize-project` to have run (creates team structure)
- `/code-review` is installed by `/initialize-project` as pre-push hook
- `/update-code-index` operates on structure created by `/initialize-project`
- `/cancel-ralph` only works when `/ralph-loop` is running

Sources: [README.md:52-62](), [commands/initialize-project.md:676-698]()

---

# Page: Configuration and Project Structure

# Configuration and Project Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [commands/initialize-project.md](commands/initialize-project.md)
- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



This document provides a technical reference for all configuration files and directory structures created by Claude Bootstrap. It covers the format specifications, file locations, and relationships between configuration components.

For information about how to extend these configurations with custom skills, see [Extending Claude Bootstrap](#9.3). For information about the commands that create and modify these structures, see [Commands Reference](#9.1).

---

## Directory Structure Overview

Claude Bootstrap creates a standardized directory structure that separates code documentation, project specifications, session state, and configuration files.

**Complete Project Structure**

```mermaid
graph TB
    ROOT["project-root/"]
    
    subgraph "Claude Configuration"
        CLAUDE_DIR[".claude/"]
        SKILLS[".claude/skills/"]
        SKILL_BASE["base.md"]
        SKILL_SEC["security.md"]
        SKILL_LANG["[language].md"]
        SKILL_FW["[framework].md"]
    end
    
    subgraph "Project Specifications"
        SPECS["_project_specs/"]
        OVERVIEW["overview.md"]
        FEATURES["features/"]
        TODOS["todos/"]
        TODO_ACTIVE["active.md"]
        TODO_BACKLOG["backlog.md"]
        TODO_COMPLETE["completed.md"]
        SESSION["session/"]
        CURR_STATE["current-state.md"]
        DECISIONS["decisions.md"]
        LANDMARKS["code-landmarks.md"]
        ARCHIVE["archive/"]
        PROMPTS["prompts/"]
        TEAM["team/"]
    end
    
    subgraph "Code Documentation"
        DOCS["docs/"]
        ARCH["architecture.md"]
        API["api.md"]
        SETUP["setup.md"]
    end
    
    subgraph "Scripts"
        SCRIPTS["scripts/"]
        VERIFY["verify-tooling.sh"]
        SECURITY["security-check.sh"]
    end
    
    subgraph "CI/CD"
        GITHUB[".github/"]
        WORKFLOWS["workflows/"]
        QUALITY["quality.yml"]
        SEC_WF["security.yml"]
    end
    
    subgraph "Configuration Files"
        CLAUDE_MD["CLAUDE.md"]
        GITIGNORE[".gitignore"]
        ENV_EXAMPLE[".env.example"]
    end
    
    ROOT --> CLAUDE_DIR
    ROOT --> SPECS
    ROOT --> DOCS
    ROOT --> SCRIPTS
    ROOT --> GITHUB
    ROOT --> CLAUDE_MD
    ROOT --> GITIGNORE
    ROOT --> ENV_EXAMPLE
    
    CLAUDE_DIR --> SKILLS
    SKILLS --> SKILL_BASE
    SKILLS --> SKILL_SEC
    SKILLS --> SKILL_LANG
    SKILLS --> SKILL_FW
    
    SPECS --> OVERVIEW
    SPECS --> FEATURES
    SPECS --> TODOS
    SPECS --> SESSION
    SPECS --> PROMPTS
    SPECS --> TEAM
    
    TODOS --> TODO_ACTIVE
    TODOS --> TODO_BACKLOG
    TODOS --> TODO_COMPLETE
    
    SESSION --> CURR_STATE
    SESSION --> DECISIONS
    SESSION --> LANDMARKS
    SESSION --> ARCHIVE
    
    DOCS --> ARCH
    DOCS --> API
    DOCS --> SETUP
    
    SCRIPTS --> VERIFY
    SCRIPTS --> SECURITY
    
    GITHUB --> WORKFLOWS
    WORKFLOWS --> QUALITY
    WORKFLOWS --> SEC_WF
```

Sources: [commands/initialize-project.md:134-143](), [skills/base.md:99-135]()

---

## CLAUDE.md - Project Instructions

`CLAUDE.md` is the primary configuration file that Claude reads to understand project-specific context. It references skills, defines the tech stack, and specifies default behavior.

**File Location**: `CLAUDE.md` (project root)

**CLAUDE.md Structure Mapping**

```mermaid
graph LR
    CLAUDE_MD["CLAUDE.md"]
    
    subgraph "Skills Section"
        SKILLS_REF["Skills Loaded<br/>- base.md<br/>- security.md<br/>- [language].md"]
        SKILLS_DIR[".claude/skills/"]
    end
    
    subgraph "Behavior Section"
        AUTO_ITER["Default Behavior:<br/>Automatic Iterative TDD"]
        RALPH["Auto-invoke /ralph-loop"]
        OPT_OUT["Opt-out phrases"]
    end
    
    subgraph "Project Context"
        TECH_STACK["Tech Stack<br/>Language, Framework, DB"]
        COMMANDS["Commands<br/>test, lint, typecheck"]
        SCHEMA["Schema Location"]
    end
    
    subgraph "Quality Section"
        CONSTRAINTS["Quality Gates<br/>20 lines/function<br/>200 lines/file<br/>80% coverage"]
    end
    
    subgraph "Session Section"
        PERSISTENCE["Session Persistence<br/>Checkpoint triggers<br/>Decision logging"]
    end
    
    CLAUDE_MD --> SKILLS_REF
    SKILLS_REF --> SKILLS_DIR
    CLAUDE_MD --> AUTO_ITER
    AUTO_ITER --> RALPH
    AUTO_ITER --> OPT_OUT
    CLAUDE_MD --> TECH_STACK
    TECH_STACK --> COMMANDS
    TECH_STACK --> SCHEMA
    CLAUDE_MD --> CONSTRAINTS
    CLAUDE_MD --> PERSISTENCE
```

Sources: [templates/CLAUDE.md:1-113]()

### CLAUDE.md Format Specification

| Section | Required | Format | Purpose |
|---------|----------|--------|---------|
| Skills Loaded | Yes | Bulleted list of `.claude/skills/*.md` files | References which skills apply to this project |
| Default Behavior | Yes | Markdown with code examples | Defines automatic Ralph loop invocation rules |
| Tech Stack | Yes | Key-value pairs | Specifies language, framework, database, testing tools |
| Commands | Yes | Code block with shell commands | Documents how to run tests, lint, typecheck, etc. |
| Quality Gates | Yes | Table | Enforces complexity limits and coverage thresholds |
| Session Persistence | Yes | Bulleted list | Checkpoint triggers and state management rules |
| Project-Specific Context | Optional | Freeform markdown | Custom patterns, gotchas, or deviations |

Sources: [templates/CLAUDE.md:1-113](), [commands/initialize-project.md:320-438]()

### Skills References in CLAUDE.md

The skills section lists which skill files from `.claude/skills/` apply to the current project:

```markdown
## Skills Loaded
- base.md (TDD workflow, atomic todos, simplicity rules)
- iterative-development.md (Ralph Wiggum loops)
- security.md (OWASP patterns, secrets management)
- typescript.md (TypeScript strict + eslint + jest)
- react-web.md (React + hooks + React Query)
```

**Skill Selection Logic**: During `/initialize-project`, skills are copied from `~/.claude/skills/` to `.claude/skills/` based on project type. Core skills (base, security, session-management, project-tooling) are always included. Language and framework skills are conditionally included.

Sources: [commands/initialize-project.md:146-166](), [templates/CLAUDE.md:3-6]()

---

## _project_specs/ Directory Structure

The `_project_specs/` directory contains all project specifications, feature definitions, todos, and session state. It is separated from code documentation in `docs/`.

**_project_specs/ Organization**

```mermaid
graph TB
    SPECS["_project_specs/"]
    
    subgraph "Project Definition"
        OVERVIEW["overview.md<br/>Vision, Goals, Success Metrics"]
    end
    
    subgraph "Feature Specifications"
        FEATURES["features/<br/>One file per feature"]
        FEAT_A["feature-auth.md"]
        FEAT_B["feature-payments.md"]
    end
    
    subgraph "Todo Tracking"
        TODOS["todos/"]
        ACTIVE["active.md<br/>Current work"]
        BACKLOG["backlog.md<br/>Future work"]
        COMPLETED["completed.md<br/>Done items"]
    end
    
    subgraph "Session State"
        SESSION["session/"]
        CURRENT["current-state.md<br/>Live session state"]
        DECISIONS["decisions.md<br/>Append-only log"]
        LANDMARKS["code-landmarks.md<br/>Code navigation"]
        ARCHIVE["archive/<br/>Past sessions"]
    end
    
    subgraph "AI-First Projects"
        PROMPTS["prompts/<br/>LLM prompt specs"]
    end
    
    subgraph "Team Coordination"
        TEAM["team/<br/>Multi-person state"]
        STATE["state.md"]
        CONTRIB["contributors.md"]
        HANDOFFS["handoffs/"]
    end
    
    SPECS --> OVERVIEW
    SPECS --> FEATURES
    SPECS --> TODOS
    SPECS --> SESSION
    SPECS --> PROMPTS
    SPECS --> TEAM
    
    FEATURES --> FEAT_A
    FEATURES --> FEAT_B
    
    TODOS --> ACTIVE
    TODOS --> BACKLOG
    TODOS --> COMPLETED
    
    SESSION --> CURRENT
    SESSION --> DECISIONS
    SESSION --> LANDMARKS
    SESSION --> ARCHIVE
    
    TEAM --> STATE
    TEAM --> CONTRIB
    TEAM --> HANDOFFS
```

Sources: [skills/base.md:99-135](), [commands/initialize-project.md:136-143]()

### overview.md

**File Location**: `_project_specs/overview.md`

Defines high-level project vision, goals, non-goals, and success metrics.

**Format**:
```markdown
# Project Overview

## Vision
[1-2 paragraph description of what this project is and why it exists]

## Goals
- [ ] Goal 1 - specific, measurable
- [ ] Goal 2 - specific, measurable

## Non-Goals
- What this project will NOT do
- Scope boundaries

## Success Metrics
- How we measure success
- KPIs or acceptance criteria
```

Sources: [commands/initialize-project.md:444-460]()

### features/

**Directory Location**: `_project_specs/features/`

Contains one markdown file per feature with detailed specifications, acceptance criteria, and design notes.

**Naming Convention**: `feature-[name].md` (e.g., `feature-authentication.md`, `feature-payment-processing.md`)

**Typical Feature Spec Format**:
```markdown
# Feature: [Name]

## Description
[What this feature does]

## User Stories
- As a [user type], I want [goal] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Approach
[High-level design, APIs, data models]

## Security Considerations
[Any security-specific requirements]

## Testing Strategy
[How this feature will be tested]
```

Sources: [skills/base.md:110-116]()

### todos/ - Atomic Work Units

**Directory Location**: `_project_specs/todos/`

Tracks all work as atomic, testable units following the TDD workflow. Contains three files:

| File | Purpose | Workflow |
|------|---------|----------|
| `active.md` | Current sprint/work in progress | Move items here from backlog when starting work |
| `backlog.md` | Future work, prioritized | Add new todos here, prioritize by importance |
| `completed.md` | Done items for reference | Move from active.md when TDD execution log shows COMPLETE |

Sources: [skills/base.md:114-120](), [commands/initialize-project.md:462-493]()

**Atomic Todo Format**

Every todo must follow this exact format to ensure testability and TDD compliance:

```markdown
## [TODO-042] Add email validation to signup form

**Status:** pending | in-progress | blocked | done
**Priority:** high | medium | low
**Estimate:** XS | S | M | L | XL

### Description
[One paragraph describing what needs to be done]

### Acceptance Criteria
- [ ] Criterion 1 - specific, measurable
- [ ] Criterion 2 - specific, measurable

### Validation
How to verify this is complete:
- Manual: [steps to manually test]
- Automated: [test file/command that validates this]

### Test Cases
| Input | Expected Output | Notes |
|-------|-----------------|-------|
| user@example.com | Valid, no error | Standard email |
| notanemail | Invalid, show error | No @ symbol |

### Dependencies
- Depends on: [TODO-041]
- Blocks: [TODO-045]

### TDD Execution Log
| Phase | Command | Result | Timestamp |
|-------|---------|--------|-----------|
| RED | `npm test -- --grep "email validation"` | 5 tests failed ✓ | 2024-01-15 10:30 |
| GREEN | `npm test -- --grep "email validation"` | 5 tests passed ✓ | 2024-01-15 11:15 |
| VALIDATE | `npm run lint && npm run typecheck && npm test -- --coverage` | Pass, 84% ✓ | 2024-01-15 11:20 |
| COMPLETE | Moved to completed.md | ✓ | 2024-01-15 11:22 |
```

Sources: [skills/base.md:138-384]()

**Todo Status Transitions**

```mermaid
stateDiagram-v2
    [*] --> backlog: "New todo created"
    backlog --> active: "Start work"
    active --> in_progress: "Begin TDD workflow"
    in_progress --> in_progress: "RED → GREEN → VALIDATE loop"
    in_progress --> blocked: "Access/Environment error"
    blocked --> in_progress: "Blocker resolved"
    in_progress --> done: "All validations pass"
    done --> completed_md: "Move to completed.md"
    completed_md --> [*]
```

Sources: [skills/base.md:180-214]()

### session/ - Context Preservation

**Directory Location**: `_project_specs/session/`

Maintains session state for resumability across context windows and work sessions.

**Session Files**

| File | Update Frequency | Purpose |
|------|------------------|---------|
| `current-state.md` | After every todo completion or ~20 tool calls | Live session state, current task, next steps |
| `decisions.md` | When making architectural choices | Append-only log of key decisions with rationale |
| `code-landmarks.md` | When adding entry points or patterns | Quick reference to important code locations |
| `archive/` | End of major features or sessions | Past session summaries, archived context |

Sources: [skills/base.md:116-122](), [commands/initialize-project.md:495-617]()

#### current-state.md Format

**File Location**: `_project_specs/session/current-state.md`

```markdown
<!--
CHECKPOINT RULES (from session-management.md):
- Quick update: After any todo completion
- Full checkpoint: After ~20 tool calls or decisions
- Archive: End of session or major feature complete
-->

# Current Session State

*Last updated: 2024-01-15 14:30*

## Active Task
[One sentence describing current work]

## Current Status
- **Phase**: exploring | planning | implementing | testing | debugging
- **Progress**: [X of Y steps, or description]
- **Blocking Issues**: None

## Context Summary
[2-3 sentences summarizing current state of work]

## Files Being Modified
| File | Status | Notes |
|------|--------|-------|
| src/auth/validate.ts | In progress | Adding email validation |
| src/auth/validate.test.ts | Complete | Tests written, passing |

## Next Steps
1. [ ] Run full validation suite
2. [ ] Update CLAUDE.md with validation patterns
3. [ ] Move TODO-042 to completed.md

## Key Context to Preserve
- Email validation uses Zod schema from src/schemas/user.ts
- Tests cover 5 edge cases per acceptance criteria

## Resume Instructions
To continue this work:
1. Read src/auth/validate.test.ts to see test coverage
2. Verify all tests pass with `npm test -- --grep "email validation"`
3. If passing, proceed to next todo in active.md
```

Sources: [commands/initialize-project.md:495-537]()

#### decisions.md Format

**File Location**: `_project_specs/session/decisions.md`

Append-only log of architectural and implementation decisions.

```markdown
<!--
LOG DECISIONS WHEN:
- Choosing between architectural approaches
- Selecting libraries or tools
- Making security-related choices
- Deviating from standard patterns
-->

# Decision Log

## [2024-01-15] Use Zod for input validation instead of custom validators

**Decision**: Adopt Zod library for all input validation
**Context**: Need runtime validation for API inputs and form data
**Options Considered**: 
- Custom validators (manual type guards)
- Joi (callback-based)
- Zod (TypeScript-first)
**Choice**: Zod
**Reasoning**: 
- Automatic TypeScript type inference from schemas
- Composable validators reduce duplication
- Better error messages out of box
**Trade-offs**: 
- Additional dependency (~8kb)
- Team needs to learn Zod syntax
**References**: src/schemas/user.ts, src/schemas/product.ts
```

Sources: [commands/initialize-project.md:539-571]()

#### code-landmarks.md Format

**File Location**: `_project_specs/session/code-landmarks.md`

Quick reference for navigating the codebase when resuming work.

```markdown
# Code Landmarks

## Entry Points
| Location | Purpose |
|----------|---------|
| src/index.ts | Main application entry (Express server) |
| src/cli.ts | CLI tool entry point |

## Core Business Logic
| Location | Purpose |
|----------|---------|
| src/auth/ | Authentication and authorization |
| src/validation/ | Input validation with Zod schemas |

## Configuration
| Location | Purpose |
|----------|---------|
| src/config.ts | Environment/app config loader |
| .env.example | Required environment variables |

## Key Patterns
| Pattern | Example Location | Notes |
|---------|------------------|-------|
| Repository pattern | src/repos/UserRepo.ts | All DB access through repos |
| Middleware chain | src/middleware/auth.ts | Express middleware for auth |

## Testing
| Location | Purpose |
|----------|---------|
| tests/ | Test files mirror src/ structure |
| tests/fixtures/ | Test data fixtures |

## Gotchas & Non-Obvious Behavior
| Location | Issue | Notes |
|----------|-------|-------|
| src/db/migrations/ | Must be in chronological order | Timestamp-based naming |
| src/auth/tokens.ts | Tokens expire in 24hrs | Set JWT_EXPIRY env var to change |
```

Sources: [commands/initialize-project.md:573-617]()

### prompts/ - LLM Prompt Specifications

**Directory Location**: `_project_specs/prompts/`

For AI-first applications where LLMs handle core logic, this directory contains prompt templates, evaluation criteria, and version history.

**Typical Contents**:
- `classification-prompt.md` - Prompts for classification tasks
- `extraction-prompt.md` - Prompts for data extraction
- `evals/` - Test cases and expected outputs for prompt evaluation

This directory is created when `/initialize-project` detects AI-first project type (checks for `anthropic` or `openai` in dependencies).

Sources: [commands/initialize-project.md:123](), [skills/base.md:123]()

### team/ - Multi-Person Coordination

**Directory Location**: `_project_specs/team/`

Created when project is converted to team mode via `/check-contributors --team`. Contains files for coordinating multiple developers using Claude Code on the same repository.

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `state.md` | Active sessions, claimed todos, file conflicts | At session start/end, when claiming todos |
| `contributors.md` | Team members, ownership areas, focus | When team composition changes |
| `handoffs/` | Context transfer notes between developers | When passing work to another person |

Sources: [README.md:226-231]()

---

## Environment and Secrets Configuration

### .env.example

**File Location**: `.env.example` (project root)

Template for environment variables. NEVER contains actual values. Committed to git as documentation.

**Format**:
```bash
# .env.example - Copy to .env and fill in values
# Server-side only (NEVER prefix with VITE_ or NEXT_PUBLIC_)

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# APIs
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-proj-xxx

# Supabase (if applicable)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx

# Client-side safe (public, non-sensitive)
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJxxx
NEXT_PUBLIC_API_URL=https://api.example.com
```

**Security Rule**: Only use `VITE_*` or `NEXT_PUBLIC_*` prefixes for non-sensitive, publicly exposed values (like Supabase anon key or public API URLs). Never for secrets.

Sources: [commands/initialize-project.md:203-214]()

### .gitignore Security Patterns

**File Location**: `.gitignore` (project root)

The `.gitignore` file includes mandatory security-critical patterns:

```gitignore
# Environment files - NEVER commit
.env
.env.*
!.env.example

# Secrets
*.pem
*.key
*.p12
credentials.json
secrets.json
service-account*.json

# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build outputs
dist/
build/

# IDE
.idea/
.vscode/settings.json
.DS_Store
```

These patterns are non-negotiable and enforced by pre-commit hooks via `scripts/security-check.sh`.

Sources: [commands/initialize-project.md:168-200]()

---

## Scripts Configuration

### verify-tooling.sh

**File Location**: `scripts/verify-tooling.sh`

Shell script that validates all required CLI tools are installed and authenticated. Created during `/initialize-project`.

**What It Checks**:
- GitHub CLI (`gh auth status`)
- Vercel CLI (`vercel whoami`)
- Supabase CLI (`supabase projects list`)

**Usage**:
```bash
./scripts/verify-tooling.sh
```

**Exit Codes**:
- 0: All tools authenticated
- 1: One or more tools missing or not authenticated

Sources: [commands/initialize-project.md:216-263]()

### security-check.sh

**File Location**: `scripts/security-check.sh`

Pre-commit security validation script. Runs automatically via git hooks to prevent secret leakage.

**Checks Performed**:
1. `.env` files are not staged for commit
2. Common secret patterns in staged files
3. `VITE_*` or `NEXT_PUBLIC_*` prefixed secrets (common mistake)
4. `npm audit` for Node.js projects
5. `safety check` for Python projects

**Blocking Conditions**:
- `.env` file is staged → ERROR, exit 1
- Secrets in `VITE_*` env vars → ERROR, exit 1
- High/critical vulnerabilities in dependencies → WARNING

**Integration**: Referenced in `.husky/pre-commit` (Node.js) or `.pre-commit-config.yaml` (Python).

Sources: [commands/initialize-project.md:270-318]()

---

## GitHub Actions Workflows

### quality.yml

**File Location**: `.github/workflows/quality.yml`

CI workflow that enforces quality gates on every push and pull request.

**Quality Gates**:
- Linting with auto-fix
- Type checking (TypeScript: `tsc --noEmit`, Python: `mypy`)
- Full test suite execution
- **80% minimum code coverage** (blocks merge below threshold)

**Node.js/TypeScript Example**:
```yaml
name: Quality

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --coverage --watchAll=false
      - name: Check coverage
        run: |
          COVERAGE=$(npm test -- --coverage --silent | grep "All files" | awk '{print $10}' | sed 's/%//')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 80% threshold"
            exit 1
          fi
```

Sources: [commands/initialize-project.md:619-623](), [README.md:515-530]()

### security.yml

**File Location**: `.github/workflows/security.yml`

Security scanning workflow that runs on push, pull requests, and weekly schedule.

**Security Checks**:
1. **Secret Scanning**: TruffleHog scans entire git history for leaked secrets
2. **Dependency Audit**: 
   - Node.js: `npm audit --audit-level=high`
   - Python: `safety check`

**Schedule**: Runs on every push/PR + weekly on Mondays at 9am (catches newly disclosed vulnerabilities in dependencies)

Sources: [commands/initialize-project.md:625-668]()

---

## Stack-Specific Configuration

### TypeScript/Node.js Projects

**Key Configuration Files**:
- `tsconfig.json` - TypeScript compiler options (strict mode enabled)
- `package.json` - Scripts for `test`, `lint`, `typecheck`, `build`
- `.eslintrc.js` or `.eslintrc.json` - ESLint rules
- `jest.config.js` or `vitest.config.ts` - Test runner configuration

**Required npm Scripts**:
```json
{
  "scripts": {
    "test": "jest --coverage",
    "test:watch": "jest --watch",
    "lint": "eslint . --fix",
    "typecheck": "tsc --noEmit",
    "validate": "npm run lint && npm run typecheck && npm test"
  }
}
```

**Pre-commit Hook Setup** (Husky + lint-staged):
```bash
npx husky init
npx husky set .husky/pre-commit "npx lint-staged && ./scripts/security-check.sh"
```

Sources: [commands/initialize-project.md:675-676]()

### Python Projects

**Key Configuration Files**:
- `pyproject.toml` - Project metadata, dependencies, tool configurations
- `ruff.toml` or `[tool.ruff]` section in `pyproject.toml` - Linter config
- `mypy.ini` or `[tool.mypy]` in `pyproject.toml` - Type checker config
- `pytest.ini` or `[tool.pytest.ini_options]` - Test configuration

**Required pyproject.toml Scripts Equivalent**:
```bash
# Testing
pytest --cov --cov-report=term-missing --cov-fail-under=80

# Linting
ruff check . --fix

# Type checking
mypy src/

# Full validation
ruff check . && mypy src/ && pytest --cov --cov-fail-under=80
```

**Pre-commit Hook Setup** (.pre-commit-config.yaml):
```yaml
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: ruff check --fix
        language: system
        types: [python]
      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
      - id: security-check
        name: security-check
        entry: ./scripts/security-check.sh
        language: system
        pass_filenames: false
```

Sources: [commands/initialize-project.md:672-674]()

### React/Next.js Projects

**Additional Configuration**:
- `next.config.js` or `next.config.mjs` - Next.js framework config
- `tailwind.config.js` - Tailwind CSS config (if using Tailwind)
- `playwright.config.ts` - E2E testing config (if using Playwright)

**Environment Variable Prefixes**:
- `NEXT_PUBLIC_*` - Exposed to client (public values only)
- No prefix - Server-side only (secrets)

**Example next.config.js with Security Headers**:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
```

Sources: [README.md:666-678]()

---

## Configuration File Relationships

**Configuration File Dependencies**

```mermaid
graph TB
    subgraph "Claude Reads These First"
        CLAUDE_MD["CLAUDE.md"]
        SKILLS_DIR[".claude/skills/"]
    end
    
    subgraph "Session State (Read on Resume)"
        CURRENT["_project_specs/session/<br/>current-state.md"]
        DECISIONS["_project_specs/session/<br/>decisions.md"]
        LANDMARKS["_project_specs/session/<br/>code-landmarks.md"]
    end
    
    subgraph "Work Tracking"
        ACTIVE["_project_specs/todos/<br/>active.md"]
        BACKLOG["_project_specs/todos/<br/>backlog.md"]
    end
    
    subgraph "Quality Enforcement"
        QUALITY_YML[".github/workflows/<br/>quality.yml"]
        SECURITY_YML[".github/workflows/<br/>security.yml"]
        PRE_COMMIT[".husky/pre-commit or<br/>.pre-commit-config.yaml"]
        SEC_SCRIPT["scripts/<br/>security-check.sh"]
    end
    
    subgraph "Runtime Configuration"
        ENV_EXAMPLE[".env.example"]
        ENV[".env<br/>(gitignored)"]
        GITIGNORE[".gitignore"]
    end
    
    subgraph "Build/Test Configuration"
        PKG_JSON["package.json or<br/>pyproject.toml"]
        TS_CONFIG["tsconfig.json or<br/>mypy.ini"]
        TEST_CONFIG["jest.config.js or<br/>pytest.ini"]
    end
    
    CLAUDE_MD -->|"references"| SKILLS_DIR
    CLAUDE_MD -->|"defines commands in"| PKG_JSON
    CLAUDE_MD -->|"points to schema in"| LANDMARKS
    
    CURRENT -->|"tracks todos from"| ACTIVE
    DECISIONS -->|"informs architecture"| CLAUDE_MD
    LANDMARKS -->|"quick nav to"| TS_CONFIG
    
    ACTIVE -->|"moved to completed<br/>after TDD log complete"| BACKLOG
    
    PRE_COMMIT -->|"runs"| SEC_SCRIPT
    SEC_SCRIPT -->|"checks for"| ENV
    SEC_SCRIPT -->|"enforces patterns in"| GITIGNORE
    
    QUALITY_YML -->|"runs commands from"| PKG_JSON
    QUALITY_YML -->|"uses config from"| TEST_CONFIG
    SECURITY_YML -->|"validates"| ENV_EXAMPLE
    
    ENV_EXAMPLE -->|"template for"| ENV
    GITIGNORE -->|"ignores"| ENV
```

Sources: [commands/initialize-project.md:1-821](), [templates/CLAUDE.md:1-113](), [skills/base.md:99-135]()

---

## Idempotency and Updates

All configuration files are designed for idempotent updates. Running `/initialize-project` multiple times:

**Always Updates** (overwrites with latest):
- `.claude/skills/*.md` - Skills are always refreshed from `~/.claude/skills/`
- `scripts/verify-tooling.sh` - Regenerated to latest version
- `scripts/security-check.sh` - Regenerated to latest version
- `.github/workflows/quality.yml` - Updated with latest CI patterns
- `.github/workflows/security.yml` - Updated with latest security checks

**Never Overwrites** (preserves user changes):
- `CLAUDE.md` - Updates only the Skills section, preserves Project-Specific Patterns
- `_project_specs/todos/*.md` - Never touches existing todos
- `_project_specs/session/*.md` - Never overwrites session state
- `.env` - Never created or modified (user manages this)
- `package.json` / `pyproject.toml` - Never modifies existing configuration

**Creates If Missing**:
- `.gitignore` - Adds missing security patterns without removing existing entries
- `.env.example` - Creates template if doesn't exist
- `_project_specs/` structure - Creates missing directories and placeholder files

Sources: [commands/initialize-project.md:1-6](), [commands/initialize-project.md:322-324]()

---

# Page: Extending Claude Bootstrap

# Extending Claude Bootstrap

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [install.sh](install.sh)
- [skills/base.md](skills/base.md)
- [templates/CLAUDE.md](templates/CLAUDE.md)

</details>



## Purpose and Scope

This page documents how advanced users can extend Claude Bootstrap to meet custom needs: creating new skills, adding commands, modifying initialization behavior, and contributing changes back to the project. For information about using the existing skills system, see [Skills Architecture](#5.1). For details on the standard commands, see [Commands Reference](#9.1).

---

## Skills System Architecture

### Skill File Structure

Skills are markdown files that follow a standardized format. Every skill must be self-contained and declarative.

**Core Structure:**

```markdown
# Skill Name - Brief Description

## Core Principle
High-level philosophy

## Patterns
Specific implementation patterns

## Anti-Patterns
What to avoid

## Validation
How to verify compliance
```

**Sources:** [skills/base.md:1-580]()

### Skill Loading Flow

**Diagram: Skill Installation and Loading Pipeline**

```mermaid
graph TB
    subgraph "Source Repository"
        REPO["~/.claude-bootstrap/skills/"]
        BASE["base.md"]
        LANG["python.md, typescript.md"]
        FRAME["react-web.md, nodejs-backend.md"]
        CUSTOM["your-custom-skill.md"]
    end
    
    subgraph "Install Script"
        INSTALL["install.sh"]
        COPY_CMD["cp skills/*.md ~/.claude/skills/"]
    end
    
    subgraph "Global Claude Directory"
        GLOBAL["~/.claude/skills/"]
        G_BASE["base.md"]
        G_LANG["python.md, typescript.md"]
        G_CUSTOM["your-custom-skill.md"]
    end
    
    subgraph "Project Initialization"
        INIT_CMD["/initialize-project"]
        SELECT["Skill Selection Logic"]
        DETECT["Detect: language, framework, features"]
    end
    
    subgraph "Project Directory"
        PROJ_SKILLS[".claude/skills/"]
        P_BASE["base.md (always)"]
        P_SELECTED["Selected skills"]
        P_CUSTOM["Custom skills (if selected)"]
    end
    
    subgraph "Claude Code Runtime"
        LOAD["Skill Loader"]
        CLAUDEMD["CLAUDE.md"]
        CONTEXT["Active Context"]
    end
    
    REPO --> INSTALL
    BASE --> COPY_CMD
    LANG --> COPY_CMD
    FRAME --> COPY_CMD
    CUSTOM --> COPY_CMD
    
    INSTALL --> COPY_CMD
    COPY_CMD --> GLOBAL
    
    GLOBAL --> G_BASE
    GLOBAL --> G_LANG
    GLOBAL --> G_CUSTOM
    
    G_BASE --> INIT_CMD
    G_LANG --> INIT_CMD
    G_CUSTOM --> INIT_CMD
    
    INIT_CMD --> SELECT
    SELECT --> DETECT
    DETECT --> PROJ_SKILLS
    
    PROJ_SKILLS --> P_BASE
    PROJ_SKILLS --> P_SELECTED
    PROJ_SKILLS --> P_CUSTOM
    
    P_BASE --> LOAD
    P_SELECTED --> LOAD
    LOAD --> CLAUDEMD
    CLAUDEMD --> CONTEXT
```

**Key Points:**

| Stage | Location | Purpose |
|-------|----------|---------|
| **Source** | `~/.claude-bootstrap/skills/` | Master repository of all available skills |
| **Installation** | `~/.claude/skills/` | Global Claude directory, skills available for all projects |
| **Project Copy** | `.claude/skills/` | Project-specific copy, overwritten on re-initialization |
| **Runtime** | `CLAUDE.md` references | Skills actively loaded in Claude context |

**Sources:** [install.sh:1-66](), [skills/base.md:99-135]()

---

## Creating Custom Skills

### Skill File Format

Custom skills follow the same format as core skills. The structure ensures consistency and discoverability.

**Minimal Skill Template:**

```markdown
# Custom Skill Name - One-Line Description

## Core Principle
What this skill enforces or enables.

## When to Use
Specific scenarios where this skill applies.

## Patterns

### Pattern 1: Name
Description of the pattern.

```[language]
// Example code
```

### Pattern 2: Name
Description of the pattern.

## Validation
How Claude (or developer) can verify compliance.

## Anti-Patterns
What NOT to do.
```

**Sources:** [skills/base.md:1-20]()

### Skill Categories

Skills are organized by category. Custom skills should align with existing categories or define new ones.

**Diagram: Skill Category Hierarchy**

```mermaid
graph TB
    subgraph "Core Skills (Always Loaded)"
        CORE["Core Category"]
        BASE["base.md<br/>TDD, simplicity rules"]
        SECURITY["security.md<br/>OWASP patterns"]
        CREDS["credentials.md<br/>API key management"]
        SESSION["session-management.md<br/>Context preservation"]
        REVIEW["code-review.md<br/>Mandatory reviews"]
        COMMITS["commit-hygiene.md<br/>PR size limits"]
        DEDUP["code-deduplication.md<br/>Capability index"]
        TEAM["team-coordination.md<br/>Multi-dev state"]
    end
    
    subgraph "Language Skills (Conditional)"
        LANG["Language Category"]
        PYTHON["python.md<br/>ruff, mypy, pytest"]
        TS["typescript.md<br/>strict mode, eslint"]
    end
    
    subgraph "Framework Skills (Conditional)"
        FRAME["Framework Category"]
        REACT["react-web.md<br/>Hooks, React Query"]
        NATIVE["react-native.md<br/>Platform patterns"]
        NODE["nodejs-backend.md<br/>Express, Fastify"]
    end
    
    subgraph "Integration Skills (Conditional)"
        INTEG["Integration Category"]
        STRIPE["web-payments.md<br/>Stripe patterns"]
        POSTHOG["posthog-analytics.md<br/>Event tracking"]
        REDDIT["reddit-ads.md<br/>Campaign API"]
    end
    
    subgraph "Custom Skills (User-Defined)"
        CUSTOM["Custom Category"]
        CUSTOM1["your-domain-skill.md"]
        CUSTOM2["your-company-patterns.md"]
    end
    
    CORE --> BASE
    CORE --> SECURITY
    CORE --> CREDS
    CORE --> SESSION
    CORE --> REVIEW
    CORE --> COMMITS
    CORE --> DEDUP
    CORE --> TEAM
    
    LANG --> PYTHON
    LANG --> TS
    
    FRAME --> REACT
    FRAME --> NATIVE
    FRAME --> NODE
    
    INTEG --> STRIPE
    INTEG --> POSTHOG
    INTEG --> REDDIT
    
    CUSTOM --> CUSTOM1
    CUSTOM --> CUSTOM2
```

**Sources:** [README.md:396-466]()

### Creating a Custom Skill: Step-by-Step

**1. Create Skill File**

Place your skill in the source repository:

```bash
cd ~/.claude-bootstrap/skills/
touch my-custom-skill.md
```

**2. Define Skill Content**

Example custom skill for GraphQL best practices:

```markdown
# GraphQL API Skill - Type-Safe Query Development

## Core Principle
GraphQL APIs must maintain strict type safety from schema to resolver to client.

## Patterns

### Schema-First Development
Define schema before implementing resolvers.

```graphql
type User {
  id: ID!
  email: String!
  posts: [Post!]!
}

type Query {
  user(id: ID!): User
}
```

### Resolver Pattern
```typescript
// resolvers/user.ts
export const userResolver = {
  Query: {
    user: async (_: any, { id }: { id: string }, ctx: Context) => {
      return ctx.db.user.findUnique({ where: { id } });
    },
  },
};
```

### Client Code Generation
Always generate types from schema.

```bash
# Generate TypeScript types
npm run graphql-codegen
```

## Validation
- [ ] Schema valid: `npm run validate-schema`
- [ ] Types generated: Check `src/generated/graphql.ts`
- [ ] Resolvers typed: No `any` types in resolver signatures

## Anti-Patterns
- ❌ Resolver logic without types
- ❌ Manual type definitions (schema is source of truth)
- ❌ Ignoring N+1 query issues (use DataLoader)
```

**3. Install Globally**

```bash
cd ~/.claude-bootstrap
./install.sh
```

This copies your custom skill to `~/.claude/skills/`.

**4. Include in Projects**

Skills are copied to projects during initialization. To include your custom skill:

**Option A: Always include (add to core set)**

Edit the initialization command logic to always copy your skill.

**Option B: Conditional include (based on project type)**

Add detection logic to `/initialize-project` command that copies your skill when specific conditions are met (e.g., when GraphQL is detected).

**Option C: Manual include**

Copy skill to project manually:
```bash
cp ~/.claude/skills/my-custom-skill.md .claude/skills/
```

Update `CLAUDE.md` to reference it:
```markdown
## Skills Loaded
- base.md
- my-custom-skill.md (GraphQL best practices)
```

**Sources:** [install.sh:19-31](), [templates/CLAUDE.md:1-113]()

### Skill Best Practices

| Principle | Implementation |
|-----------|----------------|
| **Self-contained** | Each skill stands alone, no dependencies on other skills (except `base.md`) |
| **Actionable** | Provide concrete patterns, not vague guidance |
| **Verifiable** | Include validation criteria that Claude or developer can check |
| **Examples-driven** | Show code examples for every pattern |
| **Anti-patterns explicit** | Document what NOT to do as clearly as what to do |

**Sources:** [skills/base.md:1-20]()

---

## Adding Custom Commands

### Command File Structure

Commands are markdown files placed in `~/.claude/commands/` that define custom slash commands for Claude Code.

**Command Format:**

```markdown
# Command Name

## Description
Brief description of what this command does.

## Usage
```bash
/command-name [arguments]
```

## Implementation
[Command implementation details]

## Examples
```bash
/command-name --example
```
```

**Sources:** [install.sh:19-22]()

### Command Installation Flow

**Diagram: Command Installation and Execution**

```mermaid
graph TB
    subgraph "Source Repository"
        CMD_SRC["~/.claude-bootstrap/commands/"]
        INIT["initialize-project.md"]
        REVIEW["code-review.md"]
        CONTRIB["check-contributors.md"]
        INDEX["update-code-index.md"]
        CUSTOM["my-custom-command.md"]
    end
    
    subgraph "Installation"
        INST["install.sh"]
        COPY["cp commands/*.md<br/>~/.claude/commands/"]
    end
    
    subgraph "Global Commands"
        GLOBAL["~/.claude/commands/"]
        G_INIT["initialize-project.md"]
        G_REVIEW["code-review.md"]
        G_CUSTOM["my-custom-command.md"]
    end
    
    subgraph "Claude Code CLI"
        PARSER["Command Parser"]
        DETECT["/my-custom-command"]
        LOAD["Load command.md"]
        EXECUTE["Execute logic"]
    end
    
    subgraph "Project Context"
        PROJ["Current working directory"]
        FILES["Project files"]
        STATE["_project_specs/"]
    end
    
    CMD_SRC --> INIT
    CMD_SRC --> REVIEW
    CMD_SRC --> CONTRIB
    CMD_SRC --> INDEX
    CMD_SRC --> CUSTOM
    
    INIT --> INST
    REVIEW --> INST
    CONTRIB --> INST
    CUSTOM --> INST
    
    INST --> COPY
    COPY --> GLOBAL
    
    GLOBAL --> G_INIT
    GLOBAL --> G_REVIEW
    GLOBAL --> G_CUSTOM
    
    G_CUSTOM --> PARSER
    PARSER --> DETECT
    DETECT --> LOAD
    LOAD --> EXECUTE
    
    EXECUTE --> PROJ
    PROJ --> FILES
    PROJ --> STATE
```

**Sources:** [install.sh:19-22](), [README.md:52-70]()

### Creating a Custom Command

**Example: Audit Command for Code Quality**

**File:** `~/.claude-bootstrap/commands/audit-quality.md`

```markdown
# /audit-quality - Comprehensive Code Quality Audit

## Description
Analyzes codebase for complexity violations, test coverage gaps, and security issues. Generates actionable report.

## Usage
```bash
/audit-quality [options]

Options:
  --strict     Fail on any violations (exit code 1)
  --fix        Auto-fix violations where possible
  --report     Generate detailed markdown report
```

## Implementation

### Detection Logic

1. **Complexity Analysis**
   - Scan all files for function length violations (>20 lines)
   - Check parameter counts (>3 params)
   - Identify nesting depth violations (>2 levels)

2. **Coverage Analysis**
   - Run test suite with coverage
   - Identify files below 80% threshold
   - List untested functions

3. **Security Scan**
   - Check for hardcoded secrets
   - Verify `.env` in `.gitignore`
   - Scan for client-exposed secrets (`VITE_*`, `NEXT_PUBLIC_*`)

### Output Format

```markdown
# Code Quality Audit Report

## Complexity Violations (5 found)

| File | Function | Lines | Max | Action |
|------|----------|-------|-----|--------|
| src/api/users.ts | fetchUser | 32 | 20 | Split into helper functions |

## Coverage Gaps (12 files below 80%)

| File | Coverage | Target | Uncovered Lines |
|------|----------|--------|-----------------|
| src/utils/format.ts | 65% | 80% | 45-67, 89-102 |

## Security Issues (2 critical)

| Issue | Severity | File | Line | Fix |
|-------|----------|------|------|-----|
| API key in code | Critical | src/config.ts | 12 | Move to .env |
```

### Error Handling

If no issues found:
```
✅ Code quality audit passed
   - All files under 200 lines
   - All functions under 20 lines
   - Coverage above 80%
   - No security issues
```

If issues found without `--strict`:
```
⚠️ Code quality issues found (see report above)
   Run with --fix to auto-fix or --strict to fail CI
```

If issues found with `--strict`:
```
❌ Code quality audit failed
   5 violations found
   Exit code: 1
```

## Examples

```bash
# Basic audit
/audit-quality

# Generate report file
/audit-quality --report > audit-report.md

# Auto-fix violations
/audit-quality --fix

# Strict mode (for CI)
/audit-quality --strict
```

## Integration

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

if ! claude /audit-quality --strict; then
  echo "Fix quality issues before committing"
  exit 1
fi
```

### CI/CD
```yaml
# .github/workflows/quality.yml
- name: Code Quality Audit
  run: |
    claude /audit-quality --strict --report
    cat audit-report.md >> $GITHUB_STEP_SUMMARY
```
```

**Install the command:**

```bash
cd ~/.claude-bootstrap
./install.sh
```

**Sources:** [install.sh:19-22]()

### Command Conventions

| Convention | Rule |
|------------|------|
| **Naming** | Use kebab-case: `/my-command-name` |
| **Parameters** | Support `--flags` for options, avoid positional args |
| **Output** | Clear success/failure indicators (✅ ❌ ⚠️) |
| **Error handling** | Graceful failures with actionable error messages |
| **Idempotency** | Safe to run multiple times without side effects |

**Sources:** [README.md:248-253]()

---

## Modifying Initialization Workflow

### Initialization Command Structure

The `/initialize-project` command orchestrates project setup. Understanding its flow enables customization.

**Diagram: /initialize-project Execution Flow**

```mermaid
graph TB
    START["/initialize-project invoked"]
    
    subgraph "Phase 1: Validation"
        CHECK_DIR["Check if valid directory"]
        CHECK_CLI["Validate CLIs:<br/>gh, vercel, supabase"]
        REPORT_MISSING["Report missing CLIs"]
    end
    
    subgraph "Phase 2: Project Discovery"
        DETECT_EXISTING["Check for existing files"]
        GIT_STATUS["Git status: new vs existing"]
        DETECT_LANG["Detect language:<br/>package.json, requirements.txt"]
        DETECT_FRAME["Detect framework:<br/>next.config, vite.config"]
    end
    
    subgraph "Phase 3: User Input"
        ASK_LANG["Ask: Language?<br/>(Python, TypeScript)"]
        ASK_FRAME["Ask: Framework?<br/>(React, FastAPI, etc)"]
        ASK_DB["Ask: Database?<br/>(Supabase, PostgreSQL)"]
        ASK_AI["Ask: AI-first?<br/>(yes/no)"]
        ASK_INTEGRATIONS["Ask: Integrations?<br/>(Stripe, PostHog, etc)"]
    end
    
    subgraph "Phase 4: Skill Selection"
        SELECT_CORE["Select core skills:<br/>base.md, security.md"]
        SELECT_LANG["Select language skills"]
        SELECT_FRAME["Select framework skills"]
        SELECT_INTEGRATIONS["Select integration skills"]
    end
    
    subgraph "Phase 5: File Generation"
        COPY_SKILLS["Copy selected skills<br/>to .claude/skills/"]
        GEN_CLAUDE_MD["Generate CLAUDE.md"]
        GEN_GITIGNORE["Generate/update .gitignore"]
        GEN_WORKFLOWS["Generate GitHub Actions"]
        GEN_SPECS["Create _project_specs/"]
        GEN_SCRIPTS["Copy scripts/<br/>security-check.sh"]
    end
    
    subgraph "Phase 6: Repository Setup"
        CHECK_GH["Check GitHub repo"]
        CREATE_REPO["Create repo if needed"]
        INIT_GIT["git init if needed"]
        FIRST_COMMIT["Initial commit"]
    end
    
    subgraph "Phase 7: External Config"
        VERCEL["Vercel project setup"]
        SUPABASE["Supabase project link"]
        CREDS["Read Access.txt"]
        GEN_ENV["Generate .env"]
    end
    
    subgraph "Phase 8: Completion"
        SUMMARY["Print setup summary"]
        NEXT_STEPS["Show next steps"]
        PROMPT_SPECS["Prompt: Define first feature"]
    end
    
    START --> CHECK_DIR
    CHECK_DIR --> CHECK_CLI
    CHECK_CLI --> REPORT_MISSING
    REPORT_MISSING --> DETECT_EXISTING
    
    DETECT_EXISTING --> GIT_STATUS
    GIT_STATUS --> DETECT_LANG
    DETECT_LANG --> DETECT_FRAME
    
    DETECT_FRAME --> ASK_LANG
    ASK_LANG --> ASK_FRAME
    ASK_FRAME --> ASK_DB
    ASK_DB --> ASK_AI
    ASK_AI --> ASK_INTEGRATIONS
    
    ASK_INTEGRATIONS --> SELECT_CORE
    SELECT_CORE --> SELECT_LANG
    SELECT_LANG --> SELECT_FRAME
    SELECT_FRAME --> SELECT_INTEGRATIONS
    
    SELECT_INTEGRATIONS --> COPY_SKILLS
    COPY_SKILLS --> GEN_CLAUDE_MD
    GEN_CLAUDE_MD --> GEN_GITIGNORE
    GEN_GITIGNORE --> GEN_WORKFLOWS
    GEN_WORKFLOWS --> GEN_SPECS
    GEN_SPECS --> GEN_SCRIPTS
    
    GEN_SCRIPTS --> CHECK_GH
    CHECK_GH --> CREATE_REPO
    CREATE_REPO --> INIT_GIT
    INIT_GIT --> FIRST_COMMIT
    
    FIRST_COMMIT --> VERCEL
    VERCEL --> SUPABASE
    SUPABASE --> CREDS
    CREDS --> GEN_ENV
    
    GEN_ENV --> SUMMARY
    SUMMARY --> NEXT_STEPS
    NEXT_STEPS --> PROMPT_SPECS
```

**Sources:** [README.md:64-70]()

### Customizing Skill Selection Logic

To add custom logic that automatically includes specific skills based on project characteristics:

**1. Add Detection Logic**

Detect custom conditions in Phase 2 (Project Discovery):

```markdown
### Custom Detection: E-Commerce Project

Check for indicators:
- `package.json` contains `@shopify/*` or `@medusajs/*`
- Files: `shopify.config.js`, `medusa-config.js`
- Directory: `src/ecommerce/`, `plugins/`

If detected, set flag: `is_ecommerce = true`
```

**2. Expand Selection Rules**

In Phase 4 (Skill Selection), add conditional logic:

```markdown
### E-Commerce Skill Selection

If `is_ecommerce` and Shopify detected:
  - Copy `shopify-apps.md`
  - Copy `web-payments.md` (Stripe likely needed)
  - Copy `posthog-analytics.md` (tracking likely needed)

If `is_ecommerce` and Medusa detected:
  - Copy `medusa.md`
  - Copy `web-payments.md`
```

**3. Update Template Generation**

Modify `CLAUDE.md` generation to reference custom skills:

```markdown
## Skills Loaded
- base.md
- typescript.md
- react-web.md
- shopify-apps.md (E-commerce patterns)
- web-payments.md (Stripe integration)
```

**Sources:** [templates/CLAUDE.md:1-113]()

### Adding Custom Project Templates

To support new project types (e.g., Chrome extension, CLI tool):

**1. Create Template Directory**

```bash
mkdir ~/.claude-bootstrap/templates/chrome-extension/
```

**2. Define Template Structure**

```
templates/chrome-extension/
├── manifest.json.template
├── popup.html.template
├── background.js.template
├── CLAUDE.md.template
└── tsconfig.json.template
```

**3. Add Template Logic to Initialization**

Extend Phase 3 (User Input) to detect/ask for Chrome extension:

```markdown
### Chrome Extension Detection

Ask: "Is this a Chrome extension? (y/n)"

If yes:
  - Copy chrome-extension templates
  - Select chrome-extension.md skill (if exists)
  - Generate manifest.json with proper structure
  - Set up webpack/vite for extension bundling
```

**Sources:** [templates/CLAUDE.md:1-113]()

### Modifying File Generation

Customize what files get generated in Phase 5:

**Example: Custom GitHub Actions Workflow**

**File:** `~/.claude-bootstrap/templates/workflows/custom-quality.yml`

```yaml
name: Custom Quality Checks
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Custom Audit
        run: |
          npm install
          claude /audit-quality --strict
```

**Include in initialization:**

```markdown
### Workflow Generation (Phase 5)

Copy workflows:
- quality.yml (standard)
- security.yml (standard)
- custom-quality.yml (if custom flag set)
```

**Sources:** [README.md:296-317]()

---

## Testing Custom Extensions

### Testing Custom Skills

**Validation checklist:**

| Test | Method |
|------|--------|
| **Syntax** | Ensure markdown is valid, no broken formatting |
| **References** | Verify all file paths in examples exist |
| **Commands** | Test example commands actually work |
| **Integration** | Install skill, initialize project, verify Claude loads it |

**Test procedure:**

```bash
# 1. Install custom skill
cd ~/.claude-bootstrap
./install.sh

# 2. Create test project
mkdir /tmp/test-custom-skill
cd /tmp/test-custom-skill

# 3. Initialize with custom skill
claude
> /initialize-project

# 4. Verify skill is loaded
cat .claude/skills/my-custom-skill.md

# 5. Verify CLAUDE.md references it
cat CLAUDE.md | grep "my-custom-skill"

# 6. Test skill patterns work
# (Try implementing something using the skill's patterns)
```

**Sources:** [install.sh:1-66]()

### Testing Custom Commands

**Command test checklist:**

| Test | Expected Result |
|------|-----------------|
| **Invocation** | `/my-command` executes without error |
| **Help text** | Command shows usage when invoked incorrectly |
| **Error handling** | Graceful failures with clear messages |
| **Output format** | Consistent with other commands (✅ ❌ ⚠️) |
| **Idempotency** | Running twice produces same result |

**Test procedure:**

```bash
# 1. Install command
cd ~/.claude-bootstrap
./install.sh

# 2. Test invocation
cd /tmp/test-project
claude
> /my-custom-command

# 3. Test with flags
> /my-custom-command --help
> /my-custom-command --strict

# 4. Test error cases
> /my-custom-command --invalid-flag  # Should show error

# 5. Test idempotency
> /my-custom-command
> /my-custom-command  # Should produce same output
```

**Sources:** [install.sh:19-22]()

---

## Contributing Extensions Back

### Contribution Workflow

**Diagram: Contributing Custom Extensions**

```mermaid
graph TB
    subgraph "Development"
        LOCAL["Local development<br/>~/.claude-bootstrap/"]
        CREATE["Create skill/command"]
        TEST["Test in real projects"]
        REFINE["Refine based on usage"]
    end
    
    subgraph "Preparation"
        DOC["Document in skill/command"]
        EXAMPLES["Add concrete examples"]
        VALIDATE["Validate syntax"]
        README_UPDATE["Update README if needed"]
    end
    
    subgraph "Git Workflow"
        FORK["Fork repository"]
        BRANCH["Create feature branch"]
        COMMIT["Commit changes"]
        PUSH["Push to fork"]
        PR["Create pull request"]
    end
    
    subgraph "Review Process"
        REVIEW["Maintainer review"]
        FEEDBACK["Address feedback"]
        APPROVE["Approval"]
        MERGE["Merge to main"]
    end
    
    subgraph "Distribution"
        RELEASE["Next release"]
        USERS["install.sh gets updates"]
        PROJECTS["Projects get via re-init"]
    end
    
    LOCAL --> CREATE
    CREATE --> TEST
    TEST --> REFINE
    REFINE --> DOC
    
    DOC --> EXAMPLES
    EXAMPLES --> VALIDATE
    VALIDATE --> README_UPDATE
    
    README_UPDATE --> FORK
    FORK --> BRANCH
    BRANCH --> COMMIT
    COMMIT --> PUSH
    PUSH --> PR
    
    PR --> REVIEW
    REVIEW --> FEEDBACK
    FEEDBACK --> COMMIT
    REVIEW --> APPROVE
    APPROVE --> MERGE
    
    MERGE --> RELEASE
    RELEASE --> USERS
    USERS --> PROJECTS
```

### Contribution Guidelines

**Before contributing:**

1. **Test extensively** - Use the skill/command in real projects for at least a week
2. **Document thoroughly** - Include clear examples and anti-patterns
3. **Follow conventions** - Match existing skill/command structure
4. **Provide rationale** - Explain why this extension is needed

**Skill contribution requirements:**

| Requirement | Details |
|-------------|---------|
| **Format** | Follow standard skill structure (see [Creating Custom Skills](#creating-custom-skills)) |
| **Examples** | Include working code examples for every pattern |
| **Anti-patterns** | Document what NOT to do |
| **Validation** | Provide concrete validation criteria |
| **Self-contained** | No dependencies on other skills (except `base.md`) |

**Command contribution requirements:**

| Requirement | Details |
|-------------|---------|
| **Format** | Follow standard command structure |
| **Usage section** | Clear syntax with all flags documented |
| **Examples** | Multiple usage examples covering common cases |
| **Error handling** | Graceful failures with actionable messages |
| **Testing** | Demonstrate command works in clean project |

**Sources:** [README.md:692-700]()

### Pull Request Template

When submitting a pull request for a custom extension:

**PR Title Format:**
```
[SKILL] Add GraphQL best practices skill
[COMMAND] Add /audit-quality command
```

**PR Description Template:**
```markdown
## Extension Type
- [ ] New skill
- [ ] New command
- [ ] Modification to existing skill/command
- [ ] New template

## Description
Brief description of what this adds/changes.

## Motivation
Why is this extension needed? What problem does it solve?

## Testing
- [ ] Tested in real project for 1+ week
- [ ] All examples verified working
- [ ] Installed via install.sh and tested
- [ ] No breaking changes to existing behavior

## Documentation
- [ ] README updated (if needed)
- [ ] Examples provided
- [ ] Anti-patterns documented

## Validation
Describe how this extension can be validated:
- [ ] Validation criteria 1
- [ ] Validation criteria 2
```

**Sources:** [README.md:692-700]()

---

## Advanced Customization

### Skill Composition Patterns

For complex domains, compose multiple focused skills rather than one large skill.

**Example: E-Commerce Domain**

Instead of:
```
❌ ecommerce-everything.md (500 lines)
```

Use composition:
```
✅ ecommerce-catalog.md (Product management patterns)
✅ ecommerce-cart.md (Shopping cart patterns)
✅ ecommerce-checkout.md (Checkout flow patterns)
✅ ecommerce-fulfillment.md (Order processing patterns)
```

**Benefits:**

| Benefit | Impact |
|---------|--------|
| **Focused** | Each skill addresses one concern |
| **Reusable** | Catalog patterns work for any e-commerce platform |
| **Maintainable** | Updates to checkout don't affect catalog |
| **Selective loading** | Only load skills needed for the project |

**Sources:** [skills/base.md:54-68]()

### Integration with CI/CD

Custom commands can integrate with CI/CD pipelines:

**Example: GitHub Actions Integration**

```yaml
# .github/workflows/custom-audit.yml
name: Custom Quality Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Claude
        run: |
          git clone https://github.com/alinaqi/claude-bootstrap.git ~/.claude-bootstrap
          cd ~/.claude-bootstrap && ./install.sh
      
      - name: Run Custom Audit
        run: claude /audit-quality --strict --report
      
      - name: Upload Report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: audit-report.md
```

**Sources:** [README.md:515-530]()

### Skill Override Patterns

Projects can override global skills with project-specific versions:

**Override mechanism:**

1. Global skill: `~/.claude/skills/react-web.md`
2. Project override: `.claude/skills/react-web.md` (custom version)
3. Claude loads project version first (takes precedence)

**Use cases:**

| Use Case | Pattern |
|----------|---------|
| **Company standards** | Override `base.md` with company-specific limits |
| **Client requirements** | Override `security.md` with client security policies |
| **Legacy projects** | Override framework skills for older versions |

**Implementation:**

```bash
# Copy global skill to project
cp ~/.claude/skills/base.md .claude/skills/

# Edit project version
vim .claude/skills/base.md

# Modify limits for this specific project
# (e.g., 30 lines per function instead of 20)

# Commit project-specific skill
git add .claude/skills/base.md
git commit -m "Add project-specific complexity limits"
```

**Sources:** [skills/base.md:1-20]()

---

## Summary Table: Extension Points

| Extension Type | File Location | Update Method | Distribution |
|----------------|---------------|---------------|--------------|
| **Core skill** | `~/.claude-bootstrap/skills/` | `./install.sh` | Copied to all projects on init |
| **Custom skill** | `~/.claude-bootstrap/skills/` | `./install.sh` | Copied to projects on init (if selected) |
| **Project skill override** | `.claude/skills/` | Manual copy + edit | Project-specific, committed to repo |
| **Global command** | `~/.claude-bootstrap/commands/` | `./install.sh` | Available in all projects |
| **Project template** | `~/.claude-bootstrap/templates/` | `./install.sh` | Used during initialization |
| **Workflow template** | `~/.claude-bootstrap/templates/workflows/` | `./install.sh` | Copied to `.github/workflows/` on init |

**Sources:** [install.sh:1-66](), [README.md:296-317](), [skills/base.md:99-135]()