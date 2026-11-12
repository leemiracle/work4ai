<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/IsaacCapture · extra page Web Client Metrics, Recording and Tests · fetched 2026-10-26 -->

# Web Client Metrics, Recording and Tests

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deps/cloudxr/webxr_client/.dockerignore](deps/cloudxr/webxr_client/.dockerignore)
- [deps/cloudxr/webxr_client/eslint.config.js](deps/cloudxr/webxr_client/eslint.config.js)
- [deps/cloudxr/webxr_client/helpers/LoadIWER.test.ts](deps/cloudxr/webxr_client/helpers/LoadIWER.test.ts)
- [deps/cloudxr/webxr_client/helpers/LoadIWER.ts](deps/cloudxr/webxr_client/helpers/LoadIWER.ts)
- [deps/cloudxr/webxr_client/helpers/Metrics.ts](deps/cloudxr/webxr_client/helpers/Metrics.ts)
- [deps/cloudxr/webxr_client/helpers/PerformanceProfiles.ts](deps/cloudxr/webxr_client/helpers/PerformanceProfiles.ts)
- [deps/cloudxr/webxr_client/helpers/WebGLState.ts](deps/cloudxr/webxr_client/helpers/WebGLState.ts)
- [deps/cloudxr/webxr_client/helpers/WebGlUtils.ts](deps/cloudxr/webxr_client/helpers/WebGlUtils.ts)
- [deps/cloudxr/webxr_client/helpers/controlChannel.test.ts](deps/cloudxr/webxr_client/helpers/controlChannel.test.ts)
- [deps/cloudxr/webxr_client/helpers/metricsAccumulator.test.ts](deps/cloudxr/webxr_client/helpers/metricsAccumulator.test.ts)
- [deps/cloudxr/webxr_client/helpers/metricsAccumulator.ts](deps/cloudxr/webxr_client/helpers/metricsAccumulator.ts)
- [deps/cloudxr/webxr_client/helpers/metricsUpdates.ts](deps/cloudxr/webxr_client/helpers/metricsUpdates.ts)
- [deps/cloudxr/webxr_client/helpers/overridePressureObserver.ts](deps/cloudxr/webxr_client/helpers/overridePressureObserver.ts)
- [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.test.tsx](deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.test.tsx)
- [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx](deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx)
- [deps/cloudxr/webxr_client/jest.setup.js](deps/cloudxr/webxr_client/jest.setup.js)
- [deps/cloudxr/webxr_client/playwright.config.js](deps/cloudxr/webxr_client/playwright.config.js)
- [deps/cloudxr/webxr_client/src/RecorderComponent.tsx](deps/cloudxr/webxr_client/src/RecorderComponent.tsx)
- [deps/cloudxr/webxr_client/src/RecorderContext.tsx](deps/cloudxr/webxr_client/src/RecorderContext.tsx)
- [deps/cloudxr/webxr_client/src/TraceVisualization.tsx](deps/cloudxr/webxr_client/src/TraceVisualization.tsx)
- [deps/cloudxr/webxr_client/src/xrInputRecorder.test.ts](deps/cloudxr/webxr_client/src/xrInputRecorder.test.ts)
- [deps/cloudxr/webxr_client/src/xrInputRecorder.ts](deps/cloudxr/webxr_client/src/xrInputRecorder.ts)
- [deps/cloudxr/webxr_client/tests/mock/CloudXRComponentTest.html](deps/cloudxr/webxr_client/tests/mock/CloudXRComponentTest.html)
- [deps/cloudxr/webxr_client/tests/mock/CloudXRComponentTest.tsx](deps/cloudxr/webxr_client/tests/mock/CloudXRComponentTest.tsx)
- [deps/cloudxr/webxr_client/tests/mock/MockCloudXR.ts](deps/cloudxr/webxr_client/tests/mock/MockCloudXR.ts)
- [deps/cloudxr/webxr_client/tests/mock/MockCloudXRTests.html](deps/cloudxr/webxr_client/tests/mock/MockCloudXRTests.html)
- [deps/cloudxr/webxr_client/tests/mock/MockCloudXRTests.ts](deps/cloudxr/webxr_client/tests/mock/MockCloudXRTests.ts)
- [deps/cloudxr/webxr_client/tests/mock/cloudxr-mock-alias.ts](deps/cloudxr/webxr_client/tests/mock/cloudxr-mock-alias.ts)
- [deps/cloudxr/webxr_client/tests/mock/webglMockScene.ts](deps/cloudxr/webxr_client/tests/mock/webglMockScene.ts)
- [deps/cloudxr/webxr_client/tests/playwright/AppMockTest.spec.js](deps/cloudxr/webxr_client/tests/playwright/AppMockTest.spec.js)
- [deps/cloudxr/webxr_client/tests/playwright/CloudXRComponentTest.spec.js](deps/cloudxr/webxr_client/tests/playwright/CloudXRComponentTest.spec.js)
- [deps/cloudxr/webxr_client/webpack.component-mock.js](deps/cloudxr/webxr_client/webpack.component-mock.js)
- [tests/python/core/cloudxr/oob_hub_test_server.py](tests/python/core/cloudxr/oob_hub_test_server.py)

