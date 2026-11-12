<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/spark-rapids-common · page 6 Contributing Guidelines · fetched 2026-10-26 -->

# Contributing Guidelines

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This document outlines the contribution requirements and development practices for the spark-rapids-common repository. It covers the Developer Certificate of Origin (DCO) sign-off requirements, quality gate compliance, and submission workflows that all contributors must follow.

For information about specific quality gates and their implementation details, see [Quality Gates System](#2). For project management automation, see [Project Management](#3).

## Developer Certificate of Origin Requirements

All contributions to spark-rapids-common must comply with the Developer Certificate of Origin (DCO) version 1.1. This requirement ensures legal compliance and establishes clear contribution ownership.

### DCO Compliance Workflow

```mermaid
flowchart TD
    DEV["Developer"] --> COMMIT["Create Commit"]
    COMMIT --> SIGNOFF{"Use --signoff flag?"}
    SIGNOFF -->|No| REJECT["Commit Rejected"]
    SIGNOFF -->|Yes| VALID["Valid Signed Commit"]
    
    VALID --> PR["Create Pull Request"]
    PR --> SIGNOFF_CHECK["signoff-check Action"]
    SIGNOFF_CHECK --> VALIDATE["Validate DCO Signatures"]
    
    VALIDATE --> CHECK_RESULTS{"All commits signed?"}
    CHECK_RESULTS -->|No| BLOCK["Block PR Merge"]
    CHECK_RESULTS -->|Yes| ALLOW["Allow PR Merge"]
    
    BLOCK --> NOTIFY["Notify Developer"]
    NOTIFY --> AMEND["Amend Commits with -s"]
    AMEND --> FORCE_PUSH["Force Push Updates"]
    FORCE_PUSH --> SIGNOFF_CHECK
```

The sign-off process requires the `--signoff` or `-s` flag when committing changes. This appends a `Signed-off-by` line containing the contributor's real name and email address.

**Sources:** [CONTRIBUTING.md:11-21]()

### Sign-off Implementation

Contributors must use their real name and configured Git email address when signing off commits:

```bash
git commit -s -m "Add cool feature."
```

The resulting commit message includes:
```
Signed-off-by: Your Name <your@email.com>
```

This signature certifies compliance with the DCO requirements defined in [CONTRIBUTING.md:28-66](). Contributors must not use pseudonyms or anonymous contributions.

**Sources:** [CONTRIBUTING.md:11-24]()

## Quality Gate Compliance

The repository enforces multiple quality gates that must pass before contributions can be merged. These gates ensure code quality, documentation integrity, and legal compliance.

### Quality Gate Architecture

```mermaid
graph TB
    subgraph "Contribution Process"
        PR["Pull Request"] --> GATES["Quality Gates"]
    end
    
    subgraph "Automated Checks"
        GATES --> LICENSE["license-header-check"]
        GATES --> SIGNOFF_ACTION["signoff-check"]
        GATES --> MARKDOWN["markdown-link-check"] 
        GATES --> SHELL["shell-check"]
        GATES --> PRDESC["pr-description-check"]
    end
    
    subgraph "Implementation Files"
        LICENSE --> LIC_ACTION["license-header-check/action.yml"]
        SIGNOFF_ACTION --> SIGN_ACTION["signoff-check/action.yml"]
        MARKDOWN --> MD_ACTION["markdown-link-check/action.yml"]
        SHELL --> SH_ACTION["shell-check/action.yml"]
        PRDESC --> PR_ACTION["pr-description-check/action.yml"]
    end
    
    subgraph "Validation Results"
        LIC_ACTION --> MERGE_GATE["Merge Decision"]
        SIGN_ACTION --> MERGE_GATE
        MD_ACTION --> MERGE_GATE
        SH_ACTION --> MERGE_GATE
        PR_ACTION --> MERGE_GATE
    end
    
    MERGE_GATE --> SUCCESS["Merge Allowed"]
    MERGE_GATE --> FAILURE["Merge Blocked"]
```

Each quality gate must pass for pull request approval. The `signoff-check` action specifically validates DCO compliance by examining commit signatures.

**Sources:** [CONTRIBUTING.md:5-10]()

## Development Workflow

Contributors must follow a structured development workflow that integrates DCO compliance with the repository's quality assurance systems.

### Contribution Process Flow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Local as "Local Repository" 
    participant GH as "GitHub Repository"
    participant Actions as "GitHub Actions"
    participant Review as "Code Reviewers"
    
    Dev->>Local: "git clone repository"
    Dev->>Local: "Create feature branch"
    Dev->>Local: "Make changes"
    Dev->>Local: "git commit -s"
    
    Note over Dev,Local: DCO sign-off required
    
    Dev->>GH: "git push origin feature-branch"
    Dev->>GH: "Create Pull Request"
    
    GH->>Actions: "Trigger quality gates"
    
    par License Check
        Actions->>Actions: "license-header-check"
    and DCO Check  
        Actions->>Actions: "signoff-check"
    and Documentation
        Actions->>Actions: "markdown-link-check"
    and Shell Scripts
        Actions->>Actions: "shell-check"
    and PR Format
        Actions->>Actions: "pr-description-check"
    end
    
    Actions-->>GH: "Quality gate results"
    GH-->>Dev: "Status checks feedback"
    
    alt All checks pass
        GH->>Review: "Request code review"
        Review-->>GH: "Approve changes"
        GH->>GH: "Merge pull request"
    else Checks fail
        Dev->>Local: "Fix issues"
        Dev->>Local: "git commit -s --amend"
        Dev->>GH: "git push --force"
    end
```

The workflow ensures DCO compliance is validated automatically through the `signoff-check` action, preventing non-compliant contributions from being merged.

**Sources:** [CONTRIBUTING.md:1-67]()

## DCO Certificate Text

The Developer Certificate of Origin establishes the legal framework for contributions. Contributors certify they have the right to submit their work under the project's open source license.

### DCO Version 1.1 Requirements

| Certification | Description |
|---------------|-------------|
| **(a) Original Work** | Contribution created wholly or partially by contributor with submission rights |
| **(b) Previous Work** | Based on appropriately licensed previous work with modification rights |
| **(c) Third Party** | Provided by another person who certified (a), (b), or (c) without modification |
| **(d) Public Record** | Understanding that contribution and personal information are public and permanent |

The full DCO text is maintained in [CONTRIBUTING.md:28-66]() and follows the standard established by the Linux Foundation at developercertificate.org.

**Sources:** [CONTRIBUTING.md:26-66]()

## Code Review Requirements

All contributions require code owner approval as defined in the repository's `CODEOWNERS` configuration. The review process integrates with DCO validation to ensure both technical and legal compliance.

### Review Integration Points

```mermaid
graph LR
    subgraph "Code Review System"
        CODEOWNERS["CODEOWNERS file"] --> REVIEWERS["Automatic Reviewer Assignment"]
        REVIEWERS --> APPROVAL["Code Owner Approval Required"]
    end
    
    subgraph "DCO Integration"
        SIGNOFF_CHECK["signoff-check action"] --> DCO_STATUS["DCO Validation Status"]
        DCO_STATUS --> MERGE_BLOCK["Merge Protection"]
    end
    
    subgraph "Merge Decision"
        APPROVAL --> MERGE_GATE["Merge Gate"]
        MERGE_BLOCK --> MERGE_GATE
        MERGE_GATE --> FINAL["Final Merge Decision"]
    end
```

The code review system works in conjunction with DCO validation to ensure contributions meet both technical standards and legal requirements before integration.

**Sources:** [CONTRIBUTING.md:5-10]()