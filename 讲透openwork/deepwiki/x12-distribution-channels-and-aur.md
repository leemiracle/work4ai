<!-- source: DeepWiki mcp.deepwiki.com · repo different-ai/openwork · extra page Distribution Channels and AUR · fetched 2026-10-26 -->

# Distribution Channels and AUR

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/aur-validate.yml](.github/workflows/aur-validate.yml)
- [.github/workflows/daytona-snapshot-drift.yml](.github/workflows/daytona-snapshot-drift.yml)
- [.github/workflows/dev-daytona-snapshot.yml](.github/workflows/dev-daytona-snapshot.yml)
- [.github/workflows/download-stats.yml](.github/workflows/download-stats.yml)
- [.github/workflows/opencode-agents.yml](.github/workflows/opencode-agents.yml)
- [.github/workflows/release-daytona-snapshot.yml](.github/workflows/release-daytona-snapshot.yml)
- [STATS.md](STATS.md)
- [STATS_V2.md](STATS_V2.md)
- [apps/desktop/scripts/electron-after-sign.cjs](apps/desktop/scripts/electron-after-sign.cjs)
- [apps/desktop/scripts/electron-after-sign.test.cjs](apps/desktop/scripts/electron-after-sign.test.cjs)
- [apps/server/README.md](apps/server/README.md)
- [apps/server/bin/openwork-server.mjs](apps/server/bin/openwork-server.mjs)
- [apps/server/bin/platform.mjs](apps/server/bin/platform.mjs)
- [apps/server/scripts/build-opencode-plugin-deps.mjs](apps/server/scripts/build-opencode-plugin-deps.mjs)
- [apps/server/scripts/build-opencode-plugin-deps.test.mjs](apps/server/scripts/build-opencode-plugin-deps.test.mjs)
- [apps/server/scripts/npm-web-smoke.mjs](apps/server/scripts/npm-web-smoke.mjs)
- [apps/server/scripts/publish-npm.mjs](apps/server/scripts/publish-npm.mjs)
- [packaging/aur/.SRCINFO](packaging/aur/.SRCINFO)
- [packaging/aur/PKGBUILD](packaging/aur/PKGBUILD)
- [packaging/aur/README.md](packaging/aur/README.md)
- [scripts/aur/publish-aur.sh](scripts/aur/publish-aur.sh)
- [scripts/aur/update-aur.sh](scripts/aur/update-aur.sh)
- [scripts/prune-daytona-dev-snapshots.mjs](scripts/prune-daytona-dev-snapshots.mjs)
- [scripts/stats.mjs](scripts/stats.mjs)
- [scripts/update-daytona-snapshot-pin.mjs](scripts/update-daytona-snapshot-pin.mjs)

</details>



This page details the various distribution channels for OpenWork, focusing on GitHub releases, updater manifests, npm publishing for `openwork-server`, download stats and metrics tracking, and the automated processes for the Arch User Repository (AUR).

## Overview

OpenWork is distributed through several channels to reach different user bases:
- **GitHub Releases**: Primary source for desktop application binaries across macOS, Windows, and Linux. These releases also serve as the source for updater manifests and AUR tarballs.
- **Updater Manifests**: Used by the Electron desktop application for in-app updates (`latest.json`), ensuring users always have the latest version.
- **npm Publishing**: The `openwork-server` component is published to npm via automated staging and publishing scripts (`apps/server/scripts/publish-npm.mjs`), allowing developers and self-hosters to easily integrate or run the server [apps/server/README.md:1-20](), [apps/server/scripts/publish-npm.mjs:1-110]().
- **Arch User Repository (AUR)**: Provides a community-maintained package for Arch Linux users (`openwork`), leveraging GitHub releases for its source [packaging/aur/PKGBUILD:1-17](), [packaging/aur/.SRCINFO:1-27]().

Sources: [packaging/aur/PKGBUILD:1-17](), [packaging/aur/.SRCINFO:1-27](), [apps/server/README.md:1-20](), [apps/server/scripts/publish-npm.mjs:1-110]()

## npm Publishing of `openwork-server`

