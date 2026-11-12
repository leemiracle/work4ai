<!-- source: DeepWiki mcp.deepwiki.com · repo android/ndk-samples · page 2 Build System · fetched 2026-10-23 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build.yml](.github/workflows/build.yml)
- [audio-echo/app/build.gradle](audio-echo/app/build.gradle)
- [build-logic/README.md](build-logic/README.md)
- [build-logic/build.gradle.kts](build-logic/build.gradle.kts)
- [build-logic/settings.gradle.kts](build-logic/settings.gradle.kts)
- [build-logic/src/main/java/com/android/ndk/samples/buildlogic/AndroidApplicationConventionPlugin.kt](build-logic/src/main/java/com/android/ndk/samples/buildlogic/AndroidApplicationConventionPlugin.kt)
- [build-logic/src/main/java/com/android/ndk/samples/buildlogic/KotlinConventionPlugin.kt](build-logic/src/main/java/com/android/ndk/samples/buildlogic/KotlinConventionPlugin.kt)
- [build-logic/src/main/java/com/android/ndk/samples/buildlogic/Versions.kt](build-logic/src/main/java/com/android/ndk/samples/buildlogic/Versions.kt)
- [gradle/libs.versions.toml](gradle/libs.versions.toml)
- [hello-neon/app/proguard-rules.pro](hello-neon/app/proguard-rules.pro)
- [hello-neon/app/src/main/AndroidManifest.xml](hello-neon/app/src/main/AndroidManifest.xml)
- [hello-neon/app/src/main/cpp/helloneon-intrinsics.h](hello-neon/app/src/main/cpp/helloneon-intrinsics.h)
- [hello-neon/app/src/main/res/mipmap-hdpi/ic_launcher.png](hello-neon/app/src/main/res/mipmap-hdpi/ic_launcher.png)
- [settings.gradle](settings.gradle)

</details>



The Android NDK Samples repository utilizes a modern Gradle-based build system designed to standardize build configurations across multiple sample applications while simplifying dependency management. This page describes the architecture, components, and configuration of the build system used throughout the repository.

