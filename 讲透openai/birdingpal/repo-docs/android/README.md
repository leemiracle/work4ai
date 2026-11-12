← [Birding Buddy](../README.md)

# Birding Buddy — Android App

An Android voice companion that helps you identify birds in the field, analyze bird calls, and maintain a personal bird book — all powered by [OpenAI Realtime](https://platform.openai.com/docs/guides/realtime).

## Features

- **Voice identification** — describe what you see and the assistant identifies likely species
- **Bird-call analysis** — record a bird call; the app sends it to a [BirdNET](https://birdnet.cornell.edu/)-compatible analyzer and the assistant explains the results
- **Bird book** — add identified birds to a personal log with auto-fetched facts (family, habitat, diet, notes); stored on-device
- **BLE trigger** — optionally pair a Bluetooth Low Energy button to start/stop sessions hands-free

## Requirements

- JDK 17
- Android command-line SDK tools (`sdkmanager`, `adb`)
- Android API 34 platform + build tools
- An [OpenAI API key](https://platform.openai.com/api-keys)
- *(Optional)* A BirdNET-compatible bird-call analysis endpoint for the audio analysis feature

## Setup

### 1. Verify Java

```bash
java -version
```

Must be Java 17. On macOS:

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"
```

### 2. Install Android SDK packages

```bash
sdkmanager --install \
  "platform-tools" \
  "platforms;android-34" \
  "build-tools;34.0.0"

yes | sdkmanager --licenses
```

### 3. Configure API keys

Create (or edit) `local.properties` in the project root:

```
OPENAI_API_KEY=replace-with-your-api-key
BIRDNET_ANALYZER_URL=https://your-birdnet-server.example.com
```

`BIRDNET_ANALYZER_URL` is only required if you want bird-call audio analysis. Without it, voice identification and the bird book still work.

### 4. Build

```bash
./gradlew assembleDebug
```

APK output: `app/build/outputs/apk/debug/app-debug.apk`

### 5. Install on device

Enable USB debugging on your Android phone, then:

```bash
adb devices
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Launch:

```bash
adb shell am start -n com.openaiexperiments.birdingbuddy/.MainActivity
```

## First Run

1. **Grant permissions** — allow Microphone and Location when prompted. Location is used to improve bird-call analysis accuracy; if denied, the analyzer falls back to default coordinates.
2. **Hold to talk** — press and hold the mic button to speak with the assistant. Release to send.
3. **Analyze a bird call** — press the bird-call button to start recording ambient sound, press again to stop and analyze. The assistant will describe what it hears.
4. **Bird book** — when the assistant identifies a bird, ask it to "add that to my bird book." Facts are fetched from OpenAI and saved on-device.

## Architecture

| Layer | Technology |
|---|---|
| UI | Kotlin + Jetpack Compose |
| Voice session | OpenAI Realtime API (WebSocket) |
| Bird-call analysis | BirdNET-compatible HTTP endpoint (`POST /birds/analyze-call`) |
| Bird info lookup | OpenAI Chat Completions (`gpt-4o-mini`) |
| Bird book storage | On-device JSON file (`context.filesDir/bird_book.json`) |
| BLE trigger | Android BLE via `BirdBuddyBleManager` |
| Background session | Android foreground service (`BirdBuddySessionService`) |

### BirdNET analyzer API contract

The app sends a `multipart/form-data` `POST` to `{BIRDNET_ANALYZER_URL}/birds/analyze-call` with:

| Field | Type | Description |
|---|---|---|
| `data` | WAV binary | Recorded audio |
| `lat` | float | Latitude (for regional species filtering) |
| `lon` | float | Longitude |
| `week` | int | Week of year (1–48, for seasonal filtering) |

Expected response: a JSON object or array with species candidates and confidence scores. The assistant receives this payload directly and describes the results to the user.

## Security Note

`OPENAI_API_KEY` is embedded in the debug APK via `BuildConfig`. **Do not distribute APKs built this way publicly.** For production use, replace the key with [ephemeral session tokens](https://platform.openai.com/docs/guides/realtime#authentication) generated server-side.

## Contributing

Issues and pull requests are welcome. Please open an issue first to discuss larger changes before submitting a PR.
