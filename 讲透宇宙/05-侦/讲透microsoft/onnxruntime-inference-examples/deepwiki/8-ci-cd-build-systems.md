<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/onnxruntime-inference-examples · page 8 CI/CD & Build Systems · fetched 2026-10-26 -->

# CI/CD & Build Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.config/tsaoptions.json](.config/tsaoptions.json)
- [.pipelines/OneBranch.Official.yml](.pipelines/OneBranch.Official.yml)
- [.pipelines/OneBranch.PullRequest.yml](.pipelines/OneBranch.PullRequest.yml)
- [c_cxx/CMakeLists.txt](c_cxx/CMakeLists.txt)
- [c_cxx/fns_candy_style_transfer/fns_candy_style_transfer.c](c_cxx/fns_candy_style_transfer/fns_candy_style_transfer.c)
- [c_cxx/fns_candy_style_transfer/image_file.h](c_cxx/fns_candy_style_transfer/image_file.h)
- [c_cxx/fns_candy_style_transfer/image_file_libpng.c](c_cxx/fns_candy_style_transfer/image_file_libpng.c)
- [c_cxx/imagenet/image_loader_libjpeg.cc](c_cxx/imagenet/image_loader_libjpeg.cc)
- [c_cxx/imagenet/runnable_task.h](c_cxx/imagenet/runnable_task.h)
- [c_cxx/squeezenet/main.cpp](c_cxx/squeezenet/main.cpp)
- [c_sharp/image_classification/image_classification.csproj](c_sharp/image_classification/image_classification.csproj)
- [ci_build/azure_pipelines/mobile-examples-pipeline.yml](ci_build/azure_pipelines/mobile-examples-pipeline.yml)
- [ci_build/azure_pipelines/templates/use-python-step.yml](ci_build/azure_pipelines/templates/use-python-step.yml)
- [ci_build/azure_pipelines/templates/xcode-build-and-test-step.yml](ci_build/azure_pipelines/templates/xcode-build-and-test-step.yml)
- [ci_build/download_ort_release.ps1](ci_build/download_ort_release.ps1)
- [mobile/examples/basic_usage/ios/Podfile](mobile/examples/basic_usage/ios/Podfile)
- [mobile/examples/object_detection/ios/ORTObjectDetection/prepare_model.sh](mobile/examples/object_detection/ios/ORTObjectDetection/prepare_model.sh)
- [mobile/examples/object_detection/ios/Podfile](mobile/examples/object_detection/ios/Podfile)
- [mobile/examples/question_answering/ios/ORTQuestionAnswering/Podfile](mobile/examples/question_answering/ios/ORTQuestionAnswering/Podfile)
- [mobile/examples/speech_recognition/ios/Podfile](mobile/examples/speech_recognition/ios/Podfile)
- [mobile/examples/super_resolution/ios/ORTSuperResolution/Podfile](mobile/examples/super_resolution/ios/ORTSuperResolution/Podfile)

</details>



This document details the Continuous Integration and Continuous Deployment (CI/CD) pipelines and build systems used in the ONNX Runtime Inference Examples repository. It covers the configuration, workflow, and functionality of the build infrastructure that ensures examples are properly tested across different platforms.

