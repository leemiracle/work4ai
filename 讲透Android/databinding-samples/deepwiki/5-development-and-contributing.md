<!-- source: DeepWiki mcp.deepwiki.com · repo android/databinding-samples · page 5 Development and Contributing · fetched 2026-10-23 -->

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)

</details>



This document provides comprehensive guidance for developers who want to contribute to the Android Data Binding samples repository. It covers the legal framework, contribution processes, development standards, and integration with the project's CI/CD infrastructure.

This page focuses on the mechanics of contributing code and samples to the repository. For information about the build system infrastructure, see page [4](#4). For details about Google's internal sample packaging system, see page [5.1](#5.1).

## Legal Framework and Licensing

The repository operates under a dual licensing and contributor agreement structure managed by Google. All contributions must comply with both Android and Google Contributor License Agreements before code can be accepted.

### License Structure

The project is licensed under the Apache License 2.0 with Google as the copyright holder. The license provides broad permissions for use, modification, and distribution while maintaining proper attribution requirements.

| License Component | Details |
|------------------|---------|
| License Type | Apache License 2.0 |
| Copyright Holder | The Android Open Source Project (2018) |
| License File | [LICENSE:1-202]() |
| Attribution Requirements | Must retain copyright, patent, trademark notices |
| Redistribution Terms | Source and object form distribution permitted |

### Contributor License Agreement Requirements

Before any contributions can be accepted, contributors must complete the appropriate Contributor License Agreement process. The repository requires dual CLA compliance for both Android and Google projects.

```mermaid
flowchart TD
    A["Contributor"] --> B{"Contribution Type"}
    B -->|"Individual Developer"| C["Individual CLA"]
    B -->|"Corporate Employee"| D["Corporate CLA"]
    
    C --> E["Sign Individual CLA<br/>cla.developers.google.com"]
    D --> F["Sign Corporate CLA<br/>cla.developers.google.com"]
    
    E --> G["Sign Android CLA"]
    F --> G
    G --> H["Sign Google CLA"]
    H --> I["CLA Verification Complete"]
    I --> J["Pull Requests Accepted"]
    
    K["CONTRIBUTING.md"] --> L["CLA Process Documentation"]
    L --> C
    L --> D
```

**Sources:** [CONTRIBUTING.md:8-17](), [CONTRIBUTING.md:1-36]()

## Contribution Process Workflow

The contribution process follows a structured workflow that ensures code quality and proper legal compliance before integration into the main repository.

### Issue-Driven Development Process

All contributions must begin with an issue submission to establish communication with the repository maintainers and ensure the proposed changes align with project goals.

```mermaid
flowchart TD
    A["Developer"] --> B["Submit Issue<br/>describing proposed change"]
    B --> C["Repository Owner<br/>responds to issue"]
    C --> D{"Change Accepted?"}
    
    D -->|"Yes"| E["Verify CLA Status"]
    D -->|"No"| F["Issue Closed<br/>with feedback"]
    
    E --> G{"CLA Signed?"}
    G -->|"No"| H["Complete CLA Process"]
    G -->|"Yes"| I["Fork Repository"]
    H --> I
    
    I --> J["Develop and Test<br/>Code Changes"]
    J --> K["Code Style Compliance<br/>Android Code Style Guide"]
    K --> L["Unit Test Coverage<br/>All tests must pass"]
    L --> M["Submit Pull Request"]
    
    N["CONTRIBUTING.md"] --> O["Process Documentation"]
    O --> B
    O --> K
    O --> L
```

**Sources:** [CONTRIBUTING.md:22-35]()

### Code Quality and Style Requirements

The repository enforces strict adherence to Android development standards and requires comprehensive testing for all contributions.

| Requirement | Standard | Verification |
|------------|----------|--------------|
| Code Style | [Android Code Style Guide](https://source.android.com/source/code-style.html) | Manual review during PR |
| Testing Coverage | Unit tests for all functionality | Automated CI/CD verification |
| Existing Style Consistency | Match sample-specific patterns | Manual review |
| Documentation | Inline comments and README updates | Manual review |

**Sources:** [CONTRIBUTING.md:29-34]()

## Development Environment Integration

Contributors must work within the established development environment to ensure consistency with the project's build and testing infrastructure.

### Repository Fork and Development Setup

The development process requires forking the repository and maintaining compatibility with the existing build system configuration.

```mermaid
graph TB
    subgraph "Contributor Environment"
        A["Forked Repository"] --> B["Local Development"]
        B --> C["BasicSample Changes"]
        B --> D["TwoWaySample Changes"]
    end
    
    subgraph "Build System Compatibility"
        E["Gradle Wrapper 8.4<br/>BasicSample"] --> F["JDK 17 Compatibility"]
        G["Gradle Wrapper 7.5<br/>TwoWaySample"] --> H["JDK 11 Compatibility"]
    end
    
    subgraph "Testing Requirements"
        I["Espresso UI Tests"] --> J["Android Emulator"]
        K["Unit Tests"] --> L["Local JVM"]
        M["Lint Checks"] --> N["Code Quality"]
    end
    
    C --> E
    D --> G
    C --> I
    D --> I
    C --> K
    D --> K
    C --> M
    D --> M
    
    subgraph "CI/CD Integration"
        O["GitHub Actions"] --> P["Path-Based Triggering"]
        P --> Q["BasicSample/**"]
        P --> R["TwoWaySample/**"]
    end
    
    F --> O
    H --> O
    J --> O
    L --> O
    N --> O
```

**Sources:** [CONTRIBUTING.md:28](), CI/CD configuration from system analysis

## Code Contribution Standards

### Sample Application Contribution Guidelines

When contributing to either BasicSample or TwoWaySample, developers must maintain the educational progression and architectural patterns established in each application.

| Sample Application | Contribution Focus | Architecture Requirements |
|-------------------|-------------------|--------------------------|
| BasicSample | Foundational data binding concepts | Observable patterns, ViewModel integration |
| TwoWaySample | Advanced two-way binding | Complex ViewModels, inverse binding adapters |

### Testing Integration Requirements

All contributions must include appropriate test coverage that integrates with the existing testing framework infrastructure.

```mermaid
flowchart LR
    subgraph "Testing Framework Integration"
        A["New Feature"] --> B["Unit Tests"]
        A --> C["UI Tests"]
        
        B --> D["JUnit Framework"]
        C --> E["Espresso Framework"]
        
        D --> F["Local Test Execution"]
        E --> G["Android Emulator Tests"]
        
        F --> H["CI/CD Pipeline"]
        G --> H
        
        H --> I["Automated Verification"]
        I --> J["Build Artifacts"]
        I --> K["Test Reports"]
    end
    
    subgraph "Quality Gates"
        L["Lint Checks"] --> M["Code Quality Verification"]
        N["ProGuard Rules"] --> O["Release Build Verification"]
    end
    
    H --> L
    H --> N
```

**Sources:** [CONTRIBUTING.md:34](), Testing infrastructure from system analysis

## Legal Compliance and Attribution

### Apache License 2.0 Compliance

All contributions become part of the Apache License 2.0 licensed codebase and must comply with the license terms for redistribution and modification.

The license grants broad rights while requiring proper attribution and notice preservation:

- **Copyright License**: Perpetual, worldwide, non-exclusive rights to reproduce, modify, and distribute
- **Patent License**: Protection for contributors and users against patent litigation
- **Attribution Requirements**: Preservation of copyright, patent, and trademark notices
- **Redistribution Terms**: Requirements for license inclusion and modification notices

### Contribution Ownership and Rights

Contributors retain ownership of their contributions while granting necessary rights to the project under the Apache License 2.0 framework.

```mermaid
graph TD
    subgraph "Contribution Rights Framework"
        A["Contributor"] --> B["Original Work Creation"]
        B --> C["CLA Signature"]
        C --> D["Rights Grant to Google"]
        
        D --> E["Apache License 2.0<br/>Public Distribution"]
        D --> F["Google Internal Use<br/>Sample Distribution"]
        
        G["LICENSE File"] --> H["Apache License Terms"]
        H --> I["Copyright: Android Open Source Project"]
        I --> J["2018 Copyright Date"]
    end
    
    subgraph "Legal Framework Files"
        K["CONTRIBUTING.md"] --> L["CLA Requirements"]
        K --> M["Contribution Process"]
        N["LICENSE"] --> O["License Terms"]
        N --> P["Attribution Requirements"]
    end
    
    C --> K
    E --> N
```

**Sources:** [LICENSE:189-201](), [CONTRIBUTING.md:5-20]()

## Integration with Project Infrastructure

### CI/CD Pipeline Integration

Contributor changes automatically integrate with the sophisticated CI/CD infrastructure that provides automated testing and verification across multiple environments.

The CI/CD system uses path-based triggering to optimize build times and resource usage:

- **BasicSample contributions**: Trigger JDK 17 builds with Gradle 8.4
- **TwoWaySample contributions**: Trigger JDK 11 builds with Gradle 7.5
- **Repository-wide changes**: Trigger comprehensive testing across both samples

### Artifact Generation and Preservation

The CI/CD system generates and preserves build artifacts for debugging and verification purposes, ensuring that contributor changes can be thoroughly tested and validated.

```mermaid
flowchart TD
    subgraph "Contributor Integration Flow"
        A["Pull Request"] --> B["Path Detection"]
        B --> C{"Change Scope"}
        
        C -->|"BasicSample/**"| D["BasicSample Workflow"]
        C -->|"TwoWaySample/**"| E["TwoWaySample Workflow"]
        C -->|"Repository Root"| F["Full Repository Test"]
        
        D --> G["JDK 17 Setup"]
        E --> H["JDK 11 Setup"]
        F --> I["Multi-Environment Test"]
        
        G --> J["Gradle 8.4 Build"]
        H --> K["Gradle 7.5 Build"]
        
        J --> L["Android Emulator Tests"]
        K --> L
        I --> L
        
        L --> M["Artifact Upload"]
        M --> N["Build Verification"]
        N --> O["Merge Approval"]
    end
```

**Sources:** CI/CD configuration analysis, [CONTRIBUTING.md:28-35]()

---

