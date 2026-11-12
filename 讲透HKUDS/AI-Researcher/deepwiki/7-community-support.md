<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/AI-Researcher · page 7 Community & Support · fetched 2026-11-09 -->

# Community & Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Communication.md](Communication.md)

</details>



This page provides information about community resources, support channels, and how to engage with the HKUDS research group for assistance with the AI-Researcher system. For technical documentation about system usage, see [Usage Guide](#6). For installation procedures, see [Installation & Setup](#6.1).

## Overview

The AI-Researcher project maintains multiple communication channels for users to seek help, discuss research ideas, and collaborate with the development team. The primary support infrastructure is maintained by the HKUDS (Hong Kong University Data Science) research group.

## Communication Channels

### Official Discussion Groups

The HKUDS research group provides two primary communication platforms for real-time discussion and support:

| Platform | Purpose | Access Method |
|----------|---------|---------------|
| WeChat | Chinese-language community discussions, quick help, announcements | QR code in Communication.md |
| Feishu (Lark) | Team collaboration, structured discussions, file sharing | QR code in Communication.md |

Both platforms offer direct access to the development team and the broader research community. Users can join by scanning QR codes provided in [Communication.md:1-7]().

**Sources:** Communication.md

### GitHub Repository

The primary codebase and issue tracking system is hosted at:
```
https://github.com/HKUDS/AI-Researcher
```

The GitHub repository serves as the authoritative source for:
- Source code and documentation
- Issue reporting and bug tracking
- Feature requests and enhancement proposals
- Release notes and version history
- Community contributions via pull requests

## Support Resource Topology

```mermaid
graph TB
    subgraph "User Needs"
        INSTALL["Installation Issues<br/>.env configuration<br/>Docker setup"]
        USAGE["Usage Questions<br/>Task execution<br/>Parameter tuning"]
        BUG["Bug Reports<br/>Error messages<br/>Unexpected behavior"]
        RESEARCH["Research Discussion<br/>Benchmark tasks<br/>Novel ideas"]
        CONTRIB["Contributions<br/>Code changes<br/>Documentation"]
    end
    
    subgraph "Support Channels"
        WECHAT["WeChat Group<br/>Real-time chat<br/>Quick questions"]
        FEISHU["Feishu Group<br/>Structured discussion<br/>File sharing"]
        GITHUB["GitHub Issues<br/>github.com/HKUDS/AI-Researcher<br/>Bug tracking"]
        WIKI["Documentation Wiki<br/>Pages 1-7<br/>Technical reference"]
    end
    
    subgraph "Code Resources"
        ENV_TEMPLATE[".env.template<br/>Configuration template"]
        README["README.md<br/>Quick start guide"]
        RUN_INFER_PLAN["run_infer_plan.py<br/>Level 1 execution"]
        RUN_INFER_IDEA["run_infer_idea.py<br/>Level 2 execution"]
        WRITING["writing.py<br/>Paper generation"]
        BENCHMARK["benchmark/<br/>Evaluation framework"]
    end
    
    INSTALL --> WECHAT
    INSTALL --> WIKI
    INSTALL -.-> ENV_TEMPLATE
    INSTALL -.-> README
    
    USAGE --> WECHAT
    USAGE --> FEISHU
    USAGE --> WIKI
    USAGE -.-> RUN_INFER_PLAN
    USAGE -.-> RUN_INFER_IDEA
    
    BUG --> GITHUB
    BUG --> WECHAT
    BUG -.-> RUN_INFER_PLAN
    BUG -.-> RUN_INFER_IDEA
    BUG -.-> WRITING
    
    RESEARCH --> FEISHU
    RESEARCH --> WECHAT
    RESEARCH -.-> BENCHMARK
    
    CONTRIB --> GITHUB
    CONTRIB --> FEISHU
    
    WIKI --> README
    WIKI --> ENV_TEMPLATE
```

**Sources:** Communication.md, README.md (inferred from system architecture)

## Getting Help

### Documentation Resources

The system provides comprehensive documentation across multiple wiki pages:

| Topic | Wiki Page | Purpose |
|-------|-----------|---------|
| System Overview | [Overview](#1) | High-level capabilities and architecture |
| Installation | [Installation & Setup](#6.1) | Docker setup, API configuration |
| Configuration | [Environment Configuration](#4.1) | `.env` parameters, LLM settings |
| Level 1 Tasks | [Level 1 Tasks](#6.2) | Running tasks with given ideas |
| Level 2 Tasks | [Level 2 Tasks](#6.3) | Reference-based idea generation |
| Web Interface | [Web Interface](#6.4) | GUI-based operation |
| Benchmarks | [Benchmark System](#3.3) | Evaluation framework usage |

### Common Support Scenarios

#### Installation and Configuration Issues

For problems related to environment setup:

1. Review [.env.template:1-end]() for complete configuration options
2. Check Docker container status and logs
3. Verify API keys for OpenRouter or GitHub AI
4. Consult [Environment Configuration](#4.1) for detailed parameter descriptions
5. Post in WeChat/Feishu group for quick assistance

#### Execution Errors

For errors during research task execution:

1. Check log files generated in the workspace directory
2. Verify task configuration parameters in `.env`
3. Review [Research Agent](#3.1) documentation for expected behavior
4. For Level 1 tasks, examine [run_infer_plan.py:1-end]() execution flow
5. For Level 2 tasks, examine [run_infer_idea.py:1-end]() execution flow
6. Report persistent issues on GitHub with error logs

#### Benchmark Evaluation Questions

For questions about benchmark tasks or evaluation:

1. Review [Benchmark System](#3.3) for framework overview
2. Check specific task documentation:
   - [Diffusion & Flow Matching](#5.1) for generative model tasks
   - [Graph Neural Networks](#5.2) for GNN tasks
   - [Reasoning](#5.3) for LLM reasoning tasks
3. Examine benchmark JSON files in `benchmark/` directory
4. Discuss novel research directions in Feishu group

**Sources:** README.md, .env.template, Communication.md

## Issue Resolution Workflow

```mermaid
graph TB
    START["User Encounters Issue"]
    
    subgraph "Self-Service Diagnosis"
        CHECK_DOCS["Check Wiki Documentation<br/>Pages 1-7"]
        CHECK_ENV["Review .env Configuration<br/>.env.template"]
        CHECK_LOGS["Examine Log Files<br/>workplace_*/*.log"]
        CHECK_README["Consult README.md<br/>Quick start guide"]
    end
    
    subgraph "Community Support"
        WECHAT_POST["Post in WeChat Group<br/>Quick questions"]
        FEISHU_POST["Post in Feishu Group<br/>Detailed discussions"]
    end
    
    subgraph "Official Channels"
        GITHUB_SEARCH["Search GitHub Issues<br/>github.com/HKUDS/AI-Researcher/issues"]
        GITHUB_CREATE["Create GitHub Issue<br/>Bug report template"]
    end
    
    subgraph "Resolution Resources"
        CODE_FIX["Code-level Fix<br/>Modify .py files"]
        CONFIG_FIX["Configuration Fix<br/>Update .env"]
        WORKAROUND["Workaround Solution<br/>Alternative approach"]
        UPSTREAM_FIX["Development Fix<br/>Pull request merged"]
    end
    
    START --> CHECK_DOCS
    CHECK_DOCS --> CHECK_ENV
    CHECK_ENV --> CHECK_LOGS
    CHECK_LOGS --> CHECK_README
    
    CHECK_README --> SOLVED1{"Resolved?"}
    SOLVED1 -->|Yes| END1["Issue Resolved"]
    SOLVED1 -->|No| WECHAT_POST
    
    WECHAT_POST --> SOLVED2{"Resolved?"}
    SOLVED2 -->|Yes| END2["Issue Resolved"]
    SOLVED2 -->|Complex| FEISHU_POST
    SOLVED2 -->|Bug| GITHUB_SEARCH
    
    FEISHU_POST --> SOLVED3{"Resolved?"}
    SOLVED3 -->|Yes| END3["Issue Resolved"]
    SOLVED3 -->|No| GITHUB_SEARCH
    
    GITHUB_SEARCH --> EXISTS{"Issue<br/>Exists?"}
    EXISTS -->|Yes| SUBSCRIBE["Subscribe to Issue<br/>Track progress"]
    EXISTS -->|No| GITHUB_CREATE
    
    GITHUB_CREATE --> TRIAGE["Development Team<br/>Triage and response"]
    
    TRIAGE --> CODE_FIX
    TRIAGE --> CONFIG_FIX
    TRIAGE --> WORKAROUND
    TRIAGE --> UPSTREAM_FIX
    
    CODE_FIX --> END4["Issue Resolved"]
    CONFIG_FIX --> END5["Issue Resolved"]
    WORKAROUND --> END6["Issue Resolved"]
    UPSTREAM_FIX --> END7["Issue Resolved"]
    SUBSCRIBE --> END8["Wait for Fix"]
```

**Sources:** Communication.md, README.md

## Contributing to AI-Researcher

The AI-Researcher project welcomes contributions from the research community. Contributions can take several forms:

### Types of Contributions

| Contribution Type | Description | Process |
|------------------|-------------|---------|
| Bug Fixes | Correct errors in existing code | GitHub pull request |
| Feature Enhancements | Add new capabilities to existing components | Discuss in Feishu → GitHub PR |
| New Benchmarks | Add evaluation tasks to `benchmark/` | Feishu discussion → JSON file |
| Documentation | Improve wiki pages or README | GitHub pull request |
| Research Extensions | Novel research ideas or implementations | Feishu research discussion |

### Contribution Workflow

For code contributions:

1. **Fork** the repository at `https://github.com/HKUDS/AI-Researcher`
2. **Set up** development environment following [Installation & Setup](#6.1)
3. **Discuss** major changes in Feishu group before implementation
4. **Implement** changes with clear code comments
5. **Test** modifications using existing benchmarks
6. **Submit** pull request with detailed description
7. **Respond** to code review feedback

For new benchmark tasks:

1. Study existing benchmark JSON files in `benchmark/` directory
2. Define task following structure of similar benchmarks
3. Create ground truth implementation with documentation
4. Discuss benchmark design in Feishu group
5. Submit JSON file and supporting materials via GitHub

**Sources:** README.md, Communication.md

## Community Engagement Model

```mermaid
graph TB
    subgraph "User Roles"
        RESEARCHER["Research User<br/>Running experiments<br/>Generating papers"]
        DEVELOPER["Developer<br/>Contributing code<br/>Fixing bugs"]
        EVALUATOR["Benchmark User<br/>Evaluating AI research<br/>Comparing methods"]
    end
    
    subgraph "Engagement Activities"
        RUN_TASKS["Execute Research Tasks<br/>run_infer_plan.py<br/>run_infer_idea.py"]
        EVAL_BENCH["Run Benchmarks<br/>benchmark/*.json"]
        DISCUSS["Discuss Results<br/>WeChat/Feishu"]
        REPORT["Report Issues<br/>GitHub Issues"]
        CONTRIBUTE["Submit Code<br/>Pull Requests"]
        SHARE["Share Research<br/>Papers generated"]
    end
    
    subgraph "Development Resources"
        CODEBASE["AI-Researcher Codebase<br/>github.com/HKUDS/AI-Researcher"]
        WIKI_DOCS["Wiki Documentation<br/>Pages 1-7"]
        BENCH_SYSTEM["Inno-Bench Framework<br/>benchmark/"]
        ENV_CONFIG[".env Configuration<br/>.env.template"]
    end
    
    subgraph "Support Ecosystem"
        HKUDS["HKUDS Research Group<br/>Development Team"]
        COMMUNITY["User Community<br/>WeChat + Feishu"]
    end
    
    RESEARCHER --> RUN_TASKS
    RESEARCHER --> EVAL_BENCH
    RESEARCHER --> DISCUSS
    RESEARCHER --> SHARE
    
    DEVELOPER --> CONTRIBUTE
    DEVELOPER --> REPORT
    DEVELOPER --> DISCUSS
    
    EVALUATOR --> EVAL_BENCH
    EVALUATOR --> DISCUSS
    EVALUATOR --> REPORT
    
    RUN_TASKS -.-> CODEBASE
    RUN_TASKS -.-> ENV_CONFIG
    
    EVAL_BENCH -.-> BENCH_SYSTEM
    EVAL_BENCH -.-> WIKI_DOCS
    
    CONTRIBUTE --> CODEBASE
    REPORT --> CODEBASE
    
    DISCUSS --> COMMUNITY
    SHARE --> COMMUNITY
    
    COMMUNITY --> HKUDS
    CODEBASE --> HKUDS
```

**Sources:** Communication.md, README.md

## Research Group Information

### HKUDS (Hong Kong University Data Science)

The AI-Researcher project is developed and maintained by the HKUDS research group. The group focuses on:

- **Autonomous Research Systems**: AI agents for scientific discovery
- **Graph Neural Networks**: Advanced architectures and learning paradigms
- **Generative Modeling**: Diffusion models and flow-based generation
- **Large Language Models**: Reasoning enhancement and instruction tuning

### Academic Context

The AI-Researcher system is part of ongoing research into autonomous scientific innovation. The Inno-Bench evaluation framework represents a significant contribution to measuring AI research capabilities across multiple domains (see [Benchmark System](#3.3)).

Publications and research outputs generated using AI-Researcher should acknowledge the HKUDS research group and cite relevant benchmark tasks from [Benchmark Tasks & Domains](#5).

### Joining the Research Community

To engage with the HKUDS research community:

1. **Join Discussion Groups**: Scan QR codes in [Communication.md:5]() to access WeChat and Feishu groups
2. **Follow GitHub Repository**: Star and watch the repository for updates
3. **Participate in Discussions**: Share research ideas and results in Feishu
4. **Contribute Benchmarks**: Propose new evaluation tasks for Inno-Bench
5. **Collaborate on Research**: Discuss potential research collaborations with the team

**Sources:** Communication.md, README.md

## Quick Reference: Support Contact Matrix

| Issue Type | Primary Channel | Secondary Channel | Response Time |
|------------|----------------|-------------------|---------------|
| Installation Help | WeChat Group | [Installation & Setup](#6.1) | < 24 hours |
| Configuration Questions | WeChat Group | [Environment Configuration](#4.1) | < 24 hours |
| Usage Questions | Feishu Group | [Usage Guide](#6) | < 48 hours |
| Bug Reports | GitHub Issues | WeChat Group | Varies |
| Feature Requests | Feishu Group | GitHub Issues | Discussion-based |
| Research Collaboration | Feishu Group | HKUDS Team | Discussion-based |
| Benchmark Questions | Feishu Group | [Benchmark System](#3.3) | < 48 hours |

**Note**: Response times are approximate and depend on community activity and issue complexity. Critical bugs affecting system stability receive priority attention.

**Sources:** Communication.md

## Additional Resources

### External Links

- **GitHub Repository**: https://github.com/HKUDS/AI-Researcher
- **HKUDS Profile**: https://github.com/HKUDS/.github/blob/main/profile/QR.png (QR codes)
- **Docker Image**: tjbtech1/airesearcher:v1

### Related Documentation

- [Overview](#1) - System introduction and capabilities
- [System Architecture](#2) - Technical architecture overview
- [Usage Guide](#6) - Practical usage instructions
- [Benchmark Tasks & Domains](#5) - Research domain coverage

**Sources:** Communication.md, README.md, .env.template