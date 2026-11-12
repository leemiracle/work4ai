<!-- source: DeepWiki mcp.deepwiki.com · repo android/location-samples · page 4 Development Setup · fetched 2026-10-23 -->

# Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Geofencing/app/build.gradle](Geofencing/app/build.gradle)
- [Geofencing/app/src/main/AndroidManifest.xml](Geofencing/app/src/main/AndroidManifest.xml)
- [Geofencing/build.gradle](Geofencing/build.gradle)
- [Geofencing/gradle.properties](Geofencing/gradle.properties)
- [Geofencing/gradle/wrapper/gradle-wrapper.jar](Geofencing/gradle/wrapper/gradle-wrapper.jar)
- [Geofencing/gradle/wrapper/gradle-wrapper.properties](Geofencing/gradle/wrapper/gradle-wrapper.properties)
- [Geofencing/gradlew](Geofencing/gradlew)
- [Geofencing/gradlew.bat](Geofencing/gradlew.bat)
- [LocationUpdatesBackgroundKotlin/app/build.gradle](LocationUpdatesBackgroundKotlin/app/build.gradle)
- [LocationUpdatesBackgroundKotlin/app/src/main/AndroidManifest.xml](LocationUpdatesBackgroundKotlin/app/src/main/AndroidManifest.xml)
- [LocationUpdatesBackgroundKotlin/app/src/main/res/drawable/ic_location_on_24px.xml](LocationUpdatesBackgroundKotlin/app/src/main/res/drawable/ic_location_on_24px.xml)
- [LocationUpdatesBackgroundKotlin/app/src/main/res/drawable/ic_my_location_24px.xml](LocationUpdatesBackgroundKotlin/app/src/main/res/drawable/ic_my_location_24px.xml)
- [LocationUpdatesBackgroundKotlin/app/src/main/res/layout/activity_main.xml](LocationUpdatesBackgroundKotlin/app/src/main/res/layout/activity_main.xml)
- [LocationUpdatesBackgroundKotlin/app/src/main/res/values/dimens.xml](LocationUpdatesBackgroundKotlin/app/src/main/res/values/dimens.xml)
- [LocationUpdatesBackgroundKotlin/build.gradle](LocationUpdatesBackgroundKotlin/build.gradle)
- [LocationUpdatesBackgroundKotlin/gradle.properties](LocationUpdatesBackgroundKotlin/gradle.properties)
- [LocationUpdatesBackgroundKotlin/gradle/wrapper/gradle-wrapper.properties](LocationUpdatesBackgroundKotlin/gradle/wrapper/gradle-wrapper.properties)

</details>



This document provides a comprehensive guide for setting up the development environment for the Google Play Location & Context APIs samples repository. It covers build system configuration, dependency management, SDK requirements, and environment setup procedures required to build and run the sample applications.

