<!-- source: DeepWiki mcp.deepwiki.com · repo mvanhorn/last30days-skill · extra page Credential Stores and Cookie Extraction · fetched 2026-10-26 -->

# Credential Stores and Cookie Extraction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [changelog.d/+safari-cookie-domain-match.security.md](changelog.d/+safari-cookie-domain-match.security.md)
- [docs/plans/2026-08-31-feat-bird-cookies-linux-macmini-plan.md](docs/plans/2026-08-31-feat-bird-cookies-linux-macmini-plan.md)
- [skills/last30days/scripts/box_chrome_login.py](skills/last30days/scripts/box_chrome_login.py)
- [skills/last30days/scripts/lib/agentcookie.py](skills/last30days/scripts/lib/agentcookie.py)
- [skills/last30days/scripts/lib/chrome_cdp.py](skills/last30days/scripts/lib/chrome_cdp.py)
- [skills/last30days/scripts/lib/chrome_cookies.py](skills/last30days/scripts/lib/chrome_cookies.py)
- [skills/last30days/scripts/lib/cookie_extract.py](skills/last30days/scripts/lib/cookie_extract.py)
- [skills/last30days/scripts/lib/safari_cookies.py](skills/last30days/scripts/lib/safari_cookies.py)
- [skills/last30days/scripts/setup-keychain.sh](skills/last30days/scripts/setup-keychain.sh)
- [skills/last30days/scripts/setup-pass.sh](skills/last30days/scripts/setup-pass.sh)
- [tests/test_agentcookie.py](tests/test_agentcookie.py)
- [tests/test_box_chrome_login.py](tests/test_box_chrome_login.py)
- [tests/test_chrome_cdp.py](tests/test_chrome_cdp.py)
- [tests/test_chrome_cookies.py](tests/test_chrome_cookies.py)
- [tests/test_cookie_extract.py](tests/test_cookie_extract.py)
- [tests/test_env_keychain.py](tests/test_env_keychain.py)
- [tests/test_env_pass.py](tests/test_env_pass.py)
- [tests/test_safari_cookies.py](tests/test_safari_cookies.py)
- [tests/test_x_extras_gating.py](tests/test_x_extras_gating.py)

</details>



## Purpose and Scope
This page provides a technical deep dive into how the `last30days` engine securely manages API keys, secrets, and local browser session cookies. It covers cross-platform secret storage primitives (macOS Keychain, Linux `pass`, and restricted `.env` file permissions) as well as zero-configuration browser cookie acquisition engines. This subsystem bypasses manual token generation by extracting live session credentials directly from local browser stores (Firefox, Chromium-based browsers, and Safari) and remote debugging endpoints (`chrome_cdp`, `agentcookie`, and `box_chrome_login`).

---

## 1. Secret Storage and Platform Backends

The engine resolves configuration through a prioritized cascade where persistent system secret stores act as secure fallbacks for local environment files.

### macOS Keychain Integration
On macOS systems, API keys and authentication tokens are stored as generic passwords using the system `security` binary. The `setup-keychain.sh` script automates storage using service names prefixed with `last30days-<KEY>` for the active user `[skills/last30days/scripts/setup-keychain.sh:1-46]()`. 
* **Security Guard:** The setup script validates that keychain read queries (`security find-generic-password`) never request plaintext outputs into logs or intermediate shell variables outside secure subprocess boundaries [tests/test_env_keychain.py:27-39]().
* **Opt-Out Control:** Setting the environment variable `LAST30DAYS_SKIP_KEYCHAIN=1` short-circuits keychain loading entirely in `lib/env.py` [tests/test_env_keychain.py:106-120]().

### Linux/Unix `pass` Password Manager
For POSIX environments lacking macOS Keychain, the engine integrates with `pass(1)` via `setup-pass.sh`. Secrets are stored under the path prefix `last30days/<KEY>` (or `LAST30DAYS_PASS_PREFIX`) [skills/last30days/scripts/setup-pass.sh:1-48](). The loader queries `pass show` during preflight initialization to populate missing environment keys without exposing them on the command line.

