<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-cookbook · page 3 Content Management and Publishing System · fetched 2026-10-26 -->

# Content Management and Publishing System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/authors_schema.json](.github/authors_schema.json)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [.github/registry_schema.json](.github/registry_schema.json)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [authors.yaml](authors.yaml)
- [examples/agents_sdk/building_reliable_agents_memory_compaction.ipynb](examples/agents_sdk/building_reliable_agents_memory_compaction.ipynb)
- [examples/agents_sdk/context_personalization.ipynb](examples/agents_sdk/context_personalization.ipynb)
- [examples/agents_sdk/session_memory.ipynb](examples/agents_sdk/session_memory.ipynb)
- [examples/completions_usage_api.ipynb](examples/completions_usage_api.ipynb)
- [examples/evaluation/moving-from-openai-evals-to-promptfoo.md](examples/evaluation/moving-from-openai-evals-to-promptfoo.md)
- [examples/gpt-5/prompt_personalities.ipynb](examples/gpt-5/prompt_personalities.ipynb)
- [examples/gpt4-1_prompting_guide.ipynb](examples/gpt4-1_prompting_guide.ipynb)
- [examples/skills_in_api.ipynb](examples/skills_in_api.ipynb)
- [images/memory_comparison.jpg](images/memory_comparison.jpg)
- [images/openai-cookbook-white.png](images/openai-cookbook-white.png)
- [images/openai-cookbook.png](images/openai-cookbook.png)
- [images/promptfoo-custom-example-view.png](images/promptfoo-custom-example-view.png)
- [images/summarizingSession.jpg](images/summarizingSession.jpg)
- [images/trimingSession.jpg](images/trimingSession.jpg)
- [registry.yaml](registry.yaml)

</details>



## Purpose and Scope
This section details the content management and publishing system that powers the OpenAI Cookbook repository (`openai/openai-cookbook`) and its published website interface at `cookbook.openai.com` [README.md:1-10](). The system orchestrates content ingestion, metadata organization via `registry.yaml` [registry.yaml:1-5](), contributor attribution via `authors.yaml` [authors.yaml:1-5](), schema validation through `.github/registry_schema.json` and `.github/authors_schema.json` [.github/registry_schema.json:1-48](), and contribution guidelines enforced by pull request templates [.github/pull_request_template.md:1-24]() and validation scripts [CONTRIBUTING.md:26-30]().

Sources: [README.md:1-10](), [registry.yaml:1-5](), [authors.yaml:1-5](), [.github/registry_schema.json:1-48](), [.github/pull_request_template.md:1-24](), [CONTRIBUTING.md:26-30]()

## System Overview
The content management system acts as the core bridge between raw repository assets (`examples/`, `articles/`) and the generated static site output (`cookbook.openai.com`) [README.md:1-10](), [CONTRIBUTING.md:15-20](). It relies on a centralized manifest file (`registry.yaml`) [registry.yaml:3-5]() and an author lookup file (`authors.yaml`) [authors.yaml:3-5](), both validated against strict JSON schemas [.github/registry_schema.json:1-48]().

Title: Content Management Architecture and Data Flow
```mermaid
graph TB
    subgraph NaturalLanguageSpace["Natural Language & Documentation Space"]
        ContentAuthors[""Contributors & Authors"""]
        MarkdownArticles[""Long-form Articles (articles/*.md)"""]
        JupyterNotebooks[""Example Notebooks (examples/*.ipynb)"""]
    end

    subgraph CodeEntitySpace["Code Entity Space & Manifests"]
        RegistryYaml[""registry.yaml Manifest [registry.yaml:3-5]"""]
        AuthorsYaml[""authors.yaml Lookup [authors.yaml:3-5]"""]
        RegistrySchema[""JsonSchemaValidator: .github/registry_schema.json [.github/registry_schema.json:1-48]"""]
        AuthorsSchema[""JsonSchemaValidator: .github/authors_schema.json"""]
    end

    subgraph PublishingPipeline["Publishing Pipeline & Output"]
        SiteGenerator[""WebsiteGenerator: cookbook.openai.com [README.md:1-10]"""]
        NavigationBuilder[""NavigationBuilder: Tag & Category Indices"""]
        SearchIndex[""SearchIndexBuilder: Content Search"""]
    end

    MarkdownArticles --> RegistryYaml
    JupyterNotebooks --> RegistryYaml
    ContentAuthors --> AuthorsYaml

    RegistryYaml --> RegistrySchema
    AuthorsYaml --> AuthorsSchema

    RegistrySchema --> SiteGenerator
    AuthorsSchema --> SiteGenerator
    SiteGenerator --> NavigationBuilder
    SiteGenerator --> SearchIndex
```
Sources: [README.md:1-10](), [registry.yaml:3-5](), [authors.yaml:3-5](), [.github/registry_schema.json:1-48](), [CONTRIBUTING.md:15-20]()

## Content Registry Architecture
The `registry.yaml` file functions as the authoritative content manifest. Each item in the YAML array defines specific metadata fields required to render content items on the website [registry.yaml:1-184]().

