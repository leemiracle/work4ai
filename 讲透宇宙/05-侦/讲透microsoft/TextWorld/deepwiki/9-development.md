<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TextWorld · page 9 Development · fetched 2026-10-26 -->

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.azure/pipelines/linux-template.yml](.azure/pipelines/linux-template.yml)
- [.azure/pipelines/macos-template.yml](.azure/pipelines/macos-template.yml)
- [.azure/pipelines/prerelease.yml](.azure/pipelines/prerelease.yml)
- [.azure/pipelines/release.yml](.azure/pipelines/release.yml)
- [.azure/pipelines/tests.yml](.azure/pipelines/tests.yml)
- [MANIFEST.in](MANIFEST.in)
- [pyproject.toml](pyproject.toml)
- [setup.sh](setup.sh)
- [textworld/__init__.py](textworld/__init__.py)
- [tools/prep-release.sh](tools/prep-release.sh)

</details>



This section provides comprehensive information for developers contributing to TextWorld, covering development environment setup, testing infrastructure, continuous integration pipelines, and package distribution processes. For information about using TextWorld's core APIs and game generation, see [Core Concepts](#3) and [Game Generation](#4).

## Development Environment Setup

TextWorld requires a specific development environment setup that includes external dependencies like Inform7 compiler and Glulx interpreters. The primary setup is managed through the `setup.sh` script which handles cross-platform installation of these dependencies.

### Development Environment Architecture

```mermaid
graph TB
    subgraph "Development Setup Process"
        setupsh["setup.sh"]
        deps["System Dependencies"]
        inform7["Inform7 Installation"]
        glulx["Glulx Build"]
        pyenv["Python Environment"]
    end
    
    subgraph "External Dependencies"
        inform7cli["Inform7 CLI (6M62)"]
        cheapglk["cheapglk"]
        gitglulx["Git-Glulx"]
        graphviz["graphviz"]
    end
    
    subgraph "Python Dependencies"
        reqtxt["requirements.txt"]
        reqfull["requirements-full.txt"]
        pyproject["pyproject.toml"]
    end
    
    setupsh --> deps
    deps --> inform7
    deps --> glulx
    setupsh --> inform7cli
    setupsh --> cheapglk 
    setupsh --> gitglulx
    
    pyenv --> reqtxt
    pyenv --> reqfull
    pyenv --> pyproject
    
    inform7 --> inform7cli
    glulx --> cheapglk
    glulx --> gitglulx
    deps --> graphviz
```

The `setup.sh` script performs platform-specific installation of Inform7 and Glulx components. On Linux, it downloads and extracts the Inform7 CLI distribution [setup.sh:21-31](). On macOS, it additionally mounts the Inform7 DMG to extract platform-specific binaries [setup.sh:50-64](). The script also builds the modified Glulx interpreters from source [setup.sh:67-77]().

**Sources:** [setup.sh:1-78](), [pyproject.toml:1-38]()

## Testing Infrastructure

TextWorld uses a comprehensive testing infrastructure that supports multiple Python versions and platforms through Azure Pipelines. The testing system is designed to validate both source installations and PyPI package installations.

### Test Execution Pipeline

```mermaid
graph TB
    subgraph "Test Configuration"
        teststage["Test Stage"]
        linuxtemplate["linux-template.yml"]
        macostemplate["macos-template.yml"]
        testmatrix["Test Matrix"]
    end
    
    subgraph "Python Versions"
        py39["Python 3.9"]
        py310["Python 3.10"]
        py311["Python 3.11"]
        py312["Python 3.12"]
    end
    
    subgraph "Platforms"
        ubuntu["ubuntu-latest"]
        macos["macOS-latest"]
    end
    
    subgraph "Installation Methods"
        fromsource["From Source"]
        frompypi["From PyPI"]
    end
    
    subgraph "Test Execution"
        pytest["pytest"]
        coverage["Code Coverage"]
        codecov["Codecov Upload"]
    end
    
    teststage --> linuxtemplate
    teststage --> macostemplate
    
    linuxtemplate --> py39
    linuxtemplate --> py310
    linuxtemplate --> py311
    linuxtemplate --> py312
    
    macostemplate --> py39
    macostemplate --> py312
    
    ubuntu --> fromsource
    macos --> fromsource
    
    fromsource --> pytest
    frompypi --> pytest
    pytest --> coverage
    coverage --> codecov
```

