<!-- source: DeepWiki mcp.deepwiki.com · repo android/health-samples · page 6 Build System and Dependencies · fetched 2026-10-23 -->

# Build System and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [health-connect/HealthConnectSample/app/build.gradle](health-connect/HealthConnectSample/app/build.gradle)
- [health-connect/HealthConnectSample/build.gradle](health-connect/HealthConnectSample/build.gradle)
- [health-connect/HealthConnectSample/gradle/wrapper/gradle-wrapper.properties](health-connect/HealthConnectSample/gradle/wrapper/gradle-wrapper.properties)
- [health-platform-v1/HealthPlatformSample/app/build.gradle](health-platform-v1/HealthPlatformSample/app/build.gradle)
- [health-platform-v1/HealthPlatformSample/build.gradle](health-platform-v1/HealthPlatformSample/build.gradle)
- [health-platform-v1/HealthPlatformSample/gradle/wrapper/gradle-wrapper.properties](health-platform-v1/HealthPlatformSample/gradle/wrapper/gradle-wrapper.properties)
- [health-services/ExerciseSampleCompose/gradle/libs.versions.toml](health-services/ExerciseSampleCompose/gradle/libs.versions.toml)
- [health-services/ExerciseSampleCompose/gradle/wrapper/gradle-wrapper.properties](health-services/ExerciseSampleCompose/gradle/wrapper/gradle-wrapper.properties)
- [health-services/MeasureDataCompose/gradle/libs.versions.toml](health-services/MeasureDataCompose/gradle/libs.versions.toml)
- [health-services/MeasureDataCompose/gradle/wrapper/gradle-wrapper.properties](health-services/MeasureDataCompose/gradle/wrapper/gradle-wrapper.properties)
- [health-services/PassiveDataCompose/gradle/libs.versions.toml](health-services/PassiveDataCompose/gradle/libs.versions.toml)
- [health-services/PassiveDataCompose/gradle/wrapper/gradle-wrapper.properties](health-services/PassiveDataCompose/gradle/wrapper/gradle-wrapper.properties)
- [health-services/PassiveGoalsCompose/gradle/libs.versions.toml](health-services/PassiveGoalsCompose/gradle/libs.versions.toml)
- [health-services/PassiveGoalsCompose/gradle/wrapper/gradle-wrapper.properties](health-services/PassiveGoalsCompose/gradle/wrapper/gradle-wrapper.properties)

</details>



This document describes the build system and dependency management strategy for the `android/health-samples` repository. It covers the use of Gradle, version catalogs, plugin configuration, dependency update automation, and the Gradle wrapper setup across the various sample applications. The focus is on how the repository ensures consistent, reproducible builds and manages dependencies for all health sample projects.

