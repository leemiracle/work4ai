<!-- source: DeepWiki mcp.deepwiki.com · repo android/media-samples · extra page MovieActivity - Video Playback Example · fetched 2026-10-23 -->

# MovieActivity - Video Playback Example

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainViewModel.kt](PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainViewModel.kt)
- [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt](PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt)
- [PictureInPictureKotlin/app/src/main/res/drawable/ic_refresh_24dp.xml](PictureInPictureKotlin/app/src/main/res/drawable/ic_refresh_24dp.xml)
- [PictureInPictureKotlin/app/src/main/res/layout/main_activity.xml](PictureInPictureKotlin/app/src/main/res/layout/main_activity.xml)
- [PictureInPictureKotlin/app/src/main/res/layout/movie_activity.xml](PictureInPictureKotlin/app/src/main/res/layout/movie_activity.xml)

</details>



## Purpose and Scope

This document covers the `MovieActivity` component within the PictureInPictureKotlin sample, which demonstrates advanced video playback functionality integrated with Android's MediaSession framework and Picture-in-Picture mode. The `MovieActivity` showcases how to properly implement media controls, lifecycle management, and seamless transitions between fullscreen and PiP modes for video content.

For information about the stopwatch-based PiP example, see [MainActivity - Stopwatch Example](#2.1.1). For comprehensive testing approaches across both examples, see [Testing Infrastructure](#2.1.3).

## System Architecture Overview

The `MovieActivity` system demonstrates a complete video playback solution with MediaSession integration and Picture-in-Picture support. The architecture centers around three primary components working together to provide a seamless media experience.

```mermaid
graph TB
    subgraph "MovieActivity System Architecture"
        MovieActivity["MovieActivity<br/>Main Activity Controller"]
        MovieView["MovieView<br/>Custom Video Widget"]
        MediaSessionCompat["MediaSessionCompat<br/>System Media Integration"]
        
        subgraph "Callback System"
            MovieListener["MovieView.MovieListener<br/>Video Event Handler"]
            MediaSessionCallback["MediaSessionCallback<br/>Media Control Handler"]
        end
        
        subgraph "Android Framework"
            PiPSystem["PictureInPictureParams<br/>PiP Configuration"]
            MediaController["MediaControllerCompat<br/>Media Session Controller"]
            PlaybackState["PlaybackStateCompat<br/>Playback State Management"]
        end
        
        subgraph "UI Components"
            MovieLayout["movie_activity.xml<br/>Layout Definition"]
            ScrollView["ScrollView<br/>Description Area"]
            ControlButtons["Control Buttons<br/>PiP & Switch"]
        end
    end
    
    MovieActivity --> MovieView
    MovieActivity --> MediaSessionCompat
    MovieActivity --> PiPSystem
    
    MovieView --> MovieListener
    MediaSessionCompat --> MediaSessionCallback
    MediaSessionCompat --> MediaController
    MediaSessionCompat --> PlaybackState
    
    MovieListener --> MovieActivity
    MediaSessionCallback --> MovieView
    
    MovieActivity --> MovieLayout
    MovieLayout --> ScrollView
    MovieLayout --> ControlButtons
```

Sources: [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:1-327](), [PictureInPictureKotlin/app/src/main/res/layout/movie_activity.xml:1-80]()

## Core Components Breakdown

### MovieActivity Class Structure

The `MovieActivity` extends `AppCompatActivity` and serves as the primary coordinator for video playback, media session management, and Picture-in-Picture functionality.

| Component | Type | Purpose | Key Methods |
|-----------|------|---------|-------------|
| `MovieActivity` | Activity | Main controller | `onCreate()`, `minimize()`, `updatePictureInPictureParams()` |
| `movieListener` | MovieView.MovieListener | Video event handling | `onMovieStarted()`, `onMovieStopped()`, `onMovieMinimized()` |
| `MediaSessionCallback` | Inner Class | Media control handling | `onPlay()`, `onPause()`, `onSkipToNext()`, `onSkipToPrevious()` |
| `session` | MediaSessionCompat | System media integration | Media metadata and playback state |

```mermaid
graph TB
    subgraph "MovieActivity Implementation Details"
        subgraph "Constants"
            TAG["TAG = 'MediaSessionPlaybackActivity'"]
            MEDIA_ACTIONS_PLAY_PAUSE["MEDIA_ACTIONS_PLAY_PAUSE<br/>Play/Pause Actions"]
            MEDIA_ACTIONS_ALL["MEDIA_ACTIONS_ALL<br/>All Media Actions"]
            PLAYLIST_SIZE["PLAYLIST_SIZE = 2<br/>Simulated Playlist"]
        end
        
        subgraph "Core Fields"
            binding["binding: MovieActivityBinding<br/>View Binding Instance"]
            session["session: MediaSessionCompat<br/>Media Session"]
            movieListener["movieListener: MovieView.MovieListener<br/>Video Event Callbacks"]
        end
        
        subgraph "Key Methods"
            initializeMediaSession["initializeMediaSession()<br/>Setup Media Session"]
            updatePlaybackState["updatePlaybackState()<br/>Update Session State"]
            minimize["minimize()<br/>Enter PiP Mode"]
            adjustFullScreen["adjustFullScreen()<br/>Handle Orientation"]
        end
        
        subgraph "Lifecycle Handlers"
            onCreate["onCreate()<br/>Initialize UI"]
            onStart["onStart()<br/>Start Media Session"]
            onStop["onStop()<br/>Pause & Release"]
            onPictureInPictureModeChanged["onPictureInPictureModeChanged()<br/>Handle PiP Transitions"]
        end
    end
    
    binding --> movieListener
    session --> initializeMediaSession
    initializeMediaSession --> updatePlaybackState
    minimize --> updatePlaybackState
    onCreate --> onStart
    onStart --> onStop
```

Sources: [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:42-63](), [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:96-114]()

## MediaSession Integration

The `MovieActivity` demonstrates proper MediaSession implementation for system-level media control integration. The MediaSession provides standardized media controls that work across the Android system, including notification panels, lock screens, and Picture-in-Picture overlays.

### MediaSession Setup and Configuration

```mermaid
graph LR
    subgraph "MediaSession Initialization Flow"
        initializeMediaSession["initializeMediaSession()"]
        createSession["session = MediaSessionCompat(this, TAG)"]
        setActive["session.isActive = true"]
        setController["MediaControllerCompat.setMediaController()"]
        
        subgraph "Metadata Setup"
            createMetadata["MediaMetadataCompat.Builder()"]
            setTitle["putString(METADATA_KEY_DISPLAY_TITLE)"]
            buildMetadata["build()"]
        end
        
        subgraph "Callback Setup"
            setCallback["session.setCallback(MediaSessionCallback)"]
            MediaSessionCallback["MediaSessionCallback(binding.movie)"]
        end
        
        subgraph "Initial State"
            checkPlaying["Check binding.movie.isPlaying"]
            setState["updatePlaybackState()"]
        end
    end
    
    initializeMediaSession --> createSession
    createSession --> setActive
    setActive --> setController
    setController --> createMetadata
    createMetadata --> setTitle
    setTitle --> buildMetadata
    buildMetadata --> setCallback
    setCallback --> MediaSessionCallback
    MediaSessionCallback --> checkPlaying
    checkPlaying --> setState
```

Sources: [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:121-144]()

### MediaSessionCallback Implementation

The `MediaSessionCallback` inner class handles media control actions and manages playlist simulation with dynamic action availability.

| Method | Action | Playlist Logic |
|---------|--------|----------------|
| `onPlay()` | `movieView.play()` | No playlist changes |
| `onPause()` | `movieView.pause()` | No playlist changes |
| `onSkipToNext()` | `movieView.startVideo()` | Increment `indexInPlaylist`, disable next at end |
| `onSkipToPrevious()` | `movieView.startVideo()` | Decrement `indexInPlaylist`, disable previous at start |

```mermaid
graph TB
    subgraph "MediaSessionCallback Playlist Management"
        subgraph "State Variables"
            indexInPlaylist["indexInPlaylist: Int = 1<br/>Current Position"]
            PLAYLIST_SIZE_VAL["PLAYLIST_SIZE = 2<br/>Total Items"]
        end
        
        subgraph "Skip Next Logic"
            onSkipToNext["onSkipToNext()"]
            checkNext["indexInPlaylist < PLAYLIST_SIZE?"]
            incrementNext["indexInPlaylist++"]
            updateNextActions["Update Available Actions"]
        end
        
        subgraph "Skip Previous Logic"
            onSkipToPrevious["onSkipToPrevious()"]
            checkPrev["indexInPlaylist > 0?"]
            decrementPrev["indexInPlaylist--"]
            updatePrevActions["Update Available Actions"]
        end
        
        subgraph "Action States"
            AllActions["MEDIA_ACTIONS_ALL<br/>All Controls Available"]
            PlayPauseNext["PLAY_PAUSE + SKIP_TO_NEXT<br/>Can't Skip Previous"]
            PlayPausePrev["PLAY_PAUSE + SKIP_TO_PREVIOUS<br/>Can't Skip Next"]
        end
    end
    
    onSkipToNext --> checkNext
    checkNext -->|Yes| incrementNext
    incrementNext --> updateNextActions
    updateNextActions --> PlayPausePrev
    updateNextActions --> AllActions
    
    onSkipToPrevious --> checkPrev
    checkPrev -->|Yes| decrementPrev
    decrementPrev --> updatePrevActions
    updatePrevActions --> PlayPauseNext
    updatePrevActions --> AllActions
```

Sources: [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:269-326]()

## Picture-in-Picture Implementation

The Picture-in-Picture implementation in `MovieActivity` demonstrates advanced PiP configuration with proper aspect ratio calculation, source rect hints for smooth transitions, and auto-enter functionality.

### PiP Configuration and Parameters

```mermaid
graph TB
    subgraph "Picture-in-Picture Configuration Flow"
        subgraph "Initialization"
            doOnLayout["binding.movie.doOnLayout"]
            updatePictureInPictureParams["updatePictureInPictureParams()"]
        end
        
        subgraph "Parameter Calculation"
            aspectRatio["Rational(movie.width, movie.height)<br/>Calculate Aspect Ratio"]
            visibleRect["Rect().getGlobalVisibleRect()<br/>Source Rectangle"]
            paramsBuilder["PictureInPictureParams.Builder()"]
        end
        
        subgraph "Parameter Setting"
            setAspectRatio["setAspectRatio(aspectRatio)"]
            setSourceRectHint["setSourceRectHint(visibleRect)"]
            setAutoEnterEnabled["setAutoEnterEnabled(true)"]
            build["build()"]
        end
        
        subgraph "Application"
            setPictureInPictureParams["setPictureInPictureParams(params)"]
            minimize["minimize() -> enterPictureInPictureMode()"]
        end
    end
    
    doOnLayout --> updatePictureInPictureParams
    updatePictureInPictureParams --> aspectRatio
    updatePictureInPictureParams --> visibleRect
    aspectRatio --> paramsBuilder
    visibleRect --> paramsBuilder
    paramsBuilder --> setAspectRatio
    setAspectRatio --> setSourceRectHint
    setSourceRectHint --> setAutoEnterEnabled
    setAutoEnterEnabled --> build
    build --> setPictureInPictureParams
    setPictureInPictureParams --> minimize
```

Sources: [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:108-110](), [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:189-206](), [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:211-213]()

### PiP Mode Transitions and Control Visibility

The activity handles PiP mode changes by managing UI element visibility and adapting the interface for the constrained PiP environment.

| PiP State | Video Controls | Scroll Content | Media Session |
|-----------|----------------|----------------|---------------|
| Entering PiP | Hide (`hideControls()`) | Hidden automatically | Active with actions |
| In PiP | Hidden | Hidden | Handles system controls |
| Exiting PiP | Show if paused (`showControls()`) | Visible | Active with actions |

Sources: [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:174-187]()

## Lifecycle Management

The `MovieActivity` implements comprehensive lifecycle management to ensure proper media session handling, video playback state, and resource cleanup.

### Activity Lifecycle Integration

```mermaid
graph TB
    subgraph "MovieActivity Lifecycle Flow"
        subgraph "Startup Phase"
            onCreate["onCreate()<br/>Initialize UI & Listeners"]
            onStart["onStart()<br/>Initialize MediaSession"]
        end
        
        subgraph "Runtime Phase"
            onRestart["onRestart()<br/>Show Controls if Not PiP"]
            onConfigurationChanged["onConfigurationChanged()<br/>Adjust Full Screen"]
            onWindowFocusChanged["onWindowFocusChanged()<br/>Adjust Full Screen"]
            onPictureInPictureModeChanged["onPictureInPictureModeChanged()<br/>Handle PiP Transitions"]
        end
        
        subgraph "Shutdown Phase"
            onStop["onStop()<br/>Pause Video & Release Session"]
        end
        
        subgraph "MovieView Events"
            onMovieStarted["onMovieStarted()<br/>Update to PLAYING State"]
            onMovieStopped["onMovieStopped()<br/>Update to PAUSED State"]
            onMovieMinimized["onMovieMinimized()<br/>Enter PiP Mode"]
        end
    end
    
    onCreate --> onStart
    onStart --> onRestart
    onRestart --> onConfigurationChanged
    onConfigurationChanged --> onStop
    
    onMovieStarted --> onMovieStopped
    onMovieStopped --> onMovieMinimized
    
    onPictureInPictureModeChanged -.-> onMovieStarted
    onWindowFocusChanged -.-> onConfigurationChanged
```

Sources: [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:96-114](), [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:116-119](), [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:146-152]()

## UI Layout Structure

The `movie_activity.xml` layout provides a clean, video-focused interface with the `MovieView` as the primary component and supporting controls in a scrollable area below.

### Layout Component Hierarchy

```mermaid
graph TB
    subgraph "movie_activity.xml Layout Structure"
        LinearLayout["LinearLayout<br/>Root Container<br/>android:orientation='vertical'"]
        
        subgraph "Primary Video Area"
            MovieView["com.example.android.pictureinpicture.widget.MovieView<br/>android:id='@+id/movie'<br/>android:src='@raw/vid_bigbuckbunny'<br/>android:title='@string/title_bigbuckbunny'"]
        end
        
        subgraph "Secondary Content Area"
            ScrollView["ScrollView<br/>android:id='@+id/scroll'<br/>android:layout_weight='1'"]
            
            subgraph "Scroll Content"
                VerticalLinearLayout["LinearLayout<br/>android:id='@+id/vertical'<br/>Vertical Orientation"]
                
                subgraph "Control Elements"
                    PipButton["Button<br/>android:id='@+id/pip'<br/>@string/enter_picture_in_picture"]
                    ExplanationText["TextView<br/>android:id='@+id/explanation'<br/>@string/explanation_movie"]
                    SwitchButton["Button<br/>android:id='@+id/switch_example'<br/>@string/switch_custom"]
                end
            end
        end
    end
    
    LinearLayout --> MovieView
    LinearLayout --> ScrollView
    ScrollView --> VerticalLinearLayout
    VerticalLinearLayout --> PipButton
    VerticalLinearLayout --> ExplanationText
    VerticalLinearLayout --> SwitchButton
```

The layout adapts to orientation changes through the `adjustFullScreen()` method, which hides the scroll content in landscape mode and adjusts the `MovieView` bounds accordingly.

Sources: [PictureInPictureKotlin/app/src/main/res/layout/movie_activity.xml:17-80](), [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MovieActivity.kt:220-233]()

---

