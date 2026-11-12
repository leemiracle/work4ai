<!-- source: DeepWiki mcp.deepwiki.com · repo Leonxlnx/taste-skill · extra page cdp.mjs: Zero-Dependency Browser Driver · fetched 2026-10-26 -->

# cdp.mjs: Zero-Dependency Browser Driver

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/taste-skill/scripts/lib/cdp.mjs](skills/taste-skill/scripts/lib/cdp.mjs)
- [tests/profile-cleanup.mjs](tests/profile-cleanup.mjs)

</details>



This page details `cdp.mjs`, a zero-dependency client for the Chrome DevTools Protocol (CDP). It enables programmatic control of Chrome, Edge, or Chromium browsers directly from Node.js, without requiring external npm packages like Puppeteer. Its primary role within `taste-skill` is to drive real-browser inspections and screenshot captures during the Gate phase of the pipeline.

## Overview

`cdp.mjs` provides core functionalities for:
*   **Browser Discovery**: Locating an installed Chrome-compatible browser executable.
*   **Browser Launching**: Starting a headless browser instance with specific configurations and managing its lifecycle.
*   **Page Interaction**: Navigating to URLs, executing JavaScript, taking screenshots, and simulating user input like mouse wheel events.
*   **Profile Management**: Creating and cleaning up temporary browser profiles to ensure isolated and clean runs. This includes a robust mechanism for identifying and removing abandoned profiles.

The module leverages Node.js's built-in `WebSocket` client (requiring Node 22+) and `child_process` for spawning the browser process.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:1-3]()

## Browser Discovery: `findChrome()`

The `findChrome()` function attempts to locate a Chrome, Edge, or Chromium executable on the system. It checks common installation paths across Windows, macOS, and Linux, and also respects `CHROME_PATH` or `PUPPETEER_EXECUTABLE_PATH` environment variables.

```javascript
export function findChrome() {
  const env = process.env.CHROME_PATH || process.env.PUPPETEER_EXECUTABLE_PATH;
  if (env && existsSync(env)) return env;
  // ... platform-specific paths ...
  for (const c of candidates) if (c && existsSync(c)) return c;
  return null;
}
```

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:11-38]()

## Browser Launching: `Browser.launch()`

The `Browser.launch()` static method is responsible for starting a new headless browser instance. It performs several critical steps:

1.  **Environment Check**: Ensures Node.js 22+ is running for the built-in `WebSocket`.
2.  **Executable Discovery**: Calls `findChrome()` to locate the browser executable.
3.  **Profile Management**:
    *   Determines a temporary directory for browser profiles (defaulting to `os.tmpdir()`).
    *   Calls `sweepProfiles()` to clean up any abandoned profiles from previous runs.
    *   Creates a new, unique temporary directory (`ad-chrome-`) for the current browser session.
    *   Writes an `OWNER` file (`taste-skill-owner.json`) into the profile directory to mark ownership by the current process and the spawned Chrome process. This file contains the hostname, the Node.js process ID (`pid`), and the Chrome process ID (`chrome`).
4.  **Process Spawning**: Spawns the browser executable with a set of arguments tailored for headless operation, performance, and isolation. Key arguments include:
    *   `--headless=new`: Runs the browser in new headless mode.
    *   `--remote-debugging-port=0`: Assigns a random available port for CDP.
    *   `--user-data-dir=<temp_profile_dir>`: Uses the newly created temporary profile.
    *   `--disk-cache-size`, `--media-cache-size`: Limits cache sizes.
    *   `--window-size`: Sets the initial viewport dimensions.
    *   Various `--disable-*` flags to prevent unwanted browser behaviors (e.g., background throttling, translation).
5.  **CDP Connection**:
    *   Parses the WebSocket URL from the browser's stderr output.
    *   Establishes a WebSocket connection to the browser's DevTools endpoint.
    *   Initializes internal state for managing CDP commands and events.
6.  **Resource Cleanup**: Registers `drop()` handlers for `exit`, `SIGINT`, `SIGTERM`, and `SIGHUP` events to ensure the spawned browser process is killed and its temporary profile directory is removed upon the Node.js process exiting.

### Browser Launch Flow
```mermaid
graph TD
    A[Browser.launch() called] --> B{Node 22+?};
    B -- No --> E[Error: Node 22+ required];
    B -- Yes --> C[findChrome() to locate executable];
    C -- Not found --> E;
    C -- Found --> D[Determine temp profile base dir];
    D --> F[sweepProfiles() to clean old profiles];
    F --> G[Create new temp profile dir "ad-chrome-*"];
    G --> H[Write taste-skill-owner.json (Node PID)];
    H --> I[Spawn Chrome process with args];
    I --> J[Capture Chrome PID];
    J --> K[Update taste-skill-owner.json (Chrome PID)];
    K --> L[Listen to Chrome stderr for WebSocket URL];
    L -- URL found --> M[Establish WebSocket connection to CDP];
    M -- Connected --> N[Return Browser instance];
    I -- Chrome exits early --> E;
    L -- Timeout --> E;
    M -- Connection error --> E;
    N --> O[Register exit/signal handlers to drop() profile and kill Chrome];
```

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:64-128]()

## Page Interaction APIs

The `Browser` class provides methods to interact with browser pages.

### `Browser.send(method, params, sessionId, timeoutMs)`
This is the low-level method for sending raw CDP commands. It manages request IDs, pending promises, and timeouts.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:130-137]()

### `Browser.newPage()`
Creates a new browser page (tab) and returns a `Page` instance. It internally uses `Target.createTarget` and `Target.attachToTarget` CDP commands.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:140-147]()

