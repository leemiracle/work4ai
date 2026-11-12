<!-- source: DeepWiki mcp.deepwiki.com · repo android/media-samples · page 2 Picture-in-Picture Samples · fetched 2026-10-23 -->

# Picture-in-Picture Samples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PictureInPicture/app/build.gradle](PictureInPicture/app/build.gradle)
- [PictureInPicture/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.java](PictureInPicture/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.java)
- [PictureInPicture/app/src/androidTest/java/com/example/android/pictureinpicture/MediaSessionPlaybackActivityTest.java](PictureInPicture/app/src/androidTest/java/com/example/android/pictureinpicture/MediaSessionPlaybackActivityTest.java)
- [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MainActivity.java](PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MainActivity.java)
- [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MediaSessionPlaybackActivity.java](PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MediaSessionPlaybackActivity.java)
- [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/widget/MovieView.java](PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/widget/MovieView.java)
- [PictureInPictureKotlin/README.md](PictureInPictureKotlin/README.md)
- [PictureInPictureKotlin/app/src/main/AndroidManifest.xml](PictureInPictureKotlin/app/src/main/AndroidManifest.xml)
- [PictureInPictureKotlin/app/src/main/res/values/dimens.xml](PictureInPictureKotlin/app/src/main/res/values/dimens.xml)
- [PictureInPictureKotlin/app/src/main/res/values/strings.xml](PictureInPictureKotlin/app/src/main/res/values/strings.xml)

</details>



This document covers the Picture-in-Picture demonstration projects in the Android Media Samples repository. These samples showcase how to implement Picture-in-Picture (PiP) mode functionality in Android applications, providing both Kotlin and Java implementations with different approaches to media control integration.

