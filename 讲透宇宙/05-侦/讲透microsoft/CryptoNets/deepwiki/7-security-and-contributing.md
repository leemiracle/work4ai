<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CryptoNets · page 7 Security and Contributing · fetched 2026-10-26 -->

# Security and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [SECURITY.md](SECURITY.md)

</details>



This document covers security policies and guidelines for contributing to the CryptoNets project. It outlines the vulnerability reporting process, license terms, and general contribution workflows. For information about the testing framework used to validate contributions, see [Testing Framework](#5.1). For details about build configuration and project structure, see [Build Configuration](#5.2).

## Security Vulnerability Reporting

Microsoft takes security seriously across all repositories, including CryptoNets. The project follows Microsoft's standard security response procedures for vulnerability disclosure and remediation.

### Reporting Process

Security vulnerabilities should **never** be reported through public GitHub issues. Instead, all security issues must be reported through the Microsoft Security Response Center (MSRC) using one of the following methods:

| Method | Contact | Notes |
|--------|---------|--------|
| Web Portal | https://msrc.microsoft.com/create-report | Preferred method with tracking |
| Email | secure@microsoft.com | Alternative for users who prefer not to log in |
| PGP Encrypted Email | secure@microsoft.com | Use Microsoft's PGP key for sensitive reports |

The security team commits to responding within 24 hours of receiving a report. If no response is received within this timeframe, follow up via email to ensure the original message was received.

### Required Information

When reporting a security vulnerability, include as much of the following information as possible to help with triage and resolution:

- **Issue Type**: Buffer overflow, injection vulnerability, cryptographic weakness, etc.
- **Affected Files**: Full paths to source files related to the issue
- **Source Location**: Specific tag, branch, commit, or direct URL
- **Reproduction Steps**: Detailed step-by-step instructions
- **Configuration**: Any special setup required to reproduce the issue
- **Proof of Concept**: Exploit code or demonstration (if available)
- **Impact Assessment**: How an attacker might exploit the vulnerability

### Security Reporting Workflow

```mermaid
flowchart TD
    A[Developer/Researcher Discovers Vulnerability] --> B{Is it in CryptoNets Repository?}
    B -->|Yes| C[Gather Required Information]
    B -->|No| D[Report to Appropriate Team]
    
    C --> E[Choose Reporting Method]
    E --> F[MSRC Web Portal]
    E --> G[Email to secure@microsoft.com]
    E --> H[PGP Encrypted Email]
    
    F --> I[MSRC Receives Report]
    G --> I
    H --> I
    
    I --> J[Response Within 24 Hours]
    J --> K[Vulnerability Assessment]
    K --> L[Coordinated Vulnerability Disclosure]
    L --> M[Patch Development]
    M --> N[Security Advisory Published]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333,stroke-width:2px
    style N fill:#bfb,stroke:#333,stroke-width:2px
```

**Sources**: [SECURITY.md:1-42]()

### Bug Bounty Program

Security researchers may be eligible for rewards through Microsoft's Bug Bounty Program. More complete and detailed vulnerability reports can contribute to higher bounty awards. The program covers qualifying vulnerabilities found in Microsoft-owned repositories.

## Contributing Guidelines

CryptoNets is an open-source project released under the MIT License. Contributors must understand the licensing terms and follow standard open-source contribution practices.

### License Requirements

The project uses the MIT License with Microsoft Corporation holding the copyright. All contributions become part of the licensed codebase under these terms:

- **Permission Granted**: Use, modify, publish, distribute, sublicense, and sell
- **Conditions**: Include copyright notice and license in all copies
- **Limitations**: No warranty provided; no liability assumed by Microsoft

### Contribution Workflow

```mermaid
flowchart TD
    A[Contributor Identifies Issue/Enhancement] --> B[Fork Repository]
    B --> C[Create Feature Branch]
    C --> D[Implement Changes]
    
    D --> E[Local Testing]
    E --> F{Tests Pass?}
    F -->|No| G[Fix Issues]
    G --> E
    F -->|Yes| H[Run NeuralNetworksTest Suite]
    
    H --> I{All Tests Pass?}
    I -->|No| J[Debug Test Failures]
    J --> G
    I -->|Yes| K[Submit Pull Request]
    
    K --> L[Code Review]
    L --> M{Review Approved?}
    M -->|No| N[Address Feedback]
    N --> L
    M -->|Yes| O[Merge to Main Branch]
    
    subgraph TestSuites[Test Validation]
        P[LayersTest]
        Q[CaltechTests] 
        R[TestNetwork]
        S[BasicOperations]
    end
    
    H --> P
    H --> Q
    H --> R
    H --> S
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style O fill:#bfb,stroke:#333,stroke-width:2px
    style TestSuites fill:#ffd,stroke:#333,stroke-width:2px
```

**Sources**: [LICENSE:1-22]()

### Code Quality Standards

Contributors should ensure their changes maintain the existing code quality and testing standards:

| Component | Test Project | Key Test Classes |
|-----------|--------------|------------------|
| Neural Networks | NeuralNetworksTest | `LayersTest`, `TestNetwork` |
| HE Operations | HE Wrapper Tests | `BasicOperations`, `BudgetAnalysis` |
| Dataset Processing | Integration Tests | `CaltechTests` |

### Codebase Integration Points

Understanding the major components helps contributors identify where their changes fit within the system architecture:

```mermaid
graph TB
    subgraph Core["Core Libraries"]
        HEWrapper["HE Wrapper<br/>IFactory Interface<br/>EncryptedSealBfvFactory"]
        NeuralNets["NeuralNetworks<br/>Layer Implementations<br/>Base Framework"]
    end
    
    subgraph Apps["Applications"]
        BasicExample["BasicExample.exe<br/>HE Operations Demo"]
        CryptoNets["CryptoNets.exe<br/>Original Implementation"]
        LowLatency["LowLatencyCryptoNets.exe<br/>LoLa Variants"]
        CifarCrypto["CifarCryptoNets.exe<br/>CIFAR-10 Implementation"]
        Caltech["Caltech101.exe<br/>CalTech-101 Implementation"]
    end
    
    subgraph Data["Data Pipeline"]
        DataPreprocess["DataPreprocess.exe<br/>ML.NET Pipeline"]
        GetMNIST["GetMNIST.cs"]
        GetCIFAR["GetCIFAR.cs"]
        GetCAL["GetCAL.cs"]
    end
    
    subgraph Tests["Test Suites"]
        NeuralNetTest["NeuralNetworksTest<br/>MSTest Framework"]
        LayersTest["LayersTest.cs"]
        CaltechTests["CaltechTests.cs"]
        TestNetwork["TestNetwork.cs"]
    end
    
    HEWrapper --> BasicExample
    HEWrapper --> CryptoNets
    HEWrapper --> LowLatency
    HEWrapper --> CifarCrypto
    HEWrapper --> Caltech
    
    NeuralNets --> CryptoNets
    NeuralNets --> LowLatency
    NeuralNets --> CifarCrypto
    NeuralNets --> Caltech
    
    DataPreprocess --> Apps
    GetMNIST --> DataPreprocess
    GetCIFAR --> DataPreprocess
    GetCAL --> DataPreprocess
    
    NeuralNetTest --> NeuralNets
    LayersTest --> NeuralNetTest
    CaltechTests --> NeuralNetTest
    TestNetwork --> NeuralNetTest
```

**Sources**: Project structure analysis

## Legal and Compliance

### Copyright Notice

All source code in the CryptoNets repository is copyrighted by Microsoft Corporation. The copyright notice must be preserved in all derivative works and distributions.

### License Terms Summary

| Aspect | Requirement |
|--------|-------------|
| **Usage** | Free for any purpose including commercial use |
| **Modification** | Permitted with copyright notice preservation |
| **Distribution** | Allowed with license inclusion |
| **Sublicensing** | Permitted under same terms |
| **Warranty** | None provided - software used "as is" |
| **Liability** | Microsoft assumes no liability for damages |

### Vulnerability Disclosure Policy

Microsoft follows the principle of **Coordinated Vulnerability Disclosure (CVD)**. This means:

- Security issues are disclosed responsibly
- Sufficient time is provided for patches before public disclosure
- Credit is given to security researchers following responsible disclosure
- Public disclosure includes sufficient detail for users to assess risk

**Sources**: [SECURITY.md:39](), [LICENSE:1-22]()

---

