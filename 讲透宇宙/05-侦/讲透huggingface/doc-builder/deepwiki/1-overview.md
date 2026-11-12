<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/doc-builder · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [MANIFEST.in](MANIFEST.in)
- [README.md](README.md)
- [setup.py](setup.py)
- [src/doc_builder/__init__.py](src/doc_builder/__init__.py)
- [src/doc_builder/commands/__init__.py](src/doc_builder/commands/__init__.py)
- [src/doc_builder/utils.py](src/doc_builder/utils.py)
- [tests/test_utils.py](tests/test_utils.py)

</details>



## Purpose and Scope

The `doc-builder` system is a comprehensive documentation generation and deployment platform designed specifically for Hugging Face repositories. It transforms various documentation formats (Python docstrings, RST files, Markdown files, and Jupyter notebooks) into a unified MDX format and renders them as interactive web documentation using a SvelteKit-based frontend.

This document covers the overall architecture and high-level system interactions. For detailed information about specific subsystems, see [Core Processing Systems](#2) for document conversion engines, [GitHub Actions Integration](#3) for CI/CD workflows, [Command Line Interface](#4) for CLI usage, and [Frontend System Architecture](#5) for the SvelteKit rendering system.

Sources: [README.md:1-39](), [setup.py:21-37](), [src/doc_builder/__init__.py:20-26]()

## System Architecture Overview

The `doc-builder` follows a layered pipeline architecture that processes multiple input formats through conversion engines, builds unified documentation, and deploys it via automated workflows.

### Core System Flow

```mermaid
graph TB
    subgraph inputs["Input Sources"]
        python_src["Python Source Code<br/>(.py files with docstrings)"]
        rst_docs["RST Documentation<br/>(.rst files)"]
        md_docs["Markdown Documentation<br/>(.md/.mdx files)"]
        jupyter_nb["Jupyter Notebooks<br/>(.ipynb files)"]
    end
    
    subgraph processing["Core Processing Layer"]
        autodoc_engine["autodoc module<br/>(Python API extraction)"]
        rst_converter["convert_rst_to_mdx<br/>(RST transformation)"]
        nb_converter["notebook-to-mdx<br/>(Notebook conversion)"]
        build_doc_engine["build_doc<br/>(Main orchestrator)"]
    end
    
    subgraph output["Output Generation"]
        mdx_files["MDX Files<br/>(Unified format)"]
        svelte_build["SvelteKit Build System<br/>(kit/ folder)"]
        html_output["HTML Documentation<br/>(Static website)"]
    end
    
    subgraph deployment["Deployment Layer"]
        github_actions["GitHub Actions Workflows<br/>(.github/workflows)"]
        hf_hub["Hugging Face Hub<br/>(Documentation hosting)"]
    end
    
    python_src --> autodoc_engine
    rst_docs --> rst_converter
    jupyter_nb --> nb_converter
    md_docs --> build_doc_engine
    
    autodoc_engine --> build_doc_engine
    rst_converter --> build_doc_engine
    nb_converter --> build_doc_engine
    
    build_doc_engine --> mdx_files
    mdx_files --> svelte_build
    svelte_build --> html_output
    
    github_actions --> build_doc_engine
    html_output --> hf_hub
```

Sources: [README.md:40-111](), [src/doc_builder/__init__.py:22-26](), [setup.py:36]()

## Command-Line Interface Structure

The system is controlled through the `doc-builder` CLI, which provides commands for different stages of the documentation pipeline.

### CLI Command Architecture

```mermaid
graph TD
    cli_entry["doc-builder CLI<br/>(doc_builder_cli.py)"]
    
    cli_entry --> preview_cmd["preview command<br/>(Live development server)"]
    cli_entry --> build_cmd["build command<br/>(Documentation generation)"]
    cli_entry --> notebook_cmd["notebook-to-mdx command<br/>(Notebook conversion)"]
    cli_entry --> push_cmd["push command<br/>(Hub deployment)"]
    cli_entry --> style_cmd["style command<br/>(Code formatting)"]
    cli_entry --> convert_cmd["convert command<br/>(Format conversion)"]
    
    build_cmd --> build_doc_func["build_doc function"]
    notebook_cmd --> notebook_converter["Notebook conversion logic"]
    style_cmd --> style_doc_files["style_doc_files function"]
    convert_cmd --> convert_rst_to_mdx["convert_rst_to_mdx function"]
    push_cmd --> hub_integration["Hugging Face Hub API"]
    
    build_doc_func --> autodoc_func["autodoc function"]
    build_doc_func --> conversion_engines["Document converters"]
```

Sources: [setup.py:36](), [README.md:57-111](), [src/doc_builder/__init__.py:22-26]()

## Input Processing and Conversion Pipeline

The system handles multiple input formats through specialized conversion engines that normalize content into MDX format.

| Input Format | Converter Module | Output Format | Key Features |
|--------------|------------------|---------------|--------------|
| Python docstrings | `autodoc` | MDX with API docs | Extracts class/function signatures, handles Google-style docstrings |
| RST files | `convert_rst_to_mdx` | MDX | Converts reStructuredText syntax to Markdown |
| Markdown files | Direct processing | MDX | Minimal transformation, adds MDX components |
| Jupyter notebooks | `notebook-to-mdx` | MDX | Converts cells to markdown, preserves code blocks |

### Document Processing Flow

```mermaid
flowchart LR
    subgraph input_stage["Input Processing"]
        docstrings["Python Docstrings<br/>(Google format)"]
        rst_files["RST Files<br/>(.rst extension)"]
        md_files["Markdown Files<br/>(.md/.mdx extension)"]
        notebooks["Jupyter Notebooks<br/>(.ipynb files)"]
    end
    
    subgraph conversion_stage["Conversion Stage"]
        autodoc_process["autodoc()<br/>(API documentation)"]
        rst_process["convert_rst_to_mdx()<br/>(RST conversion)"]
        md_process["Direct processing<br/>(Minimal changes)"]
        nb_process["notebook-to-mdx<br/>(Cell conversion)"]
    end
    
    subgraph build_stage["Build Orchestration"]
        build_doc_orchestrator["build_doc()<br/>(Main coordinator)"]
        link_resolution["Link Resolution"]
        toc_generation["TOC Generation<br/>(_toctree.yml)"]
    end
    
    subgraph output_stage["Output Generation"]
        unified_mdx["Unified MDX Files"]
        svelte_processing["SvelteKit Processing<br/>(kit/src)"]
        final_html["HTML Documentation"]
    end
    
    docstrings --> autodoc_process
    rst_files --> rst_process
    md_files --> md_process
    notebooks --> nb_process
    
    autodoc_process --> build_doc_orchestrator
    rst_process --> build_doc_orchestrator
    md_process --> build_doc_orchestrator
    nb_process --> build_doc_orchestrator
    
    build_doc_orchestrator --> link_resolution
    build_doc_orchestrator --> toc_generation
    link_resolution --> unified_mdx
    toc_generation --> unified_mdx
    
    unified_mdx --> svelte_processing
    svelte_processing --> final_html
```

Sources: [README.md:456-498](), [src/doc_builder/__init__.py:22-25](), [README.md:97-111]()

## GitHub Actions Integration Points

The system integrates deeply with GitHub Actions to provide automated documentation builds for pull requests and releases.

### CI/CD Workflow Architecture

```mermaid
graph TB
    subgraph triggers["Event Triggers"]
        pr_event["Pull Request<br/>(pull_request event)"]
        push_event["Push to Main<br/>(push event)"]
        release_event["Release Creation<br/>(release event)"]
    end
    
    subgraph workflows["GitHub Actions Workflows"]
        pr_workflow["build_pr_documentation.yml<br/>(PR documentation build)"]
        main_workflow["build_main_documentation.yml<br/>(Main branch build)"]
        upload_workflow["upload_pr_documentation.yml<br/>(Artifact upload)"]
        delete_workflow["delete_doc_comment_trigger.yml<br/>(Comment cleanup)"]
    end
    
    subgraph doc_builder_commands["doc-builder Commands"]
        build_command["doc-builder build<br/>(Documentation generation)"]
        notebook_command["doc-builder notebook-to-mdx<br/>(Notebook conversion)"]
        push_command["doc-builder push<br/>(Hub deployment)"]
    end
    
    subgraph deployment_targets["Deployment Targets"]
        pr_artifacts["PR Artifacts<br/>(GitHub Actions artifacts)"]
        hf_hub_staging["HF Hub Staging<br/>(PR previews)"]
        hf_hub_prod["HF Hub Production<br/>(Main documentation)"]
    end
    
    pr_event --> pr_workflow
    push_event --> main_workflow
    release_event --> main_workflow
    
    pr_workflow --> build_command
    pr_workflow --> notebook_command
    main_workflow --> build_command
    main_workflow --> push_command
    
    build_command --> pr_artifacts
    push_command --> hf_hub_prod
    pr_artifacts --> upload_workflow
    upload_workflow --> hf_hub_staging
```

Sources: [README.md:112-142](), [README.md:178-197]()

## Core Dependencies and Integration

The system relies on several key dependencies that define its capabilities and integration points.

| Component | Type | Purpose | Key Files |
|-----------|------|---------|-----------|
| `black` | Python formatter | Code styling and formatting | Used in `style_doc_files` |
| `GitPython` | Git integration | Repository operations | Branch detection, version control |
| `pyyaml` | Configuration | YAML parsing for `_toctree.yml`, `_versions.yml` | Configuration management |
| `huggingface_hub` | Hub integration | Deployment to Hugging Face Hub | Documentation hosting |
| `nbformat` | Notebook processing | Jupyter notebook parsing | Notebook-to-MDX conversion |
| SvelteKit | Frontend framework | Documentation rendering | Located in `kit/` folder |

### System Utilities and Caching

```mermaid
graph LR
    subgraph utilities["System Utilities"]
        utils_module["utils.py<br/>(Core utilities)"]
        cache_system["DOC_BUILDER_CACHE<br/>(~/.cache/huggingface/doc_builder)"]
        kit_locator["locate_kit_folder()<br/>(SvelteKit discovery)"]
        version_updater["update_versions_file()<br/>(Version management)"]
    end
    
    subgraph external_deps["External Dependencies"]
        git_repo["Git Repository<br/>(Source code)"]
        hf_cache["HF_HOME Cache<br/>(Hugging Face cache)"]
        node_env["Node.js Environment<br/>(SvelteKit build)"]
    end
    
    utils_module --> cache_system
    utils_module --> kit_locator
    utils_module --> version_updater
    
    cache_system --> hf_cache
    kit_locator --> node_env
    version_updater --> git_repo
```

Sources: [setup.py:6](), [src/doc_builder/utils.py:27-31](), [src/doc_builder/utils.py:130-151](), [src/doc_builder/utils.py:55-86]()

## Package Structure and Entry Points

The `hf-doc-builder` package is organized as a modular system with clear separation of concerns between document processing, CLI interface, and utilities.

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `doc_builder.autodoc` | API documentation generation | `autodoc()` |
| `doc_builder.build_doc` | Main build orchestration | `build_doc()` |
| `doc_builder.convert_rst_to_mdx` | RST conversion | `convert_rst_to_mdx()`, `convert_rst_docstring_to_mdx()` |
| `doc_builder.style_doc` | Code formatting | `style_doc_files()` |
| `doc_builder.utils` | System utilities | `update_versions_file()`, `locate_kit_folder()` |
| `doc_builder.commands.doc_builder_cli` | CLI entry point | `main()` |

The package exports its main functions through `__init__.py` and provides a console script entry point `doc-builder` that maps to the CLI module.

Sources: [src/doc_builder/__init__.py:20-26](), [setup.py:32-36]()

---