Title: Registry Entry Resolution and Schema Mapping
```mermaid
graph LR
    subgraph NaturalLanguageSpace["Content Definition (Natural Language)"]
        EntryTitle[""title: 'Build a prior review assistant' [registry.yaml:20]"""]
        EntryDesc[""description: 'Build and deploy...' [registry.yaml:23]"""]
    end

    subgraph CodeEntitySpace["Registry & Mapping Logic"]
        RegistryEntry[""registry.yaml Entry [registry.yaml:20-35]"""]
        PathField[""path: examples/partners/AWS/... [registry.yaml:21]"""]
        SlugField[""slug: prior-authorization-review-agentcore [registry.yaml:22]"""]
        AuthorsList[""authors: [sks-oai] [registry.yaml:25-26]"""]
        TagsList[""tags: [partners, agents-sdk] [registry.yaml:27-35]"""]
        AuthorsLookup[""authors.yaml Record [authors.yaml:11-14]"""]
    end

    subgraph OutputSpace["Website Target"]
        RenderedPage[""cookbook.openai.com/prior-authorization-review-agentcore [README.md:1-10], [registry.yaml:22]"""]
    end

    EntryTitle --> RegistryEntry
    EntryDesc --> RegistryEntry
    RegistryEntry --> PathField
    RegistryEntry --> SlugField
    RegistryEntry --> AuthorsList
    RegistryEntry --> TagsList
    AuthorsList --> AuthorsLookup
    PathField --> RenderedPage
    AuthorsLookup --> RenderedPage
```
Sources: [README.md:1-10](), [registry.yaml:20-35](), [authors.yaml:11-14]()

## Content Types and Organization
The repository organizes educational content into structured directories under `examples/` and `articles/` [CONTRIBUTING.md:15-20](). Every published piece requires a corresponding entry in `registry.yaml` [CONTRIBUTING.md:18]().

| Content Type | Path Pattern | Example Tags | Purpose |
|--------------|--------------|--------------|---------|
| API Examples | `examples/*.ipynb` | `audio`, `transcription`, `gpt-5` | Practical API usage demonstrations |
| Technical Articles | `articles/*.md` | `responses`, `cost-management` | Conceptual guidance and best practices |
| Partner Content | `examples/partners/` | `partners`, `bedrock`, `promptfoo` | Third-party ecosystem integrations |
| Agents SDK | `examples/agents_sdk/` | `agents-sdk`, `memory`, `personalization` | Framework-specific agentic patterns |
| Codex & Tools | `examples/codex/` | `codex`, `automation`, `planning` | Developer tool and IDE integrations |

Sources: [registry.yaml:7-19](), [registry.yaml:20-35](), [registry.yaml:37-48](), [CONTRIBUTING.md:15-20]()

## Author Management System
The `authors.yaml` file defines custom contributor details (name, website, avatar) [authors.yaml:1-5](). If an author slug specified in `registry.yaml` is absent from `authors.yaml`, the build system falls back to querying the contributor's GitHub profile [authors.yaml:3-4]().

Title: Author Attribution Resolution Pipeline
```mermaid
graph TB
    subgraph NaturalLanguageSpace["Author Profile Metadata"]
        GitHubProfile[""GitHub User Profile (github.com/username)"""]
        CustomAuthor[""Custom Author Entry [authors.yaml:6-10]"""]
    end

    subgraph CodeEntitySpace["Author System Code & Manifests"]
        AuthorsYaml[""authors.yaml [authors.yaml:1-5]"""]
        RegistryAuthorKey[""registry.yaml authors[] [registry.yaml:12-13]"""]
        AuthorSchemaValidation[""authors_schema.json [.github/authors_schema.json]"""]
    end

    subgraph OutputSpace["Website Rendering"]
        AuthorBadge[""Author Profile Card & Link [README.md:1-10]"""]
    end

    GitHubProfile --> AuthorsYaml
    CustomAuthor --> AuthorsYaml
    AuthorsYaml --> AuthorSchemaValidation
    RegistryAuthorKey --> AuthorsYaml
    AuthorsYaml --> AuthorBadge
```
Sources: [registry.yaml:12-13](), [authors.yaml:1-10](), [README.md:1-10]()

## Validation and Schema Enforcement
To maintain repository data hygiene, validation schemas are defined in `.github/registry_schema.json` and `.github/authors_schema.json` [.github/registry_schema.json:1-48](). These schemas enforce required properties (`title`, `path`, `slug`, `tags`, `authors`) [.github/registry_schema.json:45](), date formats [.github/registry_schema.json:37-40](), and prevent additional properties [.github/registry_schema.json:46](). Notebook validation scripts check structure integrity [CONTRIBUTING.md:26-30]().

Sources: [.github/registry_schema.json:1-48](), [CONTRIBUTING.md:22-35]()

## Content Lifecycle Management
Content moves through distinct lifecycle phases from local development to production publication:
- **Draft:** Developed locally in `examples/` or `articles/` without a `registry.yaml` entry.
- **Review:** Submitted via pull request using the pull request template [.github/pull_request_template.md:1-24](), verified against the contribution rubric (Relevance, Uniqueness, Spelling/Grammar, Clarity, Correctness, Completeness) [CONTRIBUTING.md:40-50](), and validated with structure scripts [CONTRIBUTING.md:26-30]().
- **Published:** Registered in `registry.yaml` with required metadata and rendered on `cookbook.openai.com` [registry.yaml:3-5](), [README.md:1-10]().

Sources: [.github/pull_request_template.md:1-24](), [CONTRIBUTING.md:26-50](), [registry.yaml:3-5]()

## Publishing and Website Generation
The publishing pipeline transforms raw Markdown, notebooks, and YAML registry definitions into the static site hosted at `cookbook.openai.com` [README.md:1-10](), [registry.yaml:3-5]().

Sources: [README.md:1-10](), [registry.yaml:3-5]()

---

