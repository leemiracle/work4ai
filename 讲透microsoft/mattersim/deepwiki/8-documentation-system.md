<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/mattersim · page 8 Documentation System · fetched 2026-10-26 -->

# Documentation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/gh-pages.yaml](.github/workflows/gh-pages.yaml)
- [.nojekyll](.nojekyll)
- [docs/Makefile](docs/Makefile)
- [docs/README.md](docs/README.md)
- [docs/_static/mattersim.png](docs/_static/mattersim.png)
- [docs/conf.py](docs/conf.py)
- [docs/make.bat](docs/make.bat)
- [docs/user_guide/installation.rst](docs/user_guide/installation.rst)

</details>



## Purpose and Scope

This documentation system manages the build process, automated deployment, and local development workflows for MatterSim's technical documentation. It uses Sphinx as the documentation generator with GitHub Pages for hosting and GitHub Actions for continuous deployment. For information about contributing to the documentation content itself, see [Contributing Guidelines](#7.4).

## Architecture Overview

The documentation system follows a modern static site generation approach with automated deployment:

```mermaid
graph TB
    subgraph "Documentation Sources"
        RST["RST Files<br/>docs/user_guide/*.rst"]
        MD["Markdown Files<br/>*.md"]
        NB["Jupyter Notebooks<br/>*.ipynb"]
        STATIC["Static Assets<br/>docs/_static/*"]
    end
    
    subgraph "Build System"
        CONF["docs/conf.py<br/>Sphinx Configuration"]
        MAKE["docs/Makefile<br/>Build Commands"]
        BAT["docs/make.bat<br/>Windows Build"]
    end
    
    subgraph "GitHub Actions Pipeline"
        TRIGGER["Push/PR Trigger<br/>main branch"]
        BUILD["sphinx-build<br/>Generate HTML"]
        DEPLOY["peaceiris/actions-gh-pages<br/>Deploy to GitHub Pages"]
    end
    
    subgraph "Output"
        HTML["docs/_build/html/<br/>Generated Site"]
        PAGES["GitHub Pages<br/>Hosted Documentation"]
    end
    
    RST --> BUILD
    MD --> BUILD
    NB --> BUILD
    STATIC --> BUILD
    
    CONF --> BUILD
    MAKE --> BUILD
    
    TRIGGER --> BUILD
    BUILD --> HTML
    BUILD --> DEPLOY
    DEPLOY --> PAGES
    
    CONF -.-> MAKE
    CONF -.-> BAT
```

Sources: [docs/conf.py](), [docs/Makefile](), [docs/make.bat](), [.github/workflows/gh-pages.yaml]()

## Sphinx Configuration

The documentation system is built on Sphinx with a comprehensive set of extensions and configurations:

### Core Configuration

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| **Extensions** | `sphinx.ext.autodoc` | Auto-generate API documentation |
| | `sphinx.ext.napoleon` | Google/NumPy docstring support |
| | `sphinx_autodoc_typehints` | Type hint documentation |
| | `sphinx.ext.mathjax` | Mathematical notation |
| | `sphinx_copybutton` | Copy code button |
| | `nbsphinx` | Jupyter notebook support |
| **Theme** | `sphinx_book_theme` | Modern book-style theme |
| **Formats** | `.rst`, `.md` | Multiple markup format support |

The main configuration is defined in `docs/conf.py`:

```mermaid
graph LR
    subgraph "Sphinx Extensions"
        AUTODOC["sphinx.ext.autodoc<br/>API Documentation"]
        NAPOLEON["sphinx.ext.napoleon<br/>Docstring Processing"]
        HINTS["sphinx_autodoc_typehints<br/>Type Documentation"]
        MATHJAX["sphinx.ext.mathjax<br/>Math Rendering"]
        COPY["sphinx_copybutton<br/>Code Copying"]
        NB["nbsphinx<br/>Notebook Support"]
    end
    
    subgraph "Source Processing"
        RST_PROC["ReStructuredText<br/>Parser"]
        MD_PROC["CommonMark<br/>Markdown Parser"]
        NB_PROC["Jupyter Notebook<br/>Processor"]
    end
    
    subgraph "Theme System"
        BOOK["sphinx_book_theme<br/>Modern UI"]
        STATIC_FILES["_static/<br/>CSS, Images, JS"]
        LOGO["mattersim-with-name.png<br/>Site Logo"]
    end
    
    AUTODOC --> RST_PROC
    NAPOLEON --> RST_PROC
    HINTS --> RST_PROC
    
    MD_PROC --> BOOK
    RST_PROC --> BOOK
    NB_PROC --> BOOK
    
    STATIC_FILES --> BOOK
    LOGO --> BOOK
```