### File Permissions and `.env` Hardening
Local `.env` files are checked for restrictive file permissions. To prevent unauthorized access by multi-tenant local users, configuration loaders enforce that files containing tokens (`AUTH_TOKEN`, `CT0`, API keys) reside in directories with restricted read/write flags.

```mermaid
title "Credential Priority Resolution and Storage Backends"
graph TD
    subcode ["Code Entity Space"]
        Config["lib/env.py::get_config"]
        EnvFile["Environment Variables (.env)"]
        Keychain["lib/env._load_keychain"]
        PassStore["lib/env._load_pass"]
    end

    EnvFile -->|"Highest Priority"| Config
    Keychain -->|"macOS Darwin Fallback"| Config
    PassStore -->|"Linux/POSIX Fallback"| Config

    style Config fill:#none,stroke:#333,stroke-width:2px
    style Keychain fill:#none,stroke:#333,stroke-width:2px
    style PassStore fill:#none,stroke:#333,stroke-width:2px
```
*Sources: [skills/last30days/scripts/setup-keychain.sh:1-46](), [skills/last30days/scripts/setup-pass.sh:1-48](), [tests/test_env_keychain.py:106-120]()*

---

## 2. Browser Cookie Extraction Engine

To achieve zero-config authentication for services like X/Twitter (`auth_token` and `ct0`), the engine extracts cookies directly from active browser profile databases on disk.

### Firefox Cookie Extraction (`cookie_extract.py`)
Firefox stores cookies in SQLite databases (`cookies.sqlite`) within profile directories located via `profiles.ini` [skills/last30days/scripts/lib/cookie_extract.py:66-135]().
* **TOCTOU Mitigation:** Because Firefox locks `cookies.sqlite` at runtime, the engine copies the database to a temporary file using `tempfile.mkstemp()` [skills/last30days/scripts/lib/cookie_extract.py:174-182](). To eliminate the Time-Of-Check-To-Time-Of-Use window where `copy2` might temporarily expose live session secrets with looser source permissions, the file is written directly via `copyfile` and immediately locked with `_lock_temp_cookie_copy` enforcing `0o600` permissions on POSIX systems [skills/last30days/scripts/lib/cookie_extract.py:25-30, 174-182]().
* **WSL Support:** Under Windows Subsystem for Linux (WSL), the module automatically scans `/mnt/c/Users/*/AppData/Roaming/Mozilla/Firefox` to locate Windows host profiles [skills/last30days/scripts/lib/cookie_extract.py:33-63]().

### Chromium-Based Browser Cookie Extraction (`chrome_cookies.py`)
Chromium-based browsers (Chrome, Brave, Edge, Vivaldi, Opera, Arc) store cookies encrypted using **v10 encryption** (AES-128-CBC with a key derived from the OS Keychain via PBKDF2) [skills/last30days/scripts/lib/chrome_cookies.py:1-12]().
* **Key Derivation:** The passphrase is retrieved from the macOS Keychain service (e.g., `Chrome Safe Storage`, `Brave Safe Storage`) and passed into `_derive_aes_key()` using PBKDF2-HMAC-SHA1 (`1003` iterations) [skills/last30days/scripts/lib/chrome_cookies.py:54-108]().
* **Decryption Pipeline:** Ciphertexts are decrypted using the system `openssl` CLI (`-aes-128-cbc`, `-nopad`), followed by PKCS7 padding removal (`_remove_pkcs7_padding`) [skills/last30days/scripts/lib/chrome_cookies.py:111-185](). For Chromium 130+ databases (`db_version >= 24`), a 32-byte SHA-256 prefix is stripped from the plaintext buffer [skills/last30days/scripts/lib/chrome_cookies.py:151-154]().

