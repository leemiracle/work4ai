<!-- source: DeepWiki mcp.deepwiki.com · repo android/androidify · page 10 Glossary · fetched 2026-10-23 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/main/AndroidManifest.xml](app/src/main/AndroidManifest.xml)
- [app/src/main/java/com/android/developers/androidify/navigation/NavigationRoutes.kt](app/src/main/java/com/android/developers/androidify/navigation/NavigationRoutes.kt)
- [core/network/src/main/java/com/android/developers/androidify/ondevice/LocalSegmentationDataSource.kt](core/network/src/main/java/com/android/developers/androidify/ondevice/LocalSegmentationDataSource.kt)
- [core/network/src/main/java/com/android/developers/androidify/startup/FirebaseAppCheckInitializer.kt](core/network/src/main/java/com/android/developers/androidify/startup/FirebaseAppCheckInitializer.kt)
- [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt](core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt)
- [core/util/src/main/java/com/android/developers/androidify/util/LocalFileProvider.kt](core/util/src/main/java/com/android/developers/androidify/util/LocalFileProvider.kt)
- [core/xr/src/main/java/com/android/developers/androidify/xr/SpatialUiModes.kt](core/xr/src/main/java/com/android/developers/androidify/xr/SpatialUiModes.kt)
- [core/xr/src/main/java/com/android/developers/androidify/xr/XrPreview.kt](core/xr/src/main/java/com/android/developers/androidify/xr/XrPreview.kt)
- [data/src/main/java/com/android/developers/androidify/data/ImageGenerationRepository.kt](data/src/main/java/com/android/developers/androidify/data/ImageGenerationRepository.kt)
- [feature/creation/src/main/java/com/android/developers/androidify/creation/CreationScreen.kt](feature/creation/src/main/java/com/android/developers/androidify/creation/CreationScreen.kt)
- [feature/creation/src/main/java/com/android/developers/androidify/creation/CreationViewModel.kt](feature/creation/src/main/java/com/android/developers/androidify/creation/CreationViewModel.kt)
- [feature/creation/src/main/java/com/android/developers/androidify/creation/EditScreenLayoutType.kt](feature/creation/src/main/java/com/android/developers/androidify/creation/EditScreenLayoutType.kt)
- [feature/creation/src/main/java/com/android/developers/androidify/creation/xr/EditScreenHomeSpaceModePreviews.kt](feature/creation/src/main/java/com/android/developers/androidify/creation/xr/EditScreenHomeSpaceModePreviews.kt)
- [feature/creation/src/main/java/com/android/developers/androidify/creation/xr/EditScreenSpatial.kt](feature/creation/src/main/java/com/android/developers/androidify/creation/xr/EditScreenSpatial.kt)
- [feature/home/src/main/java/com/android/developers/androidify/home/xr/HomeScreenHomeSpaceModePreviews.kt](feature/home/src/main/java/com/android/developers/androidify/home/xr/HomeScreenHomeSpaceModePreviews.kt)
- [feature/results/src/androidTest/java/com/android/developers/androidify/results/ResultsScreenTest.kt](feature/results/src/androidTest/java/com/android/developers/androidify/results/ResultsScreenTest.kt)
- [feature/results/src/main/java/com/android/developers/androidify/customize/AspectRatioTool.kt](feature/results/src/main/java/com/android/developers/androidify/customize/AspectRatioTool.kt)
- [feature/results/src/main/java/com/android/developers/androidify/customize/BackgroundTool.kt](feature/results/src/main/java/com/android/developers/androidify/customize/BackgroundTool.kt)
- [feature/results/src/main/java/com/android/developers/androidify/customize/ComposableBitmapRendererImpl.kt](feature/results/src/main/java/com/android/developers/androidify/customize/ComposableBitmapRendererImpl.kt)
- [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportScreen.kt](feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportScreen.kt)
- [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportViewModel.kt](feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportViewModel.kt)
- [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeState.kt](feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeState.kt)
- [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeTool.kt](feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeTool.kt)
- [feature/results/src/main/java/com/android/developers/androidify/customize/GenericTool.kt](feature/results/src/main/java/com/android/developers/androidify/customize/GenericTool.kt)
- [feature/results/src/main/java/com/android/developers/androidify/results/BotResultCard.kt](feature/results/src/main/java/com/android/developers/androidify/results/BotResultCard.kt)
- [feature/results/src/main/java/com/android/developers/androidify/results/ResultsLayoutType.kt](feature/results/src/main/java/com/android/developers/androidify/results/ResultsLayoutType.kt)
- [feature/results/src/main/java/com/android/developers/androidify/results/ResultsViewModel.kt](feature/results/src/main/java/com/android/developers/androidify/results/ResultsViewModel.kt)
- [feature/results/src/test/kotlin/com/android/developers/androidify/customize/CustomizeStateTest.kt](feature/results/src/test/kotlin/com/android/developers/androidify/customize/CustomizeStateTest.kt)
- [gradle/libs.versions.toml](gradle/libs.versions.toml)
- [wear/src/main/java/com/android/developers/androidify/ui/CallToActionButton.kt](wear/src/main/java/com/android/developers/androidify/ui/CallToActionButton.kt)
- [wear/src/main/java/com/android/developers/androidify/ui/CallToActionScreen.kt](wear/src/main/java/com/android/developers/androidify/ui/CallToActionScreen.kt)
- [wear/src/main/java/com/android/developers/androidify/ui/TransmissionScreen.kt](wear/src/main/java/com/android/developers/androidify/ui/TransmissionScreen.kt)

