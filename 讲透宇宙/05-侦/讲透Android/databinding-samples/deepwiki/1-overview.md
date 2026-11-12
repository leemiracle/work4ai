<!-- source: DeepWiki mcp.deepwiki.com · repo android/databinding-samples · page 1 Overview · fetched 2026-10-23 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [BasicSample/.google/packaging.yaml](BasicSample/.google/packaging.yaml)
- [README.md](README.md)

</details>



This document provides an overview of the Android Data Binding samples repository, which contains educational Android applications demonstrating the Android Data Binding Library. The repository consists of two progressively complex sample applications: BasicSample for foundational concepts and TwoWaySample for advanced patterns. For detailed information about the repository structure and setup, see [Repository Structure](#1.1) and [Getting Started](#1.2).

## Purpose and Educational Progression

The repository serves as a comprehensive educational resource for Android developers learning data binding concepts. The samples are designed with a clear progression from basic to advanced implementations, providing practical examples of data binding patterns and anti-patterns.

```mermaid
graph TB
    subgraph "Learning Progression"
        A["BasicSample<br/>(Intermediate Level)"] --> B["TwoWaySample<br/>(Advanced Level)"]
    end
    
    subgraph "BasicSample Concepts"
        A --> A1["Layout Expressions<br/>@{user.name}"]
        A --> A2["Binding Adapters<br/>Custom attributes"]
        A --> A3["ViewModel Integration<br/>Architecture Components"]
        A --> A4["Observable Fields<br/>Manual updates"]
    end
    
    subgraph "TwoWaySample Concepts"
        B --> B1["Two-Way Data Binding<br/>@={viewModel.property}"]
        B --> B2["Advanced Binding Adapters<br/>Inverse converters"]
        B --> B3["Animations Integration<br/>UI state transitions"]
        B --> B4["Data Persistence<br/>SharedPreferences"]
    end
    
    subgraph "Technologies"
        C["Kotlin Language"] --> A
        C --> B
        D["Android Data Binding Library"] --> A
        D --> B
    end
```

**Educational Progression Diagram**

Sources: [README.md:4-9](), [BasicSample/.google/packaging.yaml:28-37]()

## Repository Architecture

The repository contains two main sample applications with comprehensive build and testing infrastructure. Each sample targets different learning objectives and demonstrates specific data binding patterns.

| Sample | Level | Primary Focus | Key Demonstrations |
|--------|-------|---------------|-------------------|
| BasicSample | Intermediate | Foundation concepts | `ObservableFieldActivity`, `ViewModelActivity`, binding adapters |
| TwoWaySample | Advanced | Two-way binding | `IntervalTimerViewModel`, inverse binding, persistence |

```mermaid
graph TB
    subgraph "Repository Structure"
        ROOT["android-databinding-samples"] --> BASIC["BasicSample/"]
        ROOT --> TWOWAY["TwoWaySample/"]
        ROOT --> INFRA["Infrastructure"]
    end
    
    subgraph "BasicSample Code Entities"
        BASIC --> BASIC_MAIN["MainActivity"]
        BASIC --> BASIC_OBS["ObservableFieldActivity"]
        BASIC --> BASIC_VM["ViewModelActivity"]
        BASIC --> BASIC_PROFILE["ProfileLiveDataViewModel"]
        BASIC --> BASIC_UTILS["BindingAdapters"]
    end
    
    subgraph "TwoWaySample Code Entities"
        TWOWAY --> TWOWAY_MAIN["MainActivity"]
        TWOWAY --> TWOWAY_VM["IntervalTimerViewModel"]
        TWOWAY --> TWOWAY_UTIL["util package"]
        TWOWAY --> TWOWAY_CONVERTER["Converter classes"]
    end
    
    subgraph "Infrastructure Components"
        INFRA --> CI["GitHub Actions Workflows"]
        INFRA --> BUILD["Gradle Wrapper Scripts"]
        INFRA --> DOCS["README.md"]
        INFRA --> PKG["Google Packaging Metadata"]
    end
```

**Repository Architecture with Code Entities**

Sources: [README.md:8-9](), [BasicSample/.google/packaging.yaml:16-42]()

## Sample Application Characteristics

### BasicSample
- **Status**: Published (`PUBLISHED`)
- **Level**: Intermediate
- **Language**: Kotlin
- **Focus**: Layout expressions, binding adapters, ViewModel integration
- **Key Classes**: Activities demonstrating different data binding approaches

### TwoWaySample  
- **Level**: Advanced
- **Language**: Kotlin
- **Focus**: Two-way data binding, animations, converters, inverse converters
- **Key Classes**: Complex ViewModel implementations with bidirectional data flow

## Integration with Android Ecosystem

The repository references additional official Android samples that demonstrate data binding in production contexts:

- **Android Architecture Blueprints**: Data binding with architecture best practices
- **Android Architecture Components Samples**: Advanced patterns with Dagger and GitHub API
- **Android Sunflower**: Data binding within Android Jetpack ecosystem

## Issue Reporting and Support

Issues are categorized by component:

| Issue Type | Reporting Location |
|------------|-------------------|
| Sample code issues | GitHub repository issues |
| Build-related issues | Gradle Plugin issue tracker |
| Android Studio integration | Android Studio issue tracker |

```mermaid
graph LR
    subgraph "Issue Categories"
        DEV["Developer"] --> SAMPLE["Sample Code Issues"]
        DEV --> BUILD["Build System Issues"]
        DEV --> IDE["IDE Integration Issues"]
    end
    
    subgraph "Reporting Channels"
        SAMPLE --> GITHUB["GitHub Issues"]
        BUILD --> GRADLE["Gradle Plugin Tracker"]
        IDE --> STUDIO["Android Studio Tracker"]
    end
```

**Issue Reporting Flow**

Sources: [README.md:17-19]()

The repository serves as both a learning resource and a reference implementation for Android Data Binding Library usage patterns, with comprehensive infrastructure supporting continuous integration and educational content delivery.

Sources: [README.md:1-40](), [BasicSample/.google/packaging.yaml:1-42]()

---

