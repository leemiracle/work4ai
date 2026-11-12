<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/genalog · page 5 Project Information · fetched 2026-10-26 -->

# Project Information

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [CHANGELOG.md](CHANGELOG.md)
- [VERSION.txt](VERSION.txt)
- [docs/genalog_docs/_config.yml](docs/genalog_docs/_config.yml)
- [docs/genalog_docs/docstring/genalog.ocr.rst](docs/genalog_docs/docstring/genalog.ocr.rst)
- [docs/genalog_docs/e2e_dataset_pipeline.md](docs/genalog_docs/e2e_dataset_pipeline.md)

</details>



This document covers the configuration, assets, versioning, and metadata that define the genalog project infrastructure. This includes the Jupyter Book documentation system setup, version management processes, repository organization, and project branding elements.

For information about the core genalog functionality and system architecture, see [System Architecture](#1.2). For development workflow and testing infrastructure, see [Development](#3).

## Documentation System Configuration

The genalog project uses Jupyter Book to generate its documentation website, configured through a centralized YAML configuration file that defines the book structure, execution settings, and publishing parameters.

### Jupyter Book Configuration Structure

```mermaid
graph TB
    subgraph "Documentation Configuration"
        A["_config.yml"]
        B["Book Metadata"]
        C["Execute Settings"]
        D["Repository Integration"]
        E["HTML Settings"]
        F["Sphinx Extensions"]
    end
    
    subgraph "Book Metadata"
        G["title: ''"]
        H["author: 'Jianjie Liu and Amit Gupte'"]
        I["logo: 'static/genalog_full_logo.svg'"]
        J["description: 'Guide for end-to-end synthetic analog document generation'"]
    end
    
    subgraph "Execution Configuration"
        K["execute_notebooks: off"]
        L["notebook_interface: 'notebook'"]
    end
    
    subgraph "Repository Links"
        M["url: 'https://github.com/microsoft/genalog'"]
        N["path_to_book: '/docs/genalog_docs'"]
        O["branch: 'main'"]
    end
    
    subgraph "HTML Output"
        P["favicon: 'static/genalog_favicon.svg'"]
        Q["baseurl: 'https://microsoft.github.io/genalog/'"]
        R["use_repository_button: true"]
        S["use_issues_button: true"]
    end
    
    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    
    B --> G
    B --> H
    B --> I
    B --> J
    
    C --> K
    C --> L
    
    D --> M
    D --> N
    D --> O
    
    E --> P
    E --> Q
    E --> R
    E --> S
```

The documentation system is configured with notebook execution disabled (`execute_notebooks: off`) to ensure consistent builds and prevent execution dependencies during documentation generation. The configuration enables direct GitHub integration through repository buttons and issue tracking links.

**Sources:** [docs/genalog_docs/_config.yml:1-44]()

### Sphinx API Documentation

```mermaid
graph LR
    subgraph "Sphinx Extensions"
        A["sphinx_inline_tabs"]
        B["sphinx.ext.autodoc"]
        C["sphinx.ext.napoleon"]
        D["sphinx.ext.viewcode"]
    end
    
    subgraph "Napoleon Configuration"
        E["napoleon_google_docstring: True"]
        F["autodoc_member_order: groupwise"]
        G["autoclass_content: both"]
    end
    
    subgraph "Generated Documentation"
        H["genalog.ocr.rst"]
        I["API Reference Pages"]
        J["Docstring Rendering"]
    end
    
    A --> I
    B --> H
    C --> J
    D --> I
    
    E --> J
    F --> H
    G --> H
```

The system uses Google-style docstrings (`napoleon_google_docstring: True`) and groups class members logically (`autodoc_member_order: groupwise`). The `autoclass_content: both` setting includes both the class docstring and `__init__` method documentation.

**Sources:** [docs/genalog_docs/_config.yml:34-43](), [docs/genalog_docs/docstring/genalog.ocr.rst:1-35]()

## Version Management and Release Process

The project follows semantic versioning with a centralized version file and structured changelog management.

### Version Control Structure

| Component | Location | Format | Current Value |
|-----------|----------|--------|---------------|
| Version Number | `VERSION.txt` | `x.y.z` | `0.1.0` |
| Release Notes | `CHANGELOG.md` | Keep a Changelog | v0.1.0 |
| Versioning Scheme | - | Semantic Versioning | `MAJOR.MINOR.PATCH` |

```mermaid
graph TD
    subgraph "Version Management"
        A["VERSION.txt"]
        B["CHANGELOG.md"]
        C["Release Process"]
    end
    
    subgraph "Semantic Versioning Rules"
        D["MAJOR: Breaking changes"]
        E["MINOR: New features"]
        F["PATCH: Bug fixes"]
    end
    
    subgraph "Changelog Categories"
        G["Added: New features"]
        H["Changed: Existing functionality"]
        I["Deprecated: Soon-to-be removed"]
        J["Removed: Now removed features"]
        K["Fixed: Bug fixes"]
        L["Security: Vulnerabilities"]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    C --> F
    
    B --> G
    B --> H
    B --> I
    B --> J
    B --> K
    B --> L
```

The changelog follows the "Keep a Changelog" format with categorized change types. The initial release (v0.1.0) includes HTML document templates, image degradation effects, text alignment algorithms, and end-to-end NER-OCR labeling capabilities.

**Sources:** [VERSION.txt:1](), [CHANGELOG.md:1-23]()

## Repository Structure and Metadata

The repository uses standard Python project conventions with comprehensive gitignore rules for development artifacts, credentials, and build outputs.

### Repository Organization

```mermaid
graph TB
    subgraph "Repository Root"
        A[".gitignore"]
        B["VERSION.txt"]
        C["CHANGELOG.md"]
    end
    
    subgraph "Documentation Structure"
        D["docs/genalog_docs/"]
        E["_config.yml"]
        F["static/"]
        G["docstring/"]
    end
    
    subgraph "Ignored Artifacts"
        H["Test Output: test_out/"]
        I["Credentials: .secret*, .cred*"]
        J["Environments: .env*, venv/"]
        K["Build Artifacts: dist/, build/"]
        L["Coverage Reports: htmlcov/, .coverage"]
    end
    
    A --> H
    A --> I
    A --> J
    A --> K
    A --> L
    
    D --> E
    D --> F
    D --> G
```

The gitignore configuration protects sensitive information including secrets (`.secret*`, `.cred*`), environment configurations (`.env*`), and development artifacts like test outputs and coverage reports.

**Sources:** [.gitignore:1-155]()

### Asset Management

```mermaid
graph LR
    subgraph "Brand Assets"
        A["static/genalog_full_logo.svg"]
        B["static/genalog_favicon.svg"]
    end
    
    subgraph "Documentation Assets"
        C["static/labeled_synthetic_pipeline.png"]
        D["Example Images"]
    end
    
    subgraph "Usage Locations"
        E["_config.yml logo"]
        F["_config.yml favicon"]
        G["Pipeline Documentation"]
    end
    
    A --> E
    B --> F
    C --> G
    
    subgraph "Asset Configuration"
        H["logo: static/genalog_full_logo.svg"]
        I["favicon: static/genalog_favicon.svg"]
    end
    
    E --> H
    F --> I
```

Project branding assets are centralized in the `static/` directory and referenced through the Jupyter Book configuration. The logo appears in the documentation header while the favicon provides browser tab identification.

**Sources:** [docs/genalog_docs/_config.yml:3,26](), [docs/genalog_docs/e2e_dataset_pipeline.md:3-4]()

## Publication and Distribution Configuration

The project is configured for publication through GitHub Pages with integration to academic research and PyPI distribution.

### Publication Channels

| Channel | URL | Purpose |
|---------|-----|---------|
| GitHub Pages | `https://microsoft.github.io/genalog/` | Primary documentation |
| ArXiv Paper | `https://arxiv.org/abs/2108.02899` | Academic publication |
| GitHub Repository | `https://github.com/microsoft/genalog` | Source code |
| PyPI Package | `pip install genalog` | Distribution |

```mermaid
graph TB
    subgraph "Publication Configuration"
        A["baseurl: 'https://microsoft.github.io/genalog/'"]
        B["extra_footer: ArXiv paper link"]
        C["use_repository_button: true"]
        D["use_issues_button: true"]
    end
    
    subgraph "Academic Integration"
        E["Document Intelligence Workshop"]
        F["KDD 2021"]
        G["ArXiv: 2108.02899"]
    end
    
    subgraph "GitHub Integration"
        H["Repository Links"]
        I["Issue Tracking"]
        J["Source Code Access"]
    end
    
    A --> H
    B --> E
    B --> F
    B --> G
    C --> H
    D --> I
    
    E --> G
    F --> G
```

The documentation footer prominently links to the academic paper from the Document Intelligence Workshop at KDD 2021, establishing the research context for the synthetic document generation methodology.

**Sources:** [docs/genalog_docs/_config.yml:28-32]()

## API Documentation Generation

The project uses automated API documentation generation through Sphinx with reStructuredText files that define module organization and deprecation notices.

### Module Documentation Structure

```mermaid
graph TD
    subgraph "API Documentation Files"
        A["genalog.ocr.rst"]
        B["Module Sections"]
        C["Deprecation Notices"]
    end
    
    subgraph "OCR Module Documentation"
        D["genalog.ocr.common"]
        E["genalog.ocr.grok"]
        F["genalog.ocr.metrics"]
        G["genalog.ocr.rest_client"]
        H["genalog.ocr.blob_client"]
    end
    
    subgraph "Deprecation Information"
        I["Azure Computer Vision SDK"]
        J["Official Microsoft SDK"]
        K["Migration Recommendation"]
    end
    
    A --> B
    A --> C
    B --> D
    B --> E
    B --> F
    B --> G
    B --> H
    
    C --> I
    C --> J
    C --> K
```

The OCR module documentation includes explicit deprecation warnings directing users toward the official Azure Computer Vision SDK, indicating the project's evolution toward standard Microsoft tooling.

**Sources:** [docs/genalog_docs/docstring/genalog.ocr.rst:1-35]()

---

