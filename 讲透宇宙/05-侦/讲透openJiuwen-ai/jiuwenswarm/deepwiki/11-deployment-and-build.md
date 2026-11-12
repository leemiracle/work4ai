<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/jiuwenswarm · page 11 Deployment and Build · fetched 2026-11-02 -->

# Deployment and Build

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/Dockerfile.claw](docker/Dockerfile.claw)
- [docker/Dockerfile.claw.base](docker/Dockerfile.claw.base)
- [jiuwenswarm/common/version.py](jiuwenswarm/common/version.py)
- [packages/jiuwenswarm-tui/pyproject.toml](packages/jiuwenswarm-tui/pyproject.toml)
- [scripts/build-exe.bat](scripts/build-exe.bat)
- [scripts/build-exe.ps1](scripts/build-exe.ps1)
- [scripts/build-macos.sh](scripts/build-macos.sh)
- [scripts/build.ps1](scripts/build.ps1)
- [scripts/build.sh](scripts/build.sh)
- [scripts/installer.iss](scripts/installer.iss)
- [scripts/jiuwenswarm.spec](scripts/jiuwenswarm.spec)
- [tests/ui_e2e/cron_ui_report.py](tests/ui_e2e/cron_ui_report.py)
- [tests/ui_e2e/todo_ui_report.py](tests/ui_e2e/todo_ui_report.py)

</details>



This page provides a high-level overview of the build systems and deployment strategies for JiuwenSwarm. The project supports multiple distribution formats, ranging from containerized Docker environments for server-side deployment to standalone desktop executables and specialized terminal UI (TUI) packages.

### Distribution Overview

JiuwenSwarm is built as a multi-process system requiring both a Python backend (AgentServer and Gateway) and a React-based frontend. The build process typically involves two major stages:
1.  **Frontend Compilation**: Building the React SPA located in `jiuwenswarm/channels/web/frontend` using `npm` [scripts/build.sh:12-24]().
2.  **Backend Packaging**: Bundling the Python source, resources, and the compiled frontend into a final distributable format (Docker Image, Wheel, or Executable) [scripts/jiuwenswarm.spec:59-63]().

The following diagram illustrates the relationship between source entities and the resulting build artifacts:

**Build Artifact Pipeline**
```mermaid
graph TD
    subgraph "Source_Space"
        [web_frontend] --> |"npm_run_build"| [dist_folder]
        [jiuwenswarm_python] --> |"pyproject.toml"| [python_env]
        [resources] --> |"agent_templates"| [bundled_data]
    end

    subgraph "Build_Processes"
        [dist_folder] & [python_env] & [bundled_data] --> [build_sh]
        [dist_folder] & [python_env] & [bundled_data] --> [jiuwenswarm_spec]
        [dist_folder] & [python_env] & [bundled_data] --> [Dockerfile_claw]
    end

    subgraph "Deployment_Artifacts"
        [build_sh] --> |"pip_build"| [whl_package]
        [jiuwenswarm_spec] --> |"PyInstaller"| [exe_dmg_bundle]
        [Dockerfile_claw] --> |"Docker_engine"| [container_image]
    end
```
Sources: [scripts/build.sh:1-68](), [scripts/jiuwenswarm.spec:1-63](), [docker/Dockerfile.claw:1-27]()

---

### Docker Deployment
Docker is the recommended method for server-side or headless deployments. The project provides a multi-stage build process to ensure a lean production image.

*   **`Dockerfile.claw`**: The primary container definition that bundles the web frontend and the server. It automates the `npm install` and `npm run build` steps before installing the Python package with `pip install -e ".[all]"` [docker/Dockerfile.claw:13-22]().
*   **Base Images**: `Dockerfile.claw.base` provides a pre-configured environment with Node.js and Python 3.11 to speed up subsequent builds [docker/Dockerfile.claw.base:1-7]().
*   **Networking**: The container exposes port `5173` by default and uses `jiuwenswarm-start` as the entry point [docker/Dockerfile.claw:24-26]().

For detailed configuration and environment variable setup, see [Docker Deployment (#11.1)]().

---

### Desktop Executable and Installer
For end-users requiring a native application experience, JiuwenSwarm can be packaged into a standalone executable for Windows and macOS.

*   **PyInstaller Configuration**: The `jiuwenswarm.spec` file defines how the application is bundled, including hidden imports for critical libraries like `webview`, `chromadb`, and `openjiuwen` [scripts/jiuwenswarm.spec:72-94]().
*   **Platform Scripts**: 
    *   **Windows**: Uses `build-exe.ps1` or `build-exe.bat` to trigger the build, followed by `installer.iss` for creating an Inno Setup installer [scripts/build-exe.bat:1-32](), [scripts/installer.iss:1-49]().
    *   **macOS**: Uses `build-macos.sh` to generate a `.app` bundle and a `.dmg` disk image [scripts/build-macos.sh:1-45]().
*   **Desktop Wrapper**: The application entry point for the executable is `scripts/jiuwenswarm_exe_entry.py`, which leverages `jiuwenswarm.channels.web.desktop_app` [scripts/jiuwenswarm.spec:115](), [scripts/jiuwenswarm.spec:93]().

For details on building the desktop application, see [Desktop Executable and Installer (#11.2)]().

---

### Package Builds (Wheel and TUI)
In addition to full application bundles, JiuwenSwarm supports standard Python packaging.

*   **Core Wheel**: `scripts/build.sh` (or `build.ps1` on Windows) compiles the frontend and generates a `.whl` file using the `build` module [scripts/build.sh:53-56](). It includes a cleanup mechanism to ensure `node_modules` are not included in the final package [scripts/build.sh:34-51]().
*   **JiuwenSwarm TUI**: A specialized package for terminal-based interaction. It is defined in `packages/jiuwenswarm-tui/pyproject.toml` and provides the `jiuwenswarm-tui` entry point [packages/jiuwenswarm-tui/pyproject.toml:1-16]().

**Entity Mapping: Build Scripts to Outputs**
| Script | Primary Tool | Output Artifact | Targeted Platform |
| :--- | :--- | :--- | :--- |
| `build.sh` | `python -m build` | `.whl` package | Cross-platform Python |
| `jiuwenswarm.spec` | `PyInstaller` | `dist/jiuwenswarm/` | Windows/macOS Desktop |
| `installer.iss` | `Inno Setup` | `JiuwenSwarm-setup.exe` | Windows Installer |
| `build-macos.sh` | `hdiutil` | `JiuwenSwarm.dmg` | macOS Disk Image |
| `Dockerfile.claw` | `docker build` | Container Image | Linux/Cloud/Server |

Sources: [scripts/build.sh:53-68](), [scripts/jiuwenswarm.spec:141-171](), [scripts/installer.iss:19-20](), [scripts/build-macos.sh:40-41](), [docker/Dockerfile.claw:1-27]()

---

### Versioning
The project version is centrally managed in `jiuwenswarm/common/version.py` [jiuwenswarm/common/version.py:3](). This version string is referenced across all build scripts, including the macOS `BUNDLE` configuration [scripts/jiuwenswarm.spec:182-183]() and the Inno Setup metadata [scripts/installer.iss:5]().

Sources: [jiuwenswarm/common/version.py:1-3](), [scripts/jiuwenswarm.spec:182-183](), [scripts/installer.iss:5]()

---

