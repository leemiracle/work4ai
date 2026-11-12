# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [cloakbrowser/_version.py](cloakbrowser/_version.py)
- [dotnet/README.md](dotnet/README.md)
- [dotnet/src/CloakBrowser/CloakBrowser.csproj](dotnet/src/CloakBrowser/CloakBrowser.csproj)
- [dotnet/src/CloakBrowser/CloakVersion.cs](dotnet/src/CloakBrowser/CloakVersion.cs)
- [js/package-lock.json](js/package-lock.json)
- [js/package.json](js/package.json)

</details>



This page introduces CloakBrowser: what it is, why it exists, its high-level architecture connecting the three language packages (Python, JavaScript, and .NET) to the patched Chromium binary, and the bot-detection services it bypasses.

---

## What Is CloakBrowser

CloakBrowser is a stealth browser automation library distributed as three packages: `cloakbrowser` on PyPI, `cloakbrowser` on npm, and `CloakBrowser` on NuGet [README.md:101-122](). All packages are thin wrappers around a custom-built Chromium binary that has **71+ source-level C++ patches** applied directly to the browser engine [README.md:39-43](), [README.md:153-154]().

The library is a **drop-in replacement** for Playwright (Python, JavaScript, and .NET) and Puppeteer (JavaScript). Users call `launch()` and receive a standard Playwright `Browser` or Puppeteer `Browser` object; the API remains unchanged, allowing for a migration from stock automation frameworks by simply swapping the import [README.md:35-37](), [README.md:135-147]().

Sources: [README.md:35-43](), [README.md:101-122](), [README.md:135-147](), [README.md:153-154]()

---

## Why Source-Level Patches

Existing stealth tools (like `playwright-stealth` or `undetected-chromedriver`) work by injecting JavaScript or tweaking Chrome flags. These techniques are easily detected by modern antibot systems through overwritten `navigator` properties, CDP signal leakage, or proxy signal leaks [README.md:21-23]().

CloakBrowser patches Chromium at the C++ layer before compilation [README.md:21-23](). The binary that ships is a real Chromium build — the fingerprint modifications are present in the renderer and browser processes natively. Detection surfaces see consistent, correlated values (GPU, screen, UA, hardware reporting) that match a real user's browser because it *is* a real browser [README.md:21-23](), [README.md:39-43]().

**Key improvements over standard automation:**
- **Coherent Identities:** Fingerprints are built from real-world hardware values (GPU, display, graphics parameters) so they form a self-consistent device with no internal contradictions [README.md:158-159](), [CHANGELOG.md:11-14]().
- **Proxy Signal Removal:** DNS/connect/SSL timing is zeroed, proxy cache headers are stripped, and `Proxy-Connection` header leaks are removed to prevent detection [README.md:165-166]().
- **WebRTC IP Spoofing:** The `--fingerprint-webrtc-ip=auto` flag resolves proxy exit IPs to spoof WebRTC ICE candidates natively [README.md:167-168]().
- **Automation Signal Masking:** Patches internal CDP and automation signals that reCAPTCHA Enterprise and other advanced systems use to identify remote-controlled browsers [README.md:39-43]().

Sources: [README.md:21-23](), [README.md:39-43](), [README.md:158-168](), [CHANGELOG.md:11-14]()

---

## Free vs. Pro Tier Model

CloakBrowser operates on a tiered binary model. While the wrapper code is open-source (MIT License), the binaries are governed by a separate license [README.md:45-45]().

| Tier | Binary Version | Features |
|---|---|---|
| **Free** | Chromium v146 | 58+ patches. Available for personal and commercial use via GitHub sign-in [README.md:166-167](). |
| **Pro** | Chromium v150+ | 71+ source-level patches. Latest fingerprint updates, highest reCAPTCHA scores (0.9), Windows native GPU passthrough, and expanded locale coverage [README.md:153-159](), [CHANGELOG.md:11-13](). |

The Pro tier requires a `license_key` (`licenseKey` in JS, `LicenseKey` in .NET) passed to `launch()` or set via the `CLOAKBROWSER_LICENSE_KEY` environment variable [README.md:155-155](). The wrappers automatically handle license validation and session counting, raising a `CloakBrowserLicenseError` if limits are exceeded or if the license is invalid [CHANGELOG.md:38-45]().

Sources: [README.md:153-167](), [CHANGELOG.md:11-45]()

---

## System Architecture

The codebase consists of parallel implementations across three languages, all targeting a shared binary ecosystem.

**CloakBrowser: Module and Entity Map**

```mermaid
graph TD
    subgraph "Python Package (PyPI: cloakbrowser)"
        PyInit["cloakbrowser/__init__.py\n(launch / launch_async)"]
        PyDownload["cloakbrowser/download.py\nensure_binary"]
        PyConfig["cloakbrowser/config.py\nget_default_stealth_args"]
        PyHuman["cloakbrowser/human/config.py\nHumanConfig"]
    end

    subgraph "JavaScript Package (npm: cloakbrowser)"
        JSIndex["js/src/index.ts\n(launch / launchContext)"]
        JSPuppeteer["js/src/puppeteer.ts\n(Puppeteer launch)"]
        JSDownload["js/src/download.ts\nensureBinary"]
        JSConfig["js/src/config.ts\ngetEffectiveVersion"]
    end

    subgraph ".NET Package (NuGet: CloakBrowser)"
        NetLauncher["dotnet/src/CloakBrowser/CloakLauncher.cs\nLaunchAsync"]
        NetDownload["dotnet/src/CloakBrowser/Download.cs\nEnsureBinaryAsync"]
        NetConfig["dotnet/src/CloakBrowser/Config.cs\nGetDefaultStealthArgs"]
        NetHuman["dotnet/src/CloakBrowser/Human/HumanConfig.cs\nHumanConfig"]
    end

    subgraph "Binary Layer"
        BinCache["~/.cloakbrowser/\n(Binary & License Cache)"]
        BinExec["Stealth Chromium\n(v146 Free / v150 Pro)"]
        LicenseGate["cloakbrowser.dev\n(License Validation)"]
    end

    PyInit --> PyDownload
    JSIndex --> JSDownload
    NetLauncher --> NetDownload

    PyInit -.-> BinExec
    JSIndex -.-> BinExec
    NetLauncher -.-> BinExec
    
    PyDownload -.-> LicenseGate
    JSDownload -.-> LicenseGate
    NetDownload -.-> LicenseGate
    
    BinExec --> BinCache
```

Sources: [README.md:101-122](), [js/package.json:1-21](), [cloakbrowser/_version.py:1-1](), [dotnet/src/CloakBrowser/CloakVersion.cs:1-8](), [dotnet/README.md:108-146]()

---

## Launch and Resolution Flow

When a user calls `launch()`, the wrapper performs binary resolution and stealth configuration before spawning the process.

**launch() to usable Browser object**

```mermaid
sequenceDiagram
    participant User as User Code
    participant Wrapper as launch() / LaunchAsync()
    participant BinaryMgr as ensure_binary() / EnsureBinaryAsync()
    participant Config as config.py / Config.cs / config.ts
    participant Framework as Playwright / Puppeteer
    participant Binary as Patched Chromium Binary

    User->>Wrapper: launch(humanize=True, geoip=True)
    Wrapper->>BinaryMgr: resolve path (Free vs Pro via license_key)
    BinaryMgr-->>Wrapper: /path/to/stealth_chrome
    Wrapper->>Config: get_default_stealth_args()
    Config-->>Wrapper: --fingerprint=SEED --fingerprint-gpu=...
    Wrapper->>Framework: chromium.launch(executable_path, args)
    Framework->>Binary: spawn with C++ patches
    Binary-->>Framework: CDP Connection
    Framework-->>Wrapper: Browser Object
    Wrapper->>User: Browser (with Humanize decorators/patches)
```

Sources: [README.md:55-95](), [CHANGELOG.md:43-45](), [dotnet/README.md:48-66](), [dotnet/README.md:114-123]()

---

## Stealth Mechanism Summary

- **71+ Source-Level Patches:** Covers canvas, WebGL, audio, fonts, GPU, screen, WebRTC, network timing, and automation signals [README.md:39-43](), [README.md:153-154]().
- **`humanize=True`:** Activates a behavioral layer simulating Bézier mouse curves, per-character typing with mistypes, and realistic scroll patterns across all three languages [README.md:40-40](), [CHANGELOG.md:22-31]().
- **GeoIP Auto-Detection:** Automatically matches browser timezone and locale to the proxy's exit IP using an offline GeoLite2 database [README.md:82-82](), [CHANGELOG.md:37-37]().
- **Native SOCKS5/HTTP Proxy:** Credentials and UDP (QUIC/HTTP3) are handled natively by the binary to prevent proxy-specific header leaks [README.md:165-166]().

Sources: [README.md:39-43](), [README.md:153-166](), [CHANGELOG.md:22-37]()

---

## Bot Detection Results

CloakBrowser is tested against major detection services to ensure high human-scores.

| Detection Service | Stock Playwright | CloakBrowser | Status |
|---|---|---|---|
| **reCAPTCHA v3** | ~0.1 (Bot) | **0.9** (Human) | ✅ Pass [README.md:41-41]() |
| **Cloudflare Turnstile** | Blocked | **Pass** | ✅ Pass [README.md:28-30]() |
| **FingerprintJS** | Detected | **Pass** | ✅ Pass [README.md:42-42]() |
| **BrowserScan** | Detected | **Normal** | ✅ Pass [README.md:42-42]() |

Sources: [README.md:28-30](), [README.md:41-42]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [cloakbrowser/_version.py](cloakbrowser/_version.py)
- [js/README.md](js/README.md)
- [js/package.json](js/package.json)

</details>



This page covers installation, first-steps configuration, and minimal working examples for the Python, JavaScript, and .NET packages. It serves as the practical entry point for new users.

For a conceptual overview of how the packages relate to the stealth binary and automation frameworks, see the **Overview** page. For full API parameter reference, see **Python API Reference**, **JavaScript Playwright API**, or **.NET API Reference**.

---

## Prerequisites

| Requirement | Python | JavaScript | .NET |
|---|---|---|---|
| Runtime | Python ≥ 3.9 | Node.js ≥ 20.0.0 | .NET 8.0 SDK |
| Automation framework | `playwright` | `playwright-core` or `puppeteer-core` | `Microsoft.Playwright` |
| Binary download | ~200 MB | ~200 MB | ~200 MB |
| Supported platforms | Linux, macOS, Windows | Linux, macOS, Windows | Linux, macOS, Windows |

Sources: [js/package.json:57-59](), [js/README.md:25-28](), [README.md:123-123](), [CHANGELOG.md:11-11]()

---

## Installation

### Python
```bash
pip install cloakbrowser
```
The `playwright` and `httpx` packages are dependencies and are installed automatically. For optional GeoIP auto-detection, install the extra:
```bash
pip install 'cloakbrowser[geoip]'
```
Sources: [README.md:103-105](), [README.md:131-133]()

### JavaScript
Install `cloakbrowser` alongside your preferred automation framework.
```bash
# For use with Playwright
npm install cloakbrowser playwright-core

# For use with Puppeteer
npm install cloakbrowser puppeteer-core
```
To enable GeoIP auto-detection, install `mmdb-lib`.
Sources: [js/README.md:23-29](), [js/README.md:141-146]()

### .NET
```bash
dotnet add package CloakBrowser
```
The .NET client is a community-maintained wrapper built on `Microsoft.Playwright` and mirrors the Python/JS wrappers.
Sources: [README.md:120-123]()

---

## Free vs. Pro Tier

CloakBrowser operates on a tiered binary model:
*   **Free Tier**: Access to Chromium v146. This version includes 71 source-level patches and is the default for all users without a license key.
*   **Pro Tier**: Access to the latest builds (e.g., Chromium v150.0.7871.114.6). Pro binaries include improved rendering consistency, expanded hardware-profile pools, and server-verified reCAPTCHA v3 scores of 0.9.

To activate Pro, provide a `license_key` (Python) / `licenseKey` (JS) / `LicenseKey` (.NET) in the launch function or set the `CLOAKBROWSER_LICENSE_KEY` environment variable. You can also use `cloakbrowser login` to authenticate via GitHub for a free license key.

Sources: [README.md:41-45](), [README.md:153-155](), [CHANGELOG.md:11-16](), [CHANGELOG.md:47-47](), [js/README.md:166-167]()

---

## Binary Download and Resolution

On the first call to `launch()` or `ensureBinary()`, the package resolves the correct binary based on your tier and platform.

Title: Binary Resolution and Download Flow
```mermaid
flowchart TD
    A["launch() called"] --> B{"CLOAKBROWSER_BINARY_PATH set?"}
    B -->|"Yes"| C["Use custom binary path\nskip all download logic"]
    B -->|"No"| D{"License Key provided?"}
    D -->|"Yes"| E["Resolve latest Pro version\nfrom cloakbrowser.dev"]
    D -->|"No"| F["Use default Free version\n(v146)"]
    E --> G{"Binary present in\n~/.cloakbrowser/?"}
    F --> G
    G -->|"No"| H["Download .tar.gz\nfrom DOWNLOAD_BASE_URL"]
    H --> I["Verify SHA-256 and\nEd25519 signature"]
    I --> J["Extract archive\napply path-traversal filter"]
    J --> K["Set chmod 755\nmacOS: remove quarantine xattr"]
    K --> L["Return binary path"]
    G -->|"Yes"| L
```

Sources: [README.md:127-127](), [js/README.md:31-31](), [CHANGELOG.md:11-17]()

---

## Minimal Examples

### Python
```python
from cloakbrowser import launch

browser = launch(
    proxy="http://user:pass@residential-proxy:port",
    geoip=True,       # match timezone + locale to proxy IP
    headless=False,   # headed mode
    humanize=True     # human-like mouse, keyboard, scroll
)
page = browser.new_page()
page.goto("https://example.com")
browser.close()
```
Sources: [README.md:80-86]()

### JavaScript (Playwright)
```javascript
import { launch } from 'cloakbrowser';

const browser = await launch({
    proxy: 'http://user:pass@residential-proxy:port',
    geoip: true,
    headless: false,
    humanize: true,
});
const page = await browser.newPage();
await page.goto('https://example.com');
await browser.close();
```
Sources: [js/README.md:49-56]()

### .NET
```csharp
using CloakBrowser;

var browser = await CloakLauncher.LaunchAsync(new LaunchOptions { 
    Proxy = "http://user:pass@residential-proxy:port",
    GeoIp = true,
    Headless = false, 
    Humanize = true 
});
var page = await browser.NewPageAsync();
await page.GotoAsync("https://example.com");
await browser.CloseAsync();
```
Sources: [README.md:117-123](), [CHANGELOG.md:22-22]()

---

## Code Entity Mapping

This diagram maps natural language concepts to specific code entities across the three supported languages.

Title: Natural Language Space to Code Entity Space
```mermaid
graph TD
    subgraph "Python (cloakbrowser)"
        PyLaunch["launch() / launch_async()"]
        PyBinary["ensure_binary() / binary_info()"]
        PyConfig["_version.py: __version__"]
    end

    subgraph "JavaScript (js/src)"
        JSLaunch["launch() / launchContext()"]
        JSBinary["ensureBinary() / binaryInfo()"]
        JSConfig["package.json: version"]
    end

    subgraph ".NET (dotnet/src/CloakBrowser)"
        DotNetLaunch["CloakLauncher.LaunchAsync()"]
        DotNetConfig["LaunchOptions.cs: LaunchOptions"]
        DotNetHuman["Humanize.Unwrap()"]
    end

    Concept1["Launch Browser"] --> PyLaunch
    Concept1 --> JSLaunch
    Concept1 --> DotNetLaunch

    Concept2["Manage Binary"] --> PyBinary
    Concept2 --> JSBinary

    Concept3["Version Config"] --> PyConfig
    Concept3 --> JSConfig
    Concept3 --> DotNetConfig

    Concept4["Humanize Interop"] --> DotNetHuman
```

Sources: [README.md:55-75](), [js/README.md:37-72](), [cloakbrowser/_version.py:1-1](), [js/package.json:3-3](), [CHANGELOG.md:31-31]()

---

## Docker Setup

The `cloakhq/cloakbrowser` Docker image comes with system dependencies and the stealth binary pre-installed.

### Binary Pre-download
To include the binary in your own image to avoid runtime downloads:
```dockerfile
# Python
RUN python -m cloakbrowser install

# JavaScript
RUN npx cloakbrowser install
```
Sources: [js/README.md:168-168](), [README.md:49-51]()

### Running the Container
The container supports headed mode via an internal virtual display.
```bash
docker run --rm cloakhq/cloakbrowser cloaktest
```
Sources: [README.md:50-51]()

---

## Configuration Summary

| Option | Python | JS | .NET | Description |
|---|---|---|---|---|
| Proxy | `proxy` | `proxy` | `Proxy` | Supports HTTP/SOCKS5 with inline auth. |
| GeoIP | `geoip` | `geoip` | `GeoIp` | Match timezone/locale to proxy exit IP. |
| Humanize | `humanize` | `humanize` | `Humanize` | Enable Bézier curves and human typing timing. |
| License | `license_key` | `licenseKey` | `LicenseKey` | Activate Pro tier (v150+) features. |

Sources: [README.md:80-95](), [js/README.md:47-56](), [CHANGELOG.md:53-53](), [README.md:155-155]()

---

# Page: Python Package

# Python Package

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/__init__.py](cloakbrowser/__init__.py)
- [cloakbrowser/browser.py](cloakbrowser/browser.py)
- [cloakbrowser/config.py](cloakbrowser/config.py)
- [js/src/config.ts](js/src/config.ts)
- [js/src/index.ts](js/src/index.ts)
- [js/src/playwright.ts](js/src/playwright.ts)
- [js/src/puppeteer.ts](js/src/puppeteer.ts)
- [js/src/types.ts](js/src/types.ts)
- [js/tests/launch.test.ts](js/tests/launch.test.ts)

</details>