Sources: [docs/conf.py:16-24](), [docs/conf.py:33-38](), [docs/conf.py:46]()

## GitHub Pages Deployment

The automated deployment pipeline uses GitHub Actions to build and publish documentation:

### Deployment Workflow

```mermaid
graph TB
    subgraph "Triggers"
        PUSH["Push to main<br/>branch"]
        PR["Pull Request<br/>to main"]
    end
    
    subgraph "Build Environment Setup"
        CHECKOUT["actions/checkout@v3<br/>Get Repository"]
        PYTHON["actions/setup-python@v4<br/>Python 3.9"]
        PANDOC["apt-get install<br/>pandoc"]
    end
    
    subgraph "Dependency Installation"
        SPHINX_DEPS["sphinx sphinx-autodoc-typehints<br/>sphinx_book_theme sphinx-copybutton"]
        NB_DEPS["nbsphinx recommonmark<br/>Pygments pandoc"]
    end
    
    subgraph "Build Process"
        CD_DOCS["cd docs/"]
        MAKE_HTML["make html"]
        BUILD_OUTPUT["docs/_build/html/"]
    end
    
    subgraph "Deployment"
        CONDITION["Check: main branch<br/>& microsoft/mattersim"]
        DEPLOY_ACTION["peaceiris/actions-gh-pages@v3<br/>GitHub Token Auth"]
        PUBLISH["Publish to<br/>gh-pages branch"]
    end
    
    PUSH --> CHECKOUT
    PR --> CHECKOUT
    
    CHECKOUT --> PYTHON
    PYTHON --> PANDOC
    PANDOC --> SPHINX_DEPS
    SPHINX_DEPS --> NB_DEPS
    
    NB_DEPS --> CD_DOCS
    CD_DOCS --> MAKE_HTML
    MAKE_HTML --> BUILD_OUTPUT
    
    BUILD_OUTPUT --> CONDITION
    CONDITION --> DEPLOY_ACTION
    DEPLOY_ACTION --> PUBLISH
```

Sources: [.github/workflows/gh-pages.yaml:3-11](), [.github/workflows/gh-pages.yaml:28-38](), [.github/workflows/gh-pages.yaml:39-42](), [.github/workflows/gh-pages.yaml:44-49]()

### Deployment Configuration

The deployment workflow includes several key features:

| Feature | Configuration | Purpose |
|---------|---------------|---------|
| **Triggers** | `push` to main, `pull_request` to main | Automatic builds on changes |
| **Permissions** | `contents: write` | Allow deployment to gh-pages |
| **Conditional Deploy** | Repository and branch checks | Prevent unauthorized deployments |
| **Token Auth** | `${{ secrets.GITHUB_TOKEN }}` | Secure deployment authorization |

Sources: [.github/workflows/gh-pages.yaml:12-13](), [.github/workflows/gh-pages.yaml:45]()

## Local Development Setup

### Prerequisites and Installation

Developers can build documentation locally using the provided tooling:

```mermaid
graph TB
    subgraph "Prerequisites"
        SPHINX_CORE["sphinx sphinx-autodoc-typehints<br/>sphinx_book_theme sphinx-copybutton"]
        MARKDOWN["recommonmark<br/>Markdown Support"]
        NOTEBOOK["nbsphinx nbconvert<br/>Jupyter Notebook Support"]
        PANDOC_PKG["pandoc<br/>Document Converter"]
    end
    
    subgraph "Build Commands"
        MAKEFILE["make html<br/>Unix/Linux/macOS"]
        BATCH["make.bat html<br/>Windows"]
        DIRECT["sphinx-build -b html docs docs/_build<br/>Direct Command"]
    end
    
    subgraph "Local Server"
        HTTP_SERVER["python3 -m http.server<br/>--directory docs/_build 8000"]
        BROWSER["http://localhost:8000<br/>View Documentation"]
    end
    
    SPHINX_CORE --> MAKEFILE
    MARKDOWN --> MAKEFILE
    NOTEBOOK --> MAKEFILE
    PANDOC_PKG --> MAKEFILE
    
    SPHINX_CORE --> BATCH
    MARKDOWN --> BATCH
    NOTEBOOK --> BATCH
    PANDOC_PKG --> BATCH
    
    SPHINX_CORE --> DIRECT
    
    MAKEFILE --> HTTP_SERVER
    BATCH --> HTTP_SERVER
    DIRECT --> HTTP_SERVER
    
    HTTP_SERVER --> BROWSER
```

Sources: [docs/README.md:4-18](), [docs/README.md:20-30]()

### Build System Structure

The build system provides multiple interfaces for different environments:

