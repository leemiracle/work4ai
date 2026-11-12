<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-boot · page 4 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/build.gradle](app/build.gradle)
- [app/testkey_untrusted.jks](app/testkey_untrusted.jks)
- [build.gradle](build.gradle)

</details>



This document covers the Android build configuration, Gradle setup, and compilation process for the Termux:Boot application. It explains how the project is structured for building APK files using the Android Gradle Plugin and Gradle wrapper system.

For information about the continuous integration workflows that automate this build system, see [Continuous Integration](#5.1). For details about the Android application components that are built by this system, see [Android Application Structure](#3.1).

## Build System Architecture

The Termux:Boot build system follows the standard Android Gradle Plugin architecture with a two-level configuration approach: a top-level project configuration and an application-specific module configuration.

### Build Configuration Structure

```mermaid
graph TB
    subgraph "Project Root"
        TBG["build.gradle<br/>Top-level configuration"]
        GP["gradle.properties<br/>Global properties"]
        GWP["gradle/wrapper/<br/>gradle-wrapper.properties"]
        GWJ["gradle/wrapper/<br/>gradle-wrapper.jar"]
    end
    
    subgraph "app/ Module"
        ABG["app/build.gradle<br/>Application configuration"]
        TKU["app/testkey_untrusted.jks<br/>Debug signing keystore"]
        PRO["app/proguard-rules.pro<br/>Obfuscation rules"]
    end
    
    subgraph "Build Outputs"
        APK["termux-boot-app_*.apk<br/>Application package"]
        MAP["mapping.txt<br/>ProGuard mappings"]
    end
    
    TBG -->|"Applies Android Gradle Plugin"| ABG
    GP -->|"Configures build properties"| ABG
    GWP -->|"Defines Gradle version"| GWJ
    GWJ -->|"Bootstraps build"| TBG
    
    ABG -->|"Compiles and packages"| APK
    TKU -->|"Signs debug builds"| APK
    PRO -->|"Minimizes release builds"| MAP
    MAP -->|"Included with"| APK
```

Sources: [build.gradle:1-18](), [app/build.gradle:1-72]()

### Build Dependencies and Plugin Configuration

The build system is anchored by the Android Gradle Plugin version `8.3.2` declared in the top-level `build.gradle`. This plugin provides the Android-specific build tasks and configurations needed to compile Java source code into Android APK packages.

```mermaid
graph LR
    subgraph "External Dependencies"
        AGP["com.android.tools.build:gradle:8.3.2<br/>Android Gradle Plugin"]
        AX["androidx.annotation:annotation:1.7.0<br/>AndroidX Annotations"]
        MC["mavenCentral()<br/>Maven repository"]
        GR["google()<br/>Google repository"]
    end
    
    subgraph "Build Configuration"
        BC["buildscript.dependencies"]
        AR["allprojects.repositories"]
        AD["app.dependencies"]
    end
    
    subgraph "Application Build"
        CP["com.android.application<br/>Plugin application"]
        CC["Compile classes"]
        PA["Package APK"]
    end
    
    MC -->|"Provides"| AGP
    GR -->|"Provides"| AGP
    GR -->|"Provides"| AX
    
    BC -->|"Declares"| AGP
    AR -->|"Configures"| MC
    AR -->|"Configures"| GR
    AD -->|"Implements"| AX
    
    AGP -->|"Enables"| CP
    CP -->|"Executes"| CC
    CC -->|"Produces"| PA
```

Sources: [build.gradle:1-18](), [app/build.gradle:56-58]()

## Application Build Configuration

The core build logic resides in [app/build.gradle:1-72](), which configures the Android application module with specific settings for the Termux:Boot app.

### Application Identity and Versioning

The application is configured with a fixed identity and semantic versioning system:

| Configuration | Value | Source |
|---------------|-------|---------|
| `applicationId` | `"com.termux.boot"` | [app/build.gradle:12]() |
| `namespace` | `"com.termux.boot"` | [app/build.gradle:4]() |
| `versionCode` | `1000` | [app/build.gradle:15]() |
| `versionName` | `"0.8.1"` (default) | [app/build.gradle:16]() |

The version name can be overridden by the environment variable `TERMUX_BOOT_APP_BUILD__APP_VERSION_NAME` for CI/CD builds, and the system includes semantic version validation via the `validateVersionName()` function at [app/build.gradle:66-71]().

### SDK Version Configuration

The build targets a wide range of Android devices through dynamic SDK version configuration:

```mermaid
graph LR
    subgraph "SDK Configuration"
        MIN["minSdk<br/>project.properties.minSdkVersion"]
        TARGET["targetSdk<br/>project.properties.targetSdkVersion"] 
        COMPILE["compileSdk<br/>project.properties.compileSdkVersion"]
    end
    
    subgraph "Runtime Properties"
        PROPS["project.properties<br/>External configuration"]
    end
    
    subgraph "Build Configuration"
        DEF["defaultConfig<br/>app/build.gradle"]
        AND["android block<br/>app/build.gradle"]
    end
    
    PROPS -->|"Provides values"| MIN
    PROPS -->|"Provides values"| TARGET
    PROPS -->|"Provides values"| COMPILE
    
    MIN -->|"Sets minimum API"| DEF
    TARGET -->|"Sets target API"| DEF
    COMPILE -->|"Sets compile API"| AND
```

Sources: [app/build.gradle:6](), [app/build.gradle:13-14]()

### Build Types and Signing Configuration

The application defines two build types with distinct configurations:

#### Debug Build Type
- Uses custom signing configuration with `testkey_untrusted.jks`
- Keystore password: `xrj45yWGLbsO7W0v`
- Key alias: `alias`
- No code obfuscation

#### Release Build Type  
- Enables ProGuard minification (`minifyEnabled true`)
- Enables resource shrinking (`shrinkResources true`)
- Uses default ProGuard configuration plus custom rules from `proguard-rules.pro`

```mermaid
graph TB
    subgraph "Signing Configuration"
        TKU["testkey_untrusted.jks<br/>Debug keystore"]
        SC["signingConfigs.debug<br/>Configuration block"]
    end
    
    subgraph "Build Types"
        DBT["debug<br/>Build type"]
        RBT["release<br/>Build type"]
    end
    
    subgraph "Output Processing"
        MIN["minifyEnabled: true"]
        SHR["shrinkResources: true"]
        PRO["proguard-rules.pro"]
    end
    
    TKU -->|"Stores key material"| SC
    SC -->|"Applied to"| DBT
    
    RBT -->|"Enables"| MIN
    RBT -->|"Enables"| SHR
    RBT -->|"Uses"| PRO
```

Sources: [app/build.gradle:22-41]()

### APK Output Naming

The build system generates APK files with descriptive names using the `applicationVariants.all` configuration block. The naming pattern follows:

```
termux-boot-app_[VERSION_TAG].apk
```

Where `VERSION_TAG` is either:
- Environment variable `TERMUX_BOOT_APP_BUILD__APK_VERSION_TAG` (for CI builds)
- `v[versionName]+[buildType]` (for local builds)

This configuration is implemented in [app/build.gradle:48-53]().

### Custom Gradle Tasks

The build includes a custom `versionName` task that outputs the current version name for use in automation scripts:

```mermaid
graph LR
    subgraph "Custom Tasks"
        VNT["versionName task<br/>line 60-64"]
    end
    
    subgraph "Configuration Access"
        DC["android.defaultConfig<br/>Version source"]
        VN["versionName property<br/>String output"]
    end
    
    subgraph "Build Automation"
        CI["CI/CD scripts<br/>External consumers"]
    end
    
    VNT -->|"Reads from"| DC
    DC -->|"Provides"| VN
    VNT -->|"Prints"| VN
    VN -->|"Consumed by"| CI
```

Sources: [app/build.gradle:60-64]()

## Project-Level Configuration

The top-level [build.gradle:1-18]() provides the foundation for the entire build system by configuring the Android Gradle Plugin and repository access.

### Plugin Management
The `buildscript` block declares the Android Gradle Plugin dependency (`com.android.tools.build:gradle:8.3.2`) and configures the repositories needed to resolve build dependencies.

### Repository Configuration
Both `buildscript` and `allprojects` blocks configure identical repository access:
- `mavenCentral()` for general Java/Kotlin dependencies
- `google()` for Android-specific artifacts and Google Play services

This dual configuration ensures that both build plugins and application dependencies can be resolved during the build process.

Sources: [build.gradle:1-18]()

---