</details>



This page details the performance metrics monitoring, HUD rendering pipeline, input recording/trace visualization subsystem, Jest unit testing architecture, Playwright browser test suites, and the IWER (Immersive WebXR Emulator) integration utilized by the `isaaccapture` web client (`webxr_client`).

---

## 1. Performance Metrics Accumulation and HUD

To prevent expensive DOM mutations and layout trashing from React re-renders at 72–90 FPS, the web client renders performance metrics (Render FPS, Streaming FPS, Pose-to-Render latency, and Session Quality scores) onto an offscreen 2D canvas texture via `PerformanceCanvasImage`.

The component maintains an offscreen HTML canvas (`1024x760`) [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx:42-43]() and draws metric bars and text using a cached 2D context inside a `useFrame` loop [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx:135-166](). The resulting canvas is wrapped in a Three.js `CanvasTexture` [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx:147-149]() with `matrixAutoUpdate = false` and bound directly to a `@react-three/uikit` `Image` component (`imageRef.current.texture.value`) [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx:30-33](). This avoids stringifying textures and triggers efficient GPU uploads (`texture.needsUpdate = true`) without triggering React reconciliation passes [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx:25-28]().

Session quality scores (0–4) map to distinct RGBA color profiles defined in `SESSION_QUALITY_COLORS` [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx:59-66](), visualizing network health through graded height bars (`SESSION_QUALITY_BAR_HEIGHTS`) [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx:72]().

### Performance Rendering Data Flow

```mermaid
title "Performance Metrics HUD Data Flow"
graph TD
  A["CloudXR.MetricsName"] -->|Signals| B["PerformanceCanvasImage.tsx"]
  B -->|Draws via 2D Context| C["HTMLCanvasElement CANVAS_WIDTH=1024"]
  C -->|CanvasTexture update| D["Three.js CanvasTexture"]
  D -->|Assigned via ref| E["UIKit Image Component"]
  E -->|GPU Upload per-frame| F["In-Headset HUD Display"]

  style A fill:#fff,stroke:#000,stroke-width:2px
  style B fill:#fff,stroke:#000,stroke-width:2px
  style C fill:#fff,stroke:#000,stroke-width:2px
  style D fill:#fff,stroke:#000,stroke-width:2px
  style E fill:#fff,stroke:#000,stroke-width:2px
  style F fill:#fff,stroke:#000,stroke-width:2px
```

Sources:
- `deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx` [deps/cloudxr/webxr_client/helpers/react/PerformanceCanvasImage.tsx:1-167]()

---

## 2. Input Recorder and Trace Visualization

