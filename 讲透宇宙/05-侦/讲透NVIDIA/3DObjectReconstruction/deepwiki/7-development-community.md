<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/3DObjectReconstruction · page 7 Development & Community · fetched 2026-10-26 -->

# Development & Community

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)

</details>



This document provides an overview of the development process, community governance, and contribution pathways for the NVIDIA 3D Object Reconstruction project. It covers the organizational structure, communication channels, and policies that guide community participation.

For detailed contribution procedures, see [Contributing Guidelines](#7.1). For bug reporting and support, see [Issue Templates & Support](#7.2). For security policies and licensing information, see [Security & Licensing](#7.3).

## Project Governance

The NVIDIA 3D Object Reconstruction project follows an open-source development model with NVIDIA maintaining primary stewardship. The project welcomes community contributions while maintaining quality standards and technical direction alignment with NVIDIA's research objectives.

### Community Structure

```mermaid
graph TB
    subgraph "NVIDIA Core Team"
        MAINTAINERS["Project Maintainers<br/>(Code Review & Merge Authority)"]
        LEADS["Project Leads<br/>(Technical Direction)"]
    end
    
    subgraph "Community Contributors"
        CONTRIBUTORS["Active Contributors<br/>(Regular Code Submissions)"]
        OCCASIONAL["Occasional Contributors<br/>(Bug Fixes, Documentation)"]
        USERS["End Users<br/>(Issue Reporting, Feedback)"]
    end
    
    subgraph "Communication Channels"
        GITHUB_ISSUES["GitHub Issues<br/>(github.com/NVIDIA/3DObjectReconstruction/issues)"]
        GITHUB_DISCUSSIONS["GitHub Discussions<br/>(Feature Requests, Q&A)"]
        PR_REVIEWS["Pull Request Reviews<br/>(Code Review Process)"]
    end
    
    LEADS --> MAINTAINERS
    MAINTAINERS --> PR_REVIEWS
    CONTRIBUTORS --> GITHUB_ISSUES
    CONTRIBUTORS --> PR_REVIEWS
    OCCASIONAL --> GITHUB_ISSUES
    USERS --> GITHUB_ISSUES
    USERS --> GITHUB_DISCUSSIONS
    
    MAINTAINERS --> CONTRIBUTORS
    CONTRIBUTORS --> OCCASIONAL
```

**Sources:** [CODE_OF_CONDUCT.md:42-53](), [CONTRIBUTING.md:1-22]()

## Development Workflow

The project follows a structured development process that integrates with the existing codebase architecture and deployment systems.

### Contribution Process Flow

```mermaid
flowchart TD
    subgraph "Issue Identification"
        ISSUE_TYPES["GitHub Issue Types<br/>- Bug Reports<br/>- Feature Requests<br/>- Documentation"]
        ENV_SCRIPT["print_env.sh<br/>(Environment Diagnostics)"]
        LABELS["Issue Labels<br/>- good first issue<br/>- help wanted<br/>- breaking/non-breaking"]
    end
    
    subgraph "Development Phase"
        BRANCH_NAMING["Branch Naming Convention<br/>- fea-feature-name<br/>- enh-enhancement-name<br/>- bug-fix-name"]
        CODE_CHANGES["Code Implementation<br/>- Core Changes<br/>- Unit Tests<br/>- Integration Validation"]
        DEMO_VALIDATION["Demo Validation<br/>3d_object_reconstruction_demo.ipynb"]
    end
    
    subgraph "Review & Integration"
        PR_CREATION["Pull Request Creation<br/>(github.com/nvidia/3DObjectReconstruction/compare)"]
        PR_LABELS["PR Labeling<br/>- breaking/non-breaking<br/>- feature/improvement/bugfix"]
        CODE_REVIEW["Code Review Process<br/>(NVIDIA Team + Community)"]
        MERGE_APPROVAL["Merge Approval<br/>(Maintainer Authority)"]
    end
    
    ISSUE_TYPES --> ENV_SCRIPT
    ENV_SCRIPT --> LABELS
    LABELS --> BRANCH_NAMING
    BRANCH_NAMING --> CODE_CHANGES
    CODE_CHANGES --> DEMO_VALIDATION
    DEMO_VALIDATION --> PR_CREATION
    PR_CREATION --> PR_LABELS
    PR_LABELS --> CODE_REVIEW
    CODE_REVIEW --> MERGE_APPROVAL
```

**Sources:** [CONTRIBUTING.md:6-35](), [CONTRIBUTING.md:39-59]()

## Code Quality Standards

The project maintains specific standards for code contributions that align with the existing architecture and AI pipeline components.

### Technical Requirements

| Requirement Category | Standards | Validation Method |
|---------------------|-----------|-------------------|
| **Code Integration** | Must integrate with `NVBundleSDF` framework | Unit tests + integration validation |
| **Demo Compatibility** | Must work with default inference example | Manual testing with demo notebook |
| **Documentation** | All public APIs must be documented | Code review verification |
| **Testing** | Unit tests for new functionality | Automated test execution |
| **Configuration** | Follow existing schema patterns in `src/nvidia/objectreconstruction/configs/` | Schema validation |

### Breaking Change Policy

The project categorizes changes as "breaking" or "non-breaking" using GitHub labels. Breaking changes are those that modify the codebase in a non-backward-compatible way, particularly affecting:

- Public API interfaces in `NVBundleSDF` class
- Configuration schema changes in `schema.py`
- Changes to data loader interfaces in `ReconstructionDataLoader`
- Modifications to the main pipeline workflow

**Sources:** [CONTRIBUTING.md:41-46]()

## Community Standards

The project operates under the Contributor Covenant Code of Conduct, establishing standards for inclusive and professional community interaction.

### Code of Conduct Framework

```mermaid
graph LR
    subgraph "Community Standards"
        POSITIVE["Positive Behaviors<br/>- Inclusive Language<br/>- Respectful Dialogue<br/>- Constructive Criticism<br/>- Community Focus<br/>- Empathy"]
        UNACCEPTABLE["Unacceptable Behaviors<br/>- Harassment<br/>- Personal Attacks<br/>- Privacy Violations<br/>- Inappropriate Conduct"]
    end
    
    subgraph "Enforcement Structure"
        MAINTAINER_RESPONSIBILITY["Maintainer Responsibilities<br/>- Standards Clarification<br/>- Corrective Action<br/>- Content Moderation"]
        REPORTING["Conduct Reporting<br/>GitHub_Conduct@nvidia.com"]
        CONSEQUENCES["Enforcement Actions<br/>- Content Removal<br/>- Temporary Ban<br/>- Permanent Ban"]
    end
    
    POSITIVE --> MAINTAINER_RESPONSIBILITY
    UNACCEPTABLE --> REPORTING
    REPORTING --> MAINTAINER_RESPONSIBILITY
    MAINTAINER_RESPONSIBILITY --> CONSEQUENCES
```

**Sources:** [CODE_OF_CONDUCT.md:11-40](), [CODE_OF_CONDUCT.md:64-71]()

## Security and Vulnerability Reporting

The project maintains a comprehensive security policy for reporting vulnerabilities and security concerns.

### Security Reporting Process

Security vulnerabilities should **never** be reported through GitHub issues. Instead, use designated NVIDIA security channels:

| Contact Method | Details | Use Case |
|----------------|---------|----------|
| **Web Form** | [NVIDIA Security Vulnerability Submission](https://www.nvidia.com/object/submit-security-vulnerability.html) | Standard vulnerability reporting |
| **Email** | `psirt@nvidia.com` | Direct security team contact |
| **PGP Encrypted Email** | Use [NVIDIA PGP Key](https://www.nvidia.com/en-us/security/pgp-key) | Sensitive vulnerability details |

### Required Vulnerability Information

When reporting security issues, include:
- Product/Driver name and version/branch containing vulnerability
- Vulnerability type (code execution, denial of service, buffer overflow, etc.)
- Reproduction instructions
- Proof-of-concept or exploit code
- Potential impact assessment

**Sources:** [SECURITY.md:5-19]()

## Support Channels

The project provides multiple channels for community support and engagement:

### Primary Support Matrix

| Channel Type | Platform | Purpose | Response Time |
|-------------|----------|---------|---------------|
| **Bug Reports** | GitHub Issues | Technical issues, bugs | Community + maintainer triage |
| **Feature Requests** | GitHub Issues | New functionality proposals | Design discussion required |
| **Documentation Issues** | GitHub Issues | Docs improvements, clarifications | Community contributions welcome |
| **General Questions** | GitHub Discussions | Usage questions, troubleshooting | Community-driven responses |
| **Security Issues** | `psirt@nvidia.com` | Vulnerability reporting | Coordinated disclosure process |
| **Conduct Issues** | `GitHub_Conduct@nvidia.com` | Code of conduct violations | Confidential investigation |

### Environment Diagnostics

For bug reports, contributors should run the environment diagnostic script to gather relevant system information:

```bash
./3DObjectReconstruction/print_env.sh
```

This script captures system configuration details that help maintainers reproduce and diagnose issues effectively.

**Sources:** [CONTRIBUTING.md:6-12](), [SECURITY.md:1-24](), [CODE_OF_CONDUCT.md:64-71]()

---

