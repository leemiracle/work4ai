<!-- source: DeepWiki mcp.deepwiki.com · repo android/media-samples · page 5 Build System and CI/CD · fetched 2026-10-23 -->

# Build System and CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/scripts/gradlew_recursive.sh](.github/scripts/gradlew_recursive.sh)
- [.github/workflows/android.yml](.github/workflows/android.yml)
- [PictureInPicture/gradle/wrapper/gradle-wrapper.jar](PictureInPicture/gradle/wrapper/gradle-wrapper.jar)
- [PictureInPicture/gradlew](PictureInPicture/gradlew)
- [PictureInPicture/gradlew.bat](PictureInPicture/gradlew.bat)

</details>



This document covers the build infrastructure, continuous integration pipeline, and automated build processes for the Android Media Samples repository. It details how the multi-project Gradle setup works, the GitHub Actions CI/CD pipeline, and the build optimization strategies used across all sample applications.

For information about individual project build configurations, see [PictureInPictureKotlin Build Configuration](#2.1.4) and [VideoPlayer Build System](#3.2).

## CI/CD Pipeline Architecture

The repository uses GitHub Actions for continuous integration, with a custom recursive build strategy to handle multiple independent Android projects within a single repository.

```mermaid
flowchart TD
    trigger["Push/PR to main branch"]
    checkout["Checkout Repository"]
    java["Setup JDK 1.8"]
    build["Execute gradlew_recursive.sh"]
    zip["Zip Build Artifacts"]
    upload["Upload Artifacts"]
    
    trigger --> checkout
    checkout --> java
    java --> build
    build --> zip
    zip --> upload
    
    subgraph "Build Process Details"
        script["gradlew_recursive.sh"]
        find["Find all gradlew files"]
        optimize["Apply CI Optimizations"]
        execute["Execute assembleDebug"]
        
        script --> find
        find --> optimize
        optimize --> execute
    end
    
    build --> script
```

The main CI workflow is defined in [.github/workflows/android.yml:15-44]() and consists of the following key components:

| Component | Configuration | Purpose |
|-----------|--------------|---------|
| **Trigger** | Push/PR on `main` branch | Automatic build validation |
| **Runner** | `ubuntu-18.04` | Consistent Linux environment |
| **Java Version** | JDK 1.8 | Android development compatibility |
| **Build Command** | `gradlew_recursive.sh assembleDebug` | Multi-project build execution |
| **Artifacts** | APK, AAB, AAR, SO files | Deployable build outputs |

Sources: [.github/workflows/android.yml:17-43]()

## Gradle Wrapper System

Each sample project uses the standard Gradle Wrapper pattern to ensure consistent build environments across different development machines and CI systems.

```mermaid
flowchart LR
    subgraph "Gradle Wrapper Components"
        gradlew["gradlew (Unix)"]
        gradlewbat["gradlew.bat (Windows)"]
        jar["gradle-wrapper.jar"]
        properties["gradle-wrapper.properties"]
    end
    
    subgraph "Build Execution"
        javaHome["JAVA_HOME Detection"]
        classPath["Classpath Setup"]
        mainClass["GradleWrapperMain"]
        gradleExec["Gradle Execution"]
    end
    
    gradlew --> javaHome
    gradlewbat --> javaHome
    jar --> classPath
    properties --> classPath
    javaHome --> classPath
    classPath --> mainClass
    mainClass --> gradleExec
```

The wrapper system provides platform-specific entry points:

- **Unix Systems**: [PictureInPicture/gradlew:1-234]() - POSIX-compliant shell script
- **Windows Systems**: [PictureInPicture/gradlew.bat:1-90]() - Windows batch script  
- **Core Runtime**: [PictureInPicture/gradle/wrapper/gradle-wrapper.jar]() - Java execution environment

Key features of the wrapper implementation:

| Feature | Implementation | Location |
|---------|---------------|-----------|
| **Java Detection** | Automatic `JAVA_HOME` discovery | [PictureInPicture/gradlew:121-140]() |
| **Memory Configuration** | Default JVM options `-Xmx64m -Xms64m` | [PictureInPicture/gradlew:89]() |
| **Cross-Platform** | Shell and batch script variants | [PictureInPicture/gradlew](), [PictureInPicture/gradlew.bat]() |
| **Classpath Setup** | Gradle wrapper JAR inclusion | [PictureInPicture/gradlew:117]() |

Sources: [PictureInPicture/gradlew:65-234](), [PictureInPicture/gradlew.bat:17-90]()

## Multi-Project Build Strategy

The repository implements a recursive build strategy to handle multiple independent Android projects, each with their own Gradle configuration.

```mermaid
flowchart TD
    subgraph "Repository Root"
        script["gradlew_recursive.sh"]
        find["find . -name 'gradlew'"]
    end
    
    subgraph "Discovered Projects"
        pip["PictureInPicture/gradlew"]
        pipk["PictureInPictureKotlin/gradlew"]
        vp["VideoPlayer/gradlew"]
        mr["MediaRouter/gradlew"]
        others["...other projects/gradlew"]
    end
    
    subgraph "Build Execution per Project"
        dirname["dirname $GRADLEW"]
        exec["bash $GRADLEW -p $SAMPLE"]
        flags["--no-parallel --stacktrace"]
    end
    
    script --> find
    find --> pip
    find --> pipk
    find --> vp
    find --> mr
    find --> others
    
    pip --> dirname
    pipk --> dirname
    vp --> dirname
    mr --> dirname
    others --> dirname
    
    dirname --> exec
    exec --> flags
```

The recursive build process in [.github/scripts/gradlew_recursive.sh:30-36]() implements the following logic:

1. **Project Discovery**: Scans for all `gradlew` files in the repository
2. **Directory Resolution**: Extracts project directory from wrapper location
3. **Isolated Execution**: Runs each project build independently
4. **CI Optimization**: Applies consistent CI-specific flags

Sources: [.github/scripts/gradlew_recursive.sh:30-36]()

## Build Optimization

The CI environment applies specific Gradle optimizations to maximize build performance and reliability on GitHub Actions infrastructure.

### Memory and Performance Settings

The build script configures optimal JVM settings for the CI environment:

| Setting | Value | Purpose |
|---------|-------|---------|
| **Heap Size** | `-Xms4g -Xmx4g` | Consistent 4GB memory allocation |
| **OOM Handling** | `-XX:+HeapDumpOnOutOfMemoryError` | Debug memory issues |
| **Daemon** | `false` | Disable for CI stability |
| **Workers** | `max=2` | Match GitHub Actions CPU allocation |
| **Kotlin Incremental** | `false` | Ensure clean builds |
| **Kotlin Strategy** | `in-process` | Reduce process overhead |

```mermaid
flowchart LR
    subgraph "CI Optimizations"
        memory["Memory: 4GB Heap"]
        daemon["Daemon: Disabled"]
        workers["Workers: Limited to 2"]
        kotlin["Kotlin: Non-incremental"]
        encoding["Encoding: UTF-8"]
    end
    
    subgraph "Applied To"
        project1["Project 1 Build"]
        project2["Project 2 Build"]
        projectN["Project N Build"]
    end
    
    memory --> project1
    daemon --> project1
    workers --> project1
    kotlin --> project1
    encoding --> project1
    
    memory --> project2
    daemon --> project2
    workers --> project2
    kotlin --> project2
    encoding --> project2
    
    memory --> projectN
    daemon --> projectN
    workers --> projectN
    kotlin --> projectN
    encoding --> projectN
```

These optimizations are applied through environment variables in [.github/scripts/gradlew_recursive.sh:19-28]():

- **Predictable Memory Usage**: Fixed heap size prevents OOM errors
- **CI Stability**: Daemon disabled to avoid state issues between builds
- **Resource Efficiency**: Worker limitation matches available CPU cores
- **Clean Builds**: Disabled incremental compilation ensures reproducibility

Sources: [.github/scripts/gradlew_recursive.sh:19-28]()

## Artifact Management

The CI pipeline automatically collects and uploads build artifacts from all projects.

```mermaid
flowchart TD
    subgraph "Build Outputs"
        apk["*.apk files"]
        aab["*.aab files"] 
        aar["*.aar files"]
        so["*.so files"]
    end
    
    subgraph "Collection Process"
        search["Find in */build/ directories"]
        zip["zip -r assemble.zip"]
        pattern["Pattern: **/build/*.{apk,aab,aar,so}"]
    end
    
    subgraph "Upload Process"
        upload["actions/upload-artifact@v1"]
        name["Artifact name: assemble"]
        path["Path: assemble.zip"]
    end
    
    apk --> search
    aab --> search
    aar --> search
    so --> search
    
    search --> zip
    zip --> pattern
    pattern --> upload
    upload --> name
    name --> path
```

The artifact collection process defined in [.github/workflows/android.yml:37-43]() includes:

- **APK Files**: Compiled Android application packages
- **AAB Files**: Android App Bundles for Play Store distribution  
- **AAR Files**: Android Archive libraries
- **SO Files**: Native shared libraries

The zip command pattern `**/build/*.{apk,aab,aar,so}` recursively collects all build outputs from any project's `build/` directory, ensuring comprehensive artifact capture across the multi-project repository structure.

Sources: [.github/workflows/android.yml:37-43]()

---

