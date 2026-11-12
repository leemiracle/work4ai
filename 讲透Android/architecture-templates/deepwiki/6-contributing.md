<!-- source: DeepWiki mcp.deepwiki.com · repo android/architecture-templates · page 6 Contributing · fetched 2026-10-23 -->

# Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This document outlines the process and guidelines for contributing to the Android Architecture Starter Templates repository. It covers the legal requirements, contribution workflow, coding standards, and pull request process. For information about using the templates in your own projects, see [Getting Started](#4).

## Prerequisites

Before contributing to the Android Architecture Templates repository, you need to complete some legal requirements by signing a Contributor License Agreement (CLA).

### Contributor License Agreements

Google requires all contributors to sign a Contributor License Agreement before accepting contributions:

- **Individual contributors**: If you're writing original source code and own the intellectual property, sign the [individual CLA]() (external link).
- **Corporate contributors**: If you're contributing on behalf of your company, sign the [corporate CLA]() (external link).

After signing the appropriate CLA, you'll be able to submit pull requests to the repository.

Sources: [CONTRIBUTING.md:3-18]()

## Contribution Workflow

The following diagram illustrates the standard workflow for contributing to the repository:

```mermaid
flowchart TD
    A["Identify issue/improvement"] --> B["Submit issue describing proposed change"]
    B --> C["Receive response from repo owner"]
    C --> D["Sign CLA if not already done"]
    D --> E["Fork repository"]
    E --> F["Develop and test changes"]
    F --> G["Ensure code style compliance"]
    G --> H["Write/update tests"]
    H --> I["Submit pull request"]
    I --> J["Review process"]
    J --> K["Address feedback (if any)"]
    K --> L["Changes merged"]
```

**Contribution Process Diagram**

Sources: [CONTRIBUTING.md:20-32]()

### Step-by-Step Contribution Guide

1. **Submit an issue** describing your proposed change to the repository
2. **Wait for a response** from the repository owner regarding your issue
3. **Sign a CLA** if your proposed change is accepted and you haven't already signed one
4. **Fork the repository** to create your own copy for development
5. **Develop and test** your code changes
6. **Ensure style compliance** with the existing codebase style guidelines
7. **Write appropriate tests** for your changes and ensure all tests pass
8. **Submit a pull request** for review

Sources: [CONTRIBUTING.md:20-32]()

## Coding Standards

All contributions must adhere to the existing style in the Android Architecture Starter Templates. The repository follows the [AOSP Java Code Style for Contributors]() (external link).

The following diagram illustrates how coding standards apply to different components of the templates:

```mermaid
flowchart TD
    subgraph "Code Quality Standards"
        Style["AOSP Java Code Style"]
        Tests["Comprehensive Test Coverage"]
        Doc["Clear Documentation"]
    end

    subgraph "Template Components"
        UI["UI Layer\n(Compose, Material3)"]
        VM["ViewModel Layer"]
        Data["Data Layer\n(Repository, Room)"]
        DI["Dependency Injection\n(Hilt)"]
    end

    Style --> UI
    Style --> VM
    Style --> Data
    Style --> DI
    
    Tests --> UI
    Tests --> VM
    Tests --> Data
    Tests --> DI
    
    Doc --> UI
    Doc --> VM
    Doc --> Data
    Doc --> DI
```

**Code Standards Application Diagram**

Sources: [CONTRIBUTING.md:27-30]()

## Testing Requirements

All contributions must include appropriate tests. The following diagram shows the relationship between code components and testing requirements:

```mermaid
flowchart LR
    subgraph "Code Components"
        UIChanges["UI Changes"]
        ViewModelChanges["ViewModel Changes"]
        DataLayerChanges["Data Layer Changes"]
        InfraChanges["Infrastructure Changes"]
    end

    subgraph "Required Tests"
        UITests["UI Tests\n(Compose Testing)"]
        UnitTests["Unit Tests\n(ViewModel, Repository)"]
        IntegrationTests["Integration Tests\n(Data Flow)"]
        E2ETests["End-to-End Tests"]
    end

    UIChanges --> UITests
    UIChanges --> E2ETests
    
    ViewModelChanges --> UnitTests
    ViewModelChanges --> IntegrationTests
    
    DataLayerChanges --> UnitTests
    DataLayerChanges --> IntegrationTests
    
    InfraChanges --> UnitTests
    InfraChanges --> E2ETests
```

**Testing Requirements Diagram**

Sources: [CONTRIBUTING.md:31]()

## Pull Request Process

When submitting a pull request to the Android Architecture Starter Templates repository, ensure you:

1. **Reference the issue** that your pull request addresses
2. **Document your changes** clearly in the pull request description
3. **Verify all tests pass** before submission
4. **Be responsive** to feedback and questions during the review process

The following diagram illustrates the pull request lifecycle:

```mermaid
sequenceDiagram
    participant C as Contributor
    participant R as Repository
    participant M as Maintainer
    
    C->>R: Fork repository
    C->>C: Make changes
    C->>C: Run tests
    C->>R: Submit pull request
    R->>M: Notification of new PR
    M->>R: Review code
    
    alt Changes needed
        M->>C: Request changes
        C->>C: Make requested changes
        C->>R: Update pull request
        R->>M: Review updated code
    end
    
    M->>R: Approve changes
    M->>R: Merge pull request
    R->>C: Notification of merged PR
```

**Pull Request Lifecycle Diagram**

Sources: [CONTRIBUTING.md:32]()

## Repository Structure and Contributing Areas

The following diagram shows the main components of the repository where you might contribute, and how they relate to specific files and directories:

```mermaid
flowchart TD
    subgraph "Android Architecture Templates"
        Root["Repository Root"]
        
        Root --> Base["Base Template"]
        Root --> Multi["Multimodule Template"]
        Root --> Tools["Tools"]
        Root --> Docs["Documentation"]
        
        Base --> BaseUI["UI Layer Files"]
        Base --> BaseVM["ViewModel Files"]
        Base --> BaseData["Data Layer Files"]
        Base --> BaseDI["Dependency Injection Files"]
        
        Multi --> AppModule["App Module Files"]
        Multi --> FeatureModules["Feature Module Files"]
        Multi --> CoreModules["Core Module Files"]
        
        Tools --> CustomizerScript["customizer.sh Script"]
        
        Docs --> README["README.md"]
        Docs --> Contributing["CONTRIBUTING.md"]
    end
```

**Repository Structure Diagram**

Sources: [CONTRIBUTING.md]()

## Conclusion

Contributing to the Android Architecture Starter Templates helps improve the quality and usefulness of these templates for the Android developer community. By following the guidelines in this document, you can ensure that your contributions meet the standards required for inclusion in the repository.

If you have any questions about the contribution process, please open an issue in the repository for clarification before submitting your pull request.

---