The testing infrastructure runs on multiple combinations of operating systems and Python versions. Linux tests run on all supported Python versions (3.9-3.12) [.azure/pipelines/tests.yml:14-26](), while macOS tests run on Python 3.9 and 3.12 [.azure/pipelines/tests.yml:27-34](). Each test job installs system dependencies, sets up the TextWorld environment, and runs the full test suite with coverage reporting.

**Sources:** [.azure/pipelines/tests.yml:1-35](), [.azure/pipelines/linux-template.yml:1-47](), [.azure/pipelines/macos-template.yml:1-40]()

## CI/CD Pipeline Architecture

The CI/CD system uses Azure Pipelines with separate workflows for testing, prerelease, and production release. The system supports both source-based development and package distribution validation.

### Pipeline Flow and Components

```mermaid
graph TB
    subgraph "Source Control"
        maintrigger["main branch trigger"]
        prvalidation["PR validation"]
    end
    
    subgraph "Testing Pipeline"
        teststage["Test Stage"]
        installsource["Install from Source"]
        installpypi["Install from PyPI"]
        runtests["Run pytest"]
        publishcov["Publish Coverage"]
    end
    
    subgraph "Prerelease Pipeline"
        prereleasestage["Prerelease Stage"]
        buildpackage["Build Package"]
        uploadpypi["Upload to PyPI"]
        testprerelease["Test Prerelease"]
    end
    
    subgraph "Release Pipeline"
        releasestage["Release Stage"]
        finalpackage["Final Package"]
        publishpypi["Publish to PyPI"]
    end
    
    subgraph "External Services"
        codecovservice["Codecov"]
        pypirepo["PyPI Repository"]
        azureagents["Azure Agents"]
    end
    
    maintrigger --> teststage
    prvalidation --> teststage
    
    teststage --> installsource
    teststage --> installpypi
    installsource --> runtests
    installpypi --> runtests
    runtests --> publishcov
    publishcov --> codecovservice
    
    teststage --> prereleasestage
    prereleasestage --> buildpackage
    buildpackage --> uploadpypi
    uploadpypi --> pypirepo
    uploadpypi --> testprerelease
    
    prereleasestage --> releasestage
    releasestage --> finalpackage
    finalpackage --> publishpypi
    publishpypi --> pypirepo
    
    teststage --> azureagents
    prereleasestage --> azureagents
    releasestage --> azureagents
```

The CI/CD system distinguishes between development testing and package validation. The `installFromSource` variable controls whether tests install TextWorld from source code or from PyPI packages [.azure/pipelines/linux-template.yml:20-28](). This allows validation of both development workflows and published packages.

**Sources:** [.azure/pipelines/tests.yml:6-8](), [.azure/pipelines/prerelease.yml:32-35](), [.azure/pipelines/release.yml:1-29]()

## Packaging and Distribution

TextWorld uses modern Python packaging standards with `pyproject.toml` as the primary configuration and `MANIFEST.in` for including non-Python assets. The packaging system handles complex binary dependencies and platform-specific components.

### Package Structure and Dependencies