For information about continuous integration, code formatting, and artifact management, see [CI/CD and Quality Assurance](#7). For details on dependency update automation and version constraints, see [Dependency Automation](#6.2). For architectural patterns and best practices, see [Common Patterns and Best Practices](#8).

---

## Purpose and Scope

This page documents:

- The structure and configuration of the Gradle build system across all sample applications.
- The use of version catalogs (`libs.versions.toml`) for dependency and plugin version management.
- The Gradle wrapper configuration and versioning.
- The relationship between build files and sample modules.
- How dependency versions are kept up to date and consistent.

This page does **not** cover CI workflow details, code formatting, or code review processes.

---

## Overview of the Build System

The repository uses Gradle as the build system for all sample applications. Each sample is either a standalone Gradle project or a subproject within a multi-module structure. The build system is designed for:

- Consistency: Centralized version management using version catalogs.
- Reproducibility: Use of the Gradle wrapper to pin build tool versions.
- Maintainability: Automated dependency updates and clear plugin configuration.

### Diagram: Build System Structure and Key Files

```mermaid
flowchart TB
    subgraph "RepositoryRoot"
        direction TB
        "health-services/ExerciseSampleCompose/gradle/libs.versions.toml"["libs.versions.toml"]
        "health-services/ExerciseSampleCompose/gradle/wrapper/gradle-wrapper.properties"["gradle-wrapper.properties"]
        "health-services/ExerciseSampleCompose/build.gradle"[build.gradle]
        "health-services/ExerciseSampleCompose/app/build.gradle"["app/build.gradle"]
        "health-services/MeasureDataCompose/gradle/libs.versions.toml"["libs.versions.toml"]
        "health-services/MeasureDataCompose/gradle/wrapper/gradle-wrapper.properties"["gradle-wrapper.properties"]
        "health-services/MeasureDataCompose/build.gradle"[build.gradle]
        "health-services/PassiveDataCompose/gradle/libs.versions.toml"["libs.versions.toml"]
        "health-services/PassiveDataCompose/gradle/wrapper/gradle-wrapper.properties"["gradle-wrapper.properties"]
        "health-services/PassiveGoalsCompose/gradle/libs.versions.toml"["libs.versions.toml"]
        "health-services/PassiveGoalsCompose/gradle/wrapper/gradle-wrapper.properties"["gradle-wrapper.properties"]
        "health-connect/HealthConnectSample/build.gradle"["build.gradle"]
        "health-connect/HealthConnectSample/app/build.gradle"["app/build.gradle"]
        "health-connect/HealthConnectSample/gradle/wrapper/gradle-wrapper.properties"["gradle-wrapper.properties"]
        "health-platform-v1/HealthPlatformSample/build.gradle"["build.gradle"]
        "health-platform-v1/HealthPlatformSample/app/build.gradle"["app/build.gradle"]
        "health-platform-v1/HealthPlatformSample/gradle/wrapper/gradle-wrapper.properties"["gradle-wrapper.properties"]
    end
    "libs.versions.toml" -- "Defines versions for dependencies/plugins" --> "build.gradle"
    "gradle-wrapper.properties" -- "Pins Gradle version" --> "build.gradle"
    "build.gradle" -- "Configures project-wide plugins" --> "app/build.gradle"
    "app/build.gradle" -- "Defines app module dependencies" --> "Sample Application"
```
Sources:  
- [health-services/ExerciseSampleCompose/gradle/libs.versions.toml:1-74]()
- [health-services/ExerciseSampleCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/MeasureDataCompose/gradle/libs.versions.toml:1-39]()
- [health-services/MeasureDataCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/PassiveDataCompose/gradle/libs.versions.toml:1-38]()
- [health-services/PassiveDataCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/PassiveGoalsCompose/gradle/libs.versions.toml:1-44]()
- [health-services/PassiveGoalsCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-connect/HealthConnectSample/build.gradle:1-60]()
- [health-connect/HealthConnectSample/app/build.gradle:1-101]()
- [health-connect/HealthConnectSample/gradle/wrapper/gradle-wrapper.properties:1-24]()
- [health-platform-v1/HealthPlatformSample/build.gradle:1-44]()
- [health-platform-v1/HealthPlatformSample/app/build.gradle:1-101]()
- [health-platform-v1/HealthPlatformSample/gradle/wrapper/gradle-wrapper.properties:1-8]()

---

## Gradle Wrapper Configuration

Each sample project includes a `gradle-wrapper.properties` file to ensure builds use a specific, tested version of Gradle. This guarantees reproducibility across different environments and CI systems.

| Sample Project                | Gradle Version (as of latest commit) |
|-------------------------------|--------------------------------------|
| ExerciseSampleCompose         | 8.14.2                              |
| MeasureDataCompose            | 8.10.2                              |
| PassiveDataCompose            | 8.10.2                              |
| PassiveGoalsCompose           | 8.10.2                              |
| HealthConnectSample           | 8.10.2                              |
| HealthPlatformSample          | 8.10.2                              |

The Gradle wrapper is invoked via `./gradlew` and downloads the specified version if not already present.

Sources:  
- [health-services/ExerciseSampleCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/MeasureDataCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/PassiveDataCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/PassiveGoalsCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-connect/HealthConnectSample/gradle/wrapper/gradle-wrapper.properties:1-24]()
- [health-platform-v1/HealthPlatformSample/gradle/wrapper/gradle-wrapper.properties:1-8]()

---

## Version Catalogs and Dependency Management

Most Wear OS samples use [libs.versions.toml](#6.1) files to centralize dependency and plugin versions. This approach:

- Reduces duplication across modules.
- Simplifies upgrades and dependency consistency.
- Enables referencing versions by symbolic names in build scripts.

### Example: Key Sections in `libs.versions.toml`

- `[versions]`: Defines version numbers for libraries and plugins.
- `[libraries]`: Maps logical names to Maven coordinates and version references.
- `[plugins]`: Maps plugin IDs to version references.

#### Table: Example Entries from `libs.versions.toml`

| Section      | Key                        | Value/Reference                        |
|--------------|----------------------------|----------------------------------------|
| [versions]   | androidx-wear-compose      | "1.5.0-beta04"                         |
| [libraries]  | androidx-health-services   | module = "androidx.health:health-services-client", version.ref = "health-services" |
| [plugins]    | com-android-application    | id = "com.android.application", version.ref = "android-gradle-plugin" |

Sources:  
- [health-services/ExerciseSampleCompose/gradle/libs.versions.toml:1-74]()
- [health-services/MeasureDataCompose/gradle/libs.versions.toml:1-39]()
- [health-services/PassiveDataCompose/gradle/libs.versions.toml:1-38]()
- [health-services/PassiveGoalsCompose/gradle/libs.versions.toml:1-44]()

---

## Build File Structure and Plugin Application

Each sample project typically contains:

- A root `build.gradle` (or `build.gradle.kts`) for project-wide configuration.
- An `app/build.gradle` for the main application module.

Plugins are applied either via the version catalog or directly in the build files. Common plugins include:

- `com.android.application`
- `org.jetbrains.kotlin.android`
- `com.google.dagger.hilt.android` (for samples using Hilt)
- `com.diffplug.spotless` (for code formatting)
- `io.github.takahirom.roborazzi` (for screenshot testing in ExerciseSampleCompose)

### Diagram: Plugin and Dependency Flow

```mermaid
flowchart TD
    "libs.versions.toml"["libs.versions.toml"]
    "build.gradle"["build.gradle"]
    "app/build.gradle"["app/build.gradle"]
    "com-android-application"["com.android.application"]
    "org-jetbrains-kotlin-android"["org.jetbrains.kotlin.android"]
    "dagger-hilt"["com.google.dagger.hilt.android"]
    "spotless"["com.diffplug.spotless"]
    "roborazzi"["io.github.takahirom.roborazzi"]

    "libs.versions.toml" -- "Defines plugin versions" --> "build.gradle"
    "build.gradle" -- "Applies plugins" --> "app/build.gradle"
    "app/build.gradle" -- "Uses plugins" --> "com-android-application"
    "app/build.gradle" -- "Uses plugins" --> "org-jetbrains-kotlin-android"
    "app/build.gradle" -- "Uses plugins" --> "dagger-hilt"
    "build.gradle" -- "Applies formatting" --> "spotless"
    "app/build.gradle" -- "Screenshot testing" --> "roborazzi"
```
Sources:  
- [health-services/ExerciseSampleCompose/gradle/libs.versions.toml:65-71]()
- [health-services/ExerciseSampleCompose/build.gradle:1-60]()
- [health-services/ExerciseSampleCompose/app/build.gradle:1-101]()
- [health-connect/HealthConnectSample/build.gradle:1-60]()
- [health-connect/HealthConnectSample/app/build.gradle:1-101]()

---

## Dependency Versioning and Consistency

Dependency versions are managed in one of two ways:

- **Version Catalogs (`libs.versions.toml`)**: Used in most Wear OS samples for both libraries and plugins.
- **Gradle Properties/Ext Variables**: Used in HealthConnectSample and HealthPlatformSample, where versions are defined in the root `build.gradle` using `ext` properties and referenced in `app/build.gradle`.

This ensures that all modules within a sample use the same versions for critical dependencies such as Compose, Health Services, Health Connect, and Hilt.

### Table: Example Version References

| Sample                  | Compose Version Reference         | Health API Version Reference         | Kotlin Version Reference      |
|-------------------------|----------------------------------|--------------------------------------|------------------------------|
| ExerciseSampleCompose   | `androidx-compose` in `[versions]`| `health-services` in `[versions]`    | `kotlin` in `[versions]`     |
| MeasureDataCompose      | `compose` in `[versions]`         | `health-services` in `[versions]`    | `org-jetbrains-kotlin`       |
| HealthConnectSample     | `composeBom` in `app/build.gradle`| `health_connect_version` in `ext`    | `kotlin_version` in `ext`    |
| HealthPlatformSample    | `composeBom` in `app/build.gradle`| `health_platform_version` in `ext`   | `kotlin_version` in `ext`    |

Sources:  
- [health-services/ExerciseSampleCompose/gradle/libs.versions.toml:1-74]()
- [health-services/MeasureDataCompose/gradle/libs.versions.toml:1-39]()
- [health-connect/HealthConnectSample/build.gradle:17-39]()
- [health-connect/HealthConnectSample/app/build.gradle:66-100]()
- [health-platform-v1/HealthPlatformSample/build.gradle:17-39]()
- [health-platform-v1/HealthPlatformSample/app/build.gradle:71-100]()

---

## Build Features and Compiler Options

All samples enable Jetpack Compose via the `buildFeatures` block and specify the Compose compiler extension version. Java 17 is used as the source and target compatibility for all modules. Desugaring is enabled where required for Java 8+ APIs on lower API levels.

Example configuration (see code for details):

- `buildFeatures { compose true }`
- `composeOptions { kotlinCompilerExtensionVersion = "1.5.15" }`
- `compileOptions { sourceCompatibility JavaVersion.VERSION_17 }`
- `coreLibraryDesugaringEnabled true` (for minSdk < 26)

Sources:  
- [health-connect/HealthConnectSample/app/build.gradle:52-57]()
- [health-platform-v1/HealthPlatformSample/app/build.gradle:58-63]()

---

## Relationship to Dependency Automation

Automated dependency updates and version constraints are handled by Renovate Bot and package rules, which are described in detail in [Dependency Automation](#6.2).

---

## Summary Table: Build System Components by Sample

| Sample                  | Build System | Version Catalog | Gradle Wrapper | Plugin Management | Dependency Versioning |
|-------------------------|-------------|----------------|---------------|------------------|----------------------|
| ExerciseSampleCompose   | Gradle      | Yes            | 8.14.2        | Catalog/Direct   | `libs.versions.toml` |
| MeasureDataCompose      | Gradle      | Yes            | 8.10.2        | Catalog/Direct   | `libs.versions.toml` |
| PassiveDataCompose      | Gradle      | Yes            | 8.10.2        | Catalog/Direct   | `libs.versions.toml` |
| PassiveGoalsCompose     | Gradle      | Yes            | 8.10.2        | Catalog/Direct   | `libs.versions.toml` |
| HealthConnectSample     | Gradle      | No             | 8.10.2        | Direct           | `ext` in build.gradle|
| HealthPlatformSample    | Gradle      | No             | 8.10.2        | Direct           | `ext` in build.gradle|

Sources:  
- [health-services/ExerciseSampleCompose/gradle/libs.versions.toml:1-74]()
- [health-services/ExerciseSampleCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/MeasureDataCompose/gradle/libs.versions.toml:1-39]()
- [health-services/MeasureDataCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/PassiveDataCompose/gradle/libs.versions.toml:1-38]()
- [health-services/PassiveDataCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/PassiveGoalsCompose/gradle/libs.versions.toml:1-44]()
- [health-services/PassiveGoalsCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-connect/HealthConnectSample/build.gradle:1-60]()
- [health-connect/HealthConnectSample/app/build.gradle:1-101]()
- [health-connect/HealthConnectSample/gradle/wrapper/gradle-wrapper.properties:1-24]()
- [health-platform-v1/HealthPlatformSample/build.gradle:1-44]()
- [health-platform-v1/HealthPlatformSample/app/build.gradle:1-101]()
- [health-platform-v1/HealthPlatformSample/gradle/wrapper/gradle-wrapper.properties:1-8]()

---

## Diagram: Mapping Sample Names to Build Files

```mermaid
graph TD
    "ExerciseSampleCompose"["ExerciseSampleCompose"]
    "MeasureDataCompose"["MeasureDataCompose"]
    "PassiveDataCompose"["PassiveDataCompose"]
    "PassiveGoalsCompose"["PassiveGoalsCompose"]
    "HealthConnectSample"["HealthConnectSample"]
    "HealthPlatformSample"["HealthPlatformSample"]

    "ExerciseSampleCompose" -- "libs.versions.toml" --> "health-services/ExerciseSampleCompose/gradle/libs.versions.toml"
    "ExerciseSampleCompose" -- "gradle-wrapper.properties" --> "health-services/ExerciseSampleCompose/gradle/wrapper/gradle-wrapper.properties"
    "ExerciseSampleCompose" -- "build.gradle" --> "health-services/ExerciseSampleCompose/build.gradle"
    "ExerciseSampleCompose" -- "app/build.gradle" --> "health-services/ExerciseSampleCompose/app/build.gradle"

    "MeasureDataCompose" -- "libs.versions.toml" --> "health-services/MeasureDataCompose/gradle/libs.versions.toml"
    "MeasureDataCompose" -- "gradle-wrapper.properties" --> "health-services/MeasureDataCompose/gradle/wrapper/gradle-wrapper.properties"
    "MeasureDataCompose" -- "build.gradle" --> "health-services/MeasureDataCompose/build.gradle"

    "PassiveDataCompose" -- "libs.versions.toml" --> "health-services/PassiveDataCompose/gradle/libs.versions.toml"
    "PassiveDataCompose" -- "gradle-wrapper.properties" --> "health-services/PassiveDataCompose/gradle/wrapper/gradle-wrapper.properties"
    "PassiveDataCompose" -- "build.gradle" --> "health-services/PassiveDataCompose/build.gradle"

    "PassiveGoalsCompose" -- "libs.versions.toml" --> "health-services/PassiveGoalsCompose/gradle/libs.versions.toml"
    "PassiveGoalsCompose" -- "gradle-wrapper.properties" --> "health-services/PassiveGoalsCompose/gradle/wrapper/gradle-wrapper.properties"
    "PassiveGoalsCompose" -- "build.gradle" --> "health-services/PassiveGoalsCompose/build.gradle"

    "HealthConnectSample" -- "build.gradle" --> "health-connect/HealthConnectSample/build.gradle"
    "HealthConnectSample" -- "app/build.gradle" --> "health-connect/HealthConnectSample/app/build.gradle"
    "HealthConnectSample" -- "gradle-wrapper.properties" --> "health-connect/HealthConnectSample/gradle/wrapper/gradle-wrapper.properties"

    "HealthPlatformSample" -- "build.gradle" --> "health-platform-v1/HealthPlatformSample/build.gradle"
    "HealthPlatformSample" -- "app/build.gradle" --> "health-platform-v1/HealthPlatformSample/app/build.gradle"
    "HealthPlatformSample" -- "gradle-wrapper.properties" --> "health-platform-v1/HealthPlatformSample/gradle/wrapper/gradle-wrapper.properties"
```
Sources:  
- [health-services/ExerciseSampleCompose/gradle/libs.versions.toml:1-74]()
- [health-services/ExerciseSampleCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/ExerciseSampleCompose/build.gradle:1-60]()
- [health-services/ExerciseSampleCompose/app/build.gradle:1-101]()
- [health-services/MeasureDataCompose/gradle/libs.versions.toml:1-39]()
- [health-services/MeasureDataCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/MeasureDataCompose/build.gradle:1-60]()
- [health-services/PassiveDataCompose/gradle/libs.versions.toml:1-38]()
- [health-services/PassiveDataCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/PassiveDataCompose/build.gradle:1-60]()
- [health-services/PassiveGoalsCompose/gradle/libs.versions.toml:1-44]()
- [health-services/PassiveGoalsCompose/gradle/wrapper/gradle-wrapper.properties:1-8]()
- [health-services/PassiveGoalsCompose/build.gradle:1-60]()
- [health-connect/HealthConnectSample/build.gradle:1-60]()
- [health-connect/HealthConnectSample/app/build.gradle:1-101]()
- [health-connect/HealthConnectSample/gradle/wrapper/gradle-wrapper.properties:1-24]()
- [health-platform-v1/HealthPlatformSample/build.gradle:1-44]()
- [health-platform-v1/HealthPlatformSample/app/build.gradle:1-101]()
- [health-platform-v1/HealthPlatformSample/gradle/wrapper/gradle-wrapper.properties:1-8]()

---

## See Also

- [Version Catalogs](#6.1) for details on the structure and usage of `libs.versions.toml`.
- [Dependency Automation](#6.2) for information on Renovate Bot, package rules, and version constraints.
- [CI/CD and Quality Assurance](#7) for build, test, and artifact workflows.

---

---

