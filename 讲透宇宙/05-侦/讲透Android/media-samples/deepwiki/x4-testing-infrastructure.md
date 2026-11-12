<!-- source: DeepWiki mcp.deepwiki.com · repo android/media-samples · extra page Testing Infrastructure · fetched 2026-10-23 -->

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PictureInPictureKotlin/app/src/androidTest/AndroidManifest.xml](PictureInPictureKotlin/app/src/androidTest/AndroidManifest.xml)
- [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.kt](PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.kt)
- [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MovieActivityTest.kt](PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MovieActivityTest.kt)

</details>



This document covers the comprehensive testing infrastructure for the PictureInPictureKotlin sample application. The testing system focuses on UI automation and integration testing to validate Picture-in-Picture functionality, media playback behavior, and user interface interactions.

For information about the actual MainActivity and MovieActivity components being tested, see [MainActivity - Stopwatch Example](#2.1.1) and [MovieActivity - Video Playback Example](#2.1.2).

## Test Architecture Overview

The testing infrastructure uses Android's instrumentation testing framework with Espresso for UI automation. The system provides comprehensive coverage of both PiP modes and media playback scenarios.

### Testing Framework Integration

```mermaid
graph TB
    subgraph "Android Testing Framework"
        AndroidJUnit4["AndroidJUnit4"]
        InstrumentationRegistry["InstrumentationRegistry"]
        ActivityScenario["ActivityScenario"]
    end
    
    subgraph "UI Testing Libraries"
        Espresso["Espresso"]
        ViewMatchers["ViewMatchers"]
        ViewActions["ViewActions"]
        ViewAssertions["ViewAssertions"]
    end
    
    subgraph "Assertion Libraries"
        Truth["Google Truth"]
        Hamcrest["Hamcrest Matchers"]
    end
    
    subgraph "Test Classes"
        MainActivityTest["MainActivityTest"]
        MovieActivityTest["MovieActivityTest"]
    end
    
    subgraph "Target Components"
        MainActivity["MainActivity"]
        MovieActivity["MovieActivity"]
        MovieView["MovieView"]
    end
    
    AndroidJUnit4 --> MainActivityTest
    AndroidJUnit4 --> MovieActivityTest
    ActivityScenario --> MainActivityTest
    ActivityScenario --> MovieActivityTest
    
    Espresso --> MainActivityTest
    Espresso --> MovieActivityTest
    ViewMatchers --> MainActivityTest
    ViewMatchers --> MovieActivityTest
    
    Truth --> MainActivityTest
    Truth --> MovieActivityTest
    Hamcrest --> MovieActivityTest
    
    MainActivityTest --> MainActivity
    MovieActivityTest --> MovieActivity
    MovieActivityTest --> MovieView
```

**Sources:** [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.kt:1-61](), [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MovieActivityTest.kt:1-164]()

## Test Classes and Coverage

### MainActivityTest

The `MainActivityTest` class provides focused testing for the stopwatch-based PiP functionality. It validates core PiP behavior and timer operations using minimal test cases.

```mermaid
graph TB
    subgraph "MainActivityTest Structure"
        TestClass["MainActivityTest"]
        StartTest["start()"]
        PipTest["pip()"]
    end
    
    subgraph "Test Targets"
        MainActivity["MainActivity"]
        StopwatchTimer["Stopwatch Timer"]
        PipMode["PiP Mode"]
    end
    
    subgraph "UI Components"
        TimeView["R.id.time"]
        StartButton["R.id.start_or_pause"]
        PipButton["R.id.pip"]
    end
    
    TestClass --> StartTest
    TestClass --> PipTest
    
    StartTest --> StopwatchTimer
    StartTest --> TimeView
    StartTest --> StartButton
    
    PipTest --> PipMode
    PipTest --> PipButton
    PipTest --> MainActivity
```

**Key Test Methods:**

| Test Method | Purpose | Validation |
|-------------|---------|------------|
| `start()` | Validates stopwatch functionality | Timer updates from "00:00:00" when started |
| `pip()` | Tests PiP mode transition | `isInPictureInPictureMode` property changes |

**Sources:** [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.kt:39-60]()

### MovieActivityTest

The `MovieActivityTest` class provides comprehensive testing for video playback scenarios, MediaSession integration, and complex PiP behavior with media controls.

```mermaid
graph TB
    subgraph "MovieActivityTest Structure"
        TestClass["MovieActivityTest"]
        PipPlayingTest["movie_playingOnPip()"]
        PauseResumeTest["movie_pauseAndResume()"]
        LandscapeTest["fullscreen_enabledOnLandscape()"]
        PortraitTest["fullscreen_disabledOnPortrait()"]
    end
    
    subgraph "Test Infrastructure"
        ActivityRule["ActivityScenarioRule"]
        CustomMatchers["Custom ViewMatchers"]
        CustomActions["Custom ViewActions"]
    end
    
    subgraph "Target Components"
        MovieActivity["MovieActivity"]
        MovieView["MovieView"]
        MediaController["MediaController"]
        PlaybackState["PlaybackStateCompat"]
    end
    
    TestClass --> ActivityRule
    TestClass --> PipPlayingTest
    TestClass --> PauseResumeTest
    TestClass --> LandscapeTest
    TestClass --> PortraitTest
    
    ActivityRule --> MovieActivity
    CustomMatchers --> MovieView
    CustomActions --> MovieView
    
    PipPlayingTest --> PlaybackState
    PauseResumeTest --> MediaController
```

**Advanced Test Features:**

| Feature | Implementation | Purpose |
|---------|----------------|---------|
| Custom Matcher | `isPlaying()` | Validates `MovieView.isPlaying` state |
| Custom Action | `showControls()` | Triggers control visibility in `MovieView` |
| MediaSession Testing | `assertMediaStateIs()` | Validates `PlaybackStateCompat` states |
| Orientation Testing | Screen rotation | Tests fullscreen behavior changes |

**Sources:** [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MovieActivityTest.kt:52-164]()

## Testing Methodology

### Picture-in-Picture Testing Strategy

The testing approach validates PiP functionality through direct activity state inspection and UI interaction patterns.

```mermaid
graph LR
    subgraph "PiP Test Flow"
        LaunchActivity["launchActivity<T>()"]
        CheckInitialState["Check Normal Mode"]
        TriggerPip["Click PiP Button"]
        ValidatePipState["Assert isInPictureInPictureMode"]
        CheckContinuity["Validate State Continuity"]
    end
    
    subgraph "State Validation"
        ActivityState["Activity.isInPictureInPictureMode"]
        ViewState["View State Preservation"]
        MediaState["MediaSession State"]
    end
    
    LaunchActivity --> CheckInitialState
    CheckInitialState --> TriggerPip
    TriggerPip --> ValidatePipState
    ValidatePipState --> CheckContinuity
    
    CheckInitialState --> ActivityState
    ValidatePipState --> ActivityState
    CheckContinuity --> ViewState
    CheckContinuity --> MediaState
```

**Sources:** [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.kt:49-59](), [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MovieActivityTest.kt:56-76]()

### MediaSession Integration Testing

The test infrastructure validates MediaSession state consistency across PiP transitions and playback control interactions.

```mermaid
graph TB
    subgraph "MediaSession Test Pattern"
        InitialCheck["Check Initial Playback State"]
        UserAction["Perform UI Action"]
        StateValidation["Validate MediaController State"]
        ViewValidation["Validate View State"]
    end
    
    subgraph "State Types"
        PlayingState["STATE_PLAYING"]
        PausedState["STATE_PAUSED"]
        ViewPlaying["MovieView.isPlaying"]
    end
    
    subgraph "Test Actions"
        ToggleClick["Click R.id.toggle"]
        PipClick["Click R.id.minimize"]
        ShowControls["Custom showControls()"]
    end
    
    InitialCheck --> UserAction
    UserAction --> StateValidation
    StateValidation --> ViewValidation
    
    StateValidation --> PlayingState
    StateValidation --> PausedState
    ViewValidation --> ViewPlaying
    
    UserAction --> ToggleClick
    UserAction --> PipClick
    UserAction --> ShowControls
```

**Sources:** [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MovieActivityTest.kt:79-94](), [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MovieActivityTest.kt:126-132]()

## Test Configuration

### AndroidManifest Configuration

The test manifest defines the instrumentation testing environment with required activity declarations for the Android Test Infrastructure.

```mermaid
graph TB
    subgraph "Test Manifest Structure"
        TestManifest["androidTest/AndroidManifest.xml"]
        TestPackage["com.example.android.pictureinpicture.test"]
    end
    
    subgraph "Required Test Activities"
        BootstrapActivity["InstrumentationActivityInvoker$BootstrapActivity"]
        EmptyActivity["InstrumentationActivityInvoker$EmptyActivity"]
        EmptyFloatingActivity["InstrumentationActivityInvoker$EmptyFloatingActivity"]
    end
    
    TestManifest --> TestPackage
    TestPackage --> BootstrapActivity
    TestPackage --> EmptyActivity
    TestPackage --> EmptyFloatingActivity
```

**Sources:** [PictureInPictureKotlin/app/src/androidTest/AndroidManifest.xml:17-33]()

### Test Dependencies and Framework Integration

The testing infrastructure integrates multiple Android testing libraries with specific annotations and configurations:

| Component | Usage | Purpose |
|-----------|--------|---------|
| `@RunWith(AndroidJUnit4::class)` | Test runner configuration | Enables Android instrumentation testing |
| `@LargeTest` | Test categorization | Marks UI integration tests |
| `ActivityScenarioRule` | Activity lifecycle management | Provides controlled activity testing environment |
| `launchActivity<T>()` | Activity launching | Creates activity instances for testing |
| `InstrumentationRegistry` | Test synchronization | Manages test execution timing |

**Sources:** [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.kt:35-37](), [PictureInPictureKotlin/app/src/androidTest/java/com/example/android/pictureinpicture/MovieActivityTest.kt:48-53]()

---

