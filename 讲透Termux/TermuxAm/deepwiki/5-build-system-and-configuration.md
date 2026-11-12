<!-- source: DeepWiki mcp.deepwiki.com · repo termux/TermuxAm · page 5 Build System and Configuration · fetched 2026-10-26 -->

# Build System and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/build.gradle](app/build.gradle)
- [build.gradle](build.gradle)
- [gradle/wrapper/gradle-wrapper.properties](gradle/wrapper/gradle-wrapper.properties)

</details>



This document covers the build system configuration that enables TermuxAm to compile and access Android's hidden APIs. The build configuration is specifically designed to bypass Android's API restrictions while maintaining compatibility across Android versions.

For information about the compiled application components, see [Core Application Components](#4). For deployment and packaging details, see [Entry Points and Execution](#3).

## Overview

The TermuxAm build system uses a carefully configured Android Gradle build to enable access to restricted Android APIs. The configuration centers around maintaining a `targetSdkVersion` of 27 and integrating the HiddenApiBypass library to work around Android's hidden API restrictions introduced in Android 9 (API 28).

### Build Architecture

```mermaid
graph TB
    subgraph "Root Configuration"
        RBG["build.gradle<br/>Root Project"]
        GWP["gradle-wrapper.properties<br/>Gradle 7.5"]
    end
    
    subgraph "Application Configuration"
        ABG["app/build.gradle<br/>Main Build Config"]
        TSD["targetSdkVersion 27<br/>Hidden API Access"]
        HAB["HiddenApiBypass:4.3<br/>API Bypass Library"]
    end
    
    subgraph "Build Outputs"
        APK["TermuxAm APK<br/>Compiled Application"]
        TESTS["Instrumented Tests<br/>AndroidJUnitRunner"]
    end
    
    RBG --> ABG
    GWP --> ABG
    ABG --> TSD
    ABG --> HAB
    ABG --> APK
    ABG --> TESTS
    
    TSD --> APK
    HAB --> APK
```

**Sources:** [app/build.gradle:1-41](), [build.gradle:1-21](), [gradle/wrapper/gradle-wrapper.properties:1-6]()

## Application Build Configuration

The core build configuration in `app/build.gradle` contains critical settings that enable hidden API access and ensure compatibility with Android's security restrictions.

### Android Configuration Block

The `android` configuration block defines the application's compilation and runtime parameters:

| Setting | Value | Purpose |
|---------|-------|---------|
| `namespace` | `"com.termux.termuxam"` | Application package namespace |
| `compileSdkVersion` | `33` | Latest SDK for compilation |
| `minSdkVersion` | `21` | Android 5.0+ compatibility |
| `targetSdkVersion` | `27` | **Critical for hidden API access** |
| `applicationId` | `"com.termux.termuxam"` | Unique application identifier |

The `targetSdkVersion` setting is the most critical configuration, as explained in the inline comment at [app/build.gradle:9-14]():

```
// Note: targetSdkVersion affects only tests,
//       normally, even though this is packaged as apk,
//       it's not loaded as apk so targetSdkVersion is ignored.
//       targetSdkVersion this must be < 28 because this application accesses hidden apis
```

**Sources:** [app/build.gradle:3-20]()

### Hidden API Access Configuration

```mermaid
graph LR
    subgraph "API Restrictions"
        API28["Android 9+ (API 28)<br/>Hidden API Restrictions"]
        HAR["Hidden API Reflection<br/>Blocked by Default"]
    end
    
    subgraph "Bypass Strategy"
        TSD["targetSdkVersion 27<br/>Legacy Behavior"]
        HAB["HiddenApiBypass Library<br/>v4.3"]
    end
    
    subgraph "Application Access"
        IAM["IActivityManager<br/>Reflection Access"]
        AMS["ActivityManagerService<br/>Hidden APIs"]
    end
    
    API28 --> HAR
    HAR --> TSD
    HAR --> HAB
    TSD --> IAM
    HAB --> IAM
    IAM --> AMS
```

The application uses two complementary strategies to access hidden APIs:

1. **Legacy targetSdkVersion**: Set to 27 to avoid Android 9's hidden API restrictions
2. **HiddenApiBypass Library**: Runtime bypass for additional protection

The HiddenApiBypass dependency is configured at [app/build.gradle:38-39]():
```gradle
// https://github.com/LSPosed/AndroidHiddenApiBypass
implementation "org.lsposed.hiddenapibypass:hiddenapibypass:4.3"
```

**Sources:** [app/build.gradle:12-14](), [app/build.gradle:38-39]()

### Build Types and Testing

The build configuration includes standard Android build types and comprehensive testing support:

```mermaid
graph TB
    subgraph "Build Types"
        REL["release<br/>minifyEnabled: false"]
        DBG["debug<br/>(implicit)"]
    end
    
    subgraph "Testing Configuration"
        TIR["testInstrumentationRunner<br/>AndroidJUnitRunner"]
        ATD["androidTestImplementation<br/>Test Dependencies"]
    end
    
    subgraph "Test Dependencies"
        TR["androidx.test:runner:1.5.2"]
        TJ["androidx.test.ext:junit:1.1.5"]
        ANN["androidx.annotation:annotation:1.7.1"]
    end
    
    REL --> TIR
    DBG --> TIR
    TIR --> ATD
    ATD --> TR
    ATD --> TJ
    ATD --> ANN
```

The release build type disables ProGuard minification at [app/build.gradle:22-27]() to preserve reflection-based access patterns required for hidden API usage.

**Sources:** [app/build.gradle:17](), [app/build.gradle:22-27](), [app/build.gradle:33-36]()

## Root Project Configuration

The root `build.gradle` file establishes the project-wide build environment and repository configuration.

### Buildscript Configuration

The buildscript block defines the Android Gradle Plugin version and repository sources:

```gradle
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath "com.android.tools.build:gradle:7.4.2"
    }
}
```

All projects inherit repository configuration from the `allprojects` block at [build.gradle:11-16](), ensuring consistent dependency resolution across modules.

**Sources:** [build.gradle:1-16]()

### Gradle Wrapper

The Gradle wrapper configuration ensures consistent build environments across different development machines:

| Property | Value | Purpose |
|----------|-------|---------|
| `distributionUrl` | `gradle-7.5-all.zip` | Gradle version 7.5 with full distribution |
| `distributionBase` | `GRADLE_USER_HOME` | Local Gradle cache location |

**Sources:** [gradle/wrapper/gradle-wrapper.properties:1-6]()

## Build Configuration Dependencies

```mermaid
graph TB
    subgraph "External Dependencies"
        GOOG["google()<br/>Repository"]
        MC["mavenCentral()<br/>Repository"]
        AGP["Android Gradle Plugin<br/>7.4.2"]
        HAB["HiddenApiBypass<br/>4.3"]
    end
    
    subgraph "Test Dependencies"
        ATR["AndroidX Test Runner<br/>1.5.2"]
        ATJ["AndroidX Test JUnit<br/>1.1.5"]
        ANN["AndroidX Annotation<br/>1.7.1"]
    end
    
    subgraph "Build Outputs"
        APK["TermuxAm APK<br/>Production Build"]
        TESTS["Test APK<br/>Instrumented Tests"]
    end
    
    GOOG --> AGP
    MC --> HAB
    MC --> ATR
    MC --> ATJ
    MC --> ANN
    
    AGP --> APK
    HAB --> APK
    ATR --> TESTS
    ATJ --> TESTS
    ANN --> APK
```

The dependency configuration prioritizes:
1. **Hidden API access** through HiddenApiBypass
2. **Comprehensive testing** with AndroidX test framework
3. **Minimal runtime dependencies** to reduce attack surface

**Sources:** [app/build.gradle:30-40](), [build.gradle:2-8](), [build.gradle:12-15]()

---

