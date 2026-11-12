<!-- source: DeepWiki mcp.deepwiki.com · repo adap/flower · page 8 Documentation System · fetched 2026-10-21 -->

# Documentation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.devcontainer/Dockerfile](.devcontainer/Dockerfile)
- [.github/actions/bootstrap/action.yml](.github/actions/bootstrap/action.yml)
- [.github/workflows/baselines.yml](.github/workflows/baselines.yml)
- [.github/workflows/deprecated_baselines.yml](.github/workflows/deprecated_baselines.yml)
- [baselines/docs/source/conf.py](baselines/docs/source/conf.py)
- [baselines/flwr_baselines/dev/bootstrap.sh](baselines/flwr_baselines/dev/bootstrap.sh)
- [baselines/flwr_baselines/dev/setup-defaults.sh](baselines/flwr_baselines/dev/setup-defaults.sh)
- [baselines/flwr_baselines/dev/venv-create.sh](baselines/flwr_baselines/dev/venv-create.sh)
- [baselines/flwr_baselines/dev/venv-delete.sh](baselines/flwr_baselines/dev/venv-delete.sh)
- [baselines/flwr_baselines/dev/venv-reset.sh](baselines/flwr_baselines/dev/venv-reset.sh)
- [baselines/flwr_baselines/flwr_baselines/publications/adaptive_federated_optimization/main.py](baselines/flwr_baselines/flwr_baselines/publications/adaptive_federated_optimization/main.py)
- [dev/bootstrap.sh](dev/bootstrap.sh)
- [dev/update-html-themes.py](dev/update-html-themes.py)
- [examples/docs/source/conf.py](examples/docs/source/conf.py)
- [framework/docs/locales/fr/LC_MESSAGES/framework-docs.po](framework/docs/locales/fr/LC_MESSAGES/framework-docs.po)
- [framework/docs/locales/ko/LC_MESSAGES/framework-docs.po](framework/docs/locales/ko/LC_MESSAGES/framework-docs.po)
- [framework/docs/locales/pt_BR/LC_MESSAGES/framework-docs.po](framework/docs/locales/pt_BR/LC_MESSAGES/framework-docs.po)
- [framework/docs/locales/zh_Hans/LC_MESSAGES/framework-docs.po](framework/docs/locales/zh_Hans/LC_MESSAGES/framework-docs.po)
- [framework/docs/source/conf.py](framework/docs/source/conf.py)

</details>



The Flower documentation system provides comprehensive, multilingual documentation for the federated learning framework. It consists of a Sphinx-based build system with integrated localization, extensive examples, and automated maintenance workflows.

