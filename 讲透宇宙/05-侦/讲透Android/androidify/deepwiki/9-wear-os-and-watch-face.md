<!-- source: DeepWiki mcp.deepwiki.com · repo android/androidify · page 9 Wear OS and Watch Face · fetched 2026-10-23 -->

# Wear OS and Watch Face

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmark/build.gradle.kts](benchmark/build.gradle.kts)
- [build-plugin/src/main/kotlin/com/android/developers/androidify/plugin/AndroidApplicationPlugin.kt](build-plugin/src/main/kotlin/com/android/developers/androidify/plugin/AndroidApplicationPlugin.kt)
- [build-plugin/src/main/kotlin/com/android/developers/androidify/plugin/AndroidLibraryPlugin.kt](build-plugin/src/main/kotlin/com/android/developers/androidify/plugin/AndroidLibraryPlugin.kt)
- [watchface/build.gradle.kts](watchface/build.gradle.kts)
- [watchface/src/main/java/com/android/developers/androidify/watchface/creator/Signer.kt](watchface/src/main/java/com/android/developers/androidify/watchface/creator/Signer.kt)
- [watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearAssetTransmitter.kt](watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearAssetTransmitter.kt)
- [watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearDeviceRepository.kt](watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearDeviceRepository.kt)
- [watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearableApiAvailability.kt](watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearableApiAvailability.kt)
- [wear/build.gradle.kts](wear/build.gradle.kts)
- [wear/watchface/build.gradle.kts](wear/watchface/build.gradle.kts)

</details>



The Androidify ecosystem includes a dedicated Wear OS companion application and a sophisticated watch face generation system. This allows users to not only create AI-generated bots on their mobile devices but also deploy them as functional watch faces to connected Wear OS hardware. The system leverages the **Wearable Data Layer API** for communication and the **Watch Face Format (WFF)** for rendering.

### System Overview

The Wear OS integration is split into two primary functional areas:
1.  **Companion App**: A Wear OS application that listens for data from the phone, manages the onboarding state, and handles the local installation of generated watch faces.
2.  **Watch Face Module**: A library used by the mobile app to package bot images into a Watch Face Format (WFF) APK, sign it locally, and transmit it to the watch.

### High-Level Component Interaction

The following diagram illustrates the communication flow between the mobile app and the Wear OS device during the watch face creation and transfer process.

**Watch Face Transfer Flow**
```mermaid
graph TD
    subgraph "Mobile Device (:watchface)"
        [WatchFaceCreator] -- "Generates & Signs" --> WF_APK["Watch Face APK"]
        [WearAssetTransmitterImpl] -- "1. InitialRequest" --> [MessageClient]
        [WearAssetTransmitterImpl] -- "2. sendFile" --> [ChannelClient]
        [WearDeviceRepositoryImpl] -- "Discovers" --> [NodeClient]
    end

    subgraph "Wear OS Device (:wear)"
        [AndroidifyDataListenerService] -- "Listens" --> [WearableListenerService]
        [WatchFacePushStateManager] -- "Manages Install" --> [DataStore]
        [DefaultWatchFace] -- "Token Validation" --> [DwfValidation]
    end

    [MessageClient] -. "Protobuf via Data Layer" .-> [AndroidifyDataListenerService]
    [ChannelClient] -. "Byte Stream" .-> [AndroidifyDataListenerService]
```

**Sources:**
*   [watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearAssetTransmitter.kt:72-82]()
*   [watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearDeviceRepository.kt:41-45]()
*   [wear/build.gradle.kts:124-135]()

---

### Wear OS Companion App
The `wear` module contains the Wear OS application. It is built using **Wear Compose** and serves as the receiver for assets generated on the phone. A critical component is the `AndroidifyDataListenerService`, which extends `WearableListenerService` to process incoming `InitialRequest` and file transfers via the Wearable Data Layer.

Key responsibilities:
*   **Onboarding**: Managing the initial user experience on the watch.
*   **State Management**: Using `WatchFacePushStateManager` to track the progress of incoming watch face updates.
*   **Validation**: Utilizing generated tokens (`wf_token.xml`) to ensure the authenticity of pushed watch faces.

For details, see [Wear OS Companion App](#9.1).

**Sources:**
*   [wear/build.gradle.kts:64-83]()
*   [wear/build.gradle.kts:148-157]()

---

### Watch Face Generation and Transfer
The `watchface` module provides the machinery to convert a generated bot image into a wearable asset. This involves a multi-step process:

1.  **Packaging**: The system uses a native packaging library to wrap the bot image and WFF XML into a specialized APK.
2.  **Signing**: The `Signer.kt` utility generates or retrieves an RSA key pair from the `AndroidKeyStore` to sign the generated APK locally on the mobile device.
3.  **Discovery**: `WearDeviceRepository` uses `CapabilityClient` to find reachable Wear OS nodes that have the Androidify companion app installed.
4.  **Transmission**: `WearAssetTransmitter` coordinates a three-step handshake (Setup, Transfer, Confirmation) using `MessageClient` and `ChannelClient`.

For details, see [Watch Face Generation and Transfer](#9.2).

**Watch Face Code Entity Mapping**
```mermaid
graph LR
    subgraph "Logic Space"
        "Device Discovery"
        "APK Signing"
        "Asset Transfer"
    end

    subgraph "Code Space"
        [WearDeviceRepositoryImpl] -- "implements" --> "Device Discovery"
        [signApk] -- "uses" --> "ApkSigner"
        [WearAssetTransmitterImpl] -- "manages" --> "Asset Transfer"
    end

    [WearDeviceRepositoryImpl] -.-> [NodeClient]
    [signApk] -.-> [KeyStore]
    [WearAssetTransmitterImpl] -.-> [ChannelClient]
```

**Sources:**
*   [watchface/src/main/java/com/android/developers/androidify/watchface/creator/Signer.kt:58-62]()
*   [watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearDeviceRepository.kt:54-65]()
*   [watchface/src/main/java/com/android/developers/androidify/watchface/transfer/WearAssetTransmitter.kt:112-144]()

---

### Build Configuration
The Wear OS components have specific build requirements to ensure compatibility and security:
*   **Min SDK**: Set to 36 for Wear OS components [wear/build.gradle.kts:31]().
*   **Version Offsetting**: The Wear app uses a version code offset to maintain a distinct version space from the mobile app while staying in sync [wear/build.gradle.kts:33-35]().
*   **Validation Tooling**: The build process includes a `ProcessFilesTask` that runs a `DwfValidation` CLI tool to verify the Watch Face Format and generate a validation token [wear/build.gradle.kts:101-164]().

**Sources:**
*   [wear/build.gradle.kts:31-35]()
*   [wear/watchface/build.gradle.kts:26-30]()
*   [wear/build.gradle.kts:124-135]()

---

