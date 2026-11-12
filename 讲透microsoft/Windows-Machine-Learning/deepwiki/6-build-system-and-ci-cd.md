<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Windows-Machine-Learning · page 6 Build System and CI/CD · fetched 2026-10-26 -->

# Build System and CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Samples/WinMLSamplesGallery/WinMLSamplesGallery/Samples/OpenCVInterop/README.md](Samples/WinMLSamplesGallery/WinMLSamplesGallery/Samples/OpenCVInterop/README.md)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.cpp](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.cpp)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.h)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/RandomAccessStream.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/RandomAccessStream.h)
- [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/WeakBuffer.h](Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/WeakBuffer.h)
- [azure-pipelines-samples.yml](azure-pipelines-samples.yml)
- [external/tools/BuildOpenCV.ps1](external/tools/BuildOpenCV.ps1)
- [external/tools/CMakeConfigureOpenCV.ps1](external/tools/CMakeConfigureOpenCV.ps1)
- [package.config](package.config)

</details>



This document describes the automated build system, continuous integration, and deployment pipeline for the Windows Machine Learning repository. It covers the Azure DevOps pipeline configuration, dependency management including OpenCV integration, multi-platform build orchestration, and artifact publishing workflows.

For information about the development tools built by this system, see [Development Tools](#3). For details about the sample applications that are built and tested, see [Sample Applications](#4).

## Pipeline Architecture

The build system is orchestrated through Azure DevOps using a matrix build strategy that targets multiple platforms and configurations simultaneously.

### CI/CD Pipeline Overview

```mermaid
graph TB
    subgraph "Trigger Sources"
        GitCommit["Git Commits to master"]
        ManualTrigger["Manual Pipeline Trigger"]
    end
    
    subgraph "Azure DevOps Pipeline"
        PipelineYml["azure-pipelines-samples.yml"]
        MatrixBuild["Build Matrix Strategy"]
        
        subgraph "Build Configurations"
            ReleaseX64["Release_x64"]
            DebugX64["Debug_x64"] 
            ReleaseX86["Release_x86"]
            DebugX86["Debug_x86"]
        end
    end
    
    subgraph "Build Stages"
        SubmoduleSync["Git Submodule Sync"]
        SDKInstall["Windows SDK Installation"]
        OpenCVBuild["OpenCV CMake Build"]
        SamplesBuild["Samples MSBuild"]
        UITests["UI Test Execution"]
        ArtifactPublish["Artifact Publishing"]
    end
    
    GitCommit --> PipelineYml
    ManualTrigger --> PipelineYml
    PipelineYml --> MatrixBuild
    MatrixBuild --> ReleaseX64
    MatrixBuild --> DebugX64
    MatrixBuild --> ReleaseX86
    MatrixBuild --> DebugX86
    
    ReleaseX64 --> SubmoduleSync
    SubmoduleSync --> SDKInstall
    SDKInstall --> OpenCVBuild
    OpenCVBuild --> SamplesBuild
    SamplesBuild --> UITests
    UITests --> ArtifactPublish
```

Sources: [azure-pipelines-samples.yml:1-219]()

### Build Matrix Configuration

The pipeline executes builds across multiple platform and configuration combinations using a parallel execution strategy:

| Platform | Configuration | Build Target | Package Output |
|----------|---------------|--------------|----------------|
| x64 | Release | Full samples + AppPackages | MSIX bundles |
| x64 | Debug | Samples only | Debug binaries |
| x86 | Release | Full samples + AppPackages | MSIX bundles |
| x86 | Debug | Samples only | Debug binaries |

Sources: [azure-pipelines-samples.yml:30-45]()

## Dependency Management

### Git Submodule Integration

The build system manages external dependencies through Git submodules, particularly for OpenCV integration:

```mermaid
graph LR
    subgraph "External Dependencies"
        OpenCVSubmodule["external/opencv<br/>Git Submodule"]
        WindowsSDK["Windows SDK 10.0.19041.0"]
        NuGetPackages["NuGet Dependencies"]
    end
    
    subgraph "Sync Process"
        GitSubmoduleUpdate["git submodule update --init --recursive"]
        ChocoInstall["choco install windows-sdk-10-version-2004-all"]
        NuGetRestore["nuget restore"]
    end
    
    subgraph "Build Tools"
        CMakeConfigureOpenCV["CMakeConfigureOpenCV.ps1"]
        BuildOpenCV["BuildOpenCV.ps1"]
        VSBuild["Visual Studio MSBuild"]
    end
    
    OpenCVSubmodule --> GitSubmoduleUpdate
    WindowsSDK --> ChocoInstall
    NuGetPackages --> NuGetRestore
    
    GitSubmoduleUpdate --> CMakeConfigureOpenCV
    CMakeConfigureOpenCV --> BuildOpenCV
    BuildOpenCV --> VSBuild
```

Sources: [azure-pipelines-samples.yml:47-52](), [azure-pipelines-samples.yml:58-63]()

### OpenCV Build Pipeline

The OpenCV integration requires a multi-stage build process using CMake and MSBuild:

```mermaid
graph TB
    subgraph "OpenCV Configuration"
        CMakeConfigureScript["CMakeConfigureOpenCV.ps1"]
        CMakeArgs["CMAKE Arguments<br/>-DWITH_OPENCL=OFF<br/>-DWITH_FFMPEG=OFF<br/>-DBUILD_opencv_world=ON"]
        GeneratorSelection["Visual Studio 16 2019"]
    end
    
    subgraph "Build Process"
        OpenCVSolution["build/external/opencv/cmake_config/$(BuildPlatform)/OpenCV.sln"]
        BuildTarget["MSBuild /t:Build"]
        InstallTarget["INSTALL.vcxproj"]
        InstallExecution["MSBuild Install"]
    end
    
    subgraph "Output Artifacts"
        OpenCVLibs["OpenCV Libraries"]
        OpenCVHeaders["OpenCV Headers"]
        NativeIntegration["WinMLSamplesGalleryNative"]
    end
    
    CMakeConfigureScript --> CMakeArgs
    CMakeArgs --> GeneratorSelection
    GeneratorSelection --> OpenCVSolution
    OpenCVSolution --> BuildTarget
    BuildTarget --> InstallTarget
    InstallTarget --> InstallExecution
    
    InstallExecution --> OpenCVLibs
    OpenCVLibs --> NativeIntegration
    OpenCVHeaders --> NativeIntegration
```

Sources: [external/tools/CMakeConfigureOpenCV.ps1:1-63](), [azure-pipelines-samples.yml:64-92]()

## Sample Application Build Process

### MSBuild Orchestration

The pipeline builds multiple sample applications using MSBuild with specific configurations and parameters:

```mermaid
graph TB
    subgraph "Sample Applications"
        WinMLSamplesGallery["WinMLSamplesGallery.sln"]
        MNISTTutorial["MNIST/Tutorial/cs/mnist_demo.sln"]
        MNISTUWP["MNIST/UWP/cs/mnist_demo.sln"]
        FNSCandyStyle["FNSCandyStyleTransfer/UWP/CS/snapcandy.sln"]
        MNISTCppCx["MNIST/UWP/cppcx/mnist_cppcx.sln"]
        SamplesTest["Testing/**/SamplesTest.sln"]
    end
    
    subgraph "Build Configurations"
        NuGetRestore["NuGet Package Restoration"]
        MSBuildParams["MSBuild Parameters<br/>/p:WindowsTargetPlatformVersion<br/>/p:AppxPackageSigningEnabled=false<br/>/t:Restore,Clean,Build"]
        PublishMode["Release: /t:Publish<br/>Debug: Build Only"]
    end
    
    subgraph "Output Artifacts"
        DebugBinaries["Debug Binaries"]
        AppPackages["MSIX App Packages"]
        TestAssemblies["UI Test Assemblies"]
    end
    
    WinMLSamplesGallery --> NuGetRestore
    NuGetRestore --> MSBuildParams
    MSBuildParams --> PublishMode
    
    PublishMode --> DebugBinaries
    PublishMode --> AppPackages
    SamplesTest --> TestAssemblies
```

Sources: [azure-pipelines-samples.yml:94-186]()

### Native Component Integration

The WinMLSamplesGalleryNative component requires special handling for OpenCV dependencies:

```mermaid
graph LR
    subgraph "Native Components"
        OpenCVImage["OpenCVImage.cpp<br/>OpenCV Integration"]
        WeakBuffer["WeakBuffer.h<br/>Memory Management"]
        RandomAccessStream["RandomAccessStream.h<br/>Stream Utilities"]
    end
    
    subgraph "Build Dependencies"
        OpenCVLibraries["OpenCV Libraries<br/>opencv_world.lib"]
        WindowsWinRT["Windows WinRT APIs"]
        MachineLearningAPI["Windows.AI.MachineLearning"]
    end
    
    subgraph "Preprocessor Definitions"
        USEOpenCV["USE_OPENCV<br/>Conditional Compilation"]
        WinRTProjections["C++/WinRT Projections"]
    end
    
    OpenCVImage --> OpenCVLibraries
    WeakBuffer --> WindowsWinRT
    RandomAccessStream --> MachineLearningAPI
    
    USEOpenCV --> OpenCVImage
    WinRTProjections --> WeakBuffer
```

Sources: [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/OpenCVImage.cpp:1-117](), [Samples/WinMLSamplesGallery/WinMLSamplesGalleryNative/WeakBuffer.h:1-76]()

## Testing and Quality Assurance

### UI Test Execution

The pipeline includes automated UI testing to validate sample functionality:

```mermaid
graph TB
    subgraph "Test Projects"
        SamplesTestSln["Testing/**/SamplesTest.sln"]
        UITestAssemblies["UI Test Assemblies"]
    end
    
    subgraph "Test Configuration"
        TestMSBuildArgs["-v:diag<br/>/p:OutDir=$(System.DefaultWorkingDirectory)<br/>/p:WindowsTargetPlatformVersion<br/>/t:Restore,Clean,Build"]
        TestPlatform["Platform: $(BuildPlatform)"]
        TestConfiguration["Configuration: $(BuildConfiguration)"]
    end
    
    subgraph "Test Execution Environment"
        VMImage["vmImage: windows-latest"]
        WindowsTargetPlatform["WindowsTargetPlatformVersion: 10.0.19041.0"]
        TestTimeout["timeoutInMinutes: 90"]
    end
    
    SamplesTestSln --> TestMSBuildArgs
    TestMSBuildArgs --> TestPlatform
    TestPlatform --> TestConfiguration
    
    VMImage --> TestTimeout
    WindowsTargetPlatform --> UITestAssemblies
```

Sources: [azure-pipelines-samples.yml:128-138]()

## Artifact Publishing

### Build Output Management

The pipeline publishes build artifacts for distribution and deployment:

```mermaid
graph TB
    subgraph "Artifact Sources"
        SamplesGalleryBin["Samples/WinMLSamplesGallery/WinMLSamplesGallery (Package)/bin"]
        AppPackagesDir["AppPackages Directory"]
        TestBinaries["Test Binaries"]
    end
    
    subgraph "Copy Operations"
        CopyFiles1["CopyFiles@2<br/>SamplesTest & AppPackages"]
        CopyFiles2["CopyFiles@2<br/>Sample Executables"]
        MoveAppPackages["PowerShell Move<br/>AppPackages"]
    end
    
    subgraph "Published Artifacts"
        ArtifactStaging["Build.ArtifactStagingDirectory"]
        PublishedArtifact["WinMLPublicSamples<br/>Artifact Name"]
    end
    
    subgraph "Artifact Contents"
        AdapterSelection["AdapterSelection"]
        CustomOperator["CustomOperator"] 
        CustomTensorization["CustomTensorization"]
        SqueezeNetObjectDetection["SqueezeNetObjectDetection"]
        MSIXBundles["MSIX App Bundles"]
    end
    
    SamplesGalleryBin --> CopyFiles1
    AppPackagesDir --> CopyFiles2
    TestBinaries --> MoveAppPackages
    
    CopyFiles1 --> ArtifactStaging
    CopyFiles2 --> ArtifactStaging
    MoveAppPackages --> ArtifactStaging
    
    ArtifactStaging --> PublishedArtifact
    PublishedArtifact --> AdapterSelection
    PublishedArtifact --> CustomOperator
    PublishedArtifact --> CustomTensorization
    PublishedArtifact --> SqueezeNetObjectDetection
    PublishedArtifact --> MSIXBundles
```

Sources: [azure-pipelines-samples.yml:188-218]()

## Build Variables and Configuration

### Environment Variables

The pipeline uses several key environment variables for build configuration:

| Variable | Value | Purpose |
|----------|-------|---------|
| `SamplesBin` | SamplesBin | Binary output directory |
| `WINDOWS_WINMD` | C:\Program Files (x86)\Windows Kits\10\UnionMetadata\10.0.19041.0\Windows.winmd | Windows metadata path |
| `WindowsTargetPlatformVersion` | 10.0.19041.0 | SDK version target |

Sources: [azure-pipelines-samples.yml:11-15]()

### Build Tools and Versions

The build system requires specific tool versions for consistent builds:

- **NuGet**: Version 5.11.0 for package management
- **Visual Studio**: Version 16.0 (Visual Studio 2019) for MSBuild
- **CMake**: Visual Studio 16 2019 generator for OpenCV
- **Windows SDK**: Version 10.0.19041.0 (Version 2004)

Sources: [azure-pipelines-samples.yml:53-57](), [external/tools/CMakeConfigureOpenCV.ps1:10-14]()

---

