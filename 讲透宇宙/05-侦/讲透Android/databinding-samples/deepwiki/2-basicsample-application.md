<!-- source: DeepWiki mcp.deepwiki.com · repo android/databinding-samples · page 2 BasicSample Application · fetched 2026-10-23 -->

# BasicSample Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [BasicSample/README.md](BasicSample/README.md)
- [BasicSample/app/build.gradle](BasicSample/app/build.gradle)

</details>



This document provides a comprehensive overview of the BasicSample application, which serves as the foundational learning module for Android Data Binding concepts. The BasicSample demonstrates core data binding features including layout expressions, observability patterns, and binding adapters through practical examples that progress from anti-patterns to best practices.

For advanced two-way data binding patterns, see [TwoWaySample Application](#3). For detailed build system configuration, see [Build System and Infrastructure](#4).

## Application Overview

The BasicSample application is an educational Android project that demonstrates fundamental data binding concepts through three distinct activity implementations. Each activity showcases different approaches to data binding, allowing developers to understand the evolution from basic implementations to architecture-compliant solutions.

The application presents a user profile interface where users can interact with profile data, demonstrating how data binding reduces boilerplate code and improves UI-data synchronization. The sample intentionally includes both recommended practices and documented anti-patterns to provide comprehensive learning opportunities.

### Application Architecture

```mermaid
graph TB
    subgraph "BasicSample Application Structure"
        MainActivity["MainActivity"] --> ObservableFieldActivity["ObservableFieldActivity"]
        MainActivity --> ViewModelActivity["ViewModelActivity"]
        
        subgraph "Data Layer"
            ObservableFieldProfile["ObservableFieldProfile"]
            ProfileObservableFieldsViewModel["ProfileObservableFieldsViewModel"]
            ProfileLiveDataViewModel["ProfileLiveDataViewModel"]
            ProfileObservableViewModel["ProfileObservableViewModel"]
        end
        
        subgraph "Layout Files"
            activity_main["activity_main.xml"]
            observable_field_profile["observable_field_profile.xml"]
            viewmodel_profile["viewmodel_profile.xml"]
        end
        
        subgraph "Binding Utilities"
            BindingAdapters["BindingAdapters.kt"]
            ConverterUtil["ConverterUtil.kt"]
        end
        
        ObservableFieldActivity --> ObservableFieldProfile
        ObservableFieldActivity --> observable_field_profile
        
        ViewModelActivity --> ProfileObservableFieldsViewModel
        ViewModelActivity --> ProfileLiveDataViewModel
        ViewModelActivity --> ProfileObservableViewModel
        ViewModelActivity --> viewmodel_profile
        
        observable_field_profile --> BindingAdapters
        viewmodel_profile --> BindingAdapters
        observable_field_profile --> ConverterUtil
    end
```

Sources: [BasicSample/README.md:1-299]()

### Data Binding Patterns Demonstrated

The BasicSample implements three distinct data binding approaches, each representing different levels of architectural sophistication:

```mermaid
graph LR
    subgraph "Data Binding Pattern Evolution"
        BasicBinding["Basic Data Binding<br/>findViewById elimination"]
        ObservableFields["Observable Fields<br/>ObservableInt, ObservableField"]
        LiveDataBinding["LiveData Integration<br/>Architecture Components"]
        ObservableClasses["Observable Classes<br/>Full observability control"]
    end
    
    subgraph "Implementation Classes"
        MainActivity_impl["MainActivity<br/>Basic binding setup"]
        ObservableFieldActivity_impl["ObservableFieldActivity<br/>ObservableFieldProfile"]
        ViewModelActivity_impl["ViewModelActivity<br/>ProfileLiveDataViewModel<br/>ProfileObservableFieldsViewModel<br/>ProfileObservableViewModel"]
    end
    
    BasicBinding --> MainActivity_impl
    ObservableFields --> ObservableFieldActivity_impl
    LiveDataBinding --> ViewModelActivity_impl
    ObservableClasses --> ViewModelActivity_impl
    
    subgraph "Binding Features"
        LayoutExpressions["Layout Expressions<br/>@{user.name}"]
        BindingAdapters_feat["Binding Adapters<br/>app:progressTint"]
        BindingMethods["Binding Methods<br/>app:srcCompat"]
        BindingConverters["Binding Converters<br/>app:hideIfZero"]
    end
    
    MainActivity_impl --> LayoutExpressions
    ObservableFieldActivity_impl --> BindingAdapters_feat
    ViewModelActivity_impl --> BindingMethods
    ViewModelActivity_impl --> BindingConverters
```

Sources: [BasicSample/README.md:19-257]()

## Application Structure

The BasicSample follows a clear progression from basic to advanced data binding concepts:

| Component | Purpose | Implementation Pattern |
|-----------|---------|----------------------|
| `MainActivity` | Entry point demonstrating basic data binding | findViewById elimination |
| `ObservableFieldActivity` | Shows reactive UI with observable fields | Anti-pattern demonstration |
| `ViewModelActivity` | Architecture Components integration | Best practice implementation |
| `ObservableFieldProfile` | Simple data model with observable fields | Direct field observation |
| `ProfileLiveDataViewModel` | Lifecycle-aware data management | LiveData integration |
| `ProfileObservableFieldsViewModel` | Observable field management | ViewModel pattern |
| `ProfileObservableViewModel` | Full observability control | Custom observable implementation |

### Build Configuration

The BasicSample application uses modern Android development practices with specific build configurations:

```mermaid
graph TB
    subgraph "Build Configuration"
        BuildGradle["build.gradle"] --> AndroidConfig["Android Configuration"]
        BuildGradle --> Dependencies["Dependencies"]
        BuildGradle --> BuildFeatures["Build Features"]
        
        AndroidConfig --> Namespace["namespace: com.example.android.databinding.basicsample"]
        AndroidConfig --> JavaVersion["Java 17 compatibility"]
        AndroidConfig --> TestRunner["AndroidJUnitRunner"]
        
        BuildFeatures --> DataBinding["dataBinding: true"]
        
        Dependencies --> AndroidX["AndroidX Libraries"]
        Dependencies --> Testing["Testing Framework"]
        
        AndroidX --> AppCompat["appcompat"]
        AndroidX --> ConstraintLayout["constraintlayout"]
        AndroidX --> ActivityKtx["activity-ktx"]
        AndroidX --> LifecycleViewModel["lifecycle-viewmodel-ktx"]
        
        Testing --> JUnit["JUnit"]
        Testing --> Espresso["Espresso"]
        Testing --> AndroidXTest["AndroidX Test"]
    end
```

Sources: [BasicSample/app/build.gradle:23-65]()

Key build configuration elements:

- **Data Binding Enabled**: [BasicSample/app/build.gradle:42]() enables the data binding feature
- **Kotlin Support**: [BasicSample/app/build.gradle:19-21]() includes Kotlin Android plugin and kapt
- **Java 17 Compatibility**: [BasicSample/app/build.gradle:45-47]() sets source and target compatibility
- **Architecture Components**: [BasicSample/app/build.gradle:54-55]() includes lifecycle and activity dependencies
- **Testing Infrastructure**: [BasicSample/app/build.gradle:60-63]() provides comprehensive testing support

## Navigation to Detailed Documentation

The BasicSample application is documented across several specialized pages:

- **Core Data Binding Concepts** [#2.1](#2.1): Detailed analysis of `ObservableFieldActivity` implementation, including documented anti-patterns and the transition to better practices
- **ViewModel Architecture** [#2.2](#2.2): Comprehensive coverage of `ViewModelActivity` and the three ViewModel implementations showing Android Architecture Components integration  
- **Binding Utilities and Adapters** [#2.3](#2.3): Documentation of custom binding adapters, binding methods, and binding converters that extend data binding functionality
- **Testing Framework** [#2.4](#2.4): Espresso-based testing approach and strategies for testing data binding implementations
- **Application Configuration** [#2.5](#2.5): Android manifest structure and application-level configuration details

Sources: [BasicSample/README.md:1-299](), [BasicSample/app/build.gradle:1-66]()

---