The `openwork-server` component packages a filesystem-backed API for remote clients, bundled for Node.js (`apps/server/scripts/publish-npm.mjs`) [apps/server/README.md:1-4](), [apps/server/scripts/publish-npm.mjs:1-25](). 

### Staging Pipeline

The staging script `stageNpmPackage` (`apps/server/scripts/publish-npm.mjs`) builds and arranges the package layout prior to publication:
1. **Node Bundle Verification**: Checks for the existence of the compiled server bundle at `dist/npm-bundle/openwork-server.mjs` [apps/server/scripts/publish-npm.mjs:23-27]().
2. **Web UI & Plugin Validation**: Verifies that the self-hosted web UI bundle (`apps/app/dist/index.html`) and OpenCode plugin distribution files (`dist/opencode-plugins/`) are present [apps/server/scripts/publish-npm.mjs:28-39]().
3. **Plugin Dependencies Archive**: Locates the pre-resolved OpenCode plugin dependency archive (`dist/opencode-plugin-deps-*.tgz`) [apps/server/scripts/publish-npm.mjs:41-47]().
4. **External Dependencies Filtering**: Copies required external runtime dependencies (such as `jsonc-parser`) from the monorepo root package definition [apps/server/scripts/publish-npm.mjs:9-15](), [apps/server/scripts/publish-npm.mjs:49-54]().
5. **Output Assembly**: Stages launchers (`bin/openwork-server.mjs`, `bin/platform.mjs`), bundled scripts, `pdfium.wasm`, plugins, web UI assets, and a clean `package.json` into `dist/npm` [apps/server/scripts/publish-npm.mjs:56-93]().

### Natural Language to Code: npm Publishing Flow

Title: "npm Package Staging and Publishing Pipeline"
```mermaid
graph TD
    subgraph "Natural_Language_Space"
        "Stage Package Files"["Stage files into dist/npm"]
        "Check Bundle Integrity"["Verify server bundle & WASM"]
        "Publish to npm Registry"["Run pnpm publish"]
    end

    subgraph "Code_Entity_Space"
        "stageNpmPackage"["apps/server/scripts/publish-npm.mjs:stageNpmPackage"]
        "BUNDLE_EXTERNAL_DEPENDENCIES"["apps/server/scripts/publish-npm.mjs:BUNDLE_EXTERNAL_DEPENDENCIES"]
        "main"["apps/server/scripts/publish-npm.mjs:main"]
    end

    "Stage Package Files" --> "stageNpmPackage"
    "Check Bundle Integrity" --> "BUNDLE_EXTERNAL_DEPENDENCIES"
    "Publish to npm Registry" --> "main"
```

Sources: [apps/server/scripts/publish-npm.mjs:1-110]()

## AUR Packaging

This document describes the Arch Linux User Repository (AUR) packaging workflow for OpenWork. It covers the `PKGBUILD` structure, automated update scripts, and the process for maintaining the package and its metadata for both `x86_64` and `aarch64` architectures.

### Overview

OpenWork provides an AUR package named `openwork` that distributes pre-built Electron bundles from GitHub releases [packaging/aur/PKGBUILD:5-10](). The current packaging approach downloads platform-specific `.tar.gz` bundles, installs them under `/opt/openwork`, and sets up the necessary system integration including desktop entries, icons, and binary symlinks [packaging/aur/PKGBUILD:39-64]().

The AUR workflow consists of:
- **PKGBUILD and .SRCINFO**: Package metadata and build instructions [packaging/aur/PKGBUILD:1-64](), [packaging/aur/.SRCINFO:1-27]().
- **Update Scripts**: Automated version and checksum updates via `update-aur.sh` [scripts/aur/update-aur.sh:1-106]().
- **Publish Scripts**: Logic to push changes to the official AUR repository via `publish-aur.sh` [scripts/aur/publish-aur.sh:1-69]().
- **CI Validation**: GitHub Actions workflow to validate the package using `namcap` and `makepkg` within an Arch Linux container [.github/workflows/aur-validate.yml:1-181]().

