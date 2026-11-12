<!-- source: DeepWiki mcp.deepwiki.com · repo CloakHQ/CloakBrowser · page 2 Getting Started · fetched 2026-10-30 -->

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

