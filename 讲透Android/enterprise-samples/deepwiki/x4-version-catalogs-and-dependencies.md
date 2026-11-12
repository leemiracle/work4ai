<!-- source: DeepWiki mcp.deepwiki.com · repo android/enterprise-samples · extra page Version Catalogs and Dependencies · fetched 2026-10-23 -->

# Version Catalogs and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Work-profile-codelab/app-finished/build.gradle.kts](Work-profile-codelab/app-finished/build.gradle.kts)
- [Work-profile-codelab/app-starter/build.gradle.kts](Work-profile-codelab/app-starter/build.gradle.kts)
- [Work-profile-codelab/app-starter/src/main/res/values/styles.xml](Work-profile-codelab/app-starter/src/main/res/values/styles.xml)
- [Work-profile-codelab/build.gradle.kts](Work-profile-codelab/build.gradle.kts)
- [Work-profile-codelab/gradle.properties](Work-profile-codelab/gradle.properties)
- [Work-profile-codelab/gradle/libs.versions.toml](Work-profile-codelab/gradle/libs.versions.toml)
- [Work-profile-codelab/gradle/wrapper/gradle-wrapper.properties](Work-profile-codelab/gradle/wrapper/gradle-wrapper.properties)

</details>



This document covers the centralized dependency management system used in the Android Enterprise Samples repository, specifically focusing on Gradle Version Catalogs implementation. It details how versions, libraries, and plugins are defined and consumed across all sample applications.