### `Page` Class
The `Page` class encapsulates interactions with a single browser tab.

#### `page.goto(url, { timeoutMs, waitUntil })`
Navigates the page to a given URL. It supports `timeoutMs` and `waitUntil` options (e.g., `'networkidle0'`, `'domcontentloaded'`, `'load'`). It uses `Page.navigate` and waits for the specified event.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:150-164]()

#### `page.eval(expression, { timeoutMs, awaitPromise })`
Executes a JavaScript `expression` within the page's context. It uses `Runtime.evaluate`. `awaitPromise` can be set to `true` to wait for the promise returned by the expression to resolve.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:166-175]()

#### `page.screenshot(options)`
Takes a screenshot of the page. Options include `format` (png/jpeg), `quality`, `clip` (x, y, width, height, scale), and `fullPage`. It uses `Page.captureScreenshot`.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:177-190]()

#### `page.wheel(x, y, deltaX, deltaY, { timeoutMs })`
Simulates a mouse wheel event at specified coordinates with given deltas. This is useful for scrolling. It uses `Input.dispatchMouseEvent` with type `'mouseWheel'`.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:192-200]()

#### `page.on(method, handler)` and `page.off(method, handler)`
Registers and unregisters event listeners for CDP events specific to this page's session (e.g., `Page.loadEventFired`, `Runtime.consoleAPICalled`).

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:202-211]()

#### `page.close()`
Closes the page (tab). It uses `Target.closeTarget`.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:213-215]()

### `Browser.close()`
Closes the entire browser instance, kills the process, and cleans up the temporary profile directory.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:217-220]()

## Throwaway Profiles and Cleanup

`cdp.mjs` is designed to use "throwaway profiles" for each browser launch. This ensures that each run starts with a clean browser state, free from cookies, cache, or extensions from previous sessions.

### `taste-skill-owner.json` Ownership Markers

To facilitate robust cleanup, each temporary profile directory created by `Browser.launch()` contains a file named `taste-skill-owner.json`. This file records:
*   `host`: The hostname of the machine that created the profile.
*   `pid`: The process ID of the Node.js script that launched the browser.
*   `chrome`: The process ID of the spawned Chrome browser.

This ownership marker is crucial for `sweepProfiles()` to correctly identify and remove abandoned profiles.

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:40-43]()
*   [skills/taste-skill/scripts/lib/cdp.mjs:78-79]()

### `sweepProfiles(base)` Cleanup

The `sweepProfiles(base)` function is called at the beginning of `Browser.launch()` to clean up any profiles left behind by previous, potentially crashed, runs. It iterates through directories starting with `ad-chrome-` within the `base` directory (typically `os.tmpdir()`).

For each such directory, it attempts to read the `taste-skill-owner.json` file. A profile is removed only if *all* of the following conditions are met:
1.  The `taste-skill-owner.json` file exists and is valid JSON.
2.  The `host` in the owner file matches the current machine's hostname.
3.  Both the `pid` (Node.js process) and `chrome` (browser process) recorded in the owner file are no longer alive (checked using `process.kill(pid, 0)`).

Profiles without an owner file (e.g., created by older versions or other tools) or those belonging to another machine are never touched. This prevents accidental deletion of profiles not managed by `taste-skill`.

### Profile Cleanup Logic
```mermaid
graph TD
    A[sweepProfiles(base) called] --> B{Read directories in base};
    B --> C{For each dir 'ad-chrome-*'};
    C --> D{Read taste-skill-owner.json};
    D -- Error/Missing --> E[Skip: Not owned or invalid];
    D -- Success --> F{Owner.host == current hostname?};
    F -- No --> E;
    F -- Yes --> G{Owner.pid and Owner.chrome are both NOT alive?};
    G -- No --> E;
    G -- Yes --> H[Remove profile directory recursively];
```

Sources:
*   [skills/taste-skill/scripts/lib/cdp.mjs:50-62]()
*   [skills/taste-skill/scripts/lib/cdp.mjs:45-48]()

## Testing Profile Cleanup: `tests/profile-cleanup.mjs`

The `tests/profile-cleanup.mjs` file contains tests specifically for the profile management and cleanup logic in `cdp.mjs`.

It uses a fixture-based approach where a child process is spawned (`--fixture` argument) to simulate a browser launch and profile creation/cleanup scenarios. This isolates the test from the main test runner's process lifecycle.

Key test cases include:
*   **`launch preserves older foreign profiles and close removes its own`**: Verifies that `Browser.launch()` does not delete profiles that are still in use or not owned by the current machine, but successfully cleans up its own profile upon `browser.close()`.
*   **`sweep removes a profile only when its owner file says both processes are gone`**: Directly tests `sweepProfiles()` with various scenarios:
    *   Abandoned profiles (both Node and Chrome PIDs are dead) are removed.
    *   Profiles with an alive Node process are kept.
    *   Profiles with an alive Chrome process are kept.
    *   Profiles owned by a different hostname are kept.
    *   Profiles without an `OWNER` file are kept.
    *   Profiles with malformed `OWNER` files are kept.
    *   Profiles with invalid PIDs are kept.
    *   Directories not matching the `ad-chrome-` prefix are ignored.

The tests use a "fake Chrome" executable [tests/profile-cleanup.mjs:61-63]() that simply prints the DevTools WebSocket URL and then idles, avoiding the need for a real browser installation during testing.

Sources:
*   [tests/profile-cleanup.mjs:1-100]()

---

