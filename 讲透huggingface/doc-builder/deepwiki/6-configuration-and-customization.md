<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/doc-builder · page 6 Configuration and Customization · fetched 2026-10-26 -->

# Configuration and Customization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [MANIFEST.in](MANIFEST.in)
- [kit/src/lib/FrameworkContentBlock.svelte](kit/src/lib/FrameworkContentBlock.svelte)
- [kit/src/lib/stores.ts](kit/src/lib/stores.ts)
- [kit/src/lib/types.ts](kit/src/lib/types.ts)
- [kit/svelte.config.js](kit/svelte.config.js)
- [setup.py](setup.py)
- [src/doc_builder/__init__.py](src/doc_builder/__init__.py)
- [src/doc_builder/commands/__init__.py](src/doc_builder/commands/__init__.py)
- [src/doc_builder/utils.py](src/doc_builder/utils.py)
- [tests/test_utils.py](tests/test_utils.py)

</details>



This document covers how to configure and customize doc-builder for different projects and use cases. It explains the various configuration mechanisms, customization points, and extension options available in the system.

For information about building and deploying documentation, see the [Build Process and Deployment](#6.1) page. For details on extending doc-builder functionality, see the [Development and Extension Guide](#7) page.

## Configuration Architecture

Doc-builder provides multiple configuration layers that work together to customize the documentation generation process. The system follows a hierarchical configuration approach where project-specific settings can override default behaviors.

### Configuration Loading Mechanism

```mermaid
graph TD
    A["doc_folder"] --> B["_config.py"]
    B --> C["read_doc_config()"]
    C --> D["importlib.machinery.SourceFileLoader"]
    D --> E["doc_config module"]
    E --> F["get_doc_config()"]
    
    G["Environment Variables"] --> H["DOC_BUILDER_CACHE"]
    G --> I["HF_HOME"]
    G --> J["XDG_CACHE_HOME"]
    
    K["Git Repository"] --> L["get_default_branch_name()"]
    L --> M["git symbolic-ref"]
    
    F --> N["Global Configuration"]
    H --> O["Cache Configuration"]
    M --> P["Branch Configuration"]
    
    N --> Q["Build Process"]
    O --> Q
    P --> Q
```

The configuration system loads project-specific settings from a `_config.py` file in the documentation source directory. This Python module is executed dynamically to provide flexible configuration options.

**Sources:** [src/doc_builder/utils.py:91-108]()

### Project Configuration File Structure

Doc-builder expects a `_config.py` file in the documentation source directory. This file is loaded as a Python module, allowing for dynamic configuration:

| Configuration Type | Purpose | Code Location |
|-------------------|---------|---------------|
| `default_branch_name` | Git branch configuration | [src/doc_builder/utils.py:36-38]() |
| Custom preprocessors | Content transformation | [kit/svelte.config.js:18-27]() |
| Framework settings | UI framework behavior | [kit/src/lib/types.ts:1-19]() |
| Cache settings | Build cache configuration | [src/doc_builder/utils.py:27-31]() |

**Sources:** [src/doc_builder/utils.py:91-108](), [kit/svelte.config.js:14-64]()

## Frontend Customization System

The SvelteKit frontend provides extensive customization options through preprocessors, stores, and component configuration.

### Preprocessor Configuration Pipeline

```mermaid
graph LR
    A["MDX Content"] --> B["hashInCodePreprocess"]
    B --> C["docstringPreprocess"]
    C --> D["frameworkcontentPreprocess"]
    D --> E["inferenceSnippetPreprocess"]
    E --> F["tokenizersLangPreprocess"]
    F --> G["hfOptionsPreprocess"]
    G --> H["mdsvexPreprocess"]
    H --> I["vitePreprocess"]
    
    I --> J["Processed Content"]
    
    K["svelte.config.js"] --> L["preprocess array"]
    L --> B
    L --> C
    L --> D
    L --> E
    L --> F
    L --> G
    L --> H
    L --> I
```

The preprocessing pipeline transforms content through a series of configurable processors. Each preprocessor handles specific content types and transformations.

**Sources:** [kit/svelte.config.js:18-27]()

### UI Component Configuration

The frontend uses a store-based system for managing UI state and customization:

```mermaid
graph TD
    A["Store System"] --> B["getGroupStore()"]
    A --> C["getFrameworkStore()"]
    A --> D["selectedInferenceLang"]
    A --> E["selectedTokenizersLang"]
    A --> F["selectedHfOptions"]
    
    B --> G["CodeBlockFw.svelte"]
    C --> H["FrameworkContent.svelte"]
    D --> I["InferenceApi.svelte"]
    E --> J["TokenizersLanguageContent.svelte"]
    F --> K["HfOptions.svelte"]
    
    L["AccordianState enum"] --> M["OPEN"]
    L --> N["CLOSED"] 
    L --> O["HASHASHLINK"]
    
    C --> L
    H --> P["Framework switching"]
    H --> Q["Content visibility"]
```

The store system manages component state and user preferences, with persistent storage through `localStorage`.

**Sources:** [kit/src/lib/stores.ts:1-36](), [kit/src/lib/FrameworkContentBlock.svelte:34-42]()

## Environment Configuration

Doc-builder uses environment variables for system-wide configuration:

### Cache and Path Configuration

| Environment Variable | Purpose | Default Value | Code Reference |
|---------------------|---------|---------------|----------------|
| `HF_HOME` | Hugging Face cache home | `~/.cache/huggingface` | [src/doc_builder/utils.py:27-29]() |
| `XDG_CACHE_HOME` | XDG cache directory | `~/.cache` | [src/doc_builder/utils.py:28]() |
| `DOC_BUILDER_CACHE` | Doc-builder cache path | `$HF_HOME/doc_builder` | [src/doc_builder/utils.py:31]() |
| `DOCS_LIBRARY` | Documentation library name | `transformers` | [kit/svelte.config.js:43]() |
| `DOCS_VERSION` | Documentation version | `main` | [kit/svelte.config.js:45]() |
| `DOCS_LANGUAGE` | Documentation language | `en` | [kit/svelte.config.js:47]() |

### SvelteKit Path Configuration

```mermaid
graph LR
    A["process.env"] --> B["DOCS_LIBRARY"]
    A --> C["DOCS_VERSION"]
    A --> D["DOCS_LANGUAGE"]
    
    B --> E["Path Generation"]
    C --> E
    D --> E
    
    E --> F["/docs/library/version/language"]
    
    G["process.argv"] --> H["dev mode check"]
    H --> I["Base Path Decision"]
    
    I -->|dev| J["Empty base path"]
    I -->|build| F
```

The path configuration system dynamically generates URL paths based on environment variables and build mode.

**Sources:** [kit/svelte.config.js:39-49]()

## Package Configuration

### Installation and Dependencies

The package configuration defines installation options and dependencies:

```mermaid
graph TD
    A["setup.py"] --> B["install_requires"]
    A --> C["extras_require"]
    
    B --> D["Core Dependencies"]
    D --> E["black"]
    D --> F["GitPython"]
    D --> G["tqdm"]
    D --> H["pyyaml"]
    D --> I["packaging"]
    D --> J["nbformat"]
    D --> K["huggingface_hub"]
    D --> L["pillow"]
    
    C --> M["Optional Extras"]
    M --> N["transformers"]
    M --> O["testing"]
    M --> P["quality"]
    M --> Q["all"]
    M --> R["dev"]
    M --> S["release"]
    
    T["Console Scripts"] --> U["doc-builder CLI"]
    U --> V["doc_builder.commands.doc_builder_cli:main"]
```

**Sources:** [setup.py:6-37]()

## Version Management Configuration

Doc-builder includes a sophisticated version management system for documentation versions:

### Version File Management

```mermaid
graph TD
    A["update_versions_file()"] --> B["_versions.yml"]
    B --> C["YAML Structure"]
    
    C --> D["Main Version"]
    C --> E["Semantic Versions"]
    
    F["get_default_branch_name()"] --> G["Git Command"]
    G --> H["Default Branch Detection"]
    
    I["Version Comparison"] --> J["package_version.parse()"]
    J --> K["Semantic Version Ordering"]
    
    L["Version Insertion Logic"] --> M["Compare with existing"]
    M --> N["Insert in correct position"]
    M --> O["Skip if duplicate"]
```

The version management system maintains a `_versions.yml` file with proper semantic version ordering.

**Sources:** [src/doc_builder/utils.py:55-86](), [tests/test_utils.py:26-68]()

## Customization Extension Points

### Repository Detection and Caching

Doc-builder provides mechanisms for detecting and caching repository information:

```mermaid
graph TD
    A["is_doc_builder_repo()"] --> B["setup.py check"]
    B --> C["First line validation"]
    
    D["locate_kit_folder()"] --> E["Local search"]
    E --> F["Repository detection"]
    F --> G["Cache fallback"]
    
    H["get_cached_repo()"] --> I["Clone if needed"]
    I --> J["Update if exists"]
    
    K["Repository Locations"] --> L["Module parent"]
    K --> M["Current directory"]
    K --> N["Cached clone"]
```

**Sources:** [src/doc_builder/utils.py:118-183]()

### File Route Transformation

The system includes utilities for transforming file routes between different formats:

```mermaid
graph LR
    A["MDX Files"] --> B["sveltify_file_route()"]
    B --> C["Svelte Routes"]
    
    D["guide.mdx"] --> E["guide/+page.svelte"]
    F["path/to/doc.mdx"] --> G["path/to/doc/+page.svelte"]
    
    H["Route Transformation"] --> I["File Extension Check"]
    I --> J["Path Manipulation"]
    J --> K["Svelte Route Format"]
```

This transformation is essential for integrating generated MDX content with the SvelteKit routing system.

**Sources:** [src/doc_builder/utils.py:185-196](), [tests/test_utils.py:70-84]()

## Framework and UI Type Configuration

Doc-builder defines configurable types for different frameworks and UI components:

| Type | Values | Usage |
|------|--------|--------|
| `Framework` | `pytorch`, `tensorflow`, `jax` | Framework-specific content | 
| `Group` | `group1`, `group2` | Code block grouping |
| `TokenizersLanguage` | `python`, `rust`, `node` | Language-specific tokenizer docs |
| `InferenceSnippetLang` | `python`, `js`, `curl` | API example languages |
| `CourseFramework` | `pt`, `tf` | Course content frameworks |

These types are used throughout the UI components to provide consistent framework switching and content organization.

**Sources:** [kit/src/lib/types.ts:1-19](), [kit/src/lib/stores.ts:1-36]()

---