For information about the CI/CD build pipeline that utilizes these dependencies, see [CI/CD Pipeline](#3.1). For details about the Gradle wrapper execution system, see [Gradle Wrapper Scripts](#3.2.1).

## Overview

The repository employs Gradle Version Catalogs as the centralized dependency management solution, replacing traditional dependency declarations in individual `build.gradle` files. This system provides type-safe dependency management and ensures version consistency across all modules in the Work Profile Codelab project.

**Version Catalog Architecture**

```mermaid
graph TB
    subgraph "Version Catalog System"
        TOML["libs.versions.toml<br/>Central Catalog"]
        
        subgraph "Catalog Sections"
            VERSIONS["[versions]<br/>Version Declarations"]
            LIBRARIES["[libraries]<br/>Library Definitions"]
            PLUGINS["[plugins]<br/>Plugin Definitions"]
        end
        
        TOML --> VERSIONS
        TOML --> LIBRARIES
        TOML --> PLUGINS
    end
    
    subgraph "Build Files"
        ROOT["build.gradle.kts<br/>Root Project"]
        STARTER["app-starter/build.gradle.kts<br/>Starter Module"]
        FINISHED["app-finished/build.gradle.kts<br/>Finished Module"]
    end
    
    subgraph "Dependency References"
        PLUGIN_REF["alias(libs.plugins.*)"]
        LIB_REF["implementation(libs.*)"]
        TEST_REF["testImplementation(libs.*)"]
    end
    
    VERSIONS --> LIBRARIES
    VERSIONS --> PLUGINS
    
    LIBRARIES --> LIB_REF
    PLUGINS --> PLUGIN_REF
    
    LIB_REF --> STARTER
    LIB_REF --> FINISHED
    TEST_REF --> STARTER
    TEST_REF --> FINISHED
    PLUGIN_REF --> ROOT
    PLUGIN_REF --> STARTER
    PLUGIN_REF --> FINISHED
```

Sources: [Work-profile-codelab/gradle/libs.versions.toml:1-43](), [Work-profile-codelab/build.gradle.kts:17-20](), [Work-profile-codelab/app-starter/build.gradle.kts:17-19](), [Work-profile-codelab/app-finished/build.gradle.kts:17-19]()

## Version Catalog Structure

The version catalog is defined in `libs.versions.toml` using TOML (Tom's Obvious, Minimal Language) format. The catalog organizes dependency management into three main sections:

### Version Declarations

```mermaid
graph LR
    subgraph "Version Variables"
        AGP["agp = '8.8.0'"]
        KOTLIN["kotlin = '2.0.21'"]
        CORE_KTX["coreKtx = '1.15.0'"]
        JUNIT["junit = '4.13.2'"]
        APPCOMPAT["appcompat = '1.7.0'"]
        MATERIAL["material = '1.12.0'"]
        ACTIVITY["activity = '1.9.3'"]
        CONSTRAINT["constraintlayout = '2.2.0'"]
        RECYCLER["recyclerview = '1.3.2'"]
    end
    
    subgraph "Version Categories"
        BUILD_TOOLS["Build Tools<br/>AGP, Kotlin"]
        ANDROIDX["AndroidX Libraries<br/>Core, AppCompat, UI"]
        TESTING["Testing Libraries<br/>JUnit, Espresso"]
    end
    
    AGP --> BUILD_TOOLS
    KOTLIN --> BUILD_TOOLS
    CORE_KTX --> ANDROIDX
    APPCOMPAT --> ANDROIDX
    MATERIAL --> ANDROIDX
    ACTIVITY --> ANDROIDX
    CONSTRAINT --> ANDROIDX
    RECYCLER --> ANDROIDX
    JUNIT --> TESTING
```

The version section defines all dependency versions as variables that can be referenced throughout the catalog, ensuring consistency and simplifying version updates.

Sources: [Work-profile-codelab/gradle/libs.versions.toml:15-27]()

### Library Definitions

The libraries section maps dependency coordinates to their versions using a structured format:

| Library Alias | Group | Artifact | Version Reference |
|--------------|--------|----------|------------------|
| `androidx-core-ktx` | androidx.core | core-ktx | coreKtx |
| `androidx-appcompat` | androidx.appcompat | appcompat | appcompat |
| `material` | com.google.android.material | material | material |
| `androidx-activity` | androidx.activity | activity | activity |
| `androidx-constraintlayout` | androidx.constraintlayout | constraintlayout | constraintlayout |
| `androidx-recyclerview` | androidx.recyclerview | recyclerview | recyclerview |
| `jetbrains-kotlin-stdlib-jdk7` | org.jetbrains.kotlin | kotlin-stdlib-jdk7 | kotlin |

Sources: [Work-profile-codelab/gradle/libs.versions.toml:28-39]()

### Plugin Definitions

```mermaid
graph TB
    subgraph "Plugin Catalog"
        ANDROID_APP["android-application<br/>id: com.android.application<br/>version.ref: agp"]
        KOTLIN_ANDROID["kotlin-android<br/>id: org.jetbrains.kotlin.android<br/>version.ref: kotlin"]
    end
    
    subgraph "Build File Usage"
        ROOT_PLUGINS["Root build.gradle.kts<br/>alias(libs.plugins.android.application) apply false<br/>alias(libs.plugins.kotlin.android) apply false"]
        MODULE_PLUGINS["Module build.gradle.kts<br/>alias(libs.plugins.android.application)<br/>alias(libs.plugins.kotlin.android)"]
    end
    
    ANDROID_APP --> ROOT_PLUGINS
    KOTLIN_ANDROID --> ROOT_PLUGINS
    ANDROID_APP --> MODULE_PLUGINS
    KOTLIN_ANDROID --> MODULE_PLUGINS
```

Sources: [Work-profile-codelab/gradle/libs.versions.toml:40-43](), [Work-profile-codelab/build.gradle.kts:17-20](), [Work-profile-codelab/app-starter/build.gradle.kts:17-19]()

## Dependency Management Flow

The version catalog enables type-safe dependency references across all build files in the project:

**Dependency Resolution Flow**

```mermaid
graph TD
    subgraph "libs.versions.toml"
        VERSION_DEF["[versions]<br/>coreKtx = '1.15.0'"]
        LIB_DEF["[libraries]<br/>androidx-core-ktx = { group = 'androidx.core', name = 'core-ktx', version.ref = 'coreKtx' }"]
    end
    
    subgraph "Build Script Resolution"
        ALIAS_REF["libs.androidx.core.ktx"]
        GRADLE_RESOLUTION["androidx.core:core-ktx:1.15.0"]
    end
    
    subgraph "Module Dependencies"
        STARTER_IMPL["app-starter/build.gradle.kts<br/>implementation(libs.androidx.core.ktx)"]
        FINISHED_IMPL["app-finished/build.gradle.kts<br/>implementation(libs.androidx.core.ktx)"]
    end
    
    VERSION_DEF --> LIB_DEF
    LIB_DEF --> ALIAS_REF
    ALIAS_REF --> GRADLE_RESOLUTION
    GRADLE_RESOLUTION --> STARTER_IMPL
    GRADLE_RESOLUTION --> FINISHED_IMPL
```

### Implementation Dependencies

Both the `app-starter` and `app-finished` modules utilize identical dependency sets, demonstrating the consistency achieved through version catalogs:

**Core Dependencies:**
- `libs.androidx.core.ktx` - AndroidX Core KTX extensions
- `libs.androidx.appcompat` - AppCompat support library
- `libs.material` - Material Design components
- `libs.androidx.activity` - Activity framework
- `libs.androidx.constraintlayout` - ConstraintLayout library
- `libs.jetbrains.kotlin.stdlib.jdk7` - Kotlin standard library
- `libs.androidx.recyclerview` - RecyclerView component

**Testing Dependencies:**
- `libs.junit` - Unit testing framework
- `libs.androidx.junit` - AndroidX JUnit extensions
- `libs.androidx.espresso.core` - UI testing framework

Sources: [Work-profile-codelab/app-starter/build.gradle.kts:57-69](), [Work-profile-codelab/app-finished/build.gradle.kts:57-69]()

## Configuration Synchronization

The version catalog system ensures that both sample applications maintain identical dependency versions, supporting the educational progression from starter to finished implementation:

| Configuration Aspect | Value | Location |
|---------------------|--------|----------|
| Compile SDK | 35 | Both modules |
| Target SDK | 35 | Both modules |
| Min SDK | 29 | Both modules |
| Java Compatibility | VERSION_11 | Both modules |
| Kotlin JVM Target | "11" | Both modules |
| View Binding | true | Both modules |

**Module Configuration Alignment**

```mermaid
graph LR
    subgraph "Shared Configuration"
        SDK_CONFIG["compileSdk: 35<br/>targetSdk: 35<br/>minSdk: 29"]
        JAVA_CONFIG["Java VERSION_11<br/>Kotlin JVM Target: '11'"]
        FEATURES["viewBinding: true"]
    end
    
    subgraph "app-starter Module"
        STARTER_CONFIG["android { } block<br/>Lines 22-55"]
    end
    
    subgraph "app-finished Module"
        FINISHED_CONFIG["android { } block<br/>Lines 22-55"]
    end
    
    SDK_CONFIG --> STARTER_CONFIG
    JAVA_CONFIG --> STARTER_CONFIG
    FEATURES --> STARTER_CONFIG
    
    SDK_CONFIG --> FINISHED_CONFIG
    JAVA_CONFIG --> FINISHED_CONFIG
    FEATURES --> FINISHED_CONFIG
```

Sources: [Work-profile-codelab/app-starter/build.gradle.kts:22-55](), [Work-profile-codelab/app-finished/build.gradle.kts:22-55]()

## Gradle Configuration Properties

The project utilizes specific Gradle properties to optimize build performance and enable modern Android development features:

**Build Optimization Properties:**
- `org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8` - JVM memory allocation
- `android.useAndroidX=true` - AndroidX library usage
- `android.nonTransitiveRClass=true` - R class optimization
- `kotlin.code.style=official` - Kotlin code style enforcement

Sources: [Work-profile-codelab/gradle.properties:9-23]()

## Gradle Wrapper Integration

The version catalog system integrates with the Gradle wrapper configuration to ensure consistent build environments:

**Wrapper Configuration:**
- Distribution URL: `gradle-8.10.2-bin.zip`
- Distribution Base: `GRADLE_USER_HOME`
- Storage Path: `wrapper/dists`

Sources: [Work-profile-codelab/gradle/wrapper/gradle-wrapper.properties:1-6]()

---