Sources: [packaging/aur/PKGBUILD:1-64](), [packaging/aur/.SRCINFO:1-27](), [scripts/aur/update-aur.sh:1-106](), [scripts/aur/publish-aur.sh:1-69](), [.github/workflows/aur-validate.yml:1-181]()

### PKGBUILD Structure

#### Package Metadata

The `PKGBUILD` defines the basic package information and supported architectures:

| Field | Value | Description |
|-------|-------|-------------|
| `pkgname` | `openwork` | AUR package name [packaging/aur/PKGBUILD:5]() |
| `pkgver` | `0.0.0` | Current version (auto-updated) [packaging/aur/PKGBUILD:6]() |
| `pkgrel` | `1` | Package release number [packaging/aur/PKGBUILD:7]() |
| `arch` | `('x86_64' 'aarch64')` | Supported CPU architectures [packaging/aur/PKGBUILD:9]() |
| `license` | `('MIT')` | Software license [packaging/aur/PKGBUILD:11]() |
| `options` | `(!strip)` | Disables symbol stripping to preserve Electron binary integrity [packaging/aur/PKGBUILD:13]() |

Sources: [packaging/aur/PKGBUILD:5-13]()

#### Dependencies

Runtime dependencies include libraries required by the Electron runtime and Chrome sandbox:

```bash
depends=('gtk3' 'nss' 'alsa-lib' 'libxss' 'libxtst' 'xdg-utils' 'at-spi2-core' 'libdrm' 'libxkbcommon' 'mesa' 'dbus' 'hicolor-icon-theme')
```

These ensure the application can render the UI and interact with system services like D-Bus and X11/Wayland [packaging/aur/PKGBUILD:12]().

Sources: [packaging/aur/PKGBUILD:12]()

#### Architecture-Specific Sources

The package dynamically resolves source URLs based on the target architecture:

- **x86_64**: Downloads `openwork-linux-x64-${pkgver}.tar.gz` from GitHub releases [packaging/aur/PKGBUILD:16-17]().
- **aarch64**: Downloads `openwork-linux-arm64-${pkgver}.tar.gz` from GitHub releases [packaging/aur/PKGBUILD:19-20]().

Sources: [packaging/aur/PKGBUILD:16-20]()

#### Package Function and Installation Logic

The `package()` function handles the layout of the application on the filesystem:

1. **Extraction**: Identifies the correct `bundle_dir` based on the current architecture `${CARCH}` [packaging/aur/PKGBUILD:23-37]().
2. **Installation to /opt**: Copies the entire unpacked bundle to `/opt/openwork` [packaging/aur/PKGBUILD:39-40]().
3. **Binary Symlinking**: Creates a symlink at `/usr/bin/openwork` pointing to `/opt/openwork/openwork` [packaging/aur/PKGBUILD:42-44]().
4. **Icon Installation**: Installs `openwork-logo-square.svg` to `/usr/share/icons/hicolor/scalable/apps/openwork.svg` [packaging/aur/PKGBUILD:46-47]().
5. **Desktop Entry**: Generates a `.desktop` file at `/usr/share/applications/openwork.desktop` with support for the `openwork://` URI scheme [packaging/aur/PKGBUILD:49-61]().
6. **Security**: Sets permissions (`chmod 4755`) on `chrome-sandbox` for correct Electron sandboxing [packaging/aur/PKGBUILD:63]().

Sources: [packaging/aur/PKGBUILD:22-64]()

## Automated Update Workflow

The repository includes scripts to synchronize the AUR package with new GitHub releases.

### Natural Language to Code: Update Logic

Title: "AUR Metadata Update Flow"
```mermaid
graph TD
    subgraph "Natural_Language_Space"
        "Bump version in PKGBUILD"["Bump version in PKGBUILD"]
        "Calculate SHA256 for x64/arm64"["Calculate SHA256 for x64/arm64"]
        "Sync metadata"["Sync .SRCINFO with PKGBUILD"]
    end

    subgraph "Code_Entity_Space"
        "update-aur.sh"["scripts/aur/update-aur.sh"]
        "Python_Regex_Block"["Python re.sub block in update-aur.sh"]
        "SRCINFO_Logic"["SRCINFO update logic in update-aur.sh"]
    end

    "Bump version in PKGBUILD" --> "update-aur.sh"
    "update-aur.sh" --> "Python_Regex_Block"
    "Calculate SHA256 for x64/arm64" --> "update-aur.sh"
    "Sync metadata" --> "SRCINFO_Logic"
```

