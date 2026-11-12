<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/ViMax · page 12 Community and Support · fetched 2026-11-09 -->

# Community and Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Communication.md](Communication.md)
- [LICENSE](LICENSE)

</details>



This page documents resources for getting help with ViMax, contributing to the project, and understanding licensing terms. It covers community discussion channels (WeChat, Feishu), the GitHub issue tracker, contribution workflows, and the MIT license under which ViMax is released.

For technical troubleshooting and error resolution, see [Troubleshooting Guide](#10.6).

---

## Support Channels Overview

ViMax provides multiple channels for community interaction and support, each serving distinct purposes in the development lifecycle.

### Support Channel Architecture

```mermaid
graph TB
    subgraph "User Entry Points"
        USER["User with Question/Issue"]
    end
    
    subgraph "Community Channels"
        WECHAT["WeChat Discussion Group<br/>Communication.md QR Code"]
        FEISHU["Feishu Discussion Group<br/>Communication.md QR Code"]
    end
    
    subgraph "Official Channels"
        ISSUES["GitHub Issues<br/>github.com/HKUDS/ViMax/issues"]
        PR["Pull Requests<br/>github.com/HKUDS/ViMax/pulls"]
    end
    
    subgraph "Documentation"
        README["README.md<br/>Installation & Quickstart"]
        WIKI["Wiki Pages<br/>Technical Documentation"]
        LICENSE_FILE["LICENSE<br/>MIT Terms"]
    end
    
    subgraph "Codebase"
        MAIN_IDEA["main_idea2video.py"]
        MAIN_SCRIPT["main_script2video.py"]
        CONFIGS["configs/*.yaml"]
        PYPROJECT["pyproject.toml"]
    end
    
    USER --> WECHAT
    USER --> FEISHU
    USER --> ISSUES
    USER --> README
    
    WECHAT -.informal discussion.-> FEISHU
    ISSUES -.formal bug reports.-> PR
    
    README --> MAIN_IDEA
    README --> MAIN_SCRIPT
    README --> CONFIGS
    
    WIKI --> PYPROJECT
    WIKI --> CONFIGS
    
    PR --> CODEBASE
```

**Channel Selection Guide**:

| Channel | Purpose | Response Time | Formality | Best For |
|---------|---------|---------------|-----------|----------|
| WeChat | Real-time discussion, quick questions | Minutes-Hours | Informal | Setup help, usage questions |
| Feishu | Organized discussion threads | Hours | Semi-formal | Feature requests, design discussion |
| GitHub Issues | Bug reports, reproducible problems | Days | Formal | Bugs, API issues, documentation gaps |
| Pull Requests | Code contributions, patches | Days-Weeks | Formal | Feature implementations, fixes |

**Sources**: [Communication.md:1-7]()

---

## Getting Help

### Community Discussion Groups

ViMax maintains active discussion groups on WeChat and Feishu for real-time community support. These channels are hosted by HKUDS (Hong Kong University Data Science Lab).

**Accessing Discussion Groups**:

The [Communication.md:1-7]() file contains QR codes for joining both platforms:

```
Communication.md structure:
├── Introduction text
├── WeChat QR code image
│   └── Hosted at: https://github.com/HKUDS/.github/blob/main/profile/QR.png
└── Feishu QR code (implied)
```

**WeChat Group**:
- Scan QR code at [Communication.md:5]()
- Image width: 400px
- Suitable for: Quick questions, installation troubleshooting, API configuration help

**Feishu Group**:
- Scan QR code at [Communication.md:5]()
- Suitable for: Technical discussions, feature requests, workflow optimization

**Discussion Topics Covered**:
- API key configuration issues (see [Configuration Basics](#2.2))
- Installation problems with `uv` or dependencies in `pyproject.toml`
- Rate limiting and quota management (see [Rate Limiting Configuration](#8.4))
- Pipeline execution questions for `main_idea2video.py` or `main_script2video.py`

**Sources**: [Communication.md:1-7]()

### GitHub Issue Tracker

For reproducible bugs, API errors, or documentation improvements, file issues at the official repository:

**Repository**: `https://github.com/HKUDS/ViMax`

**When to File an Issue**:

```mermaid
flowchart TD
    START["Encountered Problem"] --> Q1{"Is it reproducible?"}
    Q1 -->|Yes| Q2{"Related to code execution?"}
    Q1 -->|No| WECHAT["Ask in WeChat/Feishu"]
    
    Q2 -->|Yes| Q3{"Error traceback available?"}
    Q2 -->|No| FEISHU["Discuss in Feishu"]
    
    Q3 -->|Yes| ISSUE["File GitHub Issue"]
    Q3 -->|No| DEBUG["Run with logging enabled<br/>working_dir inspection"]
    
    DEBUG --> ISSUE
    
    Q4{"Documentation unclear?"}
    Q4 -->|Yes| DOC_ISSUE["File Documentation Issue"]
    Q4 -->|No| FEATURE["File Feature Request"]
```

**Issue Template Structure**:

| Section | Content | Example |
|---------|---------|---------|
| **Title** | Concise problem statement | `RateLimiter deadlock when image_generator quota exceeded` |
| **Environment** | Python version, OS, dependencies | `Python 3.12, Ubuntu 22.04, uv 0.5.13` |
| **Configuration** | Relevant YAML config sections | Rate limits from `configs/idea2video.yaml` |
| **Reproduction** | Minimal code to reproduce | Commands run from `main_idea2video.py` |
| **Expected Behavior** | What should happen | Pipeline should wait and retry |
| **Actual Behavior** | What actually happens | Pipeline hangs at `RateLimiter.acquire()` |
| **Logs** | Error tracebacks, working_dir contents | Stack trace, `.working_dir/` file listing |

**Sources**: [Communication.md:1-7]()

---

## Contributing

ViMax is open-source and welcomes contributions from the community. All contributions must adhere to the MIT License terms.

### Contribution Workflow

```mermaid
graph TB
    subgraph "Preparation Phase"
        FORK["Fork Repository<br/>github.com/HKUDS/ViMax"]
        CLONE["Clone Fork Locally"]
        BRANCH["Create Feature Branch<br/>git checkout -b feature/xyz"]
    end
    
    subgraph "Development Phase"
        MODIFY["Modify Codebase"]
        TEST["Test Changes<br/>Run pipelines"]
        LINT["Check Code Quality<br/>ruff, mypy"]
        COMMIT["Commit Changes<br/>git commit -m 'descriptive message'"]
    end
    
    subgraph "Submission Phase"
        PUSH["Push to Fork<br/>git push origin feature/xyz"]
        PR["Open Pull Request"]
        REVIEW["Code Review"]
        MERGE["Merge to Main"]
    end
    
    subgraph "Testing Targets"
        TEST_IDEA["python main_idea2video.py"]
        TEST_SCRIPT["python main_script2video.py"]
        TEST_CONFIG["Validate YAML configs"]
    end
    
    FORK --> CLONE
    CLONE --> BRANCH
    BRANCH --> MODIFY
    
    MODIFY --> TEST
    TEST --> LINT
    LINT --> COMMIT
    COMMIT --> PUSH
    
    PUSH --> PR
    PR --> REVIEW
    REVIEW --> MERGE
    
    TEST --> TEST_IDEA
    TEST --> TEST_SCRIPT
    TEST --> TEST_CONFIG
```

### Contribution Guidelines

**Code Contributions**:

1. **Agent Development**: New agents should follow the pattern in existing agents (see [Agent Architecture](#5.1)).
2. **Pipeline Extensions**: Modifications to `Idea2VideoPipeline` or `Script2VideoPipeline` should maintain the async execution model and preserve caching capability.
3. **Tool Integration**: Adding new external services should include wrapping with a `RateLimiter` and updating configuration schemas.

**Documentation Contributions**:

1. **Wiki Pages**: Follow existing page structure (Overview → Technical Details → Examples) and include code citations: `[path/to/file:startLine-endLine]()`.
2. **Code Comments**: Document parameters, return values, and exceptions in docstrings.

**Testing Requirements**:

| Contribution Type | Required Tests | Validation Method |
|-------------------|----------------|-------------------|
| New Agent | End-to-end pipeline run | `python main_idea2video.py --idea "test"` |
| Pipeline Modification | Resume capability test | Delete intermediate files, rerun |
| Configuration Change | YAML validation | Load config, verify all fields |

**Sources**: [Communication.md:1-7](), [LICENSE:1-22]()

---

## License

ViMax is released under the MIT License, a permissive open-source license that allows broad usage rights with minimal restrictions.

### MIT License Terms

The complete license text is available at [LICENSE:1-22](). Key provisions:

**Copyright**: Copyright (c) 2025 [LICENSE:3]()

**Permissions Granted**:
- **Use**: Run ViMax for any purpose, commercial or non-commercial [LICENSE:5-9]()
- **Modify**: Edit source code, customize agents, extend pipelines [LICENSE:5-9]()
- **Distribute**: Share original or modified versions [LICENSE:5-9]()
- **Sublicense**: Include in projects with different licenses [LICENSE:5-9]()
- **Sell**: Incorporate into commercial products [LICENSE:5-9]()

**Conditions**:
1. **Attribution**: Include original copyright notice and license text in all copies [LICENSE:12-13]()

**Disclaimer**:
The software is provided "AS IS" without warranties of any kind. Key disclaimer excerpts from [LICENSE:15-21]():

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

### License Implications for Users

```mermaid
graph TB
    subgraph "User Actions"
        USE["Using ViMax"]
        MODIFY["Modifying ViMax"]
        DISTRIBUTE["Distributing ViMax"]
        COMMERCIAL["Commercial Use"]
    end
    
    subgraph "Requirements"
        NOTICE["Include Copyright Notice<br/>LICENSE file"]
        NONE["No Additional Requirements"]
    end
    
    subgraph "Freedoms"
        FREE_USE["Run without restrictions"]
        FREE_MOD["Customize agents, pipelines"]
        FREE_DIST["Share with others"]
        FREE_SELL["Sell products using ViMax"]
    end
    
    USE --> FREE_USE
    USE --> NONE
    
    MODIFY --> FREE_MOD
    MODIFY --> NONE
    
    DISTRIBUTE --> FREE_DIST
    DISTRIBUTE --> NOTICE
    
    COMMERCIAL --> FREE_SELL
    COMMERCIAL --> NOTICE
```

**Sources**: [LICENSE:1-22]()

---

## Getting Started with Community Participation

### First-Time Contributors

**Recommended Path**:

1. **Join Discussion Groups**: Scan QR codes in [Communication.md:5]() to join WeChat/Feishu.
2. **Read Documentation**: Review [Getting Started](#2) and [System Architecture](#3).
3. **Run Examples**: Execute `main_idea2video.py` and `main_script2video.py` with sample inputs.
4. **Identify Contribution Area**: Choose from new agents, pipeline optimizations, or documentation improvements.

**Support Resources Summary**:

| Resource | URL/Location | Purpose |
|----------|--------------|---------|
| WeChat Group | [Communication.md:5]() QR code | Real-time help |
| Feishu Group | [Communication.md:5]() QR code | Organized discussions |
| GitHub Issues | `github.com/HKUDS/ViMax/issues` | Bug reports, features |
| License | [LICENSE:1-22]() | Legal terms |

**Sources**: [Communication.md:1-7](), [LICENSE:1-22]()

---