### Safari Binary Cookie Extraction (`safari_cookies.py`)
Safari stores cookies in `~/Library/Cookies/Cookies.binarycookies`, an unparsed binary format [skills/last30days/scripts/lib/safari_cookies.py:1-8]().
* **Parser Architecture:** `_parse_binary_cookies()` validates the `cook` magic header, unpacks big-endian page size tables, and extracts individual cookie records [skills/last30days/scripts/lib/safari_cookies.py:157-203]().
* **Domain Matching:** `_host_matches()` verifies host boundaries strictly, ensuring stored cookies with leading dots (`.x.com`) or subdomains match exact targets without matching malicious substrings (e.g., rejecting `x.com.evil.tld`) [skills/last30days/scripts/lib/safari_cookies.py:144-155]().

---

## 3. Extras-Host Authentication and CDP/Sidecar Acquisition

On non-macOS platforms (Linux servers, headless nodes) or specific agent sink roles where local browser DBs cannot be directly decrypted, the engine falls back to remote debugging and sidecar acquisition protocols.

### Chrome DevTools Protocol (`chrome_cdp.py`) and Agent Cookies (`agentcookie.py`)
* `chrome_cdp.py` connects to running Chromium instances exposing remote debugging ports (defaulting to the last30days extras NUX port `18800`) to inspect live document cookies via CDP [skills/last30days/scripts/box_chrome_login.py:15-46]().
* `agentcookie.py` orchestrates helper sidecar processes to retrieve authenticated headers securely across container boundaries.

### Box Chrome Login Helper (`box_chrome_login.py`)
When browser cookies are entirely absent on an extras host, `box_chrome_login.py` generates gated launch recipes for disposable sign-in sessions [skills/last30days/scripts/box_chrome_login.py:1-27]().
* **Safety Guards:** On official-only hosts (`LAST30DAYS_HOST=grok-bot`), the helper suppresses browser launch recipes entirely, enforcing official API-only retrieval policies [skills/last30days/scripts/box_chrome_login.py:51-84]().
* **Binary Constraints:** It strictly wraps the host `box-chrome` binary (which sets `--class=box-chrome`) to prevent session initialization failures associated with raw `google-chrome-stable` flag soups [skills/last30days/scripts/box_chrome_login.py:20-26, 102-140]().

```mermaid
title "Natural Language Space to Code Entity Space: Host-Gated X Cookie Discovery Pipeline"
graph TD
    subcode ["Code Entity Space"]
        EnvCheck["lib/env.x_extras_enabled"]
        PolicyCheck["lib/env.x_policy"]
        CookieExtract["lib/cookie_extract.extract_cookies"]
        ChromeCDP["lib/chrome_cdp.read_x_cookies"]
        AgentCookie["lib/agentcookie.read_x_cookies"]
        BoxLogin["box_chrome_login.build_recipe"]
    end

    PolicyCheck -->|"Cookie Discovery Enabled?"| EnvCheck
    EnvCheck -->|"MacBook / Standard Host"| CookieExtract
    EnvCheck -->|"Linux / Extras Host"| AgentCookie
    AgentCookie -->|"Fallback"| ChromeCDP
    ChromeCDP -->|"Unauthenticated"| BoxLogin

    style EnvCheck fill:#none,stroke:#333,stroke-width:2px
    style PolicyCheck fill:#none,stroke:#333,stroke-width:2px
    style CookieExtract fill:#none,stroke:#333,stroke-width:2px
    style ChromeCDP fill:#none,stroke:#333,stroke-width:2px
    style AgentCookie fill:#none,stroke:#333,stroke-width:2px
    style BoxLogin fill:#none,stroke:#333,stroke-width:2px
```
*Sources: [skills/last30days/scripts/lib/cookie_extract.py:1-182](), [skills/last30days/scripts/box_chrome_login.py:1-140](), [tests/test_x_extras_gating.py:40-105]()*

---

