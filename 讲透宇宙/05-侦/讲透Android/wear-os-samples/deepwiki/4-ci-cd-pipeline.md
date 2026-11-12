<!-- source: DeepWiki mcp.deepwiki.com · repo android/wear-os-samples · page 4 CI/CD Pipeline · fetched 2026-10-23 -->

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/Complications.yml](.github/workflows/Complications.yml)
- [.github/workflows/ComposeStarter.yml](.github/workflows/ComposeStarter.yml)
- [.github/workflows/DataLayer.yml](.github/workflows/DataLayer.yml)
- [.github/workflows/WearOAuth.yml](.github/workflows/WearOAuth.yml)
- [.github/workflows/WearSpeakerSample.yml](.github/workflows/WearSpeakerSample.yml)
- [.github/workflows/WearTilesKotlin.yml](.github/workflows/WearTilesKotlin.yml)
- [.github/workflows/copy-branch.yml](.github/workflows/copy-branch.yml)

</details>



This document describes the Continuous Integration and Continuous Delivery (CI/CD) pipeline implemented for the Wear OS Samples repository. The pipeline ensures that all sample applications build correctly, pass tests, and generate usable artifacts. For information about the build system configuration itself, see [Build System](#3).

## Pipeline Overview

The Wear OS Samples repository uses GitHub Actions to implement CI/CD workflows for each sample project. These workflows automatically build and test sample applications whenever relevant code changes are made.

```mermaid
flowchart TD
    subgraph "GitHub Repository Events"
        PR["Pull Request"]
        Push["Push to main"]
        Manual["Manual workflow_dispatch"]
    end
    
    subgraph "GitHub Actions Workflows"
        WF1["ComposeStarter.yml"]
        WF2["WearTilesKotlin.yml"]
        WF3["WearSpeakerSample.yml"]
        WF4["DataLayer.yml"]
        WF5["WearOAuth.yml"]
        WF6["Complications.yml"]
    end
    
    subgraph "Jobs"
        Build["build job"]
        APK["apk job"]
    end
    
    subgraph "Artifacts"
        BuildOutputs["Build Outputs"]
        BuildReports["Build Reports"]
        ReleaseAPK["Release APK"]
    end
    
    PR --> WF1
    PR --> WF2
    PR --> WF3
    PR --> WF4
    PR --> WF5
    PR --> WF6
    
    Push --> WF1
    Push --> WF2
    Push --> WF3
    Push --> WF4
    Push --> WF5
    Push --> WF6
    
    Manual --> WF1
    Manual --> WF2
    Manual --> WF3
    Manual --> WF4
    Manual --> WF5
    Manual --> WF6
    
    WF1 --> Build
    WF1 --> APK
    WF2 --> Build
    WF3 --> Build
    WF3 --> APK
    WF4 --> Build
    WF4 --> APK
    WF5 --> Build
    WF6 --> Build
    
    Build --> BuildOutputs
    Build --> BuildReports
    APK --> ReleaseAPK
```

Sources:
- `.github/workflows/ComposeStarter.yml`
- `.github/workflows/WearTilesKotlin.yml`
- `.github/workflows/WearSpeakerSample.yml`
- `.github/workflows/DataLayer.yml`
- `.github/workflows/WearOAuth.yml`
- `.github/workflows/Complications.yml`

## Workflow Files and Structure

Each sample project has a dedicated workflow file in the `.github/workflows` directory. These files define when and how the CI/CD pipeline runs for each sample.

### Workflow Triggers

Each workflow is triggered by:

1. **Push to main branch** - Only when files in the corresponding sample directory are modified
2. **Pull request** - Only when files in the corresponding sample directory are modified
3. **Manual dispatch** - Can be manually triggered through the GitHub Actions interface

```mermaid
flowchart LR
    subgraph "Sample Project" 
        Code["Project Code Files"]
    end
    
    subgraph "GitHub Events"
        PR["Pull Request"]
        Push["Push to main"]
        Manual["Manual workflow_dispatch"]
    end
    
    subgraph "Path Filtering"
        Filter["paths: 'SampleName/**'"]
    end
    
    subgraph "Workflow"
        WF["GitHub Actions Workflow"]
    end
    
    Code --> |"changes"| PR
    Code --> |"changes"| Push
    
    PR --> Filter
    Push --> Filter
    Manual --> |"no filtering"| WF
    
    Filter --> WF
```

Sources:
- `.github/workflows/ComposeStarter.yml:3-12`
- `.github/workflows/WearTilesKotlin.yml:3-14`
- `.github/workflows/WearSpeakerSample.yml:3-12`
- `.github/workflows/DataLayer.yml:3-12`

## Build Job

The primary job in each workflow is the `build` job, which builds and tests the sample application.

```mermaid
flowchart TD
    Start["Job: build"] --> Checkout["actions/checkout@v4"]
    Checkout --> SetupJava["actions/setup-java@v4\n(JDK 17, Zulu distribution)"]
    SetupJava --> CacheKey["Generate cache key\n./scripts/checksum.sh"]
    CacheKey --> Cache["actions/cache@v4\n(Gradle caches)"]
    Cache --> Build["./gradlew check\n(in sample directory)"]
    Build --> UploadAPKs["Upload build outputs (APKs)\nactions/upload-artifact@v4"]
    Build --> UploadReports["Upload build reports\nactions/upload-artifact@v4"]
```

Sources:
- `.github/workflows/ComposeStarter.yml:18-60`
- `.github/workflows/WearSpeakerSample.yml:18-58`
- `.github/workflows/DataLayer.yml:18-62`

### Environment Setup

Each workflow sets an environment variable `SAMPLE_PATH` to specify the sample project directory:

```
env:
  SAMPLE_PATH: SampleName
```

This variable is used throughout the workflow to reference the correct project directory.

Sources:
- `.github/workflows/ComposeStarter.yml:14-15`
- `.github/workflows/WearTilesKotlin.yml:16-17`
- `.github/workflows/WearSpeakerSample.yml:14-15`
- `.github/workflows/DataLayer.yml:14-15`

### Gradle Caching

To optimize build performance, the workflows implement a caching strategy for Gradle dependencies:

```mermaid
flowchart TD
    Script["./scripts/checksum.sh"] --> Checksum["checksum.txt file\n(based on project files)"]
    Checksum --> CacheKey["Cache key:\ngradle-${{ hashFiles('checksum.txt') }}"]
    
    CacheKey --> CachePaths["Cache paths:"]
    CachePaths --> Modules["~/.gradle/caches/modules-*"]
    CachePaths --> Jars["~/.gradle/caches/jars-*"]
    CachePaths --> BuildCache["~/.gradle/caches/build-cache-*"]
```

Sources:
- `.github/workflows/ComposeStarter.yml:32-41`
- `.github/workflows/WearSpeakerSample.yml:32-41`
- `.github/workflows/DataLayer.yml:32-41`

## APK Job

Many workflows include a dedicated `apk` job that specifically builds release APKs:

```mermaid
flowchart TD
    Start["Job: apk"] --> Checkout["actions/checkout@v4"]
    Checkout --> SetupJava["actions/setup-java@v4\n(JDK 17)"]
    SetupJava --> CacheKey["Generate cache key"]
    CacheKey --> Cache["Restore Gradle cache"]
    Cache --> Build["./gradlew module:assembleRelease"]
    Build --> Upload["Upload APK artifact\nName: App\nPath: sample/module/build/outputs/apk/release/*.apk"]
```

Sources:
- `.github/workflows/ComposeStarter.yml:62-94`
- `.github/workflows/WearSpeakerSample.yml:60-92`
- `.github/workflows/DataLayer.yml:63-95`

The exact command varies by project:
- ComposeStarter: `./gradlew app:assembleRelease`
- WearSpeakerSample: `./gradlew wear:assembleRelease`
- DataLayer: `./gradlew app:assembleRelease`

## Project-Specific Workflow Variations

While the workflows follow a common structure, there are variations for specific projects:

### WearTilesKotlin

The WearTilesKotlin workflow uses `gradle/gradle-build-action@v3` instead of the manual caching approach:

```mermaid
flowchart LR
    Setup["Setup"] --> GradleAction["gradle/gradle-build-action@v3"]
    GradleAction --> BuildRoot["build-root-directory: ${{ env.SAMPLE_PATH }}"]
    BuildRoot --> GradleCheck["./gradlew check"]
```

Sources:
- `.github/workflows/WearTilesKotlin.yml:34-41`

### WearOAuth

The WearOAuth workflow handles multiple modules and uploads artifacts from both:

```mermaid
flowchart LR
    Build["./gradlew check"] --> Outputs["Upload build outputs"]
    Outputs --> PKCE["oauth-pkce/build/outputs"]
    Outputs --> DeviceGrant["oauth-device-grant/build/outputs"]
    
    Build --> Reports["Upload build reports"]
    Reports --> PKCEReports["oauth-pkce/build/reports"]
    Reports --> DeviceGrantReports["oauth-device-grant/build/reports"]
```

Sources:
- `.github/workflows/WearOAuth.yml:47-62`

### DataLayer

The DataLayer workflow uploads artifacts from both the wearable and mobile application modules:

```mermaid
flowchart LR
    Build["./gradlew check"] --> Outputs["Upload build outputs"]
    Outputs --> Wearable["Wearable/build/outputs"]
    Outputs --> Application["Application/build/outputs"]
    
    Build --> Reports["Upload build reports"]
    Reports --> WearableReports["Wearable/build/reports"]
    Reports --> ApplicationReports["Application/build/reports"]
```

Sources:
- `.github/workflows/DataLayer.yml:47-61`

## Branch Management Workflow

A special workflow exists to duplicate the `main` branch to the legacy `master` branch:

```mermaid
flowchart TD
    Push["Push to main"] --> CopyBranch["copy-branch job"]
    CopyBranch --> Checkout["Checkout repo\n(with master branch)"]
    Checkout --> ConfigGit["Configure Git user"]
    ConfigGit --> Merge["git merge origin/main"]
    Merge --> Push["git push\n(to master branch)"]
```

Sources:
- `.github/workflows/copy-branch.yml`

This ensures backward compatibility for scripts or documentation that might still reference the `master` branch.

## Artifact Management

The workflows upload two types of artifacts:

1. **Build outputs (APKs)** - Debug APKs and related build outputs
2. **Build reports** - Test results, lint reports, and other build diagnostics

In addition, the `apk` job uploads a release APK with the artifact name "App".

Sources:
- `.github/workflows/ComposeStarter.yml:47-60`
- `.github/workflows/ComposeStarter.yml:90-94`
- `.github/workflows/WearSpeakerSample.yml:47-58`
- `.github/workflows/WearSpeakerSample.yml:88-92`

## Summary of Workflow Jobs and Artifacts

| Sample Project | Workflow File | Build Job | APK Job | Artifacts |
|----------------|---------------|-----------|---------|-----------|
| ComposeStarter | ComposeStarter.yml | ✓ | ✓ | - app/build/outputs<br>- app/build/reports<br>- App (release APK) |
| WearTilesKotlin | WearTilesKotlin.yml | ✓ | ✗ | - app/build/outputs<br>- app/build/reports |
| WearSpeakerSample | WearSpeakerSample.yml | ✓ | ✓ | - wear/build/outputs<br>- wear/build/reports<br>- App (release APK) |
| DataLayer | DataLayer.yml | ✓ | ✓ | - Wearable/build/outputs<br>- Application/build/outputs<br>- build reports<br>- App (release APK) |
| WearOAuth | WearOAuth.yml | ✓ | ✗ | - oauth-pkce/build/outputs<br>- oauth-device-grant/build/outputs<br>- build reports |
| Complications | Complications.yml | ✓ | ✗ | - Wearable/build/outputs<br>- Wearable/build/reports |

Sources:
- `.github/workflows/ComposeStarter.yml`
- `.github/workflows/WearTilesKotlin.yml`
- `.github/workflows/WearSpeakerSample.yml`
- `.github/workflows/DataLayer.yml`
- `.github/workflows/WearOAuth.yml`
- `.github/workflows/Complications.yml`

---

