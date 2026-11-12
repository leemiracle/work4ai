<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-apt-repo · page 3 Installation and Usage · fetched 2026-10-26 -->

# Installation and Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [README.rst](README.rst)
- [setup.py](setup.py)

</details>



This page provides a comprehensive overview of installing and using `termux-apt-repo`, covering the available installation methods, basic usage patterns, and repository publishing workflows. It serves as the entry point for understanding how to integrate this tool into your development and distribution processes.

For detailed installation procedures, see [Installation Methods](#3.1). For step-by-step usage examples, see [Basic Usage and Examples](#3.2). For advanced configuration options and features, see [Advanced Features and Options](#3.3).

## Installation Overview

The `termux-apt-repo` tool can be installed through multiple methods depending on your environment and requirements. The installation process varies between Termux environments and standard Linux distributions.

### Installation Methods Diagram

```mermaid
flowchart TB
    subgraph "Installation Sources"
        A["`GitHub Repository
        termux/termux-apt-repo`"]
        B["`PyPI Package
        termux-apt-repo`"]
        C["`Termux Package
        pkg install termux-apt-repo`"]
    end
    
    subgraph "Installation Methods"
        D["`Local Installation
        make install`"]
        E["`PyPI Installation
        pip3 install termux-apt-repo`"]
        F["`Termux Package Manager
        pkg install termux-apt-repo`"]
    end
    
    subgraph "Target Environments"
        G["`Termux Environment
        Android/Linux`"]
        H["`Standard Linux
        Distributions`"]
        I["`Development Environment
        Local builds`"]
    end
    
    A --> D
    B --> E
    C --> F
    
    D --> I
    E --> H
    F --> G
    E --> G
    
    D -.-> G
    E -.-> I
```

**Sources:** [README.rst:14-16](), [README.rst:35-36](), [setup.py:8-17](), [Makefile:1-2]()

### Package Distribution Details

The tool is distributed as a Python package with the following characteristics:

| Property | Value | Source |
|----------|-------|---------|
| Package Name | `termux-apt-repo` | [setup.py:9]() |
| Version | `0.5` | [setup.py:10]() |
| Script Name | `termux-apt-repo` | [setup.py:17]() |
| License | Apache License 2.0 | [setup.py:11]() |
| Target Python | Python 3 | [setup.py:21]() |

**Sources:** [setup.py:8-23]()

## Basic Usage Workflow

The core functionality revolves around processing `.deb` files and generating APT repository structures. The tool follows a straightforward input-processing-output workflow.

### Usage Command Structure

```mermaid
flowchart LR
    subgraph "Command Structure"
        A["`termux-apt-repo`"]
        B["`Optional Arguments
        --use-hard-links
        --sign`"]
        C["`Input Directory
        .deb files location`"]
        D["`Output Directory
        repository tree`"]
        E["`Distribution Name
        dist (optional)`"]
        F["`Component Name
        comp (optional)`"]
    end
    
    subgraph "Processing Pipeline"
        G["`Scan Input Directory
        for .deb files`"]
        H["`Extract Package Metadata
        control files`"]
        I["`Generate Repository Structure
        dists/dist/comp/binary-arch/`"]
        J["`Create Metadata Files
        Packages, Contents, Release`"]
    end
    
    subgraph "Output Structure"
        K["`APT Repository Tree
        standard Debian format`"]
        L["`Package Files
        copied or hard-linked`"]
        M["`Repository Metadata
        compressed and signed`"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    G --> H
    H --> I
    I --> J
    
    J --> K
    I --> L
    J --> M
```

**Sources:** [README.rst:19-34]()

### Command-Line Interface

The basic command syntax follows this pattern:

```bash
termux-apt-repo [options] input output [dist] [comp]
```

| Argument | Type | Description | Default |
|----------|------|-------------|---------|
| `input` | Required | Folder containing `.deb` files | - |
| `output` | Required | Output folder for repository tree | - |
| `dist` | Optional | Distribution folder name | - |
| `comp` | Optional | Component folder name | - |
| `--use-hard-links` | Flag | Use hard links instead of copying | Copy files |
| `--sign` | Flag | Sign repository with GPG key | Unsigned |

**Sources:** [README.rst:21-34]()

## Publishing and Distribution

After generating the repository structure, the output directory must be made accessible to APT clients. The tool supports multiple publishing methods to accommodate different deployment scenarios.

### Publishing Methods

```mermaid
flowchart TB
    subgraph "Generated Repository"
        A["`APT Repository Directory
        output from termux-apt-repo`"]
    end
    
    subgraph "Publishing Methods"
        B["`Direct Web Server
        run on server directly`"]
        C["`rsync Transfer
        rsync --delete -r`"]
        D["`Archive Distribution
        zip or tar files`"]
        E["`GitHub Pages
        static site hosting`"]
    end
    
    subgraph "Access Points"
        F["`Public URL
        $REPO_URL`"]
    end
    
    subgraph "Client Configuration"
        G["`sources.list.d
        APT configuration`"]
        H["`Repository Access
        deb [trusted=yes] $REPO_URL`"]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    
    B --> F
    C --> F
    D --> F
    E --> F
    
    F --> G
    G --> H
```

**Sources:** [README.rst:42-55](), [README.rst:57-76]()

### Repository Access Configuration

Users access the published repository by configuring their APT sources:

1. **Configuration File Location:** `$PREFIX/etc/apt/sources.list.d/`
2. **Repository Entry Format:** `deb [trusted=yes] $REPO_URL $dist $comp`
3. **Trust Settings:** `[trusted=yes]` required for unsigned repositories

**Sources:** [README.rst:60-76]()

## Core Script Integration

The `termux-apt-repo` script serves as the central processing engine, integrating with system utilities and following standard APT repository conventions.

### System Dependencies and Integration

```mermaid
flowchart TB
    subgraph "Core Script"
        A["`termux-apt-repo
        Python script`"]
    end
    
    subgraph "System Utilities"
        B["`ar utility
        .deb extraction`"]
        C["`tar utility
        archive processing`"]
        D["`xz compression
        metadata compression`"]
        E["`gpg signing
        repository signing`"]
    end
    
    subgraph "Input Processing"
        F["`Debian Package Files
        .deb format`"]
        G["`Control Information
        package metadata`"]
        H["`Binary Content
        package files`"]
    end
    
    subgraph "Output Generation"
        I["`Repository Structure
        dists/dist/comp/binary-arch/`"]
        J["`Packages Files
        package indexes`"]
        K["`Contents Files
        file listings`"]
        L["`Release Files
        repository metadata`"]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    
    F --> A
    A --> G
    A --> H
    
    A --> I
    A --> J
    A --> K
    A --> L
```

**Sources:** [README.rst:4-9](), [README.rst:19-34]()

This overview establishes the foundation for understanding `termux-apt-repo` installation and usage. The subsequent sections provide detailed implementations of each aspect covered here, with specific examples and advanced configuration options.

---

