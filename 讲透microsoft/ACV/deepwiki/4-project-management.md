<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ACV · page 4 Project Management · fetched 2026-10-26 -->

# Project Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SUPPORT.md](SUPPORT.md)

</details>



## Purpose and Scope

This document covers the repository governance, community guidelines, and development policies for the Microsoft ACV (Autonomic Computing Vision) repository. It addresses how contributors and users should interact with the project, report issues, seek support, and maintain community standards.

For technical implementation details of the self-managing systems, see [Self-Managing Systems](#2). For information about the OSrCIR research implementation, see [OSrCIR System](#3).

## Repository Governance Structure

The ACV repository follows Microsoft's open source governance model, with clearly defined policies for community interaction and support processes.

### Governance Framework

```mermaid
graph TB
    subgraph "Microsoft ACV Repository Governance"
        REPO["ACV Repository<br/>github.com/microsoft/ACV"]
        
        subgraph "Governance Files"
            SUPPORT["SUPPORT.md<br/>Issue Filing & Help"]
            COC["CODE_OF_CONDUCT.md<br/>Community Standards"]
            LICENSE["LICENSE<br/>MIT License"]
            SECURITY["SECURITY.md<br/>Vulnerability Reporting"]
        end
        
        subgraph "Contact Points"
            PRIMARY["v-zhiyzhang@microsoft.com<br/>Primary Support Contact"]
            OPENCODE["opencode@microsoft.com<br/>Code of Conduct Issues"]
            GITHUB_ISSUES["GitHub Issues<br/>Bug Reports & Features"]
        end
        
        subgraph "External Policies"
            MS_COC["Microsoft Open Source<br/>Code of Conduct"]
            MS_SUPPORT["Microsoft Support Policy<br/>Limited Resources"]
        end
    end
    
    REPO --> SUPPORT
    REPO --> COC
    REPO --> LICENSE
    REPO --> SECURITY
    
    SUPPORT --> PRIMARY
    SUPPORT --> GITHUB_ISSUES
    COC --> OPENCODE
    COC --> MS_COC
    SUPPORT --> MS_SUPPORT
```

**Sources:** [SUPPORT.md:1-14](), [CODE_OF_CONDUCT.md:1-10]()

## Community Management Process

The repository implements a structured approach to community management through standardized files and clear escalation paths.

### Issue Management and Support Flow

```mermaid
graph TD
    subgraph "User Support Process"
        USER["Repository User<br/>Developer/Researcher"]
        SEARCH["Search Existing Issues<br/>GitHub Issues Tab"]
        NEW_ISSUE["File New Issue<br/>Bug or Feature Request"]
        EMAIL_SUPPORT["Email Support<br/>v-zhiyzhang@microsoft.com"]
        
        subgraph "Issue Types"
            BUG["Bug Report<br/>Technical Issues"]
            FEATURE["Feature Request<br/>Enhancement Ideas"]
            QUESTION["Usage Questions<br/>Help Requests"]
        end
        
        subgraph "Resolution Paths"
            COMMUNITY["Community Response<br/>GitHub Discussion"]
            MAINTAINER["Maintainer Response<br/>Direct Email"]
            COC_VIOLATION["Code of Conduct<br/>opencode@microsoft.com"]
        end
    end
    
    USER --> SEARCH
    SEARCH --> NEW_ISSUE
    USER --> EMAIL_SUPPORT
    
    NEW_ISSUE --> BUG
    NEW_ISSUE --> FEATURE
    EMAIL_SUPPORT --> QUESTION
    
    BUG --> COMMUNITY
    FEATURE --> COMMUNITY
    QUESTION --> MAINTAINER
    
    COMMUNITY --> COC_VIOLATION
    MAINTAINER --> COC_VIOLATION
```

**Sources:** [SUPPORT.md:3-7](), [SUPPORT.md:9-9](), [CODE_OF_CONDUCT.md:9-9]()

## Support Policy and Resources

The repository operates under Microsoft's limited support model for open source projects, with specific resources available for different types of assistance.

### Support Matrix

| Support Type | Resource | Contact Method | Response Expectation |
|--------------|----------|----------------|---------------------|
| Bug Reports | GitHub Issues | [GitHub Issues]() | Community-driven |
| Feature Requests | GitHub Issues | [GitHub Issues]() | Community-driven |
| Usage Questions | Direct Email | `v-zhiyzhang@microsoft.com` | Best effort |
| Code of Conduct Issues | Microsoft OpenCode | `opencode@microsoft.com` | Formal process |
| Security Vulnerabilities | Security Policy | See [Security and Legal](#4.2) | Coordinated disclosure |

**Sources:** [SUPPORT.md:3-14](), [CODE_OF_CONDUCT.md:9-9]()

## Code of Conduct Enforcement

The repository adheres to the Microsoft Open Source Code of Conduct, providing clear guidelines for community behavior and enforcement mechanisms.

### Behavioral Standards Framework

```mermaid
graph LR
    subgraph "Code of Conduct Implementation"
        ADOPTION["Microsoft Open Source<br/>Code of Conduct Adoption"]
        
        subgraph "Reference Resources"
            MAIN_COC["opensource.microsoft.com/<br/>codeofconduct/"]
            FAQ["Microsoft Code of<br/>Conduct FAQ"]
            CONTACT["opencode@microsoft.com<br/>Questions & Concerns"]
        end
        
        subgraph "Repository Integration"
            COC_FILE["CODE_OF_CONDUCT.md<br/>Local Reference"]
            ISSUE_TEMPLATE["GitHub Issue Templates<br/>COC Reporting"]
            COMMUNITY_HEALTH["GitHub Community<br/>Health Score"]
        end
        
        subgraph "Enforcement Actions"
            WARNING["Warning<br/>First Violation"]
            TEMPORARY["Temporary Ban<br/>Repeated Issues"]
            PERMANENT["Permanent Ban<br/>Severe Violations"]
        end
    end
    
    ADOPTION --> MAIN_COC
    ADOPTION --> FAQ
    ADOPTION --> CONTACT
    
    MAIN_COC --> COC_FILE
    FAQ --> COC_FILE
    CONTACT --> COC_FILE
    
    COC_FILE --> ISSUE_TEMPLATE
    COC_FILE --> COMMUNITY_HEALTH
    
    CONTACT --> WARNING
    CONTACT --> TEMPORARY
    CONTACT --> PERMANENT
```

**Sources:** [CODE_OF_CONDUCT.md:1-10]()

## Development Policies

The repository maintains clear policies for development contributions and community engagement, ensuring consistency with Microsoft's open source standards.

### Policy Implementation Structure

| Policy Area | Implementation File | Key Requirements |
|-------------|-------------------|------------------|
| Community Behavior | `CODE_OF_CONDUCT.md` | Microsoft Open Source standards |
| Support Procedures | `SUPPORT.md` | GitHub Issues, email escalation |
| Legal Framework | `LICENSE` | MIT License terms |
| Security Reporting | `SECURITY.md` | Vulnerability disclosure process |

The project management framework ensures that:

1. **Issue Tracking**: All bugs and features are managed through GitHub Issues with duplicate prevention
2. **Community Standards**: Behavior is governed by Microsoft's established code of conduct
3. **Support Escalation**: Clear pathways exist for different types of assistance
4. **Legal Compliance**: Proper licensing and security policies are maintained

For detailed information about support procedures and community guidelines, see [Support and Community Guidelines](#4.1). For security policies and legal frameworks, see [Security and Legal](#4.2).

**Sources:** [SUPPORT.md:1-14](), [CODE_OF_CONDUCT.md:1-10]()

---