The `XRInputRecorder` subsystem captures headset poses, controller inputs, and hand joint skeletons during live XR sessions for offline debugging, regression testing, and trace replay.

### Recorder Architecture

Managed centrally by `RecorderProvider` in `RecorderContext.tsx` [deps/cloudxr/webxr_client/src/RecorderContext.tsx:18-24](), the recorder operates in three mutually exclusive modes: `idle`, `recording`, and `replaying`. 
- **Recording Mode**: Each frame intercepted via `XRInputRecorder.beginFrame()` serializes tracking states into an in-memory `Recording` structure containing timestamped `RecordedFrame` entries [deps/cloudxr/webxr_client/src/xrInputRecorder.test.ts:110-118]().
- **Replay Mode**: Supports time-paced interpolation or strict frame-stepped pacing (`ReplayPacing`) [deps/cloudxr/webxr_client/src/xrInputRecorder.test.ts:162-176](), feeding recorded pose streams back into the client pipeline to simulate physical tracking sequences without requiring an active headset or operator.
- **Import/Export**: Recordings can be serialized to JSON blobs (`onSaveRecording`) or loaded via hidden file inputs (`onLoadRecording` / `XRInputRecorder.importJSON()`) [deps/cloudxr/webxr_client/src/RecorderContext.tsx:100-138]().

Sources:
- `deps/cloudxr/webxr_client/src/RecorderContext.tsx` [deps/cloudxr/webxr_client/src/RecorderContext.tsx:1-182]()
- `deps/cloudxr/webxr_client/src/xrInputRecorder.test.ts` [deps/cloudxr/webxr_client/src/xrInputRecorder.test.ts:1-197]()

---

## 3. Testing Infrastructure: Jest Mocks and Playwright Tests

The web client employs a dual testing strategy utilizing Jest for unit/component logic and Playwright for end-to-end browser execution against mock CloudXR servers.

### Jest Environment and Mocks
- **`jest.setup.js`**: Patches global environments to supply Web Timing API stubs (`performance.mark`, `performance.measure`) required during CloudXR SDK initialization under JSDOM [deps/cloudxr/webxr_client/jest.setup.js:18-33](). It also polyfills `WebSocket` using the `ws` library on older Node versions to support control channel tests [deps/cloudxr/webxr_client/jest.setup.js:35-44]().
- **Mock CloudXR Layer**: `MockCloudXR.ts` implements the `CloudXR.Session` interface [deps/cloudxr/webxr_client/tests/mock/MockCloudXR.ts:109-110]() to simulate session connection lifecycles, network quality profiles [deps/cloudxr/webxr_client/tests/mock/MockCloudXR.ts:66-73](), and WebGL rendering (`WebGLMockScene`) [deps/cloudxr/webxr_client/tests/mock/MockCloudXR.ts:25-33]() without an active server.
- **Webpack Aliasing**: `webpack.component-mock.js` redirects `@nvidia/cloudxr` imports to `cloudxr-mock-alias.ts`, allowing production components like `CloudXRComponent.tsx` to run against mock sessions [deps/cloudxr/webxr_client/webpack.component-mock.js:45-53](), [deps/cloudxr/webxr_client/tests/mock/cloudxr-mock-alias.ts:18-38]().

### Playwright E2E Suites
- **`playwright.config.js`**: Configures Chromium execution inside headless environments using SwiftShader software WebGL (`--use-angle=swiftshader`) and disables native WebXR (`--disable-features=WebXR`) so that IWER provides `navigator.xr` [deps/cloudxr/webxr_client/playwright.config.js:10-23](). It automatically spins up development servers for mock test harnesses [deps/cloudxr/webxr_client/playwright.config.js:38-57]().
- **`CloudXRComponentTest.spec.js`**: Drives a scripted 6-step sequence testing retry logic, recoverable/unrecoverable error classification, and stream test handlers by asserting on console output logs prefixed with `[CloudXRComponentTest]` [deps/cloudxr/webxr_client/tests/playwright/CloudXRComponentTest.spec.js:9-34]().