For information about dataset management, see [FederatedDataset](#4.1). For deployment documentation, see [Docker Deployment](#5.1).

## Documentation Architecture

The documentation system is built on Sphinx with reStructuredText source files and supports multiple output formats including HTML and PDF. The system is designed to handle both framework documentation and community-contributed content.

```mermaid
graph TB
    subgraph "Source Content"
        RST["RST Source Files<br/>framework/docs/source/"]
        CONF["conf.py<br/>Configuration"]
        CHANGELOG["changelog.rst<br/>Release Notes"]
    end
    
    subgraph "Build System"
        SPHINX["Sphinx Builder"]
        BABEL["Babel Extractor"]
        POT["POT Template<br/>framework-docs.pot"]
    end
    
    subgraph "Localization"
        PO_FR["French PO<br/>locales/fr/LC_MESSAGES/"]
        PO_ZH["Chinese PO<br/>locales/zh_Hans/LC_MESSAGES/"]
        PO_KO["Korean PO<br/>locales/ko/LC_MESSAGES/"]
        PO_PT["Portuguese PO<br/>locales/pt_BR/LC_MESSAGES/"]
        WEBLATE["Weblate Platform<br/>Translation Management"]
    end
    
    subgraph "Output"
        HTML["HTML Documentation"]
        PDF["PDF Documentation"]
        TRANSLATIONS["Translated Docs"]
    end
    
    RST --> SPHINX
    CONF --> SPHINX
    CHANGELOG --> SPHINX
    
    SPHINX --> BABEL
    BABEL --> POT
    
    POT --> PO_FR
    POT --> PO_ZH  
    POT --> PO_KO
    POT --> PO_PT
    
    PO_FR --> WEBLATE
    PO_ZH --> WEBLATE
    PO_KO --> WEBLATE
    PO_PT --> WEBLATE
    
    SPHINX --> HTML
    SPHINX --> PDF
    PO_FR --> TRANSLATIONS
    PO_ZH --> TRANSLATIONS
    PO_KO --> TRANSLATIONS
    PO_PT --> TRANSLATIONS
```

**Sphinx Build System Architecture**

Sources: [framework/docs/locales/fr/LC_MESSAGES/framework-docs.po:1-50](), [CHANGELOG.md:1-6]()

## Core Documentation Components

The documentation system consists of several key components that work together to provide comprehensive coverage of the Flower framework.

| Component | Location | Purpose |
|-----------|----------|---------|
| Source Files | `framework/docs/source/` | ReStructuredText documentation source |
| Configuration | `framework/docs/source/conf.py` | Sphinx build configuration |
| Locales | `framework/docs/locales/*/LC_MESSAGES/` | Translation files |
| Templates | `framework/docs/source/_templates/` | Custom documentation templates |
| Static Assets | `framework/docs/source/_static/` | Images, CSS, JavaScript |

```mermaid
graph TB
    subgraph "Documentation Sources"
        BUILD_RST["build.rst<br/>Build Guides"]
        CONTRIBUTE_RST["contribute.rst<br/>Contributor Docs"]
        DEPLOY_RST["deploy.rst<br/>Deployment Guides"]
        SIMULATE_RST["simulate.rst<br/>Simulation Docs"]
        INDEX_RST["index.rst<br/>Main Index"]
        REFERENCE_RST["reference.rst<br/>API Reference"]
    end
    
    subgraph "Generated Content"
        API_DOCS["API Documentation<br/>Auto-generated"]
        CLI_DOCS["CLI Reference<br/>Auto-generated"]
        TUTORIALS["Tutorial Notebooks<br/>Jupyter Integration"]
    end
    
    subgraph "Support Files"
        CONF_PY["conf.py<br/>Sphinx Config"]
        REQUIREMENTS["requirements.txt<br/>Doc Dependencies"]
        MAKEFILE["Makefile<br/>Build Automation"]
    end
    
    BUILD_RST --> API_DOCS
    CONTRIBUTE_RST --> CLI_DOCS
    INDEX_RST --> TUTORIALS
    
    CONF_PY --> API_DOCS
    CONF_PY --> CLI_DOCS
    REQUIREMENTS --> CONF_PY
    MAKEFILE --> CONF_PY
```

**Documentation Source Structure**

Sources: [framework/docs/locales/fr/LC_MESSAGES/framework-docs.po:18-45](), [framework/docs/locales/zh_Hans/LC_MESSAGES/framework-docs.po:22-105]()

## Translation Infrastructure

The documentation system implements GNU gettext-based internationalization with community translation support through Weblate. Translation strings are extracted from source files and managed through `.po` files for each supported language.

### Supported Languages

| Language | Code | PO File Location | Translator Count |
|----------|------|------------------|------------------|
| French | `fr` | `locales/fr/LC_MESSAGES/framework-docs.po` | Community |
| Chinese (Simplified) | `zh_Hans` | `locales/zh_Hans/LC_MESSAGES/framework-docs.po` | Community |
| Korean | `ko` | `locales/ko/LC_MESSAGES/framework-docs.po` | Community |
| Portuguese (Brazil) | `pt_BR` | `locales/pt_BR/LC_MESSAGES/framework-docs.po` | Community |

### Translation Workflow

```mermaid
graph LR
    subgraph "Source Extraction"
        RST_SOURCE["RST Source Files"]
        BABEL_EXTRACT["babel extract"]
        POT_FILE["framework-docs.pot<br/>Translation Template"]
    end
    
    subgraph "Translation Management"
        WEBLATE_PLATFORM["Weblate Platform<br/>hosted.weblate.org"]
        TRANSLATORS["Community<br/>Translators"]
    end
    
    subgraph "Language Files"
        FR_PO["French PO File"]
        ZH_PO["Chinese PO File"] 
        KO_PO["Korean PO File"]
        PT_PO["Portuguese PO File"]
    end
    
    subgraph "Build Output"
        GETTEXT_COMPILE["msgfmt compile"]
        LOCALIZED_DOCS["Localized<br/>Documentation"]
    end
    
    RST_SOURCE --> BABEL_EXTRACT
    BABEL_EXTRACT --> POT_FILE
    POT_FILE --> WEBLATE_PLATFORM
    
    WEBLATE_PLATFORM --> TRANSLATORS
    TRANSLATORS --> FR_PO
    TRANSLATORS --> ZH_PO
    TRANSLATORS --> KO_PO
    TRANSLATORS --> PT_PO
    
    FR_PO --> GETTEXT_COMPILE
    ZH_PO --> GETTEXT_COMPILE
    KO_PO --> GETTEXT_COMPILE
    PT_PO --> GETTEXT_COMPILE
    
    GETTEXT_COMPILE --> LOCALIZED_DOCS
```

**Translation Workflow Process**

Sources: [framework/docs/locales/fr/LC_MESSAGES/framework-docs.po:613-720](), [framework/docs/locales/zh_Hans/LC_MESSAGES/framework-docs.po:610-736](), [framework/docs/locales/ko/LC_MESSAGES/framework-docs.po:589-736]()

## Examples and Baselines Integration

The documentation system provides comprehensive coverage of examples and research baselines, making them discoverable and maintainable as part of the main documentation.

### Example Categories

```mermaid
graph TB
    subgraph "Quickstart Examples"
        QS_PYTORCH["quickstart-pytorch<br/>PyTorch Integration"]
        QS_TENSORFLOW["quickstart-tensorflow<br/>TensorFlow Integration"]
        QS_HUGGINGFACE["quickstart-huggingface<br/>Transformers Integration"]
        QS_PYTORCH_LIGHTNING["quickstart-pytorch-lightning<br/>Lightning Integration"]
        QS_PANDAS["quickstart-pandas<br/>Analytics Integration"]
        QS_SCIKIT["sklearn-logreg-mnist<br/>Scikit-learn Integration"]
    end
    
    subgraph "Advanced Examples"  
        ADV_PYTORCH["advanced-pytorch<br/>Advanced PyTorch Features"]
        ADV_TENSORFLOW["advanced-tensorflow<br/>Advanced TensorFlow Features"]
        VERTICAL_FL["vertical-fl<br/>Vertical Federated Learning"]
        EMBEDDED["embedded-devices<br/>Raspberry Pi & Jetson"]
        PRIVACY["opacus, tensorflow-privacy<br/>Privacy-Preserving FL"]
    end
    
    subgraph "Research Baselines"
        FEDAVG["fedavg<br/>Federated Averaging"]
        FEDPROX["fedprox<br/>FedProx Algorithm"]
        MOON["moon<br/>MOON Algorithm"]
        TAMUNA["tamuna<br/>TAMUNA Algorithm"]
        DASHA["dasha<br/>DASHA Algorithm"]
    end
    
    QS_PYTORCH --> ADV_PYTORCH
    QS_TENSORFLOW --> ADV_TENSORFLOW
    QS_HUGGINGFACE --> PRIVACY
    ADV_PYTORCH --> FEDAVG
    ADV_TENSORFLOW --> FEDPROX
```

**Examples and Baselines Organization**

Sources: [README.md:92-122](), [README.md:123-160]()

## Automated Maintenance

The documentation system includes automated maintenance workflows to ensure consistency and accuracy across releases.

### Version Management

The system automatically updates documentation versions during release cycles through automated scripts that maintain consistency across different file types.

```mermaid
graph TB
    subgraph "Version Update Process"
        UPDATE_SCRIPT["dev/update_python.py<br/>Version Update Script"]
        CONF_PY["framework/docs/source/conf.py<br/>Documentation Config"]
        RST_FILES["*.rst Files<br/>ReStructuredText Sources"]
        PO_FILES["*.po Files<br/>Translation Files"]
    end
    
    subgraph "Validation"
        COPYRIGHT_CHECK["dev/test-copyright.sh<br/>Copyright Validation"]
        BUILD_TEST["Sphinx Build Test"]
        LINK_CHECK["Link Validation"]
    end
    
    UPDATE_SCRIPT --> CONF_PY
    UPDATE_SCRIPT --> RST_FILES
    UPDATE_SCRIPT --> PO_FILES
    
    CONF_PY --> COPYRIGHT_CHECK
    RST_FILES --> BUILD_TEST
    PO_FILES --> LINK_CHECK
```

**Automated Maintenance Workflow**

### Copyright Management

The documentation system enforces consistent copyright headers across all documentation configuration files using automated validation.

| Check Type | Script | Target Files | Pattern |
|------------|--------|--------------|---------|
| Copyright Header | `dev/test-copyright.sh` | `*/docs/source/conf.py` | `f"{datetime.date.today().year} Flower Labs GmbH"` |
| Version Consistency | `dev/update_python.py` | `**/*.rst`, `**/*.po` | Python version strings |
| Link Validation | CI/CD Pipeline | All documentation | External link health |

Sources: [dev/test-copyright.sh:1-16](), [dev/update_python.py:145-192](), [CHANGELOG.md:3-6]()

## Build and Deployment Pipeline

The documentation system is integrated with the overall Flower CI/CD pipeline, providing automated builds, validation, and deployment of documentation across multiple languages and formats.

```mermaid
graph TB
    subgraph "Source Control"
        GIT_REPO["Git Repository<br/>Documentation Sources"]
        PR_VALIDATION["Pull Request<br/>Documentation Changes"]
    end
    
    subgraph "Build Pipeline"
        SPHINX_BUILD["Sphinx Build<br/>Multi-format Output"]
        TRANSLATION_BUILD["Translation Build<br/>msgfmt Compilation"]
        VALIDATION["Link & Format<br/>Validation"]
    end
    
    subgraph "Deployment Targets"
        DOCS_SITE["flower.ai/docs<br/>Live Documentation"]
        PDF_BUILDS["PDF Documentation<br/>Download Versions"]
        TRANSLATION_SITES["Localized Sites<br/>Multi-language"]
    end
    
    GIT_REPO --> PR_VALIDATION
    PR_VALIDATION --> SPHINX_BUILD
    SPHINX_BUILD --> TRANSLATION_BUILD
    TRANSLATION_BUILD --> VALIDATION
    
    VALIDATION --> DOCS_SITE
    VALIDATION --> PDF_BUILDS  
    VALIDATION --> TRANSLATION_SITES
```

**Documentation Build and Deployment Pipeline**

Sources: [framework/docs/locales/fr/LC_MESSAGES/framework-docs.po:4-16](), [framework/docs/locales/zh_Hans/LC_MESSAGES/framework-docs.po:8-20]()

---

