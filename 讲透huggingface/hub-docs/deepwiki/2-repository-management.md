<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/hub-docs · page 2 Repository Management · fetched 2026-10-26 -->

# Repository Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [datasetcard.md](datasetcard.md)
- [docs/hub/collections.md](docs/hub/collections.md)
- [docs/hub/datasets-cards.md](docs/hub/datasets-cards.md)
- [docs/hub/datasets-gated.md](docs/hub/datasets-gated.md)
- [docs/hub/model-cards.md](docs/hub/model-cards.md)
- [docs/hub/models-gated.md](docs/hub/models-gated.md)
- [docs/hub/paper-pages.md](docs/hub/paper-pages.md)
- [docs/hub/repositories-licenses.md](docs/hub/repositories-licenses.md)
- [modelcard.md](modelcard.md)

</details>



This document provides a high-level overview of the core repository management features that apply to all three primary repository types on the Hugging Face Hub: Models, Datasets, and Spaces. It covers metadata management, licensing, community features, and repository organization.

For detailed technical specifications and implementation guides for each type, see:
- [Models](#2.1) — Uploading, model cards, inference widgets, and gated access.
- [Datasets](#2.2) — Dataset cards, Dataset Viewer (Data Studio), and multimodal data configuration.
- [Spaces](#2.3) — SDKs (Gradio, Docker), GPU hardware, and deployment options.

## Repository Types and Structure

The Hugging Face Hub hosts three primary repository types, each utilizing a `README.md` file (the "card") as the central point for documentation and machine-readable metadata.

```mermaid
graph TB
    subgraph "Repository Types"
        [ModelRepo] -- "README.md" --> [ModelCard]
        [DatasetRepo] -- "README.md" --> [DatasetCard]
        [SpaceRepo] -- "README.md" --> [SpaceCard]
    end
    
    subgraph "Common Management Components"
        [YAML_Metadata] -- "Stored in Card Header" --> [Hub_Features]
        [Gating_System] -- "Access Control" --> [User_Requests]
        [Collections] -- "Grouping" --> [Repo_Sets]
    end

    [ModelCard] --> [YAML_Metadata]
    [DatasetCard] --> [YAML_Metadata]
    [SpaceCard] --> [YAML_Metadata]
    
    [Hub_Features] --> [Filtering_Search]
    [Hub_Features] --> [Library_Detection]
    [Hub_Features] --> [Widget_Config]
```
Sources: [docs/hub/model-cards.md:6-7](), [docs/hub/datasets-cards.md:5-7]()

## Metadata and Card Management

Repository cards serve dual purposes: providing human-readable documentation and storing structured metadata. Metadata is defined in a YAML block at the top of the `README.md` file.

### Metadata Features
Metadata enables the Hub to index repositories for search and trigger specific UI elements:
* **Discovery**: Fields like `language`, `tags`, and `task_categories` enable filtering at `huggingface.co/models` or `/datasets`.
* **Lineage**: The `base_model` field tracks fine-tunes, adapters, and merges.
* **Library Integration**: The `library_name` field (e.g., `transformers`, `flair`, `keras`) determines which code snippets and inference logic are displayed.

### Editing Metadata
Users can manage metadata through three primary interfaces:
1. **Metadata UI**: A visual editor on the repository page for common fields.
2. **Direct YAML Editing**: Manual modification of the `README.md` header.
3. **Programmatic Access**: Using the `huggingface_hub` Python library to update metadata.

Sources: [docs/hub/model-cards.md:23-43](), [docs/hub/model-cards.md:81-98](), [docs/hub/datasets-cards.md:9-26]()

## Licensing System

The Hub provides a standardized licensing system to define permissions for code, models, and data. Licenses are specified in the card metadata using unique identifiers.

| License Family | Example Identifiers |
| :--- | :--- |
| **Open Source** | `apache-2.0`, `mit`, `bsd-3-clause`, `gpl-3.0` |
| **Creative Commons** | `cc-by-4.0`, `cc-by-nc-sa-4.0`, `cc0-1.0` |
| **OpenRAIL** | `openrail`, `bigscience-bloom-rail-1.0`, `creativeml-openrail-m` |
| **Custom/Other** | `other` (requires `license_name` and `license_link`) |

Sources: [docs/hub/repositories-licenses.md:11-63](), [modelcard.md:6-8]()

## Access Control and Gating

For sensitive or research-stage assets, the Hub supports **Gated Repositories**. This requires users to share contact information and potentially agree to specific terms before accessing files.

* **Approval Modes**:
    * **Automatic Approval**: Access is granted immediately upon the user sharing their info.
    * **Manual Approval**: Repository authors must review and `accept` or `reject` requests via the UI or API.
* **API Management**: Access requests can be managed programmatically using endpoints like `/api/models/{repo_id}/user-access-request/pending`.

Sources: [docs/hub/models-gated.md:1-29](), [docs/hub/models-gated.md:55-65](), [docs/hub/datasets-gated.md:1-33]()

## Organizational Tools

### Collections
Collections allow users and organizations to group related repositories (Models, Datasets, Spaces, and Papers) on a single page.
* **Use Cases**: Showcasing a complete project, bookmarking resources, or gating a group of repositories simultaneously (Enterprise feature).
* **Notes & Images**: Items in a collection can have custom text notes and images attached for context.

Sources: [docs/hub/collections.md:1-16](), [docs/hub/collections.md:58-62](), [docs/hub/collections.md:85-93]()

### Paper Pages
The Hub extracts arXiv IDs from repository cards to link artifacts (models/datasets) to their original research papers. Users can "claim authorship" of papers to verify their profile and group their contributions.

Sources: [docs/hub/paper-pages.md:1-22](), [docs/hub/datasets-cards.md:48-54]()

---