### Testing Architecture

```mermaid
title "Web Client Testing and Mock Architecture"
graph TD
  A["Playwright Test runner\nplaywright.config.js"] -->|Drives browser| B["Test Harness Page\nCloudXRComponentTest.tsx"]
  B -->|Renders component| C["CloudXRComponent.tsx"]
  C -->|Aliased via WebGL alias| D["MockCloudXR.ts"]
  D -->|Emulates WebXR via| E["IWER XRDevice Runtime\nLoadIWER.ts"]
  
  F["Jest Unit Runner\njest.setup.js"] -->|Executes suite| G["xrInputRecorder.test.ts"]
  F -->|Executes suite| H["metricsAccumulator.test.ts"]

  style A fill:#fff,stroke:#000,stroke-width:2px
  style B fill:#fff,stroke:#000,stroke-width:2px
  style C fill:#fff,stroke:#000,stroke-width:2px
  style D fill:#fff,stroke:#000,stroke-width:2px
  style E fill:#fff,stroke:#000,stroke-width:2px
  style F fill:#fff,stroke:#000,stroke-width:2px
  style G fill:#fff,stroke:#000,stroke-width:2px
  style H fill:#fff,stroke:#000,stroke-width:2px
```

Sources:
- `deps/cloudxr/webxr_client/jest.setup.js` [deps/cloudxr/webxr_client/jest.setup.js:1-44]()
- `deps/cloudxr/webxr_client/tests/mock/MockCloudXR.ts` [deps/cloudxr/webxr_client/tests/mock/MockCloudXR.ts:1-139]()
- `deps/cloudxr/webxr_client/tests/mock/cloudxr-mock-alias.ts` [deps/cloudxr/webxr_client/tests/mock/cloudxr-mock-alias.ts:1-70]()
- `deps/cloudxr/webxr_client/webpack.component-mock.js` [deps/cloudxr/webxr_client/webpack.component-mock.js:1-76]()
- `deps/cloudxr/webxr_client/playwright.config.js` [deps/cloudxr/webxr_client/playwright.config.js:1-78]()
- `deps/cloudxr/webxr_client/tests/playwright/CloudXRComponentTest.spec.js` [deps/cloudxr/webxr_client/tests/playwright/CloudXRComponentTest.spec.js:1-137]()

---

## 4. IWER WebXR Emulator Integration

When running in environments lacking physical XR hardware (such as CI containers or developer workstations without connected headsets), the web client dynamically loads the **IWER (Immersive WebXR Emulator)** runtime via `LoadIWER.ts`.

### Implementation Details
1. **Support Detection**: Checks whether `navigator.xr` supports `immersive-vr` or `immersive-ar` sessions [deps/cloudxr/webxr_client/helpers/LoadIWER.ts:53-59]().
2. **CDN Fallback Loading**: If immersive support is absent, the helper injects the `iwer` library (`iwer.min.js`) and `@iwer/devui` (`iwer-devui.min.js`) scripts from unpkg [deps/cloudxr/webxr_client/helpers/LoadIWER.ts:61-100]().
3. **Runtime Installation**: Instantiates an `XRDevice` profile (defaulting to `metaQuest3`), installs the optional DevUI overlay if available, and forces runtime installation via `device.installRuntime({ forceInstall: true })` [deps/cloudxr/webxr_client/helpers/LoadIWER.ts:102-115]().
4. **Global Injection**: Exposes the emulator instance on `window.xrDevice`, satisfying standard `navigator.xr` calls for subsequent Three.js/React-XR components [deps/cloudxr/webxr_client/helpers/LoadIWER.ts:116]().

Sources:
- `deps/cloudxr/webxr_client/helpers/LoadIWER.ts` [deps/cloudxr/webxr_client/helpers/LoadIWER.ts:1-140]()

---