For information about specific build configurations for individual samples, see [Basic JNI Samples](#3) or other sample-specific pages.

## Overview

The build system is designed with several key objectives:

- Provide consistent build configurations across all samples
- Centralize version management for dependencies and SDK versions
- Standardize native code integration through CMake
- Simplify application setup with convention plugins

```mermaid
graph TD
    subgraph "NDK Samples Build System"
        VS["Version Catalog<br>/gradle/libs.versions.toml"] --> CP["Convention Plugins<br>/build-logic/"]
        VS --> SD["Sample Dependencies"]
        CP --> AP["Android Application<br>Plugin"]
        CP --> LP["Android Library<br>Plugin"]
        CP --> KP["Kotlin Convention<br>Plugin"]
        AP --> SBP["Standard Build<br>Parameters"]
        SBP --> CSK["Compile SDK"]
        SBP --> NDK["NDK Version"]
        SBP --> CMK["CMake Version"]
        SG["settings.gradle"] --> PI["Project Inclusion"]
        VS --> |"Uses"| SDV["Standard Dependency<br>Versions"]
    end
```

Sources: [gradle/libs.versions.toml](), [build-logic/src/main/java/com/android/ndk/samples/buildlogic/Versions.kt](), [build-logic/build.gradle.kts](), [settings.gradle]()

## Version Management

The build system centralizes version management using Gradle's version catalog feature. This ensures that all samples use consistent dependency versions and build configurations.

### Version Catalog

The repository uses a central `libs.versions.toml` file to define all dependency versions, libraries, and plugins.

```mermaid
graph TD
    subgraph "Version Catalog Structure"
        VF["libs.versions.toml"] --> V["[versions]"]
        VF --> L["[libraries]"]
        VF --> P["[plugins]"]
        
        V --> SDK["Android SDK<br>agp = 8.7.0<br>kotlin = 1.9.0"]
        V --> TP["Third Party Versions<br>curl = 7.79.1-beta-1<br>oboe = 1.9.0"]
        V --> AF["AndroidX Libraries<br>androidxCore = 1.13.1"]
        
        L --> AC["androidx-core<br>group = androidx.core<br>name = core<br>version.ref = androidxCore"]
        L --> BL["build-logic deps<br>android-gradlePlugin"]
        
        P --> AP["android-application<br>com.android.application"]
        P --> KP["jetbrainsKotlinAndroid<br>org.jetbrains.kotlin.android"]
    end
```

Sources: [gradle/libs.versions.toml]()

Key sections in the version catalog:
- **`[versions]`**: Defines version constants for all dependencies and plugins
- **`[libraries]`**: Defines library dependencies with references to version constants
- **`[plugins]`**: Defines Gradle plugins with version references

### Standard Versions

The project defines standard versions for SDK, NDK, and other build parameters in a dedicated Kotlin class:

```kotlin
object Versions {
    const val COMPILE_SDK = 34
    const val TARGET_SDK = 34
    const val MIN_SDK = 21
    const val NDK = "27.1.12297006" // r27b
    const val CMAKE = "3.22.1"
    val JAVA = JavaVersion.VERSION_1_8
}
```

Sources: [build-logic/src/main/java/com/android/ndk/samples/buildlogic/Versions.kt]()

## Convention Plugins

The build system uses convention plugins to standardize build configurations across all samples. These plugins are defined in the `build-logic` directory and applied to individual sample projects.

```mermaid
flowchart TD
    subgraph "Convention Plugins Architecture"
        BL["build-logic"] --> CP["Convention Plugins"]
        CP --> AAP["AndroidApplicationConventionPlugin"]
        CP --> ALP["AndroidLibraryConventionPlugin"]
        CP --> KCP["KotlinConventionPlugin"]
        
        AAP --> |"Applies"| AAPC["- Sets compileSdk<br>- Sets ndkVersion<br>- Configures CMake<br>- Sets default config<br>- Keeps debug symbols"]
        
        KCP --> |"Applies"| KCPC["- Kotlin Android Plugin<br>- JVM Target Settings"]
        
        SA["Sample Application"] --> |"Applies<br>Plugin ID"| PID["ndksamples.android.application"]
        PID --> |"Implements"| AAP
    end
```

Sources: [build-logic/src/main/java/com/android/ndk/samples/buildlogic/AndroidApplicationConventionPlugin.kt](), [build-logic/build.gradle.kts](), [build-logic/src/main/java/com/android/ndk/samples/buildlogic/KotlinConventionPlugin.kt]()

### Android Application Convention Plugin

The `AndroidApplicationConventionPlugin` applies standard configurations to Android application modules:

- Sets the compile SDK to version 34
- Configures the NDK version to "27.1.12297006" (r27b)
- Sets the CMake version to 3.22.1
- Configures minSdk (21) and targetSdk (34)
- Preserves debug symbols for native libraries in debug builds

Sample projects apply this plugin with a simple declaration:

```kotlin
plugins {
    id "ndksamples.android.application"
}
```

Sources: [build-logic/src/main/java/com/android/ndk/samples/buildlogic/AndroidApplicationConventionPlugin.kt](), [audio-echo/app/build.gradle]()

### Kotlin Convention Plugin

The `KotlinConventionPlugin` handles Kotlin-specific configurations:

- Applies the Kotlin Android plugin
- Sets JVM target compatibility

Sources: [build-logic/src/main/java/com/android/ndk/samples/buildlogic/KotlinConventionPlugin.kt]()

## Native Code Integration

The build system standardizes native code integration across samples using CMake. Each sample application configures its CMake settings in its build.gradle file.

```mermaid
graph TD
    subgraph "Native Code Build System"
        AG["app/build.gradle"] --> |"Configures"| ENC["externalNativeBuild"]
        ENC --> |"Specifies"| CMP["CMake Path<br>src/main/cpp/CMakeLists.txt"]
        ENC --> |"Provides"| CMA["CMake Arguments<br>-DANDROID_STL=c++_static"]
        
        AAP["AndroidApplicationConventionPlugin"] --> |"Sets"| CMKV["cmake.version = 3.22.1"]
        AAP --> |"Adds"| CMKA["CMake Arguments<br>-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON"]
        
        CMP --> |"Builds"| NC["Native C/C++ Code"]
        NC --> |"Compiled to"| SO[".so Library Files"]
    end
```

Sources: [audio-echo/app/build.gradle](), [build-logic/src/main/java/com/android/ndk/samples/buildlogic/AndroidApplicationConventionPlugin.kt]()

Sample project CMake configuration:

```groovy
android {
    defaultConfig {
        externalNativeBuild {
            cmake {
                arguments '-DANDROID_STL=c++_static'
            }
        }
    }
    externalNativeBuild {
        cmake {
            path 'src/main/cpp/CMakeLists.txt'
        }
    }
}
```

Sources: [audio-echo/app/build.gradle]()

## Project Organization

The repository is organized as a multi-project Gradle build with numerous sample applications. The `settings.gradle` file defines the project structure.

```mermaid
graph TD
    subgraph "Project Structure"
        SG["settings.gradle"] --> |"Defines"| PN["rootProject.name = NDK Samples"]
        SG --> |"Includes"| SM["Sample Modules"]
        SG --> |"Configures"| RM["Repository Management"]
        
        SM --> AS1["audio-echo:app"]
        SM --> AS2["hello-jni:app"]
        SM --> AS3["teapots:classic-teapot"]
        SM --> AS4["native-activity:app"]
        SM --> AS5["...and many more"]
        
        RM --> GR["Google Repository"]
        RM --> MC["Maven Central"]
    end
```

Sources: [settings.gradle]()

Each sample is configured as a separate module, allowing individual building and testing. The convention plugins ensure consistent configuration across all samples.

## Continuous Integration

The repository includes CI/CD configuration through GitHub Actions, which builds all samples to ensure they remain functional.

```mermaid
graph TD
    subgraph "CI Build Process"
        WF[".github/workflows/build.yml"] --> |"Runs on"| UR["Ubuntu Latest"]
        WF --> |"Sets up"| JDK["JDK 17"]
        WF --> |"Configures"| SDK["Android SDK"]
        WF --> |"Executes"| GB["Gradle Build<br>./gradlew build"]
        GB --> |"Builds"| SA["All Sample Applications"]
    end
```

Sources: [.github/workflows/build.yml]()

## Using the Build System in Samples

To use the standardized build system in a sample application:

1. Include the module in `settings.gradle`
2. Apply the appropriate convention plugin in the module's `build.gradle`
3. Configure sample-specific settings as needed

Example of a sample's build.gradle file:

```groovy
plugins {
    id "ndksamples.android.application"
}

android {
    defaultConfig {
        applicationId 'com.google.sample.echo'
        versionCode 1
        versionName '1.0'
        externalNativeBuild {
            cmake {
                arguments '-DANDROID_STL=c++_static'
            }
        }
    }
    externalNativeBuild {
        cmake {
            path 'src/main/cpp/CMakeLists.txt'
        }
    }
    namespace 'com.google.sample.echo'
}

dependencies {
    implementation libs.appcompat
}
```

Sources: [audio-echo/app/build.gradle]()

Note how the sample references dependencies using the version catalog with `libs.appcompat`.

---