The samples demonstrate PiP mode for video playback scenarios and interactive applications like stopwatches. For broader video playback examples using ExoPlayer, see [VideoPlayer Sample](#3). For other media functionality demonstrations, see [Other Media Samples](#4).

## Sample Projects Overview

The repository contains two primary PiP sample applications that demonstrate different implementation approaches:

| Sample | Language | Key Features | Activities |
|--------|----------|--------------|------------|
| PictureInPictureKotlin | Kotlin | Stopwatch + Video examples, RemoteActions, MediaSession | `MainActivity`, `MovieActivity` |
| PictureInPicture | Java | Video playback with custom controls, MediaSession integration | `MainActivity`, `MediaSessionPlaybackActivity` |

Both samples target Android API level 26+ (Android 8.0 Oreo) where PiP mode was introduced for handheld devices.

**Sources:** [PictureInPictureKotlin/README.md:1-65](), [PictureInPicture/app/build.gradle:20-27]()

## PictureInPictureKotlin Architecture

The Kotlin implementation provides the most comprehensive PiP demonstration with multiple activity examples and modern Android architecture patterns.

```mermaid
graph TB
    subgraph "PictureInPictureKotlin Project"
        MainActivity[MainActivity<br/>"Stopwatch Example"]
        MovieActivity[MovieActivity<br/>"Video Playback Example"] 
        MainViewModel[MainViewModel<br/>"Stopwatch Logic"]
        
        subgraph "Android Framework APIs"
            PiPParams[PictureInPictureParams]
            RemoteAction[RemoteAction]
            MediaSession[MediaSessionCompat]
            BroadcastReceiver[BroadcastReceiver]
        end
        
        subgraph "Testing Components"
            MainActivityTest[MainActivityTest]
            MovieActivityTest[MovieActivityTest]
        end
    end
    
    MainActivity --> MainViewModel
    MainActivity --> PiPParams
    MainActivity --> RemoteAction
    MainActivity --> BroadcastReceiver
    
    MovieActivity --> MediaSession
    MovieActivity --> PiPParams
    
    MainActivityTest --> MainActivity
    MovieActivityTest --> MovieActivity
```

**Core Components:**

- **`MainActivity`**: Demonstrates PiP with a stopwatch application using `RemoteAction` controls
- **`MovieActivity`**: Shows video playback in PiP mode with `MediaSessionCompat` integration  
- **`MainViewModel`**: Manages stopwatch state using LiveData pattern
- **Testing Infrastructure**: Comprehensive UI tests using Espresso framework

**Sources:** [PictureInPictureKotlin/app/src/main/AndroidManifest.xml:28-43](), [PictureInPictureKotlin/app/src/main/res/values/strings.xml:20-47]()

## PictureInPicture (Java) Architecture

The Java implementation focuses on video playback scenarios with two different control approaches.

```mermaid
graph TB
    subgraph "PictureInPicture Java Project"
        JavaMainActivity[MainActivity<br/>"Custom RemoteActions"]
        MediaSessionActivity[MediaSessionPlaybackActivity<br/>"MediaSession Integration"]
        MovieView[MovieView<br/>"Custom Video Widget"]
        
        subgraph "Media Components"
            MediaPlayer[MediaPlayer]
            SurfaceView[SurfaceView]
            MediaSessionCompat[MediaSessionCompat]
            PlaybackStateCompat[PlaybackStateCompat]
        end
        
        subgraph "PiP Framework"
            PictureInPictureParams[PictureInPictureParams.Builder]
            RemoteActionImpl[RemoteAction]
            PendingIntent[PendingIntent]
        end
        
        subgraph "Testing"
            JavaMainTest[MainActivityTest]
            MediaSessionTest[MediaSessionPlaybackActivityTest]
        end
    end
    
    JavaMainActivity --> MovieView
    JavaMainActivity --> PictureInPictureParams
    JavaMainActivity --> RemoteActionImpl
    JavaMainActivity --> PendingIntent
    
    MediaSessionActivity --> MovieView
    MediaSessionActivity --> MediaSessionCompat
    MediaSessionActivity --> PlaybackStateCompat
    
    MovieView --> MediaPlayer
    MovieView --> SurfaceView
    
    JavaMainTest --> JavaMainActivity
    MediaSessionTest --> MediaSessionActivity
```

**Key Implementation Classes:**

- **`MainActivity`**: Custom PiP controls using `RemoteAction` and `BroadcastReceiver`
- **`MediaSessionPlaybackActivity`**: PiP integration with Android's `MediaSessionCompat` 
- **`MovieView`**: Custom video playback widget with built-in controls
- **Testing**: Separate test classes for both activity implementations

**Sources:** [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MainActivity.java:46-49](), [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MediaSessionPlaybackActivity.java:40-43](), [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/widget/MovieView.java:45-51]()

## PiP Implementation Patterns

### RemoteAction Pattern (Custom Controls)

The `MainActivity` in the Java sample demonstrates custom PiP controls using `RemoteAction`:

```mermaid
graph LR
    subgraph "PiP Remote Action Flow"
        EnterPiP[enterPictureInPictureMode]
        RemoteActionSetup[RemoteAction<br/>"Play/Pause/Info"]
        PendingIntentCreate[PendingIntent.getBroadcast]
        BroadcastReceiverHandle[BroadcastReceiver.onReceive]
        ActionExecution[Execute Action<br/>"CONTROL_TYPE_PLAY/PAUSE"]
    end
    
    EnterPiP --> RemoteActionSetup
    RemoteActionSetup --> PendingIntentCreate
    PendingIntentCreate --> BroadcastReceiverHandle
    BroadcastReceiverHandle --> ActionExecution
```

**Key Implementation Details:**

- **Action Constants**: `CONTROL_TYPE_PLAY` (1), `CONTROL_TYPE_PAUSE` (2) for intent extras
- **Request Codes**: `REQUEST_PLAY` (1), `REQUEST_PAUSE` (2), `REQUEST_INFO` (3) for distinct `PendingIntent` instances
- **BroadcastReceiver**: Registered/unregistered in `onPictureInPictureModeChanged()`

**Sources:** [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MainActivity.java:54-84](), [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MainActivity.java:245-283]()

### MediaSession Integration Pattern

The `MediaSessionPlaybackActivity` shows integration with Android's media session framework:

**MediaSession Configuration:**
- **Session Creation**: `MediaSessionCompat(this, TAG)` with custom callback
- **Metadata Setup**: `MediaMetadataCompat.Builder()` with display title
- **Playback State**: `PlaybackStateCompat.Builder()` with supported actions

**Action Mapping:**
- `MEDIA_ACTIONS_PLAY_PAUSE`: Basic play/pause functionality
- `MEDIA_ACTIONS_ALL`: Includes skip next/previous actions
- **Dynamic Actions**: Actions updated based on playlist position

**Sources:** [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MediaSessionPlaybackActivity.java:47-56](), [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/MediaSessionPlaybackActivity.java:136-158]()

## MovieView Custom Component

The `MovieView` class provides a reusable video playback widget with PiP-aware controls:

### Component Structure

| Component | Type | Purpose |
|-----------|------|---------|
| `mSurfaceView` | `SurfaceView` | Video rendering surface |
| `mMediaPlayer` | `MediaPlayer` | Video playback engine |
| `mToggle`, `mFastForward`, `mFastRewind`, `mMinimize` | `ImageButton` | Playback controls |
| `mShade` | `View` | Control overlay background |
| `TimeoutHandler` | `Handler` | Auto-hide controls timer |

### Control Behavior

- **Auto-hide**: Controls fade after `TIMEOUT_CONTROLS` (3000ms) during playback
- **Fast Forward/Rewind**: Jump by `FAST_FORWARD_REWIND_INTERVAL` (5000ms)
- **Aspect Ratio**: Dynamic sizing based on `mAdjustViewBounds` setting
- **Lifecycle Management**: Proper `MediaPlayer` resource cleanup

**Sources:** [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/widget/MovieView.java:77-132](), [PictureInPicture/app/src/main/java/com/example/android/pictureinpicture/widget/MovieView.java:521-543]()

## Testing Infrastructure

Both samples include comprehensive testing using Espresso framework:

### Test Coverage Areas

| Test Class | Target Activity | Test Scenarios |
|------------|-----------------|----------------|
| `MainActivityTest` | `MainActivity` | PiP mode entry, video playback, orientation changes |
| `MediaSessionPlaybackActivityTest` | `MediaSessionPlaybackActivity` | MediaSession state validation, PiP behavior |

### Key Test Methods

- **`movie_playingOnPip()`**: Verifies video continues playing when entering PiP mode
- **`movie_pauseAndResume()`**: Tests play/pause functionality and MediaSession state
- **`fullscreen_enabledOnLandscape()`**: Validates immersive mode behavior
- **Custom Matchers**: `isPlaying()` matcher for `MovieView` state verification

**Testing Pattern:**
```
onView(withId(R.id.movie))
    .check(matches(allOf(isDisplayed(), isPlaying())))
    .perform(showControls());
```

**Sources:** [PictureInPicture/app/src/androidTest/java/com/example/android/pictureinpicture/MainActivityTest.java:61-79](), [PictureInPicture/app/src/androidTest/java/com/example/android/pictureinpicture/MediaSessionPlaybackActivityTest.java:65-86]()

## Build Configuration

### Gradle Dependencies

Both samples share similar dependency patterns:

**Core Dependencies:**
- `androidx.core:core` - AndroidX core functionality
- `androidx.appcompat:appcompat` - AppCompat support
- `androidx.media:media` - MediaSessionCompat support

**Test Dependencies:**
- `androidx.test:runner`, `androidx.test:rules` - Testing framework
- `androidx.test.espresso:espresso-core` - UI testing
- `junit:junit` - Unit testing framework

### Manifest Configuration

**Required PiP Settings:**
- `android:supportsPictureInPicture="true"` - Enable PiP mode
- `android:configChanges="screenSize|smallestScreenSize|screenLayout|orientation"` - Handle configuration changes
- **API Level**: `minSdkVersion 26` for PiP support

**Sources:** [PictureInPicture/app/build.gradle:41-51](), [PictureInPictureKotlin/app/src/main/AndroidManifest.xml:28-43]()

---

