<!-- source: DeepWiki mcp.deepwiki.com · repo android/enterprise-samples · page 4 Development Guide · fetched 2026-10-23 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CODEOWNERS](CODEOWNERS)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This document provides comprehensive guidelines for developing and contributing to the Android Enterprise Samples repository. It covers the development workflow, contribution requirements, code review processes, and automated maintenance systems that ensure code quality and project sustainability.

For detailed information about specific contribution requirements, see [Contributing Guidelines](#4.1). For code ownership structure and review processes, see [Code Ownership and Review](#4.2). For automated dependency management and maintenance, see [Automated Maintenance](#4.3).

## Development Workflow Overview

The Android Enterprise Samples repository follows a structured development workflow that balances open contribution with quality control and enterprise-grade reliability.

```mermaid
graph TB
    subgraph "External Contribution Flow"
        DEV["Developer"] --> CLA["Sign Google CLA"]
        CLA --> FORK["Fork Repository"]
        FORK --> BRANCH["Create Feature Branch"]
        BRANCH --> CODE["Implement Changes"]
        CODE --> TEST["Local Testing"]
        TEST --> PR["Create Pull Request"]
    end
    
    subgraph "Review and Integration Process"
        PR --> CODEOWNERS["@pfmaggi @ancalabrese"]
        CODEOWNERS --> REVIEW["Code Review"]
        REVIEW --> CI["GitHub Actions CI"]
        CI --> BUILD["Build Verification"]
        BUILD --> MERGE["Merge to main"]
    end
    
    subgraph "Quality Assurance"
        MERGE --> ARTIFACTS["Generate Artifacts"]
        ARTIFACTS --> DEPLOY["Deploy to Repository"]
        RENOVATE["Renovate Bot"] --> UPDATES["Dependency Updates"]
        UPDATES --> PR
    end
    
    style CLA fill:#fff3e0
    style CODEOWNERS fill:#e1f5fe
    style CI fill:#e8f5e8
```

**Development Workflow Process**: This diagram illustrates the complete development lifecycle from external contribution through integration and quality assurance.

Sources: [CONTRIBUTING.md:1-29](), [CODEOWNERS:1](), [.github/workflows/assemble.yml]()

## Contribution Requirements

All contributions to the Android Enterprise Samples repository must meet specific legal and technical requirements before integration.

### Legal Requirements

| Requirement | Description | Reference |
|-------------|-------------|-----------|
| **Contributor License Agreement** | All contributors must sign Google's CLA before any code can be accepted | [CONTRIBUTING.md:6-16]() |
| **Apache 2.0 License** | All code contributions are licensed under Apache License Version 2.0 | [LICENSE:1-192]() |
| **Community Guidelines** | Contributors must follow Google's Open Source Community Guidelines | [CONTRIBUTING.md:25-28]() |

### Technical Requirements

```mermaid
graph LR
    subgraph "Code Quality Standards"
        STYLE["Code Style"] --> LINT["Lint Checks"]
        LINT --> BUILD["Build Success"]
        BUILD --> TEST["Test Execution"]
    end
    
    subgraph "Repository Standards"
        GITIGNORE[".gitignore Rules"] --> CLEAN["Clean Commits"]
        CLEAN --> PR_TEMPLATE["PR Description"]
        PR_TEMPLATE --> REVIEW["Code Review"]
    end
    
    subgraph "Automated Validation"
        CI_WORKFLOW["assemble.yml"] --> GRADLE["gradlew_recursive.sh"]
        GRADLE --> COMPILE["assembleDebug"]
        COMPILE --> ARTIFACTS["Build Artifacts"]
    end
    
    REVIEW --> CI_WORKFLOW
    TEST --> ARTIFACTS
```

**Technical Validation Process**: This diagram shows the automated and manual validation steps that ensure code quality and repository standards.

Sources: [CONTRIBUTING.md:18-23](), [.gitignore:1-37](), [.github/workflows/assemble.yml]()

## Code Ownership Structure

The repository implements a structured code ownership model to ensure consistent review quality and maintain project direction.

### Ownership Hierarchy

```mermaid
graph TD
    subgraph "Repository Ownership"
        CODEOWNERS_FILE["CODEOWNERS"] --> PFMAGGI["@pfmaggi"]
        CODEOWNERS_FILE --> ANCALABRESE["@ancalabrese"]
    end
    
    subgraph "Review Authority"
        PFMAGGI --> ALL_FILES["All Repository Files"]
        ANCALABRESE --> ALL_FILES
        ALL_FILES --> MANAGED_CONFIGS["ManagedConfigurations/"]
        ALL_FILES --> WORK_PROFILE["Work-profile-codelab/"]
        ALL_FILES --> BUILD_SYSTEM["gradle/, .github/"]
    end
    
    subgraph "Review Process"
        PR_SUBMIT["Pull Request Submitted"] --> AUTO_ASSIGN["Auto-assign Reviewers"]
        AUTO_ASSIGN --> REVIEW_REQUIRED["Review Required"]
        REVIEW_REQUIRED --> APPROVAL["Approval from Code Owners"]
        APPROVAL --> MERGE_PERMISSION["Merge Permission Granted"]
    end
    
    CODEOWNERS_FILE --> AUTO_ASSIGN
```

**Code Ownership and Review Structure**: This diagram shows how the `CODEOWNERS` file defines review requirements and the automated assignment process.

Sources: [CODEOWNERS:1](), [CONTRIBUTING.md:18-23]()

## Development Environment Setup

Developers working with the Android Enterprise Samples repository need to configure their environment to match the project's build requirements and standards.

### Required Tools and Versions

| Tool | Version/Configuration | Location |
|------|----------------------|----------|
| **Java Development Kit** | JDK 21 | CI configuration requirement |
| **Android Gradle Plugin** | Version defined in `libs.versions.toml` | [gradle/libs.versions.toml]() |
| **Gradle Wrapper** | Project-specific version | [gradlew](), [gradlew.bat]() |
| **Android SDK** | Latest stable with required API levels | Local configuration |

### Build System Configuration

```mermaid
graph LR
    subgraph "Gradle Build System"
        GRADLEW["gradlew / gradlew.bat"] --> WRAPPER["Gradle Wrapper"]
        WRAPPER --> VERSION_CATALOG["libs.versions.toml"]
        VERSION_CATALOG --> DEPENDENCIES["Centralized Dependencies"]
    end
    
    subgraph "Build Execution"
        RECURSIVE_SCRIPT["gradlew_recursive.sh"] --> MANAGED_CONFIGS_BUILD["ManagedConfigurations Build"]
        RECURSIVE_SCRIPT --> WORK_PROFILE_BUILD["Work-profile-codelab Build"]
        MANAGED_CONFIGS_BUILD --> ASSEMBLE_DEBUG["assembleDebug Task"]
        WORK_PROFILE_BUILD --> ASSEMBLE_DEBUG
    end
    
    subgraph "Artifact Generation"
        ASSEMBLE_DEBUG --> APK_FILES["APK Files"]
        ASSEMBLE_DEBUG --> AAB_FILES["AAB Files"] 
        ASSEMBLE_DEBUG --> AAR_FILES["AAR Files"]
        ASSEMBLE_DEBUG --> SO_FILES["SO Files"]
    end
    
    DEPENDENCIES --> MANAGED_CONFIGS_BUILD
    DEPENDENCIES --> WORK_PROFILE_BUILD
```

**Build System Architecture**: This diagram shows the Gradle-based build system that compiles all sample applications and generates distributable artifacts.

Sources: [gradlew](), [gradlew.bat](), [gradle/libs.versions.toml](), [.github/workflows/assemble.yml]()

## Automated Quality Assurance

The repository employs multiple automated systems to maintain code quality, security, and dependency currency without requiring manual intervention.

### Continuous Integration Pipeline

```mermaid
graph TB
    subgraph "GitHub Actions Triggers"
        PUSH_MAIN["Push to main"] --> WORKFLOW["assemble.yml"]
        PULL_REQUEST["Pull Request"] --> WORKFLOW
        MANUAL_DISPATCH["Manual Dispatch"] --> WORKFLOW
    end
    
    subgraph "CI Execution Environment"
        WORKFLOW --> UBUNTU_RUNNER["ubuntu-latest"]
        UBUNTU_RUNNER --> CHECKOUT_CODE["actions/checkout@v4"]
        CHECKOUT_CODE --> SETUP_JDK["actions/setup-java@v4"]
        SETUP_JDK --> JDK21["temurin JDK 21"]
    end
    
    subgraph "Build and Test Execution"
        JDK21 --> GRADLE_RECURSIVE["gradlew_recursive.sh"]
        GRADLE_RECURSIVE --> BUILD_ALL["Build All Modules"]
        BUILD_ALL --> ARTIFACT_CREATION["Create assemble.zip"]
        ARTIFACT_CREATION --> UPLOAD_ARTIFACTS["actions/upload-artifact@v4"]
    end
    
    subgraph "Quality Gates"
        BUILD_ALL --> BUILD_SUCCESS["Build Success Check"]
        BUILD_SUCCESS --> LINT_VALIDATION["Lint Validation"]
        LINT_VALIDATION --> TEST_EXECUTION["Test Execution"]
        TEST_EXECUTION --> SECURITY_SCAN["Security Scan"]
    end
    
    UPLOAD_ARTIFACTS --> DOWNLOADABLE["Downloadable Artifacts"]
```

**Continuous Integration Pipeline**: This diagram details the automated build and quality assurance process that runs on every code change.

Sources: [.github/workflows/assemble.yml](), [gradlew_recursive.sh]()

### Automated Dependency Management

The repository uses Renovate bot for automated dependency updates, ensuring security patches and feature updates are applied consistently across all modules.

| Component | Function | Configuration |
|-----------|----------|---------------|
| **Renovate Bot** | Automated dependency updates | Repository-level configuration |
| **Version Catalogs** | Centralized dependency management | [gradle/libs.versions.toml]() |
| **Security Updates** | Automatic security patch application | High priority scheduling |
| **Feature Updates** | Controlled feature dependency updates | Weekly scheduling |

Sources: [CONTRIBUTING.md:1-29](), [CODEOWNERS:1](), [LICENSE:1-192](), [.gitignore:1-37](), [README.md:1-6]()

---