For information about specific architectural patterns used across samples, see [Architecture Patterns](#3). For details about individual sample applications, see [Sample Applications](#2).

## Prerequisites and System Requirements

The repository requires specific versions of development tools and SDKs to ensure compatibility across all sample applications.

### Required Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Android Studio | Arctic Fox or later | Primary IDE |
| JDK | 8 or later | Java compilation |
| Android SDK | API 15-33 | Target platform support |
| Gradle | 7.3.3 - 8.0 | Build automation |

### Android SDK Configuration

Different samples target varying API levels based on their feature requirements:

```mermaid
graph TB
    subgraph "SDK Target Levels"
        API15["API 15<br/>LocationUpdatesBackgroundKotlin<br/>minSdkVersion"]
        API16["API 16<br/>Geofencing<br/>minSdkVersion"]
        API31["API 31<br/>LocationUpdatesBackgroundKotlin<br/>targetSdkVersion"]
        API33["API 33<br/>Geofencing<br/>targetSdkVersion"]
    end
    
    subgraph "Build Tools"
        AGP722["Android Gradle Plugin<br/>7.2.2"]
        AGP741["Android Gradle Plugin<br/>7.4.1"]
        GRADLE733["Gradle 7.3.3"]
        GRADLE80["Gradle 8.0-rc-2"]
    end
    
    API15 --> GRADLE733
    API31 --> GRADLE733
    API16 --> GRADLE80
    API33 --> GRADLE80
    
    GRADLE733 --> AGP722
    GRADLE80 --> AGP741
```

**SDK Configuration by Sample**
- **LocationUpdatesBackgroundKotlin**: `minSdkVersion 15`, `targetSdkVersion 31`
- **Geofencing**: `minSdkVersion 16`, `targetSdkVersion 33`

Sources: [LocationUpdatesBackgroundKotlin/app/build.gradle:28-29](), [Geofencing/app/build.gradle:8-9]()

## Project Structure and Build Configuration

The repository follows a multi-module structure where each sample application maintains its own build configuration and dependencies.

### Build System Architecture

```mermaid
graph TD
    ROOT["Repository Root"]
    
    subgraph "LocationUpdatesBackgroundKotlin"
        LUBK_ROOT["build.gradle<br/>Project Level"]
        LUBK_APP["app/build.gradle<br/>Module Level"]
        LUBK_WRAPPER["gradle/wrapper/<br/>gradle-wrapper.properties"]
    end
    
    subgraph "Geofencing"
        GF_ROOT["build.gradle<br/>Project Level"]
        GF_APP["app/build.gradle<br/>Module Level"]
        GF_WRAPPER["gradle/wrapper/<br/>gradle-wrapper.properties"]
    end
    
    subgraph "Other Samples"
        OTHER["Similar Structure<br/>Per Sample"]
    end
    
    ROOT --> LUBK_ROOT
    ROOT --> GF_ROOT
    ROOT --> OTHER
    
    LUBK_ROOT --> LUBK_APP
    LUBK_ROOT --> LUBK_WRAPPER
    
    GF_ROOT --> GF_APP
    GF_ROOT --> GF_WRAPPER
```

Each sample maintains independent:
- **Project-level build.gradle**: Defines `buildscript` dependencies and repository configurations
- **Module-level build.gradle**: Specifies application dependencies, SDK versions, and build variants
- **Gradle wrapper**: Ensures consistent Gradle version across development environments

Sources: [LocationUpdatesBackgroundKotlin/build.gradle:17-43](), [LocationUpdatesBackgroundKotlin/app/build.gradle:17-77](), [Geofencing/build.gradle:1-22]()

### Kotlin and Android Configuration

The samples use Kotlin as the primary development language with specific plugin configurations:

**LocationUpdatesBackgroundKotlin Configuration:**
- `kotlin-android` plugin for Android Kotlin support
- `kotlin-kapt` plugin for annotation processing
- Kotlin version: `1.6.0`
- JVM target: `1.8`

**Key Build Features:**
- `dataBinding { enabled true }` - Enables Android Data Binding
- `multiDexEnabled true` - Supports applications exceeding 64K method limit

Sources: [LocationUpdatesBackgroundKotlin/build.gradle:20](), [LocationUpdatesBackgroundKotlin/app/build.gradle:19-21,43-49]()

## Dependency Management

The samples demonstrate comprehensive dependency management covering Google Play Services, AndroidX libraries, and modern Android development tools.

### Core Dependencies Matrix

```mermaid
graph LR
    subgraph "Google Play Services"
        GPS_LOC["play-services-location<br/>19.0.1 / 17.0.0"]
        GPS_MAPS["play-services-maps<br/>17.0.0"]
    end
    
    subgraph "AndroidX Libraries"
        APPCOMPAT["appcompat<br/>1.4.1 / 1.1.0"]
        ROOM["room-runtime<br/>2.4.2"]
        LIFECYCLE["lifecycle-*<br/>2.4.1"]
        CONSTRAINT["constraintlayout<br/>2.1.3"]
    end
    
    subgraph "Kotlin Support"
        KOTLIN_STD["kotlin-stdlib-jdk7<br/>1.6.0"]
        COROUTINES["kotlinx-coroutines"]
    end
    
    subgraph "Sample Applications"
        LUBK["LocationUpdatesBackgroundKotlin"]
        GF["Geofencing"]
    end
    
    LUBK --> GPS_LOC
    LUBK --> APPCOMPAT
    LUBK --> ROOM
    LUBK --> LIFECYCLE
    LUBK --> KOTLIN_STD
    
    GF --> GPS_LOC
    GF --> GPS_MAPS
    GF --> APPCOMPAT
```

### Google Play Services Integration

All location-based samples require Google Play Services Location API:

**Version Variations by Sample:**
- LocationUpdatesBackground: `19.0.1`
- Geofencing: `17.0.0`

**Additional Services:**
- `play-services-maps` for map visualization in Geofencing sample

Sources: [LocationUpdatesBackgroundKotlin/app/build.gradle:71](), [Geofencing/app/build.gradle:29-30]()

### Database and Persistence

Advanced samples integrate Room database for local data persistence:

**Room Configuration:**
- `room-runtime:2.4.2` - Runtime library
- `room-compiler:2.4.2` - Annotation processor (kapt)

**Lifecycle Components:**
- `lifecycle-runtime-ktx:2.4.1`
- `lifecycle-viewmodel-ktx:2.4.1` 
- `lifecycle-extensions:2.2.0`

Sources: [LocationUpdatesBackgroundKotlin/app/build.gradle:63-68]()

## Environment Setup Workflow

### Initial Repository Setup

```mermaid
flowchart TD
    CLONE["git clone repository"]
    STUDIO["Import in Android Studio"]
    SDK_CHECK["Verify Android SDK<br/>API 15-33 installed"]
    
    subgraph "Per Sample Setup"
        SELECT["Select Sample Module"]
        GRADLE_SYNC["Gradle Sync"]
        DEPS_DOWNLOAD["Download Dependencies"]
        BUILD_CHECK["Verify Build Success"]
    end
    
    CLONE --> STUDIO
    STUDIO --> SDK_CHECK
    SDK_CHECK --> SELECT
    SELECT --> GRADLE_SYNC
    GRADLE_SYNC --> DEPS_DOWNLOAD
    DEPS_DOWNLOAD --> BUILD_CHECK
    
    BUILD_CHECK --> |"Next Sample"| SELECT
    BUILD_CHECK --> |"All Samples"| COMPLETE["Setup Complete"]
```

### Gradle Wrapper Configuration

Each sample includes Gradle wrapper for build consistency:

**Gradle Versions:**
- LocationUpdatesBackgroundKotlin: `gradle-7.3.3-bin.zip`
- Geofencing: `gradle-8.0-rc-2-bin.zip`

**Wrapper Properties:**
```
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
```

Use `./gradlew` (Unix) or `gradlew.bat` (Windows) for consistent builds across environments.

Sources: [LocationUpdatesBackgroundKotlin/gradle/wrapper/gradle-wrapper.properties:1-7](), [Geofencing/gradle/wrapper/gradle-wrapper.properties:1-6]()

## Permission and Manifest Configuration

Samples require specific Android permissions and manifest configurations for location and context APIs.

### Location Permission Requirements

```mermaid
graph TB
    subgraph "Runtime Permissions"
        COARSE["ACCESS_COARSE_LOCATION<br/>Required by all samples"]
        FINE["ACCESS_FINE_LOCATION<br/>Required by all samples"]
        BACKGROUND["ACCESS_BACKGROUND_LOCATION<br/>Background location samples"]
    end
    
    subgraph "System Permissions"
        NOTIF["POST_NOTIFICATIONS<br/>Notification support"]
        WAKE["WAKE_LOCK<br/>Background processing"]
    end
    
    subgraph "Sample Applications"
        LUBK_MANIFEST["LocationUpdatesBackgroundKotlin<br/>AndroidManifest.xml"]
        GF_MANIFEST["Geofencing<br/>AndroidManifest.xml"]
    end
    
    LUBK_MANIFEST --> COARSE
    LUBK_MANIFEST --> FINE
    LUBK_MANIFEST --> BACKGROUND
    
    GF_MANIFEST --> COARSE
    GF_MANIFEST --> FINE
    GF_MANIFEST --> NOTIF
    GF_MANIFEST --> WAKE
```

### Application Component Registration

**Broadcast Receivers:**
- `LocationUpdatesBroadcastReceiver` for background location updates
- `GeofenceBroadcastReceiver` for geofence transition events

**Services:**
- `GeofenceTransitionsJobIntentService` for background geofence processing

Sources: [LocationUpdatesBackgroundKotlin/app/src/main/AndroidManifest.xml:21-23,44-50](), [Geofencing/app/src/main/AndroidManifest.xml:19-22,43-51]()

## Build Variants and Configuration

### Debug and Release Configurations

**ProGuard Configuration:**
- Release builds: `minifyEnabled false` (disabled for sample clarity)
- ProGuard rules: `proguard-rules.pro` files maintain sample readability

**Data Binding:**
- Enabled in LocationUpdatesBackgroundKotlin for modern UI patterns
- Compiler: `com.android.databinding:compiler:3.1.4`

Sources: [LocationUpdatesBackgroundKotlin/app/build.gradle:36-45,69]()

## Testing and Development Tools

### Testing Dependencies

**Unit Testing:**
- `junit:junit:4.13.2` / `4.12`

**Instrumentation Testing:**
- `androidx.test.ext:junit:1.1.3`
- `androidx.test.espresso:espresso-core:3.4.0` / `3.1.1`

### Material Design Integration

- `com.google.android.material:material:1.5.0` / `1.0.0`

Sources: [LocationUpdatesBackgroundKotlin/app/build.gradle:73-76](), [Geofencing/app/build.gradle:22-28]()

---

