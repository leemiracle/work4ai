<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RepDL · page 7 Community and Support · fetched 2026-10-26 -->

# Community and Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SUPPORT.md](SUPPORT.md)

</details>



## Purpose and Scope

This section provides information about the RepDL community, support resources, and contribution processes. It covers where to get help when using RepDL, how to report issues, security vulnerability reporting, and the project's governance policies.

For technical guides on extending RepDL with custom operations or layers, see [Development Guide](#6). For API documentation, see [API Reference](#4).

---

## Overview

RepDL is an open-source project hosted on GitHub under the Microsoft organization. Community support is structured around GitHub's collaboration features, with clear channels for different types of interactions. The project follows Microsoft's open-source policies including the Microsoft Open Source Code of Conduct and standard security reporting procedures.

Sources: [SUPPORT.md:1-12](), [CODE_OF_CONDUCT.md:1-10]()

---

## Support Resources Structure

```mermaid
graph TB
    User["RepDL User"]
    
    subgraph "Primary Support Channels"
        Issues["GitHub Issues<br/>github.com/microsoft/RepDL/issues<br/>(Bug reports & feature requests)"]
        Discussions["GitHub Discussions<br/>github.com/microsoft/RepDL/discussions<br/>(Questions & help)"]
    end
    
    subgraph "Governance Documents"
        CoC["CODE_OF_CONDUCT.md<br/>Microsoft Open Source Code of Conduct"]
        Support["SUPPORT.md<br/>Support policy & channels"]
        Security["SECURITY.md<br/>Vulnerability reporting"]
        License["LICENSE<br/>MIT License terms"]
    end
    
    subgraph "Microsoft Resources"
        MSOC["Microsoft Open Source Code of Conduct<br/>opensource.microsoft.com/codeofconduct"]
        MSRC["Microsoft Security Response Center<br/>secure@microsoft.com"]
    end
    
    User -->|"Has bug or feature request"| Issues
    User -->|"Has usage question"| Discussions
    User -->|"Wants to contribute"| CoC
    User -->|"Needs support info"| Support
    User -->|"Found security issue"| Security
    User -->|"Checks license terms"| License
    
    CoC -.->|"Links to"| MSOC
    Security -.->|"Reports to"| MSRC
    
    style Issues fill:#f0f0f0
    style Discussions fill:#f0f0f0
    style CoC fill:#e8e8e8
    style Support fill:#e8e8e8
    style Security fill:#e8e8e8
    style License fill:#e8e8e8
```

**Support Channel Decision Tree**

The RepDL project uses different channels for different types of interactions:

| User Need | Channel | GitHub Location | Document Reference |
|-----------|---------|-----------------|-------------------|
| Report a bug | GitHub Issues | `github.com/microsoft/RepDL/issues` | [SUPPORT.md:5]() |
| Request a feature | GitHub Issues | `github.com/microsoft/RepDL/issues` | [SUPPORT.md:5]() |
| Ask usage questions | GitHub Discussions | `github.com/microsoft/RepDL/discussions` | [SUPPORT.md:7]() |
| Report security vulnerability | Microsoft Security Response Center | `secure@microsoft.com` | See [Security](#7.3) |
| Understand contribution rules | Code of Conduct | `CODE_OF_CONDUCT.md` | See [Contributing](#7.2) |
| Check license terms | MIT License | `LICENSE` | See [License](#7.4) |

Sources: [SUPPORT.md:1-12]()

---

## Issue and Discussion Workflow

```mermaid
flowchart TD
    Start["User encounters issue<br/>or has question"]
    
    Question{"What type<br/>of interaction?"}
    
    Bug["Bug: Unexpected behavior<br/>or error in RepDL"]
    Feature["Feature: Missing functionality<br/>or enhancement idea"]
    Usage["Question: How to use<br/>RepDL or troubleshooting"]
    Security["Security: Potential<br/>vulnerability"]
    
    SearchIssues["Search existing Issues<br/>github.com/microsoft/RepDL/issues"]
    SearchDiscussions["Search existing Discussions<br/>github.com/microsoft/RepDL/discussions"]
    
    IssueExists{"Issue already<br/>exists?"}
    DiscussionExists{"Discussion already<br/>exists?"}
    
    NewIssue["File new Issue<br/>Include: Steps to reproduce<br/>Expected vs actual behavior<br/>Environment details"]
    NewDiscussion["Start new Discussion<br/>Include: Use case<br/>Code example<br/>What you tried"]
    
    Subscribe["Subscribe to existing<br/>issue/discussion<br/>Add context if helpful"]
    
    MSRC["Report to Microsoft Security<br/>Response Center (MSRC)<br/>secure@microsoft.com"]
    
    Start --> Question
    
    Question -->|"Bug"| Bug
    Question -->|"Feature Request"| Feature
    Question -->|"Usage Question"| Usage
    Question -->|"Security Issue"| Security
    
    Bug --> SearchIssues
    Feature --> SearchIssues
    Usage --> SearchDiscussions
    Security --> MSRC
    
    SearchIssues --> IssueExists
    SearchDiscussions --> DiscussionExists
    
    IssueExists -->|"Yes"| Subscribe
    IssueExists -->|"No"| NewIssue
    
    DiscussionExists -->|"Yes"| Subscribe
    DiscussionExists -->|"No"| NewDiscussion
```

**Key Workflow Principles:**

1. **Search Before Filing**: Users should search existing issues and discussions before creating new ones to avoid duplicates [SUPPORT.md:5]().

2. **Channel Separation**: Bugs and features use GitHub Issues, while questions use GitHub Discussions [SUPPORT.md:5-7]().

3. **Security Exception**: Security vulnerabilities bypass public channels and go directly to Microsoft Security Response Center (see [Security](#7.3)).

Sources: [SUPPORT.md:1-12]()

---

## Microsoft Support Policy

RepDL follows Microsoft's standard support policy for open-source projects:

**Limited Support Scope**: Support for RepDL is limited to the resources listed in [SUPPORT.md:11]():
- GitHub Issues for bugs and feature requests
- GitHub Discussions for usage questions

**No Commercial Support**: RepDL does not include commercial Microsoft support agreements. Users rely on community support and Microsoft's open-source team responses.

**Best Effort Assistance**: The RepDL team and community provide assistance on a best-effort basis without service level agreements (SLAs).

| Support Type | Available? | Channel |
|--------------|-----------|---------|
| Bug fixes | Yes (best effort) | GitHub Issues |
| Feature requests | Yes (review and prioritization) | GitHub Issues |
| Usage questions | Yes (community + maintainers) | GitHub Discussions |
| Commercial SLA | No | N/A |
| Phone support | No | N/A |
| Email support | No | N/A |

Sources: [SUPPORT.md:9-11]()

---

## Code of Conduct

RepDL has adopted the Microsoft Open Source Code of Conduct. All community members are expected to follow these guidelines when interacting in issues, discussions, pull requests, and other community spaces.

**Key Resources:**
- Primary document: [CODE_OF_CONDUCT.md:1-10]()
- Full code: [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct)
- FAQ: [Microsoft Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq)
- Contact: `opencode@microsoft.com` for questions or concerns [CODE_OF_CONDUCT.md:9]()

**Core Principles:**
- Be respectful and inclusive
- Assume good intentions
- Focus on constructive collaboration
- Follow community guidelines in all interactions

For detailed contribution guidelines including the Contributor License Agreement (CLA) requirement, see [Contributing](#7.2).

Sources: [CODE_OF_CONDUCT.md:1-10]()

---

## Repository File Organization

```mermaid
graph LR
    subgraph "Repository Root: microsoft/RepDL"
        README["README.md<br/>Project overview<br/>Quick start"]
        
        subgraph "Community Documents"
            SUPPORT_FILE["SUPPORT.md<br/>Support channels<br/>Issue filing"]
            COC_FILE["CODE_OF_CONDUCT.md<br/>Community standards"]
            SECURITY_FILE["SECURITY.md<br/>Vulnerability reporting"]
            LICENSE_FILE["LICENSE<br/>MIT license text"]
            CONTRIBUTING["CONTRIBUTING.md<br/>Contribution guide<br/>CLA process"]
        end
        
        subgraph "Source Code"
            REPDL["repdl/<br/>Python package"]
            BACKEND["backend/<br/>C++ and CUDA"]
            EXAMPLES["examples/<br/>MNIST demo"]
        end
    end
    
    README -->|"Links to"| SUPPORT_FILE
    README -->|"Links to"| CONTRIBUTING
    
    SUPPORT_FILE -->|"References"| COC_FILE
    CONTRIBUTING -->|"References"| COC_FILE
    CONTRIBUTING -->|"References"| LICENSE_FILE
    SECURITY_FILE -->|"Reports to"| MSRC_CONTACT["secure@microsoft.com"]
```

**Document Hierarchy:**

1. **Entry Point**: `README.md` provides project overview and links to support resources
2. **Support Layer**: `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` define community policies
3. **Legal**: `LICENSE` and CLA requirements in `CONTRIBUTING.md`
4. **Source Code**: Implementation in `repdl/` and `backend/` directories

Sources: [SUPPORT.md:1-12](), [CODE_OF_CONDUCT.md:1-10]()

---

## Related Pages

This section provides an overview of community and support resources. For specific topics:

- **Getting Help**: Detailed guide on filing issues and using discussions → [Getting Help](#7.1)
- **Contributing**: Contribution process, CLA requirements, and PR guidelines → [Contributing](#7.2)
- **Security**: Vulnerability reporting procedures and MSRC contact → [Security](#7.3)
- **License**: MIT license terms and usage permissions → [License](#7.4)

For technical development information:
- **Adding Custom Operations**: Extending RepDL with new operations → [Adding Custom Operations](#6.1)
- **Development Guide**: Complete guide for contributors → [Development Guide](#6)

---

## Quick Reference Card

```mermaid
graph TD
    Question["I need to..."]
    
    Q1["Report a bug"]
    Q2["Ask how to use RepDL"]
    Q3["Request a feature"]
    Q4["Report a security issue"]
    Q5["Contribute code"]
    Q6["Understand license"]
    
    A1["GitHub Issues<br/>github.com/microsoft/RepDL/issues<br/>Search first, then file new issue"]
    A2["GitHub Discussions<br/>github.com/microsoft/RepDL/discussions<br/>Search first, then ask"]
    A3["GitHub Issues<br/>github.com/microsoft/RepDL/issues<br/>Describe use case and requirements"]
    A4["Microsoft Security Response Center<br/>secure@microsoft.com<br/>Private disclosure"]
    A5["Read CONTRIBUTING.md<br/>Sign CLA<br/>Submit pull request"]
    A6["Read LICENSE file<br/>MIT License - permissive"]
    
    Question --> Q1
    Question --> Q2
    Question --> Q3
    Question --> Q4
    Question --> Q5
    Question --> Q6
    
    Q1 --> A1
    Q2 --> A2
    Q3 --> A3
    Q4 --> A4
    Q5 --> A5
    Q6 --> A6
    
    style A1 fill:#f0f0f0
    style A2 fill:#f0f0f0
    style A3 fill:#f0f0f0
    style A4 fill:#f0f0f0
    style A5 fill:#f0f0f0
    style A6 fill:#f0f0f0
```

Sources: [SUPPORT.md:1-12](), [CODE_OF_CONDUCT.md:1-10]()

---

