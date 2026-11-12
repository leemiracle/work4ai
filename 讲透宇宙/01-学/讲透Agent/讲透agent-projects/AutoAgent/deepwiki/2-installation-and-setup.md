<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/AutoAgent · page 2 Installation and Setup · fetched 2026-10-29 -->

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/autoagent-intro.png](assets/autoagent-intro.png)
- [assets/autoagent.png](assets/autoagent.png)
- [assets/video_v1_compressed.mp4](assets/video_v1_compressed.mp4)
- [docs/docs/Get-Started/get-started-installation.md](docs/docs/Get-Started/get-started-installation.md)
- [docs/docs/Get-Started/get-started-quickstart.md](docs/docs/Get-Started/get-started-quickstart.md)
- [setup.cfg](setup.cfg)

</details>



This page provides comprehensive instructions for installing AutoAgent and configuring the basic environment. It covers system requirements, installation procedures, and initial configuration steps needed to get AutoAgent running.

For detailed API key configuration and environment variables, see [API Keys and Configuration](#2.1). For WeChat integration setup, see [WeChat Integration Setup](#2.2).

## System Requirements

AutoAgent requires specific system components and dependencies to function properly. The framework operates across multiple environments and integrates with various external services.

### Core Requirements

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| Python | 3.10+ | Runtime environment [setup.cfg:71]() |
| Docker | Latest stable | Isolated code execution environments |
| Git | Latest stable | Repository management |
| Git LFS | Enabled | Large file handling for video/image assets |

### Hardware Requirements

- **Memory**: Minimum 8GB RAM recommended.
- **Storage**: 10GB+ available space for containers and assets.
- **Network**: Stable internet connection for LLM APIs and container image pulls.

**Installation Architecture**

```mermaid
graph TB
    subgraph "Installation Process"
        [GitClone] --> [LocalRepo]
        [LocalRepo] --> [PipInstall]
        [PipInstall] --> [PackageInstall]
    end
    
    subgraph "Configuration Files"
        [setup.cfg] --> [Dependencies]
        [EnvTemplate] --> [EnvFile]
        [EnvFile] --> [APIKeys]
    end
    
    subgraph "Runtime Dependencies"
        [Dependencies] --> [PythonDeps]
        [Dependencies] --> [DockerImages]
        [Dependencies] --> [CLIEntry]
    end
    
    subgraph "External Services"
        [DockerHub] --> [DockerImages]
        [LLMProviders] --> [APIKeys]
        [GitLFS] --> [Assets]
    end
    
    [PackageInstall] --> [CLIEntry]
    [CLIEntry] --> [AutoCLI]
    
    [GitClone] ["git clone"]
    [LocalRepo] ["Local Repository"]
    [PipInstall] ["pip install -e ."]
    [PackageInstall] ["Package Installation"]
    [EnvTemplate] [".env.template"]
    [EnvFile] [".env"]
    [APIKeys] ["API Keys Configuration"]
    [PythonDeps] ["Python Packages"]
    [DockerImages] ["Docker Images"]
    [CLIEntry] ["CLI Entry Points"]
    [AutoCLI] ["'auto' command"]
    [Assets] ["Static Assets (.mp4, .svg)"]
```

Sources: [README.md:212-216](), [setup.cfg:1-81](), [setup.cfg:71]()

## Installation Process

### Step 1: Repository Setup

Clone the AutoAgent repository and navigate to the project directory:

```bash
git clone https://github.com/HKUDS/AutoAgent.git
cd AutoAgent
```

The repository includes Git LFS configuration for managing large assets in the `assets/` directory, such as `video_v1_compressed.mp4` [assets/video_v1_compressed.mp4:1-38]().

### Step 2: Package Installation

Install AutoAgent in development mode to enable local modifications:

```bash
pip install -e .
```

This command processes the configuration in `setup.cfg` [setup.cfg:1-81]() and installs all required dependencies, including `litellm`, `browsergym`, and `openai` [setup.cfg:16-66]().

### Step 3: Docker Setup

Install Docker for containerized execution environments. AutoAgent uses Docker to provide isolated environments for agents to run code safely. The framework automatically pulls the appropriate pre-built Docker images based on your system architecture when needed [README.md:65]().

**Package Dependencies and Entry Points**

```mermaid
graph LR
    subgraph "setup.cfg Configuration"
        [MetaData] --> [PackageInfo]
        [Options] --> [PackageDir]
        [Options] --> [InstallReqs]
        [EntryPoints] --> [ConsoleScripts]
    end
    
    subgraph "Core Dependencies"
        [InstallReqs] --> [LLMDeps]
        [InstallReqs] --> [WebDeps]
        [InstallReqs] --> [DataDeps]
        [InstallReqs] --> [UtilDeps]
    end
    
    subgraph "CLI Integration"
        [ConsoleScripts] --> [AutoCLI]
        [AutoCLI] --> [CLIModule]
        [CLIModule] --> [MainCommands]
    end
    
    [MetaData] ["metadata"]
    [PackageInfo] ["name: autoagent<br/>version: 0.1.0"]
    [Options] ["options"]
    [PackageDir] ["package_dir: ."]
    [InstallReqs] ["install_requires"]
    [EntryPoints] ["entry_points"]
    [ConsoleScripts] ["console_scripts"]
    [LLMDeps] ["openai>=1.52.0<br/>litellm==1.55.0"]
    [WebDeps] ["browsergym==0.13.0<br/>playwright==1.39.0"]
    [DataDeps] ["chromadb<br/>datasets<br/>pandas"]
    [UtilDeps] ["click<br/>inquirer<br/>loguru"]
    [AutoCLI] ["auto = autoagent.cli:cli"]
    [CLIModule] ["autoagent.cli"]
    [MainCommands] ["auto main<br/>auto deep-research"]
```

Sources: [setup.cfg:10-81](), [setup.cfg:73-75]()

## Basic Configuration

### Environment Variables

Create a `.env` file based on the provided template to configure API keys and system settings:

```bash
cp .env.template .env
```

Edit the `.env` file with your API keys. The GitHub token is required for many operations, while LLM provider keys are optional based on your preferred model provider.

```bash
# Required
GITHUB_AI_TOKEN=your_github_token

# Optional - Configure as needed
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
```

For a full list of supported environment variables and model compatibility flags, see [API Keys and Configuration](#2.1).

### CLI Command Structure

The installation creates the `auto` command with multiple subcommands as defined in the entry points [setup.cfg:73-75]():

| Command | Purpose |
|---------|---------|
| `auto main` | Launches the main AutoAgent interface for selecting modes. |
| `auto deep-research` | Direct entry to the Deep Research (User Mode) assistant. |

### Container Configuration

AutoAgent supports customizable container settings for execution environments, typically configured via command-line arguments:

- `--container_name`: Docker container identifier.
- `--port`: Container port mapping for the TCP bridge.
- `--git_clone`: Repository mirroring for self-modification.

Sources: [README.md:224-241](), [README.md:248-260](), [setup.cfg:73-75]()

## Verification

### Installation Verification

Test the installation by running the help command:

```bash
auto --help
```

This should display available commands and options from the CLI entry point [setup.cfg:74-75]().

### Environment Verification

Verify Docker installation and connectivity to ensure the agent can launch execution environments:

```bash
docker --version
docker info
```

### Configuration Verification

Test basic configuration by attempting to start AutoAgent:

```bash
auto main
```

The system will validate API keys and Docker availability before launching the interface.

## Common Installation Issues

### Python Version Compatibility
AutoAgent requires Python 3.10 or higher [setup.cfg:71](). Verify your version with `python --version`.

### Docker Permission Issues
On Linux systems, ensure your user has Docker permissions to avoid `sudo` requirements for every agent action:
```bash
sudo usermod -aG docker $USER
```

### Git LFS Issues
If assets like the intro video or logo are missing, ensure Git LFS is installed and assets are pulled [README.md:4]():
```bash
git lfs install
git lfs pull
```

Sources: [README.md:208-221](), [setup.cfg:16-66](), [setup.cfg:71]()

---