</details>



This glossary defines codebase-specific terms, jargon, and domain concepts used within the Androidify project. It serves as a technical reference for onboarding engineers to understand how high-level product features map to specific implementation details and code entities.

## AI and Generative Terms

### Gemini / Vertex AI
The primary suite of generative models used for text and image processing. The application integrates these via the Firebase Vertex AI SDK [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:24-36]().

*   **Gemini 2.5 Flash**: Used for text validation and descriptive prompt generation [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:63-65]().
*   **Gemini 2.0 Flash Image Generation**: Used for generating the initial Android bot images based on prompts [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:81-83]().
*   **Imagen 4.0 Ultra**: Employed for advanced image editing, such as adding backgrounds to existing bot images [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:159-161]().
*   **Gemini Nano**: An on-device model used for local validation and description generation when enabled via Remote Config [data/src/main/java/com/android/developers/androidify/data/ImageGenerationRepository.kt:60-64]().

### Prompt Validation
The process of ensuring a user's input (text or image) contains sufficient information for the AI to generate a high-quality Android bot.
*   **Text Validation**: Handled by `validatePromptHasEnoughInformation` [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:98-109]().
*   **Image Validation**: Handled by `validateImageHasEnoughInformation`, which checks if a person is clearly visible [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:111-130]().

### Fine-tuned Model
A specialized version of the generative model specifically trained to produce the "Androidify" style. It is accessed via a specific model name defined in Remote Config [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:149-152]().

**AI Data Flow Diagram**
```mermaid
graph TD
    "User Input" --> "ImageGenerationRepository"
    "ImageGenerationRepository" -- "Validation" --> "FirebaseAiDataSource"
    "FirebaseAiDataSource" -- "Schema Validation" --> "GenerativeModel (Vertex AI)"
    "GenerativeModel" -- "JSON/Bitmap" --> "FirebaseAiDataSource"
    "FirebaseAiDataSource" -- "ValidatedDescription/Bitmap" --> "ImageGenerationRepository"
    "ImageGenerationRepository" --> "CreationViewModel"
```
**Sources:** [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:45-58](), [data/src/main/java/com/android/developers/androidify/data/ImageGenerationRepository.kt:46-53]()

---

## UI and Customization Concepts

### ExportImageCanvas
A data class representing the state of the final image being prepared for sharing or export. It tracks the `aspectRatioOption`, `selectedBackgroundOption`, and the transformation of the bot image (offset, rotation, size) [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeState.kt:74-91]().