For information about specific example implementations, refer to the respective pages for [Mobile Examples](#2), [C/C++ Examples](#3), [C# Examples](#4), [Python Examples](#5), and [JavaScript Examples](#6).

## Overview of CI/CD Architecture

The repository uses two primary CI/CD pipelines:

1. **Mobile Examples Pipeline** - Azure Pipelines-based system for building and testing mobile examples
2. **OneBranch Pipeline** - Microsoft's internal CI/CD system for building and testing C/C++ examples with compliance checks

These pipelines work with various build systems depending on the target platform:
- **CMake** for C/C++ examples
- **CocoaPods** for iOS examples
- **Gradle** for Android examples
- **.NET SDK** for C# examples

## Mobile Examples Pipeline

The Mobile Examples Pipeline handles the building and testing of all mobile platform examples, using a stage-based approach to validate different platforms and example types.

```mermaid
flowchart TD
    MobilePipeline["Mobile Examples Pipeline
    ci_build/azure_pipelines/mobile-examples-pipeline.yml"] --> ProcessParameters["ProcessParameters Stage
    - Parse OrtPodVersion parameter"]
    
    ProcessParameters --> iOSStages["iOS Example Stages"]
    ProcessParameters --> AndroidStages["Android Example Stages"]
    
    iOSStages --> BasicUsageIos["BasicUsageIos Stage"]
    iOSStages --> SpeechRecognitionIos["SpeechRecognitionIos Stage"]
    iOSStages --> ObjectDetectionIos["ObjectDetectionIos Stage"]
    iOSStages --> SuperResolutionIos["SuperResolutionIos Stage"]
    iOSStages --> QuestionAnsweringIos["QuestionAnsweringIos Stage"]
    
    AndroidStages --> WhisperLocalAndroid["WhisperLocalAndroid Stage"]
    AndroidStages --> WhisperAzureAndroid["WhisperAzureAndroid Stage"]
    AndroidStages --> ObjectDetectionAndroid["ObjectDetectionAndroid Stage"]
    AndroidStages --> ImageClassificationAndroid["ImageClassificationAndroid Stage"]
    AndroidStages --> SuperResolutionAndroid["SuperResolutionAndroid Stage"]
    AndroidStages --> QuestionAnsweringAndroid["QuestionAnsweringAndroid Stage"]
```

Sources: [ci_build/azure_pipelines/mobile-examples-pipeline.yml:1-351]()

### Pipeline Parameters and Variables

The Mobile Examples Pipeline accepts the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `OrtPodVersion` | ONNX Runtime Pod version to use | "default" |

Key variables include:

| Variable | Value | Purpose |
|----------|-------|---------|
| `AndroidTestAgentPool` | "onnxruntime-Ubuntu2204-AMD-CPU" | Pool for Android tests |
| `IosTestAgentVmImage` | "macOS-14" | VM image for iOS tests |

Sources: [ci_build/azure_pipelines/mobile-examples-pipeline.yml:1-11]()

### Example Job: iOS Build Process

A typical iOS example build follows these steps:

1. **Process Parameters Stage** - Parse the `OrtPodVersion` parameter
2. **Generate/Download Model** - Prepare the model using Python scripts
3. **Update Podfile** - Modify the Podfile to use the specified ORT version
4. **Install CocoaPods** - Install dependencies using `pod install`
5. **Build and Test** - Use Xcode to build and test the example

```mermaid
flowchart LR
    Setup["Setup
    - Python setup
    - Process OrtPodVersion"] --> GenerateModel["Generate Model
    - Use Python scripts
    - Create ONNX/ORT models"]
    
    GenerateModel --> UpdatePodfile["Update Podfile
    - Set ORT version
    - templates/update-podfile-step.yml"]
    
    UpdatePodfile --> PodInstall["Pod Install
    - Install onnxruntime-objc
    - Setup dependencies"]
    
    PodInstall --> XcodeBuild["Xcode Build & Test
    - iOS simulator
    - templates/xcode-build-and-test-step.yml"]
```

Sources: [ci_build/azure_pipelines/mobile-examples-pipeline.yml:46-88](), [ci_build/azure_pipelines/templates/xcode-build-and-test-step.yml:1-32]()

### Example Job: Android Build Process

A typical Android example build follows these steps:

1. **Process Parameters Stage** - Parse parameters
2. **Setup Python and JDK** - Configure build environment
3. **Generate/Download Model** (if needed) - Prepare model files
4. **Setup Android Emulator** - Configure emulator for testing
5. **Build and Test** - Use Gradle to build and run tests

```mermaid
flowchart LR
    Setup["Setup
    - Python setup
    - JDK setup"] --> EmulatorSetup["Emulator Setup
    - Configure Android Emulator
    - templates/run-with-android-emulator-steps.yml"]
    
    EmulatorSetup --> GradleBuild["Gradle Build & Test
    - connectedDebugAndroidTest
    - Android device tests"]
```

Sources: [ci_build/azure_pipelines/mobile-examples-pipeline.yml:90-129]()

## OneBranch Pipeline

The OneBranch Pipeline is used for building and testing C/C++ examples with additional compliance and security checks. There are two variants:

1. **OneBranch.Official.yml** - For production builds with TSA security analysis
2. **OneBranch.PullRequest.yml** - For pull request validation without TSA

```mermaid
flowchart TD
    OneBranchPipeline["OneBranch Pipeline
    .pipelines/OneBranch.Official.yml"] --> LinuxStage["linux_stage
    - Build Linux Examples"]
    
    OneBranchPipeline --> WindowsStage["Windows_Build
    - Build Windows Examples"]
    
    OneBranchPipeline --> ComplianceChecks["Compliance Checks
    - TSA, BinSkim, PoliCheck"]
    
    LinuxStage --> VersionSetup["Setup BuildNumber
    - onebranch.pipeline.version@1"]
    VersionSetup --> DownloadORT_Linux["Download ORT Binaries
    - download_ort_release_and_install_deps.sh"]
    DownloadORT_Linux --> CMakeBuild["CMake Build
    - Configure & Make"]
    
    WindowsStage --> VCPKGCheckout["Checkout VCPKG
    - microsoft/vcpkg"]
    VCPKGCheckout --> VSLocate["Locate Visual Studio
    - vswhere.exe"]
    VSLocate --> DownloadORT_Win["Download ORT
    - download_ort_release.ps1"]
    DownloadORT_Win --> CMakeWindows["Configure CMake
    - vcpkg toolchain"]
    CMakeWindows --> VSBuild["VS Build
    - onnxruntime_samples.sln"]
```

Sources: [.pipelines/OneBranch.Official.yml:1-161](), [.pipelines/OneBranch.PullRequest.yml:1-161]()

### Pipeline Parameters and Variables

The OneBranch Pipeline accepts the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `debug` | Enable debug output | false |
| `ortversion` | ONNX Runtime Version | "1.15.1" |

Key variables include:

| Variable | Value | Purpose |
|----------|-------|---------|
| `ROOT` / `REPOROOT` | `$(Build.SourcesDirectory)` | Source code root |
| `OUTPUTROOT` | `$(REPOROOT)\out` | Output directory |
| `WindowsContainerImage` | `onebranch.azurecr.io/windows/ltsc2019/vse2022:latest` | Windows container |
| `LinuxContainerImage` | `onebranch.azurecr.io/linux/ubuntu-2004:latest` | Linux container |

Sources: [.pipelines/OneBranch.Official.yml:13-34]()

## Build Systems

### C/C++ Build System (CMake)

The C/C++ examples use CMake for building, with support for various execution providers and platform-specific configurations.

```mermaid
flowchart TD
    CMake["CMake Build System
    c_cxx/CMakeLists.txt"] --> ConfigOptions["Configuration Options
    - onnxruntime_USE_CUDA
    - onnxruntime_USE_TENSORRT
    - LIBPNG_ROOTDIR
    - ONNXRUNTIME_ROOTDIR"]
    
    CMake --> IncludePaths["Include Paths
    - ONNXRUNTIME_ROOTDIR/include"]
    
    CMake --> Dependencies["Dependencies"]
    Dependencies --> WIL["WIL (Windows)"]
    Dependencies --> ImageLibs["Image Libraries"]
    ImageLibs --> JPEG["JPEG (Linux)"]
    ImageLibs --> PNG["PNG (Linux)"]
    ImageLibs --> WIC["Windows Image Component (Windows)"]
    
    CMake --> Definitions["Conditional Definitions
    - USE_CUDA
    - USE_TENSORRT
    - USE_DML"]
    
    CMake --> HelperFunctions["Helper Functions
    - copy_ort_dlls"]
    
    CMake --> Subdirectories["Subdirectories"]
    Subdirectories --> Squeezenet["squeezenet"]
    Subdirectories --> StyleTransfer["fns_candy_style_transfer"]
    Subdirectories --> ModelExplorer["model-explorer"]
    Subdirectories --> Windows["Windows-only
    - imagenet
    - MNIST"]
```

Sources: [c_cxx/CMakeLists.txt:1-100]()

#### Example C/C++ Build Process

The style transfer example demonstrates a typical C/C++ build and execution process:

```mermaid
flowchart LR
    StyleTransfer["Style Transfer
    fns_candy_style_transfer.c"] --> OrtAPI["ONNX Runtime C API
    - g_ort = OrtGetApiBase()->GetApi()"]
    
    OrtAPI --> CreateSession["Create Session
    - CreateEnv
    - CreateSessionOptions
    - CreateSession"]
    
    CreateSession --> ConfigProviders["Configure Providers
    - CPU (default)
    - CUDA (optional)
    - DirectML (optional)"]
    
    ConfigProviders --> RunInference["Run Inference
    - CreateTensorWithDataAsOrtValue
    - Run
    - GetTensorMutableData"]
    
    RunInference --> ProcessOutput["Process Output
    - Convert CHW to HWC
    - Write output image"]
```

Sources: [c_cxx/fns_candy_style_transfer/fns_candy_style_transfer.c:1-233]()

### iOS Build System (CocoaPods)

iOS examples use CocoaPods for dependency management, with Xcode as the build system.

```mermaid
flowchart TD
    Podfile["Podfile
    mobile/examples/*/ios/Podfile"] --> PlatformSpec["Platform Specification
    - platform :ios, '13.0'"]
    
    Podfile --> Targets["Target Configuration"]
    Targets --> MainTarget["Main Target
    - use_frameworks!"]
    Targets --> TestTarget["Test Target
    - inherit! :search_paths"]
    
    Podfile --> Dependencies["ONNX Runtime Dependencies"]
    Dependencies --> ORT_ObjC["onnxruntime-objc
    - Objective-C/Swift API"]
    Dependencies --> ORT_C["onnxruntime-c
    - C API"]
    Dependencies --> ORT_Extensions["onnxruntime-extensions-c
    - Extensions API"]
```

Sources: [mobile/examples/basic_usage/ios/Podfile:1-12](), [mobile/examples/object_detection/ios/Podfile:1-13](), [mobile/examples/speech_recognition/ios/Podfile:1-12](), [mobile/examples/super_resolution/ios/ORTSuperResolution/Podfile:1-22](), [mobile/examples/question_answering/ios/ORTQuestionAnswering/Podfile:1-21]()

### Android Build System (Gradle)

Android examples use Gradle for building, with tasks for building and running tests on emulators.

```mermaid
flowchart LR
    Gradle["Gradle Build System"] --> Tasks["Gradle Tasks"]
    Tasks --> Build["connectedDebugAndroidTest
    - Build APK
    - Run instrumented tests"]
    
    Gradle --> Dependencies["Dependencies"]
    Dependencies --> ORT_Android["onnxruntime-android"]
    Dependencies --> AndroidLibs["Android Libraries"]
```

Sources: [ci_build/azure_pipelines/mobile-examples-pipeline.yml:101-108](), [ci_build/azure_pipelines/mobile-examples-pipeline.yml:122-129]()

### C# Build System (.NET SDK)

C# examples use the .NET SDK build system with NuGet package references.

```mermaid
flowchart TD
    CSProj["Project File
    c_sharp/image_classification/image_classification.csproj"] --> ProjectProps["Project Properties
    - TargetFramework: net6.0"]
    
    CSProj --> PackageRefs["Package References"]
    PackageRefs --> ORT["Microsoft.ML.OnnxRuntime
    - Version: 1.16.0"]
    PackageRefs --> ORT_Managed["Microsoft.ML.OnnxRuntime.Managed
    - Version: 1.16.0"]
    PackageRefs --> ImageSharp["SixLabors.ImageSharp
    - Version: 2.1.9"]
```

Sources: [c_sharp/image_classification/image_classification.csproj:1-15]()

## CI Pipeline Templates

The CI system uses several reusable templates to standardize operations across different examples:

### Xcode Build and Test Template

```mermaid
flowchart TD
    XcodeTemplate["Xcode Build Template
    xcode-build-and-test-step.yml"] --> Parameters["Parameters
    - xcWorkspacePath
    - scheme
    - args (optional)"]
    
    XcodeTemplate --> XcodeTask["Xcode@5 Task"]
    XcodeTask --> Actions["actions: 'test'"]
    XcodeTask --> Configuration["configuration: 'Debug'"]
    XcodeTask --> SDK["sdk: 'iphonesimulator'"]
    XcodeTask --> XcodeVersion["xcodeVersion: 'specifyPath'"]
    XcodeTask --> DeveloperDir["xcodeDeveloperDir: '/Applications/Xcode_15.4.app/Contents/Developer'"]
    XcodeTask --> Destination["destinationSimulators: 'iPhone 15,OS=17.5'"]
```

Sources: [ci_build/azure_pipelines/templates/xcode-build-and-test-step.yml:1-32]()

### Python and JDK Setup Templates

```mermaid
flowchart LR
    PythonTemplate["Python Setup Template
    use-python-step.yml"] --> PythonTask["UsePythonVersion@0
    - versionSpec: 3.9
    - architecture: x64"]
    
    JDKTemplate["JDK Setup Template"] --> JDKTask["JavaToolInstaller@0
    - versionSpec: 11
    - architecture: x64"]
```

Sources: [ci_build/azure_pipelines/templates/use-python-step.yml:1-13]()

## Model Preparation Process

Many examples require model preparation as part of the build process. This typically involves:

1. **Installing Python dependencies** - Using `pip install` with requirements files
2. **Downloading pre-trained models** - From model repositories 
3. **Model conversion** - Converting to ONNX or ORT format
4. **Placing models in correct location** - For access during tests

Example: Object Detection iOS model preparation:

```mermaid
flowchart TD
    PrepModel["prepare_model.sh"] --> DownloadModel["Download TFLite Model
    - curl from Kaggle API"]
    
    DownloadModel --> ExtractModel["Extract Model
    - tar -xzf
    - unzip labelmap.txt"]
    
    ExtractModel --> ConvertToONNX["Convert to ONNX
    - tf2onnx.convert
    - --opset 13"]
    
    ConvertToONNX --> ConvertToORT["Convert to ORT Format
    - onnxruntime.tools.convert_onnx_models_to_ort"]
```

Sources: [mobile/examples/object_detection/ios/ORTObjectDetection/prepare_model.sh:1-32]()

## Security and Compliance

The OneBranch pipelines include security and compliance checks configured through:

```mermaid
flowchart TD
    ComplianceConfig["Compliance Configuration"] --> TSA["TSA Security Analysis
    - .config/tsaoptions.json"]
    
    ComplianceConfig --> BinSkim["BinSkim Analysis
    - Binary analysis for security issues"]
    
    ComplianceConfig --> PoliCheck["PoliCheck Analysis
    - Scans for sensitive terms
    - Uses exclusion list"]
    
    TSA --> TSASettings["TSA Settings
    - notificationAliases: ort-engsys@microsoft.com
    - areaPath: ONNX Runtime\\Engineering Systems
    - projectName: ONNX Runtime"]
```

Sources: [.pipelines/OneBranch.Official.yml:51-60](), [.config/tsaoptions.json:1-10]()

## Conclusion

The CI/CD and build systems in the ONNX Runtime Inference Examples repository enable reliable testing across multiple platforms and example types. They ensure examples remain functional across different versions of ONNX Runtime and provide a standardized process for building examples on various platforms.

For more detailed information about specific pipeline configurations, refer to [Mobile Examples Pipeline](#8.1) and [OneBranch Pipeline](#8.2).

Sources: [ci_build/azure_pipelines/mobile-examples-pipeline.yml](), [.pipelines/OneBranch.Official.yml](), [.pipelines/OneBranch.PullRequest.yml](), [c_cxx/CMakeLists.txt]()

---