```mermaid
graph TB
    subgraph "Package Configuration"
        pyprojecttoml["pyproject.toml"]
        manifestin["MANIFEST.in"]
        setupcfg["setup.cfg"]
        requirementstxt["requirements.txt"]
    end
    
    subgraph "Build System"
        setuptools["setuptools >= 61.0"]
        cffi["cffi >= 1.0.0"]
        buildbackend["setuptools.build_meta"]
    end
    
    subgraph "Package Contents"
        pythoncode["Python Code"]
        binaryassets["Binary Assets"]
        datafiles["Data Files"]
        thirdparty["Third-party Components"]
    end
    
    subgraph "Binary Assets"
        inform7binaries["Inform7 Binaries"]
        glulxlibs["Glulx Libraries"]
        grammars["Grammar Files"]
        templates["Templates"]
    end
    
    subgraph "Distribution"
        sdist["Source Distribution"]
        wheel["Binary Wheel"]
        pypiupload["PyPI Upload"]
    end
    
    pyprojecttoml --> setuptools
    pyprojecttoml --> cffi
    pyprojecttoml --> buildbackend
    
    manifestin --> binaryassets
    manifestin --> datafiles
    manifestin --> thirdparty
    
    binaryassets --> inform7binaries
    binaryassets --> glulxlibs
    datafiles --> grammars
    datafiles --> templates
    
    setuptools --> sdist
    setuptools --> wheel
    sdist --> pypiupload
    wheel --> pypiupload
```

The package includes extensive binary assets and data files through `MANIFEST.in`. Key inclusions are Inform7 compiler binaries [MANIFEST.in:28-30](), Glulx interpreter libraries [MANIFEST.in:25](), grammar files [MANIFEST.in:13-14](), and text generation templates [MANIFEST.in:16](). The build system uses `setuptools` with `cffi` for handling binary components [pyproject.toml:2-6]().

**Sources:** [pyproject.toml:1-38](), [MANIFEST.in:1-36](), [tools/prep-release.sh:1-16]()

## Release Process

The release process involves multiple stages: preparation, testing, prerelease validation, and final release. Each stage includes specific validation steps and automated deployment.

### Release Workflow and Automation

```mermaid
graph TB
    subgraph "Preparation Phase"
        preprelease["prep-release.sh"]
        generateparsers["Generate Parsers"]
        tatsu["TatSu Parser Generation"]
    end
    
    subgraph "Testing Phase"  
        unittest["Unit Tests"]
        integrationtest["Integration Tests"]
        coveragecheck["Coverage Check"]
    end
    
    subgraph "Prerelease Phase"
        prereleasevar["TEXTWORLD_PRERELEASE=true"]
        packagesh["package.sh"]
        uploadprerelease["Upload Prerelease"]
        testprerelease["Test Prerelease Install"]
    end
    
    subgraph "Release Phase"
        finalpackage["Final Package Build"]
        twineauth["Twine Authentication"]
        pypiupload["PyPI Upload"]
        postvalidation["Post-release Validation"]
    end
    
    subgraph "Parser Generation"
        logicebnf["logic.ebnf"]
        textgenebnf["textgen.ebnf"]
        pddlebnf["pddl/*.ebnf"]
        parserpy["parser.py"]
    end
    
    preprelease --> generateparsers
    generateparsers --> tatsu
    tatsu --> logicebnf
    tatsu --> textgenebnf
    tatsu --> pddlebnf
    logicebnf --> parserpy
    textgenebnf --> parserpy
    pddlebnf --> parserpy
    
    generateparsers --> unittest
    unittest --> integrationtest
    integrationtest --> coveragecheck
    
    coveragecheck --> prereleasevar
    prereleasevar --> packagesh
    packagesh --> uploadprerelease
    uploadprerelease --> testprerelease
    
    testprerelease --> finalpackage
    finalpackage --> twineauth
    twineauth --> pypiupload
    pypiupload --> postvalidation
```

The release preparation script `prep-release.sh` generates parser files from grammar definitions using TatSu [tools/prep-release.sh:10-15](). This includes parsers for the core logic system, text generation, and PDDL environment support. The prerelease process uses the `TEXTWORLD_PRERELEASE` environment variable to create development versions [.azure/pipelines/prerelease.yml:20](), while final releases follow the standard packaging workflow.

**Sources:** [tools/prep-release.sh:1-16](), [.azure/pipelines/prerelease.yml:17-29](), [.azure/pipelines/release.yml:16-28]()

---

