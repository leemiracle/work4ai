<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/AutoAgent · page 6 Development and Contributing · fetched 2026-10-29 -->

# Development and Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.template](.env.template)
- [.gitignore](.gitignore)
- [assets/cookies/export.png](assets/cookies/export.png)
- [assets/cookies/extension.png](assets/cookies/extension.png)
- [docs/docs/Dev-Guideline/dev-guide-build-your-project.md](docs/docs/Dev-Guideline/dev-guide-build-your-project.md)
- [setup.cfg](setup.cfg)

</details>



This document provides guidance for developers who want to contribute to the AutoAgent project, set up a development environment, and understand the codebase structure. It covers development setup, package dependencies, asset management, and contribution workflows.

For information about extending AutoAgent with custom functionality, see [Extending AutoAgent](#6.3). For understanding the overall project structure, see [Project Structure](#6.1). For details on asset management and Git LFS configuration, see [Asset Management](#6.2).

## Development Environment Setup

### Prerequisites and Dependencies

AutoAgent requires Python 3.10 or higher and includes a comprehensive set of dependencies for AI, web automation, and document processing capabilities. The project uses a standard Python package structure with `setup.cfg` for configuration.

#### Development Setup Workflow

```mermaid
graph TB
    subgraph "Environment Setup"
        [PythonInstall] -- "Python 3.10+ Installation"
        [VenvCreate] -- "Virtual Environment Creation"
        [CloneRepo] -- "Repository Clone"
    end
    
    subgraph "Package Installation"
        [InstallDeps] -- "pip install -e ."
        [SetupCfg] -- "setup.cfg Processing"
        [EntryPoint] -- "Console Script Registration: auto = autoagent.cli:cli"
    end
    
    subgraph "Development Tools"
        [PreCommit] -- "pre-commit Hooks"
        [Pytest] -- "pytest Testing Framework"
        [Autopep8] -- "Code Formatting: max_line_length = 120"
    end
    
    subgraph "Verification"
        [CLITest] -- "CLI Command Test: auto --help"
        [ImportTest] -- "Package Import Test: import autoagent"
        [UnitTests] -- "Unit Test Execution: pytest"
    end
    
    [PythonInstall] --> [VenvCreate]
    [VenvCreate] --> [CloneRepo]
    [CloneRepo] --> [InstallDeps]
    [InstallDeps] --> [SetupCfg]
    [SetupCfg] --> [EntryPoint]
    [EntryPoint] --> [PreCommit]
    [PreCommit] --> [Pytest]
    [Pytest] --> [Autopep8]
    [Autopep8] --> [CLITest]
    [CLITest] --> [ImportTest]
    [ImportTest] --> [UnitTests]
```

Sources: [setup.cfg:1-81](), [setup.cfg:71-71]()

### Core Dependencies Architecture

The project includes multiple categories of dependencies that support different aspects of the AutoAgent framework:

#### Dependency Categories and Code Integration

```mermaid
graph LR
    subgraph "AI and LLM Dependencies"
        ["openai>=1.52.0"]
        ["litellm==1.55.0"]
        ["instructor"]
        ["huggingface_hub"]
        ["sentence_transformers"]
        ["tiktoken"]
    end
    
    subgraph "Web Automation Dependencies"
        ["playwright==1.39.0"]
        ["browsergym==0.13.0"]
        ["beautifulsoup4"]
        ["requests"]
        ["httpx"]
    end
    
    subgraph "Document Processing Dependencies"
        ["docling"]
        ["html2text"]
        ["mammoth"]
        ["pdfminer.six"]
        ["python_pptx"]
        ["markdownify"]
    end
    
    subgraph "Data and Storage Dependencies"
        ["chromadb"]
        ["pandas"]
        ["numpy"]
        ["datasets"]
        ["networkx"]
    end
    
    subgraph "CLI and UI Dependencies"
        ["click"]
        ["inquirer"]
        ["rich"]
        ["prompt_toolkit"]
        ["Flask"]
        ["loguru"]
    end
    
    subgraph "Core AutoAgent Modules"
        ["autoagent.cli:cli"]
        ["autoagent.agents"]
        ["autoagent.environments"]
        ["autoagent.tools"]
    end
    
    ["openai>=1.52.0"] --> ["autoagent.agents"]
    ["litellm==1.55.0"] --> ["autoagent.agents"]
    ["playwright==1.39.0"] --> ["autoagent.environments"]
    ["browsergym==0.13.0"] --> ["autoagent.environments"]
    ["chromadb"] --> ["autoagent.agents"]
    ["click"] --> ["autoagent.cli:cli"]
    ["docling"] --> ["autoagent.tools"]
    ["html2text"] --> ["autoagent.tools"]
```

Sources: [setup.cfg:16-65](), [setup.cfg:69-69]()

## Package Configuration and Build System

### Setup Configuration Structure

The `setup.cfg` file defines the package metadata, dependencies, and build configuration:

| Configuration Section | Purpose | Key Settings |
|----------------------|---------|--------------|
| `[metadata]` | Package information | `name = autoagent`, `version = 0.1.0`, `author = jiabintang` |
| `[options]` | Package structure | `packages = find_namespace`, `python_requires = >=3.10` |
| `[options.entry_points]` | CLI registration | `console_scripts = auto = autoagent.cli:cli` |
| `[options.packages.find]` | Package discovery | `where = .`, `include = autoagent*` |
| `[tool.autopep8]` | Code formatting | `max_line_length = 120`, `aggressive = 3` |

### Package Structure and Entry Points

The project uses a namespace package structure with the main entry point registered as a console script:

```mermaid
graph TB
    subgraph "Package Structure"
        [RootDir] -- "."
        [AutoAgentPkg] -- "autoagent Package"
        [SubPackages] -- "autoagent.* Subpackages"
    end
    
    subgraph "Entry Point Registration"
        [ConsoleScript] -- "console_scripts Section"
        [AutoCommand] -- "auto Command"
        [CLIModule] -- "autoagent.cli:cli Function"
    end
    
    subgraph "Build System"
        [SetupCfg] -- "setup.cfg Configuration"
        [FindNamespace] -- "find_namespace Package Discovery"
        [ZipSafe] -- "zip_safe = True"
        [IncludePackageData] -- "include_package_data = True"
    end
    
    [RootDir] --> [AutoAgentPkg]
    [AutoAgentPkg] --> [SubPackages]
    [ConsoleScript] --> [AutoCommand]
    [AutoCommand] --> [CLIModule]
    [SetupCfg] --> [FindNamespace]
    [FindNamespace] --> [ZipSafe]
    [ZipSafe] --> [IncludePackageData]
```

Sources: [setup.cfg:10-15](), [setup.cfg:67-75]()

## Asset Management and Git Configuration

### Git LFS Configuration

The project includes Git LFS (Large File Storage) configuration for managing large binary files. The `.gitattributes` file handles specific file types like MP4 to prevent repository bloat.

Sources: [.gitattributes:1]()

### Ignored Development Artifacts

The `.gitignore` file specifies directories and files that should not be tracked, including temporary workplaces, logs, and sensitive environment variables.

| Category | Patterns |
|----------|----------|
| Workspaces | `workplace_*/`, `workspace_*/`, `terminal_tmp/*` |
| Logs/DB | `*.log`, `code_db/*`, `logs/*`, `__pycache__/` |
| Results | `results/*`, `evaluation_results/*`, `casestudy_results/*` |
| Secrets | `.env` |

Sources: [.gitignore:1-31]()

## Development Workflow and Standards

### Code Quality and Formatting

The project includes `autopep8` configuration for consistent code formatting:

| Setting | Value | Purpose |
|---------|-------|---------|
| `max_line_length` | 120 | Maximum line length for code |
| `ignore` | E501,W6 | Ignored PEP8 warnings |
| `in-place` | true | Modify files in place |
| `recursive` | true | Process directories recursively |
| `aggressive` | 3 | Aggressiveness level for formatting |

Sources: [setup.cfg:76-81]()

### Testing Framework

The project uses `pytest` for testing. Development is supported by `pre-commit` hooks to ensure standards are met before code is pushed.

Sources: [setup.cfg:19-22]()

## Contributing Guidelines

### Development Setup Commands

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd AutoAgent
   ```

2. **Configure Environment**:
   Copy `.env.template` to `.env` and fill in the required tokens, specifically `GITHUB_AI_TOKEN`.
   Sources: [.env.template:1-11]()

3. **Install Development Dependencies**:
   ```bash
   pip install -e .
   ```

4. **Install Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

5. **Verify Installation**:
   ```bash
   auto --help
   pytest
   ```

### Package Extension Points

The project structure supports extension through:
- **Custom Agents**: Adding new logic to `autoagent.agents`.
- **Environment Extensions**: Creating new execution environments in `autoagent.environments`.
- **Tool Integrations**: Adding new tool capabilities in `autoagent.tools`.

For details, see [Extending AutoAgent](#6.3).

Sources: [setup.cfg:67-70]()

---

