<!-- source: DeepWiki mcp.deepwiki.com · repo android/uamp · page 6 Build System · fetched 2026-10-23 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/build.gradle](app/build.gradle)
- [app/src/main/java/com/example/android/uamp/fragments/MediaItemFragment.kt](app/src/main/java/com/example/android/uamp/fragments/MediaItemFragment.kt)
- [app/src/main/java/com/example/android/uamp/fragments/NowPlayingFragment.kt](app/src/main/java/com/example/android/uamp/fragments/NowPlayingFragment.kt)
- [automotive/src/main/java/com/example/android/uamp/automotive/SettingsFragment.kt](automotive/src/main/java/com/example/android/uamp/automotive/SettingsFragment.kt)
- [build.gradle](build.gradle)
- [common/build.gradle](common/build.gradle)
- [common/proguard-rules.pro](common/proguard-rules.pro)
- [common/src/test/java/com/example/android/uamp/media/library/MusicSourceTest.kt](common/src/test/java/com/example/android/uamp/media/library/MusicSourceTest.kt)
- [gradle.properties](gradle.properties)
- [gradle/wrapper/gradle-wrapper.properties](gradle/wrapper/gradle-wrapper.properties)

</details>



This document provides a comprehensive overview of the UAMP (Universal Android Music Player) build system, covering the project structure, Gradle configuration, module organization, and dependency management. For information about the overall architecture of the application, see [Architecture](#2).

## 1. Project Structure Overview

UAMP is organized as a multi-module Android project built with Gradle. The modular architecture enables code reuse and separation of concerns, with shared functionality in a common module and platform-specific implementations in separate modules.

```mermaid
graph TD
    subgraph "Project Structure"
        rootProject["Root Project"]
        app["app Module"]
        common["common Module"]
        automotive["automotive Module"]
        media["media Module (if present)"]
        
        rootProject --> app
        rootProject --> common
        rootProject --> automotive
        rootProject --> media
        
        app --> common
        automotive --> common
        media --> common
    end
    
    subgraph "Build Files"
        rootBuildGradle["build.gradle (root)"]
        appBuildGradle["app/build.gradle"]
        commonBuildGradle["common/build.gradle"]
        automotiveBuildGradle["automotive/build.gradle"]
        gradleProperties["gradle.properties"]
        gradleWrapper["gradle-wrapper.properties"]
    end
    
    rootProject --> rootBuildGradle
    app --> appBuildGradle
    common --> commonBuildGradle
    automotive --> automotiveBuildGradle
    rootProject --> gradleProperties
    rootProject --> gradleWrapper
```

Sources: [build.gradle](), [app/build.gradle](), [common/build.gradle](), [gradle.properties](), [gradle/wrapper/gradle-wrapper.properties]()

## 2. Gradle Configuration

UAMP uses Gradle as its build system with a specific version defined in the Gradle wrapper properties.

### 2.1 Gradle Wrapper

The project uses Gradle 6.1.1 as specified in the gradle-wrapper.properties file:

Sources: [gradle/wrapper/gradle-wrapper.properties:1-6]()

### 2.2 Root Build Configuration

The root build.gradle file defines project-wide configurations:

- SDK versions (compile, minimum, target)
- Dependency versions for the entire project
- Repository configurations (Google and Maven Central)
- Gradle and plugin versions

```mermaid
graph TD
    subgraph "Root build.gradle"
        sdkVersions["SDK Versions:<br>- compileSdkVersion: 30<br>- minSdkVersion: 19<br>- targetSdkVersion: 30"]
        dependencyVersions["Dependency Versions:<br>- androidx<br>- exoplayer<br>- kotlin<br>- etc."]
        buildscript["buildscript:<br>- repositories<br>- dependencies"]
        allprojects["allprojects:<br>- repositories"]
    end
    
    buildscript --> dependencyVersions
    buildscript --> repositories["repositories:<br>- google()<br>- mavenCentral()"]
    buildscript --> pluginDependencies["Plugin Dependencies:<br>- android gradle plugin<br>- kotlin gradle plugin<br>- strict-version-matcher"]
    
    allprojects --> repositories
```

Sources: [build.gradle:17-75]()

## 3. Module Structure and Configurations

### 3.1 Module Dependencies

The project is organized into multiple modules with specific dependencies:

```mermaid
graph TB
    subgraph "Module Dependencies"
        app["app<br>(Mobile UI)"]
        common["common<br>(Core Library)"]
        automotive["automotive<br>(Automotive UI)"]
        
        app -->|"implementation project(':common')"| common
        automotive -->|"implementation project(':common')"| common
        
        app -->|"implementation"| androidxDeps["AndroidX Dependencies:<br>- appcompat<br>- fragment-ktx<br>- recyclerview<br>- etc."]
        app -->|"implementation"| kotlinDeps["Kotlin Dependencies:<br>- kotlin-stdlib-jdk8"]
        app -->|"implementation"| glideDeps["Glide Dependencies:<br>- glide<br>- compiler (kapt)"]
        
        common -->|"api"| kotlinDeps2["Kotlin Dependencies:<br>- kotlin-stdlib-jdk8<br>- kotlinx-coroutines"]
        common -->|"api"| mediaLibs["Media Libraries:<br>- androidx.media<br>- exoplayer<br>- exoplayer extensions"]
        common -->|"api"| glideDeps
        common -->|"api"| gsonDep["Gson"]
    end
```

Sources: [app/build.gradle:60-77](), [common/build.gradle:48-82]()

### 3.2 App Module Configuration

The app module is configured as an Android application:

- Applies Android application plugin and Kotlin plugins
- Configures Android SDK versions from root project
- Enables view binding and data binding
- Defines build types with ProGuard settings
- Specifies dependencies on common module and external libraries

Sources: [app/build.gradle:17-77]()

### 3.3 Common Module Configuration

The common module is configured as an Android library:

- Applies Android library plugin and Kotlin plugins
- Configures SDK versions
- Sets up ExoPlayer dependencies with conditional logic
- Defines test configurations

```
common (library)
├── Core functionality
├── Media playback features
└── Shared resources
```

Sources: [common/build.gradle:17-82]()

## 4. Dependency Management

### 4.1 Centralized Version Management

UAMP employs a centralized approach to dependency version management using the `ext` block in the root build.gradle file:

```mermaid
graph TD
    subgraph "Dependency Version Management"
        rootBuildGradle["Root build.gradle"]
        extBlock["ext Block<br>Contains all version numbers"]
        
        moduleGradle["Module build.gradle files<br>(app, common, automotive)"]
        
        rootBuildGradle --> extBlock
        extBlock -->|"Reference with $variableName"| moduleGradle
        
        extBlock --> androidxVersions["AndroidX Versions:<br>- app_compat<br>- core_ktx<br>- media<br>- etc."]
        extBlock --> libraryVersions["Library Versions:<br>- exoplayer<br>- glide<br>- gson<br>- etc."]
        extBlock --> toolingVersions["Tooling Versions:<br>- kotlin<br>- gradle<br>- etc."]
    end
```

Sources: [build.gradle:20-50]()

### 4.2 ExoPlayer Dependency Logic

The common module has special logic for ExoPlayer dependencies:

- Checks if a local ExoPlayer project is available
- Uses local ExoPlayer modules if available, otherwise uses published artifacts

Sources: [common/build.gradle:58-73]()

## 5. Gradle Properties and Settings

The project contains several important Gradle settings in gradle.properties:

- `android.useAndroidX=true`: Enables AndroidX libraries
- `android.enableJetifier=true`: Enables translation of support libraries to AndroidX
- `org.gradle.jvmargs=-Xmx1536m`: Sets memory allocation for Gradle daemon

Sources: [gradle.properties:16-32]()

## 6. Build Features and Customizations

### 6.1 View Binding and Data Binding

The app module enables both view binding and data binding for easier UI implementation:

```mermaid
graph TD
    subgraph "Data and View Binding"
        buildFeatures["buildFeatures Block<br>in app/build.gradle"]
        viewBinding["viewBinding = true"]
        dataBinding["dataBinding = true"]
        
        buildFeatures --> viewBinding
        buildFeatures --> dataBinding
        
        viewBinding --> bindingUsage["Used in Fragments:<br>- MediaItemFragment<br>- NowPlayingFragment"]
    end
```

Sources: [app/build.gradle:47-50](), [app/src/main/java/com/example/android/uamp/fragments/MediaItemFragment.kt:36-68](), [app/src/main/java/com/example/android/uamp/fragments/NowPlayingFragment.kt:39-59]()

### 6.2 ProGuard Configuration

The project has basic ProGuard settings for release builds. The common module includes a proguard-rules.pro file with default rules.

Sources: [app/build.gradle:52-57](), [common/proguard-rules.pro:1-22]()

## 7. Build Process Overview

The following diagram illustrates the high-level build process flow:

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Gradle as "Gradle Build System"
    participant Modules as "Project Modules"
    participant Artifacts as "Build Artifacts"
    
    Dev->>Gradle: ./gradlew assembleDebug
    
    Gradle->>Gradle: Process root build.gradle
    Gradle->>Gradle: Apply Gradle properties
    
    Gradle->>Modules: Determine build order
    
    Gradle->>Modules: Build common module
    Note over Modules: Compile common module<br>Generate R.java<br>Process resources
    
    Gradle->>Modules: Build app module
    Note over Modules: Compile app module<br>Generate R.java<br>Process resources<br>Link with common module
    
    Gradle->>Modules: Build automotive module
    Note over Modules: Compile automotive module<br>Generate R.java<br>Process resources<br>Link with common module
    
    Modules->>Artifacts: Generate APKs
    
    Artifacts->>Dev: Return build results
```

Sources: [build.gradle](), [app/build.gradle](), [common/build.gradle]()

## 8. Testing Configuration

The common module includes testing configurations:

- Robolectric for unit testing with Android dependencies
- JUnit for standard unit tests
- AndroidJUnitRunner for instrumentation tests

There's also a test example that demonstrates testing with Robolectric:

Sources: [common/build.gradle:80-82](), [common/src/test/java/com/example/android/uamp/media/library/MusicSourceTest.kt:1-163]()

---