### ToolState
A generic interface for customization tools (Size, Background). Each tool provides a list of `ToolOption` and tracks the currently selected one [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeState.kt:47-50]().
*   **AspectRatioToolState**: Manages `SizeOption` (Square, Banner, Sticker, etc.) [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeState.kt:52-62]().
*   **BackgroundToolState**: Manages `BackgroundOption` (Lightspeed, IO, Plain, etc.) [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeState.kt:64-72]().

### ComposableBitmapRenderer
A utility used to convert a Jetpack Compose UI tree (specifically the `ImageResult` composable) into a static `Bitmap` for saving or sharing [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportViewModel.kt:140-146]().

### Subject Segmentation
An ML Kit feature used to remove the background from a generated bot, allowing it to be treated as a "Sticker" [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportViewModel.kt:163-178](). This is implemented in `LocalSegmentationDataSource` [core/network/src/main/java/com/android/developers/androidify/ondevice/LocalSegmentationDataSource.kt:1]() and coordinated by the repository [data/src/main/java/com/android/developers/androidify/data/ImageGenerationRepository.kt:164-166]().

**UI Entity Mapping**
```mermaid
graph LR
    subgraph "Natural Language"
        "Canvas"
        "Aspect Ratio"
        "Sticker Mode"
    end

    subgraph "Code Entity Space"
        "Canvas" --> "ExportImageCanvas [CustomizeState.kt]"
        "Aspect Ratio" --> "SizeOption [CustomizeState.kt]"
        "Sticker Mode" --> "SizeOption.Sticker [CustomizeState.kt]"
        "Sticker Mode" --> "LocalSegmentationDataSource [core/network]"
    end
```
**Sources:** [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeState.kt:74-104](), [data/src/main/java/com/android/developers/androidify/data/ImageGenerationRepository.kt:41-43]()

---

## Extended Reality (XR) Terms

### Spatial UI
The UI mode for XR devices. The app supports different layouts based on whether the device is in a standard "Home Space" or a "Full Space" immersive mode [core/xr/src/main/java/com/android/developers/androidify/xr/SpatialUiModes.kt:1]().

### LayoutType
An enum or state used to toggle between `Compact`, `Medium`, and `Spatial` layouts. For example, `CreationScreen` uses `calculateLayoutType` to determine how to arrange the editing UI [feature/creation/src/main/java/com/android/developers/androidify/creation/CreationScreen.kt:48]().

---

## Wear OS and Watch Face Terms

### Watch Face Format (WFF)
The XML-based format used for modern Android watch faces. The app generates these dynamically using the generated bot image.

### WatchFaceInstallationRepository
The bridge between the phone and the watch. It manages the connection state (`connectedWatch`) and tracks the progress of transferring assets to the Wear OS device [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportViewModel.kt:72-82]().

### TransmissionScreen
The Wear OS UI shown to the user while the phone is pushing a new watch face asset. It features a `FourColorProgressIndicator` to indicate active data transfer [wear/src/main/java/com/android/developers/androidify/ui/TransmissionScreen.kt:58-96]().

---

## Core Infrastructure

### RemoteConfigDataSource
A wrapper around Firebase Remote Config that provides feature flags and AI model configurations, such as `use_gemini_nano` or `background_vibes_enabled` [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportViewModel.kt:96-117]().

### LocalFileProvider
A utility for handling internal and external storage operations, including creating cache files for sharing and saving images to the public gallery [core/util/src/main/java/com/android/developers/androidify/util/LocalFileProvider.kt:1]().

**Sources:**
*   **AI Integration:** [core/network/src/main/java/com/android/developers/androidify/vertexai/FirebaseAiDataSource.kt:45-160](), [data/src/main/java/com/android/developers/androidify/data/ImageGenerationRepository.kt:55-129]()
*   **UI/Customization:** [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeState.kt:28-104](), [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportViewModel.kt:52-155]()
*   **Wear OS:** [wear/src/main/java/com/android/developers/androidify/ui/TransmissionScreen.kt:58-96](), [feature/results/src/main/java/com/android/developers/androidify/customize/CustomizeExportViewModel.kt:72-86]()