This page covers the structure, module layout, public API surface, versioning, and runtime dependencies of the `cloakbrowser` Python package. It is an overview document; for detailed function-level reference see [Python API Reference](#3.1), [Python Configuration Module](#3.2), and [Python Binary Management](#3.3).

---

## Purpose

The `cloakbrowser` Python package is a drop-in replacement for Playwright that routes browser automation through a patched Chromium binary. It handles binary lifecycle management (download, cache, auto-update), stealth argument configuration, and Playwright session wiring — all behind a minimal public API.

Sources: [cloakbrowser/__init__.py:1-12](), [cloakbrowser/browser.py:1-13]()

---

## Module Layout

The package lives in the `cloakbrowser/` directory at the repository root. Each module has a single, well-defined responsibility.

**Module structure diagram**

```mermaid
graph TD
    ["init [cloakbrowser/__init__.py]"]
    ["browser [cloakbrowser/browser.py]"]
    ["download [cloakbrowser/download.py]"]
    ["config [cloakbrowser/config.py]"]
    ["human [cloakbrowser/human/]"]
    ["license [cloakbrowser/license.py]"]
    ["version [cloakbrowser/_version.py]"]

    ["init [cloakbrowser/__init__.py]"] --> ["browser [cloakbrowser/browser.py]"]
    ["init [cloakbrowser/__init__.py]"] --> ["download [cloakbrowser/download.py]"]
    ["init [cloakbrowser/__init__.py]"] --> ["config [cloakbrowser/config.py]"]
    ["init [cloakbrowser/__init__.py]"] --> ["human [cloakbrowser/human/]"]
    ["init [cloakbrowser/__init__.py]"] --> ["license [cloakbrowser/license.py]"]
    ["init [cloakbrowser/__init__.py]"] --> ["version [cloakbrowser/_version.py]"]

    ["browser [cloakbrowser/browser.py]"] --> ["download [cloakbrowser/download.py]"]
    ["browser [cloakbrowser/browser.py]"] --> ["config [cloakbrowser/config.py]"]
    ["browser [cloakbrowser/browser.py]"] --> ["license [cloakbrowser/license.py]"]
    ["download [cloakbrowser/download.py]"] --> ["config [cloakbrowser/config.py]"]
    ["license [cloakbrowser/license.py]"] --> ["config [cloakbrowser/config.py]"]
```

Sources: [cloakbrowser/__init__.py:14-18]()

| Module | Primary exports | Role |
|---|---|---|
| `__init__.py` | All public symbols | Re-exports; defines `__all__`; handles lazy loading for `HumanConfig` |
| `browser.py` | `launch`, `launch_async`, `launch_context`, `ProxySettings` | Playwright session setup and browser patching |
| `download.py` | `ensure_binary`, `clear_cache`, `binary_info`, `check_for_update` | Binary lifecycle and download management |
| `config.py` | `CHROMIUM_VERSION`, `get_default_stealth_args`, path helpers | Constants, platform logic, and stealth defaults |
| `license.py` | `validate_license`, `CloakBrowserLicenseError`, `LicenseInfo` | License resolution, server validation, and Pro tier exit code mapping |
| `human/` | `HumanConfig`, `resolve_config` | Behavioral layer for human-like interactions |
| `_version.py` | `__version__` | Single-source version string |

Sources: [cloakbrowser/__init__.py:14-54]()

---

## Public API Surface

`__init__.py` is the primary entry point for user code. It imports from internal modules and declares `__all__` explicitly. Notably, it uses `__getattr__` to lazily load the `HumanConfig` components to avoid unnecessary imports if the behavioral layer is not used.

**API surface diagram**

```mermaid
graph LR
    subgraph "Natural Language Space"
        User["User Code"]
    end

    subgraph "Code Entity Space"
        init["cloakbrowser/__init__.py"]
        launch["launch()"]
        human_config["HumanConfig"]
        ver["__version__"]
        lic["validate_license()"]
        
        browser_py["cloakbrowser/browser.py"]
        human_py["cloakbrowser/human/config.py"]
        ver_py["cloakbrowser/_version.py"]
        lic_py["cloakbrowser/license.py"]
    end

    User -- "imports" --> init
    init -- "exports" --> launch
    init -- "exports" --> human_config
    init -- "exports" --> ver
    init -- "exports" --> lic

    launch -- "defined in" --> browser_py
    human_config -- "lazy loaded from" --> human_py
    ver -- "defined in" --> ver_py
    lic -- "defined in" --> lic_py
```

Sources: [cloakbrowser/__init__.py:14-54]()

The complete `__all__` list as declared in `__init__.py`:

```python
__all__ = [
    "launch",
    "launch_async",
    "launch_context",
    "launch_context_async",
    "launch_persistent_context",
    "launch_persistent_context_async",
    "ensure_binary",
    "clear_cache",
    "binary_info",
    "check_for_update",
    "CHROMIUM_VERSION",
    "get_default_stealth_args",
    "build_args",
    "maybe_resolve_geoip",
    "ProxySettings",
    "validate_license",
    "LicenseInfo",
    "CloakBrowserLicenseError",
    "HumanConfig",
    "resolve_human_config",
    "__version__",
]
```

Sources: [cloakbrowser/__init__.py:32-54]()

---

## Versioning

The package version is stored as a plain string in `_version.py`. This ensures the version is consistent across `pip show cloakbrowser`, `cloakbrowser.__version__`, and the built distribution metadata.

- Single source of truth: [cloakbrowser/_version.py:1-1]()
- Re-exported in `__init__.py` as `__version__`: [cloakbrowser/__init__.py:18-18]()

Sources: [cloakbrowser/_version.py:1-1]()

---

## Runtime Dependencies

The package relies on several key libraries to function:

| Dependency | Role |
|---|---|
| `playwright` | Core automation framework; `launch()` delegates to it. |
| `httpx` | HTTP client for binary downloads, license validation, and update checks. |
| `mmdb-lib` | (Optional) Required for `geoip=True` auto-detection. |

Sources: [cloakbrowser/browser.py:3-4](), [js/package.json:60-65]()

Python version support: `>=3.9` is required due to type hinting and dependency constraints.

---

## Licensing and Pro Tier

The Python package includes a dedicated `license.py` module to handle CloakBrowser Pro features. It maps specific Chromium exit codes (76-79) to human-readable `CloakBrowserLicenseError` messages, such as session limits or invalid keys.

- **Resolution Priority:** Explicit parameter > `CLOAKBROWSER_LICENSE_KEY` env var > `~/.cloakbrowser/license.key` file.
- **Caching:** Validated licenses are cached locally for 24 hours to minimize API calls.
- **Guard Logic:** The package uses `_install_license_guard` to intercept post-launch license denials and surface them as `CloakBrowserLicenseError` instead of generic `TargetClosedError`.

Sources: [cloakbrowser/browser.py:123-161](), [cloakbrowser/browser.py:33-41](), [cloakbrowser/__init__.py:17-17]()

---

## Typical Import Pattern

The simplest usage pattern involves importing `launch` directly from the top-level package:

```python
from cloakbrowser import launch

# Launches patched Chromium and returns a Playwright Browser object
browser = launch()
page = browser.new_page()
page.goto("https://protected-site.com")
browser.close()
```

Sources: [cloakbrowser/__init__.py:5-11]()

---

## Related Pages

- [Python API Reference](#3.1) — Full parameter-level documentation for `launch()`, `launch_context()`, and utility functions.
- [Python Configuration Module](#3.2) — `config.py` internals: platform detection, stealth argument generation, and path resolution.
- [Python Binary Management](#3.3) — `download.py` internals: download flow, extraction, and auto-update logic.
- [JavaScript Package](#4) — The parallel npm package with equivalent functionality.

---

# Page: Python API Reference

# Python API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/__init__.py](cloakbrowser/__init__.py)
- [cloakbrowser/browser.py](cloakbrowser/browser.py)
- [js/src/index.ts](js/src/index.ts)
- [js/src/playwright.ts](js/src/playwright.ts)
- [js/src/puppeteer.ts](js/src/puppeteer.ts)
- [js/src/types.ts](js/src/types.ts)
- [js/tests/launch.test.ts](js/tests/launch.test.ts)
- [tests/test_launch.py](tests/test_launch.py)
- [tests/test_launch_context.py](tests/test_launch_context.py)
- [tests/test_persistent_context.py](tests/test_persistent_context.py)

</details>



This page is a full reference for every public symbol exported by the `cloakbrowser` Python package. It covers the launch functions, utility functions for binary management, and internal mechanics such as proxy URL parsing and the `close()` patch.

- For the module layout, versioning, and runtime dependencies, see [Python Package](3).
- For the full behavior of `ensure_binary()`, the download pipeline, and auto-update logic, see [Python Binary Management](3.3).
- For `config.py` symbols such as `CHROMIUM_VERSION`, `get_default_stealth_args()`, and platform helpers, see [Python Configuration Module](3.2).
- For the equivalent JavaScript API, see [JavaScript Playwright API](4.1).

---

## Public API Surface

All public symbols are re-exported from [`cloakbrowser/__init__.py`](cloakbrowser/__init__.py:1-54)().

| Symbol | Type | Source module |
|---|---|---|
| `launch` | function | `browser.py` |
| `launch_async` | function | `browser.py` |
| `launch_context` | function | `browser.py` |
| `launch_context_async` | function | `browser.py` |
| `launch_persistent_context` | function | `browser.py` |
| `launch_persistent_context_async` | function | `browser.py` |
| `ensure_binary` | function | `download.py` |
| `clear_cache` | function | `download.py` |
| `binary_info` | function | `download.py` |
| `check_for_update` | function | `download.py` |
| `CHROMIUM_VERSION` | `str` constant | `config.py` |
| `get_default_stealth_args` | function | `config.py` |
| `ProxySettings` | `TypedDict` | `browser.py` |
| `HumanConfig` | `dataclass` | `human/config.py` |
| `resolve_human_config` | function | `human/config.py` |
| `__version__` | `str` constant | `_version.py` |

Sources: [cloakbrowser/__init__.py:14-54](), [cloakbrowser/browser.py:22-43]()

---

## Module Dependency Diagram

**Diagram: Public API call graph from `__init__.py` to implementation modules**

```mermaid
graph TD
    init["cloakbrowser/__init__.py\n(public re-exports)"]

    subgraph browser_mod["cloakbrowser/browser.py"]
        launch["launch()"]
        launch_async["launch_async()"]
        launch_context["launch_context()"]
        launch_persistent["launch_persistent_context()"]
        build_args["build_args()"]
        _resolve_proxy_config["_resolve_proxy_config()"]
        maybe_resolve_geoip["maybe_resolve_geoip()"]
    end

    subgraph download_mod["cloakbrowser/download.py"]
        ensure_binary["ensure_binary()"]
        clear_cache["clear_cache()"]
        binary_info["binary_info()"]
        check_for_update["check_for_update()"]
    end

    subgraph human_mod["cloakbrowser/human/"]
        patch_browser["patch_browser()"]
        resolve_config["resolve_config()"]
    end

    subgraph config_mod["cloakbrowser/config.py"]
        CHROMIUM_VERSION["CHROMIUM_VERSION"]
        get_default_stealth_args["get_default_stealth_args()"]
    end

    init --> launch
    init --> launch_async
    init --> launch_context
    init --> launch_persistent
    init --> ensure_binary
    init --> clear_cache
    init --> binary_info
    init --> check_for_update
    init --> CHROMIUM_VERSION

    launch --> ensure_binary
    launch --> maybe_resolve_geoip
    launch --> build_args
    
    launch_context --> launch
    launch_persistent --> ensure_binary
```

Sources: [cloakbrowser/__init__.py:14-54](), [cloakbrowser/browser.py:279-340](), [cloakbrowser/browser.py:438-540](), [cloakbrowser/browser.py:543-664]()

---

## Launch Functions

### `launch()`

[cloakbrowser/browser.py:279-340]()

Synchronous browser launch. Internally calls `sync_playwright().start()`, launches the stealth binary, and returns a patched `Browser` object.

**Signature:**
```python
def launch(
    headless: bool = True,
    proxy: str | ProxySettings | None = None,
    args: list[str] | None = None,
    stealth_args: bool = True,
    timezone: str | None = None,
    locale: str | None = None,
    geoip: bool = False,
    humanize: bool = False,
    human_preset: HumanPreset = "default",
    human_config: HumanConfigOverrides | None = None,
    extension_paths: list[str] | None = None,
    license_key: str | None = None,
    browser_version: str | None = None,
    **kwargs: Any,
) -> Browser
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `headless` | `bool` | `True` | Run in headless mode. |
| `proxy` | `str \| ProxySettings` | `None` | Proxy URL string or `ProxySettings` dict. Strings are auto-parsed. |
| `args` | `list[str]` | `None` | Additional Chromium CLI flags. |
| `stealth_args` | `bool` | `True` | Include default fingerprinting patches. Set to `False` for custom flags. |
| `timezone` | `str` | `None` | IANA timezone (e.g., `America/New_York`). Sets `--fingerprint-timezone` flag. |
| `locale` | `str` | `None` | BCP 47 locale (e.g., `en-US`). Sets `--lang` flag. |
| `geoip` | `bool` | `False` | Auto-detect timezone/locale from proxy IP. Requires `cloakbrowser[geoip]`. |
| `humanize` | `bool` | `False` | Enable human-like interaction patching. |
| `human_preset`| `str` | `"default"` | Preset for humanization behavior (`'default'` or `'careful'`). |
| `human_config`| `dict` | `None` | Custom overrides for humanization parameters. |
| `extension_paths`| `list[str]` | `None` | Paths to Chrome extensions to load. |
| `license_key`| `str` | `None` | Pro license key. Also reads from `CLOAKBROWSER_LICENSE_KEY`. |
| `browser_version`| `str` | `None` | Exact Chromium version pin. |

**Returns:** A Playwright `Browser` object. The `close()` method is monkey-patched to call `pw.stop()` after closing the browser [cloakbrowser/browser.py:321-330]().

**Backend Note:** The `backend` parameter has been removed. Passing `backend="patchright"` now raises a `TypeError` to guide users toward the unified Playwright-based implementation [tests/test_launch.py:14-29]().

Sources: [cloakbrowser/browser.py:279-340](), [cloakbrowser/browser.py:311-330](), [tests/test_launch.py:14-29]()

---

### `launch_async()`

[cloakbrowser/browser.py:343-435]()

Async version of `launch()`. Uses `async_playwright()` instead of `sync_playwright()`. All parameters and return behavior are identical to `launch()`, but the function must be awaited and `browser.close()` returns a coroutine.

Sources: [cloakbrowser/browser.py:343-435]()

---

### `launch_context()`

[cloakbrowser/browser.py:438-540]()

Convenience function that creates a `Browser` + `BrowserContext` in a single call. Unlike standard Playwright, `timezone` and `locale` are passed as **binary flags** to the browser process rather than via CDP emulation, ensuring they are undetectable.

**Returns:** A Playwright `BrowserContext` object. `context.close()` is patched to also call `browser.close()` [cloakbrowser/browser.py:531-538]().

Sources: [cloakbrowser/browser.py:438-540](), [tests/test_launch_context.py:1-190]()

---

### `launch_persistent_context()`

[cloakbrowser/browser.py:543-664]()

Launches a browser with a persistent user data directory. This is the preferred method for maintaining sessions/cookies.

**Signature:**
```python
def launch_persistent_context(
    user_data_dir: str | Path,
    headless: bool = True,
    # ... same parameters as launch() ...
    user_agent: str | None = None,
    viewport: dict | None = None,
    # ...
    **kwargs: Any,
) -> BrowserContext
```

**Key Difference:** It accepts a `user_data_dir`. Stealth arguments and binary flags (timezone, locale) are applied directly to the `launch_persistent_context` call [cloakbrowser/browser.py:613-630]().

Sources: [cloakbrowser/browser.py:543-664](), [tests/test_persistent_context.py:1-160]()

---

## Launch Flow Diagram

**Diagram: Execution path from `launch()` call to browser object returned**

```mermaid
sequenceDiagram
    participant user as "User Code"
    participant launch as "launch()"
    participant ensure_binary as "ensure_binary()"
    participant geoip as "maybe_resolve_geoip()"
    participant build as "build_args()"
    participant pw as "playwright.start()"
    participant chrome as "pw.chromium.launch()"
    participant license as "license_guard"

    user->>launch: "launch(humanize=True, ...)"
    launch->>ensure_binary: "ensure_binary()"
    ensure_binary-->>launch: "/path/to/chrome"
    launch->>geoip: "resolve proxy IP"
    geoip-->>launch: "timezone, locale, exit_ip"
    launch->>build: "generate --fingerprint-* flags"
    build-->>launch: "chrome_args"
    launch->>pw: "Start Playwright Instance"
    launch->>chrome: "launch(executable_path, args)"
    chrome-->>launch: "Browser Object"
    launch->>license: "install_license_guard()"
    launch-->>user: "Patched Browser"
```

Sources: [cloakbrowser/browser.py:279-340](), [cloakbrowser/browser.py:123-171]()

---

## Proxy Handling

### `ProxySettings` TypedDict
[cloakbrowser/browser.py:21-21]()
Defines the structure for proxy configuration if passed as a dictionary.
- `server`: `str` (Required)
- `bypass`: `str` (Optional)
- `username`: `str` (Optional)
- `password`: `str` (Optional)

### Proxy URL Parsing
**`_resolve_proxy_config(proxy: str | ProxySettings | None, ...)`** [cloakbrowser/browser.py:894-943]()
Extracts credentials and configuration from proxy inputs.
- Strings like `http://user:pass@host:port` are parsed into Playwright `proxy` dicts [cloakbrowser/browser.py:906-921]().
- Credentials are `unquote`'d to handle special characters [cloakbrowser/browser.py:22-22]().
- For binaries supporting inline auth (Pro tier), credentials may be passed via `--proxy-server` [cloakbrowser/browser.py:928-940]().

Sources: [cloakbrowser/browser.py:21-22](), [cloakbrowser/browser.py:894-943]()

---

## Utility Functions

### `binary_info() -> dict`
[js/src/types.ts:73-83]()
Returns metadata about the current installation.
- `version`: The effective Chromium version.
- `bundledVersion`: The wrapper's bundled baseline version.
- `platform`: The detected platform tag (e.g., `linux-x64`).
- `tier`: Either `"pro"` or `"free"`.
- `binaryPath`: Absolute path to the executable.
- `installed`: Boolean indicating if the binary exists on disk.
- `cacheDir`: Path to the local cache directory.

### `clear_cache()`
[cloakbrowser/download.py:299-303]()
Deletes the entire `~/.cloakbrowser` directory (or custom cache dir).

### `check_for_update()`
[cloakbrowser/download.py:270-296]()
Forces a check against GitHub for newer binary versions and updates the `latest_version` marker file.

Sources: [cloakbrowser/download.py:270-303](), [js/tests/launch.test.ts:7-24]()

---

## `close()` Patch Implementation

CloakBrowser patches the `close()` method to ensure that the underlying Playwright instance (started via `sync_playwright().start()`) is stopped, preventing orphaned processes.

```python
# browser.py implementation detail for launch()
pw = sync_playwright().start()
browser = pw.chromium.launch(...)

_original_close = browser.close

def _close_with_cleanup() -> None:
    try:
        _original_close()
    finally:
        pw.stop()

browser.close = _close_with_cleanup
```

Sources: [cloakbrowser/browser.py:311-330](), [cloakbrowser/browser.py:531-538]()

---

# Page: Python Configuration Module

# Python Configuration Module

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/config.py](cloakbrowser/config.py)
- [dotnet/src/CloakBrowser/Config.cs](dotnet/src/CloakBrowser/Config.cs)
- [dotnet/tests/CloakBrowser.Tests/ConfigTests.cs](dotnet/tests/CloakBrowser.Tests/ConfigTests.cs)
- [js/src/args.ts](js/src/args.ts)
- [js/src/config.ts](js/src/config.ts)
- [js/tests/config.test.ts](js/tests/config.test.ts)
- [tests/test_build_args.py](tests/test_build_args.py)
- [tests/test_config.py](tests/test_config.py)

</details>



`cloakbrowser/config.py` is the single source of truth for all constants, platform detection, and path-resolution logic used by the Python package. It determines which Chromium version to use, where binaries are cached, which stealth arguments to pass at launch, and how to construct download URLs.

For the functions that manage the binary lifecycle (download, extraction, updates), see [Python Binary Management](). For the launch functions that consume these stealth arguments, see [Python API Reference]().

---

## Constants

| Symbol | Value | Description |
|---|---|---|
| `CHROMIUM_VERSION` | `"146.0.7680.177.5"` | The latest Chromium version across all platforms, used for display and reference [[cloakbrowser/config.py:18]](). |
| `PLATFORM_CHROMIUM_VERSIONS` | `dict[str, str]` | Mapping of platform tags to their specific Chromium versions. Versions may vary during transition periods [[cloakbrowser/config.py:20-26]](). |
| `BINARY_SIGNING_PUBKEYS` | `list[str]` | Ed25519 public keys used to verify the `SHA256SUMS.sig` file during binary download [[cloakbrowser/config.py:37-39]](). |
| `IGNORE_DEFAULT_ARGS` | `["--enable-automation", ...]` | Playwright default flags that are suppressed because they leak automation signals [[cloakbrowser/config.py:47]](). |
| `DEFAULT_VIEWPORT` | `{"width": 1920, "height": 947}` | Realistic 1080p maximized window dimensions for a Windows target, used for headless mode [[cloakbrowser/config.py:86]](). |

Sources: [[cloakbrowser/config.py:18-86]]()

---

## Platform Model

The module uses a strict platform detection system to ensure binary compatibility.

**`SUPPORTED_PLATFORMS`** maps `(system, machine)` tuples from the `platform` module to internal platform tags:

| `platform.system()` | `platform.machine()` | Tag |
|---|---|---|
| `"Linux"` | `"x86_64"` | `"linux-x64"` |
| `"Linux"` | `"aarch64"` | `"linux-arm64"` |
| `"Darwin"` | `"arm64"` | `"darwin-arm64"` |
| `"Darwin"` | `"x86_64"` | `"darwin-x64"` |
| `"Windows"` | `"AMD64"` / `"x86_64"` | `"windows-x64"` |

**`AVAILABLE_PLATFORMS`** is derived from `PLATFORM_CHROMIUM_VERSIONS` and represents platforms where a pre-built binary is ready for download [[cloakbrowser/config.py:101]]().

### `get_platform_tag()`
[[cloakbrowser/config.py:144-154]]()

Resolves the host's platform tag. If the combination of `platform.system()` and `platform.machine()` is not found in `SUPPORTED_PLATFORMS`, it raises a `RuntimeError`.

### `check_platform_available()`
[[cloakbrowser/config.py:202-218]]()

Verifies that a pre-built binary exists for the detected platform. If the tag is not in `AVAILABLE_PLATFORMS`, it raises an error. This check is bypassed if `get_local_binary_override()` returns a value (e.g., when `CLOAKBROWSER_BINARY_PATH` is set).

Sources: [[cloakbrowser/config.py:91-101]](), [[cloakbrowser/config.py:144-154]](), [[cloakbrowser/config.py:202-218]]()

---

## Cache and Path Management

All binaries and metadata are stored in a centralized cache directory.

**Path Resolution Diagram:**

Title: "Binary Cache and Executable Path Resolution"
```mermaid
graph TD
    subgraph "get_cache_dir()"
        [CacheRoot] ["~/.cloakbrowser/\n(or CLOAKBROWSER_CACHE_DIR)"]
    end

    [CacheRoot] --> [VersionDir] ["get_binary_dir(version, pro)\nchromium-{version}{-pro}/"]
    [CacheRoot] --> [Marker] ["latest_version_{tag}\n(marker file, plain text)"]
    [CacheRoot] --> [GeoIP] ["geoip/\n(GeoLite2 database)"]

    [VersionDir] --> [BinaryPath] ["get_binary_path(version, pro)"]
    [BinaryPath] --> [LinuxExe] ["chrome\n(Linux)"]
    [BinaryPath] --> [WinExe] ["chrome.exe\n(Windows)"]
    [BinaryPath] --> [MacExe] ["Chromium.app/Contents/MacOS/Chromium\n(macOS)"]
```

| Function | Implementation |
|---|---|
| `get_cache_dir()` | Returns `Path.home() / ".cloakbrowser"` or the value of `CLOAKBROWSER_CACHE_DIR` [[cloakbrowser/config.py:160-170]](). |
| `get_binary_dir(v, pro)` | Joins the cache dir with `chromium-{v}`. Appends `-pro` suffix if `pro=True` [[cloakbrowser/config.py:172-177]](). |
| `get_binary_path(v, pro)` | Resolves the executable location based on OS (e.g., `.app` bundle on macOS, `.exe` on Windows) [[cloakbrowser/config.py:179-193]](). |
| `get_local_binary_override()` | Returns the value of `CLOAKBROWSER_BINARY_PATH` if set, allowing users to bypass the managed binary system [[cloakbrowser/config.py:195-200]](). |

Sources: [[cloakbrowser/config.py:160-200]]()

---

## Version Resolution

### `get_effective_version()`
[[cloakbrowser/config.py:220-244]]()

Determines the binary version to use at runtime by checking for updates.

1. It first retrieves the hardcoded version for the current platform via `get_chromium_version()` [[cloakbrowser/config.py:138-142]]().
2. It looks for a platform-scoped marker file (e.g., `latest_version_linux-x64`) in the cache directory [[cloakbrowser/config.py:230-232]]().
3. If the marker exists, it reads the version string and compares it against the hardcoded version using `_version_newer()`.
4. If the marker version is newer AND the binary exists on disk, it returns the marker version. Otherwise, it defaults to the hardcoded version.

### `get_download_url(version)`
[[cloakbrowser/config.py:273-284]]()

Constructs the URL for the binary archive. It supports a primary URL (typically `cloakbrowser.dev`) and a fallback URL pointing to GitHub Releases. The archive extension is automatically selected (`.zip` for Windows, `.tar.gz` for others) [[cloakbrowser/config.py:286-293]]().

### `normalize_requested_version(version)`
[[cloakbrowser/config.py:117-136]]()

Normalizes a version pin from arguments or the `CLOAKBROWSER_VERSION` environment variable. It ensures the version follows a strict numeric dotted format (e.g., `148.0.7778.215.2`) to prevent path traversal or invalid URL construction.

Sources: [[cloakbrowser/config.py:117-142]](), [[cloakbrowser/config.py:220-244]](), [[cloakbrowser/config.py:273-293]]()

---

## Stealth Arguments

### `get_default_stealth_args()`
[[cloakbrowser/config.py:54-77]]()

Generates the command-line flags required to activate the C++ source-level patches. It generates a random seed between `10000` and `99999` for every launch to ensure a unique fingerprint [[cloakbrowser/config.py:60]]().

**Platform Branching Logic:**
*   **macOS (Darwin):** Runs as a native Mac browser. It tells the fingerprint patches to use `macos` platform logic, ensuring GPU and User Agent match the native system to avoid detectable mismatches [[cloakbrowser/config.py:68-70]]().
*   **Linux / Windows:** Masquerades as a Windows desktop. It sets the fingerprint platform to `windows`. Hardware concurrency, device memory, and GPU profiles are auto-generated by the binary from the random seed [[cloakbrowser/config.py:72-76]]().

**Stealth Argument Generation:**

Title: "Stealth Argument Generation Logic"
```mermaid
flowchart TD
    [Start] ["get_default_stealth_args()"] --> [Seed] ["Generate Random Seed\n(10000-99999)"]
    [Seed] --> [Base] ["Base Args:\n--no-sandbox\n--fingerprint={seed}"]
    [Base] --> [Platform] {"platform.system()"}
    
    [Platform] -->|"Darwin"| [MacOS] ["Add macOS Profile:\n--fingerprint-platform=macos"]
    
    [Platform] -->|"Linux / Windows"| [WinSpoof] ["Add Windows Profile:\n--fingerprint-platform=windows"]
    
    [MacOS] --> [End] ["Return List[str]"]
    [WinSpoof] --> [End]
```

Sources: [[cloakbrowser/config.py:54-77]](), [[js/tests/config.test.ts:22-44]](), [[tests/test_build_args.py:91-105]]()

---

## Configuration Logic Flow

The following diagram illustrates how `config.py` entities interact to provide the runtime environment for the browser.

Title: "Configuration Data Flow and Environment Interaction"
```mermaid
graph LR
    subgraph "Environment Space"
        [ENV_PATH] ["CLOAKBROWSER_BINARY_PATH"]
        [ENV_CACHE] ["CLOAKBROWSER_CACHE_DIR"]
        [ENV_VER] ["CLOAKBROWSER_VERSION"]
    end

    subgraph "Code Entity Space (config.py)"
        [GET_OVERRIDE] ["get_local_binary_override()"]
        [GET_CACHE] ["get_cache_dir()"]
        [NORM_VER] ["normalize_requested_version()"]
        [GET_EFFECTIVE] ["get_effective_version()"]
        [GET_TAG] ["get_platform_tag()"]
        [GET_STEALTH] ["get_default_stealth_args()"]
    end

    [ENV_PATH] --> [GET_OVERRIDE]
    [ENV_CACHE] --> [GET_CACHE]
    [ENV_VER] --> [NORM_VER]
    [GET_CACHE] --> [GET_EFFECTIVE]
    [GET_TAG] --> [GET_EFFECTIVE]
    [GET_EFFECTIVE] --> [FINAL_PATH] ["get_binary_path()"]
    
    style [FINAL_PATH] stroke-width:2px
    style [GET_STEALTH] stroke-width:2px
```

Sources: [[cloakbrowser/config.py:107-183]](), [[cloakbrowser/config.py:220-244]]()

---

# Page: Python Binary Management

# Python Binary Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/download.py](cloakbrowser/download.py)
- [dotnet/src/CloakBrowser/Download.cs](dotnet/src/CloakBrowser/Download.cs)
- [js/src/download.ts](js/src/download.ts)
- [js/tests/update.test.ts](js/tests/update.test.ts)
- [tests/test_extract.py](tests/test_extract.py)
- [tests/test_update.py](tests/test_update.py)

</details>



This page documents `cloakbrowser/download.py`, which is responsible for resolving, downloading, extracting, and caching the patched Chromium binary used by the Python package. It also covers the priority resolution between Free and Pro tiers, background auto-update system, SHA-256 checksum verification, Ed25519 signature verification, and the public utility functions `check_for_update()`, `clear_cache()`, and `binary_info()`.

For the configuration values that `download.py` depends on (cache paths, version strings, platform detection, download URLs), see the [Python Configuration Module](3.2). For the public `launch()` API that calls `ensure_binary()` on each invocation, see the [Python API Reference](3.1).

---

## Module Constants

Module-level constants govern timing and network behavior:

| Constant | Value | Purpose |
|---|---|---|
| `DOWNLOAD_TIMEOUT` | `httpx.Timeout` | 10-minute timeout for large binary downloads. [cloakbrowser/download.py:64-64]() |
| `UPDATE_CHECK_INTERVAL` | `3600` seconds | Minimum gap between background update checks (1 hour). [cloakbrowser/download.py:67-67]() |
| `WELCOME_FREE_INTERVAL` | `86400` seconds | Interval (1 day) for re-showing the Pro upsell banner to free users. [cloakbrowser/download.py:72-72]() |
| `PRO_MAJOR` | `"150"` | Major version indicator for the Pro tier shown in banners. [cloakbrowser/download.py:77-77]() |

Sources: [cloakbrowser/download.py:63-77]()

---

## `ensure_binary()` — Binary Resolution Flow

`ensure_binary()` is the primary entry point. It is called by `launch()` and `launch_async()` before starting the browser. It returns a string path to the `chrome` executable, downloading it first if necessary. [cloakbrowser/download.py:166-173]()

**Binary Resolution Priority (in order):**

1.  **Local override** — If `CLOAKBROWSER_BINARY_PATH` is set via `get_local_binary_override()`, return that path immediately (or raise `FileNotFoundError` if it does not exist on disk). [cloakbrowser/download.py:183-191]()
2.  **Pro Tier Resolution** — If a license key is resolved via `resolve_license_key()`, validate it via `validate_license()`. If valid, call `_ensure_pro_binary()`. This handles Pro-specific downloads and verification. [cloakbrowser/download.py:198-216]()
3.  **Platform check** — Call `check_platform_available()` to fail fast on unsupported platforms. [cloakbrowser/download.py:230-230]()
4.  **Effective version** — Call `get_effective_version()` to determine whether an auto-updated binary is available via the `latest_version` marker. [cloakbrowser/download.py:256-257]()
5.  **Hardcoded fallback** — If the effective-version binary does not exist, check whether the hardcoded `CHROMIUM_VERSION` binary is already cached. [cloakbrowser/download.py:266-273]()
6.  **Download** — If no cached binary is found, download the version by calling `_download_and_extract()`. [cloakbrowser/download.py:279-279]()
7.  **Background update check** — After resolving a binary, call `_maybe_trigger_update_check()` to schedule a background update thread. [cloakbrowser/download.py:291-291]()

**Binary Resolution Flow Diagram**

```mermaid
graph TD
    A["ensure_binary()"] --> B{"get_local_binary_override()\nenv: CLOAKBROWSER_BINARY_PATH set?"}
    B -- "Yes" --> C{"Path.exists()"}
    C -- "No" --> D["raise FileNotFoundError"]
    C -- "Yes" --> E["return str(path)"]

    B -- "No" --> F{"resolve_license_key()\nValid Pro Key?"}
    F -- "Yes" --> G["_ensure_pro_binary()"]
    G -- "Success" --> H["return pro_path"]
    G -- "Auth Fail" --> I["raise BinaryVerificationError"]
    G -- "Transient Fail" --> J["raise RuntimeError"]

    F -- "No" --> K["check_platform_available()"]
    K --> L["get_effective_version()"]
    L --> M{"binary_path.exists()\nand _is_executable()?"}

    M -- "Yes" --> N["_maybe_trigger_update_check()\nreturn str(binary_path)"]

    M -- "No" --> O{"effective != platform_version?\nCheck fallback path"}
    O -- "Fallback exists" --> N
    O -- "No fallback" --> P["_download_and_extract()"]
    P --> Q{"binary_path.exists()?"}
    Q -- "No" --> R["raise RuntimeError"]
    Q -- "Yes" --> N
```

Sources: [cloakbrowser/download.py:166-292]()

---

## Download and Extraction

### `_download_and_extract(version)`

This function orchestrates the full download-and-extract cycle for a given version. It uses a **temporary file** to ensure atomicity: the archive is downloaded to a `tempfile.NamedTemporaryFile` before extraction begins. [cloakbrowser/download.py:335-337]()

Steps:
1.  Resolve URLs via `get_download_url(version)` (primary) and `get_fallback_download_url(version)`. [cloakbrowser/download.py:326-327]()
2.  Create a named temp file. [cloakbrowser/download.py:335-336]()
3.  Call `_download_file()`. It tries the primary URL first; if it fails, it tries the fallback URL. [cloakbrowser/download.py:340-349]()
4.  Verify SHA-256 checksum via `_verify_download_checksum()` unless `CLOAKBROWSER_SKIP_CHECKSUM` is true. [cloakbrowser/download.py:352-353]()
5.  Call `_extract_archive()`. [cloakbrowser/download.py:355-355]()
6.  Delete the temp file in a `finally` block. [cloakbrowser/download.py:359-359]()

Sources: [cloakbrowser/download.py:319-360]()

### Security Verification

The system employs two layers of verification to prevent tampering:

1.  **SHA-256 Checksum**: Integrity verification via `SHA256SUMS` files. [cloakbrowser/download.py:362-430]()
    *   **`_fetch_checksums(version)`**: Fetches the checksum file from the primary or fallback server. [cloakbrowser/download.py:379-398]()
    *   **`_verify_checksum(file_path, expected_hash)`**: Computes the SHA-256 hash in 64KB chunks. [cloakbrowser/download.py:418-430]()
2.  **Ed25519 Signature (Pro Only)**: Pro binaries use a signed manifest for authenticity. [cloakbrowser/download.py:767-791]()
    *   **`_verify_signature(data, signature)`**: Uses `cryptography` to verify the manifest against pinned `BINARY_SIGNING_PUBKEYS`. [cloakbrowser/download.py:767-791]()
    *   **`_verify_pro_download(binary_path, manifest)`**: Ensures the downloaded binary matches the hash specified in the signed manifest. [cloakbrowser/download.py:749-764]()

Sources: [cloakbrowser/download.py:362-430](), [cloakbrowser/download.py:749-791]()

### Extraction and Post-Processing

`_extract_archive(archive_path, dest_dir, binary_path)` handles extraction via `tarfile` or `zipfile`. [cloakbrowser/download.py:444-446]()

| Behavior | Detail |
|---|---|
| **Path-traversal filter** | Members with absolute paths or `..` raise `RuntimeError`. [cloakbrowser/download.py:506-516]() |
| **Symlink safety** | Absolute symlink targets are skipped to prevent out-of-bounds writes. [cloakbrowser/download.py:519-525]() |
| **Directory flattening** | `_flatten_single_subdir()` moves contents up if the archive contains a single root folder. [cloakbrowser/download.py:563-581]() |
| **macOS Quarantine** | Runs `xattr -cr` on macOS to remove the `com.apple.quarantine` attribute. [cloakbrowser/download.py:606-613]() |

Sources: [cloakbrowser/download.py:433-613]()

---

## Auto-Update System

### Background Daemon Thread

`_maybe_trigger_update_check()` starts a daemon thread running `_check_and_download_update()`. This ensures the main application is not blocked by network I/O. [cloakbrowser/download.py:717-726]()

### Rate Limiting and Guards

The system uses a `.last_update_check` file in the cache directory to store a Unix timestamp. [cloakbrowser/download.py:729-743]()

The check is skipped if:
*   `CLOAKBROWSER_AUTO_UPDATE=false`. [cloakbrowser/download.py:731-732]()
*   `CLOAKBROWSER_BINARY_PATH` is set. [cloakbrowser/download.py:734-735]()
*   The 1-hour `UPDATE_CHECK_INTERVAL` has not passed. [cloakbrowser/download.py:740-743]()

**Background Update Sequence Diagram**

```mermaid
sequenceDiagram
    participant EB as "ensure_binary()"
    participant MTUC as "_maybe_trigger_update_check()"
    participant Thread as "Daemon Thread"
    participant API as "GitHub/Pro API"
    participant DAE as "_download_and_extract()"
    participant WVM as "_write_version_marker()"

    EB->>MTUC: resolve binary
    MTUC->>Thread: threading.Thread(daemon=True).start()
    
    Thread->>API: _get_latest_chromium_version()
    API-->>Thread: version_string
    
    alt "Newer version available"
        Thread->>DAE: download_and_extract(version)
        Thread->>WVM: write latest_version marker
    end
```

Sources: [cloakbrowser/download.py:695-746]()

---

## Public Utility Functions

### `check_for_update()`
Synchronously checks for and downloads a newer Chromium version. Returns the new version string if updated, else `None`. [cloakbrowser/download.py:673-692]()

### `clear_cache()`
Removes the entire `get_cache_dir()` using `shutil.rmtree`. [cloakbrowser/download.py:643-651]()

### `binary_info()`
Returns a dictionary containing the current `version`, `tier` (Free/Pro), `platform`, `binary_path`, and `installed` status. [cloakbrowser/download.py:654-666]()

Sources: [cloakbrowser/download.py:643-692]()

---

# Page: JavaScript Package

# JavaScript Package

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/__init__.py](cloakbrowser/__init__.py)
- [cloakbrowser/_version.py](cloakbrowser/_version.py)
- [js/README.md](js/README.md)
- [js/package.json](js/package.json)
- [js/src/index.ts](js/src/index.ts)
- [js/src/types.ts](js/src/types.ts)
- [js/tests/launch.test.ts](js/tests/launch.test.ts)

</details>



This page covers the structure, module format, export paths, dependencies, and build configuration of the `cloakbrowser` npm package located in the `js/` subdirectory of the repository. It is a structural overview intended to orient developers to how the package is laid out.

- For the **Playwright API reference** (functions like `launch()`, `launchContext()`), see [JavaScript Playwright API](#4.1).
- For the **Puppeteer API reference**, see [JavaScript Puppeteer API](#4.2).
- For the **configuration module** (`src/config.ts`), see [JavaScript Configuration Module](#4.3).
- For **binary download and management** (`src/download.ts`), see [JavaScript Binary Management](#4.4).

---

## Package Identity

The package is published to npm under the name `cloakbrowser`. Its manifest is at [js/package.json:1-97]().

| Field | Value |
|---|---|
| `name` | `cloakbrowser` [js/package.json:2]() |
| `version` | `0.5.7` [js/package.json:3]() |
| `license` | MIT [js/package.json:50]() |
| `type` | `module` (ESM) [js/package.json:5]() |
| Node.js requirement | `>=20.0.0` [js/package.json:58]() |
| Repository subdirectory | `js/` [js/package.json:54]() |

The `"type": "module"` declaration means all `.js` files in the package are treated as ES Modules. There is no CommonJS build. The version `0.5.7` is synchronized with the Python package version [cloakbrowser/_version.py:1]().

Sources: [js/package.json:1-59](), [cloakbrowser/_version.py:1]()

---

## Module Format and Build Output

The package is written in TypeScript and compiled with `tsc`. Source files live under `js/src/`, and the compiler emits into `js/dist/`. Only the `dist/` directory is included in the published package [js/package.json:25-27]().

The build script is `tsc`, invoked via `npm run build` [js/package.json:93]() or `npm run typecheck` for validation [js/package.json:94](). The package targets Node.js environments supporting ESM.

Sources: [js/package.json:92-96]()

---

## Export Paths

The package defines three named export conditions in the `"exports"` field [js/package.json:8-21]():

**Package export map:**

```mermaid
graph TD
    subgraph "npm_package:[cloakbrowser]"
        ExportRoot["\".\"<br/>(default export)"]
        ExportPuppeteer["\"./puppeteer\"<br/>(subpath export)"]
        ExportHuman["\"./human\"<br/>(subpath export)"]
        CLIBin["\"bin\": \"cloakbrowser\""]
    end

    subgraph "dist_output:[dist/]"
        IndexJS["dist/index.js"]
        IndexDTS["dist/index.d.ts"]
        PuppeteerJS["dist/puppeteer.js"]
        PuppeteerDTS["dist/puppeteer.d.ts"]
        HumanIndexJS["dist/human/index.js"]
        CLIJS["dist/cli.js"]
    end

    subgraph "src_source:[src/]"
        SrcIndex["src/index.ts"]
        SrcPuppeteer["src/puppeteer.ts"]
        SrcPlaywright["src/playwright.ts"]
        SrcDownload["src/download.ts"]
        SrcConfig["src/config.ts"]
        SrcTypes["src/types.ts"]
        SrcHuman["src/human/index.ts"]
    end

    ExportRoot -->|"import"| IndexJS
    ExportRoot -->|"types"| IndexDTS
    ExportPuppeteer -->|"import"| PuppeteerJS
    ExportPuppeteer -->|"types"| PuppeteerDTS
    ExportHuman -->|"import"| HumanIndexJS
    CLIBin --> CLIJS

    IndexJS --> SrcIndex
    PuppeteerJS --> SrcPuppeteer
    SrcIndex --> SrcPlaywright
    SrcIndex --> SrcDownload
    SrcIndex --> SrcConfig
    SrcIndex --> SrcTypes
    HumanIndexJS --> SrcHuman
```

Sources: [js/package.json:8-24](), [js/src/index.ts:18-33]()

### Default export (`.`)

Importing from `'cloakbrowser'` resolves to `dist/index.js`, which re-exports from the Playwright integration. The entry point is `js/src/index.ts`, which aggregates:

| Export Category | Source module |
|---|---|
| Playwright Launchers | `src/playwright.ts` [js/src/index.ts:19]() |
| Binary Lifecycle | `src/download.ts` [js/src/index.ts:22]() |
| Constants & Stealth | `src/config.ts` [js/src/index.ts:25]() |
| Licensing | `src/license.ts` [js/src/index.ts:28]() |
| Type Definitions | `src/types.ts` [js/src/index.ts:31]() |

### Puppeteer subpath (`./puppeteer`)

Importing from `'cloakbrowser/puppeteer'` resolves to `dist/puppeteer.js`, which exposes the Puppeteer-based `launch()` function. This is a separate entry point because Puppeteer's API and behavior differ from Playwright's (notably around proxy credential injection). See [JavaScript Puppeteer API](#4.2) for details.

Sources: [js/package.json:13-16]()

---

## Source File Layout

**Diagram: Source modules and their roles**

```mermaid
graph LR
    subgraph "src_directory:[js/src/]"
        index["index.ts<br/>(Playwright entry)"]
        puppeteer_ts["puppeteer.ts<br/>(Puppeteer entry)"]
        playwright_ts["playwright.ts<br/>launch() / launchContext()"]
        download_ts["download.ts<br/>ensureBinary() / clearCache()"]
        config_ts["config.ts<br/>CHROMIUM_VERSION<br/>getDefaultStealthArgs()"]
        types_ts["types.ts<br/>LaunchOptions<br/>BinaryInfo"]
        human_dir["human/<br/>(Behavioral Layer)"]
        license_ts["license.ts<br/>validateLicense()"]
    end

    index --> playwright_ts
    index --> download_ts
    index --> config_ts
    index --> types_ts
    index --> license_ts

    puppeteer_ts --> download_ts
    puppeteer_ts --> config_ts

    playwright_ts --> download_ts
    playwright_ts --> config_ts
    playwright_ts --> human_dir
```

| File | Responsibility |
|---|---|
| `src/index.ts` | Default (Playwright) export aggregator [js/src/index.ts:1-33]() |
| `src/puppeteer.ts` | Puppeteer-specific entry point [js/package.json:13-16]() |
| `src/playwright.ts` | Playwright `launch()` implementations and option builders [js/src/index.ts:19]() |
| `src/download.ts` | Binary lifecycle: download, extract, cache, update [js/src/index.ts:22]() |
| `src/config.ts` | Constants and platform-specific configuration [js/src/index.ts:25]() |
| `src/types.ts` | Shared TypeScript type definitions [js/src/types.ts:1-84]() |
| `src/license.ts` | Pro license validation logic [js/src/index.ts:28]() |
| `src/human/` | Humanize behavioral layer for mouse/keyboard simulation [js/package.json:17-20]() |

Sources: [js/package.json:8-21](), [js/src/index.ts:18-33]()

---

## Dependencies

### Runtime dependency

| Package | Version constraint | Purpose |
|---|---|---|
| `tar` | `^7.0.0` | Extracts the downloaded `.tar.gz` binary archive [js/package.json:81]() |

`tar` is the mandatory runtime dependency used for binary extraction across all supported platforms.

Sources: [js/package.json:80-82]()

### Peer dependencies (optional)

Automation frameworks and GeoIP libraries are declared as **optional** peer dependencies [js/package.json:60-79]().

| Peer dependency | Minimum version | Optional |
|---|---|---|
| `playwright-core` | `>=1.53.0` | Yes [js/package.json:67-69]() |
| `puppeteer-core` | `>=21.0.0` | Yes [js/package.json:70-72]() |
| `mmdb-lib` | `>=2.0.0` | Yes [js/package.json:73-75]() |
| `socks-proxy-agent`| `>=10.0.0` | Yes [js/package.json:76-78]() |

The `peerDependenciesMeta` block marks these as `optional: true`, suppressing package manager warnings when only one is installed. A missing peer dependency only throws an error if the corresponding `launch()` function is called.

Sources: [js/package.json:60-79]()

### Dev dependencies

| Package | Purpose |
|---|---|
| `typescript` | TypeScript compiler [js/package.json:89]() |
| `@types/node` | Node.js type declarations [js/package.json:84]() |
| `playwright-core` | Used in tests and development [js/package.json:86]() |
| `puppeteer-core` | Used in tests and development [js/package.json:87]() |
| `vitest` | Test runner [js/package.json:90]() |

Sources: [js/package.json:83-91]()

---

## npm Scripts

| Script | Command | Purpose |
|---|---|---|
| `build` | `tsc` | Compile TypeScript to `dist/` [js/package.json:93]() |
| `typecheck` | `tsc --noEmit` | Type-check without emitting files [js/package.json:94]() |
| `test` | `vitest run` | Run the test suite [js/package.json:95]() |

Sources: [js/package.json:92-96]()

---

## Published Files

Only the `dist/` directory is included in the npm tarball [js/package.json:25-27](). The `dist/` directory contains:

- Compiled `.js` files (ESM)
- `.d.ts` type declaration files for full TypeScript support [js/package.json:7]()
- CLI entry point `dist/cli.js` mapped to the `cloakbrowser` command [js/package.json:22-24]()

Sources: [js/package.json:22-27]()

---

# Page: JavaScript Playwright API

# JavaScript Playwright API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/__init__.py](cloakbrowser/__init__.py)
- [cloakbrowser/browser.py](cloakbrowser/browser.py)
- [cloakbrowser/human/__init__.py](cloakbrowser/human/__init__.py)
- [js/src/human/index.ts](js/src/human/index.ts)
- [js/src/index.ts](js/src/index.ts)
- [js/src/playwright.ts](js/src/playwright.ts)
- [js/src/puppeteer.ts](js/src/puppeteer.ts)
- [js/src/types.ts](js/src/types.ts)
- [js/tests/launch.test.ts](js/tests/launch.test.ts)

</details>



This page covers the default `cloakbrowser` npm export, which uses `playwright-core` as its automation backend. It documents every exported function, type, and constant available when you import from `'cloakbrowser'`.

For the Puppeteer export path, see [4.2](). For the underlying binary download and caching logic, see [4.4](). For configuration constants and stealth argument generation, see [4.3]().

---

## Module Entry Point

All Playwright-facing symbols are re-exported from [js/src/index.ts:1-33]() in five groups:

| Export group | Source file | Symbols |
|---|---|---|
| Launch functions | `src/playwright.ts` | `launch`, `launchContext`, `launchPersistentContext`, `buildLaunchOptions`, `buildContextOptions`, `humanizeBrowser` |
| Binary management | `src/download.ts` | `ensureBinary`, `clearCache`, `binaryInfo`, `checkForUpdate` |
| Configuration | `src/config.ts` | `CHROMIUM_VERSION`, `getDefaultStealthArgs` |
| License | `src/license.ts` | `validateLicense`, `CloakBrowserLicenseError` |
| Types | `src/types.ts` | `LaunchOptions`, `LaunchContextOptions`, `LaunchPersistentContextOptions`, `BinaryInfo` |

**Export map diagram**

```mermaid
graph TD
    User["\"import from 'cloakbrowser'\""]
    index["\"src/index.ts\""]
    playwright["\"src/playwright.ts\""]
    download["\"src/download.ts\""]
    config["\"src/config.ts\""]
    license["\"src/license.ts\""]
    types["\"src/types.ts\""]

    User --> index
    index -->|"launch, launchContext, launchPersistentContext, buildLaunchOptions, buildContextOptions, humanizeBrowser"| playwright
    index -->|"ensureBinary, clearCache, binaryInfo, checkForUpdate"| download
    index -->|"CHROMIUM_VERSION, getDefaultStealthArgs"| config
    index -->|"validateLicense, CloakBrowserLicenseError"| license
    index -->|"LaunchOptions, LaunchContextOptions, LaunchPersistentContextOptions, BinaryInfo"| types
```

Sources: [js/src/index.ts:1-33](), [js/src/playwright.ts:1-20]()

---

## Types

### `LaunchOptions`
Base options for launching a browser instance [js/src/types.ts:8-44]().

| Property | Type | Default | Description |
|---|---|---|---|
| `headless` | `boolean` | `true` | Runs Chromium without a visible window [js/src/types.ts:9-10](). |
| `proxy` | `string \| object` | — | Proxy URL string or Playwright proxy object [js/src/types.ts:17](). |
| `args` | `string[]` | — | Additional Chromium CLI arguments [js/src/types.ts:19](). |
| `stealthArgs` | `boolean` | `true` | When `false`, suppresses default `--fingerprint-*` flags [js/src/types.ts:22-23](). |
| `timezone` | `string` | — | IANA timezone (e.g., "America/New_York"). Sets `--fingerprint-timezone` [js/src/types.ts:24-25](). |
| `locale` | `string` | — | BCP 47 locale (e.g., "en-US"). Sets `--lang` binary flag [js/src/types.ts:26-27](). |
| `geoip` | `boolean` | — | Auto-detect timezone/locale from proxy IP (requires `mmdb-lib`) [js/src/types.ts:28-29](). |
| `humanize` | `boolean` | — | Enables human-like mouse/keyboard behavioral layer [js/src/types.ts:38-39](). |
| `humanPreset` | `'default' \| 'careful'` | — | Behavioral preset for humanize layer [js/src/types.ts:40-41](). |
| `humanConfig` | `Partial<HumanConfig>` | — | Override individual human behavior parameters [js/src/types.ts:42-43](). |
| `licenseKey` | `string` | — | Pro license key for v150+ binaries [js/src/types.ts:30-31](). |
| `browserVersion`| `string` | — | Exact Chromium version pin [js/src/types.ts:32-33](). |
| `launchOptions` | `Record<string, unknown>` | — | Raw options passed to `chromium.launch()` [js/src/types.ts:36-37](). |

### `LaunchContextOptions`
Extends `LaunchOptions` for ephemeral contexts [js/src/types.ts:46-66]().

| Property | Type | Description |
|---|---|---|
| `userAgent` | `string` | Custom User-Agent string [js/src/types.ts:47-48](). |
| `viewport` | `object \| null` | Viewport dimensions. Set `null` to disable emulation [js/src/types.ts:49-50](). |
| `colorScheme` | `string` | 'light', 'dark', or 'no-preference' [js/src/types.ts:55-56](). |
| `timezoneId` | `string` | Alias for `timezone`. Resolved via `resolveTimezone()` [js/src/types.ts:53-54](). |
| `contextOptions` | `BrowserContextOptions` | Extra options forwarded to `browser.newContext()`. `locale` and `timezoneId` are stripped here to avoid CDP detection [js/src/types.ts:61-65](). |

### `LaunchPersistentContextOptions`
Extends `LaunchContextOptions` for persistent profiles [js/src/types.ts:68-71]().

| Property | Type | Description |
|---|---|---|
| `userDataDir` | `string` | **Required.** Path to the user profile directory [js/src/types.ts:69-70](). |

### `BinaryInfo`
Metadata about the local stealth binary [js/src/types.ts:73-83](). Includes `version`, `bundledVersion`, `platform`, `tier` ("pro" or "free"), `binaryPath`, `installed` status, `cacheDir`, and `downloadUrl`.

Sources: [js/src/types.ts:1-83](), [js/src/playwright.ts:28-58]()

---

## Launch Functions

### `launch(options?)`
**Signature:** `async function launch(options: LaunchOptions = {}): Promise<Browser>`

Launches the stealth Chromium browser via `playwright-core` [js/src/playwright.ts:194-222]().

1. **Options Processing**: Uses `buildLaunchOptions()` to resolve the binary path, GeoIP data, and proxy settings [js/src/playwright.ts:200]().
2. **Execution**: Calls `chromium.launch()` with generated arguments [js/src/playwright.ts:200](). It catches license errors and rethrows them as `CloakBrowserLicenseError` [js/src/playwright.ts:202-203]().
3. **Viewport Patch**: For headed launches, it patches `newContext` and `newPage` to default to `noViewport: true`, preventing the "impossible window" tell (outerWidth < innerWidth) [js/src/playwright.ts:206-212]().
4. **Humanize**: If `humanize: true`, the returned `Browser` is patched via `humanizeBrowser()` [js/src/playwright.ts:214]().

### `launchContext(options?)`
**Signature:** `async function launchContext(options: LaunchContextOptions = {}): Promise<BrowserContext>`

Creates a browser and an ephemeral context in one call [js/src/playwright.ts:241-286]().

*   **Native Stealth**: Calls `filterStealthCtxOptions()` to strip `locale` and `timezoneId` from `contextOptions`. These are instead passed as binary flags to avoid detectable CDP emulation [js/src/playwright.ts:42-58](), [js/src/playwright.ts:256]().
*   **Close Patching**: The `context.close()` method is patched to also call `browser.close()`, ensuring the browser process is reaped when the context is closed [js/src/playwright.ts:267-271]().
*   **Default Viewport**: Applies `DEFAULT_VIEWPORT` if no viewport is provided and the binary version requires it for headless coherence [js/src/playwright.ts:98-103]().

### `launchPersistentContext(options)`
**Signature:** `async function launchPersistentContext(options: LaunchPersistentContextOptions): Promise<BrowserContext>`

Launches a non-incognito session with a disk-based profile using `chromium.launchPersistentContext()` [js/src/playwright.ts:305-357]().

Sources: [js/src/playwright.ts:194-357](), [js/src/types.ts:46-71]()

---

## Internal Logic & Helpers

### `buildLaunchOptions(options)`
**Signature:** `async function buildLaunchOptions(options: LaunchOptions = {}): Promise<PlaywrightLaunchOptions>`

Constructs the final object passed to Playwright's `launch()` [js/src/playwright.ts:120-161](). It resolves the binary path via `ensureBinary()` [js/src/playwright.ts:126-130](), parses proxies via `resolveProxyConfig()` [js/src/playwright.ts:132-137](), and merges CLI arguments via `buildArgs()` [js/src/playwright.ts:140]().

### `buildContextOptions(options)`
**Signature:** `export function buildContextOptions(options: LaunchContextOptions = {}): BrowserContextOptions`

Resolves context-level settings, specifically managing viewport logic [js/src/playwright.ts:83-112]().
*   **Headed**: Sets `viewport: null` so the page tracks the real window [js/src/playwright.ts:103]().
*   **Headless**: Uses `DEFAULT_VIEWPORT` (1280x720) unless the binary is new enough to support `headlessNoViewport` [js/src/playwright.ts:98-103]().

### Proxy URL Parsing
The system uses `parseProxyUrl()` and `resolveProxyConfig()` to handle authentication.
*   **SOCKS5**: Credentials are auto-encoded into the URL via `normalizeSocksStringUrl()` to prevent truncation [js/src/proxy.ts:106-158]().
*   **HTTP**: On newer binaries, inline credentials (`user:pass@host`) are passed via `--proxy-server` [js/src/proxy.ts:168-174](). On older binaries, credentials are stripped and injected via `page.authenticate()` [js/src/puppeteer.ts:124-137]().

### Timezone Resolution (`resolveTimezone`)
A helper that aliases `timezoneId` to `timezone` to support various API naming conventions without warnings [js/src/playwright.ts:28-35]().

---

## Code Entity Map

The diagram below maps high-level user-facing concepts to the exact code entities that implement them.

```mermaid
graph LR
    subgraph "User API"
        UC1["\"launch()\""]
        UC2["\"launchContext()\""]
        UC3["\"launchPersistentContext()\""]
    end

    subgraph "src/playwright.ts"
        PL1["\"launch()\""]
        PL2["\"launchContext()\""]
        PL3["\"launchPersistentContext()\""]
        PL4["\"resolveTimezone()\""]
        PL5["\"buildLaunchOptions()\""]
        PL6["\"buildContextOptions()\""]
        PL7["\"effectiveHeadless()\""]
    end

    subgraph "src/proxy.ts"
        PR1["\"resolveProxyConfig()\""]
        PR2["\"parseProxyUrl()\""]
    end

    subgraph "src/human/index.ts"
        HU1["\"patchBrowser()\""]
        HU2["\"patchContext()\""]
    end

    subgraph "playwright-core"
        PW1["\"chromium.launch()\""]
        PW2["\"browser.newContext()\""]
        PW3["\"chromium.launchPersistentContext()\""]
    end

    UC1 --> PL1
    UC2 --> PL2
    UC3 --> PL3

    PL1 --> PL5
    PL5 --> PW1
    PL5 --> PR1
    PR1 --> PR2
    PL1 --> HU1

    PL2 --> PL4
    PL2 --> PL1
    PL2 --> PL6
    PL6 --> PL7
    PL6 --> PW2
    PL2 --> HU2
    
    PL3 --> PL4
    PL3 --> PW3
    PL3 --> PR1
    PL3 --> HU2
```

Sources: [js/src/playwright.ts:1-357](), [js/src/proxy.ts:1-180](), [js/src/index.ts:1-33]()

---

## Behavioral Layer (Humanize)

When `humanize: true` is passed, the package activates the behavioral stealth layer.

*   **Data Flow**: Functions import `patchBrowser` or `patchContext` and `resolveConfig` dynamically to minimize startup overhead [js/src/playwright.ts:172-173](), [js/src/playwright.ts:278-279]().
*   **Configuration**: The `humanPreset` and `humanConfig` are merged into a final configuration object via `resolveConfig()` [js/src/playwright.ts:174-177]().
*   **Patching**: 
    *   `launch()` calls `humanizeBrowser()` which calls `patchBrowser()` [js/src/playwright.ts:178]().
    *   `launchContext()` and `launchPersistentContext()` call `patchContext()` [js/src/playwright.ts:283](), [js/src/playwright.ts:353]().
*   **Cursor Tracking**: The system maintains a `CursorState` instance per-page to track `x` and `y` coordinates for Bézier curve calculations [js/src/human/index.ts:148-152]().

Sources: [js/src/playwright.ts:166-179](), [js/src/playwright.ts:277-284](), [js/src/playwright.ts:347-355](), [js/src/human/index.ts:1-152]()

---

# Page: JavaScript Puppeteer API

# JavaScript Puppeteer API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [js/src/human-puppeteer/index.ts](js/src/human-puppeteer/index.ts)
- [js/src/proxy.ts](js/src/proxy.ts)
- [js/tests/proxy.test.ts](js/tests/proxy.test.ts)
- [js/tests/puppeteer.test.ts](js/tests/puppeteer.test.ts)
- [js/tests/stealth.puppeteer.test.ts](js/tests/stealth.puppeteer.test.ts)
- [js/tests/stealth.test.ts](js/tests/stealth.test.ts)
- [tests/test_proxy.py](tests/test_proxy.py)
- [tests/test_stealth_unit.py](tests/test_stealth_unit.py)

</details>



This page documents the `cloakbrowser/puppeteer` subpath export: its exported functions `launch()` and `launchPersistentContext()`, how it configures the stealth binary for Puppeteer, and the specific mechanisms used for proxy credential injection. It also documents the known reCAPTCHA Enterprise limitation inherent to Puppeteer's CDP protocol and the human-like behavioral patching support.

For the default (Playwright) export, see [JavaScript Playwright API](). For shared configuration and binary management functions, see [JavaScript Configuration Module]() and [JavaScript Binary Management]().

---

## Import Path

The Puppeteer API is exposed on the `cloakbrowser/puppeteer` package subpath, distinct from the default `cloakbrowser` Playwright export.

```js
import { launch, launchPersistentContext } from 'cloakbrowser/puppeteer';
```

The source entry point is [js/src/puppeteer.ts:1-197]().

`puppeteer-core` is a peer dependency and is **not** statically imported at module load time. Instead, it is dynamically imported inside the launch functions at call time [js/src/puppeteer.ts:182](), [js/src/puppeteer.ts:219](), so the module loads without error even if `puppeteer-core` is absent.

---

## Exported API

The Puppeteer subpath exports two primary functions:

| Export | Type | Description |
|--------|------|-------------|
| `launch` | `(options?: LaunchOptions) => Promise<Browser>` | Launch the stealth Chromium browser via Puppeteer [js/src/puppeteer.ts:181]() |
| `launchPersistentContext` | `(options: LaunchOptions & { userDataDir: string }) => Promise<Browser>` | Launch with a persistent user profile directory [js/src/puppeteer.ts:217]() |

There is no `launchContext()`, `ensureBinary()`, `clearCache()`, `binaryInfo()`, or `checkForUpdate()` on this subpath. Those utilities are available on the default Playwright export (see [JavaScript Playwright API]()).

---

## Launch Sequence

**Title: `launch()` call sequence in puppeteer.ts**

```mermaid
sequenceDiagram
    participant Caller as "Caller"
    participant launch as "launch() [puppeteer.ts]"
    participant puppeteerCore as "puppeteer-core (dynamic import)"
    participant ensureBinary as "ensureBinary() [download.ts]"
    participant buildArgs as "buildArgs() [args.ts]"
    participant maybeResolveGeoip as "maybeResolveGeoip() [geoip.ts]"
    participant humanPatch as "patchBrowser() [human-puppeteer/index.ts]"

    Caller->>launch: "launch(options)"
    launch->>puppeteerCore: "import('puppeteer-core')"
    launch->>ensureBinary: "ensureBinary()"
    ensureBinary-->>launch: "binaryPath"
    launch->>maybeResolveGeoip: "maybeResolveGeoip(options)"
    maybeResolveGeoip-->>launch: "resolved (tz/locale/exitIp)"
    launch->>buildArgs: "buildArgs({ ...options, ...resolved })"
    buildArgs-->>launch: "args[]"
    
    launch->>puppeteerCore: "puppeteer.default.launch({ executablePath, headless, args })"
    puppeteerCore-->>launch: "browser (Browser)"
    
    alt "proxyAuth credentials present"
        launch->>launch: "applyPostLaunch() -> monkey-patch browser.newPage()"
    end

    alt "options.humanize === true"
        launch->>humanPatch: "patchBrowser(browser, cfg)"
    end
    
    launch-->>Caller: "browser"
```

Sources: [js/src/puppeteer.ts:181-215](), [js/src/puppeteer.ts:63-78](), [js/src/puppeteer.ts:141-165](), [js/src/download.ts:11-40](), [js/src/geoip.ts:17-17]()

---

## Arguments Construction

The launch functions use an internal `resolveArgs()` helper [js/src/puppeteer.ts:63]() to assemble the Chromium CLI argument list via `buildArgs()` [js/src/puppeteer.ts:75](). This includes:

1. **Stealth Flags**: If `options.stealthArgs` is not `false`, it includes all `--fingerprint-*` flags generated by `getDefaultStealthArgs()` [js/tests/puppeteer.test.ts:64-71]().
2. **GeoIP Flags**: If `geoip: true` is set, `maybeResolveGeoip` [js/src/puppeteer.ts:71]() resolves the proxy's location and appends `--fingerprint-timezone` and `--lang` (locale) flags to the `args` array.
3. **WebRTC Spoofing**: If an `exitIp` is resolved from the proxy, it appends `--fingerprint-webrtc-ip=${exitIp}` [js/src/puppeteer.ts:74]().
4. **Automation Suppression**: The `ignoreDefaultArgs` parameter is set to `IGNORE_DEFAULT_ARGS` [js/src/puppeteer.ts:200](), which removes the `--enable-automation` flag that typically triggers "Chrome is being controlled by automated test software" banners.

---

## Proxy Handling

Puppeteer's underlying Chromium implementation for `--proxy-server` does not support inline credentials for HTTP proxies on all platforms. The Puppeteer wrapper handles this by detecting platform support via `binarySupportsHttpProxyInlineAuth()` [js/src/puppeteer.ts:103]().

**Title: Proxy credential flow in puppeteer.ts**

```mermaid
flowchart TD
    A["options.proxy provided?"]
    A -->|"No"| Z["No proxy args added"]
    A -->|"Yes"| B{"isSocksProxy?"}
    B -->|"Yes"| C["args.push(...resolveProxyConfig)"]
    B -->|"No"| D{"binarySupportsHttpProxyInlineAuth()?"}
    D -->|"Yes"| E["args.push(--proxy-server=URL_with_creds)"]
    D -->|"No"| F["parseProxyUrl(options.proxy)"]
    F --> G["args.push(--proxy-server=server_only)"]
    G --> H["Store proxyAuth = { username, password }"]
    H --> I["Launch browser"]
    I --> J{"proxyAuth set?"}
    J -->|"Yes"| K["Monkey-patch browser.newPage()"]
    K --> L["Each call: origNewPage() then page.authenticate(proxyAuth)"]
    L --> M["Return Browser"]
    J -->|"No"| M
```

Sources: [js/src/puppeteer.ts:87-138](), [js/src/puppeteer.ts:146-154](), [js/src/proxy.ts:42-46](), [js/tests/puppeteer.test.ts:147-167]()

### `newPage()` Monkey-Patch

If `proxyAuth` is detected (due to an unsupported platform or version for inline HTTP auth), the `browser.newPage` method is intercepted during `applyPostLaunch` [js/src/puppeteer.ts:146](). 

```typescript
if (proxyAuth) {
  const origNewPage = browser.newPage.bind(browser);
  const auth = proxyAuth;
  browser.newPage = async (...pageArgs: Parameters<typeof origNewPage>) => {
    const page = await origNewPage(...pageArgs);
    await page.authenticate(auth);
    return page;
  };
}
```
[js/src/puppeteer.ts:146-154]()

---

## Humanize Behavioral Layer

If `humanize: true` is passed, the browser is patched using the Puppeteer-specific behavioral layer [js/src/puppeteer.ts:156-164](). This enables:
- **Bézier Mouse Movements**: Natural cursor paths for `click()` and `hover()` [js/src/human-puppeteer/index.ts:52]().
- **Organic Typing**: Per-character delays and mistype simulation via Puppeteer-specific `humanType` [js/src/human-puppeteer/index.ts:54]().
- **Natural Scrolling**: Accelerated/decelerated wheel events using `smoothWheel` [js/src/human-puppeteer/index.ts:55]().
- **Stealth-Awareness**: The `patchBrowser` function injects logic to intercept Puppeteer actions. It uses CDP Isolated Worlds via `StealthEval` [js/src/human-puppeteer/index.ts:68-140]() for DOM queries like `isInputElement` to avoid main-world JS detection [js/src/human-puppeteer/index.ts:33]().

---

## Differences From the Playwright Export

**Title: Playwright vs. Puppeteer architecture comparison**

```mermaid
flowchart LR
    subgraph "cloakbrowser (Playwright)"
        PL_launch["launch() [playwright.ts]"]
        PL_human["patchBrowser() [human/index.ts]"]
        PL_proxy["proxy via BrowserTypeLaunchOptions"]
    end
    subgraph "cloakbrowser/puppeteer"
        PP_launch["launch() [puppeteer.ts]"]
        PP_human["patchBrowser() [human-puppeteer/index.ts]"]
        PP_auth["page.authenticate() monkey-patch"]
        PP_dynamic["Dynamic puppeteer-core import"]
    end
```

| Aspect | Playwright (`cloakbrowser`) | Puppeteer (`cloakbrowser/puppeteer`) |
|--------|-----------------------------|---------------------------------------|
| Framework import | Static | Dynamic `import('puppeteer-core')` [js/src/puppeteer.ts:182]() |
| Proxy credentials | Native Playwright support | Platform-dependent; uses `page.authenticate()` fallback [js/src/puppeteer.ts:146-154]() |
| Behavioral Layer | Statically imported | Dynamically imported `human-puppeteer/index.js` [js/src/puppeteer.ts:157]() |
| `launchContext()` | ✅ Supported | ❌ Not available |
| Viewport Default | `DEFAULT_VIEWPORT` | `DEFAULT_VIEWPORT` (headless) or `null` (headed) [js/tests/puppeteer.test.ts:81-97]() |

Sources: [js/src/puppeteer.ts:1-215](), [js/src/playwright.ts:1-208](), [js/tests/puppeteer.test.ts:81-97]()

---

## Known Limitation: reCAPTCHA Enterprise

Puppeteer communicates with Chromium over the Chrome DevTools Protocol (CDP). reCAPTCHA Enterprise is known to monitor for CDP-specific automation signals at the protocol level (e.g., `Runtime.enable`, `Page.enable`). These signals are inherent to how Puppeteer operates and are separate from the browser fingerprint patches applied to the Chromium binary.

CloakBrowser's source-level patches successfully bypass standard reCAPTCHA v2/v3, but users requiring high scores on **reCAPTCHA Enterprise** are strongly encouraged to use the **Playwright** export path, as Playwright's communication model is less prone to these specific CDP leaks.

---

## Minimal Example

```typescript
import { launch } from 'cloakbrowser/puppeteer';

// With humanize — human-like mouse, keyboard, scroll
const browser = await launch({ 
  humanize: true,
  proxy: 'http://user:pass@proxy.example.com:8080'
});

const page = await browser.newPage();
await page.goto('https://example.com');
await page.click('#login');  // Bézier curve mouse movement
await page.type('#email', 'user@example.com');  // Per-character timing
await browser.close();
```

Sources: [js/src/puppeteer.ts:168-180]()

---

# Page: JavaScript Configuration Module

# JavaScript Configuration Module

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/config.py](cloakbrowser/config.py)
- [dotnet/src/CloakBrowser/Config.cs](dotnet/src/CloakBrowser/Config.cs)
- [dotnet/tests/CloakBrowser.Tests/ConfigTests.cs](dotnet/tests/CloakBrowser.Tests/ConfigTests.cs)
- [js/src/args.ts](js/src/args.ts)
- [js/src/config.ts](js/src/config.ts)
- [js/tests/config.test.ts](js/tests/config.test.ts)
- [tests/test_build_args.py](tests/test_build_args.py)
- [tests/test_config.py](tests/test_config.py)

</details>



This page documents `js/src/config.ts`, the central configuration module for the JavaScript package. It provides version constants, platform detection, binary path resolution, version comparison utilities, download URL construction, and the default stealth argument set used when launching the patched Chromium binary.

For how these values are consumed at launch time, see the binary management page ([4.4]()) and the Playwright API page ([4.1]()). The Python equivalent of this module is documented at [3.2]().

---

## Constants

### `WRAPPER_VERSION`
[js/src/config.ts:13-23]()

The version of the `cloakbrowser` npm package itself, read from `package.json`. This is used during update checks to compare the local installation against the latest available release on GitHub.

### `CHROMIUM_VERSION`
[js/src/config.ts:31]()

The hardcoded version string for the Stealth Chromium binary associated with this release. Format: `MAJOR.MINOR.PATCH.BUILD.PATCH_REV` (e.g. `146.0.7680.177.5`). This value acts as the baseline in all version comparisons.

### `PLATFORM_CHROMIUM_VERSIONS`
[js/src/config.ts:33-39]()

A mapping of platform tags to specific Chromium versions. This allows different platforms to ship different binary versions during transition periods or platform-specific patch cycles.

### `BINARY_SIGNING_PUBKEYS`
[js/src/config.ts:50-52]()

A list of Ed25519 public keys (base64 encoded) used to verify the `SHA256SUMS` manifest signature during binary downloads. This ensures that the download origin alone cannot certify a tampered binary.

### `DOWNLOAD_BASE_URL`
[js/src/config.ts:156-158]()

Resolved from the `CLOAKBROWSER_DOWNLOAD_URL` environment variable at module load time. Defaults to `https://cloakbrowser.dev`.

### `GITHUB_API_URL`
[js/src/config.ts:160-161]()

The GitHub Releases API endpoint used for update checks: `https://api.github.com/repos/CloakHQ/cloakbrowser/releases`.

---

## Platform Model

**Title: Platform sets and their membership**

```mermaid
graph TD
    subgraph "SUPPORTED_PLATFORMS (all known)"
        SP1["linux-x64"]
        SP2["linux-arm64"]
        SP3["darwin-arm64"]
        SP4["darwin-x64"]
        SP5["win32-x64"]
    end

    subgraph "AVAILABLE_PLATFORMS (binaries exist)"
        AP1["linux-x64"]
        AP2["linux-arm64"]
        AP3["darwin-arm64"]
        AP4["darwin-x64"]
        AP5["windows-x64"]
    end

    SP1 --> AP1
    SP2 --> AP2
    SP3 --> AP3
    SP4 --> AP4
    SP5 --> AP5
```

Sources: [js/src/config.ts:57-66]()

`SUPPORTED_PLATFORMS` maps Node.js `process.platform` and `process.arch` combinations to internal platform tags [js/src/config.ts:57-63](). `AVAILABLE_PLATFORMS` is derived from the keys of `PLATFORM_CHROMIUM_VERSIONS` [js/src/config.ts:66](), representing platforms where a pre-built binary is hosted.

| Node Platform | Node Arch | Internal Tag | Available |
|---|---|---|---|
| `linux` | `x64` | `linux-x64` | Yes |
| `linux` | `arm64` | `linux-arm64` | Yes (Version: 146.0.7680.177.3) |
| `darwin` | `arm64` | `darwin-arm64` | Yes |
| `darwin` | `x64` | `darwin-x64` | Yes |
| `win32` | `x64` | `windows-x64` | Yes |

**Note on ARM64 Linux:** While `linux-arm64` is supported and present in the version map [js/src/config.ts:35](), it currently tracks a different patch revision than the x64 counterpart [js/src/config.ts:34-35](). Note that while it is supported in code, binaries may not always be available for every patch revision.

Sources: [js/src/config.ts:33-39](), [js/src/config.ts:57-66](), [js/src/config.ts:94-113]()

---

## Platform Detection Functions

### `getPlatformTag()`
[js/src/config.ts:94-113]()

Maps the current environment's `process.platform` and `process.arch` to a normalized tag string used for directory naming and download URL construction. It throws an `Error` if the platform is not supported.

### `checkPlatformAvailable()`
[js/src/config.ts:140-151]()

Ensures the current platform has a pre-built binary available by checking against `AVAILABLE_PLATFORMS`. It skips the check if a local binary override is provided via `CLOAKBROWSER_BINARY_PATH`.

---

## Binary Path Functions

**Title: Binary path construction logic**

```mermaid
flowchart TD
    env1["CLOAKBROWSER_CACHE_DIR env var"]
    home["os.homedir() + /.cloakbrowser"]
    getCacheDir["getCacheDir()"]
    getBinaryDir["getBinaryDir(version?)"]
    getBinaryPath_win["getBinaryPath() — Windows\nreturns .../chrome.exe"]
    getBinaryPath_mac["getBinaryPath() — macOS\nreturns .../Chromium.app/Contents/MacOS/Chromium"]
    getBinaryPath_linux["getBinaryPath() — Linux\nreturns .../chrome"]

    env1 -->|"set"| getCacheDir
    home -->|"not set"| getCacheDir
    getCacheDir --> getBinaryDir
    getBinaryDir -->|"win32"| getBinaryPath_win
    getBinaryDir -->|"darwin"| getBinaryPath_mac
    getBinaryDir -->|"linux"| getBinaryPath_linux
```

Sources: [js/src/config.ts:118-138]()

### `getCacheDir()`
[js/src/config.ts:118-122]()

Returns the base directory for CloakBrowser data. Defaults to `~/.cloakbrowser` unless overridden by `CLOAKBROWSER_CACHE_DIR`.

### `getBinaryDir(version?, pro?)`
[js/src/config.ts:124-127]()

Returns the directory path for a specific Chromium version: `<cacheDir>/chromium-<version>`. If `pro` is true, a `-pro` suffix is appended to the folder name.

### `getBinaryPath(version?, pro?)`
[js/src/config.ts:129-138]()

Returns the absolute path to the executable file. It handles platform-specific internal structures, such as the `.app` bundle on macOS [js/src/config.ts:131-133]() and `.exe` extension on Windows [js/src/config.ts:134-136]().

---

## Version Resolution

### `getEffectiveVersion(pro?, releaseChannel?, version?)`
[js/src/config.ts:185-207]()

Determines the best binary version to use. It checks for a `latest_version_<platform>` marker file in the cache directory (e.g., `latest_version_linux-x64`) [js/src/config.ts:192](). If the marker contains a version newer than the hardcoded baseline and the binary exists on disk, it returns the newer version [js/src/config.ts:197-201]().

**Title: getEffectiveVersion() decision flow**

```mermaid
flowchart TD
    Start(["getEffectiveVersion()"])
    ReadMarker["Read latest_version_TAG marker\nfrom getCacheDir()"]
    Exists{"Marker file\nexists?"}
    Newer{"versionNewer(markerVersion,\ngetChromiumVersion())?"}
    BinaryExists{"getBinaryPath(markerVersion)\nexists on disk?"}
    ReturnMarker["return markerVersion"]
    ReturnDefault["return getChromiumVersion()"]

    Start --> ReadMarker
    ReadMarker --> Exists
    Exists -->|"no"| ReturnDefault
    Exists -->|"yes"| Newer
    Newer -->|"no"| ReturnDefault
    Newer -->|"yes"| BinaryExists
    BinaryExists -->|"no"| ReturnDefault
    BinaryExists -->|"yes"| ReturnMarker
```

Sources: [js/src/config.ts:185-207]()

### `parseVersion(v)`
[js/src/config.ts:209-211]()

Converts a version string (e.g., `146.0.7680.177.5`) into a `number[]` for comparison.

### `versionNewer(a, b)`
[js/src/config.ts:213-221]()

Performs a segment-by-segment numeric comparison of two version strings. Returns `true` if `a > b`.

---

## Download URL Construction

### `getDownloadUrl(version?)`
[js/src/config.ts:174-177]()

Constructs the primary download URL using `DOWNLOAD_BASE_URL`.

### `getFallbackDownloadUrl(version?)`
[js/src/config.ts:179-182]()

Constructs a fallback URL pointing to GitHub Releases using `GITHUB_DOWNLOAD_BASE_URL`.

### `getArchiveName(tag?)`
[js/src/config.ts:170-172]()

Returns the filename for the binary archive, using `.zip` for Windows and `.tar.gz` for other platforms via `getArchiveExt()` [js/src/config.ts:166-168]().

---

## Default Stealth Arguments

### `getDefaultStealthArgs()`
[js/src/config.ts:242-270]()

Returns the CLI flags required to activate source-level patches. It generates a random seed between 10000 and 99999 for the `--fingerprint` flag [js/src/config.ts:248].

**Title: getDefaultStealthArgs() platform branching**

```mermaid
flowchart TD
    Call["getDefaultStealthArgs()"]
    Seed["seed = random(10000, 99999)"]
    Base["baseArgs = [\n  '--no-sandbox',\n  '--fingerprint=seed'\n]"]
    IsMac{"platform === 'darwin'?"}
    MacArgs["[...baseArgs,\n'--fingerprint-platform=macos']"]
    OtherArgs["[...baseArgs,\n'--fingerprint-platform=windows']"]

    Call --> Seed --> Base --> IsMac
    IsMac -->|"yes"| MacArgs
    IsMac -->|"no"| OtherArgs
```

Sources: [js/src/config.ts:242-270](), [js/tests/config.test.ts:23-45]()

| Platform | Fingerprint Platform | Hardware Spoofing |
|---|---|---|
| macOS | `macos` | Native values used |
| Linux | `windows` | Windows profile (v14+ auto-gen) |
| Windows | `windows` | Windows profile (v14+ auto-gen) |

---

## Local Binary Override

### `getLocalBinaryOverride()`
[js/src/config.ts:226-228]()

Checks for the `CLOAKBROWSER_BINARY_PATH` environment variable. If set, this path will be used directly, bypassing platform availability checks and the automatic download/update system.

---

## Module Export Summary

| Export | Kind | Description |
|---|---|---|
| `CHROMIUM_VERSION` | `const string` | Latest baseline version across all platforms |
| `WRAPPER_VERSION` | `let string` | Version of the npm package |
| `getPlatformTag()` | function | Detects normalized platform string |
| `getBinaryPath()` | function | Resolves executable path based on OS |
| `getEffectiveVersion()` | function | Resolves version including auto-updates |
| `getDefaultStealthArgs()` | function | Generates randomized stealth CLI flags |
| `getDownloadUrl()` | function | Constructs binary download URL |
| `getFallbackDownloadUrl()` | function | Constructs GitHub fallback download URL |
| `getLocalBinaryOverride()` | function | Returns path from `CLOAKBROWSER_BINARY_PATH` |

Sources: [js/src/config.ts:1-270](), [js/tests/config.test.ts:1-167]()

---

# Page: JavaScript Binary Management

# JavaScript Binary Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/download.py](cloakbrowser/download.py)
- [dotnet/src/CloakBrowser/Download.cs](dotnet/src/CloakBrowser/Download.cs)
- [js/src/download.ts](js/src/download.ts)
- [js/tests/signature.test.ts](js/tests/signature.test.ts)
- [js/tests/update.test.ts](js/tests/update.test.ts)
- [tests/test_update.py](tests/test_update.py)

</details>



This page documents `js/src/download.ts`, which handles downloading, caching, and updating the patched Chromium binary in the JavaScript package. It covers the public API (`ensureBinary`, `clearCache`, `binaryInfo`, `checkForUpdate`) and all internal helpers involved in download, extraction, and background update logic.

For the equivalent Python implementation, see [Python Binary Management](3.3). For the configuration values (`CHROMIUM_VERSION`, `getCacheDir`, `getBinaryPath`, `getEffectiveVersion`, etc.) that `download.ts` depends on, see [JavaScript Configuration Module](4.3). For how `ensureBinary` is called from the launch path, see [JavaScript Playwright API](4.1).

---

## Public API

The module exports several public functions for managing the lifecycle of the stealth binary:

| Function | Signature | Purpose |
|---|---|---|
| `ensureBinary` | `(licenseKey?, browserVersion?) => Promise<string>` | Returns path to the chrome executable, downloading if necessary. Supports Free and Pro tiers. |
| `clearCache` | `() => void` | Deletes the entire `~/.cloakbrowser/` directory. |
| `binaryInfo` | `() => BinaryInfo` | Returns version, tier, path, and installation status of the current binary. |
| `checkForUpdate` | `() => Promise<string \| null>` | Checks GitHub Releases (Free) or cloakbrowser.dev (Pro) for updates. |

Sources: [js/src/download.ts:76-80](), [js/src/download.ts:212-218](), [js/src/download.ts:221-236](), [js/src/download.ts:518-522]()

---

## Constants

Timing and tier constants govern download and update behavior:

| Constant | Value | Purpose |
|---|---|---|
| `DOWNLOAD_TIMEOUT_MS` | `600_000` (10 minutes) | Timeout for the HTTP download stream. |
| `UPDATE_CHECK_INTERVAL_SEC` | `3600` (1 hour) | Minimum elapsed time between background update checks. |
| `WELCOME_FREE_INTERVAL_SEC` | `86_400` (1 day) | Interval to re-show the Pro upsell banner to free users. |
| `PRO_MAJOR` | `"150"` | Major version indicator for the Pro tier. |

Sources: [js/src/download.ts:40-52]()

---

## `ensureBinary()` Resolution Flow

`ensureBinary` applies a strict priority order: local override first, then Pro tier resolution (if a license key is provided), and finally the Free tier resolution.

**`ensureBinary` decision diagram:**

```mermaid
flowchart TD
    A["ensureBinary(licenseKey, browserVersion)"] --> B{"getLocalBinaryOverride()\nCLOAKBROWSER_BINARY_PATH set?"}
    B -->|"yes"| C{"File exists?"}
    C -->|"no"| D["throw Error"]
    C -->|"yes"| E["return localOverride path"]

    B -->|"no"| F{"licenseKey provided?"}
    F -->|"yes"| G["validateLicense(key)"]
    G --> H{"valid?"}
    H -->|"yes"| I["ensureProBinary()"]
    H -->|"no"| J["Log failure, use free tier"]
    
    F -->|"no"| K["checkPlatformAvailable()"]
    J --> K
    I --> K
    
    K --> L{"browserVersion pinned?"}
    L -->|"yes"| M["downloadAndExtract(requestedVersion)"]
    L -->|"no"| N["effective = getEffectiveVersion()"]
    
    N --> O{"binaryPath exists?"}
    O -->|"yes"| P["maybeTriggerUpdateCheck()\nreturn path"]
    O -->|"no"| Q["downloadAndExtract(platformDefault)"]
    M --> P
    Q --> P
```

Sources: [js/src/download.ts:76-186]()

### Pro vs. Free Resolution
If a valid license key is detected via `validateLicense`, the system attempts `ensureProBinary`. [js/src/download.ts:98-116]() A `BinaryVerificationError` during Pro download is re-thrown immediately to prevent silent downgrades to the Free tier, which might compromise stealth requirements. [js/src/download.ts:119-128]()

---

## `getEffectiveVersion()` and the `latest_version` Marker

The "effective version" determines which cached binary is used. It is resolved in `config.ts` but driven by the `download.ts` update logic.

- On first use, no marker file exists, so `getChromiumVersion()` (the hardcoded version) is used.
- After a successful background update, `writeVersionMarker` writes the new version string to `latest_version_{platform}` in the cache directory. [js/src/download.ts:606-613]()
- `getEffectiveVersion()` reads this marker. It only returns the marker version if:
  1. The marker version is strictly newer than `getChromiumVersion()` (per `versionNewer`). [js/src/config.ts:182-184]()
  2. The binary file for that version actually exists on disk. [js/src/config.ts:187-190]()

Sources: [js/src/config.ts:170-194](), [js/src/download.ts:606-613]()

---

## `downloadAndExtract()`

`downloadAndExtract(version?)` orchestrates the full download + extraction sequence. It uses an atomic temp-file approach to prevent partial or corrupted downloads from being treated as valid binaries.

**Download and extraction diagram:**

```mermaid
sequenceDiagram
    participant "ensureBinary / checkForUpdate" as Caller
    participant "downloadAndExtract()" as DAE
    participant "downloadFile()" as DF
    participant "verifyDownloadChecksum()" as VDC
    participant "extractArchive()" as EA
    participant "flattenSingleSubdir()" as FSS

    Caller->>"downloadAndExtract()": call with optional version
    "downloadAndExtract()"->>DAE: getDownloadUrl(version)
    DAE->>"downloadFile()": tmpPath = _download_{Date.now()}.tar.gz
    "downloadFile()"->>DF: pipeline(fetch, writeStream)
    DF-->>DAE: file written to tmpPath
    DAE->>"verifyDownloadChecksum()": verify signature & hash
    VDC-->>DAE: BinaryVerificationError if tampered
    DAE->>"extractArchive()": archivePath=tmpPath, destDir=binaryDir
    "extractArchive()"->>EA: tarExtract (or PowerShell on Windows)
    EA->>"flattenSingleSubdir()": move contents up if single subdir
    "flattenSingleSubdir()"-->>EA: done
    EA-->>DAE: binary ready
    DAE-->>Caller: tmpPath deleted in finally block
```

Sources: [js/src/download.ts:279-322]()

### Verification (Checksums & Signatures)
Unless `CLOAKBROWSER_SKIP_CHECKSUM` is set, the system performs multi-stage verification:
1. **Signature Verification**: `verifySignature()` fetches `SHA256SUMS.sig` and verifies it against the pinned `BINARY_SIGNING_PUBKEYS` using Ed25519 via `cryptoVerify`. [js/src/download.ts:346-372]()
2. **Checksum Verification**: `verifyDownloadChecksum()` fetches the `SHA256SUMS` manifest, parses the hash for the current platform, and compares it against `createHash("sha256")` of the local file. [js/src/download.ts:324-344]()
3. **Version Binding**: The signed manifest must contain a `version=X.X.X.X` line matching the requested version to prevent downgrade attacks. [js/src/download.ts:336-339]()

Sources: [js/src/download.ts:324-372](), [js/src/config.ts:50-54]()

### `extractArchive()` and Windows Support
Extraction logic branches based on the platform:
- **Windows**: Uses `execFileSync` to call `PowerShell` with `Expand-Archive`. This avoids a dependency on `tar` for Windows users. [js/src/download.ts:474-490]()
- **Other**: Uses the `tar` npm package (`tarExtract`) with a `filter` that blocks absolute paths and path-traversal (`..`) sequences. [js/src/download.ts:448-471]()

Sources: [js/src/download.ts:440-491]()

### `flattenSingleSubdir()`
Detects if `destDir` contains exactly one subdirectory and moves its contents up one level. This is skipped for `.app` bundles on macOS to preserve application structure. [js/src/download.ts:497-514]()

---

## Background Auto-Update

After `ensureBinary()` finds a valid binary, it calls `maybeTriggerUpdateCheck()`. This fires a fire-and-forget background check if the `UPDATE_CHECK_INTERVAL_SEC` has passed. [js/src/download.ts:560-569]()

**Update check flow:**

```mermaid
flowchart TD
    A["maybeTriggerUpdateCheck()"] --> B["shouldCheckForUpdate()"]
    B --> C{"Rate Limit?\n(1 hour)"}
    C -->|"no"| D["getLatestChromiumVersion()"]
    D --> E{"Newer version available?"}
    E -->|"yes"| F["downloadAndExtract(latest)"]
    F --> G["writeVersionMarker(latest)"]
    G --> H["Log: background update complete"]
```

Sources: [js/src/download.ts:560-604]()

### `getLatestChromiumVersion()`
Queries the GitHub Releases API (`GITHUB_API_URL`). It iterates through the releases, looking for a tag that:
1. Is not a draft. [js/src/download.ts:628]()
2. Starts with `chromium-v`. [js/src/download.ts:631]()
3. Contains an asset matching the current platform tag (e.g., `cloakbrowser-linux-x64.tar.gz`). [js/src/download.ts:636-639]()

Sources: [js/src/download.ts:616-648]()

---

## `clearCache()` and `binaryInfo()`

- **`clearCache()`**: Force-removes the entire cache directory using `fs.rmSync`. [js/src/download.ts:212-218]()
- **`binaryInfo()`**: Aggregates metadata including the effective version, tier (Free/Pro), local path, and the download URL. [js/src/download.ts:221-236]()

Sources: [js/src/download.ts:212-236]()

---

# Page: .NET Package

# .NET Package

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dotnet/.gitignore](dotnet/.gitignore)
- [dotnet/CloakBrowser.sln](dotnet/CloakBrowser.sln)
- [dotnet/README.md](dotnet/README.md)
- [dotnet/examples/CloakBrowser.Examples/CloakBrowser.Examples.csproj](dotnet/examples/CloakBrowser.Examples/CloakBrowser.Examples.csproj)
- [dotnet/examples/CloakBrowser.Examples/Program.cs](dotnet/examples/CloakBrowser.Examples/Program.cs)
- [dotnet/src/CloakBrowser.Cli/CloakBrowser.Cli.csproj](dotnet/src/CloakBrowser.Cli/CloakBrowser.Cli.csproj)
- [dotnet/src/CloakBrowser.Generators/CloakBrowser.Generators.csproj](dotnet/src/CloakBrowser.Generators/CloakBrowser.Generators.csproj)
- [dotnet/src/CloakBrowser.Generators/InterfaceDelegationGenerator.cs](dotnet/src/CloakBrowser.Generators/InterfaceDelegationGenerator.cs)
- [dotnet/src/CloakBrowser/CloakBrowser.csproj](dotnet/src/CloakBrowser/CloakBrowser.csproj)
- [dotnet/src/CloakBrowser/CloakLauncher.cs](dotnet/src/CloakBrowser/CloakLauncher.cs)
- [dotnet/src/CloakBrowser/CloakVersion.cs](dotnet/src/CloakBrowser/CloakVersion.cs)
- [js/package-lock.json](js/package-lock.json)

</details>



The CloakBrowser .NET package is a complete, faithful port of the CloakBrowser Python and JavaScript wrappers, built for **.NET 8 / C#**. It provides a drop-in replacement for the official `Microsoft.Playwright` library, enabling source-level fingerprint patches and humanized interaction patterns while maintaining a statically-typed API surface [dotnet/src/CloakBrowser/CloakBrowser.csproj:12-15]().

## Architecture Overview

Unlike Python or JavaScript, .NET's Playwright implementation uses **sealed interfaces** (e.g., `IPage`, `ILocator`, `IMouse`) that cannot be monkey-patched at runtime [dotnet/README.md:50-52](). To overcome this, CloakBrowser uses a **transparent decorator pattern** powered by a custom Roslyn source generator [dotnet/src/CloakBrowser/CloakBrowser.csproj:39-43]().

### The Decorator Pattern
When `Humanize = true` is passed to the launch options, CloakBrowser returns wrapped versions of Playwright objects [dotnet/src/CloakBrowser/CloakLauncher.cs:80-89](). These wrappers (e.g., `HumanizedPage`) intercept specific calls like `ClickAsync` or `FillAsync` to inject human-like behavior while delegating all other members verbatim to the underlying Playwright instance via the `InterfaceDelegationGenerator` [dotnet/src/CloakBrowser.Generators/InterfaceDelegationGenerator.cs:11-25]().

### Code Entity Mapping: Decorator Flow
The following diagram illustrates how user code interacts with the decorator layer to reach the patched Chromium binary.

**System Entity Mapping: .NET Wrapper Architecture**
```mermaid
graph LR
    subgraph "User_Code_Space"["User Code Space"]
        A["User Application"]
    end

    subgraph "CloakBrowser_NET_Package"["CloakBrowser .NET Package"]
        B["CloakLauncher"]
        C["HumanizedPage (IPage)"]
        D["HumanizedMouse (IMouse)"]
        E["InterfaceDelegationGenerator"]
    end

    subgraph "External_Dependencies"["External Dependencies"]
        F["Microsoft.Playwright"]
        G["Stealth Chromium Binary"]
    end

    A -- "LaunchAsync(LaunchOptions)" --> B
    B -- "Returns" --> C
    C -- "Delegates non-intercepted" --> F
    C -- "Intercepts Click/Fill" --> D
    E -- "Generates Boilerplate at Compile-Time" --> C
    F -- "Controls" --> G
    B -- "Injects --fingerprint flags" --> G
```
Sources: [dotnet/src/CloakBrowser/CloakLauncher.cs:58-66](), [dotnet/src/CloakBrowser.Generators/InterfaceDelegationGenerator.cs:11-25](), [dotnet/README.md:63-66]()

---

## Primary Entry Point: CloakLauncher

The `CloakLauncher` static class is the primary entry point for the library, mirroring the `launch` functions in the Python and JS implementations [dotnet/src/CloakBrowser/CloakLauncher.cs:12-16](). Because .NET Playwright is async-only, `CloakLauncher` provides an exclusively asynchronous surface [dotnet/src/CloakBrowser/CloakLauncher.cs:13-14]().

### Launch Methods
- **`LaunchAsync`**: Launches a browser instance with specified `LaunchOptions`. It returns a `CloakBrowserHandle` which wraps the `IBrowser` [dotnet/src/CloakBrowser/CloakLauncher.cs:22-98]().
- **`LaunchContextAsync`**: Launches a browser and creates a new `IBrowserContext` in one call, returning a `CloakContextHandle` [dotnet/src/CloakBrowser/CloakLauncher.cs:105-155]().
- **`LaunchPersistentContextAsync`**: Launches a browser using a persistent user profile directory, ensuring cookies and local storage survive across runs [dotnet/examples/CloakBrowser.Examples/Program.cs:101-109]().

For a full list of parameters and return types, see [.NET API Reference](#5.1).

---

## Core Subsystems

The .NET package achieves feature parity with other implementations through several specialized modules:

| Subsystem | File(s) | Responsibility |
| :--- | :--- | :--- |
| **Configuration** | `Config.cs` | Platform detection, versioning, and capability gates like `BinarySupportsHeadlessNoViewport` [dotnet/README.md:115-115](). |
| **Binary Management** | `Download.cs` | SHA-256 and Ed25519 verified downloads of the patched binary using `BouncyCastle.Cryptography` [dotnet/src/CloakBrowser/CloakBrowser.csproj:33-36](). |
| **Humanize Layer** | `Human/`, `Wrappers/` | Bézier mouse curves, human typing with mistype simulation, and actionability checks [dotnet/README.md:125-146](). |
| **GeoIP** | `GeoIp.cs` | Auto-detecting timezone/locale from proxy exit IPs via MaxMind GeoLite2 [dotnet/src/CloakBrowser/CloakLauncher.cs:29-30](). |

### Code Entity Mapping: Project Structure
This diagram maps the logical subsystems to their physical file locations within the `dotnet/` directory.

**System Entity Mapping: Project Layout**
```mermaid
graph TD
    subgraph "CloakBrowser.sln"
        subgraph "CloakBrowser.csproj"["CloakBrowser.csproj (Core Library)"]
            DIR_H["Human/"]
            DIR_W["Wrappers/"]
            CFG["Config.cs"]
            DL["Download.cs"]
            CL["CloakLauncher.cs"]
        end

        subgraph "CloakBrowser.Generators.csproj"
            IDG["InterfaceDelegationGenerator.cs"]
        end

        subgraph "CloakBrowser.Cli.csproj"
            PROG["Program.cs (CLI Entry)"]
        end
    end

    IDG -- "Generates code for" --> DIR_W
    CL -- "Uses" --> CFG
    CL -- "Uses" --> DL
    PROG -- "Invokes" --> DL
```
Sources: [dotnet/CloakBrowser.sln:6-21](), [dotnet/src/CloakBrowser/CloakBrowser.csproj:30-43](), [dotnet/README.md:110-149]()

---

## Distribution and Tooling

### NuGet Distribution
The package is distributed via NuGet as `CloakBrowser`. It targets `net8.0` and depends on `Microsoft.Playwright` (v1.49.0), `MaxMind.GeoIP2`, and `BouncyCastle.Cryptography` for Ed25519 signature verification [dotnet/src/CloakBrowser/CloakBrowser.csproj:12-36](). The library version is centrally defined in `CloakVersion.cs` [dotnet/src/CloakBrowser/CloakVersion.cs:4-8]().

### Command Line Interface (CLI)
The package includes a CLI tool (`cloakbrowser-cli`) that provides utilities for managing the environment [dotnet/src/CloakBrowser.Cli/CloakBrowser.Cli.csproj:8-8]():
- `install`: Pre-downloads the patched Chromium binary.
- `info`: Displays diagnostic information, platform detection, and license status.
- `update`: Checks for and installs binary updates.
- `clear-cache`: Removes downloaded binaries and temporary files.

For details on configuration and the CLI, see [.NET Configuration and Binary Management](#5.2).

---

## Child Pages

- **[.NET API Reference](#5.1)** — Full reference for `CloakLauncher` methods, `LaunchOptions`, and the async-only surface.
- **[.NET Configuration and Binary Management](#5.2)** — Details on platform detection, Ed25519 signature verification via BouncyCastle, and the CLI.
- **[.NET Humanize Decorator Layer](#5.3)** — Deep dive into the Roslyn source generator and the transparent interaction engine (Bézier mouse, human typing).

---

# Page: .NET API Reference

# .NET API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bin/docker-entrypoint.sh](bin/docker-entrypoint.sh)
- [dotnet/src/CloakBrowser/CloakLauncher.cs](dotnet/src/CloakBrowser/CloakLauncher.cs)
- [dotnet/src/CloakBrowser/GeoIp.cs](dotnet/src/CloakBrowser/GeoIp.cs)
- [dotnet/src/CloakBrowser/Handles.cs](dotnet/src/CloakBrowser/Handles.cs)
- [dotnet/src/CloakBrowser/LaunchOptions.cs](dotnet/src/CloakBrowser/LaunchOptions.cs)
- [dotnet/src/CloakBrowser/ProxySettings.cs](dotnet/src/CloakBrowser/ProxySettings.cs)
- [dotnet/src/CloakBrowser/Wrappers/HumanizedBrowserContext.cs](dotnet/src/CloakBrowser/Wrappers/HumanizedBrowserContext.cs)
- [dotnet/tests/CloakBrowser.Tests/MiscTests.cs](dotnet/tests/CloakBrowser.Tests/MiscTests.cs)
- [dotnet/tests/CloakBrowser.Tests/Wrappers/BrowserContextWrapperTests.cs](dotnet/tests/CloakBrowser.Tests/Wrappers/BrowserContextWrapperTests.cs)

</details>



This page provides a detailed technical reference for the `CloakBrowser` .NET 8 / C# package. The .NET implementation follows a decorator/wrapper pattern, primarily using the `CloakLauncher` static class to interface with a patched stealth Chromium binary through the Playwright framework.

Unlike the Python implementation, which offers both synchronous and asynchronous APIs, the .NET package is **async-only** to align with the native architecture of the Microsoft Playwright library [dotnet/src/CloakBrowser/CloakLauncher.cs:9-14]().

## CloakLauncher Static Methods

`CloakLauncher` is the primary entry point for launching stealth browser instances. It handles binary resolution, GeoIP detection, license validation, and argument construction before delegating the actual launch to Playwright.

### `LaunchAsync()`
Launches a stealth Chromium browser and returns a `CloakBrowserHandle`. This is the equivalent of Playwright's `IBrowserType.LaunchAsync`.

*   **Signature:** `public static async Task<CloakBrowserHandle> LaunchAsync(LaunchOptions? options = null)` [dotnet/src/CloakBrowser/CloakLauncher.cs:22]()
*   **Data Flow:**
    1.  Resolves binary path via `Download.EnsureBinaryAsync` [dotnet/src/CloakBrowser/CloakLauncher.cs:26-28]().
    2.  Optionally resolves GeoIP data (timezone, locale, exit IP) using `MaybeResolveGeoIpAsync` [dotnet/src/CloakBrowser/CloakLauncher.cs:29-30]().
    3.  Resolves proxy settings into Playwright options or Chrome CLI args via `ProxyResolver.Resolve` [dotnet/src/CloakBrowser/CloakLauncher.cs:31-32]().
    4.  Builds final stealth arguments including random fingerprint seeds and timezone/locale flags [dotnet/src/CloakBrowser/CloakLauncher.cs:38-41]().
    5.  Launches the process via `playwright.Chromium.LaunchAsync` [dotnet/src/CloakBrowser/CloakLauncher.cs:58-66]().
    6.  Wraps the resulting `IBrowser` in a `CloakBrowserHandle` which manages the Playwright lifecycle [dotnet/src/CloakBrowser/CloakLauncher.cs:88-89]().

### `LaunchContextAsync()`
Launches a browser and immediately creates a new browser context. This is a convenience wrapper that returns a `CloakContextHandle`.

*   **Signature:** `public static async Task<CloakContextHandle> LaunchContextAsync(LaunchContextOptions? options = null)` [dotnet/src/CloakBrowser/CloakLauncher.cs:105]()
*   **Implementation:** It calls `LaunchAsync` internally with a suppressed maximize flag if a viewport is provided, then invokes `NewContextAsync` on the resulting browser handle [dotnet/src/CloakBrowser/CloakLauncher.cs:115-141]().

### `LaunchPersistentContextAsync()`
Launches a stealth browser with a persistent user data directory. Returns a `CloakContextHandle`.

*   **Signature:** `public static async Task<CloakContextHandle> LaunchPersistentContextAsync(string userDataDir, LaunchContextOptions? options = null)` [dotnet/src/CloakBrowser/CloakLauncher.cs:158-159]()

**Sources:** [dotnet/src/CloakBrowser/CloakLauncher.cs:15-159]()

---

## Configuration Classes

### LaunchOptions
The base configuration class for all launch methods. It mirrors the keyword arguments of the Python implementation [dotnet/src/CloakBrowser/LaunchOptions.cs:9]().

| Property | Type | Description |
| :--- | :--- | :--- |
| `Headless` | `bool` | Whether to run the browser in headless mode. Defaults to `true` [dotnet/src/CloakBrowser/LaunchOptions.cs:12](). |
| `Proxy` | `object?` | Proxy: a URL string or a `ProxySettings` object [dotnet/src/CloakBrowser/LaunchOptions.cs:15](). |
| `Args` | `List<string>?` | Additional Chromium command-line arguments [dotnet/src/CloakBrowser/LaunchOptions.cs:18](). |
| `StealthArgs` | `bool` | Include default stealth fingerprint args. Defaults to `true` [dotnet/src/CloakBrowser/LaunchOptions.cs:21](). |
| `Timezone` | `string?` | IANA timezone ID (e.g., `America/New_York`) - sets `--fingerprint-timezone` [dotnet/src/CloakBrowser/LaunchOptions.cs:24](). |
| `Locale` | `string?` | BCP 47 locale (e.g., `en-US`) - sets `--lang` and `--fingerprint-locale` [dotnet/src/CloakBrowser/LaunchOptions.cs:27](). |
| `GeoIp` | `bool` | Auto-detect Timezone/Locale (and WebRTC exit IP) from proxy IP [dotnet/src/CloakBrowser/LaunchOptions.cs:30](). |
| `Humanize` | `bool` | Enable the human-like behavior layer [dotnet/src/CloakBrowser/LaunchOptions.cs:33](). |
| `HumanPreset` | `HumanPreset` | Preset for humanization behaviors. Defaults to `Default` [dotnet/src/CloakBrowser/LaunchOptions.cs:36](). |
| `HumanConfig` | `IReadOnlyDictionary<string, object>?` | Custom humanize config overrides [dotnet/src/CloakBrowser/LaunchOptions.cs:39](). |
| `ExtensionPaths` | `List<string>?` | Paths to Chromium extensions to load [dotnet/src/CloakBrowser/LaunchOptions.cs:42](). |
| `LicenseKey` | `string?` | CloakBrowser Pro license key [dotnet/src/CloakBrowser/LaunchOptions.cs:49](). |
| `BrowserVersion` | `string?` | Specific Chromium version to pin [dotnet/src/CloakBrowser/LaunchOptions.cs:58](). |
| `Viewport` | `(int, int)?` | Viewport size (Width, Height). Null means "use default 1920x947" [dotnet/src/CloakBrowser/LaunchOptions.cs:81](). |
| `UserAgent` | `string?` | Custom User-Agent string [dotnet/src/CloakBrowser/LaunchOptions.cs:78](). |

### LaunchContextOptions
Extends `LaunchOptions` for context-specific emulation settings [dotnet/src/CloakBrowser/LaunchOptions.cs:75]().

| Property | Type | Description |
| :--- | :--- | :--- |
| `NoViewport` | `bool` | Disable viewport emulation to track OS window [dotnet/src/CloakBrowser/LaunchOptions.cs:84](). |
| `ColorScheme` | `string?` | Color scheme preference: `light`, `dark`, or `no-preference` [dotnet/src/CloakBrowser/LaunchOptions.cs:87](). |
| `StorageStatePath` | `string?` | Path to Playwright storage-state JSON [dotnet/src/CloakBrowser/LaunchOptions.cs:90](). |

**Sources:** [dotnet/src/CloakBrowser/LaunchOptions.cs:1-91]()

---

## Core Infrastructure Entities

### ProxySettings
Defines the proxy configuration, mirroring the Python `ProxySettings` TypedDict [dotnet/src/CloakBrowser/ProxySettings.cs:7]().
*   `Server`: Proxy server URL (e.g., `http://proxy:8080` or `socks5://proxy:1080`) [dotnet/src/CloakBrowser/ProxySettings.cs:10]().
*   `Username` / `Password`: Credentials for authenticated proxies [dotnet/src/CloakBrowser/ProxySettings.cs:16-19]().
*   `Bypass`: Comma-separated bypass list [dotnet/src/CloakBrowser/ProxySettings.cs:13]().

### CloakBrowserHandle
A launched stealth browser that owns the underlying Playwright instance [dotnet/src/CloakBrowser/Handles.cs:13]().
1.  **Lifecycle Management:** Disposing of the `IPlaywright` instance when `CloseAsync` is called [dotnet/src/CloakBrowser/Handles.cs:109-113]().
2.  **Humanize Injection:** If `Humanize` is enabled, it wraps the browser in a transparent humanizing decorator [dotnet/src/CloakBrowser/Handles.cs:56-58]().
3.  **License Guard:** Wraps the browser to surface post-handshake license denials [dotnet/src/CloakBrowser/Handles.cs:61-62]().
4.  **Raw Access:** Provides `RawBrowser` as an escape hatch to the un-wrapped Playwright browser [dotnet/src/CloakBrowser/Handles.cs:33]().

### CloakBrowserLicenseError
The .NET package maps binary exit codes and handshake denials to `CloakBrowserLicenseError` [dotnet/src/CloakBrowser/CloakLauncher.cs:71-72](). This is handled by the `LicenseGuard` which monitors a per-launch denial file written by the binary [dotnet/src/CloakBrowser/Handles.cs:130-137]().

**Sources:** [dotnet/src/CloakBrowser/ProxySettings.cs:1-21](), [dotnet/src/CloakBrowser/Handles.cs:1-137](), [dotnet/src/CloakBrowser/CloakLauncher.cs:46-74]()

---

## Architecture Diagrams

### Entity Association Map
This diagram bridges the natural language concepts of the .NET API to the specific code entities implementing them.

```mermaid
graph TD
    subgraph "Public API Surface"
        CL["CloakLauncher"]
        LO["LaunchOptions"]
        LCO["LaunchContextOptions"]
    end

    subgraph "Internal Logic"
        PR["ProxyResolver"]
        DL["Download"]
        LIC["License"]
        GI["GeoIp"]
        LG["LicenseGuard"]
    end

    subgraph "Output Handles"
        BH["CloakBrowserHandle"]
        CH["CloakContextHandle"]
    end

    CL -- "uses" --> LO
    CL -- "calls" --> DL["Download.EnsureBinaryAsync"]
    CL -- "calls" --> GI["GeoIp.ResolveProxyGeoWithIpAsync"]
    CL -- "calls" --> PR["ProxyResolver.Resolve"]
    CL -- "validates" --> LIC["License.LicenseErrorFrom"]
    
    CL -- "returns" --> BH
    CL -- "returns" --> CH
    BH -- "wraps with" --> LG
```
**Sources:** [dotnet/src/CloakBrowser/CloakLauncher.cs:15-159](), [dotnet/src/CloakBrowser/GeoIp.cs:97-133](), [dotnet/src/CloakBrowser/Handles.cs:13-62]()

### Proxy and GeoIP Data Flow
Detailed view of how the `CloakLauncher` coordinates proxy resolution and GeoIP detection before launching Chromium.

```mermaid
graph TD
    Start["LaunchOptions.Proxy"] --> GeoCheck{"GeoIp == true?"}
    
    GeoCheck -- "Yes" --> ResolveGeo["GeoIp.ResolveProxyGeoWithIpAsync"]
    ResolveGeo --> Flags["Set --fingerprint-timezone and --fingerprint-locale"]
    ResolveGeo --> WebRTC["Set --fingerprint-webrtc-ip"]
    
    GeoCheck -- "No" --> ProxyRes["ProxyResolver.Resolve"]
    
    ProxyRes --> PWProxy["PlaywrightProxy"]
    ProxyRes --> ExtraArgs["Extra Chromium Args"]
    
    Flags --> Launch["playwright.Chromium.LaunchAsync"]
    WebRTC --> Launch
    PWProxy --> Launch
    ExtraArgs --> Launch
```
**Sources:** [dotnet/src/CloakBrowser/CloakLauncher.cs:26-66](), [dotnet/src/CloakBrowser/GeoIp.cs:97-133]()

---

# Page: .NET Configuration and Binary Management

# .NET Configuration and Binary Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/download.py](cloakbrowser/download.py)
- [dotnet/src/CloakBrowser/Config.cs](dotnet/src/CloakBrowser/Config.cs)
- [dotnet/src/CloakBrowser/Download.cs](dotnet/src/CloakBrowser/Download.cs)
- [dotnet/tests/CloakBrowser.Tests/ConfigTests.cs](dotnet/tests/CloakBrowser.Tests/ConfigTests.cs)
- [dotnet/tests/CloakBrowser.Tests/DownloadConfigTests.cs](dotnet/tests/CloakBrowser.Tests/DownloadConfigTests.cs)
- [dotnet/tests/CloakBrowser.Tests/SignatureTests.cs](dotnet/tests/CloakBrowser.Tests/SignatureTests.cs)
- [js/src/args.ts](js/src/args.ts)
- [js/src/download.ts](js/src/download.ts)
- [js/tests/config.test.ts](js/tests/config.test.ts)
- [tests/test_build_args.py](tests/test_build_args.py)
- [tests/test_config.py](tests/test_config.py)

</details>



This page documents the configuration, platform detection, and binary lifecycle management for the CloakBrowser .NET package. These systems ensure that the correct stealth Chromium binary is resolved, authenticated, and maintained for the host environment.

## Configuration and Platform Detection

The configuration layer in `Config.cs` handles platform-specific versioning and the generation of default stealth arguments. It mirrors the logic found in the Python and JavaScript implementations to ensure cross-language behavioral parity.

### Platform Resolution
CloakBrowser supports `linux-x64`, `linux-arm64`, `darwin-arm64`, `darwin-x64`, and `windows-x64` [dotnet/src/CloakBrowser/Config.cs:20-28](). The `GetPlatformTag()` method uses `RuntimeInformation` to detect the OS and architecture at runtime [dotnet/src/CloakBrowser/Config.cs:155-180]().

### Capability Gates
The .NET wrapper uses version-based gates to enable or disable features based on the capabilities of the specific Chromium binary version being used. These gates prevent incoherent behavior (like `outerWidth < innerWidth`) when using older binaries.

| Gate | Purpose | Version Threshold |
| :--- | :--- | :--- |
| `BinarySupportsHeadlessNoViewport` | Allows headless mode to run without a forced viewport, enabling better window/screen coherence. | `148.0.7778.215.4` [dotnet/src/CloakBrowser/Config.cs:188-202]() |
| `BinarySupportsHttpProxyInlineAuth` | Allows passing HTTP proxy credentials directly via `--proxy-server=http://user:pass@host`. | Platform-dependent [dotnet/src/CloakBrowser/Config.cs:220-230]() |
| `BinarySupportsMaximizedWindow` | Enables the `--start-maximized` flag compatibility. | `146.0.7680.177.5` [dotnet/src/CloakBrowser/Config.cs:204-218]() |

Sources: [dotnet/src/CloakBrowser/Config.cs:10-140](), [dotnet/src/CloakBrowser/Config.cs:155-230]()

### Stealth Argument Generation
`GetDefaultStealthArgs()` generates the base command-line flags required for the patched binary. This includes a random fingerprint seed between 10,000 and 99,999 generated using a thread-safe `Random` instance [dotnet/src/CloakBrowser/Config.cs:72-78]().
*   **macOS**: Uses `--fingerprint-platform=macos` to maintain native GPU and font profiles [dotnet/src/CloakBrowser/Config.cs:81-86]().
*   **Linux/Windows**: Uses `--fingerprint-platform=windows` to masquerade as a Windows environment [dotnet/src/CloakBrowser/Config.cs:88-93]().

Sources: [dotnet/src/CloakBrowser/Config.cs:70-94]()

## Binary Management

The `Download` class manages the lifecycle of the Chromium binary, including version resolution, atomic downloads, and integrity verification.

### Version Resolution Flow
`EnsureBinaryAsync()` follows a strict priority list to find the binary path:
1.  **Local Override**: If `CLOAKBROWSER_BINARY_PATH` is set, it is used immediately [dotnet/src/CloakBrowser/Download.cs:183-191]().
2.  **Pro Tier**: If a valid `licenseKey` is provided or found in environment variables, it attempts to download the Pro binary from `cloakbrowser.dev` [dotnet/src/CloakBrowser/Download.cs:203-216]().
3.  **Pinned Version**: If `CLOAKBROWSER_VERSION` is set, it fetches that specific version [dotnet/src/CloakBrowser/Download.cs:231-252]().
4.  **Effective Version**: Checks for a version previously downloaded via the auto-update mechanism (stored in the `.latest_version` marker) [dotnet/src/CloakBrowser/Download.cs:263-270]().
5.  **Bundled Default**: Falls back to the hardcoded version for the current platform [dotnet/src/CloakBrowser/Download.cs:273-280]().

### Integrity and Signature Verification
CloakBrowser uses **BouncyCastle** to perform Ed25519 signature verification on the downloaded manifest (`SHA256SUMS`). 
1.  **Download**: The archive, manifest, and signature (`SHA256SUMS.sig`) are downloaded [dotnet/src/CloakBrowser/Download.cs:411-445]().
2.  **Signature Check**: `VerifySignature()` checks the manifest against the signature using the pinned public keys in `Config.BinarySigningPubkeys` [dotnet/src/CloakBrowser/Download.cs:482-508]().
3.  **Checksum Check**: `VerifyDownloadChecksum()` compares the SHA-256 hash of the downloaded archive against the entry in the verified manifest [dotnet/src/CloakBrowser/Download.cs:510-538]().

If any check fails, a `BinaryVerificationError` is thrown, preventing the execution of potentially tampered code [dotnet/src/CloakBrowser/Download.cs:30-34]().

Sources: [dotnet/src/CloakBrowser/Download.cs:183-280](), [dotnet/src/CloakBrowser/Download.cs:411-538]()

### Binary Extraction and Setup
Archives are extracted using `TarFile.ExtractToDirectory` for Unix-like systems and `ZipFile.ExtractToDirectory` for Windows [dotnet/src/CloakBrowser/Download.cs:641-655](). On macOS, the `com.apple.quarantine` extended attribute is removed from the extracted bundle via `xattr -d` to allow execution without user prompts [dotnet/src/CloakBrowser/Download.cs:691-705]().

## CLI (CloakBrowser.Cli)

The .NET package includes a CLI tool (`CloakBrowser.Cli`) for manual management of the binary environment. It is a direct port of the Python CLI logic.

### Commands
*   **`install`**: Triggers `Download.EnsureBinaryAsync()` to pre-warm the cache [dotnet/src/CloakBrowser.Cli/Program.cs:64-68]().
*   **`info` / `doctor`**: Collects diagnostics about the environment, license, and binary status. Supports `--quick` (skip network/launch tests) and `--json` [dotnet/src/CloakBrowser.Cli/Program.cs:70-85]().
*   **`update`**: Forces a check for a newer Chromium version and updates the `.latest_version` marker [dotnet/src/CloakBrowser.Cli/Program.cs:40-42]().
*   **`clear-cache`**: Deletes the `~/.cloakbrowser` directory to reset the environment [dotnet/src/CloakBrowser.Cli/Program.cs:43-45]().

### Diagnostic Data Flow
The `Diagnostics.Collect` method aggregates system information:
1.  **Environment**: .NET version, OS, and Architecture [dotnet/src/CloakBrowser.Cli/Program.cs:91-93]().
2.  **Binary**: Current version, tier (Free/Pro), and installation path [dotnet/src/CloakBrowser.Cli/Program.cs:95-126]().
3.  **Fonts**: Checks for essential Windows fonts (Segoe UI, etc.) required for stealth coherence [dotnet/src/CloakBrowser.Cli/Program.cs:147-169]().
4.  **License**: Validates the license key and retrieves active session counts [dotnet/src/CloakBrowser.Cli/Program.cs:171-193]().

Sources: [dotnet/src/CloakBrowser.Cli/Program.cs:29-85](), [dotnet/src/CloakBrowser.Cli/Program.cs:87-195]()

## Diagrams

### Binary Resolution Logic
This diagram bridges the user's intent (requesting a browser) to the code entities responsible for finding or downloading the binary.

```mermaid
graph TD
    User["User calls CloakLauncher.LaunchAsync"] --> Ensure["Download.EnsureBinaryAsync()"]
    Ensure --> Override{"Config.GetLocalBinaryOverride()?"}
    Override -- "Yes" --> ReturnPath["Return CLOAKBROWSER_BINARY_PATH"]
    Override -- "No" --> LicenseCheck{"License.ValidateLicense()?"}
    
    LicenseCheck -- "Valid" --> ProFlow["Download.EnsureProBinaryAsync()"]
    LicenseCheck -- "Invalid/None" --> FreeFlow["Check local cache for default version"]
    
    ProFlow --> ProDL["Download.DownloadAndExtractAsync(pro: true)"]
    FreeFlow --> FreeDL["Download.DownloadAndExtractAsync(pro: false)"]
    
    ProDL --> Verify["Download.VerifyDownloadChecksum()"]
    FreeDL --> Verify
    
    Verify --> Sig["Download.VerifySignature() (Ed25519)"]
    Sig --> Ext["Download.ExtractArchiveAsync()"]
```
Sources: [dotnet/src/CloakBrowser/Download.cs:183-280](), [dotnet/src/CloakBrowser/Download.cs:411-538]()

### CLI Diagnostics Flow
This diagram shows how the `cloakbrowser info` command gathers data across different modules.

```mermaid
graph LR
    CLI["CloakBrowser.Cli/Program.cs"] --> Diag["Diagnostics.Collect()"]
    Diag --> Config["Config.GetPlatformTag()"]
    Diag --> License["License.ValidateLicense()"]
    Diag --> Session["License.GetActiveSessionCount()"]
    Diag --> BinaryInfo["Download.BinaryInfo()"]
    Diag --> Fonts["Fonts.CountFontsPresent()"]
    
    subgraph "Output Formatting"
        Diag --> Text["PrintDiagnostics()"]
        Diag --> JSON["JsonSerializer.Serialize()"]
    end
```
Sources: [dotnet/src/CloakBrowser.Cli/Program.cs:70-85](), [dotnet/src/CloakBrowser.Cli/Program.cs:87-195]()

---

# Page: .NET Humanize Decorator Layer

# .NET Humanize Decorator Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dotnet/.gitignore](dotnet/.gitignore)
- [dotnet/CloakBrowser.sln](dotnet/CloakBrowser.sln)
- [dotnet/examples/CloakBrowser.Examples/CloakBrowser.Examples.csproj](dotnet/examples/CloakBrowser.Examples/CloakBrowser.Examples.csproj)
- [dotnet/examples/CloakBrowser.Examples/Program.cs](dotnet/examples/CloakBrowser.Examples/Program.cs)
- [dotnet/src/CloakBrowser.Cli/CloakBrowser.Cli.csproj](dotnet/src/CloakBrowser.Cli/CloakBrowser.Cli.csproj)
- [dotnet/src/CloakBrowser.Generators/CloakBrowser.Generators.csproj](dotnet/src/CloakBrowser.Generators/CloakBrowser.Generators.csproj)
- [dotnet/src/CloakBrowser.Generators/InterfaceDelegationGenerator.cs](dotnet/src/CloakBrowser.Generators/InterfaceDelegationGenerator.cs)
- [dotnet/src/CloakBrowser/Human/Actionability.cs](dotnet/src/CloakBrowser/Human/Actionability.cs)
- [dotnet/src/CloakBrowser/Human/HumanPage.cs](dotnet/src/CloakBrowser/Human/HumanPage.cs)
- [dotnet/src/CloakBrowser/Human/StealthDom.cs](dotnet/src/CloakBrowser/Human/StealthDom.cs)
- [dotnet/src/CloakBrowser/Wrappers/HumanCursor.cs](dotnet/src/CloakBrowser/Wrappers/HumanCursor.cs)
- [dotnet/src/CloakBrowser/Wrappers/Humanize.cs](dotnet/src/CloakBrowser/Wrappers/Humanize.cs)
- [dotnet/src/CloakBrowser/Wrappers/HumanizedFrame.cs](dotnet/src/CloakBrowser/Wrappers/HumanizedFrame.cs)
- [dotnet/src/CloakBrowser/Wrappers/HumanizedLocator.cs](dotnet/src/CloakBrowser/Wrappers/HumanizedLocator.cs)
- [dotnet/src/CloakBrowser/Wrappers/HumanizedPage.cs](dotnet/src/CloakBrowser/Wrappers/HumanizedPage.cs)
- [dotnet/src/CloakBrowser/Wrappers/LocatorHumanizer.cs](dotnet/src/CloakBrowser/Wrappers/LocatorHumanizer.cs)
- [dotnet/tests/CloakBrowser.Tests/Human/StealthDomTests.cs](dotnet/tests/CloakBrowser.Tests/Human/StealthDomTests.cs)

</details>



The .NET Humanize Decorator Layer provides a transparent behavioral wrapper over the Playwright .NET library. It implements human-like interaction patterns (mouse movement, typing, and scrolling) while maintaining the standard Playwright interface. This layer is critical for bypassing behavioral bot detection by ensuring that automation signals match human-typical kinematics and timings.

## Overview and Motivation

Unlike Python or JavaScript, where dynamic monkey-patching allows modifying library behavior at runtime, Playwright .NET uses `sealed` classes and internal interfaces that prevent traditional decoration of the core library objects. To achieve a "drop-in" experience where users can simply use `IPage`, `ILocator`, or `IMouse` as normal, CloakBrowser utilizes a **Roslyn Source Generator** (`InterfaceDelegationGenerator`) to create a decorator tree at compile time [dotnet/src/CloakBrowser/CloakBrowser.csproj:20-20]().

### Key Characteristics
*   **Transparent Interception**: Methods like `ClickAsync`, `FillAsync`, and `TypeAsync` are intercepted and routed through humanization logic [dotnet/src/CloakBrowser/Wrappers/HumanizedPage.cs:108-124]().
*   **Compile-Time Generation**: Wrappers for `IBrowser`, `IBrowserContext`, `IPage`, `ILocator`, `IFrame`, `IKeyboard`, and `IMouse` are generated to forward all non-intercepted calls to the underlying Playwright instance via the `[GenerateInterfaceDelegation]` attribute [dotnet/src/CloakBrowser/Wrappers/HumanizedPage.cs:16-17]().
*   **Zero Leakage**: Every object returned by a humanized parent (e.g., a `Locator` from a `Page`) is automatically re-wrapped, ensuring the "humanized" state persists throughout the object graph [dotnet/src/CloakBrowser/Wrappers/Humanize.cs:11-18]().
*   **Parity**: The Bézier curves, typing jitters, and scroll acceleration math are direct ports of the Python/JS implementations, ensuring cross-language behavioral consistency [dotnet/src/CloakBrowser/Human/HumanPage.cs:31-35]().

---

## Architecture: The Decorator Tree

The humanization layer starts at the `CloakLauncher` and propagates down through the Playwright hierarchy.

### Data Flow and Wrapping Logic
The following diagram illustrates how a raw Playwright object is transformed into a humanized version that satisfies the same interface.

**Humanization Object Graph**
```mermaid
graph TD
    subgraph "Playwright Space"
        B["IPage (Raw)"]
        C["IBrowserContext (Raw)"]
        L["ILocator (Raw)"]
    end

    subgraph "Humanize Decorator Layer"
        HP["HumanizedPage"]
        HC["HumanizedBrowserContext"]
        HL["HumanizedLocator"]
        HF["HumanizedFrame"]
    end

    HP -- "Wraps" --> B
    HC -- "Wraps" --> C
    HL -- "Wraps" --> L

    HC -- "NewPageAsync()" --> HP
    HP -- "Locator()" --> HL
    HP -- "MainFrame" --> HF
    
    HP -- "Internal" --> HumanPage["HumanPage Engine"]
    HL -- "Internal" --> LocatorHumanizer["LocatorHumanizer"]
```
Sources: [dotnet/src/CloakBrowser/Wrappers/Humanize.cs:26-47](), [dotnet/src/CloakBrowser/Wrappers/HumanizedPage.cs:97-102](), [dotnet/src/CloakBrowser/Wrappers/HumanizedLocator.cs:16-17]()

### Component Mapping

| .NET Interface | Humanized Wrapper | Responsibility |
| :--- | :--- | :--- |
| `IBrowserContext` | `HumanizedBrowserContext` | Memoizes wrappers via `ConditionalWeakTable` so `page.Context` returns a stable identity [dotnet/src/CloakBrowser/Wrappers/Humanize.cs:40-50](). |
| `IPage` | `HumanizedPage` | Routes selector-based actions through `HumanPage` engine; wraps `Mouse` and `Keyboard` [dotnet/src/CloakBrowser/Wrappers/HumanizedPage.cs:30-38](). |
| `ILocator` | `HumanizedLocator` | Implements humanized `ClickAsync`, `FillAsync`, and `DragToAsync` using the page's shared cursor [dotnet/src/CloakBrowser/Wrappers/HumanizedLocator.cs:48-95](). |
| `IFrame` | `HumanizedFrame` | Resolves locators within the frame and routes them through `LocatorHumanizer` [dotnet/src/CloakBrowser/Wrappers/HumanizedFrame.cs:41-66](). |
| `IElementHandle` | `HumanizedElementHandle` | Provides humanized interaction for raw handles [dotnet/src/CloakBrowser/Wrappers/Humanize.cs:89-90](). |

---

## Technical Implementation Details

### The HumanCursor and Shared State
To prevent the cursor from "jumping" between independent calls, CloakBrowser uses a `HumanCursor` class. This instance is shared between a `HumanizedPage` and all its derived `Locators`, `Frames`, and `Mouse` objects [dotnet/src/CloakBrowser/Wrappers/HumanCursor.cs:7-12](). It tracks the virtual `(X, Y)` position and maintains the CDP isolated world session for stealthy DOM reads [dotnet/src/CloakBrowser/Wrappers/HumanCursor.cs:32-33]().

### Stealth DOM: Isolated World Reads
Humanized actions often need to check if an element is visible or find its bounding box without triggering Playwright's main-world automation signals.
*   **StealthDom**: Implements a subset of Playwright's selector grammar (CSS, XPath, `text=`, `:has-text`) in JavaScript [dotnet/src/CloakBrowser/Human/StealthDom.cs:16-23]().
*   **IsolatedWorld**: Executes this JS via CDP `Runtime.evaluate` in a separate execution context, making the reads invisible to most bot detectors [dotnet/src/CloakBrowser/Human/StealthDom.cs:11-14]().
*   **Fail-Open**: If a complex selector (e.g., `internal:role`) is used, the system returns `StealthStatus.Unsupported` and falls back to standard Playwright reads [dotnet/src/CloakBrowser/Human/StealthDom.cs:20-23]().

### Actionability and Shared Timeouts
The `.NET` layer implements a retry loop with backoff [100, 250, 500, 1000]ms for actionability checks (attached, visible, stable, enabled, editable) [dotnet/src/CloakBrowser/Human/Actionability.cs:72-100]().
*   **Timeout Budget**: All sub-steps of an action (moving, clicking, waiting) share a single deadline calculated from the initial `Timeout` option to prevent exponential timeout growth [dotnet/src/CloakBrowser/Human/Actionability.cs:110-115]().
*   **OptionReader**: Since Playwright's option classes (e.g., `PageClickOptions`) have no common base, CloakBrowser uses reflection to extract `Timeout`, `Force`, and `Delay` values [dotnet/src/CloakBrowser/Wrappers/Humanize.cs:127-143]().

### Keyboard: Non-ASCII and Stealth Path
The `HumanKeyboard` engine handles text input with specific bypasses:
*   **CDP Stealth Path**: If a CDP session is available, keys are dispatched via `Input.dispatchKeyEvent` to ensure they appear as "trusted" events [dotnet/src/CloakBrowser/Wrappers/HumanCursor.cs:99-100]().
*   **Non-ASCII Handling**: Characters that cannot be represented as physical key codes (emojis, CJK) are handled through a specialized path to ensure compatibility [dotnet/src/CloakBrowser/Human/HumanPage.cs:31-35]().

---

## Interaction Logic Flow

The following diagram bridges the high-level user call to the internal humanization logic.

**Action Execution Flow (e.g., ClickAsync)**
```mermaid
sequenceDiagram
    participant User as User Code
    participant HP as HumanizedPage
    participant LD as LocatorHumanizer
    participant SD as StealthDom (Isolated World)
    participant PW as Playwright (Raw)

    User->>HP: ClickAsync(".btn")
    HP->>LD: ClickAsync(locator, cursor, cfg)
    LD->>SD: BuildBoxJs(".btn")
    SD-->>LD: BoundingBox {x, y, w, h}
    Note over LD: Fallback to PW if SD unsupported
    LD->>PW: Mouse.MoveAsync(bezier_path)
    LD->>PW: Mouse.DownAsync()
    Note over LD: Random Human Delay
    LD->>PW: Mouse.UpAsync()
    HP-->>User: Task Completed
```
Sources: [dotnet/src/CloakBrowser/Wrappers/LocatorHumanizer.cs:101-151](), [dotnet/src/CloakBrowser/Human/StealthDom.cs:100-107](), [dotnet/src/CloakBrowser/Wrappers/HumanizedPage.cs:108-109]()

## Pointer-Events Fail-Open
Before clicking, the layer verifies if the element is actually receiving pointer events using `document.elementFromPoint` in the isolated world [dotnet/src/CloakBrowser/Human/StealthDom.cs:133-147](). If the element is covered by another tag, it throws a `ElementNotReceivingEventsError` [dotnet/src/CloakBrowser/Human/Actionability.cs:61-66](). However, if the geometry resolution is uncertain, it "fails open" to allow the click to proceed rather than blocking a valid interaction.

Sources:
* [dotnet/src/CloakBrowser/Wrappers/Humanize.cs:1-143]()
* [dotnet/src/CloakBrowser/Wrappers/HumanizedPage.cs:1-130]()
* [dotnet/src/CloakBrowser/Wrappers/HumanizedLocator.cs:1-120]()
* [dotnet/src/CloakBrowser/Human/HumanPage.cs:36-130]()
* [dotnet/src/CloakBrowser/Human/Actionability.cs:72-170]()
* [dotnet/src/CloakBrowser/Human/StealthDom.cs:1-147]()
* [dotnet/src/CloakBrowser/Wrappers/HumanCursor.cs:1-101]()

---

# Page: Stealth System

# Stealth System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [cloakbrowser/config.py](cloakbrowser/config.py)
- [js/src/config.ts](js/src/config.ts)
- [js/src/human-puppeteer/index.ts](js/src/human-puppeteer/index.ts)
- [js/tests/stealth.puppeteer.test.ts](js/tests/stealth.puppeteer.test.ts)
- [js/tests/stealth.test.ts](js/tests/stealth.test.ts)
- [tests/test_stealth_unit.py](tests/test_stealth_unit.py)

</details>



This page explains the end-to-end mechanism by which CloakBrowser evades bot detection: the source-level binary patches, how launch arguments activate them, and how platform-specific fingerprint spoofing is applied. It covers what is patched, why, and the measured detection results.

For the individual `--fingerprint-*` flag reference, see [Fingerprint Flags Reference](#6.1). For how the behavioral layer mimics human interactions, see [Humanize Behavioral Layer](#6.2). For details on the optional GeoIP resolution system, see [GeoIP Auto-Detection](#6.3).

---

## Approach: Source-Level C++ Patches

CloakBrowser's stealth capability comes from **71 source-level C++ patches** (upgraded to 73 in recent Pro builds) applied directly to Chromium's core before compilation [README.md:39-45](). The resulting binary is distributed as a pre-built artifact, ensuring that fingerprints are modified at the binary level rather than via detectable runtime scripts.

This is distinct from common alternative approaches:

| Approach | Example Tools | How It Works | Why It Fails |
|---|---|---|---|
| JavaScript injection | `playwright-stealth` | Overwrites `navigator` properties at runtime | Detectable by JS integrity checks; breaks on Chrome updates |
| Config/flag patches | `undetected-chromedriver` | Sets browser flags to hide automation | Flags themselves become detection signals |
| CDP manipulation | `puppeteer-extra` | Modifies devtools protocol messages | CDP protocol leaks remain visible |
| **C++ source patches** | **CloakBrowser** | Modifies browser internals before compilation | Detection sites see a real browser because it *is* one |

The patched binary is downloaded to `~/.cloakbrowser/` on first launch [cloakbrowser/config.py:160-170](). The Python, JavaScript, and .NET packages are thin wrappers that point Playwright or Puppeteer at this binary with the correct activation arguments.

Sources: [README.md:39-45](), [README.md:153-156](), [CHANGELOG.md:11-17](), [cloakbrowser/config.py:160-170]()

---

## What Is Patched

The C++ patches modify critical browser surfaces that are commonly used for fingerprinting and automation detection. Unlike JS-based spoofing, these patches are active even before the first line of page-script executes.

| Surface | Browser API / Signal | Effect of Patch |
|---|---|---|
| **Canvas** | `toDataURL`, `getImageData` | Deterministic noise seeded by `--fingerprint` [cloakbrowser/config.py:65](). |
| **WebGL/WebGPU** | `UNMASKED_RENDERER_WEBGL` | Returns spoofed GPU renderer, vendor, and device IDs [README.md:39](). |
| **Audio** | `OfflineAudioContext`, AAC | Seeded noise on audio processing and AAC encoder output [README.md:39](). |
| **Fonts** | `document.fonts` / CSS checks | Consistent font list matching spoofed platform [CHANGELOG.md:13](). |
| **Hardware** | `hardwareConcurrency` | Returns configured value via `--fingerprint-hardware-concurrency` [CHANGELOG.md:12](). |
| **Storage** | `StorageBuckets` Quota | Normalizes storage quotas to bypass incognito detection [CHANGELOG.md:14](). |
| **Automation** | `navigator.webdriver` | Returns `false` at the source level by ignoring `--enable-automation` [cloakbrowser/config.py:47](). |
| **Network** | DNS/SSL/Connect timing | Zeroes proxy-induced timing leaks and strips proxy headers [README.md:166](). |
| **WebRTC** | ICE Candidates | Spoofs WebRTC IPs to match proxy exit IP via `--fingerprint-webrtc-ip` [README.md:168](). |
| **User-Agent** | UA string and Client Hints | Matches spoofed platform; removes `HeadlessChrome` [CHANGELOG.md:14](). |
| **SAPI Voices** | `speechSynthesis` | Localized voice tables for Windows personas [CHANGELOG.md:13](). |

Sources: [README.md:39-41](), [README.md:153-168](), [CHANGELOG.md:11-17](), [cloakbrowser/config.py:47-65]()

---

## Stealth Argument Activation

The patches in the binary are dormant unless activated via command-line flags at launch. The wrapper packages call `get_default_stealth_args()` (Python) or `getDefaultStealthArgs()` (JS) to generate these flags automatically on every `launch()` call.

**Activation Flow: Code to Binary**

```mermaid
flowchart TD
    UserLaunch["launch() / launch_context()"]
    GetArgs["get_default_stealth_args() [cloakbrowser/config.py:54-77]\ngetDefaultStealthArgs() [js/src/config.ts]"]
    Seed["random.randint(10000, 99999)\n--fingerprint=SEED"]
    Platform{"platform.system() [cloakbrowser/config.py:61]\nprocess.platform [js/src/config.ts]"}
    MacArgs["--fingerprint-platform=macos"]
    WinArgs["--fingerprint-platform=windows"]
    BaseArgs["--no-sandbox\n--fingerprint=SEED"]
    Framework["playwright-core / puppeteer-core"]
    BinExec["Patched Chromium binary\nreads flags at startup"]
    PatchesActive["C++ patches activated\nusing flag values as parameters"]

    UserLaunch --> GetArgs
    GetArgs --> Seed
    GetArgs --> Platform
    GetArgs --> BaseArgs
    Platform -->|"Darwin"| MacArgs
    Platform -->|"Linux / Windows"| WinArgs
    BaseArgs --> Framework
    MacArgs --> Framework
    WinArgs --> Framework
    Framework --> BinExec
    BinExec --> PatchesActive
```

Sources: [cloakbrowser/config.py:54-77](), [js/src/config.ts:33-39](), [README.md:153-156]()

---

## Platform-Specific Fingerprint Strategy

CloakBrowser applies different strategies based on the host OS to ensure cross-signal consistency.

```mermaid
flowchart LR
    subgraph "Host OS [cloakbrowser/config.py:91-98]"
        Linux["Linux x64 / arm64"]
        MacARM["macOS arm64"]
        MacX64["macOS x64"]
        Win64["Windows x64"]
    end

    subgraph "Spoofed Identity [cloakbrowser/config.py:68-76]"
        WinID["Windows identity\n(NVIDIA GPU pool\nWindows UA string\nWindows font set)"]
        MacID["Native macOS identity\n(Apple GPU\nmacOS UA string\nmacOS font set)"]
    end

    Linux -->|"--fingerprint-platform=windows"| WinID
    Win64 -->|"--fingerprint-platform=windows"| WinID
    MacARM -->|"--fingerprint-platform=macos"| MacID
    MacX64 -->|"--fingerprint-platform=macos"| MacID
```

- **Linux masquerades as Windows:** Linux desktops are a statistical anomaly in web traffic. CloakBrowser defaults Linux hosts to a Windows identity to blend into the largest market share [cloakbrowser/config.py:72-76]().
- **macOS uses native values:** Claiming an NVIDIA GPU on an Apple Silicon machine creates a detectable inconsistency. CloakBrowser uses native macOS values for consistency across all hardware reporting APIs [cloakbrowser/config.py:68-70]().
- **Windows Native GPU Passthrough:** Pro binaries can pass through real hardware values directly to match real browser behavior when not spoofing [README.md:159]().
- **Deterministic GPU Profiles:** GPU vendor/renderer flags drive realistic GPU profiles based on the fingerprint seed [CHANGELOG.md:12]().

Sources: [cloakbrowser/config.py:54-77](), [README.md:153-159](), [CHANGELOG.md:11-17]()

---

## Seed-Based Fingerprint Correlation

A single random integer seed (range 10000–99999) drives all seed-dependent patches via the `--fingerprint=SEED` flag [cloakbrowser/config.py:60-65](). In the Pro tier (v150+), this seed is used to select a "Coherent Identity" where screen size, RAM, CPU cores, and GPU model are chosen together to match a popular, real-world device configuration [CHANGELOG.md:12]().

To maintain a persistent identity across sessions, pin the seed explicitly in the `args` list:

```python
# Python example
browser = launch(args=["--fingerprint=42069"])
```

Sources: [cloakbrowser/config.py:60-65](), [CHANGELOG.md:11-17]()

---

## Detection Test Results

CloakBrowser is verified against live detection services. Pro tier binaries (Chromium 150+) provide the highest scores.

| Detection Service | Stock Playwright | CloakBrowser | Notes |
|---|---|---|---|
| **reCAPTCHA v3** | 0.1 | **0.9** | Human-level score (Pro binary) [README.md:41](). |
| **Cloudflare Turnstile** | FAIL | **PASS** | Bypasses managed and non-interactive challenges [README.md:28-30](). |
| **FingerprintJS** | DETECTED | **PASS** | Passes advanced bot detection; requires `geoip=True` for consistency [README.md:42](). |
| **BrowserScan** | DETECTED | **NORMAL** | 0 abnormal signals detected [README.md:42](). |

Sources: [README.md:28-30](), [README.md:41-42](), [CHANGELOG.md:11-17]()

---

## Subsystems

- [Fingerprint Flags Reference](#6.1) — Detailed reference for every binary flag.
- [Humanize Behavioral Layer](#6.2) — How `humanize=True` enables realistic mouse and keyboard patterns.
- [GeoIP Auto-Detection](#6.3) — Automatically syncing timezone and locale with your proxy IP.

---

# Page: Fingerprint Flags Reference

# Fingerprint Flags Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [cloakbrowser/config.py](cloakbrowser/config.py)
- [dotnet/src/CloakBrowser/Config.cs](dotnet/src/CloakBrowser/Config.cs)
- [dotnet/tests/CloakBrowser.Tests/ConfigTests.cs](dotnet/tests/CloakBrowser.Tests/ConfigTests.cs)
- [js/src/args.ts](js/src/args.ts)
- [js/src/config.ts](js/src/config.ts)
- [js/tests/config.test.ts](js/tests/config.test.ts)
- [tests/test_build_args.py](tests/test_build_args.py)
- [tests/test_config.py](tests/test_config.py)

</details>



This page documents every `--fingerprint-*` and related Chromium command-line flag recognized by the patched CloakBrowser binary. It covers what browser surface each flag controls, the per-platform defaults applied automatically on each launch, and the additional flags available for manual customization.

For a conceptual explanation of how the stealth system works end-to-end (including the C++ patches these flags activate), see **6. Stealth System**. For the Python and JavaScript functions that assemble and pass these flags, see `cloakbrowser/config.py` [cloakbrowser/config.py:54-76]() and `js/src/config.ts` [js/src/config.ts:31-39]().

---

## How Fingerprint Flags Work

The patched Chromium binary exposes a set of custom command-line flags. These flags are **not** standard Chromium flags — they are read by source-level C++ patches compiled into the binary. Without the patched binary, these flags are silently ignored.

A single integer **seed** (`--fingerprint`) drives the majority of patches. All seed-based surfaces (canvas, WebGL, audio, fonts, client rects) derive their spoofed values from this one number, so they remain internally consistent — they look like they came from a single real machine rather than independent random noise.

The remaining flags override specific browser metadata values (platform, GPU strings, hardware concurrency, etc.) that must match the OS/hardware profile being impersonated.

**Diagram: Seed-to-surface propagation**

```mermaid
graph TD
    seed["--fingerprint=SEED (10000-99999)"]
    canvas["Canvas fingerprint"]
    webgl["WebGL rendering output"]
    audio["Audio processing fingerprint"]
    fonts["Font enumeration results"]
    rects["Client rect measurements"]

    seed --> canvas
    seed --> webgl
    seed --> audio
    seed --> fonts
    seed --> rects

    platform["--fingerprint-platform"]
    ua["navigator.platform\nUser-Agent OS string\nGPU pool selection"]
    platform --> ua

    concurrency["--fingerprint-hardware-concurrency"]
    hc["navigator.hardwareConcurrency"]
    concurrency --> hc

    gpuvendor["--fingerprint-gpu-vendor"]
    gpurenderer["--fingerprint-gpu-renderer"]
    webglunmasked["WebGL UNMASKED_VENDOR_WEBGL\nWebGL UNMASKED_RENDERER_WEBGL"]
    gpuvendor --> webglunmasked
    gpurenderer --> webglunmasked

    brand["--fingerprint-brand"]
    brandver["--fingerprint-brand-version"]
    platformver["--fingerprint-platform-version"]
    uat["User-Agent string\nClient Hints (Sec-CH-UA)"]
    brand --> uat
    brandver --> uat
    platformver --> uat

    location["--fingerprint-location"]
    geo["navigator.geolocation"]
    location --> geo

    timezone["--timezone"]
    tz["Intl.DateTimeFormat\nDate timezone offsets"]
    timezone --> tz
```

Sources: [cloakbrowser/config.py:54-76](), [js/src/args.ts:15-71]()

---

## Default Flags

These flags are assembled and passed automatically by `get_default_stealth_args()` (Python) [cloakbrowser/config.py:54-76](), `getDefaultStealthArgs()` (JS) [js/src/config.ts:31-39](), or `GetDefaultStealthArgs()` (.NET) [dotnet/src/CloakBrowser/Config.cs:70-94]() on every launch call. Starting with recent binary versions, hardware concurrency, device memory, screen, and GPU strings are auto-generated from the seed and platform.

| Flag | Linux/Windows Default | macOS Default | Browser Surface Controlled |
|---|---|---|---|
| `--fingerprint` | Random `10000`–`99999` | Random `10000`–`99999` | Master seed: canvas, WebGL output, audio fingerprint, font enumeration, client rect measurements |
| `--fingerprint-platform` | `windows` | `macos` | `navigator.platform`, User-Agent OS component, GPU string pool selection |

> **Note:** On macOS, CloakBrowser skips general platform/GPU spoofing and runs as a native Mac browser to avoid detectable mismatches in fonts and GPU behavior [cloakbrowser/config.py:57-59](). On Linux and Windows, it defaults to a Windows profile [cloakbrowser/config.py:72-76]().

Sources: [cloakbrowser/config.py:54-76](), [js/tests/config.test.ts:23-45](), [dotnet/src/CloakBrowser/Config.cs:70-94]()

---

## Additional Flags

These flags are recognized by the binary but **not always included in the default stealth args**. Pass them via the `args` parameter of `launch()` to customize specific surfaces.

| Flag | Value Format | Browser Surface Controlled |
|---|---|---|
| `--fingerprint-brand` | String: `Chrome`, `Edge`, etc. | Browser brand name in User-Agent string and `Sec-CH-UA` Client Hints |
| `--fingerprint-brand-version` | Version string, e.g. `130` | Brand version in User-Agent string and `Sec-CH-UA` Client Hints |
| `--fingerprint-platform-version` | Version string, e.g. `10.0.0` | `Sec-CH-UA-Platform-Version` Client Hint |
| `--fingerprint-hardware-concurrency` | Integer | `navigator.hardwareConcurrency` value |
| `--fingerprint-gpu-vendor` | String | Overrides the `UNMASKED_VENDOR_WEBGL` string |
| `--fingerprint-gpu-renderer` | String | Overrides the `UNMASKED_RENDERER_WEBGL` string |
| `--fingerprint-location` | `lat,lon`, e.g. `40.7128,-74.0060` | `navigator.geolocation` coordinates |
| `--timezone` | IANA timezone, e.g. `America/New_York` | `Intl.DateTimeFormat` resolved timezone, `Date` offset behavior |
| `--fingerprint-timezone` | IANA timezone | Alias for `--timezone`, set via `timezone` parameter [js/src/args.ts:55-62]() |
| `--fingerprint-locale` | BCP 47 locale, e.g. `en-US` | Browser language and `navigator.languages` list |
| `--fingerprint-storage-quota` | Integer (bytes) | Normalizes StorageBuckets API quota to close incognito detection vectors |
| `--fingerprint-taskbar-height`| Integer (pixels) | Controls `availHeight` calculation by subtracting taskbar height from screen height |
| `--fingerprint-sapi-voices` | Integer | Spoofs the number of available SpeechSynthesis voices |
| `--fingerprint-noise` | Boolean | Enables/disables rendering noise injection (Canvas/WebGL) |
| `--fingerprint-webrtc-ip` | IP or `auto` | Spoofs WebRTC ICE candidates. `auto` resolves via proxy [tests/test_build_args.py:178-185]() |
| `--fingerprint-allow-3p-cookies`| Boolean | Controls third-party cookie blocking behavior |
| `--fingerprint-windows-font-metrics`| Boolean | Activates high-fidelity Windows font profiles [js/src/args.ts:45-53]() |

Sources: [js/src/args.ts:15-71](), [tests/test_build_args.py:6-35](), [dotnet/tests/CloakBrowser.Tests/ConfigTests.cs:63-78]()

---

## Platform Branching Logic

The default arg assembly uses the runtime OS to decide which flags to emit. This diagram maps platform identity to the exact code paths and output arguments.

**Diagram: `get_default_stealth_args` branching**

```mermaid
flowchart TD
    Start(["launch() called"])
    StealthCheck{"stealthArgs\nenabled?"}
    Start --> StealthCheck

    StealthCheck -->|"No"| NoArgs["No fingerprint flags added\n(user supplies their own via args=[])"]

    StealthCheck -->|"Yes"| Seed["Generate random seed\nrandom.randint(10000, 99999)"]

    Seed --> Base["Base args always added:\n--no-sandbox\n--fingerprint=SEED"]

    Base --> OSCheck{"platform.system()"}

    OSCheck -->|"Darwin"| MacArgs["Add:\n--fingerprint-platform=macos"]
    OSCheck -->|"Linux / Windows"| WinArgs["Add:\n--fingerprint-platform=windows"]

    MacArgs --> PassToChromium["Pass all args to patched Chromium binary"]
    WinArgs --> PassToChromium
    Base --> PassToChromium
```

Sources: [cloakbrowser/config.py:54-76](), [js/tests/config.test.ts:23-45](), [dotnet/src/CloakBrowser/Config.cs:70-94]()

---

## Code Entity Map

**Diagram: Flag assembly — from launch call to binary args**

```mermaid
graph LR
    subgraph Python["Python Package"]
        PyLaunch["browser.py\nlaunch()"]
        PyConfig["config.py\nget_default_stealth_args()"]
        PyBuildArgs["browser.py\nbuild_args()"]
    end

    subgraph JS["JavaScript Package"]
        JSLaunch["playwright.ts\nlaunch()"]
        JSConfig["config.ts\ngetDefaultStealthArgs()"]
        JSBuildArgs["args.ts\nbuildArgs()"]
    end

    subgraph Flags["Assembled Flag Sets"]
        DefaultFlags["Default stealth args\n(platform-conditional)"]
        UserArgs["User-supplied args=[]\nfrom launch() call"]
        TimezoneLocale["--fingerprint-timezone\n--lang / --fingerprint-locale"]
    end

    subgraph Binary["Patched Chromium Binary"]
        ChromiumBin["chrome / Chromium.app\n(Source-level C++ patches)"]
    end

    PyLaunch --> PyBuildArgs
    PyBuildArgs --> PyConfig
    JSLaunch --> JSBuildArgs
    
    JSBuildArgs --> JSConfig

    PyConfig --> DefaultFlags
    JSConfig --> DefaultFlags
    
    JSBuildArgs --> TimezoneLocale
    PyBuildArgs --> TimezoneLocale

    DefaultFlags --> ChromiumBin
    UserArgs --> ChromiumBin
    TimezoneLocale --> ChromiumBin
```

Sources: [js/src/args.ts:15-71](), [cloakbrowser/config.py:54-76](), [tests/test_build_args.py:3-4]()

---

## Flag Details

### `--fingerprint`
- **Type:** Integer, range `10000`–`99999`
- **Role:** Master seed for all seed-derived patches.
- **Surfaces affected:** Canvas 2D fingerprint, WebGL rendering noise, AudioContext fingerprint, font metric perturbation, `getBoundingClientRect` / `getClientRects` output.
- **Default:** A new random integer is generated per `launch()` call [cloakbrowser/config.py:60-60](), [js/tests/config.test.ts:39-45](), [dotnet/src/CloakBrowser/Config.cs:73-78]().

### `--fingerprint-platform`
- **Type:** String enum: `windows`, `macos`, `linux`
- **Role:** Tells the binary which OS profile to impersonate. Controls `navigator.platform` and the OS component of the User-Agent string.
- **Linux/Windows default:** `windows` [cloakbrowser/config.py:76-76]().
- **macOS default:** `macos` [cloakbrowser/config.py:70-70]().

### `--timezone` / `--fingerprint-timezone`
- **Type:** IANA timezone identifier, e.g. `America/New_York`
- **Role:** Sets the browser's timezone natively via C++ patch, replacing detectable CDP-level emulation.
- **Implementation:** The `timezone` parameter in `launch()` is injected as `--fingerprint-timezone` in the argument builder [js/src/args.ts:55-62]() and [tests/test_build_args.py:6-9]().

### `--fingerprint-locale`
- **Type:** BCP 47 locale string, e.g. `en-US`
- **Role:** Sets the browser's language natively. 
- **Implementation:** Injected alongside `--lang` when the `locale` parameter is passed to `launch()` [js/src/args.ts:63-71]() and [tests/test_build_args.py:12-16]().

### `--fingerprint-webrtc-ip`
- **Type:** String (IP address or `auto`)
- **Role:** Spoofs the IP address reported by WebRTC ICE candidates.
- **Implementation:** When set to `auto`, the wrapper resolves the exit IP of the provided proxy and injects the actual IP as the flag value [tests/test_build_args.py:178-185]().

Sources: [cloakbrowser/config.py:54-76](), [js/src/args.ts:15-71](), [tests/test_build_args.py:6-185](), [dotnet/src/CloakBrowser/Config.cs:70-94]()

---

# Page: Humanize Behavioral Layer

# Humanize Behavioral Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/human/__init__.py](cloakbrowser/human/__init__.py)
- [cloakbrowser/human/actionability.py](cloakbrowser/human/actionability.py)
- [cloakbrowser/human/actionability_async.py](cloakbrowser/human/actionability_async.py)
- [cloakbrowser/human/config.py](cloakbrowser/human/config.py)
- [cloakbrowser/human/keyboard.py](cloakbrowser/human/keyboard.py)
- [cloakbrowser/human/keyboard_async.py](cloakbrowser/human/keyboard_async.py)
- [cloakbrowser/human/mouse.py](cloakbrowser/human/mouse.py)
- [cloakbrowser/human/mouse_async.py](cloakbrowser/human/mouse_async.py)
- [cloakbrowser/human/scroll.py](cloakbrowser/human/scroll.py)
- [cloakbrowser/human/scroll_async.py](cloakbrowser/human/scroll_async.py)
- [js/src/human-puppeteer/scroll.ts](js/src/human-puppeteer/scroll.ts)
- [js/src/human/actionability.ts](js/src/human/actionability.ts)
- [js/src/human/config.ts](js/src/human/config.ts)
- [js/src/human/elementhandle.ts](js/src/human/elementhandle.ts)
- [js/src/human/index.ts](js/src/human/index.ts)
- [js/src/human/keyboard.ts](js/src/human/keyboard.ts)
- [js/src/human/mouse.ts](js/src/human/mouse.ts)
- [js/src/human/scroll.ts](js/src/human/scroll.ts)
- [js/tests/humanize.test.ts](js/tests/humanize.test.ts)
- [tests/test_humanize_unit.py](tests/test_humanize_unit.py)
- [tests/test_stealth_reproduction_110.py](tests/test_stealth_reproduction_110.py)

</details>



The **Humanize Behavioral Layer** is a sophisticated subsystem within CloakBrowser designed to bypass behavioral analysis used by advanced bot detection services (e.g., reCAPTCHA v3, Cloudflare Turnstile, DataDome). It replaces the "teleporting" mouse movements and instantaneous typing typical of automation frameworks with realistic, non-linear, and randomized human-like interactions across Python, JavaScript, and .NET.

## Overview

When `humanize=True` (Python), `humanize: true` (JS), or `Humanize = true` (.NET) is passed to launch functions, CloakBrowser activates a suite of patches via `patch_browser`/`patch_context`/`patch_page` (Python) or `patchBrowser`/`patchContext`/`patchPage` (JS) [[cloakbrowser/human/__init__.py:1-12]](), [[js/src/human/index.ts:1-23]](). In .NET, where monkey-patching is restricted by sealed interfaces, a transparent decorator pattern is used via a Roslyn source generator [[dotnet/src/CloakBrowser/Config.cs:20-25]]().

### Key Capabilities
*   **Bézier Curve Mouse Movement:** Replaces straight-line jumps with organic, curved paths using cubic Bézier math [[cloakbrowser/human/mouse.py:32-41]](), [[js/tests/humanize.test.ts:147-157]]().
*   **Per-Character Typing:** Simulates realistic keystroke timing, including shift-key delays and intentional mistype simulation [[cloakbrowser/human/keyboard.py:66-105]](), [[js/src/human/keyboard.ts:28-34]]().
*   **Inertial Scrolling:** Implements mouse wheel acceleration, deceleration, and overshoot to mimic physical scrolling [[cloakbrowser/human/scroll.py:136-163]](), [[js/src/human/scroll.ts:105-137]]().
*   **Idle Micro-movements:** Optionally adds subtle cursor drift between actions to simulate a resting human hand [[cloakbrowser/human/mouse.py:122-132]](), [[js/src/human/mouse.js:27]]().
*   **Cursor State Tracking:** Maintains a persistent `_CursorState` (Python) or `CursorState` (JS) to ensure movements start from the last known position rather than (0,0) [[cloakbrowser/human/__init__.py:189-196]](), [[js/src/human/index.ts:144-148]]().
*   **Stealth DOM Evaluation:** Uses CDP Isolated Worlds for `isInputElement` and `isSelectorFocused` checks to remain invisible to main-world JS monkey-patches [[cloakbrowser/human/__init__.py:70-139]](), [[js/src/human/index.ts:43-141]]().
*   **Actionability Engine:** Implements a retry loop with backoff ([100, 250, 500, 1000]ms) for `attached`, `visible`, `stable`, `enabled`, and `editable` checks [[cloakbrowser/human/actionability.py:73-86]](), [[js/src/human/actionability.ts:80-91]]().

**Sources:** [[cloakbrowser/human/__init__.py:1-12]](), [[js/src/human/index.ts:1-23]](), [[js/src/human/config.ts:1-6]]().

---

## Configuration: HumanConfig and Presets

The behavioral engine is governed by the `HumanConfig` dataclass (Python) or interface (JS). This object centralizes all numeric parameters for humanization.

### Built-in Presets
CloakBrowser provides two primary presets:
1.  **`default`**: Balanced speed and humanization suitable for most use cases [[cloakbrowser/human/config.py:170]](), [[js/src/human/config.ts:83-139]]().
2.  **`careful`**: Slower typing, longer aiming delays, and mandatory idle micro-movements between actions [[cloakbrowser/human/config.py:138-166]](), [[js/src/human/config.ts:145-180]]().

### Parameters Reference
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `typing_delay` | `float` | Base delay between keystrokes in ms (Default: 70) [[js/src/human/config.ts:85]](). |
| `mistype_chance` | `float` | Probability (0-1) of hitting an adjacent key [[js/src/human/config.ts:94]](). |
| `mouse_steps_divisor` | `float` | Controls the density of points in a Bézier curve relative to distance [[js/src/human/config.ts:99]](). |
| `scroll_delta_base` | `Range` | The amount of pixels moved per "click" of the scroll wheel [[js/src/human/config.ts:120]](). |
| `idle_between_actions`| `bool` | If true, performs micro-movements while waiting for next command [[js/src/human/config.ts:67]](). |
| `mouse_wobble_max` | `float` | Maximum amplitude of random deviation during movement [[js/src/human/config.ts:102]](). |

### Configuration Resolution
The `resolve_config()` (Python) and `resolveConfig()` (JS) functions merge a named preset with optional user overrides to produce a final `HumanConfig` instance [[cloakbrowser/human/config.py:175-201]](), [[js/src/human/config.ts:196-208]]().

**Sources:** [[cloakbrowser/human/config.py:71-131]](), [[js/src/human/config.ts:12-69]](), [[js/tests/humanize.test.ts:9-69]]().

---

## Architecture and Data Flow

The humanize layer operates by monkey-patching the `Page`, `BrowserContext`, and `Locator` classes (Python/JS) or using decorators (.NET). When a user calls a method like `page.click()`, the patched version calculates movements before calling the "original" unpatched methods.

Title: Humanize Layer Interaction Flow
```mermaid
graph TD
    subgraph "Automation Script"
        A["page.fill('#login', 'pass')"]
    end

    subgraph "Humanize Behavioral Layer"
        B["patchPage / patch_page"]
        C["resolveConfig / resolve_config"]
        D["CursorState / _CursorState"]
        E["humanType / human_type"]
        F["humanMove / human_move"]
        S["StealthEval / _SyncIsolatedWorld"]
    end

    subgraph "Playwright/Puppeteer Core"
        G["_original.mouse.move"]
        H["_original.keyboard.down"]
        I["CDP Input.dispatchKeyEvent"]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    B -- "isInputElement" --> S
    E --> F
    F --> G
    E --> H
    E -- "Shift Symbols" --> I
```
**Sources:** [[cloakbrowser/human/__init__.py:189-196]](), [[js/src/human/index.ts:149-153]](), [[js/src/human/keyboard.ts:161-189]](), [[js/src/human/index.ts:58-92]]().

---

## Implementation Details

### Mouse Movement (Bézier Curves)
CloakBrowser uses a cubic Bézier curve calculation to generate intermediate points between the current position and the target [[cloakbrowser/human/mouse.py:32-41]](). 
*   **Wobble:** A `mouse_wobble_max` factor adds random deviation to the path [[js/src/human/config.ts:102]]().
*   **Bursting:** Movement is broken into "bursts" with micro-pauses defined by `mouse_burst_size` and `mouse_burst_pause` [[js/src/human/config.ts:105-106]]().

### Keyboard Simulation
The `human_type` function processes strings character-by-character:
1.  **Mistype Simulation:** If a mistype occurs (via `mistype_chance`), the system types an adjacent key, pauses, hits 'Backspace', then types the correct key [[js/src/human/keyboard.ts:104-112]]().
2.  **Stealth Shift Symbols:** When a CDP session is available, shift symbols are typed via `Input.dispatchKeyEvent` to produce `isTrusted=true` events without triggering `evaluate` stack traces [[js/src/human/keyboard.ts:161-189]]().

### Scroll Logic
Scrolling via `scrollToElement` or `humanScrollIntoView` involves:
1.  Moving mouse to a random neutral viewport area [[js/src/human/scroll.ts:83-88]]().
2.  Inertia simulation loop: acceleration steps, cruise, and deceleration [[js/src/human/scroll.ts:105-120]]().
3.  **Smooth Wheel:** Breaks each logical click into a burst of small wheel events [[js/src/human/scroll.ts:29-40]]().
4.  **Overshoot:** Optional chance to scroll past target and then correct back [[js/src/human/scroll.ts:140-151]]().

Title: Behavioral Logic Hierarchy
```mermaid
classDiagram
    class HumanConfig {
        +typing_delay: number
        +mouse_min_steps: number
        +mistype_chance: number
        +scroll_delta_base: [number, number]
    }
    class CursorState {
        +x: number
        +y: number
        +initialized: boolean
    }
    class MouseEngine {
        +humanMove()
        +humanClick()
        +clickTarget()
        +humanIdle()
    }
    class KeyboardEngine {
        +humanType()
    }
    class ScrollEngine {
        +humanScrollIntoView()
        +smoothWheel()
    }

    HumanConfig --* MouseEngine
    HumanConfig --* KeyboardEngine
    HumanConfig --* ScrollEngine
    CursorState -- MouseEngine : tracks
```
**Sources:** [[js/src/human/config.ts:12-69]](), [[js/src/human/index.ts:149-153]](), [[js/src/human/mouse.js:1-10]](), [[js/src/human/keyboard.ts:1-10]](), [[js/src/human/scroll.ts:1-8]]().

---

## Patching Mechanism

### 1. Interception Levels
CloakBrowser patches standard methods: `click()`, `fill()`, `type()`, `hover()`, `dblclick()`, `scroll`, `drag_to()`. For example, `page.click(selector)` will:
1.  Ensure actionability (attached, visible, stable) [[js/src/human/actionability.ts:149-190]]().
2.  Scroll element into view using humanized logic if off-screen [[js/src/human/elementhandle.ts:157-165]]().
3.  Calculate a random `clickTarget` within the bounding box [[js/src/human/elementhandle.ts:171]]().
4.  Check pointer events via `elementFromPoint` in a CDP isolated world [[js/src/human/actionability.ts:197-210]]().

### 2. Locator & ElementHandle
The Playwright `Locator` class and `ElementHandle` instances are patched. Methods like `page.locator("button").click()` or an element returned by `page.$()` automatically use the behavioral engine [[js/src/human/elementhandle.ts:83-110]](), [[cloakbrowser/human/__init__.py:112-135]]().

### 3. Python Async & Sync
The Python package provides full parity. Every sync function (e.g., `patch_page`) has an `_async` counterpart (e.g., `patch_page_async`) using `asyncio.sleep` and `await` [[cloakbrowser/human/mouse_async.py:24-66]](), [[cloakbrowser/human/keyboard_async.py:27-66]]().

**Sources:** [[cloakbrowser/human/__init__.py:145-173]](), [[js/src/human/index.ts:25-36]](), [[js/src/human/elementhandle.ts:1-23]](), [[cloakbrowser/human/scroll_async.py:68-179]]().

---

# Page: GeoIP Auto-Detection

# GeoIP Auto-Detection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bin/docker-entrypoint.sh](bin/docker-entrypoint.sh)
- [cloakbrowser/geoip.py](cloakbrowser/geoip.py)
- [dotnet/src/CloakBrowser/GeoIp.cs](dotnet/src/CloakBrowser/GeoIp.cs)
- [dotnet/src/CloakBrowser/LaunchOptions.cs](dotnet/src/CloakBrowser/LaunchOptions.cs)
- [dotnet/tests/CloakBrowser.Tests/MiscTests.cs](dotnet/tests/CloakBrowser.Tests/MiscTests.cs)
- [js/src/geoip.ts](js/src/geoip.ts)
- [js/tests/geoip.test.ts](js/tests/geoip.test.ts)
- [pyproject.toml](pyproject.toml)
- [tests/test_geoip.py](tests/test_geoip.py)

</details>



The GeoIP auto-detection feature allows CloakBrowser to automatically align the browser's fingerprint (specifically timezone and locale) with the physical location of the proxy server being used. This prevents a common "mismatch" signal used by bot detection services where a browser claims to be in one timezone while its IP address originates from another.

## Overview

When `geoip=True` is passed to the `launch()` function, CloakBrowser attempts to resolve the proxy's geographic location before starting the browser process. The resolved values are then injected directly into the Stealth Chromium binary via command-line flags (`--fingerprint-timezone`, `--fingerprint-locale`, and `--fingerprint-webrtc-ip`), ensuring they are active from the very first request [cloakbrowser/browser.py:114-116](), [js/src/playwright.ts:83-85](), [dotnet/src/CloakBrowser/LaunchOptions.cs:29-30]().

### Key Features
*   **Automatic Synchronization**: Automatically sets `--fingerprint-timezone` and `--lang` (or `--fingerprint-locale`) based on the proxy IP [js/src/geoip.ts:123-127](), [cloakbrowser/geoip.py:140-147](), [dotnet/src/CloakBrowser/GeoIp.cs:131-133]().
*   **Local Database**: Uses a local GeoLite2-City.mmdb (~70 MB) for fast, privacy-preserving lookups [js/src/geoip.ts:7-9](), [cloakbrowser/geoip.py:7-9]().
*   **Exit IP Resolution**: Attempts to find the real "exit IP" of the proxy (using a CONNECT tunnel or SOCKS tunnel) to handle cases where the proxy gateway is in a different region than the exit node [cloakbrowser/geoip.py:209-212](), [js/src/geoip.ts:181-185]().
*   **WebRTC Spoofing**: The resolved exit IP is passed to the binary via `--fingerprint-webrtc-ip`, preventing leaks of the local machine's public IP through WebRTC [cloakbrowser/browser.py:151-153](), [js/src/playwright.ts:106-108]().
*   **Fallback Logic**: If the exit IP cannot be determined, it falls back to resolving the proxy hostname's IP via DNS [js/src/geoip.ts:108](), [cloakbrowser/geoip.py:126-127](), [dotnet/src/CloakBrowser/GeoIp.cs:114-115]().
*   **Resolution Timeout**: To prevent hanging browser launch, the process is bounded by a timeout (default 5s), configurable via `CLOAKBROWSER_GEOIP_TIMEOUT_SECONDS` [cloakbrowser/geoip.py:32-33](), [js/src/geoip.ts:25](), [dotnet/src/CloakBrowser/GeoIp.cs:26-27]().

## Installation

GeoIP is an optional feature to keep the base package weight low.

### Python
Install the `geoip` extra to pull in the `geoip2` and `socksio` dependencies.
```bash
pip install cloakbrowser[geoip]
```
Sources: [pyproject.toml:58](), [cloakbrowser/geoip.py:3-6]()

### JavaScript / Node.js
Install the `mmdb-lib` peer dependency.
```bash
npm install mmdb-lib
```
Sources: [js/src/geoip.ts:4-5]()

## Implementation Detail

### Data Flow: Proxy to Browser Flags

The following diagram illustrates how a proxy URL is transformed into browser configuration flags across the different language implementations.

**Proxy Geo-Resolution Flow**
```mermaid
graph TD
    A["launch(geoip=True, proxy='...')"] --> B["maybe_resolve_geoip() / maybeResolveGeoip()"]
    B --> C{"Is geoip=True?"}
    C -- "Yes" --> D["resolve_proxy_geo_with_ip() / resolveProxyGeo()"]
    C -- "No" --> End["Launch with defaults"]
    
    D --> E["_resolve_exit_ip() / resolveExitIp()"]
    E -- "Failure" --> F["_resolve_proxy_ip() / resolveProxyIp()"]
    E -- "Success" --> G["Query GeoLite2-City.mmdb"]
    F --> G
    
    G --> H["Extract time_zone & iso_code"]
    H --> I["Map iso_code via COUNTRY_LOCALE_MAP"]
    I --> J["Return (timezone, locale, ip)"]
    
    J --> K["Append --fingerprint-timezone=..."]
    J --> L["Append --fingerprint-locale=... / --lang=..."]
    J --> N["Append --fingerprint-webrtc-ip=..."]
    K --> M["Spawn Stealth Chromium"]
    L --> M
    N --> M
```
Sources: [cloakbrowser/browser.py:114-153](), [js/src/geoip.ts:81-131](), [cloakbrowser/geoip.py:93-151](), [dotnet/src/CloakBrowser/GeoIp.cs:97-151]()

### Exit IP Resolution
CloakBrowser performs an "Exit IP" check by making a request to an IP echo service (like `api.ipify.org`) *through* the configured proxy [cloakbrowser/geoip.py:181-185](), [js/src/geoip.ts:181-185](). 

*   **Python**: Uses `httpx` with proxy support. If SOCKS proxies are used, it handles them via `httpx` SOCKS support (requires `socksio`) [cloakbrowser/geoip.py:209-245]().
*   **JavaScript**: For SOCKS5, it uses `socks-proxy-agent` [js/src/geoip.ts:192-202](). For HTTP/HTTPS, it implements a manual `CONNECT` tunnel using `node:http` to establish a socket and then performs an `https` request over that socket to an echo service [js/src/geoip.ts:228-269]().
*   **Direct Connection**: If no proxy is provided but `geoip=True` is set, CloakBrowser queries the echo services directly to determine the machine's public IP and adjust the timezone/locale accordingly [cloakbrowser/geoip.py:101-103](), [js/src/geoip.ts:78-80](), [dotnet/src/CloakBrowser/GeoIp.cs:93-95]().

### Database Management
*   **Storage**: The database is stored in `~/.cloakbrowser/geoip/GeoLite2-City.mmdb` [cloakbrowser/geoip.py:270-273](), [js/src/geoip.ts:316-318]().
*   **Update Interval**: The system checks the file age every time it is used. If the database is older than 30 days (`GEOIP_UPDATE_INTERVAL`), a background update is triggered [cloakbrowser/geoip.py:31](), [js/src/geoip.ts:24](), [dotnet/src/CloakBrowser/GeoIp.cs:21]().
*   **Atomic Updates**: Downloads are performed to a `.tmp` file and renamed only upon successful completion to prevent database corruption [cloakbrowser/geoip.py:302-306](), [js/src/geoip.ts:340-343]().
*   **Concurrency**: A lock (`_GEOIP_DOWNLOAD_LOCK` in Python, `GeoIpDownloadGate` in .NET) ensures that multiple concurrent browser launches do not trigger multiple simultaneous 70MB downloads [cloakbrowser/geoip.py:37](), [dotnet/src/CloakBrowser/GeoIp.cs:25](), [js/tests/geoip.test.ts:119-153]().

## Country to Locale Mapping

Because GeoIP databases provide ISO country codes (e.g., `US`) but browsers require BCP 47 locales (e.g., `en-US`), CloakBrowser maintains a `COUNTRY_LOCALE_MAP` covering 132 countries, including common residential and mobile proxy exit regions [cloakbrowser/geoip.py:40-77](), [js/src/geoip.ts:28-65](), [dotnet/src/CloakBrowser/GeoIp.cs:38-77]().

| ISO Code | BCP 47 Locale | ISO Code | BCP 47 Locale |
| :--- | :--- | :--- | :--- |
| US | en-US | JP | ja-JP |
| GB | en-GB | DE | de-DE |
| FR | fr-FR | BR | pt-BR |
| ES | es-ES | RU | ru-RU |
| CN | zh-CN | KR | ko-KR |
| SI | sl-SI | PE | es-PE |

Sources: [cloakbrowser/geoip.py:40-77](), [js/src/geoip.ts:28-65](), [dotnet/src/CloakBrowser/GeoIp.cs:38-77](), [tests/test_geoip.py:56-69]()

## Code Entities

### Functions and Classes
| Language | Entity | Role |
| :--- | :--- | :--- |
| Python | `resolve_proxy_geo()` | Entry point for resolving (tz, locale) from a URL. [cloakbrowser/geoip.py:80]() |
| Python | `maybe_resolve_geoip()` | Logic deciding if resolution is needed based on params and raw flags. [cloakbrowser/browser.py:114]() |
| JS | `resolveProxyGeo()` | Async function returning a `GeoResult` object. [js/src/geoip.ts:81]() |
| JS | `resolveExitIp()` | Node.js implementation of the CONNECT/SOCKS tunnel resolution. [js/src/geoip.ts:181]() |
| .NET | `GeoIp` | Static class containing `ResolveProxyGeoAsync()` and the locale map. [dotnet/src/CloakBrowser/GeoIp.cs:15]() |

### Constants and Environment
| Constant | Value / Purpose |
| :--- | :--- |
| `GEOIP_DB_URL` | P3TERX mirror for GeoLite2-City.mmdb (no license key required). [cloakbrowser/geoip.py:27](), [js/src/geoip.ts:21](), [dotnet/src/CloakBrowser/GeoIp.cs:18-19]() |
| `GEOIP_UPDATE_INTERVAL` | 30 days (seconds in Python, MS in JS). [cloakbrowser/geoip.py:31](), [js/src/geoip.ts:24]() |
| `CLOAKBROWSER_GEOIP_TIMEOUT_SECONDS` | Env var to override the default 5s resolution budget. [cloakbrowser/geoip.py:33](), [js/src/geoip.ts:134](), [dotnet/src/CloakBrowser/GeoIp.cs:27]() |

**GeoIP System Architecture**
```mermaid
classDiagram
    class GeoIPModule {
        +resolve_proxy_geo(proxy_url)
        +resolve_proxy_geo_with_ip(proxy_url)
        +resolveProxyGeo(proxyUrl)
        +ResolveProxyGeoAsync(proxyUrl)
        +_ensure_geoip_db()
        +_resolve_exit_ip()
        +resolveExitIp()
    }
    class BrowserLauncher {
        +launch(geoip, proxy, timezone, locale)
        +maybe_resolve_geoip()
        +maybeResolveGeoip()
        +MaybeResolveGeoIpAsync()
    }
    class Config {
        +get_cache_dir()
        +getCacheDir()
    }
    class ProxyUtils {
        +ensureProxyScheme()
        +isSocksProxy()
    }
    
    BrowserLauncher ..> GeoIPModule : "calls resolve_proxy_geo / resolveProxyGeo"
    BrowserLauncher ..> ProxyUtils : "normalizes proxy URLs"
    GeoIPModule ..> Config : "uses for storage path"
    GeoIPModule ..> COUNTRY_LOCALE_MAP : "maps country to BCP 47"
```
Sources: [cloakbrowser/browser.py:114-143](), [cloakbrowser/geoip.py:36-66](), [js/src/geoip.ts:16-43](), [dotnet/src/CloakBrowser/GeoIp.cs:15-88](), [js/src/playwright.ts:83-85]()

---

# Page: Licensing and Pro Tier

# Licensing and Pro Tier

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [BINARY-LICENSE.md](BINARY-LICENSE.md)
- [LICENSE](LICENSE)
- [cloakbrowser/license.py](cloakbrowser/license.py)
- [dotnet/src/CloakBrowser/License.cs](dotnet/src/CloakBrowser/License.cs)
- [dotnet/tests/CloakBrowser.Tests/LicenseTests.cs](dotnet/tests/CloakBrowser.Tests/LicenseTests.cs)
- [js/src/license.ts](js/src/license.ts)
- [js/tests/license.test.ts](js/tests/license.test.ts)
- [tests/test_license.py](tests/test_license.py)
- [tests/test_license_error.py](tests/test_license_error.py)

</details>



CloakBrowser operates on a dual-tier model consisting of a **Free** tier and a **Pro** tier. While the Free tier provides the foundational stealth patches (up to version 146), the Pro tier (v150+) unlocks advanced features, continuous updates, and higher-fidelity fingerprinting. This page documents the licensing resolution logic, validation mechanics, and the error-handling system used to manage Pro access across Python, JavaScript, and .NET implementations.

### Tier Comparison

| Feature | Free Tier | Pro Tier |
| :--- | :--- | :--- |
| **Chromium Version** | Fixed (v146) | Latest (v150+) |
| **Binary Source** | Public GitHub Releases | Private `cloakbrowser.dev` CDN |
| **License Key** | Not Required | Required |
| **Session Limits** | Unlimited | Plan-dependent (Solo/Team/Business) |
| **Updates** | Manual | Automated via Pro API |

Sources: [cloakbrowser/license.py:1-20](), [js/src/license.ts:1-20](), [dotnet/src/CloakBrowser/License.cs:45-60](), [BINARY-LICENSE.md:23-35]()

---

## License Key Resolution

The wrapper implementations resolve the license key using a strict priority hierarchy. This ensures that developers can easily override keys for CI/CD or local development without modifying code.

### Resolution Priority
1.  **Explicit Parameter**: The `license_key` (Python) / `licenseKey` (JS/.NET) argument passed to `launch()`.
2.  **Environment Variable**: The `CLOAKBROWSER_LICENSE_KEY` variable.
3.  **Local File**: The contents of `~/.cloakbrowser/license.key`.

### Key Injection Logic
The Pro binary is designed to read the license key from its own environment. The wrappers use `build_launch_env` (Python/JS) or `BuildLaunchEnv` (.NET) to decide if the key needs to be injected into the child process:
*   **Injected**: If the key comes from a parameter or a custom file path (since the binary cannot see these).
*   **Not Injected**: If the key is already in the parent environment or exists in the default `~/.cloakbrowser/license.key` file (which the binary reads directly).

### License Resolution Flow
The following diagram illustrates how the system resolves and validates a key before launching the binary.

Title: License Key Resolution and Validation Pipeline
```mermaid
graph TD
    subgraph "Key Resolution Logic"
        START["launch(license_key=...)"] --> P["resolve_license_key()"]
        P --> P_PARAM["1. Explicit Param?"]
        P_PARAM -- "Yes" --> SRC_P["Source: Param"]
        P_PARAM -- "No" --> P_ENV["2. CLOAKBROWSER_LICENSE_KEY?"]
        P_ENV -- "Yes" --> SRC_E["Source: Env"]
        P_ENV -- "No" --> P_FILE["3. ~/.cloakbrowser/license.key?"]
        P_FILE -- "Yes" --> SRC_F["Source: DefaultFile"]
        P_FILE -- "No" --> SRC_N["Source: None"]
    end

    subgraph "Validation & Cache Layer"
        SRC_P --> VAL["validate_license()"]
        SRC_E --> VAL
        SRC_F --> VAL
        VAL --> CACHE{"Check .license_cache<br/>(TTL 24h)"}
        CACHE -- "Fresh & Valid" --> B["Launch Pro Binary"]
        CACHE -- "Stale/Missing" --> API["POST /api/license/validate"]
        API -- "200 OK" --> B
        API -- "Fail/Timeout" --> STALE{"Fallback to Stale Cache?"}
        STALE -- "Yes" --> B
        STALE -- "No" --> FREE["Fallback to Free Binary"]
    end
```
Sources: [cloakbrowser/license.py:19-68](), [js/src/license.ts:45-84](), [dotnet/src/CloakBrowser/License.cs:80-124](), [tests/test_license.py:27-68]()

---

## Validation and Caching

To minimize latency and avoid dependency on the license server for every launch, CloakBrowser implements a local caching mechanism.

### API Interactions
The wrappers communicate with `https://cloakbrowser.dev` for three primary functions:
1.  **Validation**: `validate_license()` / `validateLicense()` checks key validity and plan details.
2.  **Version Check**: `get_pro_latest_version()` determines the latest available Pro binary.
3.  **Session Tracking**: `get_active_session_count()` reports how many concurrent sessions are currently active for the key.

### Local Cache (`.license_cache`)
*   **Location**: Stored in the cache directory (default `~/.cloakbrowser/.license_cache`).
*   **Security**: The key itself is **never stored** in plain text; only the SHA-256 hash of the key is saved.
*   **TTL**: Valid for 24 hours (`LICENSE_CACHE_TTL` / `LICENSE_CACHE_TTL_MS`).
*   **Stale Fallback**: If the license server is unreachable, the system will allow a launch if a stale (expired) cache entry exists and was previously valid.

Sources: [cloakbrowser/license.py:26-47](), [js/src/license.ts:16-21](), [dotnet/src/CloakBrowser/License.cs:54-65](), [tests/test_license.py:70-138](), [js/tests/license.test.ts:88-158]()

---

## Error Handling and Exit Codes

When a Pro binary refuses to run (e.g., due to an expired license or session limit), it exits with a specific numeric code. The wrappers intercept these codes and raise a `CloakBrowserLicenseError` with a human-readable message.

### Pro Binary Exit Codes
| Code | Message |
| :--- | :--- |
| **76** | Session limit reached for your plan. |
| **77** | License key is invalid, expired, or missing. |
| **78** | License server unreachable (and no valid cache). |
| **79** | Local configuration problem (cache directory not writable). |

### Code Entity Mapping: Error Propagation
The system uses `license_error_message` (Python), `licenseErrorMessage` (JS), or `LicenseErrorMessage` (.NET) to parse exit codes from automation framework error strings (e.g., Playwright's `process did exit: exitCode=N` logs).

Title: Binary Exit Code to Wrapper Exception Mapping
```mermaid
sequenceDiagram
    participant B as "Pro Binary (C++)"
    participant W as "Wrapper (license.py / license.ts)"
    participant U as "User Application"

    B->>B: Check Session Limit
    Note over B: Limit Reached
    B->>W: exit(76)
    Note over W: Catch Launch Error
    W->>W: license_error_message(error_text)
    Note over W: Regex match "exitCode=76"
    W-->>U: throw CloakBrowserLicenseError("Session limit reached...")
```
Sources: [cloakbrowser/license.py:79-118](), [js/src/license.ts:52-82](), [dotnet/src/CloakBrowser/License.cs:81-108](), [tests/test_license_error.py:23-37]()

### Post-Handshake Denials
For denials that occur after a successful CDP connection (e.g., a session limit check that resolves late), the binary writes the exit code to a unique JSON file specified by the `CLOAKBROWSER_LICENSE_STATUS_FILE` environment variable. The wrapper's `read_denial_file()` / `readDenialFile()` function performs a destructive read of this file to surface the error on the next API call.

Sources: [cloakbrowser/license.py:127-179](), [js/src/license.ts:100-148](), [dotnet/src/CloakBrowser/License.cs:128-155]()

---

## CLI and Session Monitoring

The CLI provides tools to inspect the current license status and active session usage. This is particularly useful for debugging "Session limit reached" errors.

*   **Session Count**: The `info` command (or `doctor`) displays the current number of active sessions reported by the server via `get_active_session_count`.
*   **License Info**: Displays the plan type (e.g., `solo`, `team`) and expiration date.
*   **Welcome Banner**: On launch, a tier-aware banner is displayed to notify the user of their current status (Free vs. Pro).

For more information on using the CLI to diagnose license issues, see [CLI Reference](#7.2).

### Related Pages
- [Environment Variables Reference](#7.1) — Detailed list of variables including `CLOAKBROWSER_LICENSE_KEY`.
- [CLI Reference](#7.2) — Using the `info` command to check license and session status.

Sources: [cloakbrowser/license.py:214-235](), [js/src/license.ts:250-270](), [dotnet/src/CloakBrowser/License.cs:60-64]()

---

# Page: Environment Variables Reference

# Environment Variables Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/__main__.py](cloakbrowser/__main__.py)
- [cloakbrowser/config.py](cloakbrowser/config.py)
- [dotnet/src/CloakBrowser.Cli/Program.cs](dotnet/src/CloakBrowser.Cli/Program.cs)
- [dotnet/src/CloakBrowser/Config.cs](dotnet/src/CloakBrowser/Config.cs)
- [dotnet/src/CloakBrowser/Diagnostics.cs](dotnet/src/CloakBrowser/Diagnostics.cs)
- [dotnet/tests/CloakBrowser.Tests/ConfigTests.cs](dotnet/tests/CloakBrowser.Tests/ConfigTests.cs)
- [js/src/args.ts](js/src/args.ts)
- [js/src/cli.ts](js/src/cli.ts)
- [js/src/config.ts](js/src/config.ts)
- [js/tests/config.test.ts](js/tests/config.test.ts)
- [tests/test_build_args.py](tests/test_build_args.py)
- [tests/test_cli.py](tests/test_cli.py)
- [tests/test_config.py](tests/test_config.py)

</details>



This page provides a comprehensive reference for all environment variables used by CloakBrowser to manage binary resolution, caching, and licensing, alongside a consolidated summary of parameters for the `launch()` family of functions across Python, JavaScript, and .NET.

---

## Environment Variables

CloakBrowser uses environment variables to allow flexible configuration in CI/CD, Docker, and restricted environments without changing code.

| Variable | Type | Default | Purpose |
|:---|:---|:---|:---|
| `CLOAKBROWSER_BINARY_PATH` | Path | *(None)* | Local override for the Chromium executable path. Bypasses automatic downloads [cloakbrowser/config.py:180-184](), [js/src/config.ts:141-142](). |
| `CLOAKBROWSER_CACHE_DIR` | Path | `~/.cloakbrowser` | Root directory for downloaded binaries, license keys, and GeoIP databases [cloakbrowser/config.py:160-169](), [js/src/config.ts:118-122](). |
| `CLOAKBROWSER_DOWNLOAD_URL` | URL | `https://cloakbrowser.dev` | Primary mirror for binary downloads and Pro version API [cloakbrowser/config.py:189-191](), [js/src/config.ts:156-158](). |
| `CLOAKBROWSER_VERSION` | String | *(Bundled)* | Force a specific Chromium version (e.g., `148.0.7778.215.2`) [cloakbrowser/config.py:124-135](), [js/src/config.ts:75-87](). |
| `CLOAKBROWSER_LICENSE_KEY` | String | *(None)* | Pro license key for latest patches and Pro binaries [cloakbrowser/license.py:19-20](), [js/src/license.ts:48-51](), [dotnet/src/CloakBrowser/License.cs:86-87](). |
| `CLOAKBROWSER_AUTO_UPDATE` | Boolean | `true` | Enable background version checks and automatic binary updates [cloakbrowser/download.py:270-271](). |
| `CLOAKBROWSER_SKIP_CHECKSUM` | Boolean | `false` | Skip SHA-256 and Ed25519 signature verification (not recommended) [cloakbrowser/download.py:410-412](). |
| `CLOAKBROWSER_BACKEND` | String | `playwright` | (Python only) Switch between `playwright` and `patchright` backends [cloakbrowser/browser.py:109-109](). |
| `CLOAKBROWSER_RELEASE_CHANNEL`| String | `stable` | Select `stable` or `preview` binary release channels [cloakbrowser/config.py:107-114](), [js/src/config.ts:70-73](). |

**Sources:** [cloakbrowser/config.py:107-191](), [js/src/config.ts:70-158](), [cloakbrowser/license.py:19-30](), [dotnet/src/CloakBrowser/Config.cs:119-150]()

---

## Implementation and Data Flow

Environment variables are resolved early in the `ensure_binary` (Python), `ensureBinary` (JS), or `EnsureBinaryAsync` (.NET) lifecycle. If `CLOAKBROWSER_BINARY_PATH` is present, all download and version logic is bypassed [cloakbrowser/config.py:180-184](), [js/src/config.ts:141-142]().

### Environment Resolution Diagram

The following diagram shows how environment variables map to internal configuration entities and functions across the different language implementations.

```mermaid
graph TD
    subgraph "EnvVars" ["Environment Variables"]
        EBP["CLOAKBROWSER_BINARY_PATH"]
        ECD["CLOAKBROWSER_CACHE_DIR"]
        ELK["CLOAKBROWSER_LICENSE_KEY"]
        ECV["CLOAKBROWSER_VERSION"]
    end

    subgraph "PythonEntities" ["Python: cloakbrowser/"]
        PY_CFG_LBO["config.py: get_local_binary_override()"]
        PY_CFG_GCD["config.py: get_cache_dir()"]
        PY_LIC_RLK["license.py: resolve_license_key()"]
        PY_CFG_NRV["config.py: normalize_requested_version()"]
    end

    subgraph "JSEntities" ["JavaScript: js/src/"]
        JS_CFG_LBO["config.ts: getLocalBinaryOverride()"]
        JS_CFG_GCD["config.ts: getCacheDir()"]
        JS_LIC_RLK["license.ts: resolveLicenseKey()"]
        JS_CFG_NRV["config.ts: normalizeRequestedVersion()"]
    end

    subgraph "DotNetEntities" ["DotNet: CloakBrowser/"]
        DN_CFG_LBO["Config.cs: GetLocalBinaryOverride()"]
        DN_LIC_RLK["License.cs: ResolveLicenseKey()"]
    end

    EBP --> PY_CFG_LBO
    EBP --> JS_CFG_LBO
    EBP --> DN_CFG_LBO
    
    ECD --> PY_CFG_GCD
    ECD --> JS_CFG_GCD
    
    ELK --> PY_LIC_RLK
    ELK --> JS_LIC_RLK
    ELK --> DN_LIC_RLK
    
    ECV --> PY_CFG_NRV
    ECV --> JS_CFG_NRV

    PY_CFG_LBO --> PY_DWN["download.py: ensure_binary()"]
    JS_CFG_LBO --> JS_DWN["download.ts: ensureBinary()"]
```

**Sources:** [cloakbrowser/config.py:107-169](), [js/src/config.ts:70-138](), [cloakbrowser/license.py:19-20](), [js/src/license.ts:48-84](), [dotnet/src/CloakBrowser/License.cs:80-123]()

---

## Launch Parameters Reference

Across all three languages, the `launch()`, `launch_context()`, and `launch_persistent_context()` functions share a core set of parameters that control the stealth engine and browser behavior.

### Parameters Summary

| Parameter | Type (Py/JS/.NET) | Default | Description |
|:---|:---|:---|:---|
| `headless` | `bool` / `boolean` / `bool` | `True` | Run in headless mode. Injects `DEFAULT_VIEWPORT` (1920x947) to maintain coherence [cloakbrowser/config.py:86-86](), [js/src/config.ts:31-39](). |
| `proxy` | `ProxySettings` \| `str` | `None` | Proxy configuration. Inline credentials in URLs are parsed automatically [js/src/playwright.ts:24-30](). |
| `args` | `list[str]` / `string[]` | `[]` | Extra CLI flags passed to Chromium. Merged with stealth defaults [js/src/args.ts:15-40](). |
| `stealth_args` | `bool` | `True` | Inject source-level fingerprinting flags like `--fingerprint` [cloakbrowser/config.py:54-76](), [js/src/args.ts:18-22](). |
| `timezone` | `str` | `None` | IANA Timezone (e.g., `Europe/Berlin`). Injects `--fingerprint-timezone` [js/src/args.ts:55-62](), [tests/test_build_args.py:6-9](). |
| `locale` | `str` | `None` | BCP 47 Locale (e.g., `de-DE`). Injects `--lang` and `--fingerprint-locale` [js/src/args.ts:63-71](), [tests/test_build_args.py:12-16](). |
| `geoip` | `bool` | `False` | Auto-detect Timezone/Locale from Proxy exit IP [cloakbrowser/browser.py:63-63](). |
| `humanize` | `bool` | `False` | Enable behavioral humanization layer (Bézier curves, typing delays) [cloakbrowser/browser.py:65-65](). |
| `human_preset` | `str` | `"default"` | Behavioral preset (`default` or `careful`) [cloakbrowser/browser.py:66-66](). |
| `license_key` | `str` | `None` | Override `CLOAKBROWSER_LICENSE_KEY` for this launch [cloakbrowser/license.py:28-30](). |
| `browser_version` | `str` | `None` | Override `CLOAKBROWSER_VERSION` for this launch [cloakbrowser/config.py:138-141](). |

**Sources:** [cloakbrowser/browser.py:56-71](), [js/src/args.ts:15-109](), [cloakbrowser/config.py:54-86](), [dotnet/src/CloakBrowser/Config.cs:70-94]()

---

### Parameter Transformation Logic

The following diagram illustrates how high-level parameters provided by the user are transformed into low-level Chromium CLI flags and behavioral patches.

```mermaid
flowchart LR
    subgraph "Inputs" ["Launch Parameters"]
        P_GEO["geoip=True"]
        P_TZ["timezone='UTC'"]
        P_HUM["humanize=True"]
    end

    subgraph "Processing" ["Logic Entities"]
        PY_GEO["browser.py: maybe_resolve_geoip()"]
        PY_BLD["args.ts: buildArgs() / browser.py: build_args()"]
        PY_PAT["browser.py: patch_browser() / playwright.ts: patchBrowser()"]
    end

    subgraph "Outputs" ["Execution"]
        F_TZ["--fingerprint-timezone=UTC"]
        F_LOC["--fingerprint-locale=..."]
        B_HUM["Humanized Behavioral Layer"]
    end

    P_GEO --> PY_GEO
    PY_GEO --> PY_BLD
    P_TZ --> PY_BLD
    PY_BLD --> F_TZ
    PY_BLD --> F_LOC
    P_HUM --> PY_PAT
    PY_PAT --> B_HUM
```

**Sources:** [cloakbrowser/browser.py:154-187](), [js/src/args.ts:15-109](), [js/src/playwright.ts:16-17]()

---

### Licensing and Pro Exit Codes

When using CloakBrowser Pro, the binary performs license validation. If validation fails, the binary exits with specific codes that the wrapper translates into a `CloakBrowserLicenseError` with a human-readable message.

| Code | Message |
|:---|:---|
| `76` | **Session limit reached**: You have exceeded the concurrent session limit for your plan [cloakbrowser/license.py:80-83](), [js/src/license.ts:53-53](). |
| `77` | **Invalid License**: Key is invalid, expired, or missing [cloakbrowser/license.py:84-87](), [js/src/license.ts:54-54](). |
| `78` | **Server Unreachable**: Could not verify license due to network issues [cloakbrowser/license.py:88-91](), [js/src/license.ts:55-55](). |
| `79` | **Config Problem**: The `~/.cloakbrowser` directory is not writable [cloakbrowser/license.py:92-95](), [js/src/license.ts:56-56](). |

**Sources:** [cloakbrowser/license.py:79-96](), [js/src/license.ts:49-57](), [dotnet/src/CloakBrowser/License.cs:81-87]()

---

# Page: CLI Reference

# CLI Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/__main__.py](cloakbrowser/__main__.py)
- [dotnet/src/CloakBrowser.Cli/Program.cs](dotnet/src/CloakBrowser.Cli/Program.cs)
- [dotnet/src/CloakBrowser/Diagnostics.cs](dotnet/src/CloakBrowser/Diagnostics.cs)
- [dotnet/tests/CloakBrowser.Tests/DiagnosticsTests.cs](dotnet/tests/CloakBrowser.Tests/DiagnosticsTests.cs)
- [dotnet/tests/CloakBrowser.Tests/FontWarningTests.cs](dotnet/tests/CloakBrowser.Tests/FontWarningTests.cs)
- [js/src/cli.ts](js/src/cli.ts)
- [js/src/fonts.ts](js/src/fonts.ts)
- [js/tests/cli.test.ts](js/tests/cli.test.ts)
- [js/tests/fonts.test.ts](js/tests/fonts.test.ts)
- [tests/test_cli.py](tests/test_cli.py)
- [tests/test_font_warning.py](tests/test_font_warning.py)
- [tests/test_free_version_pin.py](tests/test_free_version_pin.py)
- [tests/test_login.py](tests/test_login.py)

</details>



The CloakBrowser CLI provides a unified interface across all three language implementations (Python, JavaScript, and .NET) for managing the stealth Chromium binary lifecycle and diagnosing environment compatibility.

## Command Overview

The CLI is accessible via the following entry points:
*   **Python**: `python -m cloakbrowser <command>` [cloakbrowser/__main__.py:1-9]()
*   **JavaScript**: `npx cloakbrowser <command>` [js/src/cli.ts:1-11]()
*   ** .NET**: `dotnet cloakbrowser <command>` (or the compiled `cloakbrowser` executable) [dotnet/src/CloakBrowser.Cli/Program.cs:7-12]()

### Subcommands

| Command | Description | Implementation Detail |
| :--- | :--- | :--- |
| `login` | Saves a license key (or gets a free key via GitHub). | Validates key before saving to `license.key`. [js/src/cli.ts:45]() |
| `logout` | Removes the saved license key, reverting to the free binary. | Deletes the local `license.key` file. [js/src/cli.ts:46]() |
| `install` | Downloads the Chromium binary with progress reporting. | Calls `ensure_binary()` / `ensureBinary()`. [js/src/cli.ts:53-56]() |
| `info` | Displays environment and binary diagnostics. | Alias: `doctor`. Supports `--quick` and `--json`. [js/src/cli.ts:48-49]() |
| `update` | Checks for and downloads a newer binary. | Rate-limited by `.last_update_check`. [js/src/cli.ts:50]() |
| `clear-cache` | Removes all cached binaries from the local system. | Deletes the contents of the cache directory. [js/src/cli.ts:51]() |

**Sources:** [js/src/cli.ts:42-52](), [cloakbrowser/__main__.py:1-9](), [dotnet/src/CloakBrowser.Cli/Program.cs:8-15]()

---

## Diagnostics Pipeline (`info` / `doctor`)

The `collectDiagnostics` (JS) / `_collect_diagnostics` (Python) / `Diagnostics.Collect` (.NET) function aggregates system state into a structured dictionary. This data is then rendered as human-readable text or raw JSON.

### Diagnostic Flow

Title: "CLI Diagnostic Pipeline"
```mermaid
graph TD
    START["CLI info/doctor"] --> PROBE_ENV["Environment Probe (OS, Arch, Runtime)"]
    PROBE_ENV --> RES_LIC["License Resolution (resolveLicense)"]
    RES_LIC --> EFF_BIN["Binary Resolution (effectiveBinary)"]
    
    subgraph "Network Gated"
        EFF_BIN -- "if !quick && Pro" --> VER_LOOKUP["Version Lookup (getProLatestRelease)"]
        RES_LIC -- "if !quick && Pro" --> SESS_COUNT["Session Count (getActiveSessionCount)"]
    end
    
    VER_LOOKUP --> TESTS["Launch Test (--version flag)"]
    SESS_COUNT --> TESTS
    
    TESTS -- "if Linux" --> LDD["Shared Library Check (ldd)"]
    LDD --> FONTS["Font Probe (fc-list)"]
    FONTS --> GEOIP["GeoIP DB Check"]
    GEOIP --> OUTPUT["Render Text/JSON"]
```
**Sources:** [js/src/cli.ts:170-220](), [cloakbrowser/__main__.py:179-230](), [dotnet/src/CloakBrowser/Diagnostics.cs:13-107]()

### 1. Environment Probe
The CLI captures the host OS, architecture, and runtime version (Node.js `process.version`, Python `platform.python_version()`, or .NET `RuntimeInformation.FrameworkDescription`). It also computes the `platform_tag` used for binary selection.
*   **Sources**: [js/src/cli.ts:173-177](), [cloakbrowser/__main__.py:183-187](), [dotnet/src/CloakBrowser/Diagnostics.cs:17-23]()

### 2. License and Session Resolution
The CLI resolves the license key via `resolveLicenseKey()` from environment variables (`CLOAKBROWSER_LICENSE_KEY`) or the local `license.key` file.
*   **Pro License**: If a valid Pro key is found and `--quick` is not passed, the CLI performs a network request to `cloakbrowser.dev` to retrieve the `latest_version` and the `active` session count via `getActiveSessionCount`. [js/src/cli.ts:164-171](), [cloakbrowser/__main__.py:207-213]()
*   **Session Display**: For Pro users, the CLI shows "active" sessions. If the server is unreachable or the license is "leaseless", it reports the status as such in the JSON output. [dotnet/src/CloakBrowser/Diagnostics.cs:33-43]()
*   **Sources**: [js/src/cli.ts:119-133](), [cloakbrowser/__main__.py:122-146](), [dotnet/src/CloakBrowser/Diagnostics.cs:27-42]()

### 3. Binary Resolution via `effectiveBinary()`
This logic mirrors the runtime `ensure_binary()` flow but avoids downloading. It determines which binary *would* launch based on priority:
1.  **Override**: `CLOAKBROWSER_BINARY_PATH` via `getLocalBinaryOverride()`. [js/src/cli.ts:140-153]()
2.  **Pinned**: `CLOAKBROWSER_VERSION` via `normalizeRequestedVersion()`. [js/src/cli.ts:154]()
3.  **Tier-based**: Pro (cached or latest) vs. Free (bundled version). [js/src/cli.ts:177-183]()

If a Pro license is present but no binary is cached, it indicates that the "next launch downloads the latest". [dotnet/src/CloakBrowser.Cli/Program.cs:141-143]()
*   **Sources**: [js/src/cli.ts:136-168](), [cloakbrowser/__main__.py:148-177](), [dotnet/src/CloakBrowser/Diagnostics.cs:144-200]()

### 4. Shared Library and Font Checks
On Linux, the CLI performs specific checks to ensure the binary can execute and spoofing is coherent:
*   **ldd Check**: Runs `ldd -- <path>` against the binary to identify missing `.so` dependencies (e.g., `libnss3.so`). It filters lines containing `=> not found`. [js/src/cli.ts:95-116](), [cloakbrowser/__main__.py:102-119]()
*   **Font Probe**: Uses `fc-list` via `countFontsPresent()` to count installed fonts against two sets:
    *   `WINDOWS_FONT_TELLS`: 8 core fonts (e.g., Segoe UI, Calibri, Consolas). [js/src/fonts.ts:20-29]()
    *   `OFFICE_FONT_TELLS`: 10 supplemental fonts (e.g., Wingdings, Book Antiqua). [js/src/fonts.ts:35-46]()
*   **Sources**: [js/src/cli.ts:27](), [dotnet/src/CloakBrowser/Diagnostics.cs:80-91](), [js/src/fonts.ts:57-68]()

### 5. Launch Test
Unless `--quick` is specified, the CLI attempts to execute the resolved binary with the `--version` flag.
*   **Windows Handling**: On Windows, Chromium ignores `--version` and starts a browser. The CLI appends `--no-startup-window` to force an immediate exit, allowing the return code to serve as the health check. [js/src/cli.ts:77-79](), [cloakbrowser/__main__.py:75-87]()
*   **Sources**: [js/src/cli.ts:67-92](), [cloakbrowser/__main__.py:75-99](), [dotnet/src/CloakBrowser/Diagnostics.cs:66-76]()

---

## Code Entity Map

The following table maps CLI concepts to their specific implementation entities across the codebase.

| CLI Concept | Python Entity | JavaScript Entity | .NET Entity |
| :--- | :--- | :--- | :--- |
| **Main Entry** | `cloakbrowser.__main__` | `js/src/cli.ts` | `CloakBrowser.Cli/Program.cs` |
| **Diagnostics** | `_collect_diagnostics()` | `collectDiagnostics()` | `Diagnostics.Collect()` |
| **Binary Logic** | `_effective_binary()` | `effectiveBinary()` | `Diagnostics.EffectiveBinary()` |
| **Font Sets** | `WINDOWS_FONT_TELLS` | `WINDOWS_FONT_TELLS` | `CloakLauncher.WindowsFontTells` |
| **GeoIP Check** | `os.path.isfile` | `fs.existsSync` | `File.Exists` |

Title: "Diagnostic Data Structure"
```mermaid
classDiagram
    class Diagnostics {
        +environment: dict
        +binary: dict
        +launch: dict
        +license: dict
        +fonts: dict
        +geoip: dict
    }
    class BinaryInfo {
        +path: string
        +version: string
        +tier: string "free"|"pro"|"override"
        +installed: boolean
    }
    class LicenseInfo {
        +tier: string
        +valid: boolean
        +sessions: dict
    }
    Diagnostics --> BinaryInfo : describes
    Diagnostics --> LicenseInfo : describes
```
**Sources:** [js/src/cli.ts:170-171](), [cloakbrowser/__main__.py:179-181](), [dotnet/src/CloakBrowser/Diagnostics.cs:13-15]()

---

## GeoIP and Modules

*   **GeoIP**: The CLI checks for the presence of `GeoLite2-City.mmdb` in the `~/.cloakbrowser/geoip/` directory. It reports `db_present` as a boolean. If a `--proxy` flag is passed to the `info` command, it performs a live resolution test via `resolveProxyGeoWithIpAsync` (or equivalent) to show the `exit_ip`, `timezone`, and `locale`. [js/src/cli.ts:208-212](), [dotnet/src/CloakBrowser/Diagnostics.cs:96-119]()
*   **Modules**: The CLI verifies if optional dependencies (like `playwright` or `mmdb-lib` in JS, or `Microsoft.Playwright` in .NET) are available in the current environment via `moduleAvailable()`. [js/src/cli.ts:58-65](), [dotnet/src/CloakBrowser/Diagnostics.cs:123-129]()

**Sources:** [js/src/cli.ts:208-220](), [cloakbrowser/__main__.py:221-230](), [dotnet/src/CloakBrowser/Diagnostics.cs:95-106](), [js/tests/cli.test.ts:88-102]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/dependabot.yml](.github/dependabot.yml)
- [.github/workflows/attest-release.yml](.github/workflows/attest-release.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/publish.yml](.github/workflows/publish.yml)
- [flake.lock](flake.lock)
- [flake.nix](flake.nix)
- [js/tsconfig.json](js/tsconfig.json)

</details>



This page covers the repository layout, toolchain setup, and build procedures for contributors to CloakBrowser. It describes the structure of the Python, JavaScript, and .NET packages, how to build each, and how the test suites are organized across all three ecosystems.

For detailed documentation on individual test cases and how to run them, see the [Testing](#8.1) child page. For the binary release workflow, see [Releasing Binaries](#8.2). For integration examples across various frameworks, see [Integration Examples](#8.3).

---

## Repository Layout

The repository hosts three independently publishable packages — the Python package at the root, the JavaScript package under `js/`, and the .NET package under `dotnet/` — along with shared infrastructure for examples, tests, and CI.

**Repository structure map**

```mermaid
graph TD
    Root["(repo root)"]

    Root --> PyPkg["cloakbrowser/\n(Python package source)"]
    Root --> JsDir["js/\n(JavaScript package source)"]
    Root --> DotnetDir["dotnet/\n(.NET package source)"]
    Root --> GH[".github/\n(CI workflows)"]

    PyPkg --> PyInit["__init__.py"]
    PyPkg --> PyDown["download.py"]
    PyPkg --> PyConfig["config.py"]
    PyPkg --> PyVer["_version.py"]

    JsDir --> JsSrc["src/"]
    JsDir --> JsPkg["package.json"]
    JsDir --> JsTs["tsconfig.json"]

    DotnetDir --> DnSrc["src/CloakBrowser/"]
    DotnetDir --> DnGen["src/CloakBrowser.Generators/"]
    DotnetDir --> DnCli["src/CloakBrowser.Cli/"]
    DotnetDir --> DnSln["CloakBrowser.sln"]

    Root --> Docker["Dockerfile"]
    Root --> Nix["flake.nix"]
```

Sources: [.github/workflows/publish.yml:58-60](), [js/package.json:1-21](), [flake.nix:19-30](), [js/tsconfig.json:1-19]()

---

## Python Package

### Build System

The Python package uses [hatchling](https://hatch.pypa.io) as its build backend. Versioning is managed centrally in `cloakbrowser/_version.py`.

| Setting | Value |
|---|---|
| Build backend | `hatchling.build` |
| Version source | `cloakbrowser/_version.py` [cloakbrowser/_version.py:1-1]() |
| Runtime dependencies | `playwright`, `httpx` |

### Building and Running

To build the Python package for distribution:

```bash
pip install build
python -m build
```

The CLI can be run during development using the module syntax:
```bash
python -m cloakbrowser info
```

### Python Module Roles

```mermaid
graph LR
    subgraph "Natural Language Space"
        API["Public API Surface"]
        Binary["Binary Lifecycle"]
        Version["Version Authority"]
    end

    subgraph "Code Entity Space"
        API --> PyInit["cloakbrowser/__init__.py"]
        Binary --> PyDown["cloakbrowser/download.py"]
        Version --> PyVer["cloakbrowser/_version.py"]
    end
```

Sources: [.github/workflows/publish.yml:77-80](), [.github/workflows/ci.yml:18-20](), [cloakbrowser/_version.py:1-1]()

---

## JavaScript Package

### Build System

The JavaScript package lives under `js/` and uses the TypeScript compiler (`tsc`) to produce ESM output in the `dist/` directory. It defines multiple export paths for Playwright, Puppeteer, and the Humanize layer [js/package.json:8-21]().

| Setting | Value |
|---|---|
| Build tool | `typescript` (tsc) [js/package.json:93-93]() |
| Module format | ESM (`type: module`) [js/package.json:5-5]() |
| Target Output | `js/dist/` [js/tsconfig.json:9-9]() |
| Primary Exports | `.`, `./puppeteer`, `./human` [js/package.json:8-21]() |

Sources: [js/package.json:1-97](), [js/tsconfig.json:1-19](), [.github/workflows/publish.yml:94-97]()

### npm Scripts

| Script | Command | Purpose |
|---|---|---|
| `build` | `npm run build` | Compile TypeScript source to `dist/` [js/package.json:93-93]() |
| `typecheck` | `npm run typecheck` | Type-check without emitting files [js/package.json:94-94]() |
| `test` | `npm test` | Run the JavaScript test suite via Vitest [js/package.json:95-95]() |

---

## .NET Package

### Build System

The .NET package targets .NET 8.0 and includes a specialized Roslyn source generator for the humanize decorator layer.

| Project | Role |
|---|---|
| `CloakBrowser.csproj` | Main library (Playwright wrapper) |
| `CloakBrowser.Generators.csproj` | Roslyn source generator for interface delegation |
| `CloakBrowser.Cli.csproj` | Command-line tool |
| `CloakBrowser.sln` | Solution file for building all components |

Sources: [.github/workflows/publish.yml:118-120](), [.github/workflows/ci.yml:44-46]()

### Building and Running

Build the entire solution from the `dotnet/` directory:
```bash
dotnet build dotnet/CloakBrowser.sln -c Release
```

Run the tests:
```bash
dotnet test dotnet/CloakBrowser.sln -c Release
```

### .NET Entity Roles

```mermaid
graph LR
    subgraph "Natural Language Space"
        Launcher["Primary Entry Point"]
        CLI["Command Line Interface"]
        Build["Build Solution"]
    end

    subgraph "Code Entity Space"
        Launcher --> CL["CloakLauncher.cs"]
        CLI --> CP["CloakBrowser.Cli/Program.cs"]
        Build --> SLN["CloakBrowser.sln"]
    end

    CP -- "uses" --> CL
```

Sources: [.github/workflows/publish.yml:118-120](), [.github/workflows/ci.yml:44-46]()

---

## CLI and Utilities

CloakBrowser provides CLI tools in all three languages to manage the underlying patched Chromium binary.

| Command | Action | Implementation (Py / JS / .NET) |
|---|---|---|
| `install` | Download binary | CLI subcommand |
| `info` | Show diagnostic info | CLI subcommand |
| `update` | Check for newer binary | CLI subcommand |
| `clear-cache` | Wipe `.cloakbrowser/` | CLI subcommand |

Sources: [js/package.json:22-24](), [.github/workflows/publish.yml:118-120]()

---

## CI/CD and Releasing

The project uses GitHub Actions for continuous integration and automated publishing across all three package managers.

* **CI Workflow**: Runs Python (pytest), JavaScript (vitest), and .NET (xUnit) tests on every push [.github/workflows/ci.yml:10-46]().
* **Publish Workflow**: Triggered by version tags. It validates version synchronization across `_version.py`, `package.json`, and `CloakBrowser.csproj` before publishing to PyPI, npm, and NuGet [.github/workflows/publish.yml:55-64]().
* **OIDC Trusted Publishing**: The workflow uses OIDC for secure, passwordless publishing to PyPI, npm, and NuGet [.github/workflows/publish.yml:70-71, 88-89, 105-106]().
* **Docker**: Builds and signs multi-arch images (`linux/amd64`, `linux/arm64`) using Cosign [.github/workflows/publish.yml:148-157]().
* **Attestation**: Release binaries are attested for build provenance using Sigstore OIDC [.github/workflows/attest-release.yml:1-30]().

---

## Test Suite Overview

Detailed documentation is available on the [Testing](#8.1) child page.

| Aspect | Python | JavaScript | .NET |
|---|---|---|---|
| Framework | `pytest` | `vitest` | `xUnit` |
| Location | `tests/` | `js/tests/` | `dotnet/tests/` |
| Fast CI | `-m "not slow"` | `npm test` | `dotnet test` |

Sources: [.github/workflows/ci.yml:20-46](), [.github/workflows/publish.yml:32-45](), [js/package.json:95-95]()

---

# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cloakbrowser/human/stealth_dom.py](cloakbrowser/human/stealth_dom.py)
- [js/src/human/stealthDom.ts](js/src/human/stealthDom.ts)
- [js/src/proxy.ts](js/src/proxy.ts)
- [js/tests/extension-loading.test.ts](js/tests/extension-loading.test.ts)
- [js/tests/humanize.test.ts](js/tests/humanize.test.ts)
- [js/tests/proxy.test.ts](js/tests/proxy.test.ts)
- [js/tests/puppeteer.test.ts](js/tests/puppeteer.test.ts)
- [js/tests/setup.ts](js/tests/setup.ts)
- [js/tests/stealthDom.test.ts](js/tests/stealthDom.test.ts)
- [js/tests/update.test.ts](js/tests/update.test.ts)
- [js/vitest.config.ts](js/vitest.config.ts)
- [tests/conftest.py](tests/conftest.py)
- [tests/test_extension_loading.py](tests/test_extension_loading.py)
- [tests/test_human_visual.mjs](tests/test_human_visual.mjs)
- [tests/test_human_visual.py](tests/test_human_visual.py)
- [tests/test_humanize_unit.py](tests/test_humanize_unit.py)
- [tests/test_proxy.py](tests/test_proxy.py)
- [tests/test_update.py](tests/test_update.py)

</details>



This page documents the test suites for the Python, JavaScript, and .NET packages in CloakBrowser. It covers unit tests for configuration and version logic, proxy parsing, signature verification, and the behavioral "humanize" layer, as well as integration tests against live bot detection services.

## Overview

CloakBrowser maintains three parallel test suites to ensure feature parity and stability across all supported languages.

| Language | Framework | Test Directory | Key Features Tested |
|:---|:---|:---|:---|
| **Python** | `pytest` | `tests/` | Versioning, Stealth integration, Humanize logic, Persistent Context, GeoIP |
| **JavaScript** | `vitest` | `js/tests/` | Versioning, Stealth CDP, Humanize logic, Ed25519 Signatures |
| **.NET** | `xUnit` | `dotnet/tests/` | Signature verification, API parity, Humanize decorator logic |

All suites utilize the `CLOAKBROWSER_BINARY_PATH` environment variable in CI to point to a pre-downloaded Stealth Chromium binary, skipping the download phase during test execution [js/tests/launch.test.ts:26-31]().

---

## Python Test Suite (pytest)

The Python suite is located in the `tests/` directory and uses `pytest-asyncio` for asynchronous test support.

### Running Tests

```bash
# Run all fast tests (excludes slow network-dependent tests)
pytest -m "not slow"

# Run all tests including live bot detection (requires network)
pytest

# Run humanize visual verification script
python tests/test_human_visual.py
```

The `slow` marker is used to categorize tests that hit external services or require a live browser binary [tests/test_humanize_unit.py:7-10]().

### Core Test Modules

#### Version and Update Logic (`tests/test_update.py`)
- **`TestVersionComparison`**: Validates `_version_tuple` and `_version_newer` [tests/test_update.py:46-80](). It handles 4-part (e.g., `145.0.7718.0`) and 5-part build numbers [tests/test_update.py:65-70]().
- **`TestShouldCheckForUpdate`**: Tests the rate-limiting logic using the `.last_update_check` marker file [tests/test_update.py:116-147]().
- **`TestEffectiveVersion`**: Verifies that `get_effective_version` correctly prioritizes the `latest_version_{platform}` marker file [tests/test_update.py:150-166]().

#### Proxy Parsing (`tests/test_proxy.py`)
- **`TestParseProxyUrl`**: Verifies extraction of credentials, handling of URL-encoded passwords (e.g., `p%40ss%3Aword`), and protocol detection for `socks5://` [tests/test_proxy.py:13-43]().
- **`TestBuildProxyKwargs`**: Tests the version-gated logic that decides between Playwright's `proxy` dict and CloakBrowser's inline `--proxy-server` arg based on the Chromium version floor [tests/test_proxy.py:45-108]().

#### Humanize Unit Tests (`tests/test_humanize_unit.py`)
- **`TestBezierMath`**: Verifies that `human_move` generates a non-linear curved path with multiple intermediate steps [tests/test_humanize_unit.py:121-166]().
- **`TestAsyncCompat`**: Ensures async versions of the mouse/keyboard drivers correctly handle Playwright's `AsyncRawMouse` [tests/test_humanize_unit.py:192-205]().

#### Isolated World DOM Reads (`js/tests/stealthDom.test.ts`)
The humanize layer uses an isolated CDP world to read DOM state without triggering standard Playwright automation signals.
- **`stealthDom builders`**: Tests the JS generation for `buildBoxJs`, `buildActionableJs`, and `buildPointerJs` [js/tests/stealthDom.test.ts:64-83]().
- **`resolver semantics`**: Executes the shipped resolver JS against Node-based DOM stubs to verify that `:has-text` and `nth` selectors resolve correctly [js/tests/stealthDom.test.ts:90-118]().

**Sources:** `tests/test_update.py`, `tests/test_proxy.py`, `tests/test_humanize_unit.py`, `js/tests/stealthDom.test.ts`, `cloakbrowser/human/stealth_dom.py`

---

## JavaScript Test Suite (vitest)

The JavaScript suite is located in `js/tests/` and uses `vitest` for fast, concurrent execution.

### Core Test Modules

#### Puppeteer Integration (`js/tests/puppeteer.test.ts`)
- **`launch`**: Verifies that the Puppeteer wrapper correctly calls `ensureBinary`, injects stealth args, and handles `defaultViewport` based on headless state [js/tests/puppeteer.test.ts:44-97]().
- **`Proxy Fallback`**: Tests that macOS (Free tier) correctly falls back to `page.authenticate` for HTTP proxies since the binary lacks inline auth [js/tests/puppeteer.test.ts:147-167]().

#### Humanize Unit Tests (`js/tests/humanize.test.ts`)
- **`resolveConfig`**: Validates preset resolution for `default` and `careful` configurations, including custom overrides [js/tests/humanize.test.ts:8-68]().
- **`humanMove`**: Mocks `raw.move` to ensure Bézier paths are curved and do not contain single jumps exceeding 50% of the total distance [js/tests/humanize.test.ts:103-157]().

#### Proxy URL Parsing (`js/tests/proxy.test.ts`)
- **`parseProxyUrl`**: Tests extraction of credentials from both standard URLs and bare `user:pass@host:port` formats [js/tests/proxy.test.ts:8-53]().
- **`isSocksProxy`**: Validates protocol detection for `socks5://` and `socks5h://` [js/tests/proxy.test.ts:122-150]().
- **`resolveProxyConfig`**: Tests the logic that maps proxy inputs to either Playwright `proxyOption` or Chrome `proxyArgs` [js/tests/proxy.test.ts:152-205]().

#### Update Logic (`js/tests/update.test.ts`)
- **`version comparison`**: Tests `parseVersion` and `versionNewer` for 4-part and 5-part versions [js/tests/update.test.ts:30-71]().
- **`wrapper update check`**: Verifies that the library warns the user if a newer npm package version is available on GitHub [js/tests/update.test.ts:167-205]().

**Sources:** `js/tests/puppeteer.test.ts`, `js/tests/humanize.test.ts`, `js/tests/proxy.test.ts`, `js/tests/update.test.ts`, `js/src/proxy.ts`

---

## .NET Test Suite (xUnit)

The .NET suite is located in `dotnet/tests/CloakBrowser.Tests/` and targets .NET 8.

- **`SignatureTests.cs`**: Mirrors the JS/Python signature verification logic using BouncyCastle's Ed25519 implementation.
- **`BezierMathTests.cs`**: Validates that the C# implementation of Bézier curves produces points within the expected bounds and matches the Python/JS trajectory.
- **Humanize Decorator Tests**: Verifies that the Roslyn source-generated `HumanizedPage` correctly intercepts calls to `ClickAsync` and `TypeAsync` to inject behavioral delays.

---

## Visual Humanize Testing

Behavioral "human-like" movements are difficult to assert with boolean logic, so CloakBrowser includes visual test scripts for manual observation.

- **Python**: `tests/test_human_visual.py`
- **JavaScript**: `js/tests/test_human_visual.mjs`

These scripts launch the browser with `humanize=True` and perform sequences of `hover()`, `click()`, and `type()` to demonstrate non-linear mouse paths and variable typing speeds.

---

## System Mapping Diagrams

**Diagram: Python Test Entity Mapping**

```mermaid
graph TD
  subgraph "tests/"
    T_UPDATE["test_update.py"]
    T_HUMAN["test_humanize_unit.py"]
    T_PROXY["test_proxy.py"]
    T_VISUAL["test_human_visual.py"]
  end

  subgraph "cloakbrowser/"
    C_DWN["download.py:check_for_update()"]
    C_MSE["human/mouse.py:human_move()"]
    C_PRX["browser.py:_parse_proxy_url()"]
    C_SDOM["human/stealth_dom.py:build_box_js()"]
  end

  T_UPDATE -- "tests" --> C_DWN
  T_HUMAN -- "validates" --> C_MSE
  T_PROXY -- "validates" --> C_PRX
  T_VISUAL -- "uses" --> C_SDOM
```
Sources: `tests/test_update.py`, `tests/test_humanize_unit.py`, `tests/test_proxy.py`, `cloakbrowser/human/stealth_dom.py`

**Diagram: JavaScript Test Entity Mapping**

```mermaid
graph TD
  subgraph "js/tests/"
    JS_PUP["puppeteer.test.ts"]
    JS_HUMAN["humanize.test.ts"]
    JS_PROXY["proxy.test.ts"]
    JS_SDOM["stealthDom.test.ts"]
  end

  subgraph "js/src/"
    JS_WRAP["puppeteer.ts:launch()"]
    JS_MSE["human/mouse.ts:humanMove()"]
    JS_PRX["proxy.ts:parseProxyUrl()"]
    JS_SD_SRC["human/stealthDom.ts:buildBoxJs()"]
  end

  JS_PUP -- "verifies wrapper" --> JS_WRAP
  JS_HUMAN -- "validates Bezier" --> JS_MSE
  JS_PROXY -- "validates" --> JS_PRX
  JS_SDOM -- "tests isolated world" --> JS_SD_SRC
```
Sources: `js/tests/puppeteer.test.ts`, `js/tests/humanize.test.ts`, `js/tests/proxy.test.ts`, `js/tests/stealthDom.test.ts`

**Sources:**
- `tests/test_update.py`
- `tests/test_humanize_unit.py`
- `tests/test_proxy.py`
- `js/tests/humanize.test.ts`
- `js/tests/update.test.ts`
- `js/tests/proxy.test.ts`
- `js/tests/puppeteer.test.ts`
- `js/tests/stealthDom.test.ts`
- `js/src/proxy.ts`
- `cloakbrowser/human/stealth_dom.py`
- `js/src/human/stealthDom.ts`
- `tests/conftest.py`

---

# Page: Releasing Binaries

# Releasing Binaries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/dependabot.yml](.github/dependabot.yml)
- [.github/workflows/attest-release.yml](.github/workflows/attest-release.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/publish.yml](.github/workflows/publish.yml)

</details>



This page documents the GitHub Actions workflows used to publish Stealth Chromium binaries, attest to their build provenance, and release the Python, JavaScript, and .NET packages to their respective registries (PyPI, npm, NuGet) and Docker Hub.

---

## Binary Release Workflow

The `Release Binary` workflow (located in `.github/workflows/release-binary.yml`) creates a GitHub Release entry with a structured release body. It does **not** build the Chromium binary; it creates the release metadata shell to which binary `.tar.gz` and `.zip` files are manually attached.

### Triggering a Release
The workflow is triggered via `workflow_dispatch`. A maintainer must provide:
*   **tag**: The Git tag (e.g., `chromium-v145.0.7632.159.2`).
*   **title**: Human-readable title (e.g., `Stealth Chromium Build`).
*   **patch_count**: Number of source-level patches applied to the Chromium source code (default `16`).

### Release Body Structure
The workflow generates a Markdown body with installation instructions for `pip`, `npm`, and `dotnet`, highlighting that the binary auto-downloads on first launch. It also includes links to the SHA-256 checksums of the attached assets.

Sources: [.github/workflows/attest-release.yml:7-8](), [.github/workflows/attest-release.yml:21-22]()

---

## Build Provenance Attestation

To ensure the integrity of released binaries, the `Attest Release Binary` workflow provides SLSA (Supply-chain Levels for Software Artifacts) provenance using GitHub's attestation service and Sigstore OIDC.

### Attestation Flow
Title: "Binary Provenance Attestation Flow"
```mermaid
graph TD
    "Trigger[workflow_dispatch]" -- "input:tag" --> "Download[gh_release_download]"
    "Download" -- "pattern:cloakbrowser-*.tar.gz,cloakbrowser-*.zip" --> "Identify[Identify_Assets]"
    "Identify" --> "Attest[actions/attest-build-provenance]"
    "Attest" -- "Sigstore_OIDC" --> "Bundle[Generate_Sigstore_Bundle]"
    "Bundle" --> "GitHub[Write_Attestation_to_GitHub_UI]"
```

This workflow requires `id-token: write` for Sigstore OIDC and `attestations: write` for the GitHub Attestation API [[.github/workflows/attest-release.yml:13-15]()] to sign the assets downloaded from the specified release tag [[.github/workflows/attest-release.yml:18-22]()]. The attestation targets all `.tar.gz` and `.zip` assets matching the `cloakbrowser-*` pattern [[.github/workflows/attest-release.yml:27-29]()].

Sources: [.github/workflows/attest-release.yml:1-30]()

---

## Package Publishing Workflow

The `Publish` workflow (`.github/workflows/publish.yml`) handles the distribution of the Python package to PyPI, the JavaScript package to npm, the .NET package to NuGet, and the Docker image to Docker Hub. It is triggered by pushing a version tag (e.g., `v1.2.3`) or manually via `workflow_dispatch` [[.github/workflows/publish.yml:3-18]()].

### Version Synchronization Validation
Before publishing, the `validate-version` job ensures that the Git tag matches the internal version strings across all three language ecosystems to prevent accidental mismatched releases [[.github/workflows/publish.yml:47-64]()]:
*   **Python**: Extracted from `cloakbrowser/_version.py` using regex to find the `__version__` variable [[.github/workflows/publish.yml:58-58]()].
*   **JavaScript**: Extracted from `js/package.json` using `json.load` to read the `version` field [[.github/workflows/publish.yml:59-59]()].
*   ** .NET**: Extracted from `dotnet/src/CloakBrowser/CloakBrowser.csproj` using regex to find the `<Version>` tag [[.github/workflows/publish.yml:60-60]()].

### Trusted Publishing (OIDC)
The workflow utilizes OIDC trusted publishing, removing the need for long-lived secrets like `PYPI_TOKEN`, `NPM_TOKEN`, or `NUGET_API_KEY`.
*   **PyPI**: Uses `pypa/gh-action-pypi-publish` with `id-token: write` permissions to authenticate against PyPI [[.github/workflows/publish.yml:70-82]()].
*   **npm**: Uses `npm publish --provenance` to link the npm package to the specific GitHub Actions run [[.github/workflows/publish.yml:88-99]()]. It uses Node 24 to ensure a stable `npm` version [[.github/workflows/publish.yml:94-94]()].
*   **NuGet**: Uses the `NuGet/login` action to exchange a GitHub OIDC token for a short-lived NuGet API key [[.github/workflows/publish.yml:105-120]()].

### Docker Release and Signing
The `publish-docker` job builds multi-platform images (`linux/amd64`, `linux/arm64`) [[.github/workflows/publish.yml:148-148]()].
1.  **Version Extraction**: The version is pulled from `cloakbrowser/_version.py` to tag the image [[.github/workflows/publish.yml:133-136]()].
2.  **Signing**: Images are signed using `cosign` with GitHub's OIDC identity (`id-token: write`) [[.github/workflows/publish.yml:155-157]()].
3.  **Attestation**: Build provenance and SBOMs are generated and attached to the image using `actions/attest-build-provenance` [[.github/workflows/publish.yml:158-161]()].

### Publishing Pipeline Logic
Title: "Cross-Language Package Publishing Pipeline"
```mermaid
flowchart TD
    "Start[push_tag_v*]" --> "Test[Job:test]"
    "Test" --> "Val[Job:validate-version]"
    "Val" --> "PyPI[Job:publish-pypi]"
    "Val" --> "NPM[Job:publish-npm]"
    "Val" --> "NuGet[Job:publish-nuget]"
    "Val" --> "Docker[Job:publish-docker]"

    subgraph "Verification_Logic"
    "Test" -- "pytest_&_npm_test_&_dotnet_test" --> "Val"
    "Val" -- "Sync_Check:_Python_JS_NET" --> "PyPI"
    end

    subgraph "Distribution_Targets"
    "PyPI" -- "OIDC_Trusted_Publishing" --> "Target1[PyPI]"
    "NPM" -- "npm_publish_--provenance" --> "Target2[npm]"
    "NuGet" -- "NuGet/login_OIDC" --> "Target3[NuGet]"
    "Docker" -- "cosign_sign_&_attestation" --> "Target4[Docker_Hub]"
    end
```

Sources: [.github/workflows/publish.yml:1-161](), [.github/workflows/ci.yml:1-47]()

---

## Release Consistency Summary

The following table summarizes how each component of the CloakBrowser ecosystem is versioned and distributed.

| Component | Version Source | Release Target | Signing / Provenance Method |
| :--- | :--- | :--- | :--- |
| **Python** | `cloakbrowser/_version.py` [[.github/workflows/publish.yml:58-58]()] | PyPI | OIDC Trusted Publishing |
| **JavaScript** | `js/package.json` [[.github/workflows/publish.yml:59-59]()] | npm | OIDC + npm `--provenance` |
| **.NET** | `CloakBrowser.csproj` [[.github/workflows/publish.yml:60-60]()] | NuGet | OIDC via `NuGet/login` |
| **Docker** | `cloakbrowser/_version.py` [[.github/workflows/publish.yml:135-135]()] | Docker Hub | Cosign Keyless + SLSA Attestation |
| **Binaries** | Manual Tag Input [[.github/workflows/attest-release.yml:7-8]()] | GitHub Releases | GitHub Build Provenance Attestations |

Sources: [.github/workflows/publish.yml:58-60](), [.github/workflows/publish.yml:135-135](), [.github/workflows/publish.yml:155-161](), [.github/workflows/attest-release.yml:24-30]()

---

# Page: Integration Examples

# Integration Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [bin/cloakserve](bin/cloakserve)
- [bin/cloaktest](bin/cloaktest)
- [examples/basic.py](examples/basic.py)
- [examples/fingerprint_scan_test.py](examples/fingerprint_scan_test.py)
- [examples/integrations/agent_browser.sh](examples/integrations/agent_browser.sh)
- [examples/integrations/aws_lambda/Dockerfile](examples/integrations/aws_lambda/Dockerfile)
- [examples/integrations/aws_lambda/INSTRUCTIONS.md](examples/integrations/aws_lambda/INSTRUCTIONS.md)
- [examples/integrations/aws_lambda/lambda-entrypoint.sh](examples/integrations/aws_lambda/lambda-entrypoint.sh)
- [examples/integrations/aws_lambda/lambda_handler.py](examples/integrations/aws_lambda/lambda_handler.py)
- [examples/integrations/browser_use_example.py](examples/integrations/browser_use_example.py)
- [examples/integrations/crawl4ai_example.py](examples/integrations/crawl4ai_example.py)
- [examples/integrations/crawlee_example.py](examples/integrations/crawlee_example.py)
- [examples/integrations/langchain_loader.py](examples/integrations/langchain_loader.py)
- [examples/integrations/scrapling_example.py](examples/integrations/scrapling_example.py)
- [examples/integrations/selenium_example.py](examples/integrations/selenium_example.py)
- [examples/integrations/undetected_chromedriver.py](examples/integrations/undetected_chromedriver.py)
- [examples/persistent_context.py](examples/persistent_context.py)
- [examples/recaptcha_score.py](examples/recaptcha_score.py)
- [examples/stealth_test.py](examples/stealth_test.py)
- [js/examples/basic-playwright.ts](js/examples/basic-playwright.ts)
- [js/examples/basic-puppeteer.ts](js/examples/basic-puppeteer.ts)
- [js/examples/persistent-context.ts](js/examples/persistent-context.ts)
- [js/examples/stagehand.ts](js/examples/stagehand.ts)
- [js/examples/stealth-test.ts](js/examples/stealth-test.ts)
- [tests/test_cloakserve.py](tests/test_cloakserve.py)
- [tests/test_lambda_security.py](tests/test_lambda_security.py)
- [tests/test_stealth.py](tests/test_stealth.py)

</details>



The `examples/` and `js/examples/` directories provide a comprehensive suite of implementation patterns for CloakBrowser. These examples demonstrate how to leverage the patched Chromium binary across various automation frameworks, AI agents, and stealth testing platforms.

## Core Usage Examples

These examples demonstrate the fundamental lifecycle of a CloakBrowser instance, including binary resolution, context management, and basic navigation.

| Example File | Framework | Key Feature |
|:---|:---|:---|
| `examples/basic.py` | Playwright (Python) | Standard `launch()` and page navigation. |
| `js/examples/basic-playwright.ts` | Playwright (JS) | ESM-based `launch()` with TypeScript types. |
| `js/examples/basic-puppeteer.ts` | Puppeteer (JS) | Integration via the `cloakbrowser/puppeteer` subpath. |
| `examples/persistent_context.py` | Playwright (Python) | `launch_persistent_context()` for session retention. |

### Persistent Context Flow
Persistent contexts allow for the reuse of browser profiles (cookies, local storage, cache) across restarts while maintaining stealth patches.

**Persistent Context Initialization**
```mermaid
sequenceDiagram
    participant User as "User Script"
    participant CB as "cloakbrowser.launch_persistent_context()"
    participant Bin as "Chromium Binary"
    participant FS as "User Data Dir"

    User->>CB: Provide "userDataDir" & "headless=True"
    CB->>Bin: Execute with "--user-data-dir" and "--fingerprint"
    Bin->>FS: Load/Save Session Data
    Bin-->>CB: "BrowserContext" Ready
    CB-->>User: Return "BrowserContext"
```
Sources: `examples/persistent_context.py:1-25`(), `js/examples/persistent-context.ts:1-30`()

## Stealth & Fingerprint Testing

CloakBrowser includes specialized scripts to validate its effectiveness against modern bot detection services.

### Stealth Test Suite (`stealth_test.py` / `stealth-test.ts`)
This script executes a battery of tests against industry-standard detectors. It uses `page.evaluate()` to extract pass/fail verdicts directly from the DOM of the target sites.

*   **Sannysoft**: Checks for classic leaks like `navigator.webdriver` [examples/stealth_test.py:26-50]().
*   **Incolumitas**: Performs 30+ comprehensive checks [examples/stealth_test.py:52-71]().
*   **Rebrowser**: Detects automation signals and CDP leaks [examples/stealth_test.py:74-88]().
*   **reCAPTCHA v3**: Specifically targets the `recaptcha-demo.appspot.com` endpoint to verify human-level scores (typically 0.9) [examples/recaptcha_score.py:1-35]().

### Fingerprint Scanning (`fingerprint_scan_test.py`)
This script focuses on "weak signals" often used to detect headless environments, such as taskbar height, content index presence, and WebGPU availability [examples/fingerprint_scan_test.py:27-86](). It also extracts deep signal breakdowns from **CreepJS**, including `likeHeadless`, `headless`, and `stealth` percentages [examples/fingerprint_scan_test.py:89-177]().

Sources: `examples/stealth_test.py:1-180`(), `examples/fingerprint_scan_test.py:1-180`(), `examples/recaptcha_score.py:1-35`(), `tests/test_stealth.py:1-188`()

## Framework Integrations (Python)

CloakBrowser can be integrated into existing Python scraping ecosystems by manually providing the binary path and stealth arguments.

### Selenium & Undetected Chromedriver
*   **Selenium**: Integration via `selenium_example.py` uses `Options.binary_location` and `Options.add_argument()` for each stealth flag.
*   **Undetected Chromedriver**: The `undetected_chromedriver.py` example combines `uc`'s driver-level patches with CloakBrowser's source-level patches.

### Crawlee & Scrapling
*   **Crawlee**: Integration in `crawlee_example.py` subclassing `PlaywrightBrowserPlugin` to override the `new_browser` method.
*   **Scrapling**: Uses CDP via WebSocket to connect the `StealthyFetcher` to a CloakBrowser instance.

**Crawlee Plugin Implementation**
```mermaid
classDiagram
    class PlaywrightBrowserPlugin {
        <<Crawlee>>
    }
    class CloakBrowserPlugin {
        +new_browser() PlaywrightBrowserController
    }
    class PlaywrightBrowserController {
        <<Crawlee>>
    }
    PlaywrightBrowserPlugin <|-- CloakBrowserPlugin
    CloakBrowserPlugin ..> PlaywrightBrowserController : creates
    CloakBrowserPlugin ..> "ensure_binary()" : calls
    CloakBrowserPlugin ..> "get_default_stealth_args()" : calls
```
Sources: `examples/integrations/crawlee_example.py:1-30`(), `examples/integrations/scrapling_example.py:1-30`(), `examples/integrations/selenium_example.py:1-30`(), `examples/integrations/undetected_chromedriver.py:1-30`()

## AI Agent Integrations

CloakBrowser acts as the "stealth browser provider" for various LLM-driven agent frameworks, typically via the Chrome DevTools Protocol (CDP).

| Integration | Method | Implementation Detail |
|:---|:---|:---|
| **browser-use** | CDP | Launches with `--remote-debugging-port=9242` and connects via `BrowserSession(cdp_url=...)` [examples/integrations/browser_use_example.py:20-27](). |
| **Crawl4AI** | CDP | Connects `AsyncWebCrawler` to a CloakBrowser instance via `BrowserConfig(cdp_url=...)` [examples/integrations/crawl4ai_example.py:18-24](). |
| **LangChain** | Custom Loader | Wraps `launch_async()` in `langchain_loader.py` to produce LangChain `Document` objects. |
| **Stagehand** | Local Launch | In `js/examples/stagehand.ts`, it passes `binaryPath` and `stealthArgs` to the `Stagehand` constructor. |

Sources: `examples/integrations/browser_use_example.py:1-43`(), `examples/integrations/crawl4ai_example.py:1-39`(), `examples/integrations/langchain_loader.py:1-40`(), `js/examples/stagehand.ts:1-30`()

## CLI & Shell Utilities

### cloakserve (CDP Multiplexer)
The `bin/cloakserve` utility is a CDP multiplexer that spawns separate Chrome processes per unique fingerprint seed, routing connections through a single port [bin/cloakserve:2-16](). It manages a `ChromePool` of `ChromeProcess` objects [bin/cloakserve:174-201]().

**CDP Multiplexer Architecture**
```mermaid
graph TD
    subgraph "ClientSpace"
        C1["Playwright (seed=1)"]
        C2["AIAgent (seed=2)"]
    end
    subgraph "cloakserve"
        CP["ChromePool"]
        P1["ChromeProcess (seed=1)"]
        P2["ChromeProcess (seed=2)"]
    end
    subgraph "OS"
        B1["StealthChromium (Port 5100)"]
        B2["StealthChromium (Port 5101)"]
    end

    C1 -- "CDP Port 9222" --> CP
    C2 -- "CDP Port 9222" --> CP
    CP -- "get_or_launch" --> P1
    CP -- "get_or_launch" --> P2
    P1 -- "spawn" --> B1
    P2 -- "spawn" --> B2
```
Sources: `bin/cloakserve:1-168`(), `tests/test_cloakserve.py:1-170`()

### agent_browser.sh
A reference shell script for the `agent-browser` Node.js CLI. It uses Python one-liners to resolve the binary path and stealth arguments, then exports them as environment variables for the agent.

Sources: `examples/integrations/agent_browser.sh:1-15`()

## AWS Lambda Deployment

CloakBrowser can be deployed to AWS Lambda using a container image. This pattern allows for one-shot stealth scrapes in a serverless environment.

### Dockerfile & Entrypoint
The `Dockerfile` derives from `cloakhq/cloakbrowser:latest` and adds the `awslambdaric` (Runtime Interface Client) and `aws-lambda-rie` (Runtime Interface Emulator) [examples/integrations/aws_lambda/Dockerfile:36-47](). 

The `lambda-entrypoint.sh` script handles Xvfb startup on display `:99` and routes commands to the Lambda runtime if the command matches a `module.func` pattern [examples/integrations/aws_lambda/lambda-entrypoint.sh:41-50]().

### Lambda Handler (`lambda_handler.py`)
The handler provides a robust scraping interface that includes:
*   **URL Validation**: Rejects non-HTTP schemes and private/internal IP ranges to prevent SSRF [examples/integrations/aws_lambda/lambda_handler.py:79-97]().
*   **Smart Wait**: Polls the DOM until the HTML length stabilizes, providing a more reliable stopping condition than `networkidle` for SPAs [examples/integrations/aws_lambda/lambda_handler.py:151-180]().
*   **Retry Orchestration**: Automatically retries on transient failures (e.g., certificate errors or timeouts) with adjusted internal arguments [examples/integrations/aws_lambda/lambda_handler.py:43-55]().

**Lambda Scrape Flow**
```mermaid
sequenceDiagram
    participant AWS as "AWS Lambda"
    participant H as "lambda_handler.py"
    participant X as "Xvfb (:99)"
    participant CB as "cloakbrowser.launch_context_async"
    participant P as "Page"

    AWS->>H: Invoke with {url, proxy, humanize}
    H->>X: Ensure display ready
    H->>H: _validate_url(url)
    H->>CB: launch_context_async(headless=False, ...)
    CB-->>H: "BrowserContext"
    H->>P: page.goto(url)
    H->>H: _smart_wait()
    H->>P: page.content() / page.screenshot()
    H-->>AWS: Return {title, html, screenshot_b64}
```

Sources: `examples/integrations/aws_lambda/Dockerfile:1-80`(), `examples/integrations/aws_lambda/lambda_handler.py:1-200`(), `examples/integrations/aws_lambda/lambda-entrypoint.sh:1-53`(), `examples/integrations/aws_lambda/INSTRUCTIONS.md:1-150`(), `Dockerfile:1-55`()

---

# Page: Widevine DRM

# Widevine DRM

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bin/fetch-widevine.py](bin/fetch-widevine.py)
- [cloakbrowser/widevine.py](cloakbrowser/widevine.py)
- [dotnet/src/CloakBrowser/Widevine.cs](dotnet/src/CloakBrowser/Widevine.cs)
- [js/src/widevine.ts](js/src/widevine.ts)
- [js/tests/widevine-integration.test.ts](js/tests/widevine-integration.test.ts)
- [js/tests/widevine.test.ts](js/tests/widevine.test.ts)
- [tests/test_fetch_widevine.py](tests/test_fetch_widevine.py)
- [tests/test_widevine.py](tests/test_widevine.py)

</details>



CloakBrowser binaries are built with Widevine support enabled; however, the Content Decryption Module (CDM) is a proprietary Google component that cannot be redistributed with the browser package [cloakbrowser/widevine.py:3-6](). To enable DRM-protected video playback (e.g., Netflix, Hulu), users must sideload the CDM. 

This page documents the automation tools provided to fetch the CDM and the internal "hint-file" seeding mechanism that allows the CDM to be recognized on the very first launch of a persistent profile [js/src/widevine.ts:5-12]().

## The Hint-File Mechanism

Chromium discovers sideloaded CDMs in two phases. First, an early-startup pass reads a "hint file" from the user data directory. Second, a later asynchronous component-updater pass writes that hint file. Because automation frameworks like Playwright and Puppeteer launch with `--disable-component-update`, the updater never writes the hint, typically requiring a "two-launch dance" to activate DRM [cloakbrowser/widevine.py:8-12]().

CloakBrowser solves this by pre-seeding the hint file `latest-component-updated-widevine-cdm` inside the `<user-data-dir>/WidevineCdm/` directory before the browser process starts [cloakbrowser/widevine.py:33-35]().

### Platform Limitations
*   **Linux**: Fully supported. The hint-file mechanism is specific to Linux and ChromeOS [js/src/widevine.ts:14-15]().
*   **Windows**: No-op. The CDM cannot initialize due to DRM host verification requirements [cloakbrowser/widevine.py:18-20]().
*   **macOS**: No-op. macOS uses a different CDM layout [cloakbrowser/widevine.py:20-21]().

**Sources:** [cloakbrowser/widevine.py:1-21](), [js/src/widevine.ts:1-15]()

## CDM Resolution Logic

The library attempts to locate a valid CDM directory (defined as a directory containing `manifest.json`) using the following priority [js/src/widevine.ts:50-60]():

1.  **Environment Variable**: If `CLOAKBROWSER_WIDEVINE_CDM` is set, it is used exclusively. If the path is invalid (lacks `manifest.json`), seeding is skipped without falling back [cloakbrowser/widevine.py:61-69]().
2.  **Binary Directory**: `<chrome-binary-dir>/WidevineCdm`. This is the standard location for manual sideloads [cloakbrowser/widevine.py:73-74]().
3.  **Cache Directory**: `<cache-dir>/WidevineCdm` (typically `~/.cloakbrowser/WidevineCdm`). This allows a single CDM fetched by `fetch-widevine.py` to serve multiple browser versions or Pro/Free tiers [cloakbrowser/widevine.py:74-77]().

### Widevine System Data Flow
This diagram illustrates how the CDM is resolved and how the hint file is seeded into the profile.

```mermaid
graph TD
    subgraph "ResolutionPhase"
        ENV["Env: CLOAKBROWSER_WIDEVINE_CDM"]
        BIN_DIR["Binary Dir / WidevineCdm"]
        CACHE_DIR["Cache Dir / WidevineCdm"]
    end

    RESOLVE["resolve_widevine_cdm_dir()"]
    SEED["seed_widevine_hint()"]
    
    ENV -->|Priority 1| RESOLVE
    BIN_DIR -->|Priority 2| RESOLVE
    CACHE_DIR -->|Priority 3| RESOLVE

    RESOLVE -->|Path to .so| SEED
    SEED -->|Write JSON| HINT["userDataDir/WidevineCdm/latest-component-updated-widevine-cdm"]
    
    subgraph "ChromiumStartup"
        HINT -->|Read by| CHROME["Chromium Binary"]
        CHROME -->|Load| SO["libwidevinecdm.so"]
    end
```
**Sources:** [cloakbrowser/widevine.py:43-77](), [js/src/widevine.ts:63-79](), [dotnet/src/CloakBrowser/Widevine.cs:37-61]()

## Utility Scripts

### fetch-widevine.py (Python)
The `bin/fetch-widevine.py` script automates the retrieval of the CDM from Google's component-update servers.

*   **Architecture**: Supports Linux x86-64 only. Google does not publish an ARM64 Linux CDM [bin/fetch-widevine.py:44-57]().
*   **Integrity**:
    *   Verifies the download against server-provided SHA-256 hashes [bin/fetch-widevine.py:16-20]().
    *   If the `cryptography` library is available, it performs CRX3 RSA publisher signature verification to ensure the binary was signed by the official Widevine app ID (`oimompecagnajdejgnnjijobebaeigek`) [bin/fetch-widevine.py:100-150]().
*   **Protobuf Parsing**: Implements a minimal `_parse_pb` reader to extract signature proofs and signed headers from the CRX3 container [bin/fetch-widevine.py:74-91]().

**Sources:** [bin/fetch-widevine.py:1-21](), [bin/fetch-widevine.py:37-38](), [bin/fetch-widevine.py:74-91]()

## Implementation Reference

### Python
The Python implementation in `cloakbrowser/widevine.py` uses `pathlib` for cross-platform path resolution and `json.dumps` to create the hint file.

| Function | Description |
| :--- | :--- |
| `resolve_widevine_cdm_dir(binary_path)` | Scans the filesystem for a `manifest.json` in prioritized locations [cloakbrowser/widevine.py:43](). |
| `seed_widevine_hint(user_data_dir, binary_path)` | The main entry point called during `launch_persistent_context()` [cloakbrowser/widevine.py:80](). |
| `_seeding_disabled()` | Checks `CLOAKBROWSER_WIDEVINE` for "0", "false", or "off" [cloakbrowser/widevine.py:37](). |

**Sources:** [cloakbrowser/widevine.py:25-129]()

### JavaScript / TypeScript
The JS implementation in `js/src/widevine.ts` mirrors the Python logic using `node:fs` and `node:path`.

| Function | Description |
| :--- | :--- |
| `resolveWidevineCdmDir(binaryPath)` | Returns the absolute, symlink-resolved path to the CDM [js/src/widevine.ts:63](). |
| `seedWidevineHint(userDataDir, binaryPath)` | Writes the hint file; uses `fs.mkdirSync` with `{ recursive: true }` [js/src/widevine.ts:87](). |

**Sources:** [js/src/widevine.ts:1-126]()

### .NET (C#)
The .NET implementation in `Widevine.cs` is a direct port of the Python logic.

| Function | Description |
| :--- | :--- |
| `ResolveWidevineCdmDir(string binaryPath)` | Uses `Environment.GetEnvironmentVariable` and `Path.Combine` [dotnet/src/CloakBrowser/Widevine.cs:37](). |
| `SeedWidevineHint(string? userDataDir, string binaryPath)` | Uses `JsonSerializer` with `UnsafeRelaxedJsonEscaping` to match JS output formatting [dotnet/src/CloakBrowser/Widevine.cs:68](). |

**Sources:** [dotnet/src/CloakBrowser/Widevine.cs:20-124]()

## Testing

The Widevine subsystem is covered by integration and unit tests that verify resolution logic and framework wiring.

*   **Python Unit Tests**: `tests/test_widevine.py` verifies idempotency, environment variable exclusivity, and cache-root fallbacks [tests/test_widevine.py:78-150]().
*   **Fetch Utility Tests**: `tests/test_fetch_widevine.py` exercises CRX3/Protobuf parsing and signature verification using synthesized CRX files and throwaway RSA keys [tests/test_fetch_widevine.py:1-8]().
*   **JavaScript Unit Tests**: `js/tests/widevine.test.ts` provides comprehensive coverage for resolution order and Linux-only constraints [js/tests/widevine.test.ts:51-157]().
*   **JavaScript Integration Tests**: `js/tests/widevine-integration.test.ts` mocks `playwright-core` and `puppeteer-core` to ensure `seedWidevineHint` is invoked during `launchPersistentContext` [js/tests/widevine-integration.test.ts:31-57]().

### Code Entity Mapping
This diagram maps the logical Widevine operations to specific functions across the three language implementations.

```mermaid
classDiagram
    class PythonImplementation {
        "cloakbrowser/widevine.py"
        seed_widevine_hint()
        resolve_widevine_cdm_dir()
    }
    class JSImplementation {
        "js/src/widevine.ts"
        seedWidevineHint()
        resolveWidevineCdmDir()
    }
    class DotNetImplementation {
        "CloakBrowser/Widevine.cs"
        SeedWidevineHint()
        ResolveWidevineCdmDir()
    }
    
    PythonImplementation --|> JSImplementation : "Parity"
    JSImplementation --|> DotNetImplementation : "Parity"
```
**Sources:** [cloakbrowser/widevine.py:1-30](), [js/src/widevine.ts:1-20](), [dotnet/src/CloakBrowser/Widevine.cs:1-20]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [BINARY-LICENSE.md](BINARY-LICENSE.md)
- [CHANGELOG.md](CHANGELOG.md)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [cloakbrowser/__main__.py](cloakbrowser/__main__.py)
- [cloakbrowser/browser.py](cloakbrowser/browser.py)
- [cloakbrowser/download.py](cloakbrowser/download.py)
- [cloakbrowser/geoip.py](cloakbrowser/geoip.py)
- [dotnet/README.md](dotnet/README.md)
- [dotnet/src/CloakBrowser.Cli/Program.cs](dotnet/src/CloakBrowser.Cli/Program.cs)
- [dotnet/src/CloakBrowser/CloakBrowser.csproj](dotnet/src/CloakBrowser/CloakBrowser.csproj)
- [dotnet/src/CloakBrowser/CloakVersion.cs](dotnet/src/CloakBrowser/CloakVersion.cs)
- [dotnet/src/CloakBrowser/Diagnostics.cs](dotnet/src/CloakBrowser/Diagnostics.cs)
- [dotnet/src/CloakBrowser/Download.cs](dotnet/src/CloakBrowser/Download.cs)
- [js/package-lock.json](js/package-lock.json)
- [js/src/cli.ts](js/src/cli.ts)
- [js/src/download.ts](js/src/download.ts)
- [js/src/geoip.ts](js/src/geoip.ts)
- [js/src/playwright.ts](js/src/playwright.ts)
- [js/src/puppeteer.ts](js/src/puppeteer.ts)
- [js/tests/geoip.test.ts](js/tests/geoip.test.ts)
- [pyproject.toml](pyproject.toml)
- [tests/test_cli.py](tests/test_cli.py)
- [tests/test_geoip.py](tests/test_geoip.py)

</details>



This page provides definitions for codebase-specific terms, technical jargon, and abbreviations used throughout the CloakBrowser project. It serves as a reference for onboarding engineers to understand the underlying mechanics of stealth automation, the binary lifecycle, and the Pro licensing system.

## Stealth & Fingerprinting Terminology

Terms related to the core mission of CloakBrowser: bypassing bot detection by modifying browser identity and behavior.

| Term | Definition | Implementation Detail |
| :--- | :--- | :--- |
| **Source-level Patches** | Modifications made directly to the Chromium C++ source code before compilation. | Unlike JS injection, these cannot be detected by monitoring the DOM or environment globals. [README.md:21-23](), [README.md:39-40]() |
| **Fingerprint Seed** | A random integer (10000-99999) generated at launch to drive deterministic randomization of browser fingerprints. | Generated in `get_default_stealth_args` and passed via `--fingerprint`. [cloakbrowser/config.py:30-31](), [js/src/config.ts:30-31]() |
| **Stealth Args** | Command-line flags passed to the Chromium binary to activate specific C++ patches. | Managed via `get_default_stealth_args()` in Python and `getDefaultStealthArgs()` in JS. [cloakbrowser/config.py:30-31](), [js/src/playwright.ts:13-15]() |
| **Automation Signals** | Browser properties (like `navigator.webdriver`) that reveal the browser is controlled by a script. | CloakBrowser suppresses these by ignoring default Playwright flags like `--enable-automation`. [cloakbrowser/config.py:26-27](), [js/src/playwright.ts:10-11]() |
| **CDP Leaks** | Detection vectors where Chrome DevTools Protocol (CDP) commands produce different internal signals than real hardware. | Mitigated by source-level patches that intercept CDP input events to mimic real user signals. [README.md:39-40](), [CHANGELOG.md:14-16]() |
| **Hardware Identity** | The combination of GPU, RAM, CPU cores, and screen characteristics reported by the browser. | In Pro builds, these are chosen to form a popular, self-consistent device with no internal contradictions. [CHANGELOG.md:11-14](), [README.md:157-159]() |
| **Coherence** | The consistency of browser signals across different APIs (e.g., WebGL reporting the same GPU as the User-Agent). | CloakBrowser ensures coherence across top-level and nested frames. [CHANGELOG.md:14-15](), [CHANGELOG.md:23-24]() |
| **Noise Injection** | The technique of adding subtle, deterministic randomization to canvas, WebGL, and audio data. | Activated via `--fingerprint-noise` and driven by the seed. [README.md:39-40]() |

### Code Entity Mapping: Stealth System
The following diagram connects stealth concepts to the specific functions and flags that implement them.

Title: Stealth System Architecture
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        n1["FingerprintSeed"] --> n2["SourcePatches"]
        n3["AutomationSignals"] --> n4["CDPLeaks"]
    end

    subgraph "CodeEntitySpace"
        n1 --- f1["get_default_stealth_args()"]
        f1 --- f2["--fingerprint={seed}"]
        n2 --- f3["CHROMIUM_VERSION"]
        n3 --- f4["IGNORE_DEFAULT_ARGS"]
        f4 --- f5["--enable-automation"]
        n4 --- f6["--fingerprint-noise"]
    end
```
**Sources:** [cloakbrowser/config.py:24-43](), [js/src/playwright.ts:8-15](), [CHANGELOG.md:11-24]()

---

## Binary Lifecycle & Licensing Terms

Terms related to how the patched Chromium binary is distributed, verified, and restricted via licensing.

*   **Binary Cache**: The local directory where Chromium binaries are stored. Defaults to `~/.cloakbrowser/`. [cloakbrowser/download.py:38-39](), [js/src/download.ts:27-28]()
*   **Marker Files**: Small files in the cache dir used for state tracking, such as `.latest_version`, `.welcome_shown`, or `.last_update_check`. [cloakbrowser/download.py:67-73](), [cloakbrowser/download.py:126-127](), [js/src/download.ts:41-48]()
*   **Effective Version**: The specific Chromium version string selected for launch, prioritizing auto-updated versions over the hardcoded default. [cloakbrowser/download.py:41-42](), [js/src/download.ts:30-31](), [js/src/cli.ts:137-140]()
*   **Platform Tag**: A string identifying the OS and architecture (e.g., `linux-x64`, `win32`, `darwin-arm64`). [cloakbrowser/download.py:44-45](), [js/src/download.ts:33-34]()
*   **Free vs. Pro Tier**: The Free tier uses an older binary; the Pro tier provides access to v150+ builds with the latest patches. [README.md:41-45](), [CHANGELOG.md:11-13]()
*   **BinaryVerificationError**: An error raised when a downloaded binary fails SHA-256 checksum or Ed25519 signature verification. [js/src/download.ts:61-66](), [cloakbrowser/download.py:52-60]()
*   **Ed25519 Signature**: A cryptographic signature used to verify binary authenticity before extraction. [js/src/download.ts:8-12](), [dotnet/src/CloakBrowser/CloakBrowser.csproj:33-36]()
*   **License Gate**: A check within the Pro binary that exits with specific codes (76-79) if a valid license is not present or session limits are reached. [cloakbrowser/browser.py:51-56](), [CHANGELOG.md:45-47]()
*   **Session Limit**: The maximum number of concurrent browser instances allowed by a license key. [js/src/cli.ts:29-30](), [CHANGELOG.md:45-47]()
*   **License Cache TTL**: The duration for which license validation results are stored locally to allow offline launch. [js/src/download.ts:43-48]()

---

## Subsystem Names

*   **Humanize**: The behavioral layer that simulates human-like mouse curves, keyboard timing, and scroll patterns. [README.md:40-41](), [js/src/playwright.ts:166-170](), [js/src/puppeteer.ts:156-160]()
*   **GeoIP**: Resolves the exit IP of a proxy to determine the correct timezone and locale. [README.md:129-133](), [js/src/geoip.ts:17-19]()
*   **CloakServe**: A specialized CDP server mode for remote browser management. [README.md:164-165]()
*   **CloakTest**: A Docker-based utility to verify stealth passing. [README.md:49-51]()
*   **Doctor**: A diagnostic alias for the `info` command that performs environment probes. [cloakbrowser/__main__.py:5-8](), [js/src/cli.ts:7-10]()

---

## Bot Detection & API Terms

*   **reCAPTCHA / Turnstile / FingerprintJS / BrowserScan / DataDome**: Third-party services CloakBrowser is designed to bypass. [README.md:41-43]()
*   **Persistent Context**: A browser session that saves profile data (cookies, localStorage) to a disk directory. [js/src/playwright.ts:7-12]()
*   **Incognito Detection**: Bot detection techniques that identify private browsing modes; CloakBrowser patches these to appear as normal sessions. [README.md:21-23]()
*   **Storage Quota Normalization**: A patch to ensure `navigator.storage.estimate()` returns values consistent with the spoofed hardware. [CHANGELOG.md:14-15]()
*   **Bézier Curves**: Mathematical paths used for realistic, non-linear mouse movement in the humanize layer. [README.md:168-169]()
*   **Patchright**: A specific backend parameter for the Python package to use an alternative automation driver. [cloakbrowser/browser.py:24-31]()
*   **Decorator Layer**: The architectural pattern used in .NET to wrap Playwright interfaces. [dotnet/src/CloakBrowser/CloakBrowser.csproj:39-43]()
*   **Roslyn Source Generator**: The code generation tool used in .NET to generate humanized wrappers at compile time. [dotnet/src/CloakBrowser/CloakBrowser.csproj:39-43]()
*   **OIDC Trusted Publishing**: The secure release mechanism used for PyPI and npm. [README.md:149-150]()
*   **Widevine CDM**: The Content Decryption Module required for DRM-protected video playback. [js/src/widevine.ts:25-27](), [cloakbrowser/browser.py:43-44]()

### Code Entity Mapping: Humanize Subsystem
This diagram shows how the high-level concept of "Humanize" translates into specific classes and configuration objects in the code.

Title: Humanize Subsystem Mapping
```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        n1["HumanizeBehavior"] --> n2["MouseMovement"]
        n1["HumanizeBehavior"] --> n3["KeyboardInput"]
        n1["HumanizeBehavior"] --> n4["Presets"]
    end

    subgraph "CodeEntitySpace"
        n1 --- c1["HumanConfig"]
        c1 --- c2["human_config"]
        n2 --- c3["BézierCurves"]
        n3 --- c4["typing_delay"]
        n4 --- c5["'default'"]
        n4 --- c6["'careful'"]
    end
```
**Sources:** [README.md:40-41](), [js/src/playwright.ts:166-179](), [js/src/puppeteer.ts:156-165]()

---
**Sources:**
- [README.md:21-169]()
- [CHANGELOG.md:11-47]()
- [cloakbrowser/config.py:24-43]()
- [js/src/config.ts:30-169]()
- [js/src/download.ts:27-160]()
- [cloakbrowser/download.py:38-205]()
- [js/src/cli.ts:1-140]()
- [js/src/playwright.ts:7-179]()
- [js/src/puppeteer.ts:7-165]()
- [dotnet/src/CloakBrowser/CloakBrowser.csproj:1-50]()
- [cloakbrowser/browser.py:24-173]()