Sources: [scripts/aur/update-aur.sh:1-106]()

### Update Script Details

The `update-aur.sh` script automates the metadata refresh:
1. **Asset Download**: Downloads the `.tar.gz` bundles for both `x64` and `arm64` from the specified GitHub release tag [scripts/aur/update-aur.sh:40-41]().
2. **Checksum Calculation**: Computes `sha256sum` for both architectures [scripts/aur/update-aur.sh:44-45]().
3. **PKGBUILD Update**: Uses an embedded Python block to perform regex replacement on `pkgver`, `pkgrel`, `sha256sums_x86_64`, and `sha256sums_aarch64` [scripts/aur/update-aur.sh:47-63]().
4. **.SRCINFO Update**: Updates the `.SRCINFO` file to reflect the new version, renamed source files, and checksums [scripts/aur/update-aur.sh:65-106]().

Sources: [scripts/aur/update-aur.sh:40-106]()

## Publish Workflow

The `publish-aur.sh` script handles the Git operations required to push changes to the official AUR repository.

### Natural Language to Code: Publish Logic

Title: "AUR Publishing Authentication and Push"
```mermaid
graph TD
    subgraph "Natural_Language_Space"
        "Auth via SSH"["Authenticate via SSH Key"]
        "Clone AUR Repo"["Clone AUR Git Repo"]
        "Commit Changes"["Commit PKGBUILD changes"]
        "Push to AUR"["Push to aur.archlinux.org"]
    end

    subgraph "Code_Entity_Space"
        "publish-aur.sh"["scripts/aur/publish-aur.sh"]
        "AUR_SSH_PRIVATE_KEY"["AUR_SSH_PRIVATE_KEY secret"]
        "AUR_REMOTE"["ssh://aur@aur.archlinux.org/openwork.git"]
    end

    "Auth via SSH" --> "AUR_SSH_PRIVATE_KEY"
    "Clone AUR Repo" --> "publish-aur.sh"
    "Commit Changes" --> "publish-aur.sh"
    "Push to AUR" --> "AUR_REMOTE"
```

Sources: [scripts/aur/publish-aur.sh:1-69]()

### Publish Script Details

1. **Authentication**: Uses the `AUR_SSH_PRIVATE_KEY` environment variable to configure a temporary SSH key and populates `known_hosts` for `aur.archlinux.org` [scripts/aur/publish-aur.sh:18-45]().
2. **Repository Sync**: Clones the official AUR repository, copies the updated `PKGBUILD` and `.SRCINFO` from the local `packaging/aur/` directory, and commits the changes using "OpenWork Release Bot" [scripts/aur/publish-aur.sh:47-62]().
3. **Push**: Pushes the commit to the AUR remote [scripts/aur/publish-aur.sh:69]().

Sources: [scripts/aur/publish-aur.sh:18-69]()

## Validation and CI

The `aur-validate.yml` workflow provides automated testing of the AUR package [.github/workflows/aur-validate.yml:1-123]():
- **Environment**: Runs in an `archlinux:latest` container [.github/workflows/aur-validate.yml:124-125]().
- **Tools**: Installs `base-devel`, `namcap`, `jq`, `git`, and `sudo` for unprivileged `makepkg` execution [.github/workflows/aur-validate.yml:170-181]().
- **Validation Modes**: Supports `smoke` (basic build verification) and `publish-ready` (comprehensive checks including `namcap`) [.github/workflows/aur-validate.yml:22-29]().
- **Artifact Sourcing**: Can validate against local build artifacts or existing GitHub releases [.github/workflows/aur-validate.yml:30-37]().

Sources: [.github/workflows/aur-validate.yml:1-181]()

---