| File | Platform | Purpose |
|------|----------|---------|
| `docs/Makefile` | Unix/Linux/macOS | Standard make-based builds |
| `docs/make.bat` | Windows | Batch file for Windows builds |
| `docs/README.md` | All | Developer setup instructions |

The build process uses Sphinx's standard directory structure:
- **Source Directory**: `.` (docs root)
- **Build Directory**: `_build`
- **Output Directory**: `_build/html`

Sources: [docs/Makefile:7-9](), [docs/make.bat:10-11](), [docs/README.md:22-24]()

## Documentation Assets and Structure

### Static Assets Management

The documentation system manages static assets through a dedicated directory structure:

```mermaid
graph LR
    subgraph "Asset Types"
        LOGO["mattersim-with-name.png<br/>Site Logo"]
        IMAGES["*.png, *.jpg<br/>Documentation Images"]
        CSS["*.css<br/>Custom Styling"]
        JS["*.js<br/>Custom Scripts"]
    end
    
    subgraph "Asset Processing"
        STATIC_PATH["html_static_path = ['_static']"]
        LOGO_CONFIG["html_logo = '_static/mattersim-with-name.png'"]
        COPY_PROCESS["Sphinx Static File Copying"]
    end
    
    subgraph "Output Integration"
        BUILD_STATIC["_build/html/_static/"]
        HTML_REFS["HTML Template References"]
        THEME_INTEGRATION["sphinx_book_theme Integration"]
    end
    
    LOGO --> STATIC_PATH
    IMAGES --> STATIC_PATH
    CSS --> STATIC_PATH
    JS --> STATIC_PATH
    
    STATIC_PATH --> LOGO_CONFIG
    STATIC_PATH --> COPY_PROCESS
    
    LOGO_CONFIG --> BUILD_STATIC
    COPY_PROCESS --> BUILD_STATIC
    
    BUILD_STATIC --> HTML_REFS
    BUILD_STATIC --> THEME_INTEGRATION
```

Sources: [docs/conf.py:44](), [docs/conf.py:46](), [docs/_static/mattersim.png]()

### GitHub Pages Configuration

The system includes GitHub Pages-specific configuration:

| File | Purpose |
|------|---------|
| `.nojekyll` | Disables Jekyll processing for GitHub Pages |
| `gh-pages` branch | Deployment target for generated HTML |

The `.nojekyll` file ensures that Sphinx-generated files with underscores (like `_static/`) are properly served by GitHub Pages.

Sources: [.nojekyll]()

## Documentation Source Formats

The system supports multiple documentation source formats through Sphinx extensions:

### Supported Formats

```mermaid
graph TB
    subgraph "Input Formats"
        RST["ReStructuredText<br/>.rst files"]
        MD["Markdown<br/>.md files"]
        IPYNB["Jupyter Notebooks<br/>.ipynb files"]
        PY["Python Docstrings<br/>.py files"]
    end
    
    subgraph "Processing Extensions"
        RST_PARSER["Native Sphinx<br/>ReStructuredText Parser"]
        MD_PARSER["recommonmark<br/>CommonMark Parser"]
        NB_PROCESSOR["nbsphinx<br/>Notebook Processor"]
        AUTODOC["sphinx.ext.autodoc<br/>Python Docstring Extractor"]
    end
    
    subgraph "Output Processing"
        HTML_GEN["HTML Generation"]
        MATHJAX["MathJax Rendering"]
        CODE_HIGHLIGHT["Pygments Syntax Highlighting"]
        COPY_BUTTONS["sphinx-copybutton Integration"]
    end
    
    RST --> RST_PARSER
    MD --> MD_PARSER
    IPYNB --> NB_PROCESSOR
    PY --> AUTODOC
    
    RST_PARSER --> HTML_GEN
    MD_PARSER --> HTML_GEN
    NB_PROCESSOR --> HTML_GEN
    AUTODOC --> HTML_GEN
    
    HTML_GEN --> MATHJAX
    HTML_GEN --> CODE_HIGHLIGHT
    HTML_GEN --> COPY_BUTTONS
```

Sources: [docs/conf.py:16-24](), [docs/conf.py:26-29](), [docs/conf.py:48-50]()

### Configuration Details

The format support is configured through the `source_suffix` dictionary and extension list:

- **ReStructuredText**: Native Sphinx support with full feature set
- **Markdown**: CommonMark parsing via `recommonmark` extension
- **Jupyter Notebooks**: Execution control via `nbsphinx_execute = "never"`
- **Python Code**: Automatic API documentation via `sphinx.ext.autodoc`

The system prevents notebook execution during build (`nbsphinx_execute = "never"`) while allowing error tolerance (`nbsphinx_allow_errors = True`) for robust builds.

Sources: [docs/conf.py:26-29](), [docs/conf.py:49-50]()

---

