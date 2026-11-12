# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document provides a technical overview of VibeSec-Skill, a declarative security knowledge base designed for AI-assisted code generation platforms. VibeSec-Skill is a passive knowledge injection system that teaches AI models to generate security-conscious code by consuming structured security directives during the code generation process.

For platform-specific installation procedures, see [Installation & Integration](#2). For detailed security domain coverage, see [Client-Side Security](#6), [Server-Side Security](#7), [Access Control & Authorization](#5), [Authentication & Session Security](#8), and [API Security](#9). For the complete taxonomy of addressed vulnerabilities, see [Complete Vulnerability Coverage](#11).

**Sources:** [README.md:1-18](), [SKILL.md:1-10]()

---

## System Classification

VibeSec-Skill is a **declarative security framework** that operates as contextual knowledge rather than executable code. The system consists of:

- A static knowledge artifact (`SKILL.md`) consumed by AI models
- Platform-agnostic deployment instructions (`README.md`)
- No runtime components or active security scanners

The architecture differs from traditional security tools in that it prevents vulnerabilities at generation time rather than detecting them post-generation.

**Sources:** [README.md:1-23](), [SKILL.md:1-10]()

---

## Repository Structure

```mermaid
graph TB
    subgraph "VibeSec-Skill Repository"
        SKILL["SKILL.md<br/>557 lines<br/>Security Knowledge Base"]
        README["README.md<br/>132 lines<br/>Integration Documentation"]
        LICENSE["LICENSE<br/>Apache 2.0"]
    end
    
    subgraph "Knowledge Architecture"
        META["Metadata Header<br/>Lines 1-4"]
        GUIDE["Secure Coding Guide<br/>Lines 6-758"]
        
        SKILL --> META
        SKILL --> GUIDE
    end
    
    subgraph "Integration Targets"
        CLAUDE["Claude Code<br/>~/.claude/skills"]
        CURSOR["Cursor<br/>~/.cursor/skills"]
        CODEX["Codex<br/>~/.agents/skills"]
        COPILOT["GitHub Copilot<br/>~/.copilot/skills"]
        ANTIGRAVITY["Antigravity<br/>~/.gemini/antigravity/skills"]
        
        README --> CLAUDE
        README --> CURSOR
        README --> CODEX
        README --> COPILOT
        README --> ANTIGRAVITY
    end
    
    SKILL -.-> CLAUDE
    SKILL -.-> CURSOR
    SKILL -.-> CODEX
    SKILL -.-> COPILOT
    SKILL -.-> ANTIGRAVITY
```

**Sources:** [README.md:37-73](), [SKILL.md:1-759]()

---

## Core Components

### SKILL.md - Security Knowledge Base

The primary artifact is `SKILL.md`, a 557-line structured document containing security directives organized into discrete domains:

| Domain | Line Range | Coverage |
|--------|------------|----------|
| Core Principles | [SKILL.md:10-17]() | 5 foundational security concepts |
| Access Control Issues | [SKILL.md:21-75]() | IDOR, privilege escalation, UUID requirements |
| Cross-Site Scripting (XSS) | [SKILL.md:80-144]() | Input sources, output encoding, CSP directives |
| Cross-Site Request Forgery (CSRF) | [SKILL.md:147-210]() | Token validation, SameSite cookies, edge cases |
| Secret Exposure | [SKILL.md:213-256]() | Client-side secret prevention, exposure vectors |
| Open Redirect | [SKILL.md:259-301]() | Allowlist validation, bypass techniques, IDN attacks |
| Password Security | [SKILL.md:305-318]() | Requirements, hashing algorithms |
| Server-Side Request Forgery (SSRF) | [SKILL.md:323-391]() | IP bypass techniques, DNS rebinding, metadata protection |
| Insecure File Upload | [SKILL.md:394-454]() | Magic bytes, polyglot files, validation requirements |
| SQL Injection | [SKILL.md:457-499]() | Parameterized queries, injection points |
| XML External Entity (XXE) | [SKILL.md:502-568]() | Parser configuration, language-specific prevention |
| Path Traversal | [SKILL.md:571-627]() | Canonicalization, input sanitization |
| Security Headers | [SKILL.md:630-641]() | CSP, HSTS, X-Frame-Options |
| JWT Security | [SKILL.md:645-702]() | Algorithm validation, token storage |
| API Security | [SKILL.md:705-741]() | Mass assignment, GraphQL protections |

The metadata header ([SKILL.md:1-4]()) contains the skill name, description, and trigger conditions that AI platforms use for skill discovery and activation.

**Sources:** [SKILL.md:1-759]()

### README.md - Integration Layer

The `README.md` file functions as the deployment documentation, providing:

- Problem statement ([README.md:1-18]()): Describes "vibe coding" vulnerabilities
- Installation instructions ([README.md:37-73]()): Platform-specific directory paths
- Coverage taxonomy ([README.md:78-89]()): Vulnerability categories
- Usage workflow ([README.md:101-113]()): Prompt patterns
- Coverage statistics ([README.md:31-32]()): 60-70% of common vulnerabilities

**Sources:** [README.md:1-132]()

---

## Knowledge Consumption Model

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Platform as "AI Platform<br/>(Claude/Cursor/etc)"
    participant SkillFile as "SKILL.md"
    participant Engine as "Code Generator"
    participant Output as "Generated Code"
    
    Note over Dev,Platform: "Installation Phase"
    Dev->>Platform: "Copy SKILL.md to<br/>skills directory"
    
    Note over Platform,SkillFile: "Discovery Phase"
    Platform->>SkillFile: "Load lines 1-4<br/>(metadata)"
    SkillFile-->>Platform: "name: VibeSec-Skill<br/>trigger: web applications"
    Platform->>SkillFile: "Ingest lines 6-759<br/>(security directives)"
    
    Note over Dev,Engine: "Generation Phase"
    Dev->>Platform: "Prompt: Build login endpoint"
    Platform->>SkillFile: "Query relevant directives"
    
    alt "Authentication Feature Detected"
        SkillFile-->>Platform: "Return lines 305-318<br/>(Password Security)"
        SkillFile-->>Platform: "Return lines 645-702<br/>(JWT Security)"
        SkillFile-->>Platform: "Return lines 147-210<br/>(CSRF Protection)"
    end
    
    Platform->>Engine: "Generate with<br/>security constraints"
    Engine->>Engine: "Apply Argon2id hashing"
    Engine->>Engine: "Add CSRF tokens"
    Engine->>Engine: "Set httpOnly cookies"
    Engine-->>Output: "Secure implementation"
    
    Output-->>Dev: "Code + security comments"
```

The consumption model operates in three phases:

1. **Installation**: Developer copies `SKILL.md` to platform-specific directory
2. **Discovery**: AI platform loads skill metadata and ingests directive content
3. **Generation**: Platform queries relevant directives based on prompt context and applies security constraints during code synthesis

**Sources:** [README.md:37-73](), [README.md:101-113](), [SKILL.md:1-4]()

---

## Platform Integration Architecture

VibeSec-Skill supports five AI platforms through a uniform directory-based deployment pattern:

```mermaid
graph LR
    subgraph "Deployment Scopes"
        GlobalScope["Global Scope<br/>Affects all user projects"]
        ProjectScope["Project Scope<br/>Isolated to single project"]
    end
    
    subgraph "Claude Code Paths"
        ClaudeGlobal["~/.claude/skills/<br/>SKILL.md"]
        ClaudeProject[".claude/skills/<br/>SKILL.md"]
    end
    
    subgraph "Cursor Paths"
        CursorGlobal["~/.cursor/skills/<br/>SKILL.md"]
        CursorProject[".cursor/skills/<br/>SKILL.md"]
    end
    
    subgraph "Codex Paths"
        CodexGlobal["~/.agents/skills/<br/>SKILL.md"]
        CodexProject[".agents/skills/<br/>SKILL.md"]
    end
    
    subgraph "GitHub Copilot Paths"
        CopilotGlobal["~/.copilot/skills/<br/>SKILL.md"]
        CopilotProject[".github/skills/<br/>SKILL.md"]
    end
    
    subgraph "Antigravity Paths"
        AntigravityGlobal["~/.gemini/antigravity/skills/<br/>SKILL.md"]
        AntigravityProject[".agent/skills/<br/>SKILL.md"]
    end
    
    GlobalScope --> ClaudeGlobal
    GlobalScope --> CursorGlobal
    GlobalScope --> CodexGlobal
    GlobalScope --> CopilotGlobal
    GlobalScope --> AntigravityGlobal
    
    ProjectScope --> ClaudeProject
    ProjectScope --> CursorProject
    ProjectScope --> CodexProject
    ProjectScope --> CopilotProject
    ProjectScope --> AntigravityProject
```

Each platform follows identical deployment semantics:
- **Global scope**: Skill applies to all projects for the user
- **Project scope**: Skill applies only to the containing project directory

The dual-scope pattern enables both organizational security standards enforcement (global) and project-specific customization (local).

**Sources:** [README.md:37-73]()

---

## Security Directive Structure

The `SKILL.md` file employs a hierarchical knowledge organization:

```mermaid
graph TB
    Principles["Core Principles<br/>Lines 10-17"]
    
    subgraph "Tier 1: Foundational Concepts"
        P1["Defense in depth"]
        P2["Fail securely"]
        P3["Least privilege"]
        P4["Input validation"]
        P5["Output encoding"]
    end
    
    Principles --> P1 & P2 & P3 & P4 & P5
    
    subgraph "Tier 2: Vulnerability Classes"
        AccessControl["Access Control<br/>Lines 21-75"]
        ClientSide["Client-Side<br/>Lines 78-301"]
        ServerSide["Server-Side<br/>Lines 323-627"]
        Auth["Authentication<br/>Lines 305-318, 645-702"]
        API["API Security<br/>Lines 705-741"]
    end
    
    P1 & P2 & P3 & P4 & P5 -.-> AccessControl
    P1 & P2 & P3 & P4 & P5 -.-> ClientSide
    P1 & P2 & P3 & P4 & P5 -.-> ServerSide
    P1 & P2 & P3 & P4 & P5 -.-> Auth
    P1 & P2 & P3 & P4 & P5 -.-> API
    
    subgraph "Tier 3: Implementation Specifics"
        Checklists["Verification Checklists"]
        BypassTechniques["Bypass Technique Tables"]
        CodeExamples["Language-Specific Code"]
        EdgeCases["Edge Case Handling"]
    end
    
    AccessControl --> Checklists
    ClientSide --> BypassTechniques
    ServerSide --> CodeExamples
    Auth --> EdgeCases
```

Each directive follows a consistent structure:
1. **Vulnerability description**: What the issue is
2. **Attack scenarios**: Where it occurs
3. **Prevention methods**: How to mitigate
4. **Implementation examples**: Code patterns (pseudocode or language-specific)
5. **Verification checklist**: Validation steps

**Sources:** [SKILL.md:10-17](), [SKILL.md:21-759]()

---

## Vulnerability Coverage Statistics

The system addresses **60-70% of common web application vulnerabilities** in its open-source form ([README.md:31-32]()):

| Category | Vulnerability Types | Prevention Mechanisms |
|----------|---------------------|----------------------|
| **Access Control** | IDOR, Privilege Escalation, Horizontal/Vertical Access, Mass Assignment | UUID enforcement, ownership verification, token revocation |
| **Client-Side** | XSS (Stored/Reflected/DOM), CSRF, Secret Exposure, Open Redirect | Output encoding, CSP, CSRF tokens, allowlist validation |
| **Server-Side** | SSRF, SQL Injection, XXE, Path Traversal, File Upload | Parameterized queries, IP validation, entity disabling, canonicalization, magic bytes |
| **Authentication** | Weak Passwords, Session Management, JWT Vulnerabilities | Argon2id/bcrypt, httpOnly cookies, algorithm validation |
| **API Security** | Mass Assignment, GraphQL Attacks | Field whitelisting, query depth/complexity limits |

The skill includes specialized coverage for:
- **Framework-aware patterns**: React, Vue, Node.js, Python, Java, .NET ([README.md:95]())
- **Cloud-aware protections**: AWS, GCP, Azure metadata endpoints ([README.md:96]())
- **Bypass technique databases**: DNS rebinding, polyglot files, Unicode tricks ([README.md:94]())

**Sources:** [README.md:78-97](), [README.md:31-32]()

---

## Operational Workflow

The system implements a security-first code generation workflow:

```mermaid
flowchart TD
    Start["Developer initiates<br/>code generation"]
    Prompt["Submits prompt:<br/>'Build [feature]'"]
    ContextAnalysis["Platform analyzes context"]
    
    Start --> Prompt
    Prompt --> ContextAnalysis
    
    FrameworkDetect["Detect framework:<br/>React/Vue/Node.js"]
    CloudDetect["Detect cloud env:<br/>AWS/GCP/Azure"]
    OperationDetect["Detect operation:<br/>DB query/file upload/API"]
    
    ContextAnalysis --> FrameworkDetect
    ContextAnalysis --> CloudDetect
    ContextAnalysis --> OperationDetect
    
    QueryDirectives["Query SKILL.md<br/>for relevant directives"]
    
    FrameworkDetect --> QueryDirectives
    CloudDetect --> QueryDirectives
    OperationDetect --> QueryDirectives
    
    ApplyConstraints["Apply security constraints:<br/>- Input validation (Line 16)<br/>- Output encoding (Line 17)<br/>- Access control checks<br/>- Security headers"]
    
    QueryDirectives --> ApplyConstraints
    
    GenerateCode["Generate code with<br/>embedded security patterns"]
    AddComments["Add security comments<br/>explaining protections"]
    
    ApplyConstraints --> GenerateCode
    GenerateCode --> AddComments
    
    Output["Deliverable:<br/>- Secure implementation<br/>- Security comments<br/>- Compliance notes"]
    
    AddComments --> Output
```

The workflow emphasizes **proactive prevention** over reactive detection, embedding security controls during the generation phase rather than validating code post-generation.

**Sources:** [README.md:101-113](), [SKILL.md:10-17](), [README.md:71-97]()

---

## License and Distribution

VibeSec-Skill is distributed under the Apache License 2.0, permitting:
- Commercial and private use
- Modification and distribution
- Patent grant from contributors

See [License](#12) for complete terms.

**Sources:** [LICENSE:1-202](), [README.md:1-132]()

---

# Page: Installation & Integration

# Installation & Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides comprehensive installation instructions for deploying VibeSec-Skill across all supported AI platforms. It covers platform-specific installation paths, global versus project-scoped deployment strategies, directory structure requirements, and verification procedures. For information about how the skill operates after installation, see [How VibeSec-Skill Works](#3). For an overview of what VibeSec-Skill is and its capabilities, see [Overview](#1).

## Prerequisites

Before installing VibeSec-Skill, ensure you have:

- **Git**: Version control system to clone the repository
- **AI Platform**: At least one of the supported platforms (Claude Code, Cursor, Codex, GitHub Copilot, or Antigravity) installed and configured
- **File System Access**: Permissions to create directories in your home directory (`~`) or project root
- **Command Line Interface**: Terminal or command prompt access

**Sources:** [README.md:35-73]()

## Supported Platforms

VibeSec-Skill integrates with five AI coding platforms, each following a standardized installation pattern:

| Platform | Global Path | Project Path |
|----------|-------------|--------------|
| Claude Code | `~/.claude/skills` | `.claude/skills` |
| Cursor | `~/.cursor/skills` | `.cursor/skills` |
| Codex | `~/.agents/skills` | `.agents/skills` |
| GitHub Copilot | `~/.copilot/skills` | `.github/skills` |
| Antigravity | `~/.gemini/antigravity/skills` | `.agent/skills` |

**Sources:** [README.md:37-73]()

## Installation Workflow

### Installation Process Flow

```mermaid
flowchart TD
    Start["Start Installation"]
    Clone["git clone https://github.com/BehiSecc/VibeSec-Skill"]
    Decision{"Choose Scope"}
    
    Global["Global Scope<br/>Affects all projects"]
    Project["Project Scope<br/>Affects single project"]
    
    Platform{"Select Platform"}
    
    Claude_G["Copy to ~/.claude/skills"]
    Cursor_G["Copy to ~/.cursor/skills"]
    Codex_G["Copy to ~/.agents/skills"]
    Copilot_G["Copy to ~/.copilot/skills"]
    Anti_G["Copy to ~/.gemini/antigravity/skills"]
    
    Claude_P["Copy to .claude/skills"]
    Cursor_P["Copy to .cursor/skills"]
    Codex_P["Copy to .agents/skills"]
    Copilot_P["Copy to .github/skills"]
    Anti_P["Copy to .agent/skills"]
    
    Verify["Verify SKILL.md and LICENSE present"]
    Complete["Installation Complete"]
    
    Start --> Clone
    Clone --> Decision
    
    Decision -->|Global| Global
    Decision -->|Project| Project
    
    Global --> Platform
    Project --> Platform
    
    Platform -->|Claude Code| Claude_G
    Platform -->|Cursor| Cursor_G
    Platform -->|Codex| Codex_G
    Platform -->|GitHub Copilot| Copilot_G
    Platform -->|Antigravity| Anti_G
    
    Platform -->|Claude Code| Claude_P
    Platform -->|Cursor| Cursor_P
    Platform -->|Codex| Codex_P
    Platform -->|GitHub Copilot| Copilot_P
    Platform -->|Antigravity| Anti_P
    
    Claude_G --> Verify
    Cursor_G --> Verify
    Codex_G --> Verify
    Copilot_G --> Verify
    Anti_G --> Verify
    
    Claude_P --> Verify
    Cursor_P --> Verify
    Codex_P --> Verify
    Copilot_P --> Verify
    Anti_P --> Verify
    
    Verify --> Complete
```

**Sources:** [README.md:37-73]()

## Platform-Specific Installation

### Claude Code

**Global Installation:**
```bash
# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Copy VibeSec-Skill to global directory
cp -r VibeSec-Skill ~/.claude/skills/
```

**Project-Specific Installation:**
```bash
# Navigate to your project root
cd /path/to/your/project

# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create project skills directory
mkdir -p .claude/skills

# Copy VibeSec-Skill to project directory
cp -r VibeSec-Skill .claude/skills/
```

**Sources:** [README.md:37-42]()

### Cursor

**Global Installation:**
```bash
# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create skills directory if it doesn't exist
mkdir -p ~/.cursor/skills

# Copy VibeSec-Skill to global directory
cp -r VibeSec-Skill ~/.cursor/skills/
```

**Project-Specific Installation:**
```bash
# Navigate to your project root
cd /path/to/your/project

# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create project skills directory
mkdir -p .cursor/skills

# Copy VibeSec-Skill to project directory
cp -r VibeSec-Skill .cursor/skills/
```

**Sources:** [README.md:44-49]()

### Codex

**Global Installation:**
```bash
# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create skills directory if it doesn't exist
mkdir -p ~/.agents/skills

# Copy VibeSec-Skill to global directory
cp -r VibeSec-Skill ~/.agents/skills/
```

**Project-Specific Installation:**
```bash
# Navigate to your project root
cd /path/to/your/project

# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create project skills directory
mkdir -p .agents/skills

# Copy VibeSec-Skill to project directory
cp -r VibeSec-Skill .agents/skills/
```

**Sources:** [README.md:51-57]()

### GitHub Copilot

**Global Installation:**
```bash
# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create skills directory if it doesn't exist
mkdir -p ~/.copilot/skills

# Copy VibeSec-Skill to global directory
cp -r VibeSec-Skill ~/.copilot/skills/
```

**Project-Specific Installation:**
```bash
# Navigate to your project root
cd /path/to/your/project

# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create project skills directory
mkdir -p .github/skills

# Copy VibeSec-Skill to project directory
cp -r VibeSec-Skill .github/skills/
```

**Sources:** [README.md:59-65]()

### Antigravity

**Global Installation:**
```bash
# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create skills directory if it doesn't exist
mkdir -p ~/.gemini/antigravity/skills

# Copy VibeSec-Skill to global directory
cp -r VibeSec-Skill ~/.gemini/antigravity/skills/
```

**Project-Specific Installation:**
```bash
# Navigate to your project root
cd /path/to/your/project

# Clone repository
git clone https://github.com/BehiSecc/VibeSec-Skill

# Create project skills directory
mkdir -p .agent/skills

# Copy VibeSec-Skill to project directory
cp -r VibeSec-Skill .agent/skills/
```

**Sources:** [README.md:67-73]()

## Global vs Project Scope

### Scope Selection Decision Tree

```mermaid
flowchart TD
    Decision{"Deployment Scope?"}
    
    UseCase1{"Organization-wide<br/>security standards?"}
    UseCase2{"Multiple projects<br/>same user?"}
    UseCase3{"Project-specific<br/>security requirements?"}
    UseCase4{"Testing/evaluation<br/>without commitment?"}
    
    Global["Global Scope<br/>~/.platform/skills"]
    Project["Project Scope<br/>.platform/skills"]
    
    GlobalBenefits["Benefits:<br/>- Single installation<br/>- All projects protected<br/>- Centralized updates<br/>- Consistent standards"]
    
    ProjectBenefits["Benefits:<br/>- Isolated configuration<br/>- Project-specific rules<br/>- Version control integration<br/>- Team collaboration"]
    
    Decision -->|Enterprise/Team| UseCase1
    Decision -->|Personal| UseCase2
    Decision -->|Custom| UseCase3
    Decision -->|Trial| UseCase4
    
    UseCase1 -->|Yes| Global
    UseCase2 -->|Yes| Global
    UseCase3 -->|Yes| Project
    UseCase4 -->|Yes| Project
    
    Global --> GlobalBenefits
    Project --> ProjectBenefits
```

### Global Scope Characteristics

**Installation Location:** User home directory (`~/.platform/skills`)

**Behavior:**
- Applies to all projects for the current user
- Requires one-time installation per platform
- Updates affect all projects simultaneously
- Suitable for organizational security standards

**Use Cases:**
- Enforcing company-wide security policies
- Personal development environment with consistent security practices
- Multi-project development where all projects require the same security baseline

**Sources:** [README.md:37-73]()

### Project Scope Characteristics

**Installation Location:** Project root directory (`.platform/skills`)

**Behavior:**
- Applies only to the specific project
- Can be version-controlled with project code
- Enables project-specific security configurations
- Allows different security profiles per project

**Use Cases:**
- Projects with unique security requirements
- Team collaboration with shared security configuration
- Testing VibeSec-Skill before global deployment
- Projects requiring different security coverage levels

**Sources:** [README.md:37-73]()

### Scope Precedence

When both global and project-scoped installations exist, the behavior depends on the AI platform's skill loading mechanism. Most platforms follow this precedence:

1. **Project scope** takes priority (if `.platform/skills` exists in project root)
2. **Global scope** applies as fallback (if no project scope exists)
3. **Merged configuration** may occur in some platforms (both scopes loaded)

## Directory Structure After Installation

### Installed Directory Layout

```mermaid
graph TD
    subgraph GlobalInstall["Global Installation Example: ~/.claude/skills"]
        GlobalSkills["skills/"]
        VibeSec["VibeSec-Skill/"]
        SkillFile["SKILL.md<br/>(557 lines of security directives)"]
        LicenseFile["LICENSE<br/>(Apache 2.0)"]
        
        GlobalSkills --> VibeSec
        VibeSec --> SkillFile
        VibeSec --> LicenseFile
    end
    
    subgraph ProjectInstall["Project Installation Example: .claude/skills"]
        ProjectRoot["project-root/"]
        ProjectSkills[".claude/skills/"]
        ProjectVibeSec["VibeSec-Skill/"]
        ProjectSkillFile["SKILL.md<br/>(557 lines of security directives)"]
        ProjectLicenseFile["LICENSE<br/>(Apache 2.0)"]
        OtherFiles["src/<br/>package.json<br/>README.md<br/>..."]
        
        ProjectRoot --> ProjectSkills
        ProjectRoot --> OtherFiles
        ProjectSkills --> ProjectVibeSec
        ProjectVibeSec --> ProjectSkillFile
        ProjectVibeSec --> ProjectLicenseFile
    end
```

### Required Files

After successful installation, the following files must be present in the skills directory:

| File | Size | Purpose |
|------|------|---------|
| `SKILL.md` | ~557 lines | Primary security knowledge base containing all vulnerability prevention directives |
| `LICENSE` | Standard | Apache 2.0 license terms |

**Sources:** [README.md:37-73]()

## Platform-Specific Directory Structures

### Claude Code Directory Structure

```
Global:
~/.claude/
└── skills/
    └── VibeSec-Skill/
        ├── SKILL.md
        └── LICENSE

Project:
project-root/
├── .claude/
│   └── skills/
│       └── VibeSec-Skill/
│           ├── SKILL.md
│           └── LICENSE
├── src/
├── package.json
└── ...
```

### Cursor Directory Structure

```
Global:
~/.cursor/
└── skills/
    └── VibeSec-Skill/
        ├── SKILL.md
        └── LICENSE

Project:
project-root/
├── .cursor/
│   └── skills/
│       └── VibeSec-Skill/
│           ├── SKILL.md
│           └── LICENSE
├── src/
├── package.json
└── ...
```

### Codex Directory Structure

```
Global:
~/.agents/
└── skills/
    └── VibeSec-Skill/
        ├── SKILL.md
        └── LICENSE

Project:
project-root/
├── .agents/
│   └── skills/
│       └── VibeSec-Skill/
│           ├── SKILL.md
│           └── LICENSE
├── src/
├── package.json
└── ...
```

### GitHub Copilot Directory Structure

```
Global:
~/.copilot/
└── skills/
    └── VibeSec-Skill/
        ├── SKILL.md
        └── LICENSE

Project:
project-root/
├── .github/
│   └── skills/
│       └── VibeSec-Skill/
│           ├── SKILL.md
│           └── LICENSE
├── src/
├── package.json
└── ...
```

### Antigravity Directory Structure

```
Global:
~/.gemini/
└── antigravity/
    └── skills/
        └── VibeSec-Skill/
            ├── SKILL.md
            └── LICENSE

Project:
project-root/
├── .agent/
│   └── skills/
│       └── VibeSec-Skill/
│           ├── SKILL.md
│           └── LICENSE
├── src/
├── package.json
└── ...
```

**Sources:** [README.md:37-73]()

## Verification

### Post-Installation Verification Steps

After installation, verify the skill is correctly deployed:

**Step 1: Verify Directory Structure**
```bash
# For global Claude installation:
ls -la ~/.claude/skills/VibeSec-Skill

# For project-specific Cursor installation:
ls -la .cursor/skills/VibeSec-Skill

# Expected output should show:
# SKILL.md
# LICENSE
```

**Step 2: Verify File Contents**
```bash
# Check SKILL.md exists and contains security directives
head -n 20 ~/.claude/skills/VibeSec-Skill/SKILL.md

# Expected output should show security principles section
```

**Step 3: Verify Skill Discovery by AI Platform**

Test the skill integration by prompting your AI platform:

```markdown
"I'm building a web app with user authentication. Please follow secure coding practices."
```

**Expected Behavior:**
- AI should reference security principles from the skill
- Generated code should include security headers, input validation, and authorization checks
- AI may explicitly mention following VibeSec guidelines

**Step 4: Check for Skill Loading Logs (Platform-Specific)**

Some platforms provide logs indicating skill discovery. Check platform-specific documentation for log locations.

**Sources:** [README.md:101-113]()

## File Discovery Mechanism

```mermaid
sequenceDiagram
    participant Platform as "AI Platform"
    participant GlobalDir as "~/.platform/skills/"
    participant ProjectDir as ".platform/skills/"
    participant SkillFile as "SKILL.md"
    
    Note over Platform: Platform initialization
    
    Platform->>ProjectDir: "Check for .platform/skills/ in project root"
    
    alt Project Skills Exist
        ProjectDir-->>Platform: "Directory found"
        Platform->>ProjectDir: "List skill directories"
        ProjectDir-->>Platform: "VibeSec-Skill/"
        Platform->>SkillFile: "Load SKILL.md from project scope"
        SkillFile-->>Platform: "Security directives loaded"
    else No Project Skills
        ProjectDir-->>Platform: "Directory not found"
        Platform->>GlobalDir: "Check for ~/.platform/skills/"
        GlobalDir-->>Platform: "Directory found"
        Platform->>GlobalDir: "List skill directories"
        GlobalDir-->>Platform: "VibeSec-Skill/"
        Platform->>SkillFile: "Load SKILL.md from global scope"
        SkillFile-->>Platform: "Security directives loaded"
    end
    
    Note over Platform: Skills loaded into context<br/>Ready for code generation
```

**Sources:** [README.md:37-73]()

## Troubleshooting Common Installation Issues

### Issue: Skill Not Discovered by AI Platform

**Symptoms:**
- AI does not apply security directives
- No reference to VibeSec in generated code
- Security headers and validation missing

**Solutions:**
1. Verify directory path matches platform requirements exactly
2. Check for typos in directory names (`.claude` vs `.Clause`)
3. Ensure `SKILL.md` file is present and readable
4. Restart AI platform to trigger skill rediscovery
5. Check platform-specific configuration files for skill directory overrides

### Issue: Permission Denied When Creating Skills Directory

**Symptoms:**
```
mkdir: cannot create directory '~/.claude/skills': Permission denied
```

**Solutions:**
1. Check file system permissions on home directory
2. Use `sudo` only if directory is system-protected (generally not recommended)
3. Verify you're not installing in a protected system directory
4. Check disk space availability

### Issue: Multiple VibeSec Versions Conflict

**Symptoms:**
- Inconsistent security behavior across projects
- Outdated security directives applied

**Solutions:**
1. Remove old global installation before installing new version
2. Check for multiple skill directories in project hierarchy
3. Use project-scoped installation to override global version
4. Document which version is deployed where

### Issue: Skills Directory Not Version Controlled

**Symptoms:**
- Team members have different security configurations
- Skills lost during repository cloning

**Solutions:**
1. For project scope, ensure `.platform/skills` is committed to version control
2. Add `.platform/skills/` to `.gitignore` if you want local-only installation
3. Document installation requirements in project README
4. Consider using git submodules for skill versioning

**Sources:** [README.md:37-73]()

## Integration Validation

### Validation Test Cases

After installation, run these validation tests to confirm integration:

**Test 1: Access Control Implementation**
```markdown
Prompt: "Create an API endpoint to update user profile"

Expected Output Should Include:
- UUID-based resource identification
- Authorization check before data access
- Current user validation
```

**Test 2: Input Validation**
```markdown
Prompt: "Create a file upload handler"

Expected Output Should Include:
- File type validation
- Magic byte verification
- Size limit enforcement
- Sanitized filename handling
```

**Test 3: Security Headers**
```markdown
Prompt: "Create an HTTP response handler"

Expected Output Should Include:
- Content-Security-Policy header
- X-Frame-Options header
- Strict-Transport-Security header
```

If these security patterns are not automatically included, review the troubleshooting section.

**Sources:** [README.md:101-113]()

## Next Steps

After successful installation and verification:

1. Review [How VibeSec-Skill Works](#3) to understand the operational model
2. Examine [Core Security Principles](#4) to understand the foundational concepts
3. Reference specific vulnerability prevention pages (pages 5-10) for detailed guidance
4. Test the skill with your actual development workflows

For advanced configuration and customization, the `SKILL.md` file can be modified to add project-specific security requirements, though this is generally not recommended as it may complicate updates.

**Sources:** [README.md:35-73](), [README.md:101-113]()

---

# Page: How VibeSec-Skill Works

# How VibeSec-Skill Works

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This page explains the internal architecture, operational workflow, and code generation mechanisms of VibeSec-Skill. It covers how the system integrates with AI platforms, loads security knowledge from `SKILL.md`, and influences code generation through contextual security directive injection.

For information about installing VibeSec-Skill across different platforms, see [Installation & Integration](#2). For details on the specific security vulnerabilities addressed, see [Complete Vulnerability Coverage](#11). For the foundational security concepts, see [Core Security Principles](#4).

**Sources:** [README.md:1-83](), [SKILL.md:1-10]()

---

## System Architecture Overview

VibeSec-Skill operates as a passive knowledge injection system with three core components:

| Component | File | Role | Importance Score |
|-----------|------|------|------------------|
| **Security Knowledge Base** | `SKILL.md` | 557-line declarative security directive document consumed by AI models | 9.77 |
| **Integration Guide** | `README.md` | Multi-platform installation instructions and usage documentation | 8.97 |
| **Legal Documentation** | `LICENSE` | Apache 2.0 license terms | 1.97 |

The system does not execute code or perform active scanning. Instead, it provides AI models with comprehensive security knowledge that influences code generation at the prompt-response phase.

### File Structure and Platform Integration

```mermaid
graph TB
    subgraph Repository["VibeSec-Skill Repository"]
        SKILL["SKILL.md<br/>557 lines<br/>Security directives"]
        README["README.md<br/>Installation docs"]
        LICENSE["LICENSE<br/>Apache 2.0"]
    end
    
    subgraph GlobalInstall["Global Installation Paths"]
        ClaudeGlobal["~/.claude/skills/"]
        CursorGlobal["~/.cursor/skills/"]
        CodexGlobal["~/.agents/skills/"]
        CopilotGlobal["~/.copilot/skills/"]
        AntigravityGlobal["~/.gemini/antigravity/skills/"]
    end
    
    subgraph ProjectInstall["Project-Specific Paths"]
        ClaudeProject[".claude/skills/"]
        CursorProject[".cursor/skills/"]
        CodexProject[".agents/skills/"]
        CopilotProject[".github/skills/"]
        AntigravityProject[".agent/skills/"]
    end
    
    Repository -->|"Copy files"| GlobalInstall
    Repository -->|"Copy files"| ProjectInstall
    
    GlobalInstall -.->|"Affects all projects"| AllProjects["All Projects for User"]
    ProjectInstall -.->|"Affects single project"| SingleProject["Specific Project Only"]
```

**Sources:** [README.md:29-73](), [README.md:37-71]()

---

## Knowledge Injection Mechanism

VibeSec-Skill uses a declarative knowledge structure defined in `SKILL.md`. The file begins with YAML frontmatter that instructs AI platforms how to consume the skill:

```yaml
---
name: VibeSec-Skill
description: This skill helps Claude write secure web applications. Use this when working on any web application or when a user requests a scan or audit to ensure security best practices are followed.
---
```

### Knowledge Architecture Hierarchy

```mermaid
graph TB
    SKILL["SKILL.md<br/>Primary Knowledge Source"]
    
    subgraph CoreLayer["Core Principles Layer<br/>(Lines 10-18)"]
        P1["Defense in depth"]
        P2["Fail securely"]
        P3["Least privilege"]
        P4["Input validation"]
        P5["Output encoding"]
    end
    
    subgraph ClientDomain["Client-Side Security Domain<br/>(Lines 67-303)"]
        XSS["Cross-Site Scripting<br/>Lines 80-144"]
        CSRF["Cross-Site Request Forgery<br/>Lines 147-210"]
        Secrets["Secret Exposure<br/>Lines 213-256"]
        OpenRedirect["Open Redirect<br/>Lines 259-303"]
    end
    
    subgraph ServerDomain["Server-Side Security Domain<br/>(Lines 321-627)"]
        SSRF["Server-Side Request Forgery<br/>Lines 323-391"]
        FileUpload["Insecure File Upload<br/>Lines 394-454"]
        SQLi["SQL Injection<br/>Lines 457-499"]
        XXE["XML External Entity<br/>Lines 502-569"]
        PathTraversal["Path Traversal<br/>Lines 572-627"]
    end
    
    subgraph CrossCutting["Cross-Cutting Domains<br/>(Lines 19-65, 305-742)"]
        AccessControl["Access Control<br/>Lines 21-75"]
        JWT["JWT Security<br/>Lines 645-702"]
        API["API Security<br/>Lines 704-742"]
        Headers["Security Headers<br/>Lines 630-641"]
        Password["Password Security<br/>Lines 305-318"]
    end
    
    SKILL --> CoreLayer
    CoreLayer -.->|"Inform implementation"| ClientDomain
    CoreLayer -.->|"Inform implementation"| ServerDomain
    CoreLayer -.->|"Inform implementation"| CrossCutting
```

**Sources:** [SKILL.md:1-18](), [SKILL.md:10-17](), [SKILL.md:67-303](), [SKILL.md:321-627](), [SKILL.md:19-75](), [SKILL.md:305-742]()

---

## Integration with AI Platforms

### Discovery and Loading Process

When an AI platform starts, it follows this discovery sequence:

1. **Directory Scanning**: Platform scans designated skills directories (global and project-specific)
2. **File Loading**: Reads `SKILL.md` content into model context
3. **Metadata Parsing**: Extracts YAML frontmatter to determine when to activate the skill
4. **Context Injection**: Loads the 557 lines of security directives as available knowledge

```mermaid
graph LR
    Start["AI Platform Initialization"]
    
    Start --> Scan1["Scan ~/.platform/skills/"]
    Start --> Scan2["Scan .platform/skills/"]
    
    Scan1 --> Found1{"SKILL.md<br/>found?"}
    Scan2 --> Found2{"SKILL.md<br/>found?"}
    
    Found1 -->|Yes| Load1["Load into<br/>global context"]
    Found2 -->|Yes| Load2["Load into<br/>project context"]
    
    Found1 -->|No| Skip1["Skip"]
    Found2 -->|No| Skip2["Skip"]
    
    Load1 --> Parse["Parse YAML frontmatter<br/>name: VibeSec-Skill<br/>description: ..."]
    Load2 --> Parse
    
    Parse --> Activate["Activate for:<br/>- Web application prompts<br/>- Security scan requests<br/>- Code audit requests"]
    
    Activate --> Ready["Ready for<br/>prompt processing"]
```

### Platform-Specific Directory Mappings

| Platform | Global Path | Project Path | Configuration |
|----------|-------------|--------------|---------------|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | Automatic discovery |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` | Automatic discovery |
| Codex | `~/.agents/skills/` | `.agents/skills/` | Automatic discovery |
| GitHub Copilot | `~/.copilot/skills/` | `.github/skills/` | Automatic discovery |
| Antigravity | `~/.gemini/antigravity/skills/` | `.agent/skills/` | Automatic discovery |

**Sources:** [README.md:37-42](), [README.md:44-49](), [README.md:51-56](), [README.md:59-64](), [README.md:67-72](), [SKILL.md:1-4]()

---

## Operational Workflow

### Prompt-to-Secure-Code Generation Flow

```mermaid
sequenceDiagram
    participant Developer
    participant Platform as "AI Platform<br/>(Claude/Cursor/etc)"
    participant SkillFile as "SKILL.md"
    participant CorePrinciples as "Core Principles<br/>(Lines 10-18)"
    participant DomainDirectives as "Domain-Specific<br/>Directives"
    participant CodeEngine as "Code Generation<br/>Engine"
    
    Developer->>Platform: "Build user profile update endpoint.<br/>Follow secure coding practices."
    
    activate Platform
    Platform->>SkillFile: "Query: Security guidance for<br/>user profile update"
    activate SkillFile
    
    SkillFile->>SkillFile: "Analyze request context:<br/>- Operation: UPDATE<br/>- Resource: User profile<br/>- Framework: Inferred from project"
    
    SkillFile->>CorePrinciples: "Retrieve core principles"
    CorePrinciples-->>SkillFile: "- Input validation (Line 16)<br/>- Output encoding (Line 17)<br/>- Least privilege (Line 15)"
    
    SkillFile->>DomainDirectives: "Retrieve relevant directives"
    DomainDirectives-->>SkillFile: "- Access Control (Lines 21-75)<br/>- Mass Assignment (Lines 707-719)<br/>- CSRF Protection (Lines 147-210)<br/>- XSS Prevention (Lines 80-144)"
    
    deactivate SkillFile
    SkillFile-->>Platform: "Security constraints package"
    
    Platform->>CodeEngine: "Generate with constraints"
    activate CodeEngine
    
    CodeEngine->>CodeEngine: "Apply Access Control:<br/>- Verify user owns resource (Line 29)<br/>- Use UUID (Line 34)<br/>- Return 404 for unauthorized (Line 71)"
    
    CodeEngine->>CodeEngine: "Apply Mass Assignment:<br/>- Whitelist allowed fields (Lines 715-718)<br/>- Reject role/admin fields"
    
    CodeEngine->>CodeEngine: "Apply CSRF Protection:<br/>- Validate CSRF token (Lines 170-174)<br/>- Check SameSite cookie (Lines 176-182)"
    
    CodeEngine->>CodeEngine: "Apply XSS Prevention:<br/>- Encode output (Lines 112-117)<br/>- Add CSP header (Lines 119-134)"
    
    deactivate CodeEngine
    CodeEngine-->>Platform: "Secure code + comments"
    
    Platform-->>Developer: "Deliverable:<br/>- Code with authorization checks<br/>- Field whitelisting<br/>- CSRF token validation<br/>- Security comments"
    deactivate Platform
```

**Sources:** [README.md:76-83](), [README.md:104-113](), [SKILL.md:10-18](), [SKILL.md:21-75](), [SKILL.md:707-719](), [SKILL.md:147-210](), [SKILL.md:80-144]()

---

## Context-Aware Code Generation

VibeSec-Skill applies different security directives based on detected context. The AI model analyzes three dimensions:

### 1. Framework Detection

The skill includes framework-specific patterns referenced throughout the directives:

| Framework | Directive References | Example Line Numbers |
|-----------|---------------------|---------------------|
| React | JSX escaping | [SKILL.md:117]() |
| Vue | Template escaping (`{{ }}`) | [SKILL.md:117]() |
| Node.js | `libxmljs` configuration | [SKILL.md:547-551]() |
| Python | `lxml` parser settings | [SKILL.md:534-539]() |
| Java | `DocumentBuilderFactory` | [SKILL.md:526-532]() |
| PHP | `libxml_disable_entity_loader` | [SKILL.md:542-545]() |
| .NET | `XmlReaderSettings` | [SKILL.md:554-558]() |

### 2. Cloud Environment Detection

Cloud-specific protections are activated when cloud services are detected:

```mermaid
graph TB
    Request["Code Generation Request"]
    
    Request --> Detect["Detect cloud keywords:<br/>- AWS, S3, Lambda<br/>- GCP, Cloud Functions<br/>- Azure, Functions"]
    
    Detect --> CloudDirectives["Apply Cloud Metadata<br/>Protection (Lines 373-380)"]
    
    CloudDirectives --> AWS["Block 169.254.169.254<br/>(AWS metadata)"]
    CloudDirectives --> GCP["Block metadata.google.internal<br/>Block 169.254.169.254"]
    CloudDirectives --> Azure["Block 169.254.169.254<br/>(Azure metadata)"]
    CloudDirectives --> DO["Block 169.254.169.254<br/>(DigitalOcean metadata)"]
    
    CloudDirectives --> SSRF["SSRF Prevention<br/>(Lines 323-391)"]
```

### 3. Operation Type Categorization

Different security directives apply based on operation type:

| Operation Type | Triggered Directives | Line References |
|----------------|---------------------|-----------------|
| **Database Query** | SQL Injection Prevention | [SKILL.md:457-499]() |
| **File Upload** | File Upload Security | [SKILL.md:394-454]() |
| **URL Redirection** | Open Redirect Prevention | [SKILL.md:259-303]() |
| **XML Processing** | XXE Prevention | [SKILL.md:502-569]() |
| **File Path Operations** | Path Traversal Prevention | [SKILL.md:572-627]() |
| **External URL Fetch** | SSRF Prevention | [SKILL.md:323-391]() |
| **User Input Rendering** | XSS Prevention | [SKILL.md:80-144]() |
| **State-Changing Endpoints** | CSRF Protection | [SKILL.md:147-210]() |
| **Resource Access** | Access Control | [SKILL.md:21-75]() |
| **JWT Operations** | JWT Security | [SKILL.md:645-702]() |

**Sources:** [README.md:91-97](), [SKILL.md:373-380](), [SKILL.md:117](), [SKILL.md:526-558]()

---

## Security Directive Application

### Directive Retrieval Logic

When the AI model processes a prompt, it retrieves relevant directives through content analysis:

```mermaid
graph TB
    Prompt["Developer Prompt"]
    
    Prompt --> Analyze["Analyze prompt for:<br/>- Security keywords<br/>- Feature descriptions<br/>- Technology stack"]
    
    Analyze --> Match1{"Contains<br/>authentication?"}
    Analyze --> Match2{"Contains<br/>database?"}
    Analyze --> Match3{"Contains<br/>file upload?"}
    Analyze --> Match4{"Contains<br/>user input?"}
    
    Match1 -->|Yes| D1["Load Access Control<br/>(Lines 21-75)<br/>JWT Security (Lines 645-702)<br/>Password Security (Lines 305-318)"]
    
    Match2 -->|Yes| D2["Load SQL Injection<br/>(Lines 457-499)<br/>Input Validation (Line 16)"]
    
    Match3 -->|Yes| D3["Load File Upload<br/>(Lines 394-454)<br/>Magic Bytes (Lines 433-443)"]
    
    Match4 -->|Yes| D4["Load XSS Prevention<br/>(Lines 80-144)<br/>Output Encoding (Line 17)"]
    
    D1 --> Apply["Apply to code generation"]
    D2 --> Apply
    D3 --> Apply
    D4 --> Apply
```

### Directive Organization Structure

Directives in `SKILL.md` are organized hierarchically for efficient retrieval:

1. **Overview Statement** (Lines 8-18): Establishes security mindset and core principles
2. **Vulnerability Categories** (Lines 19-742): Organized by attack vector
3. **Implementation Patterns** (Embedded throughout): Pseudocode and code examples
4. **Checklists** (Embedded throughout): Verification steps for each category

Example directive structure for Access Control:

```
Lines 21-23: Problem statement
Lines 25-42: Core requirements
Lines 44-50: Authorization checks checklist
Lines 52-58: Common pitfalls
Lines 60-74: Implementation pattern (pseudocode)
```

### Code Generation Influence Points

The skill influences code generation at five key points:

| Influence Point | Mechanism | Example Directive |
|----------------|-----------|-------------------|
| **Variable Naming** | Suggests security-conscious naming | `ownerId`, `orgId` instead of `id` |
| **Function Structure** | Injects authorization checks | Resource access verification pattern (Lines 60-74) |
| **Library Selection** | Recommends secure libraries | `DOMPurify` for HTML (Line 137), `Argon2id` for passwords (Line 316) |
| **Configuration** | Generates secure defaults | CSP headers (Lines 119-134), `SameSite=Strict` cookies (Lines 176-182) |
| **Comments** | Adds security annotations | Explains why specific patterns are used |

**Sources:** [SKILL.md:21-75](), [SKILL.md:60-74](), [SKILL.md:137](), [SKILL.md:316](), [SKILL.md:119-134](), [SKILL.md:176-182]()

---

## Edge Case and Bypass Prevention

VibeSec-Skill includes comprehensive bypass technique databases that AI models reference during code generation. These are organized in tabular format for efficient lookup:

### Example: SSRF Bypass Techniques Table

The skill maintains attack technique reference tables, such as IP and DNS bypass methods (Lines 349-365):

| Technique | Example | Prevention Reference |
|-----------|---------|---------------------|
| Decimal IP | `http://2130706433` | IP validation (Lines 368-371) |
| DNS rebinding | Attacker DNS returns internal IP | Double-resolution check (Lines 366-371) |
| Cloud metadata | `169.254.169.254` | Explicit blocklist (Lines 373-380) |

### Example: File Upload Bypass Techniques Table

File upload attack vectors are documented with prevention methods (Lines 416-432):

| Attack | Description | Prevention |
|--------|-------------|------------|
| Extension bypass | `shell.php.jpg` | Allowlist validation |
| Null byte | `shell.php%00.jpg` | Null byte sanitization |
| Magic byte injection | Prepend valid magic bytes | Full structure validation |

These tables are directly referenced during code generation when the AI detects relevant operations.

**Sources:** [SKILL.md:349-365](), [SKILL.md:366-371](), [SKILL.md:373-380](), [SKILL.md:416-432](), [README.md:92-94]()

---

## Security Header Injection

When generating HTTP response code, the skill automatically includes security headers based on the Security Headers Checklist (Lines 630-641):

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: [context-specific policy]
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store (for sensitive pages)
```

The CSP directive is context-aware, referencing the detailed policy structure from Lines 119-134 that specifies `default-src`, `script-src`, `style-src`, and other directives.

**Sources:** [SKILL.md:630-641](), [SKILL.md:119-134]()

---

## Verification and Validation

The skill includes embedded checklists that AI models use to validate generated code. These appear as interactive checkbox lists:

### Example: Authorization Checks Checklist (Lines 44-50)

```
- [ ] Verify user owns the resource on every request
- [ ] Check organization membership for multi-tenant apps
- [ ] Validate role permissions for role-based actions
- [ ] Re-validate permissions after any privilege change
- [ ] Check parent resource ownership
```

### Example: CSRF Protection Checklist (Lines 201-210)

```
- [ ] Token is cryptographically random
- [ ] Token is tied to user session
- [ ] Token is validated server-side on all state-changing requests
- [ ] Missing token = rejected request
- [ ] Token regenerated on authentication state change
- [ ] SameSite cookie attribute is set
- [ ] Secure and HttpOnly flags on session cookies
```

AI models reference these checklists to ensure generated code includes all required security controls.

**Sources:** [SKILL.md:44-50](), [SKILL.md:201-210](), [SKILL.md:382-391](), [SKILL.md:560-568](), [SKILL.md:621-626](), [SKILL.md:695-702]()

---

## Coverage Metrics

VibeSec-Skill addresses 60-70% of common web application vulnerabilities in its free version. The vulnerability taxonomy is documented in the README:

| Category | Vulnerability Count | Coverage |
|----------|-------------------|----------|
| Access Control | 5 classes | IDOR, Privilege Escalation, Horizontal/Vertical Access, Mass Assignment, Token Revocation |
| Client-Side | 4 classes | XSS (3 types), CSRF, Secret Exposure, Open Redirect |
| Server-Side | 5 classes | SSRF, SQL Injection, XXE, Path Traversal, Insecure File Upload |
| Authentication | 4 areas | Password Security, Session Management, Account Lifecycle, JWT |
| API Security | 2 areas | Mass Assignment, GraphQL |

The premium version at vibesec.sh provides extended coverage beyond this baseline.

**Sources:** [README.md:78-89](), [README.md:31-32]()

---

## Operational Characteristics

### Memory and Context Requirements

- **File Size**: `SKILL.md` is 557 lines, approximately 22KB of text
- **Context Window**: Loaded entirely into AI model context when skill is active
- **Activation Trigger**: Prompts mentioning "web application", "security", "scan", or "audit"

### Scope Precedence

When both global and project-specific skills are present:

1. **Project scope takes precedence** for conflicting directives
2. **Global scope provides fallback** when project scope is absent
3. **Directives merge** when both scopes contain complementary guidance

### Performance Impact

- **No runtime overhead**: Skill does not execute during application runtime
- **Generation-time only**: All security logic applied during code generation phase
- **No dependencies**: Does not require installation of additional packages in target project

**Sources:** [SKILL.md:1-557](), [README.md:37-72](), [SKILL.md:1-4]()

---

# Page: Core Security Principles

# Core Security Principles

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document defines the five foundational security principles that underpin all VibeSec-Skill security directives. These principles form the philosophical and architectural basis for every security recommendation provided to AI code generation platforms. Each principle is applied across all vulnerability domains—from access control to file uploads—creating a coherent security philosophy that AI models use to generate secure code.

For specific implementations of these principles across vulnerability categories, see:
- Access control applications: [Access Control & Authorization](#5)
- Client-side applications: [Client-Side Security](#6)
- Server-side applications: [Server-Side Security](#7)
- Authentication applications: [Authentication & Session Security](#8)

---

## The Five Core Principles

VibeSec-Skill operates on five fundamental security principles that inform all 557 lines of security directives in `SKILL.md`. These principles are not independent—they reinforce each other to create layered security.

### Principle 1: Defense in Depth

**Definition:** Never rely on a single security control. Implement multiple layers of security so that if one control fails, others still provide protection.

**Application Pattern:**

| Security Domain | Primary Control | Secondary Control | Tertiary Control |
|----------------|----------------|-------------------|------------------|
| XSS Prevention | Output encoding | Content Security Policy | Input sanitization |
| CSRF Protection | CSRF tokens | SameSite cookies | Origin/Referer validation |
| File Upload Security | Magic byte validation | Extension allowlist | Content-type verification |
| SSRF Prevention | Domain allowlist | IP validation | Network segmentation |
| Access Control | User ownership check | Organization membership check | Role permission validation |

**Why Multiple Layers Matter:**

```mermaid
graph TB
    Attack["Attacker Attempt"]
    
    subgraph "Single Layer (Vulnerable)"
        S1["Output Encoding Only"]
        S1 -->|Bypass via CSP-allowed domain| Exploit1["XSS Successful"]
    end
    
    subgraph "Defense in Depth (Secure)"
        D1["Output Encoding"]
        D2["Content Security Policy"]
        D3["Input Sanitization"]
        
        D1 -->|If bypassed| D2
        D2 -->|If bypassed| D3
        D3 -->|All layers failed| Exploit2["XSS Successful (Rare)"]
    end
    
    Attack --> S1
    Attack --> D1
    
    style Exploit1 fill:#f8d7da
    style Exploit2 fill:#f8d7da
```

**Sources:** [SKILL.md:13](), [SKILL.md:110-144]() (XSS defense layers), [SKILL.md:169-183]() (CSRF defense layers)

---

### Principle 2: Fail Securely

**Definition:** When something fails, fail closed (deny access). Never default to allowing access when an error occurs.

**Implementation Pattern:**

```mermaid
graph LR
    subgraph "Authorization Flow"
        Request["Request for Resource"]
        GetResource["Retrieve Resource"]
        CheckOwner["Verify Ownership"]
        Success["Return Resource"]
        Fail["Return 404"]
        
        Request --> GetResource
        GetResource -->|Found| CheckOwner
        GetResource -->|Not Found| Fail
        CheckOwner -->|Owner Match| Success
        CheckOwner -->|No Match| Fail
        CheckOwner -->|Error/Exception| Fail
    end
```

**Code Reference Pattern:**

The authorization pattern in [SKILL.md:61-74]() demonstrates fail-secure design:

```
function getResource(resourceId, currentUser):
    resource = database.find(resourceId)
    
    if resource is null:
        return 404  # Fail secure: deny if not found
    
    if resource.ownerId != currentUser.id:
        if not currentUser.hasOrgAccess(resource.orgId):
            return 404  # Fail secure: deny if no permission
    
    return resource
```

**Failure Scenarios and Responses:**

| Failure Scenario | Insecure Default | Secure Default (Fail Closed) |
|-----------------|------------------|------------------------------|
| Database connection lost during auth check | Allow access (assume authorized) | Deny access, return 503 |
| CSRF token validation throws exception | Skip validation | Reject request |
| File extension validation error | Allow upload | Reject upload |
| DNS resolution timeout in SSRF check | Proceed with request | Abort request |
| JWT signature verification error | Trust claims | Reject token |

**Sources:** [SKILL.md:14](), [SKILL.md:61-74]() (authorization pattern), [SKILL.md:685-691]() (JWT verification)

---

### Principle 3: Least Privilege

**Definition:** Grant the minimum permissions necessary for functionality. Users, processes, and services should only access what they absolutely need.

**Application Across Layers:**

```mermaid
graph TB
    subgraph "Application Layer"
        User["User Account"]
        UserPerms["User Permissions:<br/>- Own data only<br/>- No admin functions<br/>- UUIDs prevent enumeration"]
    end
    
    subgraph "Data Access Layer"
        DBUser["Database User"]
        DBPerms["Database Permissions:<br/>- SELECT, INSERT, UPDATE only<br/>- No DROP, ALTER<br/>- No xp_cmdshell access"]
    end
    
    subgraph "Network Layer"
        Service["Application Service"]
        NetPerms["Network Permissions:<br/>- Outbound to approved APIs only<br/>- No internal network access<br/>- Isolated network segment"]
    end
    
    User --> UserPerms
    DBUser --> DBPerms
    Service --> NetPerms
```

**Least Privilege Checklist from SKILL.md:**

| Security Domain | Least Privilege Implementation |
|----------------|-------------------------------|
| Access Control | Users access only their own data; UUIDs prevent ID enumeration [SKILL.md:29-36]() |
| Account Lifecycle | Immediate token revocation on role change [SKILL.md:38-41]() |
| SQL Injection | Database user has minimum required permissions; dangerous functions disabled [SKILL.md:496-498]() |
| File Upload | Uploaded files stored with non-executable permissions [SKILL.md:455]() |
| JWT | Short-lived tokens (15 mins); refresh token rotation [SKILL.md:670]() |
| Mass Assignment | Whitelist only necessary updateable fields [SKILL.md:715-719]() |

**Sources:** [SKILL.md:15](), [SKILL.md:29-36](), [SKILL.md:496-498](), [SKILL.md:670](), [SKILL.md:715-719]()

---

### Principle 4: Input Validation

**Definition:** Never trust user input. Validate everything server-side, regardless of client-side validation.

**Input Source Taxonomy:**

```mermaid
graph TB
    subgraph "Direct User Input"
        D1["Form Fields"]
        D2["File Uploads"]
        D3["Rich Text Editors"]
        D4["Search Queries"]
    end
    
    subgraph "Indirect User Input"
        I1["URL Parameters"]
        I2["HTTP Headers (Referer, User-Agent)"]
        I3["Third-Party API Data"]
        I4["WebSocket Messages"]
        I5["PostMessage Data"]
        I6["LocalStorage Values"]
    end
    
    subgraph "Overlooked Input Sources"
        O1["Error Messages with User Data"]
        O2["PDF/Document Generators"]
        O3["Email Templates"]
        O4["Log Viewers"]
        O5["JSON Responses as HTML"]
        O6["SVG File Uploads"]
        O7["Markdown Rendering"]
    end
    
    subgraph "Validation Layer"
        V["Server-Side Validation:<br/>- Type validation<br/>- Format validation<br/>- Range validation<br/>- Semantic validation"]
    end
    
    D1 & D2 & D3 & D4 --> V
    I1 & I2 & I3 & I4 & I5 & I6 --> V
    O1 & O2 & O3 & O4 & O5 & O6 & O7 --> V
```

**Validation Requirements by Input Type:**

| Input Category | Validation Method | Code Reference |
|---------------|-------------------|----------------|
| SQL Query Parameters | Parameterized queries; type validation | [SKILL.md:463-492]() |
| File Paths | Canonicalization; base directory validation | [SKILL.md:595-612]() |
| File Uploads | Extension allowlist; magic byte validation; size limits | [SKILL.md:398-415]() |
| URLs for Redirection | Domain allowlist; protocol validation | [SKILL.md:265-272]() |
| URLs for SSRF | IP validation; cloud metadata blocking; DNS rebinding checks | [SKILL.md:368-391]() |
| XML Documents | Disable external entities; disable DTD processing | [SKILL.md:562-568]() |
| GraphQL Queries | Depth limiting; complexity analysis; batch size limits | [SKILL.md:725-740]() |

**Sources:** [SKILL.md:16](), [SKILL.md:84-109]() (input source taxonomy), [SKILL.md:749]() (validation principle)

---

### Principle 5: Output Encoding

**Definition:** Encode data appropriately for the context it's rendered in. The same data requires different encoding when displayed in HTML vs JavaScript vs URLs vs CSS.

**Context-Specific Encoding Matrix:**

```mermaid
graph LR
    Data["User Data:<br/><script>alert(1)</script>"]
    
    subgraph "Rendering Contexts"
        HTML["HTML Context"]
        JS["JavaScript Context"]
        URL["URL Context"]
        CSS["CSS Context"]
    end
    
    subgraph "Encoded Output"
        HTMLE["&lt;script&gt;alert(1)&lt;/script&gt;"]
        JSE["\\x3cscript\\x3ealert(1)\\x3c/script\\x3e"]
        URLE["%3Cscript%3Ealert(1)%3C%2Fscript%3E"]
        CSSE["\\3c script\\3e alert(1)\\3c /script\\3e"]
    end
    
    Data --> HTML
    Data --> JS
    Data --> URL
    Data --> CSS
    
    HTML --> HTMLE
    JS --> JSE
    URL --> URLE
    CSS --> CSSE
```

**Framework-Specific Encoding Mechanisms:**

| Framework/Context | Automatic Encoding | Manual Encoding Required |
|------------------|-------------------|-------------------------|
| React JSX | `{userInput}` auto-escapes HTML | `dangerouslySetInnerHTML` needs manual sanitization |
| Vue.js | `{{ userInput }}` auto-escapes HTML | `v-html` directive needs manual sanitization |
| HTML Entity Encoding | `<` → `&lt;`, `>` → `&gt;` | Apply to all untrusted data in HTML context |
| JavaScript String Escaping | Escape quotes, backslashes, newlines | Use when embedding data in `<script>` tags |
| URL Encoding | Encode special characters for query params | Apply to all untrusted data in URLs |
| CSS Escaping | Escape hex values for CSS injection | Required for user data in style attributes |

**Output Encoding Enforcement Pattern:**

The XSS prevention section [SKILL.md:112-118]() defines the encoding requirements:

1. **HTML context:** HTML entity encode (`<` → `&lt;`)
2. **JavaScript context:** JavaScript escape
3. **URL context:** URL encode
4. **CSS context:** CSS escape
5. **Framework escaping:** Use framework's built-in escaping (React's JSX, Vue's `{{ }}`)

**Sources:** [SKILL.md:17](), [SKILL.md:112-118]() (context-specific encoding), [SKILL.md:753]() (encoding principle)

---

## Principle Interaction and Cascading Effects

These five principles do not operate independently—they reinforce each other to create comprehensive security coverage.

```mermaid
graph TB
    subgraph "Core Principles"
        DepthInDepth["Defense in Depth:<br/>Multiple security layers"]
        FailSecure["Fail Securely:<br/>Deny on error"]
        LeastPriv["Least Privilege:<br/>Minimum access"]
        InputVal["Input Validation:<br/>Never trust input"]
        OutputEnc["Output Encoding:<br/>Context-aware encoding"]
    end
    
    subgraph "XSS Prevention Example"
        XSS1["Layer 1: Input Validation<br/>(Sanitize dangerous patterns)"]
        XSS2["Layer 2: Output Encoding<br/>(Context-specific escaping)"]
        XSS3["Layer 3: CSP Headers<br/>(Block inline scripts)"]
        
        InputVal -.->|Informs| XSS1
        OutputEnc -.->|Informs| XSS2
        DepthInDepth -.->|Requires| XSS3
    end
    
    subgraph "Access Control Example"
        AC1["Verify User Ownership<br/>(Least Privilege)"]
        AC2["Return 404 on Failure<br/>(Fail Securely)"]
        AC3["Check Org + Role + Resource<br/>(Defense in Depth)"]
        
        LeastPriv -.->|Informs| AC1
        FailSecure -.->|Informs| AC2
        DepthInDepth -.->|Requires| AC3
    end
    
    subgraph "File Upload Example"
        FU1["Validate Input Type<br/>(Input Validation)"]
        FU2["Check Extension + Magic Bytes + Content<br/>(Defense in Depth)"]
        FU3["Reject on Any Validation Failure<br/>(Fail Securely)"]
        FU4["Store with No Execute Permissions<br/>(Least Privilege)"]
        
        InputVal -.->|Informs| FU1
        DepthInDepth -.->|Requires| FU2
        FailSecure -.->|Informs| FU3
        LeastPriv -.->|Informs| FU4
    end
```

**Sources:** [SKILL.md:10-17]() (principle definitions), [SKILL.md:80-144]() (XSS multi-layer), [SKILL.md:21-75]() (access control), [SKILL.md:394-455]() (file upload)

---

## Principle Application Across SKILL.md Domains

The following table maps each principle to specific sections of `SKILL.md` where it is the primary guiding principle:

| Principle | Primary Application Domains | Line References |
|-----------|----------------------------|----------------|
| **Defense in Depth** | XSS (encoding + CSP + sanitization)<br/>CSRF (tokens + SameSite + Origin validation)<br/>File Uploads (extension + magic bytes + content) | [SKILL.md:110-144]()<br/>[SKILL.md:169-210]()<br/>[SKILL.md:398-455]() |
| **Fail Securely** | Access Control (404 on no match)<br/>JWT Verification (reject on error)<br/>SSRF (abort on validation failure) | [SKILL.md:61-74]()<br/>[SKILL.md:685-691]()<br/>[SKILL.md:382-391]() |
| **Least Privilege** | Access Control (UUIDs, user-only data)<br/>SQL Injection (minimal DB permissions)<br/>Account Lifecycle (token revocation)<br/>JWT (short-lived tokens) | [SKILL.md:29-41]()<br/>[SKILL.md:496-498]()<br/>[SKILL.md:670]()<br/>[SKILL.md:715-719]() |
| **Input Validation** | SQL Injection (parameterized queries)<br/>Path Traversal (canonicalization)<br/>SSRF (IP/DNS validation)<br/>File Upload (type/content validation)<br/>GraphQL (depth/complexity limits) | [SKILL.md:463-492]()<br/>[SKILL.md:595-627]()<br/>[SKILL.md:349-391]()<br/>[SKILL.md:398-415]()<br/>[SKILL.md:725-740]() |
| **Output Encoding** | XSS (context-specific encoding)<br/>Open Redirect (URL validation)<br/>Security Headers (CSP, nosniff) | [SKILL.md:112-144]()<br/>[SKILL.md:259-302]()<br/>[SKILL.md:630-642]() |

---

## How Principles Inform Code Generation

When an AI model generates code using VibeSec-Skill, these principles are applied through a decision tree that determines which security controls to implement:

```mermaid
graph TB
    CodeRequest["Developer Requests:<br/>'Build user profile endpoint'"]
    
    subgraph "Principle Application Flow"
        Analyze["Analyze Request Context:<br/>- Feature type (CRUD operation)<br/>- Data sensitivity (user data)<br/>- Rendering context (API response)"]
        
        ApplyDepth["Defense in Depth:<br/>Apply multiple controls"]
        ApplyFail["Fail Securely:<br/>Deny on errors"]
        ApplyPriv["Least Privilege:<br/>User-only data access"]
        ApplyInput["Input Validation:<br/>Validate userId param"]
        ApplyOutput["Output Encoding:<br/>JSON serialization safe"]
        
        Analyze --> ApplyDepth
        Analyze --> ApplyFail
        Analyze --> ApplyPriv
        Analyze --> ApplyInput
        Analyze --> ApplyOutput
    end
    
    subgraph "Generated Security Controls"
        Control1["UUID for userId parameter"]
        Control2["Ownership verification check"]
        Control3["Return 404 on no match (not 403)"]
        Control4["Parameterized DB query"]
        Control5["Organization membership check"]
        Control6["Security headers in response"]
    end
    
    CodeRequest --> Analyze
    
    ApplyPriv --> Control1
    ApplyPriv --> Control2
    ApplyFail --> Control3
    ApplyInput --> Control4
    ApplyDepth --> Control5
    ApplyOutput --> Control6
```

**Sources:** [SKILL.md:10-17]() (principles), [SKILL.md:747-758]() (general security principles applied during generation)

---

## Principle Coverage Statistics

The following table quantifies how extensively each principle is covered across `SKILL.md`:

| Principle | Direct References | Implicit Applications | Total Directive Count |
|-----------|------------------|----------------------|---------------------|
| Defense in Depth | 1 explicit statement | 15+ multi-layer security sections | ~90 directives |
| Fail Securely | 1 explicit statement | 8+ failure handling patterns | ~35 directives |
| Least Privilege | 1 explicit statement | 12+ permission minimization sections | ~55 directives |
| Input Validation | 1 explicit statement | 25+ validation requirement sections | ~180 directives |
| Output Encoding | 1 explicit statement | 8+ encoding context sections | ~65 directives |

**Calculation Method:** Directive counts include all specific security requirements, checklists, code examples, and prevention strategies that implement each principle across [SKILL.md:1-557]().

**Sources:** [SKILL.md:10-17]() (explicit statements), [SKILL.md:19-757]() (directive distribution)

---

## Relationship to OWASP Top 10

VibeSec-Skill's five principles provide comprehensive coverage of the OWASP Top 10 vulnerabilities:

| OWASP Category | Covered by Principle(s) | Implementation Section |
|----------------|------------------------|----------------------|
| A01: Broken Access Control | Least Privilege, Fail Securely | [Access Control & Authorization](#5) |
| A02: Cryptographic Failures | Least Privilege (secure storage) | [Password Security](#8.1) |
| A03: Injection | Input Validation, Output Encoding | [SQL Injection Prevention](#7.2), [XSS Prevention](#6.1) |
| A04: Insecure Design | Defense in Depth, Fail Securely | All sections (architectural principle) |
| A05: Security Misconfiguration | Defense in Depth (security headers) | [Security Headers Reference](#10) |
| A06: Vulnerable Components | Defense in Depth | [SKILL.md:758]() (dependency updates) |
| A07: Authentication Failures | Fail Securely, Least Privilege | [Authentication & Session Security](#8) |
| A08: Data Integrity Failures | Input Validation, Fail Securely | [JWT Security](#8.2) |
| A09: Logging Failures | Fail Securely (no stack trace exposure) | [SKILL.md:756]() (error handling) |
| A10: SSRF | Input Validation, Defense in Depth | [SSRF Prevention](#7.1) |

**Sources:** [SKILL.md:10-17]() (principles), entire `SKILL.md` structure (OWASP coverage)

---

## Principle Violation Examples

Understanding violations helps AI models recognize insecure patterns to avoid:

| Principle Violated | Insecure Code Pattern | Line Reference | Secure Alternative Reference |
|-------------------|----------------------|----------------|----------------------------|
| Defense in Depth | Output encoding only, no CSP | N/A (anti-pattern) | [SKILL.md:119-135]() |
| Fail Securely | Return 200 on validation error | N/A (anti-pattern) | [SKILL.md:66-71]() |
| Least Privilege | Database user has DROP permissions | N/A (anti-pattern) | [SKILL.md:496]() |
| Input Validation | String concatenation in SQL | [SKILL.md:466]() (vulnerable example) | [SKILL.md:469-470]() |
| Output Encoding | Raw user input in HTML | N/A (anti-pattern) | [SKILL.md:113]() |

**Sources:** [SKILL.md:466]() (vulnerable SQL example), [SKILL.md:61-74]() (secure patterns), [SKILL.md:110-144]() (XSS patterns)

---

# Page: Access Control & Authorization

# Access Control & Authorization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document covers access control and authorization vulnerabilities and secure implementation patterns as defined in VibeSec-Skill. Authorization ensures that authenticated users can only access resources and perform actions they are explicitly permitted to access.

This page focuses specifically on resource-level authorization checks, ownership verification, and object reference security. For authentication mechanisms and session security, see [Authentication & Session Security](#8). For API-specific authorization concerns including mass assignment, see [API Security](#9).

**Sources:** [SKILL.md:21-76]()

---

## Authorization Architecture Overview

The following diagram illustrates how authorization checks integrate into the request processing flow:

```mermaid
graph TB
    Request["HTTP Request"] --> Auth["Authentication Layer"]
    Auth --> AuthCheck{"Authenticated?"}
    AuthCheck -->|No| Deny401["401 Unauthorized"]
    AuthCheck -->|Yes| ExtractUser["Extract currentUser"]
    ExtractUser --> ExtractResource["Extract resourceId"]
    ExtractResource --> FetchResource["database.find(resourceId)"]
    FetchResource --> ResourceCheck{"Resource exists?"}
    ResourceCheck -->|No| Deny404A["404 Not Found"]
    ResourceCheck -->|Yes| OwnerCheck["Verify Ownership"]
    OwnerCheck --> OwnerMatch{"resource.ownerId == currentUser.id?"}
    OwnerMatch -->|Yes| Authorized["Authorized: Return Resource"]
    OwnerMatch -->|No| OrgCheck["Check Organization Access"]
    OrgCheck --> OrgAccess{"currentUser.hasOrgAccess(resource.orgId)?"}
    OrgAccess -->|Yes| Authorized
    OrgAccess -->|No| Deny404B["404 Not Found (enumeration prevention)"]
    
    Deny404B -.-> Note["Note: 404 instead of 403 to prevent resource enumeration"]
```

**Sources:** [SKILL.md:59-74]()

---

## Core Authorization Requirements

### User-Level Authorization

Every data point and action requiring authentication must enforce user-level authorization checks. The security model requires three fundamental verifications:

| Requirement | Description | Enforcement Point |
|-------------|-------------|-------------------|
| **Ownership Verification** | Each user must only access/modify their own data | Data layer (not route level) |
| **No Cross-User Access** | No user should access data from other users or organizations | Every request |
| **Parent Resource Verification** | Check ownership of parent resources (e.g., verify post ownership when accessing comments) | Nested resource access |

The authorization check must occur at the **data layer**, not merely at the route level, to prevent bypass through parameter manipulation or API misuse.

**Sources:** [SKILL.md:27-32]()

---

### UUID-Based Resource Identification

Sequential integer IDs enable enumeration attacks where attackers can iterate through ID values to discover and access resources. VibeSec-Skill mandates non-guessable identifiers:

**Requirements:**
- Use UUIDv4 or similar non-guessable identifiers for all resources
- Exception: Sequential IDs only permitted when explicitly requested by user
- Apply to all resource types: users, documents, transactions, sessions, etc.

**Rationale:** Sequential IDs (1, 2, 3...) make IDOR attacks trivial. An attacker who gains access to resource `123` can immediately test `122`, `124`, etc. UUIDs (`550e8400-e29b-41d4-a716-446655440000`) prevent this enumeration vector.

**Sources:** [SKILL.md:34-36]()

---

### Account Lifecycle Handling

Token and session invalidation must occur immediately upon account state changes:

```mermaid
graph LR
    subgraph "Organization Removal"
        OrgRemove["User removed from organization"] --> RevokeTokens["Revoke all access tokens"]
        RevokeTokens --> InvalidateSessions["Invalidate all sessions"]
    end
    
    subgraph "Account Deletion/Deactivation"
        AcctDelete["Account deleted or deactivated"] --> RevokeKeys["Invalidate API keys"]
        RevokeKeys --> RevokeAcctTokens["Revoke access tokens"]
        RevokeAcctTokens --> InvalidateAcctSessions["Invalidate sessions"]
    end
    
    subgraph "Implementation Mechanisms"
        InvalidateSessions --> TokenRevocationList["Token Revocation List (Blacklist)"]
        InvalidateSessions --> ShortLivedTokens["Short-lived tokens with refresh mechanism"]
    end
```

**Implementation Requirements:**
- **Organization removal**: Immediately revoke all access tokens and sessions when user is removed from organization
- **Account deletion/deactivation**: Invalidate all active sessions and API keys
- **Token management**: Implement token revocation lists OR short-lived tokens with refresh mechanisms

**Sources:** [SKILL.md:38-41]()

---

## Authorization Verification Checklist

The following verification steps must be performed for every protected resource access:

| Check | Description | Failure Consequence |
|-------|-------------|---------------------|
| **Resource ownership verification** | Verify user owns the resource on every request | IDOR vulnerability |
| **Organization membership** | Check organization membership for multi-tenant applications | Horizontal privilege escalation |
| **Role permission validation** | Validate role permissions for role-based actions | Vertical privilege escalation |
| **Post-privilege-change re-validation** | Re-validate permissions after any privilege change | Stale authorization |
| **Parent resource ownership** | Check parent resource ownership for nested resources | Indirect IDOR |

**Critical Principle:** Never trust client-side data for authorization decisions. Always fetch and verify resource ownership from the authoritative data store.

**Sources:** [SKILL.md:43-49]()

---

## Common Authorization Vulnerabilities

### IDOR (Insecure Direct Object Reference)

IDOR occurs when an application exposes direct references to internal objects (database keys, filenames) without verifying the requesting user has permission to access them.

**Vulnerable Pattern:**
```
GET /api/invoices/12345
```

If the server retrieves invoice `12345` without verifying the authenticated user owns or has access to this invoice, any user can access arbitrary invoices by changing the ID parameter.

**Prevention:** Always verify the requesting user has permission to access the requested resource ID. See [Implementation Pattern](#implementation-pattern) below.

**Sources:** [SKILL.md:53]()

---

### Privilege Escalation

Privilege escalation vulnerabilities occur when authorization checks can be bypassed or role information is manipulated.

**Vertical Privilege Escalation:**
- Regular user accessing admin functionality
- User account upgrading to admin role through parameter manipulation
- Validation: Never trust role information from client-side requests

**Horizontal Privilege Escalation:**
- User A accessing User B's resources with the same privilege level
- Example: User modifying another user's profile, accessing another user's private documents
- Prevention: Verify ownership on every resource access, not just role

**Critical Rule:** Validate role changes server-side. Never trust role information from client-side requests or tokens without server-side verification.

**Sources:** [SKILL.md:54-56]()

---

### Horizontal vs. Vertical Access Control Failures

The following diagram illustrates the distinction between horizontal and vertical access control failures:

```mermaid
graph TB
    subgraph "Access Control Boundary"
        Admin["Admin User (role: admin)"]
        UserA["User A (role: user)"]
        UserB["User B (role: user)"]
        
        AdminPanel["Admin Panel"]
        UserAData["User A's Private Data"]
        UserBData["User B's Private Data"]
    end
    
    subgraph "Vertical Access (Cross-Role)"
        UserA -.->|"VULNERABILITY: Vertical Escalation"| AdminPanel
        UserB -.->|"VULNERABILITY: Vertical Escalation"| AdminPanel
    end
    
    subgraph "Horizontal Access (Same Role)"
        UserA -.->|"VULNERABILITY: Horizontal Access"| UserBData
        UserB -.->|"VULNERABILITY: Horizontal Access"| UserAData
    end
    
    subgraph "Legitimate Access"
        Admin -->|"AUTHORIZED"| AdminPanel
        UserA -->|"AUTHORIZED"| UserAData
        UserB -->|"AUTHORIZED"| UserBData
    end
```

**Horizontal Access Control Failure:** User A accessing User B's resources, where both have the same privilege level. Both are regular users, but User A should not access User B's data.

**Vertical Access Control Failure:** Regular user accessing admin functionality or resources that require elevated privileges.

**Sources:** [SKILL.md:55-56]()

---

### Mass Assignment

Mass assignment vulnerabilities occur when applications blindly accept request body fields without filtering, allowing users to modify fields they shouldn't control (e.g., `role`, `isAdmin`, `accountBalance`).

**Vulnerable Pattern:**
```javascript
User.update(req.body)
```

If the request body contains `{ name: "Alice", role: "admin" }`, the application updates both name and role, allowing privilege escalation.

**Secure Pattern:**
```javascript
const allowed = ['name', 'email', 'avatar']
const updates = pick(req.body, allowed)
User.update(updates)
```

**Prevention Requirements:**
- Explicitly whitelist allowed fields for each endpoint
- Never accept unfiltered request bodies
- Define separate field sets for different privilege levels
- Apply to all ORMs and frameworks

For detailed mass assignment prevention patterns, see [API Security](#9).

**Sources:** [SKILL.md:57](), [SKILL.md:707-722]()

---

## Implementation Pattern

The following pseudocode demonstrates the secure resource access pattern required by VibeSec-Skill:

```mermaid
graph TD
    Start["getResource(resourceId, currentUser)"] --> Fetch["resource = database.find(resourceId)"]
    Fetch --> CheckNull{"resource is null?"}
    CheckNull -->|Yes| Return404A["return 404 (Don't reveal existence)"]
    CheckNull -->|No| CheckOwner{"resource.ownerId == currentUser.id?"}
    CheckOwner -->|Yes| ReturnResource["return resource"]
    CheckOwner -->|No| CheckOrg{"currentUser.hasOrgAccess(resource.orgId)?"}
    CheckOrg -->|Yes| ReturnResource
    CheckOrg -->|No| Return404B["return 404 (not 403, prevents enumeration)"]
```

**Implementation Code Pattern:**

[SKILL.md:61-74]() provides the following pseudocode template:

```
function getResource(resourceId, currentUser):
    resource = database.find(resourceId)
    
    if resource is null:
        return 404  # Don't reveal if resource exists
    
    if resource.ownerId != currentUser.id:
        if not currentUser.hasOrgAccess(resource.orgId):
            return 404  # Return 404, not 403, to prevent enumeration
    
    return resource
```

**Key Security Decisions:**

| Decision | Rationale |
|----------|-----------|
| Return 404 for non-existent resources | Don't reveal whether resource exists |
| Return 404 (not 403) for unauthorized access | Prevents resource enumeration attacks |
| Check ownership before organization access | Enforce principle of least privilege |
| Perform check at data layer | Cannot be bypassed by route manipulation |

**Enumeration Prevention:** Returning 403 (Forbidden) reveals the resource exists but the user lacks access. Returning 404 prevents attackers from enumerating valid resource IDs.

**Sources:** [SKILL.md:59-74]()

---

## Authorization Flow in Multi-Tenant Applications

Multi-tenant applications require additional organization-level authorization checks:

```mermaid
graph TB
    Request["Resource Access Request"] --> AuthN["Authentication Check"]
    AuthN --> ExtractIDs["Extract: currentUser.id, resource.id, resource.orgId"]
    ExtractIDs --> DirectOwner{"Direct Owner?<br/>(resource.ownerId == currentUser.id)"}
    DirectOwner -->|Yes| Authorized["AUTHORIZED"]
    DirectOwner -->|No| OrgMember{"Organization Member?<br/>(currentUser.organizations contains resource.orgId)"}
    OrgMember -->|No| Denied["DENIED (404)"]
    OrgMember -->|Yes| RoleCheck{"Required Role?<br/>(currentUser.roleInOrg(resource.orgId) >= requiredRole)"}
    RoleCheck -->|No| Denied
    RoleCheck -->|Yes| ResourceTypePermission{"Resource Type Permission?<br/>(role can access resource type)"}
    ResourceTypePermission -->|No| Denied
    ResourceTypePermission -->|Yes| Authorized
```

**Verification Layers for Multi-Tenant Applications:**

1. **Direct Ownership:** `resource.ownerId == currentUser.id`
2. **Organization Membership:** `currentUser.organizations.includes(resource.orgId)`
3. **Role Validation:** User's role within the organization meets minimum requirement
4. **Resource Type Permission:** Role has permission for this resource type

**Sources:** [SKILL.md:43-49]()

---

## Authorization Check Enforcement Points

The following diagram maps authorization checks to code entity types:

```mermaid
graph LR
    subgraph "Request Entry Points"
        RESTEndpoint["REST API Endpoint<br/>(/api/resources/:id)"]
        GraphQLResolver["GraphQL Resolver<br/>(Query.resource)"]
        WebSocketHandler["WebSocket Handler<br/>(on('resource:get'))"]
    end
    
    subgraph "Authorization Layer"
        MiddlewareAuth["Authentication Middleware"]
        ResourceFetch["Resource Fetch Function<br/>(getResource())"]
        OwnershipCheck["Ownership Verification<br/>(verifyOwnership())"]
        OrgCheck["Organization Check<br/>(hasOrgAccess())"]
    end
    
    subgraph "Data Layer"
        DatabaseQuery["database.find(resourceId)"]
        OwnerIdCompare["resource.ownerId comparison"]
        OrgIdLookup["organization membership lookup"]
    end
    
    RESTEndpoint --> MiddlewareAuth
    GraphQLResolver --> MiddlewareAuth
    WebSocketHandler --> MiddlewareAuth
    
    MiddlewareAuth --> ResourceFetch
    ResourceFetch --> DatabaseQuery
    DatabaseQuery --> OwnershipCheck
    OwnershipCheck --> OwnerIdCompare
    OwnerIdCompare --> OrgCheck
    OrgCheck --> OrgIdLookup
```

**Critical Enforcement Principle:** Authorization checks must occur at the **data layer**, not merely at the routing or middleware layer. This prevents bypass through:
- Direct database access
- Internal API calls that skip routing
- Background jobs accessing resources
- Cached data retrieval

**Sources:** [SKILL.md:27-32](), [SKILL.md:59-74]()

---

## Verification and Testing Checklist

Use the following checklist to verify authorization implementation:

### Ownership Verification
- [ ] User ownership verified on every request (not cached or assumed)
- [ ] Verification uses server-side data source (database, not client tokens)
- [ ] Client-side data never trusted for authorization decisions
- [ ] Parent resource ownership checked for nested resources

### Organization and Role Checks
- [ ] Organization membership checked for multi-tenant applications
- [ ] Role permissions validated for role-based actions
- [ ] Permissions re-validated after privilege changes
- [ ] Role information validated server-side (never trust client claims)

### Resource References
- [ ] UUIDs used instead of sequential IDs (unless explicitly required)
- [ ] 404 returned for both non-existent and unauthorized resources
- [ ] No information leakage in error messages
- [ ] Resource enumeration prevented through consistent responses

### Account Lifecycle
- [ ] Access tokens revoked on organization removal
- [ ] Sessions invalidated on account deletion/deactivation
- [ ] API keys invalidated on account state changes
- [ ] Token revocation list or short-lived tokens implemented

### Mass Assignment Protection
- [ ] Allowed fields explicitly whitelisted per endpoint
- [ ] Sensitive fields (role, isAdmin, etc.) excluded from updates
- [ ] Different field sets for different privilege levels
- [ ] ORM methods use field filtering

**Sources:** [SKILL.md:43-49](), [SKILL.md:51-57]()

---

## Related Security Topics

- **Authentication mechanisms:** See [Authentication & Session Security](#8) for password security, JWT implementation, and session management
- **Session handling:** See [JWT Security](#8.2) for token storage, expiration, and algorithm validation
- **API-specific authorization:** See [API Security](#9) for mass assignment prevention and GraphQL security
- **Security headers:** See [Security Headers Reference](#10) for CORS and access control headers

**Sources:** [SKILL.md:21-76]()

---

# Page: Client-Side Security

# Client-Side Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This page provides an overview of client-side vulnerability prevention in VibeSec-Skill, introducing the four primary attack vectors that target web application clients: Cross-Site Scripting (XSS), Cross-Site Request Forgery (CSRF), secret exposure, and open redirect attacks. This material covers security concerns that execute or manifest in the browser context, where user agents process HTML, JavaScript, and other client-side assets.

For server-side vulnerabilities (SSRF, SQL injection, XXE, path traversal, file uploads), see [Server-Side Security](#7). For authentication and session management, see [Authentication & Session Security](#8). For access control and authorization logic that spans both client and server, see [Access Control & Authorization](#5).

**Sources:** [SKILL.md:78-304]()

---

## Client-Side Attack Surface

Client-side security in VibeSec-Skill addresses vulnerabilities that originate from or execute within the user's browser environment. The skill provides directive-based guidance to AI code generation systems, ensuring that generated code implements protection mechanisms at the point of creation rather than requiring post-generation security retrofitting.

```mermaid
graph TB
    subgraph "User Browser Context"
        DOM["DOM Tree<br/>(HTML Structure)"]
        JS["JavaScript Execution<br/>Environment"]
        Storage["Client Storage<br/>(localStorage/sessionStorage)"]
        Cookies["HTTP Cookies<br/>(Session State)"]
    end
    
    subgraph "Attack Vectors"
        XSS["XSS Attack<br/>Script Injection"]
        CSRF["CSRF Attack<br/>Unauthorized Actions"]
        Secrets["Secret Exposure<br/>API Keys/Tokens"]
        Redirect["Open Redirect<br/>Phishing Vector"]
    end
    
    subgraph "VibeSec-Skill Protections"
        OutputEncode["Output Encoding<br/>Context-Aware Escaping"]
        CSRFToken["CSRF Tokens<br/>SameSite Cookies"]
        EnvVars["Environment Variables<br/>Server-Side API Calls"]
        AllowList["URL Allowlist<br/>Validation"]
    end
    
    XSS -->|"Exploits"| DOM
    XSS -->|"Exploits"| JS
    CSRF -->|"Exploits"| Cookies
    Secrets -->|"Leaks via"| JS
    Secrets -->|"Leaks via"| Storage
    Redirect -->|"Abuses"| DOM
    
    OutputEncode -->|"Protects"| DOM
    OutputEncode -->|"Protects"| JS
    CSRFToken -->|"Protects"| Cookies
    EnvVars -->|"Protects"| JS
    EnvVars -->|"Protects"| Storage
    AllowList -->|"Protects"| DOM
```

**Sources:** [SKILL.md:78-304]()

---

## SKILL.md Architecture for Client-Side Security

The client-side security domain occupies a distinct section in `SKILL.md` under the "Client-Side Bugs" heading, structured as four sequential subsections. This organization allows AI models to retrieve targeted guidance based on the specific vulnerability class being addressed.

```mermaid
graph LR
    SKILLMD["SKILL.md"]
    
    subgraph "Line Range 78-304"
        ClientBugs["## Client-Side Bugs<br/>Line 78"]
        
        subgraph "XSS Domain"
            XSSHeader["### Cross-Site Scripting (XSS)<br/>Line 80"]
            InputSources["Input Sources to Protect<br/>Lines 84-109"]
            ProtectionStrat["Protection Strategies<br/>Lines 111-144"]
        end
        
        subgraph "CSRF Domain"
            CSRFHeader["### Cross-Site Request Forgery (CSRF)<br/>Line 147"]
            EndpointsReq["Endpoints Requiring CSRF Protection<br/>Lines 151-167"]
            ProtectionMech["Protection Mechanisms<br/>Lines 169-210"]
        end
        
        subgraph "Secrets Domain"
            SecretsHeader["### Secret Keys and Sensitive Data Exposure<br/>Line 213"]
            NeverExpose["Never Expose in Client-Side Code<br/>Lines 217-250"]
            BestPractices["Best Practices<br/>Lines 252-256"]
        end
        
        subgraph "Redirect Domain"
            RedirectHeader["## Open Redirect<br/>Line 259"]
            ProtectionStrat2["Protection Strategies<br/>Lines 263-280"]
            BypassTech["Bypass Techniques to Block<br/>Lines 282-301"]
        end
    end
    
    SKILLMD --> ClientBugs
    ClientBugs --> XSSHeader
    ClientBugs --> CSRFHeader
    ClientBugs --> SecretsHeader
    ClientBugs --> RedirectHeader
    
    XSSHeader --> InputSources
    XSSHeader --> ProtectionStrat
    
    CSRFHeader --> EndpointsReq
    CSRFHeader --> ProtectionMech
    
    SecretsHeader --> NeverExpose
    SecretsHeader --> BestPractices
    
    RedirectHeader --> ProtectionStrat2
    RedirectHeader --> BypassTech
```

**Sources:** [SKILL.md:78-304]()

---

## Four Client-Side Attack Vector Categories

VibeSec-Skill addresses client-side security through four vulnerability categories, each representing a distinct attack pattern with specific prevention directives.

| Attack Vector | Lines in SKILL.md | Primary Impact | Core Prevention Strategy |
|--------------|-------------------|----------------|--------------------------|
| **Cross-Site Scripting (XSS)** | [80-144]() | Execution of attacker-controlled JavaScript in victim's browser | Output encoding (context-aware), Content Security Policy (CSP) |
| **Cross-Site Request Forgery (CSRF)** | [147-210]() | Unauthorized state-changing actions using victim's authenticated session | CSRF tokens, SameSite cookies |
| **Secret Exposure** | [213-256]() | Disclosure of API keys, credentials, or sensitive data in client-side code | Environment variables, server-side API proxying |
| **Open Redirect** | [259-302]() | Redirect users to attacker-controlled domains for phishing | URL allowlist validation, relative URLs only |

### Cross-Site Scripting (XSS)

XSS vulnerabilities allow attackers to inject and execute malicious scripts in users' browsers. The skill defines three categories of input sources requiring protection: direct inputs (form fields, search queries, file names), indirect inputs (URL parameters, HTTP headers, third-party API data), and often-overlooked vectors (error messages, PDF generators, email templates). See [Cross-Site Scripting (XSS) Prevention](#6.1) for detailed protection strategies including output encoding rules and CSP configuration.

**Sources:** [SKILL.md:80-144]()

### Cross-Site Request Forgery (CSRF)

CSRF attacks exploit authenticated user sessions to perform unauthorized actions. The skill categorizes vulnerable endpoints into authenticated actions (POST/PUT/PATCH/DELETE requests, settings changes, payment endpoints) and pre-authentication actions (login, signup, password reset). Protection mechanisms include cryptographically random CSRF tokens tied to user sessions, SameSite cookie attributes, and double submit cookie patterns. See [Cross-Site Request Forgery (CSRF) Protection](#6.2) for implementation checklists and edge cases.

**Sources:** [SKILL.md:147-210]()

### Secret Exposure

Secret exposure occurs when sensitive credentials, API keys, or internal infrastructure details appear in client-accessible code. The skill categorizes secrets into three groups: API keys and secrets (third-party keys, database connection strings, JWT signing secrets), sensitive user data (credit card numbers, SSNs, passwords), and infrastructure details (internal IP addresses, database schemas, stack traces). Prevention focuses on environment variable usage and server-side API proxying. See [Secret Exposure & Open Redirect Prevention](#6.3) for hiding locations and detection strategies.

**Sources:** [SKILL.md:213-256]()

### Open Redirect

Open redirect vulnerabilities allow attackers to redirect users to malicious domains, typically for phishing attacks. The skill provides three protection strategies: allowlist validation (restrict to known domains), relative URLs only (accept paths instead of full URLs), and indirect references (use lookup mappings). A comprehensive bypass technique table documents 15 exploitation methods including @ symbol abuse, protocol tricks, Unicode normalization (IDN homograph attacks), and data URLs. See [Secret Exposure & Open Redirect Prevention](#6.3) for bypass prevention.

**Sources:** [SKILL.md:259-302]()

---

## Core Principles Applied to Client-Side Security

The five core security principles defined in [SKILL.md:10-18]() inform all client-side protection directives:

```mermaid
graph TD
    subgraph "Core Principles"
        P1["Defense in Depth<br/>Never rely on single control"]
        P2["Fail Securely<br/>Deny access on failure"]
        P3["Least Privilege<br/>Minimum permissions"]
        P4["Input Validation<br/>Server-side validation"]
        P5["Output Encoding<br/>Context-aware encoding"]
    end
    
    subgraph "Client-Side Application"
        P1 --> C1["XSS: Output Encoding + CSP + Input Sanitization"]
        P1 --> C2["CSRF: Tokens + SameSite + Origin Validation"]
        
        P2 --> C3["XSS: Default CSP denies inline scripts"]
        P2 --> C4["CSRF: Missing token = rejected request"]
        
        P3 --> C5["Secrets: No API keys in client code"]
        P3 --> C6["CSRF: Tokens scoped to sessions"]
        
        P4 --> C7["XSS: Server validates all user input"]
        P4 --> C8["Redirect: Server validates URL format"]
        
        P5 --> C9["XSS: HTML/JS/URL/CSS context-specific"]
        P5 --> C10["Redirect: URL encode user-provided paths"]
    end
```

**Defense in depth** manifests in layered XSS protections (output encoding + CSP + input sanitization) and CSRF defenses (tokens + SameSite + origin validation). **Fail securely** ensures that missing CSRF tokens result in rejected requests and default CSP policies deny inline scripts. **Least privilege** restricts API key access to server-side code only and scopes CSRF tokens to individual user sessions. **Input validation** requires server-side validation of all user input before processing, never trusting client-side checks. **Output encoding** applies context-specific escaping for HTML, JavaScript, URL, and CSS contexts to prevent XSS.

**Sources:** [SKILL.md:10-18](), [SKILL.md:78-304]()

---

## Integration with AI Code Generation Workflow

Client-side security directives in `SKILL.md` integrate into the AI code generation process through context-aware retrieval and constraint application. When a developer prompts an AI platform to generate client-side code, the platform loads relevant sections from `SKILL.md` based on detected frameworks, operation types, and user requirements.

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant AI as "AI Platform"
    participant SKILL as "SKILL.md<br/>Lines 78-304"
    participant Gen as "Code Generator"
    participant Output as "Generated Code"
    
    Dev->>AI: "Build user profile page with<br/>form to update name and email"
    
    activate AI
    AI->>SKILL: "Query: Client-side security<br/>for form handling"
    
    activate SKILL
    SKILL->>SKILL: "Detect: Form input (XSS risk)<br/>State change (CSRF risk)"
    
    SKILL-->>AI: "Return:<br/>- XSS output encoding (Lines 112-118)<br/>- CSRF token validation (Lines 170-174)<br/>- Secret exposure checks (Lines 217-250)"
    deactivate SKILL
    
    AI->>Gen: "Generate with constraints:<br/>- Encode output in HTML context<br/>- Include CSRF token in form<br/>- No API keys in client code"
    
    activate Gen
    Gen->>Gen: "Apply output encoding:<br/>HTML entity encode user input"
    Gen->>Gen: "Add CSRF protection:<br/>Include token in hidden field"
    Gen->>Gen: "Verify no secrets:<br/>Check for hardcoded keys"
    
    Gen-->>Output: "Secure implementation:<br/>- Form with CSRF token<br/>- Output-encoded display<br/>- Server-side validation"
    deactivate Gen
    
    Output-->>Dev: "Deliverable with embedded<br/>client-side security patterns"
    deactivate AI
```

The code generation engine applies client-side security constraints in three phases: **XSS prevention** (context-aware output encoding using framework-native methods like React's JSX auto-escaping), **CSRF protection** (CSRF token generation and validation on state-changing endpoints), and **secret verification** (scanning for hardcoded API keys, credentials, or sensitive data in client-accessible code). The output includes security comments documenting the applied protections.

**Sources:** [SKILL.md:78-304](), [README.md:76-83]()

---

## Client-Side Security Coverage Matrix

The following matrix maps each client-side attack vector to its directive coverage in `SKILL.md`, primary protection mechanisms, and common bypass scenarios addressed.

| Attack Vector | Directive Count | Protection Mechanisms | Bypass Scenarios Addressed |
|--------------|-----------------|----------------------|----------------------------|
| **XSS** | 20+ directives | Output encoding (HTML/JS/URL/CSS), CSP headers, input sanitization, framework escaping | Error message reflection, PDF generators, SVG uploads, markdown rendering, JSON-to-HTML |
| **CSRF** | 15+ directives | CSRF tokens (cryptographically random, session-tied), SameSite cookies (Strict/Lax), double submit cookies | Token presence check, GET with side effects, subdomain token scoping, CORS misconfig |
| **Secret Exposure** | 10+ directives | Environment variables, server-side API calls, secret hiding locations | JavaScript bundles, source maps, HTML comments, hidden fields, SSR hydration data |
| **Open Redirect** | 10+ directives | URL allowlist validation, relative URLs only, indirect reference mapping | @ symbol, protocol tricks, Unicode normalization, DNS rebinding, data URLs, backslash normalization |

**Total directive count**: 60+ client-side specific security directives spanning input validation, output encoding, token generation, secret management, and URL validation.

**Sources:** [SKILL.md:78-304]()

---

## Context-Aware Security Application

Client-side security directives adapt based on framework detection and cloud environment context. The AI platform analyzes the target technology stack and applies framework-specific implementations:

### Framework-Specific XSS Protection

| Framework | Auto-Escaping Mechanism | Manual Encoding Required | CSP Integration |
|-----------|-------------------------|--------------------------|-----------------|
| **React** | JSX expressions (`{variable}`) | `dangerouslySetInnerHTML` usage | Nonce-based CSP for inline scripts |
| **Vue.js** | Template interpolation (`{{ variable }}`) | `v-html` directive usage | CSP with inline event handler restrictions |
| **Angular** | Template binding (`{{variable}}`) | `[innerHTML]` binding | Trusted Types API integration |
| **Express/Node.js** | None (manual required) | All template outputs | Helmet.js CSP middleware |
| **Django** | Template auto-escape (default on) | `{% autoescape off %}` blocks | django-csp package integration |

The skill directs AI platforms to leverage framework-native escaping mechanisms first (e.g., React JSX auto-escaping) before applying manual encoding, ensuring generated code follows framework best practices while maintaining security.

**Sources:** [SKILL.md:112-118](), [README.md:71-75]()

---

## Security Headers for Client-Side Protection

Several HTTP security headers complement client-side vulnerability prevention. These headers are referenced throughout the client-side security directives:

| Header | Purpose | Client-Side Attack Mitigation |
|--------|---------|------------------------------|
| `Content-Security-Policy` | Define trusted content sources | XSS prevention (script-src, style-src directives) |
| `X-Content-Type-Options: nosniff` | Prevent MIME sniffing | XSS via uploaded files, content type confusion |
| `X-Frame-Options: DENY` | Prevent clickjacking | CSRF via clickjacking attack chains |
| `Referrer-Policy: strict-origin-when-cross-origin` | Control referrer information | Secret exposure via referrer leakage |
| `Strict-Transport-Security` | Enforce HTTPS | CSRF protection (SameSite cookie requirement) |

For comprehensive security header configuration, see [Security Headers Reference](#10).

**Sources:** [SKILL.md:119-144](), [SKILL.md:630-642]()

---

## Verification and Testing Guidance

Each client-side attack vector section in `SKILL.md` includes implementation checklists for verification. Example checklist for CSRF protection [SKILL.md:201-210]():

```
- [ ] Token is cryptographically random (use secure random generator)
- [ ] Token is tied to user session
- [ ] Token is validated server-side on all state-changing requests
- [ ] Missing token = rejected request
- [ ] Token regenerated on authentication state change
- [ ] SameSite cookie attribute is set
- [ ] Secure and HttpOnly flags on session cookies
```

These checklists serve dual purposes: guiding AI code generation to include required security controls and providing developers with post-generation verification steps.

**Sources:** [SKILL.md:201-210]()

---

## Relationship to Other Security Domains

Client-side security directives frequently interact with server-side security controls and access control mechanisms:

- **XSS + Access Control**: Output encoding prevents script injection that could bypass client-side authorization checks. Server-side authorization must still verify user permissions regardless of XSS protections.

- **CSRF + Access Control**: CSRF tokens prevent unauthorized state changes, but access control verifies the authenticated user owns the target resource (preventing horizontal privilege escalation via CSRF).

- **Secret Exposure + Server-Side Security**: Moving API keys to server-side prevents direct exposure, but server-side SSRF protections must validate URLs when proxying client requests to third-party APIs.

- **Open Redirect + Server-Side Security**: Redirect validation prevents phishing, but server-side path traversal protections ensure redirect targets don't expose internal file paths.

For server-side vulnerability prevention, see [Server-Side Security](#7). For access control implementation patterns, see [Access Control & Authorization](#5).

**Sources:** [SKILL.md:78-304](), [SKILL.md:21-76](), [SKILL.md:321-628]()

---

# Page: Cross-Site Scripting (XSS) Prevention

# Cross-Site Scripting (XSS) Prevention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document provides comprehensive guidance for preventing Cross-Site Scripting (XSS) vulnerabilities in web applications. XSS occurs when user-controllable data is incorporated into web pages without proper sanitization or encoding, allowing attackers to execute malicious scripts in victims' browsers.

This page covers input source identification, context-specific output encoding, Content Security Policy implementation, and input sanitization strategies as defined in the VibeSec-Skill knowledge base. For server-side injection attacks, see [SQL Injection Prevention](#7.2) and [XXE Prevention](#7.3). For secret exposure prevention, see [Secret Exposure & Open Redirect Prevention](#6.3).

**Sources:** [SKILL.md:78-144]()

---

## Overview of XSS Attack Vectors

XSS vulnerabilities arise when applications render user-controllable data without appropriate encoding for the output context. The VibeSec-Skill defines a comprehensive taxonomy of input sources that must be protected, organized into three categories: direct inputs, indirect inputs, and often-overlooked inputs.

### XSS Attack Flow

```mermaid
graph TB
    subgraph "Attack Vector Sources"
        Direct["Direct User Input<br/>(Form fields, search queries)"]
        Indirect["Indirect Input<br/>(URL params, headers, APIs)"]
        Overlooked["Overlooked Sources<br/>(Error messages, logs, PDFs)"]
    end
    
    subgraph "Application Processing"
        NoEncoding["Application renders input<br/>without encoding"]
        Context["Output Context"]
    end
    
    subgraph "Rendering Contexts"
        HTML["HTML Context<br/>&lt;div&gt;USER_DATA&lt;/div&gt;"]
        JS["JavaScript Context<br/>&lt;script&gt;var x = USER_DATA&lt;/script&gt;"]
        URL["URL Context<br/>&lt;a href='USER_DATA'&gt;"]
        CSS["CSS Context<br/>&lt;style&gt;body { bg: USER_DATA }&lt;/style&gt;"]
    end
    
    subgraph "Exploitation"
        XSS["XSS Payload Execution<br/>&lt;script&gt;alert(document.cookie)&lt;/script&gt;"]
        Impact["Impact: Session hijacking,<br/>credential theft, defacement"]
    end
    
    Direct --> NoEncoding
    Indirect --> NoEncoding
    Overlooked --> NoEncoding
    
    NoEncoding --> Context
    Context --> HTML
    Context --> JS
    Context --> URL
    Context --> CSS
    
    HTML --> XSS
    JS --> XSS
    URL --> XSS
    CSS --> XSS
    
    XSS --> Impact
```

**Sources:** [SKILL.md:80-109]()

---

## Input Sources Requiring XSS Protection

### Direct Input Sources

These are the most obvious user-controllable inputs that applications process:

| Input Source | Description | Example Vulnerability |
|--------------|-------------|----------------------|
| Form fields | Email, name, bio, comments | User submits `<script>alert(1)</script>` as bio |
| Search queries | Search box input | Search for `"><script>alert(1)</script>` |
| File names | Original filename during upload | Upload file named `file<script>.jpg` |
| Rich text editors | WYSIWYG content | Paste HTML containing `<img src=x onerror=alert(1)>` |

**Sources:** [SKILL.md:86-90]()

### Indirect Input Sources

These sources are less obvious but equally dangerous:

| Input Source | Description | Example Vulnerability |
|--------------|-------------|----------------------|
| URL parameters | Query strings | `?name=<script>alert(1)</script>` |
| URL fragments | Hash values | `#<img src=x onerror=alert(1)>` |
| HTTP headers | Referer, User-Agent if displayed | Custom Referer with XSS payload |
| Third-party API data | External service responses | API returns malicious HTML |
| WebSocket messages | Real-time communication data | Malicious message contains script tags |
| postMessage data | iframe communication | `window.postMessage('<script>...')` |
| LocalStorage/SessionStorage | If rendered to DOM | Stored XSS via storage APIs |

**Sources:** [SKILL.md:92-99]()

### Often Overlooked Input Sources

Critical but frequently forgotten attack vectors:

| Input Source | Description | Example Vulnerability |
|--------------|-------------|----------------------|
| Error messages | Errors reflecting user input | `Error: Invalid username "<script>"` |
| PDF/document generators | HTML-to-PDF converters | PDF containing executable JavaScript |
| Email templates | User data in emails | Email body with unencoded HTML |
| Log viewers | Admin panels displaying logs | Logs containing injected payloads |
| JSON responses as HTML | Improperly rendered JSON | `Content-Type: text/html` for JSON |
| SVG file uploads | SVG with embedded scripts | `<svg onload="alert(1)">` |
| Markdown rendering | If allowing raw HTML | Markdown with `<script>` tags |

**Sources:** [SKILL.md:101-109]()

---

## Protection Strategy Architecture

```mermaid
graph TB
    subgraph "Defense-in-Depth Layers"
        Input["User Input"]
        
        Input --> Layer1["Layer 1: Input Validation<br/>(Whitelist allowed patterns)"]
        Layer1 --> Layer2["Layer 2: Input Sanitization<br/>(DOMPurify for rich text)"]
        Layer2 --> Layer3["Layer 3: Output Encoding<br/>(Context-specific escaping)"]
        Layer3 --> Layer4["Layer 4: Content Security Policy<br/>(Browser enforcement)"]
        Layer4 --> Layer5["Layer 5: Security Headers<br/>(X-Content-Type-Options: nosniff)"]
        
        Layer5 --> SafeOutput["Safe Output Rendered"]
    end
    
    subgraph "Framework Integration"
        React["React JSX<br/>(Automatic HTML escaping)"]
        Vue["Vue Templates<br/>({{ }} auto-escaping)"]
        Angular["Angular<br/>(Built-in sanitization)"]
    end
    
    Layer3 -.->|"Use framework features"| React
    Layer3 -.->|"Use framework features"| Vue
    Layer3 -.->|"Use framework features"| Angular
    
    subgraph "Encoding Functions by Context"
        HTMLEncode["HTML Entity Encode<br/>< becomes &amp;lt;"]
        JSEncode["JavaScript Escape<br/>Backslash escape quotes"]
        URLEncode["URL Encode<br/>Percent-encode special chars"]
        CSSEncode["CSS Escape<br/>Backslash hex encoding"]
    end
    
    Layer3 --> HTMLEncode
    Layer3 --> JSEncode
    Layer3 --> URLEncode
    Layer3 --> CSSEncode
```

**Sources:** [SKILL.md:110-144]()

---

## Context-Specific Output Encoding

The VibeSec-Skill mandates different encoding strategies based on where user data is rendered. Each context has specific encoding requirements to prevent script execution.

### Encoding Requirements by Context

```mermaid
graph LR
    subgraph "HTML Context"
        HTMLIN["User Input: &lt;script&gt;alert(1)&lt;/script&gt;"]
        HTMLENC["HTML Entity Encode"]
        HTMLOUT["Output: &amp;lt;script&amp;gt;alert(1)&amp;lt;/script&amp;gt;"]
        
        HTMLIN --> HTMLENC
        HTMLENC --> HTMLOUT
    end
    
    subgraph "JavaScript Context"
        JSIN["User Input: '; alert(1);//"]
        JSENC["JavaScript Escape"]
        JSOUT["Output: \\'; alert(1);//"]
        
        JSIN --> JSENC
        JSENC --> JSOUT
    end
    
    subgraph "URL Context"
        URLIN["User Input: javascript:alert(1)"]
        URLENC["URL Encode + Validate Scheme"]
        URLOUT["Output: Rejected or encoded"]
        
        URLIN --> URLENC
        URLENC --> URLOUT
    end
    
    subgraph "CSS Context"
        CSSIN["User Input: expression(alert(1))"]
        CSSENC["CSS Escape"]
        CSSOUT["Output: \\65 xpression(alert(1))"]
        
        CSSIN --> CSSENC
        CSSENC --> CSSOUT
    end
```

### HTML Context Encoding

When rendering user data within HTML elements, convert special characters to HTML entities:

| Character | HTML Entity | Purpose |
|-----------|-------------|---------|
| `<` | `&lt;` | Prevent tag opening |
| `>` | `&gt;` | Prevent tag closing |
| `&` | `&amp;` | Prevent entity injection |
| `"` | `&quot;` | Prevent attribute escaping |
| `'` | `&#x27;` | Prevent attribute escaping |

**Framework Usage:**
- React JSX: Automatically escapes by default
- Vue templates: `{{ }}` syntax auto-escapes
- Angular: Built-in sanitization via `DomSanitizer`

**Sources:** [SKILL.md:112-118]()

### JavaScript Context Encoding

When inserting user data into JavaScript code, use JavaScript-specific escaping:

```
// Context: <script>var name = "USER_INPUT";</script>
// Requirements:
// - Escape quotes (" becomes \")
// - Escape backslashes (\ becomes \\)
// - Escape newlines (\n becomes \\n)
// - Consider using JSON.stringify() for complex data
```

**Sources:** [SKILL.md:114]()

### URL Context Encoding

When user data appears in URLs, apply URL encoding and validate the scheme:

```
// Context: <a href="USER_INPUT">
// Requirements:
// - URL encode special characters
// - Validate URL scheme (http/https only)
// - Reject javascript:, data:, vbscript: schemes
// - Use relative URLs when possible
```

**Sources:** [SKILL.md:115]()

### CSS Context Encoding

When user data appears in CSS, use CSS-specific escaping:

```
// Context: <style>body { background: USER_INPUT; }</style>
// Requirements:
// - CSS escape special characters
// - Reject expression() (IE-specific attack)
// - Validate color/size values against expected formats
```

**Sources:** [SKILL.md:116]()

---

## Content Security Policy (CSP) Implementation

CSP provides a browser-enforced defense layer that restricts resource loading and script execution. The VibeSec-Skill defines a comprehensive CSP configuration.

### CSP Header Structure

```mermaid
graph TB
    subgraph "CSP Directives"
        CSP["Content-Security-Policy Header"]
        
        CSP --> D1["default-src 'self'<br/>(Fallback for all directives)"]
        CSP --> D2["script-src 'self'<br/>(JavaScript sources)"]
        CSP --> D3["style-src 'self' 'unsafe-inline'<br/>(CSS sources)"]
        CSP --> D4["img-src 'self' data: https:<br/>(Image sources)"]
        CSP --> D5["font-src 'self'<br/>(Font sources)"]
        CSP --> D6["connect-src 'self' https://api.yourdomain.com<br/>(AJAX/WebSocket targets)"]
        CSP --> D7["frame-ancestors 'none'<br/>(Embedding restrictions)"]
        CSP --> D8["base-uri 'self'<br/>(Base tag restrictions)"]
        CSP --> D9["form-action 'self'<br/>(Form submission targets)"]
    end
    
    subgraph "Advanced CSP Features"
        D2 -.->|"Avoid"| Unsafe["'unsafe-inline'<br/>'unsafe-eval'"]
        D2 -.->|"Prefer"| Nonces["Nonces: 'nonce-abc123'<br/>Hashes: 'sha256-...'"]
        CSP --> Report["report-uri /csp-report<br/>(Violation reporting)"]
    end
    
    subgraph "Attack Prevention"
        D2 --> P1["Blocks inline &lt;script&gt; tags"]
        D2 --> P2["Blocks eval() and Function()"]
        D6 --> P3["Prevents data exfiltration"]
        D7 --> P4["Prevents clickjacking"]
    end
```

### CSP Configuration Template

The skill provides a production-ready CSP header configuration:

```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.yourdomain.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

**Key Directives:**

| Directive | Purpose | Configuration |
|-----------|---------|---------------|
| `default-src` | Fallback for unspecified directives | `'self'` (same origin only) |
| `script-src` | JavaScript execution sources | `'self'` (no inline scripts) |
| `style-src` | CSS sources | `'self' 'unsafe-inline'` |
| `img-src` | Image sources | `'self' data: https:` |
| `connect-src` | XHR/Fetch/WebSocket targets | Specific API domains |
| `frame-ancestors` | Embedding restrictions | `'none'` (prevent clickjacking) |
| `base-uri` | Base tag restrictions | `'self'` (prevent base tag injection) |
| `form-action` | Form submission targets | `'self'` (prevent form hijacking) |

**Sources:** [SKILL.md:119-134]()

### CSP Nonces and Hashes

For legitimate inline scripts, use nonces or hashes instead of `'unsafe-inline'`:

**Nonce-based approach:**
```html
<!-- Server generates random nonce per request -->
<script nonce="abc123">
  // Legitimate inline script
</script>
```

**Hash-based approach:**
```
<!-- CSP Header -->
script-src 'self' 'sha256-[hash-of-script-content]'
```

**Violation Reporting:**
```
report-uri /csp-report
```

Configure a reporting endpoint to receive CSP violation notifications for monitoring and debugging.

**Sources:** [SKILL.md:132-134]()

---

## Input Sanitization for Rich Text

When applications must accept HTML input (rich text editors), use established sanitization libraries rather than custom solutions.

### Sanitization Strategy

```mermaid
graph LR
    subgraph "Rich Text Input Flow"
        UserInput["User HTML Input<br/>&lt;p&gt;Hello&lt;script&gt;alert(1)&lt;/script&gt;&lt;/p&gt;"]
        
        UserInput --> Sanitizer["DOMPurify.sanitize()"]
        
        Sanitizer --> Whitelist["Apply Whitelist<br/>(Allowed: p, b, i, a, img)<br/>(Blocked: script, iframe, object)"]
        
        Whitelist --> AttributeFilter["Filter Attributes<br/>(Allowed: href, src, alt)<br/>(Blocked: on*, style)"]
        
        AttributeFilter --> SafeOutput["Safe HTML Output<br/>&lt;p&gt;Hello&lt;/p&gt;"]
    end
    
    subgraph "Library Recommendations"
        DOMPurify["DOMPurify<br/>(JavaScript)"]
        Bleach["Bleach<br/>(Python)"]
        HTMLPurifier["HTML Purifier<br/>(PHP)"]
    end
```

### DOMPurify Implementation Pattern

For JavaScript applications, the skill recommends DOMPurify:

```javascript
// Whitelist approach for rich text
const cleanHtml = DOMPurify.sanitize(userInput, {
  ALLOWED_TAGS: ['p', 'b', 'i', 'u', 'a', 'ul', 'ol', 'li'],
  ALLOWED_ATTR: ['href', 'title']
});
```

**Sanitization Rules:**
1. Use established libraries (DOMPurify for HTML)
2. Whitelist allowed tags and attributes
3. Strip or encode dangerous patterns
4. Never attempt custom HTML parsing

**Sources:** [SKILL.md:136-140]()

---

## Additional Security Headers

The VibeSec-Skill mandates additional headers that complement XSS defenses:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking (redundant with CSP `frame-ancestors`) |

### X-Content-Type-Options: nosniff

This header prevents browsers from MIME-sniffing responses, which could allow an uploaded file to be interpreted as HTML:

```
X-Content-Type-Options: nosniff
```

Without this header, an uploaded image with HTML content might be executed as a script if the browser sniffs it as `text/html`.

**Sources:** [SKILL.md:141-144]()

---

## Complete XSS Prevention Checklist

The following checklist ensures comprehensive XSS protection:

### Input Handling
- [ ] All user inputs identified (direct, indirect, overlooked sources)
- [ ] Rich text sanitized with whitelisting library (DOMPurify, Bleach)
- [ ] File uploads validated for type and content (magic bytes)
- [ ] SVG uploads either blocked or sanitized

### Output Encoding
- [ ] HTML context: HTML entity encoding applied
- [ ] JavaScript context: JavaScript escaping applied
- [ ] URL context: URL encoding + scheme validation applied
- [ ] CSS context: CSS escaping applied
- [ ] Framework auto-escaping features utilized (React JSX, Vue `{{ }}`)

### Content Security Policy
- [ ] CSP header configured with `default-src 'self'`
- [ ] `script-src` set to `'self'` (no `'unsafe-inline'`)
- [ ] `'unsafe-eval'` avoided in production
- [ ] Nonces or hashes used for legitimate inline scripts
- [ ] `frame-ancestors 'none'` set (clickjacking prevention)
- [ ] `base-uri 'self'` set (base tag injection prevention)
- [ ] `report-uri` configured for violation monitoring

### Security Headers
- [ ] `X-Content-Type-Options: nosniff` header set
- [ ] `X-Frame-Options: DENY` header set (or CSP `frame-ancestors`)

### Framework-Specific
- [ ] Framework's built-in escaping features enabled and not bypassed
- [ ] Dangerous methods avoided (`dangerouslySetInnerHTML`, `v-html` without sanitization)
- [ ] Template injection vulnerabilities prevented

**Sources:** [SKILL.md:78-144]()

---

## Integration with Core Security Principles

XSS prevention aligns with VibeSec-Skill's foundational security principles:

| Core Principle | XSS Prevention Application |
|----------------|---------------------------|
| **Defense in Depth** | Multiple layers: input validation, output encoding, CSP, security headers |
| **Fail Securely** | Reject input that fails validation rather than attempting to fix it |
| **Least Privilege** | CSP restricts script sources and capabilities |
| **Input Validation** | Validate all user-controllable data server-side |
| **Output Encoding** | Context-specific encoding for all rendered user data |

For more details on these principles, see [Core Security Principles](#4).

**Sources:** [SKILL.md:10-18](), [SKILL.md:78-144]()

---

# Page: Cross-Site Request Forgery (CSRF) Protection

# Cross-Site Request Forgery (CSRF) Protection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document details CSRF (Cross-Site Request Forgery) attack prevention mechanisms as implemented in VibeSec-Skill's secure coding guidance. CSRF vulnerabilities occur when authenticated users are tricked into performing unintended state-changing actions on web applications where they are authenticated. This page covers token-based protection, cookie security attributes, endpoint classification, edge cases, and implementation verification.

For protection against other client-side attacks, see [Cross-Site Scripting (XSS) Prevention](#6.1) and [Secret Exposure & Open Redirect Prevention](#6.3). For server-side security concerns, see [Server-Side Security](#7).

**Sources:** [SKILL.md:147-211]()

---

## CSRF Attack Vector Overview

CSRF exploits the trust that a web application has in an authenticated user's browser. An attacker crafts a malicious request that the victim's browser automatically authenticates using existing session cookies.

### Attack Flow Diagram

```mermaid
sequenceDiagram
    participant Attacker
    participant Victim as "Victim Browser"
    participant App as "Vulnerable Application"
    
    Note over Victim,App: Victim is authenticated
    Victim->>App: "Normal login"
    App->>Victim: "Set-Cookie: session=abc123"
    
    Attacker->>Victim: "Sends malicious link/page<br/><form action=app.com/transfer method=POST>"
    
    Note over Victim: Victim clicks link or<br/>visits attacker page
    
    Victim->>App: "POST /transfer amount=1000&to=attacker<br/>Cookie: session=abc123"
    
    Note over App: Application sees valid session,<br/>executes unauthorized action
    
    App->>Victim: "Transfer completed"
    
    Note over Victim,Attacker: Victim's funds transferred<br/>without consent
```

**Sources:** [SKILL.md:147-149]()

---

## Endpoints Requiring CSRF Protection

VibeSec-Skill categorizes endpoints into two protection tiers: authenticated actions and pre-authentication actions. Both require CSRF protection as they perform state changes.

### State-Changing Endpoint Classification

```mermaid
graph TB
    subgraph "Authenticated Actions"
        A1["POST/PUT/PATCH/DELETE<br/>requests"]
        A2["File upload<br/>endpoints"]
        A3["Settings change<br/>endpoints"]
        A4["Payment/transaction<br/>endpoints"]
        A5["GET with side effects<br/>(antipattern to fix)"]
    end
    
    subgraph "Pre-Authentication Actions"
        P1["Login<br/>endpoints"]
        P2["Signup<br/>endpoints"]
        P3["Password reset request<br/>endpoints"]
        P4["Password change<br/>endpoints"]
        P5["Email/phone verification<br/>endpoints"]
        P6["OAuth callback<br/>endpoints"]
    end
    
    subgraph "Protection Requirements"
        R1["CSRF Token<br/>Validation"]
        R2["SameSite Cookie<br/>Attribute"]
        R3["Defense in Depth<br/>Combination"]
    end
    
    A1 & A2 & A3 & A4 & A5 --> R1
    P1 & P2 & P3 & P4 & P5 & P6 --> R1
    
    R1 & R2 --> R3
```

### Endpoint Categories

| Category | Examples | Risk Without Protection |
|----------|----------|------------------------|
| **Authenticated Actions** | POST/PUT/PATCH/DELETE operations | Unauthorized data modification, privilege escalation |
| **File Uploads** | `/upload`, `/api/files` | Malicious file injection |
| **Settings Changes** | `/settings/profile`, `/api/config` | Account takeover, permission changes |
| **Payment/Transactions** | `/transfer`, `/checkout` | Financial fraud |
| **GET with Side Effects** | `/delete?id=123` (antipattern) | Silent data deletion |
| **Login Endpoints** | `/login`, `/auth/signin` | Login CSRF, session fixation |
| **Signup Endpoints** | `/register`, `/api/signup` | Unwanted account creation |
| **Password Reset** | `/forgot-password`, `/reset` | Password change attacks |
| **OAuth Callbacks** | `/auth/callback?code=xyz` | Authorization code interception |

**Sources:** [SKILL.md:151-167]()

---

## Protection Mechanisms

VibeSec-Skill implements three complementary CSRF protection mechanisms, following the defense-in-depth principle.

### 1. CSRF Token Implementation

CSRF tokens provide cryptographic proof that a request originated from the legitimate application rather than a third-party site.

```mermaid
graph TB
    subgraph "Token Generation"
        G1["User authenticates"]
        G2["Generate cryptographically<br/>random token"]
        G3["Store token in<br/>server-side session"]
        G4["Embed token in<br/>form/response"]
        
        G1 --> G2
        G2 --> G3
        G3 --> G4
    end
    
    subgraph "Token Validation"
        V1["Request received<br/>with token"]
        V2["Extract token from<br/>request body/header"]
        V3["Compare with<br/>session token"]
        V4{"Tokens<br/>match?"}
        V5["Process request"]
        V6["Reject request<br/>(403/401)"]
        
        V1 --> V2
        V2 --> V3
        V3 --> V4
        V4 -->|"Yes"| V5
        V4 -->|"No or missing"| V6
    end
    
    G4 -.->|"Token embedded<br/>in legitimate requests"| V1
```

#### Token Requirements

| Requirement | Implementation | Purpose |
|-------------|----------------|---------|
| **Cryptographic Randomness** | Use secure random generator (e.g., `crypto.randomBytes(32)`) | Prevent token prediction |
| **Session Binding** | Tie token to user session ID | Prevent token reuse across sessions |
| **Server-Side Validation** | Validate on every state-changing request | Enforce protection |
| **Token Regeneration** | Generate new token after login/logout | Prevent session fixation combo attacks |
| **Mandatory Validation** | Missing token = rejected request | Prevent bypass via token omission |

**Sources:** [SKILL.md:170-175]()

---

### 2. SameSite Cookie Attribute

The `SameSite` cookie attribute prevents the browser from sending cookies in cross-site requests, providing automatic CSRF protection at the browser level.

```mermaid
graph LR
    subgraph "SameSite Values"
        S1["SameSite=Strict"]
        S2["SameSite=Lax"]
        S3["SameSite=None"]
    end
    
    subgraph "Behavior"
        B1["Never sent cross-site<br/>(Best security)"]
        B2["Sent on top-level<br/>navigations only<br/>(Good balance)"]
        B3["Sent in all contexts<br/>(Requires Secure)"]
    end
    
    subgraph "Additional Attributes"
        A1["Secure<br/>(HTTPS only)"]
        A2["HttpOnly<br/>(No JS access)"]
    end
    
    S1 --> B1
    S2 --> B2
    S3 --> B3
    
    B1 -.->|"Combine with"| A1
    B1 -.->|"Combine with"| A2
    B2 -.->|"Combine with"| A1
    B2 -.->|"Combine with"| A2
```

#### Cookie Configuration Syntax

```
Set-Cookie: session=abc123; SameSite=Strict; Secure; HttpOnly
```

| Attribute | Value | Effect |
|-----------|-------|--------|
| `SameSite` | `Strict` | Cookie never sent in cross-site requests (links, forms, etc.) |
| `SameSite` | `Lax` | Cookie sent on top-level GET navigations only (user clicking link) |
| `SameSite` | `None; Secure` | Cookie sent cross-site (requires HTTPS) |
| `Secure` | N/A | Cookie only sent over HTTPS |
| `HttpOnly` | N/A | Cookie inaccessible to JavaScript (`document.cookie`) |

**Defense-in-Depth Guidance:** Always combine SameSite cookies with CSRF tokens. SameSite provides baseline protection but tokens ensure comprehensive defense against bypass scenarios.

**Sources:** [SKILL.md:176-182]()

---

### 3. Double Submit Cookie Pattern

An alternative token-based approach where the CSRF token is stored in both a cookie and request parameter, with the server validating they match.

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant Server as "Application Server"
    
    Note over Client,Server: Initial authentication
    
    Server->>Client: "Set-Cookie: csrf_token=random123; SameSite=Lax<br/>Response body: { csrfToken: 'random123' }"
    
    Note over Client: Store token for requests
    
    Client->>Server: "POST /api/transfer<br/>Cookie: csrf_token=random123<br/>X-CSRF-Token: random123"
    
    Server->>Server: "Extract cookie value: random123<br/>Extract header value: random123"
    
    Server->>Server: "Compare values"
    
    alt "Values match"
        Server->>Client: "200 OK - Request processed"
    else "Values don't match or missing"
        Server->>Client: "403 Forbidden - CSRF validation failed"
    end
```

**Implementation Note:** This pattern is useful when session state cannot be maintained server-side (e.g., stateless JWT authentication), but requires careful implementation to avoid security pitfalls.

**Sources:** [SKILL.md:184-186]()

---

## Edge Cases and Common Mistakes

VibeSec-Skill identifies critical edge cases and anti-patterns that developers must avoid when implementing CSRF protection.

### Critical Security Pitfalls

```mermaid
graph TB
    subgraph "Common Mistakes"
        M1["Token presence<br/>check only"]
        M2["No token<br/>per-form isolation"]
        M3["Assuming JSON<br/>prevents CSRF"]
        M4["Overly permissive<br/>CORS"]
        M5["Subdomain scope<br/>issues"]
        M6["GET with<br/>side effects"]
        M7["Token in URL"]
        M8["Token in URL<br/>vs header"]
    end
    
    subgraph "Consequences"
        C1["Bypass via<br/>empty token"]
        C2["Token reuse<br/>attack"]
        C3["Content-Type<br/>bypass"]
        C4["SameSite<br/>bypass"]
        C5["Subdomain<br/>takeover CSRF"]
        C6["CSRF via<br/>GET request"]
        C7["Token<br/>leakage"]
        C8["Referer<br/>leakage"]
    end
    
    M1 --> C1
    M2 --> C2
    M3 --> C3
    M4 --> C4
    M5 --> C5
    M6 --> C6
    M7 --> C7
    M8 --> C8
```

### Edge Case Reference Table

| Edge Case | Vulnerability | Mitigation |
|-----------|--------------|------------|
| **Token Presence Check** | CSRF validation depends on whether token is present (if present, validate; if absent, skip) | Always require token; missing token = rejected request |
| **Token Per Form** | Single token reused across all forms allows token leakage from one form to compromise others | Generate unique tokens per form for sensitive operations |
| **JSON APIs** | Assumption that `Content-Type: application/json` prevents CSRF | Validate `Origin`/`Referer` headers AND use tokens (Flash/older browsers can bypass) |
| **CORS Misconfiguration** | `Access-Control-Allow-Origin: *` with credentials bypasses SameSite | Never use wildcard origin with credentials; validate origin strictly |
| **Subdomain Scope** | CSRF tokens not scoped to subdomains allow subdomain takeover to lead to CSRF | Scope tokens to specific subdomain; validate `Host` header |
| **Flash/PDF Uploads** | Legacy browser plugins (Flash) could bypass SameSite cookies | Validate CSRF tokens even with SameSite (defense in depth) |
| **GET Side Effects** | State changes on GET requests (`/delete?id=123`) are always CSRF-vulnerable | Never perform state changes on GET; use POST/DELETE with CSRF protection |
| **Token Leakage** | CSRF tokens in URLs leak via Referer header, browser history, logs | Use custom headers (`X-CSRF-Token`) or request body; never URL parameters |
| **Token in URL vs Header** | URL parameters expose tokens in logs, Referer, history | Prefer custom headers (`X-CSRF-Token`) over URL parameters |

**Sources:** [SKILL.md:188-199]()

---

## Verification Checklist

VibeSec-Skill provides a comprehensive checklist for CSRF protection implementation verification.

### Implementation Validation Flow

```mermaid
graph TB
    Start["CSRF Protection<br/>Implementation"]
    
    C1{"Token is<br/>cryptographically<br/>random?"}
    C2{"Token tied to<br/>user session?"}
    C3{"Token validated<br/>on all state-changing<br/>requests?"}
    C4{"Missing token<br/>= rejected?"}
    C5{"Token regenerated<br/>on auth change?"}
    C6{"SameSite attribute<br/>set?"}
    C7{"Secure & HttpOnly<br/>flags set?"}
    
    Pass["CSRF Protection<br/>Complete"]
    Fail["Security Gap<br/>Identified"]
    
    Start --> C1
    C1 -->|"Yes"| C2
    C1 -->|"No"| Fail
    
    C2 -->|"Yes"| C3
    C2 -->|"No"| Fail
    
    C3 -->|"Yes"| C4
    C3 -->|"No"| Fail
    
    C4 -->|"Yes"| C5
    C4 -->|"No"| Fail
    
    C5 -->|"Yes"| C6
    C5 -->|"No"| Fail
    
    C6 -->|"Yes"| C7
    C6 -->|"No"| Fail
    
    C7 -->|"Yes"| Pass
    C7 -->|"No"| Fail
```

### Checklist Items

The following verification items are extracted from SKILL.md and must all be satisfied:

- [ ] **Token is cryptographically random** — Use secure random generator (e.g., `crypto.randomBytes()`, `secrets.token_hex()`)
- [ ] **Token is tied to user session** — Each session has unique token; tokens are not shared across users
- [ ] **Token is validated server-side on all state-changing requests** — POST, PUT, PATCH, DELETE all require validation
- [ ] **Missing token = rejected request** — No bypass via token omission; validation is mandatory
- [ ] **Token regenerated on authentication state change** — New token generated after login, logout, privilege change
- [ ] **SameSite cookie attribute is set** — `SameSite=Strict` or `SameSite=Lax` on session cookies
- [ ] **Secure and HttpOnly flags on session cookies** — `Secure` (HTTPS-only) and `HttpOnly` (no JavaScript access) enforced

**Sources:** [SKILL.md:201-210]()

---

## Framework-Specific Implementation Examples

While VibeSec-Skill does not provide implementation code directly (it guides AI code generation), the following patterns illustrate how CSRF protection concepts map to common frameworks.

### Token Generation and Validation Pattern

```mermaid
graph TB
    subgraph "Server-Side Components"
        SessionStore["Session Storage<br/>(Redis, Database, Memory)"]
        TokenGen["Token Generator<br/>crypto.randomBytes(32)"]
        Middleware["CSRF Validation<br/>Middleware"]
    end
    
    subgraph "Request Flow"
        Req["Incoming Request"]
        ExtractToken["Extract Token<br/>(header/body)"]
        ExtractSession["Extract Session<br/>(cookie)"]
        Compare["Compare Tokens"]
        Decision{"Match?"}
        Accept["Process Request"]
        Reject["403 Forbidden"]
    end
    
    TokenGen --> SessionStore
    SessionStore -.->|"Retrieve<br/>stored token"| Middleware
    
    Req --> ExtractToken
    Req --> ExtractSession
    ExtractToken --> Compare
    ExtractSession --> SessionStore
    SessionStore --> Compare
    Compare --> Decision
    Decision -->|"Yes"| Accept
    Decision -->|"No"| Reject
```

### Cookie Security Configuration Mapping

| Framework/Platform | Cookie Configuration Code Reference |
|-------------------|-------------------------------------|
| **Express.js (Node.js)** | `res.cookie('session', token, { sameSite: 'strict', secure: true, httpOnly: true })` |
| **Django (Python)** | `SESSION_COOKIE_SAMESITE = 'Strict'`, `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True` |
| **Laravel (PHP)** | `'same_site' => 'strict'`, `'secure' => true`, `'http_only' => true` in `config/session.php` |
| **ASP.NET Core (C#)** | `options.Cookie.SameSite = SameSiteMode.Strict; options.Cookie.SecurePolicy = CookieSecurePolicy.Always; options.Cookie.HttpOnly = true;` |
| **Rails (Ruby)** | `config.action_dispatch.cookies_same_site_protection = :strict`, `secure: true`, `httponly: true` |

**Sources:** [SKILL.md:170-210]()

---

## Integration with VibeSec-Skill Workflow

CSRF protection guidance is automatically applied when AI platforms consume SKILL.md during code generation.

### Code Generation Integration

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant AI as "AI Platform<br/>(Claude/Cursor/Copilot)"
    participant Skill as "SKILL.md<br/>Lines 147-211"
    participant Code as "Generated Code"
    
    Dev->>AI: "Create login endpoint"
    AI->>Skill: "Query CSRF requirements"
    Skill->>AI: "Return directives:<br/>- Token validation required<br/>- Pre-auth action category<br/>- SameSite cookie setup<br/>- Token regeneration on login"
    
    AI->>Code: "Generate endpoint with:<br/>- CSRF token validation<br/>- SameSite=Strict cookie<br/>- Token regeneration logic<br/>- Security comments"
    
    Code->>Dev: "Secure login implementation<br/>with CSRF protection"
    
    Note over Dev,Code: Security embedded at generation time
```

The AI platform references SKILL.md sections during code generation to:

1. **Identify endpoint category** — Classify as authenticated action or pre-authentication action
2. **Apply token validation** — Include cryptographic token generation and validation logic
3. **Configure cookies** — Set `SameSite`, `Secure`, `HttpOnly` attributes
4. **Handle edge cases** — Implement mandatory validation, token regeneration, scope checking
5. **Add verification comments** — Document security implementation for code review

**Sources:** [SKILL.md:147-211](), [README.md:76-83]()

---

## Relationship to Core Security Principles

CSRF protection exemplifies VibeSec-Skill's core security principles in practice:

| Core Principle | CSRF Application |
|---------------|------------------|
| **Defense in Depth** | Combine CSRF tokens + SameSite cookies + Origin/Referer validation (never rely on single control) |
| **Fail Securely** | Missing/invalid token = request rejected (403); never process request optimistically |
| **Least Privilege** | Token scoped to specific session; each session has unique token; no token reuse |
| **Input Validation** | Validate token presence, format, cryptographic validity, session binding server-side |
| **Output Encoding** | Not directly applicable to CSRF (relevant to XSS; see [Cross-Site Scripting Prevention](#6.1)) |

**Sources:** [SKILL.md:10-18](), [SKILL.md:147-211]()

---

## Common Vulnerability Patterns Prevented

VibeSec-Skill's CSRF protection addresses the following OWASP Top 10 and common vulnerability patterns:

- **A01:2021 – Broken Access Control** — CSRF enables unauthorized actions; token validation enforces legitimate request origin
- **A07:2021 – Identification and Authentication Failures** — Login CSRF allows attackers to fix victim sessions to attacker accounts
- **CWE-352: Cross-Site Request Forgery (CSRF)** — Direct mitigation through token-based validation
- **Session Fixation** — Token regeneration after authentication prevents session fixation combo attacks
- **Privilege Escalation** — CSRF protection on role change endpoints prevents unauthorized privilege elevation

**Sources:** [SKILL.md:147-211](), [README.md:60-67]()

---

# Page: Secret Exposure & Open Redirect Prevention

# Secret Exposure & Open Redirect Prevention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This page documents prevention strategies for two client-side vulnerability classes: **secret exposure** (sensitive data leaking to client-side code) and **open redirect** (unvalidated URL redirection). These vulnerabilities allow attackers to exfiltrate credentials or phish users by exploiting improper handling of sensitive data and user-controlled URLs.

For related client-side vulnerabilities, see [Cross-Site Scripting (XSS) Prevention](#6.1) and [Cross-Site Request Forgery (CSRF) Protection](#6.2). For server-side concerns like API key management in backend services, see [Server-Side Security](#7).

**Sources:** [SKILL.md:213-302]()

---

## Secret Exposure Prevention

### What Secrets Must Never Be Exposed

The following categories of sensitive information must never be accessible to client-side code or exposed in client-visible artifacts:

| Category | Examples | Risk |
|----------|----------|------|
| **API Keys and Secrets** | Third-party API keys (Stripe, AWS, etc.), Database connection strings, JWT signing secrets, Encryption keys, OAuth client secrets, Internal service URLs/credentials | Credential theft, unauthorized API usage, account takeover |
| **Sensitive User Data** | Full credit card numbers, Social Security Numbers, Passwords (even hashed), Security questions/answers, Full phone numbers (mask: `***-***-1234`), Sensitive PII not needed for display | Privacy breach, identity theft, regulatory violation (PCI-DSS, GDPR) |
| **Infrastructure Details** | Internal IP addresses, Database schemas, Debug information, Stack traces in production, Server software versions | Information disclosure enabling targeted attacks |

**Sources:** [SKILL.md:217-241]()

---

### Where Secrets Can Hide

Secrets often leak through overlooked channels in client-side applications. All of the following must be audited:

```mermaid
graph TB
    subgraph "Client-Side Exposure Vectors"
        JS["JavaScript bundles<br/>(app.js, vendor.js)"]
        SM["Source maps<br/>(.map files)"]
        HTML["HTML comments<br/><!-- ... -->"]
        Forms["Hidden form fields<br/><input type='hidden'>"]
        Attrs["Data attributes<br/>data-api-key=..."]
        Storage["LocalStorage/<br/>SessionStorage"]
        SSR["Initial state in SSR apps<br/>(hydration data)"]
        ENV["Environment variables<br/>(NEXT_PUBLIC_*, REACT_APP_*)"]
    end
    
    subgraph "Attack Surface"
        ViewSource["View Page Source"]
        DevTools["Browser DevTools"]
        NetworkTab["Network Inspector"]
        BundleAnalysis["Bundle Analysis Tools"]
    end
    
    JS --> ViewSource
    SM --> BundleAnalysis
    HTML --> ViewSource
    Forms --> ViewSource
    Attrs --> DevTools
    Storage --> DevTools
    SSR --> ViewSource
    ENV --> BundleAnalysis
    
    ViewSource --> Attacker["Attacker extracts secrets"]
    DevTools --> Attacker
    NetworkTab --> Attacker
    BundleAnalysis --> Attacker
```

**Diagram: Secret Exposure Attack Surface**

**Key exposure channels:**

- **JavaScript bundles** including source maps that may contain unobfuscated secrets
- **HTML comments** often left by developers during debugging
- **Hidden form fields** that pass secrets to client-side JavaScript
- **Data attributes** (`data-*`) on DOM elements
- **LocalStorage/SessionStorage** containing API keys or tokens
- **Initial state/hydration data** in server-side rendered applications (e.g., `window.__INITIAL_STATE__`)
- **Environment variables** exposed via build tools (variables prefixed with `NEXT_PUBLIC_*`, `REACT_APP_*`, `VITE_*`)

**Sources:** [SKILL.md:242-251]()

---

### Prevention Strategies

#### Environment Variable Isolation

```mermaid
graph LR
    subgraph "Incorrect Pattern"
        Client1["Client-side code"]
        EnvVar1["process.env.STRIPE_SECRET_KEY"]
        Bundle1["Bundled in app.js"]
        
        Client1 --> EnvVar1
        EnvVar1 --> Bundle1
    end
    
    subgraph "Correct Pattern"
        Client2["Client-side code"]
        API["Backend API endpoint"]
        EnvVar2[".env file<br/>(server-side only)"]
        
        Client2 -->|"API call"| API
        API --> EnvVar2
    end
    
    Bundle1 --> Exposed["Secret exposed to browser"]
    EnvVar2 --> Safe["Secret never leaves server"]
    
    style Exposed fill:#fee
    style Safe fill:#efe
```

**Diagram: Environment Variable Security Pattern**

**Core principles:**

1. **Store secrets in `.env` files** — Never commit `.env` files to version control; use `.env.example` templates
2. **Server-side only API calls** — Any operation requiring secrets must execute on the backend
3. **Prefix conventions** — Understand that build tools expose variables with specific prefixes (`NEXT_PUBLIC_`, `REACT_APP_`, etc.) to client-side code

**Example of vulnerable vs. secure patterns:**

```javascript
// VULNERABLE — Secret exposed in browser bundle
const stripeKey = process.env.STRIPE_SECRET_KEY;
stripe.checkout(stripeKey);

// SECURE — Secret stays on server
// Client calls backend API, backend uses secret
fetch('/api/create-checkout', { method: 'POST' })
  .then(res => res.json())
  .then(session => stripe.redirectToCheckout({ sessionId: session.id }));
```

**Sources:** [SKILL.md:252-256]()

---

## Open Redirect Prevention

### Vulnerable Endpoints

Any endpoint that accepts a URL parameter for redirection is vulnerable to open redirect attacks. Common scenarios include:

- **Post-authentication redirects** — `?next=/dashboard`, `?redirect_uri=...`
- **Logout redirects** — `?return_to=...`
- **Social login callbacks** — OAuth `redirect_uri` parameters
- **Multi-step workflows** — Wizards that redirect between steps
- **Error handlers** — `?error_redirect=...`
- **Marketing campaigns** — Click-through tracking URLs

**Sources:** [SKILL.md:259-263]()

---

### Protection Strategies

```mermaid
graph TB
    UserInput["User-provided URL<br/>(e.g., ?redirect=...)"]
    
    subgraph "Validation Strategies"
        Strategy1["Strategy 1:<br/>Allowlist Validation"]
        Strategy2["Strategy 2:<br/>Relative URLs Only"]
        Strategy3["Strategy 3:<br/>Indirect References"]
    end
    
    UserInput --> Strategy1
    UserInput --> Strategy2
    UserInput --> Strategy3
    
    Strategy1 --> Parse1["Parse URL<br/>(extract hostname)"]
    Parse1 --> Check1["Check if hostname<br/>in allowed_domains[]"]
    Check1 -->|"Match"| Allow1["Allow redirect"]
    Check1 -->|"No match"| Deny1["Deny redirect"]
    
    Strategy2 --> Validate2["Validate path format<br/>(starts with '/', no '//')"]
    Validate2 -->|"Valid"| Allow2["Allow redirect"]
    Validate2 -->|"Invalid"| Deny2["Deny redirect"]
    
    Strategy3 --> Lookup["Lookup in mapping<br/>{'dashboard': '/dashboard'}"]
    Lookup -->|"Found"| Allow3["Redirect to mapped URL"]
    Lookup -->|"Not found"| Deny3["Deny redirect"]
    
    style Allow1 fill:#efe
    style Allow2 fill:#efe
    style Allow3 fill:#efe
    style Deny1 fill:#fee
    style Deny2 fill:#fee
    style Deny3 fill:#fee
```

**Diagram: Open Redirect Validation Flow**

#### Strategy 1: Allowlist Validation

Maintain a strict list of permitted domains for redirection:

```python
# Pseudocode from SKILL.md:265-272
allowed_domains = ['yourdomain.com', 'app.yourdomain.com']

function isValidRedirect(url):
    parsed = parseUrl(url)
    return parsed.hostname in allowed_domains
```

**Key considerations:**
- Use exact string matching on fully-qualified domain names
- Include all legitimate subdomains explicitly
- Do not use wildcard matching (`*.yourdomain.com`) as it may be vulnerable to bypasses

#### Strategy 2: Relative URLs Only

Accept only path components without schemes or hostnames:

```python
# Accept: /dashboard, /settings/profile
# Reject: https://evil.com, //evil.com

function isValidRedirect(url):
    # Validate path starts with '/' and doesn't contain '//'
    if url.startswith('/') and '//' not in url:
        return True
    return False
```

**Key considerations:**
- Ensure path does not start with `//` (protocol-relative URL)
- Validate no protocol schemes (`http:`, `https:`, `javascript:`)

#### Strategy 3: Indirect References

Use a mapping of keys to actual URLs:

```python
# User provides: ?redirect=dashboard
# Mapping: {'dashboard': '/dashboard', 'settings': '/settings'}

redirect_map = {
    'dashboard': '/dashboard',
    'settings': '/settings/profile',
    'billing': '/account/billing'
}

target_url = redirect_map.get(user_input)
if target_url is None:
    # Invalid redirect key, use default
    target_url = '/dashboard'
```

**Sources:** [SKILL.md:265-280]()

---

### Bypass Techniques to Block

The following table documents open redirect bypass techniques that must be prevented:

| Technique | Example | Why It Works | Prevention |
|-----------|---------|--------------|------------|
| **@ symbol** | `https://legit.com@evil.com` | Browser navigates to `evil.com` with `legit.com` as username | Parse URL properly, validate hostname component only |
| **Subdomain abuse** | `https://legit.com.evil.com` | `evil.com` owns the subdomain | Validate against exact allowed domains, not substring matching |
| **Protocol tricks** | `javascript:alert(1)` | XSS via redirect | Allowlist `http`/`https` schemes only |
| **Double URL encoding** | `%252f%252fevil.com` | Decodes to `//evil.com` after double decode | Normalize once before validation, or reject encoded slashes |
| **Backslash** | `https://legit.com\@evil.com` | Some parsers normalize `\` to `/` | Reject URLs containing backslashes |
| **Null byte** | `https://legit.com%00.evil.com` | Some parsers truncate at null | Sanitize/reject null bytes before validation |
| **Tab/newline** | `https://legit.com%09.evil.com` | Whitespace confusion in parsers | Reject URLs with whitespace characters |
| **Unicode normalization** | `https://legіt.com` (Cyrillic і) | IDN homograph attack (see below) | Convert to Punycode before validation |
| **Data URLs** | `data:text/html,<script>...` | Direct payload execution | Reject `data:` scheme |
| **Protocol-relative** | `//evil.com` | Uses current page's protocol | Reject URLs starting with `//` |
| **Fragment abuse** | `https://legit.com#@evil.com` | Parsed differently by different libraries | Validate full parsed hostname, not raw string |

**Sources:** [SKILL.md:282-296]()

---

### IDN Homograph Attack Protection

Internationalized Domain Names (IDN) allow Unicode characters in domain names, enabling **homograph attacks** where visually similar characters create deceptive URLs.

**Example:**
- Legitimate: `https://paypal.com`
- Malicious: `https://pаypal.com` (Cyrillic 'а' instead of Latin 'a')

#### Protection Strategy

```mermaid
graph LR
    Input["User-provided URL<br/>(may contain Unicode)"]
    
    Convert["Convert to Punycode<br/>(xn--... format)"]
    
    Validate["Validate against<br/>allowlist"]
    
    Decision{"Allowed?"}
    
    Input --> Convert
    Convert --> Validate
    Validate --> Decision
    Decision -->|"Yes"| Allow["Redirect allowed"]
    Decision -->|"No"| Block["Block redirect"]
    
    Alternative["Alternative:<br/>Block non-ASCII domains<br/>for sensitive redirects"]
    
    style Allow fill:#efe
    style Block fill:#fee
```

**Diagram: IDN Homograph Attack Prevention**

**Implementation approaches:**

1. **Convert URLs to Punycode before validation** — Punycode represents Unicode domains in ASCII (e.g., `pаypal.com` → `xn--pypal-4ve.com`)
2. **Block non-ASCII domains entirely** for sensitive redirects (post-authentication, payment flows)

**Sources:** [SKILL.md:298-301]()

---

## Implementation Pattern Reference

The following pseudocode demonstrates a complete open redirect validation function combining multiple strategies:

```python
# Pattern combining allowlist and relative URL validation
function validateRedirect(user_provided_url, allowed_domains):
    # Strategy 1: Check if it's a safe relative URL
    if user_provided_url.startswith('/') and '//' not in user_provided_url:
        # Additional check: no protocol schemes
        if ':' not in user_provided_url:
            return user_provided_url
    
    # Strategy 2: Parse and validate against allowlist
    try:
        parsed = parseUrl(user_provided_url)
        
        # Reject non-HTTP(S) schemes
        if parsed.scheme not in ['http', 'https']:
            return None
        
        # Convert to Punycode for IDN protection
        hostname_punycode = toPunycode(parsed.hostname)
        
        # Check against allowlist
        if hostname_punycode in allowed_domains:
            return user_provided_url
    except:
        # Invalid URL format
        return None
    
    # Default: deny redirect
    return None

# Usage
allowed = ['yourdomain.com', 'app.yourdomain.com']
redirect_url = validateRedirect(request.params['redirect'], allowed)

if redirect_url:
    response.redirect(redirect_url)
else:
    response.redirect('/dashboard')  # Safe default
```

**Sources:** [SKILL.md:265-301]()

---

## Verification Checklist

Use this checklist when implementing or reviewing code that handles secrets or redirects:

### Secret Exposure Prevention

- [ ] No API keys, database credentials, or encryption keys in client-side code
- [ ] Environment variables with secrets do not use public prefixes (`NEXT_PUBLIC_*`, `REACT_APP_*`, `VITE_*`)
- [ ] Source maps disabled in production or do not contain sensitive code paths
- [ ] HTML source does not contain comments with credentials or internal URLs
- [ ] LocalStorage/SessionStorage does not store API keys (use httpOnly cookies for tokens)
- [ ] SSR initial state does not include server-side secrets
- [ ] Full credit card numbers, SSNs masked or not sent to client
- [ ] Stack traces and debug information disabled in production
- [ ] Internal IP addresses and infrastructure details not exposed

### Open Redirect Prevention

- [ ] All redirect parameters validated against allowlist or use relative URLs only
- [ ] URL scheme restricted to `http`/`https` only
- [ ] URLs parsed and hostname component validated, not substring matching
- [ ] Protocol-relative URLs (`//evil.com`) rejected
- [ ] JavaScript and data URL schemes blocked
- [ ] Double URL encoding normalized before validation
- [ ] Null bytes, backslashes, and whitespace characters rejected
- [ ] IDN homograph attacks prevented via Punycode conversion or ASCII-only policy
- [ ] Default redirect provided when validation fails (fail closed)
- [ ] No user input directly concatenated into redirect response

**Sources:** [SKILL.md:213-302]()

---

## Related Security Concerns

Secret exposure and open redirect vulnerabilities often interact with other security domains:

- **XSS via open redirect** — `javascript:` protocol redirects execute code; see [Cross-Site Scripting (XSS) Prevention](#6.1)
- **CSRF token leakage** — Tokens in URLs can leak via Referer header on redirects; see [Cross-Site Request Forgery (CSRF) Protection](#6.2)
- **SSRF via redirect chain** — Server-side redirect following can enable SSRF; see [Server-Side Request Forgery (SSRF) Prevention](#7.1)
- **JWT secrets in client code** — Signing secrets must never be client-accessible; see [JWT Security](#8.2)

**Sources:** [SKILL.md:213-302]()

---

# Page: Server-Side Security

# Server-Side Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This page provides an overview of server-side vulnerability prevention in VibeSec-Skill, covering the five primary attack vectors that occur when servers process user-controlled data: Server-Side Request Forgery (SSRF), SQL Injection, XML External Entity (XXE), Path Traversal, and Insecure File Upload.

Server-side vulnerabilities differ from client-side attacks in that they exploit server processing logic rather than browser behavior. These vulnerabilities typically allow attackers to read sensitive files, execute arbitrary code, access internal network resources, or exfiltrate data.

For client-side vulnerability prevention (XSS, CSRF, open redirects), see [Client-Side Security](#6). For access control and authorization issues (IDOR, privilege escalation), see [Access Control & Authorization](#5). For authentication-specific security, see [Authentication & Session Security](#8).

**Sources:** [SKILL.md:321-627]()

---

## Server-Side Attack Surface

Server-side vulnerabilities emerge wherever user input influences server behavior. The five attack vectors covered by VibeSec-Skill represent distinct exploitation paths, but share common characteristics.

### Attack Vector Categories

| Attack Vector | Primary Exploit | Common Entry Points | Impact |
|---------------|-----------------|---------------------|--------|
| **SSRF** | Server makes requests to attacker-controlled URLs | Webhooks, URL previews, PDF generators, import features | Internal network access, cloud metadata theft, port scanning |
| **SQL Injection** | Malicious SQL executed in database queries | Any dynamic query construction with user input | Data exfiltration, authentication bypass, data manipulation |
| **XXE** | XML parser processes malicious external entities | XML uploads, SOAP APIs, document processing | File disclosure, SSRF, denial of service |
| **Path Traversal** | Access files outside intended directory | File download/upload, template selection | Arbitrary file read, configuration disclosure |
| **Insecure Upload** | Upload malicious files that execute on server | File upload endpoints, avatar uploads, document imports | Remote code execution, XSS, denial of service |

**Sources:** [SKILL.md:323-627]()

---

## Common Patterns Across Server-Side Vulnerabilities

Despite their distinct attack mechanisms, all server-side vulnerabilities in VibeSec-Skill follow a common defensive pattern based on the core security principles defined in [SKILL.md:12-17]().

### Shared Defensive Principles

```mermaid
graph TB
    subgraph "Core Security Principles"
        P1["Defense in Depth<br/>Multiple validation layers"]
        P2["Fail Securely<br/>Deny on error"]
        P3["Least Privilege<br/>Minimal permissions"]
        P4["Input Validation<br/>Server-side only"]
    end
    
    subgraph "Server-Side Attack Vectors"
        SSRF["SSRF Prevention"]
        SQL["SQL Injection Prevention"]
        XXE["XXE Prevention"]
        Path["Path Traversal Prevention"]
        Upload["File Upload Prevention"]
    end
    
    subgraph "Common Implementation Pattern"
        V1["Validate Input<br/>Type, format, range checks"]
        V2["Sanitize/Escape<br/>Context-specific encoding"]
        V3["Use Safe APIs<br/>Parameterized, sandboxed"]
        V4["Validate Output<br/>Ensure expected result"]
    end
    
    P1 --> V1
    P2 --> V4
    P3 --> V3
    P4 --> V1
    
    V1 --> SSRF
    V1 --> SQL
    V1 --> XXE
    V1 --> Path
    V1 --> Upload
    
    V2 --> SSRF
    V2 --> SQL
    V2 --> Path
    
    V3 --> SQL
    V3 --> XXE
    V3 --> Upload
    
    V4 --> SSRF
    V4 --> Path
```

**Diagram: Core Principles Applied to Server-Side Security**

All five server-side attack vectors implement defense in depth through input validation, context-specific sanitization, safe API usage, and output validation. The core principles cascade to create a consistent security model across different vulnerability classes.

**Sources:** [SKILL.md:10-17](), [SKILL.md:321-627]()

---

## The Five Server-Side Attack Vectors

### 1. Server-Side Request Forgery (SSRF)

SSRF occurs when servers make HTTP requests to URLs controlled or influenced by users. Attackers exploit this to access internal network resources, cloud metadata endpoints, or conduct port scanning.

**Vulnerable Features:** Webhooks, URL previews, PDF generators from URLs, image fetching, RSS readers, API integrations with user-provided endpoints, proxy functionality, HTML-to-PDF converters.

**Primary Defenses:**
- Allowlist approved domains
- Network segmentation for URL-fetching services
- DNS resolution with IP validation
- Cloud metadata endpoint blocking

For comprehensive SSRF prevention including DNS rebinding protection and bypass technique coverage, see [Server-Side Request Forgery (SSRF) Prevention](#7.1).

**Sources:** [SKILL.md:323-391]()

### 2. SQL Injection

SQL injection occurs when user input is incorporated into SQL queries without proper parameterization, allowing attackers to execute arbitrary SQL commands.

**Injection Points:** WHERE clauses, ORDER BY, LIMIT/OFFSET, table/column names, INSERT/UPDATE values, IN clauses, LIKE patterns.

**Primary Defenses:**
- Parameterized queries (prepared statements)
- ORM usage with safe methods
- Input validation for data types
- Whitelisting for non-parameterizable elements (ORDER BY, table names)

For detailed SQL injection prevention patterns and ORM-specific guidance, see [SQL Injection Prevention](#7.2).

**Sources:** [SKILL.md:456-499]()

### 3. XML External Entity (XXE)

XXE vulnerabilities arise when XML parsers process external entity references in user-supplied XML, allowing file disclosure, SSRF, and denial of service.

**Vulnerable Scenarios:** SOAP APIs, XML-RPC, XML file uploads, configuration parsing, RSS/Atom feeds, Office documents (DOCX/XLSX/PPTX), SVG files, SAML assertions.

**Primary Defenses:**
- Disable DTD processing
- Disable external entity resolution
- Use JSON instead of XML where possible
- Parser-specific security configurations

For language-specific XXE prevention code examples (Java, Python, PHP, Node.js, .NET), see [XML External Entity (XXE) Prevention](#7.3).

**Sources:** [SKILL.md:501-568]()

### 4. Path Traversal

Path traversal vulnerabilities occur when user input controls file paths, allowing access to files outside intended directories through `../` sequences or encoding variations.

**Vulnerable Patterns:** Direct path concatenation, template selection, file download by name, archive extraction.

**Primary Defenses:**
- Indirect file references (mapping user input to safe paths)
- Path canonicalization with base directory validation
- Input sanitization (remove `..`, absolute path indicators)
- File extension whitelisting

For canonicalization implementation patterns and bypass techniques, see [Path Traversal Prevention](#7.4).

**Sources:** [SKILL.md:570-627]()

### 5. Insecure File Upload

File upload vulnerabilities allow attackers to upload malicious files that execute on the server, inject XSS, or exploit file processing libraries.

**Validation Requirements:** File type validation (extension + magic bytes), file content validation (structure parsing), file size limits, polyglot file detection.

**Common Bypasses:** Extension manipulation (`shell.php.jpg`), null byte injection, MIME type spoofing, magic byte prepending, SVG with JavaScript, XXE via documents, ZIP slip, ImageMagick exploits.

**Primary Defenses:**
- Magic byte validation matching expected type
- File renaming with random UUIDs
- Storage outside webroot
- Restrictive Content-Disposition headers
- CDN/separate domain isolation

For magic bytes reference table and comprehensive bypass prevention, see [Insecure File Upload Prevention](#7.5).

**Sources:** [SKILL.md:393-454]()

---

## Server-Side Security Implementation Architecture

The following diagram illustrates how VibeSec-Skill's server-side security directives map to code-level implementation patterns across different vulnerability classes.

```mermaid
graph TB
    subgraph "User Input Layer"
        URL["User-Controlled URL<br/>webhooks, imports"]
        Query["User-Controlled Query Params<br/>search, filters"]
        XML["User-Controlled XML<br/>SOAP, uploads"]
        FilePath["User-Controlled Path<br/>downloads, templates"]
        FileUpload["User-Controlled File<br/>avatars, documents"]
    end
    
    subgraph "Validation Layer"
        V1["allowlist validation<br/>isValidRedirect()"]
        V2["parameterized queries<br/>execute(query, params)"]
        V3["disable external entities<br/>setFeature(DISALLOW_DTD)"]
        V4["canonicalization<br/>safe_join(base, user_path)"]
        V5["magic byte check<br/>validateMagicBytes()"]
    end
    
    subgraph "Safe Processing Layer"
        S1["DNS resolution + IP validation<br/>resolveAndValidate()"]
        S2["prepared statements<br/>db.execute(?, [value])"]
        S3["secure parser config<br/>XMLParser(resolve_entities=False)"]
        S4["base directory enforcement<br/>os.path.commonpath([base, target])"]
        S5["file type enforcement<br/>imageLibrary.process()"]
    end
    
    subgraph "Output/Action Layer"
        O1["HTTP request with timeout<br/>fetch(validatedURL, {timeout})"]
        O2["Database query execution<br/>SELECT * FROM users WHERE id=?"]
        O3["XML parsing result<br/>etree.parse(xml, parser)"]
        O4["File read operation<br/>open(canonical_path, 'rb')"]
        O5["File storage<br/>store(uuid_name, outside_webroot)"]
    end
    
    URL --> V1 --> S1 --> O1
    Query --> V2 --> S2 --> O2
    XML --> V3 --> S3 --> O3
    FilePath --> V4 --> S4 --> O4
    FileUpload --> V5 --> S5 --> O5
    
    subgraph "Security Checklist Enforcement"
        C1["Block cloud metadata IPs<br/>169.254.169.254"]
        C2["Least privilege DB user<br/>minimal permissions"]
        C3["Use defusedxml library<br/>safe defaults"]
        C4["Test with ../ variants<br/>..%2f, ..%5c"]
        C5["Validate with nosniff header<br/>X-Content-Type-Options"]
    end
    
    S1 -.-> C1
    S2 -.-> C2
    S3 -.-> C3
    S4 -.-> C4
    S5 -.-> C5
```

**Diagram: Server-Side Vulnerability Prevention - Code-Level Implementation Pattern**

This diagram maps user input sources to specific validation functions, safe processing APIs, and secure output operations. Function names reflect actual patterns from [SKILL.md:321-627](): `isValidRedirect()` for SSRF allowlist validation, `execute(query, params)` for SQL parameterization, `setFeature(DISALLOW_DTD)` for XXE prevention, `safe_join(base, user_path)` for path traversal canonicalization, and `validateMagicBytes()` for file upload verification. The security checklist layer shows additional defense-in-depth measures specific to each attack vector.

**Sources:** [SKILL.md:266-272](), [SKILL.md:464-471](), [SKILL.md:526-558](), [SKILL.md:600-611](), [SKILL.md:401-409]()

---

## Attack Prevention Flow: From User Input to Secure Execution

The following sequence diagram shows the temporal flow of security validation for server-side operations, demonstrating how VibeSec-Skill directives translate to runtime security checks.

```mermaid
sequenceDiagram
    participant User
    participant Endpoint["API Endpoint<br/>POST /webhook"]
    participant Validator["Input Validator<br/>validateInput()"]
    participant Sanitizer["Sanitizer<br/>sanitize()/escape()"]
    participant SafeAPI["Safe API<br/>parameterize()/allowlist()"]
    participant Backend["Backend Service<br/>Database/FileSystem/Network"]
    participant Logger["Security Logger<br/>logSecurityEvent()"]
    
    User->>Endpoint: "POST {url: 'http://attacker.com'}"
    
    Note over Endpoint: SSRF Prevention Flow
    Endpoint->>Validator: "validate(url)"
    activate Validator
    Validator->>Validator: "check scheme (HTTP/HTTPS only)"
    Validator->>Validator: "resolve DNS"
    Validator->>Validator: "check IP not private/cloud metadata"
    
    alt Invalid Input
        Validator-->>Endpoint: "ValidationError"
        Endpoint-->>User: "400 Bad Request"
        Endpoint->>Logger: "log blocked SSRF attempt"
    else Valid Input
        Validator-->>Endpoint: "validated URL + resolved IP"
        deactivate Validator
        
        Endpoint->>SafeAPI: "makeRequest(url, {timeout, noRedirects})"
        activate SafeAPI
        SafeAPI->>Backend: "HTTP request with IP pinning"
        Backend-->>SafeAPI: "response"
        SafeAPI-->>Endpoint: "safe response"
        deactivate SafeAPI
    end
    
    Note over Endpoint: SQL Injection Prevention Flow
    User->>Endpoint: "GET /users?id=1' OR '1'='1"
    Endpoint->>Validator: "validateType(id, 'integer')"
    activate Validator
    
    alt Non-Integer Input
        Validator-->>Endpoint: "TypeError"
        Endpoint-->>User: "400 Bad Request"
        Endpoint->>Logger: "log SQL injection attempt"
    else Valid Integer
        Validator-->>Endpoint: "validated integer"
        deactivate Validator
        
        Endpoint->>SafeAPI: "db.execute('SELECT * FROM users WHERE id=?', [id])"
        activate SafeAPI
        Note over SafeAPI: Parameterized query prevents SQL injection
        SafeAPI->>Backend: "prepared statement"
        Backend-->>SafeAPI: "query result"
        SafeAPI-->>Endpoint: "safe data"
        deactivate SafeAPI
    end
    
    Note over Endpoint: Path Traversal Prevention Flow
    User->>Endpoint: "GET /download?file=../../etc/passwd"
    Endpoint->>Sanitizer: "safe_join(base_dir, user_file)"
    activate Sanitizer
    Sanitizer->>Sanitizer: "canonicalize paths"
    Sanitizer->>Sanitizer: "check commonpath == base_dir"
    
    alt Path Escapes Base Directory
        Sanitizer-->>Endpoint: "ValueError('Path traversal')"
        Endpoint-->>User: "403 Forbidden"
        Endpoint->>Logger: "log traversal attempt"
    else Path Within Base
        Sanitizer-->>Endpoint: "canonical_path"
        deactivate Sanitizer
        
        Endpoint->>Backend: "read(canonical_path)"
        Backend-->>Endpoint: "file contents"
    end
    
    Endpoint-->>User: "200 OK + secure response"
```

**Diagram: Server-Side Security Validation Flow**

This sequence diagram demonstrates the defense-in-depth pattern applied across SSRF, SQL injection, and path traversal prevention. Each attack vector follows a consistent flow: input validation (type/format checks), sanitization/escaping (context-specific), safe API usage (parameterization/allowlisting), and security logging. The pattern reflects the implementation guidance from [SKILL.md:340-391]() for SSRF, [SKILL.md:463-471]() for SQL injection, and [SKILL.md:600-611]() for path traversal. Failed validation results in 400/403 responses and security event logging, while successful validation proceeds to safe backend operations.

**Sources:** [SKILL.md:340-391](), [SKILL.md:463-471](), [SKILL.md:600-611]()

---

## Defense-in-Depth Implementation Matrix

The following table shows how multiple security controls are applied to each server-side vulnerability class, implementing the defense-in-depth principle from [SKILL.md:13]().

| Attack Vector | Input Validation | Safe API Usage | Output Validation | Additional Defenses |
|---------------|------------------|----------------|-------------------|---------------------|
| **SSRF** | URL scheme check, DNS resolution, IP range validation | HTTP client with timeout and redirect limits | Response size limits, content-type validation | Network segmentation, cloud metadata IP blocking |
| **SQL Injection** | Data type validation, input length limits | Parameterized queries, ORM safe methods | Never expose SQL errors to users | Least privilege DB user, disable dangerous functions |
| **XXE** | Schema validation (if DTD needed) | Disable external entities, disable DTD processing | N/A | Use JSON instead of XML, parser version updates |
| **Path Traversal** | Remove `..` sequences, whitelist characters | Canonicalization with base directory check | Validate file exists and is readable | Indirect file references, extension whitelisting |
| **File Upload** | Extension allowlist, magic byte validation | File type-specific parsers, sandboxed processing | Serve with `Content-Disposition: attachment` | Store outside webroot, random UUID names, separate domain |

**Sources:** [SKILL.md:340-391](), [SKILL.md:461-499](), [SKILL.md:523-568](), [SKILL.md:586-627](), [SKILL.md:398-454]()

---

## Common Bypass Techniques Across Attack Vectors

Attackers use similar bypass techniques across different server-side vulnerabilities. VibeSec-Skill addresses these bypass patterns explicitly.

### Encoding and Representation Bypasses

| Bypass Type | SSRF Example | SQL Example | Path Traversal Example | Prevention |
|-------------|--------------|-------------|------------------------|------------|
| **URL Encoding** | `http://127.0.0.1` → `http://127.0.0.%31` | `' OR 1=1` → `%27%20OR%201=1` | `../` → `%2e%2e%2f` | Decode before validation, validate canonical form |
| **Double Encoding** | `%2527` → `%27` → `'` | `%252f` → `%2f` → `/` | `%252e%252e%252f` | Normalize all encoding levels |
| **Alternative Representations** | Decimal IP: `2130706433` | Hex literals: `0x5345434554` | Windows separator: `..\\` | Canonicalize to standard format |
| **Null Byte Injection** | `http://legit.com%00.evil.com` | `admin'%00` | `shell.php%00.jpg` | Sanitize null bytes, check for truncation |
| **Unicode Normalization** | IDN homograph: `legіt.com` (Cyrillic) | NFKD normalization bypasses | Unicode lookalikes for `../` | Normalize to ASCII/Punycode |

**Sources:** [SKILL.md:349-365](), [SKILL.md:483-493](), [SKILL.md:615-618]()

---

## Framework-Specific Security Patterns

VibeSec-Skill provides language and framework-agnostic security guidance, but certain server-side vulnerabilities require framework-specific implementations.

### XXE Prevention by Language

| Language/Framework | Secure Configuration Function | Key Setting |
|-------------------|------------------------------|-------------|
| **Java** | `DocumentBuilderFactory.setFeature()` | `"http://apache.org/xml/features/disallow-doctype-decl", true` |
| **Python (lxml)** | `etree.XMLParser()` | `resolve_entities=False, no_network=True` |
| **PHP** | `libxml_disable_entity_loader()` | `libxml_disable_entity_loader(true)` |
| **Node.js** | Library configuration | `{ noent: false, dtdload: false }` |
| **.NET** | `XmlReaderSettings` | `DtdProcessing = DtdProcessing.Prohibit` |

Code examples for each language are provided in [SKILL.md:523-558]().

### SQL Injection Prevention by ORM

All ORMs provide parameterized query interfaces, but also expose raw query methods that can introduce SQL injection if misused. VibeSec-Skill emphasizes using ORM safe methods while watching for injection points in ORDER BY clauses and table names that cannot be parameterized.

**Sources:** [SKILL.md:473-477](), [SKILL.md:523-558]()

---

## Server-Side Security Checklists

VibeSec-Skill provides verification checklists for each attack vector to ensure comprehensive protection during code generation. The following is a consolidated checklist covering all five server-side vulnerabilities.

### Consolidated Server-Side Security Checklist

#### SSRF Protection
- [ ] URL scheme validation (HTTP/HTTPS only)
- [ ] DNS resolution with IP validation (not private/internal)
- [ ] Cloud metadata IPs explicitly blocked (`169.254.169.254`)
- [ ] Redirect following limited or disabled
- [ ] Request timeout configured
- [ ] Response size limits enforced
- [ ] Network isolation for URL-fetching services

#### SQL Injection Protection
- [ ] Parameterized queries used (no string concatenation)
- [ ] ORM safe methods used (avoid raw query methods)
- [ ] Data type validation on all inputs
- [ ] ORDER BY uses whitelisted columns
- [ ] Table/column names use whitelisting (cannot parameterize)
- [ ] Database user has least privilege permissions
- [ ] SQL errors never exposed to users

#### XXE Protection
- [ ] DTD processing disabled
- [ ] External entity resolution disabled
- [ ] External DTD loading disabled
- [ ] XInclude processing disabled
- [ ] XML parser version up-to-date
- [ ] JSON used instead of XML where possible

#### Path Traversal Protection
- [ ] User input never directly in file paths
- [ ] Paths canonicalized and validated against base directory
- [ ] `..` sequences removed or rejected
- [ ] Absolute path indicators blocked
- [ ] File extension whitelisting applied

#### File Upload Protection
- [ ] File extension validated against allowlist
- [ ] Magic bytes validated and match expected type
- [ ] File content parsed to validate structure
- [ ] Maximum file size enforced
- [ ] Files renamed with random UUIDs
- [ ] Files stored outside webroot or on separate domain
- [ ] `Content-Disposition: attachment` header set
- [ ] `X-Content-Type-Options: nosniff` header set

**Sources:** [SKILL.md:382-391](), [SKILL.md:494-499](), [SKILL.md:560-568](), [SKILL.md:621-627](), [SKILL.md:444-454]()

---

## Integration with VibeSec-Skill Workflow

When developers use VibeSec-Skill with an AI coding assistant, server-side security directives are automatically applied during code generation. The skill analyzes the request context to determine which server-side vulnerabilities are relevant.

### Context-Aware Security Application

- **Database operations detected** → SQL injection prevention applied (parameterized queries)
- **URL/webhook handling detected** → SSRF prevention applied (allowlist validation, IP checks)
- **XML processing detected** → XXE prevention applied (external entity disabling)
- **File path operations detected** → Path traversal prevention applied (canonicalization)
- **File upload endpoints detected** → Upload security applied (magic bytes, UUID renaming)

The AI assistant generates code with embedded security patterns, security comments explaining the protections, and compliance checklists referencing the specific VibeSec-Skill directives applied.

**Sources:** [SKILL.md:10-11](), [README.md:71-75]()

---

## Summary

Server-side security in VibeSec-Skill addresses five primary attack vectors through a consistent defense-in-depth pattern. Each vulnerability class (SSRF, SQL Injection, XXE, Path Traversal, File Upload) implements input validation, safe API usage, output validation, and additional security controls specific to the attack surface.

The security architecture maps directly to code-level implementation patterns with specific function signatures and security configurations. Common bypass techniques are addressed across all vulnerability classes through canonicalization, encoding normalization, and strict validation.

For detailed implementation guidance on each attack vector, refer to the child pages:
- [Server-Side Request Forgery (SSRF) Prevention](#7.1)
- [SQL Injection Prevention](#7.2)
- [XML External Entity (XXE) Prevention](#7.3)
- [Path Traversal Prevention](#7.4)
- [Insecure File Upload Prevention](#7.5)

**Sources:** [SKILL.md:321-627](), [SKILL.md:10-17]()

---

# Page: Server-Side Request Forgery (SSRF) Prevention

# Server-Side Request Forgery (SSRF) Prevention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document provides comprehensive guidance for preventing Server-Side Request Forgery (SSRF) vulnerabilities in web applications. SSRF occurs when an attacker can induce a server to make HTTP requests to arbitrary destinations, potentially accessing internal resources, cloud metadata services, or other sensitive endpoints.

This page covers server-side protection mechanisms for URL-based features. For client-side redirect vulnerabilities, see [Open Redirect Prevention](#6.3). For general input validation principles, see [Core Security Principles](#4).

**Sources:** [SKILL.md:323-391]()

---

## Vulnerability Overview

SSRF vulnerabilities allow attackers to abuse server-side functionality that fetches URLs to:
- Access internal network resources (databases, admin panels, internal APIs)
- Read cloud provider metadata endpoints (AWS, GCP, Azure credentials)
- Port scan internal infrastructure
- Bypass firewall restrictions
- Execute stored XSS through SVG/HTML injection
- Abuse trust relationships between services

```mermaid
graph TB
    subgraph "External Attacker"
        Attacker["Attacker"]
    end
    
    subgraph "Application Layer"
        WebApp["Web Application"]
        URLFetch["URL Fetching<br/>Service"]
    end
    
    subgraph "Internal Network"
        Database["Internal Database<br/>192.168.1.10"]
        AdminPanel["Admin Panel<br/>localhost:8080"]
        Metadata["Cloud Metadata<br/>169.254.169.254"]
    end
    
    subgraph "External Resources"
        LegitAPI["Legitimate API<br/>api.example.com"]
        AttackerServer["Attacker Server<br/>evil.com"]
    end
    
    Attacker -->|"1. Malicious URL"| WebApp
    WebApp -->|"2. Trigger fetch"| URLFetch
    URLFetch -.->|"3a. Intended"| LegitAPI
    URLFetch -.->|"3b. SSRF to internal"| Database
    URLFetch -.->|"3c. SSRF to admin"| AdminPanel
    URLFetch -.->|"3d. SSRF to metadata"| Metadata
    URLFetch -.->|"3e. SSRF to attacker"| AttackerServer
    
    style Attacker fill:#f8d7da
    style URLFetch fill:#fff3cd
    style Database fill:#ffe1e1
    style AdminPanel fill:#ffe1e1
    style Metadata fill:#ffe1e1
```

**Diagram: SSRF Attack Surface and Target Types**

**Sources:** [SKILL.md:323-327]()

---

## Vulnerable Features

The following application features commonly create SSRF attack surfaces when they accept or process user-controlled URLs:

| Feature Type | Description | Risk Level |
|-------------|-------------|------------|
| **Webhooks** | User provides callback URL for event notifications | High |
| **URL Previews** | Generate link previews from user-submitted URLs | High |
| **PDF Generators** | Convert URL content to PDF documents | High |
| **Image/File Fetching** | Load external images or files from URLs | High |
| **Import from URL** | Import data from user-specified endpoints | High |
| **RSS/Feed Readers** | Subscribe to and fetch RSS/Atom feeds | Medium |
| **API Integrations** | Connect to user-provided API endpoints | High |
| **Proxy Functionality** | Forward requests to user-specified destinations | Critical |
| **HTML to PDF/Image** | Render web pages as documents or images | High |

```mermaid
graph LR
    subgraph "User Input Vector"
        UserURL["User-Controlled URL"]
    end
    
    subgraph "Vulnerable Features"
        Webhook["webhook_url parameter"]
        Preview["url_to_preview parameter"]
        PDF["generate_pdf endpoint"]
        Import["import_from_url endpoint"]
        Proxy["proxy_url parameter"]
    end
    
    subgraph "Server Actions"
        HTTPRequest["HTTP Request<br/>Initiated by Server"]
    end
    
    UserURL --> Webhook
    UserURL --> Preview
    UserURL --> PDF
    UserURL --> Import
    UserURL --> Proxy
    
    Webhook --> HTTPRequest
    Preview --> HTTPRequest
    PDF --> HTTPRequest
    Import --> HTTPRequest
    Proxy --> HTTPRequest
    
    style HTTPRequest fill:#fff3cd
```

**Diagram: Common SSRF Entry Points in Application Features**

**Sources:** [SKILL.md:328-338]()

---

## Protection Strategies

### 1. Allowlist Approach (Preferred)

The most secure approach is to maintain a strict allowlist of permitted domains. Only requests to pre-approved domains are allowed.

```mermaid
graph TD
    Request["Incoming URL Request"]
    ParseURL["Parse URL"]
    ExtractDomain["Extract Domain"]
    CheckAllowlist{"Domain in<br/>Allowlist?"}
    Reject["Reject Request<br/>Return Error"]
    Proceed["Proceed with<br/>HTTP Request"]
    
    Request --> ParseURL
    ParseURL --> ExtractDomain
    ExtractDomain --> CheckAllowlist
    CheckAllowlist -->|"No"| Reject
    CheckAllowlist -->|"Yes"| Proceed
    
    style Reject fill:#f8d7da
    style Proceed fill:#d4edda
```

**Diagram: Allowlist Validation Flow**

Implementation pattern:
- Define `allowed_domains` list in configuration
- Parse user-provided URL
- Extract and normalize hostname
- Validate against allowlist before making request

**Sources:** [SKILL.md:341-343]()

### 2. Network Segmentation

Run URL-fetching services in isolated network segments with restricted access:
- Deploy in separate VPC/network zone
- Block outbound access to internal IP ranges
- Block access to cloud metadata endpoints
- Implement egress filtering rules
- Use dedicated service accounts with minimal permissions

**Sources:** [SKILL.md:345-347]()

---

## IP and DNS Bypass Techniques

Attackers use various encoding and representation techniques to bypass SSRF filters. The following table documents techniques that must be blocked:

| Technique | Example | Description | Detection Method |
|-----------|---------|-------------|------------------|
| **Decimal IP** | `http://2130706433` | 127.0.0.1 represented as decimal integer | Parse and validate resolved IP |
| **Octal IP** | `http://0177.0.0.1` | Leading zeros indicate octal encoding | Normalize before validation |
| **Hexadecimal IP** | `http://0x7f.0x0.0x0.0x1` | Hex representation with 0x prefix | Normalize before validation |
| **IPv6 Localhost** | `http://[::1]` | IPv6 loopback address | Check both IPv4 and IPv6 ranges |
| **IPv6 Mapped IPv4** | `http://[::ffff:127.0.0.1]` | IPv4 address in IPv6 format | Normalize to IPv4 before check |
| **Short IPv6** | `http://[::]` | All zeros notation | Expand and validate |
| **DNS Rebinding** | Attacker DNS returns internal IP | First resolution external, second internal | Pin resolved IP, re-validate |
| **CNAME to Internal** | Attacker domain points to internal host | DNS CNAME points to internal hostname | Resolve and validate final IP |
| **URL Parser Confusion** | `http://attacker.com#@internal` | Different parsers interpret differently | Use secure URL parser |
| **Redirect Chains** | External URL redirects to internal | HTTP redirect to internal resource | Validate each redirect hop |
| **IPv6 Scope ID** | `http://[fe80::1%25eth0]` | Interface-scoped IPv6 address | Block scope identifiers |
| **Rare IP Formats** | `http://127.1` | Shortened IP notation (127.0.0.1) | Normalize to full format |

```mermaid
graph TB
    Input["User-Provided URL"]
    
    subgraph "Bypass Attempts"
        Decimal["Decimal: 2130706433"]
        Octal["Octal: 0177.0.0.1"]
        Hex["Hex: 0x7f.0.0.0x1"]
        IPv6["IPv6: ::1"]
        Mapped["Mapped: ::ffff:127.0.0.1"]
        DNS["DNS Rebinding"]
        CNAME["CNAME Redirect"]
    end
    
    subgraph "Normalization & Validation"
        Parse["Parse URL"]
        Normalize["Normalize IP Format"]
        ResolveDNS["Resolve DNS"]
        ValidateIP["Validate IP Range"]
    end
    
    subgraph "Decision"
        IsInternal{"Internal IP?"}
        Block["Block Request"]
        Allow["Allow Request"]
    end
    
    Input --> Decimal & Octal & Hex & IPv6 & Mapped & DNS & CNAME
    Decimal & Octal & Hex & IPv6 & Mapped --> Parse
    DNS & CNAME --> ResolveDNS
    Parse --> Normalize
    Normalize --> ValidateIP
    ResolveDNS --> ValidateIP
    ValidateIP --> IsInternal
    IsInternal -->|"Yes"| Block
    IsInternal -->|"No"| Allow
    
    style Block fill:#f8d7da
    style Allow fill:#d4edda
```

**Diagram: IP/DNS Bypass Technique Detection Flow**

**Sources:** [SKILL.md:349-364]()

---

## DNS Rebinding Prevention

DNS rebinding attacks exploit the time-of-check-time-of-use (TOCTOU) gap by returning different IP addresses on subsequent DNS queries.

### Attack Sequence

1. Application resolves `attacker.com` → receives `1.2.3.4` (external IP)
2. Application validates `1.2.3.4` as safe
3. Application makes HTTP request to `attacker.com`
4. DNS query occurs again → receives `127.0.0.1` (internal IP)
5. Request reaches internal resource

### Prevention Methods

**Method 1: DNS Pinning** (Recommended)
1. Resolve DNS to IP address
2. Validate resolved IP is not internal/private
3. Pin the resolved IP for the HTTP request
4. Do not allow re-resolution during request

**Method 2: Double Resolution with Delay**
1. Resolve DNS and validate IP
2. Wait 500ms-1000ms
3. Resolve again and validate matches first resolution
4. Ensure both IPs are external and identical

**Sources:** [SKILL.md:366-371]()

---

## Cloud Metadata Protection

Cloud providers expose instance metadata at link-local addresses. These endpoints must be explicitly blocked:

| Cloud Provider | Metadata Endpoints | Contains |
|----------------|-------------------|----------|
| **AWS** | `169.254.169.254` | IAM credentials, user data, SSH keys |
| **GCP** | `metadata.google.internal`<br/>`169.254.169.254`<br/>`http://metadata` | Service account tokens, SSH keys, custom metadata |
| **Azure** | `169.254.169.254` | Access tokens, certificates, custom data |
| **DigitalOcean** | `169.254.169.254` | User data, SSH keys, network config |

```mermaid
graph TB
    subgraph "Server-Side Request"
        Request["URL Fetch Request"]
        ResolveDNS["Resolve DNS"]
        ResolvedIP["Resolved IP Address"]
    end
    
    subgraph "Metadata IP Check"
        CheckMeta{"IP matches<br/>169.254.169.254?"}
        CheckGCP{"Hostname matches<br/>metadata.google.internal?"}
        CheckMetaPattern{"IP in metadata<br/>IP ranges?"}
    end
    
    subgraph "Decision"
        BlockMeta["Block: Cloud Metadata Access"]
        ProceedValidation["Continue Validation"]
    end
    
    Request --> ResolveDNS
    ResolveDNS --> ResolvedIP
    ResolvedIP --> CheckMeta
    ResolvedIP --> CheckGCP
    ResolvedIP --> CheckMetaPattern
    
    CheckMeta -->|"Yes"| BlockMeta
    CheckGCP -->|"Yes"| BlockMeta
    CheckMetaPattern -->|"Yes"| BlockMeta
    CheckMeta -->|"No"| ProceedValidation
    CheckGCP -->|"No"| ProceedValidation
    CheckMetaPattern -->|"No"| ProceedValidation
    
    style BlockMeta fill:#f8d7da
    style ProceedValidation fill:#d4edda
```

**Diagram: Cloud Metadata Endpoint Protection Flow**

Additional protection measures:
- Block all link-local addresses (`169.254.0.0/16`)
- Block `metadata.google.internal` by hostname
- Block shorthand formats like `http://metadata`
- Implement network-level egress filtering

**Sources:** [SKILL.md:373-379]()

---

## Implementation Checklist

The following checklist provides comprehensive SSRF protection requirements:

### URL Validation
- [ ] Validate URL scheme is HTTP or HTTPS only (block `file://`, `ftp://`, `gopher://`, etc.)
- [ ] Parse URL using secure library
- [ ] Reject URLs with authentication credentials (`http://user:pass@host`)

### DNS and IP Validation
- [ ] Resolve DNS hostname to IP address
- [ ] Validate resolved IP is not in private ranges:
  - `10.0.0.0/8`
  - `172.16.0.0/12`
  - `192.168.0.0/16`
  - `127.0.0.0/8`
  - `169.254.0.0/16` (link-local)
  - `::1` (IPv6 loopback)
  - `fc00::/7` (IPv6 unique local)
- [ ] Block cloud metadata IPs explicitly (`169.254.169.254`)
- [ ] Pin resolved IP to prevent DNS rebinding

### Redirect Handling
- [ ] Limit or disable HTTP redirect following
- [ ] If following redirects, validate each redirect hop
- [ ] Set maximum redirect count (e.g., 3)
- [ ] Re-validate IP address for each redirect destination

### Request Configuration
- [ ] Set connection timeout (e.g., 5 seconds)
- [ ] Set read timeout (e.g., 10 seconds)
- [ ] Limit response size (e.g., 10MB maximum)
- [ ] Disable authentication forwarding

### Network Architecture
- [ ] Use network isolation where possible
- [ ] Deploy URL-fetching services in dedicated network segment
- [ ] Implement egress firewall rules
- [ ] Use dedicated service accounts with minimal permissions

```mermaid
graph TD
    Start["URL Input"]
    
    subgraph "Validation Pipeline"
        V1["Validate Scheme<br/>HTTP/HTTPS only"]
        V2["Parse URL<br/>Extract hostname"]
        V3["Resolve DNS<br/>Get IP address"]
        V4["Validate IP Range<br/>Not private/metadata"]
        V5["Pin IP Address"]
        V6["Configure Timeouts<br/>& Size Limits"]
        V7["Make Request<br/>with Pinned IP"]
        V8{"Redirect?"}
        V9["Validate Redirect<br/>Destination"]
    end
    
    subgraph "Outcomes"
        Success["Request Completed"]
        Reject["Reject & Log"]
    end
    
    Start --> V1
    V1 -->|"Invalid"| Reject
    V1 -->|"Valid"| V2
    V2 -->|"Parse Error"| Reject
    V2 -->|"Success"| V3
    V3 -->|"Resolution Failed"| Reject
    V3 -->|"Success"| V4
    V4 -->|"Private/Metadata"| Reject
    V4 -->|"Valid"| V5
    V5 --> V6
    V6 --> V7
    V7 --> V8
    V8 -->|"Yes"| V9
    V8 -->|"No"| Success
    V9 -->|"Invalid"| Reject
    V9 -->|"Valid"| V7
    
    style Success fill:#d4edda
    style Reject fill:#f8d7da
```

**Diagram: Complete SSRF Validation Pipeline**

**Sources:** [SKILL.md:382-391]()

---

## Private IP Range Reference

The following IP ranges must be blocked to prevent access to internal resources:

### IPv4 Private Ranges
| Range | CIDR | Description |
|-------|------|-------------|
| `10.0.0.0 - 10.255.255.255` | `10.0.0.0/8` | Private network (Class A) |
| `172.16.0.0 - 172.31.255.255` | `172.16.0.0/12` | Private network (Class B) |
| `192.168.0.0 - 192.168.255.255` | `192.168.0.0/16` | Private network (Class C) |
| `127.0.0.0 - 127.255.255.255` | `127.0.0.0/8` | Loopback addresses |
| `169.254.0.0 - 169.254.255.255` | `169.254.0.0/16` | Link-local/APIPA |
| `0.0.0.0 - 0.255.255.255` | `0.0.0.0/8` | Current network |

### IPv6 Private Ranges
| Range | CIDR | Description |
|-------|------|-------------|
| `::1` | `::1/128` | Loopback address |
| `fe80::` | `fe80::/10` | Link-local addresses |
| `fc00::` | `fc00::/7` | Unique local addresses |
| `::` | `::/128` | Unspecified address |

### Reserved/Special Ranges
| Range | CIDR | Description |
|-------|------|-------------|
| `224.0.0.0 - 239.255.255.255` | `224.0.0.0/4` | Multicast (Class D) |
| `240.0.0.0 - 255.255.255.255` | `240.0.0.0/4` | Reserved (Class E) |
| `255.255.255.255` | `255.255.255.255/32` | Broadcast address |

**Sources:** [SKILL.md:349-364](), [SKILL.md:382-391]()

---

## Integration with Defense in Depth

SSRF prevention should be implemented as part of a layered security approach:

1. **Input Validation Layer**: Allowlist validation at application entry point
2. **Network Layer**: Egress firewall rules, network segmentation
3. **DNS Layer**: DNS rebinding prevention, CNAME validation
4. **Request Layer**: IP validation, redirect control, timeout enforcement
5. **Monitoring Layer**: Log all URL fetch attempts, alert on suspicious patterns

For general input validation principles, see [Core Security Principles](#4). For complete vulnerability coverage, see [Complete Vulnerability Coverage](#11).

**Sources:** [SKILL.md:10-17](), [SKILL.md:323-391]()

---

# Page: SQL Injection Prevention

# SQL Injection Prevention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This page documents SQL injection prevention strategies as defined in the VibeSec-Skill knowledge base. SQL injection occurs when user-controlled input is incorporated into SQL queries without proper sanitization, allowing attackers to manipulate database operations. This page covers parameterized queries, ORM security, critical injection points, and defense-in-depth measures.

For other server-side vulnerabilities, see [SSRF Prevention](#7.1), [XXE Prevention](#7.3), [Path Traversal Prevention](#7.4), and [Insecure File Upload Prevention](#7.5). For input validation principles that apply across all vulnerabilities, see [Core Security Principles](#4).

**Sources:** [SKILL.md:457-499]()

---

## Vulnerability Overview

SQL injection exploits occur when user input is concatenated directly into SQL query strings. Attackers can inject malicious SQL fragments that alter query logic, bypass authentication, extract sensitive data, modify records, or execute administrative operations.

### Attack Vector Flow

```mermaid
graph TB
    UserInput["User Input<br/>(e.g., userId from request)"]
    AppCode["Application Code"]
    QueryConstruction["SQL Query Construction"]
    DatabaseExecution["Database Execution"]
    
    VulnPath["VULNERABLE PATH"]
    SecurePath["SECURE PATH"]
    
    UserInput --> AppCode
    
    AppCode -->|"String concatenation"| VulnConcat["query = 'SELECT * FROM users WHERE id = ' + userId"]
    VulnConcat --> MaliciousQuery["Attacker sends: ' OR '1'='1"]
    MaliciousQuery --> ExecutedVuln["Executed: SELECT * FROM users WHERE id = '' OR '1'='1'"]
    ExecutedVuln --> DataBreach["Returns all user records"]
    
    AppCode -->|"Parameterized query"| SecureParam["query = 'SELECT * FROM users WHERE id = ?'<br/>params = [userId]"]
    SecureParam --> ExecutedSecure["Database treats userId as literal value"]
    ExecutedSecure --> SafeResult["Returns only matching record or none"]
    
    VulnConcat -.->|"String becomes SQL code"| VulnPath
    SecureParam -.->|"Parameter treated as data"| SecurePath
    
    style UserInput fill:#f9f9f9,stroke:#333,stroke-width:2px
    style VulnConcat fill:#ffe1e1,stroke:#333,stroke-width:2px
    style MaliciousQuery fill:#ffe1e1,stroke:#333,stroke-width:2px
    style ExecutedVuln fill:#ffe1e1,stroke:#333,stroke-width:2px
    style DataBreach fill:#f8d7da,stroke:#333,stroke-width:3px
    style SecureParam fill:#e1f5ff,stroke:#333,stroke-width:2px
    style ExecutedSecure fill:#e1f5ff,stroke:#333,stroke-width:2px
    style SafeResult fill:#d4edda,stroke:#333,stroke-width:3px
```

**Sources:** [SKILL.md:457-471]()

---

## Primary Defense: Parameterized Queries

Parameterized queries (also called prepared statements) are the **PRIMARY DEFENSE** against SQL injection. They separate SQL code from data by using placeholders for user input, ensuring user-provided values are always treated as literal data, never executable code.

### Vulnerable vs. Secure Pattern

| Pattern | Example | Security Status |
|---------|---------|-----------------|
| **Vulnerable (Concatenation)** | `query = "SELECT * FROM users WHERE id = " + userId` | ❌ Allows injection |
| **Secure (Parameterized)** | `query = "SELECT * FROM users WHERE id = ?"` <br/> `execute(query, [userId])` | ✅ Safe - data separated from code |

**Sources:** [SKILL.md:463-471]()

### Language-Specific Implementation

While the SKILL.md file provides pseudocode examples, the principle applies across all database interfaces:

**Parameterized Query Pattern:**
```
query = "SELECT * FROM users WHERE id = ?"
execute(query, [userId])
```

The placeholder (`?`) or named parameter syntax varies by language/framework, but the core concept remains: never concatenate user input into SQL strings.

**Sources:** [SKILL.md:464-471]()

---

## ORM Usage and Cautions

Object-Relational Mappers (ORMs) typically parameterize queries automatically, providing built-in SQL injection protection when used correctly.

### ORM Security Considerations

```mermaid
graph TB
    ORMCall["ORM Method Call"]
    
    ORMCall --> SafeMethod["Safe ORM Methods<br/>(Auto-parameterized)"]
    ORMCall --> UnsafeMethod["Raw Query Methods<br/>(Manual parameterization required)"]
    
    SafeMethod --> Example1["User.find(id)"]
    SafeMethod --> Example2["User.where(email: email)"]
    SafeMethod --> Example3["User.update(id, data)"]
    
    UnsafeMethod --> RawQuery["User.raw('SELECT * FROM users WHERE id = ' + id)"]
    UnsafeMethod --> CustomSQL["db.execute(customQuery)"]
    
    Example1 --> AutoParam["Framework handles parameterization"]
    Example2 --> AutoParam
    Example3 --> AutoParam
    AutoParam --> Secure["Secure by default"]
    
    RawQuery --> Manual["Developer must parameterize"]
    CustomSQL --> Manual
    Manual --> Risk["Injection risk if not properly parameterized"]
    
    style SafeMethod fill:#e1f5ff,stroke:#333,stroke-width:2px
    style UnsafeMethod fill:#fff4e1,stroke:#333,stroke-width:2px
    style AutoParam fill:#d4edda,stroke:#333,stroke-width:2px
    style Manual fill:#ffe1e1,stroke:#333,stroke-width:2px
    style Secure fill:#d4edda,stroke:#333,stroke-width:3px
    style Risk fill:#f8d7da,stroke:#333,stroke-width:3px
```

### ORM Security Rules

1. **Use ORM methods that automatically parameterize** - Standard CRUD operations are safe
2. **Be cautious with raw query methods** - Methods like `.raw()`, `.execute()`, or similar require manual parameterization
3. **Watch for ORM-specific injection points** - Some ORMs have edge cases where injection is possible

**Sources:** [SKILL.md:473-476]()

---

## Input Validation as Defense-in-Depth

Input validation provides an additional security layer but is **NOT** a replacement for parameterized queries.

### Validation Strategy

| Validation Type | Purpose | Implementation |
|----------------|---------|----------------|
| **Data Type Validation** | Ensure integers are integers, not strings | Cast/parse with strict type checking |
| **Whitelist Allowed Values** | Limit to known-good values | Compare against predefined set |
| **Format Validation** | Verify expected patterns | Regex matching, length checks |

**Critical:** Input validation is defense-in-depth, not the primary defense. Always use parameterized queries regardless of validation.

**Sources:** [SKILL.md:478-481]()

---

## Critical Injection Points

SQL injection can occur at multiple points in query construction. Each requires specific attention:

### Injection Point Reference

```mermaid
graph TB
    SQLQuery["SQL Query Construction"]
    
    SQLQuery --> WhereClause["WHERE Clauses"]
    SQLQuery --> OrderByClause["ORDER BY Clauses"]
    SQLQuery --> LimitOffset["LIMIT/OFFSET Values"]
    SQLQuery --> TableColumn["Table and Column Names"]
    SQLQuery --> InsertValues["INSERT Values"]
    SQLQuery --> UpdateValues["UPDATE SET Values"]
    SQLQuery --> InClause["IN Clauses with Dynamic Lists"]
    SQLQuery --> LikePattern["LIKE Patterns"]
    
    WhereClause --> WhereSafe["Can use parameters: ?"]
    OrderByClause --> OrderByRisk["Cannot parameterize<br/>Must whitelist column names"]
    LimitOffset --> LimitSafe["Can use parameters: ?"]
    TableColumn --> TableRisk["Cannot parameterize<br/>Must whitelist identifiers"]
    InsertValues --> InsertSafe["Can use parameters: ?"]
    UpdateValues --> UpdateSafe["Can use parameters: ?"]
    InClause --> InSafe["Can use parameter arrays"]
    LikePattern --> LikeRisk["Can use parameters<br/>Must escape wildcards: % _"]
    
    WhereSafe --> Parameterized["Parameterized Protection"]
    LimitSafe --> Parameterized
    InsertSafe --> Parameterized
    UpdateSafe --> Parameterized
    InSafe --> Parameterized
    
    OrderByRisk --> Whitelist["Whitelist Protection Required"]
    TableRisk --> Whitelist
    
    LikeRisk --> Special["Special Handling:<br/>Parameterize + Escape Wildcards"]
    
    style WhereClause fill:#e1f5ff,stroke:#333,stroke-width:2px
    style LimitOffset fill:#e1f5ff,stroke:#333,stroke-width:2px
    style InsertValues fill:#e1f5ff,stroke:#333,stroke-width:2px
    style UpdateValues fill:#e1f5ff,stroke:#333,stroke-width:2px
    style InClause fill:#e1f5ff,stroke:#333,stroke-width:2px
    style OrderByClause fill:#ffe1e1,stroke:#333,stroke-width:2px
    style TableColumn fill:#ffe1e1,stroke:#333,stroke-width:2px
    style LikePattern fill:#fff4e1,stroke:#333,stroke-width:2px
    style Parameterized fill:#d4edda,stroke:#333,stroke-width:2px
    style Whitelist fill:#fff4e1,stroke:#333,stroke-width:2px
    style Special fill:#fff4e1,stroke:#333,stroke-width:2px
```

### Detailed Injection Points

| Injection Point | Can Parameterize? | Security Measure | Notes |
|-----------------|-------------------|------------------|-------|
| **WHERE clauses** | ✅ Yes | Use `?` placeholders | Standard parameterization applies |
| **ORDER BY clauses** | ❌ No | Whitelist column names | Often overlooked - parameters don't work for identifiers |
| **LIMIT/OFFSET values** | ✅ Yes | Use `?` placeholders | Treat as numeric parameters |
| **Table and column names** | ❌ No | Whitelist identifiers | Cannot parameterize SQL identifiers |
| **INSERT values** | ✅ Yes | Use `?` placeholders | Standard parameterization applies |
| **UPDATE SET values** | ✅ Yes | Use `?` placeholders | Standard parameterization applies |
| **IN clauses with dynamic lists** | ✅ Yes | Parameter arrays | Use array/list parameter binding |
| **LIKE patterns** | ⚠️ Partial | Parameterize + escape wildcards | Escape `%` and `_` characters in user input |

**Sources:** [SKILL.md:484-492]()

### ORDER BY and Table Name Handling

**Critical:** `ORDER BY` clauses and table/column names cannot be parameterized. These must use whitelisting:

```
# Whitelist approach for ORDER BY
allowed_columns = ['name', 'email', 'created_at']
if sort_column not in allowed_columns:
    return error
    
query = f"SELECT * FROM users ORDER BY {sort_column}"  # Safe because whitelisted
```

**Sources:** [SKILL.md:486-488]()

### LIKE Pattern Special Handling

`LIKE` patterns require both parameterization and wildcard escaping:

```
# User input: "test_value"
# Without escaping, _ matches any character
# Must escape: "test\_value"
escaped_input = input.replace('%', '\\%').replace('_', '\\_')
query = "SELECT * FROM users WHERE name LIKE ?"
execute(query, [escaped_input + '%'])
```

**Sources:** [SKILL.md:492]()

---

## Additional Defense Layers

Beyond parameterized queries, implement these defense-in-depth measures:

### Database-Level Protections

| Protection | Purpose | Implementation |
|-----------|---------|----------------|
| **Least Privilege** | Limit damage from successful injection | Database user should have minimum required permissions (SELECT, INSERT, UPDATE only - no DROP, ALTER, GRANT) |
| **Disable Dangerous Functions** | Prevent command execution | Disable `xp_cmdshell` (SQL Server), `sys_exec()`, `LOAD_FILE()`, and similar functions |
| **Error Handling** | Prevent information disclosure | Never expose SQL error messages to users; log errors server-side only |

**Sources:** [SKILL.md:495-498]()

### Database Permission Model

```mermaid
graph TB
    DBUser["Database User for Application"]
    
    DBUser --> AllowedPerms["Allowed Permissions"]
    DBUser --> DeniedPerms["Denied Permissions"]
    
    AllowedPerms --> SELECT["SELECT (read data)"]
    AllowedPerms --> INSERT["INSERT (create records)"]
    AllowedPerms --> UPDATE["UPDATE (modify records)"]
    AllowedPerms --> DELETE["DELETE (remove records)<br/>(if needed)"]
    
    DeniedPerms --> DROP["DROP (delete tables)"]
    DeniedPerms --> ALTER["ALTER (modify schema)"]
    DeniedPerms --> GRANT["GRANT (change permissions)"]
    DeniedPerms --> EXEC["EXECUTE system commands<br/>(xp_cmdshell, etc.)"]
    DeniedPerms --> LOAD["LOAD_FILE / OUTFILE"]
    
    AllowedPerms --> LimitDamage["Limits damage if injection occurs"]
    DeniedPerms --> BlockEscalation["Prevents privilege escalation<br/>and data exfiltration"]
    
    style AllowedPerms fill:#e1f5ff,stroke:#333,stroke-width:2px
    style DeniedPerms fill:#ffe1e1,stroke:#333,stroke-width:2px
    style LimitDamage fill:#d4edda,stroke:#333,stroke-width:2px
    style BlockEscalation fill:#d4edda,stroke:#333,stroke-width:2px
```

**Sources:** [SKILL.md:496-498]()

### Error Handling Requirements

**Never expose SQL errors to users:**
- Log detailed error messages server-side for debugging
- Return generic error messages to clients (e.g., "An error occurred")
- Prevents attackers from learning database structure through error messages

**Sources:** [SKILL.md:498]()

---

## Implementation Checklist

Use this checklist when implementing database operations:

- [ ] **All queries use parameterized queries or safe ORM methods**
- [ ] **No string concatenation of user input into SQL**
- [ ] **ORDER BY clauses use whitelisted column names**
- [ ] **Table/column names are whitelisted when dynamic**
- [ ] **LIKE patterns escape `%` and `_` wildcards**
- [ ] **IN clause arrays use parameter binding**
- [ ] **Database user has least-privilege permissions**
- [ ] **Dangerous functions (xp_cmdshell, etc.) are disabled**
- [ ] **SQL errors are not exposed to users**
- [ ] **Input is validated for expected data types**
- [ ] **Raw SQL methods in ORMs are avoided or carefully parameterized**

**Sources:** [SKILL.md:457-499]()

---

## Relationship to Core Principles

SQL injection prevention aligns with multiple core security principles documented in [Core Security Principles](#4):

| Core Principle | SQL Injection Application |
|----------------|--------------------------|
| **Defense in Depth** | Parameterized queries (primary) + input validation (secondary) + least privilege (tertiary) |
| **Fail Securely** | Return generic errors instead of SQL error details; deny access on validation failure |
| **Least Privilege** | Database user permissions limited to required operations only |
| **Input Validation** | Validate data types and formats even when using parameterized queries |

**Sources:** [SKILL.md:10-17](), [SKILL.md:478-498]()

---

# Page: XML External Entity (XXE) Prevention

# XML External Entity (XXE) Prevention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document details prevention strategies for XML External Entity (XXE) vulnerabilities in server-side code. XXE attacks exploit XML parsers that process external entity references in user-supplied XML documents, potentially leading to file disclosure, server-side request forgery, or denial of service.

This page covers parser configuration, vulnerable scenarios, and language-specific prevention code. For general server-side security principles, see [Server-Side Security](#7). For file upload security considerations that may involve XML-based formats, see [Insecure File Upload Prevention](#7.5).

**Sources:** [SKILL.md:502-569]()

---

## Understanding XXE Vulnerabilities

XML External Entity vulnerabilities occur when XML parsers process external entity references in user-supplied XML without proper restrictions. Attackers can exploit this to:

- **Read local files** via `file://` URIs
- **Perform SSRF attacks** via `http://` URIs to internal services
- **Cause denial of service** through entity expansion bombs
- **Exfiltrate data** to attacker-controlled servers

The vulnerability exists when parsers allow DTD (Document Type Definition) processing and external entity resolution by default.

**Sources:** [SKILL.md:502-505]()

---

## Attack Surface: Vulnerable Scenarios

### Direct XML Input

Applications that directly accept XML from users are primary targets:

| Scenario | Description | Risk Level |
|----------|-------------|------------|
| **SOAP APIs** | XML-based web service requests | High |
| **XML-RPC** | Remote procedure calls using XML | High |
| **XML file uploads** | User-uploaded XML configuration or data files | High |
| **Configuration file parsing** | Application settings in XML format | Medium |
| **RSS/Atom feed processing** | Parsing external feed sources | Medium |

**Sources:** [SKILL.md:506-514]()

### Indirect XML Vectors

Many file formats internally use XML, creating hidden attack surfaces:

| Format | Internal Structure | Common Use Cases |
|--------|-------------------|------------------|
| **Office Documents** | DOCX, XLSX, PPTX are ZIP archives containing XML | Document uploads, report generation |
| **SVG Files** | XML-based vector graphics | Image uploads, user avatars |
| **SAML Assertions** | XML authentication tokens | Single sign-on implementations |
| **PDF with XFA Forms** | XML Forms Architecture embedded in PDFs | Form processing |
| **Server-side conversions** | JSON/other formats converted to XML internally | API translation layers |

**Sources:** [SKILL.md:515-521]()

---

## XXE Attack Flow

```mermaid
graph TB
    Attacker["Attacker"]
    
    subgraph "Attack Payload"
        Payload["Malicious XML Document"]
        DTD["<!DOCTYPE foo [<br/><!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"]
        Reference["<data>&xxe;</data>"]
    end
    
    subgraph "Server Processing"
        Parser["XML Parser"]
        EntityResolver["External Entity<br/>Resolver"]
        FileSystem["File System<br/>Access"]
        Network["Network Request<br/>Handler"]
    end
    
    subgraph "Attack Outcomes"
        FileDisclosure["File Disclosure<br/>/etc/passwd contents"]
        SSRF["SSRF Attack<br/>http://internal-service"]
        DoS["Denial of Service<br/>Entity expansion bomb"]
    end
    
    Attacker -->|"Submit"| Payload
    Payload --> DTD
    Payload --> Reference
    DTD --> Parser
    Reference --> Parser
    
    Parser -->|"DTD enabled"| EntityResolver
    EntityResolver -->|"file://"| FileSystem
    EntityResolver -->|"http://"| Network
    
    FileSystem --> FileDisclosure
    Network --> SSRF
    Parser -->|"Recursive entities"| DoS
    
    style Payload fill:#ffe1e1
    style DTD fill:#ffe1e1
    style EntityResolver fill:#fff4e1
    style FileDisclosure fill:#f8d7da
    style SSRF fill:#f8d7da
    style DoS fill:#f8d7da
```

**XXE Attack Flow Diagram**: Demonstrates how malicious XML documents exploit entity resolution to access files, make network requests, or cause denial of service through the XML parser's entity processing mechanism.

**Sources:** [SKILL.md:502-521]()

---

## Prevention Strategies by Language and Parser

### Java: DocumentBuilderFactory Configuration

The `DocumentBuilderFactory` class requires explicit feature disabling to prevent XXE:

```mermaid
graph LR
    subgraph "Java XXE Prevention"
        DBF["DocumentBuilderFactory.newInstance()"]
        
        Feature1["setFeature<br/>disallow-doctype-decl<br/>= true"]
        Feature2["setFeature<br/>external-general-entities<br/>= false"]
        Feature3["setFeature<br/>external-parameter-entities<br/>= false"]
        Method["setExpandEntityReferences<br/>false"]
        
        SecureParser["Secure XML Parser"]
    end
    
    DBF --> Feature1
    DBF --> Feature2
    DBF --> Feature3
    DBF --> Method
    
    Feature1 --> SecureParser
    Feature2 --> SecureParser
    Feature3 --> SecureParser
    Method --> SecureParser
    
    style DBF fill:#e1f5ff
    style SecureParser fill:#d4edda
```

**Java Parser Hardening**: Configuration chain for `DocumentBuilderFactory` to disable DTD processing and external entity resolution.

**Configuration Details:**

| Feature/Method | Purpose | Required |
|----------------|---------|----------|
| `http://apache.org/xml/features/disallow-doctype-decl` | Completely disables DTD processing | Recommended |
| `http://xml.org/sax/features/external-general-entities` | Disables external general entities | Yes |
| `http://xml.org/sax/features/external-parameter-entities` | Disables external parameter entities | Yes |
| `setExpandEntityReferences(false)` | Prevents entity expansion | Yes |

**Sources:** [SKILL.md:525-532]()

---

### Python: lxml and defusedxml

Python's `lxml` library provides parser-level controls:

```mermaid
graph TB
    subgraph "Python XXE Prevention Approaches"
        direction TB
        
        Approach1["lxml.etree.XMLParser"]
        Config1["resolve_entities=False"]
        Config2["no_network=True"]
        
        Approach2["defusedxml library"]
        Safe["Secure by default"]
        
        Result["Protected Parser"]
    end
    
    Approach1 --> Config1
    Approach1 --> Config2
    Config1 --> Result
    Config2 --> Result
    
    Approach2 --> Safe
    Safe --> Result
    
    style Approach1 fill:#e1f5ff
    style Approach2 fill:#e1f5ff
    style Result fill:#d4edda
```

**Python Parser Options**: Two approaches for XXE prevention—explicit `lxml` parser configuration or the purpose-built `defusedxml` library.

**Implementation Pattern:**

| Library | Configuration | Security Level |
|---------|---------------|----------------|
| **lxml** | `XMLParser(resolve_entities=False, no_network=True)` | High (if configured) |
| **defusedxml** | Drop-in replacement for stdlib XML modules | High (default) |

**Sources:** [SKILL.md:534-539]()

---

### PHP: libxml_disable_entity_loader

PHP requires runtime configuration before XML parsing:

```mermaid
graph LR
    subgraph "PHP XXE Prevention"
        Before["Application Start"]
        LibXML["libxml_disable_entity_loader(true)"]
        
        subgraph "Parser Options"
            SimpleXML["SimpleXML"]
            DOMDocument["DOMDocument"]
            XMLReader["XMLReader"]
        end
        
        Protected["Entity Loading<br/>Disabled Globally"]
    end
    
    Before --> LibXML
    LibXML --> Protected
    
    Protected --> SimpleXML
    Protected --> DOMDocument
    Protected --> XMLReader
    
    style LibXML fill:#e1f5ff
    style Protected fill:#d4edda
```

**PHP Global Protection**: The `libxml_disable_entity_loader()` function provides application-wide protection for all libxml-based parsers.

**Sources:** [SKILL.md:541-545]()

---

### Node.js: Library Selection and Configuration

Node.js XML parsing requires careful library selection:

```mermaid
graph TB
    subgraph "Node.js XXE Prevention Strategy"
        LibSelection["Library Selection"]
        
        Safe["Libraries with safe defaults<br/>xml2js, fast-xml-parser"]
        Unsafe["libxmljs (requires configuration)"]
        
        Config["Configuration if using libxmljs:<br/>noent: false<br/>dtdload: false"]
        
        Result["Protected Parsing"]
    end
    
    LibSelection --> Safe
    LibSelection --> Unsafe
    
    Safe --> Result
    Unsafe --> Config
    Config --> Result
    
    style Safe fill:#d4edda
    style Unsafe fill:#fff4e1
    style Config fill:#e1f5ff
    style Result fill:#d4edda
```

**Node.js Parser Security**: Strategy prioritizes libraries with secure defaults, with explicit configuration required for `libxmljs`.

**Library Comparison:**

| Library | Default Security | Configuration Needed |
|---------|-----------------|---------------------|
| `xml2js` | Secure | None |
| `fast-xml-parser` | Secure | None |
| `libxmljs` | Unsafe | `{ noent: false, dtdload: false }` |

**Sources:** [SKILL.md:547-551]()

---

### .NET: XmlReaderSettings

.NET's `XmlReader` requires explicit settings configuration:

```mermaid
graph LR
    subgraph ".NET XXE Prevention"
        Settings["XmlReaderSettings"]
        
        DTD["DtdProcessing.Prohibit"]
        Resolver["XmlResolver = null"]
        
        Reader["XmlReader.Create()"]
        
        Secure["Secure XML Processing"]
    end
    
    Settings --> DTD
    Settings --> Resolver
    
    DTD --> Reader
    Resolver --> Reader
    
    Reader --> Secure
    
    style Settings fill:#e1f5ff
    style DTD fill:#fff4e1
    style Resolver fill:#fff4e1
    style Secure fill:#d4edda
```

**.NET Configuration Pattern**: Two-step hardening through DTD processing prohibition and null resolver assignment.

**Configuration Properties:**

| Property | Value | Purpose |
|----------|-------|---------|
| `DtdProcessing` | `DtdProcessing.Prohibit` | Completely disables DTD processing |
| `XmlResolver` | `null` | Prevents external resource resolution |

**Sources:** [SKILL.md:553-558]()

---

## Language-Specific Prevention Reference

### Complete Configuration Matrix

| Language/Framework | Parser Class/Function | Critical Configuration | Code Reference |
|-------------------|----------------------|----------------------|----------------|
| **Java** | `DocumentBuilderFactory` | `setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)` | [SKILL.md:526-532]() |
| **Python** | `lxml.etree.XMLParser` | `resolve_entities=False, no_network=True` | [SKILL.md:535-539]() |
| **PHP** | `libxml_disable_entity_loader()` | `libxml_disable_entity_loader(true)` | [SKILL.md:542-545]() |
| **Node.js** | `libxmljs` | `{ noent: false, dtdload: false }` | [SKILL.md:548-551]() |
| **.NET** | `XmlReaderSettings` | `DtdProcessing = DtdProcessing.Prohibit` | [SKILL.md:554-558]() |

**Sources:** [SKILL.md:523-559]()

---

## Indirect XXE Attack Surfaces

File upload functionality creates multiple XXE vectors through format conversions:

```mermaid
graph TB
    subgraph "File Upload XXE Risk Surface"
        Upload["File Upload Endpoint"]
        
        subgraph "Office Documents"
            DOCX["DOCX Upload<br/>(ZIP + XML)"]
            XLSX["XLSX Upload<br/>(ZIP + XML)"]
            PPTX["PPTX Upload<br/>(ZIP + XML)"]
        end
        
        subgraph "Vector Graphics"
            SVG["SVG Upload<br/>(XML-based)"]
        end
        
        subgraph "Other Formats"
            PDF["PDF with XFA<br/>(embedded XML)"]
            SAML["SAML Assertion<br/>(authentication XML)"]
        end
        
        Parser["XML Parser<br/>(backend processing)"]
        
        Upload --> DOCX
        Upload --> XLSX
        Upload --> PPTX
        Upload --> SVG
        Upload --> PDF
        Upload --> SAML
        
        DOCX --> Parser
        XLSX --> Parser
        PPTX --> Parser
        SVG --> Parser
        PDF --> Parser
        SAML --> Parser
        
        Parser -->|"If misconfigured"| XXE["XXE Vulnerability"]
    end
    
    style Upload fill:#e1f5ff
    style Parser fill:#fff4e1
    style XXE fill:#f8d7da
```

**Indirect XXE Vectors**: Common file formats that internally use XML, creating hidden attack surfaces during server-side processing.

**Sources:** [SKILL.md:515-521](), [SKILL.md:427]()

---

## XXE Prevention Checklist

Implementation verification steps for secure XML processing:

### Parser Configuration

- [ ] **DTD processing disabled** entirely if not required for application functionality
- [ ] **External entity resolution disabled** for both general and parameter entities
- [ ] **External DTD loading disabled** to prevent remote schema exploitation
- [ ] **XInclude processing disabled** to prevent XML inclusion attacks
- [ ] **XML parser library updated** to latest patched version

### Development Practices

- [ ] **Validate/sanitize XML** before parsing if DTD functionality is required
- [ ] **Consider JSON alternatives** for new API development to avoid XML complexity
- [ ] **Test with attack payloads** including file disclosure and SSRF attempts
- [ ] **Review all XML processing points** including indirect vectors (file uploads, format conversions)

### Defense in Depth

- [ ] **Network segmentation** limits impact of SSRF if XXE bypass occurs
- [ ] **File system permissions** restrict readable files from application user
- [ ] **Logging and monitoring** detects external entity resolution attempts
- [ ] **Input validation** rejects documents with DTD declarations at application layer

**Sources:** [SKILL.md:560-568]()

---

## Implementation Verification

### Testing Strategy

| Test Type | Payload Example | Expected Behavior |
|-----------|----------------|-------------------|
| **File Disclosure** | `<!ENTITY xxe SYSTEM "file:///etc/passwd">` | Parsing fails or entity not resolved |
| **SSRF Attempt** | `<!ENTITY xxe SYSTEM "http://internal-service">` | No network request initiated |
| **Entity Expansion** | Recursive entity definitions (billion laughs) | Parsing fails with resource limit |
| **DTD Declaration** | Any document with `<!DOCTYPE>` | Rejected if DTD disabled |

### Common Misconfiguration Patterns

| Vulnerability Pattern | Unsafe Code | Secure Alternative |
|----------------------|-------------|-------------------|
| **Default settings** | `DocumentBuilderFactory.newInstance()` without configuration | Explicitly disable features per [SKILL.md:526-532]() |
| **Partial hardening** | Only disabling external entities, leaving DTD enabled | Disable DTD entirely with `disallow-doctype-decl` |
| **Parser version** | Using outdated XML libraries with known XXE issues | Update to patched versions |
| **Inconsistent protection** | Hardening one parser while another remains vulnerable | Apply configuration to all XML parsing instances |

**Sources:** [SKILL.md:560-568]()

---

## Integration with File Upload Security

XXE prevention intersects with file upload security for XML-based formats:

| Format | XXE Risk | Prevention Strategy | Cross-Reference |
|--------|----------|-------------------|-----------------|
| **Office Documents** | High - ZIP archives contain XML files | Apply XXE prevention to document processors | [SKILL.md:427](), [#7.5](#7.5) |
| **SVG Files** | High - Pure XML with script capabilities | Sanitize SVG or disable SVG uploads entirely | [SKILL.md:426](), [#7.5](#7.5) |
| **PDF/XFA** | Medium - XFA forms embed XML | Configure PDF libraries to disable XFA or apply XXE hardening | [SKILL.md:520]() |

**Sources:** [SKILL.md:427](), [SKILL.md:515-521]()

---

## Related Security Concerns

XXE vulnerabilities often co-occur with or enable other attack types:

- **SSRF attacks**: XXE can trigger server-side requests to internal resources - see [SSRF Prevention](#7.1)
- **File upload exploitation**: Office documents and SVG files create XXE vectors - see [Insecure File Upload Prevention](#7.5)
- **Polyglot file attacks**: Files valid as both XML and other formats bypass validation - see [SKILL.md:409]()
- **DNS rebinding**: External entity resolution can be combined with DNS rebinding for SSRF - see [SKILL.md:366-371]()

**Sources:** [SKILL.md:502-521](), [SKILL.md:323-391](), [SKILL.md:427]()

---

# Page: Path Traversal Prevention

# Path Traversal Prevention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document covers path traversal vulnerability prevention in web applications. Path traversal attacks occur when user-controlled input influences file path operations, allowing attackers to access files outside intended directories. This includes reading arbitrary files, accessing configuration files, or manipulating file operations to compromise system integrity.

For related file security concerns, see [Insecure File Upload Prevention](#7.5). For input validation principles that apply broadly, see [Core Security Principles](#4).

**Sources:** [SKILL.md:572-627]()

---

## Vulnerability Mechanism

Path traversal vulnerabilities arise when applications construct file paths using unsanitized user input. Attackers exploit this by injecting directory traversal sequences (`../`, `..\`, or encoded variants) to navigate outside the intended directory structure.

### Common Vulnerable Patterns

The following code patterns expose path traversal vulnerabilities:

| Pattern | Vulnerability | Attack Example |
|---------|---------------|----------------|
| Direct concatenation | `"/uploads/" + user_input` | Input: `../../../etc/passwd` |
| Base directory joining | `base_dir + request.params['file']` | Input: `../../config/secrets.json` |
| Template path construction | `"templates/" + user_provided_template` | Input: `../../../app/database.yml` |

**Sources:** [SKILL.md:576-583]()

---

## Attack Flow Diagram

```mermaid
graph TB
    subgraph "Vulnerable Application Flow"
        A1["User Request"] -->|"filename=../../../etc/passwd"| B1["Application Code"]
        B1 -->|"file_path = '/uploads/' + user_input"| C1["Path Construction"]
        C1 -->|"/uploads/../../../etc/passwd"| D1["File System Access"]
        D1 -->|"Resolves to: /etc/passwd"| E1["Unauthorized File Read"]
    end
    
    subgraph "Secure Application Flow"
        A2["User Request"] -->|"file_id=report_q1"| B2["Application Code"]
        B2 -->|"files.get(user_input)"| C2["Indirect Reference Lookup"]
        C2 -->|"Returns: /reports/q1.pdf or None"| D2["Path Validation"]
        D2 -->|"Valid path within base"| E2["Authorized File Access"]
        D2 -->|"Invalid/Missing ID"| F2["Return 404/Error"]
    end
    
    style E1 fill:#fee,stroke:#333,stroke-width:2px
    style E2 fill:#efe,stroke:#333,stroke-width:2px
    style F2 fill:#ffe,stroke:#333,stroke-width:2px
```

**Sources:** [SKILL.md:572-627]()

---

## Prevention Strategy 1: Indirect References

The most secure approach eliminates user input from file paths entirely by using indirect references.

### Implementation Pattern

```python
# Mapping approach - user input never touches file system paths
files = {
    'report': '/reports/q1.pdf', 
    'invoice': '/invoices/2024.pdf',
    'statement': '/statements/march.pdf'
}

# User provides key, not path
file_path = files.get(user_input)

if file_path is None:
    return 404  # Invalid reference
```

### Benefits

| Aspect | Advantage |
|--------|-----------|
| Security | User input never directly controls file paths |
| Simplicity | No complex validation logic required |
| Maintainability | Centralized file path management |
| Performance | O(1) lookup with no parsing overhead |

**Sources:** [SKILL.md:587-593]()

---

## Prevention Strategy 2: Canonicalization and Validation

When user input must influence file paths (e.g., user-uploaded files with preserved names), canonicalization ensures the resolved path remains within allowed boundaries.

### Canonicalization Process Diagram

```mermaid
graph LR
    A["User Input:<br/>../../etc/passwd"] --> B["os.path.join()"]
    C["Base Directory:<br/>/var/app/uploads"] --> B
    B --> D["Combined Path:<br/>/var/app/uploads/../../etc/passwd"]
    D --> E["os.path.realpath()"]
    E --> F["Resolved Path:<br/>/etc/passwd"]
    F --> G["os.path.commonpath()"]
    H["Base Canonical:<br/>/var/app/uploads"] --> G
    G --> I{"Common path<br/>== base?"}
    I -->|"No"| J["Reject: ValueError"]
    I -->|"Yes"| K["Accept: Within bounds"]
    
    style J fill:#fee,stroke:#333,stroke-width:2px
    style K fill:#efe,stroke:#333,stroke-width:2px
```

**Sources:** [SKILL.md:595-612]()

### safe_join Function Implementation

The following pattern demonstrates proper canonicalization and validation:

```python
import os

def safe_join(base_directory, user_path):
    # Ensure base is absolute and normalized
    base = os.path.abspath(os.path.realpath(base_directory))
    
    # Join and then resolve the result
    target = os.path.abspath(os.path.realpath(os.path.join(base, user_path)))
    
    # Ensure the commonpath is the base directory
    if os.path.commonpath([base, target]) != base:
        raise ValueError("Error!")
    
    return target
```

### Function Breakdown

| Step | Function | Purpose |
|------|----------|---------|
| 1 | `os.path.abspath()` | Convert to absolute path |
| 2 | `os.path.realpath()` | Resolve symbolic links and `.` / `..` sequences |
| 3 | `os.path.join()` | Combine base and user paths |
| 4 | `os.path.commonpath()` | Verify resolved path shares base as prefix |
| 5 | Comparison check | Reject if resolved path escapes base |

**Sources:** [SKILL.md:595-612]()

---

## Prevention Strategy 3: Input Sanitization

Input sanitization should be used as defense-in-depth, never as the primary control.

### Sanitization Rules

| Element | Action | Rationale |
|---------|--------|-----------|
| `..` sequences | Remove or reject | Directory traversal primitive |
| Absolute path indicators (`/`, `C:`) | Remove or reject | Bypass base directory entirely |
| Non-alphanumeric characters | Whitelist allowed set | Prevent encoding bypasses |
| File extension | Validate against allowlist | Restrict file types |

### Sanitization Limitations

Sanitization alone is insufficient because:

- **Encoding bypasses**: `..%2F`, `..%252F` (double encoding), URL-encoded variations
- **Unicode normalization**: `..%c0%af` can decode to `../`
- **Case variations**: Windows systems may treat `..` and `..` identically
- **Null byte injection**: `../../../etc/passwd%00.txt` may truncate validation
- **OS-specific behavior**: Different path separators (`/` vs `\`)

**Always combine sanitization with canonicalization validation.**

**Sources:** [SKILL.md:614-619]()

---

## Implementation Decision Tree

```mermaid
graph TD
    A["Need to handle user file access"] --> B{"Can use<br/>indirect references?"}
    B -->|"Yes"| C["Use mapping approach"]
    C --> D["files.get(user_id)"]
    
    B -->|"No"| E{"User controls<br/>full filename?"}
    E -->|"Yes"| F["Implement safe_join"]
    F --> G["Canonicalize and validate"]
    
    E -->|"Partial control"| H["Define constraints"]
    H --> I["Whitelist extensions"]
    I --> G
    
    G --> J["Add sanitization<br/>(defense-in-depth)"]
    J --> K["Remove dangerous chars"]
    K --> L["Validate extension"]
    
    D --> M["Return file or None"]
    L --> M
    
    M --> N{"Valid file?"}
    N -->|"No"| O["Return 404"]
    N -->|"Yes"| P["Serve file"]
    
    style C fill:#efe,stroke:#333,stroke-width:2px
    style F fill:#ffa,stroke:#333,stroke-width:2px
    style O fill:#fee,stroke:#333,stroke-width:2px
    style P fill:#efe,stroke:#333,stroke-width:2px
```

**Sources:** [SKILL.md:572-627]()

---

## Common Bypass Techniques

Understanding bypass techniques ensures comprehensive protection:

| Technique | Example | Mitigation |
|-----------|---------|------------|
| URL encoding | `..%2F..%2Fetc%2Fpasswd` | Decode before validation |
| Double encoding | `..%252F..%252Fetc` | Multiple decode passes or reject encoded input |
| Unicode encoding | `..%c0%af..%c0%af` | Normalize Unicode before validation |
| Null byte injection | `../../../etc/passwd%00.txt` | Reject null bytes (`\x00`) |
| Backslash on Windows | `..\..\..\windows\system32` | Normalize path separators |
| Overlong UTF-8 | `%e0%80%ae%e0%80%ae%e0%80%af` | UTF-8 validation |
| Case variation | `..\\..\\..\\` | Case normalization on case-insensitive systems |
| Absolute paths | `/etc/passwd`, `C:\Windows\` | Reject absolute path indicators |
| Mixed separators | `..\/..\/etc/passwd` | Normalize separators before validation |

**Sources:** [SKILL.md:614-619]()

---

## Verification Checklist

Use this checklist to verify path traversal protection in code:

### Pre-Deployment Checklist

- [ ] User input never directly concatenated into file paths
- [ ] Paths canonicalized using `os.path.realpath()` or equivalent
- [ ] Resolved paths validated against base directory using `os.path.commonpath()`
- [ ] File extensions restricted to allowlist (if applicable)
- [ ] Input sanitized to remove `..`, absolute paths, and dangerous characters
- [ ] Symbolic link resolution handled (prevents symlink bypass)
- [ ] Error messages don't reveal file system structure
- [ ] File access operations use least privilege (limited OS user permissions)

### Testing Checklist

- [ ] Test with `../` sequences
- [ ] Test with `..%2F` URL-encoded sequences
- [ ] Test with absolute paths (`/etc/passwd`)
- [ ] Test with null bytes (`%00`)
- [ ] Test with mixed path separators (`../\../`)
- [ ] Test with Unicode/encoding bypasses
- [ ] Test with symbolic links (if OS supports)
- [ ] Test with overly long paths
- [ ] Verify error responses don't leak information

**Sources:** [SKILL.md:621-627]()

---

## Code Entity Reference Map

```mermaid
graph TB
    subgraph "Prevention Functions"
        SJ["safe_join(base_directory, user_path)"]
        ABS["os.path.abspath()"]
        REAL["os.path.realpath()"]
        JOIN["os.path.join()"]
        COMMON["os.path.commonpath()"]
    end
    
    subgraph "Validation Steps"
        V1["Step 1: Canonicalize base"]
        V2["Step 2: Join paths"]
        V3["Step 3: Canonicalize target"]
        V4["Step 4: Verify commonpath"]
    end
    
    subgraph "Decision Points"
        D1{"target within base?"}
        D2{"file exists?"}
        D3{"permissions OK?"}
    end
    
    SJ --> V1
    V1 --> ABS
    V1 --> REAL
    V1 --> V2
    V2 --> JOIN
    V2 --> V3
    V3 --> ABS
    V3 --> REAL
    V3 --> V4
    V4 --> COMMON
    V4 --> D1
    
    D1 -->|"No"| E1["raise ValueError"]
    D1 -->|"Yes"| D2
    D2 -->|"No"| E2["return 404"]
    D2 -->|"Yes"| D3
    D3 -->|"No"| E3["return 403"]
    D3 -->|"Yes"| SUCCESS["return file"]
    
    style E1 fill:#fee,stroke:#333,stroke-width:2px
    style E2 fill:#fee,stroke:#333,stroke-width:2px
    style E3 fill:#fee,stroke:#333,stroke-width:2px
    style SUCCESS fill:#efe,stroke:#333,stroke-width:2px
```

**Sources:** [SKILL.md:595-612]()

---

## Integration with Other Security Controls

Path traversal prevention should integrate with broader security measures:

| Security Layer | Integration Point | Purpose |
|----------------|-------------------|---------|
| Access Control | Verify resource ownership before file access | Prevent IDOR (see [Access Control & Authorization](#5)) |
| Input Validation | Validate all parameters before path operations | Defense in depth (see [Core Security Principles](#4)) |
| File Upload Security | Validate uploaded file paths | Prevent ZIP slip (see [Insecure File Upload Prevention](#7.5)) |
| Error Handling | Return generic errors (404) for invalid paths | Prevent information disclosure |
| Least Privilege | Run file access with minimal OS permissions | Limit blast radius of successful attacks |
| Logging | Log path validation failures | Detect attack attempts |

**Sources:** [SKILL.md:10-17](), [SKILL.md:572-627]()

---

## Platform-Specific Considerations

Different platforms require specific adaptations:

### Python
- Use `os.path.realpath()` to resolve symlinks
- Use `os.path.commonpath()` for boundary validation
- Consider `pathlib.Path.resolve()` for modern code

### Node.js
- Use `path.resolve()` to canonicalize
- Use `path.relative()` to check if result contains `..`
- Beware of `path.join()` alone (doesn't canonicalize)

### Java
- Use `File.getCanonicalPath()` for resolution
- Use `Path.normalize()` and `Path.toRealPath()`
- Check `startsWith()` on canonical paths

### PHP
- Use `realpath()` for canonicalization
- Verify result with `strpos()` against base directory
- Handle `false` return from `realpath()` (file doesn't exist)

### .NET
- Use `Path.GetFullPath()` for normalization
- Use `Path.GetFullPath()` result with `StartsWith()` check
- Consider `Uri` class for additional validation

**Sources:** [SKILL.md:595-612]()

---

# Page: Insecure File Upload Prevention

# Insecure File Upload Prevention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This page documents secure file upload implementation patterns that prevent exploitation through malicious file uploads. File upload functionality represents a critical attack vector where user-controlled files can introduce server-side code execution, cross-site scripting, XXE attacks, path traversal, and content-type confusion attacks.

This page covers server-side file validation, magic byte verification, bypass technique prevention, and secure storage patterns. For client-side XSS prevention through SVG uploads, see [Cross-Site Scripting (XSS) Prevention](#6.1). For XXE vulnerabilities in document uploads (DOCX, XLSX), see [XML External Entity (XXE) Prevention](#7.3). For path traversal in file extraction, see [Path Traversal Prevention](#7.4).

**Sources:** [SKILL.md:394-454]()

---

## File Upload Attack Surface

The following diagram illustrates the multi-layered attack surface presented by file upload functionality:

```mermaid
graph TB
    subgraph "Attack Vectors"
        A1["User Upload Request"]
        A2["Filename Manipulation"]
        A3["MIME Type Spoofing"]
        A4["Magic Byte Injection"]
        A5["Polyglot File Creation"]
        A6["Content Embedding"]
    end
    
    subgraph "Validation Layers"
        V1["Extension Validation<br/>(Allowlist Check)"]
        V2["Magic Byte Verification<br/>(File Signature)"]
        V3["Content Structure Validation<br/>(Parse Integrity)"]
        V4["Size Limit Enforcement"]
    end
    
    subgraph "Storage and Serving"
        S1["Filename Sanitization<br/>(UUID Generation)"]
        S2["Storage Location<br/>(Outside Webroot)"]
        S3["Content-Disposition: attachment"]
        S4["X-Content-Type-Options: nosniff"]
        S5["Restrictive Permissions<br/>(Non-executable)"]
    end
    
    subgraph "Exploit Outcomes"
        E1["Remote Code Execution"]
        E2["Stored XSS"]
        E3["XXE Attack"]
        E4["Path Traversal"]
        E5["DoS via Large Files"]
    end
    
    A1 --> A2 & A3 & A4 & A5 & A6
    
    A2 --> V1
    A3 --> V1
    A4 --> V2
    A5 --> V3
    A6 --> V3
    A1 --> V4
    
    V1 -->|"If bypass succeeds"| E1 & E2
    V2 -->|"If bypass succeeds"| E1 & E2
    V3 -->|"If bypass succeeds"| E2 & E3
    V4 -->|"If bypass succeeds"| E5
    
    V1 & V2 & V3 & V4 -->|"If validation passes"| S1
    S1 --> S2 --> S3 & S4 & S5
    
    S2 & S3 & S4 & S5 -->|"Defense in Depth"| SAFE["Secure File Access"]
```

**Sources:** [SKILL.md:394-454]()

---

## Three-Tier Validation Architecture

File upload validation must implement three independent validation layers. Relying on a single check creates bypass opportunities.

### Tier 1: File Type Validation

Extension validation provides the first security boundary but must not be the only defense.

**Implementation Requirements:**
- Check file extension against an allowlist (never use blocklist)
- Validate the complete extension, not just the final suffix
- Reject files with multiple extensions or suspicious patterns

**Bypass Prevention:**
- `shell.php.jpg` → Validate full extension chain
- `shell.jpg.php` → Only allow single extension
- `shell.php%00.jpg` → Sanitize filename for null bytes before validation

### Tier 2: Magic Byte Verification

Magic bytes (file signatures) provide cryptographic proof of file type and cannot be spoofed by simply renaming files.

**Magic Bytes Reference Table:**

| File Type | Magic Bytes (Hexadecimal) | Offset |
|-----------|---------------------------|--------|
| JPEG | `FF D8 FF` | 0 |
| PNG | `89 50 4E 47 0D 0A 1A 0A` | 0 |
| GIF87a | `47 49 46 38 37 61` | 0 |
| GIF89a | `47 49 46 38 39 61` | 0 |
| PDF | `25 50 44 46` | 0 |
| ZIP | `50 4B 03 04` | 0 |
| DOCX/XLSX/PPTX | `50 4B 03 04` | 0 (ZIP-based) |

**Implementation Pattern:**

```
Read first N bytes of uploaded file
Compare against expected magic bytes for declared file type
If mismatch: reject upload
If match: proceed to content validation
```

**Bypass Techniques to Block:**
- Prepending valid magic bytes to malicious payload → Validate entire file structure, not just header
- MIME type manipulation in Content-Type header → Always validate magic bytes, never trust HTTP headers

### Tier 3: Content Structure Validation

Content validation verifies the entire file conforms to the expected format specification.

**Image File Validation:**
```
Pass file to image processing library (PIL, ImageMagick, Sharp, etc.)
Attempt to decode/parse the entire image
If parsing fails: reject (indicates malformed or malicious file)
If parsing succeeds: file structure is valid
```

**Document File Validation:**
```
For Office documents (DOCX, XLSX, PPTX):
  - Parse as ZIP archive
  - Scan for embedded macros
  - Check for external entity references (XXE)
  - Validate XML structure of component files
```

**Polyglot File Detection:**

Polyglot files are valid in multiple formats simultaneously (e.g., a file that is both a valid JPEG and valid JavaScript). Content validation must parse the file in the expected format and reject if it contains unexpected structures.

**Sources:** [SKILL.md:398-415](), [SKILL.md:433-443]()

---

## Common Bypass Techniques and Mitigations

The following table catalogs known file upload bypass techniques and their corresponding prevention mechanisms:

| Attack Vector | Technique Example | Attack Mechanism | Prevention Strategy |
|---------------|-------------------|------------------|---------------------|
| **Extension Bypass** | `shell.php.jpg` | Server processes `.php` despite `.jpg` suffix | Validate complete extension; allowlist only; reject multi-extension files |
| **Null Byte Injection** | `shell.php%00.jpg` | Null byte truncates filename parsing | Sanitize filename; explicitly check for `%00` and null bytes; reject if present |
| **Double Extension** | `shell.jpg.php` | Web server processes final extension | Only allow single extension; validate no internal dots except before extension |
| **MIME Type Spoofing** | `Content-Type: image/jpeg` with PHP payload | Server trusts HTTP header | Validate magic bytes; ignore Content-Type header for validation decisions |
| **Magic Byte Injection** | Prepend `FF D8 FF` to PHP shell | File passes header check but contains executable code | Validate entire file structure via parsing library; not just header bytes |
| **Polyglot Files** | File valid as both JPEG and JS | Browser interprets as script despite image MIME type | Parse file as declared type; reject if parsing fails; set `X-Content-Type-Options: nosniff` |
| **SVG with JavaScript** | `<svg onload="alert(1)">` | SVG executed as HTML with embedded JS | Sanitize SVG XML; or disallow SVG entirely; serve with `Content-Disposition: attachment` |
| **XXE via Document Upload** | Malicious DOCX with external entity | Office document triggers XML parser XXE | Disable external entities in XML parser; see [XXE Prevention](#7.3) |
| **ZIP Slip** | Archive contains `../../../etc/passwd` | Path traversal during extraction | Validate extracted paths; canonicalize and check against base directory |
| **ImageMagick Exploits** | Specially crafted image triggers RCE | Image processing library vulnerability | Keep ImageMagick updated; use `policy.xml` to disable dangerous coders |
| **Filename Command Injection** | `; rm -rf /` in filename | Filename used in shell command without sanitization | Generate random UUID filenames; discard original filename entirely |
| **Content-Type Confusion** | Browser MIME sniffs uploaded file | Browser ignores declared MIME type | Set `X-Content-Type-Options: nosniff`; serve from separate domain |

**Sources:** [SKILL.md:417-432]()

---

## Secure Upload Handling Implementation

After validation, file handling must implement defense-in-depth to prevent exploitation even if validation is bypassed.

### File Storage Architecture

```mermaid
graph TB
    subgraph "Upload Processing Pipeline"
        U1["Uploaded File Received"]
        U2["Three-Tier Validation"]
        U3["Generate UUID Filename<br/>(crypto.randomUUID)"]
        U4["Discard Original Filename"]
    end
    
    subgraph "Storage Layer"
        S1["Store Outside Webroot<br/>(/var/uploads NOT /public/uploads)"]
        S2["OR: Separate Upload Domain<br/>(uploads.example.com)"]
        S3["Set File Permissions<br/>(0644 - Not Executable)"]
    end
    
    subgraph "Retrieval and Serving"
        R1["Request via Application Route<br/>(/download?id=uuid)"]
        R2["Authorization Check<br/>(User Owns Resource)"]
        R3["Read from Storage"]
        R4["Set Security Headers"]
    end
    
    subgraph "Response Headers"
        H1["Content-Disposition: attachment"]
        H2["X-Content-Type-Options: nosniff"]
        H3["Content-Type: [validated-type]"]
        H4["Cache-Control: private"]
    end
    
    U1 --> U2
    U2 -->|"Validation Passed"| U3
    U3 --> U4
    U4 --> S1
    S1 --> S3
    U4 --> S2
    S2 --> S3
    
    R1 --> R2
    R2 -->|"Authorized"| R3
    R3 --> R4
    R4 --> H1 & H2 & H3 & H4
    
    H1 & H2 & H3 & H4 --> RESPONSE["Secure File Delivery"]
```

### Storage Location Strategies

**Option 1: Outside Webroot (Preferred)**
```
Application root: /var/www/app
Public directory: /var/www/app/public
Upload directory: /var/uploads  (NOT under /var/www/app/public)
```

Files in `/var/uploads` cannot be accessed directly via HTTP. Application serves files through authenticated endpoints with authorization checks.

**Option 2: Separate Upload Domain**
```
Main application: https://app.example.com
Upload domain: https://uploads.example.com
```

Separate domain isolates uploaded content from application cookies and origin context, preventing cookie theft via XSS in uploaded files.

### Filename Sanitization

**Original filename handling:**
```
User uploads: "../../etc/passwd.jpg"
Server generates: "a3f5e9c7-4d2b-4f1a-9e8c-3b5a7d9f2c1e.jpg"
Store mapping: uuid → original filename (for display purposes only)
```

**Implementation:**
- Use `crypto.randomUUID()` or equivalent cryptographic random generator
- Preserve file extension from validated type (not from original filename)
- Store original filename in database for display purposes
- Never use original filename in file system operations

### Response Header Configuration

**Content-Disposition Header:**
```
Content-Disposition: attachment; filename="document.pdf"
```

Forces browser to download file rather than display inline, preventing execution context.

**X-Content-Type-Options Header:**
```
X-Content-Type-Options: nosniff
```

Prevents browser MIME type sniffing, ensuring browser respects declared Content-Type.

**Content-Type Header:**
```
Content-Type: image/jpeg
```

Must match the validated file type from magic byte verification, not the user-declared type.

**Sources:** [SKILL.md:444-454]()

---

## File Size Limit Enforcement

File size limits prevent denial-of-service attacks through resource exhaustion.

### Multi-Layer Size Validation

```mermaid
graph LR
    subgraph "Size Limit Layers"
        L1["Client-Side Limit<br/>(User Experience)"]
        L2["Web Server Limit<br/>(nginx client_max_body_size)"]
        L3["Application Framework Limit<br/>(Express body-parser limit)"]
        L4["Application Logic Limit<br/>(File-Type-Specific Limits)"]
    end
    
    L1 -->|"Soft Limit"| L2
    L2 -->|"Hard Limit"| L3
    L3 -->|"Hard Limit"| L4
    L4 -->|"Type-Specific Validation"| ACCEPT["Accept Upload"]
```

**Implementation Guidelines:**

| Layer | Configuration Example | Purpose |
|-------|----------------------|---------|
| Client-Side | `<input accept="image/*" max="5MB">` | Improve UX; not security boundary |
| Nginx | `client_max_body_size 10M;` | Prevent extremely large requests from reaching application |
| Express | `app.use(bodyParser({ limit: '10mb' }))` | Framework-level hard limit |
| Application | `if (file.size > 5MB) reject()` | File-type-specific limits (images smaller than videos) |

**File-Type-Specific Limits:**
- Profile images: 2-5 MB
- Document uploads: 10-20 MB
- Video uploads: 100-500 MB
- Archive files: 50-100 MB

**Sources:** [SKILL.md:411-414]()

---

## Validation Workflow Implementation

The following diagram maps validation requirements to specific code-level operations:

```mermaid
flowchart TD
    START["File Upload Request Received"]
    
    START --> CHECK_SIZE{"File Size <= Limit?"}
    CHECK_SIZE -->|"No"| REJECT_SIZE["Reject: 413 Payload Too Large"]
    CHECK_SIZE -->|"Yes"| CHECK_EXT{"Extension in Allowlist?"}
    
    CHECK_EXT -->|"No"| REJECT_EXT["Reject: 400 Invalid File Type"]
    CHECK_EXT -->|"Yes"| READ_MAGIC["Read First 16 Bytes"]
    
    READ_MAGIC --> CHECK_MAGIC{"Magic Bytes Match<br/>Expected Type?"}
    CHECK_MAGIC -->|"No"| REJECT_MAGIC["Reject: 400 File Content Mismatch"]
    CHECK_MAGIC -->|"Yes"| PARSE_CONTENT["Parse Entire File<br/>with Type-Specific Library"]
    
    PARSE_CONTENT --> CHECK_PARSE{"Parse Successful?"}
    CHECK_PARSE -->|"No"| REJECT_PARSE["Reject: 400 Malformed File"]
    CHECK_PARSE -->|"Yes"| CHECK_POLY{"Additional Content<br/>Detected?"}
    
    CHECK_POLY -->|"Yes"| REJECT_POLY["Reject: 400 Polyglot Detected"]
    CHECK_POLY -->|"No"| SANITIZE["Generate UUID Filename<br/>Discard Original"]
    
    SANITIZE --> CHECK_NULL{"Null Bytes in<br/>Original Filename?"}
    CHECK_NULL -->|"Yes"| REJECT_NULL["Reject: 400 Invalid Filename"]
    CHECK_NULL -->|"No"| STORE["Store Outside Webroot<br/>Set Permissions 0644"]
    
    STORE --> DB_RECORD["Create Database Record:<br/>- UUID<br/>- Original Filename<br/>- Validated Type<br/>- File Size<br/>- Upload Timestamp<br/>- User ID"]
    
    DB_RECORD --> SUCCESS["Return: 200 OK<br/>File ID: UUID"]
```

**Code-Level Validation Sequence:**

```
1. Receive upload at POST /api/upload endpoint
2. Check Content-Length header <= max_size
3. Extract filename from multipart form data
4. Validate filename extension against ALLOWED_EXTENSIONS array
5. Read first 16 bytes into buffer
6. Compare buffer against MAGIC_BYTES_MAP[extension]
7. If image: call image_library.decode(file_buffer)
8. If document: call document_parser.validate(file_buffer)
9. Generate uuid = crypto.randomUUID()
10. filename_final = uuid + "." + validated_extension
11. Check os.path.contains_null_bytes(original_filename)
12. Write to UPLOAD_DIR/filename_final with mode=0o644
13. INSERT INTO uploads (id, original_name, type, size, user_id) VALUES (...)
14. Return JSON response with file ID
```

**Sources:** [SKILL.md:398-415]()

---

## Edge Cases and Advanced Attacks

### ImageMagick Exploit Prevention

ImageMagick has a history of RCE vulnerabilities through specially crafted image files. When using ImageMagick or similar image processing libraries:

**Mitigation:**
- Keep ImageMagick updated to latest version
- Implement `policy.xml` to disable dangerous coders:
  ```xml
  <policy domain="coder" rights="none" pattern="EPHEMERAL" />
  <policy domain="coder" rights="none" pattern="URL" />
  <policy domain="coder" rights="none" pattern="HTTPS" />
  <policy domain="coder" rights="none" pattern="MVG" />
  <policy domain="coder" rights="none" pattern="MSL" />
  ```
- Consider alternative libraries (Sharp, Pillow) with better security track records

### SVG File Handling

SVG files are XML-based and can contain JavaScript, making them high-risk for stored XSS.

**Option 1: Disallow SVG Entirely** (Recommended)
```
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
# Note: .svg intentionally excluded
```

**Option 2: Sanitize SVG**
```
1. Parse SVG as XML
2. Strip all <script> tags
3. Remove event handler attributes (onload, onclick, etc.)
4. Remove <foreignObject> elements
5. Allowlist safe SVG elements and attributes
6. Serve with Content-Disposition: attachment
```

### ZIP Archive Handling

ZIP files present multiple attack vectors:

**ZIP Slip Prevention:**
```python
import zipfile
import os

def safe_extract(zip_path, extract_to):
    base = os.path.abspath(extract_to)
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.namelist():
            member_path = os.path.abspath(os.path.join(extract_to, member))
            if not member_path.startswith(base):
                raise Exception("ZIP Slip attack detected")
            zf.extract(member, extract_to)
```

**ZIP Bomb Detection:**
```
Check uncompressed_size before extraction
If uncompressed_size / compressed_size > 100: reject
If uncompressed_size > 1GB: reject
```

**Sources:** [SKILL.md:427-432]()

---

## Complete Implementation Checklist

Use this checklist to verify file upload implementation security:

### Validation Layer
- [ ] File extension validated against allowlist (not blocklist)
- [ ] Full extension validated (reject `file.php.jpg`)
- [ ] Single extension enforced (reject multiple dots before extension)
- [ ] Null bytes checked and rejected in filename
- [ ] Magic bytes read and verified against expected type
- [ ] Entire file parsed with type-specific library
- [ ] File size validated (per-type limits enforced)
- [ ] Content-Length header checked before processing

### Storage Layer
- [ ] Original filename discarded
- [ ] UUID-based filename generated with cryptographic randomness
- [ ] Files stored outside webroot OR on separate domain
- [ ] File permissions set to non-executable (0644)
- [ ] Web server configured to prevent direct file execution
- [ ] Database record created with UUID → original filename mapping

### Retrieval Layer
- [ ] Files served through authenticated endpoint (not static paths)
- [ ] Authorization check verifies user owns/can access file
- [ ] `Content-Disposition: attachment` header set
- [ ] `X-Content-Type-Options: nosniff` header set
- [ ] `Content-Type` header matches validated type
- [ ] `Cache-Control` header set appropriately

### Special File Types
- [ ] SVG uploads disallowed OR sanitized with XML parser
- [ ] Office documents scanned for macros and external entities
- [ ] ZIP archives validated for ZIP slip and ZIP bombs
- [ ] PDF files validated for embedded JavaScript
- [ ] ImageMagick policy.xml configured if using ImageMagick

### Configuration
- [ ] Web server `client_max_body_size` / equivalent configured
- [ ] Application framework body parser limit configured
- [ ] Upload directory has restricted file system permissions
- [ ] Separate upload domain configured with CDN (optional but recommended)

**Sources:** [SKILL.md:394-454]()

---

## Related Security Considerations

File uploads intersect with multiple other security domains:

- **Access Control:** Verify user authorization before allowing file access. See [Access Control & Authorization](#5)
- **XSS via Uploads:** SVG and HTML file uploads can execute scripts. See [Cross-Site Scripting (XSS) Prevention](#6.1)
- **XXE via Documents:** DOCX, XLSX, SVG contain XML that can trigger XXE. See [XML External Entity (XXE) Prevention](#7.3)
- **Path Traversal:** File extraction and storage must canonicalize paths. See [Path Traversal Prevention](#7.4)
- **SSRF via URLs:** If accepting URLs for file import, validate destination. See [Server-Side Request Forgery (SSRF) Prevention](#7.1)

**Sources:** [SKILL.md:394-454]()

---

# Page: Authentication & Session Security

# Authentication & Session Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This page provides an overview of authentication and session security guidance provided by VibeSec-Skill. It covers the two primary authentication mechanisms addressed by the skill:

- **Password Security**: Requirements for password policies and secure storage mechanisms
- **JWT Security**: Secure implementation of JSON Web Tokens for stateless authentication

For implementation details on password hashing algorithms and storage, see [Password Security](#8.1). For comprehensive JWT implementation patterns and vulnerability prevention, see [JWT Security](#8.2).

This page does not cover access control and authorization checks, which are addressed in [Access Control & Authorization](#5). It also does not cover CSRF protection for session-based authentication, which is covered in [CSRF Protection](#6.2).

**Sources:** [SKILL.md:305-318](), [SKILL.md:645-702]()

---

## Overview

VibeSec-Skill provides security directives for authentication mechanisms to prevent common vulnerabilities that lead to account compromise, session hijacking, and authentication bypass. The skill addresses two distinct authentication patterns commonly generated by AI coding assistants:

| Authentication Pattern | Primary Vulnerabilities Addressed | SKILL.md Coverage |
|------------------------|-----------------------------------|-------------------|
| Password-based | Weak hashing algorithms, insufficient password complexity, plaintext storage | Lines 305-318 |
| Token-based (JWT) | Algorithm confusion, missing expiration, insecure storage, weak secrets | Lines 645-702 |

The skill instructs AI models to implement defense-in-depth authentication security by combining multiple controls:
- Strong cryptographic storage for credentials
- Short-lived tokens with explicit expiration
- Secure transport and storage mechanisms (httpOnly cookies, SameSite attributes)
- Algorithm validation and secret management

**Sources:** [SKILL.md:305-318](), [SKILL.md:645-702]()

---

## Authentication Security Architecture

The following diagram illustrates how VibeSec-Skill guides AI platforms to generate authentication code with layered security controls:

```mermaid
graph TB
    subgraph "User Authentication Flow"
        User["User Credentials<br/>(username + password)"]
        LoginEndpoint["Login Endpoint"]
        PasswordVerify["Password Verification"]
        TokenGen["Token Generation"]
        SessionStore["Session/Token Storage"]
    end
    
    subgraph "VibeSec-Skill Directives"
        PWRequirements["Password Requirements<br/>SKILL.md:307-312"]
        PWStorage["Secure Storage<br/>SKILL.md:314-318<br/>(Argon2id/bcrypt/scrypt)"]
        JWTSign["jwt.sign()<br/>SKILL.md:663-674<br/>(algorithm, exp, jti)"]
        JWTCookie["Cookie Settings<br/>SKILL.md:676-682<br/>(httpOnly, secure, sameSite)"]
        JWTVerify["jwt.verify()<br/>SKILL.md:686-691<br/>(algorithms allowlist)"]
    end
    
    subgraph "Security Controls Applied"
        HashCheck["Hash Comparison<br/>(Argon2id.verify/bcrypt.compare)"]
        TokenClaims["Token Claims<br/>(sub, iat, exp, jti)"]
        CookieAttribs["Cookie Attributes<br/>(httpOnly: true<br/>secure: true<br/>sameSite: 'strict')"]
        AlgoValidation["Algorithm Validation<br/>(algorithms: ['HS256'])"]
    end
    
    User --> LoginEndpoint
    LoginEndpoint --> PasswordVerify
    
    PWRequirements -.->|"Enforced during<br/>registration"| User
    PWStorage -.->|"Guides storage<br/>implementation"| PasswordVerify
    
    PasswordVerify --> HashCheck
    HashCheck -->|"Valid"| TokenGen
    
    JWTSign -.->|"Guides token<br/>creation"| TokenGen
    TokenGen --> TokenClaims
    TokenClaims --> SessionStore
    
    JWTCookie -.->|"Guides cookie<br/>settings"| SessionStore
    SessionStore --> CookieAttribs
    
    CookieAttribs -->|"Sent to client"| AuthToken["Authentication Token<br/>(in httpOnly cookie)"]
    
    AuthToken -->|"Subsequent requests"| ProtectedEndpoint["Protected Endpoint"]
    ProtectedEndpoint --> TokenValidation["Token Validation"]
    
    JWTVerify -.->|"Guides verification<br/>logic"| TokenValidation
    TokenValidation --> AlgoValidation
    AlgoValidation -->|"Valid"| AccessGranted["Access Granted"]
```

**Sources:** [SKILL.md:305-318](), [SKILL.md:663-691]()

---

## Password Security

### Core Requirements

VibeSec-Skill directs AI models to implement password policies that balance security with usability:

| Requirement | Specification | Rationale |
|-------------|---------------|-----------|
| Minimum length | 8 characters (12+ recommended) | Prevents brute force attacks |
| Maximum length | None (or very high, e.g., 128 chars) | Allows passphrase use |
| Character requirements | Allow all characters including special chars | User choice over forced complexity |
| Character type enforcement | Not required | Avoids predictable patterns |

**Sources:** [SKILL.md:307-312]()

### Storage Mechanisms

The skill explicitly prohibits weak hashing algorithms and mandates secure alternatives:

**Prohibited Algorithms:**
- `MD5` - cryptographically broken
- `SHA1` - vulnerable to collision attacks  
- `SHA256` (plain) - too fast, vulnerable to brute force
- Plaintext storage

**Required Algorithms:**
- `Argon2id` (preferred)
- `bcrypt`
- `scrypt`

These algorithms are specifically designed for password hashing with built-in salting and computational cost factors that resist brute force attacks.

For detailed implementation patterns and language-specific examples, see [Password Security](#8.1).

**Sources:** [SKILL.md:314-318]()

---

## JWT Security

### Vulnerability Coverage

VibeSec-Skill addresses five critical JWT vulnerability classes:

```mermaid
graph LR
    subgraph "JWT Attack Vectors"
        AlgNone["alg: none Attack<br/>(Authentication Bypass)"]
        AlgConfusion["Algorithm Confusion<br/>(RSA → HMAC)"]
        WeakSecret["Weak HMAC Secret<br/>(Brute Force)"]
        NoExpiry["Missing Expiration<br/>(Infinite Token Validity)"]
        InsecureStorage["localStorage Storage<br/>(XSS Vulnerability)"]
    end
    
    subgraph "SKILL.md Prevention Directives"
        RejectNone["Reject 'none' Algorithm<br/>SKILL.md:653"]
        ExplicitAlgo["Explicit Algorithm Validation<br/>SKILL.md:654, 686"]
        StrongSecret["256+ bit Random Secret<br/>SKILL.md:655"]
        MandatoryExp["Always Set exp Claim<br/>SKILL.md:656, 670"]
        HttpOnlyCookie["httpOnly Cookie Storage<br/>SKILL.md:657, 678-682"]
    end
    
    subgraph "Generated Code Patterns"
        VerifyCode["jwt.verify(token, secret,<br/>{algorithms: ['HS256']})"]
        SignCode["jwt.sign({sub, iat, exp, jti},<br/>secret, {algorithm: 'HS256'})"]
        CookieCode["res.cookie('token', token,<br/>{httpOnly: true, secure: true,<br/>sameSite: 'strict'})"]
    end
    
    AlgNone --> RejectNone
    AlgConfusion --> ExplicitAlgo
    WeakSecret --> StrongSecret
    NoExpiry --> MandatoryExp
    InsecureStorage --> HttpOnlyCookie
    
    RejectNone --> VerifyCode
    ExplicitAlgo --> VerifyCode
    StrongSecret --> SignCode
    MandatoryExp --> SignCode
    HttpOnlyCookie --> CookieCode
```

**Sources:** [SKILL.md:645-702]()

### Token Implementation Pattern

VibeSec-Skill provides a three-phase JWT implementation pattern that AI models follow when generating authentication code:

**Phase 1: Token Signing** ([SKILL.md:663-674]())
```
jwt.sign({
  sub: userId,                    // Subject claim
  iat: Math.floor(Date.now() / 1000),  // Issued at
  exp: Math.floor(Date.now() / 1000) + (15 * 60),  // 15 min expiration
  jti: crypto.randomUUID()        // Unique token ID
}, process.env.JWT_SECRET, { 
  algorithm: 'HS256' 
})
```

**Phase 2: Token Storage** ([SKILL.md:676-682]())
```
res.cookie('token', token, {
  httpOnly: true,   // Prevents XSS access
  secure: true,     // HTTPS only
  sameSite: 'strict'  // CSRF protection
})
```

**Phase 3: Token Verification** ([SKILL.md:686-691]())
```
jwt.verify(token, secret, { algorithms: ['HS256'] }, callback)
```

The critical security control is the `algorithms` allowlist in verification, which prevents algorithm confusion attacks where attackers change the token header to use a different algorithm.

For comprehensive JWT vulnerability details, secure implementation examples, and verification checklists, see [JWT Security](#8.2).

**Sources:** [SKILL.md:663-691]()

---

## Session Security Controls

The following table maps session security requirements to specific VibeSec-Skill directives and generated code patterns:

| Security Control | SKILL.md Directive | Generated Code Pattern | Protection Against |
|------------------|-------------------|----------------------|-------------------|
| httpOnly cookie flag | Line 679 | `httpOnly: true` | XSS-based session theft |
| Secure cookie flag | Line 680 | `secure: true` | Man-in-the-middle attacks |
| SameSite attribute | Line 681 | `sameSite: 'strict'` | CSRF attacks |
| Short token lifetime | Line 670 | `exp: iat + (15 * 60)` | Token replay attacks |
| Unique token ID | Line 671 | `jti: crypto.randomUUID()` | Token revocation support |
| Secret from environment | Line 665 | `process.env.JWT_SECRET` | Secret exposure in code |
| Algorithm allowlist | Line 686 | `algorithms: ['HS256']` | Algorithm confusion |

**Sources:** [SKILL.md:663-691]()

---

## Integration with Access Control

Authentication security in VibeSec-Skill integrates with authorization checks to create a complete access control system:

```mermaid
sequenceDiagram
    participant Client
    participant AuthEndpoint["Authentication Endpoint"]
    participant JWTVerify["jwt.verify()<br/>(SKILL.md:686-691)"]
    participant ResourceEndpoint["Protected Resource Endpoint"]
    participant AuthZCheck["Authorization Check<br/>(SKILL.md:29-74)"]
    participant Resource["Resource Data"]
    
    Client->>AuthEndpoint: "POST /login<br/>{username, password}"
    
    Note over AuthEndpoint: Password verification<br/>(Argon2id/bcrypt)<br/>SKILL.md:314-318
    
    AuthEndpoint->>Client: "Set-Cookie: token=...<br/>(httpOnly, secure, sameSite)"
    
    Note over Client: Cookie stored<br/>automatically by browser
    
    Client->>ResourceEndpoint: "GET /api/resource/uuid<br/>Cookie: token=..."
    
    ResourceEndpoint->>JWTVerify: "Verify token"
    
    Note over JWTVerify: Algorithm validation<br/>algorithms: ['HS256']<br/>Expiration check
    
    JWTVerify-->>ResourceEndpoint: "decoded.sub = userId"
    
    ResourceEndpoint->>AuthZCheck: "Check resource ownership<br/>(resourceId, userId)"
    
    Note over AuthZCheck: Verify resource.ownerId<br/>== currentUser.id<br/>SKILL.md:63-74
    
    AuthZCheck-->>ResourceEndpoint: "Authorized"
    
    ResourceEndpoint->>Resource: "Fetch resource"
    Resource-->>ResourceEndpoint: "Resource data"
    ResourceEndpoint-->>Client: "200 OK + data"
```

**Key Integration Points:**

1. **Authentication → Authorization**: After `jwt.verify()` extracts `userId` from token claims (line 686-691), the application passes it to ownership verification checks (line 63-74)

2. **Session Revocation**: The `jti` claim (line 671) enables token revocation when users are removed from organizations (line 39-41)

3. **Defense in Depth**: Authentication validates the user identity, but authorization checks prevent horizontal/vertical access violations (line 53-56)

For detailed authorization patterns including IDOR prevention and privilege escalation checks, see [Access Control & Authorization](#5).

**Sources:** [SKILL.md:39-41](), [SKILL.md:63-74](), [SKILL.md:671](), [SKILL.md:686-691]()

---

## Security Checklist Integration

VibeSec-Skill provides verification checklists that AI models include as comments when generating authentication code:

### Password Security Checklist
From [SKILL.md:307-318]():
- [ ] Minimum 8 characters enforced (12+ recommended)
- [ ] No maximum length restriction (or very high limit)
- [ ] All character types allowed
- [ ] Password stored using Argon2id, bcrypt, or scrypt
- [ ] Never MD5, SHA1, or plain SHA256

### JWT Security Checklist  
From [SKILL.md:695-702]():
- [ ] Algorithm explicitly specified on verification (never trust token header)
- [ ] `alg: none` rejected
- [ ] Secret is 256+ bits of random data (not a password or phrase)
- [ ] `exp` claim always set and validated
- [ ] Tokens stored in httpOnly cookies (not localStorage/sessionStorage)
- [ ] Refresh token rotation implemented (old refresh token invalidated on use)

These checklists appear as inline comments in generated code, serving as both implementation guidance and security documentation.

**Sources:** [SKILL.md:307-318](), [SKILL.md:695-702]()

---

# Page: Password Security

# Password Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



This document covers password security requirements and storage mechanisms as defined in the VibeSec-Skill security guidance. It addresses the minimum security standards for password handling, including password strength requirements and cryptographic storage algorithms that AI-generated code should implement.

For JWT-based authentication security, see [JWT Security](#8.2). For general authentication patterns and access control, see [Authentication & Session Security](#8) and [Access Control & Authorization](#5).

**Sources:** [SKILL.md:305-318]()

---

## Overview

Password security in VibeSec-Skill operates on two distinct principles:

1. **User-Friendly Requirements**: Avoid restrictive password policies that force users into predictable patterns
2. **Strong Cryptographic Storage**: Use modern, computationally expensive hashing algorithms designed specifically for password storage

This dual approach recognizes that password complexity rules often lead to weaker passwords (e.g., `Password1!`), while proper cryptographic storage protects even weaker passwords from brute-force attacks.

**Sources:** [SKILL.md:305-318]()

---

## Password Requirements

### Recommended Policy

The VibeSec-Skill guidance defines password requirements that balance security with usability:

| Requirement | Specification | Rationale |
|------------|---------------|-----------|
| Minimum Length | 8 characters (12+ recommended) | Provides baseline entropy without excessive friction |
| Maximum Length | None (or very high, e.g., 128 chars) | Allows passphrases and password manager-generated passwords |
| Character Types | All characters allowed (including special chars) | Enables diverse password strategies |
| Composition Rules | No mandatory character type requirements | Avoids forcing predictable patterns like `Password1!` |

### Anti-Pattern: Restrictive Complexity Rules

Traditional complexity requirements (e.g., "must contain uppercase, lowercase, number, and symbol") are explicitly discouraged because they:

- Force users into predictable patterns (`Aa1!` suffix patterns)
- Reduce effective password space by eliminating simple but long passphrases
- Create friction that leads to password reuse across services

**Sources:** [SKILL.md:307-312]()

---

## Password Storage Algorithms

### Secure Hashing Functions

VibeSec-Skill mandates the use of password-specific hashing algorithms that incorporate key-stretching and resistance to hardware acceleration attacks:

```mermaid
graph TB
    subgraph "Approved Algorithms"
        A1["Argon2id"]
        A2["bcrypt"]
        A3["scrypt"]
    end
    
    subgraph "Algorithm Properties"
        P1["Memory-hard<br/>(GPU/ASIC resistant)"]
        P2["Configurable cost<br/>(adaptable over time)"]
        P3["Salt integration<br/>(prevents rainbow tables)"]
    end
    
    subgraph "Rejected Algorithms"
        R1["MD5"]
        R2["SHA1"]
        R3["Plain SHA256"]
    end
    
    A1 --> P1
    A1 --> P2
    A1 --> P3
    
    A2 --> P2
    A2 --> P3
    
    A3 --> P1
    A3 --> P2
    A3 --> P3
    
    R1 -.->|"Too fast"| Attack["Brute-force<br/>attack feasible"]
    R2 -.->|"Too fast"| Attack
    R3 -.->|"Too fast"| Attack
    
    style A1 fill:#d4edda,stroke:#333,stroke-width:2px
    style A2 fill:#d4edda,stroke:#333,stroke-width:2px
    style A3 fill:#d4edda,stroke:#333,stroke-width:2px
    style R1 fill:#f8d7da,stroke:#333,stroke-width:2px
    style R2 fill:#f8d7da,stroke:#333,stroke-width:2px
    style R3 fill:#f8d7da,stroke:#333,stroke-width:2px
```

**Diagram: Approved vs. Rejected Password Hashing Algorithms**

**Sources:** [SKILL.md:314-318]()

#### Argon2id (Recommended)

Argon2id is the preferred algorithm as it combines resistance to both side-channel timing attacks (Argon2i) and GPU/ASIC cracking (Argon2d). It is memory-hard, making parallelized cracking economically infeasible.

**Key Properties:**
- Winner of the Password Hashing Competition (2015)
- Memory-hard (configurable memory cost)
- Time-hard (configurable time cost)
- Parallelism parameter for multi-core resistance

#### bcrypt

bcrypt is a widely-supported alternative with decades of proven security. It uses the Blowfish cipher and incorporates a cost factor that can be increased over time as hardware improves.

**Key Properties:**
- Battle-tested since 1999
- Adaptive cost factor (work factor rounds)
- Built-in salt generation
- Wide language/framework support

#### scrypt

scrypt is a memory-hard key derivation function designed to make hardware brute-force attacks expensive by requiring significant memory allocation.

**Key Properties:**
- Memory-hard (configurable N parameter)
- CPU-hard (configurable r parameter)
- Parallelization control (p parameter)
- Originally designed for Tarsnap backup service

**Sources:** [SKILL.md:314-318]()

---

## Forbidden Algorithms

The following algorithms **must never be used** for password storage, as explicitly stated in SKILL.md:

### MD5
- Cryptographically broken since 2004
- Designed for speed, not password storage
- Collision vulnerabilities render it unsuitable even with salts

### SHA1
- Deprecated by NIST in 2011
- SHAttered attack (2017) demonstrated practical collision attacks
- Too fast for password hashing (billions of hashes per second on GPU)

### Plain SHA256
- While not cryptographically broken, SHA256 is designed for data integrity, not password storage
- Too fast: Modern GPUs can compute billions of SHA256 hashes per second
- No built-in salt or iteration mechanism
- Lacks memory-hardness properties needed to resist dedicated hardware

**Sources:** [SKILL.md:317-318]()

---

## Password Security Architecture

### Storage and Verification Flow

```mermaid
sequenceDiagram
    participant User as "User"
    participant App as "Application"
    participant Validator as "Password Validator"
    participant Hasher as "Password Hasher<br/>(Argon2id/bcrypt/scrypt)"
    participant DB as "Database"
    
    Note over User,DB: Registration Flow
    User->>App: "Submit password:<br/>mySecurePassphrase123"
    App->>Validator: "Validate length >= 8"
    
    alt Length < 8
        Validator-->>App: "Reject: too short"
        App-->>User: "Error: minimum 8 chars"
    else Length >= 8
        Validator-->>App: "Accept"
        App->>Hasher: "Hash password"
        
        activate Hasher
        Hasher->>Hasher: "Generate random salt"
        Hasher->>Hasher: "Apply cost parameters<br/>(memory, time, parallelism)"
        Hasher->>Hasher: "Compute hash"
        Hasher-->>App: "Return hash + salt<br/>$argon2id$v=19$m=65536..."
        deactivate Hasher
        
        App->>DB: "Store hash (never plaintext)"
        DB-->>App: "Stored"
        App-->>User: "Registration successful"
    end
    
    Note over User,DB: Login Verification Flow
    User->>App: "Submit login password"
    App->>DB: "Retrieve stored hash"
    DB-->>App: "$argon2id$v=19$m=65536..."
    
    App->>Hasher: "Verify password against hash"
    activate Hasher
    Hasher->>Hasher: "Extract salt + parameters<br/>from stored hash"
    Hasher->>Hasher: "Hash submitted password<br/>with same parameters"
    Hasher->>Hasher: "Constant-time comparison"
    
    alt Hashes match
        Hasher-->>App: "Verification SUCCESS"
        deactivate Hasher
        App-->>User: "Login successful"
    else Hashes don't match
        Hasher-->>App: "Verification FAILED"
        App-->>User: "Invalid credentials"
    end
```

**Diagram: Password Registration and Verification Sequence**

**Sources:** [SKILL.md:305-318]()

---

## Implementation Requirements

### Password Validation

When AI-generated code implements password validation, it should:

1. **Enforce Minimum Length**: Check `password.length >= 8` (or preferably `>= 12`)
2. **No Maximum Restrictions**: Avoid arbitrary caps like 32 or 64 characters
3. **Allow All Characters**: Accept unicode, special characters, spaces, emojis
4. **No Composition Enforcement**: Do not require specific character types

**Example Validation Logic:**
```
function isValidPassword(password):
    if password.length < 8:
        return false, "Password must be at least 8 characters"
    
    if password.length > 128:
        return false, "Password exceeds maximum length"
    
    return true, null
```

**Sources:** [SKILL.md:307-312]()

### Password Storage

When AI-generated code implements password storage, it must:

1. **Select Approved Algorithm**: Use Argon2id, bcrypt, or scrypt
2. **Never Store Plaintext**: Always hash before database insertion
3. **Use Framework Functions**: Leverage built-in hashing functions where available
4. **Configure Adequate Cost**: Use recommended cost parameters for the chosen algorithm

**Example Storage Pattern:**
```
// Pseudocode for secure password storage
function registerUser(username, password):
    # Validate password meets requirements
    if not isValidPassword(password):
        return error
    
    # Hash using approved algorithm
    hashedPassword = argon2id.hash(password, {
        memoryCost: 65536,  # 64 MB
        timeCost: 3,         # 3 iterations
        parallelism: 4       # 4 threads
    })
    
    # Store hash, never plaintext
    database.insert({
        username: username,
        passwordHash: hashedPassword
    })
```

**Sources:** [SKILL.md:314-318]()

---

## Algorithm Selection Decision Tree

```mermaid
graph TB
    Start["Select Password<br/>Hashing Algorithm"]
    
    Q1{"Language/framework<br/>has native Argon2id<br/>support?"}
    Q2{"Memory-hardness<br/>requirement critical<br/>(high-security app)?"}
    Q3{"Legacy codebase<br/>or bcrypt already<br/>in use?"}
    
    A1["Use Argon2id"]
    A2["Use scrypt"]
    A3["Use bcrypt"]
    
    Forbidden["Never use:<br/>MD5, SHA1, SHA256"]
    
    Start --> Q1
    Q1 -->|"Yes"| A1
    Q1 -->|"No"| Q2
    Q2 -->|"Yes"| A2
    Q2 -->|"No"| Q3
    Q3 -->|"Yes"| A3
    Q3 -->|"No"| A1
    
    Start -.->|"Explicit avoidance"| Forbidden
    
    style A1 fill:#d4edda,stroke:#333,stroke-width:2px
    style A2 fill:#d4edda,stroke:#333,stroke-width:2px
    style A3 fill:#d4edda,stroke:#333,stroke-width:2px
    style Forbidden fill:#f8d7da,stroke:#333,stroke-width:2px
```

**Diagram: Password Hashing Algorithm Selection**

**Sources:** [SKILL.md:314-318]()

---

## Security Rationale

### Why Memory-Hard Functions?

Traditional cryptographic hash functions (SHA family, MD5) were designed for speed and low resource consumption. This makes them optimal for data integrity checking but catastrophic for password storage:

| Attack Method | SHA256 Performance | Argon2id Performance | Protection Factor |
|--------------|-------------------|---------------------|-------------------|
| GPU (RTX 4090) | ~60 billion hashes/sec | ~10,000 hashes/sec | 6,000,000x slower |
| ASIC Mining Rig | ~400 billion hashes/sec | Not economical | Hardware-resistant |
| Distributed Botnet | Linearly scales | Memory costs prevent scaling | Anti-parallelization |

Memory-hard functions like Argon2id force each hash computation to allocate substantial RAM (typically 64MB+), making mass parallelization on GPUs or custom hardware economically infeasible.

### Salt Integration

All approved algorithms (Argon2id, bcrypt, scrypt) automatically generate and integrate unique salts for each password. This prevents:

- **Rainbow Table Attacks**: Pre-computed hash tables become useless
- **Duplicate Password Detection**: Two users with identical passwords store different hashes
- **Batch Cracking**: Each password must be attacked individually

**Sources:** [SKILL.md:314-318]()

---

## Common Implementation Pitfalls

### Anti-Pattern 1: Custom Password Complexity Rules

```
# INCORRECT - Forces predictable patterns
function validatePassword(password):
    hasUppercase = /[A-Z]/.test(password)
    hasLowercase = /[a-z]/.test(password)
    hasNumber = /[0-9]/.test(password)
    hasSpecial = /[!@#$%^&*]/.test(password)
    
    return hasUppercase AND hasLowercase AND hasNumber AND hasSpecial
```

**Problem**: Users will choose `Password1!` patterns, reducing effective entropy.

**Correct Approach**: Enforce only minimum length, allowing diverse strategies like passphrases.

### Anti-Pattern 2: Using SHA256 with Salt

```
# INCORRECT - SHA256 is too fast
hashedPassword = sha256(password + salt)
```

**Problem**: Even with salt, GPU-based attacks can test billions of candidates per second.

**Correct Approach**: Use purpose-built password hashing functions.

### Anti-Pattern 3: Fixed Maximum Length

```
# INCORRECT - Blocks passphrases and password managers
if password.length > 32:
    return "Password too long"
```

**Problem**: Prevents secure long passphrases and auto-generated passwords.

**Correct Approach**: Set high limits (128+ characters) or remove maximum entirely.

**Sources:** [SKILL.md:305-318]()

---

## Integration with VibeSec-Skill Workflow

When developers prompt AI platforms with VibeSec-Skill installed:

1. **Prompt Recognition**: Keywords like "user registration", "password storage", or "authentication" trigger password security guidance
2. **Requirement Injection**: AI applies the 8-character minimum, no-composition-rule policy from [SKILL.md:307-312]()
3. **Algorithm Selection**: AI selects Argon2id/bcrypt/scrypt based on language/framework context
4. **Anti-Pattern Avoidance**: AI explicitly avoids MD5, SHA1, SHA256 per [SKILL.md:317-318]()
5. **Code Generation**: Output includes properly configured hashing with comments explaining security rationale

This automated guidance eliminates the most common password storage vulnerabilities (weak hashing, plaintext storage, overly restrictive policies) at code generation time.

**Sources:** [SKILL.md:1-557]()

---

## Verification Checklist

For AI-generated password handling code, verify:

- [ ] Minimum length requirement enforced (8+ characters)
- [ ] No arbitrary maximum length restriction (or set to 128+)
- [ ] All characters allowed (no character type composition rules)
- [ ] Password hashed using Argon2id, bcrypt, or scrypt
- [ ] MD5, SHA1, and plain SHA256 are NOT used
- [ ] Plaintext passwords never stored in database
- [ ] Salt generation is automatic (built into hashing function)
- [ ] Cost parameters configured appropriately for chosen algorithm
- [ ] Password comparison uses constant-time algorithm (prevents timing attacks)

**Sources:** [SKILL.md:305-318]()

---

# Page: JWT Security

# JWT Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document covers JWT (JSON Web Token) security requirements and secure implementation patterns as defined in VibeSec-Skill. It addresses common JWT vulnerabilities including algorithm confusion attacks, token forgery, and insecure storage practices that can lead to authentication bypass.

For general password-based authentication security, see [Password Security](#8.1). For broader API authentication patterns, see [API Security](#9).

**Sources:** [SKILL.md:645-702]()

---

## JWT Token Lifecycle and Attack Surface

```mermaid
flowchart TD
    subgraph "Token Generation Phase"
        UserAuth["User Authentication"]
        GenToken["jwt.sign()"]
        Claims["Token Payload:<br/>- sub (userId)<br/>- iat (issued at)<br/>- exp (expiration)<br/>- jti (unique ID)"]
        Secret["JWT_SECRET<br/>(environment variable)"]
        Algorithm["algorithm: 'HS256'"]
    end
    
    subgraph "Token Transmission Phase"
        Cookie["httpOnly Cookie"]
        CookieFlags["Cookie Attributes:<br/>- httpOnly: true<br/>- secure: true<br/>- sameSite: 'strict'"]
        LocalStorageX["localStorage ❌<br/>(vulnerable to XSS)"]
    end
    
    subgraph "Token Verification Phase"
        IncomingToken["Incoming Request"]
        VerifyAlg["Algorithm Whitelist<br/>algorithms: ['HS256']"]
        VerifyToken["jwt.verify()"]
        ValidateExp["Validate exp claim"]
        TrustPayload["Trust decoded payload"]
    end
    
    subgraph "Attack Vectors"
        AlgNone["alg: none attack<br/>(no signature)"]
        AlgConfusion["Algorithm confusion<br/>(RS256 → HS256)"]
        WeakSecret["Weak HMAC secret<br/>(&lt;256 bits)"]
        NoExpiration["Missing exp claim<br/>(never expires)"]
        XSSSteal["XSS + localStorage<br/>(token theft)"]
    end
    
    UserAuth --> GenToken
    Secret --> GenToken
    Algorithm --> GenToken
    Claims --> GenToken
    GenToken --> Cookie
    GenToken -.->|"❌ Never"| LocalStorageX
    CookieFlags --> Cookie
    Cookie --> IncomingToken
    IncomingToken --> VerifyAlg
    VerifyAlg --> VerifyToken
    Secret --> VerifyToken
    VerifyToken --> ValidateExp
    ValidateExp --> TrustPayload
    
    AlgNone -.->|"Bypasses"| VerifyToken
    AlgConfusion -.->|"Bypasses"| VerifyToken
    WeakSecret -.->|"Enables brute-force"| Secret
    NoExpiration -.->|"Bypasses"| ValidateExp
    XSSSteal -.->|"Steals from"| LocalStorageX
```

This diagram illustrates the complete JWT lifecycle from generation through verification, showing the three critical phases where security controls must be enforced. The token generation phase establishes the cryptographic foundation through proper algorithm selection and strong secrets. The transmission phase determines attack surface through storage mechanism choice. The verification phase prevents token forgery through strict algorithm validation. Attack vectors target weaknesses in each phase: `alg: none` attacks exploit missing signature verification, algorithm confusion attacks exploit type confusion between symmetric and asymmetric algorithms, weak secrets enable brute-force attacks, missing expiration enables indefinite token validity, and localStorage storage enables XSS-based token theft.

**Sources:** [SKILL.md:662-692]()

---

## JWT Vulnerability Matrix

| Vulnerability | Attack Mechanism | Prevention Requirement |
|--------------|------------------|------------------------|
| `alg: none` attack | Token header sets `"alg": "none"`, removing signature requirement entirely | Always verify algorithm server-side; explicitly reject `none` algorithm |
| Algorithm confusion | Token changes algorithm from `RS256` (asymmetric) to `HS256` (symmetric), allowing attacker to sign with public key | Explicitly specify expected algorithm in `jwt.verify()`; never derive algorithm from token header |
| Weak HMAC secrets | Short or predictable secrets enable brute-force attacks to forge tokens | Use 256+ bit cryptographically random secrets; never use passwords or phrases |
| Missing expiration | Tokens without `exp` claim remain valid indefinitely, even after logout or compromise | Always set `exp` claim during token generation; validate expiration on every verification |
| Token in localStorage | XSS attacks can read localStorage, stealing tokens for session hijacking | Store tokens in `httpOnly`, `Secure`, `sameSite=Strict` cookies only |

**Sources:** [SKILL.md:649-658]()

---

## Algorithm Validation Architecture

The most critical JWT security requirement is algorithm validation. The verification process must whitelist allowed algorithms explicitly rather than trusting the algorithm specified in the token header.

```mermaid
graph TB
    subgraph "❌ Vulnerable Pattern"
        TokenV["Incoming Token"]
        HeaderV["Read 'alg' from<br/>token header"]
        UseAlgV["Use header alg<br/>for verification"]
        VulnV["Attacker controls<br/>verification algorithm"]
        
        TokenV --> HeaderV
        HeaderV --> UseAlgV
        UseAlgV --> VulnV
    end
    
    subgraph "✓ Secure Pattern"
        TokenS["Incoming Token"]
        WhitelistS["Hardcoded whitelist:<br/>algorithms: ['HS256']"]
        VerifyS["jwt.verify(token, secret,<br/>{algorithms: ['HS256']})"]
        RejectNone["Reject if alg: 'none'"]
        RejectMismatch["Reject if alg not in whitelist"]
        TrustPayload["Trust decoded payload"]
        
        TokenS --> VerifyS
        WhitelistS --> VerifyS
        VerifyS --> RejectNone
        VerifyS --> RejectMismatch
        RejectNone --> TrustPayload
        RejectMismatch --> TrustPayload
    end
```

The vulnerable pattern reads the algorithm from the token header and uses it for verification, giving attackers control over the verification process. The secure pattern enforces a server-side algorithm whitelist passed to `jwt.verify()`, rejecting any token that doesn't match the expected algorithm regardless of what the token header claims.

**Sources:** [SKILL.md:653-654](), [SKILL.md:686-691]()

---

## Secure Token Generation Pattern

Token generation establishes the security foundation through proper claim selection, algorithm specification, and secret management.

### Token Signing Process

[SKILL.md:663-674]() demonstrates the secure signing pattern:

```
jwt.sign({
  sub: userId,
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + (15 * 60),
  jti: crypto.randomUUID()
}, secret, { 
  algorithm: 'HS256' 
})
```

### Required Token Claims

| Claim | Purpose | Security Requirement |
|-------|---------|---------------------|
| `sub` | Subject identifier (user ID) | Non-guessable identifier; prefer UUIDs over sequential integers |
| `iat` | Issued at timestamp | Enables token age validation; prevents pre-dating attacks |
| `exp` | Expiration timestamp | **Mandatory**; tokens without expiration remain valid indefinitely |
| `jti` | JWT ID (unique identifier) | Enables token revocation/blacklisting; must be cryptographically random |

### Secret Management

The JWT secret ([SKILL.md:665]()) must be:
- Stored in environment variables (`process.env.JWT_SECRET`)
- Never hardcoded in source code
- 256+ bits of cryptographic randomness
- Not derived from passwords or phrases

Short-lived tokens (15 minutes in the example) reduce the impact of token theft. The `jti` claim provides a revocation mechanism for cases where tokens must be invalidated before expiration.

**Sources:** [SKILL.md:663-674](), [SKILL.md:655-656](), [SKILL.md:669-671]()

---

## Token Storage and Transmission Security

Token storage mechanism directly determines XSS attack surface. VibeSec-Skill requires cookie-based storage with specific security attributes.

```mermaid
flowchart LR
    subgraph "Token Storage Comparison"
        direction TB
        
        subgraph "localStorage/sessionStorage ❌"
            LS["window.localStorage.setItem('token', jwt)"]
            LSAccess["JavaScript can read:<br/>document.cookie<br/>localStorage.getItem('token')"]
            XSS["XSS Attack"]
            Steal["Token stolen via<br/>XSS payload"]
            
            LS --> LSAccess
            XSS --> LSAccess
            LSAccess --> Steal
        end
        
        subgraph "httpOnly Cookie ✓"
            Cookie["res.cookie('token', jwt, {...})"]
            Flags["httpOnly: true<br/>secure: true<br/>sameSite: 'strict'"]
            NoJS["JavaScript cannot access"]
            XSSAttempt["XSS Attack"]
            Protected["Token protected from<br/>JavaScript access"]
            
            Cookie --> Flags
            Flags --> NoJS
            XSSAttempt -.->|"Cannot read"| NoJS
            NoJS --> Protected
        end
    end
```

### Cookie Attribute Requirements

[SKILL.md:678-682]() specifies three mandatory cookie attributes:

| Attribute | Value | Protection Provided |
|-----------|-------|---------------------|
| `httpOnly` | `true` | Prevents JavaScript access via `document.cookie`; mitigates XSS token theft |
| `secure` | `true` | Ensures transmission only over HTTPS; prevents network sniffing |
| `sameSite` | `'strict'` | Prevents cross-site request inclusion; mitigates CSRF attacks |

The combination of `httpOnly` and XSS protection creates defense in depth: even if XSS vulnerabilities exist, tokens remain inaccessible to attacker-controlled JavaScript. The `sameSite` attribute provides CSRF protection independent of CSRF tokens.

**Sources:** [SKILL.md:657](), [SKILL.md:678-682](), [SKILL.md:700]()

---

## Token Verification and Algorithm Whitelisting

The verification phase must prevent token forgery through strict algorithm validation and secret verification.

### Verification Process Requirements

[SKILL.md:685-691]() demonstrates the secure verification pattern:

```
jwt.verify(token, secret, { algorithms: ['HS256'] }, (err, decoded) => {
  if (err) {
    // Handle invalid token
  }
  // Trust the payload
})
```

### Critical Verification Controls

1. **Algorithm Whitelist**: The `algorithms` parameter ([SKILL.md:686]()) must be explicitly provided. Never call `jwt.verify(token, secret)` without this parameter, as it allows the token header to specify the algorithm.

2. **Rejection of `alg: none`**: [SKILL.md:653]() requires explicit rejection of unsigned tokens. When `algorithms: ['HS256']` is specified, tokens with `"alg": "none"` are automatically rejected.

3. **Secret Validation**: The same secret used in `jwt.sign()` must be used in `jwt.verify()`. Secret rotation requires invalidating all existing tokens.

4. **Expiration Validation**: The verification library automatically validates the `exp` claim ([SKILL.md:656]()). Tokens past expiration are rejected with an error.

### Error Handling

Verification failures must be handled securely:
- Invalid signature: reject with generic "unauthorized" error
- Expired token: reject with generic "unauthorized" error  
- Missing claims: reject with generic "unauthorized" error
- Never expose specific failure reasons to prevent information leakage

**Sources:** [SKILL.md:685-691](), [SKILL.md:653-654](), [SKILL.md:696-697]()

---

## Token Lifecycle Management

JWT security requires proper lifecycle management including expiration and refresh token patterns.

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Server
    participant TokenStore
    
    User->>App: "Initial login"
    App->>Server: "POST /auth/login<br/>{credentials}"
    Server->>Server: "Validate credentials"
    Server->>Server: "jwt.sign() with exp=15min"
    Server->>TokenStore: "Generate refresh token"
    Server->>App: "Set httpOnly cookie<br/>Return refresh token"
    App->>User: "Authenticated"
    
    Note over App,Server: 15 minutes later
    
    User->>App: "Request protected resource"
    App->>Server: "GET /api/data<br/>(expired token in cookie)"
    Server->>Server: "jwt.verify() fails (expired)"
    Server->>App: "401 Unauthorized"
    App->>Server: "POST /auth/refresh<br/>{refresh_token}"
    Server->>TokenStore: "Validate refresh token"
    Server->>TokenStore: "Invalidate old refresh token"
    Server->>Server: "jwt.sign() new token"
    Server->>TokenStore: "Generate new refresh token"
    Server->>App: "Set new httpOnly cookie<br/>Return new refresh token"
    App->>Server: "Retry GET /api/data<br/>(new token)"
    Server->>App: "200 OK + data"
```

### Expiration Strategy

[SKILL.md:670]() specifies short-lived access tokens (15 minutes). This limits the window of opportunity for stolen tokens while balancing user experience.

### Refresh Token Pattern

[SKILL.md:701]() requires refresh token rotation:
- Refresh tokens enable obtaining new access tokens without re-authentication
- Old refresh token is invalidated when used to prevent replay attacks
- Refresh tokens stored server-side (database) for revocation capability
- Refresh token reuse indicates potential compromise; invalidate all user sessions

### Revocation Requirements

[SKILL.md:671]() demonstrates using `jti` claim for revocation. Server maintains a blacklist or uses stateful tokens:
- Store `jti` values in database with expiration
- On logout: add current token's `jti` to blacklist
- On verification: check if `jti` is blacklisted
- Blacklist entries expire after token's `exp` time

**Sources:** [SKILL.md:669-671](), [SKILL.md:701]()

---

## JWT Implementation Checklist

[SKILL.md:694-701]() provides a comprehensive checklist for secure JWT implementation:

- [ ] **Algorithm explicitly specified on verification**: Never trust the algorithm from the token header; always pass `algorithms` parameter to `jwt.verify()`
- [ ] **`alg: none` rejected**: Ensure unsigned tokens are rejected by specifying allowed algorithms whitelist
- [ ] **Secret is 256+ bits of random data**: Generate secrets using cryptographic random number generators; never use passwords, phrases, or predictable values
- [ ] **`exp` claim always set and validated**: Every token must have an expiration; verification libraries automatically validate expiration
- [ ] **Tokens stored in httpOnly cookies**: Never store tokens in localStorage or sessionStorage; use cookies with `httpOnly`, `secure`, and `sameSite` attributes
- [ ] **Refresh token rotation implemented**: When a refresh token is used to obtain a new access token, the old refresh token must be invalidated

### Verification Pattern

The checklist items map to specific code requirements:

| Checklist Item | Code Pattern | Location |
|----------------|--------------|----------|
| Algorithm specification | `jwt.verify(token, secret, { algorithms: ['HS256'] })` | [SKILL.md:686]() |
| Secret generation | `const secret = process.env.JWT_SECRET` (256+ bit random) | [SKILL.md:665]() |
| Expiration setting | `exp: Math.floor(Date.now() / 1000) + (15 * 60)` | [SKILL.md:670]() |
| Cookie storage | `res.cookie('token', token, { httpOnly: true, secure: true, sameSite: 'strict' })` | [SKILL.md:678-682]() |

**Sources:** [SKILL.md:694-701]()

---

## Integration with VibeSec-Skill Platform

JWT security guidance is consumed by AI platforms during code generation. When developers request authentication implementation, AI models apply these security requirements automatically.

```mermaid
flowchart TD
    DevPrompt["Developer: 'Implement JWT<br/>authentication for this API'"]
    SkillLoad["AI loads SKILL.md<br/>JWT Security section"]
    
    subgraph "AI Code Generation Process"
        GenSign["Generate jwt.sign() with:<br/>- algorithm: 'HS256'<br/>- exp claim<br/>- jti claim"]
        GenCookie["Generate res.cookie() with:<br/>- httpOnly: true<br/>- secure: true<br/>- sameSite: 'strict'"]
        GenVerify["Generate jwt.verify() with:<br/>- algorithms: ['HS256']"]
        GenSecret["Generate .env template with:<br/>JWT_SECRET placeholder"]
    end
    
    OutputCode["Secure JWT implementation"]
    Comments["Code includes security comments:<br/>- Why algorithm is whitelisted<br/>- Why httpOnly is required<br/>- Why exp is mandatory"]
    
    DevPrompt --> SkillLoad
    SkillLoad --> GenSign
    SkillLoad --> GenCookie
    SkillLoad --> GenVerify
    SkillLoad --> GenSecret
    GenSign --> OutputCode
    GenCookie --> OutputCode
    GenVerify --> OutputCode
    GenSecret --> OutputCode
    OutputCode --> Comments
```

The AI platforms integrate JWT security requirements from [SKILL.md:645-702]() into code generation, ensuring that developers receive secure implementations by default rather than having to apply security fixes post-generation. This shifts JWT security left in the development lifecycle.

**Sources:** [SKILL.md:645-702](), [README.md:76-83]()

---

# Page: API Security

# API Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document covers API-specific security vulnerabilities and their prevention mechanisms in the VibeSec-Skill framework. The focus is on two primary attack vectors that affect modern web APIs: mass assignment vulnerabilities and GraphQL-specific security issues.

For general access control and authorization issues (including IDOR and privilege escalation), see [Access Control & Authorization](#5). For authentication mechanisms including JWT security, see [Authentication & Session Security](#8).

**Sources:** [SKILL.md:705-741]()

---

## Mass Assignment Vulnerabilities

Mass assignment occurs when API endpoints accept unfiltered request bodies and directly map them to database models or object properties, allowing attackers to modify fields that should be restricted.

### Attack Vector

In mass assignment attacks, an attacker includes additional fields in API request payloads to escalate privileges or modify protected attributes. The vulnerability exists when server-side code automatically binds all request body fields to model properties without filtering.

### Vulnerable Pattern

The following pattern demonstrates a critical mass assignment vulnerability:

```javascript
// VULNERABLE — user can set { role: "admin" } in request body
User.update(req.body)
```

In this pattern, the `User.update()` method accepts the entire `req.body` object without validation. An attacker can submit a request containing:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "admin",
  "isVerified": true,
  "accountBalance": 1000000
}
```

The ORM or framework will attempt to update all fields present in the request, including `role`, `isVerified`, and `accountBalance`, which should be restricted.

**Sources:** [SKILL.md:707-713]()

### Secure Implementation Pattern

The secure approach uses explicit field whitelisting:

```javascript
// SECURE — whitelist allowed fields
const allowed = ['name', 'email', 'avatar']
const updates = pick(req.body, allowed)
User.update(updates)
```

This pattern explicitly defines which fields can be modified via the API endpoint. Any additional fields in the request are ignored, preventing unauthorized attribute modification.

**Sources:** [SKILL.md:715-718]()

### Framework-Agnostic Prevention

Mass assignment prevention applies across all ORM and framework implementations. The core principle remains consistent: **always explicitly define which fields a request can modify**.

```mermaid
graph TB
    Request["API Request<br/>POST /users/:id"]
    ReqBody["req.body<br/>{name, email, role}"]
    
    subgraph "Vulnerable Flow"
        VulnCode["User.update(req.body)"]
        VulnORM["ORM/Framework<br/>Binds all fields"]
        VulnDB["Database Update<br/>SET name=?, email=?, role=?"]
        VulnResult["Privilege Escalation<br/>User gains admin role"]
    end
    
    subgraph "Secure Flow"
        Whitelist["Allowlist Definition<br/>allowed = ['name', 'email', 'avatar']"]
        PickFn["pick(req.body, allowed)"]
        Filtered["Filtered Object<br/>{name, email}"]
        SecureORM["ORM/Framework<br/>Binds only allowed fields"]
        SecureDB["Database Update<br/>SET name=?, email=?"]
        SecureResult["Safe Update<br/>Protected fields unchanged"]
    end
    
    Request --> ReqBody
    
    ReqBody --> VulnCode
    VulnCode --> VulnORM
    VulnORM --> VulnDB
    VulnDB --> VulnResult
    
    ReqBody --> Whitelist
    Whitelist --> PickFn
    PickFn --> Filtered
    Filtered --> SecureORM
    SecureORM --> SecureDB
    SecureDB --> SecureResult
```

**Diagram: Mass Assignment Attack vs. Secure Implementation Flow**

This diagram illustrates how unfiltered `req.body` binding allows privilege escalation, while the `pick()` function with an allowlist filters the request to only permitted fields before ORM binding.

**Sources:** [SKILL.md:707-721]()

### Common Protected Fields

The following fields are frequently targeted in mass assignment attacks and should never be exposed in update endpoints:

| Field Category | Examples | Risk |
|----------------|----------|------|
| Privilege fields | `role`, `isAdmin`, `permissions`, `accessLevel` | Privilege escalation |
| Verification status | `isVerified`, `emailVerified`, `phoneVerified` | Bypass verification workflows |
| Financial fields | `balance`, `credits`, `accountBalance` | Unauthorized value manipulation |
| Timestamps | `createdAt`, `lastLogin`, `verifiedAt` | Audit trail manipulation |
| System metadata | `id`, `uuid`, `organizationId`, `ownerId` | Resource ownership bypass |

**Sources:** [SKILL.md:707-721]()

---

## GraphQL Security

GraphQL APIs introduce unique attack vectors due to their flexible query structure and introspection capabilities. The VibeSec-Skill framework addresses four primary GraphQL-specific vulnerabilities.

### Vulnerability Overview

| Vulnerability | Attack Method | Impact |
|---------------|---------------|--------|
| Introspection in production | Query `__schema` and `__type` to map entire API | Full API schema disclosure |
| Query depth attack | Deeply nested queries: `user { posts { author { posts { author... } } } }` | Resource exhaustion, DoS |
| Query complexity attack | Many expensive fields in single query | Database overload, performance degradation |
| Batching attack | Multiple operations in single request | Rate limit bypass, resource exhaustion |

**Sources:** [SKILL.md:723-730]()

### Introspection Control

GraphQL introspection allows clients to query the schema structure itself. While useful for development tools, introspection should be disabled in production to prevent attackers from mapping the entire API surface.

**Prevention:**
```javascript
introspection: process.env.NODE_ENV !== 'production'
```

This configuration enables introspection during development (`NODE_ENV` not set to `'production'`) but disables it in production environments.

**Sources:** [SKILL.md:727]()

### Query Depth Limiting

Query depth attacks exploit GraphQL's ability to nest queries arbitrarily deep, causing exponential database query growth.

**Attack Example:**
```graphql
query {
  user {
    posts {
      author {
        posts {
          author {
            posts {
              # 50+ levels deep...
            }
          }
        }
      }
    }
  }
}
```

**Prevention:**
```javascript
validationRules: [
  depthLimit(10)
]
```

The `depthLimit()` validation rule enforces a maximum query nesting level of 10, rejecting deeper queries before execution.

**Sources:** [SKILL.md:728-737]()

### Query Complexity Analysis

Query complexity attacks submit queries with many expensive field resolutions in a single request, overwhelming database connections and compute resources.

**Prevention:**
```javascript
validationRules: [
  costAnalysis({ maximumCost: 1000 })
]
```

The `costAnalysis()` rule calculates the computational cost of a query based on field resolvers and enforces a maximum total cost of 1000 (arbitrary units based on implementation).

**Sources:** [SKILL.md:729-738]()

### Batching Attack Prevention

GraphQL batching allows multiple operations in a single HTTP request. Without limits, attackers can bypass rate limiting by submitting hundreds of queries in one request.

**Prevention:**
Limit the number of operations allowed per request. This is typically implemented at the GraphQL server configuration level.

**Sources:** [SKILL.md:730]()

### Secure GraphQL Server Configuration

The complete secure `ApolloServer` configuration implementing all protections:

```javascript
const server = new ApolloServer({
  introspection: process.env.NODE_ENV !== 'production',
  validationRules: [
    depthLimit(10),
    costAnalysis({ maximumCost: 1000 })
  ]
})
```

This configuration appears in [SKILL.md:733-741]() and demonstrates the recommended baseline security posture for GraphQL APIs.

**Sources:** [SKILL.md:733-741]()

```mermaid
graph TB
    Client["GraphQL Client<br/>Query Request"]
    
    subgraph "ApolloServer Configuration"
        IntrospectionCheck{"introspection:<br/>process.env.NODE_ENV !== 'production'"}
        ValidationRules["validationRules Array"]
        DepthLimit["depthLimit(10)"]
        CostAnalysis["costAnalysis({ maximumCost: 1000 })"]
    end
    
    subgraph "Query Validation Pipeline"
        IntrospectionQuery{"Is __schema or<br/>__type query?"}
        DepthCheck{"Query depth<br/>> 10 levels?"}
        CostCheck{"Query cost<br/>> 1000?"}
        BatchCheck{"Batch count<br/>> limit?"}
    end
    
    subgraph "Outcomes"
        ProductionBlock["Block: Introspection<br/>disabled in production"]
        DepthBlock["Block: Query too deep<br/>Resource exhaustion risk"]
        CostBlock["Block: Query too complex<br/>Database overload risk"]
        BatchBlock["Block: Too many operations<br/>Rate limit bypass"]
        Execute["Execute Query<br/>Return Data"]
    end
    
    Client --> IntrospectionCheck
    IntrospectionCheck --> ValidationRules
    ValidationRules --> DepthLimit
    ValidationRules --> CostAnalysis
    
    DepthLimit --> IntrospectionQuery
    IntrospectionQuery -->|Yes + Production| ProductionBlock
    IntrospectionQuery -->|No or Dev| DepthCheck
    
    DepthCheck -->|Yes| DepthBlock
    DepthCheck -->|No| CostCheck
    
    CostAnalysis --> CostCheck
    CostCheck -->|Yes| CostBlock
    CostCheck -->|No| BatchCheck
    
    BatchCheck -->|Yes| BatchBlock
    BatchCheck -->|No| Execute
```

**Diagram: GraphQL Security Validation Pipeline with ApolloServer Configuration**

This diagram maps the `ApolloServer` configuration settings to their validation pipeline execution. Each `validationRules` array element corresponds to a specific check in the pipeline that rejects malicious queries before they reach the database layer.

**Sources:** [SKILL.md:723-741]()

---

## API Security Request Flow

The following diagram illustrates how both mass assignment and GraphQL security controls integrate into the API request lifecycle:

```mermaid
sequenceDiagram
    participant Client
    participant APIEndpoint["API Endpoint<br/>(REST or GraphQL)"]
    participant MassAssignFilter["Mass Assignment Filter<br/>pick(req.body, allowlist)"]
    participant GraphQLValidator["GraphQL Validator<br/>depthLimit, costAnalysis"]
    participant BusinessLogic["Business Logic Layer"]
    participant ORM["ORM/Database Layer<br/>User.update()"]
    participant Database
    
    Client->>APIEndpoint: "POST /api/users/:id<br/>{name, email, role}"
    
    alt REST Endpoint
        APIEndpoint->>MassAssignFilter: "req.body validation"
        MassAssignFilter->>MassAssignFilter: "Filter against allowlist<br/>allowed = ['name', 'email']"
        
        alt Disallowed fields present
            MassAssignFilter-->>Client: "Fields filtered silently<br/>or 400 Bad Request"
        else Only allowed fields
            MassAssignFilter->>BusinessLogic: "Filtered request object<br/>{name, email}"
        end
    end
    
    alt GraphQL Endpoint
        APIEndpoint->>GraphQLValidator: "Parse and validate query"
        GraphQLValidator->>GraphQLValidator: "Check introspection<br/>if production"
        GraphQLValidator->>GraphQLValidator: "Calculate query depth"
        GraphQLValidator->>GraphQLValidator: "Calculate query cost"
        
        alt Validation fails
            GraphQLValidator-->>Client: "400: Query depth/cost exceeded"
        else Validation passes
            GraphQLValidator->>BusinessLogic: "Validated query"
        end
    end
    
    BusinessLogic->>ORM: "Database operation<br/>with validated data"
    ORM->>Database: "SQL with parameterized values"
    Database-->>ORM: "Result set"
    ORM-->>BusinessLogic: "Model objects"
    BusinessLogic-->>APIEndpoint: "Response data"
    APIEndpoint-->>Client: "200 OK with sanitized data"
```

**Diagram: API Security Request Flow for REST and GraphQL**

This sequence diagram shows the divergent security validation paths for REST endpoints (mass assignment filtering via `pick()`) and GraphQL endpoints (`depthLimit` and `costAnalysis` validation) before reaching the shared business logic and ORM layers.

**Sources:** [SKILL.md:705-741]()

---

## Implementation Checklist

### Mass Assignment Protection

- [ ] Identify all API endpoints that accept request bodies
- [ ] Define explicit allowlists for updatable fields per endpoint
- [ ] Implement field filtering before ORM/model binding
- [ ] Never directly pass `req.body` to update methods
- [ ] Review ORM configuration for automatic binding behavior
- [ ] Test with additional fields in requests to verify filtering
- [ ] Document which fields are updatable in API documentation

### GraphQL Security

- [ ] Set `introspection: process.env.NODE_ENV !== 'production'`
- [ ] Implement `depthLimit()` validation rule (recommended: 10 levels)
- [ ] Implement `costAnalysis()` with appropriate `maximumCost`
- [ ] Configure operation batch limits
- [ ] Test with deep nested queries to verify depth limiting
- [ ] Test with complex queries to verify cost analysis
- [ ] Monitor query complexity metrics in production
- [ ] Document query depth and cost limits for API consumers

**Sources:** [SKILL.md:705-741]()

---

## Related Security Concerns

API security intersects with multiple other security domains covered in VibeSec-Skill:

| Related Area | Intersection with API Security | Reference |
|--------------|-------------------------------|-----------|
| Access Control | APIs must verify resource ownership and permissions | [Access Control & Authorization](#5) |
| CSRF Protection | State-changing API endpoints require CSRF tokens | [CSRF Protection](#6.2) |
| JWT Security | Token validation and storage for API authentication | [JWT Security](#8.2) |
| Input Validation | All API inputs must be validated server-side | [Core Security Principles](#4) |
| SQL Injection | ORM usage in APIs must use parameterized queries | [SQL Injection Prevention](#7.2) |

**Sources:** [SKILL.md:705-741]()

---

# Page: Security Headers Reference

# Security Headers Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document provides a comprehensive reference for HTTP security headers that should be included in web application responses to protect against common attack vectors. Security headers are HTTP response headers that instruct browsers to enable additional security protections, preventing vulnerabilities such as XSS, clickjacking, MIME sniffing attacks, and man-in-the-middle attacks.

For broader XSS protection strategies beyond CSP, see [Cross-Site Scripting (XSS) Prevention](#6.1). For authentication-related headers including cookie security, see [Authentication & Session Security](#8). For file upload security headers, see [Insecure File Upload Prevention](#7.5).

**Sources:** [SKILL.md:630-642]()

---

## Security Headers in the Defense Architecture

```mermaid
graph TB
    subgraph "Client Browser"
        Browser["Browser Security Engine"]
        Renderer["Page Renderer"]
    end
    
    subgraph "HTTP Response"
        Response["HTTP/1.1 200 OK"]
        Headers["Security Headers"]
        Body["Response Body"]
    end
    
    subgraph "Security Header Categories"
        Transport["Transport Security<br/>HSTS"]
        Content["Content Security<br/>CSP, X-Content-Type-Options"]
        Frame["Frame Protection<br/>X-Frame-Options, CSP frame-ancestors"]
        Privacy["Privacy Controls<br/>Referrer-Policy"]
        Cache["Cache Controls<br/>Cache-Control"]
    end
    
    subgraph "Threat Mitigation"
        MITM["MITM Attacks"]
        XSS["XSS Attacks"]
        Clickjack["Clickjacking"]
        MIME["MIME Sniffing"]
        Leak["Information Leakage"]
    end
    
    Response --> Headers
    Response --> Body
    
    Headers --> Transport
    Headers --> Content
    Headers --> Frame
    Headers --> Privacy
    Headers --> Cache
    
    Transport --> Browser
    Content --> Browser
    Frame --> Browser
    Privacy --> Browser
    Cache --> Browser
    
    Browser --> Renderer
    
    Transport -.->|Prevents| MITM
    Content -.->|Prevents| XSS
    Content -.->|Prevents| MIME
    Frame -.->|Prevents| Clickjack
    Privacy -.->|Prevents| Leak
    Cache -.->|Prevents| Leak
```

This diagram illustrates how security headers act as a defense layer between the server response and browser rendering engine. Each header category addresses specific threat classes by instructing the browser to enforce security policies.

**Sources:** [SKILL.md:630-642](), [SKILL.md:119-144]()

---

## Complete Security Headers Implementation

The following headers should be included in all HTTP responses to establish comprehensive browser-level security:

```mermaid
graph LR
    subgraph "Server Response Configuration"
        App["Application Server"]
        Middleware["Security Headers Middleware"]
    end
    
    subgraph "Header Injection Points"
        HSTS["Strict-Transport-Security:<br/>max-age=31536000;<br/>includeSubDomains; preload"]
        CSP["Content-Security-Policy:<br/>[policy directives]"]
        XCTO["X-Content-Type-Options:<br/>nosniff"]
        XFO["X-Frame-Options:<br/>DENY"]
        RP["Referrer-Policy:<br/>strict-origin-when-cross-origin"]
        CC["Cache-Control:<br/>no-store"]
    end
    
    subgraph "Response Flow"
        Response["HTTP Response"]
        Client["Client Browser"]
    end
    
    App --> Middleware
    Middleware --> HSTS
    Middleware --> CSP
    Middleware --> XCTO
    Middleware --> XFO
    Middleware --> RP
    Middleware --> CC
    
    HSTS --> Response
    CSP --> Response
    XCTO --> Response
    XFO --> Response
    RP --> Response
    CC --> Response
    
    Response --> Client
```

**Sources:** [SKILL.md:630-642]()

---

## Strict-Transport-Security (HSTS)

### Purpose

Forces browsers to communicate with the server exclusively over HTTPS, preventing protocol downgrade attacks and cookie hijacking via man-in-the-middle attacks.

### Configuration

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

### Directive Breakdown

| Directive | Value | Purpose |
|-----------|-------|---------|
| `max-age` | `31536000` (1 year in seconds) | Duration the browser remembers to enforce HTTPS |
| `includeSubDomains` | flag | Applies policy to all subdomains |
| `preload` | flag | Allows inclusion in browser HSTS preload lists |

### Implementation Requirements

- Only send HSTS header over HTTPS connections (browsers ignore it over HTTP)
- Start with shorter `max-age` during testing (e.g., 300 seconds)
- Increase to 1 year (`31536000`) for production
- Ensure all subdomains support HTTPS before using `includeSubDomains`
- Submit to HSTS preload list at hstspreload.org for maximum protection

### Common Pitfalls

- Sending header over HTTP (ignored by browsers)
- Using excessively long `max-age` before verifying all services work over HTTPS
- Not accounting for subdomains when using `includeSubDomains`
- Forgetting to renew certificates before expiration (users cannot bypass)

**Sources:** [SKILL.md:635]()

---

## Content-Security-Policy (CSP)

### Purpose

Mitigates XSS, data injection, and clickjacking attacks by declaring allowed sources for content types (scripts, styles, images, etc.). CSP provides the strongest defense-in-depth protection against XSS vulnerabilities.

### Complete Policy Example

```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.yourdomain.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

### Directive Reference

| Directive | Purpose | Recommended Value |
|-----------|---------|------------------|
| `default-src` | Fallback for unspecified directives | `'self'` |
| `script-src` | JavaScript source allowlist | `'self'` (avoid `'unsafe-inline'`, `'unsafe-eval'`) |
| `style-src` | CSS source allowlist | `'self' 'unsafe-inline'` (use nonces for inline styles when possible) |
| `img-src` | Image source allowlist | `'self' data: https:` |
| `font-src` | Font source allowlist | `'self'` |
| `connect-src` | XMLHttpRequest/fetch/WebSocket allowlist | `'self' https://api.yourdomain.com` |
| `frame-ancestors` | Embedding restrictions (replaces X-Frame-Options) | `'none'` or specific domains |
| `base-uri` | Restricts `<base>` tag URLs | `'self'` |
| `form-action` | Form submission target allowlist | `'self'` |

### Advanced CSP Patterns

**Nonce-Based Inline Scripts:**
```
Content-Security-Policy: script-src 'self' 'nonce-{random-value}'
```
Use unique cryptographic nonce for each request to allow specific inline scripts.

**Hash-Based Inline Scripts:**
```
Content-Security-Policy: script-src 'self' 'sha256-{hash-of-script}'
```
Allow specific inline scripts by their SHA-256 hash.

**Violation Reporting:**
```
Content-Security-Policy: ...; report-uri /csp-report
```
Monitor CSP violations to detect attacks and misconfigurations.

### Critical Security Requirements

- **Never use `'unsafe-inline'` for `script-src`** - defeats XSS protection
- **Never use `'unsafe-eval'` for `script-src`** - allows `eval()`, `Function()` execution
- Use nonces or hashes for inline scripts when necessary
- Test policy in report-only mode first: `Content-Security-Policy-Report-Only`
- Gradually tighten policy based on violation reports

**Sources:** [SKILL.md:119-135](), [SKILL.md:636]()

---

## X-Content-Type-Options

### Purpose

Prevents MIME type sniffing attacks by instructing browsers to strictly follow the declared `Content-Type` header rather than attempting to detect content type from file contents.

### Configuration

```
X-Content-Type-Options: nosniff
```

### Attack Prevention

| Attack Vector | Without Header | With `nosniff` |
|---------------|----------------|----------------|
| MIME confusion | Browser interprets `.txt` file as JavaScript if it contains script | Browser strictly enforces `Content-Type: text/plain`, prevents execution |
| Polyglot files | File valid as both image and script executes | Execution prevented if `Content-Type` is image |
| Uploaded malicious files | User uploads `script.jpg` containing JavaScript | Only processed as image, script ignored |

### Implementation Context

The `X-Content-Type-Options: nosniff` header is particularly critical in three scenarios:

1. **File upload endpoints** - prevents uploaded files from being executed as unintended types
2. **User-generated content** - ensures user content is rendered, not executed
3. **API responses** - prevents JSON responses from being interpreted as HTML/script

### Integration with Other Headers

For file uploads, combine with proper `Content-Type` and `Content-Disposition`:

```
Content-Type: image/jpeg
Content-Disposition: attachment; filename="upload.jpg"
X-Content-Type-Options: nosniff
```

**Sources:** [SKILL.md:142](), [SKILL.md:431](), [SKILL.md:450]()

---

## X-Frame-Options

### Purpose

Prevents clickjacking attacks by controlling whether the page can be embedded in `<frame>`, `<iframe>`, `<embed>`, or `<object>` elements.

### Configuration Options

```
X-Frame-Options: DENY
```

| Value | Behavior | Use Case |
|-------|----------|----------|
| `DENY` | Page cannot be framed by any site | Maximum protection for sensitive pages |
| `SAMEORIGIN` | Page can only be framed by same origin | Allow internal embedding (e.g., help widgets) |

### Modern Alternative: CSP frame-ancestors

The `frame-ancestors` CSP directive provides more granular control and supersedes `X-Frame-Options`:

```
Content-Security-Policy: frame-ancestors 'none';
```

Equivalent values:
- `frame-ancestors 'none'` ≈ `X-Frame-Options: DENY`
- `frame-ancestors 'self'` ≈ `X-Frame-Options: SAMEORIGIN`
- `frame-ancestors https://trusted.com` - allows specific domains

### Implementation Strategy

For maximum compatibility, send both headers:

```
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'; [other directives]
```

Modern browsers prioritize CSP `frame-ancestors`, while legacy browsers fall back to `X-Frame-Options`.

**Sources:** [SKILL.md:143](), [SKILL.md:128]()

---

## Referrer-Policy

### Purpose

Controls how much referrer information (URL of previous page) is sent with requests, preventing information leakage through the `Referer` header.

### Configuration

```
Referrer-Policy: strict-origin-when-cross-origin
```

### Policy Options

| Policy | Behavior | Security Level |
|--------|----------|----------------|
| `no-referrer` | Never send `Referer` | Maximum privacy |
| `strict-origin` | Send origin only, HTTPS→HTTP sends nothing | High privacy |
| `strict-origin-when-cross-origin` | Full URL for same-origin, origin for cross-origin, nothing for HTTPS→HTTP | **Recommended balance** |
| `same-origin` | Send full URL to same origin only | High privacy |
| `origin` | Send origin only | Moderate privacy |
| `no-referrer-when-downgrade` | Send unless HTTPS→HTTP (browser default) | Minimal protection |
| `unsafe-url` | Always send full URL | Not recommended |

### Use Cases

**Sensitive Applications:**
```
Referrer-Policy: no-referrer
```
Use for applications handling sensitive data (medical, financial) where URL parameters may contain PII.

**General Web Applications:**
```
Referrer-Policy: strict-origin-when-cross-origin
```
Provides good balance between analytics/functionality and privacy.

### Information Leakage Prevention

The `Referer` header can leak:
- Session tokens in URL parameters
- User IDs and resource identifiers
- Internal application structure
- Search queries and filters

**Sources:** [SKILL.md:639]()

---

## Cache-Control for Sensitive Pages

### Purpose

Prevents browsers and intermediate proxies from caching sensitive information, ensuring authenticated or personalized content is not stored and potentially exposed.

### Configuration

```
Cache-Control: no-store
```

### Directive Options

| Directive | Effect | Use Case |
|-----------|--------|----------|
| `no-store` | Never cache response | Sensitive pages (account settings, payments) |
| `no-cache` | Cache but revalidate before use | Pages that change frequently but can be cached |
| `private` | Browser can cache, proxies cannot | User-specific content |
| `max-age=0` | Cache expires immediately | Deprecated, use `no-store` |

### Implementation Patterns

```mermaid
graph TB
    Request["HTTP Request"]
    RouteCheck["Route Handler"]
    
    subgraph "Cache Policy Decision"
        Public["Public Content"]
        Auth["Authenticated Content"]
        Sensitive["Sensitive Content"]
    end
    
    subgraph "Header Application"
        PubHeader["Cache-Control:<br/>public, max-age=3600"]
        AuthHeader["Cache-Control:<br/>private, max-age=300"]
        SensHeader["Cache-Control:<br/>no-store"]
    end
    
    Request --> RouteCheck
    RouteCheck --> Public
    RouteCheck --> Auth
    RouteCheck --> Sensitive
    
    Public --> PubHeader
    Auth --> AuthHeader
    Sensitive --> SensHeader
```

### Sensitive Page Identification

Apply `Cache-Control: no-store` to:

- Login pages
- Account settings
- Payment forms
- Personal data displays
- Admin panels
- API endpoints returning user-specific data
- Pages with CSRF tokens

### Additional Cache Headers

For comprehensive cache prevention, combine with:

```
Cache-Control: no-store
Pragma: no-cache
Expires: 0
```

**Sources:** [SKILL.md:640]()

---

## Cookie Security Headers

While not standalone headers, cookie security attributes are configured via the `Set-Cookie` header and are critical for session security.

### Secure Cookie Configuration

```
Set-Cookie: session=abc123; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600
```

### Cookie Attribute Reference

| Attribute | Purpose | Recommended Value |
|-----------|---------|-------------------|
| `Secure` | Only send over HTTPS | Always set in production |
| `HttpOnly` | Prevent JavaScript access | Always set for session cookies |
| `SameSite` | CSRF protection | `Strict` or `Lax` |
| `Path` | Limit cookie scope | Most specific path possible |
| `Max-Age` | Cookie lifetime in seconds | As short as practical |
| `Domain` | Cookie domain scope | Omit or set to specific subdomain |

### SameSite Options

| Value | Behavior | Use Case |
|-------|----------|----------|
| `Strict` | Cookie never sent cross-site | Maximum CSRF protection (may break OAuth flows) |
| `Lax` | Cookie sent on top-level navigation GET | Good balance (recommended for most apps) |
| `None` | Cookie sent cross-site (requires `Secure`) | Third-party contexts only |

### Implementation Example from SKILL.md

The skill document provides this secure cookie pattern for JWT tokens:

```javascript
res.cookie('token', token, {
  httpOnly: true,  // Prevent XSS access
  secure: true,    // HTTPS only
  sameSite: 'strict'  // CSRF protection
});
```

**Sources:** [SKILL.md:176-182](), [SKILL.md:677-682]()

---

## File Upload Response Headers

File upload responses require special header combinations to prevent content injection and execution attacks.

### Secure File Upload Header Pattern

```
Content-Type: image/jpeg
Content-Disposition: attachment; filename="upload.jpg"
X-Content-Type-Options: nosniff
```

### Header Purposes

| Header | Purpose | Value |
|--------|---------|-------|
| `Content-Type` | Declare actual file type | Match validated file type exactly |
| `Content-Disposition` | Force download vs inline display | `attachment` forces download |
| `X-Content-Type-Options` | Prevent MIME sniffing | `nosniff` prevents execution |

### Attack Prevention

```mermaid
graph LR
    subgraph "Attack Attempt"
        Upload["User uploads<br/>malicious.jpg.php"]
        Server["Server validates<br/>magic bytes"]
    end
    
    subgraph "Response Headers"
        CT["Content-Type:<br/>image/jpeg"]
        CD["Content-Disposition:<br/>attachment"]
        XCTO["X-Content-Type-Options:<br/>nosniff"]
    end
    
    subgraph "Browser Behavior"
        Download["Forces download"]
        NoExec["Prevents execution"]
        StrictType["Strict type enforcement"]
    end
    
    Upload --> Server
    Server --> CT
    Server --> CD
    Server --> XCTO
    
    CT --> StrictType
    CD --> Download
    XCTO --> NoExec
    
    StrictType --> NoExec
```

### Additional File Upload Protections

1. **Serve from separate domain:** Isolate uploaded content on `uploads.yourdomain.com`
2. **Disable execution:** Set restrictive file permissions (non-executable)
3. **Random filenames:** Use UUID-based names, discard original filename
4. **Outside webroot:** Store uploads in directory not directly accessible via HTTP

**Sources:** [SKILL.md:448-453]()

---

## Implementation Verification Checklist

### Server Configuration Verification

- [ ] All responses include `Strict-Transport-Security` header with `max-age` ≥ 31536000
- [ ] All responses include `X-Content-Type-Options: nosniff`
- [ ] All responses include `X-Frame-Options: DENY` or CSP `frame-ancestors`
- [ ] CSP configured with `default-src 'self'` baseline
- [ ] CSP avoids `'unsafe-inline'` and `'unsafe-eval'` for scripts
- [ ] `Referrer-Policy` set to `strict-origin-when-cross-origin` or stricter
- [ ] Sensitive pages include `Cache-Control: no-store`

### Cookie Configuration Verification

- [ ] Session cookies have `HttpOnly` flag
- [ ] Session cookies have `Secure` flag (production)
- [ ] Session cookies have `SameSite=Strict` or `SameSite=Lax`
- [ ] Cookie `Path` attribute set to most specific path
- [ ] Cookie `Max-Age` or `Expires` limits lifetime

### File Upload Headers Verification

- [ ] Uploaded files served with correct `Content-Type`
- [ ] File responses include `X-Content-Type-Options: nosniff`
- [ ] Sensitive file downloads use `Content-Disposition: attachment`
- [ ] Uploaded content served from separate domain or path

### Testing Methods

**Header Scanner:**
```bash
curl -I https://yourdomain.com | grep -i "security\|content-security\|x-frame\|x-content"
```

**Browser DevTools:**
1. Open Network tab
2. Load application page
3. Inspect response headers for any request
4. Verify all security headers present

**Automated Scanning:**
- Use SecurityHeaders.com for automated analysis
- Run OWASP ZAP or similar scanner
- Monitor CSP violation reports

**Sources:** [SKILL.md:630-642]()

---

## Header Priority and Conflicts

### CSP vs Legacy Headers

When both CSP and legacy headers are present:

| Legacy Header | CSP Equivalent | Browser Behavior |
|---------------|----------------|------------------|
| `X-Frame-Options` | `frame-ancestors` | CSP takes precedence in modern browsers |
| `X-Content-Type-Options` | No CSP equivalent | Both needed, serve different purposes |

### Recommendation

Send both CSP and legacy headers for maximum compatibility:

```
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'; default-src 'self'; ...
```

Modern browsers prioritize CSP directives, while older browsers fall back to legacy headers.

**Sources:** [SKILL.md:119-144]()

---

## Common Misconfigurations and Pitfalls

### CSP Mistakes

| Misconfiguration | Impact | Fix |
|-----------------|--------|-----|
| `script-src 'unsafe-inline'` | Defeats XSS protection | Use nonces/hashes for inline scripts |
| `default-src *` | Allows any source | Use `'self'` or specific domains |
| Missing `base-uri` | Allows `<base>` tag injection | Add `base-uri 'self'` |
| Overly permissive `connect-src` | Allows data exfiltration | Limit to specific API domains |

### HSTS Mistakes

| Misconfiguration | Impact | Fix |
|-----------------|--------|-----|
| Sent over HTTP | Header ignored | Only send over HTTPS |
| `max-age` too short | Minimal protection window | Use 31536000 (1 year) |
| `includeSubDomains` without verification | Breaks subdomains on HTTP | Verify all subdomains support HTTPS first |

### Cookie Security Mistakes

| Misconfiguration | Impact | Fix |
|-----------------|--------|-----|
| Missing `HttpOnly` | XSS can steal session | Always set `HttpOnly` for session cookies |
| Missing `Secure` in production | MITM attacks possible | Set `Secure` flag |
| `SameSite=None` without need | Enables CSRF | Use `Strict` or `Lax` |
| Storing sensitive data in cookies | Information exposure | Use session IDs only, store data server-side |

**Sources:** [SKILL.md:119-144](), [SKILL.md:630-642](), [SKILL.md:176-182]()

---

# Page: Complete Vulnerability Coverage

# Complete Vulnerability Coverage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

This document provides a comprehensive reference matrix of all vulnerability types covered by VibeSec-Skill. It organizes vulnerabilities by category, maps them to specific sections in the `SKILL.md` knowledge base, and presents coverage statistics and protection mechanisms.

For detailed implementation guidance on specific vulnerability classes, see:
- Access control patterns: [Access Control & Authorization](#5)
- Client-side vulnerabilities: [Client-Side Security](#6) and sub-pages
- Server-side vulnerabilities: [Server-Side Security](#7) and sub-pages
- Authentication mechanisms: [Authentication & Session Security](#8)
- API-specific concerns: [API Security](#9)

**Sources:** [README.md:78-98](), [SKILL.md:1-759]()

---

## Complete Vulnerability Coverage Matrix

VibeSec-Skill provides security guidance across 5 major categories, covering 20+ distinct vulnerability types with specific prevention patterns, bypass technique documentation, and implementation checklists.

| Category | Vulnerability Type | Coverage Depth | SKILL.md Location | Prevention Approach |
|----------|-------------------|----------------|-------------------|---------------------|
| **Access Control** | IDOR (Insecure Direct Object Reference) | Comprehensive | [SKILL.md:53]() | UUID usage, ownership verification |
| | Privilege Escalation | Comprehensive | [SKILL.md:54]() | Server-side role validation |
| | Horizontal Access Control | Comprehensive | [SKILL.md:55]() | User ownership checks |
| | Vertical Access Control | Comprehensive | [SKILL.md:56]() | Role-based authorization |
| | Mass Assignment | Comprehensive | [SKILL.md:57]() | Field whitelisting |
| | Token Revocation | Comprehensive | [SKILL.md:39-41]() | Session invalidation, revocation lists |
| **Client-Side** | Stored XSS | Comprehensive | [SKILL.md:80-144]() | Output encoding, CSP |
| | Reflected XSS | Comprehensive | [SKILL.md:80-144]() | Context-aware escaping |
| | DOM-based XSS | Comprehensive | [SKILL.md:80-144]() | Safe DOM manipulation |
| | CSRF (Cross-Site Request Forgery) | Comprehensive | [SKILL.md:147-210]() | CSRF tokens, SameSite cookies |
| | Secret Key Exposure | Comprehensive | [SKILL.md:213-256]() | Environment variables, server-side API calls |
| | Open Redirect | Comprehensive | [SKILL.md:259-301]() | Allowlist validation, bypass prevention |
| **Server-Side** | SSRF (Server-Side Request Forgery) | Comprehensive | [SKILL.md:323-391]() | Allowlist, DNS validation, IP filtering |
| | SQL Injection | Comprehensive | [SKILL.md:457-499]() | Parameterized queries, ORM usage |
| | XXE (XML External Entity) | Comprehensive | [SKILL.md:502-568]() | Disable external entities, DTD processing |
| | Path Traversal | Comprehensive | [SKILL.md:572-627]() | Canonicalization, indirect references |
| | Insecure File Upload | Comprehensive | [SKILL.md:394-454]() | Magic byte validation, polyglot detection |
| **Authentication** | Weak Password Storage | Comprehensive | [SKILL.md:305-318]() | Argon2id, bcrypt, scrypt |
| | JWT Security | Comprehensive | [SKILL.md:645-702]() | Algorithm validation, expiration |
| | Session Management | Moderate | [SKILL.md:39-41, 176-183]() | HttpOnly cookies, token rotation |
| **API Security** | Mass Assignment | Comprehensive | [SKILL.md:707-719]() | Whitelist allowed fields |
| | GraphQL Abuse | Comprehensive | [SKILL.md:723-741]() | Query depth/complexity limits, introspection |

**Sources:** [SKILL.md:21-741](), [README.md:82-88]()

---

## Vulnerability to SKILL.md Section Mapping

The following diagram maps each vulnerability class to its corresponding section in the `SKILL.md` knowledge base, showing how the 759-line security directive is organized:

```mermaid
graph TB
    SKILL["SKILL.md<br/>(759 lines)"]
    
    subgraph CorePrinciples["Core Principles (lines 10-17)"]
        P1["Defense in Depth"]
        P2["Fail Securely"]
        P3["Least Privilege"]
        P4["Input Validation"]
        P5["Output Encoding"]
    end
    
    subgraph AccessControl["Access Control (lines 21-75)"]
        AC1["IDOR Prevention<br/>(lines 53)"]
        AC2["Privilege Escalation<br/>(lines 54)"]
        AC3["Mass Assignment<br/>(lines 57)"]
        AC4["Token Revocation<br/>(lines 39-41)"]
        AC5["UUID Implementation<br/>(lines 34-36)"]
    end
    
    subgraph ClientSide["Client-Side (lines 78-301)"]
        CS1["XSS Prevention<br/>(lines 80-144)"]
        CS2["CSRF Protection<br/>(lines 147-210)"]
        CS3["Secret Exposure<br/>(lines 213-256)"]
        CS4["Open Redirect<br/>(lines 259-301)"]
    end
    
    subgraph ServerSide["Server-Side (lines 323-627)"]
        SS1["SSRF Prevention<br/>(lines 323-391)"]
        SS2["File Upload Security<br/>(lines 394-454)"]
        SS3["SQL Injection<br/>(lines 457-499)"]
        SS4["XXE Prevention<br/>(lines 502-568)"]
        SS5["Path Traversal<br/>(lines 572-627)"]
    end
    
    subgraph AuthAPI["Authentication & API (lines 305-741)"]
        AA1["Password Security<br/>(lines 305-318)"]
        AA2["JWT Security<br/>(lines 645-702)"]
        AA3["Mass Assignment API<br/>(lines 707-719)"]
        AA4["GraphQL Security<br/>(lines 723-741)"]
        AA5["Security Headers<br/>(lines 630-641)"]
    end
    
    SKILL --> CorePrinciples
    SKILL --> AccessControl
    SKILL --> ClientSide
    SKILL --> ServerSide
    SKILL --> AuthAPI
    
    CorePrinciples -.->|"Informs"| AccessControl
    CorePrinciples -.->|"Informs"| ClientSide
    CorePrinciples -.->|"Informs"| ServerSide
    CorePrinciples -.->|"Informs"| AuthAPI
```

**Sources:** [SKILL.md:10-17](), [SKILL.md:21-75](), [SKILL.md:78-301](), [SKILL.md:323-627](), [SKILL.md:305-741]()

---

## Coverage Depth by Category

### Access Control Coverage

The access control section spans [SKILL.md:21-75]() and provides comprehensive coverage with specific implementation patterns.

| Aspect | Coverage Detail | Lines |
|--------|----------------|-------|
| Authorization Checks | 5-point checklist with verification steps | [SKILL.md:43-49]() |
| UUID Implementation | Explicit UUIDv4 requirement, exception handling | [SKILL.md:34-36]() |
| Account Lifecycle | Token revocation, session invalidation patterns | [SKILL.md:39-41]() |
| Implementation Pattern | Pseudocode for secure resource access | [SKILL.md:61-74]() |
| Common Pitfalls | 5 vulnerability patterns with descriptions | [SKILL.md:51-57]() |

**Protection Mechanisms:**
- User ownership verification at data layer ([SKILL.md:29-32]())
- UUIDv4 for non-guessable resource identifiers ([SKILL.md:34-36]())
- Organization membership validation ([SKILL.md:31]())
- Parent resource ownership checks ([SKILL.md:49]())
- Return `404` instead of `403` to prevent enumeration ([SKILL.md:71]())

**Sources:** [SKILL.md:21-75]()

---

### Client-Side Coverage

Client-side vulnerabilities span [SKILL.md:78-301]() across four major attack vectors.

```mermaid
graph LR
    subgraph XSS["XSS Prevention (lines 80-144)"]
        XSS1["Direct Inputs<br/>(lines 86-90)"]
        XSS2["Indirect Inputs<br/>(lines 92-99)"]
        XSS3["Overlooked Sources<br/>(lines 101-108)"]
        XSS4["Output Encoding<br/>(lines 112-117)"]
        XSS5["CSP Headers<br/>(lines 119-134)"]
    end
    
    subgraph CSRF["CSRF Protection (lines 147-210)"]
        CSRF1["Authenticated Endpoints<br/>(lines 153-158)"]
        CSRF2["Pre-Auth Endpoints<br/>(lines 160-167)"]
        CSRF3["CSRF Tokens<br/>(lines 170-174)"]
        CSRF4["SameSite Cookies<br/>(lines 176-182)"]
        CSRF5["Verification Checklist<br/>(lines 201-209)"]
    end
    
    subgraph Secrets["Secret Exposure (lines 213-256)"]
        SEC1["API Keys Protection<br/>(lines 219-225)"]
        SEC2["Sensitive User Data<br/>(lines 227-233)"]
        SEC3["Infrastructure Details<br/>(lines 235-240)"]
        SEC4["Hidden Locations<br/>(lines 242-250)"]
    end
    
    subgraph OpenRedir["Open Redirect (lines 259-301)"]
        OR1["Allowlist Validation<br/>(lines 265-272)"]
        OR2["Bypass Techniques<br/>(lines 282-295)"]
        OR3["IDN Homograph<br/>(lines 297-300)"]
    end
```

**XSS Coverage Statistics:**
- 15+ input sources documented ([SKILL.md:84-108]())
- 4 context-specific encoding methods ([SKILL.md:112-117]())
- 11-directive CSP template ([SKILL.md:121-130]())
- Input sanitization libraries referenced ([SKILL.md:136-139]())

**CSRF Coverage Statistics:**
- 12 endpoint types requiring protection ([SKILL.md:151-167]())
- 3 protection mechanisms detailed ([SKILL.md:169-187]())
- 9 edge cases and common mistakes ([SKILL.md:189-198]())
- 7-point verification checklist ([SKILL.md:203-209]())

**Sources:** [SKILL.md:78-301]()

---

### Server-Side Coverage

Server-side vulnerabilities span [SKILL.md:323-627]() with the most extensive coverage in VibeSec-Skill.

| Vulnerability | Line Range | Key Features | Bypass Techniques Covered |
|---------------|------------|--------------|---------------------------|
| **SSRF** | [SKILL.md:323-391]() | 9 vulnerable features, cloud metadata protection | 14 IP/DNS bypass methods ([SKILL.md:349-364]()) |
| **File Upload** | [SKILL.md:394-454]() | Magic bytes reference, polyglot detection | 12 bypass techniques ([SKILL.md:416-431]()) |
| **SQL Injection** | [SKILL.md:457-499]() | Parameterized queries, ORM patterns | 8 injection points documented ([SKILL.md:483-492]()) |
| **XXE** | [SKILL.md:502-568]() | 5 language-specific prevention code examples | 10 vulnerable scenarios ([SKILL.md:506-520]()) |
| **Path Traversal** | [SKILL.md:572-627]() | Canonicalization algorithm, indirect references | Input sanitization patterns ([SKILL.md:614-618]()) |

**SSRF Deep Coverage:**
```mermaid
graph TB
    SSRF["SSRF Prevention<br/>(lines 323-391)"]
    
    VulnFeatures["Vulnerable Features<br/>(lines 327-338)<br/>9 feature types"]
    
    ProtStrategies["Protection Strategies<br/>(lines 340-347)<br/>Allowlist + Network Segmentation"]
    
    BypassTech["Bypass Techniques<br/>(lines 349-364)<br/>14 documented methods"]
    
    DNSRebind["DNS Rebinding Prevention<br/>(lines 366-371)<br/>4-step algorithm"]
    
    CloudMeta["Cloud Metadata<br/>(lines 373-379)<br/>AWS, GCP, Azure, DigitalOcean"]
    
    Checklist["Implementation Checklist<br/>(lines 381-390)<br/>9 validation steps"]
    
    SSRF --> VulnFeatures
    SSRF --> ProtStrategies
    SSRF --> BypassTech
    SSRF --> DNSRebind
    SSRF --> CloudMeta
    SSRF --> Checklist
```

**File Upload Coverage Highlights:**
- Magic bytes reference table for 6 file types ([SKILL.md:433-442]())
- 12 attack types with prevention strategies ([SKILL.md:416-431]())
- 5-step secure upload handling pattern ([SKILL.md:444-453]())

**Sources:** [SKILL.md:323-627]()

---

### Authentication & API Coverage

Authentication and API security span [SKILL.md:305-318]() and [SKILL.md:645-741]().

**Password Security:**
- Minimum requirements defined ([SKILL.md:307-312]())
- Storage algorithms: `Argon2id`, `bcrypt`, `scrypt` ([SKILL.md:316]())
- Forbidden algorithms: `MD5`, `SHA1`, plain `SHA256` ([SKILL.md:317]())

**JWT Security Coverage:**

| Vulnerability Type | Prevention | Code Location |
|-------------------|------------|---------------|
| `alg: none` attack | Reject `none` algorithm | [SKILL.md:653]() |
| Algorithm confusion | Explicit algorithm specification | [SKILL.md:654, 686]() |
| Weak HMAC secrets | 256+ bit random secrets | [SKILL.md:655]() |
| Missing expiration | Always set `exp` claim | [SKILL.md:656, 670]() |
| Token in localStorage | HttpOnly, Secure, SameSite cookies | [SKILL.md:657, 676-682]() |

**JWT Implementation Pattern:**
```mermaid
sequenceDiagram
    participant Code as "Generated Code"
    participant Sign as "jwt.sign()<br/>(lines 662-674)"
    participant Cookie as "res.cookie()<br/>(lines 676-682)"
    participant Verify as "jwt.verify()<br/>(lines 685-691)"
    
    Code->>Sign: "Create token with<br/>exp, jti, algorithm"
    Sign-->>Code: "Short-lived token<br/>(15 mins)"
    Code->>Cookie: "Set with httpOnly,<br/>secure, sameSite"
    Cookie-->>Code: "Protected cookie"
    Note over Verify: "Whitelist algorithm:<br/>{ algorithms: ['HS256'] }"
    Code->>Verify: "Verify with explicit<br/>algorithm check"
    Verify-->>Code: "Validated payload"
```

**API Security:**
- Mass assignment field whitelisting ([SKILL.md:707-719]())
- GraphQL introspection disabling ([SKILL.md:727]())
- Query depth limiting ([SKILL.md:728, 737]())
- Query complexity enforcement ([SKILL.md:729, 738]())
- Batching attack prevention ([SKILL.md:730]())

**Sources:** [SKILL.md:305-318](), [SKILL.md:645-702](), [SKILL.md:705-741]()

---

## Protection Mechanism Taxonomy

VibeSec-Skill organizes protection mechanisms into distinct categories based on where they are applied in the application stack:

```mermaid
graph TB
    subgraph InputLayer["Input Validation Layer"]
        IV1["Server-side validation<br/>(line 16)"]
        IV2["Type checking<br/>(line 479)"]
        IV3["Whitelist validation<br/>(line 138, 265, 617)"]
        IV4["Canonicalization<br/>(lines 595-611)"]
    end
    
    subgraph ProcessingLayer["Processing & Storage Layer"]
        PL1["Parameterized queries<br/>(lines 463-470)"]
        PL2["ORM safe methods<br/>(lines 473-476)"]
        PL3["Password hashing<br/>(line 316)"]
        PL4["Token generation<br/>(lines 171, 667-674)"]
    end
    
    subgraph OutputLayer["Output & Response Layer"]
        OL1["Context-aware encoding<br/>(lines 112-117)"]
        OL2["Security headers<br/>(lines 630-641)"]
        OL3["CSP implementation<br/>(lines 119-134)"]
        OL4["Content-Disposition<br/>(line 449)"]
    end
    
    subgraph AuthzLayer["Authorization Layer"]
        AZ1["Ownership verification<br/>(lines 29-32, 63-73)"]
        AZ2["Role validation<br/>(line 47)"]
        AZ3["Token verification<br/>(lines 685-691)"]
        AZ4["Session checks<br/>(lines 39-41)"]
    end
    
    subgraph NetworkLayer["Network & Infrastructure Layer"]
        NL1["Allowlist enforcement<br/>(lines 341-343, 265-272)"]
        NL2["IP validation<br/>(lines 384, 369)"]
        NL3["DNS rebinding prevention<br/>(lines 366-371)"]
        NL4["Cloud metadata blocking<br/>(lines 375-379)"]
    end
    
    Request["HTTP Request"] --> InputLayer
    InputLayer --> ProcessingLayer
    ProcessingLayer --> AuthzLayer
    AuthzLayer --> OutputLayer
    
    InputLayer -.-> NetworkLayer
    ProcessingLayer -.-> NetworkLayer
```

**Sources:** [SKILL.md:10-17](), [SKILL.md:112-144](), [SKILL.md:463-499](), [SKILL.md:630-641]()

---

## Coverage Statistics

### Overall Coverage Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Total Vulnerability Classes | 20+ | [README.md:82-88]() |
| Total Directive Lines | 759 | [SKILL.md:1-759]() |
| Common Vulnerability Coverage | 60-70% | [README.md:31-32]() |
| Major Categories | 5 | [README.md:82-88]() |
| Code Examples Provided | 15+ | Throughout [SKILL.md]() |
| Bypass Techniques Documented | 40+ | Various sections |
| Implementation Checklists | 8 | Various sections |

**Sources:** [README.md:31-32](), [README.md:82-88](), [SKILL.md:1-759]()

---

### Category-Level Coverage

```mermaid
graph LR
    subgraph Stats["Coverage by Category"]
        AC["Access Control<br/>55 lines<br/>6 vulnerability types"]
        CS["Client-Side<br/>224 lines<br/>4 major attack vectors"]
        SS["Server-Side<br/>305 lines<br/>5 vulnerability classes"]
        Auth["Authentication<br/>72 lines<br/>3 security areas"]
        API["API Security<br/>37 lines<br/>2 vulnerability types"]
    end
    
    AC -->|"7.2%"| Total["759 Total Lines"]
    CS -->|"29.5%"| Total
    SS -->|"40.2%"| Total
    Auth -->|"9.5%"| Total
    API -->|"4.9%"| Total
```

**Line Distribution:**
- **Server-Side Security**: 305 lines (40.2%) - [SKILL.md:323-627]()
- **Client-Side Security**: 224 lines (29.5%) - [SKILL.md:78-301]()
- **Authentication**: 72 lines (9.5%) - [SKILL.md:305-318, 645-702]()
- **Access Control**: 55 lines (7.2%) - [SKILL.md:21-75]()
- **API Security**: 37 lines (4.9%) - [SKILL.md:705-741]()
- **Core Principles & Headers**: 66 lines (8.7%) - [SKILL.md:10-17, 630-641, 744-759]()

**Sources:** [SKILL.md:1-759]()

---

### Advanced Coverage Features

VibeSec-Skill includes coverage of advanced security concerns beyond basic vulnerability prevention:

| Advanced Feature | Description | Location |
|-----------------|-------------|----------|
| **Bypass Technique Documentation** | Specific attack bypasses attackers use | Throughout SKILL.md |
| **Edge Cases** | URL fragments, DNS rebinding, polyglot files | [SKILL.md:94-108, 359, 409, 425]() |
| **Framework-Aware Patterns** | React, Vue, Node.js, Python, Java, .NET | [SKILL.md:117, 525-558]() |
| **Cloud-Aware Protection** | AWS, GCP, Azure metadata endpoints | [SKILL.md:375-379]() |
| **Language-Specific Examples** | Java, Python, PHP, Node.js, .NET code | [SKILL.md:525-558]() |
| **Security Header Templates** | Production-ready CSP, HSTS, etc. | [SKILL.md:119-134, 630-641]() |
| **Verification Checklists** | Actionable steps for each vulnerability | [SKILL.md:43-49, 201-209, 381-390, etc.]() |

**Sources:** [README.md:91-97](), [SKILL.md:various]()

---

## Premium Version Comparison

The free VibeSec-Skill covers 60-70% of common vulnerabilities. For comprehensive coverage, a premium version is available:

| Aspect | Free Version (This Repository) | Premium Version |
|--------|-------------------------------|-----------------|
| Coverage | 60-70% of common vulnerabilities | Comprehensive coverage |
| Vulnerability Classes | 20+ documented | Extended vulnerability taxonomy |
| Availability | GitHub repository | [vibesec.sh](https://vibesec.sh) |
| Line Count | 759 lines | Extended knowledge base |
| Use Case | Individual projects, learning | Enterprise, production systems |

**Sources:** [README.md:31-32]()

---

## Cross-References to Detailed Pages

For implementation details on specific vulnerability classes covered in this matrix:

- **Access Control Implementation**: See [Access Control & Authorization](#5) for detailed patterns on IDOR prevention, privilege escalation checks, and authorization verification.

- **XSS Prevention Details**: See [Cross-Site Scripting (XSS) Prevention](#6.1) for comprehensive input source cataloging, context-specific encoding, and CSP configuration.

- **CSRF Protection Patterns**: See [Cross-Site Request Forgery (CSRF) Protection](#6.2) for token implementation, SameSite cookie configuration, and edge case handling.

- **SSRF Implementation Guide**: See [Server-Side Request Forgery (SSRF) Prevention](#7.1) for allowlist patterns, DNS rebinding prevention, and cloud metadata protection.

- **SQL Injection Prevention**: See [SQL Injection Prevention](#7.2) for parameterized query patterns and injection point identification.

- **File Upload Security**: See [Insecure File Upload Prevention](#7.5) for magic byte validation, polyglot detection, and secure handling practices.

- **JWT Implementation**: See [JWT Security](#8.2) for algorithm validation, token signing patterns, and secure cookie configuration.

- **API Security Patterns**: See [API Security](#9) for mass assignment prevention and GraphQL query limiting.

**Sources:** [README.md:1-132](), [SKILL.md:1-759]()

---

# Page: License

# License

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)

</details>



This document describes the licensing terms under which VibeSec-Skill is distributed. The project uses the Apache License 2.0, which defines the legal rights and obligations for using, modifying, and redistributing the codebase and its derivative works.

For information about the project's capabilities and usage, see [Overview](#1). For installation procedures, see [Installation & Integration](#2).

**Sources:** [LICENSE:1-202]()

---

## License Overview

VibeSec-Skill is distributed under the Apache License, Version 2.0, dated January 2004. This is a permissive open-source license approved by the Apache Software Foundation and the Open Source Initiative (OSI).

The license is located at [LICENSE:1-202]() and applies to all files in the repository, including:
- `SKILL.md` - the primary security knowledge base
- `README.md` - integration documentation
- All associated documentation and configuration files

**Sources:** [LICENSE:1-3]()

---

## Key Definitions

The Apache License 2.0 defines several terms that establish the scope of the licensing agreement:

| Term | Definition | Practical Meaning |
|------|------------|-------------------|
| **License** | Terms and conditions defined in sections 1-9 | The entire Apache 2.0 license text |
| **Licensor** | Copyright owner granting the license | BehiSecc (repository owner) |
| **Work** | The work of authorship made available under the license | VibeSec-Skill repository contents |
| **You/Your** | Individual or Legal Entity exercising permissions | Users, developers, organizations using VibeSec-Skill |
| **Source** form | Preferred form for making modifications | Markdown files (`SKILL.md`, `README.md`) |
| **Derivative Works** | Works based on or derived from the Work | Modified versions of `SKILL.md`, custom security skills, forks |
| **Contribution** | Work intentionally submitted for inclusion | Pull requests, patches, additions to the repository |

**Sources:** [LICENSE:7-65]()

---

## Grant of Rights

The Apache License 2.0 provides two primary grants to users:

### Diagram: License Grants and User Rights

```mermaid
graph TB
    License["Apache License 2.0<br/>(LICENSE:1-202)"]
    
    subgraph "Copyright Grant"
        CG["Grant of Copyright License<br/>(LICENSE:66-71)"]
        CG1["Reproduce the Work"]
        CG2["Prepare Derivative Works"]
        CG3["Publicly display/perform"]
        CG4["Sublicense"]
        CG5["Distribute in Source or Object form"]
    end
    
    subgraph "Patent Grant"
        PG["Grant of Patent License<br/>(LICENSE:73-87)"]
        PG1["Make, use, offer to sell"]
        PG2["Sell, import, transfer"]
        PG3["Patent claims coverage"]
        PG4["Termination on litigation"]
    end
    
    License --> CG
    License --> PG
    
    CG --> CG1 & CG2 & CG3 & CG4 & CG5
    PG --> PG1 & PG2 & PG3 & PG4
    
    subgraph "Applies to VibeSec-Skill"
        USE1["Copy SKILL.md to AI platforms"]
        USE2["Modify security directives"]
        USE3["Create custom security skills"]
        USE4["Integrate in commercial products"]
        USE5["Redistribute to teams/organizations"]
    end
    
    CG1 & CG2 & CG3 & CG4 & CG5 -.-> USE1 & USE2 & USE3 & USE4 & USE5
```

**Sources:** [LICENSE:66-87]()

### Copyright License (Section 2)

The license grants perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to:

- **Reproduce** - Make copies of `SKILL.md`, `README.md`, and other files
- **Prepare Derivative Works** - Modify security directives, create domain-specific variants
- **Publicly display/perform** - Share the skill publicly (e.g., in corporate wikis, training materials)
- **Sublicense** - Grant permissions to downstream users
- **Distribute** - Share the Work in source or compiled/processed forms

**Sources:** [LICENSE:66-71]()

### Patent License (Section 3)

The license grants perpetual, worldwide, non-exclusive, no-charge, royalty-free patent license to:

- **Make, have made, use** - Implement the security guidance in code
- **Offer to sell, sell, import, transfer** - Commercialize implementations

**Important limitation:** If you initiate patent litigation alleging that VibeSec-Skill infringes patents, your patent license terminates immediately.

**Sources:** [LICENSE:73-87]()

---

## Redistribution Requirements

When redistributing VibeSec-Skill or derivative works, you must comply with specific conditions:

### Diagram: Redistribution Compliance Checklist

```mermaid
graph LR
    Redistribute["Redistributing VibeSec-Skill"]
    
    subgraph "Mandatory Requirements"
        R1["Include LICENSE file<br/>(LICENSE:94-95)"]
        R2["Mark modified files<br/>(LICENSE:97-98)"]
        R3["Retain copyright/patent notices<br/>(LICENSE:100-104)"]
        R4["Include NOTICE file if present<br/>(LICENSE:106-121)"]
    end
    
    subgraph "Optional Additions"
        O1["Add your copyright statement<br/>(LICENSE:123)"]
        O2["Provide different license for modifications<br/>(LICENSE:124-128)"]
    end
    
    Redistribute --> R1 & R2 & R3 & R4
    Redistribute -.-> O1 & O2
    
    subgraph "Examples in VibeSec-Skill Context"
        EX1["Modified SKILL.md must note changes"]
        EX2["Custom security skills must include LICENSE"]
        EX3["Derivative works retain attribution"]
    end
    
    R1 & R2 & R3 -.-> EX1 & EX2 & EX3
```

**Sources:** [LICENSE:89-128]()

### Section 4: Redistribution Conditions

| Requirement | Description | VibeSec-Skill Application |
|-------------|-------------|---------------------------|
| **(a) Include License** | Provide copy of `LICENSE` file | Must include [LICENSE:1-202]() with any distribution |
| **(b) Mark Modifications** | State changes in modified files | Add comments to modified `SKILL.md` indicating changes |
| **(c) Retain Notices** | Preserve copyright, patent, trademark notices | Keep original attributions in distributed files |
| **(d) Include NOTICE** | Include NOTICE file if present | VibeSec-Skill currently has no NOTICE file |

**Additional permissions:**
- You may add your own copyright statement to modifications [LICENSE:123]()
- You may apply different license terms to your modifications, provided overall distribution complies with Apache 2.0 [LICENSE:124-128]()

**Sources:** [LICENSE:89-128]()

---

## Contribution Terms

Any contributions submitted to VibeSec-Skill are governed by specific terms:

### Section 5: Submission of Contributions

By default, any contribution intentionally submitted for inclusion (e.g., pull requests adding security directives to `SKILL.md`) is under the Apache 2.0 license terms, without additional conditions.

This means:
- Pull requests to improve `SKILL.md` are licensed under Apache 2.0
- Suggestions for new security patterns are contributed under Apache 2.0
- No separate Contributor License Agreement (CLA) is required

**Exception:** Separate license agreements with the licensor supersede this default.

**Sources:** [LICENSE:130-136]()

---

## Trademark Restrictions

### Section 6: Trademarks

The Apache 2.0 license **does not grant permission** to use:
- Trade names of the licensor
- Trademarks
- Service marks
- Product names

**Permitted use:** Reasonable and customary use to describe the origin of the Work (e.g., "Based on VibeSec-Skill" in derivative works).

**Implications:**
- Cannot claim official affiliation without permission
- Cannot use "VibeSec" or related marks in product names without authorization
- Can reference VibeSec-Skill when describing software origins

**Sources:** [LICENSE:138-141]()

---

## Warranties and Liability

The Apache License 2.0 includes important disclaimers that limit the licensor's legal exposure:

### Diagram: Legal Protections and User Responsibilities

```mermaid
graph TB
    Work["VibeSec-Skill<br/>(SKILL.md, README.md, LICENSE)"]
    
    subgraph "Disclaimer of Warranty (Section 7)"
        W1["Provided 'AS IS'<br/>(LICENSE:143-151)"]
        W2["No warranties:<br/>- TITLE<br/>- NON-INFRINGEMENT<br/>- MERCHANTABILITY<br/>- FITNESS FOR PURPOSE"]
        W3["User assumes all risks"]
    end
    
    subgraph "Limitation of Liability (Section 8)"
        L1["No Contributor liable for damages<br/>(LICENSE:153-163)"]
        L2["Includes:<br/>- Direct/indirect damages<br/>- Special/incidental damages<br/>- Loss of goodwill<br/>- Work stoppage"]
        L3["Even if advised of possibility"]
    end
    
    subgraph "User Responsibilities"
        U1["Determine appropriateness of use"]
        U2["Assume risks of redistribution"]
        U3["Evaluate security effectiveness"]
        U4["Validate in your environment"]
    end
    
    Work --> W1
    W1 --> W2 --> W3
    
    Work --> L1
    L1 --> L2 --> L3
    
    W3 & L3 -.->|"User must"| U1 & U2 & U3 & U4
```

**Sources:** [LICENSE:143-163]()

### Section 7: Disclaimer of Warranty

VibeSec-Skill is provided **"AS IS"** without warranties of any kind, including:
- **No warranty of TITLE** - No guarantee of ownership rights
- **No warranty of NON-INFRINGEMENT** - No guarantee it doesn't violate patents/copyrights
- **No warranty of MERCHANTABILITY** - No guarantee it's fit for sale/use
- **No warranty of FITNESS FOR A PARTICULAR PURPOSE** - No guarantee it meets specific security needs

**Critical implication:** While `SKILL.md` provides security guidance, users must independently verify its effectiveness for their specific use cases. The license disclaims any guarantee that following the directives prevents vulnerabilities.

**Sources:** [LICENSE:143-151]()

### Section 8: Limitation of Liability

Contributors are **not liable** for damages arising from VibeSec-Skill use, including:
- Direct, indirect, special, incidental, or consequential damages
- Loss of goodwill, work stoppage, computer failure
- Any commercial damages or losses

This applies even if contributors were advised of potential damages.

**Practical meaning:** If security vulnerabilities occur despite using VibeSec-Skill guidance, the project maintainers are not legally liable.

**Sources:** [LICENSE:153-163]()

---

## Accepting Additional Liability

### Section 9: Warranty and Liability Obligations

When redistributing VibeSec-Skill or derivative works, you may:
- Offer support, warranty, or indemnity to downstream users
- Charge fees for such services

**Requirements if you accept additional obligations:**
- Act only on your own behalf (not on behalf of other contributors)
- Indemnify, defend, and hold harmless all other contributors from liability incurred due to your additional warranties

**Example scenario:** An organization creates a commercial "VibeSec-Pro" service based on `SKILL.md`, offers security guarantees to customers, and charges fees. That organization must indemnify the original VibeSec-Skill contributors if customers sue based on those guarantees.

**Sources:** [LICENSE:165-174]()

---

## Practical Implications for VibeSec-Skill Users

### Use Case Analysis

| Use Case | Permitted | Requirements | Notes |
|----------|-----------|--------------|-------|
| **Copy SKILL.md to ~/.claude/skills** | ✓ Yes | None | Standard installation per [Installation & Integration](#2) |
| **Modify security directives in SKILL.md** | ✓ Yes | Mark modifications [LICENSE:97-98]() | Document changes in comments |
| **Create industry-specific variant (e.g., SKILL-healthcare.md)** | ✓ Yes | Include LICENSE, mark as modified | Derivative work permitted |
| **Integrate into commercial AI product** | ✓ Yes | Include LICENSE, retain attributions | No royalties required |
| **Sell consulting services using VibeSec-Skill** | ✓ Yes | Indemnify contributors if offering warranties [LICENSE:165-174]() | You accept liability for your services |
| **Redistribute to enterprise teams** | ✓ Yes | Include LICENSE with distribution | Internal corporate use permitted |
| **Use "VibeSec" trademark in product name** | ✗ No (without permission) | N/A - trademark not granted [LICENSE:138-141]() | Describe origin only |
| **Remove copyright notices** | ✗ No | Must retain [LICENSE:100-104]() | Violation of license terms |

**Sources:** [LICENSE:66-174]()

---

## License Application Workflow

### Diagram: How Apache 2.0 Applies to VibeSec-Skill Lifecycle

```mermaid
graph TB
    Obtain["Developer obtains VibeSec-Skill<br/>(git clone github.com/BehiSecc/VibeSec-Skill)"]
    
    subgraph "Rights Immediately Granted"
        G1["Copyright license active<br/>(LICENSE:66-71)"]
        G2["Patent license active<br/>(LICENSE:73-87)"]
    end
    
    subgraph "Use Scenarios"
        U1["Install to ~/.claude/skills<br/>(no redistribution)"]
        U2["Modify SKILL.md for team<br/>(derivative work)"]
        U3["Redistribute to organization<br/>(redistribution)"]
        U4["Fork and publish publicly<br/>(redistribution + modification)"]
    end
    
    subgraph "Compliance Requirements"
        C1["No requirements<br/>(personal use)"]
        C2["Mark modifications<br/>(LICENSE:97-98)"]
        C3["Include LICENSE file<br/>(LICENSE:94-95)"]
        C4["Include LICENSE + mark modifications<br/>(LICENSE:94-98)"]
    end
    
    Obtain --> G1 & G2
    G1 & G2 --> U1 & U2 & U3 & U4
    
    U1 -.->|"Requires"| C1
    U2 -.->|"Requires"| C2
    U3 -.->|"Requires"| C3
    U4 -.->|"Requires"| C4
    
    subgraph "Warranties"
        W["All use 'AS IS'<br/>No warranties<br/>(LICENSE:143-151)"]
    end
    
    U1 & U2 & U3 & U4 -.-> W
```

**Sources:** [LICENSE:66-151]()

---

## License Text Location and Format

The complete Apache License 2.0 text is stored in [LICENSE:1-202](). The file structure is:

```
LICENSE
├── Header: Apache License Version 2.0 [LICENSE:1-3]()
├── Terms and Conditions [LICENSE:5-176]()
│   ├── Section 1: Definitions [LICENSE:7-65]()
│   ├── Section 2: Copyright Grant [LICENSE:66-71]()
│   ├── Section 3: Patent Grant [LICENSE:73-87]()
│   ├── Section 4: Redistribution [LICENSE:89-128]()
│   ├── Section 5: Contributions [LICENSE:130-136]()
│   ├── Section 6: Trademarks [LICENSE:138-141]()
│   ├── Section 7: Warranty Disclaimer [LICENSE:143-151]()
│   ├── Section 8: Liability Limitation [LICENSE:153-163]()
│   └── Section 9: Additional Liability [LICENSE:165-174]()
└── Appendix: Application Instructions [LICENSE:178-201]()
```

The appendix [LICENSE:178-201]() provides boilerplate text for applying the license to new works. VibeSec-Skill does not currently include this boilerplate in individual files, as the repository-level LICENSE file applies to all contents.

**Sources:** [LICENSE:1-202]()

---

## Comparison to Other Licenses

The Apache 2.0 license was chosen for VibeSec-Skill for specific reasons:

| Feature | Apache 2.0 | MIT | GPL 3.0 |
|---------|-----------|-----|---------|
| **Patent Grant** | ✓ Explicit [LICENSE:73-87]() | ✗ Silent | ✓ Explicit |
| **Copyleft** | ✗ Permissive | ✗ Permissive | ✓ Strong copyleft |
| **Commercial Use** | ✓ Unrestricted | ✓ Unrestricted | ✓ With GPL compatibility |
| **Modification Marking** | ✓ Required [LICENSE:97-98]() | ✗ Not required | ✓ Required |
| **Trademark Protection** | ✓ Explicit [LICENSE:138-141]() | ✗ Silent | ✗ Silent |

**Why Apache 2.0 for VibeSec-Skill:**
- **Patent protection** - Ensures users can implement security patterns without patent concerns
- **Permissive redistribution** - Allows integration into commercial AI platforms without copyleft restrictions
- **Modification tracking** - Requires marking changes to `SKILL.md`, preventing confusion between original and modified security guidance
- **Trademark control** - Prevents unauthorized use of VibeSec brand while allowing derivative works

**Sources:** [LICENSE:1-202]()

---

## Summary of Key Obligations

### For Users

When using VibeSec-Skill under Apache 2.0:

**You may:**
- Use `SKILL.md` in any AI platform (commercial or personal)
- Modify security directives for your needs
- Create derivative security skills
- Redistribute to teams, organizations, or publicly
- Charge for services based on VibeSec-Skill

**You must:**
- Include `LICENSE` file when redistributing [LICENSE:94-95]()
- Mark any modifications to files [LICENSE:97-98]()
- Retain copyright and attribution notices [LICENSE:100-104]()

**You cannot:**
- Use VibeSec trademarks without permission [LICENSE:138-141]()
- Hold contributors liable for damages [LICENSE:153-163]()
- Remove copyright notices from distributed files [LICENSE:100-104]()

**You accept:**
- All warranties are disclaimed - use at your own risk [LICENSE:143-151]()
- You're responsible for validating security effectiveness
- No guarantee VibeSec-Skill prevents all vulnerabilities

**Sources:** [LICENSE:66-174]()

---

## Full License Text

The complete, legally binding Apache License 2.0 text is available at [LICENSE:1-202](). This wiki page provides a summary for technical understanding; the LICENSE file text controls in case of any discrepancy.

**Official Apache License 2.0:** http://www.apache.org/licenses/LICENSE-2.0

**Sources:** [LICENSE:1-202]()